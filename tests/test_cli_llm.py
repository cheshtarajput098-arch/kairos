"""Unit tests for CLI, LLM provider fallbacks, and security limits."""

import sys
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from kairos.cli import main, run_index, run_query, run_replay
from kairos.llm.provider import LLMProvider
from kairos.security.limits import (
    validate_chunks_count,
    validate_message_size,
    validate_sessions_per_client,
    validate_tokens_count,
    validate_words_per_turn,
)


class SampleSchema(BaseModel):
    query: str
    is_valid: bool
    count: int
    score: float
    items: list[str]
    meta: dict[str, str]
    extra: Any | None = None


def test_llm_provider_fallback_dict() -> None:
    provider = LLMProvider("none")
    res = provider.generate_json(SampleSchema, [{"role": "user", "content": "test"}])
    assert res["query"] == ""
    assert res["is_valid"] is False
    assert res["count"] == 0
    assert res["score"] == 0.0
    assert res["items"] == []
    assert res["meta"] == {}
    assert res["extra"] is None


def test_llm_provider_external_types_fallback() -> None:
    for p_type in ["gemini", "openai_compatible", "ollama", "local"]:
        provider = LLMProvider(p_type, model_name="test-model")
        res = provider.generate_json(
            SampleSchema, [{"role": "user", "content": "hello"}], limits={"tokens": 100}
        )
        assert res["count"] == 0
        assert res["is_valid"] is False


def test_security_limits_validation() -> None:
    assert validate_message_size(100) is True
    assert validate_message_size(1000000) is False

    assert validate_chunks_count(10) is True
    assert validate_chunks_count(500) is False

    assert validate_words_per_turn(50) is True
    assert validate_words_per_turn(1000) is False

    assert validate_tokens_count(500) is True
    assert validate_tokens_count(50000) is False

    assert validate_sessions_per_client(2) is True
    assert validate_sessions_per_client(10) is False


def test_cli_execution_smoke(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    run_index(corpus_dir="data/corpus", index_dir=str(index_dir))
    assert (index_dir / "chunks.json").exists()

    run_query(query="Pune workshop venues", index_dir=str(index_dir))
    run_replay(split="demo", out_dir=str(tmp_path / "replay_out"))
    assert (tmp_path / "replay_out" / "replay_summary.json").exists()


def test_cli_main_dispatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    index_dir = tmp_path / "index_main"

    # Test main index
    monkeypatch.setattr(
        sys, "argv", ["kairos", "index", "--corpus", "data/corpus", "--index-dir", str(index_dir)]
    )
    main()
    assert (index_dir / "chunks.json").exists()

    # Test main query with positional
    monkeypatch.setattr(
        sys, "argv", ["kairos", "query", "workshop in Pune", "--index-dir", str(index_dir)]
    )
    main()

    # Test main query with --q
    monkeypatch.setattr(
        sys, "argv", ["kairos", "query", "--q", "workshop in Pune", "--index-dir", str(index_dir)]
    )
    main()

    # Test main query without query text exits
    monkeypatch.setattr(sys, "argv", ["kairos", "query", "--index-dir", str(index_dir)])
    with pytest.raises(SystemExit):
        main()

    # Test main no command exits
    monkeypatch.setattr(sys, "argv", ["kairos"])
    with pytest.raises(SystemExit):
        main()

    # Test replay non-existent file exits
    monkeypatch.setattr(
        sys, "argv", ["kairos", "replay", "--transcripts", "non_existent_path.jsonl"]
    )
    with pytest.raises(SystemExit):
        main()
