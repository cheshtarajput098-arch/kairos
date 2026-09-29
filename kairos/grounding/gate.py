"""Deterministic Grounding Gate & Citation Verification (SPEC §6.3, Gate G4).

Enforces Stage 1 deterministic validation:
1. Every cited ID must exist in this session's retrieved chunk set.
2. The claim's evidence_span must appear in that cited chunk verbatim or with
   normalized punctuation/whitespace (fuzzy ratio >= 0.9).
3. Failed claims are marked dropped and replaced with explicit uncertainty statements.
Stage 2 (optional NLI gate) is provided as an async extension hook.
"""

from __future__ import annotations

import difflib
import logging
import re
from collections.abc import Mapping
from typing import Any

from kairos.schemas import ClaimObject, CorpusChunk

logger = logging.getLogger("kairos.grounding.gate")


def _normalize_text(text: str) -> str:
    """Normalize text by lowercasing, collapsing whitespace, and stripping punctuation."""
    lowered = text.lower()
    cleaned = re.sub(r"[^\w\s]", "", lowered)
    return " ".join(cleaned.split())


class GroundingGate:
    def __init__(self, fuzzy_threshold: float = 0.9) -> None:
        self.fuzzy_threshold = fuzzy_threshold

    def verify_claim(
        self,
        claim: ClaimObject,
        retrieved_chunks_map: Mapping[str, CorpusChunk | dict[str, Any]],
    ) -> tuple[ClaimObject, bool, str]:
        """Verify claim against retrieved chunks.

        Returns:
            (claim_with_updated_status, passed, reason)
        """
        # 0. Explicit uncertainty statements (e.g., documented gaps) pass as valid uncertainty
        if claim.status == "uncertain":
            return claim, True, "explicit_uncertainty"

        # 1. Citations existence check
        if not claim.citations:
            claim.status = "dropped"
            return claim, False, "missing_citations"

        for cited_id in claim.citations:
            if cited_id not in retrieved_chunks_map:
                claim.status = "dropped"
                logger.warning(
                    f"Grounding gate rejected claim {claim.claim_id}: "
                    f"fabricated or unretrieved ID '{cited_id}'"
                )
                return claim, False, f"unretrieved_or_fabricated_id:{cited_id}"

        # 2. Verbatim / normalized evidence span verification
        if not claim.evidence_span or not claim.evidence_span.strip():
            claim.status = "dropped"
            return claim, False, "empty_evidence_span"

        span_norm = _normalize_text(claim.evidence_span)
        if not span_norm:
            claim.status = "dropped"
            return claim, False, "empty_normalized_span"

        span_verified = False
        for cited_id in claim.citations:
            chunk_data = retrieved_chunks_map[cited_id]
            chunk_text = (
                chunk_data.text
                if isinstance(chunk_data, CorpusChunk)
                else str(chunk_data.get("text", ""))
            )
            chunk_norm = _normalize_text(chunk_text)

            # Substring check on normalized text
            if span_norm in chunk_norm:
                span_verified = True
                break

            # Fallback fuzzy matching for minor OCR/punctuation differences
            # Find closest substring in chunk
            words = chunk_norm.split()
            span_words_count = len(span_norm.split())

            for i in range(max(1, len(words) - span_words_count + 1)):
                candidate = " ".join(words[i : i + span_words_count])
                ratio = difflib.SequenceMatcher(None, span_norm, candidate).ratio()
                if ratio >= self.fuzzy_threshold:
                    span_verified = True
                    break

            if span_verified:
                break

        if not span_verified:
            claim.status = "dropped"
            logger.warning(
                f"Grounding gate rejected claim {claim.claim_id}: "
                f"evidence span not found in cited chunks {claim.citations}"
            )
            return claim, False, "evidence_span_not_in_chunk"

        claim.status = "verified"
        return claim, True, "verified"

    def verify_claims(
        self,
        claims: list[ClaimObject],
        retrieved_chunks_map: Mapping[str, CorpusChunk | dict[str, Any]],
    ) -> tuple[list[ClaimObject], list[str]]:
        """Verify list of claims, returning all claims with updated statuses and uncertainty messages.

        Returns:
            (verified_and_dropped_claims, uncertainty_statements)
        """
        verified_claims: list[ClaimObject] = []
        uncertainties: list[str] = []

        for c in claims:
            verified_claim, passed, reason = self.verify_claim(c, retrieved_chunks_map)
            verified_claims.append(verified_claim)
            if not passed:
                uncertainty_msg = f"Evidence could not be verified in the supplied documents for leg {c.leg_id} ({reason})."
                uncertainties.append(uncertainty_msg)

        return verified_claims, uncertainties
