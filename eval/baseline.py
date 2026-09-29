"""Minimal no-retrieval baseline for eval comparison (SPEC §9.5).

The baseline returns an empty answer for every turn, producing:
  - 0 citations
  - 0 legs
  - first_retrieval_t = None (never retrieves)
  - Ready-at-End = 0

This is used as the denominator for G1 delta and for ablation comparison.
The baseline never imports corpus or retrieval code, ensuring it can be run
on a clean machine without any index.
"""

from __future__ import annotations

from typing import Any


def baseline_turn(session_id: str, turn_id: str, turn_type: str, utterance_end: float) -> dict[str, Any]:
    """Return a no-retrieval baseline record for one turn."""
    return {
        "session_id": session_id,
        "turn_id": turn_id,
        "turn_type": turn_type,
        "utterance_end": utterance_end,
        "first_retrieval_t": None,
        "retrieval_required": False,
        "answer": "",
        "citations": [],
        "legs": [],
        "claims": [],
        "retrieved_chunk_ids": [],
        "version_diff_unchanged": [],
        "prior_claims_text": {},
        "current_claims_text": {},
        "telemetry_events": [],
        "ready_at_end": 0.0,
    }


def run_baseline(scenarios_path: str) -> list[dict[str, Any]]:
    """Run the baseline over all turns in a JSONL scenarios file.

    Parameters
    ----------
    scenarios_path:
        Path to a JSONL file where each line is a ReplayTranscript-compatible
        JSON object with at least ``session_id``, ``turn_id``, ``turn_type``
        and ``utterance_end``.

    Returns
    -------
    list of per-turn baseline records.
    """
    import json
    from pathlib import Path

    path = Path(scenarios_path)
    records: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj: dict[str, Any] = json.loads(line)
            records.append(
                baseline_turn(
                    session_id=obj.get("session_id", "baseline-session"),
                    turn_id=obj.get("turn_id", f"turn-{len(records) + 1}"),
                    turn_type=obj.get("turn_type", "single"),
                    utterance_end=float(obj.get("utterance_end", 0.0)),
                )
            )
    return records
