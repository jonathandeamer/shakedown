"""Unit tests for scripts/splc/contracts.py's stack/stream assertions."""

from __future__ import annotations

import pytest

from scripts.splc.contracts import (
    ContractViolation,
    SentinelBalance,
    StackSnapshot,
    assert_carrier_terminated,
    assert_floor_respected,
    assert_prefix_preserved,
)
from scripts.splc.ir import Char


def test_prefix_preserved_passes_when_prefix_unchanged() -> None:
    before = StackSnapshot(char=Char.HORATIO, values=(1, 2, 3))
    assert_prefix_preserved(before, [1, 2, 3, 9, 9])


def test_prefix_preserved_raises_when_prefix_mutated() -> None:
    before = StackSnapshot(char=Char.HORATIO, values=(1, 2, 3))
    with pytest.raises(ContractViolation, match="prefix beneath floor"):
        assert_prefix_preserved(before, [1, 2, 99])


def test_floor_respected_passes_when_depth_stays_above_floor() -> None:
    assert_floor_respected(Char.MACBETH, floor=2, min_depth=2)


def test_floor_respected_raises_when_depth_falls_below_floor() -> None:
    with pytest.raises(ContractViolation, match="below declared floor"):
        assert_floor_respected(Char.MACBETH, floor=2, min_depth=1)


def test_sentinel_balance_passes_when_pushes_equal_pops() -> None:
    balance = SentinelBalance(char=Char.PUCK, sentinel=-1)
    balance.record_push(-1)
    balance.record_push(5)
    balance.record_pop(5)
    balance.record_pop(-1)
    balance.assert_balanced()


def test_sentinel_balance_raises_when_unbalanced() -> None:
    balance = SentinelBalance(char=Char.PUCK, sentinel=-1)
    balance.record_push(-1)
    with pytest.raises(ContractViolation, match="pushed 1 times but popped 0"):
        balance.assert_balanced()


def test_carrier_terminated_passes_with_single_sentinel_at_floor() -> None:
    assert_carrier_terminated(Char.JULIET, [-1, 1, 2], sentinel=-1)


def test_carrier_terminated_raises_with_no_sentinel() -> None:
    with pytest.raises(ContractViolation, match="contains 0 instances"):
        assert_carrier_terminated(Char.JULIET, [1, 2], sentinel=-1)


def test_carrier_terminated_raises_with_duplicate_sentinel() -> None:
    with pytest.raises(ContractViolation, match="contains 2 instances"):
        assert_carrier_terminated(Char.JULIET, [-1, 1, -1], sentinel=-1)


def test_carrier_terminated_raises_when_sentinel_not_at_floor() -> None:
    with pytest.raises(ContractViolation, match="not seeded beneath"):
        assert_carrier_terminated(Char.JULIET, [1, -1, 2], sentinel=-1)
