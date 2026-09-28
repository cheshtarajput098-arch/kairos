"""Feature extraction for the Stage 1 Retrieval Controller (SPEC §4.2)."""
from __future__ import annotations

import re

import numpy as np
from fastembed import TextEmbedding

from kairos.index.sparse import SparseIndex

DANGLING_CONNECTORS = {
    "and", "in", "the", "for", "with", "to", "or", "of", "at", "a", "an", "is",
    "about", "on", "as", "by", "that", "this", "my", "our", "their", "its", "from"
}

PRESENTATION_CUES = [
    re.compile(r"\b(repeat|shorten|bullet|bullets|summarize|format|restructure)\b", re.IGNORECASE),
    re.compile(r"\b(in\s+(?:two\s+)?bullets?|as\s+bullets?|in\s+bullet\s+(?:points?|format)|bullet\s+format|single\s+sentence)\b", re.IGNORECASE),
    re.compile(r"\b(your\s+last\s+answer|the\s+previous\s+answer|that|it|previous)\b", re.IGNORECASE),
]

# Simple entity extractor: capitalized words, domain keywords, numbers
ENTITY_RE = re.compile(r"\b[A-Z][a-z0-9]+\b|\b\d+(?:st|nd|rd|th)?\b|\b(?:workshop|venues?|cancellation|catering|refunds?|reimbursement|travel|policy|receipts?|meeting|rooms?)\b", re.IGNORECASE)


def extract_entities(text: str) -> set[str]:
    """Extract set of searchable entity and keyword candidates from text."""
    matches = ENTITY_RE.findall(text)
    return {m.strip().lower() for m in matches if len(m.strip()) > 1}


def is_syntactic_open(text: str) -> bool:
    """Check if the prefix ends in a dangling connector word."""
    words = text.strip().split()
    if not words:
        return True
    last_word = re.sub(r"[^\w]", "", words[-1]).lower()
    return last_word in DANGLING_CONNECTORS


def detect_presentation_intent(text: str, has_prior_answer: bool) -> float:
    """Score presentation/formatting restructuring intent."""
    if not has_prior_answer:
        return 0.0

    score = 0.0
    for cue in PRESENTATION_CUES:
        if cue.search(text):
            score += 0.4
    return min(score, 1.0)


class ControllerFeatureExtractor:
    def __init__(self, sparse_index: SparseIndex | None = None):
        self.sparse_index = sparse_index
        self._embed_model: TextEmbedding | None = None
        self._last_embedding: np.ndarray | None = None
        self._last_entities: set[str] = set()
        self._last_probe: list[str] = []
        self._stable_entity_count = 0
        self._stable_probe_count = 0

    def _get_embed_model(self) -> TextEmbedding:
        if self._embed_model is None:
            self._embed_model = TextEmbedding("BAAI/bge-small-en-v1.5")
        return self._embed_model

    def reset_turn(self) -> None:
        """Reset state at turn boundary."""
        self._last_embedding = None
        self._last_entities = set()
        self._last_probe = []
        self._stable_entity_count = 0
        self._stable_probe_count = 0

    def compute_features(
        self,
        prefix: str,
        has_prior_answer: bool = False,
    ) -> dict[str, object]:
        """Compute feature vector for the given prefix."""
        words = prefix.strip().split()
        n_words = len(words)

        entities = extract_entities(prefix)
        syntactic_open = is_syntactic_open(prefix)
        presentation_intent = detect_presentation_intent(prefix, has_prior_answer)

        # Entity saturation: has entity set remained unchanged?
        if entities and entities == self._last_entities:
            self._stable_entity_count += 1
        else:
            self._stable_entity_count = 1 if entities else 0
        self._last_entities = entities

        entity_saturation = self._stable_entity_count >= 2

        # Embedding drift calculation
        drift = 1.0
        if prefix:
            model = self._get_embed_model()
            emb = next(iter(model.embed([prefix])))
            norm = np.linalg.norm(emb)
            if norm > 0:
                emb = emb / norm

            if self._last_embedding is not None:
                cosine_sim = float(np.dot(emb, self._last_embedding))
                drift = max(0.0, 1.0 - cosine_sim)
            else:
                drift = 0.0  # first prefix embedding
            self._last_embedding = emb

        # BM25 probe top-3 stability
        probe_stable = False
        probe_chunks: list[str] = []
        if self.sparse_index and n_words >= 3:
            try:
                probe_res = self.sparse_index.search(prefix, top_k=3)
                probe_chunks = [cid for cid, _ in probe_res]
                if probe_chunks and probe_chunks == self._last_probe:
                    self._stable_probe_count += 1
                else:
                    self._stable_probe_count = 1
                self._last_probe = probe_chunks
                probe_stable = self._stable_probe_count >= 2
            except Exception:  # noqa: BLE001
                probe_stable = False

        return {
            "n_words": n_words,
            "entities": sorted(entities),
            "n_entities": len(entities),
            "entity_saturation": entity_saturation,
            "drift": round(drift, 4),
            "syntactic_open": syntactic_open,
            "presentation_intent": round(presentation_intent, 2),
            "probe_stable": probe_stable,
            "probe_chunks": probe_chunks,
        }
