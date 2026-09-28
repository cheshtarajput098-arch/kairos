"""JSONL Event Logger with PII Redaction (SPEC §8)."""
from __future__ import annotations

import json
import pathlib
import re
import uuid
from typing import Any

# Regex patterns for PII redaction
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
RE_PHONE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
RE_CARD = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


def redact_pii_text(text: str, redact_types: list[str] | None = None) -> str:
    """Redact sensitive PII text patterns."""
    if not text:
        return text
    types = redact_types or ["email", "phone", "card"]
    if "email" in types:
        text = RE_EMAIL.sub("[REDACTED_EMAIL]", text)
    if "phone" in types:
        text = RE_PHONE.sub("[REDACTED_PHONE]", text)
    if "card" in types:
        text = RE_CARD.sub("[REDACTED_CARD]", text)
    return text


def redact_obj(obj: Any, log_text: bool = False, redact_types: list[str] | None = None) -> Any:
    """Recursively redact PII and mask raw text if log_text is False."""
    if isinstance(obj, str):
        if not log_text and len(obj) > 200:
            # Mask or truncate long raw transcript text if log_text is False
            return f"[TEXT_HASH:{hash(obj) & 0xffffffff:08x}_LEN:{len(obj)}]"
        return redact_pii_text(obj, redact_types)
    elif isinstance(obj, dict):
        return {k: redact_obj(v, log_text, redact_types) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [redact_obj(item, log_text, redact_types) for item in obj]
    return obj


class JSONLEventWriter:
    def __init__(self, runs_dir: pathlib.Path = pathlib.Path("runs"), run_id: str | None = None, log_text: bool = False):
        self.run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"
        self.log_dir = runs_dir / self.run_id
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.log_dir / "events.jsonl"
        self.log_text = log_text

    def write_event(self, event_dict: dict[str, Any]) -> None:
        sanitized = redact_obj(event_dict, log_text=self.log_text)
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(sanitized) + "\n")
