"""Tests for resilience and failure-mode recovery (Step 13).

Covers:
1. Graceful shutdown cancelling in-flight tasks.
2. LLM provider outage falling back gracefully to Speed 1 extractive mode.
3. Index load failure keeping /v1/ready false (HTTP 503) with clear error logging.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kairos.api.app import app, lifespan
from kairos.grounding.gate import GroundingGate
from kairos.llm.provider import LLMProvider
from kairos.schemas import ClaimObject, CorpusChunk
from kairos.synth.rewrite import Speed2Synthesizer


def test_graceful_shutdown_cancels_active_tasks() -> None:
    """Verify that lifespan exit cancels all active in-flight tasks."""
    async def _run() -> None:
        test_app = FastAPI()

        # Enter lifespan
        async with lifespan(test_app):
            # Create a mock in-flight background task
            async def mock_background_job() -> None:
                await asyncio.sleep(100.0)

            task = asyncio.create_task(mock_background_job())
            test_app.state.active_tasks.add(task)
            assert not task.done()

        # After exiting the lifespan context, task must be cancelled
        assert task.done()
        assert task.cancelled()

    asyncio.run(_run())


def test_llm_outage_fallback_to_extractive() -> None:
    """Verify that an LLM failure falls back to extractive claims with telemetry."""
    # Mock LLM provider that raises an outage exception
    failing_provider = MagicMock(spec=LLMProvider)
    failing_provider.generate_json.side_effect = RuntimeError("Provider 503: Connection refused")

    gate = GroundingGate()
    synthesizer = Speed2Synthesizer(provider=failing_provider, gate=gate)

    speed1_claims = [
        ClaimObject(
            claim_id="C1",
            leg_id="L1",
            text="The conference hall seats 200 attendees. [Doc_12 §2]",
            citations=["Doc_12 §2"],
            evidence_span="The conference hall seats 200 attendees.",
            status="verified",
            version=1,
        )
    ]
    chunks_map = {
        "Doc_12 §2": CorpusChunk(
            doc_id="Doc_12",
            section="2",
            title="Venues",
            text="The conference hall seats 200 attendees.",
            chunk_id="Doc_12 §2",
            char_start=0,
            char_end=41,
        )
    }
    events_log: list[dict[str, Any]] = []

    # Run rewrite under simulated outage
    final_claims, metrics = synthesizer.rewrite_claims(
        speed1_claims, chunks_map, events_log=events_log
    )

    # Must preserve Speed 1 claim and citation byte-for-byte
    assert len(final_claims) == 1
    assert final_claims[0].text == speed1_claims[0].text
    assert final_claims[0].citations == ["Doc_12 §2"]

    # Metrics and events must clearly flag the outage and fallback
    assert metrics.get("llm_outage") is True
    assert metrics.get("fallback_to_extractive") is True
    assert any(e.get("event") == "llm_outage_fallback" for e in events_log)


def test_index_load_failure_keeps_ready_false(caplog: pytest.LogCaptureFixture) -> None:
    """Verify that index load failure returns HTTP 503 and logs clear error."""
    client = TestClient(app)

    # Health check must remain 200 ok
    health_resp = client.get("/v1/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"

    # Simulate an index failure during /v1/ready check
    with (
        caplog.at_level(logging.ERROR),
        patch("kairos.api.app.IndexStore.load", side_effect=OSError("Corrupt chunks.json file")),
    ):
        # Reset is_ready to simulate cold start or recheck
        app.state.is_ready = False
        ready_resp = client.get("/v1/ready")

        assert ready_resp.status_code == 503
        data = ready_resp.json()
        assert data["status"] == "not_ready"
        assert "Index load failed" in data["reason"]

        # Confirm clear log line
        assert any("Index load failed during readiness check" in record.message for record in caplog.records)
