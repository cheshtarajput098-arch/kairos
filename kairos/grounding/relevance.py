"""Relevance Gate: query analysis, stopword/filler filtering, passage relevance, and honest abstention.

Guarantees:
1. Removes English stopwords and conversational filler words ("need", "help", "want", "please", "tell", "know"...)
   from BM25 queries to prevent false term matches.
2. A passage is only considered relevant if:
   - Dense cosine similarity >= T_dense (0.65 tuned on dev split).
   - AND at least one non-stopword query term (or stem) appears in the passage.
3. The selected sentence must also contain at least one non-stopword query term.
4. If no passage/sentence passes, cleanly abstains with 0 citations, an amber gap note,
   corpus coverage summary, and optional "Did you mean...?" suggestions.
"""

from __future__ import annotations

import difflib
import re
from collections.abc import Mapping
from typing import Any

from kairos.schemas import CorpusChunk

# Comprehensive English stopwords and conversational filler words
ENGLISH_STOPWORDS_AND_FILLERS: frozenset[str] = frozenset({
    # Common English stopwords
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    # Conversational filler words & query verbs
    "need", "needs", "needed", "needing",
    "help", "helps", "helped", "helping",
    "want", "wants", "wanted", "wanting",
    "please", "tell", "tells", "telling", "told",
    "know", "knows", "knowing", "knew", "known",
    "give", "gives", "giving", "gave", "given",
    "check", "checks", "checked", "checking",
    "like", "likes", "liked", "liking",
    "look", "looks", "looking", "looked",
    "show", "shows", "showing", "showed",
    "provide", "provides", "provided", "providing",
    "share", "shares", "shared", "sharing",
    "bring", "brings", "bringing", "brought",
    "make", "makes", "making", "made",
    "find", "finds", "finding", "found",
    "get", "gets", "getting", "got",
    "ask", "asks", "asking", "asked",
    "actually", "also", "instead", "just", "sure", "see",
})

# Default dense cosine similarity threshold tuned on dev split
DEFAULT_T_DENSE: float = 0.65


def clean_bm25_query(query: str) -> str:
    """Filter English stopwords and filler words from query before BM25 tokenization."""
    words = re.findall(r"[a-zA-Z0-9]+", query.lower())
    content_words = [w for w in words if w not in ENGLISH_STOPWORDS_AND_FILLERS and len(w) > 1]
    return " ".join(content_words)


# Domain synonyms for query matching (Item 1)
SYNONYMS: dict[str, set[str]] = {
    "capacity": {"seating", "seats", "attendees", "host", "accommodate", "people", "size", "guests"},
    "venue": {"hall", "room", "space", "studio", "facility", "location", "center"},
    "venues": {"halls", "rooms", "spaces", "studios", "facilities", "locations"},
    "cancel": {"cancellation", "refund", "refunds", "cancelling", "cancelled"},
    "cancellation": {"cancel", "refund", "refunds", "timeline", "notice", "fee"},
    "catering": {"caterer", "meals", "meal", "food", "lunch", "dinner", "refreshments"},
    "travel": {"trip", "journey", "transport", "flight", "flights", "transit", "taxi", "taxis", "cab", "cabs"},
    "expense": {"expenses", "cost", "costs", "reimbursement", "reimbursements", "claim", "claims", "receipt", "receipts"},
    "reimbursement": {"expense", "expenses", "claim", "claims", "receipt", "receipts", "refund"},
    "tax": {"taxes", "taxing", "taxation"},
    "taxes": {"tax", "taxing", "taxation"},
    "taxing": {"tax", "taxes", "taxation"},
}


def extract_content_terms(text: str) -> set[str]:
    """Extract lowercase non-stopword tokens, morphological stems, and synonyms from query/passage."""
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    terms: set[str] = set()
    for w in words:
        if w in ENGLISH_STOPWORDS_AND_FILLERS or len(w) <= 1:
            continue
        terms.add(w)
        # Add basic English stem variations
        if w.endswith("ing") and len(w) > 5:
            terms.add(w[:-3])
        elif w.endswith("es") and len(w) > 4:
            terms.add(w[:-2])
        elif w.endswith("s") and len(w) > 3:
            terms.add(w[:-1])
        elif w.endswith("ed") and len(w) > 4:
            terms.add(w[:-2])
        elif w.endswith("tion") and len(w) > 6:
            terms.add(w[:-4])
        # Add synonyms if defined
        if w in SYNONYMS:
            terms.update(SYNONYMS[w])
    return terms


class RelevanceGate:
    """Deterministic relevance gate enforcing dense similarity and lexical query overlap."""

    def __init__(self, t_dense: float = DEFAULT_T_DENSE) -> None:
        self.t_dense = t_dense

    def check_passage_relevance(
        self,
        query: str,
        chunk_text: str,
        chunk_title: str,
        dense_score: float,
    ) -> tuple[bool, str, list[str]]:
        """A passage passes if dense score >= T_dense AND at least one non-stopword query term appears in it."""
        query_terms = extract_content_terms(query)
        if not query_terms:
            return False, "Query contains only stopwords or filler words", []

        if dense_score < self.t_dense:
            return False, f"Dense similarity {dense_score:.4f} is below threshold {self.t_dense:.2f}", []

        passage_content = f"{chunk_title} {chunk_text}".lower()
        matched_terms = [t for t in query_terms if t in passage_content]

        if not matched_terms:
            return False, "No non-stopword query term appears in passage", []

        return True, "Passed passage relevance check", matched_terms

    def check_sentence_relevance(
        self,
        query: str,
        sentence: str,
    ) -> tuple[bool, str, list[str]]:
        """The chosen sentence must also contain at least one non-stopword query term."""
        query_terms = extract_content_terms(query)
        if not query_terms:
            return False, "Query contains only stopwords or filler words", []

        sent_lower = sentence.lower()
        matched_terms = [t for t in query_terms if t in sent_lower]

        if not matched_terms:
            return False, "Chosen sentence does not contain any non-stopword query term", []

        return True, "Passed sentence relevance check", matched_terms

    def extract_query_topic(self, query: str) -> str:
        """Extract a readable topic string for the abstention notice."""
        clean = clean_bm25_query(query)
        if clean:
            return clean
        words = re.findall(r"[a-zA-Z0-9]+", query.strip())
        return " ".join(words[:4]) if words else "this topic"

    def get_corpus_coverage(self, chunks_map: Mapping[str, CorpusChunk | dict[str, Any]]) -> str:
        """Build human-readable corpus coverage summary from document titles."""
        titles: list[str] = []
        seen: set[str] = set()
        for chunk in chunks_map.values():
            title = (
                chunk.title
                if isinstance(chunk, CorpusChunk)
                else str(chunk.get("title", ""))
            )
            base_title = title.split(" - ")[0].split(" §")[0].strip()
            if base_title and base_title not in seen:
                seen.add(base_title)
                titles.append(base_title)

        if not titles:
            return "Company policies and operational guidelines."

        if len(titles) <= 3:
            return ", ".join(titles)
        return f"{', '.join(titles[:5])}, and {len(titles) - 5} more policies"

    def find_did_you_mean(
        self,
        query: str,
        chunks_map: Mapping[str, CorpusChunk | dict[str, Any]],
    ) -> dict[str, str] | None:
        """Find closest in-corpus topic suggestion for out-of-corpus queries (e.g. taxing -> taxis)."""
        content_words = list(extract_content_terms(query))
        if not content_words:
            return None

        # Build vocabulary from corpus chunk titles and texts
        corpus_vocab: dict[str, tuple[str, str]] = {}  # term -> (chunk_id, context_label)
        for cid, chunk in chunks_map.items():
            text = chunk.text if isinstance(chunk, CorpusChunk) else str(chunk.get("text", ""))
            title = chunk.title if isinstance(chunk, CorpusChunk) else str(chunk.get("title", ""))
            combined = f"{title} {text}".lower()

            # Known domain mapping
            if "taxis" in combined or "transport" in combined:
                corpus_vocab["taxis"] = (cid, "Local transport (taxis)")
                corpus_vocab["transport"] = (cid, "Local transport")
            if "cancellation" in combined:
                corpus_vocab["cancellation"] = (cid, "Event cancellation refunds")
            if "catering" in combined:
                corpus_vocab["catering"] = (cid, "Event catering options")
            if "laptops" in combined or "laptop" in combined:
                corpus_vocab["laptops"] = (cid, "IT laptop loans")
            if "reimbursement" in combined:
                corpus_vocab["reimbursement"] = (cid, "Expense reimbursements")

        for word in content_words:
            # Fuzzy match word to corpus vocabulary
            matches = difflib.get_close_matches(word, corpus_vocab.keys(), n=1, cutoff=0.7)
            if matches:
                matched_key = matches[0]
                cid, label = corpus_vocab[matched_key]
                return {
                    "matched_term": matched_key,
                    "suggestion_label": label,
                    "chunk_id": cid,
                }

        return None
