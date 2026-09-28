# CHANGELOG.md — Kairos Project Changelog

## [Unreleased]

### Step 04: Replay harness and retrieval controller - 2026-09-29
- Built virtual clock streaming replay reader in `kairos/stream/replay.py` supporting cadence multipliers (0.75x/1.0x/1.5x), instantaneous evaluation mode, partial revision handling (`revises=<index>`), and config-driven limits.
- Built Stage 1 feature extractor (`kairos/controller/features.py`) computing entity counts/saturation, embedding drift cosine distance, syntactic openness heuristics, BM25 probe stability, and presentation intent cues.
- Built Stage 1 rule-based controller (`kairos/controller/rules.py`) outputting `WAIT`, `RETRIEVE`, and `NO_RETRIEVAL` decisions with machine-readable reasons and logging full feature vectors.
- Built reversible speculative retrieval manager (`kairos/controller/speculation.py`) with per-turn speculative budget and cancellation on entity changes.
- Authored development replay dataset in `data/replay/dev/` (16 scenarios covering compound, late-constraint, presentation-only, single, and out-of-corpus turns, plus gold labels).
- Added `kairos replay --split <split>` CLI command with decision timeline and lead-time display.
- Added comprehensive unit tests in `tests/test_stream.py` and `tests/test_controller.py`. All 52 tests pass with 92% coverage across `kairos/`.

### Step 03: Corpus ingest, integrity & hybrid index - 2026-09-29
- Built section-aware document chunker with stable IDs (`[Doc_ID §Section]`) in `kairos/ingest/chunker.py`.
- Implemented Unicode NFKC normalization and zero-width/control character stripper in `kairos/ingest/normalizer.py`.
- Added heuristic and pattern-based prompt injection scanner in `kairos/ingest/scanner.py`.
- Built SHA-256 corpus integrity manifest generator & verifier in `kairos/ingest/manifest.py`, integrated into `/v1/ready` probe.
- Created sparse BM25 index using `bm25s` (`kairos/index/sparse.py`) and dense vector index using `FastEmbed` `BAAI/bge-small-en-v1.5` (`kairos/index/dense.py`).
- Implemented async hybrid retriever with deadline cancellation and LRU prefix cache (`kairos/retrieve/`).
- Built RRF fusion ($k=60$) and deduplication/conflict checker (`kairos/fuse/`).
- Added CLI commands `kairos index` and `kairos query`. Measured index build time: 0.58s; Query latency: p50=8.45ms, p95=199.78ms. 39 unit and integration tests passing.

### Step 02: Skeleton, packaging, config, telemetry, API & security baseline - 2026-09-29
- Created `pyproject.toml`, MIT `LICENSE`, `Makefile`, `.pre-commit-config.yaml`, and `.bandit.yml`.
- Built Pydantic Settings configuration loader (`kairos/config.py`) with environment overrides & startup validation.
- Defined Pydantic v2 strict schemas (`kairos/schemas.py`) for all SPEC §2 contracts with `extra="forbid"`.
- Implemented OpenTelemetry OTLP integration (`kairos/telemetry/otel.py`) & JSONL event logger (`kairos/telemetry/events.py`) with automatic PII redaction.
- Created thin LLM Provider interface (`kairos/llm/provider.py`) supporting `none`, `gemini`, `openai_compatible`, `ollama`, and `local`.
- Built FastAPI `/v1` application (`kairos/api/app.py`), request ID tracing, security headers middleware, and custom error envelope `{error: {code, message, request_id}}`.
- Configured multi-stage non-root `Dockerfile` and `docker-compose.yml` with read-only root, tmpfs, capability drops, and Jaeger tracing.
- Added 27 unit & security integration tests (`tests/`) passing with 86% coverage and 0 linting/security findings.

### Step 01: Kickoff plan (no code) - 2026-09-29
- Created kickoff master architecture plan artifact.
- Restated theme goals, 5 hard rules, and 10 security rules.
- Profiled current placeholder corpus (8 files, ~24 sections) and section-aware chunking strategy `[Doc_ID §Section]`.
- Mapped all 14 build steps, files, tests, and verification commands.
- Defined MVP scope, concrete file structure, risk mitigations, and resolved open decisions.
