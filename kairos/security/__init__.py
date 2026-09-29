"""Security subsystem for Kairos (SPEC §13, Security Rules 1–10).

Provides:
- Input limits and validation (SPEC §13.3)
- Unicode normalization, zero-width stripping, and sanitization (SPEC §13.3)
- Context Spotlighting and instruction flagging (SPEC §13.2)
- Model and supply-chain SHA-256 integrity verification (SPEC §13.2)
"""

from __future__ import annotations

from kairos.security.integrity import calculate_sha256, verify_file_sha256, verify_model_integrity
from kairos.security.limits import (
    validate_chunks_count,
    validate_message_size,
    validate_sessions_per_client,
    validate_tokens_count,
    validate_words_per_turn,
)
from kairos.security.sanitizer import sanitize_input_text
from kairos.security.spotlight import (
    SPOTLIGHT_SYSTEM_INSTRUCTION,
    build_spotlight_block,
    build_spotlight_context,
    escape_corpus_content,
)

__all__ = [
    "SPOTLIGHT_SYSTEM_INSTRUCTION",
    "build_spotlight_block",
    "build_spotlight_context",
    "calculate_sha256",
    "escape_corpus_content",
    "sanitize_input_text",
    "validate_chunks_count",
    "validate_message_size",
    "validate_sessions_per_client",
    "validate_tokens_count",
    "validate_words_per_turn",
    "verify_file_sha256",
    "verify_model_integrity",
]
