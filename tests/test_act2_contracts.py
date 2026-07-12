"""Act II stack-contract tests: prove the list-looseness side channel on
Horatio's stack (`src_ir/act2.py` FRAME_STAGE_SIDE_*) only ever touches the
content it pushes itself, regardless of what already sat beneath its floor.
Verification-only, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §2; runs
through `scripts.splc.interpret.run_act`, never `./shakedown`."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.splc.contracts import StackSnapshot, assert_prefix_preserved
from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2

REPO = Path(__file__).parent.parent
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"

STEP_LIMIT = 200_000


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in LIST_FIXTURES.glob("*.text")),
)
def test_act2_preserves_prior_payload_on_horatio_stack(stem: str) -> None:
    input_text = (LIST_FIXTURES / f"{stem}.text").read_text()
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state

    prior_payload = [7, 13, 42]
    state.stacks[Char.HORATIO] = prior_payload + state.stacks[Char.HORATIO]
    before = StackSnapshot(char=Char.HORATIO, values=tuple(prior_payload))

    result = run_act(ACT2, state, step_limit=STEP_LIMIT)

    assert_prefix_preserved(before, result.state.stacks[Char.HORATIO])
