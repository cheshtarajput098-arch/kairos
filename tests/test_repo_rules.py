"""Repository-rule tests. They guard the hackathon's hard rules from day one and run in CI on every push.

- Rules files stay under Antigravity's reported 12,000-character-per-file limit.
- Application code never imports test data or evaluation code (no-hardcoding rule).
- No transcript text from data/replay appears inside application code (no-hardcoding rule).
- The config parses and has every required section.
- Demo scenarios and gold labels are well formed, and every gold citation points at a real corpus section.
- Secrets are never committed.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RULE_FILES = [ROOT / "AGENTS.md", ROOT / "GEMINI.md", *sorted((ROOT / ".agents" / "rules").glob("*.md"))]
RULES_CHAR_LIMIT = 12_000
APP_DIRS = [ROOT / "kairos", ROOT / "web" / "src"]
APP_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json"}


def _app_files() -> list[Path]:
    files: list[Path] = []
    for d in APP_DIRS:
        if d.exists():
            files += [p for p in d.rglob("*") if p.suffix in APP_SUFFIXES and "node_modules" not in p.parts]
    return files


def _replay_turns() -> list[dict]:
    turns = []
    for f in (ROOT / "data" / "replay").rglob("*.jsonl"):
        if f.name == "gold.jsonl":
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                turns.append(json.loads(line))
    return turns


def test_rules_files_exist_and_fit_the_limit() -> None:
    assert (ROOT / ".agents" / "rules").is_dir(), "missing .agents/rules/"
    assert len(RULE_FILES) >= 5, f"expected AGENTS.md, GEMINI.md and 3 rules files, got {RULE_FILES}"
    for f in RULE_FILES:
        n = len(f.read_text(encoding="utf-8"))
        assert n < RULES_CHAR_LIMIT, f"{f.name} is {n} chars; keep every rules file under {RULES_CHAR_LIMIT}"


def test_rules_folder_files_are_always_on() -> None:
    for f in (ROOT / ".agents" / "rules").glob("*.md"):
        head = f.read_text(encoding="utf-8").split("---")
        assert len(head) >= 3 and "trigger: always_on" in head[1], f"{f.name} must start with 'trigger: always_on' front matter"


def test_app_code_never_imports_eval_or_test_data() -> None:
    for f in (ROOT / "kairos").rglob("*.py"):
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                top = name.split(".")[0]
                assert top not in {"eval", "data", "tests"}, f"{f.relative_to(ROOT)} imports '{name}' (no-hardcoding rule)"
        src = f.read_text(encoding="utf-8")
        assert "data/replay" not in src, f"{f.relative_to(ROOT)} references data/replay (no-hardcoding rule)"


def test_no_transcript_text_in_app_code() -> None:
    phrases = set()
    for turn in _replay_turns():
        for chunk in turn.get("chunks", []):
            text = re.sub(r"\s+", " ", str(chunk.get("text", ""))).strip().lower()
            if len(text) >= 20:
                phrases.add(text)
    for f in _app_files():
        body = re.sub(r"\s+", " ", f.read_text(encoding="utf-8", errors="ignore")).lower()
        for p in phrases:
            assert p not in body, f"{f.relative_to(ROOT)} contains replay text '{p}' (no-hardcoding rule)"


def test_config_parses_with_required_sections() -> None:
    cfg = yaml.safe_load((ROOT / "config" / "default.yaml").read_text(encoding="utf-8"))
    required = {"app", "models", "controller", "decomposer", "retrieval", "fusion", "synthesis",
                "drafting", "grounding", "session", "telemetry", "security", "eval"}
    missing = required - set(cfg)
    assert not missing, f"config/default.yaml is missing sections: {missing}"
    assert cfg["telemetry"]["log_text"] is False, "raw text logging must be off by default"
    assert cfg["decomposer"]["max_legs"] <= 4


def test_demo_scenarios_are_well_formed() -> None:
    demo = ROOT / "data" / "replay" / "demo"
    turns = [json.loads(line) for line in (demo / "scenarios.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    gold = {g["turn_id"]: g for g in (json.loads(line) for line in (demo / "gold.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    assert len({t["session_id"] for t in turns}) == 3, "expect the three theme-guide scenarios"
    for t in turns:
        times = [c["t"] for c in t["chunks"]]
        assert times == sorted(times), f"{t['turn_id']}: chunk times must not go backwards"
        assert t["utterance_end"] >= times[-1], f"{t['turn_id']}: utterance_end before last chunk"
        assert t["turn_id"] in gold, f"{t['turn_id']} has no gold label"
    assert any(g.get("retrieval_required") is False and g.get("reason") == "presentation_restructure" for g in gold.values())


def _corpus_sections() -> dict[str, int]:
    """Map Doc_ID -> number of '## ' sections, for markdown corpus files."""
    out: dict[str, int] = {}
    for f in (ROOT / "data" / "corpus").glob("Doc_*.md"):
        doc_id = "_".join(f.stem.split("_")[:2])
        out[doc_id] = sum(1 for line in f.read_text(encoding="utf-8").splitlines() if line.startswith("## "))
    return out


def test_gold_citations_point_at_real_corpus_sections() -> None:
    sections = _corpus_sections()
    if not sections:  # real corpus in another format: checked by the index tests instead
        return
    for split in (ROOT / "data" / "replay").iterdir():
        g = split / "gold.jsonl"
        if not g.exists():
            continue
        for line in g.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            for ids in json.loads(line).get("answer_chunks", {}).values():
                for cid in ids:
                    doc, _, sec = cid.partition("§")
                    assert doc in sections, f"{g.name}: {cid} cites unknown document {doc}"
                    assert sec.isdigit() and 1 <= int(sec) <= sections[doc], f"{g.name}: {cid} cites a missing section"


def test_no_secrets_committed() -> None:
    assert not (ROOT / ".env").exists(), ".env must never be committed; use .env.example"
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in gi
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    for key in ("GEMINI_API_KEY=", "OPENAI_API_KEY="):
        line = next(ln for ln in env_example.splitlines() if ln.startswith(key))
        assert line == key, f"{key} in .env.example must be empty"


# ---------------------------------------------------------------- autopilot
WORKFLOWS = ROOT / ".agents" / "workflows"


def test_autopilot_workflows_exist_and_fit_the_limit() -> None:
    for name in ("build-next", "unstick", "build-status"):
        f = WORKFLOWS / f"{name}.md"
        assert f.exists(), f"missing workflow /{name}"
        text = f.read_text(encoding="utf-8")
        assert text.startswith("---\ndescription:"), f"{f.name} needs 'description' front matter"
        assert len(text) < RULES_CHAR_LIMIT, f"{f.name} is too long"
    assert (ROOT / ".agents" / "rules" / "40-autopilot.md").exists()


def _sequence_step_files() -> list[str]:
    rows = (ROOT / "build" / "SEQUENCE.md").read_text(encoding="utf-8").splitlines()
    return [re.search(r"`(build/steps/[^`]+)`", r).group(1) for r in rows if re.match(r"\| \d\d \|", r)]


def test_every_sequenced_step_exists_and_is_tracked() -> None:
    steps = _sequence_step_files()
    assert len(steps) == 14, f"expected 14 steps, got {len(steps)}"
    state = (ROOT / "docs" / "PROJECT_STATE.md").read_text(encoding="utf-8")
    for s in steps:
        f = ROOT / s
        assert f.exists(), f"{s} listed in SEQUENCE.md but missing"
        assert "40-autopilot.md" in f.read_text(encoding="utf-8"), f"{s} lacks the autopilot header"
        assert s in state, f"{s} is not in the PROJECT_STATE.md status table"


def test_autopilot_support_docs_exist() -> None:
    for d in ("DECISIONS.md", "HUMAN_TASKS.md", "PROJECT_STATE.md", "COMPLIANCE.md"):
        assert (ROOT / "docs" / d).exists(), f"docs/{d} missing"
    assert "Decisions log" in (ROOT / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
