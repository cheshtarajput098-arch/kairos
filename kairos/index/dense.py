"""Dense vector index using FastEmbed BAAI/bge-small-en-v1.5 (SPEC §1, §6.1)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

from kairos.schemas import CorpusChunk


class DenseIndex:
    def __init__(self, index_dir: Path = Path("index/dense"), model_name: str = "BAAI/bge-small-en-v1.5"):
        self.index_dir = index_dir
        self.model_name = model_name
        self.model: TextEmbedding | None = None
        self.chunk_ids: list[str] = []
        self.embeddings: np.ndarray | None = None

    def _get_model(self) -> TextEmbedding:
        if self.model is None:
            self.model = TextEmbedding(model_name=self.model_name)
        return self.model

    def build(self, chunks: list[CorpusChunk]) -> None:
        """Embed all chunks and save embeddings matrix and chunk mapping."""
        self.chunk_ids = [c.chunk_id for c in chunks]
        texts = [f"{c.title}\n{c.text}" for c in chunks]

        model = self._get_model()
        emb_list = list(model.embed(texts))
        self.embeddings = np.array(emb_list, dtype=np.float32)

        # Normalize embeddings to unit length for fast dot-product cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-12
        self.embeddings = self.embeddings / norms

        self.save()

    def save(self) -> None:
        """Save embeddings array and chunk mapping."""
        if self.embeddings is None:
            raise ValueError("Cannot save empty dense index")

        self.index_dir.mkdir(parents=True, exist_ok=True)
        np.save(self.index_dir / "embeddings.npy", self.embeddings)

        mapping_file = self.index_dir / "chunk_ids.json"
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(self.chunk_ids, f, indent=2)

    def load(self) -> None:
        """Load embeddings and chunk mapping from disk."""
        mapping_file = self.index_dir / "chunk_ids.json"
        emb_file = self.index_dir / "embeddings.npy"

        if not mapping_file.exists() or not emb_file.exists():
            raise FileNotFoundError(f"Dense index files not found in {self.index_dir}")

        with open(mapping_file, encoding="utf-8") as f:
            self.chunk_ids = json.load(f)

        self.embeddings = np.load(emb_file)

    def search(self, query: str, top_k: int = 20) -> list[tuple[str, float]]:
        """Search query against dense index. Returns list of (chunk_id, cosine_score)."""
        if self.embeddings is None or not self.chunk_ids:
            self.load()
        if self.embeddings is None:
            raise RuntimeError("Embeddings could not be loaded")

        model = self._get_model()
        q_emb = next(iter(model.embed([query])))
        q_norm = np.linalg.norm(q_emb)
        if q_norm > 0:
            q_emb = q_emb / q_norm

        scores = np.dot(self.embeddings, q_emb)
        k = min(top_k, len(self.chunk_ids))
        if k == 0:
            return []

        top_indices = np.argsort(-scores)[:k]
        results: list[tuple[str, float]] = []

        for idx in top_indices:
            chunk_id = self.chunk_ids[int(idx)]
            score = float(scores[int(idx)])
            results.append((chunk_id, score))

        return results
