"""Slice-4 high-risk fixture contracts land task by task.

Task 1 kept the entire roadmap row disabled while documenting the current
non-implemented scope. Task 2 adds the advanced-HTML binary contract, which
proves the release SPL — not Markdown.pl — performs the transform, and ships
that fixture into `_IMPLEMENTED_FIXTURES`. Task 3 adds the same binary contract
for nested blockquotes; that fixture stays out of `_IMPLEMENTED_FIXTURES` until
its own green checkpoint. Task 4 adds the same binary contract for the full
list fixture; it, too, stays out of `_IMPLEMENTED_FIXTURES` until its own
green checkpoint. Task 5 Step 1 replaces the earlier still-pending assertion
with a green scope assertion: all three Slice-4 fixtures are enabled and their
fast-IR contracts match their fixture expected output.
"""

from __future__ import annotations

import subprocess

import pytest

from tests.test_act4_slice4 import (
    INSTALLED_ORACLE_NESTED_BLOCKQUOTES,
    NESTED_QUOTE_BLANK_AT_OUTER_MARKER,
    NESTED_QUOTE_BLANK_AT_OUTER_MARKER_HTML,
    _normalize_slice4_fixture_contract,
)
from tests.test_mdtest import (
    _FIXTURES_BY_NAME,
    _IMPLEMENTED_FIXTURES,
    _SLICE4_FIXTURES,
    BINARY,
    _normalize_fixture_output,
    _run_acts,
)

_PENDING_FIXTURES = sorted(set(_FIXTURES_BY_NAME) - _IMPLEMENTED_FIXTURES)


@pytest.mark.parametrize("fixture_name", _PENDING_FIXTURES)
def test_pending_fixture_is_absent_from_implemented_fixtures(fixture_name: str) -> None:
    assert fixture_name not in _IMPLEMENTED_FIXTURES


def test_slice4_fixtures_are_named_fixtures() -> None:
    assert _SLICE4_FIXTURES <= set(_FIXTURES_BY_NAME)


def test_slice4_fixtures_are_exactly_the_three_high_risk_fixtures() -> None:
    assert _SLICE4_FIXTURES == {
        "Inline HTML (Advanced)",
        "Nested blockquotes",
        "Ordered and unordered lists",
    }


def test_slice4_fixtures_are_enabled() -> None:
    assert _SLICE4_FIXTURES <= _IMPLEMENTED_FIXTURES


@pytest.mark.parametrize("fixture_name", sorted(_SLICE4_FIXTURES))
def test_slice4_fixture_fast_ir_matches_expected(fixture_name: str) -> None:
    input_path, expected_path = _FIXTURES_BY_NAME[fixture_name]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize_fixture_output(fixture_name, actual) == _normalize_fixture_output(
        fixture_name, expected_path.read_text()
    )


def _release_binary_fixture_contract(name: str) -> None:
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    result = subprocess.run(
        [str(BINARY)],
        input=input_path.read_text(),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert _normalize_slice4_fixture_contract(
        name, result.stdout
    ) == _normalize_slice4_fixture_contract(name, expected_path.read_text())


def test_advanced_html_release_binary_contract() -> None:
    _release_binary_fixture_contract("Inline HTML (Advanced)")


def test_nested_quote_release_binary_contract() -> None:
    input_path, _ = _FIXTURES_BY_NAME["Nested blockquotes"]
    result = subprocess.run(
        [str(BINARY)],
        input=input_path.read_text(),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == INSTALLED_ORACLE_NESTED_BLOCKQUOTES


def test_nested_quote_marker_only_blank_release_binary_contract() -> None:
    result = subprocess.run(
        [str(BINARY)],
        input=NESTED_QUOTE_BLANK_AT_OUTER_MARKER,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == NESTED_QUOTE_BLANK_AT_OUTER_MARKER_HTML


def test_ordered_and_unordered_lists_release_binary_contract() -> None:
    _release_binary_fixture_contract("Ordered and unordered lists")


def test_top_level_atx_header_release_binary_contract() -> None:
    result = subprocess.run(
        [str(BINARY)],
        input="## Unordered\n",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "<h2>Unordered</h2>\n"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (" ## Unordered\n", "<p>## Unordered</p>\n"),
        ("##Unordered\n", "<p>##Unordered</p>\n"),
    ],
)
def test_rejected_atx_header_candidates_release_binary_contract(
    source: str, expected: str
) -> None:
    result = subprocess.run(
        [str(BINARY)],
        input=source,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "* parent\n\n\t* sub\n",
            "<ul>\n<li><p>parent</p>\n\n<ul><li>sub</li></ul></li>\n</ul>\n",
        ),
        (
            "* parent\n\n* sibling\n",
            "<ul>\n<li><p>parent</p></li>\n<li><p>sibling</p></li>\n</ul>\n",
        ),
        (
            "* parent\n\n",
            "<ul>\n<li>parent</li>\n</ul>\n",
        ),
    ],
)
def test_full_list_blank_transaction_release_binary_contract(
    source: str, expected: str
) -> None:
    result = subprocess.run(
        [str(BINARY)],
        input=source,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == expected


def test_full_list_blank_then_ancestor_indent_release_binary_contract() -> None:
    result = subprocess.run(
        [str(BINARY)],
        input="*\tthis\n\n\t*\tsub\n\n\tthat\n",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (
        result.stdout
        == "<ul>\n<li><p>this</p>\n\n<ul><li>sub</li></ul>\n\n<p>that</p></li>\n</ul>\n"
    )


def test_full_list_outer_sibling_release_binary_contract() -> None:
    result = subprocess.run(
        [str(BINARY)],
        input="2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\n3. Third\n",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "<ol>\n<li><p>Second:</p>\n\n<ul><li>Fee</li>\n<li>Fie</li>\n"
        "<li>Foe</li></ul></li>\n<li><p>Third</p></li>\n</ol>\n"
    )


def test_full_list_blank_then_outer_sibling_after_four_nested_items_release_binary_contract(  # noqa: E501
) -> None:
    result = subprocess.run(
        [str(BINARY)],
        input="2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\t* Fum\n\n3. Third\n",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "<ol>\n<li><p>Second:</p>\n\n<ul><li>Fee</li>\n<li>Fie</li>\n"
        "<li>Foe</li>\n<li>Fum</li></ul></li>\n<li><p>Third</p></li>\n"
        "</ol>\n"
    )
