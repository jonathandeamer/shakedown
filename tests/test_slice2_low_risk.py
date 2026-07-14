"""Slice 2 fixture-specific strict-parity and no-oracle-stub regression
tests. Fixture assertions are added task by task as each fixture's IR and
real-wrapper acceptance gates pass; see the active plan
docs/superpowers/plans/2026-07-14-slice-2-low-risk-fixtures.md."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).parent.parent
SHAKEDOWN = REPO / "shakedown"


def test_shakedown_entrypoint_still_has_no_oracle_fallback() -> None:
    text = SHAKEDOWN.read_text()
    forbidden = ("Markdown.pl", "markdown/Markdown.pl", "exec perl", "ORACLE=")
    assert not any(term in text for term in forbidden), text
