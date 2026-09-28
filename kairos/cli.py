"""Kairos CLI entrypoint (SPEC §9.6a)."""
from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(prog="kairos", description="Kairos Streaming Live RAG Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # index command
    index_parser = subparsers.add_parser("index", help="Build or verify corpus index")
    index_parser.add_argument("--corpus", default="data/corpus", help="Path to corpus directory")

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
        print(f"Indexing corpus from {args.corpus}...")
    elif args.command == "replay":
        print(f"Replaying split '{args.split}' to output directory '{args.out}'...")


if __name__ == "__main__":
    main()
