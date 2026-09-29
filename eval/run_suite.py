"""Offline evaluation suite runner -- `make eval` entry point (SPEC §9).

Usage::

    python -m eval.run_suite [--split dev] [--out runs/eval]

The runner:
1. Loads the index (building it if missing).
2. Replays the named transcript split through the full Kairos pipeline
   (Controller → Decomposer → Dispatcher → Synthesizer → Grounding Gate →
   Session Store / Delta Engine).
3. Collects per-turn records enriched with gate-measurement fields.
4. Runs G1–G6 gates via eval.gates.
5. Computes Ready-at-End.
6. Writes ``runs/eval/gates.json`` and ``runs/eval/turn_records.json``.
7. Prints a summary table; exits 0 if all gates pass, 1 if any fail.

Runs fully offline -- no API key, no network after the image build.
All thresholds come from config, not from this file.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

from eval.baseline import run_baseline
from eval.gates import GateResult, ready_at_end, run_all_gates

# kairos/ imports -- never import from data/ or eval/replay files
from kairos.controller.features import ControllerFeatureExtractor
from kairos.controller.rules import RuleBasedController
from kairos.controller.speculation import SpeculationManager
from kairos.decompose import DecompositionManager, ParallelDispatcher
from kairos.grounding.gate import GroundingGate
from kairos.index.store import IndexStore
from kairos.retrieve.hybrid import HybridRetriever
from kairos.schemas import CorpusChunk, GoldLabel, VersionDiff
from kairos.session.delta import DeltaEngine
from kairos.session.store import SessionStore
from kairos.stream.replay import ReplayReader
from kairos.synth.drafting import DraftingManager
from kairos.synth.extractive import ExtractiveSynthesizer

# ---------------------------------------------------------------------------
# Gold label loader
# ---------------------------------------------------------------------------


def _load_gold(gold_path: Path) -> dict[str, GoldLabel]:
    """Load gold labels keyed by turn_id."""
    gold: dict[str, GoldLabel] = {}
    if not gold_path.exists():
        return gold
    with open(gold_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            gl = GoldLabel.model_validate(obj)
            gold[gl.turn_id] = gl
    return gold


# ---------------------------------------------------------------------------
# Per-turn pipeline execution
# ---------------------------------------------------------------------------


def _run_turn(
    reader: ReplayReader,
    store: IndexStore,
    feature_extractor: ControllerFeatureExtractor,
    controller: RuleBasedController,
    speculation_mgr: SpeculationManager,
    retriever: HybridRetriever,
    dispatcher: ParallelDispatcher,
    decomposer: DecompositionManager,
    synthesizer: ExtractiveSynthesizer,
    gate: GroundingGate,
    drafting_mgr: DraftingManager,
    delta_engine: DeltaEngine,
    session_store: SessionStore,
) -> dict[str, Any]:
    """Execute the full pipeline for one turn and return a gate-measurement record."""
    session_id = reader.transcript.session_id
    session_state = session_store.get_or_create(session_id)
    has_prior_answer = bool(session_state.answer)

    t_id = reader.transcript.turn_id
    t_type = reader.transcript.turn_type
    u_end = reader.transcript.utterance_end

    feature_extractor.reset_turn()
    speculation_mgr.reset_turn()
    decomposer.reset_turn()
    dispatcher.reset_turn()
    drafting_mgr.reset_turn()

    first_retrieval_t: float | None = None
    turn_decisions: list[str] = []
    diff_info: VersionDiff | None = None
    v_prior = session_state.current_version
    prior_claims_text: dict[str, str] = {
        c.claim_id: c.text for c in session_state.claims
    }

    retrieved_chunk_ids: set[str] = set()
    telemetry_events: list[str] = []
    ready_at_end_val: float = 0.0

    t_start = time.perf_counter()

    if t_type == "presentation_only":
        new_ans, claims, diff = delta_engine.handle_presentation_only(session_state)
        session_store.save_version(
            session_id,
            answer=new_ans,
            claims=claims,
            citations=session_state.citations,
            diff=diff,
        )
        diff_info = diff
        turn_decisions.append("NO_RETRIEVAL(presentation_restructure)")
        telemetry_events.append("presentation_only_handled")

    elif t_type == "late_constraint":
        full_text = " ".join(c.text for c in reader.transcript.chunks)
        affected_leg = delta_engine.find_affected_leg(full_text, session_state)
        first_retrieval_t = time.perf_counter() - t_start
        turn_decisions.append("RETRIEVE(late_constraint_refinement)")
        if affected_leg:
            delta_retrieval = asyncio.run(retriever.retrieve_leg(full_text))
            dense_r: list[tuple[str, float]] = delta_retrieval.get("dense_results", [])  # type: ignore[assignment]
            sparse_r: list[tuple[str, float]] = delta_retrieval.get("sparse_results", [])  # type: ignore[assignment]
            for cid, _ in dense_r:
                retrieved_chunk_ids.add(cid)
            for cid, _ in sparse_r:
                retrieved_chunk_ids.add(cid)
            new_ans, claims, cites, diff = delta_engine.apply_constraint_refinement(
                affected_leg, delta_retrieval, store.chunks_map, session_state
            )
            session_store.save_version(
                session_id,
                answer=new_ans,
                claims=claims,
                citations=cites,
                diff=diff,
            )
            diff_info = diff
            telemetry_events.append("constraint_refinement_applied")

    else:
        # Standard WAIT / RETRIEVE / NO_RETRIEVAL path
        async def _process_standard(
            r_reader: ReplayReader,
            r_decs: list[str],
            prior_ans: bool,
            v_curr: int,
        ) -> None:
            nonlocal first_retrieval_t, ready_at_end_val
            async for ev in r_reader.stream_events():
                if ev.event_type == "utterance_end":
                    break
                features = feature_extractor.compute_features(ev.prefix, has_prior_answer=prior_ans)
                dec = controller.decide(features, ev.t, has_prior_answer=prior_ans)
                r_decs.append(f"{dec.decision}({dec.reason})")
                telemetry_events.append(f"controller:{dec.decision}")

                if dec.decision == "RETRIEVE":
                    if first_retrieval_t is None:
                        first_retrieval_t = ev.t
                    active_legs, reissued_ids = decomposer.decompose(ev.prefix, ev.t)
                    if reissued_ids:
                        leg_results = await dispatcher.dispatch_legs(active_legs, reissued_ids)
                        for leg_id, res in leg_results.items():
                            # Collect all retrieved chunk IDs from dense and sparse search
                            for cid, _ in res.get("dense_results", []):
                                retrieved_chunk_ids.add(cid)
                            for cid, _ in res.get("sparse_results", []):
                                retrieved_chunk_ids.add(cid)

                            leg_obj = next(
                                (lo for lo in active_legs if lo.leg_id == leg_id), None
                            )
                            if leg_obj:
                                drafting_mgr.draft_leg(
                                    leg_obj,
                                    res,
                                    store.chunks_map,
                                    ev.t,
                                    version=v_curr,
                                )
                                telemetry_events.append(f"draft_leg:{leg_id}")

        asyncio.run(
            _process_standard(
                reader, turn_decisions, has_prior_answer, session_state.current_version
            )
        )

        active_legs_list = list(decomposer.active_legs.values())
        committed_claims, drafting_metrics = drafting_mgr.commit_turn(
            active_legs_list,
            dispatcher.turn_results,
            store.chunks_map,
            u_end,
            version=session_state.current_version,
        )
        ready_at_end_val = float(drafting_metrics.get("ready_at_end", 0.0))
        final_ans = " ".join(c.text for c in committed_claims)
        all_cites = list(dict.fromkeys(cite for c in committed_claims for cite in c.citations))
        session_state.active_legs = {lo.leg_id: lo for lo in active_legs_list}
        session_store.save_version(
            session_id,
            answer=final_ans,
            claims=committed_claims,
            citations=all_cites,
        )
        telemetry_events.append("turn_committed")

    # Accumulate all retrieved chunk IDs into session state (SPEC §9.1: session retrieved set)
    for cid in retrieved_chunk_ids:
        chunk_obj = store.chunks_map.get(cid)
        if chunk_obj and isinstance(chunk_obj, CorpusChunk):
            session_state.retrieved_chunks[cid] = chunk_obj
        elif chunk_obj and isinstance(chunk_obj, dict):
            session_state.retrieved_chunks[cid] = CorpusChunk.model_validate(chunk_obj)

    cumulative_retrieved = set(retrieved_chunk_ids).union(session_state.retrieved_chunks.keys())

    # Determine current state for gate measurement
    current_claims_text: dict[str, str] = {c.claim_id: c.text for c in session_state.claims}
    unchanged_ids: list[str] = diff_info.unchanged if diff_info else []

    active_legs_list = list(decomposer.active_legs.values())
    claims_dicts = [
        {
            "claim_id": c.claim_id,
            "text": c.text,
            "citations": c.citations,
            "status": c.status,
        }
        for c in session_state.claims
    ]

    return {
        "session_id": session_id,
        "turn_id": t_id,
        "turn_type": t_type,
        "utterance_end": u_end,
        "first_retrieval_t": first_retrieval_t,
        "retrieval_required": t_type not in ("presentation_only",),
        "answer": session_state.answer,
        "citations": session_state.citations,
        "legs": [
            {"leg_id": lo.leg_id, "text": lo.text, "first_dispatch_s": lo.first_dispatch_s}
            for lo in active_legs_list
        ],
        "claims": claims_dicts,
        "retrieved_chunk_ids": list(cumulative_retrieved),
        "version_diff_unchanged": unchanged_ids,
        "prior_claims_text": prior_claims_text,
        "current_claims_text": current_claims_text,
        "telemetry_events": telemetry_events,
        "ready_at_end": ready_at_end_val,
        "version": session_state.current_version,
        "prior_version": v_prior,
        "decisions": turn_decisions,
        "lead_time_s": (u_end - first_retrieval_t) if first_retrieval_t is not None else None,
    }


# ---------------------------------------------------------------------------
# Suite runner
# ---------------------------------------------------------------------------


def run_suite(split: str = "dev", out_dir: str = "runs/eval") -> int:
    """Run the full eval suite on *split*, write output, return exit code."""
    scenarios_path = Path("data") / "replay" / split / "scenarios.jsonl"
    gold_path = Path("data") / "replay" / split / "gold.jsonl"

    if not scenarios_path.exists():
        print(f"[eval] ERROR: scenarios not found at {scenarios_path}", file=sys.stderr)
        return 1

    print("[eval] Loading index…")
    store = IndexStore()
    try:
        store.load()
    except Exception:  # noqa: BLE001
        print("[eval] Index not found -- building…")
        store.build()

    index_loaded = bool(store.chunks_map)
    print(f"[eval] Index loaded: {len(store.chunks_map)} chunks")

    _gold = _load_gold(gold_path)  # loaded for future gold-label-based gate extensions
    readers = ReplayReader.from_jsonl(scenarios_path, instant=True)

    feature_extractor = ControllerFeatureExtractor(store.sparse_index)
    controller = RuleBasedController()
    speculation_mgr = SpeculationManager()
    retriever = HybridRetriever(store)
    dispatcher = ParallelDispatcher(retriever)
    decomposer = DecompositionManager()
    synthesizer = ExtractiveSynthesizer()
    gate = GroundingGate()
    delta_engine = DeltaEngine(synthesizer=synthesizer)
    drafting_mgr = DraftingManager(gate=gate, synthesizer=synthesizer)
    session_store = SessionStore()

    turn_records: list[dict[str, Any]] = []

    print(f"[eval] Replaying {len(readers)} turns from '{split}' split…")
    for reader in readers:
        record = _run_turn(
            reader=reader,
            store=store,
            feature_extractor=feature_extractor,
            controller=controller,
            speculation_mgr=speculation_mgr,
            retriever=retriever,
            dispatcher=dispatcher,
            decomposer=decomposer,
            synthesizer=synthesizer,
            gate=gate,
            drafting_mgr=drafting_mgr,
            delta_engine=delta_engine,
            session_store=session_store,
        )
        turn_records.append(record)
        print(
            f"  [{record['turn_id']}] type={record['turn_type']} "
            f"legs={len(record['legs'])} "
            f"first_ret={record['first_retrieval_t']} "
            f"rae={record['ready_at_end']:.2f}"
        )

    # Run gates
    gate_results: list[GateResult] = run_all_gates(turn_records, index_loaded=index_loaded)
    rae = ready_at_end(turn_records)

    # Run baseline for comparison
    baseline_records = run_baseline(str(scenarios_path))
    baseline_gates = run_all_gates(baseline_records, index_loaded=False)

    # Write output
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    gates_output: dict[str, Any] = {
        "split": split,
        "n_turns": len(turn_records),
        "ready_at_end": rae,
        "gates": [g.as_dict() for g in gate_results],
        "baseline_gates": [g.as_dict() for g in baseline_gates],
    }
    with open(out_path / "gates.json", "w", encoding="utf-8") as fh:
        json.dump(gates_output, fh, indent=2)

    with open(out_path / "turn_records.json", "w", encoding="utf-8") as fh:
        json.dump(turn_records, fh, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print(f"EVAL RESULTS -- split={split}, n={len(turn_records)}")
    print("=" * 70)
    all_pass = True
    for g in gate_results:
        icon = "[PASS]" if g.passed else "[FAIL]"
        print(
            f"  {icon} {g.gate}: measured={g.measured:.3f}  threshold={g.threshold}  n={g.n}"
        )
        print(f"      {g.detail}")
        if not g.passed:
            all_pass = False
    print()
    print(f"  Ready-at-End: {rae['ready_at_end']:.3f}  (n={rae['n']})  {rae['detail']}")
    print("=" * 70)
    print(f"  Output: {out_path / 'gates.json'}")
    if all_pass:
        print("  ALL GATES PASSED [PASS]")
    else:
        print("  ONE OR MORE GATES FAILED [FAIL]")
    print("=" * 70)

    return 0 if all_pass else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Kairos offline eval suite")
    parser.add_argument("--split", default="dev", help="Replay split (dev | demo | test)")
    parser.add_argument("--out", default="runs/eval", help="Output directory")
    args = parser.parse_args()
    sys.exit(run_suite(args.split, args.out))


if __name__ == "__main__":
    main()
