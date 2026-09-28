"""Reciprocal Rank Fusion (RRF) for hybrid retrieval results (SPEC §6.1)."""

from __future__ import annotations


def reciprocal_rank_fusion(
    ranked_lists: list[list[tuple[str, float]]],
    k: int = 60,
    top_n: int = 8,
) -> list[tuple[str, float]]:
    """Compute RRF score over multiple ranked lists of (chunk_id, score).

    Formula: RRF_score(chunk) = sum(1 / (k + rank))
    Returns sorted list of (chunk_id, rrf_score).
    """
    rrf_scores: dict[str, float] = {}

    for ranked_list in ranked_lists:
        for rank, (chunk_id, _) in enumerate(ranked_list, start=1):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank))

    # Sort descending by RRF score
    sorted_chunks = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_chunks[:top_n]
