"""Empty-input contract: record the current real-runtime behavior and the
matching fast-interpreter state for empty stdin, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §2
("Empty stdin becomes a mandatory interpreter and real-wrapper case").

This test only records the currently observed behavior. The earlier Act I
underflow contract is no longer true: the wrapper now exits successfully with
the current trailing newline, and the fast interpreter returns without a
stack error while producing no output.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1

REPO = Path(__file__).parent.parent
WRAPPER = REPO / "shakedown"

STEP_LIMIT = 200_000


def test_real_wrapper_currently_returns_blank_line_on_empty_stdin() -> None:
    result = subprocess.run(
        [str(WRAPPER)],
        input=b"",
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert b"SPL runtime error:" not in result.stderr
    assert result.stdout == b"\n"


def test_fast_interpreter_returns_without_output_on_empty_input() -> None:
    state = InterpreterState(input_text="")
    result = run_act(ACT1, state, step_limit=STEP_LIMIT)

    assert result.state.output == []
    assert result.state.input_pos == 0
