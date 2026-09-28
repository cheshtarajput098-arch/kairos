"""Section-aware corpus chunker producing stable [Doc_ID §Section] markers (SPEC §2.1)."""

from __future__ import annotations

import re
from pathlib import Path

from kairos.ingest.normalizer import normalize_text
from kairos.schemas import CorpusChunk

SECTION_HEADER_RE = re.compile(r"^##\s+(\d+)\.\s*(.*)$", re.MULTILINE)
DOC_ID_RE = re.compile(r"^(Doc_\d+)", re.IGNORECASE)


def parse_doc_id(file_path: Path) -> str:
    """Extract standard Doc_ID (e.g. Doc_12) from filename."""
    m = DOC_ID_RE.match(file_path.stem)
    if m:
        return m.group(1)
    return file_path.stem


def chunk_document(file_path: Path, text: str | None = None) -> list[CorpusChunk]:
    """Parse a document into section-aware chunks with stable Doc_ID§Section IDs."""
    if text is None:
        raw_text = file_path.read_text(encoding="utf-8")
    else:
        raw_text = text

    clean_text = normalize_text(raw_text)
    doc_id = parse_doc_id(file_path)

    # Find main document title from first # Header if available
    title_match = re.search(r"^#\s+(.+)$", clean_text, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else file_path.stem

    # Find all ## section headers
    matches = list(SECTION_HEADER_RE.finditer(clean_text))
    chunks: list[CorpusChunk] = []

    if not matches:
        # Fallback for documents with no ## sections: single chunk section 1
        chunk = CorpusChunk(
            chunk_id=f"{doc_id}§1",
            doc_id=doc_id,
            section="1",
            title=doc_title,
            text=clean_text.strip(),
            char_start=0,
            char_end=len(clean_text),
        )
        return [chunk]

    for i, match in enumerate(matches):
        sec_num = match.group(1)
        sec_title = match.group(2).strip() or f"Section {sec_num}"
        start_pos = match.start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(clean_text)

        section_body = clean_text[start_pos:end_pos].strip()

        chunk = CorpusChunk(
            chunk_id=f"{doc_id}§{sec_num}",
            doc_id=doc_id,
            section=str(sec_num),
            title=f"{doc_title} - {sec_title}",
            text=section_body,
            char_start=start_pos,
            char_end=end_pos,
        )
        chunks.append(chunk)

    return chunks


def chunk_corpus(corpus_dir: Path) -> list[CorpusChunk]:
    """Chunk all files in the corpus directory deterministically sorted by filename."""
    all_chunks: list[CorpusChunk] = []
    files = sorted(corpus_dir.glob("Doc_*.md"))
    if not files:
        files = sorted(
            [
                f
                for f in corpus_dir.iterdir()
                if f.is_file() and not f.name.startswith(".") and f.name != "README.md"
            ]
        )

    for file_path in files:
        all_chunks.extend(chunk_document(file_path))

    return all_chunks
