"""Pure-op Act I reference strip (Task 2L Step 2 / Amendment A3) — INCOMPLETE.

Scaffold: stage-pair-valid A1.3 goto lattice extracted for pure-op fill-in.
Does **not** implement strip/table semantics yet (see .agent/blockers.md).

Completion requirements (A3.1–A3.6):
- Real pop/push/branch/let bodies; two participants per scene
- Promote HECATE_REF_URL_GUARD from spares when url_ws_nl is implemented
- Branch targets that share a label must leave a consistent stage pair;
  prefer goto into a same-pair bridge before changing pairs
- Match act1_ref_strip.apply_act1_reference_strip under USE_ACT1_REF_INTRINSIC=False
"""

from __future__ import annotations

from scripts.splc.ir import Scene, goto, scene
from src_ir.cast import HORATIO, PUCK, ROSALIND


def build_ref_scenes() -> list[Scene]:
    """A1.3 goto lattice only — pure-op bodies not yet filled."""
    return [
        scene("HECATE_REF_OPEN", goto("HECATE_REF_NEXT"), companion=HORATIO),
        scene("HECATE_REF_NEXT", goto("HECATE_REF_LEAD"), companion=PUCK),
        scene("HECATE_REF_LEAD", goto("HECATE_REF_FOUR_SPACE"), companion=HORATIO),
        scene("HECATE_REF_FOUR_SPACE", goto("HECATE_REF_BRACKET"), companion=PUCK),
        scene("HECATE_REF_BRACKET", goto("HECATE_REF_LABEL"), companion=PUCK),
        scene("HECATE_REF_LABEL", goto("HECATE_REF_COLON"), companion=PUCK),
        scene("HECATE_REF_COLON", goto("HECATE_REF_URL_WS"), companion=PUCK),
        scene("HECATE_REF_URL_WS", goto("HECATE_REF_ANGLE"), companion=HORATIO),
        scene("HECATE_REF_ANGLE", goto("HECATE_REF_URL"), companion=PUCK),
        scene("HECATE_REF_URL", goto("HECATE_REF_TITLE"), companion=PUCK),
        scene("HECATE_REF_TITLE", goto("HECATE_REF_TITLE_NL"), companion=PUCK),
        scene("HECATE_REF_TITLE_NL", goto("HECATE_REF_FOLD"), companion=PUCK),
        scene("HECATE_REF_FOLD", goto("HECATE_REF_ENCODE"), companion=ROSALIND),
        scene("HECATE_REF_ENCODE", goto("HECATE_REF_STORE"), companion=ROSALIND),
        scene("HECATE_REF_STORE", goto("HECATE_REF_KEEP"), companion=ROSALIND),
        scene("HECATE_REF_KEEP", goto("HECATE_REF_REPLAY"), companion=PUCK),
        scene("HECATE_REF_REPLAY", goto("HECATE_REF_NL"), companion=PUCK),
        scene("HECATE_REF_NL", goto("HECATE_REF_REVERSE"), companion=HORATIO),
        scene("HECATE_REF_REVERSE", goto("HECATE_REF_FINISH"), companion=PUCK),
        scene("HECATE_REF_FINISH", goto("ACT_I_DONE"), companion=HORATIO),
    ]
