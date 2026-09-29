"""Unit tests for eval/gates.py — G1–G6 gate logic and Ready-at-End."""

from __future__ import annotations

from typing import Any

import pytest

from eval.gates import (
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
# run_all_gates & Stratifications
# ---------------------------------------------------------------------------


def test_run_all_gates_returns_six() -> None:
    turns = [_retrieve_turn("t1")]
    official, strict = run_all_gates(turns, index_loaded=True)
    assert len(official) == 6
    assert len(strict) == 6
    assert [r.gate for r in official] == ["G1", "G2", "G3", "G4", "G5", "G6"]
    assert [r.gate for r in strict] == ["G1", "G2", "G3", "G4", "G5", "G6"]
    assert all(r.variant == "official" for r in official)
    assert all(r.variant == "strict" for r in strict)


def test_gate_result_as_dict() -> None:
    r = gate_g1(True)
    d = r.as_dict()
    assert "gate" in d
    assert "variant" in d
    assert "passed" in d
    assert "measured" in d
    assert "threshold" in d
    assert "n" in d


def test_ready_at_end_by_cadence() -> None:
    from eval.gates import ready_at_end_by_cadence

    turns = [
        _retrieve_turn("t1", retrieval_required=True, utterance_end=2.0, first_retrieval_t=0.5, ready_at_end_val=1.0),
        _retrieve_turn("t2", retrieval_required=True, utterance_end=2.0, first_retrieval_t=1.8, ready_at_end_val=0.0),
    ]
    res = ready_at_end_by_cadence(turns)
    assert "cadence_0_75x" in res
    assert "cadence_1_0x" in res
    assert "cadence_1_5x" in res
    assert res["n"] == 2


def test_compute_stratified_gates() -> None:
    from eval.gates import compute_stratified_gates

    turns = [
        {**_retrieve_turn("t1"), "source": "llm_drafted", "decisive_word_position": "early"},
        {**_retrieve_turn("t2"), "source": "human_external", "decisive_word_position": "last third"},
    ]
    strat = compute_stratified_gates(turns)
    assert "by_source" in strat
    assert "by_decisive_word_position" in strat
    assert "llm_drafted" in strat["by_source"]
    assert "human_external" in strat["by_source"]
    assert "early" in strat["by_decisive_word_position"]
    assert "last third" in strat["by_decisive_word_position"]


# ---------------------------------------------------------------------------
# Freeze verification tests
# ---------------------------------------------------------------------------


def test_freeze_verification(tmp_path: Any) -> None:
    from eval.freeze import compute_manifest, verify_test_split_freeze

    # Manifest should compute without error
    manifest = compute_manifest()
    assert len(manifest) >= 2
    # Verify current repo freeze
    ok, errors = verify_test_split_freeze()
    assert ok is True
    assert errors == []


# ---------------------------------------------------------------------------
# Metrics tests (SPEC §9.1a)
# ---------------------------------------------------------------------------


def test_metrics_calculation() -> None:
    from eval.metrics import compute_all_metrics, compute_ndcg_at_k, compute_recall_at_k

    # Test recall@k
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    gold = {"doc2", "doc5"}
    rec = compute_recall_at_k(retrieved, gold, k=2)
    assert rec == pytest.approx(0.5)

    # Test nDCG@10
    ndcg = compute_ndcg_at_k(retrieved, {"doc1"}, k=10)
    assert ndcg == pytest.approx(1.0)

    # Test overall metrics
    turns = [
        {
            **_retrieve_turn("t1", retrieval_required=True, utterance_end=2.0, first_retrieval_t=0.5, ready_at_end_val=1.0),
            "gold_answer_chunks": {"q1": ["doc1"]},
            "retrieved_chunk_ids": ["doc1", "doc2"],
            "legs": [{"leg_id": "L1", "text": "test query"}],
            "answer": "Test answer with five words.",
        },
        {
            **_retrieve_turn("t2", retrieval_required=False, utterance_end=1.5, first_retrieval_t=None),
            "turn_type": "presentation_only",
            "gold_answer_chunks": {},
            "retrieved_chunk_ids": [],
            "legs": [],
            "answer": "Short answer.",
        },
    ]
    res = compute_all_metrics(turns)
    assert "retrieval_effectiveness" in res
    assert "latencies_ms" in res
    assert "controller_efficiency" in res
    assert "cost_to_performance_table" in res
    assert res["controller_efficiency"]["suppression_rate"] == 1.0


# ---------------------------------------------------------------------------
# Controller Model tests (SPEC §4.4)
# ---------------------------------------------------------------------------


def test_controller_model_classifier() -> None:
    import numpy as np

    from eval.controller_model import LogisticRegressionClassifier, compute_roc_curve

    X = np.array([
        [1.0, 2.0, 1.0, 0.1, 0.0, 1.0, 0.0],
        [2.0, 3.0, 1.0, 0.05, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.8],
        [0.0, 0.0, 0.0, 0.9, 1.0, 0.0, 0.9],
    ])
    y = np.array([1, 1, 0, 0])

    clf = LogisticRegressionClassifier(learning_rate=0.2, epochs=100)
    clf.fit(X, y)

    preds = clf.predict(X)
    assert len(preds) == 4
    assert preds[0] == 1
    assert preds[2] == 0

    curve = compute_roc_curve(clf, X, y)
    assert len(curve) > 0
    assert "early_retrieval_rate" in curve[0]
    assert "false_trigger_rate" in curve[0]

    # Serialization roundtrip
    d = clf.to_dict()
    clf2 = LogisticRegressionClassifier.from_dict(d)
    preds2 = clf2.predict(X)
    assert np.array_equal(preds, preds2)


# ---------------------------------------------------------------------------
# Inter-Annotator Agreement tests (SPEC §9.6)
# ---------------------------------------------------------------------------


def test_cohens_kappa_calculation() -> None:
    from eval.iaa import compute_cohens_kappa

    labels_a = ["cat", "dog", "cat", "fish"]
    labels_b = ["cat", "dog", "dog", "fish"]
    po, kappa = compute_cohens_kappa(labels_a, labels_b)
    assert po == 0.75
    assert kappa > 0.5


# ---------------------------------------------------------------------------
# Step 08 Part 2 Tests: Ablations, Stabilisation, ASR Noise, Race, Report
# ---------------------------------------------------------------------------


def test_ablations_components() -> None:
    from eval.ablations import run_ablation_d, run_ablation_e

    records = [
        {"turn_id": "t1", "retrieval_required": True, "claims": [{"id": "c1"}], "ready_at_end": 1.0, "legs": [{"id": "l1"}]},
        {"turn_id": "t2", "retrieval_required": True, "claims": [{"id": "c2"}], "ready_at_end": 0.5, "legs": [{"id": "l2"}]},
    ]
    ab_d = run_ablation_d(records)
    assert "speed_1_extractive_only" in ab_d
    assert "two_speed_synthesis" in ab_d
    assert ab_d["speed_1_extractive_only"]["grounding_pass_rate"] == 1.0

    ab_e = run_ablation_e(records)
    assert "drafting_enabled" in ab_e
    assert "drafting_disabled" in ab_e
    assert ab_e["drafting_enabled"]["ready_at_end"] == 0.75
    assert ab_e["drafting_disabled"]["ready_at_end"] == 0.0


def test_stabilisation_turn() -> None:
    from eval.stabilisation import compute_turn_stabilisation
    from kairos.index.store import IndexStore

    store = IndexStore()
    if not store.chunks_map:
        store.load()

    scenario = {
        "turn_id": "stab-t1",
        "turn_type": "single",
        "chunks": [
            {"t": 0.0, "text": "I need venue capacity"},
            {"t": 0.8, "text": "in Pune for 30 attendees."},
        ],
        "utterance_end": 1.8,
    }
    gold = {
        "turn_id": "stab-t1",
        "retrieval_required": True,
        "answer_chunks": {"capacity": ["Doc_12§2"]},
    }

    res = compute_turn_stabilisation(scenario, gold, store, controller_trigger_t=0.8)
    assert res is not None
    assert "t_sc_s" in res
    assert "t_suf_s" in res
    assert "phi" in res
    assert "volatility" in res
    assert "hidden_latency_s" in res
    assert res["phi"] >= 0.0


def test_asr_noise_injection() -> None:
    from eval.asr_noise import inject_asr_noise

    sc = {
        "turn_id": "noise-t1",
        "chunks": [
            {"t": 0.0, "text": "I need room for thirty people in Pune and policy details"},
            {"t": 1.0, "text": "and catering options for the guests."},
        ],
    }
    clean = inject_asr_noise(sc, target_wer=0.0)
    assert clean["chunks"][0]["text"] == sc["chunks"][0]["text"]

    noisy_5 = inject_asr_noise(sc, target_wer=0.05, seed=123)
    assert len(noisy_5["chunks"]) >= len(sc["chunks"])

    noisy_10 = inject_asr_noise(sc, target_wer=0.10, seed=456)
    assert len(noisy_10["chunks"]) >= len(sc["chunks"])


def test_race_computation_mock() -> None:
    from eval.race import compute_race_run

    mock_records = [
        {
            "turn_id": "test-s01-t1",
            "retrieval_required": True,
            "first_retrieval_t": 0.8,
            "utterance_end": 2.1,
            "ready_at_end": 1.0,
        }
    ]
    res = compute_race_run(split="test", turn_records=mock_records)
    assert "summary" in res
    assert "turns" in res
    assert res["summary"]["n_turns"] > 0
    assert res["summary"]["median_time_saved_s"] >= 0.0


def test_build_report_generation(tmp_path: Any) -> None:
    from eval.build_report import format_eval_report

    out_file = tmp_path / "TEST_EVAL_REPORT.md"
    content = format_eval_report(dest_path=out_file)
    assert out_file.exists()
    assert "Kairos" in content
    assert "G1" in content
    assert "Ready-at-End" in content


