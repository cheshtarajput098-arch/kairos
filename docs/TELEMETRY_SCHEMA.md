# Telemetry Schema & Event Reference — Kairos

This document defines the complete telemetry specification for Kairos, covering OpenTelemetry trace spans, streaming WebSocket events, structured log formats, and sample event records.

---

## 1. Streaming WebSocket Events (`/v1/stream`)

During live audio transcript streaming, the server pushes JSON-serialized event envelopes over the WebSocket connection.

### Event Catalog

| Event Name | Emitter Stage | Trigger Condition | Description |
|---|---|---|---|
| `controller_decision` | Stage 1 (Controller) | Every inbound transcript chunk | Emits controller decision (`WAIT`, `RETRIEVE`, `SUPPRESS`) and reasoning. |
| `subqueries_updated` | Stage 2 (Decomposer) | Controller decision == `RETRIEVE` | Emits active decomposed retrieval legs with first-dispatch timestamps. |
| `draft_verified` | Stage 5 (Drafting Mgr) | Leg retrieval completes mid-speech | Emits verified provisional claim before utterance finishes. |
| `turn_completed` | Session / Drafting | Last chunk received (`is_final=true`) | Emits final committed extractive answer, version, citations, claims, and metrics. |
| `speed2_completed` | Stage 5 (Rewrite) | Grounded rewrite passes GroundingGate | Emits fluent rewritten answer (v2) with byte-identical citations. |
| `llm_fallback` | Stage 5 (Rewrite) | Local LLM fails or circuit breaker open | Notifies client that extractive grounded answer was retained. |

---

## 2. Event Payload Schemas & Field Definitions

### 1. `controller_decision`
Emitted for every transcript chunk arriving over the stream.

```json
{
  "event": "controller_decision",
  "t": 1.20,
  "decision": "RETRIEVE",
  "reason": "sufficient_entities_and_low_drift"
}
```

* **`event`** (string): Strictly `"controller_decision"`.
* **`t`** (float): Current virtual or real-time timestamp in seconds.
* **`decision`** (string): One of `"WAIT"`, `"RETRIEVE"`, or `"SUPPRESS"`.
* **`reason`** (string): Causal explanation (e.g. `"syntactic_openness_wait"`, `"semantic_drift_detected"`, `"presentation_reformat"`).

---

### 2. `subqueries_updated`
Emitted when the multi-intent decomposer isolates or updates sub-queries for parallel dispatch.

```json
{
  "event": "subqueries_updated",
  "t": 1.40,
  "legs": [
    {
      "leg_id": "L1",
      "text": "venue capacity in Pune",
      "first_dispatch_s": 1.40
    },
    {
      "leg_id": "L2",
      "text": "AV rental costs in Pune",
      "first_dispatch_s": 1.40
    }
  ]
}
```

* **`legs`** (array): Array of active retrieval legs:
  * `leg_id` (string): Stable leg identifier (`L1`, `L2`, etc.).
  * `text` (string): Normalized clause query with inherited context.
  * `first_dispatch_s` (float): Timestamp when leg search was first triggered.

---

### 3. `draft_verified`
Emitted mid-utterance as soon as a retrieval leg returns candidates that pass deterministic GroundingGate validation.

```json
{
  "event": "draft_verified",
  "t": 1.75,
  "leg_id": "L1",
  "claim": {
    "claim_id": "claim_L1_v1",
    "leg_id": "L1",
    "text": "The Grand Ballroom in Pune accommodates up to 250 attendees. [Doc_12 §2]",
    "citations": ["Doc_12 §2"],
    "evidence_span": "accommodates up to 250 attendees",
    "status": "verified",
    "version": 1
  }
}
```

* **`claim.status`** (string): `"verified"` (passed gate) or `"uncertain"` (corpus gap).
* **`claim.evidence_span`** (string): Verbatim sentence extract ($\le 30$ words).
* **`claim.citations`** (array of strings): Cited chunk identifiers matching pattern `[Doc_XX §YY]`.

---

### 4. `turn_completed`
Emitted immediately upon processing the final utterance chunk (`is_final=true`).

```json
{
  "event": "turn_completed",
  "turn_type": "compound",
  "answer": "The Grand Ballroom in Pune accommodates up to 250 attendees. [Doc_12 §2] Standard AV rental packages start at $350 per day. [Doc_14 §1]",
  "version": 1,
  "citations": ["Doc_12 §2", "Doc_14 §1"],
  "claims": [
    {
      "claim_id": "claim_L1_v1",
      "leg_id": "L1",
      "text": "The Grand Ballroom in Pune accommodates up to 250 attendees. [Doc_12 §2]",
      "citations": ["Doc_12 §2"],
      "evidence_span": "accommodates up to 250 attendees",
      "status": "verified",
      "version": 1
    }
  ],
  "metrics": {
    "utterance_end_s": 2.20,
    "first_retrieval_s": 1.20,
    "lead_time_s": 1.00,
    "ttft_s": 0.00,
    "ready_at_end": 1.0,
    "retrievals": 2
  }
}
```

* **`turn_type`** (string): `"single"`, `"compound"`, `"late_constraint"`, `"presentation_only"`, or `"out_of_corpus"`.
* **`metrics.lead_time_s`** (float): Seconds between first retrieval trigger and utterance end ($> 0$ indicates early retrieval).
* **`metrics.ready_at_end`** (float): `1.0` if answer was drafted prior to utterance end, else `0.0`.

---

### 5. `speed2_completed`
Emitted asynchronously when the local LLM completes a grounded fluent rewrite.

```json
{
  "event": "speed2_completed",
  "answer": "Workshop venues in Pune seat up to 250 people in the Grand Ballroom [Doc_12 §2], with standard audiovisual equipment available from $350 daily [Doc_14 §1].",
  "version": 2,
  "citations": ["Doc_12 §2", "Doc_14 §1"],
  "metrics": {
    "rewrite_pass_rate": 1.0,
    "latency_ms": 425.5,
    "rewrites_attempted": 2,
    "rewrites_accepted": 2,
    "rewrites_rejected": 0,
    "llm_outage": false
  }
}
```

---

## 3. OpenTelemetry Spans & Attributes

Kairos emits distributed traces over OTLP (`http://jaeger:4318/v1/traces`):

| Span Name | Parent Span | Mandatory Attributes |
|---|---|---|
| `kairos.stream.turn` | Root | `session_id`, `turn_id`, `turn_type` |
| `kairos.controller.evaluate` | `kairos.stream.turn` | `chunk_t`, `decision`, `reason`, `drift` |
| `kairos.decompose.split` | `kairos.stream.turn` | `clause_count`, `active_legs` |
| `kairos.retrieve.hybrid` | `kairos.stream.turn` | `leg_id`, `dense_hits`, `sparse_hits`, `latency_ms` |
| `kairos.synth.extractive` | `kairos.stream.turn` | `leg_id`, `candidate_count`, `top_score` |
| `kairos.synth.rewrite` | `kairos.stream.turn` | `model_name`, `tokens_generated`, `pass_rate` |
| `kairos.grounding.gate` | `kairos.synth.*` | `claim_id`, `citation_verified`, `span_match_ratio` |
| `kairos.session.delta` | `kairos.stream.turn` | `version_before`, `version_after`, `claims_patched` |

---

## 4. Privacy & Masking Guarantees

In accordance with Security Rule 6:
* All PII patterns (emails, credit card sequences, international phone numbers) are masked with `[REDACTED]` prior to logging.
* Raw audio transcript logging is disabled by default; only message lengths and SHA-256 hashes are recorded unless `KAIROS_TELEMETRY__LOG_TEXT=true` is explicitly enabled.
