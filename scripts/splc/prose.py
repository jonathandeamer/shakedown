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
        if n < 0:
            raise ValueError(
                f"no stable_utility phrase for negative value {n} "
                f"(speaker {speaker.value})"
            )
        families = self._data.get("value_atoms")
        family = speaker.toml_key
        if not isinstance(families, dict) or family not in families:
            family = "default"
        return emit_value(n, family=family)

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
