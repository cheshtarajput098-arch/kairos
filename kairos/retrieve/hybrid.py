"""Async concurrent hybrid retrieval with deadline cancellation (SPEC §6.1)."""

from __future__ import annotations

import asyncio
import time

from kairos.index.store import IndexStore
from kairos.retrieve.cache import RetrievalCache


class HybridRetriever:
    def __init__(
        self,
        index_store: IndexStore,
        cache: RetrievalCache | None = None,
        deadline_ms: int = 400,
        top_k_dense: int = 20,
        top_k_sparse: int = 20,
    ):
        self.index_store = index_store
        self.cache = cache or RetrievalCache()
        self.deadline_ms = deadline_ms
        self.top_k_dense = top_k_dense
        self.top_k_sparse = top_k_sparse

    async def retrieve_leg(
        self,
        query: str,
        deadline_override_ms: int | None = None,
    ) -> dict[str, object]:
        """Perform concurrent dense and sparse retrieval for a query under a strict deadline.

        Returns:
            Dict containing dense_results, sparse_results, latency_ms, status (completed|cancelled|reused_cache)
        """
        cached = self.cache.get(query)
        if cached is not None:
            return {
                "dense_results": cached["dense_results"],
                "sparse_results": cached["sparse_results"],
                "latency_ms": 0.0,
                "status": "reused_cache",
            }

        start_time = time.perf_counter()
        deadline_s = (deadline_override_ms or self.deadline_ms) / 1000.0

        async def _run_dense() -> list[tuple[str, float]]:
            return await asyncio.to_thread(
                self.index_store.dense_index.search, query, self.top_k_dense
            )

        async def _run_sparse() -> list[tuple[str, float]]:
            return await asyncio.to_thread(
                self.index_store.sparse_index.search, query, self.top_k_sparse
            )

        dense_task = asyncio.create_task(_run_dense())
        sparse_task = asyncio.create_task(_run_sparse())

        try:
            dense_res, sparse_res = await asyncio.wait_for(
                asyncio.gather(dense_task, sparse_task),
                timeout=deadline_s,
            )
            status = "completed"
        except TimeoutError:
            # Cancel overruns immediately
            dense_task.cancel()
            sparse_task.cancel()
            # Return any partial completed leg if available, else empty
            dense_res = (
                dense_task.result()
                if dense_task.done() and not dense_task.cancelled() and not dense_task.exception()
                else []
            )
            sparse_res = (
                sparse_task.result()
                if sparse_task.done()
                and not sparse_task.cancelled()
                and not sparse_task.exception()
                else []
            )
            status = "cancelled"

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = {
            "dense_results": dense_res,
            "sparse_results": sparse_res,
            "latency_ms": round(elapsed_ms, 2),
            "status": status,
        }

        if status == "completed":
            self.cache.put(query, result)

        return result
