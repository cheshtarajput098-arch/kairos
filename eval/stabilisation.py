"""Stabilisation ceiling analysis per arXiv:2606.20113 (SPEC §9.4).

Computes prefix-level stabilisation metrics:
- t_sc: first prefix from which top-1 chunk equals full-query top-1
- t_suf: first prefix whose top-k contains gold answer chunk
- phi: t* / duration (fraction of utterance elapsed before retrieval sufficiency)
- volatility V: frequency of top-1 ranking shifts across prefix progression
- hidden latency bound H: min(L, max(0, (duration - t*) / delta))
- trigger gap: controller trigger point vs t_suf
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from kairos.index.store import IndexStore

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "runs" / "eval" / "stabilisation.json"


def compute_turn_stabilisation(
    scenario: dict[str, Any],
    gold: dict[str, Any],
    store: IndexStore,
    controller_trigger_t: float | None = None,
    measured_retrieval_latency_s: float = 0.040,
    cadence_delta: float = 1.0,
) -> dict[str, Any] | None:
    """Compute stabilisation metrics for a single turn."""
    retrieval_required = gold.get("retrieval_required", True)
    if not retrieval_required:
        return None

    chunks = scenario.get("chunks", [])
    if not chunks:
        return None

    utterance_end = float(scenario.get("utterance_end", chunks[-1].get("t", 0.0) + 0.5))
    if utterance_end <= 0.0:
        utterance_end = 1.0

    # Collect all gold chunk IDs for this turn
    gold_chunks: set[str] = set()
    for ids in gold.get("answer_chunks", {}).values():
        gold_chunks.update(ids)

    # Prefix progression
    prefix_texts: list[str] = []
    prefix_times: list[float] = []
    current_text = ""

    for ch in chunks:
        current_text = (current_text + " " + ch.get("text", "")).strip()
        prefix_texts.append(current_text)
        prefix_times.append(float(ch.get("t", 0.0)))

    n_prefixes = len(prefix_texts)
    if n_prefixes == 0:
        return None

    # Full query top-1 chunk
    full_query = prefix_texts[-1]
    full_search = store.dense_index.search(full_query, top_k=5)
    full_top1 = full_search[0][0] if full_search else ""

    # Evaluate each prefix
    top1_per_prefix: list[str] = []
    contains_gold_per_prefix: list[bool] = []

    for p_text in prefix_texts:
        res = store.dense_index.search(p_text, top_k=5)
        top1 = res[0][0] if res else ""
        top1_per_prefix.append(top1)
        res_ids = {cid for cid, _ in res}
        contains_gold = bool(res_ids.intersection(gold_chunks)) if gold_chunks else True
        contains_gold_per_prefix.append(contains_gold)

    # 1. t_sc: first prefix from which top-1 equals full_top1 for all remaining prefixes
    t_sc_idx = n_prefixes - 1
    for i in range(n_prefixes):
        if all(top1_per_prefix[j] == full_top1 for j in range(i, n_prefixes)):
            t_sc_idx = i
            break
    t_sc = prefix_times[t_sc_idx]

    # 2. t_suf: first prefix whose top-k contains a gold answer chunk
    t_suf_idx = n_prefixes - 1
    found_suf = False
    for i in range(n_prefixes):
        if contains_gold_per_prefix[i]:
            t_suf_idx = i
            found_suf = True
            break
    t_suf = prefix_times[t_suf_idx] if found_suf else t_sc

    # 3. t*: sufficiency trigger target (t_suf if gold exists else t_sc)
    t_star = t_suf
    phi = t_star / utterance_end

    # 4. Volatility V: top-1 changes divided by (n_prefixes - 1)
    shifts = sum(
        1 for i in range(n_prefixes - 1) if top1_per_prefix[i] != top1_per_prefix[i + 1]
    )
    volatility = shifts / max(1, n_prefixes - 1)

    # 5. Hidden latency bound H = min(L, max(0, (utterance_end - t*) / delta))
    lead_time_potential = max(0.0, (utterance_end - t_star) / cadence_delta)
    h_bound = min(measured_retrieval_latency_s, lead_time_potential)
    fraction_latency_hidden = (h_bound / measured_retrieval_latency_s) if measured_retrieval_latency_s > 0 else 1.0

    # 6. Controller trigger gap
    gap_s: float | None = None
    if controller_trigger_t is not None:
        gap_s = round(controller_trigger_t - t_suf, 3)

    return {
        "turn_id": scenario["turn_id"],
        "utterance_end_s": round(utterance_end, 3),
        "n_chunks": n_prefixes,
        "t_sc_s": round(t_sc, 3),
        "t_suf_s": round(t_suf, 3),
        "t_star_s": round(t_star, 3),
        "phi": round(phi, 3),
        "volatility": round(volatility, 3),
        "hidden_latency_s": round(h_bound, 4),
        "fraction_latency_hidden": round(fraction_latency_hidden, 3),
        "controller_trigger_s": round(controller_trigger_t, 3) if controller_trigger_t is not None else None,
        "trigger_gap_s": gap_s,
    }


def run_stabilisation_suite(
    split: str = "test",
    out_file: Path | None = None,
    store: IndexStore | None = None,
    turn_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute stabilisation ceiling evaluation over all turns in split."""
    scenarios_path = ROOT / "data" / "replay" / split / "scenarios.jsonl"
    gold_path = ROOT / "data" / "replay" / split / "gold.jsonl"

    scenarios = [json.loads(line) for line in scenarios_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    gold_list = [json.loads(line) for line in gold_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    gold_by_turn = {g["turn_id"]: g for g in gold_list}

    # Map controller trigger from turn_records
    trigger_map: dict[str, float] = {}
    if turn_records is None:
        rec_path = ROOT / "runs" / "eval" / "turn_records.json"
        if rec_path.exists():
            turn_records = json.loads(rec_path.read_text(encoding="utf-8"))
        else:
            turn_records = []

    for tr in turn_records:
        if tr.get("first_retrieval_t") is not None:
            trigger_map[tr["turn_id"]] = float(tr["first_retrieval_t"])

    if store is None:
        store = IndexStore()
        store.load()

    turn_metrics: list[dict[str, Any]] = []
    for sc in scenarios:
        tid = sc["turn_id"]
        gold = gold_by_turn.get(tid, {})
        trig_t = trigger_map.get(tid)
        res = compute_turn_stabilisation(sc, gold, store, controller_trigger_t=trig_t)
        if res is not None:
            turn_metrics.append(res)

    # Compute aggregate distributions
    n = len(turn_metrics)
    if n == 0:
        return {"error": "No retrieval turns found"}

    phis = [m["phi"] for m in turn_metrics]
    vols = [m["volatility"] for m in turn_metrics]
    h_fracs = [m["fraction_latency_hidden"] for m in turn_metrics]
    gaps = [m["trigger_gap_s"] for m in turn_metrics if m["trigger_gap_s"] is not None]

    sorted_gaps = sorted(gaps) if gaps else [0.0]
    n_gaps = len(sorted_gaps)

    gap_distribution = {
        "p25": round(sorted_gaps[int(0.25 * n_gaps)], 3),
        "p50_median": round(sorted_gaps[int(0.50 * n_gaps)], 3),
        "p75": round(sorted_gaps[int(0.75 * n_gaps)], 3),
        "mean": round(sum(sorted_gaps) / max(1, n_gaps), 3),
        "min": round(sorted_gaps[0], 3),
        "max": round(sorted_gaps[-1], 3),
    }

    aggregates = {
        "mean_phi": round(sum(phis) / n, 3),
        "median_phi": round(sorted(phis)[int(0.5 * n)], 3),
        "mean_volatility": round(sum(vols) / n, 3),
        "mean_latency_hidden_fraction": round(sum(h_fracs) / n, 3),
        "mean_trigger_gap_s": gap_distribution["mean"],
        "gap_distribution_s": gap_distribution,
        "n_retrieval_turns_evaluated": n,
        "methodology": "Galbraith (2026), 'When Does Streaming Tool Use Help?', arXiv:2606.20113",
    }

    output = {
        "split": split,
        "summary": aggregates,
        "per_turn": turn_metrics,
    }

    out_p = out_file or DEFAULT_OUT
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stabilisation ceiling analysis (arXiv:2606.20113)")
    parser.add_argument("--split", default="test", help="Replay split (dev | test)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output JSON path")
    args = parser.parse_args()

    results = run_stabilisation_suite(args.split, args.out)
    print("Stabilisation analysis completed successfully.")
    summary = results.get("summary", {})
    print(f"  Mean phi (t*/duration): {summary.get('mean_phi')}")
    print(f"  Mean volatility V: {summary.get('mean_volatility')}")
    print(f"  Mean latency hidden fraction: {summary.get('mean_latency_hidden_fraction'):.1%}")
    print(f"  Trigger vs t_suf median gap: {summary.get('gap_distribution_s', {}).get('p50_median')} s")
    print(f"Results saved to {args.out}")


if __name__ == "__main__":
    main()
