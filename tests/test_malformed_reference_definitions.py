"""Malformed reference definitions must render as literal paragraphs (oracle parity)."""

from __future__ import annotations

import pytest

from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4

STEP_LIMIT = 200_000

# Verified against `perl ~/markdown/Markdown.pl` on 2026-07-22.
CASES = [
    pytest.param("[not]:\n", "<p>[not]:</p>\n", id="empty-url"),
    pytest.param("[not]:   \n", "<p>[not]:   </p>\n", id="empty-url-spaces"),
    pytest.param(
        "[]: destination\n",
        "<p>[]: destination</p>\n",
        id="empty-label",
    ),
    pytest.param(
        "[x] : destination\n",
        "<p>[x] : destination</p>\n",
        id="space-before-colon",
    ),
]


def _render(src: str) -> str:
    state = InterpreterState(input_text=src)
    for act in (ACT1, ACT2, ACT3, ACT4):
        state = run_act(act, state, step_limit=STEP_LIMIT).state
    return state.output_text()


@pytest.mark.parametrize("src,expected", CASES)
def test_malformed_reference_definition_renders_literally(
    src: str, expected: str
) -> None:
    assert _render(src) == expected
