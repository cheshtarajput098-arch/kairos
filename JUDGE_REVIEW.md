# JUDGE_REVIEW.md — Kairos through a Samsung judge's eyes

A mock review of Kairos **as specified in SPEC.md and built through Tier 3**, written the way an R&D judge panel would read it. Use it three ways: the agent checks the build against it (step 14, `build/steps/p11-release.md`), the team rehearses the Q&A section, and every "concern" below links to the spec change that answers it.

This reviews the plan, not a running system. Until it runs, every number here is TBD.

---

## 1. The ten minutes a judge actually spends

What a judge will most likely do, in order. Every step must work first time on a clean machine.

1. Read the README hero: the three headline numbers and a 20-second GIF.
2. `git clone` → `docker compose up` → open `http://localhost:8000`.
3. Press **Play the demo** and watch Story mode run the three scenarios.
4. Flip **Show how it works** and look at the Timeline.
5. Paste one of *their* transcripts into the judge playground, or run `kairos replay` on it.
6. Open `docs/EVAL_REPORT.md` and look for the denominator (n) and the failures.
7. Skim the Architecture Brief for trade-offs, then close the tab.

If step 2 or 5 fails, nothing else matters. That is why G1 and the held-out adapter sit in Tier 1.

---

## 2. What would excite me

1. **"It answered before I finished talking."** Retrieving early is what the theme asks for; *answering* early with verified drafts, measured by a precise Ready-at-End, goes past it. The Answer Canvas makes it visible without any explanation.
2. **The time-travel scrubber.** Dragging to the millisecond before utterance end and seeing a verified draft already on screen is proof, not a claim. Very few hackathon teams will show evidence this strong.
3. **Zero fabricated citations as a guarantee.** A deterministic ID + span gate runs before any model judges anything, and it also gates the LLM rewrite. The "Try to break it" button showing a fabricated citation get blocked live is memorable.
4. **Honest measurement.** Official *and* strict gate numbers side by side, n on every percentage, failures in the report, a stabilisation ceiling that separates "our engineering" from "the language itself", and robustness under ASR noise instead of a limitation footnote. It reads like a research team, not a demo team.
5. **Refine, don't restart, made concrete.** Only the affected sentence rewrites itself; everything else is byte-identical, with a diff to prove it.
6. **It runs offline on a CPU.** For a device-focused organisation, a small local model, a 2-CPU / 4 GB profile and no API dependency speak directly to on-device assistants.

---

## 3. Where I would push — and what the spec now does about it

| # | Concern a judge would raise | Why it matters | What we changed | Where |
|---|---|---|---|---|
| 1 | "Your test set was written by an LLM from your own corpus. Of course entities come early." | Inflated G2 and Ready-at-End would be the first thing an expert suspects. | ≥ 30% of test turns written by outsiders; every turn tagged by source and decisive-word position; ≥ 10 hard late-decisive turns; results split by both; inter-annotator agreement. | SPEC §9.6 |
| 2 | "Is Ready-at-End just a number you made up to look good?" | A new metric invites suspicion of gaming. | Byte-identical definition; post-rollback claims never count; reported at three cadences; paired with rollback exposure (how long wrong drafts were visible). | SPEC §6.4 |
| 3 | "Showing an answer while I'm still talking is distracting, and in voice you can't talk over me." | A product judge will question the user value. | Drafts are never spoken; in voice the benefit is TTFT near zero; on screen it's a user setting. Both the brief and the UI say so. | SPEC §6.4, §14.3 |
| 4 | "Does the local LLM actually run fast enough on a laptop, let alone a phone-class CPU?" | Speed 2 could make answers visibly jump late. | Benchmarked model choice; latency policy that defers or disables Speed 2 with a logged reason; device-class profile at 2 CPUs / 4 GB. | SPEC §1, §6.2, §15.4 |
| 5 | "Will it work on *our* held-out transcripts and corpus?" | The theme says evaluation is private. | Tolerant adapter, clean CLI, any corpus format, a second-corpus sanity check, the judge playground; a default for every unknown in `docs/DECISIONS.md`. | SPEC §9.6a, docs/DECISIONS.md |
| 6 | "Isn't this over-engineered for 'architectural parsimony'?" | The theme explicitly penalises heavy stacks. | Core-vs-harness diagram with core line count and per-stage cost; the harness adds no request-path stages beyond measured security middleware. | SPEC §11a |
| 7 | "Users in India code-mix. How does an English embedder cope?" | An India R&D panel may ask. | Optional code-mixed slice, measured and reported honestly, with the fix named. | SPEC §9.4b |
| 8 | "Two people built all this? Show me it isn't half-finished." | Half-built features cost more than missing ones. | Tiered scope, each tier complete and tagged, a cut list, and no README promise without code. | SPEC §15 |
| 9 | "Your deck says MiniLM; did you actually train it?" | Deck/code mismatch damages trust. | The deck-changes note updates the slides to what was actually built. | build/steps/p11-release.md |

---

## 4. Remarks I would write on the score sheet (if built as specified)

- **Strengths:** "Clear problem framing and a genuinely novel capability (answer-as-you-speak) with a rigorous, non-gameable metric. Grounding guarantees are architectural, not statistical. Exceptionally honest evaluation: official and strict gates, n everywhere, failure analysis, robustness under ASR noise. Strong demo discipline (Story mode, scrubber). Production-minded: security threat model with tests, offline operation, device-class profiling."
- **Weaknesses to expect:** "Rule-based controller and decomposer may still struggle on very disfluent speech; results on external human-written turns are lower than on drafted ones (if true, report it). The Speed-2 rewrite adds latency variance on CPU. Live ASR is only simulated in the measured results. English-first retrieval."
- **Would ask to see:** "Ready-at-End on the human-written turns at 1× cadence; rollback exposure; the device-profile numbers; one failure case end to end in the telemetry."

---

## 5. Likely Q&A — rehearse these answers

Fill each `<…>` from `runs/` before the presentation. Never quote a number you haven't measured.

1. **"What's new here compared with Stream RAG?"** Stream RAG predicts tool queries during speech and trains a model to do so. We answer during speech, with no training, a deterministic grounding gate and a commit/rollback protocol, and we measure the ceiling that any such system can reach.
2. **"Define Ready-at-End precisely."** The share of final claims byte-identical to a verified draft that existed at utterance end; rolled-back claims never count. Ours: `<value>` at 1× (n=`<n>`), `<value>` on externally written turns.
3. **"What happens when a draft is wrong?"** It's rolled back and re-synthesised from new evidence; it was visibly provisional, and rollback exposure was `<ms>` on average.
4. **"How do you guarantee zero fabricated citations?"** Every cited ID must be in this session's retrieved set and the quoted span must appear in that chunk, checked in code before emission, including for the LLM rewrite. Fabricated IDs on the test set: 0 (n=`<claims>`).
5. **"Why not just use a bigger LLM?"** Cost, latency and offline operation. The cost-to-performance table shows what each component buys; the rewrite is optional and gated.
6. **"Your controller is rule-based. Why not learned?"** We have both (Ablation A). The curve shows where each operating point sits; we ship `<arm>` because `<reason from data>`.
7. **"How does it degrade with real ASR?"** At 10% WER, G2 is `<value>` and G3 `<value>` (clean: `<value>`/`<value>`); the live mic path is demo-only and labelled as such.
8. **"Could this run on a phone?"** Under 2 CPUs / 4 GB: TTFT `<value>`, peak memory `<value>`; Speed 2 `<stays in budget / is deferred>`.
9. **"What was your worst failure?"** Late disambiguation: the decisive word came last, so lead time is 0 and we report it as 0 (`<k>` turns); the stabilisation ceiling shows no system could have done better there.
10. **"Is anything hard-coded to the benchmark?"** No. There's an import boundary test, a grep audit, suggested questions come from corpus headings, and the adapter and thresholds were checked against a second corpus.
11. **"Where does user data go?"** Nowhere. Sessions are in memory and cleared on end, logs redact PII and don't store raw text by default, and there are no accounts or history.
12. **"What would you build next as a PRISM worklet?"** Live ASR end to end with measured controller cost; multilingual embeddings; publishing the stabilisation measurements as a reusable benchmark.

---

## 6. UI rating (of the specification)

| Aspect | Rating | Comment |
|---|---|---|
| Concept and clarity | 9.5 / 10 | Two modes solve the "customer vs judge" tension; the Answer Canvas and colour threading make the differentiator self-explanatory. |
| Visual direction | 9 / 10 | "Calm Precision" suits a premium assistant; colour carries meaning. Needs real design iteration to land. |
| Interaction design | 9 / 10 | Every state is event-driven, reduced-motion handled, honest gaps built in. Risk: too much motion at once; keep it slow and rare. |
| Accessibility and quality gates | 9 / 10 | WCAG 2.2 AA, axe, Lighthouse, keyboard map, aria-live per section. |
| Evidence of UX quality | 8.5 / 10 | SUS + first-impression test with n=5 is honest but small; say so. |
| **Spec overall** | **~9 / 10** | |
| **Likely built result** | **7.5–9 / 10** | Depends almost entirely on the polish loops in Prompt 9b and on cutting breadth for depth. An AI agent will build the features; making them *feel* premium takes several rounds of your own review. |

Biggest UI risks: Inspector sprawl (six screens) diluting polish; animation jank on low-end laptops; Speed-2 text swaps looking jumpy. The UI rule "polish beats breadth" and the cut list exist for exactly this.

---

## 7. Projected score if built well through Tier 3

| Criterion (unconfirmed weights) | Score |
|---|---|
| Working prototype (30%) | 9.0 |
| Technical depth (25%) | 9.2 |
| Innovation (20%) | 9.5 |
| Relevance to theme (15%) | 9.5 |
| Presentation & documentation (10%) | 9.0 |
| **Weighted** | **≈ 9.2** |

This is a judgement, not a guarantee. It falls quickly if G1 fails on a clean machine, if the held-out format breaks the adapter, if the test set looks self-serving, or if the demo stutters. Those four are the real risks. Everything in Tier 1 exists to remove them.
