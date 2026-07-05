"""splc IR validation: every violation is an error naming the scene."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.literary_surfaces import load_literary_surfaces
from scripts.splc.ir import (
    Char,
    act,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    scene,
    val,
)

LITERARY_TOML = Path(__file__).parent.parent / "src" / "literary.toml"


def _prose():  # noqa: ANN202
    from scripts.splc.prose import ProseEngine

    return ProseEngine(load_literary_surfaces(LITERARY_TOML))


def _tiny_act():  # noqa: ANN202
    # Uses real Act I scene labels so the TOML ledger check passes.
    return act(
        1,
        Char.HECATE,
        [
            scene(
                "ACT_I_START",
                let(Char.ROSALIND, const(1)),
                goto("ACT_I_DONE"),
            ),
            scene("ACT_I_DONE", halt_act(), companion=Char.ROSALIND),
        ],
    )


def test_valid_act_passes_and_returns_entry_pairs() -> None:
    from scripts.splc.validate import validate

    pairs = validate(_tiny_act(), _prose())
    assert pairs["ACT_I_START"] is None  # act start: empty stage
    assert pairs["ACT_I_DONE"] == (Char.HECATE, Char.ROSALIND)


def test_undefined_jump_target_rejected() -> None:
    from scripts.splc.validate import IrError, validate

    bad = act(
        1,
        Char.HECATE,
        [scene("ACT_I_START", let(Char.ROSALIND, const(1)), goto("NOWHERE"))],
    )
    with pytest.raises(IrError, match="NOWHERE"):
        validate(bad, _prose())


def test_fallthrough_rejected() -> None:
    from scripts.splc.validate import IrError, validate

    bad = act(
        1,
        Char.HECATE,
        [
            scene("ACT_I_START", let(Char.ROSALIND, const(1))),
            scene("ACT_I_DONE", halt_act(), companion=Char.ROSALIND),
        ],
    )
    with pytest.raises(IrError, match="ACT_I_START.*terminal"):
        validate(bad, _prose())


def test_unknown_scene_label_rejected() -> None:
    from scripts.splc.validate import IrError, validate

    bad = act(1, Char.HECATE, [scene("NO_SUCH_SCENE", halt_act(), companion=Char.PUCK)])
    with pytest.raises(IrError, match="NO_SUCH_SCENE"):
        validate(bad, _prose())


def test_unknown_recall_key_rejected() -> None:
    from scripts.splc.validate import IrError, validate

    bad = act(
        1,
        Char.HECATE,
        [scene("ACT_I_START", pop(Char.PUCK, recall="no_such_key"), halt_act())],
    )
    with pytest.raises(IrError, match="no_such_key"):
        validate(bad, _prose())


def test_three_characters_in_one_scene_rejected() -> None:
    from scripts.splc.validate import IrError, validate

    bad = act(
        1,
        Char.HECATE,
        [
            scene(
                "ACT_I_START",
                let(Char.ROSALIND, const(1)),
                let(Char.PUCK, val(Char.ROSALIND)),
                halt_act(),
            )
        ],
    )
    with pytest.raises(IrError, match="ACT_I_START"):
        validate(bad, _prose())


def test_inconsistent_predecessor_pairs_rejected() -> None:
    from scripts.splc.validate import IrError, validate

    bad = act(
        1,
        Char.HECATE,
        [
            scene(
                "ACT_I_START",
                branch(eq(val(Char.ROSALIND), const(0)), then="ACT_I_DONE"),
                goto("HECATE_READ_INPUT"),
                companion=Char.ROSALIND,
            ),
            scene(
                "HECATE_READ_INPUT",
                let(Char.PUCK, const(1)),
                branch(
                    eq(val(Char.PUCK), const(1)), then="ACT_I_DONE", else_="ACT_I_DONE"
                ),
            ),
            scene("ACT_I_DONE", halt_act(), companion=Char.ROSALIND),
        ],
    )
    # ACT_I_DONE is reached with (Hecate, Rosalind) from the first scene's branch
    # but (Hecate, Puck) from the second scene's branch.
    with pytest.raises(IrError, match="ACT_I_DONE"):
        validate(bad, _prose())


def test_expr_and_cond_references_stay_offstage() -> None:
    from scripts.splc.validate import participants

    sc = scene(
        "ACT_I_START",
        let(Char.ROSALIND, val(Char.HORATIO)),
        branch(
            eq(val(Char.MACBETH), const(0)),
            then="ACT_I_START",
            else_="ACT_I_START",
        ),
    )
    # Horatio and Macbeth are only referenced, never targeted: they stay
    # off stage and Rosalind is the sole non-anchor participant.
    assert participants(sc, Char.HECATE) == (Char.HECATE, Char.ROSALIND)


def test_scene_with_no_targets_requires_companion() -> None:
    from scripts.splc.validate import IrError, participants

    sc = scene(
        "ACT_I_START",
        branch(
            eq(val(Char.HORATIO), const(0)),
            then="ACT_I_START",
            else_="ACT_I_START",
        ),
    )
    with pytest.raises(IrError, match="companion"):
        participants(sc, Char.HECATE)


def test_offstage_value_reference_validates() -> None:
    from scripts.splc.validate import validate

    a = act(
        1,
        Char.HECATE,
        [
            scene(
                "ACT_I_START",
                let(Char.ROSALIND, val(Char.HORATIO)),
                goto("ACT_I_DONE"),
            ),
            scene("ACT_I_DONE", halt_act(), companion=Char.ROSALIND),
        ],
    )
    validate(a, _prose())  # must not raise


def test_mixed_goto_and_branch_predecessors_agree() -> None:
    from scripts.splc.validate import validate

    a = act(
        1,
        Char.HECATE,
        [
            # Branch predecessor: leaves (Hecate, Puck).
            scene(
                "ACT_I_START",
                let(Char.PUCK, const(1)),
                branch(
                    eq(val(Char.PUCK), const(0)),
                    then="ACT_I_DONE",
                    else_="HECATE_READ_INPUT",
                ),
            ),
            # Goto predecessor with the same leaving pair.
            scene(
                "HECATE_READ_INPUT",
                let(Char.PUCK, const(2)),
                goto("ACT_I_DONE"),
            ),
            # Target stages a different pair: branch-defined entry (Hecate, Puck).
            scene(
                "ACT_I_DONE",
                let(Char.ROSALIND, const(1)),
                halt_act(),
            ),
        ],
    )
    pairs = validate(a, _prose())
    assert pairs["ACT_I_DONE"] == (Char.HECATE, Char.PUCK)
