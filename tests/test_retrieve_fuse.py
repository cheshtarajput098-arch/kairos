"""Unit tests for hybrid retrieval, deadline cancellation, caching, and RRF fusion."""

import asyncio
from pathlib import Path

import pytest

from kairos.fuse.dedupe import deduplicate_and_rank
from kairos.fuse.rrf import reciprocal_rank_fusion
from kairos.index.store import IndexStore
from kairos.retrieve.cache import RetrievalCache
from kairos.retrieve.hybrid import HybridRetriever


def test_rrf_scoring_toy_example() -> None:
    # Ranked list 1 (dense): A (rank 1), B (rank 2), C (rank 3)
    # Ranked list 2 (sparse): B (rank 1), A (rank 2), D (rank 3)
    dense_list = [("Doc_A§1", 0.9), ("Doc_B§1", 0.8), ("Doc_C§1", 0.7)]
    sparse_list = [("Doc_B§1", 12.0), ("Doc_A§1", 10.0), ("Doc_D§1", 8.0)]

    k = 60
    fused = reciprocal_rank_fusion([dense_list, sparse_list], k=k, top_n=5)
    fused_dict = dict(fused)

    # For A: 1/(60+1) + 1/(60+2) = 1/61 + 1/62
    expected_a = (1.0 / 61) + (1.0 / 62)
    # For B: 1/(60+2) + 1/(60+1) = 1/62 + 1/61
    expected_b = (1.0 / 62) + (1.0 / 61)

    assert abs(fused_dict["Doc_A§1"] - expected_a) < 1e-6
    assert abs(fused_dict["Doc_B§1"] - expected_b) < 1e-6
    # Both A and B rank higher than C and D
    assert fused_dict["Doc_A§1"] > fused_dict["Doc_C§1"]
    assert fused_dict["Doc_B§1"] > fused_dict["Doc_D§1"]


def test_chunk_ids_survive_retrieval_and_fusion_byte_for_byte(tmp_path: Path) -> None:
    store = IndexStore(index_dir=tmp_path / "index", corpus_dir=Path("data/corpus"))
    store.build()

    retriever = HybridRetriever(store)
    res = asyncio.run(retriever.retrieve_leg("cancellation policy refunds"))

    dense_res = res["dense_results"]
    sparse_res = res["sparse_results"]
    fused = reciprocal_rank_fusion([dense_res, sparse_res], k=60, top_n=5)
    top_chunks = deduplicate_and_rank(fused, store.chunks_map, top_n=3)

    assert len(top_chunks) > 0
    for chunk_id, _ in top_chunks:
        assert chunk_id in store.chunks_map
        # Byte-for-byte check: ID must match exactly
        assert store.get_chunk(chunk_id).chunk_id == chunk_id


def test_retrieval_cache_hit_and_reused_status(tmp_path: Path) -> None:
    store = IndexStore(index_dir=tmp_path / "index", corpus_dir=Path("data/corpus"))
    store.build()

    cache = RetrievalCache()
    retriever = HybridRetriever(store, cache=cache)

    query = "workshop venues in Pune"
    res1 = asyncio.run(retriever.retrieve_leg(query))
    assert res1["status"] == "completed"

    res2 = asyncio.run(retriever.retrieve_leg(query))
    assert res2["status"] == "reused_cache"
    assert res2["dense_results"] == res1["dense_results"]


def test_deadline_cancellation_under_strict_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = IndexStore(index_dir=tmp_path / "index", corpus_dir=Path("data/corpus"))
    store.build()

    # Simulate an artificially slow dense search
    def slow_search(query: str, top_k: int = 20):
        import time

        time.sleep(0.3)
        return []

    monkeypatch.setattr(store.dense_index, "search", slow_search)

    # Set 50ms deadline, so 300ms search times out and triggers cancellation
    retriever = HybridRetriever(store, deadline_ms=50)
    res = asyncio.run(retriever.retrieve_leg("test query"))
    assert res["status"] == "cancelled"
