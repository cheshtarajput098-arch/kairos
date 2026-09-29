# Operations Runbook — Kairos

This document provides operational specifications, service-level objectives (SLOs), configuration references, and runbooks for operating Kairos in production and evaluation environments.

---

## 1. System Architecture & Component Limits

Kairos is a low-latency, event-driven streaming live RAG engine designed to run entirely on laptop-class CPU hardware.

### Service Level Objectives (SLOs)

| Metric | Target (Laptop CPU) | Fallback Behavior |
|---|---|---|
| **Retrieval Stage Deadline** | < 400 ms per leg | Cancel in-flight leg; return partial sparse/dense candidates |
| **Speed-1 Extractive Synthesis** | < 50 ms per turn | Directly stream top-scoring chunk sentence |
| **Speed-2 Grounded Rewrite Deadline** | < 2500 ms per turn | Retain Speed 1 extractive claim (`rewrite_rejected`) |
| **Ready-at-End Ratio** | >= 70% of answers ready at speech end | Fall back to immediate end-of-utterance emission |
| **Memory Footprint** | <= 4 GB total RAM | CPU quantized model (Q4_K_M) + lazy FastEmbed loading |
| **Circuit Breaker Trip Threshold** | 3 consecutive failures | 30s fast-fail window to protect CPU from starvation |

---

## 2. Configuration Reference (`config/default.yaml`)

### Key Parameters

```yaml
models:
  local_llm:
    enabled: true                                       # Falls back to Speed 1 automatically if missing
    gguf_file: models/qwen2.5-1.5b-instruct-q4_k_m.gguf
    sha256: d34d8e8b0b8c6a2e457f920211a5ef5999818b2c4516df240092f61a15328214
    n_threads: 4
    context_tokens: 4096
    max_output_tokens: 256
    temperature: 0.0

synthesis:
  speed2:
    enabled: true
    provider: local                                     # local | none | hosted
    deadline_ms: 2500
    run_policy: after_draft                             # after_draft | after_utterance_end | off
    circuit_breaker:
      failures_to_open: 3
      reset_after_s: 30
```

---

## 3. Operational Runbooks

### Runbook 1: Fresh Machine Deployment (Evaluation Gate G1)
To run Kairos on a fresh system with zero pre-existing models or API keys:
```bash
docker compose up --build -d
docker compose run --rm kairos make ready
docker compose run --rm kairos make eval SPLIT=test
```
*Note: If the GGUF model file is absent, Kairos automatically degrades to pure Speed-1 extractive synthesis, guaranteeing 100% G1 reproducibility with zero external downloads required.*

### Runbook 2: Index Verification & Integrity Re-indexing
To verify corpus integrity or rebuild indexes after document updates:
```bash
docker compose run --rm kairos python -m kairos.cli index --corpus data/corpus
```

### Runbook 3: Circuit Breaker Recovery
If the local LLM exceeds deadlines or encounters corrupted context, the circuit breaker opens:
1. Calls to `generate_json` fail fast for 30 seconds.
2. Speed-1 extractive answers continue to stream uninterrupted.
3. After 30 seconds, a probe call checks model liveness and auto-recovers to `CLOSED`.

---

## 4. Disaster Recovery & Security Boundaries

1. **Corpus Isolation**: Inbound network egress from synthesis pipelines is blocked. Parametric knowledge injection is forbidden.
2. **Read-Only Rootfs**: Containers operate with `read_only: true`. Runtime state is written only to tmpfs or mounted `runs/` volumes.
3. **Session Auto-TTL**: In-memory sessions expire after 1800 seconds and are purged from RAM.
