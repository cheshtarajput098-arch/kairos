"""Inter-Rater Agreement & Fluency Benchmark Scoring (SPEC §6.2, §9.3 Ablation D).

Computes:
1. Mean fluency score for Speed 1 (extractive) vs Speed 2 (grounded rewrite).
2. Inter-rater absolute agreement percentage.
3. Within-1-point agreement percentage.
4. Cohen's Kappa for inter-annotator reliability.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RATINGS_FILE = ROOT / "eval" / "fluency" / "ratings.json"
RESULTS_FILE = ROOT / "runs" / "eval" / "fluency_results.json"


def compute_cohens_kappa(rater1: list[int], rater2: list[int]) -> float:
    """Compute Cohen's unweighted kappa between two raters on ordinal scale."""
    if len(rater1) != len(rater2) or not rater1:
        return 0.0

    n = len(rater1)
    # Observed agreement
    po = sum(1 for a, b in zip(rater1, rater2) if a == b) / n

    # Expected agreement
    categories = sorted(set(rater1).union(set(rater2)))
    pe = 0.0
    for cat in categories:
        p1 = sum(1 for a in rater1 if a == cat) / n
        p2 = sum(1 for b in rater2 if b == cat) / n
        pe += p1 * p2

    if pe >= 1.0:
        return 1.0
    return (po - pe) / (1.0 - pe)


def evaluate_fluency(ratings_path: Path | None = None) -> dict[str, Any]:
    """Score blind human ratings and unblind Speed 1 vs Speed 2 comparisons."""
    path = ratings_path or RATINGS_FILE
    if not path.exists():
        from eval.fluency.sample_answers import sample_and_create_ratings_sheet

        sample_and_create_ratings_sheet()

    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])

    speed1_scores: list[int] = []
    speed2_scores: list[int] = []

    rater1_all: list[int] = []
    rater2_all: list[int] = []

    for item in items:
        key_a = item["secret_key"]["A"]
        _key_b = item["secret_key"]["B"]

        r1_a = int(item["rater_1"]["score_A"])
        r1_b = int(item["rater_1"]["score_B"])
        r2_a = int(item["rater_2"]["score_A"])
        r2_b = int(item["rater_2"]["score_B"])

        rater1_all.extend([r1_a, r1_b])
        rater2_all.extend([r2_a, r2_b])

        # Attribute scores to respective methods
        if key_a == "speed_1_extractive":
            speed1_scores.extend([r1_a, r2_a])
            speed2_scores.extend([r1_b, r2_b])
        else:
            speed1_scores.extend([r1_b, r2_b])
            speed2_scores.extend([r1_a, r2_a])

    n_ratings = len(rater1_all)
    abs_agree = sum(1 for a, b in zip(rater1_all, rater2_all) if a == b)
    within_one = sum(1 for a, b in zip(rater1_all, rater2_all) if abs(a - b) <= 1)

    mean_s1 = sum(speed1_scores) / len(speed1_scores) if speed1_scores else 0.0
    mean_s2 = sum(speed2_scores) / len(speed2_scores) if speed2_scores else 0.0
    kappa = compute_cohens_kappa(rater1_all, rater2_all)

    results = {
        "n_samples": len(items),
        "total_judgments": n_ratings,
        "speed_1_extractive_mean": round(mean_s1, 2),
        "speed_2_rewrite_mean": round(mean_s2, 2),
        "fluency_delta": round(mean_s2 - mean_s1, 2),
        "inter_rater_agreement": {
            "absolute_agreement_pct": round((abs_agree / n_ratings) * 100.0, 1) if n_ratings else 0.0,
            "within_one_point_pct": round((within_one / n_ratings) * 100.0, 1) if n_ratings else 0.0,
            "cohens_kappa": round(kappa, 3),
        },
        "raters": [
            items[0]["rater_1"]["name"] if items else "Rater 1",
            items[0]["rater_2"]["name"] if items else "Rater 2",
        ],
    }

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Score fluency ratings")
    parser.add_argument("--ratings", type=Path, default=RATINGS_FILE, help="Path to ratings JSON")
    args = parser.parse_args()

    res = evaluate_fluency(args.ratings)
    print("\n" + "=" * 60)
    print("FLUENCY EVALUATION BENCHMARK (Ablation D)")
    print("=" * 60)
    print(f"Sample size: {res['n_samples']} turns ({res['total_judgments']} total blind ratings)")
    print(f"Speed 1 (Extractive) Mean: {res['speed_1_extractive_mean']} / 5.0")
    print(f"Speed 2 (Grounded Rewrite) Mean: {res['speed_2_rewrite_mean']} / 5.0")
    print(f"Improvement: +{res['fluency_delta']} points")
    print(f"Absolute Agreement: {res['inter_rater_agreement']['absolute_agreement_pct']}%")
    print(f"Within +/-1 Point: {res['inter_rater_agreement']['within_one_point_pct']}%")
    print(f"Cohen's Kappa: {res['inter_rater_agreement']['cohens_kappa']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
