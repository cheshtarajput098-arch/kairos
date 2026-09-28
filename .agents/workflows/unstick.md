---
description: Diagnose and fix a blocked Kairos build step
---

When the user types `/unstick`:

1. Read `AGENTS.md`, `.agents/rules/`, `docs/PROJECT_STATE.md` and `docs/DECISIONS.md`. Find the step marked `blocked` (or the last `in_progress` step) and the error recorded for it.
2. Reproduce the failure by re-running the exact failing command. Read the full output.
3. Find the root cause, not just the symptom. Check the obvious things first: missing dependency in the lockfile, wrong path, Docker not running, port already in use, model file not downloaded, a test that is itself wrong.
4. Apply the smallest fix that keeps every rule. Never weaken a test or gate to get past it; if a test itself is wrong, fix the test and explain why in `docs/DECISIONS.md`.
5. Re-run the step's full verification. If it now passes, set the step back to `in_progress` so `/build-next` can finish it (or `done` if everything in the step is complete), and commit.
6. If it still fails after 5 attempts, explain in plain, beginner-friendly language what is wrong and exactly what the human should do (for example "open Docker Desktop and wait until it says Running, then type /build-next"). Record it in `docs/PROJECT_STATE.md`.
7. End with: "Open a new conversation and type `/build-next`."
