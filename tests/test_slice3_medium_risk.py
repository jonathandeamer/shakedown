"""Slice-3 medium-risk fixture contracts.

Step 1 keeps the entire roadmap row disabled while documenting the expected
future capabilities as strict xfails. Later tasks replace these xfails with
green contracts as each fixture ships.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.test_mdtest import (
    _FIXTURES_BY_NAME,
    _IMPLEMENTED_FIXTURES,
    _SLICE3_FIXTURES,
    _SLICE3_TASK3_FIXTURES,
    _normalize_fixture_output,
    _run_acts,
)

REPO = Path(__file__).parent.parent
BINARY = REPO / "shakedown"


def _fixture_paths(name: str) -> tuple[Path, Path]:
    return _FIXTURES_BY_NAME[name]


def _fixture_bytes_match(name: str) -> None:
    input_path, expected_path = _fixture_paths(name)
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize_fixture_output(name, actual) == _normalize_fixture_output(
        name, expected_path.read_text()
    )


@pytest.mark.parametrize("fixture_name", sorted(_SLICE3_FIXTURES))
def test_slice3_fixture_enablement_matches_shipped_scope(fixture_name: str) -> None:
    enabled_slice3 = {
        "Hard-wrapped paragraphs with list-like lines",
        *_SLICE3_TASK3_FIXTURES,
    }
    if fixture_name in enabled_slice3:
        assert fixture_name in _IMPLEMENTED_FIXTURES
        return
    assert fixture_name not in _IMPLEMENTED_FIXTURES


def test_hard_wrap_ambiguity_contract() -> None:
    _fixture_bytes_match("Hard-wrapped paragraphs with list-like lines")


@pytest.mark.parametrize("fixture_name", _SLICE3_TASK3_FIXTURES[:3])
def test_link_contracts(fixture_name: str) -> None:
    _fixture_bytes_match(fixture_name)


@pytest.mark.parametrize("fixture_name", _SLICE3_TASK3_FIXTURES[3:])
def test_image_and_title_quote_contracts(fixture_name: str) -> None:
    _fixture_bytes_match(fixture_name)


@pytest.mark.parametrize("fixture_name", _SLICE3_TASK3_FIXTURES)
def test_task3_binary_contracts(fixture_name: str) -> None:
    input_path, expected_path = _fixture_paths(fixture_name)
    result = subprocess.run(
        [str(BINARY)],
        input=input_path.read_text(),
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert _normalize_fixture_output(
        fixture_name, result.stdout
    ) == _normalize_fixture_output(fixture_name, expected_path.read_text())


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
