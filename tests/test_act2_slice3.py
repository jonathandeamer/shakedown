"""Slice-3 Act II contracts land task by task."""

from pathlib import Path

from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from scripts.splc.token_decode import decode_stream
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from tests.test_mdtest import _run_acts

STEP_LIMIT = 200_000
_BLOCKQUOTE_CODE_FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Blockquotes with code blocks.text"
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


def test_hard_wrap_digit_dot_line_stays_in_paragraph_without_blank_boundary() -> None:
    actual = _run_acts("Paragraph\n8. Oops\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<p>Paragraph\n8. Oops</p>\n"


def test_hard_wrap_digit_dot_line_forms_list_with_blank_boundary() -> None:
    actual = _run_acts("\n\n8. List\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<ol>\n<li>List</li>\n</ol>\n"


def test_rejected_triple_marker_hr_candidates_preserve_plain_paragraph_stream() -> None:
    decoded = decode_stream(
        _act2_stream(
            "***This is strong and em.***\n\n"
            "So is ***this*** word.\n\n"
            "___This is strong and em.___\n\n"
            "So is ___this___ word.\n"
        )
    )

    assert [token.code for token in decoded] == [
        tokens.PARA,
        tokens.PARA,
        tokens.PARA,
        tokens.PARA,
    ]
    assert [token.text for token in decoded] == [
        "***This is strong and em.***",
        "So is ***this*** word.",
        "___This is strong and em.___",
        "So is ___this___ word.",
    ]


def test_rejected_triple_marker_hr_candidates_do_not_leak_item_start() -> None:
    stream = _act2_stream(
        "***This is strong and em.***\n\n"
        "So is ***this*** word.\n\n"
        "___This is strong and em.___\n\n"
        "So is ___this___ word.\n"
    )

    assert stream.count(tokens.ITEM_START) == 0


def test_inline_html_simple_div_block_emits_raw_html_leaf() -> None:
    decoded = decode_stream(_act2_stream("<div>\nfoo\n</div>\n"))

    assert [token.code for token in decoded] == [tokens.RAW_HTML_HASH]
    assert [token.text for token in decoded] == ["<div>\nfoo\n</div>"]


def test_inline_html_standalone_comment_emits_raw_html_leaf() -> None:
    decoded = decode_stream(_act2_stream("<!-- note -->\n"))

    assert [token.code for token in decoded] == [tokens.RAW_HTML_HASH]
    assert [token.text for token in decoded] == ["<!-- note -->"]


def test_inline_html_multiline_comment_emits_raw_html_leaf() -> None:
    decoded = decode_stream(_act2_stream("<!--\nBlah\nBlah\n-->\n"))

    assert [token.code for token in decoded] == [tokens.RAW_HTML_HASH]
    assert [token.text for token in decoded] == ["<!--\nBlah\nBlah\n-->"]


def test_inline_html_raw_hr_block_emits_raw_html_leaf() -> None:
    decoded = decode_stream(_act2_stream("<hr />\n"))

    assert [token.code for token in decoded] == [tokens.RAW_HTML_HASH]
    assert [token.text for token in decoded] == ["<hr />"]


def test_blockquote_code_fixture_forms_quote_paragraph_code_stream() -> None:
    fixture = _BLOCKQUOTE_CODE_FIXTURE.read_text()
    expected = [
        tokens.BLOCKQUOTE_OPEN,
        tokens.PARA,
        *b"Example:",
        tokens.TEXT_END,
        tokens.CODE_BLOCK,
        *b'sub status {\n    print "working";\n}\n',
        tokens.TEXT_END,
        tokens.PARA,
        *b"Or:",
        tokens.TEXT_END,
        tokens.CODE_BLOCK,
        *b'sub status {\n    return "working";\n}\n',
        tokens.TEXT_END,
        tokens.BLOCKQUOTE_CLOSE,
    ]

    assert _act2_stream(fixture) == expected
