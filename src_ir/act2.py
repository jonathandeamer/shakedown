"""Act II — block pass (Slice 1 pass-through). Ported from the hand-authored
fragment; behavior identical, quirks included (the fixed reverse count of 315
when the glyph count exceeds 128, and the 1/0 stream markers). See the plan's
Behavioral ground truth table."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    act,
    branch,
    const,
    eq,
    goto,
    gt,
    halt_act,
    let,
    mul,
    pop,
    push,
    scene,
    sub,
    val,
)
from src_ir.cast import HECATE, HORATIO, LADY_MACBETH, PUCK

_NEWLINE = const(10)

ACT: Act = act(
    2,
    LADY_MACBETH,
    [
        scene(
            "ACT_II_START",
            let(LADY_MACBETH, val(HORATIO)),
            push(LADY_MACBETH, const(1)),
            goto("MASON_READ_PARAGRAPH_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "MASON_READ_PARAGRAPH_GLYPH",
            pop(HECATE, recall="hewn_glyph"),
            let(LADY_MACBETH, sub(val(LADY_MACBETH), const(1))),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="MASON_CLOSE_PARAGRAPH",
                else_="MASON_KEEP_PARAGRAPH_GLYPH",
            ),
        ),
        scene(
            "MASON_KEEP_PARAGRAPH_GLYPH",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="MASON_CLOSE_FINAL_PARAGRAPH",
                else_="MASON_READ_PARAGRAPH_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "MASON_CLOSE_PARAGRAPH",
            push(LADY_MACBETH, const(0)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="MASON_OPEN_REVERSE_STREAM",
                else_="MASON_SKIP_BLANK_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "MASON_SKIP_BLANK_GLYPH",
            pop(HECATE, recall="blank_glyph"),
            let(LADY_MACBETH, sub(val(LADY_MACBETH), const(1))),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="MASON_AFTER_BLANK_GLYPH",
                else_="MASON_OPEN_PARAGRAPH_WITH_GLYPH",
            ),
        ),
        scene(
            "MASON_AFTER_BLANK_GLYPH",
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="MASON_OPEN_REVERSE_STREAM",
                else_="MASON_SKIP_BLANK_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "MASON_OPEN_PARAGRAPH_WITH_GLYPH",
            push(LADY_MACBETH, const(1)),
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="MASON_CLOSE_FINAL_PARAGRAPH",
                else_="MASON_READ_PARAGRAPH_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "MASON_CLOSE_FINAL_PARAGRAPH",
            push(LADY_MACBETH, const(0)),
            goto("MASON_OPEN_REVERSE_STREAM"),
            companion=HECATE,
        ),
        scene(
            "MASON_OPEN_REVERSE_STREAM",
            branch(
                gt(val(HORATIO), const(128)),
                then="MASON_SET_SLICE_ONE_REVERSE_COUNT",
                else_="MASON_SET_SHORT_REVERSE_COUNT",
            ),
            companion=PUCK,
        ),
        scene(
            "MASON_SET_SLICE_ONE_REVERSE_COUNT",
            # 315 = 9 × 35; split to stay within the 4-operator arithmetic limit
            # (test_numeric_recipe_complexity_stays_bounded).
            let(PUCK, const(9)),
            let(PUCK, mul(val(PUCK), const(35))),
            goto("HERALD_REVERSE_TOKEN_STREAM"),
        ),
        scene(
            "MASON_SET_SHORT_REVERSE_COUNT",
            let(PUCK, val(HORATIO)),
            goto("HERALD_REVERSE_TOKEN_STREAM"),
        ),
        scene(
            "HERALD_REVERSE_TOKEN_STREAM",
            pop(LADY_MACBETH, recall="masons_stone"),
            push(PUCK, val(LADY_MACBETH)),
            let(PUCK, sub(val(PUCK), const(1))),
            branch(
                eq(val(PUCK), const(0)),
                then="ACT_II_DONE",
                else_="HERALD_REVERSE_TOKEN_STREAM",
            ),
        ),
        scene("ACT_II_DONE", halt_act(), companion=PUCK),
    ],
)
