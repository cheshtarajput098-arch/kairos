# Step 09 of 14 — Two-speed answers with a local LLM

**File:** `build/steps/p07b-generative.md` · **Tier 3 — Generative polish + UI** · Run it with `/build-next` (see `build/SEQUENCE.md`).

Autopilot applies (`.agents/rules/40-autopilot.md`): wherever the text below says "ask me", "wait for my approval" or "I will …", follow the autopilot rule instead: decide using `docs/DECISIONS.md`, record the decision, and keep going. Tasks only a human can do go into `docs/HUMAN_TASKS.md`; results that depend on them stay `TBD`.

---

Implement SPEC.md §6.2 Speed 2 and generative-mode decomposition (§5), keeping every guarantee.

1. Model selection: benchmark 2–3 current small instruction-tuned open models (~1–4B, quantised GGUF, licence allowing this use) with llama-cpp-python on CPU. On the dev split, measure grounding-gate pass rate of rewrites, time to first token, tokens/s and RAM. Pick one, pin its file by SHA-256 in config, download it at image build, and record the benchmark table plus licence in AI_DISCLOSURE.md and docs/OPERATIONS.md. Ask me before choosing if the best option exceeds 4 GB RAM.
2. kairos/llm/local.py implementing generate_json with a hard token cap, deadline, temperature 0 and a circuit breaker; falls back to Speed 1 on any failure.
3. Speed-2 rewrite: input is only the verified Speed-1 claims and their spotlighted chunks; output is Claim JSON with verbatim evidence_span. Each rewritten claim replaces its Speed-1 claim only if it passes the grounding gate; otherwise log rewrite_rejected and keep Speed 1. Citations never change during a swap.
4. Generative decomposition as a second pass over the rule-based legs, under a deadline; on a miss the rule-based legs stand.
5. Latency policy: if measured Speed-2 latency would delay the committed answer beyond the configured budget, run it only after utterance end, or disable it with the reason logged and shown in Inspector.
6. Ablations D (Speed 1 vs two-speed) and E (drafting on vs off) in eval/ablations.py; a blind fluency rating sheet (20 sampled answers, 1–5, two raters) in eval/fluency/ for me and my teammate to fill in, with agreement computed automatically.
7. UI: cross-fade Speed-2 text over Speed-1 without layout shift (SPEC.md §14.3a item 5).

Tests: a rewrite containing a fabricated ID or a paraphrased (non-verbatim) span is rejected and Speed 1 stays; model missing → system still passes `make eval`; circuit breaker opens after repeated failures.

Verification: `make test`, `make eval` with and without the model file present, Ablation D and E tables. Update COMPLIANCE.md and PROJECT_STATE.md, then continue; v0.8-polish is tagged at the end of build/steps/p09b-ui-build.md.
