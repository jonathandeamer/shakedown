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
_HASH = const(35)
_END = const(tokens.STREAM_END)
_BLOCKQUOTE_MARK = RECIPES[62]
_HTML_OPEN = const(60)
_RAW_HTML_MODE = const(-2)
_RAW_HTML_START = sub(const(tokens.ITEM_START), const(1))
_PARA_START = sub(_RAW_HTML_START, const(1))
_LOOSE_SCAN = const(-10)
_LOOSE_COMMIT_JOIN = const(-11)
_LOOSE_COMMIT_SIB = const(-12)
_LOOSE_NEST_UL = const(-13)
_LOOSE_NEST_OL = const(-14)
_LOOSE_EOF = const(-15)
_LOOSE_REPLAY_UL = const(-16)
_LOOSE_REPLAY_OL = const(-17)
_LOOSE_COMMIT_QUOTE = const(-18)
_LOOSE_COMMIT_SIB_HECATE = sub(const(0), const(19))
_LOOSE_COMMIT_SIB_HECATE_TAIL = sub(const(0), const(20))
_LOOSE_COMMIT_SIB_HECATE_CLOSE_TAIL = sub(const(0), const(21))

# Amendment A13: private floors for one-physical-line code buffering.
# Spoken as sub(0, N) so they need no negative stable_utility atoms.
_CODE_LINE_FLOOR = sub(const(0), const(40))
_CODE_LINE_REPLAY_FLOOR = sub(const(0), const(41))
_CODE_LINE_NONBLANK = const(1)

# Amendment A11: private Puck floor for ATX trailing space/hash buffer.
_HEADER_TRAIL_FLOOR = sub(const(0), const(42))
_HEADER_TRAIL_SAW_HASH = const(1)

# Amendment A9/A11/A12: Setext private floors, close discriminators, and
# underline-state rail values. None is a stream token or Act-III input.
_SETEXT_CANDIDATE_FLOOR = sub(const(0), const(30))
_SETEXT_UNDERLINE_FLOOR = sub(const(0), const(31))
_SETEXT_FINAL_FLOOR = sub(const(0), const(32))
_SETEXT_RAW_CLOSE = sub(const(0), const(33))
_SETEXT_EQUALS_CLOSE = sub(const(0), const(34))
_SETEXT_DASH_CLOSE = sub(const(0), const(35))
_SETEXT_RESTORE_FLOOR = sub(const(0), const(37))
_SETEXT_UNDERLINE_STATE_FLOOR = sub(const(0), const(38))
# A9 five-state rail on Macbeth's value during underline classification.
_SETEXT_UNDERLINE_UNSEEN = const(0)
_SETEXT_UNDERLINE_EQUALS = const(1)
_SETEXT_UNDERLINE_DASH = const(2)
_SETEXT_UNDERLINE_EQUALS_TAIL = const(3)
_SETEXT_UNDERLINE_DASH_TAIL = const(4)
_SETEXT_EQUALS_MARK = const(61)
_SETEXT_DASH_MARK = const(45)


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
            branch(eq(val(HECATE), _HTML_OPEN), then="PASS_WRAP_DOT"),
            # Always enter HEADER_GUARD. Positive Horatio is a failed CODE_GATE
            # indent count (1–3 spaces); HEADER_OPEN rejects ATX in that case
            # via REPLAY_DONE so Horatio is cleared before RAW (a leftover
            # positive count is otherwise misread as quote depth). Non-positive
            # Horatio (column 0, or private negative sentinel after code close)
            # may open ATX so '#' still wins over the Setext candidate path.
            goto("PASS_HEADER_GUARD"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HEADER_GUARD",
            branch(eq(val(HECATE), _HASH), then="PASS_HEADER_OPEN"),
            let(HORATIO, const(0)),
            goto("PASS_HR_GATE_MARKER"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HEADER_OPEN",
            # Failed CODE_GATE indent: do not count this '#' as ATX. Clear the
            # indent via the existing REPLAY_DONE arm and resume raw with the
            # held glyph still in Hecate.
            branch(gt(val(HORATIO), const(0)), then="PASS_HEADER_REPLAY_DONE"),
            let(HORATIO, const(1)),
            goto("PASS_HEADER_SCAN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HEADER_SCAN",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_HEADER_TEXT_OPEN"),
            branch(eq(val(HECATE), _TAB), then="PASS_HEADER_TEXT_OPEN"),
            branch(eq(val(HECATE), _HASH), then="PASS_HEADER_MORE"),
            goto("PASS_HEADER_REPLAY_HASHES"),
            companion=HECATE,
        ),
        scene(
            "PASS_HEADER_MORE",
            branch(lt(val(HORATIO), const(6)), then="PASS_HEADER_COUNT"),
            goto("PASS_HEADER_REPLAY_HASHES"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HEADER_COUNT",
            let(HORATIO, add(val(HORATIO), const(1))),
            goto("PASS_HEADER_SCAN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HEADER_TEXT_OPEN",
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_HEADER_REPLAY_SPACE"),
            push(LADY_MACBETH, const(tokens.HEADER)),
            push(LADY_MACBETH, val(HORATIO)),
            push(LADY_MACBETH, val(HECATE)),
            goto("PASS_HEADER_TEXT"),
            companion=HECATE,
        ),
        scene(
            "PASS_HEADER_TEXT",
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_HEADER_CLOSE"),
            # A11: first space opens the trailing space/hash deferral machine.
            branch(eq(val(HECATE), _SPACE), then="PASS_HEADER_TRAIL_OPEN"),
            push(LADY_MACBETH, val(HECATE)),
            goto("PASS_HEADER_TEXT"),
            companion=HECATE,
        ),
        # --- Amendment A11 ATX trailing-hash machine.
        # Puck holds the deferred spaces/hashes run above a private floor and
        # the private saw_hash bit in its value. Lady Macbeth/Hecate remain
        # the sole _read() pair. Drop only at newline after at least one hash;
        # otherwise replay deferred bytes before the held glyph or close.
        scene(
            "PASS_HEADER_TRAIL_OPEN",
            push(PUCK, _HEADER_TRAIL_FLOOR),
            push(PUCK, val(HECATE)),
            let(PUCK, const(0)),
            goto("PASS_HEADER_TRAIL_SCAN"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_HEADER_TRAIL_SCAN",
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_HEADER_TRAIL_DECIDE"),
            branch(eq(val(HECATE), _SPACE), then="PASS_HEADER_TRAIL_CAPTURE"),
            branch(eq(val(HECATE), _HASH), then="PASS_HEADER_TRAIL_CAPTURE"),
            goto("PASS_HEADER_TRAIL_REPLAY"),
            companion=HECATE,
        ),
        scene(
            "PASS_HEADER_TRAIL_CAPTURE",
            push(PUCK, val(HECATE)),
            branch(eq(val(HECATE), _SPACE), then="PASS_HEADER_TRAIL_SCAN"),
            let(PUCK, _HEADER_TRAIL_SAW_HASH),
            goto("PASS_HEADER_TRAIL_SCAN"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_HEADER_TRAIL_DECIDE",
            # At newline the deferred run is exactly Markdown.pl's trailing
            # `[ \t]*\#*` suffix: drop pure spaces and space+hash closers.
            # (A11's saw_hash bit still records hash sightings in CAPTURE;
            # REPLAY remains the mid-line non-space/non-hash escape.)
            goto("PASS_HEADER_TRAIL_DROP"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_HEADER_TRAIL_DROP",
            # Discard deferred glyphs. On the private floor, re-seed it and
            # hand off to REPLAY (same Hecate/Puck pair) which clears the
            # floor and enters EXIT→CLOSE — avoiding a cross-pair branch
            # into PASS_HEADER_CLOSE (Lady Macbeth/Hecate).
            pop(PUCK, recall="trail_glyph"),
            push(PUCK, val(PUCK)),
            branch(
                eq(val(PUCK), _HEADER_TRAIL_FLOOR),
                then="PASS_HEADER_TRAIL_REPLAY",
            ),
            pop(PUCK, recall="trail_glyph"),
            goto("PASS_HEADER_TRAIL_DROP"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_HEADER_TRAIL_REPLAY",
            pop(PUCK, recall="trail_glyph"),
            branch(
                eq(val(PUCK), _HEADER_TRAIL_FLOOR),
                then="PASS_HEADER_TRAIL_EXIT",
            ),
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_HEADER_TRAIL_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "PASS_HEADER_TRAIL_EXIT",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_HEADER_CLOSE"),
            push(LADY_MACBETH, val(HECATE)),
            goto("PASS_HEADER_TEXT"),
            companion=HECATE,
        ),
        scene(
            "PASS_HEADER_CLOSE",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_DONE"),
            goto("PASS_LISTS_BLOCK_START"),
            companion=HECATE,
        ),
        # --- Amendment A9+A11+A12 Setext underline rail and transfer chain.
        scene(
            "PASS_SETEXT_CANDIDATE",
            push(LADY_MACBETH, _SETEXT_CANDIDATE_FLOOR),
            push(LADY_MACBETH, val(HECATE)),
            goto("PASS_SETEXT_CANDIDATE_SCAN"),
            companion=HECATE,
        ),
        scene(
            "PASS_SETEXT_CANDIDATE_SCAN",
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_SETEXT_EOF_MODE",
            ),
            *_read(),
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_SETEXT_UNDERLINE_STATE_OPEN",
            ),
            goto("PASS_SETEXT_CANDIDATE_SCAN"),
            companion=HECATE,
        ),
        scene(
            "PASS_SETEXT_EOF_MODE",
            let(HORATIO, const(0)),
            let(HECATE, const(0)),
            goto("PASS_SETEXT_FINALIZE"),
            anchor=HECATE,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_STATE_OPEN",
            push(MACBETH, _SETEXT_UNDERLINE_STATE_FLOOR),
            push(MACBETH, val(MACBETH)),
            let(MACBETH, _SETEXT_UNDERLINE_UNSEEN),
            goto("PASS_SETEXT_UNDERLINE"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE",
            push(HORATIO, _SETEXT_UNDERLINE_FLOOR),
            goto("PASS_SETEXT_UNDERLINE_SCAN"),
            anchor=HECATE,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_SCAN",
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_SETEXT_UNDERLINE_EOF_STATE",
            ),
            *_read(),
            goto("PASS_SETEXT_UNDERLINE_CAPTURE"),
            companion=HECATE,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_CAPTURE",
            push(HORATIO, val(HECATE)),
            goto("PASS_SETEXT_UNDERLINE_CLASSIFY"),
            anchor=HECATE,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_CLASSIFY",
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_SETEXT_UNDERLINE_PROOF_STAGE",
            ),
            branch(
                eq(val(HECATE), _SPACE),
                then="PASS_SETEXT_UNDERLINE_CLASSIFY_SPACE",
            ),
            branch(
                eq(val(HECATE), _TAB),
                then="PASS_SETEXT_UNDERLINE_CLASSIFY_SPACE",
            ),
            branch(
                eq(val(HECATE), _SETEXT_EQUALS_MARK),
                then="PASS_SETEXT_UNDERLINE_CLASSIFY_EQ",
            ),
            branch(
                eq(val(HECATE), _SETEXT_DASH_MARK),
                then="PASS_SETEXT_UNDERLINE_CLASSIFY_DASH",
            ),
            goto("PASS_SETEXT_UNDERLINE_REQUEUE_STAGE"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_CLASSIFY_SPACE",
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_EQUALS),
                then="PASS_SETEXT_UNDERLINE_SET_EQUALS_TAIL",
            ),
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_EQUALS_TAIL),
                then="PASS_SETEXT_UNDERLINE_SCAN",
            ),
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_DASH),
                then="PASS_SETEXT_UNDERLINE_SET_DASH_TAIL",
            ),
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_DASH_TAIL),
                then="PASS_SETEXT_UNDERLINE_SCAN",
            ),
            goto("PASS_SETEXT_UNDERLINE_REQUEUE_STAGE"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_SET_EQUALS_TAIL",
            let(MACBETH, _SETEXT_UNDERLINE_EQUALS_TAIL),
            goto("PASS_SETEXT_UNDERLINE_SCAN"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_SET_DASH_TAIL",
            let(MACBETH, _SETEXT_UNDERLINE_DASH_TAIL),
            goto("PASS_SETEXT_UNDERLINE_SCAN"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_CLASSIFY_EQ",
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_UNSEEN),
                then="PASS_SETEXT_UNDERLINE_SET_EQUALS",
            ),
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_EQUALS),
                then="PASS_SETEXT_UNDERLINE_SCAN",
            ),
            goto("PASS_SETEXT_UNDERLINE_REQUEUE_STAGE"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_SET_EQUALS",
            let(MACBETH, _SETEXT_UNDERLINE_EQUALS),
            goto("PASS_SETEXT_UNDERLINE_SCAN"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_CLASSIFY_DASH",
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_UNSEEN),
                then="PASS_SETEXT_UNDERLINE_SET_DASH",
            ),
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_DASH),
                then="PASS_SETEXT_UNDERLINE_SCAN",
            ),
            goto("PASS_SETEXT_UNDERLINE_REQUEUE_STAGE"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_SET_DASH",
            let(MACBETH, _SETEXT_UNDERLINE_DASH),
            goto("PASS_SETEXT_UNDERLINE_SCAN"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_PROOF_STAGE",
            branch(
                eq(val(MACBETH), _SETEXT_UNDERLINE_UNSEEN),
                then="PASS_SETEXT_UNDERLINE_REQUEUE_STAGE",
            ),
            push(HORATIO, val(MACBETH)),
            pop(MACBETH, recall="underline_warrant"),
            push(HORATIO, val(MACBETH)),
            pop(MACBETH, recall="underline_warrant"),
            pop(HORATIO, recall="underline_warrant"),
            let(MACBETH, val(HORATIO)),
            pop(HORATIO, recall="underline_warrant"),
            branch(
                eq(val(HORATIO), _SETEXT_UNDERLINE_EQUALS),
                then="PASS_SETEXT_EQUALS",
            ),
            branch(
                eq(val(HORATIO), _SETEXT_UNDERLINE_EQUALS_TAIL),
                then="PASS_SETEXT_EQUALS",
            ),
            branch(
                eq(val(HORATIO), _SETEXT_UNDERLINE_DASH),
                then="PASS_SETEXT_DASH",
            ),
            branch(
                eq(val(HORATIO), _SETEXT_UNDERLINE_DASH_TAIL),
                then="PASS_SETEXT_DASH",
            ),
            goto("PASS_SETEXT_UNDERLINE_REQUEUE_STAGE"),
            anchor=MACBETH,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_REQUEUE_STAGE",
            pop(MACBETH, recall="underline_warrant"),
            push(HECATE, val(MACBETH)),
            pop(MACBETH, recall="underline_warrant"),
            pop(HECATE, recall="underline_warrant"),
            let(MACBETH, val(HECATE)),
            let(HECATE, const(0)),
            goto("PASS_SETEXT_REQUEUE"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_UNDERLINE_EOF_STATE",
            pop(MACBETH, recall="underline_warrant"),
            push(HECATE, val(MACBETH)),
            pop(MACBETH, recall="underline_warrant"),
            pop(HECATE, recall="underline_warrant"),
            let(MACBETH, val(HECATE)),
            let(HECATE, const(0)),
            goto("PASS_SETEXT_REQUEUE"),
            anchor=HECATE,
            companion=MACBETH,
        ),
        scene(
            "PASS_SETEXT_EQUALS",
            pop(HORATIO, recall="underline_byte"),
            branch(
                eq(val(HORATIO), _SETEXT_UNDERLINE_FLOOR),
                then="PASS_SETEXT_EQUALS_POST_DISCARD",
            ),
            goto("PASS_SETEXT_EQUALS"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_EQUALS_POST_DISCARD",
            # Proved path: mode 1 and clear Hecate's value so FINALIZE's
            # requeue-count add is a no-op. Countdown pad-drop lives in the
            # close restore (Lady Macbeth + Horatio) under A12.
            let(HORATIO, const(1)),
            let(HECATE, const(0)),
            goto("PASS_SETEXT_FINALIZE"),
            anchor=HECATE,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_DASH",
            pop(HORATIO, recall="underline_byte"),
            branch(
                eq(val(HORATIO), _SETEXT_UNDERLINE_FLOOR),
                then="PASS_SETEXT_DASH_POST_DISCARD",
            ),
            goto("PASS_SETEXT_DASH"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_DASH_POST_DISCARD",
            let(HORATIO, const(2)),
            let(HECATE, const(0)),
            goto("PASS_SETEXT_FINALIZE"),
            anchor=HECATE,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_REQUEUE",
            pop(HORATIO, recall="underline_byte"),
            branch(
                eq(val(HORATIO), _SETEXT_UNDERLINE_FLOOR),
                then="PASS_SETEXT_REQUEUE_POST_RESTORE",
            ),
            push(HECATE, val(HORATIO)),
            let(HECATE, add(val(HECATE), const(1))),
            goto("PASS_SETEXT_REQUEUE"),
            anchor=HECATE,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_REQUEUE_POST_RESTORE",
            let(HORATIO, const(0)),
            goto("PASS_SETEXT_FINALIZE"),
            anchor=HECATE,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_FINALIZE",
            let(LADY_MACBETH, add(val(LADY_MACBETH), val(HECATE))),
            push(HECATE, val(LADY_MACBETH)),
            push(HECATE, _SETEXT_FINAL_FLOOR),
            goto("PASS_SETEXT_FINALIZE_TRANSFER"),
            companion=HECATE,
        ),
        scene(
            "PASS_SETEXT_FINALIZE_TRANSFER",
            pop(LADY_MACBETH, recall="candidate_glyph"),
            branch(
                eq(val(LADY_MACBETH), _SETEXT_CANDIDATE_FLOOR),
                then="PASS_SETEXT_REPLAY",
            ),
            branch(
                eq(val(HORATIO), const(0)),
                then="PASS_SETEXT_FINALIZE_TRANSFER_DONE",
            ),
            branch(
                eq(val(LADY_MACBETH), _NEWLINE),
                then="PASS_SETEXT_FINALIZE_TRANSFER",
            ),
            push(HECATE, val(LADY_MACBETH)),
            goto("PASS_SETEXT_FINALIZE_TRANSFER"),
            companion=HECATE,
        ),
        scene(
            "PASS_SETEXT_FINALIZE_TRANSFER_DONE",
            push(HECATE, val(LADY_MACBETH)),
            goto("PASS_SETEXT_FINALIZE_TRANSFER"),
            companion=HECATE,
        ),
        scene(
            "PASS_SETEXT_REPLAY",
            branch(eq(val(HORATIO), const(1)), then="PASS_SETEXT_REPLAY_EQUALS"),
            branch(eq(val(HORATIO), const(2)), then="PASS_SETEXT_REPLAY_DASH"),
            push(PUCK, _SETEXT_RAW_CLOSE),
            goto("PASS_SETEXT_REPLAY_TRANSFER"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_SETEXT_REPLAY_EQUALS",
            push(PUCK, _SETEXT_EQUALS_CLOSE),
            goto("PASS_SETEXT_REPLAY_TRANSFER"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_SETEXT_REPLAY_DASH",
            push(PUCK, _SETEXT_DASH_CLOSE),
            goto("PASS_SETEXT_REPLAY_TRANSFER"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_SETEXT_REPLAY_TRANSFER",
            pop(HECATE, recall="title_glyph"),
            branch(
                eq(val(HECATE), _SETEXT_FINAL_FLOOR),
                then="PASS_SETEXT_REPLAY_TRANSFER_DONE",
            ),
            push(PUCK, val(HECATE)),
            goto("PASS_SETEXT_REPLAY_TRANSFER"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_SETEXT_REPLAY_TRANSFER_DONE",
            pop(HECATE, recall="saved_countdown"),
            let(PUCK, val(HECATE)),
            goto("PASS_SETEXT_BRIDGE"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_SETEXT_BRIDGE",
            push(HORATIO, val(PUCK)),
            push(HORATIO, _SETEXT_RESTORE_FLOOR),
            goto("PASS_SETEXT_BRIDGE_TRANSFER"),
            anchor=PUCK,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_BRIDGE_TRANSFER",
            pop(PUCK, recall="replay_glyph"),
            branch(
                eq(val(PUCK), _SETEXT_RAW_CLOSE),
                then="PASS_SETEXT_CLOSE",
            ),
            branch(
                eq(val(PUCK), _SETEXT_EQUALS_CLOSE),
                then="PASS_SETEXT_EQUALS_CLOSE",
            ),
            branch(
                eq(val(PUCK), _SETEXT_DASH_CLOSE),
                then="PASS_SETEXT_DASH_CLOSE",
            ),
            push(HORATIO, val(PUCK)),
            goto("PASS_SETEXT_BRIDGE_TRANSFER"),
            anchor=PUCK,
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_EQUALS_CLOSE",
            push(LADY_MACBETH, const(tokens.HEADER)),
            push(LADY_MACBETH, const(1)),
            goto("PASS_SETEXT_EQUALS_CLOSE_RESTORE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_EQUALS_CLOSE_RESTORE",
            pop(HORATIO, recall="restored_glyph"),
            branch(
                eq(val(HORATIO), _SETEXT_RESTORE_FLOOR),
                then="PASS_SETEXT_EQUALS_CLOSE_POST_RESTORE",
            ),
            push(LADY_MACBETH, val(HORATIO)),
            goto("PASS_SETEXT_EQUALS_CLOSE_RESTORE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_EQUALS_CLOSE_POST_RESTORE",
            pop(HORATIO, recall="saved_countdown"),
            let(LADY_MACBETH, val(HORATIO)),
            # A7/A9: reset Horatio to neutral block state 0 before proved close.
            # Leaving mode 1 would send PASS_LISTS_DONE into PASS_CONTAINERS_REPLAY.
            let(HORATIO, const(0)),
            # Act I ends with exactly two newlines. The proved underline already
            # consumed the first; when only the second remains, drop it so
            # A12's terminal PROVED_CLOSE reaches DONE without a dispatcher read.
            branch(
                gt(val(LADY_MACBETH), const(1)),
                then="PASS_SETEXT_PROVED_CLOSE",
            ),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_SETEXT_PROVED_CLOSE",
            ),
            let(LADY_MACBETH, const(0)),
            goto("PASS_SETEXT_PROVED_CLOSE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_DASH_CLOSE",
            push(LADY_MACBETH, const(tokens.HEADER)),
            push(LADY_MACBETH, const(2)),
            goto("PASS_SETEXT_DASH_CLOSE_RESTORE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_DASH_CLOSE_RESTORE",
            pop(HORATIO, recall="restored_glyph"),
            branch(
                eq(val(HORATIO), _SETEXT_RESTORE_FLOOR),
                then="PASS_SETEXT_DASH_CLOSE_POST_RESTORE",
            ),
            push(LADY_MACBETH, val(HORATIO)),
            goto("PASS_SETEXT_DASH_CLOSE_RESTORE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_DASH_CLOSE_POST_RESTORE",
            pop(HORATIO, recall="saved_countdown"),
            let(LADY_MACBETH, val(HORATIO)),
            let(HORATIO, const(0)),
            branch(
                gt(val(LADY_MACBETH), const(1)),
                then="PASS_SETEXT_PROVED_CLOSE",
            ),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_SETEXT_PROVED_CLOSE",
            ),
            let(LADY_MACBETH, const(0)),
            goto("PASS_SETEXT_PROVED_CLOSE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_CLOSE",
            pop(HORATIO, recall="restored_glyph"),
            branch(
                eq(val(HORATIO), _SETEXT_RESTORE_FLOOR),
                then="PASS_SETEXT_CLOSE_COUNTDOWN",
            ),
            push(LADY_MACBETH, val(HORATIO)),
            goto("PASS_SETEXT_CLOSE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_SETEXT_CLOSE_COUNTDOWN",
            pop(HORATIO, recall="saved_countdown"),
            push(HECATE, val(HORATIO)),
            let(HORATIO, const(0)),
            goto("PASS_SETEXT_CLOSE_POST_RESTORE"),
            anchor=HORATIO,
            companion=HECATE,
        ),
        scene(
            "PASS_SETEXT_CLOSE_POST_RESTORE",
            pop(HECATE, recall="saved_countdown"),
            let(LADY_MACBETH, val(HECATE)),
            # Raw failed-setext close: first-line glyphs are already on Lady
            # Macbeth without TEXT_END. Requeued look-ahead (invalid underline
            # or blank NL) sits on Hecate's input. Resume paragraph collection
            # so hard-wrapped list-like lines stay in the same PARA; a blank
            # look-ahead ends the paragraph via HEADER_CLOSE's TEXT_END
            # (same LM+Hecate pair — PROVED_CLOSE is reserved for proved
            # equals/dash close from the Horatio pair).
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_HEADER_CLOSE",
            ),
            *_read(),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_HEADER_CLOSE",
            ),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_SETEXT_PROVED_CLOSE",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_DONE"),
            goto("PASS_LISTS_BLOCK_START"),
            companion=HECATE,
        ),
        scene(
            "PASS_HEADER_REPLAY_HASHES",
            push(LADY_MACBETH, _HASH),
            branch(eq(val(HORATIO), const(1)), then="PASS_HEADER_REPLAY_DONE"),
            let(HORATIO, sub(val(HORATIO), const(1))),
            goto("PASS_HEADER_REPLAY_HASHES"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HEADER_REPLAY_DONE",
            let(HORATIO, const(0)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HEADER_REPLAY_SPACE",
            push(LADY_MACBETH, _HASH),
            branch(eq(val(HORATIO), const(1)), then="PASS_HEADER_REPLAY_SPACE_DONE"),
            let(HORATIO, sub(val(HORATIO), const(1))),
            goto("PASS_HEADER_REPLAY_SPACE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_HEADER_REPLAY_SPACE_DONE",
            push(LADY_MACBETH, _SPACE),
            let(HORATIO, const(0)),
            goto("PASS_LISTS_RAW_AFTER_NEWLINE"),
            companion=HORATIO,
        ),
        # --- Bounded raw-HTML recognition at a top-level block boundary.
        # Comments and hr tags are special-cased by their first name glyph;
        # div blocks require the exact un-attributed opening tag. Once open,
        # the leaf runs to the next blank boundary and sheds its final line
        # ending before TEXT_END.
        scene(
            "PASS_WRAP_DOT",
            *_read(),
            branch(eq(val(HECATE), const(33)), then="PASS_QUOTE_GUARD"),
            branch(eq(val(HECATE), const(104)), then="PASS_QUOTE_GUARD"),
            branch(eq(val(HECATE), const(117)), then="PASS_QUOTE_GUARD"),
            branch(eq(val(HECATE), const(100)), then="PASS_WRAP_REPLAY"),
            push(LADY_MACBETH, _HTML_OPEN),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_WRAP_REPLAY",
            *_read(),
            branch(eq(val(HECATE), const(105)), then="PASS_WRAP_GUARD"),
            push(LADY_MACBETH, _HTML_OPEN),
            push(LADY_MACBETH, const(100)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_WRAP_GUARD",
            *_read(),
            branch(eq(val(HECATE), const(118)), then="PASS_QUOTE_REPLAY"),
            push(LADY_MACBETH, _HTML_OPEN),
            push(LADY_MACBETH, const(100)),
            push(LADY_MACBETH, const(105)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_REPLAY",
            *_read(),
            branch(eq(val(HECATE), const(62)), then="PASS_QUOTE_FINISH"),
            branch(eq(val(HECATE), _SPACE), then="PASS_HTML_BLOCK_ATTR"),
            push(LADY_MACBETH, _HTML_OPEN),
            push(LADY_MACBETH, const(100)),
            push(LADY_MACBETH, const(105)),
            push(LADY_MACBETH, const(118)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_GUARD",
            push(LADY_MACBETH, _RAW_HTML_START),
            push(LADY_MACBETH, _HTML_OPEN),
            push(LADY_MACBETH, val(HECATE)),
            let(HORATIO, _RAW_HTML_MODE),
            goto("PASS_LISTS_RAW_NEXT"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_FINISH",
            push(LADY_MACBETH, _RAW_HTML_START),
            push(LADY_MACBETH, _HTML_OPEN),
            push(LADY_MACBETH, const(100)),
            push(LADY_MACBETH, const(105)),
            push(LADY_MACBETH, const(118)),
            push(LADY_MACBETH, const(62)),
            let(HORATIO, _RAW_HTML_MODE),
            goto("PASS_LISTS_RAW_NEXT"),
            companion=HORATIO,
        ),
        # An attributed opening tag keeps its whole raw run: the separating
        # space and every attribute glyph flow into the leaf untouched.
        scene(
            "PASS_HTML_BLOCK_ATTR",
            push(LADY_MACBETH, _RAW_HTML_START),
            push(LADY_MACBETH, _HTML_OPEN),
            push(LADY_MACBETH, const(100)),
            push(LADY_MACBETH, const(105)),
            push(LADY_MACBETH, const(118)),
            push(LADY_MACBETH, val(HECATE)),
            let(HORATIO, _RAW_HTML_MODE),
            goto("PASS_LISTS_RAW_NEXT"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_CLOSE",
            let(HORATIO, val(LADY_MACBETH)),
            pop(LADY_MACBETH, recall="held_label_glyph"),
            let(LADY_MACBETH, val(HORATIO)),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            let(HORATIO, const(-1)),
            goto("PASS_CODE_CLOSE"),
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
            branch(eq(val(HORATIO), const(0)), then="PASS_CODE_REPLAY"),
            branch(eq(val(PUCK), const(42)), then="PASS_HR_FALLBACK_LIST_HANDOFF"),
            branch(eq(val(PUCK), const(45)), then="PASS_HR_FALLBACK_LIST_HANDOFF"),
            branch(eq(val(PUCK), const(95)), then="PASS_CODE_REPLAY"),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_HR_FALLBACK_LIST_HANDOFF",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 1),
            push(MACBETH, const(1)),
            let(MACBETH, const(1)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
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
            companion=HORATIO,
        ),
        scene(
            "PASS_HR_REPLAY_CLOSE",
            let(MACBETH, const(0)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=MACBETH,
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
            branch(
                eq(val(HORATIO), const(0)),
                then="PASS_CODE_LINE_CAPTURE_OPEN",
            ),
            push(LADY_MACBETH, _NEWLINE),
            goto("PASS_CODE_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CODE_BLANK",
            *emit_token(LADY_MACBETH, tokens.CODE_BLOCK),
            goto("PASS_CODE_LINE_CAPTURE_OPEN"),
            companion=HECATE,
        ),
        # --- Amendment A13: one-physical-line blank-payload normalization.
        # PASS_CODE_GLYPH (Lady Macbeth + Hecate) is the sole _read() owner —
        # the two-participant validator forbids combining _read() with a Puck
        # push in one scene (same split as A8/A11 SCAN vs CAPTURE). Puck
        # buffers the post-indent line; Horatio reverse-replays nonblank
        # payload in source order. CAPTURE_SCAN is the Hecate+Puck capture
        # half only (design pair ledger).
        scene(
            "PASS_CODE_LINE_CAPTURE_OPEN",
            push(PUCK, _CODE_LINE_FLOOR),
            let(PUCK, const(0)),
            goto("PASS_CODE_GLYPH"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_CODE_GLYPH",
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_CODE_LINE_BLANK_DROP",
            ),
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_CODE_LINE_BLANK_DROP"),
            goto("PASS_CODE_LINE_CAPTURE_SCAN"),
            companion=HECATE,
        ),
        scene(
            "PASS_CODE_LINE_CAPTURE_SCAN",
            push(PUCK, val(HECATE)),
            branch(eq(val(HECATE), _SPACE), then="PASS_CODE_GLYPH"),
            branch(eq(val(HECATE), _TAB), then="PASS_CODE_GLYPH"),
            let(PUCK, _CODE_LINE_NONBLANK),
            goto("PASS_CODE_GLYPH"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_CODE_LINE_BLANK_DROP",
            branch(
                eq(val(PUCK), _CODE_LINE_NONBLANK),
                then="PASS_CODE_LINE_KEEP_REVERSE_OPEN",
            ),
            pop(PUCK, recall="kept_tally"),
            branch(
                eq(val(PUCK), _CODE_LINE_FLOOR),
                then="PASS_CODE_LINE_KEEP_REVERSE_OPEN",
            ),
            goto("PASS_CODE_LINE_BLANK_DROP"),
            anchor=HECATE,
            companion=PUCK,
        ),
        scene(
            "PASS_CODE_LINE_KEEP_REVERSE_OPEN",
            # Blank path arrives with Puck value still holding the floor
            # sentinel and an empty stack; nonblank has glyphs above floor.
            push(HORATIO, _CODE_LINE_REPLAY_FLOOR),
            goto("PASS_CODE_LINE_KEEP_REVERSE_TRANSFER"),
            anchor=PUCK,
            companion=HORATIO,
        ),
        scene(
            "PASS_CODE_LINE_KEEP_REVERSE_TRANSFER",
            branch(
                eq(val(PUCK), _CODE_LINE_FLOOR),
                then="PASS_CODE_LINE_KEEP_REPLAY",
            ),
            pop(PUCK, recall="replay_glyph"),
            branch(
                eq(val(PUCK), _CODE_LINE_FLOOR),
                then="PASS_CODE_LINE_KEEP_REPLAY",
            ),
            push(HORATIO, val(PUCK)),
            goto("PASS_CODE_LINE_KEEP_REVERSE_TRANSFER"),
            anchor=PUCK,
            companion=HORATIO,
        ),
        scene(
            "PASS_CODE_LINE_KEEP_REPLAY",
            pop(HORATIO, recall="kept_measure"),
            branch(
                eq(val(HORATIO), _CODE_LINE_REPLAY_FLOOR),
                then="PASS_CODE_LINE_CLOSE",
            ),
            push(LADY_MACBETH, val(HORATIO)),
            goto("PASS_CODE_LINE_KEEP_REPLAY"),
            anchor=HORATIO,
            companion=LADY_MACBETH,
        ),
        scene(
            "PASS_CODE_LINE_CLOSE",
            # Replay floor already discarded by KEEP_REPLAY; emit newline or close.
            branch(eq(val(HECATE), _NEWLINE), then="PASS_CODE_LINE_END"),
            goto("PASS_CODE_CLOSE"),
            anchor=HORATIO,
            companion=LADY_MACBETH,
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
            branch(gt(val(HORATIO), const(0)), then="PASS_LISTS_RAW_GLYPH"),
            branch(lt(val(HECATE), const(48)), then="PASS_SETEXT_CANDIDATE"),
            branch(gt(val(HECATE), const(57)), then="PASS_SETEXT_CANDIDATE"),
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
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_QUOTE_EOF_GATE"),
            *_read("blank_glyph"),
            branch(gt(val(HORATIO), const(0)), then="PASS_QUOTE_AFTER_NEWLINE"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_RAW_BLANK"),
            goto("PASS_LISTS_RAW_GLYPH"),
        ),
        scene(
            "PASS_QUOTE_EOF_GATE",
            branch(gt(val(HORATIO), const(0)), then="PASS_QUOTE_EOF_CLOSE"),
            goto("PASS_LISTS_DONE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_EOF_CLOSE",
            let(PUCK, const(0)),
            goto("PASS_QUOTE_NEST_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "PASS_QUOTE_AFTER_NEWLINE",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_QUOTE_BLANK"),
            let(PUCK, const(0)),
            goto("PASS_QUOTE_CONTINUE_PREFIX"),
            companion=PUCK,
        ),
        scene(
            "PASS_QUOTE_BLANK",
            let(PUCK, const(0)),
            goto("PASS_QUOTE_NEST_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "PASS_QUOTE_BLANK_DONE",
            goto("PASS_LISTS_DONE"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_LIST_BLANK",
            let(HORATIO, const(0)),
            goto("PASS_LISTS_BLANK"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_RAW_BLANK",
            branch(eq(val(HORATIO), _RAW_HTML_MODE), then="PASS_QUOTE_CLOSE"),
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
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_LIST_END"),
            branch(gt(val(HORATIO), const(0)), then="PASS_LISTS_GATE_UNORDERED"),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_ITEM_BEGIN_LOOSE",
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            push(LADY_MACBETH, const(2)),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_LIST_END"),
            branch(gt(val(HORATIO), const(0)), then="PASS_LISTS_GATE_UNORDERED"),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=HECATE,
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
            goto("PASS_LISTS_INDENT_SIBLING_GUARD"),
        ),
        scene(
            "PASS_LISTS_INDENT_SIBLING_GUARD",
            let(PUCK, const(0)),
            goto("PASS_LISTS_ITEM_LINE_CLASSIFY"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_ITEM_LINE_CLASSIFY",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_LOOSE_PROVISION"),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_1"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_INDENT_TAB_GUARD"),
            goto("PASS_LISTS_LINE_HEAD"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_LOOSE_PROVISION",
            let(HORATIO, _LOOSE_SCAN),
            goto("PASS_LISTS_BLANK"),
            companion=HORATIO,
        ),
        # Commit helper: rewrite the current item payload from tight to loose
        # while preserving the mixed-stream suffix on Macbeth above a
        # temporary floor.
        scene(
            "PASS_CONTAINERS_OPEN",
            push(PUCK, val(MACBETH)),
            goto("PASS_CONTAINERS_SAVE_COUNT"),
            companion=PUCK,
        ),
        scene(
            "PASS_CONTAINERS_SAVE_COUNT",
            push(PUCK, val(LADY_MACBETH)),
            goto("PASS_CONTAINERS_SAVE_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "PASS_CONTAINERS_SAVE_GLYPH",
            push(PUCK, val(HECATE)),
            goto("PASS_CONTAINERS_SAVE_SENTINEL"),
            companion=PUCK,
        ),
        scene(
            "PASS_CONTAINERS_SAVE_SENTINEL",
            push(MACBETH, const(tokens.ITEM_START)),
            goto("PASS_CONTAINERS_DEPTH"),
            companion=MACBETH,
        ),
        scene(
            "PASS_CONTAINERS_DEPTH",
            pop(LADY_MACBETH, recall="masons_stone"),
            branch(
                eq(val(HORATIO), _LOOSE_COMMIT_SIB_HECATE_TAIL),
                then="PASS_CONTAINERS_DEPTH_SKIP_SUBTREE",
            ),
            branch(
                eq(val(LADY_MACBETH), const(tokens.ITEM_START)),
                then="PASS_CONTAINERS_EOF",
            ),
            push(MACBETH, val(LADY_MACBETH)),
            goto("PASS_CONTAINERS_DEPTH"),
        ),
        scene(
            "PASS_CONTAINERS_DEPTH_SKIP_TAIL",
            let(HORATIO, _LOOSE_COMMIT_SIB_HECATE_TAIL),
            goto("PASS_CONTAINERS_DEPTH_SKIP_TAIL_SAVE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CONTAINERS_DEPTH_SKIP_TAIL_SAVE",
            push(MACBETH, val(LADY_MACBETH)),
            goto("PASS_CONTAINERS_DEPTH"),
            companion=MACBETH,
        ),
        scene(
            "PASS_CONTAINERS_DEPTH_SKIP_SUBTREE",
            push(MACBETH, val(LADY_MACBETH)),
            branch(
                eq(val(LADY_MACBETH), const(tokens.LIST_OPEN)),
                then="PASS_CONTAINERS_DEPTH_SKIP_SUBTREE_CLOSE",
            ),
            goto("PASS_CONTAINERS_DEPTH"),
        ),
        scene(
            "PASS_CONTAINERS_DEPTH_SKIP_SUBTREE_CLOSE",
            let(HORATIO, _LOOSE_COMMIT_SIB_HECATE_CLOSE_TAIL),
            goto("PASS_CONTAINERS_DEPTH"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CONTAINERS_EOF",
            branch(
                eq(val(HORATIO), _LOOSE_COMMIT_SIB_HECATE),
                then="PASS_CONTAINERS_DEPTH_SKIP_TAIL",
            ),
            pop(MACBETH, recall="fallen_rampart"),
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            push(LADY_MACBETH, const(2)),
            goto("PASS_CONTAINERS_CLOSE"),
        ),
        scene(
            "PASS_CONTAINERS_CLOSE",
            pop(MACBETH, recall="fallen_rampart"),
            branch(
                eq(val(HORATIO), _LOOSE_COMMIT_SIB_HECATE_CLOSE_TAIL),
                then="PASS_CONTAINERS_CLOSE_SKIP_SUBTREE",
            ),
            branch(
                eq(val(MACBETH), const(tokens.ITEM_START)),
                then="PASS_CONTAINERS_CLOSE_ROUTE",
            ),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_CONTAINERS_CLOSE"),
        ),
        scene(
            "PASS_CONTAINERS_CLOSE_SKIP_SUBTREE",
            push(LADY_MACBETH, val(MACBETH)),
            branch(
                eq(val(MACBETH), const(tokens.LIST_CLOSE)),
                then="PASS_CONTAINERS_CLOSE_SKIP_SUBTREE_CLOSE",
            ),
            goto("PASS_CONTAINERS_CLOSE"),
            companion=MACBETH,
        ),
        scene(
            "PASS_CONTAINERS_CLOSE_SKIP_SUBTREE_CLOSE",
            let(HORATIO, _LOOSE_COMMIT_SIB),
            goto("PASS_CONTAINERS_CLOSE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CONTAINERS_CLOSE_ROUTE",
            pop(PUCK, recall="kept_measure"),
            goto("PASS_CONTAINERS_RESTORE_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "PASS_CONTAINERS_RESTORE_GLYPH",
            let(HECATE, val(PUCK)),
            goto("PASS_CONTAINERS_POP_COUNT"),
            companion=HECATE,
        ),
        scene(
            "PASS_CONTAINERS_POP_COUNT",
            pop(PUCK, recall="kept_measure"),
            goto("PASS_CONTAINERS_RESTORE_COUNT"),
            companion=PUCK,
        ),
        scene(
            "PASS_CONTAINERS_RESTORE_COUNT",
            let(LADY_MACBETH, val(PUCK)),
            goto("PASS_CONTAINERS_POP_DEPTH"),
            companion=PUCK,
        ),
        scene(
            "PASS_CONTAINERS_POP_DEPTH",
            pop(PUCK, recall="kept_measure"),
            goto("PASS_CONTAINERS_RESTORE_DEPTH"),
            companion=PUCK,
        ),
        scene(
            "PASS_CONTAINERS_RESTORE_DEPTH",
            let(MACBETH, val(PUCK)),
            goto("PASS_CONTAINERS_CLOSE_BRANCH"),
            companion=MACBETH,
        ),
        scene(
            "PASS_CONTAINERS_CLOSE_BRANCH",
            branch(
                eq(val(HORATIO), _LOOSE_COMMIT_JOIN),
                then="PASS_LISTS_LOOSE_COMMIT",
            ),
            branch(
                eq(val(HORATIO), _LOOSE_COMMIT_SIB),
                then="PASS_LISTS_LOOSE_COMMIT",
            ),
            branch(eq(val(HORATIO), _LOOSE_NEST_UL), then="PASS_LISTS_LOOSE_NESTED"),
            branch(eq(val(HORATIO), _LOOSE_NEST_OL), then="PASS_LISTS_LOOSE_NESTED"),
            branch(
                eq(val(HORATIO), _LOOSE_COMMIT_QUOTE),
                then="PASS_LISTS_LOOSE_QUOTE",
            ),
            goto("FRAME_STAGE_SIDE_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "FRAME_STAGE_SIDE_OPEN",
            pop(MACBETH, recall="fallen_rampart"),
            let(LADY_MACBETH, val(MACBETH)),
            pop(MACBETH, recall="fallen_rampart"),
            goto("FRAME_STAGE_SIDE_PEEK"),
            companion=MACBETH,
        ),
        scene(
            "FRAME_STAGE_SIDE_PEEK",
            let(PUCK, val(MACBETH)),
            goto("PASS_LISTS_INDENT_DEEP_GUARD"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_INDENT_DEEP_GUARD",
            pop(MACBETH, recall="kept_measure"),
            push(MACBETH, val(MACBETH)),
            push(MACBETH, val(PUCK)),
            branch(eq(val(MACBETH), _END), then="FRAME_STAGE_SIDE_TOP"),
            goto("FRAME_STAGE_SIDE_NESTED"),
            companion=MACBETH,
        ),
        scene(
            "FRAME_STAGE_SIDE_TOP",
            let(MACBETH, const(1)),
            goto("PASS_LISTS_BLANK"),
            companion=MACBETH,
        ),
        scene(
            "FRAME_STAGE_SIDE_NESTED",
            let(MACBETH, const(2)),
            goto("PASS_LISTS_BLANK"),
        ),
        scene(
            "PASS_CONTAINERS_BOUNDARY",
            branch(
                eq(val(HECATE), _BLOCKQUOTE_MARK),
                then="PASS_QUOTE_CONTINUE_PREFIX",
            ),
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
                gt(val(MACBETH), const(1)),
                then="PASS_LISTS_SIB_OUTDENT",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_SIB_OUTDENT",
            # Close the nested list, drop one depth frame, then always close
            # the parent item before opening the same- or outer-level sibling
            # (UL and OL). Skipping ITEM_CLOSE for *+/- left parent items open
            # and scrambled Act-IV list-kind emission (Slice-5 A17).
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            let(MACBETH, sub(val(MACBETH), const(1))),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
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
            "PASS_LISTS_INDENT_TAB",
            let(PUCK, add(val(PUCK), const(1))),
            goto("PASS_LISTS_INDENT_TAB_READ"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_INDENT_TAB_READ",
            *_read(),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_INDENT_TAB_GUARD"),
            goto("PASS_LISTS_INDENT_CLASSIFY_FOUR"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_INDENT_TAB_GUARD",
            goto("PASS_LISTS_INDENT_TAB"),
            companion=HECATE,
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
            *_read(),
            goto("PASS_LISTS_INDENT_DEPTH_GUARD"),
        ),
        scene(
            "PASS_LISTS_INDENT_DEPTH_GUARD",
            let(PUCK, add(val(PUCK), const(1))),
            goto("PASS_LISTS_INDENT_CLASSIFY_FOUR"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_INDENT_CLASSIFY_FOUR",
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_1"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(
                eq(val(HECATE), const(42)),
                then="PASS_LISTS_INDENT_FOUR_ROUTE_UL",
            ),
            branch(
                eq(val(HECATE), const(43)),
                then="PASS_LISTS_INDENT_FOUR_ROUTE_UL",
            ),
            branch(
                eq(val(HECATE), const(45)),
                then="PASS_LISTS_INDENT_FOUR_ROUTE_UL",
            ),
            goto("PASS_LISTS_INDENT_ORDERED_FOUR"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_INDENT_FOUR_ROUTE_UL",
            branch(lt(val(PUCK), val(MACBETH)), then="PASS_LISTS_NEST_SAVE_UL"),
            goto("PASS_LISTS_DEEP_SAVE_UL"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_INDENT_ORDERED_FOUR",
            branch(
                lt(val(HECATE), const(48)),
                then="PASS_LISTS_INDENT_FOUR_GUARD",
            ),
            branch(
                gt(val(HECATE), const(57)),
                then="PASS_LISTS_INDENT_FOUR_GUARD",
            ),
            branch(lt(val(PUCK), val(MACBETH)), then="PASS_LISTS_NEST_SAVE_OL"),
            goto("PASS_LISTS_DEEP_SAVE_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_INDENT_FOUR_GUARD",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_OUTDENT"),
            goto("PASS_LISTS_INDENT_FOUR_CONTINUE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_INDENT_FOUR_CONTINUE",
            push(LADY_MACBETH, _NEWLINE),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_INDENT_CLASSIFY",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_INDENT_REPLAY_GUARD"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_INDENT_REPLAY_GUARD"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_INDENT_REPLAY_GUARD"),
            goto("PASS_LISTS_INDENT_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_INDENT_REPLAY_GUARD",
            goto("PASS_LISTS_NEST_SAVE_UL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_INDENT_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_CONTINUE_GUARD"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_CONTINUE_GUARD"),
            goto("PASS_LISTS_NEST_SAVE_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_CONTINUE_GUARD",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_OUTDENT"),
            goto("PASS_LISTS_JOIN_LINE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_OUTDENT",
            branch(eq(val(MACBETH), const(1)), then="PASS_LISTS_LOOSE_OUTDENT_JOIN"),
            branch(lt(val(PUCK), val(MACBETH)), then="PASS_LISTS_LOOSE_OUTDENT_CLOSE"),
            goto("PASS_LISTS_LOOSE_OUTDENT_JOIN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_OUTDENT_CLOSE",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            let(MACBETH, sub(val(MACBETH), const(1))),
            goto("PASS_LISTS_LOOSE_OUTDENT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_LOOSE_OUTDENT_JOIN",
            branch(eq(val(MACBETH), const(0)), then="PASS_LISTS_LOOSE_COMMIT_JOIN"),
            let(HORATIO, _LOOSE_COMMIT_JOIN),
            goto("PASS_CONTAINERS_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_NEST_SAVE_UL",
            branch(gt(val(PUCK), const(1)), then="PASS_LISTS_DEEP_SAVE_UL"),
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_NEST_TEST_UL"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_DEEP_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_DEEP_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_NEST_EMIT_UL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_NEST_EMIT_UL"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_GUARD"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_DEEP_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_DEEP_EMIT_UL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_DEEP_EMIT_UL"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_GUARD"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_NEST_SAVE_OL",
            branch(gt(val(PUCK), const(1)), then="PASS_LISTS_DEEP_SAVE_OL"),
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_NEST_TEST_DOT"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_DEEP_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_DEEP_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_NEST_TEST_OL"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_GUARD"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_DEEP_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_DEEP_TEST_OL"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_GUARD"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_NEST_EMIT_OL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_NEST_EMIT_OL"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_REPLAY_GUARD"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_DEEP_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_DEEP_EMIT_OL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_DEEP_EMIT_OL"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_REPLAY_GUARD"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_NEST_EMIT_UL",
            branch(
                eq(val(HORATIO), _LOOSE_NEST_UL),
                then="PASS_LISTS_NEST_OPEN_UL",
            ),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_NEST_UL"),
            branch(
                eq(val(MACBETH), const(1)),
                then="PASS_LISTS_NEST_EMIT_UL_OPEN",
            ),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_NEST_EMIT_OL",
            branch(
                eq(val(HORATIO), _LOOSE_NEST_OL),
                then="PASS_LISTS_NEST_OPEN_OL",
            ),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_NEST_OL"),
            branch(
                eq(val(MACBETH), const(1)),
                then="PASS_LISTS_NEST_EMIT_OL_OPEN",
            ),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
            companion=HECATE,
        ),
        scene(
            # Keep the parent item open across the nested list (same as DEEP).
            # Parent ITEM_CLOSE is emitted on SIB_OUTDENT after nested LIST_CLOSE
            # so UL and OL sibling outdents share one close shape (Slice-5 A17;
            # the old soft-close here forced UL outdent to skip ITEM_CLOSE and
            # broke deep same-kind UL nests that never soft-closed).
            "PASS_LISTS_NEST_EMIT_UL_OPEN",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("PASS_LISTS_NEST_OPEN_UL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_NEST_EMIT_OL_OPEN",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("PASS_LISTS_NEST_OPEN_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_LOOSE_NEST_UL",
            let(HORATIO, _LOOSE_NEST_UL),
            goto("PASS_CONTAINERS_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_NEST_OL",
            let(HORATIO, _LOOSE_NEST_OL),
            goto("PASS_CONTAINERS_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_DEEP_EMIT_UL",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_NEST_UL"),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("PASS_LISTS_NEST_OPEN_UL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_DEEP_EMIT_OL",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_NEST_OL"),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("PASS_LISTS_NEST_OPEN_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_NEST_OPEN_UL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 1),
            push(MACBETH, const(1)),
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        scene(
            "PASS_LISTS_NEST_OPEN_OL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 2),
            push(MACBETH, const(2)),
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        # --- Blank line inside a list: continuation, sibling, or list end.
        scene(
            "PASS_LISTS_BLANK",
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_LOOSE_EOF_GUARD"),
            *_read("blank_glyph"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            goto("PASS_LISTS_BLANK_RESET_PUCK"),
        ),
        scene(
            "PASS_LISTS_BLANK_RESET_PUCK",
            let(PUCK, const(0)),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_1"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_INDENT_TAB"),
            goto("PASS_LISTS_BLANK_HEAD"),
            companion=PUCK,
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
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_BLANK_ROLLBACK_GOTO"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_BLANK_ROLLBACK_GOTO"),
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
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_GUARD"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_INDENT_GUARD"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_GUARD"),
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
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_GUARD"),
            goto("PASS_LISTS_LIST_END_REPLAY"),
        ),
        scene(
            "PASS_LISTS_BSIB_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BSIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_BSIB_EMIT"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_REPLAY_GUARD"),
            goto("PASS_LISTS_LIST_END_REPLAY_DOT"),
        ),
        scene(
            "PASS_LISTS_BSIB_EMIT",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_SIBLING"),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            branch(
                gt(val(MACBETH), const(1)),
                then="PASS_LISTS_BSIB_OUTDENT",
            ),
            goto("PASS_LISTS_ITEM_BEGIN_LOOSE"),
            companion=MACBETH,
        ),
        scene(
            "PASS_LISTS_LOOSE_SIBLING",
            let(HORATIO, _LOOSE_COMMIT_SIB_HECATE),
            branch(
                gt(val(MACBETH), const(1)),
                then="PASS_LISTS_LOOSE_COMMIT_HECATE",
            ),
            let(HORATIO, _LOOSE_COMMIT_SIB),
            goto("PASS_CONTAINERS_OPEN"),
        ),
        scene(
            "PASS_LISTS_LOOSE_COMMIT_HECATE",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            let(MACBETH, sub(val(MACBETH), const(1))),
            goto("PASS_CONTAINERS_OPEN"),
        ),
        scene(
            "PASS_LISTS_BSIB_OUTDENT",
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            let(MACBETH, sub(val(MACBETH), const(1))),
            goto("PASS_LISTS_ITEM_BEGIN_LOOSE"),
        ),
        scene(
            "PASS_LISTS_INDENT_GUARD",
            *_read(),
            branch(eq(val(HECATE), val(PUCK)), then="PASS_LISTS_NEST_GUARD"),
            goto("PASS_LISTS_BSIB_EMIT"),
        ),
        scene(
            "PASS_LISTS_NEST_GUARD",
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_FULL_GUARD"),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_NEST_GUARD"),
            branch(eq(val(HECATE), val(PUCK)), then="PASS_LISTS_NEST_GUARD"),
            goto("PASS_LISTS_LIST_END_REPLAY"),
        ),
        scene(
            "PASS_LISTS_FULL_GUARD",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            *emit_token(LADY_MACBETH, tokens.HR),
            pop(MACBETH, recall="fallen_rampart"),
            let(MACBETH, const(0)),
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_AFTER_LIST"),
            goto("PASS_LISTS_BLOCK_START"),
            companion=MACBETH,
        ),
        # Blank + indented continuation: the item is loose; the blank and the
        # outdented line join its text.
        scene(
            "PASS_LISTS_BLANK_INDENT_1",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_2"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_INDENT_CLASSIFY"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_2",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_3"),
            branch(eq(val(HECATE), _BLOCKQUOTE_MARK), then="PASS_LISTS_QUOTE_GUARD"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_INDENT_CLASSIFY"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_3",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_4"),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_INDENT_CLASSIFY"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_4",
            *_read(),
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_INDENT_CLASSIFY_FOUR"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_QUOTE_GUARD",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_QUOTE_PREP"),
            goto("PASS_CONTAINERS_QUOTE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_QUOTE_PREP",
            let(HORATIO, _LOOSE_COMMIT_QUOTE),
            goto("PASS_CONTAINERS_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_QUOTE",
            let(HORATIO, const(0)),
            goto("PASS_CONTAINERS_QUOTE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_BLANK_JOIN",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_JOIN"),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, _PARA_START),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_LOOSE_JOIN",
            let(HORATIO, _LOOSE_COMMIT_JOIN),
            goto("PASS_CONTAINERS_OPEN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_CONTAINERS_QUOTE",
            branch(eq(val(HORATIO), const(0)), then="PASS_QUOTE_NEST_GUARD"),
            goto("PASS_QUOTE_NEST_DEPTH"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_NEST_GUARD",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.BLOCKQUOTE_OPEN)),
            let(HORATIO, add(val(MACBETH), const(1))),
            goto("PASS_QUOTE_PREFIX_FINISH"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_NEST_DEPTH",
            let(PUCK, add(val(PUCK), const(1))),
            branch(
                gt(val(PUCK), val(HORATIO)),
                then="PASS_QUOTE_NEST_OPEN",
            ),
            goto("PASS_QUOTE_PREFIX"),
            companion=PUCK,
        ),
        scene(
            "PASS_QUOTE_NEST_OPEN",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.BLOCKQUOTE_OPEN)),
            let(HORATIO, add(val(HORATIO), const(1))),
            goto("PASS_QUOTE_PREFIX"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_PREFIX",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_QUOTE_FINISH_OPTIONAL"),
            branch(eq(val(HECATE), _TAB), then="PASS_QUOTE_PREFIX_OPTIONAL"),
            goto("PASS_QUOTE_CONTINUE_CLASSIFY"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_PREFIX_OPTIONAL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_RAW_GLYPH"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_RAW_GLYPH"),
            goto("PASS_QUOTE_CONTINUE_CLASSIFY"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_PREFIX_CLASSIFY",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_QUOTE_PREFIX_BLANK"),
            branch(
                gt(val(HORATIO), add(val(MACBETH), val(PUCK))),
                then="PASS_QUOTE_NEST_CLOSE",
            ),
            goto("PASS_LISTS_GATE_UNORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_PREFIX_BLANK",
            branch(gt(val(MACBETH), const(0)), then="PASS_QUOTE_PREFIX_LIST_END"),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=MACBETH,
        ),
        scene(
            "PASS_QUOTE_PREFIX_LIST_END",
            goto("PASS_LISTS_LIST_END"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_CONTINUE_PREFIX",
            let(PUCK, const(0)),
            branch(
                eq(val(HECATE), _BLOCKQUOTE_MARK),
                then="PASS_QUOTE_NEST_DEPTH",
            ),
            goto("PASS_QUOTE_NEST_REPLAY"),
            companion=PUCK,
        ),
        scene(
            "PASS_QUOTE_PREFIX_REPLAY",
            goto("PASS_LISTS_BLOCK_START"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_LIST_CLEAR",
            let(HORATIO, const(0)),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_QUOTE_LIST_BLANK"),
            goto("PASS_QUOTE_LIST_REPLAY"),
            companion=LADY_MACBETH,
        ),
        scene(
            "PASS_QUOTE_LIST_REPLAY",
            let(PUCK, const(0)),
            goto("PASS_LISTS_ITEM_LINE_CLASSIFY"),
            companion=PUCK,
        ),
        scene(
            "PASS_QUOTE_PREFIX_FINISH",
            let(PUCK, add(val(PUCK), const(1))),
            goto("PASS_QUOTE_PREFIX"),
            companion=PUCK,
        ),
        scene(
            "PASS_QUOTE_NEST_CLOSE",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(LADY_MACBETH, const(tokens.BLOCKQUOTE_CLOSE)),
            let(HORATIO, sub(val(HORATIO), const(1))),
            branch(eq(val(PUCK), const(0)), then="PASS_QUOTE_NEST_REPLAY"),
            goto("PASS_QUOTE_PREFIX_CLASSIFY"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_NEST_REPLAY",
            goto("PASS_QUOTE_NEST_FINISH"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_NEST_FINISH",
            branch(gt(val(HORATIO), val(MACBETH)), then="PASS_QUOTE_NEST_CLOSE"),
            goto("PASS_QUOTE_NEST_BLANK"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_NEST_BLANK",
            let(HORATIO, const(0)),
            branch(gt(val(MACBETH), const(0)), then="PASS_QUOTE_LIST_CLEAR"),
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_QUOTE_BLANK_DONE"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_QUOTE_PREFIX_REPLAY"),
            goto("PASS_HR_GATE"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_FINISH_OPTIONAL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_RAW_GLYPH"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_RAW_GLYPH"),
            goto("PASS_QUOTE_CONTINUE_CLASSIFY"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_CONTINUE_CLASSIFY",
            branch(
                eq(val(HECATE), _BLOCKQUOTE_MARK),
                then="PASS_QUOTE_TOP_CONTINUE_CLASSIFY",
            ),
            branch(eq(val(HORATIO), const(1)), then="PASS_QUOTE_TOP_CONTINUE_CLASSIFY"),
            goto("PASS_QUOTE_PREFIX_CLASSIFY"),
            companion=HORATIO,
        ),
        scene(
            "PASS_QUOTE_TOP_CONTINUE_CLASSIFY",
            branch(
                eq(val(HECATE), _BLOCKQUOTE_MARK),
                then="PASS_LISTS_GATE_UNORDERED",
            ),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_QUOTE_TOP_CONTINUE_BLANK"),
            branch(gt(val(MACBETH), const(0)), then="PASS_LISTS_LINE_HEAD"),
            goto("PASS_QUOTE_PREFIX_CLASSIFY"),
            companion=HECATE,
        ),
        scene(
            "PASS_QUOTE_TOP_CONTINUE_BLANK",
            goto("PASS_QUOTE_PREFIX_BLANK"),
            companion=HECATE,
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
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_INDENT_TAB_GUARD"),
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
            pop(MACBETH, recall="fallen_rampart"),
            push(MACBETH, val(MACBETH)),
            branch(eq(val(MACBETH), _END), then="PASS_LISTS_CLOSE_ALL_DONE"),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL"),
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL_DONE",
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
                else_="PASS_HR_GATE",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL_REPLAY",
            pop(MACBETH, recall="fallen_rampart"),
            branch(eq(val(MACBETH), _END), then="PASS_LISTS_CLOSE_REPLAY_DONE"),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            push(MACBETH, val(MACBETH)),
            branch(eq(val(MACBETH), _END), then="PASS_LISTS_CLOSE_REPLAY_DONE"),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY"),
        ),
        scene(
            "PASS_LISTS_CLOSE_REPLAY_DONE",
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
            pop(MACBETH, recall="fallen_rampart"),
            push(MACBETH, val(MACBETH)),
            branch(
                eq(val(MACBETH), _END),
                then="PASS_LISTS_CLOSE_REPLAY_DOT_DONE",
            ),
            push(LADY_MACBETH, const(tokens.ITEM_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY_DOT"),
        ),
        scene(
            "PASS_LISTS_CLOSE_REPLAY_DOT_DONE",
            let(MACBETH, const(0)),
            goto("PASS_LISTS_RAW_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_DONE",
            branch(eq(val(HORATIO), _RAW_HTML_MODE), then="PASS_QUOTE_CLOSE"),
            branch(
                eq(val(HORATIO), const(1)),
                then="PASS_CONTAINERS_REPLAY",
                else_="FRAME_STAGE_MAIN_OPEN",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_LOOSE_COMMIT",
            branch(
                eq(val(HORATIO), _LOOSE_COMMIT_JOIN),
                then="PASS_LISTS_LOOSE_COMMIT_JOIN",
            ),
            let(HORATIO, const(0)),
            goto("PASS_LISTS_BSIB_EMIT"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_COMMIT_JOIN",
            let(HORATIO, const(0)),
            goto("PASS_LISTS_BLANK_JOIN"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_NESTED",
            branch(eq(val(HORATIO), _LOOSE_NEST_UL), then="PASS_LISTS_LOOSE_NESTED_UL"),
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("PASS_LISTS_NEST_EMIT_OL"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_NESTED_UL",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("PASS_LISTS_NEST_EMIT_UL"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_EOF",
            goto("PASS_LISTS_LOOSE_ROLLBACK"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_ROLLBACK",
            goto("PASS_LISTS_LOOSE_REPLAY"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_REPLAY",
            branch(
                eq(val(HORATIO), _LOOSE_REPLAY_UL),
                then="PASS_LISTS_LOOSE_REPLAY_UL",
            ),
            branch(
                eq(val(HORATIO), _LOOSE_REPLAY_OL),
                then="PASS_LISTS_LOOSE_REPLAY_OL",
            ),
            let(HORATIO, const(0)),
            goto("PASS_LISTS_LIST_END"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_REPLAY_UL",
            let(HORATIO, const(0)),
            goto("PASS_LISTS_LIST_END_REPLAY"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_REPLAY_OL",
            let(HORATIO, const(0)),
            goto("PASS_LISTS_LIST_END_REPLAY_DOT"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_GUARD",
            let(HORATIO, _LOOSE_REPLAY_UL),
            goto("PASS_LISTS_LOOSE_EOF"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_EOF_GUARD",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_ROLLBACK_GUARD"),
            goto("PASS_LISTS_END_OF_INPUT"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_BLANK_ROLLBACK_GOTO",
            goto("PASS_LISTS_LOOSE_ROLLBACK_GUARD"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_LOOSE_ROLLBACK_GUARD",
            branch(lt(val(HORATIO), const(0)), then="PASS_LISTS_LOOSE_SET_EOF"),
            goto("PASS_LISTS_LIST_END"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_SET_EOF",
            let(HORATIO, _LOOSE_EOF),
            goto("PASS_LISTS_LOOSE_EOF"),
            companion=HORATIO,
        ),
        scene(
            "PASS_LISTS_LOOSE_REPLAY_GUARD",
            let(HORATIO, _LOOSE_REPLAY_OL),
            goto("PASS_LISTS_LOOSE_EOF"),
            companion=HORATIO,
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
                eq(val(MACBETH), const(tokens.HEADER)),
                then="PASS_PARA_COPY_HEADER",
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
            branch(
                eq(val(MACBETH), _RAW_HTML_START),
                then="PASS_QUOTE_CODE",
            ),
            branch(eq(val(MACBETH), _PARA_START), then="PASS_PARA_ITEM_TEXT"),
            goto("PASS_PARA_OPEN_PARA"),
        ),
        scene(
            "PASS_BLOCK_BOUNDARY",
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_BLOCK_REPLAY"),
            companion=MACBETH,
        ),
        scene(
            "PASS_QUOTE_CODE",
            push(LADY_MACBETH, const(tokens.RAW_HTML_HASH)),
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
            "PASS_PARA_COPY_HEADER",
            push(LADY_MACBETH, const(tokens.HEADER)),
            pop(MACBETH, recall="staged_stone"),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_BLOCK_REPLAY"),
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
            branch(
                eq(val(MACBETH), const(tokens.TEXT_END)),
                then="PASS_PARA_CLOSE_BLANK",
            ),
            branch(
                eq(val(MACBETH), const(tokens.BLOCKQUOTE_CLOSE)),
                then="PASS_PARA_CLOSE_BLANK",
            ),
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
