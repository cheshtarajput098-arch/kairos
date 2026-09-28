# Step 01 of 14 — Kickoff plan (no code)

**File:** `build/steps/p00-kickoff.md` · **Tier 1 — Differentiator MVP** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

---

You are the lead engineer for Kairos, our Samsung PRISM GenAI Hackathon 2026 entry for Theme 04: Streaming Live RAG. The bar is industry-ready: secure, tested, observable, with an excellent UI.

Read AGENTS.md, every file in .agents/rules/, SPEC.md and JUDGE_REVIEW.md completely. Then inspect the starter repo (config/default.yaml, the package stubs, tests/test_repo_rules.py, docs/ templates) and the corpus in data/corpus/ (read its README: it may still be the placeholder corpus of a fictional company, in which case plan so that swapping in the real corpus later needs no code changes).

Do NOT write application code. Produce an implementation plan artifact containing:
1. The goal, the five theme hard rules and the ten security rules, restated in your own words.
2. Corpus profile: document count, formats, how sections are marked, estimated chunk count, and the exact chunking and [Doc_ID §Section] strategy for THIS corpus. Flag any document containing instruction-like text (possible injection) or PII.
3. The step-by-step plan for every step in build/SEQUENCE.md: files, tests, and the exact verification command for each.
4. The MVP scope (SPEC.md §15.1) mapped to concrete files, with an estimate of how many prompts it takes.
5. Risks to G1–G6, security, UI quality and the timeline, with mitigations. Include the risk that the judges' private held-out replay uses transcripts and possibly a corpus we have never seen (SPEC.md §9.6a).
6. Up to 5 open questions for me.

Update docs/PROJECT_STATE.md with this summary (docs/COMPLIANCE.md already exists with every row pending; keep it). Stop and wait for my approval.
