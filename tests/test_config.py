"""Unit tests for Kairos configuration & Settings loader."""

import pytest

from kairos.config import load_config


def test_load_config_defaults() -> None:
    settings = load_config()
    assert settings.app.env == "dev"
    assert settings.app.port == 8000
    assert settings.security.max_message_bytes == 4096
    assert settings.telemetry.log_text is False


def test_load_config_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAIROS_ENV", "prod")
    monkeypatch.setenv("KAIROS_TOKEN_SECRET", "super-secret-token")
    settings = load_config()
    assert settings.app.env == "prod"
    assert settings.token_secret == "super-secret-token"


def test_tbd_cleaning_handling() -> None:
    settings = load_config()
    # Optional model fields marked as TBD in default.yaml should clean to None
    assert settings.models.embedding.revision is None
    assert settings.models.reranker.revision is None
    assert settings.models.local_llm.gguf_file == "models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
