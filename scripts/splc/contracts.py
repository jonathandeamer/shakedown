"""Verification-only stack/stream contract assertions for the IR interpreter.

Typed snapshots and assertions for four invariants named by
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §2:
no pop below a declared stack floor, sentinel frames consumed exactly once,
a borrowed stack's prefix beneath its floor sentinel is preserved, and a
carrier stream ends with exactly one bottom-of-stream sentinel. These
assertions are test-only: they never run inside `./shakedown` and add no
runtime operations or rendered SPL.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from scripts.splc.ir import Char


class ContractViolation(RuntimeError):
    """Raised when a stack/stream contract described above is broken."""


@dataclass(frozen=True)
class StackSnapshot:
    """A stack's contents for `char`, taken at some point during a run."""

    char: Char
    values: tuple[int, ...]

    @property
    def floor(self) -> int:
        """Depth beneath which content must survive any borrow/release."""
        return len(self.values)


def assert_prefix_preserved(before: StackSnapshot, after: list[int]) -> None:
    """Assert the stack still starts with exactly `before`'s contents.

    Used when a stack is borrowed for temporary carrier use (e.g. Horatio's
    list-looseness side channel) and later released: whatever was beneath
    the borrow's floor must come back unchanged, in order.
    """
    prefix = tuple(after[: before.floor])
    if prefix != before.values:
        raise ContractViolation(
            f"{before.char.value}: prefix beneath floor {before.floor} "
            f"changed from {before.values!r} to {prefix!r}"
        )


def assert_floor_respected(char: Char, floor: int, min_depth: int) -> None:
    """Assert the stack never fell below `floor` during the observed run.

    `min_depth` is the smallest stack length seen; a caller records it while
    replaying push/pop events (e.g. via an interpreter boundary observer).
    """
    if min_depth < floor:
        raise ContractViolation(
            f"{char.value}: stack depth fell to {min_depth}, below declared "
            f"floor {floor}"
        )


@dataclass
class SentinelBalance:
    """Tracks push/pop counts for one sentinel value on one stack."""

    char: Char
    sentinel: int
    pushes: int = field(default=0)
    pops: int = field(default=0)

    def record_push(self, value: int) -> None:
        if value == self.sentinel:
            self.pushes += 1

    def record_pop(self, value: int) -> None:
        if value == self.sentinel:
            self.pops += 1

    def assert_balanced(self) -> None:
        if self.pushes != self.pops:
            raise ContractViolation(
                f"{self.char.value}: sentinel {self.sentinel} pushed "
                f"{self.pushes} times but popped {self.pops} times"
            )


def assert_carrier_terminated(char: Char, values: list[int], sentinel: int) -> None:
    """Assert a carrier stack holds exactly one bottom-of-stream sentinel,
    seeded beneath its content (index 0 in push order)."""
    count = values.count(sentinel)
    if count != 1:
        raise ContractViolation(
            f"{char.value}: carrier stack contains {count} instances of "
            f"sentinel {sentinel}, expected exactly one"
        )
    if values[0] != sentinel:
        raise ContractViolation(
            f"{char.value}: carrier stack sentinel {sentinel} is not seeded "
            f"beneath its content"
        )
