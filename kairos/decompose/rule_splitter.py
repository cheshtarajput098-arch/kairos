"""Rule-based Multi-Intent Clause Splitter with Context Inheritance (SPEC §5).

Splits compound utterances into sub-queries on coordinating conjunctions and list commas
between clauses that contain content nouns, inheriting shared context (locations, head entities,
numbers) into every generated leg to prevent context dilution/loss.
"""
from __future__ import annotations

import re

from kairos.schemas import SubQuery

# Common question lead-ins to strip for cleaner sub-queries
_QUESTION_PREFIXES = re.compile(
    r"^(?:what\s+(?:is|are|about|would\s+be)\s+(?:the\s+)?|"
    r"tell\s+me\s+(?:about\s+)?(?:the\s+)?|"
    r"can\s+you\s+(?:tell\s+me\s+about|provide|share|give\s+me)\s+(?:the\s+)?|"
    r"how\s+(?:about|is|are)\s+(?:the\s+)?|"
    r"please\s+(?:provide|share|tell\s+me\s+about)\s+(?:the\s+)?|"
    r"i\s+(?:want|would\s+like)\s+to\s+know\s+(?:about\s+)?(?:the\s+)?|"
    r"give\s+me\s+(?:the\s+)?|"
    r"check\s+(?:the\s+)?)+",
    re.IGNORECASE,
)

# Coordinating conjunctions and clause boundary splitters
_SPLIT_CONJUNCTIONS = re.compile(
    r"\s*(?:,\s*(?:and|plus|as\s+well\s+as|along\s+with|also)?\s*|\s+(?:and|plus|as\s+well\s+as|along\s+with|also)\s+)\s*",
    re.IGNORECASE,
)

# Pronouns/referents indicating clause needs context inheritance
_REFERENT_WORDS = {"their", "its", "the", "any", "these", "those", "for"}


class RuleBasedSplitter:
    def __init__(self, max_legs: int = 4) -> None:
        self.max_legs = max_legs

    def split(self, text: str) -> list[SubQuery]:
        """Decompose text into sub-queries carrying shared context."""
        cleaned = text.strip(" ?.!;,")
        if not cleaned:
            return []

        # 1. Identify clauses by splitting on conjunctions and commas
        raw_clauses = [c.strip(" ?.!;,") for c in _SPLIT_CONJUNCTIONS.split(cleaned) if c.strip()]
        if len(raw_clauses) <= 1:
            # Single clause turn
            entities = self._extract_entities(cleaned)
            return [SubQuery(leg_id="L1", text=cleaned, entities=entities)]

        # 2. Extract shared context from the primary clause
        primary_clause = raw_clauses[0]
        shared_context = self._extract_shared_context(primary_clause)

        # 3. Process each clause
        sub_queries: list[SubQuery] = []
        for idx, clause in enumerate(raw_clauses):
            # Check if clause has content nouns
            if not self._has_content_words(clause):
                continue

            leg_text = self._build_leg_text(clause, idx, shared_context)
            entities = self._extract_entities(leg_text)
            leg_id = f"L{len(sub_queries) + 1}"
            sub_queries.append(SubQuery(leg_id=leg_id, text=leg_text, entities=entities))

            if len(sub_queries) >= self.max_legs:
                break

        if not sub_queries:
            entities = self._extract_entities(cleaned)
            return [SubQuery(leg_id="L1", text=cleaned, entities=entities)]

        return sub_queries

    def _extract_shared_context(self, clause: str) -> dict[str, str]:
        """Extract locations, head noun entities, and numbers from primary clause."""
        context: dict[str, str] = {}

        core_clause = _QUESTION_PREFIXES.sub("", clause).strip()

        stop_proper = {
            "What", "Where", "When", "Which", "Who", "Whom", "Whose", "Why", "How",
            "Can", "Could", "Would", "Should", "Tell", "Please", "Check", "Give", "Show",
            "The", "A", "An", "Is", "Are", "In", "At", "For", "To", "On", "Of", "With",
        }

        # Look for locations / proper nouns (capitalized words like Pune, Mumbai, Riverside)
        caps = [
            c for c in re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", core_clause)
            if c not in stop_proper
        ]
        if caps:
            context["location"] = caps[0]

        # Look for numbers (e.g. '40 people', '50 seats', '10 days')
        num_match = re.search(r"\b\d+\s+[a-z]+\b", core_clause, re.IGNORECASE)
        if num_match:
            context["quantity"] = num_match.group(0)

        # Look for prepositional head context (e.g. 'for customer workshops', 'of workshop venues')
        head_match = re.search(r"\b(?:for|of|in|at)\s+([a-z\s]+?)(?:\s+in|\s+at|$)", core_clause, re.IGNORECASE)
        if head_match:
            cand = head_match.group(1).strip()
            if len(cand.split()) <= 4 and cand not in {"the", "a", "an"}:
                context["head_phrase"] = cand

        return context

    def _build_leg_text(self, clause: str, idx: int, shared_context: dict[str, str]) -> str:
        """Construct full sub-query by inheriting shared context if missing."""
        # Strip conversational prefixes
        core_clause = _QUESTION_PREFIXES.sub("", clause).strip()
        if not core_clause:
            core_clause = clause

        # Clean referent pronouns at the start: e.g. "their catering options" -> "catering options"
        core_clause = re.sub(r"^(?:their|its|the)\s+", "", core_clause, flags=re.IGNORECASE).strip()

        # If it's the primary clause, return cleaned
        if idx == 0:
            return core_clause

        # For subsequent clauses, check if context is already present
        loc = shared_context.get("location")
        head = shared_context.get("head_phrase")

        needs_loc = loc and (loc.lower() not in core_clause.lower())
        needs_head = head and (head.lower() not in core_clause.lower())

        inherited_parts: list[str] = []
        if needs_head:
            inherited_parts.append(f"for {head}")
        if needs_loc:
            inherited_parts.append(f"in {loc}")

        if inherited_parts:
            # Combine core clause with inherited context
            leg_text = f"{core_clause} {' '.join(inherited_parts)}"
        else:
            leg_text = core_clause

        return leg_text.strip()

    def _has_content_words(self, clause: str) -> bool:
        """Check if clause contains content nouns/verbs rather than just stop words."""
        words = re.findall(r"\b[A-Za-z]{3,}\b", clause.lower())
        stop_words = {"what", "about", "tell", "please", "also", "with", "from", "that", "this", "they", "them"}
        content_words = [w for w in words if w not in stop_words]
        return len(content_words) >= 1

    def _extract_entities(self, text: str) -> list[str]:
        """Extract key searchable entities from sub-query text."""
        # Capitalized proper nouns
        caps = re.findall(r"\b[A-Z][a-z]+\b", text)
        # Content nouns (length >= 4)
        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        stopwords = {
            "what", "where", "when", "which", "about", "their", "there", "these",
            "those", "would", "could", "should", "options", "details",
        }
        content = [w for w in words if w not in stopwords]
        entities = list(dict.fromkeys(caps + content))
        return entities[:5]
