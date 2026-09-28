"""Typed Pydantic Settings loader for Kairos configuration.

Validates config/default.yaml and environment variable overrides at startup.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    env: Literal["dev", "prod"] = "dev"
    host: str = "0.0.0.0"  # nosec B104
    port: int = 8000
    runs_dir: Path = Path("runs")
    index_dir: Path = Path("index")
    corpus_dir: Path = Path("data/corpus")
    seed: int = 42


class EmbeddingModelConfig(BaseModel):
    name: str = "BAAI/bge-small-en-v1.5"
    revision: str | None = None
    sha256: str | None = None
    dim: int = 384


class RerankerModelConfig(BaseModel):
    enabled: bool = False
    name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    revision: str | None = None


class NLIModelConfig(BaseModel):
    enabled: bool = False
    name: str | None = None
    threshold: float = 0.5


class LocalLLMModelConfig(BaseModel):
    enabled: bool = True
    gguf_file: str | None = None
    sha256: str | None = None
    n_threads: int = 4
    context_tokens: int = 4096
    max_output_tokens: int = 256
    temperature: float = 0.0


class ControllerClassifierConfig(BaseModel):
    arm: Literal["rule", "model"] = "rule"
    model_file: str | None = None


class ModelsConfig(BaseModel):
    embedding: EmbeddingModelConfig = Field(default_factory=EmbeddingModelConfig)
    reranker: RerankerModelConfig = Field(default_factory=RerankerModelConfig)
    nli: NLIModelConfig = Field(default_factory=NLIModelConfig)
    local_llm: LocalLLMModelConfig = Field(default_factory=LocalLLMModelConfig)
    controller_classifier: ControllerClassifierConfig = Field(
        default_factory=ControllerClassifierConfig
    )


class ProbeConfig(BaseModel):
    enabled: bool = True
    top_k: int = 3


class ControllerConfig(BaseModel):
    drift_threshold: float = 0.15
    stable_chunks: int = 2
    min_entities: int = 1
    probe: ProbeConfig = Field(default_factory=ProbeConfig)
    presentation_intent_threshold: float = 0.7
    max_speculative_retrievals: int = 3


class DisfluencyConfig(BaseModel):
    fillers: list[str] = Field(default_factory=lambda: ["uh", "um", "erm", "hmm", "like"])
    repair_cues: list[str] = Field(default_factory=lambda: ["no", "sorry", "actually", "wait"])


class DecomposerConfig(BaseModel):
    mode: Literal["rule", "llm"] = "rule"
    max_legs: int = 4
    dedupe_cosine: float = 0.9
    llm_deadline_ms: int = 600
    disfluency: DisfluencyConfig = Field(default_factory=DisfluencyConfig)
    gold_match_cosine: float = 0.6


class RetrievalCacheConfig(BaseModel):
    enabled: bool = True
    max_entries: int = 1024


class RetrievalConfig(BaseModel):
    deadline_ms: int = 400
    top_k_dense: int = 20
    top_k_sparse: int = 20
    cache: RetrievalCacheConfig = Field(default_factory=RetrievalCacheConfig)


class FusionConfig(BaseModel):
    rrf_k: int = 60
    top_n: int = 8
    near_dup_cosine: float = 0.95
    conflict_check: bool = True


class CircuitBreakerConfig(BaseModel):
    failures_to_open: int = 3
    reset_after_s: int = 30


class Speed2Config(BaseModel):
    enabled: bool = True
    provider: Literal["local", "gemini", "openai_compatible", "ollama", "none"] = "local"
    deadline_ms: int = 2500
    run_policy: Literal["after_draft", "after_utterance_end", "off"] = "after_draft"
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)


class SynthesisConfig(BaseModel):
    speed2: Speed2Config = Field(default_factory=Speed2Config)
    max_evidence_span_words: int = 30


class DraftingConfig(BaseModel):
    enabled: bool = True
    max_rollbacks_per_turn: int = 3


class GroundingConfig(BaseModel):
    span_fuzzy_ratio: float = 0.9
    nli_async: bool = True


class SessionDeltaConfig(BaseModel):
    constraint_similarity: float = 0.55
    new_topic_similarity: float = 0.35
    cues: list[str] = Field(default_factory=lambda: ["actually", "also", "instead", "but"])


class SessionConfig(BaseModel):
    ttl_s: int = 1800
    max_sessions: int = 200
    delta: SessionDeltaConfig = Field(default_factory=SessionDeltaConfig)


class TelemetryConfig(BaseModel):
    jsonl: bool = True
    otlp_endpoint: str = "http://jaeger:4318"
    log_text: bool = False
    redact: list[str] = Field(default_factory=lambda: ["email", "phone", "card"])
    overhead_target_pct: float = 2.0


class RateLimitConfig(BaseModel):
    http_per_min: int = 120
    ws_messages_per_min: int = 600


class WSConfig(BaseModel):
    idle_timeout_s: int = 120
    max_connection_s: int = 3600
    queue_size: int = 256


class SecurityConfig(BaseModel):
    token_ttl_s: int = 3600
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:8000", "http://127.0.0.1:8000"]
    )
    max_message_bytes: int = 4096
    max_chunks_per_turn: int = 200
    max_words_per_turn: int = 400
    max_sessions_per_client: int = 5
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    ws: WSConfig = Field(default_factory=WSConfig)
    llm_tokens_per_turn: int = 2048
    spotlighting: bool = True
    injection_flag_threshold: float = 0.6


class ASRNoiseConfig(BaseModel):
    wer_levels: list[float] = Field(default_factory=lambda: [0.05, 0.10])
    partial_revision_rate: float = 0.25
    disfluency_rate: float = 0.15
    seed: int = 7


class LatencyModelConfig(BaseModel):
    words_per_second: float = 2.5


class EvalConfig(BaseModel):
    cadences: list[float] = Field(default_factory=lambda: [0.75, 1.0, 1.5])
    asr_noise: ASRNoiseConfig = Field(default_factory=ASRNoiseConfig)
    latency_model: LatencyModelConfig = Field(default_factory=LatencyModelConfig)


class Settings(BaseSettings):
    app: AppConfig = Field(default_factory=AppConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    controller: ControllerConfig = Field(default_factory=ControllerConfig)
    decomposer: DecomposerConfig = Field(default_factory=DecomposerConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    fusion: FusionConfig = Field(default_factory=FusionConfig)
    synthesis: SynthesisConfig = Field(default_factory=SynthesisConfig)
    drafting: DraftingConfig = Field(default_factory=DraftingConfig)
    grounding: GroundingConfig = Field(default_factory=GroundingConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    eval: EvalConfig = Field(default_factory=EvalConfig)

    token_secret: str = Field(default="change-me", validation_alias="KAIROS_TOKEN_SECRET")
    llm_provider: str = Field(default="none", validation_alias="KAIROS_LLM_PROVIDER")
    gemini_api_key: SecretStr | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def load_config(config_path: Path | None = None) -> Settings:
    path = config_path or Path("config/default.yaml")
    raw_data: dict[str, Any] = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}

    # Helper function to sanitize any "TBD" strings to None for optional fields
    def _clean_tbd(d: Any) -> Any:
        if isinstance(d, dict):
            return {k: _clean_tbd(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [_clean_tbd(v) for v in d]
        elif d == "TBD":
            return None
        return d

    clean_data = _clean_tbd(raw_data)

    # Honor environment variable overrides for nested app.env etc. if explicitly set
    if "KAIROS_ENV" in os.environ:
        clean_data.setdefault("app", {})["env"] = os.environ["KAIROS_ENV"]

    settings = Settings(**clean_data)

    # Fail fast validations
    if settings.telemetry.log_text and settings.app.env == "prod":
        raise ValueError(
            "raw text logging (telemetry.log_text=True) is strictly forbidden in production!"
        )

    return settings
