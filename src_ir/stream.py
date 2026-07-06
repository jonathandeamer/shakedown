"""Shared <=4-operator value recipes and tokenized-stream emission helpers.

Single home for byte values whose default atom decomposition would exceed
the 4-operator compliance bound (test_numeric_recipe_complexity_stays_bounded)
and for arity-checked token emission (emit_token). The Slice-1 stream-count
constants (128/315/387) were retired by the P1 stream migration: the stream
is bottom-terminated by tokens.STREAM_END."""

from __future__ import annotations

from scripts.splc.ir import BinOp, Char, Push, add, const, mul, push, sub
from src_ir import tokens

# Byte values whose default decomposition exceeds the 4-operator bound.
# 47/61/62 moved verbatim from src_ir/act4.py's _EMIT_RECIPE; the rest are
# Act III's (audit "Constants" section). All arithmetic is asserted by
# tests/test_stream_recipes.py.
RECIPES: dict[int, BinOp] = {
    47: sub(mul(const(3), const(16)), const(1)),  # '/' = 3x16 - 1
    59: sub(mul(const(8), const(8)), add(const(1), const(4))),  # ';' = 64 - 5
    61: sub(mul(const(8), const(8)), add(const(1), const(2))),  # '=' = 64 - 3
    62: sub(mul(const(8), const(8)), const(2)),  # '>' = 64 - 2
    63: sub(mul(const(8), const(8)), const(1)),  # '?' = 64 - 1
    91: mul(  # '[' = 7 x 13
        sub(const(8), const(1)), add(const(8), add(const(4), const(1)))
    ),
    107: sub(  # 'k' = 16x7 - 5
        mul(const(16), sub(const(8), const(1))), add(const(1), const(4))
    ),
    109: sub(  # 'm' = 16x7 - 3
        mul(const(16), sub(const(8), const(1))), add(const(1), const(2))
    ),
    110: sub(mul(const(16), sub(const(8), const(1))), const(2)),  # 'n' = 16x7 - 2
    111: sub(mul(const(16), sub(const(8), const(1))), const(1)),  # 'o' = 16x7 - 1
    115: add(  # 's' = 16x7 + 3
        mul(const(16), sub(const(8), const(1))), add(const(1), const(2))
    ),
}


def emit_token(target: Char, code: int, *payloads: int) -> list[Push]:
    """Push a token's code and fixed payloads per the arity table.

    Text-bearing tokens stream their glyph run afterwards; the caller closes
    it with push(target, const(tokens.TEXT_END))."""
    arity = tokens.ARITY[code]
    if len(payloads) != arity.payloads:
        raise ValueError(
            f"token {code} takes {arity.payloads} payload(s), got {len(payloads)}"
        )
    return [push(target, const(code)), *(push(target, const(p)) for p in payloads)]
