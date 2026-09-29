# HUMAN_TASKS.md — things only people can do

The agent adds items here instead of stopping. None of them block the build. The more of them you do, the higher the score, because judges trust human-checked results more. Tick an item by changing `open` to `done`.

| # | Task | Why it matters | How (short) | Status |
|---|---|---|---|---|
| H1 | Push to GitHub regularly | Your work is only safe and submittable once it's on GitHub. | `git push && git push --tags` after each `/build-next`. | open |
| H2 | Replace the placeholder corpus when the real one is available | Answers must come from the supplied corpus. | Follow `data/corpus/README.md`, then type `/build-next`. | open |
| H3 | Review the test-set gold labels (after step 08) | Unreviewed labels weaken every gate number. | Open `data/replay/test/gold.jsonl`, fix anything wrong, set `review_status: reviewed`. Each of you does 20 turns independently first (for the agreement score). | open |
| H4 | Get test questions from classmates (after step 08) | A test set written only by an AI looks self-serving to judges (JUDGE_REVIEW §3). | Send `eval/external_turns/INSTRUCTIONS.md` to 4–6 classmates; paste their questions into a file in `eval/external_turns/` and type `/build-next`. | open |
| H5 | Blind fluency ratings (after step 09) | Evidence that rewritten answers read better than raw extracts. | Open `eval/fluency/ratings.json`, review ratings for 20 sampled turns, then run `python -m eval.fluency.score` to update `runs/eval/fluency_results.json`. | open |
| H6 | 5-person usability test (after step 11) | Real UX evidence (SUS score). | Follow `docs/UX_TEST.md`, then ask the agent to run `build/steps/p09c-usability-results.md`. | open |
| H7 | Record the ≤ 5-minute demo video (after step 14) | A required deliverable. | Follow `docs/DEMO_SCRIPT.md`; record the screen while Story mode plays and narrate. | open |
| H8 | Fill in the presentation deck (after step 14) | A required deliverable; blanks look unfinished. | Use the numbers sheet in `docs/presentation/`. | open |
| H9 | Final push with the release tag | The judged commit must carry the tag. | `git push origin main --tags`. | open |
| H10 | Capture 20-second Story mode demo GIF | Gives judges an immediate visual preview of live streaming RAG in README. | Run Story mode at http://localhost:8000, record 20s GIF, save to `docs/img/story_mode_demo.gif`. | open |
