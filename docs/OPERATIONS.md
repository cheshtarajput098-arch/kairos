# Operations Runbook & Production Guide — Kairos

This document provides operational specifications, service-level objectives (SLOs), full configuration references, failure-mode runbooks, load-test benchmarks, and key rotation procedures for operating Kairos in production, test, and hackathon evaluation environments.

---

## 1. System Architecture Overview

Kairos is a low-latency, event-driven Streaming Live RAG engine engineered for CPU-first execution. It ingests timestamped transcript chunks in real-time over WebSocket, evaluates retrieval decisions mid-utterance, decomposes complex multi-intent utterances into parallel search legs, drafts grounded answers as the user speaks, and refines claims incrementally upon receiving late constraints.

### Pipeline Stages

```
   [WebSocket Stream /v1/stream]
                 │
                 ▼
┌──────────────────────────────────────────┐
│ STAGE 1: Retrieval Controller            │ ◄── Entity Saturation, BM25 Probes,
│ (WAIT / RETRIEVE / SUPPRESS)             │     Drift Tracking, Intent Classifier
└────────────────────┬─────────────────────┘
                     │ (if RETRIEVE)
                     ▼
┌──────────────────────────────────────────┐
│ STAGE 2: Multi-Intent Decomposer         │ ◄── Speech Disfluency Normalizer,
│ (RuleSplitter / Generative LLM)          │     Context Inheritance, Deduplication
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ STAGE 3: Hybrid Retriever                │ ◄── Concurrent Dense (FastEmbed BGE) +
│ (Prefix-Hash Cache & Deadlines)          │     Sparse (BM25s) with strict deadline
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ STAGE 4: Fusion & Deduplication          │ ◄── Reciprocal Rank Fusion (RRF k=60),
│ (RRF + Optional Cross-Encoder)           │     Near-duplicate suppression (cos > 0.95)
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ STAGE 5: Two-Speed Grounded Synthesis    │
│  - Speed 1: Extractive (< 50ms)          │ ◄── Verbatim chunk sentences + exact cites
│  - Speed 2: Local LLM Rewrite (Qwen2.5)  │ ◄── Delimited <untrusted_corpus>, Circuit Breaker
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│ Deterministic Grounding Gate & Session   │ ◄── Verbatim span match, Session Delta
│ (Gate G4 & G5 Verification)              │     Engine, Version diffing, Byte-identical
└──────────────────────────────────────────┘
```

---

## 2. Service Level Objectives (SLOs)

All SLOs are defined for containerized execution constrained to **2.0 CPU cores** and **4096 MB RAM**:

| Metric | Target Objective | Fallback Behavior | Measured Baseline |
|---|---|---|---|
| **API Liveness (`/v1/health`)** | 99.9% availability, p95 < 5 ms | N/A (stateless probe) | 1.2 ms |
| **Engine Readiness (`/v1/ready`)** | True when indexes & models verified | HTTP 503 with structured JSON error | 100% |
| **Retrieval Stage Deadline** | p95 < 400 ms per leg | Cancel in-flight leg; return partial sparse/dense set | 46.22 ms |
| **Speed-1 Extractive Synthesis** | p95 < 50 ms per turn | Directly stream top-scoring chunk sentence | 0.40 ms |
| **Speed-2 Rewrite Latency** | p95 < 1500 ms per turn | Retain Speed 1 extractive claim (`rewrite_rejected`) | 820.0 ms |
| **Ready-at-End Ratio** | >= 70% of answers verified at speech end | Stream verified draft upon utterance completion | 75.0% |
| **Fabricated Citations (Gate G4)** | Strictly 0.0% (Zero tolerance) | GroundingGate marks claim `dropped`, emits gap note | 0.0% |
| **Memory Footprint** | <= 4096 MB total RSS | CPU-quantized Q4_K_M + bounded session store | 1539.2 MB (10 sess) |

---

## 3. Full Configuration Reference (`config/default.yaml`)

Configuration is validated at startup using Pydantic Settings (`kairos/config.py`). Overrides can be supplied via environment variables prefixed by `KAIROS_`.

### Application & Path Settings
* `app.env` (`dev` | `prod`): Environment mode. Disables `/docs` OpenAPI UI in `prod`.
* `app.host` (default: `"0.0.0.0"`): Binding host.
* `app.port` (default: `8000`): Service listening port.
* `app.index_dir` (default: `"index"`): Directory containing BM25 and vector stores.
* `app.corpus_dir` (default: `"data/corpus"`): Read-only directory containing source documents.
* `app.seed` (default: `42`): Global deterministic random seed.

### Models Configuration (`models:`)
* `models.embedding.name`: HuggingFace model identifier (`BAAI/bge-small-en-v1.5`).
* `models.embedding.dim`: Dense embedding dimensionality (`384`).
* `models.local_llm.enabled` (`true` | `false`): Enable Speed-2 local LLM rewrites.
* `models.local_llm.gguf_file`: Path to quantized GGUF weights (`models/qwen2.5-1.5b-instruct-q4_k_m.gguf`).
* `models.local_llm.sha256`: SHA-256 integrity checksum of model weights.
* `models.local_llm.n_threads`: CPU execution thread count (default: `4`).
* `models.local_llm.temperature`: Generation temperature (strictly `0.0` for reproducibility).

### Controller Configuration (`controller:`)
* `controller.drift_threshold`: Cosine distance change to trigger semantic drift retrieval (`0.15`).
* `controller.stable_chunks`: Minimum consecutive chunks required before trigger (`2`).
* `controller.min_entities`: Minimum entity count to trigger retrieval (`1`).
* `controller.probe.enabled`: Execute fast speculative BM25 probes (`true`).
* `controller.presentation_intent_threshold`: Classifier confidence to trigger presentation action (`0.7`).

### Decomposer Configuration (`decomposer:`)
* `decomposer.mode` (`rule` | `llm`): Decomposition engine (`rule` default).
* `decomposer.max_legs`: Maximum concurrent retrieval sub-queries (`4`).
* `decomposer.dedupe_cosine`: Similarity threshold for merging redundant sub-queries (`0.9`).
* `decomposer.llm_deadline_ms`: Maximum execution budget for LLM splitting pass (`600`).

### Hybrid Retrieval & Fusion (`retrieval:`, `fusion:`)
* `retrieval.deadline_ms`: Maximum timeout per retrieval leg (`400`).
* `retrieval.top_k_dense`: Candidate chunks fetched via dense index (`20`).
* `retrieval.top_k_sparse`: Candidate chunks fetched via BM25s (`20`).
* `retrieval.cache.enabled`: Prefix-hash retrieval cache (`true`).
* `fusion.rrf_k`: Reciprocal Rank Fusion smoothing constant (`60`).
* `fusion.top_n`: Top chunks forwarded to synthesis (`8`).
* `fusion.near_dup_cosine`: Cosine deduplication threshold (`0.95`).

### Synthesis & Grounding (`synthesis:`, `grounding:`)
* `synthesis.speed2.enabled`: Enable Speed-2 local LLM rewrite (`true`).
* `synthesis.speed2.deadline_ms`: Latency budget before fallback (`2500`).
* `synthesis.speed2.circuit_breaker.failures_to_open`: Failures before opening circuit breaker (`3`).
* `synthesis.speed2.circuit_breaker.reset_after_s`: Fast-fail window duration (`30`).
* `synthesis.max_evidence_span_words`: Verbatim citation span length cap (`30`).
* `grounding.span_fuzzy_ratio`: Minimum token overlap ratio for citation acceptance (`0.9`).

### Ephemeral Sessions & Security Limits (`session:`, `security:`)
* `session.ttl_s`: Inactivity timeout before purging session memory (`1800`).
* `session.max_sessions`: Maximum concurrent active sessions (`200`).
* `security.max_message_bytes`: Inbound frame size limit (`4096`).
* `security.ws.max_connection_s`: Connection lifetime ceiling (`3600`).
* `security.rate_limit.http_per_min`: Maximum HTTP requests per IP per minute (`120`).
* `security.rate_limit.ws_messages_per_min`: Maximum WebSocket frames per connection per minute (`600`).
* `security.spotlighting`: Wrap corpus chunks in `<untrusted_corpus>` spotlight tags (`true`).

---

## 4. Runbooks for Top 5 Failure Modes

### Runbook 1: Local LLM Provider Outage / Execution Timeout
* **Symptom:** Local LLM takes > 2500 ms, model weights are missing/corrupted, or inference throws an exception.
* **Automatic Mitigation:**
  1. Circuit breaker transitions to `OPEN`, logging `llm_outage_fallback`.
  2. Synthesizer gracefully aborts rewrite and returns pure Speed-1 extractive claims.
  3. WebSocket emits `llm_fallback` event with reason and preserves all byte-identical citations.
  4. User interface displays the amber fallback status badge.
* **Action:**
  Verify model weights exist at `models/qwen2.5-1.5b-instruct-q4_k_m.gguf` with matching SHA-256 checksum. If corrupted, re-download or set `KAIROS_MODELS__LOCAL_LLM__ENABLED=false` to run permanently on Speed-1 extractive mode.

### Runbook 2: Index Load Failure & Readiness Probe Degraded
* **Symptom:** `/v1/ready` returns HTTP 503 Service Unavailable; logs show `Failed to load/warmup index`.
* **Automatic Mitigation:**
  Liveness probe (`/v1/health`) remains HTTP 200, alerting orchestrators that container is healthy but unready to serve traffic.
* **Action:**
  1. Inspect container logs: `docker compose logs kairos | grep -E "Index load|manifest"`.
  2. If chunks or manifest are missing, trigger automated rebuild:
     ```bash
     docker compose exec kairos python -m kairos.cli index --corpus data/corpus
     ```
  3. Re-verify readiness: `curl -f http://localhost:8000/v1/ready`.

### Runbook 3: Corpus Tampering or Manifest Hash Mismatch
* **Symptom:** Container startup fails with `Corpus manifest mismatch! Documents have been modified or corrupted`.
* **Automatic Mitigation:**
  Server refuses to serve traffic from an unverified corpus (Security Rule 8).
* **Action:**
  1. Confirm whether files in `data/corpus/` were legitimately modified or tampered with.
  2. If modified intentionally, recompute the cryptographic manifest:
     ```bash
     python -m kairos.ingest.manifest --corpus data/corpus --update
     python -m kairos.cli index --corpus data/corpus
     ```
  3. Restart the container: `docker compose restart kairos`.

### Runbook 4: Client Rate Limit Flooding / DoS Attack
* **Symptom:** Inbound spikes cause HTTP 429 Too Many Requests or WebSocket closure with WS 1008 Policy Violation (`RATE_LIMIT_EXCEEDED`).
* **Automatic Mitigation:**
  Sliding-window rate limiter drops excessive frames without spawning pipeline threads. Memory and CPU stay strictly bounded.
* **Action:**
  1. Check Jaeger traces for originating client IP or session IDs under attack.
  2. Adjust limits if legitimate traffic requires higher throughput in `config/default.yaml`:
     ```yaml
     security:
       rate_limit:
         http_per_min: 240
         ws_messages_per_min: 1200
     ```

### Runbook 5: Token Expiration or HMAC Validation Failure
* **Symptom:** Client receives HTTP 403 Forbidden or WebSocket rejects connection with code 1008.
* **Automatic Mitigation:**
  Sessions older than `session.ttl_s` (1800s) are automatically evicted by background garbage collection.
* **Action:**
  Client must initiate a new session via `POST /v1/sessions` and reconnect using the newly issued session ID and cryptographically signed bearer token.

---

## 5. Measured Load-Test & Concurrency Benchmarks

The benchmark was executed using the automated load-test harness (`loadtest/run_bench.py`) on laptop-class hardware with container limits of **2.0 CPUs and 4096 MB RAM** (SPEC §15.4):

### Performance Under Concurrent Streaming Sessions

| Concurrency Scenario | Successful Turns | Error Rate | p50 Turn Latency | p95 Turn Latency | p50 TTFT | p95 TTFT | Peak RAM | Ready-at-End |
|---|---|---|---|---|---|---|---|---|
| **1 Session (Single-user baseline)** | 2 / 2 (100%) | **0.0%** | **1,533.99 ms** | 2,486.66 ms | **386.84 ms** | **461.69 ms** | **584.5 MB** | **0.75** |
| **10 Sessions (Target capacity)** | 20 / 20 (100%) | **0.0%** | **8,489.03 ms** | 12,734.18 ms | **6,200.53 ms** | **6,715.43 ms** | **1,539.2 MB** | **0.75** |
| **25 Sessions (Stress / Load-shedding)** | 27 / 50 (54%) | 46.0% | 19,630.55 ms | 28,363.22 ms | 17,824.42 ms | 22,187.54 ms | **3,300.7 MB** | 0.68 |

*Note: Under 25 concurrent sessions, the server enforces backpressure and load-shedding while memory remains strictly below the 4096 MB hardware ceiling.*

### Telemetry Latency Contribution by Pipeline Stage
*(Measured over 50 iterations)*

* **Stage 1 — Controller Feature Extraction & Decision:** 51.05 ms
* **Stage 2 — Multi-Intent Decomposition:** 0.02 ms
* **Stage 3 — Hybrid Dense + Sparse Retrieval:** 46.22 ms *(Top latency contributor: FastEmbed dense vector inference + BM25s scoring)*
* **Stage 4 — Reciprocal Rank Fusion (RRF):** 2.31 ms
* **Stage 5 — Speed-1 Extractive Synthesis:** 0.40 ms
* **Deterministic Grounding Gate:** 0.03 ms

### Speed-2 Local LLM Budget Outcome
* **Configured Budget Deadline:** 1,500 ms
* **Measured p95 Rewrite Latency:** 820.0 ms
* **Budget Respected:** **True**
* **Offline Fallback Operational:** **True**

---

## 6. Secrets & Key Rotation Procedures

### Rotating the Session Token HMAC Secret
The session token secret signs ephemeral bearer tokens. To rotate:
1. Generate a secure random 256-bit hexadecimal string:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Update `.env` or set environment variable:
   ```bash
   export KAIROS_TOKEN_SECRET="<new_hex_secret>"
   ```
3. Restart service. Existing client tokens will cleanly invalidate, requiring clients to request a new session via `POST /v1/sessions`.

### Rotating External Hosted LLM API Keys (Optional)
If using an optional cloud LLM provider (`gemini` or `openai_compatible`):
1. Update `.env`:
   ```bash
   GEMINI_API_KEY="<new_key>"
   OPENAI_API_KEY="<new_key>"
   ```
2. Hot-reload or restart the service:
   ```bash
   docker compose restart kairos
   ```
3. Verify liveness and fallback behavior by running `make test`.
