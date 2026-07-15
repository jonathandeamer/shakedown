"""Act II — block dispatcher (Spike A P2): list pass + paragraph pass.

Carrier choreography (design spec ping-pong, §6.3):
  PASS_LISTS:   Hecate (glyphs, countdown on Lady Macbeth) -> Lady Macbeth
  STAGE:        Lady Macbeth -> Macbeth
  PASS_PARA:    Macbeth -> Lady Macbeth
  FRAME_REVERSE: Lady Macbeth -> Puck (unchanged from P1)

Registers during PASS_LISTS: Lady Macbeth = input countdown; Hecate = current
glyph; Macbeth = open-list depth (statically restored after frame pops);
Horatio = quote-open state; Puck = saved marker char. Macbeth's stack holds
the open-list frame sentinels (kind per level) above a -1 floor.

The list pass emits item content onto the mixed carrier bracketed as
[ITEM_START(-2), looseness, glyphs..., 0, ITEM_CLOSE]. PASS_PARA replaces each
ITEM_START with LIST_ITEM, forms PARA blocks from raw regions, and copies
ITEM_CLOSE and other structural tokens unchanged.
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
from src_ir.stream import RECIPES, emit_token

_NEWLINE = const(10)
_SPACE = const(32)
_TAB = const(9)
_END = const(tokens.STREAM_END)
_PARA_START = const(tokens.HEADER)
_BLOCKQUOTE_MARK = RECIPES[62]


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
        # --- Frame entry: seed the carrier and frame floor.
        scene(
            "ACT_II_START",
            let(LADY_MACBETH, val(HORATIO)),
            push(LADY_MACBETH, _END),
            let(HORATIO, const(0)),
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
                else_="PASS_HR_GATE",
            ),
        ),
        scene(
            "PASS_HR_GATE",
            let(HORATIO, const(0)),
            goto("PASS_HR_GATE_MARKER"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HR_GATE_MARKER",
            let(PUCK, const(0)),
            branch(eq(val(HECATE), _SPACE), then="PASS_HR_SAVE"),
            branch(eq(val(HECATE), const(42)), then="PASS_HR_MARKER_SAVE"),
            branch(eq(val(HECATE), const(45)), then="PASS_HR_MARKER_SAVE"),
            branch(eq(val(HECATE), const(95)), then="PASS_HR_MARKER_SAVE"),
            goto("PASS_LISTS_GATE_UNORDERED"),
            companion=PUCK,
        ),
        scene(
            "PASS_HR_SAVE",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_HR_PAIR_RETURN"),
            branch(eq(val(HECATE), _SPACE), then="PASS_HR_PAIR_RETURN"),
            branch(eq(val(HECATE), const(42)), then="PASS_HR_MARKER_SAVE"),
            branch(eq(val(HECATE), const(45)), then="PASS_HR_MARKER_SAVE"),
            branch(eq(val(HECATE), const(95)), then="PASS_HR_MARKER_SAVE"),
            goto("PASS_HR_PAIR_RETURN"),
            companion=PUCK,
        ),
        scene(
            "PASS_CODE_GATE",
            let(HORATIO, add(val(HORATIO), const(1))),
            branch(eq(val(HORATIO), const(4)), then="PASS_CODE_BLANK"),
            branch(
                eq(val(HORATIO), sub(const(0), const(96))),
                then="PASS_BLOCK_FINISH",
            ),
            goto("PASS_CODE_GATE_READ"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CODE_GATE_READ",
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_CODE_CLOSE"),
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_CODE_CONTINUE"),
            branch(eq(val(HECATE), _SPACE), then="PASS_CODE_GATE"),
            goto("PASS_CODE_CLOSE"),
            companion=HECATE,
        ),
        scene(
            "PASS_CODE_CONTINUE",
            let(HORATIO, sub(const(0), const(100))),
            push(HORATIO, _NEWLINE),
            goto("PASS_CODE_GATE_READ"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HR_MARKER_SAVE",
            let(PUCK, val(HECATE)),
            goto("PASS_HR_SCAN"),
            companion=PUCK,
        ),
        scene(
            "PASS_HR_SCAN",
            let(MACBETH, const(1)),
            goto("PASS_HR_SCAN_READ"),
            companion=MACBETH,
        ),
        scene(
            "PASS_HR_SCAN_READ",
            *_read(),
            branch(eq(val(HECATE), val(PUCK)), then="PASS_HR_CONFIRM"),
            branch(eq(val(HECATE), _SPACE), then="PASS_HR_SPACE"),
            goto("PASS_HR_REPLAY"),
            companion=HECATE,
        ),
        scene(
            "PASS_HR_SPACE",
            *_read(),
            branch(eq(val(HECATE), val(PUCK)), then="PASS_HR_CONFIRM"),
            branch(eq(val(PUCK), const(95)), then="PASS_HR_REPLAY"),
            branch(eq(val(MACBETH), const(1)), then="PASS_HR_FALLBACK_LIST_HANDOFF"),
            goto("PASS_HR_REPLAY"),
            companion=HECATE,
        ),
        scene(
            "PASS_HR_CONFIRM",
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("PASS_HR_CONFIRM_READ"),
            companion=MACBETH,
        ),
        scene(
            "PASS_HR_CONFIRM_READ",
            *_read(),
            branch(eq(val(HECATE), val(PUCK)), then="PASS_HR_CONFIRM"),
            branch(eq(val(HECATE), _SPACE), then="PASS_HR_SPACE"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_HR_EMIT"),
            goto("PASS_HR_REPLAY"),
            companion=HECATE,
        ),
        scene(
            "PASS_HR_EMIT",
            let(HORATIO, const(-1)),
            branch(gt(val(MACBETH), const(2)), then="PASS_BLOCK_RETURN"),
            goto("PASS_HR_PAIR_RETURN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HR_PAIR_RETURN",
            branch(eq(val(HECATE), _SPACE), then="PASS_CODE_GATE"),
            goto("PASS_HR_REPLAY"),
            companion=HECATE,
        ),
        scene(
            "PASS_HR_REPLAY",
            branch(eq(val(PUCK), const(0)), then="PASS_HR_FALLBACK"),
            branch(eq(val(HORATIO), const(0)), then="PASS_HR_FALLBACK"),
            push(LADY_MACBETH, _SPACE),
            branch(eq(val(HORATIO), const(1)), then="PASS_HR_FALLBACK"),
            push(LADY_MACBETH, _SPACE),
            branch(eq(val(HORATIO), const(2)), then="PASS_HR_FALLBACK"),
            push(LADY_MACBETH, _SPACE),
            goto("PASS_HR_FALLBACK"),
            companion=HECATE,
        ),
        scene(
            "PASS_HR_FALLBACK",
            branch(eq(val(PUCK), const(0)), then="PASS_LISTS_BLOCK_BLANK"),
            branch(gt(val(MACBETH), const(1)), then="PASS_CODE_REPLAY"),
            branch(eq(val(PUCK), const(95)), then="PASS_CODE_REPLAY"),
            branch(eq(val(HORATIO), const(0)), then="PASS_CODE_REPLAY"),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_HR_FALLBACK_LIST_HANDOFF",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 1),
            push(MACBETH, const(1)),
            let(MACBETH, const(1)),
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            push(LADY_MACBETH, const(1)),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=MACBETH,
        ),
        scene(
            "PASS_CODE_REPLAY",
            let(HORATIO, val(MACBETH)),
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_HR_REPLAY_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HR_REPLAY_OPEN",
            branch(eq(val(HORATIO), const(1)), then="PASS_HR_REPLAY_KEEP"),
            let(HORATIO, sub(val(HORATIO), const(1))),
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_HR_REPLAY_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HR_REPLAY_KEEP",
            let(HORATIO, const(0)),
            goto("PASS_HR_REPLAY_CLOSE"),
            anchor=HORATIO,
            companion=MACBETH,
        ),
        scene(
            "PASS_HR_REPLAY_CLOSE",
            let(MACBETH, const(0)),
            goto("PASS_LISTS_RAW_GLYPH"),
            anchor=MACBETH,
            companion=HECATE,
        ),
        scene(
            "PASS_BLOCK_RETURN",
            *emit_token(LADY_MACBETH, tokens.HR),
            let(MACBETH, const(0)),
            goto("PASS_CODE_CLOSE"),
            companion=MACBETH,
        ),
        scene(
            "PASS_CODE_OPEN",
            pop(HORATIO, recall="code_chamber_mark"),
            let(HORATIO, add(val(HORATIO), const(1))),
            branch(eq(val(HORATIO), const(0)), then="PASS_CODE_GLYPH"),
            push(LADY_MACBETH, _NEWLINE),
            goto("PASS_CODE_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CODE_BLANK",
            *emit_token(LADY_MACBETH, tokens.CODE_BLOCK),
            goto("PASS_CODE_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_CODE_GLYPH",
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_CODE_CLOSE"),
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_CODE_LINE_END"),
            push(LADY_MACBETH, val(HECATE)),
            goto("PASS_CODE_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_CODE_LINE_END",
            push(LADY_MACBETH, _NEWLINE),
            let(HORATIO, sub(const(0), const(100))),
            push(HORATIO, _END),
            goto("PASS_CODE_GATE_READ"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CODE_CLOSE",
            branch(eq(val(HORATIO), const(-1)), then="PASS_LISTS_BLOCK_BLANK"),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_DONE"),
            goto("PASS_HR_GATE"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_BLOCK_BLANK",
            push(LADY_MACBETH, val(HECATE)),
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_DONE"),
            goto("PASS_LISTS_BLOCK_START"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_GATE_UNORDERED",
            branch(eq(val(HECATE), _BLOCKQUOTE_MARK), then="PASS_CONTAINERS_QUOTE"),
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_MARK_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_MARK_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_MARK_SAVE_UL"),
            goto("PASS_LISTS_GATE_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_GATE_ORDERED",
            branch(gt(val(MACBETH), const(0)), then="PASS_LISTS_ITEM_GLYPH"),
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
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_RAW_BLANK"),
            branch(
                eq(val(HORATIO), const(1)),
                then="PASS_LISTS_ITEM_SKIP_SPACES",
            ),
            goto("PASS_LISTS_RAW_GLYPH"),
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
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            push(LADY_MACBETH, const(1)),
            goto("PASS_LISTS_ITEM_SKIP_SPACES"),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_ITEM_BEGIN_LOOSE",
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            push(LADY_MACBETH, const(2)),
            goto("PASS_LISTS_ITEM_SKIP_SPACES"),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_ITEM_SKIP_SPACES",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_LIST_END"),
            branch(gt(val(HORATIO), const(0)), then="PASS_LISTS_GATE_UNORDERED"),
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
            branch(
                eq(val(HORATIO), const(2)),
                then="PASS_CONTAINERS_REPLAY",
            ),
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_END_OF_INPUT"),
            *_read(),
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_END_OF_INPUT"),
            branch(
                eq(val(HORATIO), const(1)),
                then="PASS_CONTAINERS_BOUNDARY",
            ),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_CONTAINERS_OPEN"),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_1"),
            goto("PASS_LISTS_LINE_HEAD"),
        ),
        # A blank makes the current item loose. Rewrite the payload already
        # emitted after ITEM_START while preserving the mixed-stream suffix
        # on Macbeth above a temporary floor.
        scene(
            "PASS_CONTAINERS_OPEN",
            push(MACBETH, val(LADY_MACBETH)),
            push(MACBETH, const(tokens.ITEM_START)),
            goto("PASS_CONTAINERS_DEPTH"),
        ),
        scene(
            "PASS_CONTAINERS_DEPTH",
            pop(LADY_MACBETH, recall="masons_stone"),
            branch(
                eq(val(LADY_MACBETH), const(tokens.ITEM_START)),
                then="PASS_CONTAINERS_EOF",
            ),
            push(MACBETH, val(LADY_MACBETH)),
            goto("PASS_CONTAINERS_DEPTH"),
        ),
        scene(
            "PASS_CONTAINERS_EOF",
            pop(MACBETH, recall="fallen_rampart"),
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            push(LADY_MACBETH, const(2)),
            goto("PASS_CONTAINERS_CLOSE"),
        ),
        scene(
            "PASS_CONTAINERS_CLOSE",
            pop(MACBETH, recall="fallen_rampart"),
            branch(
                eq(val(MACBETH), const(tokens.ITEM_START)),
                then="FRAME_STAGE_SIDE_OPEN",
            ),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_CONTAINERS_CLOSE"),
        ),
        scene(
            "FRAME_STAGE_SIDE_OPEN",
            pop(MACBETH, recall="fallen_rampart"),
            let(LADY_MACBETH, val(MACBETH)),
            pop(MACBETH, recall="fallen_rampart"),
            push(MACBETH, val(MACBETH)),
            goto("PASS_LISTS_BLANK"),
        ),
        scene(
            "PASS_CONTAINERS_BOUNDARY",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_CONTAINERS_BOUNDARY"),
            branch(eq(val(HECATE), _TAB), then="PASS_CONTAINERS_BOUNDARY"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_LIST_END"),
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
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            branch(
                eq(val(MACBETH), const(2)),
                then="PASS_LISTS_SIB_OUTDENT",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
            companion=MACBETH,
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
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            branch(
                eq(val(MACBETH), const(1)),
                then="PASS_LISTS_NEST_OPEN_UL",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_NEST_EMIT_OL",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            branch(
                eq(val(MACBETH), const(1)),
                then="PASS_LISTS_NEST_OPEN_OL",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
            companion=MACBETH,
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
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            branch(
                eq(val(MACBETH), const(2)),
                then="PASS_LISTS_BSIB_OUTDENT",
                else_="PASS_LISTS_ITEM_BEGIN_LOOSE",
            ),
            companion=MACBETH,
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
            branch(eq(val(HECATE), _BLOCKQUOTE_MARK), then="PASS_CONTAINERS_QUOTE"),
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
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, _PARA_START),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_CONTAINERS_QUOTE",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.BLOCKQUOTE_OPEN)),
            let(HORATIO, add(val(MACBETH), const(1))),
            goto("PASS_LISTS_ITEM_SKIP_SPACES"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CONTAINERS_REPLAY",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.BLOCKQUOTE_CLOSE)),
            let(HORATIO, const(0)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="FRAME_STAGE_SIDE_POP",
                else_="PASS_CONTAINERS_REPLAY_SCAN",
            ),
            companion=HORATIO,
        ),
        scene(
            "PASS_CONTAINERS_REPLAY_SCAN",
            *_read("blank_glyph"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_1"),
            goto("PASS_LISTS_LINE_HEAD"),
            companion=HECATE,
        ),
        scene(
            "FRAME_STAGE_SIDE_POP",
            goto("FRAME_STAGE_MAIN_OPEN"),
            companion=MACBETH,
        ),
        # --- List end and input end.
        scene(
            "PASS_LISTS_LIST_END",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL"),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_LIST_END_REPLAY",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY"),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_LIST_END_REPLAY_DOT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY_DOT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_END_OF_INPUT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL"),
            companion=MACBETH,
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
                eq(val(HORATIO), const(1)),
                then="PASS_LISTS_RAW_AFTER_NEWLINE",
            ),
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
            branch(
                eq(val(HORATIO), const(1)),
                then="PASS_CONTAINERS_REPLAY",
                else_="FRAME_STAGE_MAIN_OPEN",
            ),
            companion=HECATE,
        ),
        # --- Staging: reverse the mixed stream onto Macbeth.
        scene(
            "FRAME_STAGE_MAIN_OPEN",
            push(MACBETH, _END),
            goto("FRAME_STAGE_MAIN_POP"),
        ),
        scene(
            "FRAME_STAGE_MAIN_POP",
            pop(LADY_MACBETH, recall="masons_stone"),
            branch(eq(val(LADY_MACBETH), _END), then="PASS_PARA_OPEN"),
            push(MACBETH, val(LADY_MACBETH)),
            goto("FRAME_STAGE_MAIN_POP"),
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
                eq(val(MACBETH), const(tokens.TEXT_END)),
                then="PASS_PARA_NEXT",
            ),
            branch(eq(val(MACBETH), const(tokens.HR)), then="PASS_PARA_COPY_CLOSE"),
            branch(
                eq(val(MACBETH), const(tokens.LIST_OPEN)),
                then="PASS_PARA_COPY_OPEN",
            ),
            branch(
                eq(val(MACBETH), const(tokens.LIST_CLOSE)),
                then="PASS_PARA_COPY_CLOSE",
            ),
            branch(
                eq(val(MACBETH), const(tokens.BLOCKQUOTE_OPEN)),
                then="PASS_PARA_COPY_CLOSE",
            ),
            branch(
                eq(val(MACBETH), const(tokens.BLOCKQUOTE_CLOSE)),
                then="PASS_PARA_COPY_CLOSE",
            ),
            branch(
                eq(val(MACBETH), const(tokens.ITEM_START)),
                then="PASS_PARA_ITEM_OPEN",
            ),
            branch(
                eq(val(MACBETH), const(tokens.ITEM_CLOSE)),
                then="PASS_PARA_ITEM_CLOSE",
            ),
            branch(
                eq(val(MACBETH), const(tokens.CODE_BLOCK)),
                then="PASS_BLOCK_BOUNDARY",
            ),
            branch(eq(val(MACBETH), _PARA_START), then="PASS_PARA_ITEM_TEXT"),
            goto("PASS_PARA_OPEN_PARA"),
        ),
        scene(
            "PASS_BLOCK_BOUNDARY",
            push(LADY_MACBETH, const(tokens.CODE_BLOCK)),
            goto("PASS_BLOCK_REPLAY"),
            companion=MACBETH,
        ),
        scene(
            "PASS_BLOCK_REPLAY",
            pop(MACBETH, recall="staged_stone"),
            push(LADY_MACBETH, val(MACBETH)),
            branch(eq(val(MACBETH), const(tokens.TEXT_END)), then="PASS_PARA_NEXT"),
            goto("PASS_BLOCK_REPLAY"),
            companion=MACBETH,
        ),
        scene(
            "PASS_BLOCK_FINISH",
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_CODE_CONTINUE"),
            push(HECATE, val(HECATE)),
            let(LADY_MACBETH, add(val(LADY_MACBETH), const(1))),
            goto("PASS_CODE_OPEN"),
            companion=HECATE,
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
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_NEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_ITEM_OPEN",
            push(LADY_MACBETH, const(tokens.LIST_ITEM)),
            pop(MACBETH, recall="staged_stone"),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_ITEM_TEXT"),
        ),
        scene(
            "PASS_PARA_ITEM_TEXT",
            *emit_token(LADY_MACBETH, tokens.PARA),
            goto("PASS_PARA_TEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_ITEM_CLOSE",
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_PARA_NEXT"),
            companion=MACBETH,
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
            branch(
                eq(val(MACBETH), const(tokens.TEXT_END)),
                then="PASS_PARA_CLOSE_BLANK",
            ),
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
