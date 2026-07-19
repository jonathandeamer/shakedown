"""Slice-4 Act II contracts land task by task.

Task 1 characterized the pre-Slice-4 Act II grammar for the three high-risk
fixtures as strict xfails. Task 2 replaced the advanced-HTML xfail with the
live contracts below, Task 3 replaced the nested-quote xfail with the exact
balanced-depth stream this act must produce, and Task 4 replaced the full-list
xfail with the live contracts below.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.paths import markdown_pl, mdtest_fixtures_dir
from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char, Const, Goto, Push
from scripts.splc.token_decode import decode_stream
from scripts.splc.token_structure import validate_stream
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import _LOOSE_NEST_OL, _LOOSE_NEST_UL
from src_ir.act2 import ACT as ACT2
from tests.test_mdtest import _interpret_ir, _normalize_fixture_output

STEP_LIMIT = 500_000

ADVANCED_HTML = '<div>\n<div style=">"/>\n</div>\n'
NESTED_QUOTE = "> foo\n>\n> > bar\n>\n> foo\n"
NESTED_QUOTE_BLANK_AT_OUTER_MARKER = "> > a\n>\n> > b\n"
FULL_LIST = "1. First\n2. Second:\n\t* Fee\n\t* Fie\n3. Third\n"

BASICS_SETEXT_H1 = "Markdown: Basics\n================\n"
BASICS_SETEXT_H2 = (
    "Getting the Gist of Markdown's Formatting Syntax\n"
    "------------------------------------------------\n"
)
BASICS_PROJECT_SUBMENU = (
    '<ul id="ProjectSubmenu">\n'
    '    <li><a href="/projects/markdown/" '
    'title="Markdown Project Page">Main</a></li>\n'
    '    <li><a class="selected" title="Markdown Basics">Basics</a></li>\n'
    '    <li><a href="/projects/markdown/syntax" '
    'title="Markdown Syntax Documentation">Syntax</a></li>\n'
    '    <li><a href="/projects/markdown/license" '
    'title="Pricing and License Information">License</a></li>\n'
    '    <li><a href="/projects/markdown/dingus" '
    'title="Online Markdown Web Form">Dingus</a></li>\n'
    "</ul>\n"
)
BASICS_ATX_CLOSING_HASH = "## Heading ##\n"
BASICS_ATX_TRAILING_SPACES = "## Heading  \n"
BASICS_ATX_INTERIOR_HASH = "## A # b\n"
_BASICS_FIXTURE = mdtest_fixtures_dir() / "Markdown Documentation - Basics.text"

_ADVANCED_HTML_FIXTURE = mdtest_fixtures_dir() / "Inline HTML (Advanced).text"

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


def _act2_scene_trace_with_values(
    input_text: str,
) -> list[tuple[str, int, int, int, int, int]]:
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    trace: list[tuple[str, int, int, int, int, int]] = []

    class _Observer:
        def on_scene(self, label: str, state: InterpreterState) -> None:
            trace.append(
                (
                    label,
                    state.values[Char.HECATE],
                    state.values[Char.HORATIO],
                    state.values[Char.LADY_MACBETH],
                    state.values[Char.MACBETH],
                    state.values[Char.PUCK],
                )
            )

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


def _oracle_html(input_text: str) -> str:
    result = subprocess.run(
        ["perl", str(markdown_pl())],
        input=input_text,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


@pytest.mark.parametrize(
    ("source", "level", "text"),
    [
        (BASICS_SETEXT_H1, 1, "Markdown: Basics"),
        (
            BASICS_SETEXT_H2,
            2,
            "Getting the Gist of Markdown's Formatting Syntax",
        ),
    ],
    ids=["setext_h1", "setext_h2"],
)
def test_basics_setext_witness_uses_existing_header_role(
    source: str, level: int, text: str
) -> None:
    assert _decoded_triplets(source) == [
        (tokens.HEADER, (level,), text),
    ]


def test_basics_raw_html_witness_uses_existing_raw_html_hash_role() -> None:
    assert _decoded_triplets(BASICS_PROJECT_SUBMENU) == [
        (tokens.RAW_HTML_HASH, (), BASICS_PROJECT_SUBMENU.rstrip("\n")),
    ]


def test_basics_closing_hash_witness_uses_existing_header_role() -> None:
    assert _decoded_triplets(BASICS_ATX_CLOSING_HASH) == [
        (tokens.HEADER, (2,), "Heading"),
    ]


def test_basics_phrase_emphasis_after_code_examples_stays_a_header() -> None:
    decoded = decode_stream(_act2_stream(_BASICS_FIXTURE.read_text()))

    assert (tokens.HEADER, (3,), "Phrase Emphasis") in [
        (token.code, token.payloads, token.text) for token in decoded
    ]


def test_basics_minimal_setext_positive_count_preserves_the_next_source_glyph() -> None:
    assert _decoded_triplets(BASICS_SETEXT_H1 + "After.\n") == [
        (tokens.HEADER, (1,), "Markdown: Basics"),
        (tokens.PARA, (), "After."),
    ]


def test_basics_minimal_setext_terminal_trace_restores_zero_without_an_extra_read() -> (
    None
):
    trace = _act2_scene_trace_with_values(BASICS_SETEXT_H1)
    labels = [label for label, *_ in trace]

    proved_close_index = labels.index("PASS_SETEXT_PROVED_CLOSE")
    _, _, _, lady_macbeth, _, _ = trace[proved_close_index]
    assert lady_macbeth == 0
    assert "PASS_LISTS_BLOCK_START" not in labels[proved_close_index + 1 :]


def test_basics_minimal_setext_positive_trace_restores_count_before_dispatch() -> None:
    trace = _act2_scene_trace_with_values(BASICS_SETEXT_H1 + "After.\n")
    labels = [label for label, *_ in trace]

    proved_close_index = labels.index("PASS_SETEXT_PROVED_CLOSE")
    _, _, _, lady_macbeth, _, _ = trace[proved_close_index]
    assert lady_macbeth > 0

    block_start_index = labels.index("PASS_LISTS_BLOCK_START", proved_close_index + 1)
    _, hecate, _, _, _, _ = trace[block_start_index + 1]
    assert hecate == ord("A")


@pytest.mark.parametrize(
    "source",
    [
        BASICS_ATX_CLOSING_HASH,
        BASICS_ATX_TRAILING_SPACES,
        BASICS_ATX_INTERIOR_HASH,
    ],
    ids=["closing_hash_suffix", "spaces_only_suffix", "interior_hash_suffix"],
)
def test_basics_atx_suffix_witness_matches_fast_ir_oracle_bytes(source: str) -> None:
    expected = _oracle_html(source)
    actual = _interpret_ir(source)

    assert _normalize_fixture_output("Markdown Documentation - Basics", actual) == (
        _normalize_fixture_output("Markdown Documentation - Basics", expected)
    )


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


_FULL_LIST_FIXTURE = mdtest_fixtures_dir() / "Ordered and unordered lists.text"

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


def test_ul_nested_sibling_outdent_emits_parent_item_close() -> None:
    """Same-kind UL outdent must close the parent item (Slice-5 A17 / Step 2a)."""
    source = "* parent\n    * child\n* sibling\n"
    assert _decoded_triplets(source) == [
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "parent"),
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "child"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "sibling"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]
    expected = (
        "<ul>\n<li>parent\n<ul><li>child</li></ul></li>\n<li>sibling</li>\n</ul>\n"
    )
    actual = _interpret_ir(source)
    assert actual == expected
    oracle = subprocess.run(
        ["perl", str(markdown_pl())],
        input=source.encode(),
        capture_output=True,
        check=True,
    ).stdout.decode()
    assert actual == oracle


def test_ol_nested_sibling_outdent_already_emits_parent_item_close() -> None:
    """Positive control: OL sibling marker path already closed the parent item."""
    source = "1. parent\n    * child\n2. sibling\n"
    assert _decoded_triplets(source) == [
        (tokens.LIST_OPEN, (2,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "parent"),
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "child"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "sibling"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
    ]
    expected = (
        "<ol>\n<li>parent\n<ul><li>child</li></ul></li>\n<li>sibling</li>\n</ol>\n"
    )
    assert _interpret_ir(source) == expected


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


# Slice-5 A17: ordinary top-level nest open keeps the parent item open
# (TEXT_END only). Parent ITEM_CLOSE is emitted after nested LIST_CLOSE on
# SIB_OUTDENT so UL and OL sibling outdents share one close shape. This is
# the source-level IR contract behind the re-blessed nested_one_level dump.
_ACT2_SCENES_BY_LABEL = {sc.label: sc for sc in ACT2.scenes}


@pytest.mark.parametrize(
    ("open_label", "target_label"),
    [
        ("PASS_LISTS_NEST_EMIT_UL_OPEN", "PASS_LISTS_NEST_OPEN_UL"),
        ("PASS_LISTS_NEST_EMIT_OL_OPEN", "PASS_LISTS_NEST_OPEN_OL"),
    ],
)
def test_full_list_ordinary_nest_open_keeps_parent_open_for_child_list(
    open_label: str, target_label: str
) -> None:
    scene = _ACT2_SCENES_BY_LABEL[open_label]
    ops = scene.ops

    assert isinstance(ops[0], Push)
    assert isinstance(ops[0].expr, Const)
    assert ops[0].expr.value == tokens.TEXT_END

    assert isinstance(ops[1], Goto)
    assert ops[1].target == target_label


def test_full_list_nested_one_level_stream_closes_parent_after_nested_list() -> None:
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
    # Parent item stays open: PARA (not ITEM_CLOSE) immediately before nest.
    assert codes[child_open_index - 1] == tokens.PARA
    # Nested list ends, then parent ITEM_CLOSE, then the outer sibling item.
    nested_close_index = codes.index(tokens.LIST_CLOSE)
    assert codes[nested_close_index + 1] == tokens.ITEM_CLOSE
    assert codes[nested_close_index + 2] == tokens.LIST_ITEM


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


# --- Amendment A13: code-line blank-payload normalization contracts. ---

# Exact aggregate witness: after the mandatory four-space code prefix is
# removed, the middle spaces-only physical line must become a bare newline.
CODE_LINE_BLOCKQUOTE_WITNESS = (
    "    <blockquote>\n"
    "        <p>One.</p>\n"
    "        \n"
    "        <p>Two.</p>\n"
    "    </blockquote>\n"
)
CODE_LINE_FOUR_SPACE_ONLY = "    line1\n    \n    line3\n"
CODE_LINE_EIGHT_SPACE_ONLY = "    line1\n        \n    line3\n"
CODE_LINE_TRAILING_SPACES = "    foo  \n"

_CODE_LINE_EXPECTED_PAYLOADS: dict[str, str] = {
    "blockquote_witness": (
        "<blockquote>\n    <p>One.</p>\n\n    <p>Two.</p>\n</blockquote>\n"
    ),
    "four_space_only": "line1\n\nline3\n",
    "eight_space_only": "line1\n\nline3\n",
    "trailing_spaces": "foo  \n",
}


@pytest.mark.parametrize(
    ("source", "expected_payload"),
    [
        (
            CODE_LINE_BLOCKQUOTE_WITNESS,
            _CODE_LINE_EXPECTED_PAYLOADS["blockquote_witness"],
        ),
        (
            CODE_LINE_FOUR_SPACE_ONLY,
            _CODE_LINE_EXPECTED_PAYLOADS["four_space_only"],
        ),
        (
            CODE_LINE_EIGHT_SPACE_ONLY,
            _CODE_LINE_EXPECTED_PAYLOADS["eight_space_only"],
        ),
        (
            CODE_LINE_TRAILING_SPACES,
            _CODE_LINE_EXPECTED_PAYLOADS["trailing_spaces"],
        ),
    ],
    ids=[
        "blockquote_witness",
        "four_space_only",
        "eight_space_only",
        "trailing_spaces",
    ],
)
def test_code_line_blank_payload_witness_decoded_payload(
    source: str, expected_payload: str
) -> None:
    decoded = decode_stream(_act2_stream(source))
    code_blocks = [token for token in decoded if token.code == tokens.CODE_BLOCK]

    assert len(code_blocks) == 1
    assert code_blocks[0].text == expected_payload


@pytest.mark.parametrize(
    "source",
    [
        CODE_LINE_BLOCKQUOTE_WITNESS,
        CODE_LINE_FOUR_SPACE_ONLY,
        CODE_LINE_EIGHT_SPACE_ONLY,
        CODE_LINE_TRAILING_SPACES,
    ],
    ids=[
        "blockquote_witness",
        "four_space_only",
        "eight_space_only",
        "trailing_spaces",
    ],
)
def test_code_line_blank_payload_matches_fast_release_and_raw_oracle(
    source: str,
) -> None:
    from tests.test_mdtest import BINARY

    input_bytes = source.encode()
    expected = _oracle_html(source).encode()

    fast_actual = _interpret_ir(source)
    assert isinstance(fast_actual, str)
    assert fast_actual.encode() == expected

    release = subprocess.run(
        [str(BINARY)],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    assert release.returncode == 0, release.stderr.decode()
    assert release.stdout == expected


# --- Amendment A16: whitespace-only blank-line boundary (paragraph scanner). ---

PARA_WS_MINIMAL_BLANK = "Para:\n    \n    code line\n"
PARA_WS_PREFIXED_CONTINUATION = "Para:\n    still para\n"
PARA_WS_ORDINARY_CONTINUATION = "Para:\nnext line\n"
PARA_WS_SYNTAX_WITNESS = (
    "And then define the link:\n\t\n\t[Daring Fireball]: http://daringfireball.net/\n"
)


@pytest.mark.parametrize(
    ("source", "expected_roles"),
    [
        (
            PARA_WS_MINIMAL_BLANK,
            [tokens.PARA, tokens.CODE_BLOCK],
        ),
        (
            PARA_WS_SYNTAX_WITNESS,
            [tokens.PARA, tokens.CODE_BLOCK],
        ),
        (
            PARA_WS_PREFIXED_CONTINUATION,
            [tokens.PARA],
        ),
        (
            PARA_WS_ORDINARY_CONTINUATION,
            [tokens.PARA],
        ),
    ],
    ids=[
        "minimal_blank",
        "syntax_witness",
        "prefixed_continuation",
        "ordinary_continuation",
    ],
)
def test_para_ws_decoded_stream_shape(source: str, expected_roles: list[int]) -> None:
    decoded = decode_stream(_act2_stream(source))
    assert [token.code for token in decoded] == expected_roles
    if expected_roles == [tokens.PARA, tokens.CODE_BLOCK]:
        assert decoded[0].text == (
            "Para:" if source == PARA_WS_MINIMAL_BLANK else "And then define the link:"
        )
        assert decoded[1].text is not None
        assert "code line" in decoded[1].text or "Daring Fireball" in decoded[1].text
    else:
        assert decoded[0].text is not None
        assert "\n" in decoded[0].text or decoded[0].text.startswith("Para:")


@pytest.mark.parametrize(
    "source",
    [
        PARA_WS_MINIMAL_BLANK,
        PARA_WS_SYNTAX_WITNESS,
        PARA_WS_PREFIXED_CONTINUATION,
        PARA_WS_ORDINARY_CONTINUATION,
    ],
    ids=[
        "minimal_blank",
        "syntax_witness",
        "prefixed_continuation",
        "ordinary_continuation",
    ],
)
def test_para_ws_matches_fast_release_and_raw_oracle(source: str) -> None:
    from tests.test_mdtest import BINARY

    input_bytes = source.encode()
    expected = _oracle_html(source).encode()

    fast_actual = _interpret_ir(source)
    assert isinstance(fast_actual, str)
    assert fast_actual.encode() == expected

    release = subprocess.run(
        [str(BINARY)],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    assert release.returncode == 0, release.stderr.decode()
    assert release.stdout == expected
