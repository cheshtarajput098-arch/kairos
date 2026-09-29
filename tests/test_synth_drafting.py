"""Unit tests for Speed-1 extractive synthesis and Answer-as-you-speak drafting (SPEC §6.2, §6.4)."""

from __future__ import annotations

from kairos.schemas import CorpusChunk, Leg
from kairos.synth.drafting import DraftingManager
from kairos.synth.extractive import ExtractiveSynthesizer


def test_extractive_synthesis_leg() -> None:
    synthesizer = ExtractiveSynthesizer()
    leg = Leg(
        leg_id="L1",
        text="What is the seating capacity of venues in Pune?",
        entities=["Pune", "capacity"],
        first_dispatch_s=1.0,
    )
    chunks_map = {
        "Doc_12§2": CorpusChunk(
            chunk_id="Doc_12§2",
            doc_id="Doc_12",
            section="2",
            title="Venues",
            text="Workshop Venue Alpha in Pune has a maximum seating capacity of 50 attendees. Additional chairs may be requested.",
            char_start=0,
            char_end=116,
        )
    }
    retrieval_res = {
        "dense_results": [("Doc_12§2", 0.95)],
        "sparse_results": [("Doc_12§2", 4.5)],
    }

    claim = synthesizer.synthesize_leg(leg, retrieval_res, chunks_map, version=1)
    assert claim is not None
    assert claim.leg_id == "L1"
    assert claim.citations == ["Doc_12§2"]
    assert "[Doc_12§2]" not in claim.text
    assert "seating capacity of 50 attendees" in claim.evidence_span
    assert len(claim.evidence_span.split()) <= 30


def test_draft_committed_byte_identical() -> None:
    drafting_mgr = DraftingManager()
    leg = Leg(
        leg_id="L1",
        text="capacity of venues in Pune",
        entities=["Pune"],
        first_dispatch_s=1.0,
    )
    chunks_map = {
        "Doc_12§2": CorpusChunk(
            chunk_id="Doc_12§2",
            doc_id="Doc_12",
            section="2",
            title="Venues",
            text="Workshop Venue Alpha in Pune has a maximum seating capacity of 50 attendees.",
            char_start=0,
            char_end=78,
        )
    }
    retrieval_res = {"dense_results": [("Doc_12§2", 0.95)], "sparse_results": []}

    # Mid-utterance draft verified at t=1.2s
    draft = drafting_mgr.draft_leg(leg, retrieval_res, chunks_map, t=1.2)
    assert draft is not None
    assert drafting_mgr.first_verified_draft_t == 1.2

    # Utterance ends at t=2.0s with unchanged leg
    final_legs = [leg]
    committed_claims, metrics = drafting_mgr.commit_turn(
        final_legs,
        {"L1": retrieval_res},
        chunks_map,
        utterance_end_t=2.0,
    )

    assert len(committed_claims) == 1
    # Byte-identical claim text and citations
    assert committed_claims[0].text == draft.text
    assert committed_claims[0].citations == draft.citations
    assert metrics["ready_at_end"] == 1.0
    assert metrics["draft_survival_rate"] == 1.0
    assert metrics["rollback_rate"] == 0.0
    # Negative time: verified 0.8s before utterance end
    assert metrics["first_verified_rel_end_s"] == -0.8
    assert any(e["event"] == "draft_committed" for e in metrics["events"])


def test_draft_rollback_on_mutated_leg() -> None:
    drafting_mgr = DraftingManager()
    chunks_map = {
        "Doc_12§2": CorpusChunk(
            chunk_id="Doc_12§2",
            doc_id="Doc_12",
            section="2",
            title="Venues",
            text="Workshop Venue Alpha in Pune has a maximum seating capacity of 50 attendees.",
            char_start=0,
            char_end=78,
        ),
        "Doc_14§1": CorpusChunk(
            chunk_id="Doc_14§1",
            doc_id="Doc_14",
            section="1",
            title="Venues Mumbai",
            text="Corporate Hall Beta in Mumbai can accommodate up to 100 delegates comfortably.",
            char_start=0,
            char_end=80,
        ),
    }

    # Leg drafted initially as Pune at t=1.0s
    leg_t1 = Leg(leg_id="L1", text="venues in Pune", entities=["Pune"], first_dispatch_s=1.0)
    draft = drafting_mgr.draft_leg(
        leg_t1,
        {"dense_results": [("Doc_12§2", 0.9)]},
        chunks_map,
        t=1.0,
    )
    assert draft is not None

    # User modifies speech mid-turn: "in Pune - no, Mumbai" -> final leg is Mumbai
    leg_final = Leg(leg_id="L1", text="venues in Mumbai", entities=["Mumbai"], first_dispatch_s=1.5)
    final_results = {"L1": {"dense_results": [("Doc_14§1", 0.95)]}}

    # Utterance ends at t=2.0s
    committed_claims, metrics = drafting_mgr.commit_turn(
        [leg_final],
        final_results,
        chunks_map,
        utterance_end_t=2.0,
    )

    assert len(committed_claims) == 1
    # Draft was rolled back and re-synthesized for Mumbai
    assert "Mumbai" in committed_claims[0].text
    assert committed_claims[0].citations == ["Doc_14§1"]
    assert metrics["ready_at_end"] == 0.0  # re-synthesized claim does not count as ready-at-end
    assert metrics["rollback_rate"] == 1.0
    assert metrics["rollbacks_count"] == 1
    # Exposure time = 2.0 - 1.0 = 1000ms
    assert metrics["rollback_exposure_ms"] == 1000.0
    assert any(e["event"] == "draft_rolled_back" for e in metrics["events"])
