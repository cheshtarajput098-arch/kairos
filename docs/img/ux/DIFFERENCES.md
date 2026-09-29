# UX Screenshots & Visual Alignment Differences (SPEC §14, Item 14)

Captured at 1440px (Desktop) and 390px (Mobile) viewports directly from the running engine:
- `docs/img/ux/assistant_desktop_1440px.png`: Desktop Assistant Mode (1440×900)
- `docs/img/ux/inspector_desktop_1440px.png`: Desktop Inspector Mode (1440×900)
- `docs/img/ux/assistant_mobile_390px.png`: Mobile Assistant Mode (390×844, iPhone 14/15 viewport)

---

## Comparison with Design Boards (`docs/design/board_01.png` – `board_05.png`)

| Screen / Feature | Design Board Reference | Implementation Status | Notes / Differences |
|---|---|---|---|
| **Mic Bar** | Board 1 & 2 bottom bar | Fully Implemented | 54px ivory circular mic orb with active listening ring (`ring-4 ring-[#ECE9E2]/30 animate-pulse`), live copy: *"Listening… Keep talking. Kairos is already looking things up."*, Stop button, integrated input field, and send button. |
| **First-Run Suggestions** | Board 1 initial state | Enhanced (Dynamic) | Instead of hand-written sample questions, 3–5 suggested questions are dynamically generated from corpus headings at index time (`/v1/suggestions`) per Item 6. |
| **Two-Speed Text & Cross-Fade** | Board 2 & SPEC §6.2 | Fully Implemented | Speed-2 rewrite cross-fades over the Speed-1 sentence using zero-shift CSS grid stacking (`col-start-1 row-start-1`), and source pills sit in a stable container immediately following without moving. |
| **Draft Rollback** | SPEC §5.4 | Fully Implemented | When a draft is retracted (`status === 'retracted'`), it fades to 30% opacity with a spinner ("Refilling draft with updated details…") and smoothly cross-fades to 100% when the replacement draft arrives. |
| **Source Pills & Popover** | Board 2 & 5 | Fully Implemented | Sequential numbers (1, 2, 3...) in order of first appearance. Hover or focus reveals the exact quoted passage; clicking opens and highlights the quoted sentence in the Sources panel. |
| **Quick Actions** | Board 2 bottom row | Fully Implemented | *Shorter*, *As bullets*, *Explain simply*, *Copy*. The first three run as presentation-only turns with zero searches (`retrievals = 0`). *"No new search needed"* appears only after clicking presentation actions. |
| **Status Banners & Error States** | SPEC §14.5 | Fully Implemented | Includes offline/reconnecting banner with auto-retry, mic permission denied banner with "Type instead" focus, HTTP 429 rate limit card with `request_id`, out-of-scope card, and general error cards with `request_id`. |
| **Settings Sheet** | SPEC §14.3a | Fully Implemented | Slide-over drawer with *"Show answer while I speak"* toggle (controls provisional draft visibility) and *Text size* selector (Normal 15px, Large 17px, Extra Large 19px). |
| **Session Telemetry Feedback** | SPEC §14.3 | Fully Implemented | Thumbs up / thumbs down buttons on settled answers emitting ephemeral telemetry events (`/v1/telemetry/feedback`) without persistent user profiling (Corpus Isolation Rule 4). |
| **Self-Hosted Typography** | SPEC §14.2 | Fully Implemented | `@font-face` declarations for Geist, Newsreader, and Geist Mono with system fallbacks. Zero network requests to Google Fonts or external CDNs. |
| **Accessibility & Shortcuts** | SPEC §14.7 | Fully Implemented | `aria-live="polite"` on answer canvas; keyboard shortcuts (`Space` talk/stop, `/` focus input, `I` toggle Inspector, `Esc` close); `@media (prefers-reduced-motion: reduce)` disables all animations. |
| **Inspector Tabs** | Board 4 | Fully Implemented | 5 sub-tabs (*Timeline*, *Race vs. batch*, *Results*, *Corpus*, *Playground*). Timeline Gantt chart with lead time KPIs, verified claims table, and event log with Jaeger deep link. |
| **Mobile Layout (390px)** | Board 5 | Fully Implemented | 100% responsive fluid column, touch targets $\ge 44\text{px}$, bottom drawer modal for Sources with badge count, and mobile-friendly Story bar. |
