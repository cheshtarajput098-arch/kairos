"""Unit tests for corpus manifest integrity and index store."""

from pathlib import Path

from kairos.index.store import IndexStore
from kairos.ingest.manifest import generate_corpus_manifest, verify_corpus_manifest


def test_manifest_generation_and_verification(tmp_path: Path) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "Doc_01.md").write_text("# Doc 1\n## 1. Sec 1\nText 1", encoding="utf-8")
    (corpus_dir / "Doc_02.md").write_text("# Doc 2\n## 1. Sec 1\nText 2", encoding="utf-8")

    manifest_file = tmp_path / "corpus.manifest.json"
    generate_corpus_manifest(corpus_dir, manifest_file)

    assert manifest_file.exists()
    is_valid, reason = verify_corpus_manifest(corpus_dir, manifest_file)
    assert is_valid is True
    assert "verified" in reason.lower()


def test_tampered_corpus_file_fails_verification(tmp_path: Path) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    doc_file = corpus_dir / "Doc_01.md"
    doc_file.write_text("# Doc 1\n## 1. Sec 1\nOriginal Text", encoding="utf-8")

    manifest_file = tmp_path / "corpus.manifest.json"
    generate_corpus_manifest(corpus_dir, manifest_file)

    # Tamper with the document
    doc_file.write_text("# Doc 1\n## 1. Sec 1\nTampered Content!", encoding="utf-8")

    is_valid, reason = verify_corpus_manifest(corpus_dir, manifest_file)
    assert is_valid is False
    assert "mismatch" in reason.lower()


def test_index_store_build_and_load(tmp_path: Path) -> None:
    corpus_dir = Path("data/corpus")
    index_dir = tmp_path / "index"

    store = IndexStore(index_dir=index_dir, corpus_dir=corpus_dir)
    store.build()

    assert (index_dir / "chunks.json").exists()
    assert (index_dir / "provenance.json").exists()
    assert (index_dir / "bm25").exists()
    assert (index_dir / "dense").exists()

    loaded_store = IndexStore(index_dir=index_dir, corpus_dir=corpus_dir)
    loaded_store.load()
    assert len(loaded_store.chunks_map) > 0
    assert "Doc_12§2" in loaded_store.chunks_map
