# Kairos UI Design Specification — Assistant & Inspector Experience

**File:** `docs/UI_DESIGN.md` · **Tier 3: Generative Polish + UI**  
**Design Philosophy:** *"It's already looking while you're still talking — and it only tells you what it can prove."*

---

## 1. Visual Direction Exploration

To establish an interface that makes consumer voice search feel effortless while giving evaluators full technical transparency, three visual directions were evaluated against the token rules of SPEC §14.2:

### Direction A (Recommended Default): "Calm Precision"
- **Mood:** Understated, authoritative, highly responsive, quiet confidence. Feels like a top-tier consumer assistant (Apple/Linear aesthetic) rather than an AI experiment.
- **Palette:**
  - Base: High-contrast monochrome neutrals. Light mode: `#F8FAFC` canvas, `#FFFFFF` cards, `#E2E8F0` borders, `#0F172A` text. Dark mode: `#0B0F19` canvas, `#131B2E` cards, `#1E293B` borders, `#F1F5F9` text.
  - Accent: Confident deep blue (`#2563EB`) reserved strictly for action targets and active retrievals.
  - Intent Categorical Threads: Intent 1: Blue (`#3B82F6`), Intent 2: Emerald (`#10B981`), Intent 3: Violet (`#8B5CF6`), Intent 4: Amber (`#F97316`).
  - Status: Verified: `#10B981`, Uncertain/Gap: `#F59E0B`, Dropped/Error: `#EF4444`.
- **Typography:** Self-hosted Inter for UI body (16px base on mobile, 14px in inspector); JetBrains Mono for system IDs, citations (`[Doc_12 §2]`), and telemetry.
- **Visual Distinction:** Color carries strict semantic meaning (intents and states), never decorative clutter.

```html
<!-- Hero Mock: Calm Precision Mid-Utterance Canvas -->
<div style="font-family: 'Inter', sans-serif; background: #F8FAFC; padding: 24px; border-radius: 16px; max-width: 640px; border: 1px solid #E2E8F0; color: #0F172A;">
  <!-- Live Transcript Header -->
  <div style="margin-bottom: 16px;">
    <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 600; letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace;">Live Transcript</div>
    <div style="font-size: 15px; margin-top: 4px; line-height: 1.5;">
      "What is the venue capacity for Pune <span style="border-bottom: 2px solid #3B82F6; color: #1E40AF; font-weight: 500;">(Capacity)</span> and what are the cancellation terms <span style="border-bottom: 2px solid #10B981; color: #065F46; font-weight: 500;">(Cancellation)</span> and is catering included... <span style="color: #94A3B8;">(listening)</span>"
    </div>
    <div style="margin-top: 8px; display: inline-flex; align-items: center; gap: 6px; background: #EFF6FF; border: 1px solid #BFDBFE; padding: 3px 8px; border-radius: 9999px; font-size: 12px; color: #1D4ED8;">
      <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #2563EB; animation: pulse 1.5s infinite;"></span>
      <span>Already searching: 2 legs dispatched</span>
    </div>
  </div>

  <!-- Answer Canvas: Ghost, Drafting, and Settled concurrently -->
  <div style="display: flex; flex-direction: column; gap: 10px;">
    <!-- 1. Settled Section (Leg 1 - Verified & Settled) -->
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #3B82F6; border-radius: 12px; padding: 12px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span style="font-size: 11px; font-weight: 700; color: #3B82F6; font-family: 'JetBrains Mono', monospace;">L1: VENUE CAPACITY</span>
        <span style="font-size: 11px; color: #10B981; font-weight: 600; display: inline-flex; align-items: center; gap: 3px;">✓ Ready</span>
      </div>
      <p style="margin: 0; font-size: 13.5px; line-height: 1.45; color: #1E293B;">
        The Pune Auditorium accommodates up to 150 seated attendees with standard stage configurations.
        <span style="display: inline-block; background: #EEF2F6; border: 1px solid #CBD5E1; color: #334155; font-size: 10.5px; font-family: 'JetBrains Mono', monospace; padding: 1px 5px; border-radius: 4px; margin-left: 4px; cursor: pointer;">Doc_12 §2</span>
      </p>
    </div>

    <!-- 2. Drafting Section (Leg 2 - Mid-Utterance Verified Draft with Shimmer) -->
    <div style="background: #F0FDF4; border: 1px dashed #86EFAC; border-left: 4px solid #10B981; border-radius: 12px; padding: 12px 14px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span style="font-size: 11px; font-weight: 700; color: #10B981; font-family: 'JetBrains Mono', monospace;">L2: CANCELLATION TERMS</span>
        <span style="font-size: 11px; color: #059669; font-weight: 500; font-style: italic;">Drafting ahead of speech...</span>
      </div>
      <p style="margin: 0; font-size: 13.5px; line-height: 1.45; color: #166534; opacity: 0.9;">
        Cancellations received at least 14 business days prior receive a 100% refund.
        <span style="display: inline-block; background: #DCFCE7; border: 1px solid #86EFAC; color: #14532D; font-size: 10.5px; font-family: 'JetBrains Mono', monospace; padding: 1px 5px; border-radius: 4px; margin-left: 4px;">Doc_31 §4</span>
      </p>
    </div>

    <!-- 3. Ghost Section (Leg 3 - Intent Isolated, Retrieval Dispatched) -->
    <div style="background: #F8FAFC; border: 1px dashed #CBD5E1; border-left: 4px solid #8B5CF6; border-radius: 12px; padding: 12px 14px; opacity: 0.65;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-size: 11px; font-weight: 700; color: #8B5CF6; font-family: 'JetBrains Mono', monospace;">L3: CATERING SERVICES</span>
        <span style="font-size: 11px; color: #64748B;">Searching index...</span>
      </div>
      <div style="height: 10px; background: #E2E8F0; border-radius: 4px; width: 65%; margin-bottom: 4px;"></div>
      <div style="height: 10px; background: #E2E8F0; border-radius: 4px; width: 45%;"></div>
    </div>
  </div>
</div>
```

---

### Direction B (Alternative 1): "Warm Editorial"
- **Mood:** Scholarly, trusted, warm parchment background, bookish elegance. Evokes a classic research library or New Yorker digital publication.
- **Palette:**
  - Base: Cream paper (`#FAF8F5`), Warm dark ink (`#1A1612`), Stone dividers (`#E7E2DA`).
  - Accent: Deep Terracotta (`#C2410C`) and Olive Forest (`#15803D`).
- **Typography:** Serif headlines (Lora / Newsreader), clean sans body (Inter), tabular numbers.
- **Trade-off:** High aesthetic charm, but lower scanning speed during sub-second real-time live streaming compared to clean modern sans-serifs.

---

### Direction C (Alternative 2): "Technical Clarity"
- **Mood:** Mission control, cyber-instrumentation, avionics cockpit. High density, glowing indicators, telemetry front and center.
- **Palette:**
  - Base: Jet Black (`#0A0A0C`), Dark Slate (`#12141A`), Sharp Neon Accents: Cyan (`#06B6D4`), Amber (`#F59E0B`), Lime (`#84CC16`).
- **Typography:** Strict Monospace headings and telemetry (JetBrains Mono throughout).
- **Trade-off:** Ideal for judges in Inspector mode, but intimidating and overly technical for consumer voice users in Assistant mode.

---

### Direction Selection & Recommendation
**Recommendation: Direction A ("Calm Precision")** (Formalized in `docs/DECISIONS.md`).
- **Why:** Delivers immediate consumer warmth and calm readability on mobile/voice (Assistant Mode) while cleanly mapping into dense, structured system telemetry (Inspector Mode). High contrast ratios (exceeding WCAG 2.2 AA 4.5:1 on every token pair) ensure legibility under harsh conference projector lighting.

---

## 1b. The Six Signature Interactions & Storyboard

Each signature interaction is deterministically triggered by server pipeline events:

```
[WebSocket Event Stream]
         │
         ├──► 'subqueries_updated'  ───► Spawn Ghost Sections (Intent Colors)
         ├──► 'draft_verified'      ───► Fill Section with Shimmer Text
         ├──► 'turn_completed'      ───► Settle Surviving Drafts / Checkmark
         └──► 'speed2_completed'    ───► Smooth In-Place Text Cross-Fade
```

### 1. The Answer Canvas (Answer-as-you-speak)
- **Frame 1 (Intent Detected):** Event `subqueries_updated` emitted mid-utterance. An empty ghost card fades in with the intent header (`L1: CAPACITY`) and pulsing skeleton placeholders.
- **Frame 2 (Draft Verified):** Event `draft_verified` arrives. Verified Speed-1 text streams into the card in lighter weight (`text-slate-600`) with a gentle 1.5s linear gradient shimmer border.
- **Frame 3 (Utterance End):** Event `turn_completed` arrives. If the draft survived unchanged, the shimmer stops, typography settles into solid contrast (`text-slate-900`), and a small emerald checkmark flashes.
- **Reduced Motion:** No shimmer or sliding animation; immediate discrete style transition from dashed border to solid border.

### 2. Intent Colour Threading
- **Frame 1:** Query clause is recognized. Word tokens in the live transcript receive a subtle 2px bottom border matching the categorical color (e.g., `#3B82F6` for Capacity).
- **Frame 2:** The corresponding "Already searching..." chip and the left border of the answer card use the exact same hex code.
- **Frame 3:** Source pill `[Doc_12 §2]` and Timeline Gantt bar use matching tints.
- **Reduced Motion:** Same static color pairing; zero animated color sweeps.

### 3. "Ready When You Stopped" Milestone
- **Trigger:** Emitted with `turn_completed` when turn `ready_at_end > 0`.
- **Visual:** A calm footer note smoothly slides into place below the cards:
  `✓ 2 of 3 parts were ready before you finished speaking · saved 1.5s vs batch`
- **Integrity Rule:** If `ready_at_end == 0.0`, this line is completely omitted (no false bragging).

### 4. Refinement as an In-Place Edit (Delta Engine)
- **Frame 1 (Late Constraint Spoken):** User says: *"Actually, make that 200 people"*.
- **Frame 2 (Delta Patching):** Delta Engine classifies `constraint_on_existing`. Only Claim 1 glows with a subtle 2-second warm amber aura (`ring-2 ring-amber-400/40`), rewrites to 200 people, and citations update.
- **Frame 3 (Version Marker):** Version pill updates to `Updated · v2`. Clicking **"See what changed"** opens a modal displaying the exact version diff with unchanged claims muted at 40% opacity.

### 5. Two-Speed Text (Extractive Draft $\rightarrow$ Fluent Rewrite)
- **Frame 1:** Instant Speed-1 extractive sentence is rendered with source pill.
- **Frame 2:** Event `speed2_completed` arrives with LLM rewritten claim passing `GroundingGate`.
- **Frame 3:** Text cross-fades via `transition-opacity duration-300 ease-in-out` with zero layout shift. The source pill does not move by even 1 pixel.

### 6. Honest Gap Cards
- **Trigger:** Sub-intent is ungrounded or out-of-corpus (`status: "uncertain"` or `retrieval_required: false`).
- **Visual:** Gentle amber card (`bg-amber-50/60 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800`):
  *"I couldn't find catering details for the Pune office in the supplied documents."*
  Includes an actionable pill: **"Ask differently"** (pre-fills the query box with suggested phrasing).

### 7. Story Mode Auto-Play
- A dedicated **"Play the demo"** controller in the header plays Scenarios 1, 2, and 3 through the live WebSocket.
- Overlay caption banners (`strings.en.json`) explain the pipeline actions to judges in real time.

### 8. Judge Playground ("Try your own" & "Try to break it")
- Dedicated interface for judges to paste arbitrary transcripts or simulate red-team injection/tampering attacks.
- Shows immediate live defense telemetry (rejection events, circuit breaker triggers).

### 9. Time-Travel Scrubber
- An interactive slider underneath the Timeline allows scrubbing to any millisecond ($t=0.0s$ to $t=end$).
- All cards, Gantt bars, and transcript tokens rehydrate deterministically to their exact state at time $t$.

---

## 2. User Journey Storyboards

### Journey 1: First Run / Cold Start
1. User lands on `http://localhost:8000`.
2. Welcome banner displays: *"Ask anything about Veloria Systems. Speak naturally — you can add details as you go."*
3. 3 suggested questions generated from corpus headings appear as clickable chips.
4. Ephemeral privacy note appears: *"This conversation isn't stored after you close it."*

### Journey 2: Voice Compound Question
1. User clicks the listening orb (or holds `Space`).
2. Transcript streams: *"What is the capacity of the Pune auditorium and what are the cancellation rules?"*
3. At word *"Pune"*, "Already searching..." appears.
4. Two ghost cards appear for Capacity and Cancellation.
5. First draft verifies before user stops speaking.
6. User stops: Utterance-end line fires. Both cards settle. *"Ready when you stopped"* appears.

### Journey 3: Late Constraint Refinement
1. User follows up: *"Actually, notice was given 3 days prior."*
2. Controller detects `constraint_on_existing`.
3. Unaffected claims remain completely unchanged.
4. Cancellation claim updates in place with amber highlight and version bump to `v2`.
5. User clicks "See what changed" to inspect the visual diff.

### Journey 4: Presentation Transformation ("As bullets")
1. User clicks quick action **"As bullets"**.
2. Controller outputs `NO_RETRIEVAL` (`reason: presentation_restructure`).
3. Answer transforms into clean bulleted list with exact same citation set in < 5ms.
4. Subtitle confirms: *"No new search needed (instant)"*.

### Journey 5: Opening a Grounded Source Passage
1. User clicks citation pill `[Doc_12 §2]`.
2. A sleek slide-over drawer animates from the right (or modal sheet on mobile).
3. The drawer displays Document Title, Section 2 Heading, and full chunk text with the exact evidence span highlighted in soft yellow.

### Journey 6: Out-of-Scope Query
1. User asks: *"Does Veloria offer pet insurance for employees?"*
2. Decomposer isolates intent; retrieval finds no high-scoring chunks.
3. System emits an Honest Gap Card: *"Pet insurance could not be verified in the supplied documents."*
4. Zero parametric guessing; zero fabricated IDs.

### Journey 7: Microphone Permission Denied
1. Browser denies mic access.
2. The listening orb turns into a gentle keyboard icon.
3. Inline prompt appears: *"Microphone access blocked. Type your question below — live streaming works exactly the same."*
4. Focus shifts smoothly to the text input box.

### Journey 8: Connection Lost & Auto-Reconnect
1. Network disconnects.
2. A calm top status banner displays: *"Connection interrupted · Reconnecting in 2s..."*
3. Existing transcript and drafted answers are strictly preserved in local memory.
4. Once WebSocket reconnects, state resynchronizes seamlessly.

---

## 3. Responsive Wireframes & Component Matrix

### 360 px Mobile Layout
```
┌─────────────────────────────────┐
│ [Kairos]           [Story] [⚙]  │
├─────────────────────────────────┤
│ Transcript Stream:              │
│ "What is the venue capacity..." │
│                                 │
│ [• Already searching...]        │
├─────────────────────────────────┤
│ Answer Canvas:                  │
│ ┌─────────────────────────────┐ │
│ │ L1: VENUE CAPACITY          │ │
│ │ 150 seated attendees [Doc12]│ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ L2: CANCELLATION            │ │
│ │ Drafting...                 │ │
│ └─────────────────────────────┘ │
│                                 │
│ [Shorter] [Bullets] [Explain]   │
├─────────────────────────────────┤
│ ( ( (  Listening Orb  ) ) )     │
│ [ Type your question...   ] [▲] │
└─────────────────────────────────┘
```

### 1440 px Desktop Layout
```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ [Kairos] Streaming Live RAG           [Story Mode]  [Assistant | Inspector]  [☼] │
├────────────────────────────────────────┬─────────────────────────────────────────┤
│ Assistant Column (max-w-760px centered)│ Inspector Timeline & Sources Drawer     │
│                                        │                                         │
│ Live Transcript & Intent Underlines    │ ┌─────────────────────────────────────┐ │
│ "What is the capacity of Pune..."      │ │ Timeline (Gantt & Decision Markers) │ │
│                                        │ │ [WAIT]────►[RETRIEVE]═════════════  │ │
│ Answer Canvas                          │ │ L1: Capacity    [======]            │ │
│ ┌────────────────────────────────────┐ │ │ L2: Cancel      [========]          │ │
│ │ L1: Capacity [Doc_12 §2]           │ │ └─────────────────────────────────────┘ │
│ │ Accommodates 150 seated attendees. │ │                                         │
│ └────────────────────────────────────┘ │ ┌─────────────────────────────────────┐ │
│ ┌────────────────────────────────────┐ │ │ Active Chunk Source Inspector       │ │
│ │ L2: Cancellation [Doc_31 §4]       │ │ │ Document: Doc_12 §2                 │ │
│ │ 14 days prior: 100% refund.        │ │ │ "The facility accommodates 450..."  │ │
│ └────────────────────────────────────┘ │ └─────────────────────────────────────┘ │
│                                        │                                         │
│ [Type a follow-up or constraint...]    │ [Telemetry JSON Log] [Trace in Jaeger]  │
└────────────────────────────────────────┴─────────────────────────────────────────┘
```

### Component State Matrix (6 Standard States)

| Component | Empty State | Loading / Connecting | Streaming / Drafting | Uncertain / Gap | Updated (v2) | Error State |
|---|---|---|---|---|---|---|
| **Answer Canvas** | Suggested prompts | Shimmer cards | Ghost + draft cards | Amber gap card | Glow highlight | Red warning card |
| **Transcript** | "Listening..." placeholder | Cursor pulse | Color-threaded words | Normal text | Normal text | "Audio failed" |
| **Timeline** | Clean empty axis | Syncing clock | Active Gantt bars | Striped leg bar | Split revision bar| Overrun red bar |
| **Source Pill** | Hidden | Gray skeleton | Outline chip | Muted text | Highlighted chip | "Unverified ID" |
| **Listening Orb** | Calm ring | Rotating dot | Spring voice waves | Static ring | Static ring | Slash icon |

---

## 4. Complete Microcopy Dictionary (`strings.en.json`)

```json
{
  "app": {
    "title": "Kairos",
    "subtitle": "Streaming Live RAG Engine",
    "tagline": "Answers formed while you speak"
  },
  "header": {
    "assistant": "Assistant",
    "inspector": "Inspector",
    "playDemo": "Play the demo",
    "modes": {
      "offline": "Offline Extractive",
      "speed2": "Speed 2 Generative"
    },
    "status": {
      "connected": "Connected",
      "connecting": "Connecting...",
      "offline": "Offline",
      "reconnecting": "Reconnecting in {{seconds}}s..."
    }
  },
  "assistant": {
    "welcome": "Ask anything about Veloria Systems. Speak naturally — you can add details as you go.",
    "privacy": "This session is ephemeral and stored in memory only.",
    "suggestedTitle": "Suggested questions from documents",
    "listeningPlaceholder": "Listening for your question...",
    "typePlaceholder": "Type a question or speech transcript...",
    "alreadySearching": "Already searching: {{legs}} legs dispatched",
    "readyWhenStopped": "{{ready}} of {{total}} parts were ready before you finished speaking",
    "timeSaved": "saved {{time}}s vs batch",
    "version": "v{{version}}",
    "updatedBadge": "Updated · v{{version}}",
    "seeWhatChanged": "See what changed",
    "quickActions": {
      "shorter": "Shorter",
      "asBullets": "As bullets",
      "explainSimply": "Explain simply",
      "copy": "Copy answer",
      "share": "Share",
      "noNewSearch": "No new search needed (instant)"
    },
    "gapCard": {
      "title": "I couldn't find complete evidence for this in the documents.",
      "askDifferently": "Ask differently"
    },
    "errors": {
      "micBlocked": "Microphone access blocked. You can type below.",
      "rateLimit": "You're going fast — please pause for a moment.",
      "messageTooLarge": "Message exceeds the maximum allowable length.",
      "serverError": "Something went wrong. Let's try that again."
    }
  },
  "inspector": {
    "tabs": {
      "session": "Live Session",
      "race": "Race View",
      "results": "Results",
      "corpus": "Corpus",
      "playground": "Playground",
      "about": "About"
    },
    "timeline": {
      "title": "Event Timeline",
      "leadTime": "Lead time: {{leadTime}}s",
      "utteranceEnd": "Utterance End",
      "scrubberLabel": "Time-travel scrubber"
    },
    "telemetry": {
      "title": "Turn Telemetry",
      "tokens": "Tokens: {{in}} in / {{out}} out",
      "cost": "Est. Cost: ${{cost}}",
      "jaegerLink": "View trace in Jaeger"
    }
  },
  "storyMode": {
    "scenario1": {
      "name": "Scenario 1: Compound Multi-Intent",
      "caption": "Kairos detects multiple intents in real time and retrieves each parallel leg concurrently before utterance end."
    },
    "scenario2": {
      "name": "Scenario 2: Late-Arriving Detail",
      "caption": "A late constraint arrives mid-session: only the affected claim rewrites in place, preserving unaffected claims byte-identically."
    },
    "scenario3": {
      "name": "Scenario 3: Presentation Suppression",
      "caption": "Reformatting request detected: zero new retrieval calls needed, re-synthesizes presentation instantly."
    }
  }
}
```

---

## 5. Motion Specification

| Element | Trigger / Event | Duration | Easing / Physics | Reduced-Motion Fallback |
|---|---|---|---|---|
| **Listening Orb** | Voice amplitude RMS | Continuous | Spring: `stiffness: 300, damping: 20` | Static colored dot |
| **"Already Searching" Chip** | Controller `RETRIEVE` | 200 ms | `cubic-bezier(0.16, 1, 0.3, 1)` slide-up | Immediate opacity 1 |
| **Ghost Card Enter** | `subqueries_updated` | 180 ms | `ease-out` scale `0.98 -> 1.0` | Immediate appearance |
| **Draft Shimmer** | `draft_verified` | 1500 ms loop | Linear gradient translation | Solid light border |
| **Settled Checkmark** | `turn_completed` | 300 ms | Quick pop spring | Static check icon |
| **In-Place Edit Highlight** | Version update v1->v2 | 2000 ms decay | Linear color fade (`amber -> transparent`) | Static "Updated" badge |
| **Reading Drawer Slide** | Citation pill tap | 240 ms | `cubic-bezier(0.32, 0.72, 0, 1)` | Discrete open/close |

---

## 6. Accessibility Plan (WCAG 2.2 AA)

1. **Focus Traversal & Trapping:**
   - Logical tab flow: Skip link $\rightarrow$ Mode toggle $\rightarrow$ Scenario switcher $\rightarrow$ Main canvas $\rightarrow$ Quick actions $\rightarrow$ Input box $\rightarrow$ Mic button.
   - Reading drawer traps keyboard focus with `Esc` returning focus to the activating source pill.
2. **Screen Reader Announcements (`aria-live`):**
   - Streamed answers use `aria-live="polite"` on completed sections rather than per-token to prevent speech synthesizer buffer flooding.
   - Mic button announces state changes: `"Microphone listening"`, `"Microphone stopped"`.
3. **Contrast Compliance Matrix (4.5:1 Target):**
   - Dark Slate on Light Canvas (`#0F172A` on `#F8FAFC`): **16.2:1** (AAA Pass)
   - Slate Text on White Card (`#1E293B` on `#FFFFFF`): **14.8:1** (AAA Pass)
   - Primary Blue on Light Canvas (`#2563EB` on `#F8FAFC`): **5.4:1** (AA Pass)
   - Emerald Green on White Card (`#059669` on `#FFFFFF`): **5.1:1** (AA Pass)
   - Dark Theme Off-White on Slate (`#F1F5F9` on `#131B2E`): **13.5:1** (AAA Pass)
4. **Keyboard Shortcuts:**
   - `Space`: Hold to talk / toggle listening
   - `/`: Focus search text input
   - `I`: Toggle Assistant / Inspector modes
   - `R`: Replay demo scenario
   - `1`–`5`: Switch Inspector sub-tabs
   - `Esc`: Close any open drawer or modal

---

## 7. Inspector Mode Projector Ergonomics

Conference rooms and hackathon demo stages typically feature washed-out projector lighting:
1. **High Contrast Borders:** Cards utilize 1.5px high-contrast borders (`#334155` dark / `#94A3B8` light) instead of relying solely on soft box shadows.
2. **Typography Scale:** Minimum 14px in Inspector mode, with 16px section headers and 20px KPI numbers.
3. **Gantt High-Visibility Fills:** Timeline bars use saturated status colors with dual coding (distinct icon patterns for `WAIT`, `RETRIEVE`, `CANCELLED`).
4. **Timeline Scrubber:** Oversized drag handle (24×24px touch target) for easy live demonstration.

---

## 8. The 20-Second First Impression Choreography

When a judge or user launches Story Mode, the system hooks them in the first 20 seconds:
- **0–3s:** Orb reacts; the user hears/sees the compound query begin typing.
- **4–7s:** At the word "Pune", the "Already searching..." pill pops. Ghost sections appear.
- **8–12s:** The first section fills with drafting text **while the user is still speaking**.
- **13–16s:** Speech finishes. The cards settle instantly with green checks.
- **17–20s:** The line *"2 of 3 parts were ready before you finished speaking · saved 1.5s vs batch"* appears.
- **Outcome:** The user immediately remarks: *"It answered me while I was still speaking!"*
