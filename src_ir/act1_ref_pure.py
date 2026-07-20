"""Pure-op Act I reference strip (Task 2L Step 2c / Amendment A4.6).

Step 2c — line machine: NEXT / LEAD / FOUR_SPACE / NL / KEEP per A3.2
self-loop mapping, still keeping every line as body (no definition strip yet).

Pipeline (two transfers only — A4.2):
  after normalize reverse: Hecate.stack top = first
  scan (line machine, keep-all): Puck.stack top = last (+ KEPT_START base)
  trailing-NL policy: FOLD/ENCODE/STORE (temporary homes until 2e owns them)
  drain: REVERSE Puck → Hecate top = first; length in Hecate.value
  FINISH: Horatio.value/stack = length

Registers (A4.1 / A4.3):
  Hecate.value = remaining source count
  Horatio.value = ov (leading-space count at line start; 0 after NL)
  Puck.stack = kept body (top = last); Puck.value = take-idiom rem scratch

A4.5 spares promoted for stage-pair bridges:
  LEAD_GUARD  — ov += 1, then LEAD (accept space)
  LABEL_GUARD — lead saw SP: ov==3 → FOUR_SPACE else LEAD_GUARD
  REPLAY_GUARD — push NL + rem-- + goto NL (line-end bridge)

REPLAY seeds KEPT_START (2d reclaims REPLAY for capture flush).
USE_ACT1_REF_INTRINSIC stays False.
"""

from __future__ import annotations

from scripts.splc.ir import (
    Scene,
    add,
    branch,
    const,
    eq,
    goto,
    let,
    pop,
    push,
    scene,
    sub,
    val,
)
from src_ir.cast import HECATE, HORATIO, PUCK

# KEPT_START = -8 (A1.2 / A4.3)
_KS = sub(const(0), const(8))
_NL = const(10)
_SP = const(32)
_0 = const(0)
_1 = const(1)
_3 = const(3)

# pop(HECATE) with companion=PUCK → speaker is Puck
_RECALL_PUCK = "kept_measure"
# pop(PUCK) with Hecate on stage → speaker is Hecate
_RECALL_HECATE = "cauldron_dreg"
# pop(HORATIO) with Hecate on stage → speaker is Hecate
_RECALL_HORATIO_LEN = "kept_tally"


def build_ref_scenes() -> list[Scene]:
    """A4.6 Step 2c line machine; strip/store semantics land in 2d–2e."""
    return [
        # Cold entry from HECATE_REVERSE_CHECK (Hecate, Horatio).
        scene(
            "HECATE_REF_OPEN",
            pop(HORATIO, recall=_RECALL_HORATIO_LEN),
            let(HECATE, val(HORATIO)),
            let(HORATIO, _0),  # ov = 0
            goto("HECATE_REF_REPLAY"),
            companion=HORATIO,
        ),
        # Seed KEPT_START (2c cold seed; 2d reclaims REPLAY for flush).
        scene(
            "HECATE_REF_REPLAY",
            push(PUCK, _KS),
            goto("HECATE_REF_NEXT"),
            companion=PUCK,
        ),
        # Line-start dispatcher (oracle mode "next").
        scene(
            "HECATE_REF_NEXT",
            # Never-true chain keeps unreached 2d labels in entry_pairs.
            branch(
                eq(val(HECATE), sub(val(HECATE), _1)),
                then="HECATE_REF_BRACKET",
            ),
            branch(eq(val(HECATE), _0), then="HECATE_REF_FOLD"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
            branch(eq(val(HECATE), _SP), then="HECATE_REF_LEAD_GUARD"),
            # '[' or other: keep as body (2d branches '[' → BRACKET).
            push(PUCK, val(HECATE)),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # Line-end bridge: NL already taken; push it, rem--, reset ov via NL.
        scene(
            "HECATE_REF_REPLAY_GUARD",
            push(PUCK, _NL),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_NL"),
            companion=PUCK,
        ),
        # ov += 1 then accept that space on Puck via LEAD.
        scene(
            "HECATE_REF_LEAD_GUARD",
            let(HORATIO, add(val(HORATIO), _1)),
            goto("HECATE_REF_LEAD"),
            companion=HORATIO,
        ),
        # Push current SP; take next lead glyph; dispatch.
        # Entry: Hecate.value is SP, Puck.value is rem, ov already updated.
        scene(
            "HECATE_REF_LEAD",
            push(PUCK, _SP),
            let(HECATE, sub(val(PUCK), _1)),
            branch(eq(val(HECATE), _0), then="HECATE_REF_FOLD"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            branch(eq(val(HECATE), _SP), then="HECATE_REF_LABEL_GUARD"),
            branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
            # Non-space (incl. '['): keep as body for 2c.
            push(PUCK, val(HECATE)),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # Lead saw another SP: fourth → FOUR_SPACE; else ov++ via LEAD_GUARD.
        scene(
            "HECATE_REF_LABEL_GUARD",
            branch(eq(val(HORATIO), _3), then="HECATE_REF_FOUR_SPACE"),
            goto("HECATE_REF_LEAD_GUARD"),
            companion=PUCK,
        ),
        # Fourth leading space ⇒ not a definition; keep rest of line as body.
        scene(
            "HECATE_REF_FOUR_SPACE",
            push(PUCK, _SP),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # Keep non-def glyphs until NL (oracle mode "keep").
        scene(
            "HECATE_REF_KEEP",
            branch(eq(val(HECATE), _0), then="HECATE_REF_FOLD"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
            push(PUCK, val(HECATE)),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # End-of-line: reset ov, resume at line start.
        scene(
            "HECATE_REF_NL",
            let(HORATIO, _0),
            goto("HECATE_REF_NEXT"),
            companion=HORATIO,
        ),
        # Trailing-NL policy on Puck (top = last). FOLD/ENCODE/STORE temporary
        # until 2e owns fold/encode/store semantics.
        scene(
            "HECATE_REF_FOLD",
            pop(PUCK, recall=_RECALL_HECATE),
            branch(eq(val(PUCK), _KS), then="HECATE_REF_STORE"),
            branch(eq(val(PUCK), _NL), then="HECATE_REF_FOLD"),
            push(PUCK, val(PUCK)),
            goto("HECATE_REF_ENCODE"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_STORE",
            push(PUCK, _KS),
            goto("HECATE_REF_ENCODE"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_ENCODE",
            push(PUCK, _NL),
            push(PUCK, _NL),
            let(HECATE, _0),
            goto("HECATE_REF_REVERSE"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_REVERSE",
            pop(PUCK, recall=_RECALL_HECATE),
            branch(eq(val(PUCK), _KS), then="HECATE_REF_FINISH"),
            push(HECATE, val(PUCK)),
            let(HECATE, add(val(HECATE), _1)),
            goto("HECATE_REF_REVERSE"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_FINISH",
            let(HORATIO, val(HECATE)),
            push(HORATIO, val(HORATIO)),
            let(HECATE, _0),
            goto("ACT_I_DONE"),
            companion=HORATIO,
        ),
        # Never-taken 2d chain (entered only via rem == rem-1 from NEXT).
        scene("HECATE_REF_BRACKET", goto("HECATE_REF_LABEL"), companion=PUCK),
        scene("HECATE_REF_LABEL", goto("HECATE_REF_COLON"), companion=PUCK),
        scene("HECATE_REF_COLON", goto("HECATE_REF_URL_WS"), companion=PUCK),
        scene("HECATE_REF_URL_WS", goto("HECATE_REF_ANGLE"), companion=PUCK),
        scene("HECATE_REF_ANGLE", goto("HECATE_REF_URL"), companion=PUCK),
        scene("HECATE_REF_URL", goto("HECATE_REF_TITLE"), companion=PUCK),
        scene("HECATE_REF_TITLE", goto("HECATE_REF_TITLE_NL"), companion=PUCK),
        scene("HECATE_REF_TITLE_NL", goto("HECATE_REF_NEXT"), companion=PUCK),
    ]
