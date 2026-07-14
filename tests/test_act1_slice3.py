"""Slice-3 Act I contracts land task by task."""

from __future__ import annotations

import pytest

from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.cast import HECATE

STEP_LIMIT = 200_000


def _run_act1(input_text: str) -> str:
    state = InterpreterState(input_text=input_text)
    run_act(ACT1, state, step_limit=STEP_LIMIT)
    return "".join(chr(code) for code in reversed(state.stacks[HECATE]))


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        (
            'Body [label][ref].\n\n   [REF]: </dest/> "Title"\n',
            "Body [label][ref].\n\n",
        ),
        (
            'Body [label][ref].\n\n   [ref]: /dest/\n   "Wrapped title"\n',
            "Body [label][ref].\n\n",
        ),
    ],
    ids=["three-space-case-folded-angle-destination", "wrapped-title-line"],
)
def test_act1_strips_valid_reference_definitions(
    input_text: str, expected: str
) -> None:
    assert _run_act1(input_text) == expected
