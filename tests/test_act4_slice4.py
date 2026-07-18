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


def _normalize_ordered_and_unordered_lists_nested_wrapping(text: str) -> str:
    """Match the local Markdown.pl nested-list wrapping for this fixture.

    The checked-in mdtest expected file uses an older multiline nested-list
    shape in a few sections of this fixture. Slice 4's strict acceptance gate
    is the local Markdown.pl oracle, which emits the compact nested `<ul>`
    form. Keep this normalization local to the focused Slice-4 contracts; the
    strict parity harness remains the byte-level authority.
    """

    rewrites = (
        (
            "<ul>\n<li>Tab\n<ul>\n<li>Tab\n<ul>\n<li>Tab</li>\n</ul></li>\n</ul></li>\n</ul>",
            "<ul>\n<li>Tab\n<ul><li>Tab\n<ul><li>Tab</li></ul></li></ul></li>\n</ul>",
        ),
        (
            "<li>Second:\n<ul>\n<li>Fee</li>\n<li>Fie</li>\n<li>Foe</li>\n</ul></li>",
            "<li>Second:\n<ul><li>Fee</li>\n<li>Fie</li>\n<li>Foe</li></ul></li>",
        ),
        (
            "<li><p>Second:</p>\n\n<ul>\n<li>Fee</li>\n<li>Fie</li>\n<li>Foe</li>\n</ul></li>",
            "<li><p>Second:</p>\n\n<ul><li>Fee</li>\n<li>Fie</li>\n<li>Foe</li></ul></li>",
        ),
        (
            "<li><p>Second:</p>\n\n<ul>\n<li>Fee</li>\n<li>Fie</li>\n<li>Foe</li>\n<li>Fum</li>\n</ul></li>",
            "<li><p>Second:</p>\n\n<ul><li>Fee</li>\n<li>Fie</li>\n<li>Foe</li>\n<li>Fum</li></ul></li>",
        ),
    )
    normalized = text
    for stale, oracle in rewrites:
        normalized = normalized.replace(stale, oracle)
    return normalized


def _normalize_slice4_fixture_contract(name: str, text: str) -> str:
    normalized = _normalize_fixture_output(name, text)
    if name == "Ordered and unordered lists":
        normalized = _normalize_ordered_and_unordered_lists_nested_wrapping(normalized)
    return normalized


def _fixture_bytes_mismatch(name: str) -> None:
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize_slice4_fixture_contract(
        name, actual
    ) == _normalize_slice4_fixture_contract(name, expected_path.read_text())


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


def test_ordered_and_unordered_lists_starts_with_expected_headers_and_hr() -> None:
    input_path, _ = _FIXTURES_BY_NAME["Ordered and unordered lists"]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert "<h2>Unordered</h2>\n" in actual
    assert "\n<hr />\n\n<p>Pluses tight:</p>\n" in actual
    assert "\n<hr />\n\n<p>Minuses tight:</p>\n" in actual
    assert "\n<h2>Ordered</h2>\n" in actual
    assert "\n<h2>Nested</h2>\n" in actual


def test_ordered_and_unordered_lists_renders_nested_list_sections() -> None:
    input_path, _ = _FIXTURES_BY_NAME["Ordered and unordered lists"]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert (
        "<ul>\n<li>Tab\n<ul><li>Tab\n<ul><li>Tab</li></ul></li></ul></li>\n</ul>\n"
        in actual
    )
    assert (
        "<li>Second:\n<ul><li>Fee</li>\n<li>Fie</li>\n<li>Foe</li></ul></li>\n"
        in actual
    )


def test_top_level_atx_header_renders_h2() -> None:
    actual = _run_acts("## Unordered\n", through_act=4)
    assert actual == "<h2>Unordered</h2>\n"


def test_rejected_atx_header_candidates_render_as_paragraphs() -> None:
    assert _run_acts(" ## Unordered\n", through_act=4) == "<p>## Unordered</p>\n"
    assert _run_acts("##Unordered\n", through_act=4) == "<p>##Unordered</p>\n"


def test_full_list_blank_then_nested_marker_renders_nested_tight_list() -> None:
    actual = _run_acts("* parent\n\n\t* sub\n", through_act=4)
    assert actual == "<ul>\n<li><p>parent</p>\n\n<ul><li>sub</li></ul></li>\n</ul>\n"


def test_full_list_blank_then_sibling_marker_renders_two_loose_items() -> None:
    actual = _run_acts("* parent\n\n* sibling\n", through_act=4)
    assert actual == "<ul>\n<li><p>parent</p></li>\n<li><p>sibling</p></li>\n</ul>\n"


def test_full_list_blank_then_indented_second_paragraph_renders_loose_item() -> None:
    actual = _run_acts("* alpha\n\n  second paragraph\n* beta\n", through_act=4)
    assert actual == (
        "<ul>\n<li><p>alpha</p>\n\n<p>second paragraph</p></li>\n<li>beta</li>\n</ul>\n"
    )


def test_full_list_tab_indented_siblings_render_one_nested_sublist() -> None:
    actual = _run_acts("1. a\n\t* b\n\t* c\n", through_act=4)
    assert actual == "<ol>\n<li>a\n<ul><li>b</li>\n<li>c</li></ul></li>\n</ol>\n"


def test_full_list_list_ending_blank_stays_tight() -> None:
    actual = _run_acts("* parent\n\n", through_act=4)
    assert actual == "<ul>\n<li>parent</li>\n</ul>\n"


def test_full_list_blank_then_ancestor_indent_returns_to_outer_loose_item() -> None:
    actual = _run_acts("*\tthis\n\n\t*\tsub\n\n\tthat\n", through_act=4)
    assert (
        actual
        == "<ul>\n<li><p>this</p>\n\n<ul><li>sub</li></ul>\n\n<p>that</p></li>\n</ul>\n"
    )


def test_full_list_outer_sibling_renders_expected_html() -> None:
    actual = _run_acts(
        "2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\n3. Third\n",
        through_act=4,
    )
    assert actual == (
        "<ol>\n<li><p>Second:</p>\n\n<ul><li>Fee</li>\n<li>Fie</li>\n"
        "<li>Foe</li></ul></li>\n<li><p>Third</p></li>\n</ol>\n"
    )


def test_full_list_blank_then_outer_sibling_after_four_nested_items_renders_expected_html(  # noqa: E501
) -> None:
    actual = _run_acts(
        "2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\t* Fum\n\n3. Third\n",
        through_act=4,
    )
    assert actual == (
        "<ol>\n<li><p>Second:</p>\n\n<ul><li>Fee</li>\n<li>Fie</li>\n"
        "<li>Foe</li>\n<li>Fum</li></ul></li>\n<li><p>Third</p></li>\n"
        "</ol>\n"
    )
