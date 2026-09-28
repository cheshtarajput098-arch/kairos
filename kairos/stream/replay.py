"""Transcript replay reader with virtual clock, cadence scaling, and partial revisions (SPEC §2.2, §4)."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator
from pathlib import Path

from kairos.config import load_config
from kairos.schemas import ReplayChunk, ReplayTranscript


class ReplayEvent:
    def __init__(
        self,
        event_type: str,
        t: float,
        text: str,
        prefix: str,
        chunk_index: int,
        is_revised: bool = False,
        raw_chunk: ReplayChunk | None = None,
    ):
        self.event_type = event_type
        self.t = t
        self.text = text
        self.prefix = prefix
        self.chunk_index = chunk_index
        self.is_revised = is_revised
        self.raw_chunk = raw_chunk


class ReplayReader:
    def __init__(
        self,
        transcript: ReplayTranscript,
        cadence: float = 1.0,
        instant: bool = False,
    ):
        self.transcript = transcript
        self.cadence = cadence
        self.instant = instant
        self.settings = load_config()

    @classmethod
    def from_jsonl(
        cls, file_path: Path, cadence: float = 1.0, instant: bool = False
    ) -> list[ReplayReader]:
        """Read all turns from a JSONL file."""
        readers: list[ReplayReader] = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                transcript = ReplayTranscript.model_validate(data)
                readers.append(cls(transcript, cadence=cadence, instant=instant))
        return readers

    async def stream_events(self) -> AsyncGenerator[ReplayEvent, None]:
        """Stream replay events over a virtual clock."""
        chunks = self.transcript.chunks[: self.settings.security.max_chunks_per_turn]
        chunks_history: list[str] = []
        last_t = 0.0

        for idx, chunk in enumerate(chunks):
            # Virtual clock delay scaled by cadence
            if not self.instant:
                delay = (chunk.t - last_t) * (1.0 / self.cadence)
                if delay > 0:
                    await asyncio.sleep(delay)
                last_t = chunk.t

            is_revision = False
            if chunk.revises is not None and 0 <= chunk.revises < len(chunks_history):
                # Partial revision: replace earlier chunk
                chunks_history[chunk.revises] = chunk.text
                is_revision = True
            else:
                chunks_history.append(chunk.text)

            prefix = " ".join(chunks_history).strip()

            # Enforce max words per turn limit
            words = prefix.split()
            if len(words) > self.settings.security.max_words_per_turn:
                prefix = " ".join(words[: self.settings.security.max_words_per_turn])

            event_type = "transcript_revised" if is_revision else "chunk_received"
            yield ReplayEvent(
                event_type=event_type,
                t=chunk.t,
                text=chunk.text,
                prefix=prefix,
                chunk_index=idx,
                is_revised=is_revision,
                raw_chunk=chunk,
            )

        # Final utterance end event
        if not self.instant:
            delay = (self.transcript.utterance_end - last_t) * (1.0 / self.cadence)
            if delay > 0:
                await asyncio.sleep(delay)

        yield ReplayEvent(
            event_type="utterance_end",
            t=self.transcript.utterance_end,
            text="",
            prefix=" ".join(chunks_history).strip(),
            chunk_index=len(chunks),
        )
