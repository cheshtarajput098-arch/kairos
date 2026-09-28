# AGENTS.md — Kairos (Samsung PRISM GenAI Hackathon 2026, Theme 04: Streaming Live RAG)

Every agent working in this repository reads this file before starting any task. It is the source of truth. `SPEC.md` holds the full design; this file holds the rules that must never be broken.

## 1. What we are building

Kairos is an event-driven **Streaming Live RAG engine**. It consumes timestamped transcript chunks, decides per chunk whether to WAIT, RETRIEVE or NO_RETRIEVAL (suppress), decomposes compound utterances into sub-queries, retrieves from a supplied corpus with hybrid search, synthesises a grounded answer with per-claim citations, refines answers in place when late constraints arrive, and emits full telemetry.

**What makes us different** (SPEC.md §0, items 7–9): Kairos *answers* while you speak, not just retrieves (drafts verified before the utterance ends, measured as Ready-at-End); its answers are two-speed (an instant grounded extract, then a fluent rewrite that must pass the same grounding gate); and it is measured under real-speech noise (ASR revisions, disfluencies), not only on clean text. Protect these three in every decision.

We are judged on six acceptance gates (G1–G6, see SPEC.md §9) and on the hackathon's deliverables. Everything we build must move a gate or a deliverable. If it moves neither, do not build it. **The judges run their own private held-out replay**, so the system must work on transcripts and corpora we have never seen (SPEC.md §9.6a). Every requirement in the theme guide is tracked in SPEC.md §18 / `docs/COMPLIANCE.md`, and no row may be left without evidence.

## 2. Hard rules (graded by the theme; violating any one can disqualify us)

1. **Corpus isolation.** Every factual claim comes from the supplied corpus only. No web search, no scraping, no external knowledge API, no parametric-memory answers at runtime. The generator prompt must forbid outside knowledge, and the grounding gate must drop any claim not supported by a retrieved chunk.
2. **No hard-coding / no precomputation.** Never embed test prompts, test queries, gold answers, canned responses or per-query branches in application code. No `if "Pune" in text`. No lookup tables keyed on benchmark utterances. Test data lives only under `data/replay/` and `eval/`, and application code under `kairos/` must never import from them.
3. **Rigorous grounding.** Every claim carries at least one `[Doc_ID §Section]` citation that exists in this session's retrieved set. If evidence is missing, emit an explicit uncertainty statement or a targeted clarification request — never a guess.
4. **Session-bound state.** Memory is ephemeral and scoped to one session ID. No cross-session profiles, no persistent user store, no writing session content to disk except telemetry logs. Clear the session store on session end.
5. **Architectural parsimony.** No LangChain, LangGraph, LlamaIndex, CrewAI, AutoGen or any agent framework. One Python asyncio event loop, five stages, one session store. Every added component needs a line in `docs/ARCHITECTURE_BRIEF.md` justifying its latency and compute cost.

## 4. Honesty rules (judges check these)

- **Never fabricate a metric.** Every number in README, reports, dashboard or slides is read from a file produced by `make eval`. If a number is not measured yet, write `TBD`, not an estimate.
- **Report failures.** Edge-case failures go into the report with telemetry evidence, not into a footnote.
- **Report the denominator.** Every percentage is shown with its n.

## 5. How to work (agent workflow)

1. **Plan first.** For any task larger than one file, write an implementation plan artifact before editing code. This team works in **autopilot** (`.agents/rules/40-autopilot.md`): write the plan, then proceed without waiting for approval, and log decisions in `docs/DECISIONS.md`.
2. **Tests before or with code.** Every module gets unit tests in `tests/`. A task is not done until `make test` passes.
3. **Verify with commands, not narrative.** Finish every task by running the relevant command (`make test`, `make replay`, `make eval`, `docker compose up`) and pasting the real output summary.
4. **One reviewable slice at a time.** Do not touch modules outside the current phase without asking.
5. **Update `docs/PROJECT_STATE.md`** at the end of every task: what was done, what is left, known issues.
6. **Never commit secrets.** API keys go in `.env` (git-ignored); ship `.env.example`.

## More rules (always on)

The rest of the rules live in `.agents/rules/` so that each file stays under Antigravity's rules-file size limit. They are just as binding as this file:
- `.agents/rules/10-security.md` — the ten security rules.
- `.agents/rules/20-engineering.md` — engineering, industry-readiness, scope tiers, repo layout, definition of done.
- `.agents/rules/30-ui.md` — the UI quality bar.
- `.agents/rules/40-autopilot.md` — how to work unattended: one step per `/build-next` run, decide from `docs/DECISIONS.md`, never block, never fake human work.

The build order is `build/SEQUENCE.md`; progress lives in `docs/PROJECT_STATE.md`.

If any of those files is missing from your context, read it before starting work.
