"""Slice-3 Act IV contracts land task by task."""

from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from src_ir import tokens
from src_ir.act4 import ACT as ACT4
from tests.test_mdtest import _run_acts

STEP_LIMIT = 200_000


def _text_token(code: int, text: str) -> list[int]:
    return [tokens.TEXT_END, *(ord(char) for char in reversed(text)), code]


def _render_stream(parts: list[list[int]]) -> str:
    state = InterpreterState()
    state.stacks[Char.PUCK] = [tokens.STREAM_END]
    for part in reversed(parts):
        state.stacks[Char.PUCK].extend(part)
    run_act(ACT4, state, step_limit=STEP_LIMIT)
    return state.output_text()


def test_multiline_paragraph_newline_is_not_dispatched_as_raw_html() -> None:
    actual = _run_acts("alpha\nbeta\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<p>alpha\nbeta</p>\n"


def test_inline_image_emits_stripped_angle_destination_and_title() -> None:
    actual = _run_acts('![Alt text](</url/> "with a title").\n', through_act=4)
    assert isinstance(actual, str)
    assert actual == '<p><img src="/url/" alt="Alt text" title="with a title" />.</p>\n'


def test_inline_image_without_title_keeps_empty_title_attribute() -> None:
    actual = _run_acts("![Alt text](/path/to/img.jpg)\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == '<p><img src="/path/to/img.jpg" alt="Alt text" title="" /></p>\n'


def test_reference_image_emits_resolved_source_and_title() -> None:
    actual = _run_acts(
        '![alt text][foo]\n\n  [foo]: /url/ "Title here"\n',
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == '<p><img src="/url/" alt="alt text" title="Title here" /></p>\n'


def test_collapsed_reference_image_uses_alt_text_as_lookup_id() -> None:
    actual = _run_acts(
        '![alt text][]\n\n  [alt text]: /url/ "Title here"\n',
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == '<p><img src="/url/" alt="alt text" title="Title here" /></p>\n'


def test_link_titles_escape_literal_quotes_as_quot_entities() -> None:
    actual = _run_acts(
        'Foo [bar][].\n\n  [bar]: /url/ "Title with "quotes" inside"\n',
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == (
        '<p>Foo <a href="/url/" title="Title with &quot;quotes&quot; inside">'
        "bar</a>.</p>\n"
    )


def test_inline_html_simple_fixture_block_examples_emit_raw_bytes() -> None:
    actual = _run_acts("<div>\nfoo\n</div>\n\n<hr />\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<div>\nfoo\n</div>\n\n<hr />\n"


def test_inline_html_standalone_comment_emits_raw_bytes() -> None:
    actual = _run_acts("<!-- note -->\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<!-- note -->\n"


def test_inline_html_multiline_comment_emits_raw_bytes() -> None:
    actual = _run_acts("<!--\nBlah\nBlah\n-->\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<!--\nBlah\nBlah\n-->\n"


def test_blockquote_code_stream_renders_fixture_bytes() -> None:
    actual = _render_stream(
        [
            [tokens.BLOCKQUOTE_OPEN],
            _text_token(tokens.PARA, "Example:"),
            _text_token(
                tokens.PARA,
                '    sub status {\n        print "working";\n    }',
            ),
            _text_token(tokens.PARA, "Or:"),
            _text_token(
                tokens.PARA,
                '    sub status {\n        return "working";\n    }',
            ),
            [tokens.BLOCKQUOTE_CLOSE],
        ]
    )

    assert actual == (
        "<blockquote>\n"
        "  <p>Example:</p>\n\n"
        "<pre><code>sub status {\n"
        '  print "working";\n'
        "}\n"
        "</code></pre>\n\n"
        "<p>Or:</p>\n\n"
        "<pre><code>sub status {\n"
        '  return "working";\n'
        "}\n"
        "</code></pre>\n"
        "</blockquote>\n"
    )


def test_standalone_code_block_rendering_stays_unchanged() -> None:
    actual = _render_stream(
        [_text_token(tokens.CODE_BLOCK, "line one\n    line two\n")]
    )

    assert actual == "<pre><code>line one\n    line two\n</code></pre>\n"


def test_blockquote_probe_replays_one_leading_space_as_paragraph_text() -> None:
    actual = _render_stream(
        [
            [tokens.BLOCKQUOTE_OPEN],
            _text_token(tokens.PARA, " x"),
            [tokens.BLOCKQUOTE_CLOSE],
        ]
    )

    assert actual == "<blockquote>\n  <p> x</p>\n</blockquote>\n"


def test_blockquote_probe_replays_two_leading_spaces_as_paragraph_text() -> None:
    actual = _render_stream(
        [
            [tokens.BLOCKQUOTE_OPEN],
            _text_token(tokens.PARA, "  x"),
            [tokens.BLOCKQUOTE_CLOSE],
        ]
    )

    assert actual == "<blockquote>\n  <p>  x</p>\n</blockquote>\n"


def test_blockquote_probe_replays_three_leading_spaces_as_paragraph_text() -> None:
    actual = _render_stream(
        [
            [tokens.BLOCKQUOTE_OPEN],
            _text_token(tokens.PARA, "   x"),
            [tokens.BLOCKQUOTE_CLOSE],
        ]
    )

    assert actual == "<blockquote>\n  <p>   x</p>\n</blockquote>\n"


def test_blockquote_probe_replays_four_spaces_then_eof_as_paragraph_text() -> None:
    actual = _render_stream(
        [
            [tokens.BLOCKQUOTE_OPEN],
            _text_token(tokens.PARA, "    "),
            [tokens.BLOCKQUOTE_CLOSE],
        ]
    )

    assert actual == "<blockquote>\n  <p>    </p>\n</blockquote>\n"
