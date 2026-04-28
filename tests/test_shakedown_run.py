"""Dev wrapper skeleton tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
WRAPPER = REPO / "scripts" / "shakedown_run.py"


def test_wrapper_exists() -> None:
    assert WRAPPER.exists()


def test_wrapper_passes_through_empty_stdin() -> None:
    result = subprocess.run(
        [sys.executable, str(WRAPPER)],
        input=b"",
        capture_output=True,
        check=False,
    )
    assert b"Traceback" not in result.stderr, result.stderr.decode()


def test_wrapper_assembles_before_running() -> None:
    result = subprocess.run(
        [sys.executable, str(WRAPPER), "--print-assembled-path"],
        capture_output=True,
        check=True,
    )
    out = result.stdout.decode().strip()
    assert out.endswith(".cache/shakedown-dev.spl"), out
    assert Path(out).exists(), out
    assert not (REPO / "shakedown.spl").exists()


def test_wrapper_honours_cache_decision() -> None:
    result = subprocess.run(
        [sys.executable, str(WRAPPER), "--print-mode"],
        capture_output=True,
        check=True,
    )
    mode = result.stdout.decode().strip()
    assert mode in {"direct", "cached"}, mode


def test_wrapper_line_budget() -> None:
    lines = WRAPPER.read_text().splitlines()
    assert len(lines) <= 100, len(lines)
