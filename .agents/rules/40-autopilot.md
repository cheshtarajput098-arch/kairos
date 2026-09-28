---
trigger: always_on
---

# Kairos — autopilot rules

The team builds Kairos by typing `/build-next` in a new conversation, again and again. Each run executes **exactly one step** from `build/SEQUENCE.md`. The humans are beginners and are **not available to answer questions** during a run. These rules make that work safely. They override any "ask me", "wait for my approval", "stop and wait" or "I will …" wording inside the step files.

## 1. Never block on a question
- When a step asks the human to choose, approve or provide something, decide yourself:
  1. use the default in `docs/DECISIONS.md` if one exists;
  2. otherwise choose the option that keeps every hard rule, is simplest to build and test, and is easiest to reverse.
- Record every such decision in the **Decisions log** in `docs/DECISIONS.md`: step, question, choice, one-line reason.
- Still write the plan artifact the step asks for (it's the audit trail), then continue without waiting for approval.

## 2. Verify, fix, and only then call it done
- Run the step's Verification commands yourself and read the real output.
- If anything fails, fix the cause and re-run. Up to **5 fix attempts** per failure.
- Never weaken a test, gate, threshold check or CI job to make it pass. Never edit the frozen test set to pass a gate. Never mark a step done with a failing verification.
- If it still fails after 5 attempts, set the step to `blocked` in `docs/PROJECT_STATE.md` with the exact error, what you tried, and the smallest next fix, then stop and tell the human to run `/unstick`.

## 3. Big steps are split, not rushed
If a step is too large to finish well in one run, finish a coherent, tested part, set the step to `in_progress (part k of n)` in `docs/PROJECT_STATE.md` with a precise list of what remains, commit, and stop. The next `/build-next` resumes it. Quality over speed: a half-built feature is worse than a missing one.

## 4. Human-only tasks never block the build, and are never faked
Some work needs real people: reviewing gold labels, test turns written by outsiders, the 5-person usability test, blind fluency ratings, recording the video, filling in the slide deck, pushing to GitHub.
- Add each one to `docs/HUMAN_TASKS.md` (what, why it matters, exact instructions, which file to fill in) and carry on.
- Where a result depends on it, write `TBD` or mark the data honestly (`review_status: unreviewed`, `source: llm_drafted`). Never invent participants, ratings, reviews or external turns. Reports must say plainly what is still unreviewed.

## 5. Git discipline
- At the end of every run: `git add -A` and `git commit -m "Step NN: <title>"` (add `(part k)` when split).
- Create tier tags locally when the step says so. **Never push**, never force, never rewrite history, never delete branches or tags.
- Never commit `.env`, secrets, model weights, indexes or `runs/` (they're in `.gitignore`).

## 6. Safety
- Never delete or edit files in `data/corpus/` (except when the placeholder is being replaced by the real corpus, which is a human action).
- No destructive shell commands (`rm -rf` outside build caches, `git reset --hard`, `docker system prune`). Clean up only files you created in this run.
- No network access from application code at runtime. Package installs happen through the lockfile and the Docker build.

## 7. Real corpus detection
At the start of every run, check `data/corpus/`. If the placeholder documents (the fictional "Veloria Systems" files described in its README) have been replaced by other files, the real corpus has arrived: before continuing the current step, rebuild the index, re-draft `data/replay/demo/` and `data/replay/dev/` against the new documents (marked `unreviewed`), re-run the checks, and note it in `docs/PROJECT_STATE.md` and `docs/HUMAN_TASKS.md`.

## 8. Keep context small
Read `AGENTS.md`, these rules, `docs/PROJECT_STATE.md`, `docs/DECISIONS.md`, the current step file, and **only the SPEC.md sections the step names**. Don't re-read the whole spec every run. Never read or edit files in `.bundle/`: they are the original download, and the repository files are the source of truth.

## 9. End-of-run report (always, in plain language for beginners)
Finish every run with a short message:
1. **Step:** number and title; status now `done`, `in_progress (part k of n)` or `blocked`.
2. **What was built**, in 3–6 plain bullets.
3. **Checks:** the verification commands you ran and their real results (pass/fail counts).
4. **Decisions you made for the team** (from the Decisions log).
5. **New human tasks**, if any (just the titles).
6. **Next:** "Open a new conversation and type `/build-next`" (or `/unstick` if blocked).
