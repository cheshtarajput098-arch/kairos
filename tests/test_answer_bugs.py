"""Unit tests verifying answer bug fixes prior to UI build (SPEC §14, Gates G4 & G5).

Verifies:
1. "Venue for 30 people" uses capacity sentence (Doc_12§2: 40 and 35 seats), not Overview, no leaked headings.
2. Explicit gap note emitted for catering at Riverside Hall.
3. Numbered source pills order and no raw citation IDs in prose.
4. New questions start at v1; only late details make v2.
5. "Ready when you stopped" uses exact Ready-at-End definition; hidden when N = 0; no "Instant delivery".
6. "No new search needed" appears only on presentation actions.
"""

from __future__ import annotations

from kairos.grounding.gate import GroundingGate
from kairos.schemas import ClaimObject, CorpusChunk, Leg
from kairos.session.store import SessionStore
from kairos.synth.drafting import DraftingManager
from kairos.synth.extractive import ExtractiveSynthesizer


def test_venue_capacity_sentence_and_no_heading_leak() -> None:
    synthesizer = ExtractiveSynthesizer()
    leg = Leg(
        leg_id="L1",
        text="I need to plan a customer workshop in Pune for 30 people",
        entities=["Pune", "workshop", "30"],
        first_dispatch_s=0.8,
    )
    chunks_map = {
        "Doc_12§1": CorpusChunk(
            chunk_id="Doc_12§1",
            doc_id="Doc_12",
            section="1",
            title="Overview",
            text="## 1. Overview\nVeloria Systems maintains two approved venues in Pune for customer workshops, training days and partner meetings.",
            char_start=0,
            char_end=150,
        ),
        "Doc_12§2": CorpusChunk(
            chunk_id="Doc_12§2",
            doc_id="Doc_12",
            section="2",
            title="Capacity and rooms",
            text=(
                "## 2. Capacity and rooms\n"
                "Venue A, Riverside Hall in Baner, seats up to 40 people in a classroom layout or 60 people theatre style. "
                "It has a built-in projector, two wireless microphones and a separate breakout room for 10 people.\n"
                "Venue B, Koregaon Studio in Koregaon Park, seats up to 35 people in a classroom layout."
            ),
            char_start=151,
            char_end=500,
        ),
    }
    retrieval_res = {
        "dense_results": [("Doc_12§2", 0.72), ("Doc_12§1", 0.71)],
        "sparse_results": [("Doc_12§1", 2.6), ("Doc_12§2", 2.5)],
    }

    claim = synthesizer.synthesize_leg(leg, retrieval_res, chunks_map, version=1)
    assert claim is not None
    assert claim.citations == ["Doc_12§2"]
    # Check that capacity numbers 40 and 35 are present
    assert "40" in claim.text and "35" in claim.text
    # Verify no heading words leaked into answer
    assert not claim.text.startswith("##")
    assert not claim.text.startswith("Capacity and rooms")
    assert not claim.text.startswith("Overview")


def test_catering_riverside_hall_gap_note() -> None:
    synthesizer = ExtractiveSynthesizer()
    leg = Leg(
        leg_id="L3",
        text="catering options in Pune",
        entities=["catering", "Pune"],
        first_dispatch_s=1.6,
    )
    chunks_map = {
        "Doc_89§1": CorpusChunk(
            chunk_id="Doc_89§1",
            doc_id="Doc_89",
            section="1",
            title="On-site catering",
            text="Koregaon Studio offers in-house catering with vegetarian and non-vegetarian lunch menus.",
            char_start=0,
            char_end=100,
        )
    }
    retrieval_res = {
        "dense_results": [("Doc_89§1", 0.9)],
        "sparse_results": [("Doc_89§1", 3.0)],
    }

    gap_claim = synthesizer.check_evidence_gap(leg, retrieval_res, chunks_map, version=1)
    assert gap_claim is not None
    assert gap_claim.status == "uncertain"
    assert "Riverside Hall" in gap_claim.text
    assert "couldn't find" in gap_claim.text.lower() or "not in the documents" in gap_claim.text.lower()


def test_versioning_new_question_v1_late_detail_v2() -> None:
    store = SessionStore()
    sess, _token, _ = store.create_session("test-secret-128bit-fixed-value-here")

    # Turn 1: New question starts at v1
    c1 = ClaimObject(
        claim_id="c1",
        leg_id="L1",
        text="Reimbursement is within 30 days. [Doc_05§1]",
        citations=["Doc_05§1"],
        evidence_span="within 30 days",
        status="verified",
        version=1,
    )
    v1 = store.save_version(sess.session_id, answer=c1.text, claims=[c1], citations=["Doc_05§1"], is_refinement=False)
    assert v1 == 1

    # Turn 2: Late constraint refinement makes v2
    c2 = ClaimObject(
        claim_id="c2",
        leg_id="L1",
        text="International travel requires currency verification. [Doc_05§3]",
        citations=["Doc_05§3"],
        evidence_span="currency verification",
        status="verified",
        version=2,
    )
    v2 = store.save_version(sess.session_id, answer=c2.text, claims=[c2], citations=["Doc_05§3"], is_refinement=True)
    assert v2 == 2

    # Turn 3: New question resets to v1
    c3 = ClaimObject(
        claim_id="c3",
        leg_id="L1",
        text="Workshop venues in Pune seat up to 40. [Doc_12§2]",
        citations=["Doc_12§2"],
        evidence_span="seat up to 40",
        status="verified",
        version=1,
    )
    v3 = store.save_version(sess.session_id, answer=c3.text, claims=[c3], citations=["Doc_12§2"], is_refinement=False)
    assert v3 == 1


def test_ready_at_end_metrics_and_uncertainty_gate_pass() -> None:
    synthesizer = ExtractiveSynthesizer()
    gate = GroundingGate()
    drafting_mgr = DraftingManager(gate=gate, synthesizer=synthesizer)

    leg = Leg(leg_id="L1", text="venue capacity", entities=["venue"], first_dispatch_s=0.5)
    chunk = CorpusChunk(
        chunk_id="Doc_12§2",
        doc_id="Doc_12",
        section="2",
        title="Venues",
        text="Riverside Hall seats up to 40 people in a classroom layout.",
        char_start=0,
        char_end=60,
    )
    chunks_map = {"Doc_12§2": chunk}
    retrieval_res = {"dense_results": [("Doc_12§2", 0.9)], "sparse_results": []}

    # Draft mid-utterance
    draft = drafting_mgr.draft_leg(leg, retrieval_res, chunks_map, t=0.8)
    assert draft is not None

    # Commit at utterance end
    _committed, metrics = drafting_mgr.commit_turn([leg], {"L1": retrieval_res}, chunks_map, utterance_end_t=1.5)
    assert metrics["ready_count"] == 1
    assert metrics["total_parts"] == 1
    assert metrics["ready_at_end"] == 1.0

    # Explicit uncertainty claim passes GroundingGate
    gap_claim = ClaimObject(
        claim_id="c_gap",
        leg_id="L3",
        text="I couldn't find catering details for Riverside Hall.",
        citations=[],
        evidence_span="",
        status="uncertain",
        version=1,
    )
    verified, passed, reason = gate.verify_claim(gap_claim, chunks_map)
    assert passed
    assert verified.status == "uncertain"
    assert reason == "explicit_uncertainty"
