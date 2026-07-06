"""src_ir.stream: shared cross-act constants and <=4-operator recipes."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.literary_surfaces import load_literary_surfaces
from scripts.splc.ir import BinOp, Char, Const, Expr

LITERARY_TOML = Path(__file__).parent.parent / "src" / "literary.toml"

_FOLD = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
}


def _eval(expr: Expr) -> int:
    if isinstance(expr, Const):
        return expr.value
    assert isinstance(expr, BinOp), expr
    return _FOLD[expr.op](_eval(expr.left), _eval(expr.right))


def _phrase_ops(expr: Expr) -> int:
    from scripts.splc.lower import _render_expr
    from scripts.splc.prose import ProseEngine

    prose = ProseEngine(load_literary_surfaces(LITERARY_TOML))
    phrase = _render_expr(expr, Char.PUCK, Char.ROMEO, prose)
    return len(re.findall(r"\b(sum|difference|product|quotient|square)\b", phrase))


def test_stream_constants_and_count_exprs() -> None:
    from src_ir.stream import (
        SLICE_ONE_GLYPH_COUNT,
        SLICE_ONE_STREAM_COUNT,
        STREAM_THRESHOLD,
        slice_one_glyph_expr,
        slice_one_stream_expr,
    )

    assert STREAM_THRESHOLD == 128
    assert SLICE_ONE_GLYPH_COUNT == 315
    assert SLICE_ONE_STREAM_COUNT == 387
    assert _eval(slice_one_glyph_expr()) == 315
    assert _eval(slice_one_stream_expr()) == 387
    assert _phrase_ops(slice_one_glyph_expr()) <= 4
    assert _phrase_ops(slice_one_stream_expr()) <= 4


def test_recipes_evaluate_to_their_keys_within_bound() -> None:
    from src_ir.stream import RECIPES

    expected_keys = {47, 59, 61, 62, 63, 91, 107, 109, 110, 111, 115}
    assert set(RECIPES) == expected_keys
    for value, expr in RECIPES.items():
        assert _eval(expr) == value
        assert _phrase_ops(expr) <= 4, value
