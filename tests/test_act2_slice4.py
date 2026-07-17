"""Slice-4 Act II contracts land task by task.

Task 1 characterized the pre-Slice-4 Act II grammar for the three high-risk
fixtures as strict xfails. Task 2 replaced the advanced-HTML xfail with the
live contracts below, and Task 3 replaced the nested-quote xfail with the exact
balanced-depth stream this act must produce. The full-list xfail stays until
Task 4 ships.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from scripts.splc.token_decode import decode_stream
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
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


@pytest.mark.xfail(
    strict=True, reason="Task 4 has not lifted list nesting to full scope yet"
)
def test_full_list_probe_produces_nested_list_grammar() -> None:
    decoded = decode_stream(_act2_stream(FULL_LIST))
    codes = [token.code for token in decoded]

    assert codes.count(tokens.LIST_OPEN) == 2
    assert codes.count(tokens.LIST_CLOSE) == 2
    assert codes.count(tokens.ITEM_CLOSE) >= 3
