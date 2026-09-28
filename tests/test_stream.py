"""Unit tests for transcript stream reader, virtual clock, and partial revisions."""
import asyncio

import pytest

from kairos.schemas import ReplayChunk, ReplayTranscript
from kairos.stream.replay import ReplayEvent, ReplayReader


def test_instant_replay_streaming() -> None:
    transcript = ReplayTranscript(
        session_id="s1",
        turn_id="t1",
        turn_type="single",
        chunks=[
            ReplayChunk(t=0.0, text="First chunk"),
            ReplayChunk(t=1.0, text="second chunk"),
        ],
        utterance_end=1.5,
    )
    reader = ReplayReader(transcript, instant=True)

    events: list[ReplayEvent] = []
    async def _run() -> None:
        async for ev in reader.stream_events():
            events.append(ev)

    asyncio.run(_run())
    assert len(events) == 3  # 2 chunks + 1 utterance_end
    assert events[0].prefix == "First chunk"
    assert events[1].prefix == "First chunk second chunk"
    assert events[2].event_type == "utterance_end"


def test_partial_revision_handling() -> None:
    transcript = ReplayTranscript(
        session_id="s1",
        turn_id="t1",
        turn_type="single",
        chunks=[
            ReplayChunk(t=0.0, text="in Pune for thirty", partial=True),
            ReplayChunk(t=0.8, text="in Pune for 30 people", revises=0),
            ReplayChunk(t=1.6, text="with catering"),
        ],
        utterance_end=2.0,
    )
    reader = ReplayReader(transcript, instant=True)

    events: list[ReplayEvent] = []
    async def _run() -> None:
        async for ev in reader.stream_events():
            events.append(ev)

    asyncio.run(_run())
    assert events[0].is_revised is False
    assert events[0].prefix == "in Pune for thirty"

    # Second event should revise chunk 0
    assert events[1].is_revised is True
    assert events[1].event_type == "transcript_revised"
    assert events[1].prefix == "in Pune for 30 people"

    assert events[2].prefix == "in Pune for 30 people with catering"


def test_limits_enforced_from_config(monkeypatch: pytest.MonkeyPatch) -> None:
    # Test max words enforcement
    transcript = ReplayTranscript(
        session_id="s1",
        turn_id="t1",
        turn_type="single",
        chunks=[
            ReplayChunk(t=0.0, text="word " * 500),
        ],
        utterance_end=1.0,
    )
    reader = ReplayReader(transcript, instant=True)
    events: list[ReplayEvent] = []
    async def _run() -> None:
        async for ev in reader.stream_events():
            events.append(ev)

    asyncio.run(_run())
    words = events[0].prefix.split()
    assert len(words) <= 400
