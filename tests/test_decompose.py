"""Unit tests for Stage 2 Multi-Intent Decomposer (SPEC §5).

Covers:
1. Generic disfluency normalisation (fillers, repetitions, self-repairs).
2. Rule-based clause splitter with context inheritance across compound queries.
3. Embedding-based candidate deduplication.
4. Hard sub-query cap.
5. Incremental diffing with stable leg IDs and reissuing only mutated/new legs.
6. Parallel retrieval dispatcher with concurrent execution and soft failure.
7. LLM decomposer with schema validation and clean offline fallback.
"""
from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock

from kairos.decompose.disfluency import DisfluencyNormalizer
from kairos.decompose.dispatcher import ParallelDispatcher
from kairos.decompose.llm_splitter import LLMDecomposer
from kairos.decompose.manager import DecompositionManager
from kairos.decompose.rule_splitter import RuleBasedSplitter
from kairos.schemas import Leg, SubQuery


def test_disfluency_fillers() -> None:
    normalizer = DisfluencyNormalizer()
    text = "Uh um what is the catering option like you know for the event"
    clean = normalizer.normalize(text)
    assert "uh" not in clean.lower()
    assert "um" not in clean.lower()
    assert "you know" not in clean.lower()
    assert "catering option" in clean


def test_disfluency_repetitions() -> None:
    normalizer = DisfluencyNormalizer()
    text = "What is the the capacity in in the room"
    clean = normalizer.normalize(text)
    assert "the the" not in clean.lower()
    assert "in in" not in clean.lower()
    assert clean.lower() == "what is the capacity in the room"


def test_disfluency_self_repairs() -> None:
    normalizer = DisfluencyNormalizer()

    # Repair with 'no'
    r1 = normalizer.normalize("venues in Pune — no, Mumbai for workshop")
    assert "Mumbai" in r1
    assert "Pune" not in r1

    # Repair with 'actually'
    r2 = normalizer.normalize("reserve for 20 people actually 30 people")
    assert "30 people" in r2
    assert "20 people" not in r2

    # Repair with 'sorry'
    r3 = normalizer.normalize("meeting on Monday, sorry, Tuesday")
    assert "Tuesday" in r3
    assert "Monday" not in r3


def test_rule_splitter_compound_context_inheritance() -> None:
    splitter = RuleBasedSplitter(max_legs=4)
    # Synthetic compound query adapted to enterprise venue corpus
    text = "What is the capacity of workshop venues in Pune, their catering options, and AV equipment details?"
    legs = splitter.split(text)

    assert len(legs) == 3
    assert legs[0].leg_id == "L1"
    assert legs[1].leg_id == "L2"
    assert legs[2].leg_id == "L3"

    # Verify context inheritance into L2 and L3
    assert "Pune" in legs[0].text
    assert "Pune" in legs[1].text
    assert "Pune" in legs[2].text
    assert "workshop venues" in legs[1].text or "catering options" in legs[1].text


def test_embedding_deduplication() -> None:
    mgr = DecompositionManager(mode="rule", dedupe_cosine=0.85)

    candidates = [
        SubQuery(leg_id="L1", text="capacity of workshop venues in Pune"),
        SubQuery(leg_id="L2", text="what is the capacity of workshop venues in Pune"),
        SubQuery(leg_id="L3", text="catering and dining options in Pune"),
    ]

    deduped = mgr._deduplicate_candidates(candidates)
    # The first two are near identical and should collapse into 1
    assert len(deduped) == 2
    assert "capacity" in deduped[0].text
    assert "catering" in deduped[1].text


def test_cap_enforced() -> None:
    splitter = RuleBasedSplitter(max_legs=4)
    text = "Venue capacity, and catering options, and parking spaces, and audio visual gear, and wifi speed, and breakout rooms"
    legs = splitter.split(text)
    assert len(legs) <= 4


def test_incremental_diffing_and_dispatcher() -> None:
    async def _test() -> None:
        mgr = DecompositionManager(mode="rule")

        # Step 1: initial prefix yields 2 legs
        legs_t1, reissued_t1 = mgr.decompose(
            "What is the capacity of workshop venues in Pune and catering options",
            t=1.0,
        )
        assert len(legs_t1) == 2
        assert set(reissued_t1) == {"L1", "L2"}
        assert legs_t1[0].leg_id == "L1"
        assert legs_t1[1].leg_id == "L2"

        # Mock retriever
        mock_retriever = MagicMock()
        retrieve_call_count = 0

        async def mock_retrieve_leg(query: str, deadline_override_ms: int | None = None) -> dict[str, Any]:
            nonlocal retrieve_call_count
            retrieve_call_count += 1
            await asyncio.sleep(0.01)
            return {
                "dense_results": [("doc_1", 0.9)],
                "sparse_results": [("doc_1", 5.0)],
                "latency_ms": 10.0,
                "status": "completed",
            }

        mock_retriever.retrieve_leg = mock_retrieve_leg

        dispatcher = ParallelDispatcher(mock_retriever)
        res_t1 = await dispatcher.dispatch_legs(legs_t1, reissued_t1)
        assert len(res_t1) == 2
        assert retrieve_call_count == 2

        # Step 2: incoming transcript chunk adds a third clause ("parking details")
        # L1 and L2 should remain stable and NOT be reissued
        legs_t2, reissued_t2 = mgr.decompose(
            "What is the capacity of workshop venues in Pune and catering options and parking details",
            t=2.0,
        )
        assert len(legs_t2) == 3
        assert reissued_t2 == ["L3"]
        assert legs_t2[0].first_dispatch_s == 1.0  # Stable timestamp
        assert legs_t2[1].first_dispatch_s == 1.0  # Stable timestamp
        assert legs_t2[2].first_dispatch_s == 2.0  # Newly added

        res_t2 = await dispatcher.dispatch_legs(legs_t2, reissued_t2)
        assert len(res_t2) == 1
        assert "L3" in res_t2
        # Total calls: 2 from t1 + 1 from t2 = 3
        assert retrieve_call_count == 3

    asyncio.run(_test())


def test_llm_decomposer_clean_fallback() -> None:
    mock_provider = MagicMock()
    # Provider fails with an error
    mock_provider.generate_json.side_effect = RuntimeError("LLM unavailable")

    decomposer = LLMDecomposer(provider=mock_provider)
    result = decomposer.decompose("What is the capacity of workshop venues in Pune and their catering options?")

    # Clean fallback to rule-based splitter
    assert len(result) >= 1
    assert any("Pune" in leg.text for leg in result)


def test_llm_decomposer_success() -> None:
    mock_provider = MagicMock()
    mock_provider.generate_json.return_value = {
        "sub_queries": [
            {"leg_id": "temp1", "text": "capacity of workshop venues in Pune", "entities": ["Pune", "venues"]},
            {"leg_id": "temp2", "text": "catering options for workshop venues in Pune", "entities": ["Pune", "catering"]},
        ],
    }

    decomposer = LLMDecomposer(provider=mock_provider)
    result = decomposer.decompose("What is the capacity and catering in Pune?")
    assert len(result) == 2
    assert result[0].leg_id == "L1"
    assert result[1].leg_id == "L2"
    assert result[0].text == "capacity of workshop venues in Pune"


def test_parallel_dispatcher_error_resilience() -> None:
    async def _test() -> None:
        mock_retriever = MagicMock()

        async def mock_retrieve_leg(query: str, deadline_override_ms: int | None = None) -> dict[str, Any]:
            if "error" in query:
                raise ValueError("Corpus connection failed")
            return {
                "dense_results": [("doc_1", 0.9)],
                "sparse_results": [],
                "latency_ms": 5.0,
                "status": "completed",
            }

        mock_retriever.retrieve_leg = mock_retrieve_leg

        dispatcher = ParallelDispatcher(mock_retriever)
        legs = [
            Leg(leg_id="L1", text="valid query", entities=[], first_dispatch_s=1.0),
            Leg(leg_id="L2", text="error query", entities=[], first_dispatch_s=1.0),
        ]

        results = await dispatcher.dispatch_legs(legs)
        assert len(results) == 2
        assert results["L1"]["status"] == "completed"
        assert results["L2"]["status"] == "error"
        assert results["L2"]["dense_results"] == []

    asyncio.run(_test())
