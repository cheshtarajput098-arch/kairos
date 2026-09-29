"""Inter-Annotator Agreement (IAA) calculation tool (SPEC §9.6).

Computes percent agreement and Cohen's Kappa on sub-intent labeling across
two independent annotators on a sample of turns.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def compute_cohens_kappa(labels_a: list[str], labels_b: list[str]) -> tuple[float, float]:
    """Compute observed agreement (p_o) and Cohen's Kappa (kappa) between two label sequences."""
    if len(labels_a) != len(labels_b):
        raise ValueError(f"Length mismatch: {len(labels_a)} vs {len(labels_b)}")

    n = len(labels_a)
    if n == 0:
        return 1.0, 1.0

    p_o = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n

    all_categories = sorted(set(labels_a).union(set(labels_b)))
    p_e = 0.0
    for cat in all_categories:
        count_a = sum(1 for a in labels_a if a == cat)
        count_b = sum(1 for b in labels_b if b == cat)
        p_e += (count_a / n) * (count_b / n)

    if p_e >= 1.0:
        kappa = 1.0
    else:
        kappa = (p_o - p_e) / (1.0 - p_e)

    return round(p_o, 4), round(kappa, 4)


def evaluate_iaa_sample(
    sample_file_a: Path,
    sample_file_b: Path,
) -> dict[str, Any]:
    """Evaluate agreement on turn classification and sub-intent counts from two annotator jsonl files."""
    records_a = [json.loads(line) for line in sample_file_a.read_text(encoding="utf-8").splitlines() if line.strip()]
    records_b = [json.loads(line) for line in sample_file_b.read_text(encoding="utf-8").splitlines() if line.strip()]

    turns_a = {r["turn_id"]: r for r in records_a}
    turns_b = {r["turn_id"]: r for r in records_b}

    common_ids = sorted(set(turns_a.keys()).intersection(set(turns_b.keys())))
    if not common_ids:
        return {"n": 0, "percent_agreement": 1.0, "cohens_kappa": 1.0, "status": "no_common_turns"}

    type_labels_a = [str(turns_a[tid].get("retrieval_required", True)) for tid in common_ids]
    type_labels_b = [str(turns_b[tid].get("retrieval_required", True)) for tid in common_ids]

    po_retrieval, kappa_retrieval = compute_cohens_kappa(type_labels_a, type_labels_b)

    # Sub-intent count agreement
    counts_a = [str(len(turns_a[tid].get("sub_intents", []))) for tid in common_ids]
    counts_b = [str(len(turns_b[tid].get("sub_intents", []))) for tid in common_ids]
    po_counts, kappa_counts = compute_cohens_kappa(counts_a, counts_b)

    return {
        "n_samples": len(common_ids),
        "retrieval_required_po": po_retrieval,
        "retrieval_required_kappa": kappa_retrieval,
        "subintent_count_po": po_counts,
        "subintent_count_kappa": kappa_counts,
        "overall_kappa": round((kappa_retrieval + kappa_counts) / 2.0, 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute IAA across two annotators.")
    parser.add_argument("--annotator-a", type=Path, required=True)
    parser.add_argument("--annotator-b", type=Path, required=True)
    args = parser.parse_args()

    results = evaluate_iaa_sample(args.annotator_a, args.annotator_b)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
