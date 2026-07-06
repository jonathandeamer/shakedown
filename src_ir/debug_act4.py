"""Debug Act IV — token-stream dump. Shadow of src_ir/act4.py used by
`./shakedown-debug`: acts I–III run unchanged, then this play pops each
inter-act stream item until the STREAM_END sentinel and prints it as an
integer (Open your heart!) followed by a newline, instead of emitting HTML.
The sentinel itself is not printed: the dump is exactly the stream, so it
serves as the G2 baseline artifact (tests/fixtures/token_stream/)."""

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
    print_char,
    print_int,
    scene,
    val,
)
from src_ir import tokens
from src_ir.cast import PROSPERO, PUCK

# The debug play lives outside the globbed production literary ledger (a
# src/*-literary.toml entry for these would orphan them against the
# production source and fail test_scene_titles_have_toml_entries_and_match_source).
# Titles are inlined at render time instead — plain literals, outside
# literary scope per docs/superpowers/notes/correctness-first-spl-workflow.md.
SCENE_TITLES: dict[str, str] = {
    "DBG_START": "The scribe takes his station.",
    "DBG_POP": "The herald yields one word and it is counted aloud.",
    "DBG_DONE": "The counting is done.",
}

ACT: Act = act(
    4,
    PROSPERO,
    [
        scene(
            "DBG_START",
            goto("DBG_POP"),
            companion=PUCK,
        ),
        scene(
            "DBG_POP",
            pop(PUCK, recall="heralds_present_word"),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="DBG_DONE",
            ),
            print_int(PUCK),
            let(PUCK, const(10)),
            print_char(PUCK),
            goto("DBG_POP"),
        ),
        scene("DBG_DONE", halt_act(), companion=PUCK),
    ],
)
