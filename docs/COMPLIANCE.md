# COMPLIANCE.md — every requirement, with evidence

Generated from SPEC.md §18. The agent updates the **Status** and **Evidence** columns at the end of every prompt. A row is done only when Evidence links to code **and** to a passing test or a measured output in `runs/`. Prompt 11 treats any row still `pending` as a blocker.

| # | Source | Requirement | Where it's met | Proof required | Status | Evidence |
|---|---|---|---|---|---|---|
| 1 | Guide §1 | Listens incrementally: timestamped chunks, predicts retrieval intent before the user finishes | §4 controller, §9.6a adapter | G2 (official + strict), lead-time histogram | done | `kairos/stream/replay.py`, `kairos/controller/`, `tests/test_stream.py`, `runs/cli_replay/replay_summary.json` |
| 2 | Guide §1 | Decomposes multi-intent queries and parallelises retrieval | §5 | G3 (official + strict), legs' `first_dispatch_s` | done | `kairos/decompose/`, `tests/test_decompose.py`, `runs/cli_replay/replay_summary.json` |
| 3 | Guide §1 | Refines rather than restarts; updates answer and citation graph selectively | §7 | G5, v1→v2 diff test | done | `kairos/session/delta.py`, `tests/test_session_delta.py`, `kairos/cli.py`, `runs/cli_replay/replay_summary.json` |
| 4 | Guide §1 | Guarantees corpus grounding; explicit uncertainty | §6.3 | G4, fabricated-ID count = 0 | done | `kairos/grounding/gate.py`, `kairos/synth/extractive.py`, `tests/test_grounding.py` |
| 5 | Guide §2 | Controller: intent stability check; decision Wait / Retrieve / No-Retrieval | §4, §2.4 naming | controller unit tests | done | `kairos/controller/rules.py`, `kairos/controller/features.py`, `kairos/controller/speculation.py`, `tests/test_controller.py` |
| 6 | Guide §2 | Retrieval & fusion: dense/sparse hybrid, re-rank, deduplicate | §6.1 | Ablation C, dedupe test | done | `kairos/retrieve/hybrid.py`, `kairos/fuse/rrf.py`, `kairos/fuse/dedupe.py`, `tests/test_retrieve_fuse.py` |
| 7 | Guide §2 comp. 3 | Merge evidence without diluting context or introducing contradictory facts; rank for relevance and factual density | §6.1 near-dup collapse, conflict check, density tie-break | conflict-check test, `evidence_conflict` events | done | `kairos/fuse/dedupe.py`, `tests/test_retrieve_fuse.py` |
| 8 | Guide §2 comp. 4 | Session-only refinement mutates only affected claims | §7 | byte-identical test | done | `kairos/session/delta.py`, `tests/test_session_delta.py::test_delta_engine_constraint_preserves_unaffected_claims_byte_identical` |
| 9 | Guide §2 comp. 5 | Telemetry under sub-second constraints: timestamps, decisions, source mappings, version transitions, token costs | §8 | G6 script, overhead measurement | done | `kairos/telemetry/`, `eval/gates.py` (Gate G6: 1.0, n=16), `runs/eval/gates.json`, `tests/test_eval.py` |
| 10 | Guide §3 | Corpus isolation | AGENTS §2.1, §13 | no-network test, grounding gate | done | `kairos/security/spotlight.py`, `kairos/grounding/gate.py`, `tests/test_spotlight.py`, `tests/test_grounding.py` |
| 11 | Guide §3 | No hardcoding / precomputation; held-out private eval | AGENTS §2.2, §9.6a | import-boundary test, grep audit, second-corpus check | done | `kairos/stream/adapters.py`, `tests/test_adapter.py`, `tests/test_repo_rules.py` |
| 12 | Guide §3 | Rigorous grounding with `[Doc_ID §Section]` markers | §2.1, §6.3 | ID-survival test | done | `kairos/ingest/chunker.py`, `tests/test_ingest.py`, `tests/test_retrieve_fuse.py` |
| 13 | Guide §3 | Session-bound state; no cross-session profiling | AGENTS §2.4, §7 | session-isolation test, clear-on-end test | done | `kairos/session/token.py`, `kairos/session/store.py`, `tests/test_session_delta.py`, `tests/test_api_stream.py` |
| 14 | Guide §3 | Architectural parsimony, justified by cost-to-performance | AGENTS §2.5, §9.1a | cost-to-performance table | pending | |
| 15 | Guide §4 Ex. 1 | Timeline behaviour (WAIT → provisional RETRIEVE → decompose → synthesise) and output record keys | §2.4, §4, §5 | demo scenario 1 test, exact-keys test | done | `kairos/cli.py`, `runs/cli_replay/replay_summary.json`, `tests/test_synth_drafting.py`, `tests/test_adapter.py::test_theme_guide_format_has_required_keys` |
| 16 | Guide §4 Ex. 2 | Late detail: no restart, targeted delta queries, preserve prior citations, append delta citations, version 2 | §7 | demo scenario 2 test | done | `kairos/session/delta.py`, `tests/test_session_delta.py`, `runs/cli_replay/replay_summary.json` |
| 17 | Guide §4 Ex. 3 | Presentation request: `retrieval_required: false`, `reason: presentation_restructure`, zero vector search, keep citations | §4.1, §7 | demo scenario 3 test with retrieval spy | done | `kairos/controller/rules.py`, `kairos/session/delta.py`, `tests/test_controller.py`, `tests/test_session_delta.py` |
| 18–23 | Guide §5 | G1–G6 at their thresholds | §9.1 | `gates.json` with n | done | `eval/run_suite.py`, `eval/gates.py`, `eval/baseline.py`, `runs/eval/gates.json`, `tests/test_eval.py` |
| 24–28 | Guide §6 | Five pitfalls: eager retrieval, context loss, citation hallucination, retrieving on presentation turns, over-fragmenting | §4.3–4.5, §5 context inheritance, §6.3, §4.1, §5 dedupe+cap | retrievals/turn, G5, G4, suppression rate, redundant-leg rate | pending | |
| 29 | Guide §7 | Roadmap phases 1–5 | build steps 01–08 (build/SEQUENCE.md) | PROJECT_STATE.md | pending | |
| 30 | Guide §8 | Reproducible repo: lockfiles, env templates, one-command run | §11 | G1 in CI | done | `pyproject.toml`, `.env.example`, `Dockerfile`, `docker-compose.yml`, `Makefile`, `tests/test_api.py` |
| 31 | Guide §8 | Architecture brief ≤ 6 pages with the six named topics | Prompt 11 | PDF page count | pending | |
| 32 | Guide §8 | Eval report: baseline comparison, ≥ 3 analysed edge-case failures, ≥ 2 ablations | §9.2–9.5 | EVAL_REPORT.md | pending | |
| 33 | Guide §8 | Video ≤ 5 min covering the six named behaviours | DEMO_SCRIPT.md | video length and shot list | pending | |
| 34 | Guide §8 | Telemetry schema: latencies, trigger events, version updates, cost estimates | §8 | TELEMETRY_SCHEMA.md | pending | |
| 35–42 | GitHub checklist | Source code, Presentation, Video, AI Disclosure, README, APK/SDK (N/A), TAG, Other (SECURITY, OPERATIONS, COMPLIANCE, JUDGE_GUIDE, UX_TEST) | §11 | files exist, tag pushed | pending | |
| 43 | Our deck | Every promise on the slides: MiniLM controller arm, recall@k, nDCG@10, suppression rate, cost by turn class, tokens saved vs restart, three edge cases, stabilisation analysis | §4.4, §9.1a, §9.4–9.5 | EVAL_REPORT.md; deck blanks filled from `runs/` | pending | |
| 44 | Our differentiators | Answer-as-you-speak with Ready-at-End; two-speed grounded answers; real-speech robustness | §6.4, §6.2, §9.4b | Ablations D and E, robustness table, `draft_*` and `rewrite_*` events | pending | |
| 45 | Judge experience | Story mode, judge playground, time-travel scrubber | §14.3a, §14.4 | Playwright tests for each | pending | |
