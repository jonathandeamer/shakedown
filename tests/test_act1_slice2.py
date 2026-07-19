"""Slice 2 Task 1 Act-I contracts: normalized final newline, four-column tab
expansion, and no unconditional trailing-line stripping. Verification-only —
runs `src_ir.act1.ACT` through the fast interpreter and inspects the forward
glyph stream Act I hands to Act II, without a `shakespeare` subprocess."""

from __future__ import annotations

from scripts.paths import mdtest_fixtures_dir
from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.cast import HECATE, HORATIO

CODE_BLOCKS_FIXTURE = mdtest_fixtures_dir() / "Code Blocks.text"

STEP_LIMIT = 200_000


def _run_act1(input_text: str) -> tuple[str, int]:
    state = InterpreterState(input_text=input_text)
    run_act(ACT1, state, step_limit=STEP_LIMIT)
    stream = "".join(chr(code) for code in reversed(state.stacks[HECATE]))
    return stream, state.values[HORATIO]


def _expected_normalized(input_text: str) -> str:
    """Reference normalization: expand tabs to four-column stops, then force
    the carrier to end in exactly two newlines without dropping any content."""
    lines = input_text.split("\n")
    expanded_lines = []
    for line in lines:
        column = 0
        out_chars: list[str] = []
        for ch in line:
            if ch == "\t":
                spaces = 4 - (column % 4)
                out_chars.append(" " * spaces)
                column += spaces
            else:
                out_chars.append(ch)
                column += 1
        expanded_lines.append("".join(out_chars))
    body = "\n".join(expanded_lines).rstrip("\n")
    return body + "\n\n"


def test_final_newline_normalization_retains_every_line() -> None:
    input_text = "one\n\ntwo\n"
    stream, count = _run_act1(input_text)
    assert stream == _expected_normalized(input_text)
    assert stream.endswith("\n\n")
    assert not stream.endswith("\n\n\n")
    assert "one" in stream
    assert "two" in stream
    assert len(stream) == count


def test_tab_expansion_to_next_four_column_stop() -> None:
    input_text = "\tX\n \tY\n  \tZ\n   \tQ\n"
    stream, count = _run_act1(input_text)
    expected = _expected_normalized(input_text)
    assert stream == expected
    assert stream == "    X\n    Y\n    Z\n    Q\n\n"
    assert len(stream) == count


def test_code_blocks_ending_is_not_stripped_and_trailing_spaces_survive() -> None:
    data = CODE_BLOCKS_FIXTURE.read_text()
    idx = data.index("the lines in this block")
    start = data.rfind("\n\n", 0, idx) + 2
    tail = data[start:]
    assert not tail.endswith("\n"), (
        "fixture snippet must exercise the no-final-newline path"
    )

    stream, count = _run_act1(tail)

    assert stream == _expected_normalized(tail)
    assert "all contain trailing spaces  \n" in stream
    assert "code block on the last line" in stream
    assert stream.endswith("\n\n")
    assert not stream.endswith("\n\n\n")
    assert len(stream) == count
