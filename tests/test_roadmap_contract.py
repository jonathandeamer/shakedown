from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).parent.parent
CLAUDE = REPO / "CLAUDE.md"
ACTIVE_PROMPT = REPO / "docs" / "prompt-shakedown.md"
ROADMAP = REPO / "docs" / "superpowers" / "plans" / "plan-roadmap.md"


def _read(path: Path) -> str:
    return path.read_text()


def test_claude_requires_reading_roadmap_before_plan_work() -> None:
    text = _read(CLAUDE)

    assert "Before starting SPL, plan, or implementation work" in text
    assert "docs/README.md" in text
    assert "docs/superpowers/plans/plan-roadmap.md" in text
    assert "source of truth for what plan is in flight" in text


def test_active_prompt_loads_roadmap_and_instructs_read_first() -> None:
    text = _read(ACTIVE_PROMPT)

    assert "@docs/superpowers/plans/plan-roadmap.md" in text
    assert "Read `@docs/superpowers/plans/plan-roadmap.md`" in text
    assert "first unchecked step" in text


def test_roadmap_has_at_most_one_in_flight_plan() -> None:
    in_flight_rows = [
        line
        for line in _read(ROADMAP).splitlines()
        if re.search(r"\|\s*in flight\s*(?:\||$)", line)
    ]

    assert len(in_flight_rows) <= 1, in_flight_rows
