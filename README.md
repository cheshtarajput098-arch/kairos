# Kairos — it answers while you're still talking

**Samsung PRISM GenAI Hackathon 2026 · Theme 04: Streaming Live RAG · Team Coding Agent RIT (M S Ramaiah Institute of Technology)**

> **Status: under construction.** This is the starter repository. See [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) for progress. The final README (results, demo GIF, quick start) is written in Prompt 11, and every number in it will come from `runs/` output.

Kairos is an event-driven streaming RAG engine. It listens to a transcript as it arrives, decides when it is safe to search, splits compound questions into parallel searches, **drafts and verifies each part of the answer before the speaker finishes**, cites every claim to the supplied corpus (or says what it couldn't verify), and refines the answer in place when a late detail arrives.

## For the team
- Start with `KAIROS_0_START_HERE.md` (kept in `.bundle/` after unpacking). To build: open a new Antigravity conversation and type **`/build-next`**; repeat until `/build-status` shows every step done.
- Rules for the coding agent: `AGENTS.md` and `.agents/rules/`. Build steps: `build/`. Design: `SPEC.md`. Judge's view: `JUDGE_REVIEW.md`.
- Progress: `docs/PROJECT_STATE.md` · decisions: `docs/DECISIONS.md` · things only people can do: `docs/HUMAN_TASKS.md`.
- Requirement tracking: `docs/COMPLIANCE.md`.

## Quick check
```bash
pip install pytest pyyaml
pytest -q tests/test_repo_rules.py
```
