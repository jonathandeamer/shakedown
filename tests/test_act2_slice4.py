"""Slice-4 Act II contracts land task by task.

Step 1 characterizes the current (pre-Slice-4) Act II grammar for the three
high-risk fixtures as strict xfails. Later tasks replace these xfails with
green contracts as each fixture ships.
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
FULL_LIST = "1. First\n2. Second:\n\t* Fee\n\t* Fie\n3. Third\n"

_ADVANCED_HTML_FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Inline HTML (Advanced).text"
)


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


@pytest.mark.xfail(
    strict=True, reason="Task 2 has not widened raw HTML recognition yet"
)
def test_advanced_html_fixture_blocks_all_become_raw_html_leaves() -> None:
    decoded = decode_stream(_act2_stream(ADVANCED_HTML))
    assert [token.code for token in decoded] == [tokens.RAW_HTML_HASH]

    fixture_decoded = decode_stream(_act2_stream(_ADVANCED_HTML_FIXTURE.read_text()))
    raw_html_leaves = [
        token for token in fixture_decoded if token.code == tokens.RAW_HTML_HASH
    ]
    assert len(raw_html_leaves) == 5, (
        "the fixture has five div blocks; the final attributed nested pair "
        "currently falls through to a plain paragraph"
    )


@pytest.mark.xfail(
    strict=True, reason="Task 3 has not implemented balanced quote depth yet"
)
def test_nested_quote_probe_produces_two_matched_open_close_pairs() -> None:
    decoded = decode_stream(_act2_stream(NESTED_QUOTE))
    codes = [token.code for token in decoded]

    assert codes.count(tokens.BLOCKQUOTE_OPEN) == 2
    assert codes.count(tokens.BLOCKQUOTE_CLOSE) == 2


@pytest.mark.xfail(
    strict=True, reason="Task 4 has not lifted list nesting to full scope yet"
)
def test_full_list_probe_produces_nested_list_grammar() -> None:
    decoded = decode_stream(_act2_stream(FULL_LIST))
    codes = [token.code for token in decoded]

    assert codes.count(tokens.LIST_OPEN) == 2
    assert codes.count(tokens.LIST_CLOSE) == 2
    assert codes.count(tokens.ITEM_CLOSE) >= 3
