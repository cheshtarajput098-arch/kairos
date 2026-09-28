"""Text normalization utilities (SPEC §13.2, §13.3).

Applies Unicode NFKC normalization and strips control and zero-width characters.
"""
from __future__ import annotations

import re
import unicodedata

# Zero-width spaces, joiners, non-joiners, BOM, and other invisible characters
ZERO_WIDTH_CHARS = re.compile(r"[\u200B-\u200D\uFEFF\u200E\u200F\u202A-\u202E]")
# ASCII control characters excluding standard whitespace (\t, \n, \r)
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def normalize_text(text: str) -> str:
    """Normalize text using Unicode NFKC and strip invisible/control characters."""
    if not text:
        return ""
    # Unicode NFKC normalization
    normalized = unicodedata.normalize("NFKC", text)
    # Strip zero-width and invisible formatting characters
    normalized = ZERO_WIDTH_CHARS.sub("", normalized)
    # Strip non-standard control characters
    normalized = CONTROL_CHARS.sub("", normalized)
    return normalized
