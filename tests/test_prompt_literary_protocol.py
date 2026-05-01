from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).parent.parent
PROTOCOL = REPO / "docs" / "superpowers" / "notes" / "spl-literary-protocol.md"
ACTIVE_PROMPT = REPO / "docs" / "prompt-shakedown.md"
CLAUDE = REPO / "CLAUDE.md"
ROADMAP = REPO / "docs" / "superpowers" / "plans" / "plan-roadmap.md"

REQUIRED_DOCS = {
    "docs/spl/literary-spec.md",
    "docs/spl/style-lexicon.md",
    "docs/spl/codegen-style-guide.md",
    "src/literary.toml",
}

SPL_TOUCH_RE = re.compile(
    r"(src/\*\.spl|src/[^`\s]+\.spl|scripts/assemble\.py|codegen)",
    re.IGNORECASE,
)


def _read(path: Path) -> str:
    return path.read_text()


def _active_plan_paths() -> list[Path]:
    paths: list[Path] = []
    for line in _read(ROADMAP).splitlines():
        if not re.search(r"\|\s*in flight\s*(?:\||$)", line):
            continue
        path_matches = re.findall(r"`(docs/superpowers/plans/[^`]+\.md)`", line)
        assert path_matches, f"in-flight roadmap row lacks exact plan path: {line}"
        paths.extend(REPO / path for path in path_matches)
    return paths


def test_protocol_note_exists_and_names_required_inputs() -> None:
    text = _read(PROTOCOL)
    for required in REQUIRED_DOCS:
        assert required in text
    assert "Classify new prose" in text
    assert "Critical" in text
    assert "Stable Utility" in text
    assert "Recall" in text


def test_active_prompt_loads_protocol_note() -> None:
    text = _read(ACTIVE_PROMPT)
    assert "@docs/superpowers/notes/spl-literary-protocol.md" in text


def test_claude_tells_prompt_authors_to_use_protocol() -> None:
    text = _read(CLAUDE)
    assert "docs/superpowers/notes/spl-literary-protocol.md" in text
    assert "SPL-changing prompts" in text
    assert "Controlled SPL prose belongs in `src/literary.toml`" in text
    assert "`@LIT.` placeholders" in text
    assert "Do not hand-edit" in text
    assert "`shakedown.spl` for literary surface changes" in text


def test_in_flight_roadmap_row_names_exact_plan_path() -> None:
    paths = _active_plan_paths()
    assert len(paths) == 1
    assert paths[0].exists()


def test_roadmap_names_spl_literary_protocol() -> None:
    assert "docs/superpowers/notes/spl-literary-protocol.md" in _read(ROADMAP)


def test_in_flight_spl_plans_reference_protocol_or_required_docs() -> None:
    for path in _active_plan_paths():
        text = _read(path)
        if not SPL_TOUCH_RE.search(text):
            continue
        has_protocol = "docs/superpowers/notes/spl-literary-protocol.md" in text
        has_docs = all(required in text for required in REQUIRED_DOCS)
        assert has_protocol or has_docs, path
        required_tests = {
            "tests/test_literary_compliance.py",
            "tests/test_literary_toml_schema.py",
            "tests/test_assemble.py",
            "tests/test_codegen_html.py",
            "tests/test_mdtest.py -k 'Amps and angle'",
        }
        missing_tests = {
            required for required in required_tests if required not in text
        }
        assert not missing_tests, (path, missing_tests)
