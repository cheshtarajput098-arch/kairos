"""Corpus integrity manifest generator and verifier (SPEC §13.2, LLM04).

Writes and validates SHA-256 hashes for all corpus documents.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def hash_file(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def generate_corpus_manifest(corpus_dir: Path, manifest_path: Path) -> dict[str, str]:
    """Generate SHA-256 manifest of all corpus files."""
    manifest: dict[str, str] = {}
    files = sorted(
        [
            f
            for f in corpus_dir.iterdir()
            if f.is_file() and not f.name.startswith(".") and f.name != "README.md"
        ]
    )

    for file_path in files:
        manifest[file_path.name] = hash_file(file_path)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    return manifest


def verify_corpus_manifest(corpus_dir: Path, manifest_path: Path | None = None) -> tuple[bool, str]:
    """Verify that current corpus files match the manifest SHA-256 hashes.

    Returns:
        (is_valid, error_reason)
    """
    if manifest_path is None or not manifest_path.exists():
        if Path("index/corpus.manifest.json").exists():
            manifest_path = Path("index/corpus.manifest.json")
        elif Path("data/corpus.manifest.json").exists():
            manifest_path = Path("data/corpus.manifest.json")
        else:
            return (
                False,
                f"Manifest file missing at {manifest_path or 'index/corpus.manifest.json'}",
            )

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest: dict[str, str] = json.load(f)
    except Exception as e:  # noqa: BLE001
        return False, f"Failed to parse manifest: {e}"

    current_files = {
        f.name: f
        for f in corpus_dir.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.name != "README.md"
    }

    # Check for missing or added files
    if set(current_files.keys()) != set(manifest.keys()):
        return (
            False,
            f"File set mismatch: expected {set(manifest.keys())}, found {set(current_files.keys())}",
        )

    # Verify hashes
    for fname, expected_hash in manifest.items():
        actual_hash = hash_file(current_files[fname])
        if actual_hash != expected_hash:
            return False, f"Hash mismatch for {fname}: expected {expected_hash}, got {actual_hash}"

    return True, "Corpus integrity verified"
