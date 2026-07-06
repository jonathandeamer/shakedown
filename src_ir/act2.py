"""Act II — block dispatcher skeleton (Spike A P1). One production pass
(paragraph formation) inside the frame: sentinel-seeded carrier stacks and an
explicit final reverse onto Puck, so order restoration is unconditional.

Pass ordering slots (architecture spec §4.2, matching _RunBlockGamut):
headers -> horizontal rules -> lists -> code blocks -> blockquotes ->
HTML re-hash -> paragraph formation. Only paragraph formation exists; each
future pass lands as a contiguous PASS_<NAME>_* scene group inserted before
the pass that follows it, reading one carrier stack and producing onto the
other (Lady Macbeth <-> Macbeth ping-pong; Macbeth's stack is reserved for
frame sentinels, so a pass needing frames must not write to him — design
spec §6.3). The FRAME_REVERSE_* scenes always drain the last carrier.

Slice-1 quirks preserved: the unconditional leading PARA push (empty input
keeps its crash shape) and the 1/0 paragraph framing, which is exactly the
PARA token encoding (code 1, glyph run, TEXT_END). The Slice-1 fixed reverse
count (315 above the 128 threshold) is retired: the tokenized stream is
bottom-terminated by STREAM_END, making counts structurally unnecessary
(design spec, cross-act impact)."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    act,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    push,
    scene,
    sub,
    val,
)
from src_ir import tokens
from src_ir.cast import HECATE, HORATIO, LADY_MACBETH, PUCK
from src_ir.stream import emit_token

_NEWLINE = const(10)

ACT: Act = act(
    2,
    LADY_MACBETH,
    [
        scene(
            "ACT_II_START",
            let(LADY_MACBETH, val(HORATIO)),
            push(LADY_MACBETH, const(tokens.STREAM_END)),
            *emit_token(LADY_MACBETH, tokens.PARA),
            goto("PASS_PARA_READ_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_READ_GLYPH",
            pop(HECATE, recall="hewn_glyph"),
            let(LADY_MACBETH, sub(val(LADY_MACBETH), const(1))),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_PARA_CLOSE_PARAGRAPH",
                else_="PASS_PARA_KEEP_GLYPH",
            ),
        ),
        scene(
            "PASS_PARA_KEEP_GLYPH",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_PARA_CLOSE_FINAL",
                else_="PASS_PARA_READ_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_CLOSE_PARAGRAPH",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="FRAME_REVERSE_OPEN",
                else_="PASS_PARA_SKIP_BLANK",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_SKIP_BLANK",
            pop(HECATE, recall="blank_glyph"),
            let(LADY_MACBETH, sub(val(LADY_MACBETH), const(1))),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_PARA_AFTER_BLANK",
                else_="PASS_PARA_OPEN_WITH_GLYPH",
            ),
        ),
        scene(
            "PASS_PARA_AFTER_BLANK",
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="FRAME_REVERSE_OPEN",
                else_="PASS_PARA_SKIP_BLANK",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_OPEN_WITH_GLYPH",
            *emit_token(LADY_MACBETH, tokens.PARA),
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_PARA_CLOSE_FINAL",
                else_="PASS_PARA_READ_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_CLOSE_FINAL",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("FRAME_REVERSE_OPEN"),
            companion=HECATE,
        ),
        scene(
            "FRAME_REVERSE_OPEN",
            push(PUCK, const(tokens.STREAM_END)),
            goto("FRAME_REVERSE_POP"),
        ),
        scene(
            "FRAME_REVERSE_POP",
            pop(LADY_MACBETH, recall="masons_stone"),
            branch(
                eq(val(LADY_MACBETH), const(tokens.STREAM_END)),
                then="ACT_II_DONE",
            ),
            push(PUCK, val(LADY_MACBETH)),
            goto("FRAME_REVERSE_POP"),
        ),
        scene("ACT_II_DONE", halt_act(), companion=PUCK),
    ],
)
