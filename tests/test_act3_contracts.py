"""Act III span-contract tests for the buffered-scan spike.

Verification-only, per the active 2026-07-12 span architecture spike plan:
run Acts I-III through the IR interpreter, prove the carrier stream stays
structurally valid across Act III, and pin the still-red rendered paragraph
contracts before the buffered scanner lands.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class _CarrierBoundary:
    borrowed: StackSnapshot
    floor_prefix: tuple[int, ...]


def _run_to_act2(stem: str) -> InterpreterState:
    input_text = (SPAN_FIXTURES / f"{stem}.text").read_text()
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    return run_act(ACT2, state, step_limit=STEP_LIMIT).state


def _run_to_act3(stem: str) -> InterpreterState:
    state = _run_to_act2(stem)
    return run_act(ACT3, state, step_limit=STEP_LIMIT).state


def _run_to_act3_with_prefix(stem: str) -> tuple[_CarrierBoundary, InterpreterState]:
    state = _run_to_act2(stem)
    state.stacks[Char.PUCK] = list(_BORROWED_PREFIX) + state.stacks[Char.PUCK]
    borrowed = StackSnapshot(char=Char.PUCK, values=_BORROWED_PREFIX)
    boundary = _CarrierBoundary(
        borrowed=borrowed,
        # Freeze the exact bytes already beneath the future private scan floor:
        # the borrowed prefix plus the carrier's seeded STREAM_END sentinel.
        floor_prefix=tuple(state.stacks[Char.PUCK][: borrowed.floor + 1]),
    )
    return boundary, run_act(ACT3, state, step_limit=STEP_LIMIT).state


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
    state: InterpreterState, boundary: _CarrierBoundary
) -> list[int]:
    stream = state.stacks[Char.PUCK][boundary.borrowed.floor :]
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
    boundary, state = _run_to_act3_with_prefix(stem)

    assert_prefix_preserved(boundary.borrowed, state.stacks[Char.PUCK])
    assert (
        tuple(state.stacks[Char.PUCK][: len(boundary.floor_prefix)])
        == boundary.floor_prefix
    )

    stream = _stack_carrier_from_floor(state, boundary)
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


# --- Task 3: buffered code-span and escape scanner (red until Task 3 Step 3) ---
#
# These fixtures exercise the first two protected-region modes the buffered
# scanner must land: variable-length backtick code runs and backslash escapes.
# They stay red on the pre-scan `LYRIC_POP_GLYPH` copy path.
_TASK3_SCAN_FIXTURES = ("variable_code_spans", "escapes_and_overlap")


def test_act3_renders_variable_length_code_spans() -> None:
    text = _paragraph_text(_decode_carrier(_run_to_act3("variable_code_spans")))

    # Exactly two protected code regions, each with its verbatim/encoded body.
    assert text.count("<code>") == 2
    assert text.count("</code>") == 2
    assert "<code>a ` b</code>" in text
    assert "<code>x &amp; &lt;y&gt;</code>" in text


def test_act3_preserves_escaped_and_literal_span_punctuation() -> None:
    text = _paragraph_text(_decode_carrier(_run_to_act3("escapes_and_overlap")))

    # Escaped punctuation survives as literal glyphs, unpaired ticks stay bare.
    assert "*literal*" in text
    assert "[bracket]" in text
    assert "`tick`" in text


@pytest.mark.parametrize("stem", _TASK3_SCAN_FIXTURES)
def test_act3_scan_floor_matches_pre_scan_prefix(stem: str) -> None:
    boundary, state = _run_to_act3_with_prefix(stem)

    # The buffered scan runs above a private floor sentinel; every byte beneath
    # that floor must equal the pre-scan carrier prefix once the act returns.
    assert (
        tuple(state.stacks[Char.PUCK][: len(boundary.floor_prefix)])
        == boundary.floor_prefix
    )
    stream = _stack_carrier_from_floor(state, boundary)
    assert stream[0] == tokens.STREAM_END


# --- Task 4: protected-region scanner for HTML, autolinks, links/images, emphasis ---
#
# These fixtures exercise the four remaining protected-region modes the buffered
# scanner must land. They stay red on the current buffered scan implementation.
# The negative source-buffer stack assertion is added once per mode;
# it asserts no generated output is ever pushed back onto the source buffer.
_TASK4_PROTECTED_FIXTURES = (
    "inline_html_and_autolink",
    "links_images_protected",
    "overlapping_emphasis",
)


def test_act3_renders_inline_html_and_autolink() -> None:
    text = _paragraph_text(_decode_carrier(_run_to_act3("inline_html_and_autolink")))

    # Inline HTML tag preserved with its inner emphasis processed;
    # autolink emitted with once-encoded ampersands.
    assert "<span><em>raw</em></span>" in text
    # Autolink: href and link text each contain the query with exactly one &
    amp_count = text.count('&')
    assert amp_count == 2, f"Expected exactly two & in output, got {amp_count}: {text}"
    assert '<a href="http://example.com/a?x=1&y=2">' in text
    assert "http://example.com/a?x=1&y=2</a>" in text


def test_act3_renders_links_images_protected() -> None:
    text = _paragraph_text(_decode_carrier(_run_to_act3("links_images_protected")))

    # Link with inner emphasis in label; image with inner emphasis in alt.
    # Exact byte-for-byte expected sequences per Markdown.pl oracle.
    expected_link = '<a href="http://e/x_(y)" title="t">a <em>b</em></a>'
    expected_img = '<img src="img.png" alt="c <em>d</em>" title="i" />'
    assert expected_link in text, f"Missing link: {expected_link} in {text}"
    assert expected_img in text, f"Missing image: {expected_img} in {text}"
    # No extra encoded entities in link destination or image src/title
    assert text.count('&') == 0, f"Unexpected & in output: {text}"


def test_act3_renders_overlapping_emphasis() -> None:
    text = _paragraph_text(_decode_carrier(_run_to_act3("overlapping_emphasis")))

    # Nested strong/em and overlapping strong/em per Markdown.pl rules.
    # Exact byte-for-byte expected sequences per Markdown.pl oracle.
    expected_nested = "<strong><em>both</em></strong>"
    expected_overlap = "<strong>outer <em>inner</em> outer</strong>"
    assert expected_nested in text,
        f"Missing nested strong/em: {expected_nested} in {text}"
    assert expected_overlap in text,
        f"Missing overlapping strong/em: {expected_overlap} in {text}"
    # No stray asterisks or unprocessed emphasis markers
    assert "*" not in text, f"Unprocessed asterisks in output: {text}"


@pytest.mark.parametrize("stem", _TASK4_PROTECTED_FIXTURES)
def test_act3_source_buffer_never_receives_generated_output(stem: str) -> None:
    """Negative assertion: no generated HTML is ever pushed back onto PUCK."""
    boundary, state = _run_to_act3_with_prefix(stem)

    # The source buffer is the portion of PUCK above the private floor sentinel.
    # After a complete paragraph scan, the buffered scanner should have consumed
    # all source glyphs from PUCK, leaving the source region empty. Any generated
    # output goes to JULIET (output stack), never back to PUCK.
    floor_len = len(boundary.floor_prefix)
    source_region = state.stacks[Char.PUCK][floor_len:]
    assert len(source_region) == 0, (
        f"Source buffer not empty for {stem}: {source_region}"
    )


def test_act3_source_buffer_never_receives_generated_output_code_spans() -> None:
    """Negative assertion for code-span fixtures: no generated output on PUCK."""
    for stem in ("variable_code_spans", "escapes_and_overlap"):
        boundary, state = _run_to_act3_with_prefix(stem)
        floor_len = len(boundary.floor_prefix)
        source_region = state.stacks[Char.PUCK][floor_len:]
        assert len(source_region) == 0, (
            f"Source buffer not empty for {stem}: {source_region}"
        )
