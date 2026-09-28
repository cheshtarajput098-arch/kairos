"""Rule-based arm of the Stage 1 Retrieval Controller (SPEC §4.3)."""

from __future__ import annotations

from typing import Literal

from kairos.config import load_config
from kairos.schemas import ControllerDecision

DecisionType = Literal["WAIT", "RETRIEVE", "NO_RETRIEVAL"]


class RuleBasedController:
    def __init__(self) -> None:
        self.settings = load_config()

    def decide(
        self,
        features: dict[str, object],
        t: float,
        has_prior_answer: bool = False,
    ) -> ControllerDecision:
        """Evaluate features against thresholds to return WAIT / RETRIEVE / NO_RETRIEVAL."""
        cfg = self.settings.controller

        pres_score = float(features.get("presentation_intent", 0.0))  # type: ignore[arg-type]
        if has_prior_answer and pres_score >= cfg.presentation_intent_threshold:
            return ControllerDecision(
                timestamp_s=t,
                decision="NO_RETRIEVAL",
                reason="presentation_restructure",
                features=features,
            )

        n_entities = int(str(features.get("n_entities", 0)))
        drift = float(str(features.get("drift", 1.0)))
        syntactic_open = bool(features.get("syntactic_open", False))
        entity_saturation = bool(features.get("entity_saturation", False))
        probe_stable = bool(features.get("probe_stable", False))

        if n_entities < cfg.min_entities:
            return ControllerDecision(
                timestamp_s=t,
                decision="WAIT",
                reason="no_entities",
                features=features,
            )

        if syntactic_open and not probe_stable:
            return ControllerDecision(
                timestamp_s=t,
                decision="WAIT",
                reason="syntactic_open",
                features=features,
            )

        if drift < cfg.drift_threshold or entity_saturation or probe_stable:
            return ControllerDecision(
                timestamp_s=t,
                decision="RETRIEVE",
                reason="intent_stabilized",
                features=features,
            )

        return ControllerDecision(
            timestamp_s=t,
            decision="WAIT",
            reason="drift_unstable",
            features=features,
        )
