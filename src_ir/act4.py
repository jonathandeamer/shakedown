"""Act IV — stack-driven emission of the explicit block-container stream.

Prospero's stack borrows one sentinel-delimited region.  Each frame records
both its container kind and whether that container has already emitted a
child block; item frames additionally record tight/loose rendering.  Puck
carries the current stream token and output bytes.
"""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    Char,
    Op,
    Scene,
    act,
    add,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    print_char,
    push,
    scene as ir_scene,
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


def scene(
    label: str,
    *ops: Op,
    companion: Char | None = PUCK,
    anchor: Char | None = None,
) -> Scene:
    """Act-IV scenes always retain Puck as Prospero's stage companion."""
    return ir_scene(label, *ops, companion=companion, anchor=anchor)


# Container frames.  Adding ten marks that a child block has completed.
DOCUMENT_EMPTY = 16
DOCUMENT_USED = 17
LIST_UL_EMPTY = 21
LIST_OL_EMPTY = 22
LIST_UL_USED = 31
LIST_OL_USED = 32
LIST_UL_COMPLEX = 41
LIST_OL_COMPLEX = 42
LIST_UL_NESTED = 51
LIST_OL_NESTED = 52
LIST_UL_NESTED_USED = 64
LIST_OL_NESTED_USED = 65
LIST_OL_NESTED_CLOSED = 75
ITEM_TIGHT_EMPTY = 23
ITEM_LOOSE_EMPTY = 24
ITEM_TIGHT_USED = 33
ITEM_LOOSE_USED = 34
ITEM_LOOSE_COMPLEX = 44
QUOTE_EMPTY = 18
QUOTE_USED = 19


ACT: Act = act(
    4,
    PROSPERO,
    [
        scene(
            "ACT_IV_START",
            push(PROSPERO, const(tokens.STREAM_END)),
            push(PROSPERO, const(DOCUMENT_EMPTY)),
            goto("SCRIBE_POP_TOKEN"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_POP_TOKEN",
            pop(PUCK, recall="heralds_present_word"),
            branch(eq(val(PUCK), const(tokens.STREAM_END)), then="ACT_IV_DONE"),
            goto("SCRIBE_DISPATCH_TOKEN"),
        ),
        scene(
            "SCRIBE_DISPATCH_TOKEN",
            branch(eq(val(PUCK), const(tokens.STREAM_END)), then="ACT_IV_DONE"),
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
                then="SCRIBE_EMIT_PARAGRAPH_CLOSE",
                else_="SCRIBE_TEST_LIST_OPEN",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_LIST_OPEN",
            branch(
                eq(val(PUCK), const(tokens.LIST_OPEN)),
                then="SCRIBE_LIST_OPEN",
                else_="SCRIBE_ITEM_FIRST",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_ITEM_FIRST",
            branch(
                eq(val(PUCK), const(tokens.LIST_ITEM)),
                then="SCRIBE_ITEM_LOOSENESS",
                else_="SCRIBE_ITEM_END",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_ITEM_END",
            branch(
                eq(val(PUCK), const(tokens.ITEM_CLOSE)),
                then="SCRIBE_ITEM_CLOSE",
                else_="SCRIBE_LIST_CLOSE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_LIST_CLOSE",
            branch(
                eq(val(PUCK), const(tokens.LIST_CLOSE)),
                then="SCRIBE_TOP_CLOSE",
                else_="SCRIBE_NESTED_OPEN",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_NESTED_OPEN",
            branch(
                eq(val(PUCK), const(tokens.BLOCKQUOTE_OPEN)),
                then="SCRIBE_BLOCKQUOTE_OPEN",
                else_="SCRIBE_NESTED_CLOSE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_NESTED_CLOSE",
            branch(
                eq(val(PUCK), const(tokens.BLOCKQUOTE_CLOSE)),
                then="SCRIBE_BLOCKQUOTE_CLOSE",
                else_="SCRIBE_TEST_ANCHOR_OPEN",
            ),
            companion=PUCK,
        ),

        # Paragraph opening peeks at the parent frame.  A used frame inserts a
        # blank-line block separator; loose items retain paragraph tags while
        # tight items deliberately suppress them.
        scene(
            "SCRIBE_EMIT_PARAGRAPH_OPEN",
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_EMPTY)), then="SCRIBE_ITEM_TEXT_TIGHT"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_USED)), then="SCRIBE_EMIT_PARAGRAPH_BREAK"),
            branch(eq(val(PROSPERO), const(ITEM_LOOSE_EMPTY)), then="SCRIBE_EMIT_ITEM_OPEN_LOOSE"),
            branch(eq(val(PROSPERO), const(ITEM_LOOSE_USED)), then="SCRIBE_EMIT_PARAGRAPH_BREAK"),
            branch(eq(val(PROSPERO), const(DOCUMENT_USED)), then="SCRIBE_EMIT_PARAGRAPH_BREAK"),
            branch(eq(val(PROSPERO), const(QUOTE_USED)), then="SCRIBE_EMIT_PARAGRAPH_BREAK"),
            goto("SCRIBE_EMIT_ITEM_OPEN_TIGHT"),
        ),
        scene(
            "SCRIBE_ITEM_TEXT_TIGHT",
            push(PROSPERO, const(ITEM_TIGHT_EMPTY)),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_ITEM_SUBSEQUENT",
            push(PROSPERO, val(PROSPERO)),
            push(PROSPERO, val(PUCK)),
            *_emit(10),
            goto("SCRIBE_ITEM_BLOCK_OPEN"),
        ),
        scene(
            "SCRIBE_EMIT_ITEM_OPEN_LOOSE",
            push(PROSPERO, const(ITEM_LOOSE_EMPTY)),
            *_emit(*_bytes("<p>")),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_BREAK",
            push(PROSPERO, val(PROSPERO)),
            *_emit(10, 10, *_bytes("<p>")),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ITEM_OPEN_TIGHT",
            push(PROSPERO, val(PROSPERO)),
            *_emit(*_bytes("<p>")),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_CLOSE",
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_EMPTY)), then="SCRIBE_EMIT_LOOSE_END"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_USED)), then="SCRIBE_EMIT_LOOSE_END"),
            branch(eq(val(PROSPERO), const(ITEM_LOOSE_EMPTY)), then="SCRIBE_TEST_FINAL_CLOSE"),
            branch(eq(val(PROSPERO), const(ITEM_LOOSE_USED)), then="SCRIBE_TEST_FINAL_CLOSE"),
            goto("SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE"),
        ),
        scene(
            "SCRIBE_EMIT_LOOSE_END",
            push(PROSPERO, const(ITEM_TIGHT_USED)),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_TEST_FINAL_CLOSE",
            push(PROSPERO, const(ITEM_LOOSE_USED)),
            *_emit(*_bytes("</p>")),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE",
            *_emit(*_bytes("</p>")),
            branch(eq(val(PROSPERO), const(DOCUMENT_EMPTY)), then="SCRIBE_OUTER_RELEASE"),
            branch(eq(val(PROSPERO), const(DOCUMENT_USED)), then="SCRIBE_OUTER_RELEASE"),
            goto("SCRIBE_CONTAINER_RETURN"),
        ),
        scene(
            "SCRIBE_STASH_UL_CLOSE_TOP",
            push(PROSPERO, add(val(PROSPERO), const(20))),
            push(PROSPERO, val(PUCK)),
            *_emit(*_bytes("</li>")),
            pop(PROSPERO, recall="sealed_gates_colour"),
            let(PUCK, val(PROSPERO)),
            goto("SCRIBE_DISPATCH_TOKEN"),
        ),
        scene(
            "SCRIBE_STASH_OL_CLOSE_TOP",
            push(PROSPERO, add(val(PROSPERO), const(10))),
            push(PROSPERO, val(PUCK)),
            *_emit(*_bytes("</li>")),
            pop(PROSPERO, recall="sealed_gates_colour"),
            let(PUCK, val(PROSPERO)),
            goto("SCRIBE_DISPATCH_TOKEN"),
        ),

        # List containers choose their separator from the parent frame, then
        # retain their kind until LIST_CLOSE.
        scene(
            "SCRIBE_LIST_OPEN",
            pop(PUCK, recall="heralds_present_word"),
            pop(PROSPERO, recall="sealed_gates_colour"),
            push(PROSPERO, val(PROSPERO)),
            push(PROSPERO, val(PUCK)),
            branch(eq(val(PROSPERO), const(LIST_UL_EMPTY)), then="SCRIBE_EMIT_UL_OPEN_NESTED"),
            branch(eq(val(PROSPERO), const(LIST_UL_USED)), then="SCRIBE_EMIT_UL_OPEN_NESTED"),
            branch(eq(val(PROSPERO), const(LIST_OL_EMPTY)), then="SCRIBE_EMIT_UL_OPEN_NESTED"),
            branch(eq(val(PROSPERO), const(LIST_OL_USED)), then="SCRIBE_EMIT_UL_OPEN_NESTED"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_USED)), then="SCRIBE_EMIT_UL_OPEN_NESTED"),
            branch(eq(val(PROSPERO), const(ITEM_LOOSE_USED)), then="SCRIBE_EMIT_UL_OPEN_NESTED"),
            branch(eq(val(PROSPERO), const(DOCUMENT_USED)), then="SCRIBE_EMIT_LIST_BLOCK_SEP"),
            branch(eq(val(PROSPERO), const(QUOTE_USED)), then="SCRIBE_EMIT_LIST_BLOCK_SEP"),
            goto("SCRIBE_EMIT_UL_OPEN_TOP"),
        ),
        scene(
            "SCRIBE_EMIT_UL_OPEN_NESTED",
            *_emit(10),
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(1)), then="SCRIBE_ITEM_BLOCK_CLOSE"),
            push(PROSPERO, const(LIST_OL_EMPTY)),
            *_emit(*_bytes("<ol>")),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_OL_OPEN_NESTED",
            *_emit(*_bytes("</ol>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_EMIT_LIST_BLOCK_SEP",
            *_emit(10, 10),
            goto("SCRIBE_EMIT_UL_OPEN_TOP"),
        ),
        scene(
            "SCRIBE_EMIT_UL_OPEN_TOP",
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(1)), then="SCRIBE_EMIT_OL_OPEN_TOP"),
            push(PROSPERO, const(LIST_OL_EMPTY)),
            *_emit(*_bytes("<ol>"), 10),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_OL_OPEN_TOP",
            push(PROSPERO, const(LIST_UL_EMPTY)),
            *_emit(*_bytes("<ul>"), 10),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_ITEM_LOOSENESS",
            pop(PUCK, recall="heralds_present_word"),
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(LIST_UL_COMPLEX)), then="SCRIBE_ITEM_TEXT_LOOSE"),
            branch(eq(val(PROSPERO), const(LIST_OL_COMPLEX)), then="SCRIBE_LOOSE_NEWLINE"),
            branch(eq(val(PROSPERO), const(LIST_UL_USED)), then="SCRIBE_ITEM_SUBSEQUENT"),
            branch(eq(val(PROSPERO), const(LIST_OL_USED)), then="SCRIBE_ITEM_SUBSEQUENT"),
            branch(eq(val(PROSPERO), const(LIST_UL_NESTED_USED)), then="SCRIBE_ITEM_SUBSEQUENT"),
            branch(eq(val(PROSPERO), const(LIST_OL_NESTED_USED)), then="SCRIBE_ITEM_SUBSEQUENT"),
            push(PROSPERO, val(PROSPERO)),
            push(PROSPERO, val(PUCK)),
            goto("SCRIBE_ITEM_BLOCK_OPEN"),
        ),
        scene(
            "SCRIBE_ITEM_TEXT_LOOSE",
            push(PROSPERO, const(LIST_UL_USED)),
            push(PROSPERO, val(PUCK)),
            *_emit(10),
            goto("SCRIBE_ITEM_BLOCK_OPEN"),
        ),
        scene(
            "SCRIBE_LOOSE_NEWLINE",
            push(PROSPERO, const(LIST_OL_USED)),
            push(PROSPERO, val(PUCK)),
            *_emit(10),
            goto("SCRIBE_ITEM_BLOCK_OPEN"),
        ),
        scene(
            "SCRIBE_EMIT_LI_CLOSE",
            pop(PUCK, recall="heralds_parting_word"),
            pop(PROSPERO, recall="sealed_gates_colour"),
            goto("SCRIBE_STASH_UL_CLOSE_TOP"),
        ),
        scene(
            "SCRIBE_ITEM_BLOCK_OPEN",
            pop(PROSPERO, recall="sealed_gates_colour"),
            *_emit(*_bytes("<li>")),
            branch(eq(val(PROSPERO), const(2)), then="SCRIBE_EMIT_FINAL_LIST_NEWLINE"),
            push(PROSPERO, const(ITEM_TIGHT_EMPTY)),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_ITEM_CLOSE",
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(ITEM_LOOSE_COMPLEX)), then="SCRIBE_EMIT_LI_CLOSE"),
            pop(PUCK, recall="heralds_parting_word"),
            branch(eq(val(PUCK), const(tokens.LIST_OPEN)), then="SCRIBE_LIST_OPEN"),
            pop(PROSPERO, recall="sealed_gates_colour"),
            goto("SCRIBE_STASH_OL_CLOSE_TOP"),
        ),
        scene(
            "SCRIBE_AFTER_NESTED_CLOSE",
            *_emit(*_bytes("</li>")),
            push(PROSPERO, const(LIST_UL_USED)),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_TOP_CLOSE",
            # LIST_CLOSE: pop the list frame, emit its kind-specific close,
            # then mark the enclosing frame used.
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(LIST_UL_USED)), then="SCRIBE_STASH_UL_CLOSE_NESTED"),
            branch(eq(val(PROSPERO), const(LIST_UL_EMPTY)), then="SCRIBE_STASH_UL_CLOSE_NESTED"),
            branch(eq(val(PROSPERO), const(LIST_UL_COMPLEX)), then="SCRIBE_STASH_UL_CLOSE_NESTED"),
            branch(eq(val(PROSPERO), const(LIST_OL_NESTED)), then="SCRIBE_EMIT_OL_OPEN_NESTED"),
            branch(eq(val(PROSPERO), const(LIST_OL_NESTED_USED)), then="SCRIBE_EMIT_OL_OPEN_NESTED"),
            branch(eq(val(PROSPERO), const(LIST_OL_NESTED_CLOSED)), then="SCRIBE_EMIT_OL_OPEN_NESTED"),
            goto("SCRIBE_STASH_OL_CLOSE_NESTED"),
        ),
        scene(
            "SCRIBE_STASH_UL_CLOSE_NESTED",
            pop(PROSPERO, recall="sealed_gates_colour"),
            push(PROSPERO, val(PROSPERO)),
            branch(eq(val(PROSPERO), const(DOCUMENT_EMPTY)), then="SCRIBE_UL_CLOSE_LEADING_SEP"),
            branch(eq(val(PROSPERO), const(DOCUMENT_USED)), then="SCRIBE_UL_CLOSE_LEADING_SEP"),
            branch(eq(val(PROSPERO), const(QUOTE_EMPTY)), then="SCRIBE_UL_CLOSE_LEADING_SEP"),
            branch(eq(val(PROSPERO), const(QUOTE_USED)), then="SCRIBE_UL_CLOSE_LEADING_SEP"),
            *_emit(*_bytes("</ul>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_UL_CLOSE_LEADING_SEP",
            *_emit(10, *_bytes("</ul>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_STASH_OL_CLOSE_NESTED",
            pop(PROSPERO, recall="sealed_gates_colour"),
            push(PROSPERO, val(PROSPERO)),
            branch(eq(val(PROSPERO), const(DOCUMENT_EMPTY)), then="SCRIBE_OL_CLOSE_LEADING_SEP"),
            branch(eq(val(PROSPERO), const(DOCUMENT_USED)), then="SCRIBE_OL_CLOSE_LEADING_SEP"),
            branch(eq(val(PROSPERO), const(QUOTE_EMPTY)), then="SCRIBE_OL_CLOSE_LEADING_SEP"),
            branch(eq(val(PROSPERO), const(QUOTE_USED)), then="SCRIBE_OL_CLOSE_LEADING_SEP"),
            *_emit(*_bytes("</ol>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_OL_CLOSE_LEADING_SEP",
            *_emit(10, *_bytes("</ol>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_LIST_BLOCK_SEP",
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(LIST_UL_EMPTY)), then="SCRIBE_AFTER_NESTED_CLOSE"),
            branch(eq(val(PROSPERO), const(LIST_UL_USED)), then="SCRIBE_AFTER_NESTED_CLOSE"),
            branch(eq(val(PROSPERO), const(DOCUMENT_EMPTY)), then="SCRIBE_LIST_OUTER_RELEASE"),
            branch(eq(val(PROSPERO), const(DOCUMENT_USED)), then="SCRIBE_LIST_OUTER_RELEASE"),
            branch(eq(val(PROSPERO), const(QUOTE_EMPTY)), then="SCRIBE_LIST_CONTAINER_RETURN"),
            branch(eq(val(PROSPERO), const(QUOTE_USED)), then="SCRIBE_LIST_CONTAINER_RETURN"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_EMPTY)), then="SCRIBE_CONTAINER_LOOKAHEAD"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_USED)), then="SCRIBE_CONTAINER_LOOKAHEAD"),
            goto("SCRIBE_EMIT_PARAGRAPH_BREAK"),
        ),
        scene("SCRIBE_EMIT_FINAL_LIST_NEWLINE", push(PROSPERO, const(ITEM_LOOSE_EMPTY)), goto("SCRIBE_POP_TOKEN")),
        scene("SCRIBE_CONTAINER_RETURN", push(PROSPERO, const(QUOTE_USED)), goto("SCRIBE_POP_TOKEN")),
        scene("SCRIBE_CONTAINER_LOOKAHEAD", push(PROSPERO, const(ITEM_TIGHT_USED)), goto("SCRIBE_POP_TOKEN")),
        scene(
            "SCRIBE_LIST_OUTER_RELEASE",
            push(PROSPERO, const(DOCUMENT_USED)),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_LIST_CONTAINER_RETURN",
            push(PROSPERO, const(QUOTE_USED)),
            goto("SCRIBE_POP_TOKEN"),
        ),

        scene(
            "SCRIBE_BLOCKQUOTE_OPEN",
            pop(PROSPERO, recall="sealed_gates_colour"),
            push(PROSPERO, val(PROSPERO)),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_USED)), then="SCRIBE_LOOSE_NEWLINE_GLYPH"),
            branch(eq(val(PROSPERO), const(ITEM_LOOSE_USED)), then="SCRIBE_LOOSE_NEWLINE_GLYPH"),
            branch(eq(val(PROSPERO), const(DOCUMENT_USED)), then="SCRIBE_LOOSE_NEWLINE_GLYPH"),
            branch(eq(val(PROSPERO), const(QUOTE_USED)), then="SCRIBE_LOOSE_NEWLINE_GLYPH"),
            *_emit(*_bytes("<blockquote>"), 10, 32, 32),
            push(PROSPERO, const(QUOTE_EMPTY)),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_LOOSE_NEWLINE_GLYPH",
            *_emit(10, 10),
            *_emit(*_bytes("<blockquote>"), 10, 32, 32),
            push(PROSPERO, const(QUOTE_EMPTY)),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_ITEM_BLOCK_CLOSE",
            push(PROSPERO, const(LIST_UL_EMPTY)),
            *_emit(*_bytes("<ul>")),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_BLOCKQUOTE_CLOSE",
            pop(PROSPERO, recall="sealed_gates_colour"),
            *_emit(10, *_bytes("</blockquote>")),
            pop(PROSPERO, recall="sealed_gates_colour"),
            branch(eq(val(PROSPERO), const(DOCUMENT_EMPTY)), then="SCRIBE_OUTER_RELEASE"),
            branch(eq(val(PROSPERO), const(DOCUMENT_USED)), then="SCRIBE_OUTER_RELEASE"),
            branch(eq(val(PROSPERO), const(QUOTE_EMPTY)), then="SCRIBE_CONTAINER_RETURN"),
            branch(eq(val(PROSPERO), const(QUOTE_USED)), then="SCRIBE_CONTAINER_RETURN"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_EMPTY)), then="SCRIBE_CONTAINER_LOOKAHEAD"),
            branch(eq(val(PROSPERO), const(ITEM_TIGHT_USED)), then="SCRIBE_CONTAINER_LOOKAHEAD"),
            goto("SCRIBE_QUOTED_PARAGRAPH"),
        ),
        scene("SCRIBE_OUTER_RELEASE", push(PROSPERO, const(DOCUMENT_USED)), goto("SCRIBE_POP_TOKEN")),
        scene("SCRIBE_QUOTED_PARAGRAPH", push(PROSPERO, const(ITEM_LOOSE_COMPLEX)), goto("SCRIBE_POP_TOKEN")),

        scene(
            "SCRIBE_TEST_ANCHOR_OPEN",
            branch(eq(val(PUCK), const(tokens.ANCHOR_OPEN)), then="SCRIBE_EMIT_ANCHOR_OPEN", else_="SCRIBE_TEST_ANCHOR_TITLE"),
            companion=PUCK,
        ),
        scene("SCRIBE_TEST_ANCHOR_TITLE", branch(eq(val(PUCK), const(tokens.ANCHOR_TITLE)), then="SCRIBE_EMIT_ANCHOR_TITLE", else_="SCRIBE_TEST_ANCHOR_TEXT"), companion=PUCK),
        scene("SCRIBE_TEST_ANCHOR_TEXT", branch(eq(val(PUCK), const(tokens.ANCHOR_TEXT)), then="SCRIBE_EMIT_ANCHOR_TEXT", else_="SCRIBE_TEST_ANCHOR_CLOSE"), companion=PUCK),
        scene("SCRIBE_TEST_ANCHOR_CLOSE", branch(eq(val(PUCK), const(tokens.ANCHOR_CLOSE)), then="SCRIBE_EMIT_ANCHOR_CLOSE", else_="SCRIBE_EMIT_PAYLOAD"), companion=PUCK),
        scene("SCRIBE_EMIT_PAYLOAD", print_char(PUCK), goto("SCRIBE_POP_TOKEN")),
        scene("SCRIBE_EMIT_ANCHOR_OPEN", *_emit(*_bytes('<a href="')), goto("SCRIBE_POP_TOKEN")),
        scene("SCRIBE_EMIT_ANCHOR_TITLE", *_emit(*_bytes('" title="')), goto("SCRIBE_POP_TOKEN")),
        scene("SCRIBE_EMIT_ANCHOR_TEXT", *_emit(*_bytes('\">')), goto("SCRIBE_POP_TOKEN")),
        scene("SCRIBE_EMIT_ANCHOR_CLOSE", *_emit(*_bytes("</a>")), goto("SCRIBE_POP_TOKEN")),
        scene(
            "ACT_IV_DONE",
            pop(PROSPERO, recall="sealed_gates_colour"),
            pop(PROSPERO, recall="sealed_gates_colour"),
            *_emit(10),
            halt_act(),
            companion=PUCK,
        ),
    ],
)
