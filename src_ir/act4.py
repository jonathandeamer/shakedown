"""Act IV — emit pass (Slice 1 token-stream to HTML). Ported from the
hand-authored fragment; behavior identical. Anchor Prospero holds the
remaining stream count; Puck carries the current token / scratch. See the
Act IV port-readiness audit (docs/superpowers/notes/act4-port-audit.md) for
the decoded ground truth this module reproduces."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    Op,
    act,
    branch,
    const,
    eq,
    goto,
    gt,
    halt_act,
    let,
    pop,
    print_char,
    scene,
    sub,
    val,
)
from src_ir import tokens
from src_ir.cast import HORATIO, PROSPERO, PUCK
from src_ir.stream import RECIPES, STREAM_THRESHOLD, slice_one_stream_expr


def _emit(*codes: int) -> list[Op]:
    """One `let`/`print_char` pair per output byte, on Puck."""
    ops: list[Op] = []
    for code in codes:
        ops.append(let(PUCK, RECIPES.get(code, const(code))))
        ops.append(print_char(PUCK))
    return ops


ACT: Act = act(
    4,
    PROSPERO,
    [
        scene(
            "ACT_IV_START",
            branch(
                gt(val(HORATIO), const(STREAM_THRESHOLD)),
                then="SCRIBE_SET_SLICE_ONE_STREAM_COUNT",
                else_="SCRIBE_SET_SHORT_STREAM_COUNT",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_SET_SLICE_ONE_STREAM_COUNT",
            let(PROSPERO, slice_one_stream_expr()),
            goto("SCRIBE_STREAM_CHECK"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_SET_SHORT_STREAM_COUNT",
            let(PROSPERO, val(HORATIO)),
            goto("SCRIBE_STREAM_CHECK"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_STREAM_CHECK",
            branch(
                eq(val(PROSPERO), const(0)),
                then="ACT_IV_DONE",
                else_="SCRIBE_POP_TOKEN",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_POP_TOKEN",
            pop(PUCK, recall="heralds_present_word"),
            let(PROSPERO, sub(val(PROSPERO), const(1))),
            branch(
                eq(val(PUCK), const(tokens.PARA)),
                then="SCRIBE_EMIT_PARAGRAPH_OPEN",
                else_="SCRIBE_TEST_PARAGRAPH_CLOSE",
            ),
        ),
        scene(
            "SCRIBE_TEST_PARAGRAPH_CLOSE",
            branch(
                eq(val(PUCK), const(0)),
                then="SCRIBE_TEST_FINAL_CLOSE",
                else_="SCRIBE_TEST_ANCHOR_OPEN",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_ANCHOR_OPEN",
            branch(
                eq(val(PUCK), const(tokens.ANCHOR_OPEN)),
                then="SCRIBE_EMIT_ANCHOR_OPEN",
                else_="SCRIBE_TEST_ANCHOR_TITLE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_ANCHOR_TITLE",
            branch(
                eq(val(PUCK), const(tokens.ANCHOR_TITLE)),
                then="SCRIBE_EMIT_ANCHOR_TITLE",
                else_="SCRIBE_TEST_ANCHOR_TEXT",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_ANCHOR_TEXT",
            branch(
                eq(val(PUCK), const(tokens.ANCHOR_TEXT)),
                then="SCRIBE_EMIT_ANCHOR_TEXT",
                else_="SCRIBE_TEST_ANCHOR_CLOSE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_ANCHOR_CLOSE",
            branch(
                eq(val(PUCK), const(tokens.ANCHOR_CLOSE)),
                then="SCRIBE_EMIT_ANCHOR_CLOSE",
                else_="SCRIBE_EMIT_PAYLOAD",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_EMIT_PAYLOAD",
            print_char(PUCK),
            goto("SCRIBE_STREAM_CHECK"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_OPEN",
            # <a href="
            *_emit(60, 97, 32, 104, 114, 101, 102, 61, 34),
            goto("SCRIBE_STREAM_CHECK"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_TITLE",
            # " title="
            *_emit(34, 32, 116, 105, 116, 108, 101, 61, 34),
            goto("SCRIBE_STREAM_CHECK"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_TEXT",
            # ">
            *_emit(34, 62),
            goto("SCRIBE_STREAM_CHECK"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_CLOSE",
            # </a>
            *_emit(60, 47, 97, 62),
            goto("SCRIBE_STREAM_CHECK"),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_OPEN",
            # <p>
            *_emit(60, 112, 62),
            goto("SCRIBE_STREAM_CHECK"),
        ),
        scene(
            "SCRIBE_TEST_FINAL_CLOSE",
            branch(
                eq(val(PROSPERO), const(0)),
                then="SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE",
                else_="SCRIBE_EMIT_PARAGRAPH_CLOSE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_CLOSE",
            # </p>\n\n
            *_emit(60, 47, 112, 62, 10, 10),
            goto("SCRIBE_STREAM_CHECK"),
        ),
        scene(
            "SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE",
            # </p>\n
            *_emit(60, 47, 112, 62, 10),
            goto("SCRIBE_STREAM_CHECK"),
        ),
        scene("ACT_IV_DONE", halt_act(), companion=PUCK),
    ],
)
