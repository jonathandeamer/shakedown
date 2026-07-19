"""The debug target dumps the inter-act token stream as integers."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from scripts.splc.token_decode import decode_stream
from scripts.splc.token_structure import validate_stream
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2

REPO = Path(__file__).parent.parent
DEBUG_WRAPPER = REPO / "shakedown-debug"
AMPS_FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Amps and angle encoding.text"
)


def test_debug_target_dumps_integer_token_stream() -> None:
    result = subprocess.run(
        [str(DEBUG_WRAPPER)],
        input=AMPS_FIXTURE.read_bytes(),
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    lines = result.stdout.decode().strip().splitlines()
    assert len(lines) > 10
    values = [int(line) for line in lines]
    # Production Act IV emits <p> first for this fixture (Slice 1 is
    # byte-identical), so the first popped stream value must be the
    # PARAGRAPH_OPEN token.
    assert values[0] == 1


BASELINES = REPO / "tests" / "fixtures" / "token_stream"
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"
LIST_BASELINES = BASELINES / "lists"
NESTED_BLOCK_FIXTURES = (
    REPO / "tests" / "fixtures" / "architecture_spikes" / "nested_blocks"
)
NESTED_BLOCK_BASELINES = BASELINES / "nested_blocks"
SPAN_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "spans"
SPAN_BASELINES = BASELINES / "spans"
STEP_LIMIT = 200_000


def _reviewed_dump(stem: str) -> list[int]:
    return [
        int(line)
        for line in (NESTED_BLOCK_BASELINES / f"{stem}.dump").read_text().splitlines()
    ]


def _reviewed_debug_dump(stem: str) -> bytes:
    values = _reviewed_dump(stem)
    assert values[-1] == tokens.STREAM_END
    return "".join(f"{value}\n" for value in values[:-1]).encode()


def _reviewed_span_dump(stem: str) -> list[int]:
    return [
        int(line) for line in (SPAN_BASELINES / f"{stem}.dump").read_text().splitlines()
    ]


def _reviewed_span_debug_dump(stem: str) -> bytes:
    values = _reviewed_span_dump(stem)
    assert values[-1] == tokens.STREAM_END
    return "".join(f"{value}\n" for value in values[:-1]).encode()


def _act2_carrier_stream(stem: str) -> list[int]:
    state = InterpreterState(
        input_text=(NESTED_BLOCK_FIXTURES / f"{stem}.text").read_text()
    )
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    state = run_act(ACT2, state, step_limit=STEP_LIMIT).state

    stream: list[int] = []
    while state.stacks[Char.PUCK]:
        value = state.stacks[Char.PUCK].pop()
        stream.append(value)
        if value == tokens.STREAM_END:
            break
    return stream


def _dump(input_bytes: bytes) -> bytes:
    result = subprocess.run(
        [str(DEBUG_WRAPPER)],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    return result.stdout


def test_dump_matches_blessed_amps_baseline() -> None:
    """G2 gate: blessed by the P1 plan; P2 and later slices re-bless
    deliberately when the vocabulary grows, never casually."""
    assert _dump(AMPS_FIXTURE.read_bytes()) == (BASELINES / "amps.dump").read_bytes()


def test_dump_matches_blessed_short_baseline() -> None:
    assert _dump(b"hello\n\nworld\n") == (BASELINES / "short.dump").read_bytes()


def test_dump_nested_one_level_matches_blessed_p2_baseline() -> None:
    fixture = LIST_FIXTURES / "nested_one_level.text"
    baseline = (LIST_BASELINES / "nested_one_level.dump").read_bytes()
    dump = _dump(fixture.read_bytes())

    assert dump == baseline
    values = [int(line) for line in dump.decode().splitlines()]
    child_open_index = values.index(tokens.LIST_OPEN, 1)
    # Parent stays open into the nest; TEXT_END ends item text (Slice-5 A17).
    assert values[child_open_index - 1] == tokens.TEXT_END
    nested_close_index = values.index(tokens.LIST_CLOSE)
    assert values[nested_close_index + 1] == tokens.ITEM_CLOSE
    assert values[nested_close_index + 2] == tokens.LIST_ITEM


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in LIST_FIXTURES.glob("*.text")),
)
def test_dump_matches_blessed_list_baseline(stem: str) -> None:
    """G2 gate over the P2 list vocabulary: blessed by the P2 plan after
    hand-review; later slices re-bless deliberately, never casually."""
    fixture = LIST_FIXTURES / f"{stem}.text"
    assert _dump(fixture.read_bytes()) == (LIST_BASELINES / f"{stem}.dump").read_bytes()


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in NESTED_BLOCK_FIXTURES.glob("*.text")),
)
def test_dump_matches_blessed_nested_block_baseline(stem: str) -> None:
    fixture = NESTED_BLOCK_FIXTURES / f"{stem}.text"
    assert _dump(fixture.read_bytes()) == _reviewed_debug_dump(stem)


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in SPAN_FIXTURES.glob("*.text")),
)
def test_dump_matches_reviewed_span_baseline(stem: str) -> None:
    fixture = SPAN_FIXTURES / f"{stem}.text"
    assert _dump(fixture.read_bytes()) == _reviewed_span_debug_dump(stem)


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in NESTED_BLOCK_FIXTURES.glob("*.text")),
)
def test_act2_carrier_matches_reviewed_nested_block_dump(stem: str) -> None:
    assert _act2_carrier_stream(stem) == _reviewed_dump(stem)


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in NESTED_BLOCK_FIXTURES.glob("*.text")),
)
def test_act2_nested_block_carrier_has_one_terminal_sentinel(stem: str) -> None:
    stream = _act2_carrier_stream(stem)

    assert stream[-1] == tokens.STREAM_END
    assert stream.count(tokens.STREAM_END) == 1
    validate_stream(decode_stream(stream[:-1]))


def test_act2_distinguishes_quote_sibling_item_looseness() -> None:
    sibling = _act2_carrier_stream("list_quote_sibling")
    loose = _act2_carrier_stream("loose_list_quote")

    assert sibling != loose
    assert sibling == [
        4,
        1,
        5,
        2,
        1,
        97,
        108,
        112,
        104,
        97,
        0,
        7,
        1,
        98,
        114,
        97,
        118,
        111,
        0,
        8,
        15,
        5,
        1,
        1,
        99,
        104,
        97,
        114,
        108,
        105,
        101,
        0,
        15,
        6,
        -1,
    ]
    assert loose == [
        4,
        1,
        5,
        2,
        1,
        97,
        108,
        112,
        104,
        97,
        0,
        7,
        1,
        98,
        114,
        97,
        118,
        111,
        0,
        8,
        15,
        5,
        2,
        1,
        99,
        104,
        97,
        114,
        108,
        105,
        101,
        0,
        15,
        6,
        -1,
    ]
