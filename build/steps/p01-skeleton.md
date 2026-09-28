# Step 02 of 14 — Skeleton, packaging, config, telemetry, CI and security baseline

**File:** `build/steps/p01-skeleton.md` · **Tier 1 — Differentiator MVP** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

---

The starter repo already has config/default.yaml, .gitignore, .env.example, package stubs, a starter CI job and tests/test_repo_rules.py. Keep and extend them; don't recreate or weaken them, and keep tests/test_repo_rules.py passing.

Implement Prompt 1 following AGENTS.md, .agents/rules/10-security.md and .agents/rules/20-engineering.md (§3, §3A, §6), and SPEC.md §1, §2, §8, §13.3.

Build:
- pyproject.toml managed by uv with a committed uv.lock (hash-pinned); Python 3.11.
- The repository layout from .agents/rules/20-engineering.md §6 with importable packages, including kairos/security and an empty web/ placeholder.
- config/default.yaml (already present — check it against SPEC.md and add anything missing) with EVERY threshold and limit named in SPEC.md (controller, decomposer, retrieval, fusion, grounding, session, budgets, security limits: max message bytes, chunks/turn, words/turn, sessions, rate limits, deadlines, token caps), plus model names, revisions and SHA-256s. A typed Pydantic Settings loader that validates at startup and fails fast.
- Pydantic v2 strict models for every contract in SPEC.md §2 with `extra="forbid"`.
- kairos/telemetry: OpenTelemetry (OTLP, disabled cleanly when no collector) + JSONL event writer to runs/<run_id>/events.jsonl, with PII redaction (emails, phones, card-like numbers) and text logging OFF by default.
- kairos/llm: provider interface with none | gemini | openai_compatible | ollama. "none" is default and needs no network. The interface exposes only generate_json(schema, messages, limits) — no tools, no function calling.
- kairos/api: FastAPI app under /v1 with /v1/health and /v1/ready, a request_id middleware, a consistent error envelope, security-headers middleware (CSP etc. from SPEC.md §13.3), a CORS allow-list, and structured JSON logging.
- Dockerfile: multi-stage, python:3.11-slim, non-root user, model weights downloaded and SHA-verified at build. docker-compose.yml: kairos (:8000) with read_only, tmpfs, cap_drop ALL, no-new-privileges, healthcheck; jaeger bound to 127.0.0.1.
- Makefile: install, test, lint, typecheck, index, replay, eval, serve, security, web.
- .github/workflows/ci.yml: ruff, mypy --strict, pytest + coverage gate, bandit, pip-audit, gitleaks, docker build, Trivy scan (fail on HIGH/CRITICAL). .pre-commit-config.yaml mirroring the fast checks.
- .env.example, .gitignore, LICENSE (MIT, per docs/DECISIONS.md; include both team members' names), CHANGELOG.md.
- Tests: config validation, schema round-trips, unknown fields rejected, error envelope has no stack trace, security headers present, redaction works.

Verification: `make lint typecheck test security` and `docker compose up -d && curl localhost:8000/v1/health`, paste the summarised output. Update docs/PROJECT_STATE.md.
