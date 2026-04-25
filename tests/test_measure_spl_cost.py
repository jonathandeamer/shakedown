"""Smoke test for scripts/measure_spl_cost.py.

Does not measure production SPL — only validates the harness runs and parses.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_measure_spl_cost_runs_on_empty_probe(tmp_path: Path) -> None:
    probe = tmp_path / "noop.spl"
    probe.write_text(
        "Noop.\n\n"
        "Juliet, a speaker.\n\n"
        "                    Act I: Noop.\n\n"
        "                    Scene I: End.\n\n"
        "[Enter Juliet]\n"
        "[Exeunt]\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "measure_spl_cost.py"),
            str(probe),
            "--runs",
            "2",
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "first:" in result.stdout
    assert "median:" in result.stdout
