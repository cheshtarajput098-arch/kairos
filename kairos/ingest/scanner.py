"""Prompt injection & adversarial pattern detection at ingest (SPEC §13.2, §13.4).

Calculates a heuristic risk score and flags suspicious patterns without deleting chunks.
"""

from __future__ import annotations

import re

INJECTION_PATTERNS = [
    re.compile(
        r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts)",
        re.IGNORECASE,
    ),
    re.compile(r"(disregard|forget)\s+(all\s+)?(previous|prior)\s+rules", re.IGNORECASE),
    re.compile(
        r"you\s+are\s+now\s+(an?\s+)?(unrestricted|jailbroken|developer|admin)", re.IGNORECASE
    ),
    re.compile(r"<\|im_start\|>|<\|im_end\|>|\[SYSTEM\]|\[ASSISTANT\]", re.IGNORECASE),
    re.compile(
        r"(reveal|print|dump|show)\s+(your\s+)?(system\s+prompt|initial\s+prompt)", re.IGNORECASE
    ),
    re.compile(r"do\s+not\s+follow\s+any\s+policy", re.IGNORECASE),
]

ZERO_WIDTH_PATTERN = re.compile(r"[\u200B-\u200D\uFEFF]")


def scan_for_injection(raw_text: str) -> tuple[bool, float, str]:
    """Scan text for injection patterns and suspicious hidden characters.

    Returns:
        (is_flagged, score, reason)
    """
    if not raw_text:
        return False, 0.0, "clean"

    score = 0.0
    matched_reasons = []

    # Check for zero-width characters in raw input before normalization
    if ZERO_WIDTH_PATTERN.search(raw_text):
        score += 0.4
        matched_reasons.append("zero_width_chars_present")

    for pattern in INJECTION_PATTERNS:
        if pattern.search(raw_text):
            score += 0.6
            matched_reasons.append(f"matched:{pattern.pattern[:30]}")

    is_flagged = score >= 0.5
    reason = "; ".join(matched_reasons) if matched_reasons else "clean"
    return is_flagged, min(score, 1.0), reason
