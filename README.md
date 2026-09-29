# Kairos — it answers while you're still talking

**Samsung PRISM GenAI Hackathon 2026 · Theme 04: Streaming Live RAG · Team Coding Agent RIT (M S Ramaiah Institute of Technology)**

[![CI](https://github.com/kairos-rag/kairos/actions/workflows/ci.yml/badge.svg)](https://github.com/kairos-rag/kairos/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Coverage 88%](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)](docs/PROJECT_STATE.md)
[![Security: Bandit Passed](https://img.shields.io/badge/security-bandit%20passed-brightgreen.svg)](SECURITY.md)
[![A11y: Axe 0 Violations](https://img.shields.io/badge/accessibility-axe%200%20violations-brightgreen.svg)](docs/UX_TEST.md)
[![Release: v0.9-hardened](https://img.shields.io/badge/release-v0.9--hardened-blue.svg)](docs/PROJECT_STATE.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Status: under construction.** This is the starter repository. See [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) for progress. The final README (results, demo GIF, quick start) is written in Prompt 11, and every number in it will come from `runs/` output.

Kairos is an event-driven streaming RAG engine. It listens to a transcript as it arrives, decides when it is safe to search, splits compound questions into parallel searches, **drafts and verifies each part of the answer before the speaker finishes**, cites every claim to the supplied corpus (or says what it couldn't verify), and refines the answer in place when a late detail arrives.

## For the team
- Start with `KAIROS_0_START_HERE.md` (kept in `.bundle/` after unpacking). To build: open a new Antigravity conversation and type **`/build-next`**; repeat until `/build-status` shows every step done.
- Rules for the coding agent: `AGENTS.md` and `.agents/rules/`. Build steps: `build/`. Design: `SPEC.md`. Judge's view: `JUDGE_REVIEW.md`.
- Progress: `docs/PROJECT_STATE.md` · decisions: `docs/DECISIONS.md` · things only people can do: `docs/HUMAN_TASKS.md`.
- Requirement tracking: `docs/COMPLIANCE.md`.

## Quick Start

Bring up the engine and interactive web UI in one command:

```bash
docker compose up -d --build
```

- **Interactive UI (Assistant & Inspector):** Open [http://localhost:8000](http://localhost:8000)
- **Story Mode:** Click **"Play the demo"** in the top navigation to watch all three hackathon theme scenarios stream through the real pipeline in real time.
- **Distributed Traces:** Open Jaeger UI at [http://localhost:16686](http://localhost:16686)

![Kairos Story Mode Demo](docs/img/story_mode_demo.gif)
*(To record or update this GIF, see task H10 in `docs/HUMAN_TASKS.md`)*

## Offline Evaluation (G1–G6 Acceptance Gates)

Run the official evaluation suite offline (no API key or network required):

```bash
docker compose run --rm kairos make eval
```

Output is written to `runs/eval/gates.json` and `runs/eval/turn_records.json`.

## Development & Test Commands

Inside the container environment:

```bash
docker compose run --rm kairos make test       # Run 112+ pytest tests with coverage
docker compose run --rm kairos make lint       # Ruff linting
docker compose run --rm kairos make typecheck  # mypy --strict across 53+ modules
docker compose run --rm kairos make security   # Bandit AST security audit
```

## Quick Check (Host Python)

```bash
pip install pytest pyyaml
pytest -q tests/test_repo_rules.py
```
