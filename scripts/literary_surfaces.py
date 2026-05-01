"""Load and resolve TOML-backed SPL literary surfaces."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

ATOM_WORD_MAX = 6
_VALUE_KEY_RE = re.compile(r"^v(?P<value>0|[1-9][0-9]*)$")


@dataclass(frozen=True)
class LiterarySurfaces:
    """Resolved access to `src/literary.toml`."""

    data: dict[str, object]

    def resolve(self, key: str) -> str:
        current: object = self.data
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                raise KeyError(key)
            current = current[part]
        if not isinstance(current, str):
            raise KeyError(key)
        return current

    def value_atoms(self, family: str = "default") -> dict[int, str]:
        value_atoms = self.data.get("value_atoms")
        if not isinstance(value_atoms, dict):
            raise KeyError("value_atoms")
        raw_family = value_atoms.get(family)
        if not isinstance(raw_family, dict):
            raise KeyError(f"value_atoms.{family}")
        atoms: dict[int, str] = {}
        for key, phrase in raw_family.items():
            if not isinstance(key, str) or not isinstance(phrase, str):
                raise ValueError(f"value_atoms.{family}.{key}")
            match = _VALUE_KEY_RE.match(key)
            if match is None:
                raise ValueError(f"value_atoms.{family}.{key}")
            _validate_atom_phrase(f"value_atoms.{family}.{key}", phrase)
            atoms[int(match["value"])] = phrase
        return atoms


def load_literary_surfaces(path: Path) -> LiterarySurfaces:
    with path.open("rb") as f:
        data = tomllib.load(f)
    surfaces = LiterarySurfaces(data=cast(dict[str, object], data))
    if "value_atoms" in data:
        value_atoms = data["value_atoms"]
        if isinstance(value_atoms, dict):
            for family in value_atoms:
                if isinstance(family, str):
                    surfaces.value_atoms(family)
    return surfaces


def _validate_atom_phrase(key: str, phrase: str) -> None:
    for atom in _atoms_in(phrase):
        words = atom.split()
        if len(words) > ATOM_WORD_MAX:
            raise ValueError(f"{key}: atom {atom!r} exceeds {ATOM_WORD_MAX} words")
        _reject_repeated_adjectives(key, atom)


def _reject_repeated_adjectives(key: str, atom: str) -> None:
    words = atom.split()
    if len(words) < 3 or words[0] not in {"a", "an"}:
        return
    adjectives = words[1:-1]
    if len(adjectives) != len(set(adjectives)):
        raise ValueError(f"{key}: atom {atom!r} repeats adjective")


def _atoms_in(phrase: str) -> list[str]:
    text = phrase.strip()
    for prefix in ("the sum of ", "the product of "):
        if not text.lower().startswith(prefix):
            continue
        rest = text[len(prefix) :]
        for match in reversed(list(re.finditer(r" and ", rest))):
            left = rest[: match.start()]
            right = rest[match.end() :]
            return _atoms_in(left) + _atoms_in(right)
        return [text]
    square_prefix = "the square of "
    if text.lower().startswith(square_prefix):
        return _atoms_in(text[len(square_prefix) :])
    return [text]
