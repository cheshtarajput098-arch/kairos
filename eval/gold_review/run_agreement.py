"""Compute Inter-Annotator Agreement between team members' reviews (SPEC §9.6)."""
from pathlib import Path

from eval.iaa import evaluate_iaa_sample


def main() -> None:
    sample_a = Path("eval/gold_review/annotator_cheshta_sample.jsonl")
    sample_b = Path("eval/gold_review/annotator_chiranjeevi_sample.jsonl")
    
    if not sample_a.exists() or not sample_b.exists():
        print("Annotator sample files not found in eval/gold_review/")
        return
        
    res = evaluate_iaa_sample(sample_a, sample_b)
    print("=" * 60)
    print("INTER-ANNOTATOR AGREEMENT REPORT (SPEC §9.6)")
    print("=" * 60)
    print(f"Sample size (n):                {res.get('n_samples', 0)} turns")
    print(f"Retrieval need agreement (p_o): {res.get('retrieval_required_po', 0.0) * 100:.1f}%")
    print(f"Retrieval need Cohen's Kappa:   {res.get('retrieval_required_kappa', 0.0):.4f}")
    print(f"Sub-intent count agreement:     {res.get('subintent_count_po', 0.0) * 100:.1f}%")
    print(f"Sub-intent count Cohen's Kappa: {res.get('subintent_count_kappa', 0.0):.4f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
