"""Unified Hybrid Index Store and Provenance Manager (SPEC §6.1, §13.2)."""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from kairos.index.dense import DenseIndex
from kairos.index.sparse import SparseIndex
from kairos.ingest.chunker import chunk_corpus
from kairos.ingest.manifest import generate_corpus_manifest
from kairos.ingest.scanner import scan_for_injection
from kairos.schemas import CorpusChunk


def generate_corpus_suggestions(chunks: list[CorpusChunk]) -> list[str]:
    """Generate 3-5 suggested questions dynamically from corpus headings at index time (SPEC §14.3)."""
    seen_docs: set[str] = set()
    suggestions: list[str] = []

    for c in chunks:
        if c.doc_id in seen_docs:
            continue
        seen_docs.add(c.doc_id)
        parts = c.title.split(" - ")
        doc_name = parts[0].strip()
        sec_name = parts[1].strip() if len(parts) > 1 else ""

        if sec_name and sec_name.lower() not in doc_name.lower():
            suggestions.append(f"What does {doc_name} state regarding {sec_name.lower()}?")
        else:
            suggestions.append(f"What are the main provisions and guidelines in {doc_name}?")

        if len(suggestions) >= 5:
            break

    return suggestions[:5]


class IndexStore:
    def __init__(self, index_dir: Path = Path("index"), corpus_dir: Path = Path("data/corpus")):
        self.index_dir = index_dir
        self.corpus_dir = corpus_dir
        self.sparse_index = SparseIndex(index_dir / "bm25")
        self.dense_index = DenseIndex(index_dir / "dense")
        self.chunks_map: dict[str, CorpusChunk] = {}
        self.provenance: dict[str, dict[str, object]] = {}

    def build(self) -> None:
        """Run complete index build: manifest, chunking, injection scan, sparse and dense indices."""
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # 1. Write corpus integrity manifest
        manifest_path = self.index_dir / "corpus.manifest.json"
        generate_corpus_manifest(self.corpus_dir, manifest_path)
        try:
            data_manifest = Path("data/corpus.manifest.json")
            if data_manifest.parent.exists():
                generate_corpus_manifest(self.corpus_dir, data_manifest)
        except OSError:
            pass

        # 2. Ingest & chunk corpus
        chunks = chunk_corpus(self.corpus_dir)
        self.chunks_map = {c.chunk_id: c for c in chunks}

        # 3. Provenance record & injection flagging
        self.provenance = {}
        for c in chunks:
            is_flagged, score, reason = scan_for_injection(c.text)
            self.provenance[c.chunk_id] = {
                "doc_id": c.doc_id,
                "section": c.section,
                "flagged": is_flagged,
                "flag_score": score,
                "flag_reason": reason,
            }

        with open(self.index_dir / "provenance.json", "w", encoding="utf-8") as f:
            json.dump(self.provenance, f, indent=2)

        with open(self.index_dir / "chunks.json", "w", encoding="utf-8") as f:
            json.dump({cid: c.model_dump() for cid, c in self.chunks_map.items()}, f, indent=2)

        # Generate suggested questions from corpus headings at index time (SPEC §14.3)
        suggestions = generate_corpus_suggestions(chunks)
        with open(self.index_dir / "suggestions.json", "w", encoding="utf-8") as f:
            json.dump(suggestions, f, indent=2)

        # 4. Build sparse & dense indices
        self.sparse_index.build(chunks)
        self.dense_index.build(chunks)

    def load(self) -> None:
        """Load indices and chunks from disk."""
        chunks_file = self.index_dir / "chunks.json"
        prov_file = self.index_dir / "provenance.json"

        if not chunks_file.exists():
            raise FileNotFoundError(f"Chunks file missing in {self.index_dir}. Run 'make index' first.")

        with open(chunks_file, encoding="utf-8") as f:
            data = json.load(f)
            self.chunks_map = {cid: CorpusChunk.model_validate(c) for cid, c in data.items()}

        if prov_file.exists():
            with open(prov_file, encoding="utf-8") as f:
                self.provenance = json.load(f)

        self.sparse_index.load()
        self.dense_index.load()

    def warmup(self) -> None:
        """Warm up dense and sparse indexes to eliminate cold-start ONNX initialization latency."""
        try:
            self.dense_index.search("warmup query", top_k=1)
            self.sparse_index.search("warmup query", top_k=1)
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Index warmup skipped: {e}")

    def get_chunk(self, chunk_id: str) -> CorpusChunk | None:
        return self.chunks_map.get(chunk_id)
