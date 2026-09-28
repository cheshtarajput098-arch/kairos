# DECISIONS.md — defaults the agent uses instead of asking

The team cannot ask the organisers, and isn't available mid-run. These defaults replace every open question. The agent uses them without asking (autopilot rule 1) and logs any new decision at the bottom. The team can change a default at any time by editing this table; the next `/build-next` follows the new value.

## Defaults

| Topic | Default | Why |
|---|---|---|
| Corpus | Use the placeholder corpus in `data/corpus/` until the real supplied corpus appears there; detect the swap automatically (autopilot rule 7). | Lets the whole build proceed now; the design is corpus-agnostic (SPEC §9.6a). |
| Held-out replay format | Unknown, so support every format in SPEC §9.6a through the tolerant adapter and the `kairos replay` CLI, and test at least four variants. | Judges run a private replay; being format-tolerant is the only safe option. |
| Judges' corpus | Assume they may use a different copy of the corpus; `kairos index --corpus` must work on any folder. | Same reason. |
| Evaluation machine | Assume a laptop-class CPU: **4 cores, 8 GB RAM, no GPU**, internet available only while the Docker image builds. | Conservative; if it works here, it works on anything bigger. |
| Local LLM size | Choose the best benchmarked model whose quantised file and runtime fit in **≤ 4 GB RAM**; if none meets the Speed-2 latency budget, run Speed 2 after utterance end, or turn it off with the reason logged. | Keeps the 8 GB assumption safe alongside the rest of the stack. |
| Hosted LLM APIs | **Not used by default.** The system runs fully offline; hosted providers stay optional through `.env`. | No keys are needed on a judge's machine, which protects G1. |
| Judging weights | Plan against Working prototype 30%, Technical depth 25%, Innovation 20%, Relevance 15%, Presentation 10% (reported by another 3rd-edition team; not confirmed). | Best available information. |
| Repository size | Keep the git repo under 100 MB: no model weights, indexes or large binaries in git; download models at image build. | GitHub limits and fast clones. |
| Container image size | Aim for ≤ 6 GB including the local model; report the actual size in OPERATIONS.md. | Reasonable for a clean-machine build. |
| Licence | **MIT**, copyright the two team members: Cheshta Rajput and Chiranjeevi U Jadhav. | Simple and permissive; the team can change it before release. |
| Team and project names | Team Coding Agent RIT, M S Ramaiah Institute of Technology; project Kairos. | From the submission deck. |
| Visual direction | "Calm Precision" (SPEC §14.3a). | Recommended default; the team may override. |
| Controller model arm | Train logistic regression first; add the MiniLM classifier only if Tier 2 finishes with time to spare, and update the deck to match. | Cut-list order (SPEC §15.6). |
| Rerank / NLI | Off by default; add only if Tier 4 finishes early. | Cut-list order. |
| Languages | English UI and answers; the code-mixed slice is optional (cut-list item 6). | Scope. |
| Python / Node | Python 3.11; the current Node.js LTS for the web build only (not at runtime). | Stack in SPEC §1. |
| Branch | `main`. The agent commits and tags locally; the team pushes. | Autopilot rule 5. |
| Unreviewed data | Everything the agent drafts is marked `review_status: unreviewed` / `source: llm_drafted` until a human reviews it. Reports say so. | Honesty rules. |

## Decisions log (the agent appends here)

| Step | Question | Decision | Reason |
|---|---|---|---|
| Step 01 | Primary chunking strategy for placeholder corpus | Heading 2 (`## `) primary split, 350-word token window overflow split with 15% overlap | Matches document structure while preserving stable `[Doc_ID §Section]` citation markers |
| Step 03 | Dense and Sparse indexing engines | FastEmbed (`BAAI/bge-small-en-v1.5`) for dense search and `bm25s` for sparse search | Pure CPU-native execution, fast local inference, zero external servers or services required |
| Step 04 | Controller rule thresholds & presentation cue lexicon | Config-driven thresholds (drift 0.15, saturation window 2 chunks) + generic reformatting cue lexicon | High recall on presentation intents with zero hardcoded scenario terms or out-of-corpus leaks |
