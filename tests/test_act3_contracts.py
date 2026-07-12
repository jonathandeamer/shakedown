"""Act III span-contract tests for the buffered-scan spike.

Verification-only, per the active 2026-07-12 span architecture spike plan:
run Acts I-III through the IR interpreter, prove the carrier stream stays
structurally valid across Act III, and pin the still-red rendered paragraph
contracts before the buffered scanner lands.
"""

from __future__ import annotations

from pathlib import Path

import pytest

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


def _run_to_act2(stem: str) -> InterpreterState:
    input_text = (SPAN_FIXTURES / f"{stem}.text").read_text()
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    return run_act(ACT2, state, step_limit=STEP_LIMIT).state


def _run_to_act3(stem: str) -> InterpreterState:
    state = _run_to_act2(stem)
    return run_act(ACT3, state, step_limit=STEP_LIMIT).state


def _carrier_stream(state: InterpreterState) -> list[int]:
    stream: list[int] = []
    while state.stacks[Char.PUCK]:
        value = state.stacks[Char.PUCK].pop()
        stream.append(value)
        if value == tokens.STREAM_END:
            break
    return stream


def _decode_carrier(state: InterpreterState) -> list[DecodedToken]:
    stream = _carrier_stream(state)
    assert stream.count(tokens.STREAM_END) == 1
    decoded = decode_stream(stream[:-1])
    validate_stream(decoded)
    return decoded


def _rendered_paragraph_html(stem: str) -> str:
    expected = (SPAN_FIXTURES / f"{stem}.expected").read_text()
    assert expected.startswith("<p>")
    assert expected.endswith("</p>\n")
    return expected.removeprefix("<p>").removesuffix("</p>\n")


def _structural_shape(decoded: list[DecodedToken]) -> list[tuple[int, tuple[int, ...]]]:
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
def test_act3_preserves_span_fixture_block_shape_but_not_yet_rendered_html(
    stem: str,
) -> None:
    before = _decode_carrier(_run_to_act2(stem))
    after = _decode_carrier(_run_to_act3(stem))

    assert _structural_shape(after) == _structural_shape(before)
    assert _paragraph_text(after) == _rendered_paragraph_html(stem)
