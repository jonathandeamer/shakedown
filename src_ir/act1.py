"""Act I — pre-process. Slice 2 replaces the Slice 1 trailing-line strip with
bounded normalization: preserve all content, expand tabs to four-column stops,
and ensure the carrier ends in exactly two newlines."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    Let,
    Push,
    act,
    add,
    branch,
    const,
    eq,
    goto,
    gt,
    halt_act,
    let,
    mod,
    pop,
    push,
    read_char,
    scene,
    sub,
    val,
)
from src_ir.cast import HECATE, HORATIO, PUCK, ROSALIND

_EOF = const(-1)
_NEWLINE = const(10)
_SPACE = const(32)
_TAB = const(9)
_TAB_STOP = const(4)

_SENTINELS = [1, 101, 0, 2, 102, 201]


def _push_sentinels() -> list[Let | Push]:
    ops = []
    for value in _SENTINELS:
        ops.append(let(ROSALIND, const(value)))
        ops.append(push(ROSALIND, val(ROSALIND)))
    return ops


ACT: Act = act(
    1,
    HECATE,
    [
        scene(
            "ACT_I_START",
            *_push_sentinels(),
            let(HECATE, const(0)),
            let(ROSALIND, const(0)),
            goto("HECATE_READ_INPUT"),
        ),
        scene(
            "HECATE_READ_INPUT",
            read_char(PUCK),
            branch(eq(val(PUCK), _EOF), then="HECATE_NORMALIZE_FINAL"),
            branch(eq(val(PUCK), _TAB), then="HECATE_DETAB_OPEN"),
            goto("HECATE_DETAB_GLYPH"),
        ),
        scene(
            "HECATE_NORMALIZE_FINAL",
            branch(
                eq(val(HORATIO), const(0)),
                then="HECATE_LINE_STRIP_FIRST_REFERENCE",
            ),
            goto("HECATE_HANDOFF_FALLBACK"),
            companion=PUCK,
        ),
        scene(
            "HECATE_HANDOFF_FALLBACK",
            pop(PUCK, recall="normalized_line_mark"),
            let(HECATE, sub(val(HORATIO), const(1))),
            goto("HECATE_TEST_FINAL_GLYPH"),
        ),
        scene(
            "HECATE_TEST_FINAL_GLYPH",
            branch(
                eq(val(PUCK), _NEWLINE),
                then="HECATE_LINE_STRIP_FIRST_REFERENCE",
                else_="HECATE_LINE_RESTORE_BOUNDARY",
            ),
            companion=PUCK,
        ),
        scene(
            "HECATE_LINE_STRIP_FIRST_REFERENCE",
            let(ROSALIND, const(2)),
            goto("HECATE_RESTORE_FINAL_NEWLINE"),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_LINE_RESTORE_BOUNDARY",
            let(ROSALIND, const(3)),
            goto("HECATE_RESTORE_FINAL_NEWLINE"),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_RESTORE_FINAL_NEWLINE",
            let(HORATIO, val(HECATE)),
            branch(
                eq(val(PUCK), _EOF),
                then="HECATE_NORMALIZE_CLOSE",
                else_="HECATE_DETAB_GLYPH",
            ),
            companion=HORATIO,
        ),
        scene(
            "HECATE_DETAB_OPEN",
            let(ROSALIND, sub(_TAB_STOP, mod(val(HECATE), _TAB_STOP))),
            goto("HECATE_DETAB_COLUMN_TWO"),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_DETAB_COLUMN_TWO",
            let(PUCK, _SPACE),
            push(PUCK, val(PUCK)),
            goto("HECATE_DETAB_COLUMN_THREE"),
        ),
        scene(
            "HECATE_DETAB_COLUMN_THREE",
            let(HORATIO, add(val(HORATIO), const(1))),
            goto("HECATE_DETAB_COLUMN_FOUR"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_DETAB_COLUMN_FOUR",
            let(HECATE, add(val(HECATE), const(1))),
            let(ROSALIND, sub(val(ROSALIND), const(1))),
            branch(
                eq(val(ROSALIND), const(0)),
                then="HECATE_READ_INPUT",
                else_="HECATE_DETAB_COLUMN_TWO",
            ),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_DETAB_GLYPH",
            push(PUCK, val(PUCK)),
            goto("HECATE_HAND_NORMALIZED"),
        ),
        scene(
            "HECATE_HAND_NORMALIZED",
            let(HORATIO, add(val(HORATIO), const(1))),
            goto("HECATE_NORMALIZE_LINE"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_NORMALIZE_LINE",
            branch(gt(val(ROSALIND), const(0)), then="HECATE_NORMALIZE_BLANK"),
            branch(eq(val(PUCK), _NEWLINE), then="HECATE_NORMALIZE_BLANK"),
            let(HECATE, add(val(HECATE), const(1))),
            goto("HECATE_READ_INPUT"),
            companion=PUCK,
        ),
        scene(
            "HECATE_NORMALIZE_BLANK",
            let(HECATE, const(0)),
            branch(
                eq(val(ROSALIND), const(0)),
                then="HECATE_READ_INPUT",
                else_="HECATE_COLUMN_RECALL",
            ),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_COLUMN_RECALL",
            let(ROSALIND, sub(val(ROSALIND), const(1))),
            goto("HECATE_LINE_STRIP_SECOND_REFERENCE"),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_LINE_STRIP_SECOND_REFERENCE",
            branch(
                eq(val(ROSALIND), const(0)),
                then="HECATE_HAND_COUNT_TO_HORATIO",
                else_="HECATE_NORMALIZE_CLOSE",
            ),
            companion=HORATIO,
        ),
        scene(
            "HECATE_NORMALIZE_CLOSE",
            let(PUCK, _NEWLINE),
            push(PUCK, val(PUCK)),
            goto("HECATE_HAND_NORMALIZED"),
        ),
        scene(
            "HECATE_HAND_COUNT_TO_HORATIO",
            push(HORATIO, val(HORATIO)),
            goto("HECATE_REVERSE_CHECK"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_REVERSE_CHECK",
            branch(
                eq(val(HORATIO), const(0)),
                then="HECATE_REF_OPEN",
                else_="HECATE_OPEN_REVERSE_POP",
            ),
            companion=HORATIO,
        ),
        scene(
            "HECATE_OPEN_REVERSE_POP",
            goto("HECATE_REVERSE_POP"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REVERSE_POP",
            pop(PUCK, recall="detab_column_mark"),
            let(HECATE, val(PUCK)),
            push(HECATE, val(HECATE)),
            goto("HECATE_OPEN_COUNT_DECREMENT"),
        ),
        scene(
            "HECATE_OPEN_COUNT_DECREMENT",
            let(HORATIO, sub(val(HORATIO), const(1))),
            goto("HECATE_REVERSE_CHECK"),
            companion=HORATIO,
        ),
        # --- Amendment A1: reference-definition strip + Rosalind table ---
        # IR interpreter runs scripts.splc.act1_ref_strip on HECATE_REF_OPEN
        # (A1.2 stack machine) then jumps to ACT_I_DONE. The A1.3 labels are
        # chained so every reserved surface is reachable for lowering; the
        # pure-op bodies that replace this chain/intrinsic land in a later
        # Task 2 iteration.
        scene(
            "HECATE_REF_OPEN",
            goto("HECATE_REF_NEXT"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_REF_NEXT",
            goto("HECATE_REF_LEAD"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_LEAD",
            goto("HECATE_REF_FOUR_SPACE"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_REF_FOUR_SPACE",
            goto("HECATE_REF_BRACKET"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_BRACKET",
            goto("HECATE_REF_LABEL"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_LABEL",
            goto("HECATE_REF_COLON"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_COLON",
            goto("HECATE_REF_URL_WS"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_URL_WS",
            goto("HECATE_REF_ANGLE"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_REF_ANGLE",
            goto("HECATE_REF_URL"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_URL",
            goto("HECATE_REF_TITLE"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_TITLE",
            goto("HECATE_REF_TITLE_NL"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_TITLE_NL",
            goto("HECATE_REF_FOLD"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_FOLD",
            goto("HECATE_REF_ENCODE"),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_REF_ENCODE",
            goto("HECATE_REF_STORE"),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_REF_STORE",
            goto("HECATE_REF_KEEP"),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_REF_KEEP",
            goto("HECATE_REF_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_REPLAY",
            goto("HECATE_REF_NL"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_NL",
            goto("HECATE_REF_REVERSE"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_REF_REVERSE",
            goto("HECATE_REF_FINISH"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_FINISH",
            goto("ACT_I_DONE"),
            companion=HORATIO,
        ),
        scene(
            "ACT_I_DONE",
            pop(HORATIO, recall="kept_tally"),
            halt_act(),
        ),
    ],
)
