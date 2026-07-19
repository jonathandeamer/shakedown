"""Inventory pure-SPL gaps vs the slice3 Python rewrite.

Witnesses for fixtures that still require ``rewrite_task3_markdown`` on the
IR/production path until Tasks 2–5 port strip/resolve into SPL.
"""

from __future__ import annotations

import pytest

from scripts.paths import mdtest_fixtures_dir
from scripts.runtime_constants import DOCUMENTATION_STEP_LIMIT
from scripts.slice3_links import rewrite_task3_markdown
from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4
from tests.test_mdtest import (
    _FIXTURES_BY_NAME,
    _expected_fixture_output,
    _normalize_fixture_output,
)

PURE_SPL_REWRITE_RETIRED = False  # Task 5 flips to True

_REWRITE_TOUCHED = (
    "Amps and angle encoding",
    "Images",
    "Links, inline style",
    "Links, reference style",
    "Links, shortcut references",
    "Literal quotes in titles",
    "Markdown Documentation - Basics",
    "Markdown Documentation - Syntax",
)


def _interpret_ir_raw(input_text: str) -> str:
    """IR without Python rewrite (exposes SPL-pure gaps)."""
    state = InterpreterState(input_text=input_text)
    for act in (ACT1, ACT2, ACT3, ACT4):
        state = run_act(act, state, step_limit=DOCUMENTATION_STEP_LIMIT).state
    return state.output_text()


def test_rewrite_touches_expected_fixture_set() -> None:
    d = mdtest_fixtures_dir()
    touched = sorted(
        p.stem
        for p in d.glob("*.text")
        if rewrite_task3_markdown(p.read_text()) != p.read_text()
    )
    assert touched == sorted(_REWRITE_TOUCHED)


@pytest.mark.parametrize("name", _REWRITE_TOUCHED)
def test_raw_ir_matches_oracle_without_rewrite(name: str) -> None:
    if not PURE_SPL_REWRITE_RETIRED:
        pytest.xfail("SPL-pure: rewrite still required on production path")
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    input_text = input_path.read_text()
    expected = _normalize_fixture_output(
        name, _expected_fixture_output(name, input_path, expected_path)
    )
    actual = _normalize_fixture_output(name, _interpret_ir_raw(input_text))
    assert actual == expected
