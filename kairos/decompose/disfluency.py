"""Generic Disfluency Normalizer (SPEC §5).

Strips speech disfluencies prior to multi-intent decomposition:
1. Speech fillers ('uh', 'um', 'you know', etc.)
2. Immediate consecutive word repetitions ('the the' -> 'the')
3. Speech self-repairs ('in Pune — no, Mumbai' -> 'in Mumbai', 'actually', 'sorry', 'I mean')
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from kairos.config import load_config

_default_config = load_config()


class DisfluencyNormalizer:
    def __init__(
        self,
        fillers: Sequence[str] | None = None,
        repair_cues: Sequence[str] | None = None,
    ) -> None:
        self.fillers = (
            list(fillers)
            if fillers is not None
            else list(_default_config.decomposer.disfluency.fillers)
        )
        self.repair_cues = (
            list(repair_cues)
            if repair_cues is not None
            else list(_default_config.decomposer.disfluency.repair_cues)
        )

        # Precompile filler pattern (longer phrases first to avoid partial word masking)
        sorted_fillers = sorted(self.fillers, key=len, reverse=True)
        escaped_fillers = [re.escape(f) for f in sorted_fillers]
        self._fillers_regex = re.compile(
            rf"\b(?:{'|'.join(escaped_fillers)})\b[,.]?", re.IGNORECASE
        )

        # Immediate repetition pattern: e.g. "the the" -> "the"
        self._repetition_regex = re.compile(r"\b(\w+)(?:\s+\1\b)+", re.IGNORECASE)

        # Repair cues pattern: e.g. "no", "sorry", "actually", "i mean", "wait", "rather"
        sorted_cues = sorted(self.repair_cues, key=len, reverse=True)
        escaped_cues = [re.escape(c) for c in sorted_cues]
        self._repair_cues_pattern = rf"(?:{'|'.join(escaped_cues)})"

    def normalize(self, text: str) -> str:
        """Normalize disfluent speech transcript into clean text."""
        if not text:
            return ""

        result = text.strip()

        # 1. Resolve speech self-repairs
        result = self._resolve_repairs(result)

        # 2. Collapse immediate repetitions
        result = self._collapse_repetitions(result)

        # 3. Strip speech fillers
        result = self._strip_fillers(result)

        # 4. Clean up whitespace and orphan punctuation
        result = re.sub(r"\s+([,.:;?!])", r"\1", result)
        result = re.sub(r"\s*([—–])\s*", " ", result)
        result = re.sub(r"\s{2,}", " ", result)
        result = result.strip(" ,.-—–")

        return result

    def _resolve_repairs(self, text: str) -> str:
        """Resolve self-repairs where later phrasing explicitly replaces prior phrasing.

        Examples:
            'in Pune — no, Mumbai' -> 'in Mumbai'
            'for 20 people actually 30 people' -> 'for 30 people'
            'workshop on Monday, sorry, Tuesday' -> 'workshop on Tuesday'
        """
        # Pattern 1: [preposition/qualifier] [Word] [dash/comma/space] [repair_cue] [,] [replacement Word]
        # e.g., 'in Pune — no, Mumbai' -> 'in Mumbai'
        # e.g., 'Pune, sorry, Mumbai' -> 'Mumbai'
        pattern1 = re.compile(
            rf"((?:\b(?:in|at|for|to|on|of|with|under)\s+)?\b[A-Za-z0-9]+)\s*[-—–,]*\s*{self._repair_cues_pattern}\s*[,:-]*\s*((?:\b(?:in|at|for|to|on|of|with|under)\s+)?[A-Za-z0-9]+)",
            re.IGNORECASE,
        )

        def replace_match(m: re.Match[str]) -> str:
            before = m.group(1).strip()
            after = m.group(2).strip()
            # If before had a preposition ('in Pune') and after doesn't ('Mumbai'), preserve preposition
            parts_before = before.split()
            parts_after = after.split()
            if len(parts_before) > 1 and len(parts_after) == 1:
                prep = parts_before[0]
                if prep.lower() in {"in", "at", "for", "to", "on", "of", "with", "under"}:
                    return f"{prep} {after}"
            return after

        text = pattern1.sub(replace_match, text)

        # Pattern 2: standalone repair cues with trailing correction, e.g. "actually 50 seats"
        pattern2 = re.compile(
            rf"\s*[-—–,]*\s*{self._repair_cues_pattern}\s*[,:-]*\s*", re.IGNORECASE
        )
        # Only replace dangling cues if not already resolved
        text = pattern2.sub(" ", text)

        return text

    def _collapse_repetitions(self, text: str) -> str:
        """Collapse immediate identical word repetitions."""
        return self._repetition_regex.sub(r"\1", text)

    def _strip_fillers(self, text: str) -> str:
        """Remove speech filler words."""
        return self._fillers_regex.sub("", text)
