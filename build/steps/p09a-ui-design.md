# Step 10 of 14 — UI design plan

**File:** `build/steps/p09a-ui-design.md` · **Tier 3 — Generative polish + UI** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

---

Act as a principal product designer who has shipped consumer voice assistants. Read SPEC.md §14 in full.

Design Kairos so a non-technical customer loves it within 30 seconds and a judge sees the engine within 10. The product promise: "It's already looking while you're still talking — and it only tells you what it can prove."

Produce a design plan artifact containing:
1. Visual direction: fully develop the default "Calm Precision" direction (SPEC.md §14.3a) and two credible alternatives. For each: mood, palette from the token rules, type, and one hero-screen mock as HTML showing the Answer Canvas mid-utterance (ghost, drafting and settled sections at once). Recommend one and explain why.
1b. The six signature interactions in SPEC.md §14.3a (Answer Canvas, intent colour threading, "Ready when you stopped", refinement as an edit, two-speed text, honest gap cards) plus Story mode, the judge playground and the time-travel scrubber: for each, a frame-by-frame storyboard of states, what event drives each change, and its reduced-motion version.
2. User journeys as step-by-step storyboards for: first run; a compound question by voice; adding a late detail ("actually, it was international"); "as bullets"; opening a source; an out-of-scope question; mic permission denied; connection lost.
3. For every screen in both modes: a wireframe at 360 px and 1440 px, the component tree, and the empty / loading / streaming / uncertain / updated / error state of each component.
4. The complete microcopy list (every label, hint, status and error) in plain, warm language, ready for strings.en.json.
5. Motion spec: the listening orb, the "Already searching…" chip, section streaming, in-place update highlight, drawer open, all with reduced-motion fallbacks.
6. An accessibility plan: focus order, aria-live strategy, keyboard shortcuts, contrast check of every token pair.
7. How Inspector mode's Timeline, Race view and time-travel scrubber make early retrieval, drafting before utterance end, parallel legs and v1→v2 refinement obvious on a projector.
8. The 20-second first impression: what a stranger sees when Story mode starts, and why they will say "it answers while I'm talking".

No Samsung logos, product names or trade dress; original Kairos branding only. Stop and wait for my choice of direction.
