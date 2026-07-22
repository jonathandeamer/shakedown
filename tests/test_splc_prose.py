"""Prose engine: every rendered surface comes from src/literary.toml pools."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.literary_surfaces import load_literary_surfaces

LITERARY_TOML = Path(__file__).parent.parent / "src" / "literary.toml"


def _engine():  # noqa: ANN202  # return type is the class under test
    from scripts.splc.prose import ProseEngine

    return ProseEngine(load_literary_surfaces(LITERARY_TOML))


def test_scene_heading_uses_lit_placeholder() -> None:
    engine = _engine()
    heading = engine.scene_heading("ACT_I_START")
    assert heading == "Scene @ACT_I_START: @LIT.scenes.ACT_I_START.title"


def test_scene_heading_rejects_unknown_label() -> None:
    engine = _engine()
    with pytest.raises(KeyError, match="NO_SUCH_SCENE"):
        engine.scene_heading("NO_SUCH_SCENE")


def test_value_phrase_prefers_speaker_stable_utility() -> None:
    from scripts.splc.ir import Char

    engine = _engine()
    assert engine.value_phrase(Char.HECATE, 1) == "a cat"
    assert engine.value_phrase(Char.HECATE, 0) == "nothing"
    assert engine.value_phrase(Char.HECATE, -1) == "a toad"


def test_value_phrase_falls_back_to_codegen_atoms() -> None:
    from scripts.codegen_html import parse_value_phrase
    from scripts.splc.ir import Char

    engine = _engine()
    phrase = engine.value_phrase(Char.HECATE, 101)
    assert parse_value_phrase(phrase) == 101


def test_value_phrase_rejects_unpooled_negative() -> None:
    from scripts.splc.ir import Char

    engine = _engine()
    with pytest.raises(ValueError, match="-7"):
        engine.value_phrase(Char.HECATE, -7)


def test_comparator_is_seeded_deterministic_and_pooled() -> None:
    from scripts.splc.ir import Char

    engine = _engine()
    first = engine.comparator(Char.HECATE, "eq", "SCENE:0")
    again = engine.comparator(Char.HECATE, "eq", "SCENE:0")
    assert first == again
    assert first in {
        "as cursed as",
        "as rotten as",
        "as horrid as",
        "as foul as",
        "as vile as",
        "as miserable as",
    }


def test_goto_phrase_direction_pools() -> None:
    from scripts.splc.ir import Char

    engine = _engine()
    forward = engine.goto_phrase(Char.HECATE, backward=False, seed="S:0")
    backward = engine.goto_phrase(Char.HECATE, backward=True, seed="S:0")
    assert forward == "Let us proceed to"
    assert backward == "We must return to"


def test_recall_placeholder_validates_key() -> None:
    from scripts.splc.ir import Char

    engine = _engine()
    line = engine.recall_placeholder(Char.HECATE, "cauldron_dreg")
    assert line == "@LIT.characters.hecate.recall.cauldron_dreg"
    with pytest.raises(KeyError, match="no_such_key"):
        engine.recall_placeholder(Char.HECATE, "no_such_key")
