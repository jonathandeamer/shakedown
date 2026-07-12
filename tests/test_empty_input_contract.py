"""Empty-input contract: record the current real-runtime failure and the
matching fast-interpreter diagnostic for empty stdin, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §2
("Empty stdin becomes a mandatory interpreter and real-wrapper case").

This test only records the currently observed behavior — Act I underflows
popping Puck's stack while testing for a final cauldron dreg that empty
input never pushed. It is deliberately not a fix: production behavior stays
unchanged until the first feature plan allowed to change it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.splc.interpret import InterpreterState, StackUnderflow, run_act
from scripts.splc.ir import Char
from src_ir.act1 import ACT as ACT1

REPO = Path(__file__).parent.parent
WRAPPER = REPO / "shakedown"

STEP_LIMIT = 200_000


def test_real_wrapper_fails_on_empty_stdin() -> None:
    result = subprocess.run(
        [str(WRAPPER)],
        input=b"",
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert b"SPL runtime error: Tried to pop from an empty stack." in result.stderr
    assert result.stdout == b""


def test_fast_interpreter_diagnoses_empty_input_underflow() -> None:
    state = InterpreterState(input_text="")

    with pytest.raises(StackUnderflow) as excinfo:
        run_act(ACT1, state, step_limit=STEP_LIMIT)

    diagnostic = excinfo.value.diagnostic
    assert diagnostic.act == 1
    assert diagnostic.char is Char.PUCK
