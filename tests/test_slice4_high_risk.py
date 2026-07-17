"""Slice-4 high-risk fixture contracts land task by task.

Step 1 keeps the entire roadmap row disabled while documenting the current
non-implemented scope. Later tasks replace the pending-fixture assertions
with green enablement contracts as each fixture ships.
"""

from __future__ import annotations

import pytest

from tests.test_mdtest import _FIXTURES_BY_NAME, _IMPLEMENTED_FIXTURES, _SLICE4_FIXTURES

_PENDING_FIXTURES = sorted(set(_FIXTURES_BY_NAME) - _IMPLEMENTED_FIXTURES)


@pytest.mark.parametrize("fixture_name", _PENDING_FIXTURES)
def test_pending_fixture_is_absent_from_implemented_fixtures(fixture_name: str) -> None:
    assert fixture_name not in _IMPLEMENTED_FIXTURES


def test_slice4_fixtures_are_a_subset_of_pending_fixtures() -> None:
    assert _SLICE4_FIXTURES <= set(_PENDING_FIXTURES)
