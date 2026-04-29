"""Slice 1 gate: Amps and angle encoding must be SPL-owned and byte-identical."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
SHAKEDOWN = REPO / "shakedown"
HARNESS = REPO / "scripts" / "strict_parity_harness.py"
ASSEMBLED = REPO / "shakedown.spl"


def test_shakedown_entrypoint_no_longer_delegates_to_markdown_pl() -> None:
    text = SHAKEDOWN.read_text()
    forbidden = ("Markdown.pl", "markdown/Markdown.pl", "exec perl", "ORACLE=")
    assert not any(term in text for term in forbidden), text


def test_release_artifact_is_committed() -> None:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(ASSEMBLED.relative_to(REPO))],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_amps_and_angle_encoding_strict_parity() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "Amps and angle encoding",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "summary: 1/1 byte-identical" in result.stdout
