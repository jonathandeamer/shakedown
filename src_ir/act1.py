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
from src_ir.act1_ref_pure import build_ref_scenes
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
        # --- Amendment A1/A3: pure-op reference strip (Task 2L Step 2) ---
        *build_ref_scenes(),
        scene(
            "ACT_I_DONE",
            pop(HORATIO, recall="kept_tally"),
            # Stage Hecate's final exit (phase_exit): her preprocessing done and
            # her tally kept, the witch-queen leaves the witness with a parting
            # curse in her own incantatory register (cursed / rotten / horrid).
            # These let(HORATIO, val(HORATIO)) lines are identity no-ops: they
            # write Horatio's own current value back, so the kept_tally carrier
            # that Act II reads at ACT_II_START (let(LADY_MACBETH, val(HORATIO)))
            # is preserved and emitted HTML is unchanged. Hecate is the speaker
            # because the target (HORATIO) differs from the Act I anchor.
            # See docs/superpowers/notes/literary-artefact-improvements.md (1).
            # Two lines, not three: the comparator is a deterministic
            # seed-pick and no run of three consecutive op-seeds yields three
            # distinct phrases here, so a two-blow curse (cursed / horrid)
            # keeps the phrases distinct.
            let(HORATIO, val(HORATIO)),
            let(HORATIO, val(HORATIO)),
            halt_act(),
        ),
    ],
)
