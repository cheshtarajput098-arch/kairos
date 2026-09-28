"""Unit tests for Session Store, HMAC Tokens, and Delta Engine (SPEC §7, Gate G5)."""

from __future__ import annotations

import time

from kairos.schemas import ClaimObject, CorpusChunk, Leg
from kairos.session.delta import DeltaEngine
from kairos.session.store import SessionStore
from kairos.session.token import issue_token, verify_token


def test_token_issuance_and_verification() -> None:
    secret = "test-secret-key-12345"
    session_id = "abc123session"

    token, expires_at = issue_token(session_id, secret, ttl_seconds=60)
    assert expires_at > time.time()
    assert verify_token(session_id, token, secret)

    # Wrong secret fails
    assert not verify_token(session_id, token, "wrong-secret")

    # Mismatched session ID fails
    assert not verify_token("other_session_id", token, secret)

    # Expired token fails
    expired_token, _ = issue_token(session_id, secret, ttl_seconds=-10)
    assert not verify_token(session_id, expired_token, secret)


def test_session_store_lifecycle_and_isolation() -> None:
    secret = "secret-key-test"
    store = SessionStore(max_sessions=5, ttl_seconds=60)

    # Create session A
    state_a, token_a, _ = store.create_session(secret)
    # Create session B
    state_b, token_b, _ = store.create_session(secret)

    # Valid access
    assert store.get_session(state_a.session_id, token_a, secret) is not None
    assert store.get_session(state_b.session_id, token_b, secret) is not None

    # SESSION ISOLATION: Token A cannot access Session B (Security Rule 4)
    assert store.get_session(state_b.session_id, token_a, secret) is None
    assert store.get_session(state_a.session_id, token_b, secret) is None

    # Explicit clear
    store.clear_session(state_a.session_id)
    assert store.get_session(state_a.session_id, token_a, secret) is None


def test_delta_engine_presentation_only() -> None:
    delta = DeltaEngine()
    store = SessionStore()
    state, _, _ = store.create_session("sec")

    # Seed session with prior answer and claims
    claim1 = ClaimObject(
        claim_id="c1",
        leg_id="L1",
        text="Venue capacity is 50 attendees. [Doc_12§2]",
        citations=["Doc_12§2"],
        evidence_span="capacity is 50",
        status="verified",
        version=1,
    )
    claim2 = ClaimObject(
        claim_id="c2",
        leg_id="L2",
        text="Cancellation policy is 48 hours notice. [Doc_12§3]",
        citations=["Doc_12§3"],
        evidence_span="48 hours notice",
        status="verified",
        version=1,
    )
    state.answer = f"{claim1.text} {claim2.text}"
    state.claims = [claim1, claim2]
    state.citations = ["Doc_12§2", "Doc_12§3"]
    state.current_version = 1

    # User asks for presentation reformat
    turn_class = delta.classify_turn("Can you summarize this as bullet points?", state)
    assert turn_class == "presentation_only"

    new_ans, _claims, diff = delta.handle_presentation_only(state)
    assert "• Venue capacity" in new_ans
    assert "• Cancellation policy" in new_ans
    # Unchanged claims match exactly
    assert diff.unchanged == ["c1", "c2"]
    assert diff.changed == []
    assert diff.citations_added == []


def test_delta_engine_constraint_preserves_unaffected_claims_byte_identical() -> None:
    delta = DeltaEngine()
    store = SessionStore()
    state, _, _ = store.create_session("sec")

    # Initial Turn: two legs
    leg1 = Leg(
        leg_id="L1",
        text="venue capacity in Pune",
        entities=["Pune", "capacity"],
        first_dispatch_s=1.0,
    )
    leg2 = Leg(
        leg_id="L2",
        text="cancellation policy in Pune",
        entities=["Pune", "cancellation"],
        first_dispatch_s=1.0,
    )
    state.active_legs = {"L1": leg1, "L2": leg2}

    claim1 = ClaimObject(
        claim_id="c_L1",
        leg_id="L1",
        text="Venue capacity in Pune is 50 attendees. [Doc_12§2]",
        citations=["Doc_12§2"],
        evidence_span="capacity in Pune is 50",
        status="verified",
        version=1,
    )
    claim2 = ClaimObject(
        claim_id="c_L2",
        leg_id="L2",
        text="Cancellation policy requires 48 hours notice. [Doc_12§3]",
        citations=["Doc_12§3"],
        evidence_span="requires 48 hours notice",
        status="verified",
        version=1,
    )
    state.claims = [claim1, claim2]
    state.citations = ["Doc_12§2", "Doc_12§3"]
    state.answer = f"{claim1.text} {claim2.text}"
    state.current_version = 1

    # Late constraint modifying leg 1 (capacity constraint)
    late_input = "actually, the booking will be for 80 attendees"
    turn_class = delta.classify_turn(late_input, state)
    assert turn_class == "constraint_on_existing"

    affected_leg = delta.find_affected_leg(late_input, state)
    assert affected_leg is not None
    assert affected_leg.leg_id == "L1"

    # Delta retrieval mock
    delta_res = {"dense_results": [("Doc_14§1", 0.95)]}
    chunks_map = {
        "Doc_14§1": CorpusChunk(
            chunk_id="Doc_14§1",
            doc_id="Doc_14",
            section="1",
            title="Venues Large",
            text="Corporate Hall Beta can comfortably host up to 100 attendees.",
            char_start=0,
            char_end=64,
        )
    }

    _new_ans, final_claims, all_citations, diff = delta.apply_constraint_refinement(
        affected_leg, delta_res, chunks_map, state
    )

    assert len(final_claims) == 2
    # Affected claim L1 updated
    assert final_claims[0].leg_id == "L1"
    assert "Doc_14§1" in final_claims[0].citations

    # UNAFFECTED CLAIM L2 MUST BE STRICTLY BYTE-IDENTICAL (Gate G5 requirement)
    assert final_claims[1] is claim2
    assert final_claims[1].text == claim2.text
    assert final_claims[1].citations == claim2.citations

    # Diff captures the change correctly
    assert diff.changed == ["c_L1"]
    assert diff.unchanged == ["c_L2"]
    assert "Doc_14§1" in diff.citations_added
    assert "Doc_12§3" in all_citations
