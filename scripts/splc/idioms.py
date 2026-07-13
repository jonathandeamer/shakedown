"""Reusable splc IR compilation idioms and helper functions.

Provides helper functions for common Act III / Act IV choreography patterns.
"""

from scripts.splc.ir import (
    Char,
    Op,
    const,
    let,
    pop,
    push,
    sub,
    val,
)


def pop_glyph(target_char: Char, scan_char: Char, recall_key: str) -> list[Op]:
    """Pop the next glyph into target_char and decrement scan_char's scan count."""
    return [
        pop(target_char, recall=recall_key),
        let(scan_char, sub(val(scan_char), const(1))),
    ]


def stream_literal(target_char: Char, *codes: int) -> list[Op]:
    """Push token codes / payload bytes onto a character's forward stream."""
    return [push(target_char, const(code)) for code in codes]


def entity_encode(target_char: Char, *codes: int) -> list[Op]:
    """Let+push pairs on target_char (entity-emission idiom)."""
    ops: list[Op] = []
    for code in codes:
        ops.append(let(target_char, const(code)))
        ops.append(push(target_char, val(target_char)))
    return ops
