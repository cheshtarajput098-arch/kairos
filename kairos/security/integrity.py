"""Cryptographic supply chain and model integrity verification (SPEC §13.2, Security Rule 8).

Verifies model weights and corpus manifests via SHA-256 digests at startup.
Refuses to boot or serve if any file has been tampered with or corrupted.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

logger = logging.getLogger("kairos.security.integrity")


def calculate_sha256(file_path: Path) -> str:
    """Compute SHA-256 digest of a file in streaming 64KB blocks."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_file_sha256(file_path: Path, expected_sha256: str) -> bool:
    """Verify that a file's SHA-256 digest exactly matches expected hash."""
    if not file_path.exists():
        return False
    actual_hash = calculate_sha256(file_path)
    return actual_hash.lower() == expected_sha256.strip().lower()


def verify_model_integrity(model_path: Path, expected_sha256: str | None) -> None:
    """Verify integrity of a model file against its pinned SHA-256 digest.

    Raises:
        FileNotFoundError: If the model file is missing.
        RuntimeError: If SHA-256 digest mismatch is detected (tampering/corruption).
    """
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}")

    if not expected_sha256 or expected_sha256.upper() == "TBD":
        logger.warning(
            f"Model {model_path.name} has no pinned SHA-256 digest configured; skipping verification."
        )
        return

    actual_sha256 = calculate_sha256(model_path)
    if actual_sha256.lower() != expected_sha256.strip().lower():
        msg = (
            f"Model integrity verification failed for {model_path}: "
            f"expected SHA-256 '{expected_sha256}', got '{actual_sha256}'."
        )
        logger.critical(msg)
        raise RuntimeError(msg)

    logger.info(f"Model integrity verified successfully for {model_path.name} ({actual_sha256[:12]}...).")
