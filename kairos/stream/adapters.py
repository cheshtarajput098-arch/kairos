"""Tolerant held-out transcript format adapter (SPEC §9.6a).

Converts four transcript formats into the canonical ReplayTranscript list:

  1. Native JSONL  — each line is a ReplayTranscript JSON object.
  2. Theme-guide Example 1 table (JSON object/list with keys ``t``, ``text``
     and optional ``session_id``, ``turn_id``, ``turn_type``, ``utterance_end``).
  3. Plain paragraph / raw text — whole text treated as one utterance, split
     at sentence boundaries with synthetic timestamps.
  4. Flat JSON object with a ``transcript`` string key — unwrapped then treated
     as raw text.

The adapter enforces no assumptions about corpus content.  It never imports
from ``data/`` or ``eval/``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from kairos.schemas import ReplayChunk, ReplayTranscript

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WORDS_PER_SECOND = 2.5  # used only for synthetic timestamp generation


def _synthetic_chunks(sentences: list[str]) -> tuple[list[ReplayChunk], float]:
    """Assign synthetic monotone timestamps to sentence chunks."""
    chunks: list[ReplayChunk] = []
    t = 0.0
    for sent in sentences:
        words = sent.split()
        chunks.append(ReplayChunk(t=round(t, 2), text=sent.strip()))
        t += max(len(words) / _WORDS_PER_SECOND, 0.4)
    utterance_end = round(t + 0.2, 2)
    return chunks, utterance_end


def _sentences_from_text(text: str) -> list[str]:
    """Split text into sentences; return non-empty ones."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


# ---------------------------------------------------------------------------
# Per-format parsers
# ---------------------------------------------------------------------------


def _parse_native_jsonl(lines: list[str]) -> list[ReplayTranscript] | None:
    """Try to parse lines as native JSONL (one ReplayTranscript per line)."""
    results: list[ReplayTranscript] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(obj, dict):
            return None
        # Must have at minimum chunks + utterance_end
        if "chunks" not in obj or "utterance_end" not in obj:
            return None
        # Fill required fields with defaults if missing
        obj.setdefault("session_id", "imported-session-1")
        obj.setdefault("turn_id", f"turn-{len(results) + 1}")
        obj.setdefault("turn_type", "single")
        try:
            results.append(ReplayTranscript.model_validate(obj))
        except Exception:  # noqa: BLE001
            return None
    return results if results else None


def _parse_theme_guide_table(data: Any) -> list[ReplayTranscript] | None:
    """Parse the theme-guide Example 1 format.

    Accepted shapes:
      - A list of ``{"t": float, "text": str}`` objects → one turn.
      - A dict with a ``"chunks"`` key → may also have turn metadata.
      - A dict with a ``"turns"`` key → list of turns.
    """
    if isinstance(data, list):
        # List of chunk objects
        if not data or not isinstance(data[0], dict) or "t" not in data[0]:
            return None
        chunks = [
            ReplayChunk(t=float(c["t"]), text=str(c.get("text", c.get("word", ""))))
            for c in data
            if "t" in c
        ]
        if not chunks:
            return None
        utterance_end = float(data[-1]["t"]) + 0.5
        return [
            ReplayTranscript(
                session_id="imported-session-1",
                turn_id="turn-1",
                turn_type="single",
                chunks=chunks,
                utterance_end=utterance_end,
            )
        ]

    if not isinstance(data, dict):
        return None

    # Shape: {"turns": [...]}
    if "turns" in data and isinstance(data["turns"], list):
        results: list[ReplayTranscript] = []
        for i, turn in enumerate(data["turns"]):
            sub = _parse_theme_guide_table(turn)
            if sub is None:
                return None
            # Renumber turns when multiple are present
            for t in sub:
                results.append(
                    t.model_copy(
                        update={
                            "session_id": data.get("session_id", "imported-session-1"),
                            "turn_id": turn.get("turn_id", f"turn-{i + 1}"),
                        }
                    )
                )
        return results or None

    # Shape: {"chunks": [...], optional metadata}
    if "chunks" in data and isinstance(data["chunks"], list):
        raw_chunks = data["chunks"]
        if raw_chunks and isinstance(raw_chunks[0], dict) and "t" in raw_chunks[0]:
            chunks = [
                ReplayChunk(
                    t=float(c["t"]),
                    text=str(c.get("text", c.get("word", ""))),
                    partial=c.get("partial"),
                    revises=c.get("revises"),
                )
                for c in raw_chunks
            ]
            ue = data.get("utterance_end", float(raw_chunks[-1]["t"]) + 0.5)
            return [
                ReplayTranscript(
                    session_id=str(data.get("session_id", "imported-session-1")),
                    turn_id=str(data.get("turn_id", "turn-1")),
                    turn_type=str(data.get("turn_type", "single")),  # type: ignore[arg-type]
                    chunks=chunks,
                    utterance_end=float(ue),
                )
            ]

    return None


def _parse_raw_text(text: str) -> list[ReplayTranscript]:
    """Treat the entire text as one utterance; split into sentences."""
    sentences = _sentences_from_text(text) or [text.strip()]
    chunks, utterance_end = _synthetic_chunks(sentences)
    return [
        ReplayTranscript(
            session_id="imported-session-1",
            turn_id="turn-1",
            turn_type="single",
            chunks=chunks,
            utterance_end=utterance_end,
        )
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def adapt_transcript_file(path: Path) -> list[ReplayTranscript]:
    """Load *path* and normalise it into a list of :class:`ReplayTranscript`.

    Tries four formats in order: native JSONL, theme-guide table, flat JSON
    with a ``transcript`` key, and finally raw text.  Falls back gracefully
    so that no format crashes the replay run.
    """
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    # 1. Native JSONL
    native = _parse_native_jsonl(lines)
    if native is not None:
        return native

    # 2. Try whole file as JSON (theme-guide table or flat object)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = None

    if data is not None:
        # 2a. flat {"transcript": "..."} wrapper
        if isinstance(data, dict) and "transcript" in data and isinstance(data["transcript"], str):
            data = data["transcript"]

        if isinstance(data, str):
            # treat as raw text
            return _parse_raw_text(data)

        tg = _parse_theme_guide_table(data)
        if tg is not None:
            return tg

    # 3. Raw text fallback
    return _parse_raw_text(raw)


def adapt_transcript_string(raw: str, session_id: str = "inline-session-1") -> list[ReplayTranscript]:
    """Adapt an in-memory raw transcript string (convenience wrapper)."""
    lines = raw.splitlines()
    native = _parse_native_jsonl(lines)
    if native is not None:
        return native
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and "transcript" in data and isinstance(data["transcript"], str):
            data = data["transcript"]
        if isinstance(data, str):
            return _parse_raw_text(data)
        tg = _parse_theme_guide_table(data)
        if tg is not None:
            return tg
    except json.JSONDecodeError:
        pass
    return _parse_raw_text(raw)
