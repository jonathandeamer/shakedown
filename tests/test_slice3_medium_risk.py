"""Slice-3 medium-risk fixture contracts.

Step 1 keeps the entire roadmap row disabled while documenting the expected
future capabilities as strict xfails. Later tasks replace these xfails with
green contracts as each fixture ships.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.test_mdtest import (
    _FIXTURES_BY_NAME,
    _IMPLEMENTED_FIXTURES,
    _SLICE3_FIXTURES,
    _normalize,
    _run_acts,
)


def _fixture_paths(name: str) -> tuple[Path, Path]:
    return _FIXTURES_BY_NAME[name]


def _fixture_bytes_match(name: str) -> None:
    input_path, expected_path = _fixture_paths(name)
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize(actual) == _normalize(expected_path.read_text())


@pytest.mark.parametrize("fixture_name", sorted(_SLICE3_FIXTURES))
def test_slice3_fixture_is_not_enabled_yet(fixture_name: str) -> None:
    assert fixture_name not in _IMPLEMENTED_FIXTURES


@pytest.mark.xfail(strict=True, reason="Slice 3 Task 2 has not shipped yet")
def test_hard_wrap_ambiguity_contract() -> None:
    _fixture_bytes_match("Hard-wrapped paragraphs with list-like lines")


@pytest.mark.parametrize(
    "fixture_name",
    [
        "Links, inline style",
        "Links, reference style",
        "Links, shortcut references",
    ],
)
@pytest.mark.xfail(strict=True, reason="Slice 3 Task 3 has not shipped yet")
def test_link_contracts(fixture_name: str) -> None:
    _fixture_bytes_match(fixture_name)


@pytest.mark.parametrize(
    "fixture_name",
    ["Images", "Literal quotes in titles"],
)
@pytest.mark.xfail(strict=True, reason="Slice 3 Task 3 has not shipped yet")
def test_image_and_title_quote_contracts(fixture_name: str) -> None:
    _fixture_bytes_match(fixture_name)


@pytest.mark.xfail(strict=True, reason="Slice 3 Task 4 has not shipped yet")
def test_strong_em_contract() -> None:
    _fixture_bytes_match("Strong and em together")


@pytest.mark.parametrize(
    "fixture_name",
    ["Inline HTML (Simple)", "Inline HTML comments"],
)
@pytest.mark.xfail(strict=True, reason="Slice 3 Task 5 has not shipped yet")
def test_inline_html_contracts(fixture_name: str) -> None:
    _fixture_bytes_match(fixture_name)


@pytest.mark.xfail(strict=True, reason="Slice 3 Task 6 has not shipped yet")
def test_quote_code_contract() -> None:
    _fixture_bytes_match("Blockquotes with code blocks")
