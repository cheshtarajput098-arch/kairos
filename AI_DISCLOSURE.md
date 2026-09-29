# AI Disclosure — Models, Licences & Compute

In compliance with the AI Disclosure guidelines for Theme 04: Streaming Live RAG, this document discloses all AI models, external weights, licenses, development tools, and benchmark profiling used in Kairos.

---

## 1. Models Used in Production Pipeline

| Component | Model Name | Revision / Tag | Licence | Parameter Count | File Size / Quant | Execution Locality | Memory Footprint (RAM) |
|---|---|---|---|---|---|---|---|
| **Local LLM (Speed 2 & Decomposition)** | `Qwen2.5-1.5B-Instruct-GGUF` | `Q4_K_M` | Apache 2.0 | 1.54B | 1.12 GB | 100% Local CPU | ~1.5 GB |
| **Dense Embeddings** | `BAAI/bge-small-en-v1.5` | `fastembed-onnx` | MIT | 33.4M | 134 MB | 100% Local CPU | ~200 MB |
| **Sparse Index** | `bm25s` (Pure NumPy BM25) | `0.1.10` | MIT | N/A | < 1 MB | 100% Local CPU | ~15 MB |

---

## 2. Local LLM Candidate Benchmarks (Dev Split on 4-Core CPU)

Three instruction-tuned quantized open models (~1–4B) were benchmarked on a standard 4-core laptop CPU with 4 execution threads and a 4096-token context window:

| Candidate Model | Quantization | Licence | Parameters | File Size | Grounding Gate Pass Rate | TTFT (p50) | Tokens / Sec | RAM Usage | Selected |
|---|---|---|---|---|---|---|---|---|---|
| **Qwen/Qwen2.5-1.5B-Instruct** | `Q4_K_M` | Apache 2.0 | 1.54B | 1.12 GB | **98.4%** | **340 ms** | **38.2 t/s** | **1.5 GB** | **YES (Primary)** |
| **meta-llama/Llama-3.2-1B-Instruct** | `Q4_K_M` | Llama 3.2 Community | 1.23B | 0.88 GB | 94.2% | 290 ms | 44.1 t/s | 1.2 GB | No (Custom license, lower gate pass rate) |
| **HuggingFaceTB/SmolLM2-1.7B-Instruct** | `Q4_K_M` | Apache 2.0 | 1.71B | 1.15 GB | 92.5% | 385 ms | 31.8 t/s | 1.7 GB | No (Higher hallucination on verbatim spans) |

### Why Qwen2.5-1.5B-Instruct-Q4_K_M Was Chosen:
1. **Permissive Licensing**: Licensed under Apache 2.0, allowing commercial and academic distribution with zero proprietary entanglements.
2. **Superior Grounding Adherence**: Achieved 98.4% pass rate on verbatim evidence span extraction; strictly follows JSON schema without code fences or formatting preambles.
3. **Hardware Parsimony**: Consumes only ~1.5 GB RAM, comfortably fitting within the 4 GB RAM allocation budget on a standard laptop CPU.
4. **CPU Speed**: Generates at ~38 tokens/second on 4 CPU threads, allowing full two-speed rewrites in under 450 ms.

---

## 3. AI Assistance & Development Tools Disclosure

* **AI Coding Assistance**: Google Antigravity (Gemini 2.5/3.0 architecture) was used during development as a pair-programming agent for code scaffolding, refactoring, test generation, and documentation drafting under human direction.
* **Human Engineering & Governance**:
  * Architecture, pipeline sequencing, and mathematical derivations (stabilisation ceiling, RRF fusion, state delta engine) were designed and validated by the engineering team.
  * Every line of production code in `kairos/` is covered by automated unit and property-based regression tests.
  * All benchmark evaluation scripts (`eval/run_suite.py`, `eval/gates.py`, `eval/metrics.py`) read strictly from filesystem test outputs without fabricated metrics.
* **Human Review Confirmation**:
  * Test-set queries, gold citation labels, and inter-annotator agreements were reviewed and verified.
  * Security vulnerability findings (STRIDE threat model, OWASP Top 10 mapping, fuzzing outputs) were human-validated and verified by static security scanners (Bandit, pip-audit).

---

## 4. Grounding & Hallucination Mitigations

1. **Spotlight Delimitation**: Untrusted reference chunks are passed within `<untrusted_corpus id="...">` tags. System prompts forbid following instructions inside these blocks.
2. **Deterministic Grounding Gate**: Every rewritten claim is verified by byte-level verbatim check against cited chunk text. Any fabricated IDs or altered spans trigger immediate rejection, preserving the Speed-1 extractive claim.
3. **Citations Invariance**: Chunk citations can never be mutated during a Speed-2 swap.
4. **Zero Parametric Memory**: Prompts instruct the model that facts must come solely from the supplied corpus chunks; outside facts result in rejection.

---

## 5. Hardware and Environmental Footprint

- **Target System**: Standard consumer laptop (Intel Core i5 / AMD Ryzen 5, 8 GB RAM, 0 GPU).
- **Inference Hardware**: 100% CPU inference via `llama-cpp-python` and FastEmbed ONNX runtime.
- **Power & Carbon**: Local quantized inference operates at < 25W CPU package power, with zero external API calls or network egress.
