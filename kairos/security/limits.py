"""Input limits & security parameters enforcement (SPEC §13.3)."""
from __future__ import annotations

from kairos.config import load_config

settings = load_config()


def validate_message_size(size_bytes: int) -> bool:
    return size_bytes <= settings.security.max_message_bytes


def validate_chunks_count(chunk_count: int) -> bool:
    return chunk_count <= settings.security.max_chunks_per_turn
