"""Executable pre-design SPL probes for architecture-risk closure."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "docs" / "spl" / "probes" / "pre-design"


@pytest.mark.parametrize(
    ("probe_name", "expected"),
    [
        ("reference-lookup.spl", "reference lookup: pass\n"),
        ("setext-buffering.spl", "setext buffering: pass\n"),
        ("list-state-stack.spl", "list state stack: pass\n"),
    ],
)
def test_pre_design_spl_probe(probe_name: str, expected: str) -> None:
    probe_path = PROBE_DIR / probe_name
    if not probe_path.exists():
        pytest.xfail(f"{probe_name} not implemented yet")

    result = subprocess.run(
        ["uv", "run", "shakespeare", "run", str(probe_path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, (
        f"{probe_name} failed with {result.returncode}\nstderr:\n{result.stderr}"
    )
    assert result.stdout == expected
