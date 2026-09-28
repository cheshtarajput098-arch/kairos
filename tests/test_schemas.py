"""Unit tests for Pydantic v2 strict schemas (SPEC §2)."""

import pytest
from pydantic import ValidationError

from kairos.schemas import (
    CorpusChunk,
    ErrorDetail,
    ErrorEnvelope,
    ReplayTranscript,
)


def test_corpus_chunk_valid() -> None:
    chunk = CorpusChunk(
        chunk_id="Doc_12§2",
        doc_id="Doc_12",
        section="2",
        title="Workshop Venues",
        text="Sample text content",
        char_start=0,
        char_end=17,
    )
    assert chunk.chunk_id == "Doc_12§2"


def test_extra_fields_rejected() -> None:
    with pytest.raises(ValidationError):
        CorpusChunk(
            chunk_id="Doc_12§2",
            doc_id="Doc_12",
            section="2",
            title="Title",
            text="Text",
            char_start=0,
            char_end=4,
            unknown_extra_field="invalid",
        )


def test_replay_transcript_roundtrip() -> None:
    t_dict = {
        "session_id": "s01",
        "turn_id": "t1",
        "turn_type": "compound",
        "scenario": "Test scenario",
        "chunks": [{"t": 0.0, "text": "Hello world"}],
        "utterance_end": 1.5,
    }
    transcript = ReplayTranscript.model_validate(t_dict)
    assert transcript.session_id == "s01"
    assert transcript.chunks[0].text == "Hello world"
    assert transcript.model_dump(exclude_none=True) == t_dict


def test_error_envelope_schema() -> None:
    envelope = ErrorEnvelope(
        error=ErrorDetail(
            code="INVALID_INPUT",
            message="Payload too large",
            request_id="req-12345",
        )
    )
    dumped = envelope.model_dump()
    assert dumped["error"]["code"] == "INVALID_INPUT"
    assert dumped["error"]["request_id"] == "req-12345"
