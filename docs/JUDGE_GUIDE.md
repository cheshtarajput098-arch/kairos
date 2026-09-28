# JUDGE_GUIDE.md — run Kairos on your own transcripts

> Draft. Prompt 7 completes this with tested commands and real examples.

## 1. Start
```bash
git clone <repo-url> && cd kairos
docker compose up            # UI at http://localhost:8000, traces at http://localhost:16686
```
No API key is needed. Press **Play the demo** to watch the three theme scenarios.

## 2. Replay your held-out transcripts
```bash
docker compose run --rm kairos kairos replay --transcripts /path/to/your/transcripts --out /path/to/results
```
Accepted input (SPEC.md §9.6a): JSON or JSONL; one turn per line or one session per file; chunk fields named `t`/`timestamp`/`timestamp_s`/`start` and `text`/`chunk`/`transcript`; an `utterance_end` value or an `[Utterance End]` marker; or plain-text tables in the theme guide's format (`0.8 s  "…Pune for 30 people…"`).

## 3. Use your own corpus (optional)
```bash
docker compose run --rm kairos kairos index --corpus /path/to/your/corpus
```
Accepted: .md, .txt, .html, .pdf (text layer), .docx, .json.

## 4. What you get
- `results/events.jsonl`: one record per turn with the theme guide's exact keys (`retrieval_events`, `sub_queries`, `answer`, `citations`, `uncertainty`, and `retrieval_required`/`reason` on suppressed turns), plus our extra fields.
- `results/gates.json`: gate values when gold labels are supplied; otherwise telemetry-derived metrics.
- `results/summary.md`: a readable summary.

## 5. Where to look next
`docs/EVAL_REPORT.md` (results with n, failures, ablations), `docs/ARCHITECTURE_BRIEF.pdf`, `docs/TELEMETRY_SCHEMA.md`, `SECURITY.md`.
