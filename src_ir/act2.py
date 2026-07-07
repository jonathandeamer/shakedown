"""Act II — block dispatcher (Spike A P2): list pass + paragraph pass.

Carrier choreography (design spec ping-pong, §6.3):
  PASS_LISTS:   Hecate (glyphs, countdown on Lady Macbeth) -> Lady Macbeth
  STAGE:        Lady Macbeth -> Macbeth (main); Horatio -> Puck (side)
  PASS_PARA:    Macbeth (+ Puck side) -> Lady Macbeth
  FRAME_REVERSE: Lady Macbeth -> Puck (unchanged from P1)

Registers during PASS_LISTS: Lady Macbeth = input countdown; Hecate = current
glyph; Macbeth = open-list depth (statically restored after frame pops);
Horatio = current item looseness (1 tight / 2 loose); Puck = saved marker
char. Macbeth's stack holds the open-list frame sentinels (kind per level)
above a -1 floor; Horatio's stack is the per-item looseness side channel
above a -1 floor.

The list pass emits item text directly onto the carrier bracketed as
[ITEM_START(-2), glyphs..., 0]; the item's looseness is pushed onto the side
channel at item end (completion order). PASS_PARA replaces each ITEM_START
with the LIST_ITEM code and the next side-channel value (the STAGE reverse
flips the side stack so first-completed pops first).
"""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    act,
    add,
    branch,
    const,
    eq,
    goto,
    gt,
    halt_act,
    let,
    lt,
    pop,
    push,
    scene,
    sub,
    val,
)
from src_ir import tokens
from src_ir.cast import HECATE, HORATIO, LADY_MACBETH, MACBETH, PUCK
from src_ir.stream import emit_token

_NEWLINE = const(10)
_SPACE = const(32)
_TAB = const(9)
_END = const(tokens.STREAM_END)


def _read(recall: str = "hewn_glyph"):
    """Pop the next input glyph into Hecate and decrement the countdown."""
    return [
        pop(HECATE, recall=recall),
        let(LADY_MACBETH, sub(val(LADY_MACBETH), const(1))),
    ]


ACT: Act = act(
    2,
    LADY_MACBETH,
    [
        # --- Frame entry: seed the carrier, side-channel, and frame floors.
        scene(
            "ACT_II_START",
            let(LADY_MACBETH, val(HORATIO)),
            push(LADY_MACBETH, _END),
            push(HORATIO, _END),
            goto("PASS_LISTS_SEED_FRAMES"),
        ),
        scene(
            "PASS_LISTS_SEED_FRAMES",
            push(MACBETH, _END),
            let(MACBETH, const(0)),
            goto("PASS_LISTS_BLOCK_START"),
        ),
        # --- Block-start gate: list markers only at doc start / after blank.
        scene(
            "PASS_LISTS_BLOCK_START",
            *_read(),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_LISTS_BLOCK_BLANK",
                else_="PASS_LISTS_GATE_UNORDERED",
            ),
        ),
        scene(
            "PASS_LISTS_BLOCK_BLANK",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_LISTS_DONE",
                else_="PASS_LISTS_BLOCK_START",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_GATE_UNORDERED",
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_MARK_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_MARK_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_MARK_SAVE_UL"),
            goto("PASS_LISTS_GATE_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_GATE_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_RAW_GLYPH"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_RAW_GLYPH"),
            goto("PASS_LISTS_MARK_SAVE_OL"),
            companion=HECATE,
        ),
        # --- Marker confirmation at block start.
        scene(
            "PASS_LISTS_MARK_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_MARK_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_MARK_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_OPEN_UL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_OPEN_UL"),
            goto("PASS_LISTS_RAW_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_MARK_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_MARK_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_MARK_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_MARK_TEST_OL"),
            goto("PASS_LISTS_RAW_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_MARK_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_OPEN_OL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_OPEN_OL"),
            goto("PASS_LISTS_RAW_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_RAW_REPLAY_SAVED",
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_RAW_REPLAY_SAVED_DOT",
            push(LADY_MACBETH, val(PUCK)),
            push(LADY_MACBETH, const(46)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=PUCK,
        ),
        # --- Raw copy mode: non-list text flows through untouched.
        scene(
            "PASS_LISTS_RAW_GLYPH",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_LISTS_RAW_AFTER_NEWLINE",
                else_="PASS_LISTS_RAW_NEXT",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_RAW_NEXT",
            *_read(),
            goto("PASS_LISTS_RAW_GLYPH"),
        ),
        scene(
            "PASS_LISTS_RAW_AFTER_NEWLINE",
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_DONE"),
            *_read("blank_glyph"),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_LISTS_RAW_BLANK",
                else_="PASS_LISTS_RAW_GLYPH",
            ),
        ),
        scene(
            "PASS_LISTS_RAW_BLANK",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_LISTS_DONE",
                else_="PASS_LISTS_BLOCK_START",
            ),
            companion=HECATE,
        ),
        # --- List open: token, frame sentinel, first item.
        scene(
            "PASS_LISTS_OPEN_UL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 1),
            push(MACBETH, const(1)),
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        scene(
            "PASS_LISTS_OPEN_OL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 2),
            push(MACBETH, const(2)),
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        scene(
            "PASS_LISTS_ITEM_BEGIN_TIGHT",
            let(HORATIO, const(1)),
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            goto("PASS_LISTS_ITEM_SKIP_SPACES"),
        ),
        scene(
            "PASS_LISTS_ITEM_BEGIN_LOOSE",
            let(HORATIO, const(2)),
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            goto("PASS_LISTS_ITEM_SKIP_SPACES"),
        ),
        scene(
            "PASS_LISTS_ITEM_SKIP_SPACES",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            goto("PASS_LISTS_ITEM_GLYPH"),
        ),
        # --- Item text: glyphs flow directly onto the carrier.
        scene(
            "PASS_LISTS_ITEM_GLYPH",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_ITEM_LINE_END"),
            push(LADY_MACBETH, val(HECATE)),
            goto("PASS_LISTS_ITEM_NEXT"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_ITEM_NEXT",
            *_read(),
            goto("PASS_LISTS_ITEM_GLYPH"),
        ),
        scene(
            "PASS_LISTS_ITEM_LINE_END",
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_END_OF_INPUT"),
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_1"),
            goto("PASS_LISTS_LINE_HEAD"),
        ),
        # --- Line head at indent 0 inside a list: sibling marker or lazy text.
        scene(
            "PASS_LISTS_LINE_HEAD",
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_SIB_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_SIB_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_SIB_SAVE_UL"),
            goto("PASS_LISTS_LINE_HEAD_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_LINE_HEAD_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_JOIN_LINE"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_JOIN_LINE"),
            goto("PASS_LISTS_SIB_SAVE_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_JOIN_LINE",
            push(LADY_MACBETH, _NEWLINE),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_SIB_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_SIB_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_SIB_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_SIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_SIB_EMIT"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_SIB_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_SIB_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_SIB_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_SIB_TEST_OL"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_SIB_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_SIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_SIB_EMIT"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_LAZY_REPLAY_SAVED",
            push(LADY_MACBETH, _NEWLINE),
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_LAZY_REPLAY_SAVED_DOT",
            push(LADY_MACBETH, _NEWLINE),
            push(LADY_MACBETH, val(PUCK)),
            push(LADY_MACBETH, const(46)),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_SIB_EMIT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            branch(
                eq(val(MACBETH), const(2)),
                then="PASS_LISTS_SIB_OUTDENT",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
        ),
        scene(
            "PASS_LISTS_SIB_OUTDENT",
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            let(MACBETH, const(1)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        # --- Indented line inside a list (no blank): nested marker or
        # --- outdented continuation (up to four spaces stripped).
        scene(
            "PASS_LISTS_INDENT_1",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_2"),
            goto("PASS_LISTS_INDENT_CLASSIFY"),
        ),
        scene(
            "PASS_LISTS_INDENT_2",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_3"),
            goto("PASS_LISTS_INDENT_CLASSIFY"),
        ),
        scene(
            "PASS_LISTS_INDENT_3",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_4"),
            goto("PASS_LISTS_INDENT_CLASSIFY"),
        ),
        scene(
            "PASS_LISTS_INDENT_4",
            push(LADY_MACBETH, _NEWLINE),
            *_read(),
            goto("PASS_LISTS_ITEM_GLYPH"),
        ),
        scene(
            "PASS_LISTS_INDENT_CLASSIFY",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_NEST_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_NEST_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_NEST_SAVE_UL"),
            goto("PASS_LISTS_INDENT_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_INDENT_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_JOIN_LINE"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_JOIN_LINE"),
            goto("PASS_LISTS_NEST_SAVE_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_NEST_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_NEST_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_NEST_EMIT_UL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_NEST_EMIT_UL"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_NEST_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_NEST_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_NEST_TEST_OL"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_NEST_EMIT_OL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_NEST_EMIT_OL"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_NEST_EMIT_UL",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            branch(
                eq(val(MACBETH), const(1)),
                then="PASS_LISTS_NEST_OPEN_UL",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
        ),
        scene(
            "PASS_LISTS_NEST_EMIT_OL",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            branch(
                eq(val(MACBETH), const(1)),
                then="PASS_LISTS_NEST_OPEN_OL",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
        ),
        scene(
            "PASS_LISTS_NEST_OPEN_UL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 1),
            push(MACBETH, const(1)),
            let(MACBETH, const(2)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        scene(
            "PASS_LISTS_NEST_OPEN_OL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 2),
            push(MACBETH, const(2)),
            let(MACBETH, const(2)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        # --- Blank line inside a list: continuation, sibling, or list end.
        scene(
            "PASS_LISTS_BLANK",
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_END_OF_INPUT"),
            *_read("blank_glyph"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_1"),
            goto("PASS_LISTS_BLANK_HEAD"),
        ),
        scene(
            "PASS_LISTS_BLANK_HEAD",
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_BSIB_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_BSIB_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_BSIB_SAVE_UL"),
            goto("PASS_LISTS_BLANK_HEAD_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_BLANK_HEAD_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_LIST_END"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_LIST_END"),
            goto("PASS_LISTS_BSIB_SAVE_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_BSIB_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_BSIB_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_BSIB_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BSIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_BSIB_EMIT"),
            goto("PASS_LISTS_LIST_END_REPLAY"),
        ),
        scene(
            "PASS_LISTS_BSIB_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_BSIB_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_BSIB_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_BSIB_TEST_OL"),
            goto("PASS_LISTS_LIST_END_REPLAY"),
        ),
        scene(
            "PASS_LISTS_BSIB_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BSIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_BSIB_EMIT"),
            goto("PASS_LISTS_LIST_END_REPLAY_DOT"),
        ),
        scene(
            "PASS_LISTS_BSIB_EMIT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            let(HORATIO, const(2)),
            push(HORATIO, val(HORATIO)),
            branch(
                eq(val(MACBETH), const(2)),
                then="PASS_LISTS_BSIB_OUTDENT",
                else_="PASS_LISTS_ITEM_BEGIN_LOOSE",
            ),
        ),
        scene(
            "PASS_LISTS_BSIB_OUTDENT",
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            let(MACBETH, const(1)),
            goto("PASS_LISTS_ITEM_BEGIN_LOOSE"),
        ),
        # Blank + indented continuation: the item is loose; the blank and the
        # outdented line join its text.
        scene(
            "PASS_LISTS_BLANK_INDENT_1",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_2"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_2",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_3"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_3",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_4"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_4",
            *_read(),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_JOIN",
            let(HORATIO, const(2)),
            push(LADY_MACBETH, _NEWLINE),
            push(LADY_MACBETH, _NEWLINE),
            goto("PASS_LISTS_ITEM_GLYPH"),
        ),
        # --- List end and input end.
        scene(
            "PASS_LISTS_LIST_END",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            goto("PASS_LISTS_CLOSE_ALL"),
        ),
        scene(
            "PASS_LISTS_LIST_END_REPLAY",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY"),
        ),
        scene(
            "PASS_LISTS_LIST_END_REPLAY_DOT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY_DOT"),
        ),
        scene(
            "PASS_LISTS_END_OF_INPUT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            goto("PASS_LISTS_CLOSE_ALL"),
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL",
            pop(MACBETH, recall="fallen_rampart"),
            branch(eq(val(MACBETH), _END), then="PASS_LISTS_CLOSE_ALL_DONE"),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL"),
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL_DONE",
            push(MACBETH, _END),
            let(MACBETH, const(0)),
            goto("PASS_LISTS_AFTER_LIST"),
        ),
        scene(
            "PASS_LISTS_AFTER_LIST",
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_LISTS_DONE",
                else_="PASS_LISTS_RAW_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL_REPLAY",
            pop(MACBETH, recall="fallen_rampart"),
            branch(eq(val(MACBETH), _END), then="PASS_LISTS_CLOSE_REPLAY_DONE"),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY"),
        ),
        scene(
            "PASS_LISTS_CLOSE_REPLAY_DONE",
            push(MACBETH, _END),
            let(MACBETH, const(0)),
            goto("PASS_LISTS_RAW_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL_REPLAY_DOT",
            pop(MACBETH, recall="fallen_rampart"),
            branch(
                eq(val(MACBETH), _END),
                then="PASS_LISTS_CLOSE_REPLAY_DOT_DONE",
            ),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY_DOT"),
        ),
        scene(
            "PASS_LISTS_CLOSE_REPLAY_DOT_DONE",
            push(MACBETH, _END),
            let(MACBETH, const(0)),
            goto("PASS_LISTS_RAW_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_DONE",
            goto("FRAME_STAGE_MAIN_OPEN"),
            companion=HECATE,
        ),
        # --- Staging: reverse the mixed stream onto Macbeth and the
        # --- looseness side channel onto Puck.
        scene(
            "FRAME_STAGE_MAIN_OPEN",
            push(MACBETH, _END),
            goto("FRAME_STAGE_MAIN_POP"),
        ),
        scene(
            "FRAME_STAGE_MAIN_POP",
            pop(LADY_MACBETH, recall="masons_stone"),
            branch(eq(val(LADY_MACBETH), _END), then="FRAME_STAGE_SIDE_OPEN"),
            push(MACBETH, val(LADY_MACBETH)),
            goto("FRAME_STAGE_MAIN_POP"),
        ),
        scene(
            "FRAME_STAGE_SIDE_OPEN",
            goto("FRAME_STAGE_SIDE_POP"),
            anchor=HORATIO,
            companion=PUCK,
        ),
        scene(
            "FRAME_STAGE_SIDE_POP",
            pop(HORATIO, recall="kept_measure"),
            branch(eq(val(HORATIO), _END), then="PASS_PARA_OPEN"),
            push(PUCK, val(HORATIO)),
            goto("FRAME_STAGE_SIDE_POP"),
            anchor=HORATIO,
        ),
        # --- Paragraph pass: walk the staged stream, form PARA tokens from
        # --- raw regions, finalize item frames from the side channel.
        scene(
            "PASS_PARA_OPEN",
            push(LADY_MACBETH, _END),
            goto("PASS_PARA_NEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_NEXT",
            pop(MACBETH, recall="staged_stone"),
            branch(eq(val(MACBETH), _END), then="FRAME_REVERSE_OPEN"),
            branch(eq(val(MACBETH), _NEWLINE), then="PASS_PARA_NEXT"),
            branch(
                eq(val(MACBETH), const(tokens.LIST_OPEN)),
                then="PASS_PARA_COPY_OPEN",
            ),
            branch(
                eq(val(MACBETH), const(tokens.LIST_CLOSE)),
                then="PASS_PARA_COPY_CLOSE",
            ),
            branch(eq(val(MACBETH), const(tokens.ITEM_START)), then="PASS_PARA_ITEM"),
            goto("PASS_PARA_OPEN_PARA"),
        ),
        scene(
            "PASS_PARA_COPY_OPEN",
            push(LADY_MACBETH, const(tokens.LIST_OPEN)),
            pop(MACBETH, recall="staged_stone"),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_NEXT"),
        ),
        scene(
            "PASS_PARA_COPY_CLOSE",
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            goto("PASS_PARA_NEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_ITEM",
            push(LADY_MACBETH, const(tokens.LIST_ITEM)),
            pop(PUCK, recall="kept_measure"),
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_PARA_ITEM_TEXT"),
        ),
        scene(
            "PASS_PARA_ITEM_TEXT",
            pop(MACBETH, recall="staged_stone"),
            push(LADY_MACBETH, val(MACBETH)),
            branch(
                eq(val(MACBETH), const(tokens.TEXT_END)),
                then="PASS_PARA_NEXT",
                else_="PASS_PARA_ITEM_TEXT",
            ),
        ),
        scene(
            "PASS_PARA_OPEN_PARA",
            *emit_token(LADY_MACBETH, tokens.PARA),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_TEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_TEXT",
            pop(MACBETH, recall="staged_stone"),
            branch(eq(val(MACBETH), _NEWLINE), then="PASS_PARA_NEWLINE"),
            branch(eq(val(MACBETH), _END), then="PASS_PARA_FINAL_CLOSE"),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_TEXT"),
        ),
        scene(
            "PASS_PARA_NEWLINE",
            pop(MACBETH, recall="staged_stone"),
            branch(eq(val(MACBETH), _NEWLINE), then="PASS_PARA_CLOSE_BLANK"),
            branch(eq(val(MACBETH), _END), then="PASS_PARA_FINAL_CLOSE"),
            push(LADY_MACBETH, _NEWLINE),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_TEXT"),
        ),
        scene(
            "PASS_PARA_CLOSE_BLANK",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("PASS_PARA_NEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_FINAL_CLOSE",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("FRAME_REVERSE_OPEN"),
            companion=MACBETH,
        ),
        # --- Final reverse onto Puck (P1 scenes, unchanged labels/titles).
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
