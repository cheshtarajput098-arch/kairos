# Slide Deck Exact Value Mapping — Kairos Presentation

Use this reference to populate all blank placeholders in the hackathon presentation deck. All numbers are verbatim from measured runtime runs in `runs/`.

---

### Slide 8: Sequential Batch Baseline vs Kairos Race (Shared Virtual Clock)
- **Evaluation Dataset:** 64-turn frozen test split (`runs/eval/race.json`)
- **Median Turn Time Saved:** `1.508 seconds`
- **Mean Turn Time Saved:** `1.579 seconds`
- **Fraction of Turns with Savings:** `100.0%` of RETRIEVE turns ($52 / 52$)
- **Baseline Turn Latency (p50):** `3.708 s`
- **Kairos Turn Latency (p50):** `2.200 s` (Ready-at-End milestone)
- **Restart Token Waste:** `0 tokens` in Kairos vs full prompt re-ingest in baseline

---

### Slide 9: Dual Acceptance Gates Benchmark (SPEC §9.1)
*Source: `runs/eval/gates.json` (Frozen Test Split, n=64 turns, n=112 claims)*

| Gate | Description | Threshold | Official Result ($n$) | Strict Result ($n$) |
|---|---|---|---|---|
| **G1** | Offline Reproducibility | 1.0 | `1.0` ($n=1$) | `1.0` ($n=1$) |
| **G2** | Early Retrieval Triggering | $\ge 0.80$ | `1.000` ($n=52$) | `1.000` ($n=52$, mean lead 1.88s) |
| **G3** | Multi-Intent Decomposition | $\ge 0.70$ | `0.9474` ($n=19$) | `0.9474` ($n=19$) |
| **G4** | Grounding Integrity (Fabricated IDs) | $\le 0.00$ | `0.0000` ($n=112$) | `0.0000` ($n=112$, 0 fabricated) |
| **G5** | Selective State Continuity | 1.0 | `1.000` ($n=18$) | `1.000` ($n=18$, byte-identical) |
| **G6** | Telemetry Schema Compliance | 1.0 | `1.000` ($n=64$) | `1.000` ($n=64$) |

---

### Slide 10: Conversational State Evolution & Delta Engine
- **Example Turn:** Use the **Travel Reimbursement policy** (`Doc_05`) example to match Demo Video Scene 2:
  - *Turn 1:* "What is the filing deadline for domestic travel expenses, and what currency conversion rate applies?"
  - *Turn 2 (Late Detail):* "Actually, what if the trip was international?"
  - *Result:* Claim 1 (domestic deadline) preserved byte-identical (Gate G5); Claim 2 (conversion rate) patched with `Doc_05§3` in-place.
  - *Turn 3 (Presentation Restructure):* "Can you show that as bullet points?"
  - *Result:* Zero retrieval queries dispatched (`NO_RETRIEVAL(presentation_restructure)`), 0 new tokens, instant local reformatting.

---

### Slide 11: Differentiator Metrics — Answers While You Speak
*Source: `runs/eval/gates.json` & `runs/eval/stabilisation.json`*
- **Ready-at-End (1.0x speech cadence):** `65.4%` ($34 / 52$ turns ready the moment speech stops)
- **Ready-at-End (0.75x & 1.5x cadences):** `100.0%` ($52 / 52$ turns)
- **Hidden Retrieval Latency Fraction ($H$):** `1.0` ($100\%$ hidden)
- **Controller Trigger Gap ($t_{gap}$):** `0.0 seconds` median
- **Median Lead Time Before Utterance End:** `1,800.0 ms`
- **Time-to-First-Token (TTFT):** `p50 = 0.0 ms` (pre-drafted in cache), `p95 = 15.0 ms`

---

### Slide 12: Screenshots & UI Architecture
Insert the high-resolution screenshots saved in `docs/screenshots/`:
1. **Desktop Home (Board 6):** `docs/screenshots/board_06_home_desktop.png` (Hero mic orb + scenario cards)
2. **Conversation & Source Panel (Board 7):** `docs/screenshots/board_07_conversation_desktop.png` (Intent color badges + quotes drawer)
3. **Mid-Answer Streaming State:** `docs/screenshots/mid_answer_scenario_1.png` (Ghost sections + shimmer drafting + ║║║ waveform)
4. **Knowledge Sources (Board 8):** `docs/screenshots/board_08_sources_desktop.png` (Hybrid index stats + chunk table)
5. **Traces & Timeline (Board 9):** `docs/screenshots/board_09_traces_desktop.png` (Per-turn Gantt tracks + grounding checks)

---

### Slide 13: Two-Speed Grounded Synthesis & Local LLM
*Source: `runs/loadtest/results.json` & `runs/eval/fluency_results.json`*
- **Model:** `Qwen2.5-1.5B-Instruct-Q4_K_M` GGUF running 100% locally on CPU
- **Speed 1 (Extractive):** `< 1 ms` latency, exact verbatim excerpt, `100%` deterministic GroundingGate check
- **Speed 2 (Grounded Rewrite):** `820.0 ms` p95 rewrite latency (vs `1,500 ms` budget target)
- **Blind Fluency Rating (Ablation D):** `5.0 / 5.0` for Speed 2 vs `3.92 / 5.0` for Speed 1 (`+1.08` points improvement)
- **Inter-Rater Agreement:** `82.5%` absolute agreement, `100.0%` within $\pm 1$ point, Cohen's Kappa $\kappa = 0.689$
- **Circuit Breaker:** Automatic fallback to Speed 1 after 3 failures; 0 dropped turns

---

### Slide 14: Hardware Efficiency & Concurrency Benchmark
*Source: `runs/loadtest/results.json` (Evaluated on 2.0 CPU cores, 4096 MB RAM limit)*

| Concurrency | Error Rate | p50 Turn Latency | p95 Turn Latency | Peak Memory | Memory vs Ceiling |
|---|---|---|---|---|---|
| **1 Session** | `0.0%` | `1,533.99 ms` | `2,486.66 ms` | `584.5 MB` | `14.3%` of 4GB |
| **10 Sessions** | `0.0%` | `8,489.03 ms` | `12,734.18 ms` | `1,539.2 MB` | `37.6%` of 4GB |
| **25 Sessions** | `46.0%` (shed) | `19,630.55 ms` | `28,363.22 ms` | `3,300.7 MB` | `80.6%` (safe < 4GB) |

---

### Slide 15: Security, OWASP GenAI Top 10 & Red-Team Audit
*Source: `runs/eval/redteam.json` & `SECURITY.md`*
- **Adversarial Test Turns:** `32 turns` across 5 threat categories (Prompt Injection, Poisoning, PII Exfiltration, Denial-of-Service, Tampering)
- **Attack Success Rate (with Spotlighting):** `0.0%` ($0 / 32$)
- **Refusal / Safe Handling Rate:** `100.0%` ($32 / 32$)
- **PII Masking Rate:** `100.0%` (Credit cards, phone numbers, email addresses masked)
- **Security Middleware Latency Overhead:** `0.01 ms` per turn (`1.0%` of turn budget)
- **Supply Chain Integrity:** SHA-256 manifest check on corpus and model files at startup
