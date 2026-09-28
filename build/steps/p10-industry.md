# Step 13 of 14 — CI, performance, operations

**File:** `build/steps/p10-industry.md` · **Tier 4 — Hardening** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

**Tag at the end of this step:** `v0.9-hardened` (create it locally with `git tag -a v0.9-hardened -m "CI, performance, operations"`; never push).

---

Act as a staff engineer preparing Kairos for production review.

- CI: make sure .github/workflows/ci.yml runs every check in .agents/rules/20-engineering.md §3A in parallel jobs with caching, uploads coverage, the SBOM, the Lighthouse report and the eval report as artifacts, and gates merges on all of them. Add a badge row to README with real statuses.
- Performance: Locust scenario with 1 and 10 concurrent streaming sessions on a laptop CPU (add 25 only if time allows); report p50/p95 turn latency, TTFT, error rate, CPU and memory. Profile the top latency contributor from the telemetry spans and fix it without reducing dev recall.
- Device-class profile (SPEC.md §15.4): rerun the test replay with docker compose limits of 2 CPUs and 4 GB RAM; report TTFT, Ready-at-End, peak memory and the Speed-2 budget outcome in OPERATIONS.md and the Results dashboard.
- Resilience: graceful shutdown cancels in-flight tasks; LLM provider outage falls back to extractive mode with a visible UI badge; index-load failure keeps /v1/ready false with a clear log line. Add tests for each.
- docs/OPERATIONS.md: architecture overview, full config reference generated from the Settings model, SLOs (e.g. p95 TTFT, availability), runbook for the top 5 failure modes, load-test results, and how to rotate the token secret and API keys.
- Code quality pass: remove dead code, make docstrings match behaviour, and make sure no module exceeds reasonable complexity (ruff C901).

Verification: CI green with all artifacts attached; paste the load-test table and resilience test results. Update PROJECT_STATE.md and CHANGELOG.md, then tag v0.9-hardened (do not push).
