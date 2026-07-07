"""Act IV — emit pass over the tokenized stream (Spike A P2). Prospero
anchors and speaks; Puck carries the current token / scratch. Dispatch pops
until the STREAM_END sentinel; paragraph emission is the Slice-1 port
unchanged (docs/superpowers/notes/act4-port-audit.md); list emission follows
the P2 plan's oracle-derived byte rules.

List-flow invariants (from Act II construction, enforced by the G2 dumps):
- LIST_ITEM (5) and LIST_CLOSE (6) never reach SCRIBE_DISPATCH_TOKEN; they
  are consumed by lookahead inside the list flow. Only LIST_OPEN needs a
  dispatch arm.
- A LIST_OPEN is always followed by a LIST_ITEM.
- A nested LIST_CLOSE is always followed by LIST_ITEM or LIST_CLOSE; a
  top-level LIST_CLOSE never is — so close depth is decided by lookahead
  and no depth register is needed.
- Prospero's value is scratch (popped kind, then stashed lookahead);
  Prospero's stack holds the open list kinds."""

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
    push,
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


def _bytes(text: str) -> list[int]:
    return list(text.encode())


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
                else_="SCRIBE_TEST_LIST_OPEN",
            ),
            companion=PUCK,
        ),
        # Dispatch arm (only LIST_OPEN reaches the top-level chain).
        scene(
            "SCRIBE_TEST_LIST_OPEN",
            branch(
                eq(val(PUCK), const(tokens.LIST_OPEN)),
                then="SCRIBE_LIST_OPEN",
                else_="SCRIBE_TEST_ANCHOR_OPEN",
            ),
            companion=PUCK,
        ),
        # List open: kind onto Prospero's stack. Top-level opens arrive from the
        # dispatch chain; nested opens arrive from SCRIBE_ITEM_END.
        scene(
            "SCRIBE_LIST_OPEN",
            pop(PUCK, recall="heralds_present_word"),
            push(PROSPERO, val(PUCK)),
            branch(
                eq(val(PUCK), const(1)),
                then="SCRIBE_EMIT_UL_OPEN_TOP",
                else_="SCRIBE_EMIT_OL_OPEN_TOP",
            ),
        ),
        scene(
            "SCRIBE_EMIT_UL_OPEN_TOP",
            # <ul>\n
            *_emit(*_bytes("<ul>"), 10),
            goto("SCRIBE_ITEM_FIRST"),
        ),
        scene(
            "SCRIBE_EMIT_OL_OPEN_TOP",
            # <ol>\n
            *_emit(*_bytes("<ol>"), 10),
            goto("SCRIBE_ITEM_FIRST"),
        ),
        scene(
            "SCRIBE_NESTED_OPEN",
            # Reached from an item's text end: the enclosing <li> stays open.
            pop(PUCK, recall="heralds_present_word"),
            push(PROSPERO, val(PUCK)),
            branch(
                eq(val(PUCK), const(1)),
                then="SCRIBE_EMIT_UL_OPEN_NESTED",
                else_="SCRIBE_EMIT_OL_OPEN_NESTED",
            ),
        ),
        scene(
            "SCRIBE_EMIT_UL_OPEN_NESTED",
            # \n<ul>
            *_emit(10, *_bytes("<ul>")),
            goto("SCRIBE_ITEM_FIRST"),
        ),
        scene(
            "SCRIBE_EMIT_OL_OPEN_NESTED",
            # \n<ol>
            *_emit(10, *_bytes("<ol>")),
            goto("SCRIBE_ITEM_FIRST"),
        ),
        # Items. A LIST_OPEN is always followed by a LIST_ITEM, so the first-item
        # entry consumes the item code directly; subsequent items arrive with
        # their code already consumed by the </li> lookahead.
        scene(
            "SCRIBE_ITEM_FIRST",
            pop(PUCK, recall="heralds_present_word"),
            goto("SCRIBE_ITEM_LOOSENESS"),
        ),
        scene(
            "SCRIBE_ITEM_SUBSEQUENT",
            # \n between </li> and the next <li>
            *_emit(10),
            goto("SCRIBE_ITEM_LOOSENESS"),
        ),
        scene(
            "SCRIBE_ITEM_LOOSENESS",
            pop(PUCK, recall="heralds_present_word"),
            branch(
                eq(val(PUCK), const(2)),
                then="SCRIBE_EMIT_ITEM_OPEN_LOOSE",
                else_="SCRIBE_EMIT_ITEM_OPEN_TIGHT",
            ),
        ),
        scene(
            "SCRIBE_EMIT_ITEM_OPEN_TIGHT",
            *_emit(*_bytes("<li>")),
            goto("SCRIBE_ITEM_TEXT_TIGHT"),
        ),
        scene(
            "SCRIBE_ITEM_TEXT_TIGHT",
            pop(PUCK, recall="heralds_present_word"),
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="SCRIBE_ITEM_END"),
            print_char(PUCK),
            goto("SCRIBE_ITEM_TEXT_TIGHT"),
        ),
        scene(
            "SCRIBE_EMIT_ITEM_OPEN_LOOSE",
            *_emit(*_bytes("<li><p>")),
            goto("SCRIBE_ITEM_TEXT_LOOSE"),
        ),
        scene(
            "SCRIBE_ITEM_TEXT_LOOSE",
            pop(PUCK, recall="heralds_present_word"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="SCRIBE_EMIT_LOOSE_END",
            ),
            branch(eq(val(PUCK), const(10)), then="SCRIBE_LOOSE_NEWLINE"),
            print_char(PUCK),
            goto("SCRIBE_ITEM_TEXT_LOOSE"),
        ),
        scene(
            "SCRIBE_LOOSE_NEWLINE",
            # Two newlines mark a paragraph break inside the loose item; one is
            # literal text. Stash the lookahead glyph before _emit reuses Puck.
            pop(PUCK, recall="heralds_parting_word"),
            branch(eq(val(PUCK), const(10)), then="SCRIBE_EMIT_PARAGRAPH_BREAK"),
            let(PROSPERO, val(PUCK)),
            goto("SCRIBE_LOOSE_NEWLINE_GLYPH"),
        ),
        scene(
            "SCRIBE_LOOSE_NEWLINE_GLYPH",
            *_emit(10),
            let(PUCK, val(PROSPERO)),
            print_char(PUCK),
            goto("SCRIBE_ITEM_TEXT_LOOSE"),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_BREAK",
            # </p>\n\n<p>
            *_emit(*_bytes("</p>"), 10, 10, *_bytes("<p>")),
            goto("SCRIBE_ITEM_TEXT_LOOSE"),
        ),
        scene(
            "SCRIBE_EMIT_LOOSE_END",
            *_emit(*_bytes("</p>")),
            goto("SCRIBE_ITEM_END"),
            companion=PROSPERO,
        ),
        scene(
            "SCRIBE_ITEM_END",
            # Lookahead: a nested LIST_OPEN keeps this <li> open.
            pop(PUCK, recall="heralds_parting_word"),
            branch(eq(val(PUCK), const(tokens.LIST_OPEN)), then="SCRIBE_NESTED_OPEN"),
            let(PROSPERO, val(PUCK)),
            goto("SCRIBE_EMIT_LI_CLOSE"),
        ),
        scene(
            "SCRIBE_EMIT_LI_CLOSE",
            # The lookahead (LIST_ITEM or LIST_CLOSE) is stashed in Prospero.
            *_emit(*_bytes("</li>")),
            branch(
                eq(val(PROSPERO), const(tokens.LIST_ITEM)),
                then="SCRIBE_ITEM_SUBSEQUENT",
            ),
            goto("SCRIBE_LIST_CLOSE"),
        ),
        # List close. Entered with the LIST_CLOSE code already consumed. Pops
        # the kind, then one lookahead token; the lookahead picks nested vs top.
        scene(
            "SCRIBE_LIST_CLOSE",
            pop(PROSPERO, recall="sealed_gates_colour"),
            pop(PUCK, recall="heralds_parting_word"),
            branch(eq(val(PUCK), const(tokens.LIST_ITEM)), then="SCRIBE_NESTED_CLOSE"),
            branch(
                eq(val(PUCK), const(tokens.LIST_CLOSE)),
                then="SCRIBE_NESTED_CLOSE",
            ),
            goto("SCRIBE_TOP_CLOSE"),
        ),
        scene(
            "SCRIBE_NESTED_CLOSE",
            branch(
                eq(val(PROSPERO), const(1)),
                then="SCRIBE_STASH_UL_CLOSE_NESTED",
                else_="SCRIBE_STASH_OL_CLOSE_NESTED",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_STASH_UL_CLOSE_NESTED",
            # Kind is consumed by the branch above; stash the lookahead before
            # emission reuses Puck.
            let(PROSPERO, val(PUCK)),
            # </ul></li> — the parent item closes with the nested list.
            *_emit(*_bytes("</ul></li>")),
            goto("SCRIBE_AFTER_NESTED_CLOSE"),
        ),
        scene(
            "SCRIBE_STASH_OL_CLOSE_NESTED",
            let(PROSPERO, val(PUCK)),
            *_emit(*_bytes("</ol></li>")),
            goto("SCRIBE_AFTER_NESTED_CLOSE"),
        ),
        scene(
            "SCRIBE_AFTER_NESTED_CLOSE",
            branch(
                eq(val(PROSPERO), const(tokens.LIST_ITEM)),
                then="SCRIBE_ITEM_SUBSEQUENT",
            ),
            # Otherwise the stashed lookahead is another LIST_CLOSE, already
            # consumed — exactly SCRIBE_LIST_CLOSE's entry state.
            goto("SCRIBE_LIST_CLOSE"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TOP_CLOSE",
            branch(
                eq(val(PROSPERO), const(1)),
                then="SCRIBE_STASH_UL_CLOSE_TOP",
                else_="SCRIBE_STASH_OL_CLOSE_TOP",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_STASH_UL_CLOSE_TOP",
            let(PROSPERO, val(PUCK)),
            # \n</ul>
            *_emit(10, *_bytes("</ul>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_STASH_OL_CLOSE_TOP",
            let(PROSPERO, val(PUCK)),
            *_emit(10, *_bytes("</ol>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_LIST_BLOCK_SEP",
            branch(
                eq(val(PROSPERO), const(tokens.STREAM_END)),
                then="SCRIBE_EMIT_FINAL_LIST_NEWLINE",
            ),
            goto("SCRIBE_EMIT_LIST_BLOCK_SEP"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_EMIT_FINAL_LIST_NEWLINE",
            *_emit(10),
            goto("ACT_IV_DONE"),
        ),
        scene(
            "SCRIBE_EMIT_LIST_BLOCK_SEP",
            *_emit(10, 10),
            let(PUCK, val(PROSPERO)),
            goto("SCRIBE_DISPATCH_TOKEN"),
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
