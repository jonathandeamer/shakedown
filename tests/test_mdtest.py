"""
Markdown.mdtest suite — 23 fixtures from ~/mdtest/Markdown.mdtest/.

Each test feeds a .text fixture into ./shakedown and compares the output
against the corresponding .xhtml (preferred) or .html expected file.
"""

import re
import subprocess
from pathlib import Path

import pytest

FIXTURES_DIR = Path.home() / "mdtest" / "Markdown.mdtest"
BINARY = Path(__file__).parent.parent / "shakedown"


def _normalize(text: str) -> str:
    """Trim each line, collapse consecutive blank lines, strip the whole result."""
    lines = text.split("\n")
    out: list[str] = []
    prev_blank = False
    for line in lines:
        line = line.strip()
        if line == "":
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(line)
            prev_blank = False
    return "\n".join(out).strip()


def _decode_entities(text: str) -> str:
    """Decode HTML numeric character references (&#NNN; and &#xNN;).

    Used for the Auto links test only: Markdown.pl randomly encodes email
    chars as decimal or hex entities, so we normalise both sides before
    comparing.
    """
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)
    return text


def _collect_fixtures() -> list[tuple[str, Path, Path]]:
    """Return (name, input_path, expected_path) for every fixture."""
    cases = []
    for text_path in sorted(FIXTURES_DIR.glob("*.text")):
        name = text_path.stem
        xhtml = text_path.with_suffix(".xhtml")
        html = text_path.with_suffix(".html")
        expected_path = xhtml if xhtml.exists() else html
        if expected_path.exists():
            cases.append((name, text_path, expected_path))
    return cases


_FIXTURES = _collect_fixtures()


@pytest.mark.parametrize(
    "name,input_path,expected_path", _FIXTURES, ids=[f[0] for f in _FIXTURES]
)
def test_mdtest(name: str, input_path: Path, expected_path: Path) -> None:
    input_text = input_path.read_text()
    expected = expected_path.read_text()

    result = subprocess.run(
        [str(BINARY)],
        input=input_text,
        capture_output=True,
        text=True,
    )
    actual = result.stdout

    norm_expected = _normalize(expected)
    norm_actual = _normalize(actual)

    if name == "Auto links":
        norm_expected = _decode_entities(norm_expected)
        norm_actual = _decode_entities(norm_actual)

    assert norm_actual == norm_expected, (
        f"Output mismatch for '{name}'\n"
        f"--- expected\n{norm_expected}\n"
        f"+++ actual\n{norm_actual}"
    )
