"""Integration test for the Slice-5 documentation aggregates probe."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent


def test_dummy_prevent_empty_suite() -> None:
    """Dummy test to avoid empty suite exit code 5 when excluding integration tests."""
    pass


def test_documentation_probes_module_runs_via_python_m() -> None:
    """Verify the probe is importable and executable via ``python -m``."""
    result = subprocess.run(
        ["uv", "run", "python", "-m", "scripts.probe_documentation_aggregates"],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )

    assert result.returncode == 0, result.stderr
