---
description: Show Kairos build progress and what's left
---

When the user types `/build-status`, read `docs/PROJECT_STATE.md`, `build/SEQUENCE.md`, `docs/HUMAN_TASKS.md` and `docs/COMPLIANCE.md`, and reply in plain language with:
1. A table of all 14 steps with status (done / in progress / blocked / to do) and the tags created so far.
2. The current tier, and whether the project is already submittable at that tier.
3. Open human tasks, most important first.
4. How many COMPLIANCE.md rows are done vs pending.
5. The next action (usually "type /build-next in a new conversation").
Do not change any files.
