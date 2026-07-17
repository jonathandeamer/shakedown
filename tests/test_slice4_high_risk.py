"""Slice-4 high-risk fixture contracts land task by task.

Task 1 kept the entire roadmap row disabled while documenting the current
non-implemented scope. Task 2 adds the advanced-HTML binary contract, which
proves the release SPL — not Markdown.pl — performs the transform, and ships
that fixture into `_IMPLEMENTED_FIXTURES`. Task 3 adds the same binary contract
for nested blockquotes; that fixture stays out of `_IMPLEMENTED_FIXTURES` until
its own green checkpoint. The remaining Slice-4 fixture stays out until Task 4.
"""

from __future__ import annotations

import subprocess

import pytest

from tests.test_act4_slice4 import (
    INSTALLED_ORACLE_NESTED_BLOCKQUOTES,
    NESTED_QUOTE_BLANK_AT_OUTER_MARKER,
    NESTED_QUOTE_BLANK_AT_OUTER_MARKER_HTML,
)
from tests.test_mdtest import (
    _FIXTURES_BY_NAME,
    _IMPLEMENTED_FIXTURES,
    _SLICE4_FIXTURES,
    BINARY,
    _normalize_fixture_output,
)

_PENDING_FIXTURES = sorted(set(_FIXTURES_BY_NAME) - _IMPLEMENTED_FIXTURES)


@pytest.mark.parametrize("fixture_name", _PENDING_FIXTURES)
def test_pending_fixture_is_absent_from_implemented_fixtures(fixture_name: str) -> None:
    assert fixture_name not in _IMPLEMENTED_FIXTURES


def test_slice4_fixtures_are_named_fixtures() -> None:
    assert _SLICE4_FIXTURES <= set(_FIXTURES_BY_NAME)


def test_unshipped_slice4_fixtures_are_still_pending() -> None:
    assert _SLICE4_FIXTURES - _IMPLEMENTED_FIXTURES <= set(_PENDING_FIXTURES)


def _release_binary_fixture_contract(name: str) -> None:
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    result = subprocess.run(
        [str(BINARY)],
        input=input_path.read_text(),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert _normalize_fixture_output(name, result.stdout) == _normalize_fixture_output(
        name, expected_path.read_text()
    )


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
