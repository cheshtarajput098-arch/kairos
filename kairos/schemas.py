"""Pydantic v2 strict schemas for all Kairos data contracts (SPEC §2).

Enforces extra="forbid" on all models to reject unknown fields.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictBaseModel(BaseModel):
    """Base model enforcing strict validation and forbidding extra fields."""
    model_config = ConfigDict(extra="forbid", strict=True)


class CorpusChunk(StrictBaseModel):
    chunk_id: str
    doc_id: str
    section: str
    title: str
    text: str
    char_start: int
    char_end: int


class ReplayChunk(StrictBaseModel):
    t: float
    text: str
    partial: bool | None = None
    revises: int | None = None


class ReplayTranscript(StrictBaseModel):
    session_id: str
    turn_id: str
    turn_type: Literal["compound", "late_constraint", "presentation_only", "single", "out_of_corpus"]
    scenario: str | None = None
    chunks: list[ReplayChunk]
    utterance_end: float


class GoldLabel(StrictBaseModel):
    turn_id: str
    retrieval_required: bool
    sub_intents: list[str]
    answer_chunks: dict[str, list[str]]
    expected_uncertainty: str | None = None
    late_constraint_of: str | None = None
    reason: str | None = None
    expected_behaviour: str | None = None
    decisive_word_position: str | None = None
    source: str | None = None


class RetrievalEvent(StrictBaseModel):
    timestamp_s: float
    query: str
    trigger: Literal["provisional", "multi_intent", "delta"]
    event: Literal[
        "retrieval_started",
        "retrieval_completed",
        "retrieval_cancelled",
        "retrieval_reused_cache",
    ]
    leg_id: str
    latency_ms: float


class ControllerDecision(StrictBaseModel):
    timestamp_s: float
    decision: Literal["WAIT", "RETRIEVE", "NO_RETRIEVAL"]
    reason: str
    features: dict[str, Any] = Field(default_factory=dict)


class Leg(StrictBaseModel):
    leg_id: str
    text: str
    entities: list[str]
    first_dispatch_s: float


class ClaimObject(StrictBaseModel):
    claim_id: str
    leg_id: str
    text: str
    citations: list[str]
    evidence_span: str
    status: Literal["verified", "dropped", "uncertain", "retracted"]
    version: int


class VersionDiff(StrictBaseModel):
    added: list[str] = Field(default_factory=list)
    changed: list[str] = Field(default_factory=list)
    retracted: list[str] = Field(default_factory=list)
    unchanged: list[str] = Field(default_factory=list)
    citations_added: list[str] = Field(default_factory=list)


class Metrics(StrictBaseModel):
    utterance_end_s: float
    first_retrieval_s: float | None = None
    lead_time_s: float | None = None
    ttft_s: float | None = None
    e2e_latency_s: float | None = None
    retrievals: int = 0
    ready_at_end: float = 0.0
    first_verified_rel_end_s: float | None = None
    drafts: int = 0
    rollbacks: int = 0
    rewrite_pass_rate: float = 1.0
    tokens_in: int = 0
    tokens_out: int = 0
    est_cost_usd: float = 0.0


class EventRecord(StrictBaseModel):
    """Per-turn output event record (SPEC §2.4)."""
    session_id: str
    turn_id: str
    answer_version: int = 1
    parent_version: int | None = None
    retrieval_required: bool
    reason: str | None = None
    retrieval_events: list[RetrievalEvent] = Field(default_factory=list)
    sub_queries: list[str] = Field(default_factory=list)
    answer: str
    citations: list[str] = Field(default_factory=list)
    uncertainty: str | None = None
    legs: list[Leg] = Field(default_factory=list)
    controller_decisions: list[ControllerDecision] = Field(default_factory=list)
    claims: list[ClaimObject] = Field(default_factory=list)
    version_diff: VersionDiff = Field(default_factory=VersionDiff)
    metrics: Metrics


class ErrorDetail(StrictBaseModel):
    code: str
    message: str
    request_id: str


class ErrorEnvelope(StrictBaseModel):
    error: ErrorDetail
