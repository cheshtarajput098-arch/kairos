# Step 11 of 14 — UI build and polish

**File:** `build/steps/p09b-ui-build.md` · **Tier 3 — Generative polish + UI** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

**Tag at the end of this step:** `v0.8-polish` (create it locally with `git tag -a v0.8-polish -m "UI build and polish"`; never push).

---

Act as a senior frontend engineer with a designer's eye. Build the approved design to the full SPEC.md §14 bar.

Build:
- The six signature interactions from SPEC.md §14.3a, driven only by real events, polished to the storyboard from 9a (Answer Canvas with ghost → drafting → settled → rollback; intent colour threading across transcript, chips, sections, pills and Timeline bars; the "Ready when you stopped" line from measured values; refinement as an edit; two-speed cross-fade; honest gap cards).
- Story mode polished: captions, pacing, a pause/skip control; it must play flawlessly 10 times in a row (add a Playwright loop test).
- Assistant mode (§14.3), complete: mobile-first layout with thumb-reachable controls; listening orb + live transcript; "Already searching…" chip driven by real retrieval_started events; answers streamed per intent with numbered source pills, passage popover and reading drawer; amber "couldn't find…" notes with "Ask differently"; in-place refinement with change highlight and a friendly "See what changed"; quick actions (Shorter, As bullets, Explain simply, Copy, Share as text) routed as presentation-only turns; thumbs feedback kept in session telemetry only; suggested questions from corpus headings; calm offline, reconnecting, permission and rate-limit states; installable PWA shell.
- Inspector mode (§14.4), complete: Live Session (Timeline, Answer, Telemetry with Jaeger deep link), Race view vs the batch baseline with live TTFT counters, Results dashboard (hero row of the three differentiator numbers, official + strict gates with n, ablations, stabilisation plot, robustness chart, red-team ASR, SUS), Corpus explorer, Judge playground (Try your own / Try to break it), About with the core-vs-harness diagram, and the time-travel scrubber on Live Session and Race view.
- The "Show how it works" toggle keeps the live session intact.
- Frontend security (§14.6): text-only rendering, no dangerouslySetInnerHTML, token in memory, strict-CSP compatible.
- Quality gates (§14.7–14.8): TS strict with no any, ESLint + Prettier, Vitest, Storybook stories for every component state, Playwright e2e for both modes and all three theme scenarios plus an XSS payload, axe with zero violations, Lighthouse desktop and mobile ≥ 90 (saved to docs/lighthouse/), bundle ≤ 300 KB gzipped, visual regression snapshots. Add all of these to CI.

Polish loop (do it at least twice): use the browser agent on localhost to screenshot every screen and state in light and dark themes at 360, 1280 and 1440 px. Review them against Nielsen's 10 heuristics and SPEC.md §14 like a demanding design lead: hierarchy, spacing rhythm, alignment, typography, contrast, motion, copy tone, and whether a first-time user would know what to do. List the 10 highest-impact issues, fix them, re-screenshot, and save before/after images to docs/img/ux/.

Finally write docs/UX_TEST.md: a 15-minute hallway test script for 5 people (consent line, the 20-second first-impression question from SPEC.md §14.7, three tasks, the standard 10-question SUS form, and a results table left as TBD). Do not invent results — I will run the test and fill it in.

Verification: `npm run lint typecheck test`, `npx playwright test`, the Lighthouse reports, Storybook build, and the before/after screenshots. Update docs/COMPLIANCE.md and PROJECT_STATE.md.
