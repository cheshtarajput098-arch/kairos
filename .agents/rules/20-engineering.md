---
trigger: always_on
---

# Kairos — engineering rules

Part of the project rules (see AGENTS.md).

## 3. Engineering rules

- **Python 3.11**, FastAPI + WebSocket, `asyncio`. Type hints everywhere; Pydantic v2 for every event and output schema.
- **CPU-first.** The whole system, including evaluation, must run on a laptop CPU. GPU is optional acceleration, never required.
- **Offline-capable, generative by default.** With no API key and no network after the build, the system runs end to end with the local LLM for fluent answers (SPEC.md §6.2 Speed 2). If that model is missing, slow or failing, it falls back automatically to the extractive Speed-1 path and the rule-based decomposer. A hosted LLM is an optional upgrade selected by config, never a hard dependency. This is what makes G1 pass on a judge's clean machine.
- **Pinned dependencies.** Use `uv` with `uv.lock` (or `pip-tools` with a fully pinned `requirements.lock`). Pin model names and revisions in `config/default.yaml`.
- **Deterministic.** Temperature 0. Fixed seeds. Replay runs must give identical controller decisions and retrieval sets on repeat.
- **IDs are sacred.** A chunk's `[Doc_ID §Section]` marker must survive chunking, indexing, retrieval, fusion, reranking, synthesis and the grounding gate byte-for-byte.
- **Fail soft.** A malformed chunk, a timed-out retrieval leg or a generator error must never crash a replay run. Log it, emit an uncertainty flag, continue.
- **Config over code.** Thresholds (drift, entity saturation, sub-query cap, dedupe cosine, RRF k, deadlines, budgets) live in `config/default.yaml`, never as magic numbers.

## 3A. Industry-readiness rules

- **CI on every push** (GitHub Actions): ruff, mypy `--strict` on `kairos/`, pytest with coverage ≥ 85% on `kairos/`, bandit, pip-audit, gitleaks, frontend lint + typecheck + unit tests, Playwright e2e with axe accessibility checks, Docker build, Trivy image scan (fail on HIGH/CRITICAL), and a smoke eval on a small dev slice. A red CI means the task is not done.
- **pre-commit** hooks mirror the fast CI checks.
- `tests/test_repo_rules.py` must pass at every commit. It guards the no-hardcoding rule, the import boundary, config validity, demo data and the rules-file size limit. Never weaken it to make a change pass.
- **Versioned API** under `/v1`, OpenAPI docs at `/docs` (disabled when `KAIROS_ENV=prod`), consistent error envelope `{error: {code, message, request_id}}`. Stack traces never reach clients.
- **Operability**: `/v1/health` (liveness) and `/v1/ready` (index loaded, models verified), structured JSON logs with `request_id`/`session_id`/`trace_id`, graceful shutdown that cancels in-flight tasks, config validated at startup (fail fast).
- **Load-tested**: a Locust scenario with concurrent streaming sessions; report p50/p95 turn latency and error rate at 1 and 10 concurrent sessions on a laptop CPU (25 if time allows; see SPEC.md §15.6).
- **Docs a company would expect**: `SECURITY.md` (threat model, reporting), `docs/OPERATIONS.md` (runbook, config reference, SLOs), `CHANGELOG.md`, `LICENSE`.

## 3C. Differentiator MVP first, then tiers

Build the **Differentiator MVP** (SPEC.md §15.1) and tag it `v0.1-mvp` before anything else. It already includes answer-as-you-speak drafting and Story mode, because that is what makes Kairos different. Then build Tiers 2–5 strictly in order (§15.2–15.5), tagging each one. Every tier must leave a complete, submittable repo: no half-built features and no README promises the code doesn't keep. If time runs short, cut from the §15.6 cut list in order, and never cut anything marked "never cut". The MVP replay must pass in CI at every commit.

## 6. Repository layout (do not deviate without approval)

```
kairos/
  AGENTS.md  GEMINI.md  SPEC.md  JUDGE_REVIEW.md  README.md  AI_DISCLOSURE.md  LICENSE
  .agents/rules/   # 10-security.md, 20-engineering.md, 30-ui.md (always-on rules)
  Makefile  Dockerfile  docker-compose.yml  pyproject.toml  uv.lock  .env.example
  config/default.yaml
  kairos/
    ingest/        # parse, section-aware chunking, [Doc_ID §Section] markers
    index/         # dense (FastEmbed) + BM25 index build/load
    stream/        # transcript replay, chunk events, optional faster-whisper live path
    controller/    # Stage 1: WAIT / RETRIEVE / SUPPRESS, speculation + cancellation
    decompose/     # Stage 2: multi-intent decomposition, dedupe, cap, stable leg IDs
    retrieve/      # Stage 3: hybrid legs, prefix-hash cache, deadlines
    fuse/          # Stage 4: RRF, optional cross-encoder rerank
    synth/         # Stage 5: grounded synthesis (LLM or extractive), claim objects
    session/       # ephemeral session store, claim graph, versioning, delta engine
    grounding/     # deterministic ID+span gate, optional NLI gate
    telemetry/     # OpenTelemetry spans + JSONL event log
    api/           # FastAPI app (/v1), WebSocket, auth, rate limits, security headers
    security/      # input validation limits, spotlighting, injection flagging, redaction, integrity checks
    llm/           # thin provider interface: none | gemini | openai-compatible | ollama
  web/             # React + TypeScript + Vite frontend (built into kairos/api/static at image build)
  loadtest/        # Locust scenarios
  .github/workflows/  # CI
  eval/            # replay suite runner, gates, baseline, ablations, stabilisation ceiling, plots
  data/corpus/     # supplied corpus (read-only); may still be the placeholder corpus, see its README
  data/replay/     # dev/ and test/ transcript JSONL + gold labels
  docs/            # ARCHITECTURE_BRIEF.md, EVAL_REPORT.md, TELEMETRY_SCHEMA.md, DEMO_SCRIPT.md, PROJECT_STATE.md,
                   # COMPLIANCE.md (SPEC §18), JUDGE_GUIDE.md (held-out replay), UX_TEST.md, OPERATIONS.md, presentation/
  tests/
```

## 7. Definition of done for the whole project

- `git clone … && docker compose up` on a clean machine brings up the API, demo UI and Jaeger, and `docker compose run kairos make eval` completes the replay suite with no manual steps.
- `docs/EVAL_REPORT.md` shows G1–G6 with measured values and n, baseline vs. ours, ablations A/B/C, three edge-case failures, and the stabilisation-ceiling analysis.
- README, AI_DISCLOSURE.md, ARCHITECTURE_BRIEF.md (≤ 6 pages), TELEMETRY_SCHEMA.md and DEMO_SCRIPT.md exist and match the code.
- CI is green, including security scans, accessibility tests and the MVP replay.
- `docs/COMPLIANCE.md` has evidence for every row of SPEC.md §18, and `kairos replay` works on a transcript in the theme guide's own format.
- `SECURITY.md` threat model is complete and every mitigation links to its test; the red-team attack success rate is reported with n.
- The UI meets the SPEC.md §14 bar in both modes (Assistant and Inspector, including the Race view and Timeline), with Lighthouse, axe and SUS results saved in `docs/`.
- Final commit is tagged `PRISM_GENAI_HACKATHON_Y2026`.
