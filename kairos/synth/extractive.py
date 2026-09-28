"""Stage 5 Speed-1 Extractive Synthesizer (SPEC §6.2).

Extracts high-scoring, grounded sentences directly from top retrieved chunks
per leg without LLM dependency. Formats claims with verbatim evidence spans (<= 30 words)
and exact citations ([Doc_ID §Section]).
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import Any

from kairos.schemas import ClaimObject, CorpusChunk, Leg

logger = logging.getLogger("kairos.synth.extractive")

# Sentence splitter pattern
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _split_into_sentences(text: str) -> list[str]:
    """Split chunk text into sentences, stripping surrounding whitespace."""
    raw = _SENTENCE_SPLIT.split(text.strip())
    sentences = [s.strip() for s in raw if len(s.strip()) >= 15]
    return sentences if sentences else [text.strip()]


def _score_sentence(sentence: str, query: str) -> float:
    """Calculate token overlap relevance score between a sentence and query."""
    q_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", query.lower()))
    if not q_words:
        return 1.0

    s_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", sentence.lower()))
    overlap = len(q_words.intersection(s_words))
    # Normalize by query length and sentence length penalty
    return overlap / (len(q_words) + 0.1 * len(s_words))


class ExtractiveSynthesizer:
    def __init__(self) -> None:
        pass

    def synthesize_leg(
        self,
        leg: Leg,
        retrieval_results: dict[str, Any],
        chunks_map: Mapping[str, CorpusChunk | dict[str, Any]],
        version: int = 1,
    ) -> ClaimObject | None:
        """Synthesize a single claim for a leg from its top retrieved evidence."""
        # Extract top chunk IDs
        dense_results: list[tuple[str, float]] = retrieval_results.get("dense_results", [])
        sparse_results: list[tuple[str, float]] = retrieval_results.get("sparse_results", [])

        # Priority to dense/sparse combined top candidate
        candidate_ids: list[str] = []
        for cid, _ in dense_results[:3]:
            if cid not in candidate_ids and cid in chunks_map:
                candidate_ids.append(cid)
        for cid, _ in sparse_results[:3]:
            if cid not in candidate_ids and cid in chunks_map:
                candidate_ids.append(cid)

        if not candidate_ids:
            # Fallback check any available chunk
            for cid in chunks_map:
                candidate_ids.append(cid)
                break

        if not candidate_ids:
            return None

        best_sentence = ""
        best_chunk_id = candidate_ids[0]
        best_score = -1.0

        for cid in candidate_ids:
            chunk = chunks_map[cid]
            text = chunk.text if isinstance(chunk, CorpusChunk) else str(chunk.get("text", ""))
            sentences = _split_into_sentences(text)

            for s in sentences:
                score = _score_sentence(s, leg.text)
                if score > best_score:
                    best_score = score
                    best_sentence = s
                    best_chunk_id = cid

        if not best_sentence:
            chunk = chunks_map[best_chunk_id]
            best_sentence = (
                chunk.text if isinstance(chunk, CorpusChunk) else str(chunk.get("text", ""))
            )

        # Ensure evidence_span is <= 30 words per SPEC §6.2
        words = best_sentence.split()
        if len(words) > 30:
            evidence_span = " ".join(words[:30])
        else:
            evidence_span = best_sentence

        # Clean natural claim text
        claim_text = f"{evidence_span} [{best_chunk_id}]"

        return ClaimObject(
            claim_id=f"c_{leg.leg_id}",
            leg_id=leg.leg_id,
            text=claim_text,
            citations=[best_chunk_id],
            evidence_span=evidence_span,
            status="verified",
            version=version,
        )

    def synthesize_all(
        self,
        legs: list[Leg],
        leg_results_map: dict[str, dict[str, Any]],
        chunks_map: Mapping[str, CorpusChunk | dict[str, Any]],
        version: int = 1,
    ) -> list[ClaimObject]:
        """Synthesize claims for all provided legs."""
        claims: list[ClaimObject] = []
        for leg in legs:
            res = leg_results_map.get(leg.leg_id, {})
            claim = self.synthesize_leg(leg, res, chunks_map, version=version)
            if claim is not None:
                claims.append(claim)
        return claims
