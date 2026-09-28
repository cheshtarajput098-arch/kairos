# Step 12 of 14 — Security hardening and red-team evaluation

**File:** `build/steps/p08-security.md` · **Tier 4 — Hardening** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

---

Act as an application security engineer. Implement SPEC.md §13 in full and write SECURITY.md.

1. Threat model: STRIDE per trust boundary (SPEC.md §13.1) plus a table mapping every control to the current OWASP GenAI LLM Top 10 (keep the 2025 IDs LLM01–LLM10 as a cross-reference). Every row links to the test that proves it.
2. Close gaps: verify each control in §13.2 and §13.3 exists in code. Add anything missing: model-file SHA verification at startup, a circuit breaker on the LLM provider, token caps, max connection lifetime, Permissions-Policy scoped to the demo page, CSP with no unsafe-inline, SBOM generation (syft → CycloneDX) in CI.
3. Red-team set: data/replay/redteam/ with ≥ 30 turns (direct injection, system-prompt extraction, out-of-corpus bait, PII, oversized and malformed messages) and a separate poisoned test index with ≥ 10 injected chunks (instruction payloads, keyword stuffing, HTML/script payloads, zero-width hidden text). Never used for tuning.
4. eval/redteam.py: reports attack success rate with and without spotlighting (in LLM mode), fabricated-citation count (must be 0), correct refusal/uncertainty rate, and security-middleware latency overhead. Add to EVAL_REPORT.md and the /v1/results endpoint.
5. Fuzzing: Hypothesis property tests on WS message parsing and the chunker; Locust abuse scenario (flood, huge messages, many sessions) showing limits hold and the service stays healthy.
6. Scans: run bandit, pip-audit, gitleaks, Trivy and npm audit; fix or document every finding with justification in SECURITY.md.

Verification: `make security test` plus `make redteam`; paste the ASR table, scan summaries and fuzzing results. Any control without a passing test counts as missing. Update PROJECT_STATE.md.
