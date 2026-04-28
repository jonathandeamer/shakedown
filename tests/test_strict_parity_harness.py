"""Strict parity harness self-test."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
HARNESS = REPO / "scripts" / "strict_parity_harness.py"
SHAKEDOWN = REPO / "shakedown"
ORACLE = Path.home() / "markdown" / "Markdown.pl"


def test_harness_exists() -> None:
    assert HARNESS.exists()


def test_harness_runs_on_synthetic_input(tmp_path: Path) -> None:
    if not ORACLE.exists():
        pytest.skip(f"oracle not present at {ORACLE}")
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "trivial.text").write_text("hello\n")
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--shakedown",
            str(SHAKEDOWN),
            "--markdown-pl",
            str(ORACLE),
            "--fixtures-dir",
            str(fixtures),
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    assert b"trivial" in result.stdout
    assert b"byte-identical: yes" in result.stdout


def test_harness_reports_mismatch(tmp_path: Path) -> None:
    if not ORACLE.exists():
        pytest.skip(f"oracle not present at {ORACLE}")
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "trivial.text").write_text("hello\n")
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--shakedown",
            "/bin/cat",
            "--markdown-pl",
            str(ORACLE),
            "--fixtures-dir",
            str(fixtures),
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert b"byte-identical: no" in result.stdout
