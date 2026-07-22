"""Fast-interpreter parity: the Amps/short token dumps and the six list
spike inputs, run through `scripts.splc.interpret.run_act` across Acts
I-III plus the debug Act IV shadow, must equal the committed dump
baselines in tests/fixtures/token_stream/. This is a verification-only
companion to the real-interpreter gates in test_token_dump.py and
test_architecture_spikes.py, which stay in place unchanged."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.paths import mdtest_fixtures_dir
from scripts.splc.interpret import InterpreterState, run_act
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.debug_act4 import ACT as DEBUG_ACT

REPO = Path(__file__).parent.parent
BASELINES = REPO / "tests" / "fixtures" / "token_stream"
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"
LIST_BASELINES = BASELINES / "lists"
AMPS_FIXTURE = mdtest_fixtures_dir() / "Amps and angle encoding.text"

STEP_LIMIT = 200_000


def _fast_dump(input_text: str) -> bytes:
    state = InterpreterState(input_text=input_text, resolve_short_circuit=False)
    for act_module in (ACT1, ACT2, ACT3, DEBUG_ACT):
        result = run_act(act_module, state, step_limit=STEP_LIMIT)
        state = result.state
    return state.output_text().encode()


def test_fast_interpreter_matches_blessed_amps_baseline() -> None:
    input_text = AMPS_FIXTURE.read_text()
    assert _fast_dump(input_text) == (BASELINES / "amps.dump").read_bytes()


def test_fast_interpreter_matches_blessed_short_baseline() -> None:
    assert _fast_dump("hello\n\nworld\n") == (BASELINES / "short.dump").read_bytes()


def test_fast_interpreter_nested_one_level_matches_blessed_p2_baseline() -> None:
    fixture = LIST_FIXTURES / "nested_one_level.text"
    baseline = (LIST_BASELINES / "nested_one_level.dump").read_bytes()
    dump = _fast_dump(fixture.read_text())

    assert dump == baseline
    values = [int(line) for line in dump.decode().splitlines()]
    child_open_index = values.index(tokens.LIST_OPEN, 1)
    # Nest-open keeps the parent item open (TEXT_END only); parent ITEM_CLOSE
    # is emitted solely on outdent after the nested LIST_CLOSE (Slice-5 2a).
    assert values[child_open_index - 1] == tokens.TEXT_END
    child_close_index = values.index(tokens.LIST_CLOSE)
    assert values[child_close_index + 1] == tokens.ITEM_CLOSE


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in LIST_FIXTURES.glob("*.text")),
)
def test_fast_interpreter_matches_blessed_list_baseline(stem: str) -> None:
    fixture = LIST_FIXTURES / f"{stem}.text"
    baseline = LIST_BASELINES / f"{stem}.dump"
    assert _fast_dump(fixture.read_text()) == baseline.read_bytes()
