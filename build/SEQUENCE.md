# SEQUENCE.md — the build order for autopilot

`/build-next` runs the first step below whose status is not `done`, then marks it `done` in `docs/PROJECT_STATE.md`. Steps must run in this order; each tier ends with a local git tag. Stopping after any tier leaves a complete, submittable project.

| # | Step file | Tier | What it builds | Tag when done |
|---|---|---|---|---|
| 01 | `build/steps/p00-kickoff.md` | Tier 1 | Kickoff plan (no code) |  |
| 02 | `build/steps/p01-skeleton.md` | Tier 1 | Skeleton, packaging, config, telemetry, CI and security baseline |  |
| 03 | `build/steps/p02-index.md` | Tier 1 | Corpus ingest, integrity and hybrid index |  |
| 04 | `build/steps/p03-controller.md` | Tier 1 | Replay harness and retrieval controller |  |
| 05 | `build/steps/p04-decomposer.md` | Tier 1 | Multi-intent decomposer |  |
| 06 | `build/steps/p05-synthesis-session.md` | Tier 1 | Synthesis, grounding gate, drafting, session and delta engine |  |
| 07 | `build/steps/p06-mvp.md` | Tier 1 | Differentiator MVP end to end | `v0.1-mvp` |
| 08 | `build/steps/p07-evaluation.md` | Tier 2 | Test set, gates, baseline, ablations, stabilisation, robustness | `v0.5-proof` |
| 09 | `build/steps/p07b-generative.md` | Tier 3 | Two-speed answers with a local LLM |  |
| 10 | `build/steps/p09a-ui-design.md` | Tier 3 | UI design plan |  |
| 11 | `build/steps/p09b-ui-build.md` | Tier 3 | UI build and polish | `v0.8-polish` |
| 12 | `build/steps/p08-security.md` | Tier 4 | Security hardening and red-team evaluation |  |
| 13 | `build/steps/p10-industry.md` | Tier 4 | CI, performance, operations | `v0.9-hardened` |
| 14 | `build/steps/p11-release.md` | Tier 5 | Documentation, disclosure, final audit, release | `PRISM_GENAI_HACKATHON_Y2026` |

Optional, human-triggered: `build/steps/p09c-usability-results.md` (after the 5-person usability test).

**Naming note:** step texts refer to each other by their original prompt numbers ("Prompt 7b", "Prompt 11"); the file names keep those numbers (`p07b`, `p11`), so the match is direct.
