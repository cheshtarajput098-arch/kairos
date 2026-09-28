"""Unit tests for CLI, LLM provider fallbacks, and security limits."""
from pathlib import Path

from pydantic import BaseModel

from kairos.cli import run_index, run_query, run_replay
from kairos.llm.provider import LLMProvider
from kairos.security.limits import validate_chunks_count, validate_message_size


class SampleSchema(BaseModel):
    query: str
    is_valid: bool
    count: int
    score: float
    items: list[str]
    meta: dict[str, str]


def test_llm_provider_fallback_dict() -> None:
    provider = LLMProvider("none")
    res = provider.generate_json(SampleSchema, [{"role": "user", "content": "test"}])
    assert res["query"] == ""
    assert res["is_valid"] is False
    assert res["count"] == 0
    assert res["score"] == 0.0
    assert res["items"] == []
    assert res["meta"] == {}


def test_security_limits_validation() -> None:
    assert validate_message_size(100) is True
    assert validate_message_size(100000) is False

    assert validate_chunks_count(10) is True
    assert validate_chunks_count(500) is False


def test_cli_execution_smoke(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    run_index(corpus_dir="data/corpus", index_dir=str(index_dir))
    assert (index_dir / "chunks.json").exists()

    run_query(query="Pune workshop venues", index_dir=str(index_dir))
    run_replay(split="demo", out_dir=str(tmp_path / "replay_out"))
    assert (tmp_path / "replay_out" / "replay_summary.json").exists()
