"""Import external test questions submitted by classmates (SPEC §9.6).

Reads text submission files in eval/external_turns/submissions/ and converts them
into canonical ReplayTranscript and GoldLabel records.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from kairos.schemas import GoldLabel, ReplayChunk, ReplayTranscript

_TYPE_MAP = {
    "1": ("compound", True),
    "2": ("late_constraint", True),
    "3": ("presentation_only", False),
    "4": ("single", True),
    "5": ("out_of_corpus", False),
    "6": ("single", True),
    "7": ("compound", True),
    "8": ("single", True),
}

def import_submission_file(file_path: Path, session_prefix: str) -> list[tuple[ReplayTranscript, GoldLabel]]:
    """Parse one classmate submission file into transcripts and gold labels."""
    lines = file_path.read_text(encoding="utf-8").splitlines()
    results: list[tuple[ReplayTranscript, GoldLabel]] = []
    
    turn_idx = 1
    for line in lines:
        line = line.strip()
        m = re.match(r"^(\d+)\s*:\s*(.+)$", line)
        if not m:
            continue
        q_num, text = m.group(1), m.group(2).strip()
        turn_type, ret_req = _TYPE_MAP.get(q_num, ("single", True))
        turn_id = f"{session_prefix}-t{turn_idx}"
        
        # Split into simulated speech chunks (words grouped by 3)
        words = text.split()
        chunks: list[ReplayChunk] = []
        t = 0.0
        for i in range(0, len(words), 3):
            chunk_words = " ".join(words[i:i+3])
            chunks.append(ReplayChunk(t=round(t, 2), text=chunk_words))
            t += 0.8
        u_end = round(t + 0.2, 2)
        
        transcript = ReplayTranscript(
            session_id=session_prefix,
            turn_id=turn_id,
            turn_type=turn_type,
            chunks=chunks,
            utterance_end=u_end,
        )
        
        gold = GoldLabel(
            turn_id=turn_id,
            retrieval_required=ret_req,
            sub_intents=[text],
            answer_chunks={text: []},
            source="human_external",
            review_status="unreviewed",
        )
        results.append((transcript, gold))
        turn_idx += 1
        
    return results

def main() -> None:
    subs_dir = Path("eval/external_turns/submissions")
    subs_dir.mkdir(parents=True, exist_ok=True)
    
    submission_files = list(subs_dir.glob("*.txt"))
    if not submission_files:
        print(f"No submission files found in {subs_dir}. Place classmate .txt files there.")
        return
        
    all_transcripts: list[dict] = []
    all_golds: list[dict] = []
    
    for idx, sf in enumerate(submission_files, start=1):
        prefix = f"ext-s{idx:02d}"
        pairs = import_submission_file(sf, prefix)
        for t, g in pairs:
            all_transcripts.append(t.model_dump())
            all_golds.append(g.model_dump())
            
    out_t = Path("eval/external_turns/imported_transcripts.jsonl")
    out_g = Path("eval/external_turns/imported_gold.jsonl")
    
    out_t.write_text("\n".join(json.dumps(x) for x in all_transcripts) + "\n", encoding="utf-8")
    out_g.write_text("\n".join(json.dumps(x) for x in all_golds) + "\n", encoding="utf-8")
    
    print(f"Imported {len(all_transcripts)} turns across {len(submission_files)} classmate submissions.")
    print(f"Saved to {out_t} and {out_g}")

if __name__ == "__main__":
    main()
