# Step 07 of 14 — Differentiator MVP end to end

**File:** `build/steps/p06-mvp.md` · **Tier 1 — Differentiator MVP** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

**Tag at the end of this step:** `v0.1-mvp` (create it locally with `git tag -a v0.1-mvp -m "Differentiator MVP end to end"`; never push).

---

Deliver the Differentiator MVP exactly as SPEC.md §15.1. Do not start anything from later tiers.

Build:
- web/: React + TypeScript strict + Vite + Tailwind with the final design tokens (SPEC.md §14.2, "Calm Precision" direction in §14.3a) and the two-mode structure (§14.1):
  - Assistant mode (§14.3, §14.3a): live transcript with intent colour threading; "Already searching…" chip driven by real retrieval_started events; the **Answer Canvas** (ghost section per detected intent → drafting → settled at utterance end, rolled-back sections dissolve and refill); numbered source pills with a passage popover; amber "couldn't find" card; in-place refinement with "Updated · v2 · See what changed"; quick actions Shorter / As bullets (no retrieval); the "Ready when you stopped" line, shown only when Ready-at-End > 0.
  - Inspector mode (§14.4): Timeline (chunks, decision markers, leg Gantt bars in intent colours, draft markers, utterance-end line, shaded lead time), Answer panel with [Doc_ID §Section] chips and a v1/v2 diff, Telemetry panel.
  - A "Show how it works" toggle that keeps the session running.
  - **Story mode**: a "Play the demo" button that autoplays the three theme scenarios (adapted to our corpus, from data/replay/demo/) through the real pipeline with captions from strings.en.json.
  It talks to the API over the authenticated WS. Text is rendered as text only — never as HTML.
- kairos/stream/adapters.py + the `kairos replay` / `kairos index` CLI from SPEC.md §9.6a, with a test that replays a transcript written in the theme guide's Example 1 table format and checks the output record has the guide's exact keys.
- Multi-stage Dockerfile stage that builds web/ with Node and copies dist/ into kairos/api/static; FastAPI serves it at /. No Node at runtime and no CDN.
- eval/run_suite.py + eval/gates.py + eval/baseline.py minimal versions computing official G1–G6 with n plus Ready-at-End on the dev split; `make eval` runs offline with no API key.
- CI job "mvp-replay": builds the image, replays the three demo scenarios headless, and asserts expected controller decisions, leg counts, at least one committed draft before utterance end in scenario 1, a version bump on the late-constraint turn, and zero retrievals on the suppression turn.
- README quick start with a 20-second GIF of Story mode.

Verification: from a fresh clone, `docker compose up`, open http://localhost:8000, press "Play the demo" and let all three scenarios run, then `docker compose run --rm kairos make eval`. Paste gates.json and Ready-at-End, add screenshots to docs/img/, and confirm CI is green. Then run: git tag -a v0.1-mvp -m "Kairos Differentiator MVP" (do not push). Update PROJECT_STATE.md, COMPLIANCE.md and CHANGELOG.md.
