"""Tests for kairos/stream/adapters.py — format adapter (SPEC §9.6a).

Verifies that four transcript input formats are all correctly normalised
into ReplayTranscript objects with the right keys.  Tests are corpus-agnostic.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from kairos.schemas import ReplayTranscript
from kairos.stream.adapters import adapt_transcript_file, adapt_transcript_string

# ---------------------------------------------------------------------------
# Format 1: Native JSONL (one ReplayTranscript per line)
# ---------------------------------------------------------------------------

NATIVE_JSONL = textwrap.dedent("""\
    {"session_id": "s1", "turn_id": "t1", "turn_type": "single", "utterance_end": 3.0, "chunks": [{"t": 0.0, "text": "Hello world."}, {"t": 1.5, "text": "How are you?"}]}
    {"session_id": "s1", "turn_id": "t2", "turn_type": "late_constraint", "utterance_end": 5.0, "chunks": [{"t": 0.0, "text": "Actually for international trips."}]}
""")

# Theme-guide Example 1 table format (chunk list JSON)
THEME_GUIDE_CHUNKS = json.dumps(
    [{"t": 0.0, "text": "What is the venue capacity?"}, {"t": 1.2, "text": "In Pune."}]
)

# Flat JSON with transcript string
FLAT_TRANSCRIPT = json.dumps({"transcript": "This is a single sentence. And another one here."})

# Flat JSON with chunks and metadata (theme-guide dict shape)
THEME_GUIDE_DICT = json.dumps(
    {
        "session_id": "tg-s1",
        "turn_id": "tg-t1",
        "turn_type": "compound",
        "utterance_end": 4.5,
        "chunks": [
            {"t": 0.0, "text": "Venue for 50 people"},
            {"t": 1.5, "text": "and catering options."},
        ],
    }
)

# Raw plain text (no JSON at all)
RAW_TEXT = "Please summarize the reimbursement policy. Also include the approval steps."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_tmp(tmp_path: Path, content: str, name: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Tests for adapt_transcript_file
# ---------------------------------------------------------------------------


def test_native_jsonl_file(tmp_path: Path) -> None:
    p = _write_tmp(tmp_path, NATIVE_JSONL, "native.jsonl")
    turns = adapt_transcript_file(p)
    assert len(turns) == 2
    assert all(isinstance(t, ReplayTranscript) for t in turns)
    assert turns[0].turn_id == "t1"
    assert turns[1].turn_type == "late_constraint"
    assert len(turns[0].chunks) == 2


def test_theme_guide_chunk_list_file(tmp_path: Path) -> None:
    """A bare JSON array of {t, text} objects → one turn."""
    p = _write_tmp(tmp_path, THEME_GUIDE_CHUNKS, "theme_guide.json")
    turns = adapt_transcript_file(p)
    assert len(turns) == 1
    assert turns[0].turn_type == "single"
    assert len(turns[0].chunks) == 2
    assert turns[0].chunks[0].t == 0.0


def test_theme_guide_dict_file(tmp_path: Path) -> None:
    """A JSON dict with 'chunks' key and metadata."""
    p = _write_tmp(tmp_path, THEME_GUIDE_DICT, "tg_dict.json")
    turns = adapt_transcript_file(p)
    assert len(turns) == 1
    assert turns[0].session_id == "tg-s1"
    assert turns[0].turn_type == "compound"
    assert turns[0].utterance_end == pytest.approx(4.5)


def test_flat_transcript_key_file(tmp_path: Path) -> None:
    """Flat JSON object with a 'transcript' string key → raw text path."""
    p = _write_tmp(tmp_path, FLAT_TRANSCRIPT, "flat.json")
    turns = adapt_transcript_file(p)
    assert len(turns) == 1
    # Two sentences → should produce ≥1 chunk
    assert len(turns[0].chunks) >= 1
    assert turns[0].turn_type == "single"


def test_raw_text_file(tmp_path: Path) -> None:
    """Pure text file (no JSON) → synthetic chunks."""
    p = _write_tmp(tmp_path, RAW_TEXT, "raw.txt")
    turns = adapt_transcript_file(p)
    assert len(turns) == 1
    assert len(turns[0].chunks) >= 1
    # Timestamps must be monotone
    ts = [c.t for c in turns[0].chunks]
    assert ts == sorted(ts)


# ---------------------------------------------------------------------------
# Tests for adapt_transcript_string
# ---------------------------------------------------------------------------


def test_adapt_string_native_jsonl() -> None:
    turns = adapt_transcript_string(NATIVE_JSONL)
    assert len(turns) == 2
    assert turns[0].turn_id == "t1"


def test_adapt_string_raw() -> None:
    turns = adapt_transcript_string(RAW_TEXT)
    assert len(turns) == 1
    assert turns[0].utterance_end > 0


# ---------------------------------------------------------------------------
# Required key check — verifies the theme-guide's output record keys
# (SPEC §9.6a: test that replaying a transcript in the theme guide's own
# format produces a record with the guide's exact keys)
# ---------------------------------------------------------------------------

THEME_GUIDE_REQUIRED_KEYS = {
    "session_id",
    "turn_id",
    "turn_type",
    "utterance_end",
    "chunks",
}


def test_theme_guide_format_has_required_keys(tmp_path: Path) -> None:
    """Replaying a theme-guide transcript produces ReplayTranscript with required fields."""
    p = _write_tmp(tmp_path, THEME_GUIDE_DICT, "tg_keys.json")
    turns = adapt_transcript_file(p)
    assert len(turns) == 1
    t = turns[0]
    # Check all required keys are present via attribute access
    assert t.session_id
    assert t.turn_id
    assert t.turn_type
    assert t.utterance_end > 0
    assert len(t.chunks) > 0


def test_all_chunks_have_t_and_text(tmp_path: Path) -> None:
    """All chunks in output must have t (float) and text (str)."""
    for raw in (NATIVE_JSONL, THEME_GUIDE_CHUNKS, THEME_GUIDE_DICT, FLAT_TRANSCRIPT, RAW_TEXT):
        p = _write_tmp(tmp_path, raw, f"check_{hash(raw) % 9999}.txt")
        turns = adapt_transcript_file(p)
        for turn in turns:
            for chunk in turn.chunks:
                assert isinstance(chunk.t, float)
                assert isinstance(chunk.text, str)
                assert chunk.text.strip()
