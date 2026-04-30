"""Validate src/literary.toml shape and atom-cap compliance for Slice 1."""

from __future__ import annotations

import tomllib
from collections.abc import Iterator
from pathlib import Path

LITERARY_TOML = Path(__file__).parent.parent / "src" / "literary.toml"

CHARACTERS = {
    "rosalind": {"role": "librarian", "voice": "hybrid"},
    "horatio": {"role": "steward", "voice": "stable"},
    "puck": {"role": "herald", "voice": "hybrid"},
    "hecate": {"role": "sorter", "voice": "act_bound", "act": 1},
    "lady_macbeth": {"role": "mason", "voice": "act_bound", "act": 2},
    "macbeth": {"role": "apprentice", "voice": "act_bound", "act": 2},
    "romeo": {"role": "lyric_a", "voice": "act_bound", "act": 3},
    "juliet": {"role": "lyric_b", "voice": "act_bound", "act": 3},
    "prospero": {"role": "scribe", "voice": "act_bound", "act": 4},
}

REQUIRED_STABLE_UTILITY_VALUES = {1, 2, -1, 0}
ATOM_WORD_MAX = 6


def _atoms_in(phrase: str) -> list[str]:
    text = phrase.strip()
    prefix = "the sum of "
    if text.lower().startswith(prefix):
        rest = text[len(prefix) :]
        idx = rest.find(" and ")
        if idx == -1:
            return [text]
        left, right = rest[:idx], rest[idx + len(" and ") :]
        return _atoms_in(left) + _atoms_in(right)
    return [text]


def load() -> dict[str, object]:
    with LITERARY_TOML.open("rb") as f:
        return tomllib.load(f)


def test_file_exists() -> None:
    assert LITERARY_TOML.exists(), LITERARY_TOML


def test_all_characters_present() -> None:
    data = load()
    characters = data["characters"]
    assert isinstance(characters, dict)
    assert set(characters) == set(CHARACTERS), (
        sorted(set(characters)),
        sorted(set(CHARACTERS)),
    )


def test_stable_utility_coverage_for_slice1() -> None:
    data = load()
    characters = data["characters"]
    assert isinstance(characters, dict)
    for name in CHARACTERS:
        section = characters[name]
        assert isinstance(section, dict)
        stable = section.get("stable_utility", {})
        assert isinstance(stable, dict)
        for value in REQUIRED_STABLE_UTILITY_VALUES:
            key = f"v{value}" if value >= 0 else f"vneg{abs(value)}"
            assert key in stable, f"{name} missing home {key}"


def test_per_act_variants_when_present_have_legal_keys() -> None:
    data = load()
    characters = data["characters"]
    assert isinstance(characters, dict)
    for name, section in characters.items():
        assert isinstance(section, dict)
        per_act = section.get("per_act_stable_utility", {})
        assert isinstance(per_act, dict)
        for key in per_act:
            assert key in {"act1", "act2", "act3", "act4"}, (name, key)


def test_atom_cap() -> None:
    data = load()
    characters = data["characters"]
    assert isinstance(characters, dict)
    for name, section in characters.items():
        assert isinstance(section, dict)
        for surface_set, surfaces in _walk_surfaces(section):
            for value, phrase in surfaces.items():
                if not isinstance(phrase, str):
                    continue
                for atom in _atoms_in(phrase):
                    words = atom.split()
                    assert len(words) <= ATOM_WORD_MAX, (
                        f"{name}.{surface_set}.{value}: atom {atom!r} "
                        f"exceeds {ATOM_WORD_MAX} words"
                    )


def _walk_surfaces(
    section: dict[str, object],
) -> Iterator[tuple[str, dict[str, object]]]:
    stable = section.get("stable_utility")
    if isinstance(stable, dict):
        yield ("stable_utility", stable)
    per_act = section.get("per_act_stable_utility", {})
    if isinstance(per_act, dict):
        for act_key, surfaces in per_act.items():
            if isinstance(surfaces, dict):
                yield (f"per_act_stable_utility.{act_key}", surfaces)


def test_critical_zero_is_nothing() -> None:
    data = load()
    characters = data["characters"]
    assert isinstance(characters, dict)
    for name, section in characters.items():
        assert isinstance(section, dict)
        for surface_set, surfaces in _walk_surfaces(section):
            if "v0" in surfaces:
                assert surfaces["v0"] == "nothing", (
                    f"{name}.{surface_set}.v0 must be 'nothing' (Critical)"
                )


def test_current_surface_sections_exist() -> None:
    data = load()

    play = data.get("play")
    assert isinstance(play, dict)
    assert isinstance(play.get("title"), str)

    acts = data.get("acts")
    assert isinstance(acts, dict)
    assert set(acts) == {"act1", "act2", "act3", "act4"}
    for key, section in acts.items():
        assert isinstance(section, dict), key
        assert isinstance(section.get("title"), str), key

    scenes = data.get("scenes")
    assert isinstance(scenes, dict)
    assert scenes
    for label, scene in scenes.items():
        assert isinstance(scene, dict), label
        assert isinstance(scene.get("title"), str), label
        assert scene.get("pattern") in {
            "wherein",
            "bare_statement",
            "scene_of_character",
            "iconic_echo",
            "cross_character",
            "locale",
        }

    assert isinstance(data.get("iconic_moments"), dict)
    assert isinstance(data.get("dramatic_moments"), dict)


def test_character_soft_variation_and_recall_pools_exist() -> None:
    data = load()
    characters = data["characters"]
    assert isinstance(characters, dict)
    for name, section in characters.items():
        assert isinstance(section, dict), name
        soft = section.get("soft_variation")
        assert isinstance(soft, dict), name
        for key in (
            "greater_than",
            "less_than",
            "equality",
            "goto_forward",
            "goto_backward",
        ):
            values = soft.get(key)
            assert isinstance(values, list), (name, key)
            assert values, (name, key)
            assert all(isinstance(value, str) for value in values), (name, key)
        recall_pool = section.get("recall_pool")
        assert isinstance(recall_pool, list), name
        assert all(isinstance(value, str) for value in recall_pool), name
        assert len(recall_pool) == len(set(recall_pool)), name
