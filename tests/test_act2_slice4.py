"""Slice-4 Act II contracts land task by task.

Task 1 characterized the pre-Slice-4 Act II grammar for the three high-risk
fixtures as strict xfails. Task 2 replaced the advanced-HTML xfail with the
live contracts below, Task 3 replaced the nested-quote xfail with the exact
balanced-depth stream this act must produce, and Task 4 replaced the full-list
xfail with the live contracts below.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char, Const, Goto, Push
from scripts.splc.token_decode import decode_stream
from scripts.splc.token_structure import validate_stream
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import _LOOSE_NEST_OL, _LOOSE_NEST_UL
from src_ir.act2 import ACT as ACT2

STEP_LIMIT = 500_000

ADVANCED_HTML = '<div>\n<div style=">"/>\n</div>\n'
NESTED_QUOTE = "> foo\n>\n> > bar\n>\n> foo\n"
NESTED_QUOTE_BLANK_AT_OUTER_MARKER = "> > a\n>\n> > b\n"
FULL_LIST = "1. First\n2. Second:\n\t* Fee\n\t* Fie\n3. Third\n"

_ADVANCED_HTML_FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Inline HTML (Advanced).text"
)

# The five advanced-HTML shapes the fixture requires, keyed by the design's
# acceptance inventory. Each must become exactly one RAW_HTML_HASH leaf whose
# payload is the block's own bytes.
ADVANCED_ONE_LINE = "<div>foo</div>\n"
ADVANCED_NESTED_THREE_DEEP = (
    "<div>\n"
    "<div>\n"
    "<div>\n"
    "foo\n"
    "</div>\n"
    '<div style=">"/>\n'
    "</div>\n"
    "<div>bar</div>\n"
    "</div>\n"
)
# Source tabs, not spaces: Act I detab must be the only thing that widens them.
ADVANCED_INDENTED_ATTR = '<div>\n\t<div id="foo">\n\t</div>\n</div>\n'
ADVANCED_ATTRIBUTED_PAIR = (
    '<div class="inlinepage">\n<div class="toggleableend">\nfoo\n</div>\n</div>\n'
)

_ADVANCED_CASES = {
    "one_line": (ADVANCED_ONE_LINE, "<div>foo</div>"),
    "nested_three_deep": (
        ADVANCED_NESTED_THREE_DEEP,
        ADVANCED_NESTED_THREE_DEEP.rstrip("\n"),
    ),
    "style_angle_bracket": (ADVANCED_HTML, ADVANCED_HTML.rstrip("\n")),
    "indented_attr": (
        ADVANCED_INDENTED_ATTR,
        # Act I detabs the leading tab to a four-space tab stop; nothing else
        # in the payload changes.
        '<div>\n    <div id="foo">\n    </div>\n</div>',
    ),
    "attributed_pair": (
        ADVANCED_ATTRIBUTED_PAIR,
        ADVANCED_ATTRIBUTED_PAIR.rstrip("\n"),
    ),
}


def _act2_stream(input_text: str) -> list[int]:
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    state = run_act(ACT2, state, step_limit=STEP_LIMIT).state
    stream: list[int] = []
    while state.stacks[Char.PUCK]:
        value = state.stacks[Char.PUCK].pop()
        if value == tokens.STREAM_END:
            break
        stream.append(value)
    return stream


def _act2_scene_trace(input_text: str) -> list[tuple[str, int]]:
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    trace: list[tuple[str, int]] = []

    class _Observer:
        def on_scene(self, label: str, state: InterpreterState) -> None:
            trace.append((label, state.values[Char.HORATIO]))

        def on_push(self, char: Char, value: int, stack_after: list[int]) -> None:
            return None

        def on_pop(self, char: Char, value: int, stack_after: list[int]) -> None:
            return None

    run_act(ACT2, state, step_limit=STEP_LIMIT, observer=_Observer())
    return trace


@pytest.mark.parametrize("case", sorted(_ADVANCED_CASES))
def test_advanced_html_block_becomes_one_raw_html_leaf(case: str) -> None:
    source, expected_payload = _ADVANCED_CASES[case]
    decoded = decode_stream(_act2_stream(source))

    assert [token.code for token in decoded] == [tokens.RAW_HTML_HASH]
    assert decoded[0].text == expected_payload


def test_advanced_html_payload_ends_before_the_delimiting_blank_line() -> None:
    decoded = decode_stream(
        _act2_stream(ADVANCED_NESTED_THREE_DEEP + "\nAnd after the wall.\n")
    )

    assert [token.code for token in decoded] == [tokens.RAW_HTML_HASH, tokens.PARA]
    assert decoded[0].text == ADVANCED_NESTED_THREE_DEEP.rstrip("\n")
    assert decoded[1].text == "And after the wall."


def test_advanced_html_fixture_blocks_all_become_raw_html_leaves() -> None:
    decoded = decode_stream(_act2_stream(_ADVANCED_HTML_FIXTURE.read_text()))

    assert [token.code for token in decoded] == [
        tokens.PARA,
        tokens.RAW_HTML_HASH,
        tokens.PARA,
        tokens.RAW_HTML_HASH,
        tokens.PARA,
        tokens.RAW_HTML_HASH,
        tokens.PARA,
        tokens.RAW_HTML_HASH,
    ]
    assert [token.text for token in decoded if token.code == tokens.RAW_HTML_HASH] == [
        _ADVANCED_CASES["one_line"][1],
        _ADVANCED_CASES["nested_three_deep"][1],
        _ADVANCED_CASES["indented_attr"][1],
        _ADVANCED_CASES["attributed_pair"][1],
    ]


def _decoded_pairs(input_text: str) -> list[tuple[int, str | None]]:
    decoded = decode_stream(_act2_stream(input_text))
    return [(token.code, token.text) for token in decoded]


def _decoded_triplets(
    input_text: str,
) -> list[tuple[int, tuple[int, ...], str | None]]:
    decoded = decode_stream(_act2_stream(input_text))
    return [(token.code, token.payloads, token.text) for token in decoded]


def test_nested_quote_fixture_stream_is_balanced_open_to_close() -> None:
    assert _decoded_pairs(NESTED_QUOTE) == [
        (tokens.BLOCKQUOTE_OPEN, None),
        (tokens.PARA, "foo"),
        (tokens.BLOCKQUOTE_OPEN, None),
        (tokens.PARA, "bar"),
        (tokens.BLOCKQUOTE_CLOSE, None),
        (tokens.PARA, "foo"),
        (tokens.BLOCKQUOTE_CLOSE, None),
    ]


def test_nested_quote_blank_quoted_line_stays_inside_the_same_depth() -> None:
    assert _decoded_pairs("> a\n>\n> b\n") == [
        (tokens.BLOCKQUOTE_OPEN, None),
        (tokens.PARA, "a"),
        (tokens.PARA, "b"),
        (tokens.BLOCKQUOTE_CLOSE, None),
    ]


def test_nested_quote_marker_only_blank_preserves_the_inner_depth() -> None:
    assert _decoded_pairs(NESTED_QUOTE_BLANK_AT_OUTER_MARKER) == [
        (tokens.BLOCKQUOTE_OPEN, None),
        (tokens.BLOCKQUOTE_OPEN, None),
        (tokens.PARA, "a"),
        (tokens.PARA, "b"),
        (tokens.BLOCKQUOTE_CLOSE, None),
        (tokens.BLOCKQUOTE_CLOSE, None),
    ]


def test_nested_quote_outdent_returns_to_the_parent_depth() -> None:
    assert _decoded_pairs("> a\n>\n> > b\n>\n> c\n") == [
        (tokens.BLOCKQUOTE_OPEN, None),
        (tokens.PARA, "a"),
        (tokens.BLOCKQUOTE_OPEN, None),
        (tokens.PARA, "b"),
        (tokens.BLOCKQUOTE_CLOSE, None),
        (tokens.PARA, "c"),
        (tokens.BLOCKQUOTE_CLOSE, None),
    ]


def test_nested_quote_closes_before_an_unquoted_final_paragraph() -> None:
    assert _decoded_pairs("> a\n\nplain\n") == [
        (tokens.BLOCKQUOTE_OPEN, None),
        (tokens.PARA, "a"),
        (tokens.BLOCKQUOTE_CLOSE, None),
        (tokens.PARA, "plain"),
    ]


_FULL_LIST_FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Ordered and unordered lists.text"
)

# The five full-list families the fixture requires beyond the Spike A/B
# narrowings: multi-tab tight markers across all three bullet glyphs,
# multi-digit ordered labels, loose spacing, multiple item paragraphs, and
# nested list-in-list.
FULL_LIST_CASES = {
    "markers": "*\tone\n+\ttwo\n-\tthree\n",
    "multi_digit": "10. Ten\n11. Eleven\n",
    "loose": "* one\n\n* two\n",
    "paragraphs": "1. one\n\n   two\n",
    "nested": FULL_LIST,
}


@pytest.mark.parametrize("case", sorted(FULL_LIST_CASES))
def test_full_list_stream_validates_and_closes_every_item(case: str) -> None:
    decoded = decode_stream(_act2_stream(FULL_LIST_CASES[case]))
    validate_stream(decoded)

    codes = [token.code for token in decoded]
    assert codes.count(tokens.LIST_ITEM) == codes.count(tokens.ITEM_CLOSE)


def test_full_list_fixture_stream_validates_and_closes_every_item() -> None:
    decoded = decode_stream(_act2_stream(_FULL_LIST_FIXTURE.read_text()))
    validate_stream(decoded)

    codes = [token.code for token in decoded]
    assert codes.count(tokens.LIST_ITEM) == codes.count(tokens.ITEM_CLOSE)


def test_full_list_fixture_preserves_later_headers_and_hr() -> None:
    decoded = decode_stream(_act2_stream(_FULL_LIST_FIXTURE.read_text()))

    headerish = [
        (token.code, token.payloads, token.text)
        for token in decoded
        if token.code == tokens.HEADER
        or (token.code == tokens.PARA and token.text and token.text.startswith("##"))
        or token.code == tokens.HR
    ]
    assert headerish == [
        (tokens.HEADER, (2,), "Unordered"),
        (tokens.HR, (), None),
        (tokens.HR, (), None),
        (tokens.HEADER, (2,), "Ordered"),
        (tokens.HEADER, (2,), "Nested"),
    ]


def test_full_list_fixture_preserves_nested_list_structure() -> None:
    decoded = decode_stream(_act2_stream(_FULL_LIST_FIXTURE.read_text()))

    nested_header = next(
        i
        for i, token in enumerate(decoded)
        if token.code == tokens.HEADER and token.text == "Nested"
    )
    assert decoded[nested_header + 1 : nested_header + 11] == [
        decode_stream([tokens.LIST_OPEN, 1])[0],
        decode_stream([tokens.LIST_ITEM, 1])[0],
        decode_stream([tokens.PARA, ord("T"), ord("a"), ord("b"), tokens.TEXT_END])[0],
        decode_stream([tokens.LIST_OPEN, 1])[0],
        decode_stream([tokens.LIST_ITEM, 1])[0],
        decode_stream([tokens.PARA, ord("T"), ord("a"), ord("b"), tokens.TEXT_END])[0],
        decode_stream([tokens.LIST_OPEN, 1])[0],
        decode_stream([tokens.LIST_ITEM, 1])[0],
        decode_stream([tokens.PARA, ord("T"), ord("a"), ord("b"), tokens.TEXT_END])[0],
        decode_stream([tokens.ITEM_CLOSE])[0],
    ]


def test_top_level_atx_header_becomes_a_header_leaf() -> None:
    assert _decoded_pairs("## Unordered\n") == [
        (tokens.HEADER, "Unordered"),
    ]
    decoded = decode_stream(_act2_stream("## Unordered\n"))
    assert decoded[0].payloads == (2,)


@pytest.mark.parametrize(
    ("source", "expected_text"),
    [(" ## Unordered\n", "## Unordered"), ("##Unordered\n", "##Unordered")],
)
def test_rejected_atx_header_candidates_remain_paragraphs(
    source: str, expected_text: str
) -> None:
    assert _decoded_pairs(source) == [
        (tokens.PARA, expected_text),
    ]


def test_full_list_blank_then_nested_marker_commits_loose_outer_and_tight_inner() -> (
    None
):
    assert _decoded_triplets("* parent\n\n\t* sub\n") == [
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "parent"),
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "sub"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]


def test_full_list_blank_then_sibling_marker_commits_two_loose_items() -> None:
    assert _decoded_triplets("* parent\n\n* sibling\n") == [
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "parent"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "sibling"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]


def test_full_list_blank_then_indented_second_paragraph_marks_item_loose() -> None:
    assert _decoded_triplets("* alpha\n\n  second paragraph\n* beta\n") == [
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "alpha"),
        (tokens.PARA, (), "second paragraph"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "beta"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]


def test_full_list_tab_indented_siblings_stay_in_one_nested_sublist() -> None:
    assert _decoded_triplets("1. a\n\t* b\n\t* c\n") == [
        (tokens.LIST_OPEN, (2,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "a"),
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "b"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "c"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]


def test_full_list_list_ending_blank_rolls_back_to_tight_item() -> None:
    assert _decoded_triplets("* parent\n\n") == [
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "parent"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]


def test_full_list_blank_then_ancestor_indent_outdents_before_joining() -> None:
    assert _decoded_triplets("*\tthis\n\n\t*\tsub\n\n\tthat\n") == [
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "this"),
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "sub"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
        (tokens.PARA, (), "that"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]


def test_full_list_top_level_loose_outdent_leaves_sentinel_for_next_list() -> None:
    # A depth-1 list whose loose blank-then-indented continuation outdents
    # past the list itself (not into a nested parent) must not consume the
    # Act II top-level list-frame sentinel: a later, unrelated top-level
    # list must still be able to close without underflowing Macbeth.
    decoded = decode_stream(_act2_stream("1.\tx\n\n\ty\n\n# z\n*\tw\n"))
    validate_stream(decoded)

    codes = [token.code for token in decoded]
    assert codes.count(tokens.LIST_OPEN) == codes.count(tokens.LIST_CLOSE)
    assert codes.count(tokens.LIST_ITEM) == codes.count(tokens.ITEM_CLOSE)


def test_full_list_outer_sibling_preserves_tight_tail() -> None:
    assert _decoded_triplets("2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\n3. Third\n") == [
        (tokens.LIST_OPEN, (2,), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "Second:"),
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "Fee"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "Fie"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "Foe"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "Third"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]


def test_full_list_outer_sibling_preserves_four_item_subtree() -> None:
    assert _decoded_triplets(
        "2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\t* Fum\n\n3. Third\n"
    ) == [
        (tokens.LIST_OPEN, (2,), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "Second:"),
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "Fee"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "Fie"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "Foe"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "Fum"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (2,), None),
        (tokens.PARA, (), "Third"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]


def test_full_list_a12_route_uses_only_the_close_tail_helpers() -> None:
    trace = _act2_scene_trace(
        "2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\t* Fum\n\n3. Third\n"
    )
    labels = [label for label, _ in trace]

    depth_close = labels.index("PASS_CONTAINERS_DEPTH_SKIP_SUBTREE_CLOSE")
    assert trace[depth_close + 1] == (
        "PASS_CONTAINERS_DEPTH",
        -21,
    )

    close_close = labels.index("PASS_CONTAINERS_CLOSE_SKIP_SUBTREE_CLOSE")
    assert trace[close_close + 1] == (
        "PASS_CONTAINERS_CLOSE",
        -12,
    )


def test_full_list_plain_loose_continuation_never_enters_a10_to_a12_helpers() -> None:
    labels = [label for label, _ in _act2_scene_trace("1.\tItem 1\n\n\tItem 2\n")]
    assert "PASS_CONTAINERS_DEPTH_SKIP_TAIL" not in labels
    assert "PASS_CONTAINERS_DEPTH_SKIP_SUBTREE" not in labels
    assert "PASS_CONTAINERS_DEPTH_SKIP_SUBTREE_CLOSE" not in labels
    assert "PASS_CONTAINERS_CLOSE_SKIP_SUBTREE" not in labels
    assert "PASS_CONTAINERS_CLOSE_SKIP_SUBTREE_CLOSE" not in labels


# Amendment A14: the ordinary top-level nested-list branches must close the
# parent item (TEXT_END, ITEM_CLOSE) before opening the child list, not after
# it closes. This is the source-level IR contract behind the P2 blessed
# nested_one_level dump.
_ACT2_SCENES_BY_LABEL = {sc.label: sc for sc in ACT2.scenes}


@pytest.mark.parametrize(
    ("open_label", "target_label"),
    [
        ("PASS_LISTS_NEST_EMIT_UL_OPEN", "PASS_LISTS_NEST_OPEN_UL"),
        ("PASS_LISTS_NEST_EMIT_OL_OPEN", "PASS_LISTS_NEST_OPEN_OL"),
    ],
)
def test_full_list_ordinary_nest_open_closes_parent_before_child_list(
    open_label: str, target_label: str
) -> None:
    scene = _ACT2_SCENES_BY_LABEL[open_label]
    ops = scene.ops

    assert isinstance(ops[0], Push)
    assert isinstance(ops[0].expr, Const)
    assert ops[0].expr.value == tokens.TEXT_END

    assert isinstance(ops[1], Push)
    assert isinstance(ops[1].expr, Const)
    assert ops[1].expr.value == tokens.ITEM_CLOSE

    assert isinstance(ops[2], Goto)
    assert ops[2].target == target_label


def test_full_list_nested_one_level_stream_closes_parent_before_child_list_open() -> (
    None
):
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "architecture_spikes"
        / "lists"
        / "nested_one_level.text"
    )
    decoded = decode_stream(_act2_stream(fixture.read_text()))
    codes = [token.code for token in decoded]

    child_open_index = codes.index(tokens.LIST_OPEN, 1)
    assert codes[child_open_index - 1] == tokens.ITEM_CLOSE


@pytest.mark.parametrize(
    ("source", "nest_open_label", "shared_open_label", "selector"),
    [
        (
            "* parent\n\n\t* sub\n",
            "PASS_LISTS_NEST_OPEN_UL",
            "PASS_LISTS_NEST_EMIT_UL_OPEN",
            _LOOSE_NEST_UL.value,
        ),
        (
            "1. parent\n\n\t1. sub\n",
            "PASS_LISTS_NEST_OPEN_OL",
            "PASS_LISTS_NEST_EMIT_OL_OPEN",
            _LOOSE_NEST_OL.value,
        ),
    ],
)
def test_full_list_loose_nested_route_bypasses_shared_open_scene(
    source: str, nest_open_label: str, shared_open_label: str, selector: int
) -> None:
    trace = _act2_scene_trace(source)
    labels = [label for label, _ in trace]

    nest_index = labels.index(nest_open_label)
    assert trace[nest_index - 1] == (
        "PASS_LISTS_NEST_EMIT_OL"
        if nest_open_label.endswith("_OL")
        else "PASS_LISTS_NEST_EMIT_UL",
        selector,
    )
    assert shared_open_label not in labels


def test_full_list_ordinary_nested_one_level_route_still_enters_shared_open_scene() -> (
    None
):
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "architecture_spikes"
        / "lists"
        / "nested_one_level.text"
    )
    labels = [label for label, _ in _act2_scene_trace(fixture.read_text())]

    assert "PASS_LISTS_NEST_EMIT_OL_OPEN" in labels
