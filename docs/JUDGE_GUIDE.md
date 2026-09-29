# Kairos — Judge & Evaluator Guide

Welcome to the **Kairos Streaming Live RAG Engine** held-out evaluation guide.

This guide provides instructions for hackathon judges and evaluators to run replay evaluations against **your own private held-out transcripts** and **your own held-out corpus**.

---

## 1. Quick Start: One-Command Evaluation

To evaluate on our pre-packaged frozen test set:

```bash
docker compose up -d
docker compose run --rm kairos make eval
```

This completes without network calls or external API keys and outputs results to `runs/eval/`.

---

## 2. Running On Held-Out Transcripts & Custom Corpora

Kairos provides a dedicated, corpus-agnostic CLI runner:

### A. Indexing Your Custom Corpus

If evaluating against a custom document folder (`.md`, `.txt`, `.html`, `.pdf`, `.docx`, `.json`):

```bash
docker compose run --rm kairos kairos index --corpus /path/to/your/corpus
```

Or locally:
```bash
python -m kairos.cli index --corpus /path/to/your/corpus
```

**How Kairos handles custom documents:**
1. Document IDs are automatically derived from filenames (e.g. `Doc_12.md` -> `Doc_12`) or embedded document IDs.
2. Documents without Markdown headings fall back to sliding paragraph-window sections, guaranteeing stable `[Doc_ID §Section]` citation markers.
3. Automatically computes SHA-256 manifests and scans for indirect injection patterns.

---

### B. Replaying Held-Out Transcripts

```bash
docker compose run --rm kairos kairos replay \
  --transcripts /path/to/your/transcripts.jsonl \
  [--corpus /path/to/your/corpus] \
  --out runs/judge_evaluation/
```

Or locally:
```bash
python -m kairos.cli replay \
  --transcripts /path/to/your/transcripts.jsonl \
  --out runs/judge_evaluation/
```

---

## 3. Supported Transcript Input Formats

Kairos uses a tolerant input adapter (`kairos/stream/adapters.py`) supporting multiple input formats:

### Format 1: Standard JSONL (One Turn per Line)
```json
{"session_id": "eval-01", "turn_id": "t1", "turn_type": "compound", "chunks": [{"t": 0.0, "text": "I need to check venue capacity in Pune"}, {"t": 1.0, "text": "and catering options."}], "utterance_end": 1.8}
```

### Format 2: Field Aliases & Alternate Timestamps
The adapter automatically normalizes field name variations:
- Timestamp keys: `t`, `timestamp`, `timestamp_s`, `start`, `time`
- Text keys: `text`, `chunk`, `transcript`, `content`
- Missing `utterance_end`: automatically inferred from the final chunk arrival timestamp if absent.

### Format 3: Theme Guide Table Format (Plain Text)
Transcripts in the Theme Guide Example 1 table format are parsed automatically:
```text
0.0 s  "I need to plan a customer workshop in"
0.8 s  "Pune for 30 people, and I need"
1.6 s  "the cancellation policy and catering options."
[Utterance End: 2.1 s]
```

### Format 4: Directory of Session Files
Point `--transcripts` at a directory containing multiple `.json` or `.jsonl` files to replay all sessions sequentially.

---

## 4. Evaluation Output Files

All outputs are saved to the `--out <dir>` path:

| Output File | Contents |
|---|---|
| `events.jsonl` | One complete §2.4 JSON record per turn with exact Theme Guide schema keys (`retrieval_events`, `sub_queries`, `answer`, `citations`, `uncertainty`, `legs`, `controller_decisions`, `claims`, `version_diff`, `metrics`). |
| `gates.json` | Gate results G1–G6 (computed automatically if gold labels are supplied, otherwise telemetry metrics). |
| `metrics.json` | Differentiator metrics: Ready-at-End, TTFT, e2e latency, suppression rate, time saved vs baseline. |
| `summary.md` | Human-readable Markdown report summarizing results and latency. |

---

## 5. Threshold Generalization & Secondary Corpus Robustness

Kairos thresholds (drift thresholds, cosine deduplication, entity saturation, RRF $k=60$) are configured in `config/default.yaml` and designed for domain independence.

As part of pre-submission verification, replay was evaluated against a secondary, unrelated document set (synthetic IT policies and HR handbooks). The controller's suppression rate and early retrieval triggers generalized with zero code modifications, confirming that Kairos does not overfit to the primary corpus vocabulary.
