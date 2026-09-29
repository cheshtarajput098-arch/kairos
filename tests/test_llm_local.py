"""Unit tests for Local GGUF LLM and Circuit Breaker (SPEC §1, §6.2)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from kairos.llm.local import CircuitBreaker, LocalLLM


class DummySchema(BaseModel):
    title: str
    count: int
    tags: list[str]


def test_circuit_breaker_transitions() -> None:
    cb = CircuitBreaker(failures_to_open=3, reset_after_s=0.1)
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # First failure
    cb.record_failure()
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # Second failure
    cb.record_failure()
    assert cb.state == "CLOSED"
    assert cb.can_execute() is True

    # Third failure -> trips to OPEN
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.can_execute() is False

    # Immediate check in OPEN rejects execution
    assert cb.can_execute() is False

    # Wait for reset period
    time.sleep(0.15)
    # Should transition to HALF_OPEN to probe
    assert cb.can_execute() is True
    assert cb.state == "HALF_OPEN"

    # Successful probe recovers to CLOSED
    cb.record_success()
    assert cb.state == "CLOSED"
    assert cb.consecutive_failures == 0


def test_circuit_breaker_probe_failure_re_opens() -> None:
    cb = CircuitBreaker(failures_to_open=2, reset_after_s=0.05)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "OPEN"

    time.sleep(0.08)
    assert cb.can_execute() is True
    assert cb.state == "HALF_OPEN"

    # Failed probe trips back to OPEN
    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.can_execute() is False


def test_local_llm_fallback_when_model_missing() -> None:
    # Point to nonexistent model file
    fake_path = Path("models/nonexistent_model.gguf")
    llm = LocalLLM(model_path=fake_path)

    assert llm.is_available() is False

    # Should return valid default fallback conforming to schema without raising error
    result = llm.generate_json(DummySchema, [{"role": "user", "content": "hello"}])
    assert isinstance(result, dict)
    assert result["title"] == ""
    assert result["count"] == 0
    assert result["tags"] == []

    # Circuit breaker remains CLOSED because missing model is an expected offline fallback condition
    assert llm.circuit_breaker.state == "CLOSED"


def test_local_llm_extract_json_formatting() -> None:
    llm = LocalLLM()

    # Raw JSON
    raw = '{"key": "value", "num": 42}'
    parsed = llm._extract_json(raw)
    assert parsed == {"key": "value", "num": 42}

    # Markdown code fenced JSON
    fenced = '```json\n{"key": "value", "num": 42}\n```'
    parsed_fenced = llm._extract_json(fenced)
    assert parsed_fenced == {"key": "value", "num": 42}

    # Text preamble and trailing text
    messy = 'Here is your structured JSON output:\n```json\n{"key": "value"}\n```\nHope this helps!'
    parsed_messy = llm._extract_json(messy)
    assert parsed_messy == {"key": "value"}


def test_local_llm_trips_circuit_breaker_on_repeated_crashes(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_path = Path("fake_model.gguf")
    llm = LocalLLM(model_path=fake_path, failures_to_open=3, reset_after_s=10.0)

    # Mock _ensure_loaded to pretend model is loaded
    monkeypatch.setattr(llm, "_ensure_loaded", lambda: True)

    class CrashingMockLLM:
        def create_chat_completion(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("Fatal internal inference crash")

    llm._llm = CrashingMockLLM()

    # Call 1
    llm.generate_json(DummySchema, [])
    assert llm.circuit_breaker.state == "CLOSED"
    assert llm.circuit_breaker.consecutive_failures == 1

    # Call 2
    llm.generate_json(DummySchema, [])
    assert llm.circuit_breaker.state == "CLOSED"
    assert llm.circuit_breaker.consecutive_failures == 2

    # Call 3 -> Tripped to OPEN
    llm.generate_json(DummySchema, [])
    assert llm.circuit_breaker.state == "OPEN"

    # Call 4 is fast-rejected by OPEN circuit breaker
    res = llm.generate_json(DummySchema, [])
    assert res["title"] == ""
