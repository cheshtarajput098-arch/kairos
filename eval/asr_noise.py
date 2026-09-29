"""ASR noise generator and speech robustness evaluation (SPEC §9.4b).

Generates seeded noisy variants of transcripts at target WER (5% and 10%):
- Word substitutions (phonetic near-spellings, homophones)
- Word deletions and insertions
- Disfluencies (fillers: 'uh', 'um', repetitions: 'the the')
- Partial revisions (20-30% partial chunks revised mid-utterance)

Evaluates G2, G3, false-trigger rate, Ready-at-End, and G4 across clean vs 5% vs 10% WER.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
from pathlib import Path
from typing import Any

from eval.gates import (
    gate_g2_official,
    gate_g2_strict,
    gate_g3_official,
    gate_g3_strict,
    gate_g4_official,
    gate_g4_strict,
    ready_at_end,
)
from eval.run_suite import _load_gold, _run_turn
from kairos.controller.features import ControllerFeatureExtractor
from kairos.controller.rules import RuleBasedController
from kairos.controller.speculation import SpeculationManager
from kairos.decompose import DecompositionManager, ParallelDispatcher
from kairos.grounding.gate import GroundingGate
from kairos.index.store import IndexStore
from kairos.retrieve.hybrid import HybridRetriever
from kairos.schemas import ReplayTranscript
from kairos.session.delta import DeltaEngine
from kairos.session.store import SessionStore
from kairos.stream.replay import ReplayReader
from kairos.synth.drafting import DraftingManager
from kairos.synth.extractive import ExtractiveSynthesizer

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "runs" / "eval" / "robustness.json"

# Common phonetic/orthographic speech substitutions
SUBSTITUTIONS: dict[str, str] = {
    "for": "four",
    "four": "for",
    "two": "to",
    "to": "too",
    "policy": "policies",
    "policies": "policy",
    "cancellation": "cancelation",
    "venue": "venues",
    "venues": "venue",
    "room": "rooms",
    "catering": "caterings",
    "there": "their",
    "their": "there",
    "and": "an",
    "pune": "poona",
    "mumbai": "bombay",
    "delhi": "dilli",
    "conference": "conferences",
    "attendee": "attendees",
    "attendees": "attendee",
    "capacity": "capacities",
    "equipment": "equipments",
    "booking": "bookings",
}

FILLERS = ["um", "uh", "you know", "like", "actually"]


def inject_asr_noise(
    scenario: dict[str, Any],
    target_wer: float,
    seed: int = 42,
) -> dict[str, Any]:
    """Inject substitutions, deletions, insertions, disfluencies, and partials at target WER."""
    if target_wer <= 0.0:
        return copy.deepcopy(scenario)

    rng = random.Random(seed + hash(scenario.get("turn_id", "")))
    noisy_sc = copy.deepcopy(scenario)
    chunks = noisy_sc.get("chunks", [])
    noisy_chunks: list[dict[str, Any]] = []

    for idx, ch in enumerate(chunks):
        text = ch.get("text", "")
        t = ch.get("t", 0.0)
        words = text.split()
        new_words: list[str] = []

        for w in words:
            w_lower = w.lower()
            roll = rng.random()

            # Substitution
            if roll < target_wer * 0.6 and w_lower in SUBSTITUTIONS:
                sub = SUBSTITUTIONS[w_lower]
                new_words.append(sub.upper() if w.isupper() else sub.capitalize() if w.istitle() else sub)
            # Deletion (skip non-essential words)
            elif roll < target_wer * 0.8 and w_lower in ("the", "a", "an", "is", "of", "and"):
                continue
            # Repetition
            elif roll < target_wer * 0.9:
                new_words.extend([w, w])
            else:
                new_words.append(w)

        # Injected filler at chunk start
        if rng.random() < target_wer * 0.7:
            filler = rng.choice(FILLERS)
            new_words.insert(0, filler)

        chunk_text = " ".join(new_words)

        # Partial revision: occasionally emit a partial chunk then revised
        if rng.random() < 0.20 and len(new_words) > 2:
            partial_text = " ".join(new_words[:-1])
            noisy_chunks.append({
                "t": t,
                "text": partial_text,
                "partial": True,
            })
            revised_t = round(t + 0.15, 2)
            noisy_chunks.append({
                "t": revised_t,
                "text": chunk_text,
                "revises": len(noisy_chunks) - 1,
            })
        else:
            noisy_chunks.append({
                "t": t,
                "text": chunk_text,
            })

    noisy_sc["chunks"] = noisy_chunks
    return noisy_sc


def evaluate_noise_level(
    scenarios: list[dict[str, Any]],
    gold_by_turn: dict[str, Any],
    store: IndexStore,
    wer: float,
    seed: int = 42,
) -> dict[str, Any]:
    """Run replay evaluation on a noisy variant of the test set."""
    # Pipeline components
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

    noisy_scenarios = [inject_asr_noise(sc, target_wer=wer, seed=seed) for sc in scenarios]
    turn_records: list[dict[str, Any]] = []

    for sc in noisy_scenarios:
        transcript = ReplayTranscript.model_validate(sc)
        reader = ReplayReader(transcript=transcript, instant=True)
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

        gold_item = gold_by_turn.get(record["turn_id"])
        if gold_item:
            record["source"] = getattr(gold_item, "source", "llm_drafted")
            record["decisive_word_position"] = getattr(gold_item, "decisive_word_position", "middle")
            record["gold_sub_intents"] = getattr(gold_item, "sub_intents", [])
            record["gold_answer_chunks"] = getattr(gold_item, "answer_chunks", {})

        turn_records.append(record)

    # Compute metrics for this noise level
    g2_off = gate_g2_official(turn_records)
    g2_str = gate_g2_strict(turn_records)
    g3_off = gate_g3_official(turn_records)
    g3_str = gate_g3_strict(turn_records)
    g4_off = gate_g4_official(turn_records)
    g4_str = gate_g4_strict(turn_records)
    rae = ready_at_end(turn_records)

    suppress_turns = [r for r in turn_records if not r.get("retrieval_required")]
    false_triggers = sum(1 for r in suppress_turns if r.get("first_retrieval_t") is not None)
    ft_rate = (false_triggers / len(suppress_turns)) if suppress_turns else 0.0

    return {
        "wer": wer,
        "n_turns": len(turn_records),
        "g2_official": round(g2_off.measured, 4),
        "g2_strict": round(g2_str.measured, 4),
        "g3_official": round(g3_off.measured, 4),
        "g3_strict": round(g3_str.measured, 4),
        "false_trigger_rate": round(ft_rate, 4),
        "ready_at_end": round(rae["ready_at_end"], 4),
        "g4_official": round(g4_off.measured, 4),
        "g4_strict": round(g4_str.measured, 4),
    }


def run_robustness_suite(
    split: str = "test",
    out_file: Path | None = None,
    store: IndexStore | None = None,
) -> dict[str, Any]:
    """Execute speech robustness evaluation across Clean (0%), 5% WER, and 10% WER."""
    scenarios_path = ROOT / "data" / "replay" / split / "scenarios.jsonl"
    gold_path = ROOT / "data" / "replay" / split / "gold.jsonl"

    scenarios = [json.loads(line) for line in scenarios_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    gold_map = _load_gold(gold_path)

    if store is None:
        store = IndexStore()
        store.load()

    levels = [0.0, 0.05, 0.10]
    results: list[dict[str, Any]] = []

    for wer in levels:
        res = evaluate_noise_level(scenarios, gold_map, store, wer=wer)
        results.append(res)

    output = {
        "split": split,
        "n_turns": len(scenarios),
        "noise_levels": results,
        "comparison_table": {
            "columns": ["Metric", "Clean (0% WER)", "Noise (5% WER)", "Noise (10% WER)"],
            "rows": [
                [
                    "G2 Early Retrieval (Official)",
                    f"{results[0]['g2_official']:.1%}",
                    f"{results[1]['g2_official']:.1%}",
                    f"{results[2]['g2_official']:.1%}",
                ],
                [
                    "G2 Early Retrieval (Strict)",
                    f"{results[0]['g2_strict']:.1%}",
                    f"{results[1]['g2_strict']:.1%}",
                    f"{results[2]['g2_strict']:.1%}",
                ],
                [
                    "G3 Multi-Intent (Official)",
                    f"{results[0]['g3_official']:.1%}",
                    f"{results[1]['g3_official']:.1%}",
                    f"{results[2]['g3_official']:.1%}",
                ],
                [
                    "G3 Multi-Intent (Strict)",
                    f"{results[0]['g3_strict']:.1%}",
                    f"{results[1]['g3_strict']:.1%}",
                    f"{results[2]['g3_strict']:.1%}",
                ],
                [
                    "False Trigger Rate",
                    f"{results[0]['false_trigger_rate']:.1%}",
                    f"{results[1]['false_trigger_rate']:.1%}",
                    f"{results[2]['false_trigger_rate']:.1%}",
                ],
                [
                    "Ready-at-End",
                    f"{results[0]['ready_at_end']:.1%}",
                    f"{results[1]['ready_at_end']:.1%}",
                    f"{results[2]['ready_at_end']:.1%}",
                ],
                [
                    "G4 Grounding Support",
                    f"{results[0]['g4_official']:.1%}",
                    f"{results[1]['g4_official']:.1%}",
                    f"{results[2]['g4_official']:.1%}",
                ],
            ],
        },
    }

    out_p = out_file or DEFAULT_OUT
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ASR noise robustness evaluation (SPEC §9.4b)")
    parser.add_argument("--split", default="test", help="Replay split (dev | test)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output JSON path")
    args = parser.parse_args()

    res = run_robustness_suite(args.split, args.out)
    print("ASR noise robustness suite completed.")
    print("\nRobustness Comparison Table:")
    table = res.get("comparison_table", {})
    headers = table.get("columns", [])
    print(f"{headers[0]:<32} | {headers[1]:<15} | {headers[2]:<15} | {headers[3]:<15}")
    print("-" * 85)
    for row in table.get("rows", []):
        print(f"{row[0]:<32} | {row[1]:<15} | {row[2]:<15} | {row[3]:<15}")
    print(f"\nResults saved to {args.out}")


if __name__ == "__main__":
    main()
