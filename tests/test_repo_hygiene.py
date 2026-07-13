# tests/test_repo_hygiene.py
"""Repo-wide hygiene gates.

These deliberately invoke the real ruff binary (like the generated-fragment
drift test invokes the real renderer): the point is to fail the loop's
full-suite evidence gate whenever lint debt lands, even if a commit bypassed
the pre-commit hook with --no-verify or an unconfigured core.hooksPath.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent


def _ruff(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ruff", *args, str(REPO)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_ruff_check_passes() -> None:
    result = _ruff("check")
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}{result.stderr}"


def test_ruff_format_is_clean() -> None:
    result = _ruff("format", "--check")
    assert result.returncode == 0, (
        f"ruff format --check failed:\n{result.stdout}{result.stderr}"
    )
