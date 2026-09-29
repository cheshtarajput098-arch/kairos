# Kairos UX Hallway Usability Test Protocol & Script

**File:** `docs/UX_TEST.md` · **SPEC §14.7 — Usability Quality Bar**  
**Methodology:** 15-Minute Lightweight Hallway Usability Test (5 Participants)  
**Status:** Protocol defined; results pending human execution (**TBD** per Autopilot Rule 4)

---

## 1. Participant Information & Consent

### Consent Script (Read aloud to participant):
> *"Thank you for participating today. We are testing Kairos, a streaming voice search assistant designed for real-time document answering. We are testing the system interface and user clarity, not your performance. Your feedback is confidential and will be used exclusively to refine interface ergonomics. You may stop at any time. Do you consent to proceed?"*

- **Participant Consent Given:** [ ] Yes [ ] No
- **Participant ID:** `P1` / `P2` / `P3` / `P4` / `P5`
- **Session Duration:** 15 minutes max
- **Device Tested:** Desktop Chrome (1440px) or Mobile (360px viewport)

---

## 2. 20-Second First Impression Evaluation (SPEC §14.7)

### Moderator Action:
Open `http://localhost:8000`. Click **"Play the demo"** in the header. Allow Scenario 1 to run for exactly 20 seconds as speech streams and answer sections form in real time. Pause at $t=20\text{ s}$.

### Scripted Prompt:
> *"In your own words, what just happened while the speaker was talking?"*

### Response Coding Criteria:
- **Pass (Grounded Streaming Recognized):** Participant notices that answering/searching started *before* the speaker finished talking (e.g., *"It started answering while he was still talking"* or *"It was already looking up venues"*).
- **Partial:** Participant notices speed or real-time text, but believes it was a standard pre-recorded response.
- **Fail:** Participant assumed the system only began processing after the audio ended.

---

## 3. The Three Guided Tasks

### Task 1: Ask a Compound Question (Assistant Mode)
- **Prompt given to participant:**  
  *"Find out the venue capacity for a customer workshop in Pune, and whether catering options are available."*
- **Success Criteria:**
  1. Participant locates microphone button or text input within 5 seconds.
  2. Participant observes parallel retrieval intent sections.
  3. Participant spots the honest gap card for catering at Riverside Hall.
- **Observations / Friction Points:** [Record verbatim comments]

### Task 2: Refine in Place with a Late Detail
- **Prompt given to participant:**  
  *"Your team size increased to 45 people. Add that detail without restarting the conversation."*
- **Success Criteria:**
  1. Participant submits *"Actually, make that 45 people."*
  2. Participant recognizes the in-place update (v2 badge, strikethrough on capacity sentence, unchanged cancellation section).
  3. Participant understands that unaffected sections were preserved.
- **Observations / Friction Points:** [Record verbatim comments]

### Task 3: Inspect Grounding & Sources (Inspector Mode)
- **Prompt given to participant:**  
  *"Switch to the 'Show how it works' mode. Check the source citation for the Pune venue capacity and verify if any citations were made up."*
- **Success Criteria:**
  1. Participant clicks **"Show how it works"** in the header.
  2. Participant identifies the Gantt timeline or Claims table.
  3. Participant confirms 0 made-up citations from the KPI metric card.
- **Observations / Friction Points:** [Record verbatim comments]

---

## 4. Standard System Usability Scale (SUS) Questionnaire

Each participant rates the 10 standard SUS statements on a scale of **1 (Strongly Disagree)** to **5 (Strongly Agree)**:

1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

---

## 5. Results & Telemetry Summary Table

> [!NOTE]
> Per Autopilot Rule 4 (*Honesty rules: never invent participants, ratings, or reviews*), the results table is preserved as **TBD** until the 5-person hallway test is executed by the human evaluation team.

| Participant | Role / Profile | 20s Impression Recognition | Task 1 (Compound) | Task 2 (Refinement) | Task 3 (Inspector) | Raw SUS Score | Notes & Feedback |
|---|---|---|---|---|---|---|---|
| **P1** | *External classmate* | TBD | TBD | TBD | TBD | TBD | Pending evaluation |
| **P2** | *External classmate* | TBD | TBD | TBD | TBD | TBD | Pending evaluation |
| **P3** | *Domain practitioner* | TBD | TBD | TBD | TBD | TBD | Pending evaluation |
| **P4** | *Non-technical user* | TBD | TBD | TBD | TBD | TBD | Pending evaluation |
| **P5** | *Judge / Mentor* | TBD | TBD | TBD | TBD | TBD | Pending evaluation |
| **Mean** | — | **TBD** | **TBD** | **TBD** | **TBD** | **TBD** | Target: SUS ≥ 75.0 (Grade B+) |

---

## 6. Heuristic Inspection Log (Nielsen's 10 Heuristics)

| Heuristic | Assessment in Kairos Calm Precision UI | Status |
|---|---|---|
| **1. Visibility of system status** | Live waveform (`║║║`), real-time status chips ("found", "looking it up"), pulsing skeleton bars, and Ready-at-End indicators keep user informed at every millisecond. | **PASS** |
| **2. Match between system and real world** | Human-readable section headings ("Venue for 30 people"), plain language gap notes ("Not in the documents"), warm ivory typography. | **PASS** |
| **3. User control and freedom** | Mode toggle preserves state; Story Mode includes Pause/Resume/Next/Exit; Quick actions re-synthesize instantly without locking the interface. | **PASS** |
| **4. Consistency and standards** | Uniform dark theme (`#0E1014`, `#15181E`), consistent intent color threading (Intent 1: Blue, Intent 2: Green, Intent 3: Purple) across all cards, chips, and Gantt tracks. | **PASS** |
| **5. Error prevention** | Zero hallucination deterministic gate prevents fabricated citations from reaching the client; mic denials trigger graceful fallback to keyboard. | **PASS** |
| **6. Recognition rather than recall** | Numbered citation pills (`[1]`, `[2]`) map directly into the right-hand Sources panel with expandable evidence chunks. | **PASS** |
| **7. Flexibility and efficiency of use** | Assistant mode provides focused calm for casual users; "Show how it works" exposes full engineering telemetry and timeline for evaluators. | **PASS** |
| **8. Aesthetic and minimalist design** | Eliminated coloured left-border clutter; uses clean rounded elevation cards with subtle intent number badges and strict typography hierarchy. | **PASS** |
| **9. Help users recognize, diagnose, and recover from errors** | Amber gap cards provide actionable "Ask differently" pills rather than raw error codes or cryptic stack traces. | **PASS** |
| **10. Help and documentation** | Dedicated "How Kairos works" explainer card in Sources panel; comprehensive Corpus Explorer and Judge Playground in Inspector mode. | **PASS** |
