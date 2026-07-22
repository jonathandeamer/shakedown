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

from scripts.paths import mdtest_fixtures_dir
from scripts.splc.contracts import StackSnapshot, assert_prefix_preserved
from scripts.splc.interpret import InterpreterState, StackUnderflow, run_act
from scripts.splc.ir import Char, Const, Push, Val
from scripts.splc.token_decode import DecodedToken, decode_stream
from scripts.splc.token_structure import validate_stream
from scripts.splc.validate import IrError, entry_pairs, participants
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3

REPO = Path(__file__).parent.parent
SPAN_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "spans"
STEP_LIMIT = 200_000
_BORROWED_PREFIX = (7, 13, 42)
_AMPS_FIXTURE = mdtest_fixtures_dir() / "Amps and angle encoding.text"
_A17_ADAPTER_PAIRS = {
    "LYRIC_HTML_OPEN_REQUEUE": (Char.PUCK, Char.ROMEO),
    "LYRIC_AUTOLINK_OPEN_DUPLICATE": (Char.LADY_MACBETH, Char.ROMEO),
    "LYRIC_AUTOLINK_OPEN_REQUEUE": (Char.PUCK, Char.ROMEO),
    "LYRIC_AUTOLINK_CLOSE_DUPLICATE": (Char.HECATE, Char.PROSPERO),
    "LYRIC_FIELD_SOURCE_END_LITERAL": (Char.HECATE, Char.ROMEO),
    "LYRIC_FIELD_UNTERMINATED_IMAGE": (Char.HECATE, Char.PROSPERO),
    "LYRIC_FIELD_UNTERMINATED_LINK": (Char.JULIET, Char.HECATE),
    "LYRIC_LABEL_REQUEUE_END": (Char.LADY_MACBETH, Char.PUCK),
    "LYRIC_ALT_REQUEUE_SELECT": (Char.LADY_MACBETH, Char.PROSPERO),
    "LYRIC_ALT_REQUEUE_END": (Char.LADY_MACBETH, Char.PUCK),
    "LYRIC_EMPHASIS_OPEN_BUFFER": (Char.HECATE, Char.HORATIO),
    "LYRIC_EMPHASIS_COUNT_HOLD": (Char.PUCK, Char.HORATIO),
    "LYRIC_EMPHASIS_SEEK_HOLD": (Char.PUCK, Char.HORATIO),
    "LYRIC_EMPHASIS_MATCH_STRONG": (Char.PUCK, Char.PROSPERO),
    "LYRIC_EMPHASIS_MATCH_OUTPUT": (Char.JULIET, Char.PUCK),
    "LYRIC_EMPHASIS_TRIPLE_OUTPUT": (Char.JULIET, Char.PUCK),
    "LYRIC_EMPHASIS_EMIT_OUTPUT": (Char.JULIET, Char.PUCK),
}
_A17_SPARES = {
    "LYRIC_FIELD_TWO_PERSON_GUARD",
    "LYRIC_REQUEUE_TWO_PERSON_GUARD",
    "LYRIC_EMPHASIS_TWO_PERSON_GUARD",
    "LYRIC_AUTOLINK_TWO_PERSON_GUARD",
    "LYRIC_REGION_TWO_PERSON_GUARD",
}
_A18_ADAPTER_PAIRS = {
    "LYRIC_DEST_CLOSE_PAIR": (Char.ROMEO, Char.PUCK),
    "LYRIC_FIELD_TITLE_ENTRY_PAIR": (Char.HECATE, Char.ROMEO),
    "LYRIC_AUTOLINK_FIELD_HEAD_PAIR": (Char.ROMEO, Char.HECATE),
    "LYRIC_FIELD_LITERAL_POP_PAIR": (Char.JULIET, Char.ROMEO),
    "LYRIC_FIELD_UNTERMINATED_PAIR": (Char.JULIET, Char.PUCK),
    "LYRIC_FIELD_TITLE_REQUEUE_PAIR": (Char.PUCK, Char.PROSPERO),
    "LYRIC_REQUEUE_POP_PAIR": (Char.JULIET, Char.ROMEO),
    "LYRIC_EMPHASIS_SOURCE_END_PAIR": (Char.PUCK, Char.HECATE),
    "LYRIC_EMPHASIS_LITERAL_POP_PAIR": (Char.JULIET, Char.ROMEO),
    "LYRIC_REGION_RESUME_PAIR": (Char.JULIET, Char.PUCK),
}
_A18_SPARES = {
    "LYRIC_FIELD_ENTRY_GUARD",
    "LYRIC_REQUEUE_ENTRY_GUARD",
    "LYRIC_EMPHASIS_ENTRY_GUARD",
    "LYRIC_REGION_ENTRY_GUARD",
}
_A19_ADAPTER_PAIRS = {
    "LYRIC_GOTO_CODE_TICKS_HEAD": (Char.JULIET, Char.ROMEO),
    "LYRIC_GOTO_CODE_TICKS_TAIL": (Char.ROMEO, Char.PUCK),
    "LYRIC_GOTO_HTML_REQUEUE_HEAD": (Char.JULIET, Char.PUCK),
    "LYRIC_GOTO_HTML_REQUEUE_TAIL": (Char.PUCK, Char.ROMEO),
    "LYRIC_GOTO_FIELD_RETRY_HEAD": (Char.PUCK, Char.HECATE),
    "LYRIC_GOTO_FIELD_RETRY_TAIL": (Char.HECATE, Char.PROSPERO),
    "LYRIC_GOTO_AUTOLINK_DUP_HEAD": (Char.JULIET, Char.LADY_MACBETH),
    "LYRIC_GOTO_AUTOLINK_DUP_TAIL": (Char.LADY_MACBETH, Char.ROMEO),
    "LYRIC_GOTO_FIELD_OPEN_HEAD": (Char.HECATE, Char.ROMEO),
    "LYRIC_GOTO_FIELD_OPEN_TAIL": (Char.ROMEO, Char.MACBETH),
    "LYRIC_GOTO_FIELD_UNTERMINATED_HEAD": (Char.PUCK, Char.JULIET),
    "LYRIC_GOTO_FIELD_UNTERMINATED_TAIL": (Char.JULIET, Char.HECATE),
    "LYRIC_GOTO_EMPHASIS_SEEK_HEAD": (Char.ROMEO, Char.PUCK),
    "LYRIC_GOTO_EMPHASIS_SEEK_TAIL": (Char.PUCK, Char.HECATE),
}
_A19_SPARES = {
    "LYRIC_GOTO_FIELD_GUARD",
    "LYRIC_GOTO_REQUEUE_GUARD",
    "LYRIC_GOTO_EMPHASIS_GUARD",
    "LYRIC_GOTO_REGION_GUARD",
    "LYRIC_GOTO_LAST_GUARD",
}
_A3_RECOVERY_PAIRS = {
    "TRAVERSE_COPY_CODE_TEXT": (Char.JULIET, Char.PUCK),
    "TRAVERSE_COPY_CODE_GLYPH": (Char.JULIET, Char.PUCK),
    "LYRIC_DEFINITION_OPEN": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_LEAF_GUARD": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_DRAIN": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_DRAIN_KEEP": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_DRAIN_CLOSE": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_UNWIND": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_UNWIND_KEEP": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_GARDEN_GUARD": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_LINE_OPEN": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_LABEL_FIRST": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_LABEL_REST": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_COLON": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_DESTINATION": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_DESTINATION_TAIL": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_DISCARD_DRAIN": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_DISCARD_KEEP": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_DISCARD_CLOSE": (Char.JULIET, Char.PUCK),
    "LYRIC_DEFINITION_REPLAY_BEGIN": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_REPLAY_POP": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_REPLAY_KEEP": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_REPLAY_CLOSE": (Char.ROMEO, Char.PUCK),
    "LYRIC_DEFINITION_REPLAY_GUARD": (Char.JULIET, Char.PUCK),
    "LYRIC_DEFINITION_CHAMBER_GUARD": (Char.JULIET, Char.PUCK),
}
_A3_SPARES = {
    "LYRIC_DEFINITION_CLOSE_GUARD",
}


@dataclass(frozen=True)
class _CarrierBoundary:
    borrowed: StackSnapshot
    floor_prefix: tuple[int, ...]


@dataclass
class _SceneObserver:
    labels: list[str]
    scene_values: list[tuple[str, int, int, int, int]]
    text_end_routes: list[tuple[str, str, int, int]]
    lady_macbeth_pops: list[tuple[str, int]]
    romeo_pops: list[tuple[str, int]]
    puck_pushes: list[tuple[int, str, int]]
    replay_source_pops: list[int]
    current_label: str = ""
    current_scene_index: int = -1
    hecate: int = 0
    lady_macbeth: int = 0
    pending_text_end: tuple[str, int, int] | None = None
    open_reverse_puck: tuple[int, ...] | None = None
    open_reverse_juliet: tuple[int, ...] | None = None
    definition_replay_armed: bool = False
    replay_source_active: bool = False
    stop_on_replay_terminator: bool = False

    def on_scene(self, label: str, state: InterpreterState) -> None:
        if self.pending_text_end is not None:
            source, hecate, lady_macbeth = self.pending_text_end
            self.text_end_routes.append((source, label, hecate, lady_macbeth))
            self.pending_text_end = None
        self.current_label = label
        self.hecate = state.values[Char.HECATE]
        self.lady_macbeth = state.values[Char.LADY_MACBETH]
        self.labels.append(label)
        self.current_scene_index = len(self.labels) - 1
        self.scene_values.append(
            (
                label,
                state.values[Char.HECATE],
                state.values[Char.MACBETH],
                state.values[Char.PROSPERO],
                state.values[Char.LADY_MACBETH],
            )
        )
        if label == "LYRIC_OPEN_REVERSE":
            assert self.open_reverse_puck is None
            self.open_reverse_puck = tuple(state.stacks[Char.PUCK])
            self.open_reverse_juliet = tuple(state.stacks[Char.JULIET])
        elif label == "LYRIC_DEFINITION_REPLAY_BEGIN":
            self.definition_replay_armed = True
        elif label == "LYRIC_POP_GLYPH" and self.definition_replay_armed:
            self.replay_source_active = True

    def on_push(self, char: Char, value: int, stack_after: list[int]) -> None:
        if char is Char.PUCK:
            self.puck_pushes.append(
                (self.current_scene_index, self.current_label, value)
            )

    def on_pop(self, char: Char, value: int, stack_after: list[int]) -> None:
        if char is Char.PUCK and value == tokens.TEXT_END:
            assert self.pending_text_end is None
            self.pending_text_end = (self.current_label, self.hecate, self.lady_macbeth)
        if char is Char.PUCK and self.replay_source_active:
            self.replay_source_pops.append(value)
            if value == tokens.TEXT_END:
                self.replay_source_active = False
                self.definition_replay_armed = False
                if self.stop_on_replay_terminator:
                    raise _DefinitionReplayObserved
        elif char is Char.LADY_MACBETH:
            self.lady_macbeth_pops.append((self.current_label, value))
        elif char is Char.ROMEO:
            self.romeo_pops.append((self.current_label, value))


class _DefinitionReplayObserved(RuntimeError):
    pass


def _observer() -> _SceneObserver:
    return _SceneObserver(
        labels=[],
        scene_values=[],
        text_end_routes=[],
        lady_macbeth_pops=[],
        romeo_pops=[],
        puck_pushes=[],
        replay_source_pops=[],
    )


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


def _run_to_act3_observed(
    stem: str,
    *,
    resolve_short_circuit: bool = True,
) -> tuple[_CarrierBoundary, InterpreterState, _SceneObserver]:
    state = _run_to_act2(stem)
    state.resolve_short_circuit = resolve_short_circuit
    state.stacks[Char.PUCK] = list(_BORROWED_PREFIX) + state.stacks[Char.PUCK]
    borrowed = StackSnapshot(char=Char.PUCK, values=_BORROWED_PREFIX)
    boundary = _CarrierBoundary(
        borrowed=borrowed,
        floor_prefix=tuple(state.stacks[Char.PUCK][: borrowed.floor + 1]),
    )
    observer = _observer()
    result = run_act(ACT3, state, step_limit=STEP_LIMIT, observer=observer)
    return boundary, result.state, observer


def _run_text_to_act3_observed(
    text: str,
) -> tuple[_CarrierBoundary, InterpreterState, _SceneObserver]:
    state = InterpreterState(input_text=text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    state = run_act(ACT2, state, step_limit=STEP_LIMIT).state
    state.stacks[Char.PUCK] = list(_BORROWED_PREFIX) + state.stacks[Char.PUCK]
    borrowed = StackSnapshot(char=Char.PUCK, values=_BORROWED_PREFIX)
    boundary = _CarrierBoundary(
        borrowed=borrowed,
        floor_prefix=tuple(state.stacks[Char.PUCK][: borrowed.floor + 1]),
    )
    observer = _observer()
    result = run_act(ACT3, state, step_limit=STEP_LIMIT, observer=observer)
    return boundary, result.state, observer


def _run_text_to_act3(text: str) -> InterpreterState:
    return _run_text_to_act3_observed(text)[1]


def _definition_replay_source_pops(text: str) -> list[int]:
    # Definition replay is a scene the compiled play only walks when the resolve
    # pre-pass is not short-circuited, so exercise it in that mode explicitly.
    state = InterpreterState(input_text=text, resolve_short_circuit=False)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    state = run_act(ACT2, state, step_limit=STEP_LIMIT).state
    observer = _observer()
    observer.stop_on_replay_terminator = True
    try:
        run_act(ACT3, state, step_limit=STEP_LIMIT, observer=observer)
    except _DefinitionReplayObserved:
        return observer.replay_source_pops
    raise AssertionError("definition replay source boundary was not observed")


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


@pytest.mark.parametrize(
    "text",
    [
        "[x]: destination\n",
        "[x]: destination\n[y]: another\n",
    ],
    ids=["single-definition-line", "two-definition-lines"],
)
def test_act3_definition_only_input_arrives_already_stripped(text: str) -> None:
    _, state, observer = _run_text_to_act3_observed(text)

    assert _decode_carrier(state) == []
    assert "LYRIC_DEFINITION_DISCARD_CLOSE" not in observer.labels


# Only a candidate with a well-formed label but a malformed tail (e.g. a space
# before the colon) is still handed to Act III's definition-replay path. The
# other malformed forms below are rejected earlier and never reach replay; they
# also currently render as empty output instead of the oracle's literal
# paragraph (e.g. "[not]:" -> "<p>[not]:</p>"), so they are xfail pending a fix
# to malformed-definition fallthrough. See divergences.md.
_DEFINITION_REPLAY_UNREACHED = pytest.mark.xfail(
    reason=(
        "rejected before Act III replay and currently emitted as empty output "
        "instead of a literal paragraph (oracle divergence, pre-existing)"
    ),
    strict=True,
    raises=AssertionError,
)


@pytest.mark.parametrize(
    "text",
    [
        pytest.param(
            "[not]:\n", id="missing-destination", marks=_DEFINITION_REPLAY_UNREACHED
        ),
        pytest.param(
            "[not]:   \n",
            id="space-only-destination",
            marks=_DEFINITION_REPLAY_UNREACHED,
        ),
        pytest.param("[x] : destination\n", id="space-before-colon"),
        pytest.param(
            "[]: destination\n", id="empty-label", marks=_DEFINITION_REPLAY_UNREACHED
        ),
    ],
)
def test_act3_replays_rejected_definition_candidates_byte_for_byte(text: str) -> None:
    assert _definition_replay_source_pops(text) == [
        *text.removesuffix("\n").encode("utf-8"),
        tokens.TEXT_END,
    ]


def test_act3_plain_prose_bypasses_definition_replay() -> None:
    decoded = _decode_carrier(_run_text_to_act3("ordinary prose\n"))

    assert _paragraph_text(decoded) == "ordinary prose"


def test_act3_valid_definition_then_prose_arrives_as_plain_prose() -> None:
    decoded = _decode_carrier(_run_text_to_act3("[x]: destination\nplain words\n"))

    assert _paragraph_text(decoded) == "plain words"


def test_act3_fixture_reference_paragraphs_do_not_enter_definition_discard() -> None:
    fixture = _AMPS_FIXTURE.read_text()
    non_definition_only = fixture.split("\n[1]: ", 1)[0] + "\n"
    _, _, observer = _run_text_to_act3_observed(non_definition_only)

    assert "LYRIC_DEFINITION_DISCARD_CLOSE" not in observer.labels


def test_act3_code_block_payload_bypasses_span_scanner() -> None:
    text = "    \\\\* `tick` <http://example.com/>\n"
    _, state, observer = _run_text_to_act3_observed(text)
    decoded = decode_stream(_carrier_stream(state)[:-1])

    assert len(decoded) == 1
    assert decoded[0].code == tokens.CODE_BLOCK
    assert decoded[0].text == "\\\\* `tick` <http://example.com/>\n"

    reverse_open = observer.labels.index("LYRIC_OPEN_REVERSE")
    code_route = observer.labels[:reverse_open]
    assert "TRAVERSE_COPY_CODE_TEXT" in code_route
    assert "TRAVERSE_COPY_CODE_GLYPH" in code_route
    assert "LYRIC_BUFFER_OPEN" not in code_route
    assert "LYRIC_POP_GLYPH" not in code_route


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
    amp_count = text.count("&")
    assert amp_count == 2, f"Expected exactly two & in output, got {amp_count}: {text}"
    assert '<a href="http://example.com/a?x=1&amp;y=2">' in text
    assert "http://example.com/a?x=1&amp;y=2</a>" in text


def test_act3_renders_links_images_protected() -> None:
    text = _paragraph_text(_decode_carrier(_run_to_act3("links_images_protected")))

    # Link with inner emphasis in label; image with inner emphasis in alt.
    # Exact byte-for-byte expected sequences per Markdown.pl oracle.
    expected_link = '<a href="http://e/x_(y)" title="t">a <em>b</em></a>'
    expected_img = '<img src="img.png" alt="c <em>d</em>" title="i" />'
    assert expected_link in text, f"Missing link: {expected_link} in {text}"
    assert expected_img in text, f"Missing image: {expected_img} in {text}"
    # No extra encoded entities in link destination or image src/title
    assert text.count("&") == 0, f"Unexpected & in output: {text}"


def test_act3_renders_overlapping_emphasis() -> None:
    text = _paragraph_text(_decode_carrier(_run_to_act3("overlapping_emphasis")))

    # Nested strong/em and overlapping strong/em per Markdown.pl rules.
    # Exact byte-for-byte expected sequences per Markdown.pl oracle.
    expected_nested = "<strong><em>both</em></strong>"
    expected_overlap = "<strong>outer <em>inner</em> outer</strong>"
    assert expected_nested in text, (
        f"Missing nested strong/em: {expected_nested} in {text}"
    )
    assert expected_overlap in text, (
        f"Missing overlapping strong/em: {expected_overlap} in {text}"
    )
    assert "*" not in text, f"Unprocessed asterisks in output: {text}"


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in SPAN_FIXTURES.glob("*.text")),
)
def test_act3_pre_handoff_source_is_empty_and_output_is_forward(stem: str) -> None:
    boundary, state, observer = _run_to_act3_observed(stem)

    assert observer.open_reverse_puck == _BORROWED_PREFIX
    assert observer.open_reverse_juliet is not None
    assert observer.open_reverse_juliet
    assert observer.open_reverse_juliet[0] == tokens.STREAM_END
    assert_prefix_preserved(boundary.borrowed, state.stacks[Char.PUCK])
    stream = _stack_carrier_from_floor(state, boundary)
    assert stream.count(tokens.STREAM_END) == 1


_RESUME_CODES = frozenset({8, 9, 10, 11, 12, 13})


@pytest.mark.parametrize("stem", _TASK4_PROTECTED_FIXTURES)
def test_act3_text_end_event_order_is_carrier_safe(stem: str) -> None:
    _, _, observer = _run_to_act3_observed(stem)

    lyric_routes = [
        route for route in observer.text_end_routes if route[0] == "LYRIC_POP_GLYPH"
    ]
    top_level = [
        route for route in lyric_routes if route[1] == "LYRIC_TEXT_END_DISPATCH"
    ]
    assert top_level
    assert all(
        source == "LYRIC_POP_GLYPH" and target == "LYRIC_TEXT_END_DISPATCH"
        for source, target, _, _ in top_level
    )
    real = [route for route in top_level if route[3] == 0]
    assert len(real) == 1
    private = [route for route in top_level if route[3] in _RESUME_CODES]
    assert observer.labels.count("LYRIC_TEXT_END_DISPATCH") == len(top_level)
    assert observer.labels.count("LYRIC_RESUME_DISPATCH") == len(private)
    adapter_order = (
        "LYRIC_TEXT_END_DISPATCH",
        "LYRIC_RESUME_DISPATCH",
        "LYRIC_RESUME_POP_PARENT_SELECTOR",
        "LYRIC_RESUME_SAVE_PARENT_SELECTOR",
        "LYRIC_RESUME_POP_MACBETH",
        "LYRIC_RESUME_RESTORE_MACBETH",
        "LYRIC_RESUME_POP_HECATE",
        "LYRIC_RESUME_RESTORE_HECATE",
        "LYRIC_RESUME_VERIFY_FLOOR",
        "LYRIC_RESUME_RESTORE_PARENT_SELECTOR",
        "LYRIC_RESUME_CLOSE_DISPATCH",
    )
    resume_entries = [
        index
        for index, (label, _, _, _, _) in enumerate(observer.scene_values)
        if label == "LYRIC_TEXT_END_DISPATCH"
    ]
    for index in resume_entries:
        entries = observer.scene_values[index : index + len(adapter_order) + 2]
        if entries[0][4] == 0:
            assert entries[0][0] == "LYRIC_TEXT_END_DISPATCH"
            assert entries[1][0] == "TRAVERSE_COPY_TERMINATOR"
            continue
        assert (
            tuple(label for label, _, _, _, _ in entries[: len(adapter_order)])
            == adapter_order
        )
        frozen_close = entries[1][4]
        assert frozen_close in _RESUME_CODES
        assert entries[2][4] == frozen_close
        close_target = entries[len(adapter_order)]
        assert close_target[3] == frozen_close
        if close_target[0] == "LYRIC_REGION_RESUME_PAIR":
            assert entries[len(adapter_order) + 1][0] == "LYRIC_REGION_RESUME"
        else:
            assert close_target[0] in {
                "LYRIC_REGION_RESUME",
                "LYRIC_EMPHASIS_RESUME",
                "LYRIC_AUTOLINK_CLOSE",
                "LYRIC_IMAGE_TITLE_CLOSE",
            }

    resume_pop_labels = {
        "LYRIC_RESUME_POP_PARENT_SELECTOR",
        "LYRIC_RESUME_POP_MACBETH",
        "LYRIC_RESUME_POP_HECATE",
        "LYRIC_RESUME_VERIFY_FLOOR",
    }
    resume_pops = [
        (label, value)
        for label, value in observer.lady_macbeth_pops
        if label in resume_pop_labels
    ]
    assert len(resume_pops) == 4 * len(private)
    assert all(
        label in resume_pop_labels or label == "LYRIC_AUTOLINK_TEXT_OPEN"
        for label, _ in observer.lady_macbeth_pops
    )
    assert "LYRIC_RESUME_FLOOR_FAIL" not in observer.labels


@pytest.mark.parametrize("stem", _TASK4_PROTECTED_FIXTURES)
def test_act3_protected_modes_do_not_underflow(stem: str) -> None:
    try:
        _run_to_act3_observed(stem)
    except StackUnderflow as exc:
        pytest.fail(str(exc))


def test_act3_emphasis_candidate_keeps_nonmatching_lookahead() -> None:
    _, state, observer = _run_to_act3_observed("overlapping_emphasis")

    labels = observer.labels
    start = next(
        index
        for index, label in enumerate(labels[:-1])
        if label == "LYRIC_EMPHASIS_COMPARE"
        and labels[index + 1] == "LYRIC_EMPHASIS_FALLBACK"
    )
    tail = labels[start:]
    assert tail[1] == "LYRIC_EMPHASIS_FALLBACK"
    keep = tail.index("LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD")
    assert "LYRIC_EMPHASIS_REPLAY" in tail[2:keep]
    assert tail[keep + 1 : keep + 4] == [
        "LYRIC_GOTO_EMPHASIS_SEEK_HEAD",
        "LYRIC_GOTO_EMPHASIS_SEEK_TAIL",
        "LYRIC_EMPHASIS_SEEK",
    ]

    # The unmatched candidate path must preserve source order when requeued.
    text = _paragraph_text(_decode_carrier(state))
    assert "<strong>outer <em>inner</em> outer</strong>" in text


def test_act3_emphasis_candidate_restores_real_text_end_once() -> None:
    _, state, observer = _run_text_to_act3_observed("*a**\n")

    labels = observer.labels
    start = labels.index("LYRIC_EMPHASIS_SOURCE_END")
    tail = labels[start:]
    terminator_index = tail.index("TRAVERSE_COPY_TERMINATOR")

    assert labels[start - 1] in {
        "LYRIC_EMPHASIS_CAND_SOURCE_END",
        "LYRIC_EMPHASIS_SOURCE_END_PAIR",
    }
    assert tail[1] == "LYRIC_EMPHASIS_LITERAL_REVERSE"
    assert "LYRIC_POP_GLYPH" in tail[:terminator_index]
    assert tail[terminator_index - 1] == "LYRIC_TEXT_END_DISPATCH"
    assert "LYRIC_EMPHASIS_SEEK" not in tail[:terminator_index]
    assert _paragraph_text(_decode_carrier(state)) == "*a"

    routes = [
        route
        for route in observer.text_end_routes
        if route[0] == "LYRIC_POP_GLYPH" and route[1] == "LYRIC_TEXT_END_DISPATCH"
    ]
    real = [route for route in routes if route[3] == 0]
    assert len(real) == 1


def test_act3_terminal_emphasis_match_uses_resume_close() -> None:
    _, state, observer = _run_to_act3_observed("overlapping_emphasis")

    labels = observer.labels
    terminal_compare = next(
        index
        for index in range(len(labels) - 1)
        if labels[index] == "LYRIC_EMPHASIS_COMPARE"
        and labels[index + 1] == "LYRIC_EMPHASIS_MATCH"
    )
    tail = labels[terminal_compare:]

    assert "LYRIC_EMPHASIS_MATCH" in tail
    assert (
        "LYRIC_EMPHASIS_CAND_SOURCE_END"
        not in tail[: tail.index("LYRIC_EMPHASIS_MATCH")]
    )
    assert "LYRIC_EMPHASIS_RESUME" in tail
    assert _paragraph_text(_decode_carrier(state)).endswith("</strong>")


def test_act3_link_and_image_titles_follow_delayed_drain_order() -> None:
    _, _, observer = _run_to_act3_observed(
        "links_images_protected", resolve_short_circuit=False
    )

    labels = observer.labels
    link_requeue = labels.index("LYRIC_REQUEUE_OPEN")
    assert "LYRIC_FIELD_TITLE_CLOSE" in labels[:link_requeue]
    assert "LYRIC_FIELD_TITLE_CAPTURE" in labels[:link_requeue]

    image_dest = labels.index("LYRIC_IMAGE_DEST_OPEN")
    assert "LYRIC_IMAGE_TITLE_CLOSE" in labels[image_dest:]
    image_title_close = labels.index("LYRIC_IMAGE_TITLE_CLOSE", image_dest)
    region_resume = labels.index("LYRIC_REGION_RESUME", image_dest)
    assert image_title_close < region_resume

    alt_drain_start = labels.index("LYRIC_ALT_REQUEUE", image_dest)
    alt_drain_end = labels.index("LYRIC_TEXT_END_DISPATCH", alt_drain_start)
    assert not any(
        label.startswith("LYRIC_FIELD_") and label != "LYRIC_FIELD_DRAIN_CLOSE"
        for label in labels[alt_drain_start:alt_drain_end]
    )
    assert not any(
        label.startswith("LYRIC_FIELD_") or label == "LYRIC_IMAGE_TITLE_CLOSE"
        for label, _ in observer.romeo_pops
        if alt_drain_start <= labels.index(label) < alt_drain_end
    )


def test_act3_triple_emphasis_requeue_order() -> None:
    _, state, observer = _run_to_act3_observed("overlapping_emphasis")

    pushes = observer.puck_pushes
    triple_tail = next(
        index
        for index, (_, label, value) in enumerate(pushes)
        if label == "LYRIC_REQUEUE_TRIPLE_CLOSE" and value == 42
    )
    triple_head = next(
        index
        for index, (_, label, value) in enumerate(
            pushes[triple_tail + 1 :], triple_tail + 1
        )
        if label == "LYRIC_REQUEUE_TRIPLE_OPEN" and value == 42
    )
    between = pushes[triple_tail + 1 : triple_head]

    assert between
    assert all(label == "LYRIC_REQUEUE_DRAIN" for _, label, _ in between)
    assert all(value != 42 for _, _, value in between)
    assert _paragraph_text(_decode_carrier(state)).startswith(
        "<strong><em>both</em></strong>"
    )


def test_act3_matched_emphasis_requeue_preserves_parent_lookahead() -> None:
    _, _, observer = _run_to_act3_observed("overlapping_emphasis")

    labels = observer.labels
    first_match = labels.index("LYRIC_EMPHASIS_MATCH")
    tail = labels[first_match:]
    requeue_entry = next(label for label in tail if label.startswith("LYRIC_REQUEUE_"))

    assert requeue_entry == "LYRIC_REQUEUE_OPEN"


def test_act3_label_and_alt_requeue_contains_payload_only() -> None:
    _, _, observer = _run_to_act3_observed(
        "links_images_protected", resolve_short_circuit=False
    )

    labels = observer.labels
    pushes = observer.puck_pushes

    label_start = labels.index("LYRIC_LABEL_REQUEUE")
    alt_start = labels.index("LYRIC_ALT_REQUEUE")
    label_pop = labels.index("LYRIC_POP_GLYPH", label_start)
    alt_end = labels.index("LYRIC_POP_GLYPH", alt_start)

    label_payload = [
        value
        for scene_index, label, value in pushes
        if label == "LYRIC_REQUEUE_DRAIN" and label_start <= scene_index < label_pop
    ]
    alt_payload = [
        value
        for scene_index, label, value in pushes
        if label == "LYRIC_REQUEUE_DRAIN" and alt_start <= scene_index < alt_end
    ]

    assert sorted(label_payload) == sorted(
        [ord("a"), ord(" "), ord("*"), ord("b"), ord("*")]
    )
    assert sorted(alt_payload) == sorted(
        [ord("c"), ord(" "), ord("*"), ord("d"), ord("*")]
    )
    forbidden = {ord("["), ord("]"), ord("("), ord(")"), ord('"')}
    assert forbidden.isdisjoint(label_payload)
    assert forbidden.isdisjoint(alt_payload)


def test_act3_ir_requeue_and_field_floors_follow_a4_shape() -> None:
    before_handoff = True
    juliet_to_puck: list[str] = []
    labels = {sc.label for sc in ACT3.scenes}

    for sc in ACT3.scenes:
        if sc.label == "LYRIC_OPEN_REVERSE":
            before_handoff = False
        for op in sc.ops:
            if not isinstance(op, Push) or op.target is not Char.PUCK:
                continue
            if isinstance(op.expr, Val) and op.expr.char is Char.JULIET:
                juliet_to_puck.append(sc.label)
                continue
            if not before_handoff:
                continue
            if isinstance(op.expr, Val):
                assert op.expr.char in {
                    Char.PUCK,
                    Char.ROMEO,
                    Char.HORATIO,
                    Char.HECATE,
                }
            elif isinstance(op.expr, Const):
                assert op.expr.value in {tokens.TEXT_END, ord("*"), ord("_")}
            else:
                pytest.fail(f"Unexpected Puck requeue in {sc.label}: {op.expr!r}")

    assert juliet_to_puck == ["LYRIC_REVERSE_POP"]
    assert {
        "LYRIC_FIELD_OPEN",
        "LYRIC_FIELD_DRAIN_CLOSE",
        "LYRIC_RESUME_DISPATCH",
        "LYRIC_RESUME_POP_MACBETH",
        "LYRIC_RESUME_RESTORE_MACBETH",
        "LYRIC_RESUME_POP_HECATE",
        "LYRIC_RESUME_RESTORE_HECATE",
        "LYRIC_RESUME_VERIFY_FLOOR",
        "LYRIC_RESUME_FLOOR_FAIL",
    }.issubset(labels)
    field_open = next(sc for sc in ACT3.scenes if sc.label == "LYRIC_FIELD_OPEN")
    assert any(
        isinstance(op, Push)
        and op.target is Char.ROMEO
        and isinstance(op.expr, Const)
        and op.expr.value == tokens.STREAM_END
        for op in field_open.ops
    )


def test_act3_scenes_are_binary_and_reserved_adapters_match_pairs() -> None:
    labels = {sc.label for sc in ACT3.scenes}
    invalid: list[str] = []

    for sc in ACT3.scenes:
        try:
            pair = participants(sc, ACT3.anchor)
        except IrError:
            invalid.append(sc.label)
            continue
        expected = (
            _A17_ADAPTER_PAIRS.get(sc.label)
            or _A18_ADAPTER_PAIRS.get(sc.label)
            or _A19_ADAPTER_PAIRS.get(sc.label)
            or _A3_RECOVERY_PAIRS.get(sc.label)
        )
        if expected is not None:
            assert pair == expected

    assert invalid == []
    assert _A17_SPARES.isdisjoint(labels)
    assert _A18_SPARES.isdisjoint(labels)
    assert _A19_SPARES.isdisjoint(labels)
    assert _A3_SPARES.isdisjoint(labels)


def test_act3_entry_pairs_validate() -> None:
    entry_pairs(ACT3)
