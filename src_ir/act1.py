"""Act I — pre-process. Ported from the hand-authored fragment; behavior
identical, quirks included (Slice 1 unconditionally strips two trailing
reference-definition lines). See the plan's Behavioral ground truth."""

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
    halt_act,
    let,
    pop,
    push,
    read_char,
    scene,
    sub,
    val,
)
from src_ir.cast import HECATE, HORATIO, PUCK, ROSALIND

_NEWLINE = const(10)
_EOF = const(-1)

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
            goto("HECATE_READ_INPUT"),
        ),
        scene(
            "HECATE_READ_INPUT",
            read_char(PUCK),
            branch(eq(val(PUCK), _EOF), then="HECATE_TEST_FINAL_GLYPH"),
            push(PUCK, val(PUCK)),
            let(HECATE, add(val(HECATE), const(1))),
            goto("HECATE_READ_INPUT"),
        ),
        scene(
            "HECATE_TEST_FINAL_GLYPH",
            pop(PUCK, recall="cauldron_dreg"),
            let(HECATE, sub(val(HECATE), const(1))),
            branch(
                eq(val(PUCK), _NEWLINE),
                then="HECATE_RESTORE_FINAL_NEWLINE",
                else_="HECATE_LINE_STRIP_SECOND_REFERENCE",
            ),
        ),
        scene(
            "HECATE_RESTORE_FINAL_NEWLINE",
            push(PUCK, val(PUCK)),
            let(HECATE, add(val(HECATE), const(1))),
            push(PUCK, val(PUCK)),
            let(HECATE, add(val(HECATE), const(1))),
            goto("HECATE_HAND_COUNT_TO_HORATIO"),
        ),
        scene(
            "HECATE_LINE_STRIP_SECOND_REFERENCE",
            pop(PUCK, recall="sealed_second_shelf"),
            let(HECATE, sub(val(HECATE), const(1))),
            branch(
                eq(val(PUCK), _NEWLINE),
                then="HECATE_LINE_STRIP_FIRST_REFERENCE",
                else_="HECATE_LINE_STRIP_SECOND_REFERENCE",
            ),
        ),
        scene(
            "HECATE_LINE_STRIP_FIRST_REFERENCE",
            pop(PUCK, recall="sealed_first_shelf"),
            let(HECATE, sub(val(HECATE), const(1))),
            branch(
                eq(val(PUCK), _NEWLINE),
                then="HECATE_LINE_RESTORE_BOUNDARY",
                else_="HECATE_LINE_STRIP_FIRST_REFERENCE",
            ),
        ),
        scene(
            "HECATE_LINE_RESTORE_BOUNDARY",
            push(PUCK, val(PUCK)),
            let(HECATE, add(val(HECATE), const(1))),
            goto("HECATE_HAND_COUNT_TO_HORATIO"),
        ),
        scene(
            "HECATE_HAND_COUNT_TO_HORATIO",
            let(HORATIO, val(HECATE)),
            push(HORATIO, val(HORATIO)),
            goto("HECATE_REVERSE_CHECK"),
        ),
        scene(
            "HECATE_REVERSE_CHECK",
            branch(
                eq(val(HORATIO), const(0)),
                then="ACT_I_DONE",
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
            pop(PUCK, recall="cauldron_dreg"),
            let(HECATE, val(PUCK)),
            push(HECATE, val(HECATE)),
            goto("HECATE_OPEN_COUNT_DECREMENT"),
        ),
        scene(
            "HECATE_OPEN_COUNT_DECREMENT",
            let(HORATIO, sub(val(HORATIO), const(1))),
            goto("HECATE_REVERSE_CHECK"),
        ),
        scene(
            "ACT_I_DONE",
            pop(HORATIO, recall="kept_tally"),
            halt_act(),
        ),
    ],
)
