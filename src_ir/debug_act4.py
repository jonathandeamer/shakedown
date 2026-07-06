"""Debug Act IV — token-stream dump. Shadow of src_ir/act4.py used by
`./shakedown-debug`: acts I–III run unchanged, then this play pops each
inter-act token and prints it as an integer (Open your heart!) followed by a
newline, instead of emitting HTML. Shares the stream-measure constants and
recipe with act4.py so the two can never drift."""

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
    pop,
    print_char,
    print_int,
    scene,
    sub,
    val,
)
from src_ir.cast import HORATIO, PROSPERO, PUCK
from src_ir.stream import STREAM_THRESHOLD, slice_one_stream_expr

# The debug play lives outside the globbed production literary ledger (a
# src/*-literary.toml entry for these would orphan them against the
# production source and fail test_scene_titles_have_toml_entries_and_match_source).
# Titles are inlined at render time instead — verbatim from the prior
# hand-authored debug/40-act4-token-dump.spl.
SCENE_TITLES: dict[str, str] = {
    "DBG_START": "The scribe weighs the stream measure.",
    "DBG_OLD_MEASURE": "The old cell keeps its measure.",
    "DBG_SHORT_MEASURE": "The short cell takes Horatio's measure.",
    "DBG_LOOP": "The scribe asks if words remain.",
    "DBG_POP": "The herald yields one word and it is counted aloud.",
    "DBG_DONE": "The counting is done.",
}

ACT: Act = act(
    4,
    PROSPERO,
    [
        scene(
            "DBG_START",
            branch(
                gt(val(HORATIO), const(STREAM_THRESHOLD)),
                then="DBG_OLD_MEASURE",
                else_="DBG_SHORT_MEASURE",
            ),
            companion=PUCK,
        ),
        scene(
            "DBG_OLD_MEASURE",
            let(PROSPERO, slice_one_stream_expr()),
            goto("DBG_LOOP"),
            companion=PUCK,
        ),
        scene(
            "DBG_SHORT_MEASURE",
            let(PROSPERO, val(HORATIO)),
            goto("DBG_LOOP"),
            companion=PUCK,
        ),
        scene(
            "DBG_LOOP",
            branch(
                eq(val(PROSPERO), const(0)),
                then="DBG_DONE",
                else_="DBG_POP",
            ),
            companion=PUCK,
        ),
        scene(
            "DBG_POP",
            pop(PUCK, recall="heralds_present_word"),
            let(PROSPERO, sub(val(PROSPERO), const(1))),
            print_int(PUCK),
            let(PUCK, const(10)),
            print_char(PUCK),
            goto("DBG_LOOP"),
        ),
        scene("DBG_DONE", halt_act(), companion=PUCK),
    ],
)
