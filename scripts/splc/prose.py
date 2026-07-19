"""Literary engine: renders every prose surface from src/literary.toml pools.

The compiler never invents prose. Seeded pool selection is deterministic so
rebuilds are byte-stable. See design spec §Literary Engine.
"""

from __future__ import annotations

import random
from typing import cast

from scripts.codegen_html import emit_value
from scripts.literary_surfaces import LiterarySurfaces
from scripts.splc.ir import Char

_COND_POOL = {"eq": "equality", "gt": "greater_than", "lt": "less_than"}


_P100 = "the square of the sum of a little furry black cat and a black cat"
_P105 = (
    "the product of the difference between a normal little furry black cat and a"
    " cat and the difference between a little furry black cat and a cat"
)
_P112 = (
    "the product of a normal little furry black cat and the difference between"
    " a little furry black cat and a cat"
)
_P120 = (
    "the difference between the product of a normal little furry black cat and"
    " a little furry black cat and a little furry black cat"
)
_P122 = (
    "the difference between the product of a normal little furry black cat and"
    " a little furry black cat and the sum of a furry black cat and a black cat"
)
_P128 = "the product of a normal little furry black cat and a little furry black cat"
_P132 = (
    "the sum of the product of a normal little furry black cat and a little"
    " furry black cat and a furry black cat"
)
_P144 = (
    "the square of the difference between a normal little furry black cat and a"
    " furry black cat"
)

_NEG_SPECIAL_PHRASES: dict[int, str] = {
    -100: f"the difference between nothing and {_P100}",
    -101: f"the difference between nothing and the sum of {_P100} and a cat",
    -102: (f"the difference between nothing and the sum of {_P100} and a black cat"),
    -103: f"the difference between a black cat and {_P105}",
    -104: (
        f"the difference between nothing and the sum of {_P100} and a furry black cat"
    ),
    -105: f"the difference between nothing and {_P105}",
    -110: f"the difference between a black cat and {_P112}",
    -111: f"the difference between a cat and {_P112}",
    -112: f"the difference between nothing and {_P112}",
    -113: f"the difference between nothing and the sum of {_P112} and a cat",
    -114: (f"the difference between nothing and the sum of {_P112} and a black cat"),
    -115: (f"the difference between a rotten toad and the sum of a cat and {_P112}"),
    -120: f"the difference between nothing and {_P120}",
    -121: f"the difference between nothing and the sum of {_P120} and a cat",
    -122: f"the difference between nothing and {_P122}",
    -130: f"the difference between a black cat and {_P132}",
    -131: (
        f"the difference between nothing and the sum of {_P128} and the sum of"
        " a cat and a black cat"
    ),
    -140: f"the difference between a furry black cat and {_P144}",
    -141: (f"the difference between the sum of a cat and a black cat and {_P144}"),
    -142: f"the difference between a black cat and {_P144}",
}


class ProseEngine:
    def __init__(self, surfaces: LiterarySurfaces) -> None:
        self._data = cast(dict[str, object], surfaces.data)

    def _section(self, *path: str) -> dict[str, object]:
        node: object = self._data
        for key in path:
            if not isinstance(node, dict) or key not in node:
                raise KeyError(f"literary.toml missing {'.'.join(path)} (at {key!r})")
            node = node[key]
        if not isinstance(node, dict):
            raise KeyError(f"literary.toml {'.'.join(path)} is not a table")
        return cast(dict[str, object], node)

    def scene_heading(self, label: str) -> str:
        scenes = self._section("scenes")
        if label not in scenes:
            raise KeyError(f"no [scenes.{label}] entry in literary TOMLs")
        return f"Scene @{label}: @LIT.scenes.{label}.title"

    def value_phrase(self, speaker: Char, n: int) -> str:
        stable = self._section("characters", speaker.toml_key, "stable_utility")
        key = f"v{n}" if n >= 0 else f"vneg{abs(n)}"
        phrase = stable.get(key)
        if isinstance(phrase, str):
            return phrase
        if n in _NEG_SPECIAL_PHRASES:
            return _NEG_SPECIAL_PHRASES[n]
        if n < 0:
            pos_phrase = self.value_phrase(speaker, abs(n))
            return f"the difference between nothing and {pos_phrase}"
        return emit_value(n)

    def _pick(self, pool: list[str], seed: str) -> str:
        return random.Random(seed).choice(pool)

    def _variation_pool(self, speaker: Char, key: str) -> list[str]:
        pools = self._section("characters", speaker.toml_key, "soft_variation")
        pool = pools.get(key)
        if not isinstance(pool, list) or not pool:
            raise KeyError(f"empty soft_variation.{key} pool for {speaker.value}")
        return cast(list[str], pool)

    def comparator(self, speaker: Char, cond_op: str, seed: str) -> str:
        return self._pick(self._variation_pool(speaker, _COND_POOL[cond_op]), seed)

    def goto_phrase(self, speaker: Char, backward: bool, seed: str) -> str:
        key = "goto_backward" if backward else "goto_forward"
        return self._pick(self._variation_pool(speaker, key), seed)

    def recall_placeholder(self, speaker: Char, key: str) -> str:
        recalls = self._section("characters", speaker.toml_key, "recall")
        if key not in recalls:
            raise KeyError(f"no [characters.{speaker.toml_key}.recall] key {key!r}")
        return f"@LIT.characters.{speaker.toml_key}.recall.{key}"
