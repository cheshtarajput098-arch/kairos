"""Reversible speculation manager with per-turn budget (SPEC §4.5)."""

from __future__ import annotations

import asyncio

from kairos.retrieve.cache import hash_query
from kairos.schemas import RetrievalEvent


class SpeculationManager:
    def __init__(self, max_speculative: int = 3):
        self.max_speculative = max_speculative
        self.speculative_count = 0
        self.active_tasks: dict[str, asyncio.Task[object]] = {}
        self.active_entities: dict[str, set[str]] = {}
        self.events_log: list[RetrievalEvent] = []

    def reset_turn(self) -> None:
        """Reset speculative budget and active tasks for a new turn."""
        self.cancel_all()
        self.speculative_count = 0
        self.active_tasks.clear()
        self.active_entities.clear()
        self.events_log.clear()

    def can_speculate(self) -> bool:
        """Check if speculative budget has not been exhausted."""
        return self.speculative_count < self.max_speculative

    def register_task(
        self,
        query: str,
        task: asyncio.Task[object],
        entities: set[str],
        leg_id: str,
        t: float,
    ) -> str:
        """Register a new speculative retrieval task."""
        self.speculative_count += 1
        q_hash = hash_query(query)
        self.active_tasks[q_hash] = task
        self.active_entities[q_hash] = entities

        self.events_log.append(
            RetrievalEvent(
                timestamp_s=t,
                query=query,
                trigger="provisional",
                event="retrieval_started",
                leg_id=leg_id,
                latency_ms=0.0,
            )
        )
        return q_hash

    def check_and_cancel_on_revision(self, current_entities: set[str], t: float) -> list[str]:
        """Cancel speculative tasks whose entities are no longer present."""
        cancelled_hashes: list[str] = []
        for q_hash, entities in list(self.active_entities.items()):
            # If any entity used for this search disappeared from current transcript
            if entities and (entities - current_entities):
                task = self.active_tasks.get(q_hash)
                if task and not task.done():
                    task.cancel()
                    cancelled_hashes.append(q_hash)
                    self.events_log.append(
                        RetrievalEvent(
                            timestamp_s=t,
                            query=f"query_hash:{q_hash}",
                            trigger="provisional",
                            event="retrieval_cancelled",
                            leg_id=q_hash[:4],
                            latency_ms=0.0,
                        )
                    )
        for h in cancelled_hashes:
            self.active_tasks.pop(h, None)
            self.active_entities.pop(h, None)
        return cancelled_hashes

    def cancel_all(self) -> None:
        """Cancel all in-flight speculative tasks."""
        for task in self.active_tasks.values():
            if not task.done():
                task.cancel()
        self.active_tasks.clear()
        self.active_entities.clear()
