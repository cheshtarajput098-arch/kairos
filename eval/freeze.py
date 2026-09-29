"""Freeze and integrity verification for test split and config (SPEC §9.6).

Computes and verifies SHA-256 manifest over data/replay/test/ and config/default.yaml.
Evaluation fails if test split files or configuration are altered post-freeze.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "data" / "replay" / "test"
CONFIG_FILE = ROOT / "config" / "default.yaml"
MANIFEST_PATH = TEST_DIR / "manifest.sha256"


def sha256_file(path: Path) -> str:
    """Compute hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_manifest() -> dict[str, str]:
    """Compute sha256 digests for all test data files and default config."""
    manifest: dict[str, str] = {}

    # Hash config
    if CONFIG_FILE.exists():
        rel_config = CONFIG_FILE.relative_to(ROOT).as_posix()
        manifest[rel_config] = sha256_file(CONFIG_FILE)

    # Hash all files in test/ except manifest itself
    for p in sorted(TEST_DIR.rglob("*")):
        if p.is_file() and p.name != "manifest.sha256":
            rel_p = p.relative_to(ROOT).as_posix()
            manifest[rel_p] = sha256_file(p)

    return manifest


def freeze_test_split(manifest_file: Path | None = None) -> Path:
    """Write SHA-256 manifest to freeze test split."""
    dest = manifest_file or MANIFEST_PATH
    manifest = compute_manifest()
    lines = [f"{digest}  {rel_path}" for rel_path, digest in sorted(manifest.items())]
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def verify_test_split_freeze(manifest_file: Path | None = None) -> tuple[bool, list[str]]:
    """Verify that current files match frozen manifest. Returns (success, errors)."""
    target = manifest_file or MANIFEST_PATH
    if not target.exists():
        return False, [f"Manifest not found at {target}"]

    errors: list[str] = []
    lines = target.read_text(encoding="utf-8").splitlines()
    frozen_records: dict[str, str] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            frozen_records[parts[1].strip()] = parts[0].strip()

    for rel_path, expected_digest in frozen_records.items():
        actual_path = ROOT / rel_path
        if not actual_path.exists():
            errors.append(f"Missing frozen file: {rel_path}")
            continue
        current_digest = sha256_file(actual_path)
        if current_digest != expected_digest:
            errors.append(f"Digest mismatch for {rel_path}: expected {expected_digest}, got {current_digest}")

    return len(errors) == 0, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze or verify test split integrity.")
    parser.add_argument("--verify", action="store_true", help="Verify frozen manifest instead of freezing.")
    args = parser.parse_args()

    if args.verify:
        passed, errors = verify_test_split_freeze()
        if not passed:
            print("FREEZE VERIFICATION FAILED:")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
        print("Freeze verification passed: all test data and config files match manifest.")
    else:
        out = freeze_test_split()
        print(f"Test split and config successfully frozen to {out}.")


if __name__ == "__main__":
    main()
