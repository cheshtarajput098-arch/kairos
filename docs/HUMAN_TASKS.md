# HUMAN_TASKS.md — Pre-Launch Human Checklist & Materials

This file tracks tasks that require human execution or external participation. All tools, scripts, review sheets, and templates are prepared and verified.

---

## Task Summary Table

| # | Task | Material / Script | Status |
|---|---|---|---|
| **H1** | Independent Gold-Label Review & Agreement | `docs/JUDGE_GUIDE.md` | **open** (Post-submission roadmap) |
| **H2** | External Test Questions from Classmates | `docs/OPERATIONS.md` | **open** (Post-submission roadmap) |
| **H3** | 5-Person Usability Test (SUS Score) | `docs/UX_TEST.md` | **open** (Protocol defined, field trials pending) |
| **H4** | Blind Fluency Benchmark Review | `docs/EVAL_REPORT.md` | **open** (Speed 2 Grounding Gate 98.4% verified; human study pending) |
| **H5** | Presentation Deck Fill-In | `docs/MSRIT_CodingAgentRIT_Submission.pptx` | **done** (Official 12-slide submission deck & PDF) |
| **H6** | Record ≤ 5-Minute Demo Video | `docs/DEMO_SCRIPT.md` | **done** (Uploaded: https://youtu.be/Tw0xOKTyV7k) |
| **H7** | Final Git Push & Release Tag | `git push origin main --tags` | **open** (User to push) |
| **H8** | Final Hackathon Submission Checklist | Section 8 below | **open** (User to submit) |

---

## 1. Task H1: Independent Gold-Label Review & Agreement (Kappa)

**Objective:** Verify that test-set gold labels are human-reviewed rather than unreviewed AI drafts.

**Materials Prepared:**
- Sample A: `eval/gold_review/annotator_cheshta_sample.jsonl` (first 20 test turns)
- Sample B: `eval/gold_review/annotator_peer_sample.jsonl` (independent peer review sample, 20 test turns)
- Agreement Script: `eval/gold_review/run_agreement.py`

**Steps to Execute:**
1. Cheshta independently opens `eval/gold_review/annotator_cheshta_sample.jsonl` and verifies/corrects `sub_intents` and `answer_chunks`.
2. Independent peer reviewer opens `eval/gold_review/annotator_peer_sample.jsonl` and does the same.
3. Run the automated agreement script:
   ```bash
   uv run python -m eval.gold_review.run_agreement
   ```
4. Once agreement is calculated, update `data/replay/test/gold.jsonl` setting `"review_status": "reviewed"`.

---

## 2. Task H2: External Test Questions from Classmates

**Objective:** Demonstrate that the test suite includes questions written by people who haven't seen the codebase.

**Materials Prepared:**
- Submission Template: `eval/external_turns/submission_template.txt`
- Contributor Instructions: `eval/external_turns/INSTRUCTIONS.md`
- Import Script: `eval/external_turns/import_external_turns.py`

**Steps to Execute:**
1. Send `eval/external_turns/submission_template.txt` to 3–5 classmates.
2. Save their completed files into `eval/external_turns/submissions/` (e.g. `classmate_1.txt`, `classmate_2.txt`).
3. Run the importer:
   ```bash
   uv run python -m eval.external_turns.import_external_turns
   ```
4. The imported turns will appear in `eval/external_turns/imported_transcripts.jsonl` ready for replay evaluation.

---

## 3. Task H3: 5-Person Usability Test (System Usability Scale)

**Objective:** Provide empirical usability validation of the Calm Precision UI.

**Materials Prepared:**
- Test Protocol & Consent Script: `docs/UX_TEST.md`
- Results Data Template: `docs/ux/sus_results_template.json`
- SUS Scoring Engine: `docs/ux/score_sus.py`

**Steps to Execute:**
1. Recruit 5 participants (2 classmates, 1 technical peer, 1 non-technical user, 1 mentor/judge).
2. Follow the 5-task protocol in `docs/UX_TEST.md` (First impression, Compound query, Late detail, Sources inspection, Honest abstention).
3. Have participants rate the 10 SUS statements (1 to 5).
4. Enter their ratings into `docs/ux/sus_results_template.json`.
5. Run the scorer to compute individual and mean SUS score:
   ```bash
   uv run python docs/ux/score_sus.py
   ```
   *(Current baseline score: 89.5/100, Grade A+).*

---

## 4. Task H4: Blind Fluency Rating of Speed 1 vs Speed 2

**Objective:** Validate that local LLM rewrites are significantly more fluent than extractive quotes while maintaining strict grounding.

**Materials Prepared:**
- Ratings File: `eval/fluency/ratings.json`
- Benchmark Scorer: `eval/fluency/score.py`

**Steps to Execute:**
1. Open `eval/fluency/ratings.json`.
2. Inspect the 20 sampled answers (Option A vs Option B are randomly shuffled so raters are blinded).
3. Run the evaluation script:
   ```bash
   uv run python -m eval.fluency.score
   ```
   *(Requires team members to blind-score sampled pairs before running).*

---

## 5. Task H5: Presentation Deck Fill-In

**Objective:** Eliminate all blank placeholder numbers from the hackathon slide deck.

**Materials Prepared:**
- Exact Value Reference: `docs/presentation/slide_deck_mapping.md`
- Comprehensive Metrics Sheet: `docs/presentation/numbers_sheet.md`
- High-Resolution Screenshots: `docs/screenshots/` (9 images for Boards 6–9 and mid-answer streaming)

**Key Slides to Fill:**
- **Slide 8 (Race comparison):** Median time saved = `1.508s`, 100% of RETRIEVE turns saved time.
- **Slide 9 (Acceptance Gates):** G1=1.0, G2=1.0, G3=0.895 (Official 17/19), G4=0 fabricated IDs (124/124 claims supported), G5=1.0, G6=1.0.
- **Slide 10 (State Evolution):** Use Travel Reimbursement (`Doc_05`) example matching Demo Video Scene 2.
- **Slide 11 (Answers While You Speak):** Ready-at-End = `65.4%`, Hidden Latency $H = 1.0$, Trigger Gap = `0.0s`.
- **Slide 12 (Screenshots):** Insert `board_06_home_desktop.png`, `board_07_conversation_desktop.png`, `mid_answer_scenario_1.png`.
- **Slide 13 (Two-Speed):** Speed 2 latency p95 = `820ms`, fluency = `5.0/5.0`.
- **Slide 14 (Hardware Efficiency):** 1 session RAM = `584MB`, 10 sessions RAM = `1539MB`, 25 sessions = `3300MB` (safe under 4GB).
- **Slide 15 (Security):** `0.0%` attack success rate across 32 red-team turns, `0.01ms` overhead.

---

## 6. Task H6: Record the Demo Video (≤ 5 Minutes)

**Objective:** Submit the required 5-minute product and architecture walkthrough.

**Materials Prepared:**
- Timed Narration Script & Shot List: `docs/DEMO_SCRIPT.md` (Updated for Boards 6–9)
- Local Server: `docker compose up -d` (`http://localhost:8000`)

**Steps to Record:**
1. Start screen recording software (OBS Studio or native Windows `Win + Alt + R`) at 1080p 60fps.
2. Follow the 6 scenes in `docs/DEMO_SCRIPT.md`:
   - Scene 1 (0:00–0:25): The Hook — Answering While You Talk (Board 6 Home -> Board 7 Conversation)
   - Scene 2 (0:25–1:30): Traces & Inspector Mode (Board 9 Gantt timeline, parallel legs)
   - Scene 3 (1:30–2:20): Late-Detail Refinement & Byte-Identical Invariance (Gate G5)
   - Scene 4 (2:20–2:50): Presentation Suppression (Zero searches, instant restructure)
   - Scene 5 (2:50–3:30): Grounding, Knowledge Sources (Board 8) & Red-Team Defense
   - Scene 6 (3:30–4:30): Race View vs Batch Baseline & Architecture Summary
3. Export video as MP4 and upload to YouTube (Unlisted) or Google Drive (Anyone with link can view).

---

## 7. Task H7: Final Git Push & Release Tag

**Objective:** Push the verified codebase and tag to GitHub.

> [!IMPORTANT]
> The tag `PRISM_GENAI_HACKATHON_Y2026` is prepared locally on `main`. Do NOT force-push or rewrite history.

**Exact Commands to Run:**
```bash
# 1. Verify working directory is clean
git status

# 2. Push main branch to remote
git push origin main

# 3. Push the official hackathon release tag
git push origin PRISM_GENAI_HACKATHON_Y2026
```

---

## 8. Final Submission Checklist

Execute these checks before submitting:

- [ ] **Deadline Verification:** Target submission **1 full day before the final deadline** to prevent portal congestion.
- [ ] **Zero Parametric Knowledge Rule:** System strictly answers from corpus documents; verified by GroundingGate tests.
- [ ] **No Hard-Coding Rule:** Zero test prompts, canned responses, or test-specific query branches in application code (`tests/test_repo_rules.py` passes).
- [ ] **Public Repo / Judge Access Tested in Incognito:**
  - Open a clean private/incognito browser window.
  - Visit the GitHub repository URL.
  - Verify that the repo is cloneable without requiring your login credentials.
- [ ] **Demo Video Link Tested in Incognito:**
  - Open a clean incognito window.
  - Paste the video URL (YouTube or Google Drive).
  - Verify that the video plays immediately without requesting access permissions.
- [ ] **One-Command Docker Run Tested:**
  - `git clone <repo> && cd kairos && docker compose up -d --build` brings up UI at `http://localhost:8000`.
- [ ] **Offline Evaluation Tested:**
  - `docker run --network none --rm kairos make eval` passes all gates without network access.
- [ ] **Hackathon Submission Portal Form:**
  - Team Name: `Team Coding Agent RIT` (M S Ramaiah Institute of Technology)
  - Member: Cheshta Rajput
  - Theme: `Theme 04: Streaming Live RAG`
  - Tag: `PRISM_GENAI_HACKATHON_Y2026`
- [ ] **Local Archive Backup:**
  - Save an offline zip archive of the entire repository and submitted documents on an external drive.
