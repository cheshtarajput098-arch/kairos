"""Kairos CLI entrypoint (SPEC §9.6a)."""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

from kairos.fuse.dedupe import deduplicate_and_rank
from kairos.fuse.rrf import reciprocal_rank_fusion
from kairos.index.store import IndexStore
from kairos.retrieve.hybrid import HybridRetriever


def run_index(corpus_dir: str, index_dir: str = "index") -> None:
    start_time = time.perf_counter()
    print(f"Indexing corpus from '{corpus_dir}' into '{index_dir}'...")
    store = IndexStore(index_dir=Path(index_dir), corpus_dir=Path(corpus_dir))
    store.build()
    elapsed = time.perf_counter() - start_time
    print(f"Index built successfully in {elapsed:.2f}s! Total chunks indexed: {len(store.chunks_map)}")


def run_query(query: str, index_dir: str = "index") -> None:
    store = IndexStore(index_dir=Path(index_dir))
    store.load()
    retriever = HybridRetriever(store)

    start_time = time.perf_counter()
    retrieval_res = asyncio.run(retriever.retrieve_leg(query))
    dense_res: list[tuple[str, float]] = retrieval_res["dense_results"]  # type: ignore[assignment]
    sparse_res: list[tuple[str, float]] = retrieval_res["sparse_results"]  # type: ignore[assignment]

    fused = reciprocal_rank_fusion([dense_res, sparse_res], k=60, top_n=10)
    top_chunks = deduplicate_and_rank(fused, store.chunks_map, top_n=5)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    print(f"\nQuery: '{query}'")
    print(f"Hybrid retrieval + RRF completed in {elapsed_ms:.2f} ms")
    print("-" * 60)
    for rank, (chunk_id, score) in enumerate(top_chunks, start=1):
        chunk = store.get_chunk(chunk_id)
        snippet = chunk.text.replace("\n", " ")[:120] if chunk else ""
        print(f"[{rank}] [{chunk_id}] (score: {score:.4f}): {snippet}...")
    print("-" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(prog="kairos", description="Kairos Streaming Live RAG Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # index command
    index_parser = subparsers.add_parser("index", help="Build or verify corpus index")
    index_parser.add_argument("--corpus", default="data/corpus", help="Path to corpus directory")
    index_parser.add_argument("--index-dir", default="index", help="Path to index storage directory")

    # query command
    query_parser = subparsers.add_parser("query", help="Run hybrid search query against corpus")
    query_parser.add_argument("--q", required=True, help="Query string")
    query_parser.add_argument("--index-dir", default="index", help="Path to index storage directory")

    # replay command
    replay_parser = subparsers.add_parser("replay", help="Replay transcript evaluation split")
    replay_parser.add_argument("--split", default="dev", help="Replay split (demo, dev, test)")
    replay_parser.add_argument("--transcripts", help="Custom path to transcript JSON/JSONL")
    replay_parser.add_argument("--out", default="runs/cli_replay", help="Output directory")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "index":
        run_index(args.corpus, args.index_dir)
    elif args.command == "query":
        run_query(args.q, args.index_dir)
    elif args.command == "replay":
        print(f"Replaying split '{args.split}' to output directory '{args.out}'...")


if __name__ == "__main__":
    main()
