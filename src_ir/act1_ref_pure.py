"""Pure-op Act I reference strip (Task 2L Step 2a / Amendment A4.2).

Orientation-correct keep-all body + trailing-NL policy. Definition strip is
still WIP (2c–2e).

Pipeline (two transfers only — A4.2):
  after normalize reverse: Hecate.stack top = first
  scan (keep-all):         Puck.stack  top = last  (+ KEPT_START base)
  trailing-NL policy:      Puck.stack  top = last  (strip then pad two NL)
  drain:                   Puck → Hecate top = first; length in Hecate.value
  FINISH:                  Horatio.value/stack = length

Phases use dedicated labels rather than Rosalind phase codes so Horatio stays
free for later capture (A4.3). USE_ACT1_REF_INTRINSIC stays False.

Unreached A1.3 labels form a never-taken branch chain (rem == rem-1) so every
label is a jump target for validate/lower entry_pairs; 2c–2e replace those bodies.
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
_0 = const(0)
_1 = const(1)

# pop(HECATE) with companion=PUCK → speaker is Puck
_RECALL_PUCK = "kept_measure"
# pop(PUCK) with Hecate on stage → speaker is Hecate
_RECALL_HECATE = "cauldron_dreg"
# pop(HORATIO) with Hecate on stage → speaker is Hecate
_RECALL_HORATIO_LEN = "kept_tally"


def build_ref_scenes() -> list[Scene]:
    """A4.2 keep-all orientation lattice; strip semantics land in 2c–2e."""
    return [
        # Cold entry from HECATE_REVERSE_CHECK (Hecate, Horatio).
        # Length lives on Horatio.stack (value was depleted by reverse).
        scene(
            "HECATE_REF_OPEN",
            pop(HORATIO, recall=_RECALL_HORATIO_LEN),
            let(HECATE, val(HORATIO)),
            let(HORATIO, _0),
            goto("HECATE_REF_FOUR_SPACE"),
            companion=HORATIO,
        ),
        # Seed KEPT_START on Puck, then transfer body Hecate → Puck.
        scene(
            "HECATE_REF_FOUR_SPACE",
            push(PUCK, _KS),
            goto("HECATE_REF_NEXT"),
            companion=PUCK,
        ),
        # Keep-all: rem in Hecate.value; take-idiom via Puck.value (A4.1 #2).
        # Dead branch (rem == rem-1 is never true) keeps unused A1.3 labels
        # in entry_pairs so lower() can stage them; 2c–2e replace those bodies.
        scene(
            "HECATE_REF_NEXT",
            branch(
                eq(val(HECATE), sub(val(HECATE), _1)),
                then="HECATE_REF_BRACKET",
            ),
            branch(eq(val(HECATE), _0), then="HECATE_REF_NL"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            push(PUCK, val(HECATE)),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_NEXT"),
            companion=PUCK,
        ),
        # Trailing-NL policy on Puck (top = last glyph).
        scene(
            "HECATE_REF_NL",
            pop(PUCK, recall=_RECALL_HECATE),
            branch(eq(val(PUCK), _KS), then="HECATE_REF_LEAD"),
            branch(eq(val(PUCK), _NL), then="HECATE_REF_NL"),
            # Non-NL: restore glyph, then pad exactly two newlines.
            push(PUCK, val(PUCK)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # Empty body (KS only): restore sentinel and pad two NL.
        scene(
            "HECATE_REF_LEAD",
            push(PUCK, _KS),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # Pad two NL; zero length counter; drain Puck → Hecate.
        scene(
            "HECATE_REF_KEEP",
            push(PUCK, _NL),
            push(PUCK, _NL),
            let(HECATE, _0),
            goto("HECATE_REF_REVERSE"),
            companion=PUCK,
        ),
        # Single orientation-restoring transfer; length in Hecate.value.
        scene(
            "HECATE_REF_REVERSE",
            pop(PUCK, recall=_RECALL_HECATE),
            branch(eq(val(PUCK), _KS), then="HECATE_REF_FINISH"),
            push(HECATE, val(PUCK)),
            let(HECATE, add(val(HECATE), _1)),
            goto("HECATE_REF_REVERSE"),
            companion=PUCK,
        ),
        # Length → Horatio stack+value; ACT_I_DONE pops stack into value.
        scene(
            "HECATE_REF_FINISH",
            let(HORATIO, val(HECATE)),
            push(HORATIO, val(HORATIO)),
            let(HECATE, _0),
            goto("ACT_I_DONE"),
            companion=HORATIO,
        ),
        # Never-taken A1.3 chain (entered only via rem == rem-1 from NEXT).
        scene("HECATE_REF_BRACKET", goto("HECATE_REF_LABEL"), companion=PUCK),
        scene("HECATE_REF_LABEL", goto("HECATE_REF_COLON"), companion=PUCK),
        scene("HECATE_REF_COLON", goto("HECATE_REF_URL_WS"), companion=PUCK),
        scene("HECATE_REF_URL_WS", goto("HECATE_REF_ANGLE"), companion=PUCK),
        scene("HECATE_REF_ANGLE", goto("HECATE_REF_URL"), companion=PUCK),
        scene("HECATE_REF_URL", goto("HECATE_REF_TITLE"), companion=PUCK),
        scene("HECATE_REF_TITLE", goto("HECATE_REF_TITLE_NL"), companion=PUCK),
        scene("HECATE_REF_TITLE_NL", goto("HECATE_REF_FOLD"), companion=PUCK),
        scene("HECATE_REF_FOLD", goto("HECATE_REF_ENCODE"), companion=PUCK),
        scene("HECATE_REF_ENCODE", goto("HECATE_REF_STORE"), companion=PUCK),
        scene("HECATE_REF_STORE", goto("HECATE_REF_REPLAY"), companion=PUCK),
        scene("HECATE_REF_REPLAY", goto("HECATE_REF_NEXT"), companion=PUCK),
    ]
