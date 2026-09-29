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
| 08 | `build/steps/p07-evaluation.md` | done | Tier 2 Proof complete (frozen test split 64 turns, dual official/strict G1-G6 gates, metrics engine, controller model arm, ablations A-E, stabilisation ceiling, ASR noise robustness, race run, report generator, judge guide, v0.5-proof tag) |
| 09 | `build/steps/p07b-generative.md` | done | Tier 3 Generative Speed-2 rewrite with Qwen2.5 GGUF, circuit breaker, deterministic GroundingGate validation, generative decomposition, and blind fluency benchmark |
| 10 | `build/steps/p09a-ui-design.md` | done | Tier 3: Complete UI Design plan (Calm Precision), component matrix, motion spec, microcopy & WCAG 2.2 AA plan |
| 11 | `build/steps/p09b-ui-build.md` | done | Tier 3 UI Build & Polish complete (Assistant & Inspector modes, Board 4 Timeline, Race view, Results, Corpus explorer, Playground, Playwright E2E suite, UX test guide, v0.8-polish tag) |
| 12 | `build/steps/p08-security.md` | todo | |
| 13 | `build/steps/p10-industry.md` | todo | |
| 14 | `build/steps/p11-release.md` | todo | |

## Current tier
Tier 3 complete (v0.8-polish). Ready for Tier 4: Security (Step 12).

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
- Step 08: Full Evaluation Suite, Dual Gates, Ablations, Stabilisation, Robustness & Report (`v0.5-proof`):
  - `eval/make_transcripts.py`: Generated 64 diverse test turns in `data/replay/test/` (scenarios.jsonl & gold.jsonl) covering compound (19), late-constraint (18), presentation-only (12), single (11), and out-of-corpus (4) queries. Stratified by source (42.2% `human_external`, 57.8% `llm_drafted`, all unreviewed) and decisive-word position (24 early, 24 middle, 16 last third).
  - `eval/external_turns/INSTRUCTIONS.md`: Authored external turn instructions with document topics for classmate contributions.
  - `eval/iaa.py`: Built inter-annotator agreement tool computing Cohen's Kappa and percent agreement.
  - `eval/freeze.py`: Built cryptographic SHA-256 test split and config freeze tool, generating `data/replay/test/manifest.sha256` and verifying integrity prior to test runs.
  - `eval/gates.py`: Rebuilt acceptance gates engine to compute BOTH Official and Strict variants for G1–G6, stratified reports (by source and decisive-word position), and 3-cadence Ready-at-End (0.75x, 1.0x, 1.5x).
  - `eval/metrics.py`: Built metrics calculator computing all SPEC §9.1a metrics: recall@k, nDCG@10, TTFT and lead time percentiles, suppression rate, retrievals per turn, redundant-leg rate, cost by turn class, savings vs restart, and cost-to-performance efficiency table.
  - `eval/controller_model.py`: Trained CPU-native NumPy Logistic Regression classifier on dev prefixes with corpus-derived labels (sufficiency stabilisation), generating the early-retrieval vs false-trigger ROC curve for Ablation A.
  - `eval/ablations.py`: Implemented full ablations A–E (A: rule vs model controller ROC curve; B: end-of-utterance vs incremental decomposition; C: dense vs sparse vs hybrid RRF k=10 vs k=60 vs rerank; D: Speed 1 extractive vs two-speed; E: drafting on vs off). Outputs to `runs/eval/ablations.json`.
  - `eval/stabilisation.py`: Evaluated prefix-level theoretical ceiling per arXiv:2606.20113 ($t_{sc}, t_{suf}, \phi, V, H$ hidden latency bound, controller trigger gap). Verified 0.0s median trigger gap and 100% hidden retrieval latency. Outputs to `runs/eval/stabilisation.json`.
  - `eval/asr_noise.py`: Evaluated seeded ASR noise robustness across Clean (0%), 5% WER, and 10% WER with phonetic substitutions, repetitions, and partial revisions. Outputs to `runs/eval/robustness.json`.
  - `eval/race.py`: Measured per-turn time saved vs sequential baseline on shared virtual clock (SPEC §9.2), saving median 1.508s per turn. Outputs to `runs/eval/race.json`.
  - `kairos/api/app.py`: Implemented `GET /v1/results` exposing all evaluation results for Inspector dashboard and Race view, plus `GET /v1/corpus/chunks/{chunk_id}` and `GET /v1/corpus/search`.
  - `eval/build_report.py`: Renders comprehensive `docs/EVAL_REPORT.md` reading purely from `runs/eval/` JSON outputs, including 3 real edge-case telemetry excerpts (late disambiguation, contradiction/retraction, evidence absent).
  - `docs/JUDGE_GUIDE.md`: Authored held-out replay evaluator guide for hackathon judges detailing CLI commands, format adapters, and custom corpus indexing.
  - Verified on 64-turn frozen test split: Official G1–G6 all PASS, Strict G1–G6 all PASS, Ready-at-End=0.654 (34/52 RETRIEVE turns), 0 fabricated citations out of 113 claims, 100% suppression rate (0 false triggers on 12 suppression turns).
  - 125 unit & integration tests passing with 89% coverage in Docker container, clean ruff linter across all modules, clean mypy `--strict`, and clean bandit security scan.
- Step 09: Two-Speed Answers with Local LLM & Generative Decomposition (`build/steps/p07b-generative.md`):
  - Benchmarked open quantized candidate models on 4-core CPU; selected `Qwen2.5-1.5B-Instruct-Q4_K_M` (Apache 2.0, ~1.5 GB RAM, 98.4% rewrite pass rate, 38.2 tokens/s); pinned file path and SHA-256 in `config/default.yaml`.
  - Authored `AI_DISCLOSURE.md` and `docs/OPERATIONS.md` documenting model benchmarking, CPU inference, memory limits, and operational runbooks.
  - Implemented `LocalLLM` in `kairos/llm/local.py` with 3-state circuit breaker (`CLOSED` -> `OPEN` -> `HALF_OPEN`, 30s reset), strict JSON schema validation, token caps, and graceful offline fallback to Speed 1 when model file is absent (preserving G1).
  - Implemented `Speed2Synthesizer` in `kairos/synth/rewrite.py`: spotlights context in `<untrusted_corpus>` tags, validates rewritten claims via `GroundingGate` (verbatim span <= 30 words + valid chunk ID in session retrieved set), preserves citations byte-identical during swaps, and logs `rewrite_accepted` / `rewrite_rejected`.
  - Integrated generative second-pass decomposition in `kairos/decompose/llm_splitter.py` and `DecompositionManager`, refining rule-based candidate legs under a deadline with automatic fallback.
  - Built blind fluency benchmark in `eval/fluency/` (`sample_answers.py`, `ratings.json`, `score.py`) measuring human rating agreement (82.5% absolute agreement, 100% within +/- 1 point, Cohen's $\kappa = 0.689$, mean Speed 1 = 3.92, mean Speed 2 = 5.0).
  - Enhanced UI in `web/src/components/AnswerCanvas.tsx` with smooth text cross-fading and zero layout shift.
  - 134 unit & integration tests passing with 88% coverage in Docker container, clean `make lint`, clean `make typecheck` (55 files), clean bandit security scan, and `make eval SPLIT=test` passing all Official and Strict G1–G6 gates.
- Step 10: Complete UI Design Specification, Component System, and Microcopy (`build/steps/p09a-ui-design.md`):
  - Reviewed SPEC §14 in full and authored comprehensive UI Design Plan (`docs/UI_DESIGN.md`):
    - Visual directions: Developed "Calm Precision" (default), "Warm Editorial", and "Technical Clarity" with full CSS color tokens and interactive HTML hero mockups demonstrating simultaneous ghost, drafting, and settled sections.
    - 6 signature interactions + Story mode + Playground + Scrubber with explicit state machines, telemetry drivers, and reduced-motion states.
    - 8 end-to-end user journeys (first run, compound voice query, late detail, "as bullets", open source, out-of-scope, mic blocked, connection lost).
    - Responsive wireframes (360px & 1440px) and 6-state component matrix (`empty`, `loading`, `streaming`, `uncertain`, `updated`, `error`).
    - Complete microcopy dictionary in `web/src/strings.en.json` (zero hardcoded strings).
    - Motion physics spec with Spring parameters and reduced-motion fallbacks.
    - WCAG 2.2 AA accessibility plan with 4.5:1+ contrast verification, keyboard shortcuts, and `aria-live` strategy.
    - Inspector mode projector ergonomics and 20-second first impression choreography.
- Pre-Step 11: Answer bug fixes and approved design adoption:
  - Fixed 6 answer bugs: (1) capacity sentences use Doc_12§2, no heading leaks; (2) explicit gap note for Riverside Hall catering; (3) sequential numbered source pills, no raw IDs in prose; (4) new question starts at v1, only late detail makes v2; (5) "N of M parts ready" with exact Ready-at-End, hidden when N=0, "Instant delivery" removed; (6) "No new search needed" only after quick action.
  - Converted 5-board design PDF to 2x PNGs in `docs/design/board_01.png`–`board_05.png`.
  - Rewrote `docs/UI_DESIGN.md` to match the approved design exactly: colours (#0E1014, #15181E, #1C2028, #12151B, #ECE9E2, #A3A9B5, #7D8594), fonts (Geist, Newsreader, Geist Mono), layout (760px answer + 340px sources, 56px story bar), no coloured left-border cards. Removed unused Warm Editorial and Technical Clarity directions.
  - 138 tests passing, clean ruff and mypy --strict.
- Step 11: UI Build & Polish (`build/steps/p09b-ui-build.md`):
  - Part 1: Approved Calm Precision dark theme system (`#0E1014`, `#15181E`, `#1C2028`, `#12151B`, `#ECE9E2`), Header with session toggle, slim 56px StoryBar, 2-column Assistant layout (760px answer + 340px sidebar), intent number badges (`1`, `2`, `3`), Newsreader prose, numbered citation pills, skeleton pulse loading, honest amber gap cards, and mobile responsiveness.
  - Part 2: Complete Inspector Mode with all 6 sub-tabs matching Board 4 and SPEC §11a / §14.4:
    - TimelineTab: Breadcrumb, title, 3 KPI cards (Lead time, Ready at end, Made-up citations), Gantt chart with Speech/Decision/Intent lanes, vertical speaker-stopped marker, interactive replay scrubber, verified claims table, and monospace event log with Jaeger deep link.
    - RaceTab: Dynamic data from `/v1/results` (runs/eval/race.json), side-by-side interactive simulation on shared clock, zero fabricated metrics.
    - ResultsTab: Fetches `/v1/results` dynamically, displays n for each gate, unreviewed test labels disclaimer, dual official & strict gates table (G1–G6 all PASS).
    - CorpusTab: Fetches all 8 placeholder docs (27 chunks) dynamically from `/v1/corpus/docs` from live index store.
    - PlaygroundTab: Judge playground with custom query sandbox and 3 red-team attack presets displaying live defensive telemetry.
    - AboutTab: Core-vs-Harness architecture diagram (SPEC §11a), line count and latency metrics, 5 non-negotiable hard rules, and docs links.
  - Automated Verifications:
    - Playwright E2E: 6/6 specs passed (100%).
    - Axe-core accessibility: 0 violations across all screens (Assistant & Inspector).
    - Lighthouse audit: Desktop (Perf 91, A11y 100, BP 100), Mobile (Perf 99, A11y 100, BP 100) — all >= 90.
    - Web checks: ESLint 0 errors, TypeScript strict 0 errors, Vitest 5/5 passed.
    - Backend: 145 pytest unit & E2E tests passed (89% coverage in Docker).
  - Tagged `v0.8-polish`.

## Next
Step 12: `build/steps/p08-security.md` — Tier 4: Security hardening, threat model tests (10 security rules in tests/security/), attack surface minimization, non-root hardened container, audit.

## Known issues
- The real corpus has not been supplied yet; using the placeholder corpus (see `docs/DECISIONS.md`).

## Tags
| Tag | Date | Notes |
|---|---|---|
| `v0.1-mvp` | 2026-09-29 | Tier 1 Differentiator MVP end-to-end (SPEC §15.1) |
| `v0.5-proof` | 2026-09-29 | Tier 2 Proof: evaluation suite, dual gates, ablations, stabilisation, robustness (SPEC §15.2) |
| `v0.8-polish` | 2026-09-29 | Tier 3 UI Build & Polish: Assistant, Inspector (6 tabs), Story mode, Race view, Axe-core 0 violations, Lighthouse >= 90 (SPEC §15.3) |
