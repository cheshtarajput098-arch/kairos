"""Unit tests for Stage 5 Speed-2 Grounded Rewrite and GroundingGate validation (SPEC §6.2)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from kairos.grounding.gate import GroundingGate
from kairos.llm.provider import LLMProvider
from kairos.schemas import ClaimObject, CorpusChunk, RewriteResponse, RewrittenClaim
from kairos.synth.rewrite import Speed2Synthesizer


class MockLLMProvider(LLMProvider):
    def __init__(self, response_data: dict[str, Any]) -> None:
        super().__init__(provider_type="mock")
        self.response_data = response_data

    def generate_json(
        self,
        schema: type[BaseModel],
        messages: list[dict[str, str]],
        limits: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.response_data


def _sample_chunks_map() -> dict[str, CorpusChunk]:
    return {
        "Doc_12§2": CorpusChunk(
            chunk_id="Doc_12§2",
            doc_id="Doc_12",
            section="2",
            title="Veloria Office Locations",
            text=(
                "Veloria Systems maintains a regional development center in Pune, Maharashtra. "
                "The facility accommodates 450 engineers working on cloud infrastructure and AI systems."
            ),
            char_start=0,
            char_end=180,
        )
    }


def test_rewrite_accepted_preserves_citations() -> None:
    chunks_map = _sample_chunks_map()
    gate = GroundingGate()

    # Speed-1 extractive claim
    s1_claim = ClaimObject(
        claim_id="c_L1",
        leg_id="L1",
        text="The facility accommodates 450 engineers [Doc_12§2]",
        citations=["Doc_12§2"],
        evidence_span="The facility accommodates 450 engineers",
        status="verified",
        version=1,
    )

    # Mock LLM returning fluent rewrite with verbatim evidence span from Doc_12§2
    mock_response = RewriteResponse(
        rewritten_claims=[
            RewrittenClaim(
                claim_id="c_L1",
                text="The Pune facility employs 450 engineers focusing on cloud systems.",
                evidence_span="The facility accommodates 450 engineers",
            )
        ]
    ).model_dump()

    provider = MockLLMProvider(mock_response)
    synth = Speed2Synthesizer(provider=provider, gate=gate)

    events: list[dict[str, Any]] = []
    final_claims, metrics = synth.rewrite_claims([s1_claim], chunks_map, events_log=events)

    assert len(final_claims) == 1
    rewritten = final_claims[0]

    # Content is rewritten
    assert "Pune facility employs 450 engineers" in rewritten.text
    # Citations are byte-identical to Speed-1 claim
    assert rewritten.citations == ["Doc_12§2"]
    assert rewritten.claim_id == "c_L1"
    assert rewritten.evidence_span == "The facility accommodates 450 engineers"
    assert rewritten.status == "verified"

    # Metrics and events
    assert metrics["rewrites_accepted"] == 1
    assert metrics["rewrites_rejected"] == 0
    assert metrics["rewrite_pass_rate"] == 1.0
    assert any(e["event"] == "rewrite_accepted" and e["claim_id"] == "c_L1" for e in events)


def test_rewrite_rejected_on_paraphrased_span_keeps_speed1() -> None:
    chunks_map = _sample_chunks_map()
    gate = GroundingGate()

    s1_claim = ClaimObject(
        claim_id="c_L1",
        leg_id="L1",
        text="Veloria Systems maintains a regional development center in Pune [Doc_12§2]",
        citations=["Doc_12§2"],
        evidence_span="Veloria Systems maintains a regional development center in Pune",
        status="verified",
        version=1,
    )

    # Candidate with paraphrased, non-verbatim span not found in Doc_12§2
    mock_response = RewriteResponse(
        rewritten_claims=[
            RewrittenClaim(
                claim_id="c_L1",
                text="Veloria has an engineering hub in Pune.",
                evidence_span="Veloria has a huge office in Pune with many people",  # Not in chunk
            )
        ]
    ).model_dump()

    provider = MockLLMProvider(mock_response)
    synth = Speed2Synthesizer(provider=provider, gate=gate)

    events: list[dict[str, Any]] = []
    final_claims, metrics = synth.rewrite_claims([s1_claim], chunks_map, events_log=events)

    assert len(final_claims) == 1
    result_claim = final_claims[0]

    # Candidate was rejected; Speed 1 claim is retained byte-for-byte!
    assert result_claim.text == s1_claim.text
    assert result_claim.evidence_span == s1_claim.evidence_span
    assert result_claim.citations == s1_claim.citations

    # Metrics and events
    assert metrics["rewrites_accepted"] == 0
    assert metrics["rewrites_rejected"] == 1
    assert metrics["rewrite_pass_rate"] == 0.0
    assert any(e["event"] == "rewrite_rejected" and e["claim_id"] == "c_L1" for e in events)


def test_rewrite_rejected_on_fabricated_id_keeps_speed1() -> None:
    chunks_map = _sample_chunks_map()
    gate = GroundingGate()

    # Speed-1 claim with unknown/fabricated citation in retrieval set
    s1_claim = ClaimObject(
        claim_id="c_L1",
        leg_id="L1",
        text="Invalid claim [Doc_99§9]",
        citations=["Doc_99§9"],
        evidence_span="Invalid span",
        status="verified",
        version=1,
    )

    mock_response = RewriteResponse(
        rewritten_claims=[
            RewrittenClaim(
                claim_id="c_L1",
                text="Fabricated citation rewrite.",
                evidence_span="Invalid span",
            )
        ]
    ).model_dump()

    provider = MockLLMProvider(mock_response)
    synth = Speed2Synthesizer(provider=provider, gate=gate)

    events: list[dict[str, Any]] = []
    final_claims, metrics = synth.rewrite_claims([s1_claim], chunks_map, events_log=events)

    assert len(final_claims) == 1
    # Speed 1 claim is retained
    assert final_claims[0].text == s1_claim.text
    assert metrics["rewrites_rejected"] == 1
    assert any(e["event"] == "rewrite_rejected" for e in events)


def test_rewrite_fallback_when_model_missing_leaves_speed1_intact() -> None:
    chunks_map = _sample_chunks_map()
    gate = GroundingGate()

    s1_claim = ClaimObject(
        claim_id="c_L1",
        leg_id="L1",
        text="The facility accommodates 450 engineers [Doc_12§2]",
        citations=["Doc_12§2"],
        evidence_span="The facility accommodates 450 engineers",
        status="verified",
        version=1,
    )

    # Offline empty provider
    provider = LLMProvider(provider_type="none")
    synth = Speed2Synthesizer(provider=provider, gate=gate)

    final_claims, metrics = synth.rewrite_claims([s1_claim], chunks_map)
    assert len(final_claims) == 1
    assert final_claims[0].text == s1_claim.text
    assert metrics["rewrites_attempted"] == 0
    assert metrics["rewrite_pass_rate"] == 1.0
