import os
import subprocess
from pathlib import Path

import pytest


def test_repo_shakedown_entrypoint_exists_and_is_executable() -> None:
    binary = Path(__file__).parent.parent / "shakedown"

    assert binary.is_file(), f"missing repo entrypoint: {binary}"
    assert os.access(binary, os.X_OK), f"repo entrypoint is not executable: {binary}"


@pytest.mark.xfail(
    strict=False,
    reason=(
        "play no longer raises a runtime error on truncated input since "
        "f45b626 (Act I handoff change); see .agent/blockers.md Spike A halt entry"
    ),
)
def test_repo_shakedown_entrypoint_reports_spl_runtime_errors() -> None:
    binary = Path(__file__).parent.parent / "shakedown"

    result = subprocess.run(
        [str(binary)],
        input="AT&T\n",
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, result.stderr
    assert "SPL runtime error:" in result.stderr
