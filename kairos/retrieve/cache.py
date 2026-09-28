"""Prefix-hash result cache for retrieval queries (SPEC §6.1)."""
from __future__ import annotations

import hashlib
from collections import OrderedDict
from typing import Any


def hash_query(query: str) -> str:
    """Generate deterministic SHA-256 hash of normalized query."""
    normalized = " ".join(query.strip().lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


class RetrievalCache:
    def __init__(self, max_entries: int = 1024, enabled: bool = True):
        self.max_entries = max_entries
        self.enabled = enabled
        self._cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, query: str) -> Any | None:
        if not self.enabled:
            return None
        key = hash_query(query)
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, query: str, value: Any) -> None:
        if not self.enabled:
            return
        key = hash_query(query)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.max_entries:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()
