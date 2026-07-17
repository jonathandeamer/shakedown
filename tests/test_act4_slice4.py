"""Slice-4 Act IV contracts land task by task.

Step 1 keeps the three high-risk fixtures' complete-fixture bytes xfailed
through the full four-act pipeline. Later tasks replace these xfails with
green contracts as each fixture ships.
"""

from __future__ import annotations

import pytest

from tests.test_mdtest import _FIXTURES_BY_NAME, _normalize_fixture_output, _run_acts


def _fixture_bytes_mismatch(name: str) -> None:
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize_fixture_output(name, actual) == _normalize_fixture_output(
        name, expected_path.read_text()
    )


@pytest.mark.xfail(
    strict=True, reason="Task 2 has not widened raw HTML recognition yet"
)
def test_advanced_html_complete_fixture_contract() -> None:
    _fixture_bytes_mismatch("Inline HTML (Advanced)")


@pytest.mark.xfail(
    strict=True, reason="Task 3 has not implemented balanced quote depth yet"
)
def test_nested_blockquotes_complete_fixture_contract() -> None:
    _fixture_bytes_mismatch("Nested blockquotes")


@pytest.mark.xfail(
    strict=True, reason="Task 4 has not lifted list nesting to full scope yet"
)
def test_ordered_and_unordered_lists_complete_fixture_contract() -> None:
    _fixture_bytes_mismatch("Ordered and unordered lists")
