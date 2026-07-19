from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.paths import markdown_pl

REPO = Path(__file__).parent.parent
# Fast IR parity entry — not the public shakespeare-backed ./shakedown.
SHAKEDOWN = REPO / "shakedown-parity"
MARKDOWN_PL = markdown_pl()
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"
NESTED_BLOCK_FIXTURES = (
    REPO / "tests" / "fixtures" / "architecture_spikes" / "nested_blocks"
)
SPAN_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "spans"
NESTED_BLOCK_BYTE_CASES = [
    (
        "list_quote_sibling",
        b"* alpha\n\n  > bravo\n* charlie\n",
        b"<ul>\n<li><p>alpha</p>\n\n<blockquote>\n  <p>bravo</p>\n"
        b"</blockquote></li>\n<li>charlie</li>\n</ul>\n",
    ),
    (
        "quote_list_then_paragraph",
        b"> * alpha\n> * bravo\n>\n> charlie\n",
        b"<blockquote>\n  <ul>\n<li>alpha</li>\n<li>bravo</li>\n</ul>\n\n"
        b"<p>charlie</p>\n</blockquote>\n",
    ),
    (
        "loose_list_quote",
        b"* alpha\n\n  > bravo\n\n* charlie\n",
        b"<ul>\n<li><p>alpha</p>\n\n<blockquote>\n  <p>bravo</p>\n"
        b"</blockquote></li>\n<li><p>charlie</p></li>\n</ul>\n",
    ),
    (
        "closes_to_text",
        b"* alpha\n\n  > bravo\n\noutside\n",
        b"<ul>\n<li><p>alpha</p>\n\n<blockquote>\n  <p>bravo</p>\n"
        b"</blockquote></li>\n</ul>\n\n<p>outside</p>\n",
    ),
]


def _first_diff(a: bytes, b: bytes) -> int | None:
    for idx, (left, right) in enumerate(zip(a, b, strict=False)):
        if left != right:
            return idx
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def _run(argv: list[str], input_bytes: bytes) -> bytes:
    result = subprocess.run(
        argv,
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=True,
    )
    return result.stdout


def _list_cases() -> list[Path]:
    return sorted(LIST_FIXTURES.glob("*.text"))


def _nested_block_cases() -> list[Path]:
    return sorted(NESTED_BLOCK_FIXTURES.glob("*.text"))


def _span_cases() -> list[Path]:
    return sorted(SPAN_FIXTURES.glob("*.text"))


def _interpret_ir_bytes(input_bytes: bytes) -> bytes:
    from scripts.splc.interpret import InterpreterState, run_act
    from src_ir.act1 import ACT as ACT1
    from src_ir.act2 import ACT as ACT2
    from src_ir.act3 import ACT as ACT3
    from src_ir.act4 import ACT as ACT4

    input_text = input_bytes.decode("utf-8")
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=500_000).state
    state = run_act(ACT2, state, step_limit=500_000).state
    state = run_act(ACT3, state, step_limit=500_000).state
    state = run_act(ACT4, state, step_limit=500_000).state
    return state.output_text().encode("utf-8")


@pytest.mark.parametrize("fixture", _list_cases(), ids=lambda path: path.stem)
def test_list_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
    input_bytes = fixture.read_bytes()
    expected = _run(["perl", str(MARKDOWN_PL)], input_bytes)

    # 1. Run IR interpreter
    interpret_actual = _interpret_ir_bytes(input_bytes)
    assert interpret_actual == expected, (
        f"IR Interpreter mismatch for list fixture {fixture.name}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual (IR)\n{interpret_actual.decode(errors='replace')}"
    )

    # 2. Run real binary
    actual = _run([str(SHAKEDOWN)], input_bytes)
    assert actual == expected, (
        f"Output mismatch for {fixture.name}; first diff: "
        f"{_first_diff(actual, expected)}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual\n{actual.decode(errors='replace')}"
    )


@pytest.mark.parametrize("fixture", _nested_block_cases(), ids=lambda path: path.stem)
def test_nested_block_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
    input_bytes = fixture.read_bytes()
    expected = _run(["perl", str(MARKDOWN_PL)], input_bytes)

    # 1. Run IR interpreter
    interpret_actual = _interpret_ir_bytes(input_bytes)
    assert interpret_actual == expected, (
        f"IR Interpreter mismatch for nested block fixture {fixture.name}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual (IR)\n{interpret_actual.decode(errors='replace')}"
    )

    # 2. Run real binary
    actual = _run([str(SHAKEDOWN)], input_bytes)
    assert actual == expected, (
        f"Output mismatch for {fixture.name}; first diff: "
        f"{_first_diff(actual, expected)}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual\n{actual.decode(errors='replace')}"
    )


@pytest.mark.parametrize(
    ("input_bytes", "expected"),
    [(input_bytes, expected) for _, input_bytes, expected in NESTED_BLOCK_BYTE_CASES],
    ids=[stem for stem, _, _ in NESTED_BLOCK_BYTE_CASES],
)
def test_nested_block_architecture_spike_emits_expected_bytes(
    input_bytes: bytes,
    expected: bytes,
) -> None:
    # 1. Run IR interpreter
    assert _interpret_ir_bytes(input_bytes) == expected
    # 2. Run real binary
    assert _run([str(SHAKEDOWN)], input_bytes) == expected


@pytest.mark.parametrize("fixture", _span_cases(), ids=lambda path: path.stem)
def test_span_architecture_spike_matches_checked_in_oracle_bytes(
    fixture: Path,
) -> None:
    input_bytes = fixture.read_bytes()
    expected = fixture.with_suffix(".expected").read_bytes()

    # 1. Run IR interpreter
    interpret_actual = _interpret_ir_bytes(input_bytes)
    assert interpret_actual == expected, (
        f"IR Interpreter mismatch for span fixture {fixture.name}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual (IR)\n{interpret_actual.decode(errors='replace')}"
    )

    # 2. Run real binary
    shakedown_output = _run([str(SHAKEDOWN)], input_bytes)
    assert shakedown_output == expected, (
        f"Output mismatch for {fixture.name}; first diff: "
        f"{_first_diff(shakedown_output, expected)}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual\n{shakedown_output.decode(errors='replace')}"
    )
