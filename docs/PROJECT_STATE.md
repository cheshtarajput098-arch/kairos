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
| 05 | `build/steps/p04-decomposer.md` | todo | |
| 06 | `build/steps/p05-synthesis-session.md` | todo | |
| 07 | `build/steps/p06-mvp.md` | todo | |
| 08 | `build/steps/p07-evaluation.md` | todo | |
| 09 | `build/steps/p07b-generative.md` | todo | |
| 10 | `build/steps/p09a-ui-design.md` | todo | |
| 11 | `build/steps/p09b-ui-build.md` | todo | |
| 12 | `build/steps/p08-security.md` | todo | |
| 13 | `build/steps/p10-industry.md` | todo | |
| 14 | `build/steps/p11-release.md` | todo | |

## Current tier
Tier 1: Streaming replay harness, virtual clock reader, and retrieval controller complete.

## Done
- Starter repo: rules, autopilot workflows, spec, config, folder layout, placeholder corpus, demo scenarios, docs templates, repo-rule tests.
- Step 01: Kickoff plan artifact produced covering goals, hard rules, security rules, corpus profiling, sequence map, MVP scope, risk matrix, and open decisions.
- Step 02: `pyproject.toml`, MIT `LICENSE`, `Makefile`, `.pre-commit-config.yaml`, Pydantic Settings config loader (`kairos/config.py`), Pydantic v2 strict schemas (`kairos/schemas.py`), telemetry engine (`kairos/telemetry/`), thin LLM provider interface (`kairos/llm/`), FastAPI `/v1` app with health/ready probes & security headers (`kairos/api/`), `Dockerfile` & `docker-compose.yml`, 27 unit & security integration tests passing.
- Step 03: Section-aware chunker with stable IDs (`Doc_12§2`), NFKC normalizer & zero-width stripper (`kairos/ingest/normalizer.py`), prompt injection pattern & heuristic scanner (`kairos/ingest/scanner.py`), SHA-256 corpus manifest generator/verifier (`kairos/ingest/manifest.py`), sparse BM25 index (`kairos/index/sparse.py`), dense FastEmbed BGE-small index (`kairos/index/dense.py`), async hybrid retriever with deadline cancellation and prefix cache (`kairos/retrieve/`), RRF fusion & deduplication (`kairos/fuse/`), CLI index & query commands (`kairos/cli.py`). Index build time: 0.58s for 27 chunks; Query latency: p50=8.45ms, p95=199.78ms (mean 45.11ms). 39 tests passing with 0 lint/security issues.
- Step 04: Replay harness (`kairos/stream/replay.py`) with virtual clock cadence scaling (0.75x/1.0x/1.5x), instantaneous evaluation mode, partial revision handling (`revises=<index>`), and config-driven limits. Stage 1 retrieval controller (`kairos/controller/features.py`, `kairos/controller/rules.py`) with entity saturation, embedding drift tracking, syntactic openness, BM25 probe stability, and presentation intent classification. Reversible speculation manager (`kairos/controller/speculation.py`) with per-turn budgets and automatic entity-disappearance cancellation. Dev dataset (`data/replay/dev/`) with 16 turns across 5 turn types. `kairos replay --split dev` CLI. 52 tests passing (92% coverage) with zero lint or security warnings.

## Next
Step 05: `build/steps/p04-decomposer.md`. Type `/build-next` in a new conversation.

## Known issues
- The real corpus has not been supplied yet; using the placeholder corpus (see `docs/DECISIONS.md`).

## Tags
| Tag | Date | Notes |
|---|---|---|
