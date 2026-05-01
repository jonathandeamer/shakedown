from __future__ import annotations

from pathlib import Path

import pytest

from scripts.literary_surfaces import (
    LiterarySurfaces,
    load_literary_surfaces,
)


def _write_literary(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "literary.toml"
    path.write_text(text)
    return path


def test_resolve_known_literary_keys(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[play]
title = "Shakedown."

[acts.act1]
title = "Wherein the first act begins."

[scenes.DETAB_RAW]
title = "The cauldron is stirred."

[characters.hecate.recall]
detab_cauldron = "Recall the cauldron dreg."

[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
v2 = "a black cat"
v4 = "a furry black cat"
v8 = "a little furry black cat"
v16 = "a normal little furry black cat"
""",
    )

    surfaces = load_literary_surfaces(path)

    assert surfaces.resolve("play.title") == "Shakedown."
    assert surfaces.resolve("acts.act1.title") == "Wherein the first act begins."
    assert surfaces.resolve("scenes.DETAB_RAW.title") == "The cauldron is stirred."
    assert (
        surfaces.resolve("characters.hecate.recall.detab_cauldron")
        == "Recall the cauldron dreg."
    )
    assert surfaces.value_atoms("default")[16] == "a normal little furry black cat"


def test_unknown_key_raises_clear_error(tmp_path: Path) -> None:
    path = _write_literary(tmp_path, '[play]\ntitle = "Shakedown."\n')
    surfaces = load_literary_surfaces(path)

    with pytest.raises(KeyError, match="play.subtitle"):
        surfaces.resolve("play.subtitle")


def test_value_atoms_require_integer_keys(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
bad = "a cat"
""",
    )

    with pytest.raises(ValueError, match="value_atoms.default.bad"):
        load_literary_surfaces(path)


def test_value_atoms_reject_overlong_atoms(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[value_atoms.default]
v0 = "nothing"
v1 = "a big big big big big big cat"
""",
    )

    with pytest.raises(ValueError, match="exceeds 6 words"):
        load_literary_surfaces(path)


def test_value_atoms_reject_repeated_adjectives(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
v2 = "a big big cat"
""",
    )

    with pytest.raises(ValueError, match="repeats adjective"):
        load_literary_surfaces(path)


def test_literary_surfaces_type_is_constructible() -> None:
    surfaces = LiterarySurfaces(data={"play": {"title": "Shakedown."}})
    assert surfaces.resolve("play.title") == "Shakedown."
