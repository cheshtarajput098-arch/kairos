"""Unpack the Kairos bundle files (KAIROS_1_CORE.md, KAIROS_2_SPEC.md, KAIROS_3_BUILD_STEPS.md)
into the repository, byte for byte, then move the bundles into .bundle/ (git-ignored).

Usage (from the repository root):  python tools/unpack_bundles.py
Safe to re-run: identical files are skipped; a different existing file stops the run unless --force.
"""
import hashlib
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path.cwd()
START = re.compile(r"^======== FILE: (.+?) ========$")
END = "======== END FILE ========"
HEADER = re.compile(r"^<!-- kairos-bundle (\d) of 3 \| files: (\d+) \| sha256: ([0-9a-f]{64}) -->$")


def parse(bundle: pathlib.Path) -> list[tuple[str, str]]:
    text = bundle.read_text(encoding="utf-8").lstrip("\ufeff").replace("\r\n", "\n")  # tolerate BOM / Windows line endings
    lines = text.split("\n")
    head = HEADER.match(lines[0].strip())
    if not head:
        sys.exit(f"{bundle.name}: missing or damaged header line. Download the file again.")
    files, path, buf = [], None, []
    for line in lines[1:]:
        if path is None:
            m = START.match(line)
            if m:
                path, buf = m.group(1).strip(), []
        elif line == END:
            files.append((path, "\n".join(buf) + ("\n" if buf else "")))
            path = None
        else:
            buf.append(line)
    if path is not None:
        sys.exit(f"{bundle.name}: file '{path}' is not closed. The bundle is truncated; download it again.")
    digest = hashlib.sha256("".join(p + "\0" + c for p, c in files).encode("utf-8")).hexdigest()
    if len(files) != int(head.group(2)) or digest != head.group(3):
        sys.exit(f"{bundle.name}: content check failed ({len(files)} files found, {head.group(2)} expected). "
                 "The file was changed or cut off; download it again.")
    return files


def main() -> None:
    force = "--force" in sys.argv
    bundles = sorted(ROOT.glob("KAIROS_[123]_*.md"))
    if not bundles and len(list((ROOT / ".bundle").glob("KAIROS_[123]_*.md"))) == 3:
        print("Already unpacked (the bundles are in .bundle/). Nothing to do.")
        return
    if len(bundles) != 3:
        sys.exit(f"Expected 3 bundle files (KAIROS_1..3_*.md) in {ROOT}, found {len(bundles)}.")
    written = skipped = 0
    for bundle in bundles:
        for rel, content in parse(bundle):
            p = pathlib.PurePosixPath(rel)
            if p.is_absolute() or ".." in p.parts:
                sys.exit(f"Refusing unsafe path: {rel}")
            target = ROOT / p
            if target.exists():
                if target.read_text(encoding="utf-8") == content:
                    skipped += 1
                    continue
                if not force:
                    sys.exit(f"{rel} already exists with different content. Re-run with --force to overwrite.")
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
            written += 1
    store = ROOT / ".bundle"
    store.mkdir(exist_ok=True)
    for b in sorted(ROOT.glob("KAIROS_[0123]_*.md")):
        shutil.move(str(b), store / b.name)
    print(f"Unpacked OK: {written} files written, {skipped} already identical. Bundles moved to .bundle/.")


if __name__ == "__main__":
    main()
