"""Fail fast, with the real parse error, when the committed play is broken.

Without this, a non-parsing shakedown.spl surfaces as byte-mismatch
failures against empty output across the whole suite.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).parent.parent


def test_committed_shakedown_spl_parses() -> None:
    from shakespearelang import Shakespeare

    Shakespeare((REPO / "shakedown.spl").read_text())
