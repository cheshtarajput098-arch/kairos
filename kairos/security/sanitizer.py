"""Input sanitization, normalization, and character stripping (SPEC §13.3).

Features:
1. Unicode NFKC normalization.
2. Stripping non-printable control characters (preserving tab, newline, carriage return).
3. Stripping zero-width characters (U+200B..U+200D, U+FEFF, etc.).
4. Neutralizing spotlight delimiter breakout sequences.
"""

from __future__ import annotations

import re
import unicodedata

# Matches zero-width spaces, joiners, and BOM
ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200D\uFEFF\u2060\u180E]")

# Matches control characters except \t (\x09), \n (\x0A), \r (\x0D)
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]")


def sanitize_input_text(raw_text: str, max_chars: int | None = None) -> str:
    """Sanitize and normalize untrusted user input before downstream pipeline stages.

    Applies:
    - Unicode NFKC normalization
    - Removal of zero-width hidden characters
    - Removal of ASCII and Unicode C0/C1 control characters
    - Breakout tag escaping for spotlight delimiters
    - Optional maximum character truncation
    """
    if not raw_text:
        return ""

    # 1. Unicode NFKC normalization
    normalized = unicodedata.normalize("NFKC", raw_text)

    # 2. Strip zero-width hidden characters
    cleaned = ZERO_WIDTH_RE.sub("", normalized)

    # 3. Strip non-printable control characters
    cleaned = CONTROL_CHARS_RE.sub("", cleaned)

    # 4. Neutralize spotlight delimiter and script sequences to prevent breakout and injection attacks
    cleaned = cleaned.replace("<untrusted_corpus", "&lt;untrusted_corpus")
    cleaned = cleaned.replace("</untrusted_corpus>", "&lt;/untrusted_corpus&gt;")
    cleaned = cleaned.replace("<script", "&lt;script")
    cleaned = cleaned.replace("</script>", "&lt;/script&gt;")

    # 5. Length bounding if specified
    if max_chars is not None and len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]

    return cleaned
