"""Answer-as-you-speak Speculative Answer Drafting (SPEC §6.4).

Drafts and verifies each answer section before the user finishes speaking.
At utterance end, verifies whether drafts survive byte-identical (committed)
or were mutated/cancelled (rolled back), computing Ready-at-End and rollback metrics.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from kairos.grounding.gate import GroundingGate
from kairos.schemas import ClaimObject, CorpusChunk, Leg
from kairos.synth.extractive import ExtractiveSynthesizer

logger = logging.getLogger("kairos.synth.drafting")


@dataclass
class DraftEntry:
    leg_id: str
    leg_text: str
    claim: ClaimObject
    t_verified: float
    status: str = "verified_draft"  # "drafting" | "verified_draft" | "committed" | "rolled_back"
    exposure_ms: float = 0.0


class DraftingManager:
    def __init__(
        self,
        synthesizer: ExtractiveSynthesizer | None = None,
        gate: GroundingGate | None = None,
    ) -> None:
        self.synthesizer = synthesizer or ExtractiveSynthesizer()
        self.gate = gate or GroundingGate()

        # Active drafts for current turn: leg_id -> DraftEntry
        self.drafts: dict[str, DraftEntry] = {}
        self.draft_events: list[dict[str, Any]] = []
        self.first_verified_draft_t: float | None = None
        self.total_drafts_created: int = 0
        self.total_rollbacks: int = 0

    def reset_turn(self) -> None:
        """Reset drafting state for a new turn."""
        self.drafts.clear()
        self.draft_events.clear()
        self.first_verified_draft_t = None
        self.total_drafts_created = 0
        self.total_rollbacks = 0

    def draft_leg(
        self,
        leg: Leg,
        retrieval_res: dict[str, Any],
        chunks_map: Mapping[str, CorpusChunk | dict[str, Any]],
        t: float,
        version: int = 1,
    ) -> ClaimObject | None:
        """Synthesize and gate a draft section mid-utterance when leg retrieval completes."""
        self.draft_events.append(
            {
                "event": "draft_started",
                "leg_id": leg.leg_id,
                "timestamp_s": t,
            }
        )
        self.total_drafts_created += 1

        claim = self.synthesizer.synthesize_leg(leg, retrieval_res, chunks_map, version=version)
        if claim is None:
            return None

        # Pass through deterministic grounding gate
        verified_claim, passed, reason = self.gate.verify_claim(claim, chunks_map)
        if not passed:
            logger.info(f"Draft for leg {leg.leg_id} dropped by grounding gate: {reason}")
            return None

        draft_entry = DraftEntry(
            leg_id=leg.leg_id,
            leg_text=leg.text,
            claim=verified_claim,
            t_verified=t,
            status="verified_draft",
        )
        self.drafts[leg.leg_id] = draft_entry

        if self.first_verified_draft_t is None:
            self.first_verified_draft_t = t

        self.draft_events.append(
            {
                "event": "draft_verified",
                "leg_id": leg.leg_id,
                "claim_id": verified_claim.claim_id,
                "timestamp_s": t,
            }
        )
        return verified_claim

    def commit_turn(
        self,
        final_legs: list[Leg],
        leg_results_map: dict[str, dict[str, Any]],
        chunks_map: Mapping[str, CorpusChunk | dict[str, Any]],
        utterance_end_t: float,
        version: int = 1,
    ) -> tuple[list[ClaimObject], dict[str, Any]]:
        """Commit or roll back active drafts at utterance end, returning final claims and metrics.

        Returns:
            (committed_claims, drafting_metrics)
        """
        committed_claims: list[ClaimObject] = []
        byte_identical_drafts_count = 0
        total_rollback_exposure_ms = 0.0

        final_legs_by_id = {leg.leg_id: leg for leg in final_legs}

        # 1. Process existing drafts against final legs
        for leg_id, draft in list(self.drafts.items()):
            final_leg = final_legs_by_id.get(leg_id)

            # Check if leg survived unchanged
            if (
                final_leg is not None
                and final_leg.text.strip().lower() == draft.leg_text.strip().lower()
            ):
                # Leg is stable: commit draft byte-identical
                draft.status = "committed"
                committed_claims.append(draft.claim)
                byte_identical_drafts_count += 1
                self.draft_events.append(
                    {
                        "event": "draft_committed",
                        "leg_id": leg_id,
                        "claim_id": draft.claim.claim_id,
                        "timestamp_s": utterance_end_t,
                    }
                )
            else:
                # Leg mutated or was cancelled: rollback
                draft.status = "rolled_back"
                exposure = max(0.0, (utterance_end_t - draft.t_verified) * 1000.0)
                draft.exposure_ms = exposure
                total_rollback_exposure_ms += exposure
                self.total_rollbacks += 1

                self.draft_events.append(
                    {
                        "event": "draft_rolled_back",
                        "leg_id": leg_id,
                        "claim_id": draft.claim.claim_id,
                        "timestamp_s": utterance_end_t,
                        "exposure_ms": exposure,
                    }
                )

                # If final leg still exists (mutated), re-synthesize from updated evidence
                if final_leg is not None:
                    res = leg_results_map.get(leg_id, {})
                    new_claim = self.synthesizer.synthesize_leg(
                        final_leg, res, chunks_map, version=version
                    )
                    if new_claim:
                        v_claim, passed, _ = self.gate.verify_claim(new_claim, chunks_map)
                        if passed:
                            committed_claims.append(v_claim)

        # 2. Check any final legs that were never drafted mid-utterance
        for leg in final_legs:
            if leg.leg_id not in self.drafts:
                res = leg_results_map.get(leg.leg_id, {})
                claim = self.synthesizer.synthesize_leg(leg, res, chunks_map, version=version)
                if claim:
                    v_claim, passed, _ = self.gate.verify_claim(claim, chunks_map)
                    if passed:
                        committed_claims.append(v_claim)

        # 2b. Check for evidence gap claims across all final legs
        for leg in final_legs:
            check_gap_fn = getattr(self.synthesizer, "check_evidence_gap", None)
            if callable(check_gap_fn):
                res = leg_results_map.get(leg.leg_id, {})
                gap_claim = check_gap_fn(leg, res, chunks_map, version=version)
                if gap_claim and not any(c.claim_id == gap_claim.claim_id for c in committed_claims):
                    v_gap, passed, _ = self.gate.verify_claim(gap_claim, chunks_map)
                    if passed:
                        committed_claims.append(v_gap)

        # 3. Compute metrics per SPEC §6.4 & §9.1a
        total_claims = len(committed_claims)
        ready_at_end = (byte_identical_drafts_count / total_claims) if total_claims > 0 else 0.0
        draft_survival_rate = (
            (byte_identical_drafts_count / self.total_drafts_created)
            if self.total_drafts_created > 0
            else 0.0
        )
        rollback_rate = (
            (self.total_rollbacks / self.total_drafts_created)
            if self.total_drafts_created > 0
            else 0.0
        )
        first_verified_rel_end_s = (
            round(self.first_verified_draft_t - utterance_end_t, 3)
            if self.first_verified_draft_t is not None
            else None
        )

        metrics = {
            "ready_at_end": round(ready_at_end, 3),
            "ready_count": byte_identical_drafts_count,
            "total_parts": len(final_legs),
            "draft_survival_rate": round(draft_survival_rate, 3),
            "rollback_rate": round(rollback_rate, 3),
            "rollback_exposure_ms": round(total_rollback_exposure_ms, 1),
            "first_verified_rel_end_s": first_verified_rel_end_s,
            "drafts_count": self.total_drafts_created,
            "rollbacks_count": self.total_rollbacks,
            "events": self.draft_events,
        }

        return committed_claims, metrics
