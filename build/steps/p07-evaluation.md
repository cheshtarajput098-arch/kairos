# Step 08 of 14 — Test set, gates, baseline, ablations, stabilisation, robustness

**File:** `build/steps/p07-evaluation.md` · **Tier 2 — Proof** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

**Tag at the end of this step:** `v0.5-proof` (create it locally with `git tag -a v0.5-proof -m "Test set, gates, baseline, ablations, stabilisation, robustness"`; never push).

---

Implement SPEC.md §9 in full. Every number must be computed from run output files — never typed in.

- eval/make_transcripts.py: drafts test turns from the corpus (≥ 60; mix per SPEC.md §9.6) into data/replay/test/ with gold labels marked "unreviewed" and `source: llm_drafted`. Also write eval/external_turns/INSTRUCTIONS.md, a one-page brief I can hand to classmates so they write ≥ 30% of the test turns (`source: human_external`) without seeing the pipeline. Tag every turn with the decisive-word position (early / middle / last third). I will review and fix every label by hand before freezing — produce a review checklist for me and an inter-annotator agreement script (SPEC.md §9.6).
- A freeze script that hashes data/replay/test/ and config/default.yaml; eval fails if either changes after the freeze.
- gates.py: G1–G6 with n, computing BOTH the official theme-guide definition and our strict variant for each gate (SPEC.md §9.1). Never report only the flattering one. Also split every gate and Ready-at-End by turn source and by decisive-word position, and report Ready-at-End at all three cadences using the exact definition in SPEC.md §6.4.
- metrics.py: every metric in SPEC.md §9.1a (recall@k, nDCG@10, TTFT, e2e latency, per-leg retrieval latency, false-trigger rate, suppression rate, retrievals per turn, redundant-leg rate, cost by turn class, savings vs a restart baseline, and the cost-to-performance table).
- Held-out readiness (SPEC.md §9.6a): write docs/JUDGE_GUIDE.md; run the dev replay against a second, unrelated public document set and record whether thresholds generalise; test the adapter against at least four transcript format variants.
- baseline.py, ablations.py (A: rule vs model controller as a curve; B: end-of-utterance vs incremental decomposition; C: dense-only vs hybrid, RRF k=10 vs 60, rerank on/off).
- controller_model.py: trains the model-based controller on DEV prefixes with corpus-derived labels (1 if the prefix top-k already contains the full-utterance top-k answer chunks), exports it and plugs it into Ablation A.
- stabilisation.py: per test turn t_sc, t_suf, phi, volatility V, and H = min(L, max(0,(n − t*)/δ)) using measured retrieval latency and replay cadence; plots trigger point vs t_suf and the gap distribution (method from arXiv:2606.20113).
- Edge cases (late disambiguation, contradiction, evidence absent) present in test, each with a telemetry excerpt in the report.
- eval/asr_noise.py + robustness run (SPEC.md §9.4b): seeded noisy variants of the frozen test set at WER 5% and 10%, with partial revisions and injected disfluencies; report official and strict G2, G3, false-trigger rate, Ready-at-End and G4 for clean vs each noise level as a table and a line chart.
- Race run: execute baseline and Kairos on every test turn and record measured per-turn time saved (SPEC.md §9.2); expose it at /v1/results for the Race view and the "Ready when you stopped" line.
- build_report.py renders docs/EVAL_REPORT.md (gates, baseline vs ours, ablations, stabilisation, edge cases, limitations); anything missing renders TBD. Expose the same data at GET /v1/results.

Update the evidence column in docs/COMPLIANCE.md for every row this prompt covers.

Verification: `make eval` on the frozen test split; paste gates.json (official and strict) and the headline table. For any gate below target, diagnose from events.jsonl and propose the smallest fix, tuning on dev only — never edit the test set to pass. Update PROJECT_STATE.md, then tag v0.5-proof (do not push).
