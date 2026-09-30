# Video Demonstration Script & Shot List (≤ 5 Minutes) — Kairos

> 🎥 **Video Demonstration Link (YouTube):** [https://youtu.be/Tw0xOKTyV7k](https://youtu.be/Tw0xOKTyV7k)

This document provides the exact timed shot list, narration cues, and visual actions for recording the final submission video. The entire sequence is recorded live from the Kairos Web UI (`http://localhost:8000`) using Story Mode.

---

## Shot List & Narration Timeline

### 0:00 – 0:25 · The Hook: Answering While You Talk (Boards 6 & 7)
* **Visual Setup:** Browser open at `http://localhost:8000` showing the **Home Screen (Board 6)** with the 248px left navigation bar, Newsreader typography, large question box with 56px ivory mic orb, and 3 guided demo scenario cards.
* **Action:** Click "Play the demo" on Scenario 1.
* **What appears on screen:**
  * Screen transitions smoothly to **Conversation Screen (Board 7)** with the intent-colored decomposed question bubble.
  * Header shows the real-time verified counter: *"3 of 3 sentences verified"*.
  * As speech streams, ghost sections shimmer into settled verified claims *before* the speaker finishes talking.
  * The green Ready-at-End milestone line appears: *"3 of 3 parts were ready before you finished speaking"*.
  * Right-hand 380px **Source Viewer drawer** slides open showing quoted passage highlights and ranking criteria.
* **Narration:**
  > *"Most voice RAG systems make you wait in silence after you stop talking. Kairos does something different: it starts answering while you're still speaking. Watch the canvas — while the query is still being spoken, Kairos has already detected the retrieval intent, launched parallel searches, and verified the answer. The moment the speaker stops, the answer is already complete, citation-backed, and verified."*

---

### 0:30 – 1:15 · Traces: Under the Hood (Board 9)
* **Screen & Action:** Click **"Traces"** in the sidebar $\to$ Scenario 1.
* **On Screen:** Controller trigger at $t=1.2s$, parallel legs (`L1`, `L2`), 1.0s shaded lead-time bar before speech ends ($t=2.2s$).
* **Narration:**
  > *"Under the hood, Kairos doesn't wait for speech to finish. The Stage 1 Controller fires retrieval at 1.2 seconds, splitting the query into parallel legs. Both drafts are verified before the speaker stops — hiding 100% of retrieval latency."*

---

### 1:15 – 1:55 · Late Constraints: Delta Engine (Gate G5)
* **Screen & Action:** Play Scenario 2 on the Story bar; compare Version 1 and Version 2.
* **On Screen:** Late constraint (*"for at least 150 people"*) updates only the venue claim. Green *"Byte-identical"* badge on unchanged catering claim.
* **Narration:**
  > *"When the user adds a late constraint, the Session Delta Engine updates only the affected sentence. Notice the green byte-identical badge: all other claims remain untouched, satisfying Gate G5."*

---

### 1:55 – 2:30 · Zero-Retrieval Suppression (Formatting)
* **Screen & Action:** Play Scenario 3 (*"Can you format that as bullet points?"*).
* **On Screen:** Controller emits `SUPPRESS`. Zero retrieval events on the timeline; answer instantly reformats in memory.
* **Narration:**
  > *"When asked to reformat, the Controller suppresses retrieval. Zero vector searches are run, saving compute while instantly restructuring the answer in memory."*

---

### 2:30 – 3:15 · Grounding & Red-Team Defense (Boards 7 & 8)
* **Screen & Action:** Open **Knowledge Sources (Board 8)**, then in Conversation click citation pill `[1]`.
* **On Screen:** Document table (0 flagged passages, SHA-256 verified). Source drawer slides out with exact quoted sentence highlighted in green.
* **Narration:**
  > *"Every sentence has verifiable provenance. Clicking any citation opens the exact highlighted source sentence. And when adversarial prompt injections arrive, spotlighted tags isolate the text, resulting in zero hallucinated citations."*

---

### 3:15 – 3:55 · Race View: Kairos vs. Sequential Baseline
* **Screen & Action:** Click **"Evaluation"** $\to$ **Race Tab** $\to$ "Start Race".
* **On Screen:** Side-by-side comparison. Kairos finishes at $t=2.2s$ vs baseline at $t=3.7s$. Metric: **1.5s saved per turn**.
* **Narration:**
  > *"In the Race view against the traditional sequential baseline, Kairos does the heavy lifting during speech, saving a median 1.5 seconds on every turn."*

---

### 3:55 – 4:35 · Evaluation Results & Provenance
* **Screen & Action:** Switch to **Results Tab**.
* **On Screen:** 100% pass on Gates G1–G6. Prefix-level stabilisation curve showing 0.0s trigger gap.
* **Narration:**
  > *"Our evaluation suite proves this at scale: 100% pass rate across Gates G1 through G6, measured entirely on local CPU with zero cloud dependencies."*

---

### 4:35 – 5:00 · Conclusion & Headline Metrics
* **Screen & Action:** Return to Home / Assistant canvas showing clean interface.
* **Narration:**
  > *"In summary: 65% of answers ready before speech ends, zero fabricated citations, and 1.5 seconds saved per turn. That is Kairos: live RAG that answers while you speak. Thank you."*
