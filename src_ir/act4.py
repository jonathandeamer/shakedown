"""Act IV — emit pass over the tokenized stream (Spike A P1). Prospero
anchors and speaks; Puck carries the current token / scratch. Dispatch pops
until the STREAM_END sentinel (src_ir/tokens.py) — the Slice-1 fixed stream
count is retired. The final-paragraph close (single trailing newline) is
decided by a one-token lookahead at each TEXT_END. Emission ground truth is
unchanged from the Slice-1 port (docs/superpowers/notes/act4-port-audit.md)."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    Op,
    act,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    print_char,
    scene,
    val,
)
from src_ir import tokens
from src_ir.cast import PROSPERO, PUCK
from src_ir.stream import RECIPES


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
            goto("SCRIBE_POP_TOKEN"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_POP_TOKEN",
            pop(PUCK, recall="heralds_present_word"),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="ACT_IV_DONE",
            ),
            goto("SCRIBE_DISPATCH_TOKEN"),
        ),
        scene(
            "SCRIBE_DISPATCH_TOKEN",
            branch(
                eq(val(PUCK), const(tokens.PARA)),
                then="SCRIBE_EMIT_PARAGRAPH_OPEN",
                else_="SCRIBE_TEST_PARAGRAPH_CLOSE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_PARAGRAPH_CLOSE",
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
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
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_OPEN",
            # <a href="
            *_emit(60, 97, 32, 104, 114, 101, 102, 61, 34),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_TITLE",
            # " title="
            *_emit(34, 32, 116, 105, 116, 108, 101, 61, 34),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_TEXT",
            # ">
            *_emit(34, 62),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_CLOSE",
            # </a>
            *_emit(60, 47, 97, 62),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_OPEN",
            # <p>
            *_emit(60, 112, 62),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_TEST_FINAL_CLOSE",
            # Lookahead: the paragraph just closed; peek at the next stream
            # item to choose the final (single-newline) close. Stashed in
            # Prospero (his count register is retired) because _emit's
            # per-byte loop below overwrites Puck's value.
            pop(PUCK, recall="heralds_parting_word"),
            let(PROSPERO, val(PUCK)),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE",
                else_="SCRIBE_EMIT_PARAGRAPH_CLOSE",
            ),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_CLOSE",
            # </p>\n\n — then recall the stashed lookahead and dispatch it.
            *_emit(60, 47, 112, 62, 10, 10),
            let(PUCK, val(PROSPERO)),
            goto("SCRIBE_DISPATCH_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE",
            # </p>\n — the lookahead consumed STREAM_END; the play is done.
            *_emit(60, 47, 112, 62, 10),
            goto("ACT_IV_DONE"),
        ),
        scene("ACT_IV_DONE", halt_act(), companion=PUCK),
    ],
)
