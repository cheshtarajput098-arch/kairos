"""Stage 5 Session Delta Engine (SPEC §7, Gate G5).

Refines rather than restarts:
1. Classifies new turns: 'presentation_only', 'constraint_on_existing', 'contradiction', 'new_topic'.
2. For constraints: builds targeted delta queries for affected legs only, leaving unaffected
   claims byte-identical and incrementing answer version.
3. For presentation-only: reformats without retrieval, keeping citations identical.
4. For contradictions: retracts and reissues, recording diff in VersionDiff.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import Any

from kairos.schemas import ClaimObject, CorpusChunk, Leg, VersionDiff
from kairos.session.store import SessionState
from kairos.synth.extractive import ExtractiveSynthesizer

logger = logging.getLogger("kairos.session.delta")

_PRESENTATION_CUES = re.compile(
    r"\b(?:as\s+bullets|bullet\s+points|summarize|summarise|shorter|in\s+short|briefly|reformat|as\s+a\s+list)\b",
    re.IGNORECASE,
)
_CONTRADICTION_CUES = re.compile(
    r"\b(?:no\b|not\s+in\b|that'?s\s+wrong|cancel|scratch\s+that|instead\s+of)\b",
    re.IGNORECASE,
)
_CONSTRAINT_CUES = re.compile(
    r"\b(?:actually|instead|also|plus|only|must\s+have|specifically|for\s+\d+|in\s+[A-Z][a-z]+)\b",
    re.IGNORECASE,
)


class DeltaEngine:
    def __init__(self, synthesizer: ExtractiveSynthesizer | None = None) -> None:
        self.synthesizer = synthesizer or ExtractiveSynthesizer()

    def classify_turn(self, text: str, session: SessionState) -> str:
        """Classify a new turn against active session state."""
        has_prior = bool(session.answer and session.claims)
        if not has_prior:
            return "new_topic"

        clean = text.strip()
        if _PRESENTATION_CUES.search(clean):
            return "presentation_only"

        if _CONTRADICTION_CUES.search(clean):
            return "contradiction"

        if _CONSTRAINT_CUES.search(clean):
            return "constraint_on_existing"

        # Check entity/keyword overlap with existing legs
        q_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", clean.lower()))
        for leg in session.active_legs.values():
            leg_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", leg.text.lower()))
            if len(q_words.intersection(leg_words)) >= 1:
                return "constraint_on_existing"

        return "new_topic"

    def handle_presentation_only(
        self,
        session: SessionState,
    ) -> tuple[str, list[ClaimObject], VersionDiff]:
        """Restructure stored answer into bulleted presentation without retrieval."""
        claims = session.claims
        bullet_lines = []
        for c in claims:
            # Format clean bullet item
            bullet_lines.append(f"• {c.text}")

        new_answer = "\n".join(bullet_lines)
        diff = VersionDiff(
            added=[],
            changed=[],
            retracted=[],
            unchanged=[c.claim_id for c in claims],
            citations_added=[],
        )
        return new_answer, claims, diff

    def find_affected_leg(self, constraint_text: str, session: SessionState) -> Leg | None:
        """Identify which prior leg is affected by incoming constraint."""
        c_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", constraint_text.lower()))
        best_leg: Leg | None = None
        best_overlap = -1

        for leg in session.active_legs.values():
            leg_words = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", leg.text.lower()))
            overlap = len(c_words.intersection(leg_words))
            if overlap > best_overlap:
                best_overlap = overlap
                best_leg = leg

        # If no explicit keyword overlap, default to most recent leg
        if best_leg is None and session.active_legs:
            best_leg = list(session.active_legs.values())[-1]

        return best_leg

    def apply_constraint_refinement(
        self,
        affected_leg: Leg,
        delta_retrieval_res: dict[str, Any],
        chunks_map: Mapping[str, CorpusChunk | dict[str, Any]],
        session: SessionState,
    ) -> tuple[str, list[ClaimObject], list[str], VersionDiff]:
        """Patch only the affected claim while preserving unaffected claims byte-for-byte."""
        new_version = session.current_version + 1

        # Synthesize patched claim for the affected leg
        patched_claim = self.synthesizer.synthesize_leg(
            affected_leg, delta_retrieval_res, chunks_map, version=new_version
        )

        final_claims: list[ClaimObject] = []
        unchanged_ids: list[str] = []
        changed_ids: list[str] = []
        new_citations: list[str] = []

        for prior_claim in session.claims:
            if prior_claim.leg_id == affected_leg.leg_id:
                if patched_claim:
                    final_claims.append(patched_claim)
                    changed_ids.append(patched_claim.claim_id)
                    for cite in patched_claim.citations:
                        if cite not in session.citations:
                            new_citations.append(cite)
            else:
                # UNAFFECTED CLAIM: MUST STAY STRICTLY BYTE-IDENTICAL (Gate G5)
                final_claims.append(prior_claim)
                unchanged_ids.append(prior_claim.claim_id)

        all_citations = list(dict.fromkeys(session.citations + new_citations))
        new_answer = " ".join(c.text for c in final_claims)

        diff = VersionDiff(
            added=[],
            changed=changed_ids,
            retracted=[],
            unchanged=unchanged_ids,
            citations_added=new_citations,
        )

        return new_answer, final_claims, all_citations, diff

    def apply_contradiction(
        self,
        retracted_leg_id: str,
        session: SessionState,
    ) -> tuple[str, list[ClaimObject], VersionDiff]:
        """Retract a contradicted claim and update answer."""
        final_claims: list[ClaimObject] = []
        retracted_ids: list[str] = []
        unchanged_ids: list[str] = []

        for c in session.claims:
            if c.leg_id == retracted_leg_id:
                retracted_ids.append(c.claim_id)
            else:
                final_claims.append(c)
                unchanged_ids.append(c.claim_id)

        new_answer = " ".join(c.text for c in final_claims)
        diff = VersionDiff(
            added=[],
            changed=[],
            retracted=retracted_ids,
            unchanged=unchanged_ids,
            citations_added=[],
        )
        return new_answer, final_claims, diff
