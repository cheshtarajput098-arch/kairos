# data/corpus — the documents Kairos answers from

## What is here now: a PLACEHOLDER corpus
The eight `Doc_*.md` files describe **Veloria Systems, a fictional company** invented for development. They exist only so the team can build, test and demo before the real corpus arrives. Their facts are written so the three example scenarios in the theme guide behave exactly as the guide describes (including the catering gap for Venue A, which must produce an uncertainty flag).

## Replacing it with the real (supplied) corpus
The theme guide says the corpus is **supplied by the organisers**. When you receive it:
1. Delete the placeholder `Doc_*.md` files (keep this README).
2. Copy the supplied files here, unchanged (any of .md, .txt, .html, .pdf, .docx, .json).
3. Rebuild the index: `docker compose run --rm kairos kairos index --corpus data/corpus`.
4. Re-draft `data/replay/demo/` and `data/replay/dev/` against the real documents (Prompt 3), then re-run `make eval`.

## Rules
- Treat this folder as **read-only** data. Never edit the supplied files.
- Doc IDs come from file names or IDs embedded in the documents (for example `Doc_12`). Keep them unchanged, because citations like `[Doc_12 §2]` depend on them.
- Never tune thresholds to this placeholder corpus. It is tiny and friendly; the real one will not be.
- `make index` writes a SHA-256 manifest of every file here; the API refuses to serve if the files change afterwards.
