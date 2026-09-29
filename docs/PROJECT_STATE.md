# PROJECT_STATE.md — where the build is right now

The agent updates this file at the end of every `/build-next` run. Keep it short and factual.

## Step status
Statuses: `todo` · `in_progress (part k of n)` · `blocked` · `done`

| # | Step file | Status | Notes |
|---|---|---|---|
| 01 | `build/steps/p00-kickoff.md` | done | Kickoff plan completed |
| 02 | `build/steps/p01-skeleton.md` | done | Skeleton, packaging, config, telemetry, API & security baseline |
| 03 | `build/steps/p02-index.md` | done | Corpus ingest, integrity & hybrid index |
| 04 | `build/steps/p03-controller.md` | done | Replay harness & retrieval controller |
| 05 | `build/steps/p04-decomposer.md` | done | Multi-intent decomposer, deduplication & parallel dispatch |
| 06 | `build/steps/p05-synthesis-session.md` | done | Grounded synthesis, drafting, session store & delta engine |
| 07 | `build/steps/p06-mvp.md` | done | Tier 1 Differentiator MVP complete (pipeline, eval suite G1–G6, web UI, Docker multi-stage build, v0.1-mvp tag) |
| 08 | `build/steps/p07-evaluation.md` | todo | |
| 09 | `build/steps/p07b-generative.md` | todo | |
| 10 | `build/steps/p09a-ui-design.md` | todo | |
| 11 | `build/steps/p09b-ui-build.md` | todo | |
| 12 | `build/steps/p08-security.md` | todo | |
| 13 | `build/steps/p10-industry.md` | todo | |
| 14 | `build/steps/p11-release.md` | todo | |

## Current tier
Tier 1: Differentiator MVP (`v0.1-mvp`) complete. All acceptance gates G1–G6 passing.

## Done
- Starter repo: rules, autopilot workflows, spec, config, folder layout, placeholder corpus, demo scenarios, docs templates, repo-rule tests.
- Step 01: Kickoff plan artifact produced covering goals, hard rules, security rules, corpus profiling, sequence map, MVP scope, risk matrix, and open decisions.
- Step 02: `pyproject.toml`, MIT `LICENSE`, `Makefile`, `.pre-commit-config.yaml`, Pydantic Settings config loader (`kairos/config.py`), Pydantic v2 strict schemas (`kairos/schemas.py`), telemetry engine (`kairos/telemetry/`), thin LLM provider interface (`kairos/llm/`), FastAPI `/v1` app with health/ready probes & security headers (`kairos/api/`), `Dockerfile` & `docker-compose.yml`, 27 unit & security integration tests passing.
- Step 03: Section-aware chunker with stable IDs (`Doc_12§2`), NFKC normalizer & zero-width stripper (`kairos/ingest/normalizer.py`), prompt injection pattern & heuristic scanner (`kairos/ingest/scanner.py`), SHA-256 corpus manifest generator/verifier (`kairos/ingest/manifest.py`), sparse BM25 index (`kairos/index/sparse.py`), dense FastEmbed BGE-small index (`kairos/index/dense.py`), async hybrid retriever with deadline cancellation and prefix cache (`kairos/retrieve/`), RRF fusion & deduplication (`kairos/fuse/`), CLI index & query commands (`kairos/cli.py`). Index build time: 0.58s for 27 chunks; Query latency: p50=8.45ms, p95=199.78ms (mean 45.11ms). 39 tests passing with 0 lint/security issues.
- Step 04: Replay harness (`kairos/stream/replay.py`) with virtual clock cadence scaling (0.75x/1.0x/1.5x), instantaneous evaluation mode, partial revision handling (`revises=<index>`), and config-driven limits. Stage 1 retrieval controller (`kairos/controller/features.py`, `kairos/controller/rules.py`) with entity saturation, embedding drift tracking, syntactic openness, BM25 probe stability, and presentation intent classification. Reversible speculation manager (`kairos/controller/speculation.py`) with per-turn budgets and automatic entity-disappearance cancellation. Dev dataset (`data/replay/dev/`) with 16 turns across 5 turn types. `kairos replay --split dev` CLI. 52 tests passing (92% coverage) with zero lint or security warnings.
- Steps 01–03 Fixes: Pinned runtime dependencies in `pyproject.toml` and verified `uv.lock`. Multi-stage Dockerfile now installs solely from `uv.lock` with GNU `make` and pre-cached FastEmbed model. Added FastAPI startup lifespan and readiness auto-build on missing/changed corpus with writable tmpfs index volume. Added comprehensive tests for `kairos/cli.py`, `kairos/llm/provider.py`, and `kairos/security/limits.py` bringing coverage to 92%. Added `docker-smoke` CI job validating readiness and Pune query top-3 grounding (`Doc_12 §2`). Updated autopilot rules enforcing that all verification commands must be run as written and coverage must be >= 85%. All container `make` targets (`lint`, `typecheck`, `test`, `security`, `index`) verified working.
- Step 05: Multi-intent decomposer in `kairos/decompose/`: generic speech disfluency normalizer (`disfluency.py`) stripping fillers, repetitions, and self-repairs ("in Pune — no, Mumbai"); offline rule-based clause splitter (`rule_splitter.py`) with location, head entity, and quantity context inheritance preventing context loss; LLM decomposer (`llm_splitter.py`) with `<user_utterance>` spotlighting and automatic fallback; decomposition manager (`manager.py`) with BGE embedding deduplication (cosine > 0.9), hard cap (max 4 legs), stable leg IDs (`L1, L2...`), and incremental diffing; parallel retrieval dispatcher (`dispatcher.py`) running concurrent hybrid retrieval legs via `asyncio.gather`. Replay CLI (`kairos replay --split dev`) updated to display legs per turn with first-dispatch timestamps. 64 tests passing with 92% coverage and zero lint, typecheck, or security warnings.
- Step 06: Grounded Speed-1 synthesis, answer drafting, grounding gate, session store, and delta engine:
  - `kairos/security/spotlight.py`: Delimits untrusted corpus chunks in `<untrusted_corpus id="...">`, escapes tags, down-weights flagged adversarial chunks, appends prompt rules.
  - `kairos/synth/extractive.py`: Speed-1 extractive synthesizer producing natural lead-ins, <= 30-word evidence spans, and exact `[Doc_ID §Section]` citations.
  - `kairos/synth/drafting.py`: Answer-as-you-speak drafting manager supporting mid-utterance draft synthesis, deterministic gate verification, commit/rollback at utterance end, Ready-at-End calculation, and `draft_*` event logging.
  - `kairos/grounding/gate.py`: Stage 1 deterministic grounding gate dropping ungrounded/fabricated citations and mismatched evidence spans with explicit uncertainty statements.
  - `kairos/session/token.py` & `store.py`: Ephemeral session store with server-issued 128-bit IDs, HMAC-SHA256 tokens, TTL auto-cleanup, max-sessions cap, version snapshots, and 404 responses for token mismatches.
  - `kairos/session/delta.py`: Session delta engine classifying turns (`presentation_only`, `constraint_on_existing`, `contradiction`, `new_topic`), patching only affected claims while preserving unaffected claims strictly byte-identical (Gate G5), and restructuring presentation without retrieval.
  - `kairos/api/stream.py` & `app.py`: REST session endpoints (`POST /v1/sessions`, `GET /v1/sessions/{id}`, `GET /v1/sessions/{id}/diff`, `DELETE /v1/sessions/{id}`) and WebSocket streaming (`WS /v1/stream`) with origin checks, token validation, 4096-byte message limits, 60 msg/s rate limiting, and real-time event streaming.
  - Replay CLI (`kairos replay demo`) replaying all 3 hackathon demo scenarios, printing answer v1, v2, version diffs, and Ready-at-End scores.
  - 83 tests passing with 90% coverage in Docker container, clean mypy `--strict`, clean ruff, and zero bandit security issues.
- Step 07: Differentiator MVP assembly and web UI (`v0.1-mvp`):
  - `web/`: Built complete React + TypeScript + Vite + Tailwind frontend conforming to Calm Precision design tokens (SPEC §14.2, §14.3a).
    - Assistant Mode: live transcript with intent color threading, real-time "Already searching..." chip, Answer Canvas with ghost sections → drafting shimmer → settled state, source pills with popovers, "Ready when you stopped" line, and Shorter/As bullets quick actions.
    - Inspector Mode: interactive Timeline with decision markers, intent-colored leg Gantt bars, draft markers, utterance-end line, and shaded lead time; Answer panel with `[Doc_ID §Section]` chips and diffing; Telemetry panel with live event stream, Ready-at-End score, and Jaeger UI links.
    - Story Mode: autoplays the 3 hackathon demo scenarios over live authenticated WebSocket with scenario captions from `strings.en.json`.
    - Strict text-only rendering (Security Rule 1).
  - Multi-stage Dockerfile: Node builds `web/` to `dist/`, copied to `kairos/api/static` in final python image. Zero Node at runtime, zero CDN dependencies.
  - `kairos/stream/adapters.py`: Tolerant held-out transcript format adapter supporting native JSONL, theme-guide Example 1 table format, flat transcript wrappers, and raw text fallback with synthetic timestamps (SPEC §9.6a).
  - `eval/`: Complete offline evaluation suite (`eval/gates.py`, `eval/baseline.py`, `eval/run_suite.py`) computing official acceptance gates G1–G6 with honest denominators and Ready-at-End metric. `make eval` runs completely offline with no network or API key.
  - Verified evaluation gate results on dev split: G1=PASS (1.0), G2=PASS (1.0), G3=PASS (1.0), G4=PASS (0.000, 0 fabricated citations), G5=PASS (1.0), G6=PASS (1.0), Ready-at-End=0.769 (10/13 RETRIEVE turns).
  - `.github/workflows/ci.yml`: Added `mvp-replay` CI job asserting headless demo replay, controller decisions, leg counts, late-constraint version bumps, zero-retrieval suppression, and offline `make eval` gate execution.
  - 112 unit & integration tests passing with 89% coverage in Docker container, clean `make lint`, clean `make typecheck` (53 files), clean `make security`. Tagged `v0.1-mvp`.

## Next
Step 08: `build/steps/p07-evaluation.md` — Offline evaluation suite, baseline benchmarking & ablation analysis.

## Known issues
- The real corpus has not been supplied yet; using the placeholder corpus (see `docs/DECISIONS.md`).

## Tags
| Tag | Date | Notes |
|---|---|---|
| `v0.1-mvp` | 2026-09-29 | Tier 1 Differentiator MVP end-to-end (SPEC §15.1) |
