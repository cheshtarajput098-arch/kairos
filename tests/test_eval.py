"""Unit tests for eval/gates.py — G1–G6 gate logic and Ready-at-End."""

from __future__ import annotations

from typing import Any

import pytest

from eval.gates import (
    GateResult,
    gate_g1,
    gate_g2,
    gate_g3,
    gate_g4,
    gate_g5,
    gate_g6,
    ready_at_end,
    run_all_gates,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _retrieve_turn(
    turn_id: str = "t1",
    turn_type: str = "single",
    utterance_end: float = 5.0,
    first_retrieval_t: float | None = 1.0,
    retrieval_required: bool = True,
    legs: list[dict[str, Any]] | None = None,
    claims: list[dict[str, Any]] | None = None,
    retrieved_chunk_ids: list[str] | None = None,
    version_diff_unchanged: list[str] | None = None,
    prior_claims_text: dict[str, str] | None = None,
    current_claims_text: dict[str, str] | None = None,
    telemetry_events: list[str] | None = None,
    ready_at_end_val: float = 0.0,
) -> dict[str, Any]:
    # Use sentinel: None → default event list; explicit list (even []) is passed as-is
    tev = ["controller:RETRIEVE"] if telemetry_events is None else telemetry_events
    return {
        "turn_id": turn_id,
        "turn_type": turn_type,
        "utterance_end": utterance_end,
        "first_retrieval_t": first_retrieval_t,
        "retrieval_required": retrieval_required,
        "legs": legs or [],
        "claims": claims or [],
        "retrieved_chunk_ids": retrieved_chunk_ids or [],
        "version_diff_unchanged": version_diff_unchanged or [],
        "prior_claims_text": prior_claims_text or {},
        "current_claims_text": current_claims_text or {},
        "telemetry_events": tev,
        "ready_at_end": ready_at_end_val,
    }


# ---------------------------------------------------------------------------
# G1
# ---------------------------------------------------------------------------


def test_g1_passes_when_loaded() -> None:
    r = gate_g1(True)
    assert r.passed is True
    assert r.n == 1


def test_g1_fails_when_not_loaded() -> None:
    r = gate_g1(False)
    assert r.passed is False


# ---------------------------------------------------------------------------
# G2
# ---------------------------------------------------------------------------


def test_g2_passes_all_lead_time_before_end() -> None:
    turns = [
        _retrieve_turn("t1", utterance_end=5.0, first_retrieval_t=1.0),
        _retrieve_turn("t2", utterance_end=4.0, first_retrieval_t=0.5),
    ]
    r = gate_g2(turns)
    assert r.passed is True
    assert r.measured == 1.0
    assert r.n == 2


def test_g2_fails_when_too_many_late_retrievals() -> None:
    # Only 1 of 5 has first_retrieval_t < utterance_end → 20% < 70%
    turns = [
        _retrieve_turn(f"t{i}", utterance_end=3.0, first_retrieval_t=5.0)
        for i in range(4)
    ]
    turns.append(_retrieve_turn("t5", utterance_end=5.0, first_retrieval_t=1.0))
    r = gate_g2(turns)
    assert r.passed is False
    assert r.measured == pytest.approx(0.2)
    assert r.n == 5


def test_g2_no_retrieve_turns_passes() -> None:
    turns = [
        _retrieve_turn("t1", retrieval_required=False, first_retrieval_t=None)
    ]
    r = gate_g2(turns)
    assert r.passed is True
    assert r.n == 0


# ---------------------------------------------------------------------------
# G3
# ---------------------------------------------------------------------------


def test_g3_compound_two_legs_passes() -> None:
    turns = [
        _retrieve_turn(
            "t1",
            turn_type="compound",
            legs=[{"leg_id": "L1"}, {"leg_id": "L2"}],
        )
    ]
    r = gate_g3(turns)
    assert r.passed is True
    assert r.n == 1


def test_g3_compound_one_leg_fails() -> None:
    turns = [
        _retrieve_turn("t1", turn_type="compound", legs=[{"leg_id": "L1"}])
    ]
    r = gate_g3(turns)
    assert r.passed is False


def test_g3_no_compound_turns() -> None:
    turns = [_retrieve_turn("t1", turn_type="single")]
    r = gate_g3(turns)
    assert r.passed is True
    assert r.n == 0


# ---------------------------------------------------------------------------
# G4
# ---------------------------------------------------------------------------


def test_g4_zero_fabrication_passes() -> None:
    turns = [
        _retrieve_turn(
            "t1",
            claims=[{"claim_id": "c1", "citations": ["Doc_01§1"], "text": "x", "status": "verified"}],
            retrieved_chunk_ids=["Doc_01§1"],
        )
    ]
    r = gate_g4(turns)
    assert r.passed is True
    assert r.measured == pytest.approx(0.0)


def test_g4_fabricated_citation_fails() -> None:
    turns = [
        _retrieve_turn(
            "t1",
            claims=[{"claim_id": "c1", "citations": ["Doc_99§9"], "text": "x", "status": "verified"}],
            retrieved_chunk_ids=["Doc_01§1"],
        )
    ]
    r = gate_g4(turns)
    assert r.passed is False
    assert r.measured > 0


def test_g4_no_claims_passes() -> None:
    turns = [_retrieve_turn("t1", claims=[], retrieved_chunk_ids=[])]
    r = gate_g4(turns)
    assert r.passed is True
    assert r.n == 0


# ---------------------------------------------------------------------------
# G5
# ---------------------------------------------------------------------------


def test_g5_byte_identical_unchanged_passes() -> None:
    turns = [
        _retrieve_turn(
            "t1",
            turn_type="late_constraint",
            version_diff_unchanged=["c1"],
            prior_claims_text={"c1": "Exact sentence."},
            current_claims_text={"c1": "Exact sentence."},
        )
    ]
    r = gate_g5(turns)
    assert r.passed is True
    assert r.n == 1


def test_g5_modified_unchanged_claim_fails() -> None:
    turns = [
        _retrieve_turn(
            "t1",
            turn_type="late_constraint",
            version_diff_unchanged=["c1"],
            prior_claims_text={"c1": "Original text."},
            current_claims_text={"c1": "Modified text."},
        )
    ]
    r = gate_g5(turns)
    assert r.passed is False


def test_g5_no_late_constraint_turns() -> None:
    turns = [_retrieve_turn("t1", turn_type="single")]
    r = gate_g5(turns)
    assert r.passed is True
    assert r.n == 0


# ---------------------------------------------------------------------------
# G6
# ---------------------------------------------------------------------------


def test_g6_telemetry_present_passes() -> None:
    turns = [_retrieve_turn("t1", telemetry_events=["controller:RETRIEVE", "draft_leg:L1"])]
    r = gate_g6(turns)
    assert r.passed is True


def test_g6_no_telemetry_fails() -> None:
    turns = [_retrieve_turn("t1", telemetry_events=[])]
    r = gate_g6(turns)
    assert r.passed is False


# ---------------------------------------------------------------------------
# Ready-at-End
# ---------------------------------------------------------------------------


def test_ready_at_end_fraction() -> None:
    turns = [
        _retrieve_turn("t1", retrieval_required=True, ready_at_end_val=0.8),
        _retrieve_turn("t2", retrieval_required=True, ready_at_end_val=0.0),
    ]
    result = ready_at_end(turns)
    assert result["n"] == 2
    assert result["ready_at_end"] == pytest.approx(0.5)


def test_ready_at_end_no_retrieve() -> None:
    turns = [_retrieve_turn("t1", retrieval_required=False, ready_at_end_val=0.0)]
    result = ready_at_end(turns)
    assert result["n"] == 0
    assert result["ready_at_end"] == 1.0


# ---------------------------------------------------------------------------
# run_all_gates
# ---------------------------------------------------------------------------


def test_run_all_gates_returns_six() -> None:
    turns = [_retrieve_turn("t1")]
    results = run_all_gates(turns, index_loaded=True)
    assert len(results) == 6
    gates = [r.gate for r in results]
    assert gates == ["G1", "G2", "G3", "G4", "G5", "G6"]
    assert all(isinstance(r, GateResult) for r in results)


def test_gate_result_as_dict() -> None:
    r = gate_g1(True)
    d = r.as_dict()
    assert "gate" in d
    assert "passed" in d
    assert "measured" in d
    assert "threshold" in d
    assert "n" in d

