"""Slice-4 Act IV contracts land task by task.

Task 1 kept the three high-risk fixtures' complete-fixture bytes xfailed
through the full four-act pipeline. Task 2 made the advanced-HTML contract
live, Task 3 made the nested-quote contract live, and Task 4 made the
full-list contract live.
"""

from __future__ import annotations

from tests.test_mdtest import _FIXTURES_BY_NAME, _normalize_fixture_output, _run_acts

NESTED_QUOTE_BLANK_AT_OUTER_MARKER = "> > a\n>\n> > b\n"
INSTALLED_ORACLE_NESTED_BLOCKQUOTES = (
    "<blockquote>\n"
    "  <p>foo</p>\n\n"
    "<blockquote>\n"
    "  <p>bar</p>\n"
    "</blockquote>\n\n"
    "<p>foo</p>\n"
    "</blockquote>\n"
)
NESTED_QUOTE_BLANK_AT_OUTER_MARKER_HTML = (
    "<blockquote>\n"
    "  <blockquote>\n"
    "  <p>a</p>\n\n"
    "<p>b</p>\n"
    "</blockquote>\n"
    "</blockquote>\n"
)


def _fixture_bytes_mismatch(name: str) -> None:
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize_fixture_output(name, actual) == _normalize_fixture_output(
        name, expected_path.read_text()
    )


def test_advanced_html_complete_fixture_contract() -> None:
    _fixture_bytes_mismatch("Inline HTML (Advanced)")


def test_nested_quote_complete_fixture_contract() -> None:
    input_path, _ = _FIXTURES_BY_NAME["Nested blockquotes"]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert actual == INSTALLED_ORACLE_NESTED_BLOCKQUOTES


def test_nested_quote_marker_only_blank_preserves_the_inner_frame() -> None:
    actual = _run_acts(NESTED_QUOTE_BLANK_AT_OUTER_MARKER, through_act=4)
    assert actual == NESTED_QUOTE_BLANK_AT_OUTER_MARKER_HTML


FULL_LIST_MARKDOWN_1_0_1_TAIL = (
    "<p>This was an error in Markdown 1.0.1:</p>\n"
    "\n"
    "<ul>\n"
    "<li><p>this</p>\n"
    "\n"
    "<ul><li>sub</li></ul>\n"
    "\n"
    "<p>that</p></li>\n"
    "</ul>\n"
)


def test_ordered_and_unordered_lists_complete_fixture_contract() -> None:
    _fixture_bytes_mismatch("Ordered and unordered lists")


def test_ordered_and_unordered_lists_tail_matches_markdown_1_0_1_quirk() -> None:
    input_path, _ = _FIXTURES_BY_NAME["Ordered and unordered lists"]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert actual.endswith(FULL_LIST_MARKDOWN_1_0_1_TAIL)
