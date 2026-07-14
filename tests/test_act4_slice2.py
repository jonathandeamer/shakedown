"""Slice 2 Task 2 Act-IV contracts: the `HR` leaf renders as a bare
`<hr />` without entering the container-frame grammar. Verification-only —
feeds a token stream directly onto Puck's stack in Act-IV pop order and
runs `src_ir.act4.ACT` through the fast interpreter, without a
`shakespeare` subprocess."""

from __future__ import annotations

from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from src_ir import tokens
from src_ir.act4 import ACT as ACT4

STEP_LIMIT = 200_000


def test_hr_leaf_renders_self_closing_rule() -> None:
    state = InterpreterState()
    state.stacks[Char.PUCK] = [tokens.STREAM_END, tokens.HR]

    run_act(ACT4, state, step_limit=STEP_LIMIT)

    assert state.output_text() == "<hr />\n"


def test_code_block_leaf_keeps_final_linefeed_inside_pre() -> None:
    state = InterpreterState()
    state.stacks[Char.PUCK] = [
        tokens.STREAM_END,
        tokens.TEXT_END,
        45,
        45,
        45,
        tokens.CODE_BLOCK,
    ]

    run_act(ACT4, state, step_limit=STEP_LIMIT)

    assert state.output_text() == "<pre><code>---\n</code></pre>\n"
