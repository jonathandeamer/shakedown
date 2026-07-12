"""Act III span-contract tests for the buffered-scan spike.

Verification-only, per the active 2026-07-12 span architecture spike plan:
run Acts I-III through the IR interpreter, prove the carrier stream stays
structurally valid across Act III, and pin the still-red rendered paragraph
contracts before the buffered scanner lands.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.splc.contracts import StackSnapshot, assert_prefix_preserved
from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from scripts.splc.token_decode import DecodedToken, decode_stream
from scripts.splc.token_structure import validate_stream
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3

REPO = Path(__file__).parent.parent
SPAN_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "spans"
STEP_LIMIT = 200_000
_BORROWED_PREFIX = (7, 13, 42)


def _run_to_act2(stem: str) -> InterpreterState:
    input_text = (SPAN_FIXTURES / f"{stem}.text").read_text()
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    return run_act(ACT2, state, step_limit=STEP_LIMIT).state


def _run_to_act3(stem: str) -> InterpreterState:
    state = _run_to_act2(stem)
    return run_act(ACT3, state, step_limit=STEP_LIMIT).state


def _run_to_act3_with_prefix(stem: str) -> tuple[StackSnapshot, InterpreterState]:
    state = _run_to_act2(stem)
    state.stacks[Char.PUCK] = list(_BORROWED_PREFIX) + state.stacks[Char.PUCK]
    snapshot = StackSnapshot(char=Char.PUCK, values=_BORROWED_PREFIX)
    return snapshot, run_act(ACT3, state, step_limit=STEP_LIMIT).state


def _carrier_stream(state: InterpreterState) -> list[int]:
    stream: list[int] = []
    while state.stacks[Char.PUCK]:
        value = state.stacks[Char.PUCK].pop()
        stream.append(value)
        if value == tokens.STREAM_END:
            break
    assert stream
    assert stream[-1] == tokens.STREAM_END
    assert stream.count(tokens.STREAM_END) == 1
    return stream


def _decode_carrier(state: InterpreterState) -> list[DecodedToken]:
    stream = _carrier_stream(state)
    decoded = decode_stream(stream[:-1])
    validate_stream(decoded)
    return decoded


def _stack_carrier_from_floor(
    state: InterpreterState, snapshot: StackSnapshot
) -> list[int]:
    stream = state.stacks[Char.PUCK][snapshot.floor :]
    assert stream
    assert stream[0] == tokens.STREAM_END
    return stream


def _rendered_paragraph_html(stem: str) -> str:
    expected = (SPAN_FIXTURES / f"{stem}.expected").read_text()
    assert expected.startswith("<p>")
    assert expected.endswith("</p>\n")
    return expected.removeprefix("<p>").removesuffix("</p>\n")


def _non_text_shape(decoded: list[DecodedToken]) -> list[tuple[int, tuple[int, ...]]]:
    return [(token.code, token.payloads) for token in decoded]


def _paragraph_text(decoded: list[DecodedToken]) -> str:
    assert len(decoded) == 1
    token = decoded[0]
    assert token.code == tokens.PARA
    assert token.text is not None
    return token.text


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in SPAN_FIXTURES.glob("*.text")),
)
def test_act3_preserves_span_fixture_structural_stream(stem: str) -> None:
    before = _decode_carrier(_run_to_act2(stem))
    after = _decode_carrier(_run_to_act3(stem))

    # Task 2 proves Act III can rewrite paragraph text later while leaving the
    # block-level carrier shape intact across the buffered scan boundary.
    assert _non_text_shape(after) == _non_text_shape(before)


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in SPAN_FIXTURES.glob("*.text")),
)
def test_act3_preserves_borrowed_carrier_prefix_and_cleans_sentinels(
    stem: str,
) -> None:
    snapshot, state = _run_to_act3_with_prefix(stem)

    assert_prefix_preserved(snapshot, state.stacks[Char.PUCK])

    stream = _stack_carrier_from_floor(state, snapshot)
    assert stream.count(tokens.ITEM_START) == 0
    assert stream.count(tokens.STREAM_END) == 1


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in SPAN_FIXTURES.glob("*.text")),
)
def test_act3_does_not_yet_render_expected_span_html(
    stem: str,
) -> None:
    after = _decode_carrier(_run_to_act3(stem))

    assert _paragraph_text(after) == _rendered_paragraph_html(stem)
