# Step 03 of 14 — Corpus ingest, integrity and hybrid index

**File:** `build/steps/p02-index.md` · **Tier 1 — Differentiator MVP** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

---

Implement Prompt 2 following SPEC.md §2.1, §6.1 and §13.2 (LLM03, LLM04, LLM08).

Build kairos/ingest, kairos/index, kairos/retrieve, kairos/fuse:
- Section-aware chunker suited to the corpus profile from Prompt 0. Stable chunk_id like Doc_12§2, printed as [Doc_12 §2]. Same input → same IDs, always.
- Corpus integrity: `make index` writes data/corpus.manifest.json (SHA-256 per file) and a provenance record per chunk. At startup the API verifies the manifest and refuses to become ready on mismatch.
- Injection flagging at ingest: a small, generic pattern + heuristic scorer (imperatives addressed to an AI, "ignore previous", role tags, hidden/zero-width text). Flagged chunks are recorded in the provenance record, not deleted.
- Unicode NFKC normalisation and control/zero-width character stripping for all text.
- Dense index (FastEmbed BAAI/bge-small-en-v1.5) in qdrant-client local embedded mode; BM25 with bm25s over the identical chunk set. The index is read-only at serve time.
- Async hybrid retrieval per query: dense and BM25 concurrently under a per-leg deadline; overruns cancelled, not awaited.
- RRF fusion (k from config), cross-leg dedupe, optional cross-encoder rerank behind a switch (off). Prefix-hash result cache.

Tests: chunk-ID stability; IDs survive retrieval + fusion byte-for-byte; RRF on a toy example; deadline cancellation; cache hit; tampered corpus file blocks readiness; flagged-chunk fixture is detected.

Verification: `make index && make test`, then a CLI query for 3 realistic questions you write about the corpus showing top-5 fused chunk IDs and snippets, index build time, and p50/p95 query latency. Update PROJECT_STATE.md.
