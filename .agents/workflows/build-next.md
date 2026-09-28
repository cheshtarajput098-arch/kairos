---
description: Build the next step of Kairos automatically (one step per run)
---

When the user types `/build-next`, do the following. Follow `.agents/rules/40-autopilot.md` throughout: never wait for the user, decide from `docs/DECISIONS.md`, and never fake human work.

1. **Load context.** Read `AGENTS.md`, every file in `.agents/rules/`, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md` and `build/SEQUENCE.md`.
2. **Check the corpus.** Apply autopilot rule 7 (real corpus detection).
3. **Pick the step.** In the status table in `docs/PROJECT_STATE.md`:
   - if a step is `in_progress` or `blocked`, resume that step (for `blocked`, first try the "smallest next fix" recorded there);
   - otherwise take the first step in `build/SEQUENCE.md` whose status is `todo`;
   - if every step is `done`, say so, summarise the project status and list the open items in `docs/HUMAN_TASKS.md`, then stop.
4. **Announce** in one line: "Running step NN: <title>". Set its status to `in_progress` in `docs/PROJECT_STATE.md`.
5. **Read the step file** in `build/steps/` and only the SPEC.md sections it names.
6. **Plan.** Write a short implementation plan artifact (files, tests, verification commands). Don't wait for approval.
7. **Build.** Implement the step. Write tests with or before the code.
8. **Verify.** A step can only be marked done when every Verification command has been run exactly as written (including any docker compose commands) and test coverage is at least 85%. Run the step's Verification commands, plus `pytest -q tests/test_repo_rules.py` and `make test`. Fix and re-run until green, up to 5 attempts per failure (autopilot rule 2).
9. **Record.**
   - `docs/PROJECT_STATE.md`: set the step to `done` (or `in_progress (part k of n)` / `blocked` with details), update "Done", "Next" and "Known issues".
   - `docs/COMPLIANCE.md`: update Status and Evidence for every row this step touched.
   - `docs/DECISIONS.md`: add every decision you made to the log.
   - `docs/HUMAN_TASKS.md`: add any human-only work this step created.
   - `CHANGELOG.md`: one line for the step (create the file if it doesn't exist).
10. **Commit** with `git add -A && git commit -m "Step NN: <title>"`. If `build/SEQUENCE.md` lists a tag for this step and the step is `done`, create it locally with `git tag -a <tag> -m "<title>"`. Never push.
11. **Report** using the end-of-run format in autopilot rule 9, ending with: "Open a new conversation and type `/build-next` to continue."
