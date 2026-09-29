# CHANGELOG.md — Kairos Project Changelog

## [Unreleased]

### Step 08 (Part 1): Test set generation, cryptographic freeze, dual gates, and controller model arm - 2026-09-29
- Built test split generator (`eval/make_transcripts.py`) drafting 64 test turns into `data/replay/test/` (scenarios.jsonl & gold.jsonl) across 5 turn types (compound, late-constraint, presentation-only, single, out-of-corpus) with stratified sources (42.2% `human_external`, 57.8% `llm_drafted`) and decisive-word positions (24 early, 24 middle, 16 last third).
- Authored external turn guidelines (`eval/external_turns/INSTRUCTIONS.md`) with explicit corpus topics for outside contributor submissions.
- Built inter-annotator agreement evaluation script (`eval/iaa.py`) computing Cohen's Kappa and percent agreement.
- Built test split and configuration freeze tool (`eval/freeze.py`) computing and verifying `data/replay/test/manifest.sha256`.
- Extended acceptance gates engine (`eval/gates.py`) to compute BOTH Official and Strict variants for G1–G6, stratified reports (by source and decisive-word position), and 3-cadence Ready-at-End (0.75x, 1.0x, 1.5x).
- Built comprehensive metrics engine (`eval/metrics.py`) computing all SPEC §9.1a metrics: recall@k, nDCG@10, TTFT and lead-time percentiles, suppression rate, retrievals per turn, redundant-leg rate, cost by turn class, savings vs restart baseline, and cost-to-performance efficiency table.
- Implemented model-based controller arm (`eval/controller_model.py`) with CPU-native NumPy Logistic Regression trained on dev prefixes with sufficiency stabilisation labels ($t_{suf}$), generating the early-retrieval vs false-trigger ROC curve for Ablation A.
- Verified on 64-turn frozen test split: Official G1–G6 all PASS, Strict G1–G6 all PASS, Ready-at-End=0.654 (34/52 RETRIEVE turns), 0 fabricated citations out of 113 claims, 100% suppression rate (0 false triggers on 12 suppression turns).
- Added 6 new unit tests in `tests/test_eval.py`. Full suite now has 118 passing tests with 89% coverage in Docker container, clean `make lint`, clean `make typecheck` (53 files), and zero bandit security issues.

### Step 07: Differentiator MVP assembly and web UI (v0.1-mvp) - 2026-09-29
- Built React + TypeScript + Vite + Tailwind frontend in `web/` with Calm Precision design tokens (SPEC §14.2, §14.3a):
  - Assistant Mode: live transcript with intent color threading, real-time "Already searching..." chip driven by `retrieval_started` events, Answer Canvas with ghost sections, drafting shimmers, settled state, verified source pills with passage popover, "Ready when you stopped" line, and Shorter/As bullets quick actions.
  - Inspector Mode: interactive Timeline with controller decision markers, intent-colored leg Gantt bars, draft markers, utterance-end line, and shaded lead time; Answer panel with `[Doc_ID §Section]` chips and version diffs; Telemetry panel with live event stream, Ready-at-End score, and Jaeger UI links.
  - Story Mode: autoplays the 3 hackathon demo scenarios over live authenticated WebSocket with scenario captions from `strings.en.json`.
  - Strict text-only rendering adhering to Security Rule 1 (zero HTML injection).
- Updated multi-stage `Dockerfile`: Node builds `web/` to `dist/`, copied to `kairos/api/static` in final python image; zero Node at runtime, zero CDN dependencies.
- Built tolerant held-out transcript format adapter (`kairos/stream/adapters.py`) supporting native JSONL, theme-guide Example 1 table format, flat transcript wrappers, and raw text with synthetic timestamps (SPEC §9.6a).
- Built offline evaluation suite (`eval/gates.py`, `eval/baseline.py`, `eval/run_suite.py`) computing official acceptance gates G1–G6 and the Ready-at-End metric with honest denominators.
- Verified all acceptance gates pass on dev split: G1=PASS (1.0), G2=PASS (1.0), G3=PASS (1.0), G4=PASS (0.000, 0 fabricated citations out of 28 total claims), G5=PASS (1.0), G6=PASS (1.0), Ready-at-End=0.769 (10/13 RETRIEVE turns).
- Refined extractive synthesizer (`kairos/synth/extractive.py`) to eliminate arbitrary unretrieved chunk fallbacks, strictly enforcing corpus isolation (Rule 1) and rigorous grounding (Rule 3).
- Added `mvp-replay` automated CI workflow (`.github/workflows/ci.yml`) validating headless replay of the 3 theme demo scenarios, controller decision markers, leg counts, late-constraint version updates, suppression zero-retrieval, and offline `make eval` execution.
- Added 29 unit and gate integration tests across `tests/test_adapter.py` and `tests/test_eval.py`. Full suite now has 112 passing tests with 89% coverage in Docker container, clean `make lint`, clean `make typecheck` (53 files), and zero bandit security issues.
- Tagged release `v0.1-mvp` locally.


### Step 06: Grounded Speed-1 synthesis, drafting, session store & delta engine - 2026-09-29
- Built context spotlighting (`kairos/security/spotlight.py`) enclosing chunks in `<untrusted_corpus id="...">`, escaping adversarial tags, down-weighting flagged chunks, and appending system prompt isolation instructions.
- Implemented Speed-1 extractive synthesizer (`kairos/synth/extractive.py`) scoring candidate sentences by leg overlap, producing natural lead-ins, <= 30-word evidence spans, and exact `[Doc_ID §Section]` citations.
- Implemented Answer-as-you-speak drafting manager (`kairos/synth/drafting.py`) supporting mid-utterance draft synthesis, deterministic gate verification, commit/rollback at utterance end, Ready-at-End calculation, and `draft_*` telemetry events.
- Implemented Stage 1 deterministic grounding gate (`kairos/grounding/gate.py`) rejecting ungrounded or fabricated citations and mismatched spans with explicit uncertainty statements.
- Implemented ephemeral session store (`kairos/session/token.py` & `store.py`) with server-issued 128-bit IDs, HMAC-SHA256 tokens, TTL auto-cleanup, max-sessions cap, version snapshots, and 404 responses for token mismatches.
- Implemented session delta engine (`kairos/session/delta.py`) classifying turns, patching only affected claims while preserving unaffected claims strictly byte-identical (Gate G5), and restructuring presentation without retrieval.
- Implemented REST session endpoints (`POST /v1/sessions`, `GET /v1/sessions/{id}`, `GET /v1/sessions/{id}/diff`, `DELETE /v1/sessions/{id}`) and WebSocket streaming (`WS /v1/stream`) with origin checks, token validation, 4096-byte message limits, 60 msg/s rate limiting, and real-time event streaming.
- Enhanced CLI replay (`kairos replay demo`) replaying all 3 hackathon demo scenarios, printing answer v1, v2, version diffs, and Ready-at-End scores.
- Added 19 unit & integration tests across 5 new test files. Full suite has 83 passing tests with 90% coverage in Docker container, clean mypy `--strict`, clean ruff, and zero bandit security issues.

### Step 05: Multi-intent decomposer, deduplication & parallel dispatch - 2026-09-29
- Built speech disfluency normalizer (`kairos/decompose/disfluency.py`) stripping fillers ("uh", "um"), repetitions ("the the"), and self-repairs ("in Pune — no, Mumbai").
- Implemented offline rule-based clause splitter (`kairos/decompose/rule_splitter.py`) with context inheritance across clauses (locations, head noun entities, quantities) preventing context loss.
- Implemented schema-validated LLM decomposer (`kairos/decompose/llm_splitter.py`) with `<user_utterance>` spotlighting and automatic fallback to rule-based splitter.
- Built Stage 2 decomposition manager (`kairos/decompose/manager.py`) with BGE embedding candidate deduplication (cosine > 0.9), hard sub-query cap (max 4 legs), stable leg IDs (`L1, L2...`), and incremental diffing across chunk arrivals.
- Built parallel retrieval dispatcher (`kairos/decompose/dispatcher.py`) running concurrent hybrid retrieval legs via `asyncio.gather`.
- Updated replay CLI (`kairos replay --split dev`) to display legs per turn with first-dispatch timestamps.
- Added 10 unit tests in `tests/test_decompose.py`; full suite has 64 passing tests with 92% coverage across `kairos/`.

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
