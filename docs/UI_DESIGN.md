# Kairos UI Design Specification — Adopted from Approved Design Canvas

**File:** `docs/UI_DESIGN.md` · **Tier 3: Generative Polish + UI**
**Design Philosophy:** *"Answers while you speak — and only tells you what it can prove."*
**Reference Boards:** `docs/design/board_01.png` through `docs/design/board_05.png`

---

## 1. Visual Direction: "Calm Precision" (Dark)

The approved design follows a single visual direction: **Calm Precision**, a dark-themed, understated, authoritative interface. It feels like a top-tier consumer assistant rather than an AI experiment. Every colour carries strict semantic meaning — intents and states — never decoration.

### 1.1 Colour Tokens

| Token Name | Hex | Usage |
|---|---|---|
| `--bg-canvas` | `#0E1014` | Page background |
| `--bg-surface-1` | `#15181E` | Primary card / panel surfaces |
| `--bg-surface-2` | `#1C2028` | Elevated cards, input bar, source panel header |
| `--bg-surface-3` | `#12151B` | Recessed areas, sidebar background, story bar |
| `--text-primary` | `#ECE9E2` | Primary body text, answer prose (ivory warm) |
| `--text-secondary` | `#A3A9B5` | Subheadings, metadata labels, muted text |
| `--text-tertiary` | `#7D8594` | Timestamps, placeholders, dimmed text |
| `--border-default` | `#1E2330` | Card borders, dividers |
| `--border-subtle` | `#282D3A` | Separator lines within panels |
| `--intent-1` | `#8FB3FF` | Intent 1 (blue): Venue / first sub-query |
| `--intent-2` | `#62D6B4` | Intent 2 (green): Cancellation / second sub-query |
| `--intent-3` | `#B98CFF` | Intent 3 (purple): Catering / third sub-query |
| `--intent-4` | `#F0B455` | Intent 4 (amber): rare fourth sub-query |
| `--status-verified` | `#6FD39A` | Verified claims, "Ready" checks |
| `--status-gap` | `#F0B455` | Amber: uncertain gaps, "Not in the documents" |
| `--status-error` | `#EF4444` | Errors, "not found" labels |
| `--status-updated` | `#8FB3FF` | "Updated" badge on v2 sections |
| `--btn-ivory` | `#ECE9E2` | Quick action button text/border on dark bg |
| `--btn-ivory-bg` | `#1C2028` | Quick action button background |
| `--accent-blue` | `#5B8DEF` | Active state, "Play the demo" button bg |
| `--accent-green-dot` | `#4ADE80` | "Connected" status dot |

### 1.2 Typography

| Role | Font Family | Weight | Size (desktop) | Size (mobile) |
|---|---|---|---|---|
| UI chrome (nav, labels, buttons, metadata) | **Geist** (sans-serif) | 400, 500, 600 | 13–14 px | 13–14 px |
| Answer prose (body text inside answer cards) | **Newsreader** (serif) | 400 | 15–16 px | 15 px |
| System IDs, citations, event log, monospace | **Geist Mono** | 400 | 12–13 px | 12 px |
| Section headings inside answer cards | **Geist** | 600 | 15 px | 15 px |
| KPI numbers (Inspector) | **Geist** | 700 | 28–32 px | 24 px |
| Story bar / demo captions | **Geist** | 500 | 14 px | 13 px |

**Font loading:** All three fonts are self-hosted in `web/public/fonts/`. No CDN at runtime. `font-display: swap` on all `@font-face` declarations.

### 1.3 Layout Measurements

| Element | Value |
|---|---|
| Story bar height | 56 px (sits above the main content when demo is active) |
| Header (nav) height | 60 px |
| Answer column max-width | 760 px (centered in main area) |
| Sources panel width | 340 px (right, desktop only) |
| Card padding | 20–24 px |
| Card border-radius | 12 px |
| Intent number badge size | 24 × 24 px rounded square |
| Source pill (inline citation) | 20 × 20 px rounded, monospace number inside |
| Input bar height | 56 px |
| Mic orb diameter | 48 px (desktop), 56 px (mobile) |
| Mobile breakpoint | ≤ 768 px |
| Desktop min-width for side panel | 1100 px |

### 1.4 Card Style — No Coloured Left Border

> [!IMPORTANT]
> The approved design does **not** use coloured left-border cards (`border-l-*`). Instead, each answer section card uses:
> - A rounded `--bg-surface-1` card with `--border-default` border
> - An **intent number badge** (small rounded square with the intent colour as background) placed before the section heading
> - The heading text in `--text-primary` weight 600
> - No coloured left stripe

---

## 2. Component Specifications (from Boards 1–5)

### 2.1 Header Bar (all boards)

```
┌────────────────────────────────────────────────────────────────────┐
│ (○) Kairos                [Assistant] [Show how it works]  ● Connected  ▶ Play the demo  ⚙ │
│     Answers while you speak                                        │
└────────────────────────────────────────────────────────────────────┘
```

- Logo: Circle icon `(○)` + "Kairos" in Geist 600 18px + subtitle "Answers while you speak" in `--text-tertiary` Geist 400 12px.
- Mode toggle: Two pill buttons, `Assistant` (filled when active) and `Show how it works` (Inspector). Geist 500 14px. Active: `--bg-surface-2` bg, `--text-primary` text. Inactive: transparent bg, `--text-secondary`.
- Status: Green dot `--accent-green-dot` + "Connected" in `--text-secondary` Geist 400 13px.
- Play the demo: `--accent-blue` bg, white text, Geist 500 14px, `▶` icon. Pill-shaped button.
- Settings: `⚙` icon button, `--text-secondary`.

### 2.2 Story Bar (Board 1, top)

When Story Mode is active:

```
┌──────────────────────────────────────────────────────────────────┐
│ DEMO  1 of 3 · A question with three parts   [desc]   ── ●── ── ──  ⏸ ⏭ Exit │
└──────────────────────────────────────────────────────────────────┘
```

- 56 px height, `--bg-surface-3` background.
- "DEMO" badge: amber `--status-gap` bg, dark text, uppercase Geist Mono 11px.
- Progress dots: `──●──` style, current dot filled.
- Controls: Pause, Next, Exit buttons in `--text-secondary`.

### 2.3 Transcript Area (Board 1 — speaking, Board 2 — settled)

**While speaking:**
```
┌─────────────────────────────────────────────────────┐
│ ║║║  You're speaking                         1.6 s  │
│                                                     │
│ I need to plan a customer workshop in Pune          │
│ for 30 people ❶, and I need the cancellation        │
│ policy ❷ and the catering                           │
│                                                     │
│ ● Venue for 30 people · found                       │
│ ● Cancellation terms · ◌ looking it up              │
│ Listening for more…                                 │
└─────────────────────────────────────────────────────┘
```

- `--bg-surface-1` card with `--border-default` border.
- "You're speaking" label: Geist 500 13px `--text-secondary`, with audio waveform bars `║║║` in `--intent-1`.
- Timer: Geist Mono 13px `--text-tertiary`, right-aligned.
- Transcript text: Newsreader 400 18px `--text-primary`. Key phrases underlined with intent colours.
- Inline intent superscript numbers: small circles with intent bg, white number inside.
- Intent status chips below text: `● Label · status`. Dot uses intent colour. "found" in `--status-verified`, "looking it up" in `--text-tertiary` with spinner.

**After speaking (Board 2):**
- Label changes to "You said", waveform icon disappears.
- Full transcript shown, no "Listening for more…".

### 2.4 Answer Canvas (Boards 1, 2, 3)

**Section header line:**
```
❶ Venue for 30 people                    Draft · checked against source
```
- Intent badge: 24×24 rounded square with `--intent-N` bg, white number, Geist 600 13px.
- Section title: Geist 600 15px `--text-primary`.
- Status: Geist 400 12px `--text-tertiary`. `✓ Draft · checked against source` when verified. `Looking this up…` when drafting.

**Section body:**
- Newsreader 400 15px `--text-primary`.
- Inline citation pills: 20×20 rounded square, `--bg-surface-2` bg, `--border-default` border, Geist Mono 12px `--text-secondary`, sequential number inside (1, 2, 3…). No raw `[Doc_ID §Section]` in prose.

**Skeleton loading (Board 1, Cancellation terms):**
- 3–4 rounded bars in `--bg-surface-2`, widths 80%, 90%, 65%, 50%. Subtle pulse animation.
- "Looking this up…" label in `--text-tertiary`.

**Gap card (Board 2, bottom of Catering section):**
```
┌─────────────────────────────────────────────────────────┐
│ 🔍 Not in the documents                [Ask differently] │
│ I couldn't find catering details for Riverside Hall.     │
└─────────────────────────────────────────────────────────┘
```
- `--status-gap` / 10% opacity background. `--status-gap` / 30% opacity border.
- Search icon in `--status-gap`.
- "Not in the documents" in Geist 600 14px `--text-primary`.
- Body in Newsreader 400 14px `--text-secondary`.
- "Ask differently" pill button: `--btn-ivory` text, `--btn-ivory-bg` bg, `--border-default` border.

**Settled state footer (Board 2):**
```
✓ 2 of 3 parts were ready before you finished speaking · about 1.3 s sooner than waiting
```
- `--status-verified` check icon + Geist 400 13px `--text-secondary`.
- Bold the "2 of 3 parts" portion.
- Hidden when ready count = 0.

**Quick actions (Board 2):**
```
[Shorter]  [As bullets]  [Explain simply]  📋 Copy
```
- Pill buttons: `--btn-ivory-bg` bg, `--btn-ivory` text, `--border-default` border, Geist 500 13px.
- Copy button has clipboard icon.

### 2.5 Refinement View (Board 3 — v2)

**Previous question (dimmed):**
```
Earlier  I need to plan a customer workshop in Pune for 30 people, and I need the cancellation policy an…
```
- `--text-tertiary` colour, Geist 400 14px.
- "Earlier" label in `--text-secondary`.

**New detail transcript:**
```
┌────────────────────────────────────────────────────────┐
│ You added a detail  [changes part 1]           1.2 s   │
│                                                        │
│ Actually, make that 45 people.                         │
└────────────────────────────────────────────────────────┘
```
- "changes part 1" badge: `--intent-1` bg, white text, Geist 500 12px, pill-shaped.
- Underlined "45 people" with intent colour.

**Answer header:**
```
Answer   Updated · v2   See what changed
```
- "Updated · v2" badge: `--status-updated` bg, white text, Geist 500 12px.
- "See what changed" link in `--text-secondary`.

**Updated section card:**
```
❶ Venue for 45 people                              Updated
~~Both approved Pune venues fit your group: Riverside Hall in Baner seats up to 40~~
~~people in a classroom layout, and Koregaon Studio seats up to 35.~~

For 45 people, Riverside Hall works in a theatre layout, which seats up to 60. For a
classroom layout above 40 people, the Events Desk arranges an external venue on
request. ❶
```
- "Updated" label in `--status-updated` colour, right-aligned.
- Old text: strikethrough, `--text-tertiary` colour, 50% opacity.
- New text: `--text-primary`, full opacity, highlighted bg (subtle `--intent-1` at 5% opacity).

**Unchanged section card:**
```
❷ Cancellation terms                              Unchanged
(answer text at 60% opacity, --text-tertiary)
```
- "Unchanged" label in `--text-tertiary`.
- Body text dimmed to 60% opacity.

**Footer:**
```
✓ Only the part you changed was looked up again · 1 new search, 2 parts kept exactly as they were
```

### 2.6 Sources Panel (Boards 1, 2 — right side, desktop)

```
┌────────────────────────────────────┐
│ Sources           5 passages · 3 documents │
│                                    │
│ ❶ Workshop Venues in Pune          │
│   Capacity and rooms · Doc_12 §2   │
│                                    │
│ ❷ Event Cancellation and Refund Policy │
│   Notice periods · Doc_31 §2       │
│   ┌────────────────────────────┐   │
│   │ Cancellations must be submitted │
│   │ through the Events Desk portal. │
│   │ A cancellation made 14 or more  │
│   │ calendar days before the event  │
│   │ date is a standard cancellation.│
│   └────────────────────────────┘   │
│   Open the full document →         │
│                                    │
│ ❸ Event Cancellation and Refund Policy │
│   Refund terms · Doc_31 §4         │
│                                    │
│ ❹ Catering Options for Events      │
│   On-site catering · Doc_89 §1     │
│                                    │
│ ❺ Catering Options for Events      │
│   External caterers · Doc_89 §2    │
└────────────────────────────────────┘
```

- 340 px width, `--bg-surface-3` background.
- Header: "Sources" in Geist 600 16px `--text-primary`. Count in Geist 400 13px `--text-tertiary`.
- Each source: number badge (matching `--intent-N` or neutral), doc title in Geist 500 14px `--text-primary`, section + ID in Geist Mono 12px `--text-tertiary`.
- Expanded source (Board 2, source 2): shows chunk text in a `--bg-surface-2` inset card, Newsreader 400 14px. Highlighted matching span in `--status-gap` bg (soft yellow).
- "Open the full document →" link in `--accent-blue`.
- On mobile: collapsed into a bottom sheet triggered by "Sources · 5" button.

### 2.7 v2 Change Panel (Board 3 — right side)

```
┌────────────────────────────────────┐
│ What changed in v2                 │
│                                    │
│ ● Venue               Updated     │
│ ● Cancellation         Kept as is  │
│ ● Catering             Kept as is  │
│                                    │
│ Sources                            │
│ All 5 earlier sources kept. Source │
│ 1 was read again for the new       │
│ group size.                        │
│                                    │
│ Why this is fast                   │
│ Kairos keeps the parts of your     │
│ answer that are still true and     │
│ only rechecks the part your new    │
│ detail affects, instead of         │
│ starting over.                     │
└────────────────────────────────────┘
```

- Same 340 px panel, `--bg-surface-3` bg.
- Each row: intent colour dot, label, status. "Updated" in `--status-updated`, "Kept as is" in `--text-tertiary`.
- Explainer sections in Geist 400 14px `--text-secondary`.

### 2.8 Input Bar (Boards 2, 3)

```
┌──────────────────────────────────────────────────────────┐
│ 🎤  Tap the mic, or type a question or a new detail…  → │
└──────────────────────────────────────────────────────────┘
```

- `--bg-surface-2` bg, `--border-default` border, rounded full (pill shape).
- Mic button: 48 px circle, `--bg-surface-1` bg, mic icon in `--text-secondary`. On mobile: 56 px, centred at bottom.
- Placeholder: Geist 400 14px `--text-tertiary`.
- Send button: `→` arrow in `--text-secondary`, right side.

### 2.9 Inspector — Timeline (Board 4)

**Tab bar:**
```
Timeline    Race vs. batch    Results    Corpus    Try it yourself
```
- Geist 500 14px. Active tab: `--text-primary`, underline in `--accent-blue`. Inactive: `--text-tertiary`.

**Scenario header:**
```
Scenario 1 · turn s1-t1 · sample timing
Search and drafting started while the speaker was still talking
```
- Breadcrumb in Geist 400 13px `--text-tertiary`.
- Title in Geist 700 24px `--text-primary`.

**KPI cards** (3-across):
```
┌─────────────┐ ┌──────────────┐ ┌────────────────┐
│ Lead time   │ │ Ready at end │ │ Made-up citations│
│ 1.3 s       │ │ 2 of 3 parts │ │ 0               │
└─────────────┘ └──────────────┘ └────────────────┘
```
- `--bg-surface-2` bg, Geist 400 12px label in `--text-tertiary`, Geist 700 28px value in `--text-primary`.

**Gantt chart:**
- X-axis: time in seconds (0.0 s, 0.5, 1.0, 1.5, 2.0).
- Rows: Speech, Decision, 1 · Venue, 2 · Cancellation, 3 · Catering.
- Speech row: `--bg-surface-2` bars with transcript text inside, Geist 400 13px.
- Decision row: pill badges — `WAIT · unstable` (grey), `RETRIEVE · entities stable` (`--intent-2` bg), `SPLIT → 3 parts` (neutral).
- Intent rows: solid bars coloured with `--intent-N`, diamond `◆` icon for "draft verified".
- Dashed outline bar: superseded draft.
- Vertical red dashed line at `Speaker stopped · 2.1 s`.
- Legend below: ■ Search + draft for one part · ◆ Draft checked against its source · ▨ Work hidden behind speech · ┈ Replaced when the speaker said more.
- Replay slider: "Replay to" label, range input, current time in Geist Mono.

**Claims table:**
```
Claims · version 1                    each checked before it is shown

1    Both approved Pune venues…    Doc_12 §2    verified
2    Cancelling 14 or more days…   Doc_31 §2    verified
2    Later cancellations get 50%…  Doc_31 §4    verified
3    Koregaon Studio has in-house… Doc_89 §1    verified
3    Catering at Riverside Hall    no source    not found
```
- Intent number in left column, `--intent-N` colour.
- Claim text in Geist 400 14px `--text-primary`.
- Citation in Geist Mono 12px `--text-tertiary`.
- "verified" in `--status-verified`, "not found" in `--status-error`.

**Event log:**
```
Open trace in Jaeger →

0.00  controller_decision  WAIT  intent_unstable
0.80  retrieval_started  L1  "Pune workshop venue capacity 30"
1.02  draft_verified  L1  Doc_12 §2
1.60  subquery_emitted  L2  L3
1.79  draft_verified  L2  Doc_31 §2, §4
2.00  leg_updated  L3  "catering options"
2.10  draft_committed  L1  L2
2.24  draft_verified  L3  Doc_89 §1, §2 · 1 gap
```
- `--bg-surface-1` card. Geist Mono 13px, tabular layout.
- Timestamps in `--text-tertiary`. Event names in `--text-secondary`. Values in `--text-primary`.
- "Open trace in Jaeger →" link in `--accent-blue`, top-right.

### 2.10 Phone Layout (Board 5)

```
┌─────────────────────────┐
│ (○) Kairos      ⚡ ⚙    │
├─────────────────────────┤
│ You said                │
│ Plan a customer workshop│
│ in Pune for 30 people,  │
│ with the cancellation   │
│ policy and catering     │
│ options.                │
│                         │
│ ✓ 2 of 3 parts ready   │
│   before you finished   │
│                         │
│ ❶ Venue for 30 people   │
│ Both approved venues…   │
│                  ❶      │
│                         │
│ ❷ Cancellation terms    │
│ Cancel 14 or more days… │
│              ❷ ❸        │
│                         │
│ ❸ Catering              │
│ Koregaon Studio has…    │
│                  ❹      │
│ ● Not in the documents: │
│   catering for Riverside│
│   Hall.                 │
│                         │
│ [Shorter] [As bullets]  │
│       [Sources · 5]     │
├─────────────────────────┤
│ ⌨           🎤          📋 │
└─────────────────────────┘
```

- Single column, full-width cards.
- Sources collapse into a bottom sheet button: "Sources · 5".
- Bottom bar: keyboard toggle (left), large mic orb (centre, 56 px), copy button (right).
- No sources side panel. No header subtitle.

---

## 3. The Six Signature Interactions & Storyboard

Each signature interaction is deterministically triggered by a real server pipeline event. Nothing is faked with timers.

```
[WebSocket Event Stream]
         │
         ├──► 'subqueries_updated'  ───► Spawn Ghost Sections (Intent Colours)
         ├──► 'draft_verified'      ───► Fill Section with Text
         ├──► 'turn_completed'      ───► Settle Surviving Drafts / Checkmark
         └──► 'speed2_completed'    ───► Smooth In-Place Text Cross-Fade
```

### 1. The Answer Canvas (Answer-as-you-speak)
- **Board 1 (speaking):** Ghost sections with skeleton bars appear as `subqueries_updated` events arrive. The first section fills with verified text while the user is still speaking.
- **Board 2 (settled):** All sections filled. Verified checkmark. "2 of 3 parts were ready before you finished speaking" line appears.

### 2. Intent Colour Threading
- Query phrases are underlined with the matching intent colour in the transcript (Board 1: "workshop in Pune for 30 people" underlined in blue, "cancellation policy" in green, "the catering" in purple).
- The same colours are used for intent badges ❶❷❸, intent status chips, and source panel numbers.

### 3. "Ready When You Stopped" Milestone
- Emitted with `turn_completed` when `ready_at_end > 0`.
- Board 2: `✓ 2 of 3 parts were ready before you finished speaking · about 1.3 s sooner than waiting`
- Hidden when `ready_count == 0`. "Instant delivery" is **not used**.

### 4. Refinement as an In-Place Edit (Delta Engine)
- **Board 3:** Late constraint "Actually, make that 45 people" triggers delta patching.
- Only the affected section (Venue) shows updated text. Old text is struck through.
- Unchanged sections are dimmed to 60% opacity, labelled "Unchanged".
- Version badge: "Updated · v2". "See what changed" opens the right-side change panel.
- Footer: "Only the part you changed was looked up again · 1 new search, 2 parts kept exactly as they were".

### 5. Two-Speed Text (Extractive Draft → Fluent Rewrite)
- Speed-1 extractive text appears first.
- When `speed2_completed` arrives, text cross-fades via `transition-opacity duration-300 ease-in-out` with zero layout shift. The source pill does not move.

### 6. Honest Gap Cards
- Board 2: Amber card at the bottom of the Catering section.
- Title: "Not in the documents". Body: "I couldn't find catering details for Riverside Hall."
- Actionable pill button: "Ask differently" (pre-fills the query box).

### 7. Story Mode Auto-Play
- Board 1: "Play the demo" button in header. Story bar at top with DEMO badge, scenario counter, progress dots, pause/next/exit controls.
- Caption text explains the pipeline actions to judges in real time.

---

## 4. Complete Microcopy Dictionary (`strings.en.json`)

```json
{
  "app": {
    "title": "Kairos",
    "subtitle": "Answers while you speak"
  },
  "header": {
    "assistant": "Assistant",
    "inspector": "Show how it works",
    "playDemo": "Play the demo",
    "status": {
      "connected": "Connected",
      "connecting": "Connecting…",
      "offline": "Offline",
      "reconnecting": "Reconnecting in {{seconds}}s…"
    }
  },
  "storyBar": {
    "badge": "DEMO",
    "counter": "{{current}} of {{total}}",
    "exit": "Exit"
  },
  "transcript": {
    "speaking": "You're speaking",
    "said": "You said",
    "addedDetail": "You added a detail",
    "changesPart": "changes part {{n}}",
    "listeningForMore": "Listening for more…",
    "intentFound": "found",
    "intentLooking": "looking it up",
    "earlier": "Earlier"
  },
  "answer": {
    "title": "Answer",
    "formingWhileYouSpeak": "Forming while you speak",
    "checkedAgainstSources": "Every sentence checked against {{count}} sources",
    "draftStatus": "Draft · checked against source",
    "lookingUp": "Looking this up…",
    "listening": "Listening…",
    "updated": "Updated",
    "unchanged": "Unchanged",
    "versionBadge": "Updated · v{{version}}",
    "seeWhatChanged": "See what changed",
    "readyBeforeFinished": "{{ready}} of {{total}} parts were ready before you finished speaking",
    "timeSaved": "about {{time}} s sooner than waiting",
    "partChangedNote": "Only the part you changed was looked up again · {{newSearches}} new search, {{keptParts}} parts kept exactly as they were",
    "noNewSearch": "No new search needed"
  },
  "gap": {
    "title": "Not in the documents",
    "askDifferently": "Ask differently"
  },
  "quickActions": {
    "shorter": "Shorter",
    "asBullets": "As bullets",
    "explainSimply": "Explain simply",
    "copy": "Copy"
  },
  "sources": {
    "title": "Sources",
    "count": "{{passages}} passages · {{documents}} documents",
    "countSoFar": "{{count}} so far",
    "openDocument": "Open the full document →"
  },
  "changePanel": {
    "title": "What changed in v{{version}}",
    "statusUpdated": "Updated",
    "statusKept": "Kept as is",
    "sourcesKept": "All {{count}} earlier sources kept. Source {{n}} was read again for the new group size.",
    "whyFast": "Why this is fast",
    "whyFastBody": "Kairos keeps the parts of your answer that are still true and only rechecks the part your new detail affects, instead of starting over."
  },
  "input": {
    "placeholder": "Tap the mic, or type a question or a new detail…",
    "keepTalking": "Keep talking. Kairos is already looking things up.",
    "stop": "Stop"
  },
  "inspector": {
    "tabs": {
      "timeline": "Timeline",
      "race": "Race vs. batch",
      "results": "Results",
      "corpus": "Corpus",
      "tryIt": "Try it yourself"
    },
    "timeline": {
      "scenarioLabel": "Scenario {{n}} · turn {{turnId}} · sample timing",
      "title": "Search and drafting started while the speaker was still talking",
      "leadTime": "Lead time",
      "readyAtEnd": "Ready at end",
      "madeUpCitations": "Made-up citations",
      "speechRow": "Speech",
      "decisionRow": "Decision",
      "speakerStopped": "Speaker stopped · {{time}} s",
      "replayTo": "Replay to"
    },
    "claims": {
      "title": "Claims · version {{version}}",
      "subtitle": "each checked before it is shown",
      "verified": "verified",
      "notFound": "not found",
      "noSource": "no source"
    },
    "eventLog": {
      "title": "Event log",
      "openJaeger": "Open trace in Jaeger →"
    }
  },
  "howItWorks": {
    "title": "How Kairos works",
    "body": "It starts looking things up as soon as it understands part of your question, and checks every sentence against the documents before showing it. If something isn't in the documents, it says so."
  },
  "errors": {
    "micBlocked": "Microphone access blocked. Type your question below.",
    "rateLimit": "You're going fast — please pause for a moment.",
    "messageTooLarge": "Message exceeds the maximum allowable length.",
    "serverError": "Something went wrong. Let's try that again.",
    "connectionLost": "Connection interrupted · Reconnecting in {{seconds}}s…"
  }
}
```

---

## 5. Motion Specification

| Element | Trigger / Event | Duration | Easing / Physics | Reduced-Motion Fallback |
|---|---|---|---|---|
| **Mic Orb** | Voice amplitude RMS | Continuous | Spring: `stiffness: 300, damping: 20` | Static coloured dot |
| **Intent status chip** | Controller `RETRIEVE` | 200 ms | `cubic-bezier(0.16, 1, 0.3, 1)` slide-in | Immediate opacity 1 |
| **Ghost Card Enter** | `subqueries_updated` | 180 ms | `ease-out` scale `0.98 → 1.0` | Immediate appearance |
| **Skeleton Pulse** | Loading state | 1500 ms loop | Linear opacity 0.4 → 0.8 | Static bars |
| **Settled Checkmark** | `turn_completed` | 300 ms | Quick pop spring | Static check icon |
| **Strikethrough on v2** | Version update | 600 ms | Linear | Immediate strikethrough |
| **In-Place Edit Highlight** | Version update v1→v2 | 2000 ms decay | Linear colour fade (`intent → transparent`) | Static "Updated" badge |
| **Source Panel Expand** | Source card tap | 240 ms | `cubic-bezier(0.32, 0.72, 0, 1)` | Discrete open/close |
| **Mobile Source Sheet** | "Sources" button tap | 300 ms | Spring slide-up | Discrete open/close |

---

## 6. Accessibility Plan (WCAG 2.2 AA)

1. **Focus Traversal:** Skip link → Mode toggle → Story controls (if active) → Transcript → Answer cards → Quick actions → Input box → Mic button → Sources panel.
2. **Screen Reader Announcements (`aria-live`):** Streamed answers use `aria-live="polite"` on completed sections. Mic button announces: "Microphone listening" / "Microphone stopped".
3. **Contrast Compliance (4.5:1 target):**
   - `--text-primary` (`#ECE9E2`) on `--bg-canvas` (`#0E1014`): **14.7:1** (AAA Pass)
   - `--text-primary` on `--bg-surface-1` (`#15181E`): **12.8:1** (AAA Pass)
   - `--text-secondary` (`#A3A9B5`) on `--bg-canvas`: **7.2:1** (AA Pass)
   - `--text-tertiary` (`#7D8594`) on `--bg-canvas`: **4.8:1** (AA Pass)
   - `--intent-1` (`#8FB3FF`) on `--bg-surface-1`: **6.9:1** (AA Pass)
   - `--intent-2` (`#62D6B4`) on `--bg-surface-1`: **8.1:1** (AA Pass)
   - `--intent-3` (`#B98CFF`) on `--bg-surface-1`: **5.8:1** (AA Pass)
4. **Keyboard Shortcuts:**
   - `Space`: Hold to talk / toggle listening
   - `/`: Focus text input
   - `I`: Toggle Assistant / Inspector
   - `Esc`: Close any open drawer, modal, or source sheet
   - `1`–`5`: Switch Inspector tabs

---

## 7. Inspector Mode Projector Ergonomics

Conference rooms and hackathon demo stages have washed-out projector lighting:
1. **High Contrast Borders:** Cards use `--border-default` (`#1E2330`) with 1.5 px weight.
2. **Typography Scale:** Minimum 14 px in Inspector, 16 px section headers, 28+ px KPI numbers.
3. **Gantt Bars:** Saturated intent colours fill the bars. Diamond icons for "draft verified".
4. **Replay Slider:** Oversized drag handle (24×24 px touch target) for easy live demonstration.
5. **Event Log:** Monospace font, tabular alignment, sufficient line height (1.6) for readability.

---

## 8. Component State Matrix

| Component | Empty State | Loading / Connecting | Streaming / Drafting | Gap / Uncertain | Updated (v2) | Error |
|---|---|---|---|---|---|---|
| **Answer Canvas** | Suggested prompts | Skeleton bars pulse | Ghost + draft cards | Amber gap card | Strikethrough + new text | Red warning card |
| **Transcript** | "Listening…" placeholder | Cursor pulse | Intent-underlined words | Normal text | "Earlier" + dimmed | "Audio failed" |
| **Timeline** | Clean empty axis | Syncing clock | Active Gantt bars | Striped bar for gap | Split revision bar | Overrun red bar |
| **Source Pill** | Hidden | Grey skeleton | Outline chip | Muted text | Highlighted | "Unverified" |
| **Mic Orb** | Calm ring | Rotating dot | Spring voice waves | Static ring | Static ring | Slash icon |
| **Sources Panel** | "No sources yet" | Skeleton cards | Source cards appear | Gap note | "Source re-read" note | Retry prompt |

---

## 9. The 20-Second First Impression Choreography

When a judge or user launches Story Mode:
- **0–3 s:** Orb reacts; compound query begins streaming in the transcript.
- **4–7 s:** At the word "Pune", the intent status chip "● Venue for 30 people · found" pops in. Ghost section appears.
- **8–12 s:** First section fills with verified text **while the user is still speaking**. "Draft · checked against source" appears.
- **13–16 s:** Speech finishes. Cards settle with ✓ check. Remaining sections fill.
- **17–20 s:** "2 of 3 parts were ready before you finished speaking · about 1.3 s sooner than waiting" appears.
- **Outcome:** *"It answered me while I was still speaking!"*

---

## 10. Design Board Reference

The canonical visual reference is the 5 board PNGs in `docs/design/`:

| Board | File | Content |
|---|---|---|
| 1 | `board_01.png` | Assistant while speaking (mid-utterance, skeleton, sources panel) |
| 2 | `board_02.png` | Assistant settled (all sections, gap card, ready line, quick actions) |
| 3 | `board_03.png` | Assistant refined v2 (strikethrough, unchanged dimmed, change panel) |
| 4 | `board_04.png` | Inspector timeline (Gantt, KPI cards, claims, event log) |
| 5 | `board_05.png` | Phone layout (compact single-column, bottom mic) |

Step 11 (UI build) **must** build to these boards and compare screenshots against them.
