"""Stage 2 Multi-Intent Decomposition Manager (SPEC §5).

Orchestrates:
1. Speech disfluency normalization (fillers, repetitions, self-repairs).
2. Multi-intent splitting (rule-based or LLM mode).
3. Embedding-based deduplication (cosine similarity > 0.9 using BGE-small).
4. Hard sub-query cap (max 4 legs per turn).
5. Incremental diffing across chunk arrivals with stable leg IDs ('L1', 'L2', ...),
   reissuing retrieval ONLY for newly added or mutated legs.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from kairos.config import load_config
from kairos.decompose.disfluency import DisfluencyNormalizer
from kairos.decompose.llm_splitter import LLMDecomposer
from kairos.decompose.rule_splitter import RuleBasedSplitter
from kairos.schemas import Leg, SubQuery

logger = logging.getLogger("kairos.decompose.manager")

_global_embed_model = None


def _get_embed_model() -> Any:
    global _global_embed_model
    if _global_embed_model is None:
        try:
            from fastembed import TextEmbedding

            _global_embed_model = TextEmbedding("BAAI/bge-small-en-v1.5")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Could not load FastEmbed model: {e}")
            _global_embed_model = None
    return _global_embed_model


class DecompositionManager:
    def __init__(
        self,
        mode: str = "rule",
        max_legs: int = 4,
        dedupe_cosine: float = 0.9,
    ) -> None:
        self.config = load_config()
        self.mode = mode or self.config.decomposer.mode
        self.max_legs = max_legs or self.config.decomposer.max_legs
        self.dedupe_cosine = dedupe_cosine or self.config.decomposer.dedupe_cosine

        self.normalizer = DisfluencyNormalizer()
        self.rule_splitter = RuleBasedSplitter(max_legs=self.max_legs)
        self.llm_decomposer = LLMDecomposer(
            max_legs=self.max_legs, fallback_splitter=self.rule_splitter
        )

        # State tracking per turn: stable leg_id -> Leg
        self.active_legs: dict[str, Leg] = {}

    def reset_turn(self) -> None:
        """Reset state for a new turn."""
        self.active_legs.clear()

    def decompose(self, text: str, t: float) -> tuple[list[Leg], list[str]]:
        """Decompose text into deduplicated, capped legs and diff against active turn state.

        Returns:
            (all_active_legs, reissued_or_new_leg_ids)
        """
        # 1. Normalize disfluencies
        clean_text = self.normalizer.normalize(text)
        if not clean_text:
            return [], []

        # 2. Split clauses into candidate sub-queries
        if self.mode == "llm":
            candidates = self.llm_decomposer.decompose(clean_text)
        else:
            candidates = self.rule_splitter.split(clean_text)

        # 3. Deduplicate near-duplicate candidate legs via embedding similarity
        deduped = self._deduplicate_candidates(candidates)

        # 4. Enforce hard cap
        capped = deduped[: self.max_legs]

        # 5. Incremental diffing against active turn legs
        updated_legs, reissued_ids = self._diff_and_update(capped, t)

        return updated_legs, reissued_ids

    def _deduplicate_candidates(self, candidates: list[SubQuery]) -> list[SubQuery]:
        """Collapse candidates whose embedding cosine similarity > dedupe_cosine."""
        if len(candidates) <= 1:
            return candidates

        model = _get_embed_model()
        if model is None:
            # Fallback simple string matching dedupe
            seen_texts: set[str] = set()
            result: list[SubQuery] = []
            for c in candidates:
                norm = c.text.lower().strip()
                if norm not in seen_texts:
                    seen_texts.add(norm)
                    result.append(c)
            return result

        texts = [c.text for c in candidates]
        try:
            embs = list(model.embed(texts))
            norms = [np.linalg.norm(e) for e in embs]
            normalized_embs = [e / n if n > 0 else e for e, n in zip(embs, norms)]

            survivors: list[SubQuery] = []
            survivor_embs: list[np.ndarray] = []

            for idx, cand in enumerate(candidates):
                emb = normalized_embs[idx]
                is_duplicate = False
                for prev_emb in survivor_embs:
                    sim = float(np.dot(emb, prev_emb))
                    if sim >= self.dedupe_cosine:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    survivors.append(cand)
                    survivor_embs.append(emb)

            return survivors
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Embedding dedupe failed: {e}; falling back to candidates.")
            return candidates

    def _diff_and_update(self, candidates: list[SubQuery], t: float) -> tuple[list[Leg], list[str]]:
        """Incrementally match candidates against existing turn legs to preserve stable IDs."""
        reissued_ids: list[str] = []
        new_active_legs: dict[str, Leg] = {}

        for idx, cand in enumerate(candidates):
            leg_id = f"L{idx + 1}"
            existing_leg = self.active_legs.get(leg_id)

            if existing_leg is None:
                # New leg discovered in compound query
                new_leg = Leg(
                    leg_id=leg_id,
                    text=cand.text,
                    entities=cand.entities,
                    first_dispatch_s=t,
                )
                new_active_legs[leg_id] = new_leg
                reissued_ids.append(leg_id)
            elif existing_leg.text.strip().lower() != cand.text.strip().lower():
                # Leg mutated by incoming constraints or speech revisions
                existing_leg.text = cand.text
                existing_leg.entities = cand.entities
                existing_leg.first_dispatch_s = t
                new_active_legs[leg_id] = existing_leg
                reissued_ids.append(leg_id)
            else:
                # Leg is identical to previous prefix: preserve and do not reissue
                new_active_legs[leg_id] = existing_leg

        self.active_legs = new_active_legs
        return list(self.active_legs.values()), reissued_ids
