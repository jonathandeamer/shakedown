"""Slice-4 high-risk fixture contracts land task by task.

Task 1 kept the entire roadmap row disabled while documenting the current
non-implemented scope. Task 2 adds the advanced-HTML binary contract, which
proves the release SPL — not Markdown.pl — performs the transform, and ships
that fixture into `_IMPLEMENTED_FIXTURES`. The remaining Slice-4 fixtures stay
out until each reaches its own green checkpoint.
"""

from __future__ import annotations

import subprocess

import pytest

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


def test_advanced_html_release_binary_contract() -> None:
    name = "Inline HTML (Advanced)"
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
