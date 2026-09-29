# Presentation Deck Numbers Sheet — Kairos

Every number on our submission slides must come from measured runtime data in `runs/`. Use this sheet to fill every blank in the deck.

---

## 1. Corpus, Chunk & Dataset Counts

| Metric | Measured Value | Source File |
|---|---|---|
| **Corpus Document Count** | **8 documents** | `data/corpus/` (`Doc_10` to `Doc_17`) |
| **Corpus Chunk Count** | **27 chunks** | `index/chunks.json` |
| **Total Test Split Turns** | **64 turns** | `data/replay/test/scenarios.jsonl` |
| **Dev Split Turns** | **16 turns** | `data/replay/dev/scenarios.jsonl` |
| **RETRIEVE Turns in Test** | **52 turns** | `runs/eval/gates.json` |
| **SUPPRESS (Presentation) Turns** | **12 turns** | `runs/eval/gates.json` |
| **Compound Queries** | **19 turns** | `data/replay/test/scenarios.jsonl` |
| **Late Constraint Turns** | **18 turns** | `data/replay/test/scenarios.jsonl` |
| **Claims Evaluated (G4)** | **112 claims** | `runs/eval/gates.json` |

---

## 2. Acceptance Gates (Official vs Strict)

All values measured on the 64-turn frozen test split:

| Gate | Name | Official Threshold | Official Measured ($n$) | Strict Threshold | Strict Measured ($n$) | Status | Source File |
|---|---|---|---|---|---|---|---|
| **G1** | Offline Reproducibility | 1.0 | **1.0** ($n=1$) | 1.0 | **1.0** ($n=1$) | **PASS** | `runs/eval/gates.json` |
| **G2** | Early Retrieval Triggering | $\ge 0.80$ | **1.000** ($n=52$) | $\ge 0.80$ | **1.000** ($n=52$) | **PASS** | `runs/eval/gates.json` |
| **G3** | Multi-Intent Decomposition | $\ge 0.70$ | **0.9474** ($n=19$) | 1.0 | **0.9474** ($n=19$) | **PASS** | `runs/eval/gates.json` |
| **G4** | Grounding Integrity (Hallucinations) | $\le 0.00$ | **0.0000** ($n=112$) | $\le 0.00$ | **0.0000** ($n=112$) | **PASS** | `runs/eval/gates.json` |
| **G5** | Selective State Continuity | 1.0 | **1.000** ($n=18$) | 1.0 | **1.000** ($n=18$) | **PASS** | `runs/eval/gates.json` |
| **G6** | Structured Telemetry Schema | 1.0 | **1.000** ($n=64$) | 1.0 | **1.000** ($n=64$) | **PASS** | `runs/eval/gates.json` |

*Note: In Gate G4, 0 fabricated citations were emitted out of 112 claims (100% claim-to-chunk verification).*

---

## 3. Differentiator Headline Metrics

| Differentiator Metric | Measured Value | Denominator / Basis | Source File |
|---|---|---|---|
| **Ready-at-End Ratio (1.0x cadence)** | **65.4%** | 34 / 52 RETRIEVE turns | `runs/eval/gates.json` |
| **Ready-at-End Ratio (0.75x & 1.5x)** | **100.0%** | 52 / 52 RETRIEVE turns | `runs/eval/gates.json` |
| **Hidden Latency Fraction ($H$)** | **1.0 (100%)** | 52 / 52 RETRIEVE turns | `runs/eval/stabilisation.json` |
| **Median Trigger Gap ($t_{gap}$)** | **0.0 s** | 52 / 52 RETRIEVE turns | `runs/eval/stabilisation.json` |
| **Median Lead Time** | **1,800.0 ms** | p50 (mean 1,880.8 ms) | `runs/eval/metrics.json` |
| **Time-to-First-Token (TTFT)** | **p50 = 0.0 ms** | p95 = 15.0 ms, mean = 7.03 ms | `runs/eval/metrics.json` |
| **Presentation Suppression Rate** | **100.0%** | 12 / 12 presentation turns | `runs/eval/metrics.json` |
| **False Trigger Rate on Suppress** | **0.0%** | 0 / 12 false triggers | `runs/eval/metrics.json` |
| **Token Savings vs Restart** | **251 tokens** | Across late constraint turns | `runs/eval/metrics.json` |
| **Race Time Saved vs Batch Baseline**| **1.508 s median** | On shared virtual clock | `runs/eval/race.json` |
| **Fluency Rating (Ablation D)** | **5.0 / 5.0** | Speed 2 vs 3.92 for Speed 1 | `runs/eval/fluency_results.json` |

---

## 4. Hardware & Load-Test Numbers (2.0 CPU / 4096MB RAM)

| Concurrency Scenario | Error Rate | p50 Turn Latency | p95 Turn Latency | p50 TTFT | Peak RAM | Source File |
|---|---|---|---|---|---|---|
| **1 Session** | **0.0%** | **1,533.99 ms** | 2,486.66 ms | **386.84 ms** | **584.5 MB** | `runs/loadtest/results.json` |
| **10 Sessions** | **0.0%** | **8,489.03 ms** | 12,734.18 ms | **6,200.53 ms** | **1,539.2 MB** | `runs/loadtest/results.json` |
| **25 Sessions** | 46.0% (load-shedding)| 19,630.55 ms | 28,363.22 ms | 17,824.42 ms | **3,300.7 MB** | `runs/loadtest/results.json` |
| **Speed-2 Budget** | **Budget Respected** | 820.0 ms p95 (vs 1500 ms budget) | Qwen2.5-1.5B Q4_K_M | | `runs/loadtest/results.json` |
