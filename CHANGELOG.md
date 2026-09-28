# CHANGELOG.md — Kairos Project Changelog

## [Unreleased]

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
