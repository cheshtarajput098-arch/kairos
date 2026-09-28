"""Parallel Retrieval Dispatcher for Active Legs (SPEC §5, §6.1).

Dispatches concurrent hybrid retrieval across active query legs under per-leg deadlines.
Integrates with Stage 2 incremental diffing so that only newly proposed or mutated
legs trigger new retrieval tasks, preserving completed results for stable legs.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from kairos.retrieve.hybrid import HybridRetriever
from kairos.schemas import Leg

logger = logging.getLogger("kairos.decompose.dispatcher")


class ParallelDispatcher:
    def __init__(
        self,
        retriever: HybridRetriever,
        deadline_ms: int = 400,
    ) -> None:
        self.retriever = retriever
        self.deadline_ms = deadline_ms
        self.turn_results: dict[str, dict[str, Any]] = {}

    def reset_turn(self) -> None:
        """Reset dispatcher results for a new turn."""
        self.turn_results.clear()

    async def dispatch_legs(
        self,
        legs: list[Leg],
        leg_ids_to_retrieve: list[str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Dispatch concurrent retrieval for specified legs (or all if None).

        Returns:
            Dict mapping leg_id -> retrieval result dict:
            {
                "dense_results": list[tuple[str, float]],
                "sparse_results": list[tuple[str, float]],
                "latency_ms": float,
                "status": str ("completed" | "reused_cache" | "cancelled" | "error"),
            }
        """
        targets = [
            leg for leg in legs if leg_ids_to_retrieve is None or leg.leg_id in leg_ids_to_retrieve
        ]

        if not targets:
            return {}

        logger.debug(
            f"Dispatching parallel retrieval for {len(targets)} legs: "
            f"{[leg.leg_id for leg in targets]}"
        )

        async def _retrieve_single(leg: Leg) -> tuple[str, dict[str, Any]]:
            try:
                res = await self.retriever.retrieve_leg(
                    query=leg.text,
                    deadline_override_ms=self.deadline_ms,
                )
                return leg.leg_id, res
            except Exception as e:  # noqa: BLE001
                logger.error(f"Retrieval failed for leg {leg.leg_id} ('{leg.text}'): {e}")
                return leg.leg_id, {
                    "dense_results": [],
                    "sparse_results": [],
                    "latency_ms": 0.0,
                    "status": "error",
                }

        tasks = [_retrieve_single(leg) for leg in targets]
        results_list = await asyncio.gather(*tasks)

        dispatched_results: dict[str, dict[str, Any]] = {}
        for leg_id, res in results_list:
            dispatched_results[leg_id] = res
            self.turn_results[leg_id] = res

        return dispatched_results

    def get_results(self, leg_id: str) -> dict[str, Any] | None:
        """Get retrieval results for a leg from the current turn."""
        return self.turn_results.get(leg_id)

    def get_all_results(self) -> dict[str, dict[str, Any]]:
        """Get all retrieval results collected during the current turn."""
        return self.turn_results
