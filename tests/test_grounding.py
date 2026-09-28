"""Unit tests for Stage 1 Grounding Gate (SPEC §6.3, Gate G4).

Asserts:
1. Fabricated document IDs are detected and dropped (0 hallucinated IDs).
2. Missing or fabricated evidence spans are dropped.
3. Valid spans match verbatim and under whitespace/punctuation normalization.
4. Dropped claims generate explicit uncertainty statements.
"""

from __future__ import annotations

from kairos.grounding.gate import GroundingGate
from kairos.schemas import ClaimObject, CorpusChunk


def test_fabricated_id_dropped() -> None:
    gate = GroundingGate()
    retrieved_chunks = {
        "Doc_1§1": CorpusChunk(
            chunk_id="Doc_1§1",
            doc_id="Doc_1",
            section="1",
            title="Policy",
            text="The cancellation notice requires at least 48 hours.",
            char_start=0,
            char_end=52,
        )
    }

    # Claim citing fabricated/hallucinated ID
    claim = ClaimObject(
        claim_id="c1",
        leg_id="L1",
        text="Cancellation requires 48 hours notice. [Doc_99§9]",
        citations=["Doc_99§9"],
        evidence_span="requires at least 48 hours",
        status="verified",
        version=1,
    )

    verified, passed, reason = gate.verify_claim(claim, retrieved_chunks)
    assert not passed
    assert verified.status == "dropped"
    assert "fabricated_id:Doc_99§9" in reason or "unretrieved_or_fabricated_id:Doc_99§9" in reason


def test_span_missing_from_chunk_dropped() -> None:
    gate = GroundingGate()
    retrieved_chunks = {
        "Doc_1§1": CorpusChunk(
            chunk_id="Doc_1§1",
            doc_id="Doc_1",
            section="1",
            title="Policy",
            text="The cancellation notice requires at least 48 hours.",
            char_start=0,
            char_end=52,
        )
    }

    # Claim citing valid ID but hallucinating facts not in chunk
    claim = ClaimObject(
        claim_id="c1",
        leg_id="L1",
        text="The venue provides free champagne on arrival. [Doc_1§1]",
        citations=["Doc_1§1"],
        evidence_span="free champagne on arrival",
        status="verified",
        version=1,
    )

    verified, passed, reason = gate.verify_claim(claim, retrieved_chunks)
    assert not passed
    assert verified.status == "dropped"
    assert reason == "evidence_span_not_in_chunk"


def test_valid_span_and_fuzzy_normalization_verified() -> None:
    gate = GroundingGate()
    retrieved_chunks = {
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

    # Verbatim span
    c1 = ClaimObject(
        claim_id="c1",
        leg_id="L1",
        text="Seating capacity is 50 attendees. [Doc_12§2]",
        citations=["Doc_12§2"],
        evidence_span="maximum seating capacity of 50 attendees",
        status="verified",
        version=1,
    )
    v1, p1, _ = gate.verify_claim(c1, retrieved_chunks)
    assert p1
    assert v1.status == "verified"

    # Normalized punctuation/case
    c2 = ClaimObject(
        claim_id="c2",
        leg_id="L1",
        text="Capacity details. [Doc_12§2]",
        citations=["Doc_12§2"],
        evidence_span="Maximum Seating Capacity Of 50 Attendees!",
        status="verified",
        version=1,
    )
    v2, p2, _ = gate.verify_claim(c2, retrieved_chunks)
    assert p2
    assert v2.status == "verified"


def test_verify_claims_emits_uncertainty_for_dropped() -> None:
    gate = GroundingGate()
    retrieved_chunks = {
        "Doc_1§1": CorpusChunk(
            chunk_id="Doc_1§1",
            doc_id="Doc_1",
            section="1",
            title="Policy",
            text="Standard check-in time is 2:00 PM.",
            char_start=0,
            char_end=34,
        )
    }

    claims = [
        ClaimObject(
            claim_id="c1",
            leg_id="L1",
            text="Check-in is at 2:00 PM. [Doc_1§1]",
            citations=["Doc_1§1"],
            evidence_span="Standard check-in time is 2:00 PM",
            status="verified",
            version=1,
        ),
        ClaimObject(
            claim_id="c2",
            leg_id="L2",
            text="Helicopter transfer is included. [Doc_1§1]",
            citations=["Doc_1§1"],
            evidence_span="Helicopter transfer is included",
            status="verified",
            version=1,
        ),
    ]

    verified_claims, uncertainties = gate.verify_claims(claims, retrieved_chunks)
    assert len(verified_claims) == 2
    assert verified_claims[0].status == "verified"
    assert verified_claims[1].status == "dropped"
    assert len(uncertainties) == 1
    assert "Evidence could not be verified" in uncertainties[0]
