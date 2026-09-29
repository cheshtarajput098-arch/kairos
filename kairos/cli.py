"""Kairos CLI entrypoint (SPEC §9.6a)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

from kairos.controller.features import ControllerFeatureExtractor
from kairos.controller.rules import RuleBasedController
from kairos.controller.speculation import SpeculationManager
from kairos.decompose import DecompositionManager, ParallelDispatcher
from kairos.fuse.dedupe import deduplicate_and_rank
from kairos.fuse.rrf import reciprocal_rank_fusion
from kairos.grounding.gate import GroundingGate
from kairos.index.store import IndexStore
from kairos.retrieve.hybrid import HybridRetriever
from kairos.schemas import VersionDiff
from kairos.session.delta import DeltaEngine
from kairos.session.store import SessionStore
from kairos.stream.replay import ReplayReader
from kairos.synth.drafting import DraftingManager
from kairos.synth.extractive import ExtractiveSynthesizer


def run_index(corpus_dir: str, index_dir: str = "index") -> None:
    start_time = time.perf_counter()
    print(f"Indexing corpus from '{corpus_dir}' into '{index_dir}'...")
    store = IndexStore(index_dir=Path(index_dir), corpus_dir=Path(corpus_dir))
    store.build()
    elapsed = time.perf_counter() - start_time
    print(
        f"Index built successfully in {elapsed:.2f}s! Total chunks indexed: {len(store.chunks_map)}"
    )


def run_query(query: str, index_dir: str = "index") -> None:
    store = IndexStore(index_dir=Path(index_dir))
    store.load()
    retriever = HybridRetriever(store)

    start_time = time.perf_counter()
    retrieval_res = asyncio.run(retriever.retrieve_leg(query))
    dense_res: list[tuple[str, float]] = retrieval_res["dense_results"]  # type: ignore[assignment]
    sparse_res: list[tuple[str, float]] = retrieval_res["sparse_results"]  # type: ignore[assignment]

    fused = reciprocal_rank_fusion([dense_res, sparse_res], k=60, top_n=10)
    top_chunks = deduplicate_and_rank(fused, store.chunks_map, top_n=5)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    print(f"\nQuery: '{query}'")
    print(f"Hybrid retrieval + RRF completed in {elapsed_ms:.2f} ms")
    print("-" * 60)
    for rank, (chunk_id, score) in enumerate(top_chunks, start=1):
        chunk = store.get_chunk(chunk_id)
        snippet = chunk.text.replace("\n", " ")[:120] if chunk else ""
        print(f"[{rank}] [{chunk_id}] (score: {score:.4f}): {snippet}...")
    print("-" * 60)


def run_replay(
    split: str, transcripts_path: str | None = None, out_dir: str = "runs/cli_replay"
) -> None:
    input_file = (
        Path(transcripts_path)
        if transcripts_path
        else Path("data") / "replay" / split / "scenarios.jsonl"
    )
    if not input_file.exists():
        print(f"Error: Transcript file not found at {input_file}")
        sys.exit(1)

    print(f"=== Replaying '{split}' split from {input_file} ===")
    readers = ReplayReader.from_jsonl(input_file, instant=True)
    store = IndexStore()
    try:
        store.load()
    except Exception:  # noqa: BLE001
        store.build()
    store.warmup()

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

    current_session_id: str | None = None
    turn_results: list[dict[str, Any]] = []

    for reader in readers:
        session_id = reader.transcript.session_id
        session_state = session_store.get_or_create(session_id)
        has_prior_answer = bool(session_state.answer)
        if session_id != current_session_id:
            current_session_id = session_id

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
        prior_answer = session_state.answer

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
            turn_decisions.append("t=0.0s:NO_RETRIEVAL(presentation_restructure)")
        elif t_type == "late_constraint":
            full_text = " ".join(c.text for c in reader.transcript.chunks)
            affected_leg = delta_engine.find_affected_leg(full_text, session_state)
            first_retrieval_t = 0.0
            turn_decisions.append("t=0.0s:RETRIEVE(late_constraint_refinement)")
            if affected_leg:
                delta_retrieval = asyncio.run(retriever.retrieve_leg(full_text))
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
        else:

            async def _process_turn(
                r_reader: ReplayReader, r_decs: list[str], prior_ans: bool, v_curr: int
            ) -> None:
                nonlocal first_retrieval_t
                async for ev in r_reader.stream_events():
                    if ev.event_type == "utterance_end":
                        break
                    features = feature_extractor.compute_features(
                        ev.prefix, has_prior_answer=prior_ans
                    )
                    dec = controller.decide(features, ev.t, has_prior_answer=prior_ans)
                    r_decs.append(f"t={ev.t:.1f}s:{dec.decision}({dec.reason})")

                    if dec.decision == "RETRIEVE":
                        if first_retrieval_t is None:
                            first_retrieval_t = ev.t
                        active_legs, reissued_ids = decomposer.decompose(ev.prefix, ev.t)
                        if reissued_ids:
                            leg_results = await dispatcher.dispatch_legs(active_legs, reissued_ids)
                            for leg_id, res in leg_results.items():
                                leg_obj = next((l for l in active_legs if l.leg_id == leg_id), None)
                                if leg_obj:
                                    drafting_mgr.draft_leg(
                                        leg_obj,
                                        res,
                                        store.chunks_map,
                                        ev.t,
                                        version=v_curr,
                                    )

            asyncio.run(
                _process_turn(
                    reader, turn_decisions, has_prior_answer, session_state.current_version
                )
            )
            active_legs_list = list(decomposer.active_legs.values())
            committed_claims, _ = drafting_mgr.commit_turn(
                active_legs_list,
                dispatcher.turn_results,
                store.chunks_map,
                u_end,
                version=session_state.current_version,
            )
            final_ans = " ".join(c.text for c in committed_claims)
            all_cites = list(dict.fromkeys(cite for c in committed_claims for cite in c.citations))
            session_state.active_legs = {l.leg_id: l for l in active_legs_list}
            session_store.save_version(
                session_id,
                answer=final_ans,
                claims=committed_claims,
                citations=all_cites,
                is_refinement=False,
            )

        lead_time = (u_end - first_retrieval_t) if first_retrieval_t is not None else 0.0
        active_legs_list = list(decomposer.active_legs.values())
        turn_results.append(
            {
                "session_id": session_id,
                "turn_id": t_id,
                "type": reader.transcript.turn_type,
                "utterance_end": u_end,
                "first_retrieval_t": first_retrieval_t,
                "lead_time": round(lead_time, 2),
                "decisions": turn_decisions,
                "version": session_state.current_version,
                "answer": session_state.answer,
                "citations": session_state.citations,
                "legs": [
                    {
                        "leg_id": leg.leg_id,
                        "text": leg.text,
                        "first_dispatch_s": leg.first_dispatch_s,
                    }
                    for leg in active_legs_list
                ],
            }
        )

        if diff_info:
            print("\n" + "=" * 80)
            print(f"SESSION: {session_id} | TURN: {t_id} ({t_type})")
            print(f"VERSION UPDATE: v{v_prior} -> v{session_state.current_version}")
            print(f"Prior Answer (v{v_prior}):\n  {prior_answer}")
            print(f"New Answer (v{session_state.current_version}):\n  {session_state.answer}")
            print("Version Diff:")
            print(f"  Added: {diff_info.added}")
            print(f"  Changed: {diff_info.changed}")
            print(f"  Unchanged: {diff_info.unchanged}")
            print(f"  Retracted: {diff_info.retracted}")
            print(f"  Citations Added: {diff_info.citations_added}")
            print("=" * 80 + "\n")
        else:
            print("\n" + "=" * 80)
            print(f"SESSION: {session_id} | TURN: {t_id} ({t_type})")
            print(f"Answer (v{session_state.current_version}):\n  {session_state.answer}")
            print(f"Citations: {session_state.citations}")
            print("=" * 80 + "\n")

    print(f"\nReplayed {len(turn_results)} turns successfully:")
    print(
        f"{'Turn ID':<14} | {'Type':<18} | {'Utterance End':<13} | {'First Retrieve':<14} | {'Lead Time':<9} | {'Legs':<24}"
    )
    print("-" * 102)
    for r in turn_results:
        f_ret = f"{r['first_retrieval_t']:.1f}s" if r["first_retrieval_t"] is not None else "None"
        decs: list[str] = r["decisions"]
        legs_data: list[dict[str, Any]] = r["legs"]
        legs_str = (
            ", ".join(f"{l['leg_id']} ({l['first_dispatch_s']:.1f}s)" for l in legs_data)
            if legs_data
            else "None"
        )
        print(
            f"{r['turn_id']:<14} | {r['type']:<18} | {r['utterance_end']:<13.1f} | {f_ret:<14} | {r['lead_time']:<8.2f}s | {legs_str:<24}"
        )
        print(f"   Decisions: {' -> '.join(decs)}")
        for l in legs_data:
            print(f"      {l['leg_id']} [{l['first_dispatch_s']:.1f}s]: {l['text']}")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / "replay_summary.json", "w", encoding="utf-8") as f:
        json.dump(turn_results, f, indent=2)
    print(f"\nSaved replay report to {out_path / 'replay_summary.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="kairos", description="Kairos Streaming Live RAG Engine CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # index command
    index_parser = subparsers.add_parser("index", help="Build or verify corpus index")
    index_parser.add_argument("--corpus", default="data/corpus", help="Path to corpus directory")
    index_parser.add_argument(
        "--index-dir", default="index", help="Path to index storage directory"
    )

    # query command
    query_parser = subparsers.add_parser("query", help="Run hybrid search query against corpus")
    query_parser.add_argument("query_pos", nargs="?", default=None, help="Query string")
    query_parser.add_argument("--q", default=None, help="Query string flag")
    query_parser.add_argument(
        "--index-dir", default="index", help="Path to index storage directory"
    )

    # replay command
    replay_parser = subparsers.add_parser("replay", help="Replay transcript evaluation split")
    replay_parser.add_argument(
        "split_pos", nargs="?", default=None, help="Replay split (demo, dev, test)"
    )
    replay_parser.add_argument("--split", default="dev", help="Replay split (demo, dev, test)")
    replay_parser.add_argument("--transcripts", help="Custom path to transcript JSON/JSONL")
    replay_parser.add_argument("--out", default="runs/cli_replay", help="Output directory")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "index":
        run_index(args.corpus, args.index_dir)
    elif args.command == "query":
        q_text = args.query_pos or args.q
        if not q_text:
            print("Error: query text is required")
            sys.exit(1)
        run_query(q_text, args.index_dir)
    elif args.command == "replay":
        target_split = args.split_pos or args.split
        run_replay(target_split, args.transcripts, args.out)


if __name__ == "__main__":
    main()
