# Step 04 of 14 — Replay harness and retrieval controller

**File:** `build/steps/p03-controller.md` · **Tier 1 — Differentiator MVP** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

---

Implement Prompt 3 following SPEC.md §2.2 and §4.

Build:
- kairos/stream: replay reader for data/replay/**/*.jsonl emitting chunk events on a virtual clock (cadence multiplier 0.75x/1x/1.5x) into one asyncio loop, plus an instantaneous mode that preserves timestamps for fast eval. Enforce the per-turn limits from config. Support partial revisions (SPEC.md §2.2: `partial`, `revises`): on a revision, recompute the prefix, emit `transcript_revised`, and let the controller cancel speculative work whose entities disappeared.
- kairos/controller: the rule-based arm exactly as SPEC.md §4.2–4.3 (entity_set + saturation, embedding drift with the same BGE model, syntactic_open, optional BM25 probe stability, presentation_intent), deciding WAIT / RETRIEVE / SUPPRESS with a machine-readable reason. All thresholds from config.
- Reversible speculation (SPEC.md §4.5): provisional retrievals keyed by prefix hash, cancelled when the entity set changes, per-turn speculative budget, telemetry status completed | cancelled | reused_cache.
- SUPPRESS requires a prior answer in the session. Presentation-intent uses a generic cue lexicon plus an embedding-similarity classifier trained on generic examples you write in eval/controller_train/ — never on data/replay/test.
- Every decision logged with its feature vector.

Also draft data/replay/dev/ (≥ 15 turns: compound, late-constraint, presentation-only, single, out-of-corpus, plus gold.jsonl). data/replay/demo/ already holds the three theme scenarios for the placeholder corpus; if data/corpus now holds the real corpus, rewrite them against it in the same format. Put a README in each folder saying "DRAFT — needs human review".

Tests: WAIT on an entity-less prefix; RETRIEVE once entities stabilise; cancellation when a later chunk changes the entity; SUPPRESS on a reformat request after a prior answer; zero vector calls on SUPPRESS (spy); budget exhaustion degrades to batch.

Verification: `make test` and `make replay SPLIT=dev` printing each turn's decision timeline and lead time. Update PROJECT_STATE.md.
