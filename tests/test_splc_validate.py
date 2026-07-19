"""splc IR validation: every violation is an error naming the scene."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.literary_surfaces import load_literary_surfaces
from scripts.splc.ir import (
    Char,
    act,
    add,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    push,
    scene,
    val,
)
from scripts.splc.lower import lower_act
from src_ir.act2 import ACT as ACT2

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


def test_scene_anchor_override_changes_participants() -> None:
    from scripts.splc.validate import participants

    sc = scene(
        "ACT_I_START",
        let(Char.ROSALIND, const(1)),
        goto("ACT_I_DONE"),
        anchor=Char.PUCK,
    )
    # The scene-level anchor replaces the act anchor entirely.
    assert participants(sc, Char.HECATE) == (Char.PUCK, Char.ROSALIND)


def test_mixed_anchor_predecessors_compare_as_sets() -> None:
    from scripts.splc.validate import validate

    a = act(
        1,
        Char.HECATE,
        [
            # Leaves (Hecate, Puck).
            scene(
                "ACT_I_START",
                let(Char.PUCK, const(1)),
                branch(
                    eq(val(Char.PUCK), const(0)),
                    then="ACT_I_DONE",
                    else_="HECATE_READ_INPUT",
                ),
            ),
            # Same on-stage set, opposite tuple order: leaves (Puck, Hecate).
            scene(
                "HECATE_READ_INPUT",
                let(Char.HECATE, const(2)),
                branch(
                    eq(val(Char.HECATE), const(0)),
                    then="ACT_I_DONE",
                    else_="ACT_I_DONE",
                ),
                anchor=Char.PUCK,
            ),
            scene("ACT_I_DONE", halt_act(), companion=Char.PUCK),
        ],
    )
    validate(a, _prose())  # must not raise


def test_pop_recall_speaker_uses_scene_anchor() -> None:
    from scripts.splc.validate import IrError, validate

    # Pop targets the scene anchor, so the *other* pair member (Rosalind)
    # speaks the Recall — and she has no such key in her pool.
    a = act(
        1,
        Char.HECATE,
        [
            scene(
                "ACT_I_START",
                pop(Char.PUCK, recall="hewn_glyph"),
                goto("ACT_I_DONE"),
                anchor=Char.PUCK,
                companion=Char.ROSALIND,
            ),
            scene("ACT_I_DONE", halt_act(), companion=Char.ROSALIND),
        ],
    )
    with pytest.raises(IrError, match="rosalind"):
        validate(a, _prose())


def test_single_participant_scenes_can_model_buffered_span_state() -> None:
    from scripts.splc.interpret import InterpreterState, run_act
    from scripts.splc.validate import validate

    a = act(
        3,
        Char.ROMEO,
        [
            scene(
                "ACT_III_START",
                let(Char.ROMEO, const(2)),
                goto("LYRIC_BUFFER_OPEN"),
                companion=Char.PUCK,
            ),
            scene(
                "LYRIC_BUFFER_OPEN",
                let(Char.LADY_MACBETH, const(3)),
                goto("LYRIC_BUFFER_KEEP"),
                companion=Char.LADY_MACBETH,
            ),
            scene(
                "LYRIC_BUFFER_KEEP",
                push(Char.HECATE, const(-999)),
                let(Char.HECATE, const(0)),
                goto("LYRIC_BUFFER_DRAIN"),
                companion=Char.HECATE,
            ),
            scene(
                "LYRIC_BUFFER_DRAIN",
                push(Char.HECATE, const(ord("x"))),
                let(Char.HECATE, add(val(Char.HECATE), const(1))),
                goto("LYRIC_BUFFER_RETURN"),
                companion=Char.HECATE,
            ),
            scene(
                "LYRIC_BUFFER_RETURN",
                push(Char.PUCK, const(ord("!"))),
                goto("LYRIC_SCAN_NEXT"),
                companion=Char.PUCK,
            ),
            scene(
                "LYRIC_SCAN_NEXT",
                pop(Char.PUCK, recall="mornings_first_cut"),
                goto("ACT_III_DONE"),
                companion=Char.PUCK,
            ),
            scene(
                "ACT_III_DONE",
                let(Char.MACBETH, val(Char.PUCK)),
                halt_act(),
                companion=Char.MACBETH,
            ),
        ],
    )

    validate(a, _prose())
    result = run_act(a, InterpreterState(), step_limit=100)

    assert result.state.values[Char.ROMEO] == 2
    assert result.state.values[Char.LADY_MACBETH] == 3
    assert result.state.values[Char.HECATE] == 1
    assert result.state.values[Char.MACBETH] == ord("!")
    assert result.state.stacks[Char.HECATE] == [-999, ord("x")]
    assert result.state.stacks[Char.PUCK] == []


def test_goto_uses_surviving_source_stage_speaker_before_directions() -> None:
    a = act(
        1,
        Char.HECATE,
        [
            scene(
                "ACT_I_START",
                branch(
                    eq(val(Char.ROSALIND), const(0)),
                    then="ACT_I_DONE",
                    else_="HECATE_READ_INPUT",
                ),
                anchor=Char.PUCK,
                companion=Char.ROSALIND,
            ),
            scene(
                "HECATE_READ_INPUT",
                let(Char.PUCK, const(1)),
                goto("ACT_I_DONE"),
            ),
            scene(
                "ACT_I_DONE",
                halt_act(),
                anchor=Char.PUCK,
                companion=Char.ROSALIND,
            ),
        ],
    )

    text = lower_act(a, _prose())

    assert "Hecate:\n Let us proceed to scene @ACT_I_DONE.\n" not in text
    jump_index = text.index("Puck:\n Let us proceed to scene @ACT_I_DONE.\n")
    assert text.index("[Exit Hecate]\n", 0, jump_index) < jump_index
    assert text.index("[Enter Rosalind]\n", 0, jump_index) < jump_index


def test_disjoint_goto_entry_pair_is_rejected() -> None:
    from scripts.splc.validate import IrError, validate

    bad = act(
        1,
        Char.HECATE,
        [
            scene(
                "ACT_I_START",
                branch(
                    eq(val(Char.ROSALIND), const(0)),
                    then="ACT_I_DONE",
                    else_="HECATE_READ_INPUT",
                ),
                anchor=Char.PUCK,
                companion=Char.ROSALIND,
            ),
            scene(
                "HECATE_READ_INPUT",
                let(Char.JULIET, const(1)),
                goto("ACT_I_DONE"),
            ),
            scene(
                "ACT_I_DONE",
                halt_act(),
                anchor=Char.PUCK,
                companion=Char.ROSALIND,
            ),
        ],
    )

    with pytest.raises(IrError, match="HECATE_READ_INPUT.*ACT_I_DONE"):
        validate(bad, _prose())


_ACT2_SCENES_BY_LABEL = {sc.label: sc for sc in ACT2.scenes}


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("PASS_SETEXT_PROVED_CLOSE", (Char.LADY_MACBETH, Char.HECATE)),
        ("PASS_HEADER_TRAIL_OPEN", (Char.HECATE, Char.PUCK)),
        ("PASS_HEADER_TRAIL_SCAN", (Char.LADY_MACBETH, Char.HECATE)),
        ("PASS_HEADER_TRAIL_CAPTURE", (Char.HECATE, Char.PUCK)),
        ("PASS_HEADER_TRAIL_DECIDE", (Char.HECATE, Char.PUCK)),
        ("PASS_HEADER_TRAIL_DROP", (Char.HECATE, Char.PUCK)),
        ("PASS_HEADER_TRAIL_REPLAY", (Char.LADY_MACBETH, Char.PUCK)),
        ("PASS_HEADER_TRAIL_EXIT", (Char.LADY_MACBETH, Char.HECATE)),
    ],
)
def test_act2_a11_entry_pairs_use_only_the_authorized_scene_pairs(
    label: str, expected: tuple[Char, Char]
) -> None:
    from scripts.splc.validate import participants

    assert participants(_ACT2_SCENES_BY_LABEL[label], ACT2.anchor) == expected


def test_act2_a11_spare_labels_are_not_implemented_as_scenes() -> None:
    for label in (
        "PASS_SETEXT_RETURN_GUARD",
        "PASS_SETEXT_LEVEL_GUARD",
        "PASS_SETEXT_REPLAY_GUARD",
        "PASS_SETEXT_DISPATCH_GUARD",
        "PASS_SETEXT_ATX_GUARD",
        "PASS_HEADER_TRAIL_RETURN_GUARD",
        "PASS_HEADER_TRAIL_FLOOR_GUARD",
        "PASS_HEADER_TRAIL_CLOSE_GUARD",
    ):
        assert label not in _ACT2_SCENES_BY_LABEL


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("PASS_CODE_LINE_CAPTURE_OPEN", (Char.HECATE, Char.PUCK)),
        ("PASS_CODE_LINE_CAPTURE_SCAN", (Char.HECATE, Char.PUCK)),
        ("PASS_CODE_LINE_BLANK_DROP", (Char.HECATE, Char.PUCK)),
        ("PASS_CODE_LINE_KEEP_REVERSE_OPEN", (Char.PUCK, Char.HORATIO)),
        ("PASS_CODE_LINE_KEEP_REVERSE_TRANSFER", (Char.PUCK, Char.HORATIO)),
        ("PASS_CODE_LINE_KEEP_REPLAY", (Char.HORATIO, Char.LADY_MACBETH)),
        # CLOSE shares Horatio+Lady Macbeth with KEEP_REPLAY so both blank and
        # keep routes can discard the replay floor without a third participant.
        ("PASS_CODE_LINE_CLOSE", (Char.HORATIO, Char.LADY_MACBETH)),
    ],
)
def test_act2_a13_entry_pairs_use_only_the_authorized_scene_pairs(
    label: str, expected: tuple[Char, Char]
) -> None:
    from scripts.splc.validate import participants

    assert participants(_ACT2_SCENES_BY_LABEL[label], ACT2.anchor) == expected


def test_act2_a13_spare_labels_are_not_implemented_as_scenes() -> None:
    for label in (
        "PASS_CODE_LINE_RETURN_GUARD",
        "PASS_CODE_LINE_FLOOR_GUARD",
        "PASS_CODE_LINE_REPLAY_GUARD",
        "PASS_CODE_LINE_CLOSE_GUARD",
    ):
        assert label not in _ACT2_SCENES_BY_LABEL


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        # Design Amendment A17 first-pass pair ledger (supersedes A16 Macbeth pairs).
        ("PASS_PARA_WS_OPEN", (Char.HECATE, Char.PUCK)),
        ("PASS_PARA_WS_SCAN", (Char.LADY_MACBETH, Char.HECATE)),
        ("PASS_PARA_WS_CONTINUE", (Char.HECATE, Char.PUCK)),
        ("PASS_PARA_WS_BLANK_DROP", (Char.HECATE, Char.PUCK)),
        # TERMINATE is the blank-path goto bridge (Hecate+Puck matches
        # BLANK_DROP); soft-break REPLAY gotos RAW_GLYPH directly.
        ("PASS_PARA_WS_TERMINATE", (Char.HECATE, Char.PUCK)),
        ("PASS_PARA_WS_REVERSE_OPEN", (Char.PUCK, Char.HORATIO)),
        ("PASS_PARA_WS_REVERSE_TRANSFER", (Char.PUCK, Char.HORATIO)),
        ("PASS_PARA_WS_REPLAY", (Char.HORATIO, Char.LADY_MACBETH)),
    ],
)
def test_act2_a17_entry_pairs_use_only_the_authorized_scene_pairs(
    label: str, expected: tuple[Char, Char]
) -> None:
    from scripts.splc.validate import participants

    assert participants(_ACT2_SCENES_BY_LABEL[label], ACT2.anchor) == expected


def test_act2_a16_spare_labels_are_not_implemented_as_scenes() -> None:
    for label in (
        "PASS_PARA_WS_RETURN_GUARD",
        "PASS_PARA_WS_FLOOR_GUARD",
        "PASS_PARA_WS_REPLAY_GUARD",
        "PASS_PARA_WS_CONTINUE_GUARD",
    ):
        assert label not in _ACT2_SCENES_BY_LABEL


def test_act2_all_sixteen_guard_spares_are_absent_from_scenes() -> None:
    """A11+A13+A16 guard titles (12+4) must never appear as live scenes."""
    for label in (
        # A9/A11 setext + header-trail guards
        "PASS_SETEXT_RETURN_GUARD",
        "PASS_SETEXT_LEVEL_GUARD",
        "PASS_SETEXT_REPLAY_GUARD",
        "PASS_SETEXT_DISPATCH_GUARD",
        "PASS_SETEXT_ATX_GUARD",
        "PASS_HEADER_TRAIL_RETURN_GUARD",
        "PASS_HEADER_TRAIL_FLOOR_GUARD",
        "PASS_HEADER_TRAIL_CLOSE_GUARD",
        # A13 code-line guards
        "PASS_CODE_LINE_RETURN_GUARD",
        "PASS_CODE_LINE_FLOOR_GUARD",
        "PASS_CODE_LINE_REPLAY_GUARD",
        "PASS_CODE_LINE_CLOSE_GUARD",
        # A16 paragraph whitespace-boundary guards
        "PASS_PARA_WS_RETURN_GUARD",
        "PASS_PARA_WS_FLOOR_GUARD",
        "PASS_PARA_WS_REPLAY_GUARD",
        "PASS_PARA_WS_CONTINUE_GUARD",
    ):
        assert label not in _ACT2_SCENES_BY_LABEL
