# Step 05 of 14 — Multi-intent decomposer

**File:** `build/steps/p04-decomposer.md` · **Tier 1 — Differentiator MVP** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

---

Implement Prompt 4 following SPEC.md §5.

Build kairos/decompose with two modes behind config:
- offline rule-based splitter (default): split on coordinating conjunctions and list commas only where each clause has a content noun; inherit shared context (location, head entity, numbers, dates) into every leg.
- LLM mode: fixed JSON schema {"sub_queries":[{"leg_id","text","entities"}]}, temperature 0, schema-validated, user text passed only inside a delimited <user_utterance> block, falls back to offline mode on any error or timeout. No benchmark text in the prompt.
Before splitting (both modes): generic disfluency normalisation from SPEC.md §5 (fillers, repetitions, self-repairs such as "in Pune — no, Mumbai"), with the rules in config and tests on synthetic disfluent sentences you write (never test transcripts).
Both: embedding dedupe (cosine > 0.9), hard cap 4, stable leg IDs per turn, INCREMENTAL diffing (new intent → append leg; refined intent → mutate that leg and reissue only it).

Wire Stage 1 → Stage 2 → Stages 3/4 so legs retrieve in parallel as soon as they resolve.

Tests: a compound example adapted to our corpus yields 3 legs carrying the shared context; near-duplicates collapse; cap enforced; refinement reissues only the changed leg (assert retrieval call counts); malformed LLM JSON falls back cleanly.

Verification: `make test` and `make replay SPLIT=dev` showing legs per turn with first-dispatch timestamps. Update PROJECT_STATE.md.
