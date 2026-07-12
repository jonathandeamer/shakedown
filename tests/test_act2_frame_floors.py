"""Act II frame-floor contract tests: prove that Macbeth's open-list frame
stack and Horatio's looseness side channel (`src_ir/act2.py` module
docstring) never pop below whatever content already sat beneath their floor
on entry to Act II, and that content is restored unchanged once Act II
halts, across every list spike case. Verification-only, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §2;
runs through `scripts.splc.interpret.run_act`, never `./shakedown`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.splc.contracts import (
    StackSnapshot,
    assert_floor_respected,
    assert_prefix_preserved,
)
from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2

REPO = Path(__file__).parent.parent
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"

STEP_LIMIT = 200_000

# Macbeth carries the open-list frame sentinels; Horatio carries the
# per-item looseness side channel. Both are borrowed above whatever
# cross-act payload already sits on the stack (see src_ir/act2.py).
_PRIOR_PAYLOAD = (7, 13, 42)
_TRACKED_CHARS = (Char.MACBETH, Char.HORATIO)


@dataclass
class _MinDepthObserver:
    """Records the minimum stack depth reached for one tracked char."""

    char: Char
    min_depth: int

    def on_push(self, char: Char, value: int, stack_after: list[int]) -> None:
        if char is self.char:
            self.min_depth = min(self.min_depth, len(stack_after))

    def on_pop(self, char: Char, value: int, stack_after: list[int]) -> None:
        if char is self.char:
            self.min_depth = min(self.min_depth, len(stack_after))


@pytest.mark.parametrize("char", _TRACKED_CHARS, ids=lambda c: c.value)
@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in LIST_FIXTURES.glob("*.text")),
)
def test_act2_restores_frame_and_carrier_floors(stem: str, char: Char) -> None:
    input_text = (LIST_FIXTURES / f"{stem}.text").read_text()
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state

    prior_payload = list(_PRIOR_PAYLOAD)
    state.stacks[char] = prior_payload + state.stacks[char]
    before = StackSnapshot(char=char, values=tuple(prior_payload))

    observer = _MinDepthObserver(char=char, min_depth=before.floor)

    result = run_act(ACT2, state, step_limit=STEP_LIMIT, observer=observer)

    assert_floor_respected(char, before.floor, observer.min_depth)
    assert_prefix_preserved(before, result.state.stacks[char])
