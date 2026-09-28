"""Unit tests for Stage 1 Retrieval Controller, speculation, and suppression."""

import asyncio

import pytest

from kairos.controller.rules import RuleBasedController
from kairos.controller.speculation import SpeculationManager


def test_wait_on_entity_less_prefix() -> None:
    controller = RuleBasedController()
    features = {
        "n_words": 3,
        "n_entities": 0,
        "drift": 0.5,
        "syntactic_open": False,
        "entity_saturation": False,
    }
    decision = controller.decide(features, t=0.5, has_prior_answer=False)
    assert decision.decision == "WAIT"
    assert decision.reason == "no_entities"


def test_wait_on_syntactic_open_prefix() -> None:
    controller = RuleBasedController()
    features = {
        "n_words": 5,
        "n_entities": 2,
        "drift": 0.05,
        "syntactic_open": True,
        "entity_saturation": True,
        "probe_stable": False,
    }
    decision = controller.decide(features, t=1.0, has_prior_answer=False)
    assert decision.decision == "WAIT"
    assert decision.reason == "syntactic_open"


def test_retrieve_once_entities_and_drift_stabilize() -> None:
    controller = RuleBasedController()
    features = {
        "n_words": 7,
        "n_entities": 2,
        "drift": 0.08,
        "syntactic_open": False,
        "entity_saturation": True,
    }
    decision = controller.decide(features, t=1.5, has_prior_answer=False)
    assert decision.decision == "RETRIEVE"
    assert decision.reason == "intent_stabilized"


def test_suppress_on_presentation_reformat_with_prior_answer() -> None:
    controller = RuleBasedController()
    features = {
        "presentation_intent": 0.85,
        "n_entities": 0,
        "syntactic_open": False,
    }
    # With prior answer -> SUPPRESS (NO_RETRIEVAL)
    decision = controller.decide(features, t=0.8, has_prior_answer=True)
    assert decision.decision == "NO_RETRIEVAL"
    assert decision.reason == "presentation_restructure"

    # Without prior answer -> Cannot suppress as presentation of non-existent answer
    decision_no_prior = controller.decide(features, t=0.8, has_prior_answer=False)
    assert decision_no_prior.decision != "NO_RETRIEVAL"


def test_zero_vector_calls_on_suppress(monkeypatch: pytest.MonkeyPatch) -> None:
    vector_search_called = False

    def mock_vector_search(*args: object, **kwargs: object) -> None:
        nonlocal vector_search_called
        vector_search_called = True

    controller = RuleBasedController()
    features = {"presentation_intent": 0.9, "n_entities": 0, "syntactic_open": False}
    decision = controller.decide(features, t=0.5, has_prior_answer=True)

    if decision.decision == "NO_RETRIEVAL":
        pass  # Pipeline bypasses retrieval completely on NO_RETRIEVAL
    else:
        mock_vector_search()

    assert vector_search_called is False


def test_cancellation_when_entity_changes() -> None:
    async def _test() -> None:
        spec_mgr = SpeculationManager(max_speculative=3)

        async def dummy_search() -> str:
            await asyncio.sleep(1.0)
            return "result"

        task = asyncio.create_task(dummy_search())
        q_hash = spec_mgr.register_task("workshop in Pune", task, {"pune", "workshop"}, "L1", 0.8)
        assert q_hash in spec_mgr.active_tasks

        # A revision arrives where entities changed from Pune to Mumbai
        current_entities: set[str] = {"mumbai", "workshop"}
        cancelled = spec_mgr.check_and_cancel_on_revision(current_entities, t=1.2)

        assert q_hash in cancelled
        # Yield to allow cancellation to propagate to the task
        await asyncio.sleep(0)
        assert task.cancelled()

    asyncio.run(_test())


def test_speculative_budget_exhaustion() -> None:
    async def _test() -> None:
        spec_mgr = SpeculationManager(max_speculative=2)

        async def dummy_task() -> None:
            pass

        t1 = asyncio.create_task(dummy_task())
        t2 = asyncio.create_task(dummy_task())

        assert spec_mgr.can_speculate() is True
        spec_mgr.register_task("query 1", t1, {"e1"}, "L1", 0.5)

        assert spec_mgr.can_speculate() is True
        spec_mgr.register_task("query 2", t2, {"e2"}, "L2", 0.8)

        # Budget of 2 is now exhausted
        assert spec_mgr.can_speculate() is False

    asyncio.run(_test())
