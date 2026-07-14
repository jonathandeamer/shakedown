"""
Markdown.mdtest suite — 23 fixtures from ~/mdtest/Markdown.mdtest/.

Each test feeds a .text fixture into ./shakedown and compares the output
against the corresponding .xhtml (preferred) or .html expected file.
"""

import re
import subprocess
from pathlib import Path

import pytest

from scripts.slice3_links import rewrite_task3_markdown

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
_FIXTURES_BY_NAME = {
    name: (input_path, expected_path) for name, input_path, expected_path in _FIXTURES
}
_IMPLEMENTED_FIXTURES = {
    "Amps and angle encoding",
    "Code Blocks",
    "Hard-wrapped paragraphs with list-like lines",
    "Horizontal rules",
    "Tabs",
}
_SLICE3_FIXTURES = {
    "Blockquotes with code blocks",
    "Hard-wrapped paragraphs with list-like lines",
    "Images",
    "Inline HTML (Simple)",
    "Inline HTML comments",
    "Links, inline style",
    "Links, reference style",
    "Links, shortcut references",
    "Literal quotes in titles",
    "Strong and em together",
}

_SLICE3_TASK3_FIXTURES = (
    "Links, inline style",
    "Links, reference style",
    "Links, shortcut references",
    "Images",
    "Literal quotes in titles",
)


def _fixture_params() -> list[object]:
    """Return pytest params, skipping fixtures not yet shipped by the roadmap."""
    params = []
    for fixture in _FIXTURES:
        name = fixture[0]
        if name in _IMPLEMENTED_FIXTURES:
            params.append(pytest.param(*fixture, id=name))
        else:
            params.append(
                pytest.param(
                    *fixture,
                    id=name,
                    marks=pytest.mark.skip(
                        reason="fixture not yet shipped by the staged roadmap"
                    ),
                )
            )
    return params


def _run_acts(input_text: str, through_act: int) -> str | list[int]:
    from scripts.splc.interpret import InterpreterState, run_act
    from scripts.splc.ir import Char
    from src_ir import tokens
    from src_ir.act1 import ACT as ACT1
    from src_ir.act2 import ACT as ACT2
    from src_ir.act3 import ACT as ACT3
    from src_ir.act4 import ACT as ACT4

    state = InterpreterState(input_text=rewrite_task3_markdown(input_text))
    acts = (ACT1, ACT2, ACT3, ACT4)
    for act in acts[:through_act]:
        state = run_act(act, state, step_limit=500_000).state
    if through_act == 4:
        return state.output_text()
    stream = list(reversed(state.stacks[Char.PUCK]))
    if stream and stream[-1] == tokens.STREAM_END:
        stream.pop()
    return stream


def _interpret_ir(input_text: str) -> str:
    output = _run_acts(input_text, through_act=4)
    assert isinstance(output, str)
    return output


@pytest.mark.parametrize("name,input_path,expected_path", _fixture_params())
def test_mdtest(name: str, input_path: Path, expected_path: Path) -> None:
    input_text = input_path.read_text()
    expected = expected_path.read_text()
    norm_expected = _normalize(expected)
    if name == "Auto links":
        norm_expected = _decode_entities(norm_expected)

    # 1. Run the fast IR interpreter first
    interpret_actual = _interpret_ir(input_text)
    norm_interpret = _normalize(interpret_actual)
    if name == "Auto links":
        norm_interpret = _decode_entities(norm_interpret)
    assert norm_interpret == norm_expected, (
        f"IR Interpreter output mismatch for '{name}'\n"
        f"--- expected\n{norm_expected}\n"
        f"+++ actual (IR)\n{norm_interpret}"
    )

    # 2. Run the real binary to prove parity
    result = subprocess.run(
        [str(BINARY)],
        input=input_text,
        capture_output=True,
        text=True,
    )
    actual = result.stdout
    norm_actual = _normalize(actual)
    if name == "Auto links":
        norm_actual = _decode_entities(norm_actual)

    assert norm_actual == norm_expected, (
        f"Binary output mismatch for '{name}'\n"
        f"--- expected\n{norm_expected}\n"
        f"+++ actual (Binary)\n{norm_actual}"
    )


@pytest.mark.parametrize("name", _SLICE3_TASK3_FIXTURES)
def test_slice3_task3_fixture_red_contract(name: str) -> None:
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize(actual) == _normalize(expected_path.read_text())
