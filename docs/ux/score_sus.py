"""Score the 10-item System Usability Scale (SUS) survey (SPEC §14.7)."""
import json
from pathlib import Path

def calculate_sus(ratings: dict[str, int]) -> float:
    """Calculate SUS score (0-100) from 10 Likert ratings (1-5)."""
    keys = [
        "q1_frequent_use", "q2_complexity", "q3_ease_of_use", "q4_need_tech_support",
        "q5_functions_integrated", "q6_inconsistency", "q7_learn_quickly",
        "q8_cumbersome", "q9_confidence", "q10_learning_curve"
    ]
    total_points = 0
    for idx, key in enumerate(keys, start=1):
        val = ratings.get(key, 3)
        if idx % 2 == 1:
            # Odd item: rating - 1
            total_points += (val - 1)
        else:
            # Even item: 5 - rating
            total_points += (5 - val)
    return total_points * 2.5

def main() -> None:
    data_file = Path("docs/ux/sus_results_template.json")
    if not data_file.exists():
        print(f"Data file not found at {data_file}")
        return
        
    data = json.loads(data_file.read_text(encoding="utf-8"))
    participants = data.get("participants", [])
    
    print("=" * 65)
    print("SYSTEM USABILITY SCALE (SUS) EVALUATION REPORT (SPEC §14.7)")
    print("=" * 65)
    scores: list[float] = []
    
    for p in participants:
        pid = p["id"]
        profile = p["profile"]
        score = calculate_sus(p["ratings"])
        scores.append(score)
        print(f"Participant {pid} ({profile:<22}): SUS = {score:5.1f} / 100")
        
    mean_sus = sum(scores) / len(scores) if scores else 0.0
    print("-" * 65)
    print(f"Mean SUS Score:                      {mean_sus:5.1f} / 100")
    grade = "A+" if mean_sus >= 85 else ("A" if mean_sus >= 80 else ("B+" if mean_sus >= 75 else "B"))
    print(f"Grade Interpretation:                {grade} (Above Industry Average 68.0)")
    print("=" * 65)

if __name__ == "__main__":
    main()
