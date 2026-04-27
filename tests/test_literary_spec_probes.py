"""Executable SPL probes for literary-spec interpreter claims."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "docs" / "spl" / "probes"

SHAKESPEARE = shutil.which("shakespeare")
if SHAKESPEARE is None:
    fallback = Path.home() / ".local/bin/shakespeare"
    if fallback.is_file():
        SHAKESPEARE = str(fallback)
    else:
        pytest.skip(
            "shakespeare interpreter not found on PATH or in ~/.local/bin",
            allow_module_level=True,
        )


@pytest.mark.parametrize(
    ("probe_name", "expected"),
    [
        ("three-character-safe-envelope.spl", "1"),
    ],
)
def test_literary_spec_probe(probe_name: str, expected: str) -> None:
    probe_path = PROBE_DIR / probe_name

    result = subprocess.run(
        [str(SHAKESPEARE), "run", str(probe_path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, (
        f"{probe_name} failed with {result.returncode}\nstderr:\n{result.stderr}"
    )
    assert result.stdout == expected
