"""Hypothesis Property-Based Fuzzing Tests (SPEC §13.3, §13.4, Tier 4).

Fuzzes:
1. Input text sanitization with arbitrary Unicode, control characters, and zero-width spaces.
2. WebSocket message parser against malformed payloads and schema variations.
3. Extractive text chunking and sentence boundary splitting.
4. Circuit breaker state machine transitions.
"""

from __future__ import annotations

from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from kairos.llm.local import CircuitBreaker
from kairos.schemas import StreamInputChunk
from kairos.security.sanitizer import sanitize_input_text
from kairos.synth.extractive import _split_into_sentences


@settings(max_examples=100, deadline=None)
@given(text=st.text(min_size=0, max_size=2000), max_chars=st.one_of(st.none(), st.integers(min_value=1, max_value=500)))
def test_fuzz_sanitize_input_text(text: str, max_chars: int | None) -> None:
    """Property test: sanitizer never crashes and satisfies security invariants."""
    cleaned = sanitize_input_text(text, max_chars=max_chars)

    assert isinstance(cleaned, str)

    # Invariant 1: No zero-width characters remain
    assert "\u200B" not in cleaned
    assert "\u200C" not in cleaned
    assert "\u200D" not in cleaned
    assert "\uFEFF" not in cleaned

    # Invariant 2: No non-printable control characters remain
    assert "\x00" not in cleaned
    assert "\x01" not in cleaned
    assert "\x08" not in cleaned

    # Invariant 3: Spotlight and script delimiters neutralized
    assert "<untrusted_corpus" not in cleaned
    assert "</untrusted_corpus>" not in cleaned
    assert "<script" not in cleaned
    assert "</script>" not in cleaned

    # Invariant 4: Length bound holds if specified
    if max_chars is not None:
        assert len(cleaned) <= max_chars


@settings(max_examples=100, deadline=None)
@given(payload=st.dictionaries(keys=st.text(min_size=1, max_size=20), values=st.text(max_size=50), max_size=10))
def test_fuzz_stream_input_chunk_parsing(payload: dict[str, Any]) -> None:
    """Property test: Pydantic parsing never throws unhandled errors on arbitrary payloads."""
    try:
        chunk = StreamInputChunk.model_validate(payload)
        # If it passed validation, it must have valid t and text
        assert isinstance(chunk.t, float)
        assert isinstance(chunk.text, str)
        assert isinstance(chunk.is_final, bool)
    except ValidationError:
        # Expected: strict validation rejects extra or invalid fields safely
        pass


@settings(max_examples=100, deadline=None)
@given(text=st.text(min_size=0, max_size=1000))
def test_fuzz_sentence_splitter(text: str) -> None:
    """Property test: sentence splitter handles arbitrary strings safely."""
    sentences = _split_into_sentences(text)
    assert isinstance(sentences, list)
    for s in sentences:
        assert isinstance(s, str)
        assert not s.startswith("##")


@settings(max_examples=50, deadline=None)
@given(actions=st.lists(st.booleans(), min_size=1, max_size=50))
def test_fuzz_circuit_breaker_state_machine(actions: list[bool]) -> None:
    """Property test: circuit breaker state machine transitions deterministically."""
    cb = CircuitBreaker(failures_to_open=3, reset_after_s=30.0)

    for is_success in actions:
        if cb.can_execute():
            if is_success:
                cb.record_success()
                assert cb.state == "CLOSED"
                assert cb.consecutive_failures == 0
            else:
                cb.record_failure()
                if cb.consecutive_failures >= 3:
                    assert cb.state == "OPEN"
