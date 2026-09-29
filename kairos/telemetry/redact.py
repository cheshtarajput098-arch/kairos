"""PII Redaction utilities for logs and telemetry (SPEC §8, §13.2, Security Rule 6).

Redacts:
- Email addresses
- Phone numbers (international and local formats)
- Credit card / debit card numbers (13-16 digits)
"""

from __future__ import annotations

import re

# Comprehensive PII patterns
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
RE_PHONE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
RE_CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


def redact_pii(text: str, redact_types: list[str] | None = None) -> str:
    """Redact sensitive PII text patterns (email, phone, credit card)."""
    if not text:
        return ""
    types = redact_types or ["email", "phone", "card"]
    if "email" in types:
        text = RE_EMAIL.sub("[REDACTED_EMAIL]", text)
    if "phone" in types:
        text = RE_PHONE.sub("[REDACTED_PHONE]", text)
    if "card" in types:
        text = RE_CARD.sub("[REDACTED_CARD]", text)
    return text


def redact_pii_text(text: str, redact_types: list[str] | None = None) -> str:
    """Alias for redact_pii for backward compatibility."""
    return redact_pii(text, redact_types)
