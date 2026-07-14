"""Slice 2 Task 2 Act-II contracts: horizontal-rule recognition emits
`tokens.HR`, rejected candidates replay as paragraph text, and
tab-expanded four-space candidates are reserved for the Task-3 code-block
leaf rather than becoming an HR. Verification-only — runs `src_ir.act1.ACT`
then `src_ir.act2.ACT` through the fast interpreter and decodes the forward
token stream Act II hands to Act III, without a `shakespeare` subprocess."""

from __future__ import annotations

import pytest

from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from scripts.splc.token_decode import decode_stream
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2

STEP_LIMIT = 200_000


def _act2_stream(input_text: str) -> list[int]:
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    state = run_act(ACT2, state, step_limit=STEP_LIMIT).state
    stream: list[int] = []
    while state.stacks[Char.PUCK]:
        value = state.stacks[Char.PUCK].pop()
        if value == tokens.STREAM_END:
            break
        stream.append(value)
    return stream


@pytest.mark.parametrize(
    "candidate",
    ["---\n\n", "- - -\n\n", "***\n\n", "_ _ _\n\n", "  ---\n\n"],
    ids=["dashes", "spaced-dashes", "stars", "spaced-underscores", "two-space-indent"],
)
def test_hr_markers_emit_hr_token(candidate: str) -> None:
    decoded = decode_stream(_act2_stream(candidate))
    assert decoded[0].code == tokens.HR


def test_three_space_indent_hr_candidate_remains_paragraph() -> None:
    decoded = decode_stream(_act2_stream("   ---\n\n"))
    assert decoded[0].code == tokens.PARA
    assert decoded[0].text is not None
    assert "---" in decoded[0].text


def test_tab_expanded_hr_candidate_becomes_code_block_not_hr() -> None:
    decoded = decode_stream(_act2_stream("\t---\n\n"))
    assert decoded[0].code != tokens.HR
    assert decoded[0].code == tokens.CODE_BLOCK
