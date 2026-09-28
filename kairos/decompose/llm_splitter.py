"""LLM-based Multi-Intent Decomposer (SPEC §5).

Uses structured LLM generation with fixed JSON schema:
{"sub_queries": [{"leg_id": str, "text": str, "entities": list[str]}]}
Operates at temperature 0 with user text delimited in <user_utterance> blocks.
Falls back cleanly to RuleBasedSplitter on timeout, schema errors, or missing models.
"""
from __future__ import annotations

import logging
from typing import Any

from kairos.decompose.rule_splitter import RuleBasedSplitter
from kairos.llm.provider import LLMProvider
from kairos.schemas import DecompositionResponse, SubQuery

logger = logging.getLogger("kairos.decompose.llm")

_SYSTEM_PROMPT = (
    "You are an event-driven query decomposition engine. "
    "Given a user's speech transcript enclosed in <user_utterance> blocks, decompose compound multi-part "
    "questions into distinct, standalone sub-queries for parallel corpus search. "
    "Carry forward any shared context (locations, organizations, quantities, dates) into every sub-query. "
    "Do NOT answer the question. Only return structured JSON matching the requested schema."
)


class LLMDecomposer:
    def __init__(
        self,
        provider: LLMProvider | None = None,
        deadline_ms: int = 600,
        fallback_splitter: RuleBasedSplitter | None = None,
        max_legs: int = 4,
    ) -> None:
        self.provider = provider or LLMProvider()
        self.deadline_ms = deadline_ms
        self.fallback = fallback_splitter or RuleBasedSplitter(max_legs=max_legs)
        self.max_legs = max_legs

    def decompose(self, text: str) -> list[SubQuery]:
        """Decompose text using LLM with automatic fallback to RuleBasedSplitter."""
        if not text.strip():
            return []

        # Spotlight user utterance inside delimited untrusted tags (Security Rule 2)
        user_message = f"<user_utterance>\n{text.strip()}\n</user_utterance>"
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        limits: dict[str, Any] = {"deadline_ms": self.deadline_ms, "max_legs": self.max_legs}

        try:
            raw_response = self.provider.generate_json(DecompositionResponse, messages, limits)
            validated = DecompositionResponse.model_validate(raw_response)
            if validated.sub_queries:
                # Ensure leg IDs are L1, L2... and capped
                capped = validated.sub_queries[: self.max_legs]
                for idx, sq in enumerate(capped):
                    sq.leg_id = f"L{idx + 1}"
                return capped
        except Exception as e:  # noqa: BLE001
            logger.warning(f"LLM decomposition failed or timed out: {e}; falling back to rule-based splitter.")

        return self.fallback.split(text)
