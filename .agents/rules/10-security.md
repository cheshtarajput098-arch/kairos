---
trigger: always_on
---

# Kairos — security rules

Part of the project rules (see AGENTS.md). Full threat model: SPEC.md §13.

## Security rules (non-negotiable; full threat model in SPEC.md §13)

1. **Untrusted by default.** User transcripts, corpus chunks and LLM output are all untrusted data. None of them may ever be executed, interpreted as instructions, or rendered as HTML.
2. **Spotlight retrieved content.** Corpus text reaches an LLM only inside delimited, datamarked `<untrusted_corpus>` blocks, and the system prompt states that text inside them is reference data, never instructions. Chunks carrying instruction-like text are flagged at ingest and at retrieval time and logged.
3. **Zero agency.** The LLM has no tools, no function calling, no network, no file access. It only returns schema-validated JSON. Anything that fails validation is discarded.
4. **Server-issued sessions.** Session IDs are random 128-bit values issued by the server. A client can only read or modify its own session. There are no enumerable IDs and no cross-session reads.
5. **Bounded everything.** Every input and every resource has a limit: message size, chunks per turn, turn length, sessions per client, requests per minute, LLM tokens per turn, deadlines per stage. Limits live in config and are enforced server-side.
6. **No secrets or PII in logs.** API keys are never logged. Telemetry redacts emails, phone numbers and card-like numbers by default. Raw transcript logging is off by default (store hashes + lengths); a `telemetry.log_text=true` flag exists only for local debugging.
7. **Hardened container.** Non-root user, read-only root filesystem, `no-new-privileges`, all Linux capabilities dropped, only needed ports exposed, Jaeger bound to localhost.
8. **Supply chain.** Dependencies are pinned with hashes. Model files are pinned by revision and verified by SHA-256 at startup. The corpus has a SHA-256 manifest verified at startup; any mismatch refuses to serve.
9. **Security is tested, not claimed.** Every rule above has an automated test in `tests/security/`. The red-team replay set reports attack success rate in `docs/EVAL_REPORT.md`.
10. **Security adds no pipeline stages.** Controls sit at the edges (API middleware, ingest, context construction, output validation), so the five-stage design stays parsimonious. Their measured latency is reported.
