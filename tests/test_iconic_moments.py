"""Validate iconic-moment maps satisfy literary-spec budgets."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

DOC = Path(__file__).parent.parent / "docs" / "spl" / "iconic-moments.md"

SCENE_TITLE_MAX = 12
RECALL_ECHO_MIN = 4
RECALL_ECHO_MAX = 8
COMBINED_MAX = 20


def parse_iconic_moments() -> dict[str, list[dict[str, str]]]:
    """Extract the two TOML fenced blocks from the doc."""
    text = DOC.read_text()
    matches = re.findall(r"```toml\n(.*?)```", text, flags=re.DOTALL)
    assert len(matches) == 2, f"expected 2 toml blocks, got {len(matches)}"
    scene_titles = tomllib.loads(matches[0])["scene_titles"]
    recall_echoes = tomllib.loads(matches[1])["recall_echoes"]
    return {"scene_titles": scene_titles, "recall_echoes": recall_echoes}


def test_doc_exists() -> None:
    assert DOC.exists(), DOC


def test_scene_title_budget() -> None:
    moments = parse_iconic_moments()["scene_titles"]
    assert len(moments) <= SCENE_TITLE_MAX, len(moments)


def test_recall_echo_budget() -> None:
    moments = parse_iconic_moments()["recall_echoes"]
    assert RECALL_ECHO_MIN <= len(moments) <= RECALL_ECHO_MAX, len(moments)


def test_combined_ceiling() -> None:
    parsed = parse_iconic_moments()
    total = len(parsed["scene_titles"]) + len(parsed["recall_echoes"])
    assert total <= COMBINED_MAX, total


def test_single_surface_rule() -> None:
    """Each Shakespeare phrase appears in exactly one iconic surface."""
    parsed = parse_iconic_moments()
    phrases = [m["phrase"] for m in parsed["scene_titles"]]
    phrases += [m["phrase"] for m in parsed["recall_echoes"]]
    duplicates = {p for p in phrases if phrases.count(p) > 1}
    assert not duplicates, f"phrases reused across surfaces: {sorted(duplicates)}"


def test_required_fields_present() -> None:
    parsed = parse_iconic_moments()
    for moment in parsed["scene_titles"] + parsed["recall_echoes"]:
        for field in ("phrase", "play", "speaker", "shakedown_use"):
            assert field in moment, f"missing {field} in {moment}"
