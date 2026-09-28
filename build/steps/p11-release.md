# Step 14 of 14 — Documentation, disclosure, final audit, release

**File:** `build/steps/p11-release.md` · **Tier 5 — Submission** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

**Tag at the end of this step:** `PRISM_GENAI_HACKATHON_Y2026` (create it locally with `git tag -a PRISM_GENAI_HACKATHON_Y2026 -m "Documentation, disclosure, final audit, release"`; never push).

---

Write the deliverables, then act as the strictest possible hackathon judge AND an external security auditor.

Write:
- README.md: problem in 3 sentences, architecture diagram (Mermaid), one-command quick start, optional LLM mode via .env, results table pulled from the latest runs/ output (with n), screenshots, CI badges, repo map, deliverables checklist with links, APK/SDK: N/A.
- docs/ARCHITECTURE_BRIEF.md (≤ 6 pages as PDF): design rationale, trigger logic, decomposition strategy, data provenance, security architecture summary, trade-offs with a latency/compute justification per component, failure modes and mitigations, references from SPEC.md §17. Export to docs/ARCHITECTURE_BRIEF.pdf and confirm the page count.
- docs/TELEMETRY_SCHEMA.md: every span and event, every field, example records.
- docs/DEMO_SCRIPT.md: ≤ 5-minute shot list, recorded from Story mode (the fail-safe) with live narration, that visibly covers all six behaviours the theme guide names for the video (early retrieval triggering, multi-intent decomposition, late-detail refinement, presentation query suppression, citation traceability, runtime telemetry). Open in Assistant mode on a phone-sized window: the Answer Canvas visibly forming while the speaker is still talking, then "Ready when you stopped" (0:00–0:25), then flip to Inspector mode — 0:25 Scenario 1 on the Timeline (early retrieval, legs splitting); 1:30 Scenario 2 late constraint with the v1→v2 diff and "byte-identical" badges; 2:20 Scenario 3 suppression with zero retrieval events; 2:50 citation click-through, then a poisoned chunk and a fabricated citation both blocked; 3:30 Race view vs baseline; 4:05 Results dashboard hero row + gates, stabilisation and robustness plots, and a 5-second time-travel scrub proving the draft existed before utterance end; 4:40 close on the three headline numbers.
- AI_DISCLOSURE.md: runtime models (names, versions, licences, where they run), AI tools used in development (Google Antigravity and any others), which parts were AI-generated, and confirmation that gold labels, results and security findings were human-reviewed.

- docs/presentation/: a "numbers sheet" listing every blank on our submission deck (document count, chunk count, turn count, G1–G6 official and strict values) with the exact value and source file from runs/, so I can fill the slides. Also a "deck changes" note proposing the exact slide edits: a new slide for answer-as-you-speak with the Ready-at-End result and a Story-mode screenshot; two-speed answers and the local LLM on the Tools slide; move "input is replayed transcripts" from Limitations to Results with the robustness table; update Ablation A to match what we actually trained (MiniLM or logistic regression). Put the final exported deck PDF here when I provide it.
- Three headline numbers: pick the three strongest *measured* results (for example Ready-at-End, median time saved vs batch, and G4 with 0 fabricated IDs) and use the same three, worded identically, in the README hero, the Results dashboard hero row, the first 30 seconds of the video and the deck's results slide.

Audit — report every finding with file:line, severity and fix, then fix them:
1. Theme compliance: walk docs/COMPLIANCE.md row by row (SPEC.md §18). Every row needs a link to code and to a passing test or measured output; any row still "pending" is a blocker. Confirm G1–G6 (official and strict) with n, the five hard rules each enforced by a test, and the five pitfalls each addressed with a metric.
1b. Held-out readiness: take a transcript you have never used, rewrite it in two new formats (the guide's table form and a differently named JSON shape), run `kairos replay` on each from a clean container, and confirm the output records carry the guide's exact keys.
2. Loophole hunt: grep for hard-coded test text, imports from data/replay or eval inside kairos/, any runtime network call other than the configured LLM provider, any metric not read from a file, any threshold tuned on test.
3. Security: re-run all scans; try each red-team category manually through the UI; confirm logs contain no secrets or unredacted PII; confirm the container runs non-root with a read-only filesystem.
4. Reproducibility: fresh clone in a clean container, no .env, then docker compose up and make eval must pass unattended.
5. Judge view: walk through JUDGE_REVIEW.md §1 (the judge's ten minutes) on a clean machine and confirm each step works; check every concern in §3 is resolved with evidence; fill every <…> in the §5 Q&A from runs/ output (write TBD where not measured); then score the repo against SPEC.md §16 and list the 5 changes that would raise the score most with the time left.

Finally, only if every blocker from the audit is fixed, create the release tag locally:
git tag -a PRISM_GENAI_HACKATHON_Y2026 -m "Kairos final submission — Theme 04"
Then tell the human to push with: git push origin main --tags  (do not push yourself).
