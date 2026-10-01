"""BM25 Sparse Index using bm25s (SPEC §6.1)."""
from __future__ import annotations

import json
from pathlib import Path

import bm25s

from kairos.grounding.relevance import clean_bm25_query
from kairos.schemas import CorpusChunk


class SparseIndex:
    def __init__(self, index_dir: Path = Path("index/bm25")):
        self.index_dir = index_dir
        self.retriever: bm25s.BM25 | None = None
        self.chunk_ids: list[str] = []

    def build(self, chunks: list[CorpusChunk]) -> None:
        """Build BM25 index over chunks and save to disk."""
        self.chunk_ids = [c.chunk_id for c in chunks]
        corpus_texts = [f"{c.title}\n{c.text}" for c in chunks]

        corpus_tokens = bm25s.tokenize(corpus_texts, stopwords="en")
        retriever = bm25s.BM25()
        retriever.index(corpus_tokens)
        self.retriever = retriever

        self.save()

    def save(self) -> None:
        """Save BM25 index and chunk mapping to index_dir."""
        if self.retriever is None:
            raise ValueError("Cannot save uninitialized BM25 index")

        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.retriever.save(str(self.index_dir))

        mapping_file = self.index_dir / "chunk_ids.json"
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(self.chunk_ids, f, indent=2)

    def load(self) -> None:
        """Load BM25 index and chunk mapping from index_dir."""
        if not (self.index_dir / "chunk_ids.json").exists():
            raise FileNotFoundError(f"Sparse index not found at {self.index_dir}")

        self.retriever = bm25s.BM25.load(str(self.index_dir), load_corpus=False)
        mapping_file = self.index_dir / "chunk_ids.json"
        with open(mapping_file, encoding="utf-8") as f:
            self.chunk_ids = json.load(f)

    def search(self, query: str, top_k: int = 20) -> list[tuple[str, float]]:
        """Search query against BM25 index with stopword/filler filtering. Returns list of (chunk_id, score)."""
        if self.retriever is None:
            self.load()
        if self.retriever is None:
            raise RuntimeError("BM25 retriever could not be loaded")

        # 1. Clean conversational fillers and stopwords (Item 1)
        cleaned_query = clean_bm25_query(query)
        if not cleaned_query:
            return []

        query_tokens = bm25s.tokenize([cleaned_query], stopwords="en", show_progress=False)
        k = min(top_k, len(self.chunk_ids))
        if k == 0:
            return []

        doc_indices, scores = self.retriever.retrieve(
            query_tokens, k=k, show_progress=False
        )
        results: list[tuple[str, float]] = []

        for idx, score in zip(doc_indices[0], scores[0]):
            f_score = float(score)
            # Only keep chunks with positive term match score
            if f_score > 0.0:
                chunk_id = self.chunk_ids[int(idx)]
                results.append((chunk_id, f_score))

        return results
