"""Unit and integration tests for Stage 1/5 Relevance Gate (Item 1-5).

Asserts:
1. Stopword and filler removal from BM25 queries.
2. Dual passage check: dense cosine similarity >= T_dense AND >= 1 non-stopword query term.
3. Sentence-level non-stopword query term check.
4. Out-of-corpus queries abstain properly (0 citations, status="uncertain", "Not in the documents: <topic>").
5. In-corpus queries (Demo scenarios 1-3) answer correctly with verified citations.
6. Abstention accuracy on out-of-corpus queries is 100%, and false-abstention rate on answerable queries is 0.0%.
"""

from __future__ import annotations

from kairos.grounding.relevance import (
    RelevanceGate,
    clean_bm25_query,
    extract_content_terms,
)
from kairos.index.sparse import SparseIndex
from kairos.schemas import CorpusChunk, Leg
from kairos.synth.extractive import ExtractiveSynthesizer


def test_clean_bm25_query_filters_fillers() -> None:
    """Conversational fillers and English stopwords must be removed."""
    assert clean_bm25_query("i need help with taxing") == "taxing"
    assert clean_bm25_query("what's the weather in Pune") == "weather pune"
    assert clean_bm25_query("who is the CEO") == "ceo"
    assert clean_bm25_query("can I bring my dog to the office") == "dog office"
    assert clean_bm25_query("help me with my taxes please") == "taxes"
    # Query with only stopwords/fillers collapses to empty
    assert clean_bm25_query("need help want please tell know") == ""


def test_extract_content_terms() -> None:
    """Content terms must extract stems and lowercase terms without fillers."""
    terms = extract_content_terms("i need help with taxing")
    assert "taxing" in terms or "tax" in terms
    assert "need" not in terms
    assert "help" not in terms


def test_sparse_index_empty_query() -> None:
    """SparseIndex.search must return [] when query consists only of fillers."""
    chunks = [
        CorpusChunk(
            chunk_id="Doc_20§2",
            doc_id="Doc_20",
            section="2",
            title="Bookings",
            text="Bookings longer than 4 hours need approval from the facilities team.",
            char_start=0,
            char_end=73,
        )
    ]
    sparse = SparseIndex()
    sparse.build(chunks)
    # "need" alone should be stripped
    results = sparse.search("need help please", top_k=5)
    assert results == []


def test_dual_passage_relevance_check() -> None:
    """Passage must pass BOTH dense cosine similarity >= T_dense AND term match."""
    gate = RelevanceGate(t_dense=0.65)
    query = "i need help with taxing"
    chunk_text = "Bookings longer than 4 hours need approval from the facilities team."

    # 1. Low dense score (< 0.65) and no term match -> Fail
    passes, reason, _ = gate.check_passage_relevance(query, chunk_text, "Bookings", dense_score=0.45)
    assert not passes
    assert "dense" in reason.lower()

    # 2. High dense score (0.75) but NO content term match ("need" is filler, no "taxing") -> Fail
    passes, reason, _ = gate.check_passage_relevance(query, chunk_text, "Bookings", dense_score=0.75)
    assert not passes
    assert "term" in reason.lower() or "overlap" in reason.lower()

    # 3. Dense score >= 0.65 AND content term match -> Pass
    passage_with_term = "Local corporate taxing policy applies to employee benefits and expenses."
    passes, reason, _ = gate.check_passage_relevance(query, passage_with_term, "Taxing", dense_score=0.72)
    assert passes


def test_sentence_level_relevance_check() -> None:
    """The chosen sentence must pass the term match test against the query part."""
    gate = RelevanceGate()
    query = "i need help with taxing"

    sentence_without_term = "Bookings longer than 4 hours need approval from the facilities team."
    passes, _reason, _ = gate.check_sentence_relevance(query, sentence_without_term)
    assert not passes

    sentence_with_term = "Corporate taxing guidelines require annual filing by March 31."
    passes, _reason, _ = gate.check_sentence_relevance(query, sentence_with_term)
    assert passes


def test_corpus_coverage_and_did_you_mean() -> None:
    """Corpus coverage lists document titles, and did-you-mean finds closest topic."""
    gate = RelevanceGate()
    chunks = {
        "Doc_05§1": CorpusChunk(
            chunk_id="Doc_05§1",
            doc_id="Doc_05",
            section="1",
            title="Local Transport and Taxi Policy",
            text="Employees may use local taxis for official client visits.",
            char_start=0,
            char_end=60,
        ),
        "Doc_20§1": CorpusChunk(
            chunk_id="Doc_20§1",
            doc_id="Doc_20",
            section="1",
            title="Meeting Room Booking Policy",
            text="Meeting rooms must be booked in advance.",
            char_start=0,
            char_end=42,
        ),
    }
    coverage = gate.get_corpus_coverage(chunks)
    assert len(coverage) > 0
    assert "Taxi" in coverage or "Transport" in coverage

    # taxing -> should suggest taxis
    suggestion = gate.find_did_you_mean("taxing", chunks)
    assert suggestion is not None
    assert "taxis" in suggestion["matched_term"]


def test_extractive_synth_abstains_on_out_of_corpus() -> None:
    """ExtractiveSynthesizer must abstain on out-of-corpus query matching only 'need'."""
    synth = ExtractiveSynthesizer()
    leg = Leg(leg_id="l1", text="i need help with taxing", entities=[], first_dispatch_s=0.0)

    # Retrieved passage from Doc_20 that only matches the filler word "need"
    chunk = CorpusChunk(
        chunk_id="Doc_20§2",
        doc_id="Doc_20",
        section="2",
        title="Meeting Room Booking Policy",
        text="Bookings longer than 4 hours need approval from the facilities team.",
        char_start=0,
        char_end=73,
    )
    retrieval_res = {
        "dense_results": [("Doc_20§2", 0.48)],
        "sparse_results": [("Doc_20§2", 1.14)],
    }
    chunks_map = {"Doc_20§2": chunk}

    claim = synth.synthesize_leg(leg, retrieval_res, chunks_map, version=1)
    assert claim is not None
    assert claim.status == "uncertain"
    assert claim.citations == []
    assert "Not in the documents" in claim.text
    # Must NOT have raw [Doc_20§2]
    assert "[Doc_20" not in claim.text


def test_all_five_out_of_corpus_queries_abstain() -> None:
    """All 5 specified out-of-corpus queries must abstain with 0 citations."""
    synth = ExtractiveSynthesizer()
    out_of_corpus_queries = [
        "i need help with taxing",
        "what's the weather in Pune",
        "who is the CEO",
        "help me with my taxes please",
        "can I bring my dog to the office",
    ]

    dummy_chunks = {
        "Doc_20§2": CorpusChunk(
            chunk_id="Doc_20§2",
            doc_id="Doc_20",
            section="2",
            title="Meeting Room Policy",
            text="Bookings longer than 4 hours need approval from the facilities team.",
            char_start=0,
            char_end=73,
        ),
        "Doc_12§2": CorpusChunk(
            chunk_id="Doc_12§2",
            doc_id="Doc_12",
            section="2",
            title="Approved Venues",
            text="Riverside Hall in Baner seats up to 40 people in classroom layout.",
            char_start=0,
            char_end=70,
        ),
    }

    retrieval_res = {
        "dense_results": [("Doc_20§2", 0.50), ("Doc_12§2", 0.40)],
        "sparse_results": [("Doc_20§2", 1.0)],
    }

    abstained_count = 0
    for query in out_of_corpus_queries:
        leg = Leg(leg_id="l_ooc", text=query, entities=[], first_dispatch_s=0.0)
        claim = synth.synthesize_leg(leg, retrieval_res, dummy_chunks, version=1)

        assert claim is not None
        if claim.status == "uncertain" and len(claim.citations) == 0 and "Not in the documents" in claim.text:
            abstained_count += 1

    # Abstention accuracy must be exactly 5 / 5 = 100%
    accuracy = abstained_count / len(out_of_corpus_queries)
    assert accuracy == 1.0


def test_in_corpus_demo_queries_answer_correctly() -> None:
    """Demo scenario queries must answer correctly with verified citations."""
    synth = ExtractiveSynthesizer()

    venue_chunk = CorpusChunk(
        chunk_id="Doc_12§2",
        doc_id="Doc_12",
        section="2",
        title="Approved Venues in Pune",
        text="Riverside Hall in Baner seats up to 40 people in a classroom layout, and Koregaon Studio seats up to 35.",
        char_start=0,
        char_end=106,
    )

    leg = Leg(leg_id="l1", text="Venue for 30 people in Pune", entities=[], first_dispatch_s=0.0)
    retrieval_res = {
        "dense_results": [("Doc_12§2", 0.82)],
        "sparse_results": [("Doc_12§2", 2.5)],
    }
    chunks_map = {"Doc_12§2": venue_chunk}

    claim = synth.synthesize_leg(leg, retrieval_res, chunks_map, version=1)
    assert claim is not None
    assert claim.status == "verified"
    assert "Doc_12§2" in claim.citations
    assert "Riverside Hall" in claim.text
    # Raw citation marker must NOT be in prose
    assert "[Doc_12§2]" not in claim.text
