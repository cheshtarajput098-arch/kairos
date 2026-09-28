"""Cross-leg deduplication, near-duplicate collapse, and conflict detection (SPEC §6.1)."""

from __future__ import annotations

import re

from kairos.schemas import CorpusChunk

# Regex to detect numbers/dates/percentages for factual density and conflict check
NUMERIC_RE = re.compile(
    r"\b\d+(?:\.\d+)?(?:%|st|nd|rd|th|am|pm|days?|hours?|months?|years?)?\b", re.IGNORECASE
)


def compute_factual_density(text: str) -> float:
    """Compute ratio of numeric/fact tokens to total tokens."""
    tokens = text.split()
    if not tokens:
        return 0.0
    num_matches = len(NUMERIC_RE.findall(text))
    return num_matches / len(tokens)


def check_conflicts(chunks: list[CorpusChunk]) -> list[dict[str, str]]:
    """Inspect chunks for potential factual conflicts across numerical/temporal claims."""
    conflicts: list[dict[str, str]] = []
    # Simple heuristic comparison of key numerical attributes if chunks refer to same entity
    seen_facts: dict[str, str] = {}
    for c in chunks:
        numbers = NUMERIC_RE.findall(c.text)
        if numbers:
            fact_key = f"{c.doc_id}"
            fact_val = ", ".join(numbers[:3])
            if fact_key in seen_facts and seen_facts[fact_key] != fact_val:
                conflicts.append(
                    {
                        "doc_id": c.doc_id,
                        "chunk_id": c.chunk_id,
                        "fact_difference": f"{seen_facts[fact_key]} vs {fact_val}",
                    }
                )
            else:
                seen_facts[fact_key] = fact_val
    return conflicts


def deduplicate_and_rank(
    fused_results: list[tuple[str, float]],
    chunks_map: dict[str, CorpusChunk],
    top_n: int = 8,
) -> list[tuple[str, float]]:
    """Deduplicate chunks, apply factual density tie-breaks, and return top-N."""
    seen_texts: set[str] = set()
    ranked: list[tuple[str, float, float]] = []

    for chunk_id, rrf_score in fused_results:
        chunk = chunks_map.get(chunk_id)
        if not chunk:
            continue

        # Simple near-duplicate check based on normalized body text
        norm_body = " ".join(chunk.text.lower().split())
        if norm_body in seen_texts:
            continue
        seen_texts.add(norm_body)

        density = compute_factual_density(chunk.text)
        ranked.append((chunk_id, rrf_score, density))

    # Sort primarily by RRF score, tie-break by factual density
    ranked.sort(key=lambda x: (x[1], x[2]), reverse=True)

    return [(cid, score) for cid, score, _ in ranked[:top_n]]
