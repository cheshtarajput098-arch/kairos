"""Kairos CLI entrypoint (SPEC §9.6a)."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from kairos.controller.features import ControllerFeatureExtractor
from kairos.controller.rules import RuleBasedController
from kairos.controller.speculation import SpeculationManager
from kairos.fuse.dedupe import deduplicate_and_rank
from kairos.fuse.rrf import reciprocal_rank_fusion
from kairos.index.store import IndexStore
from kairos.retrieve.hybrid import HybridRetriever
from kairos.stream.replay import ReplayReader


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


def run_replay(split: str, transcripts_path: str | None = None, out_dir: str = "runs/cli_replay") -> None:
    input_file = Path(transcripts_path) if transcripts_path else Path("data") / "replay" / split / "scenarios.jsonl"
    if not input_file.exists():
        print(f"Error: Transcript file not found at {input_file}")
        sys.exit(1)

    print(f"=== Replaying '{split}' split from {input_file} ===")
    readers = ReplayReader.from_jsonl(input_file, instant=True)
    store = IndexStore()
    try:
        store.load()
    except Exception:  # noqa: BLE001
        store.build()

    feature_extractor = ControllerFeatureExtractor(store.sparse_index)
    controller = RuleBasedController()
    speculation_mgr = SpeculationManager()

    current_session_id: str | None = None
    has_prior_answer = False
    turn_results = []

    for reader in readers:
        session_id = reader.transcript.session_id
        if session_id != current_session_id:
            current_session_id = session_id
            has_prior_answer = False

        t_id = reader.transcript.turn_id
        u_end = reader.transcript.utterance_end
        feature_extractor.reset_turn()
        speculation_mgr.reset_turn()

        first_retrieval_t: float | None = None
        turn_decisions: list[str] = []

        async def _process_turn(r_reader: ReplayReader, r_decs: list[str]) -> None:
            nonlocal first_retrieval_t, has_prior_answer
            async for ev in r_reader.stream_events():
                if ev.event_type == "utterance_end":
                    break
                features = feature_extractor.compute_features(ev.prefix, has_prior_answer=has_prior_answer)
                dec = controller.decide(features, ev.t, has_prior_answer=has_prior_answer)
                r_decs.append(f"t={ev.t:.1f}s:{dec.decision}({dec.reason})")

                if dec.decision == "RETRIEVE" and first_retrieval_t is None:
                    first_retrieval_t = ev.t

            # Mark that this session now has an answer unless it was pure presentation
            if r_reader.transcript.turn_type != "presentation_only":
                has_prior_answer = True

        asyncio.run(_process_turn(reader, turn_decisions))

        lead_time = (u_end - first_retrieval_t) if first_retrieval_t is not None else 0.0
        turn_results.append({
            "turn_id": t_id,
            "type": reader.transcript.turn_type,
            "utterance_end": u_end,
            "first_retrieval_t": first_retrieval_t,
            "lead_time": round(lead_time, 2),
            "decisions": turn_decisions,
        })

    print(f"\nReplayed {len(turn_results)} turns successfully:")
    print(f"{'Turn ID':<14} | {'Type':<18} | {'Utterance End':<13} | {'First Retrieve':<14} | {'Lead Time':<9}")
    print("-" * 78)
    for r in turn_results:
        f_ret = f"{r['first_retrieval_t']:.1f}s" if r['first_retrieval_t'] is not None else "None"
        decs: list[str] = r["decisions"]  # type: ignore[assignment]
        print(f"{r['turn_id']:<14} | {r['type']:<18} | {r['utterance_end']:<13.1f} | {f_ret:<14} | {r['lead_time']:<8.2f}s")
        print(f"   Decisions: {' -> '.join(decs)}")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / "replay_summary.json", "w", encoding="utf-8") as f:
        json.dump(turn_results, f, indent=2)
    print(f"\nSaved replay report to {out_path / 'replay_summary.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="kairos", description="Kairos Streaming Live RAG Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # index command
    index_parser = subparsers.add_parser("index", help="Build or verify corpus index")
    index_parser.add_argument("--corpus", default="data/corpus", help="Path to corpus directory")
    index_parser.add_argument("--index-dir", default="index", help="Path to index storage directory")

    # query command
    query_parser = subparsers.add_parser("query", help="Run hybrid search query against corpus")
    query_parser.add_argument("query_pos", nargs="?", default=None, help="Query string")
    query_parser.add_argument("--q", default=None, help="Query string flag")
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
        q_text = args.query_pos or args.q
        if not q_text:
            print("Error: query text is required")
            sys.exit(1)
        run_query(q_text, args.index_dir)
    elif args.command == "replay":
        run_replay(args.split, args.transcripts, args.out)


if __name__ == "__main__":
    main()
