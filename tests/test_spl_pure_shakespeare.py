"""Integration gate: pure shakespeare CLI (`./shakedown`) vs mdtest oracle.

Default ``uv run pytest`` excludes ``@pytest.mark.integration`` (see
``pyproject.toml``). Run explicitly:

    uv run pytest tests/test_spl_pure_shakespeare.py -m integration -q

Or the strict harness:

    uv run python scripts/strict_parity_harness.py --shakedown ./shakedown

Compares with the same normalization as ``tests/test_mdtest.py`` (strict
Markdown.pl bytes for deterministic fixtures; entity-normalized Auto links).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.test_mdtest import (
    _FIXTURES_BY_NAME,
    _IMPLEMENTED_FIXTURES,
    _expected_fixture_output,
    _normalize_fixture_output,
)

REPO = Path(__file__).parent.parent
SHAKEDOWN = REPO / "shakedown"


@pytest.mark.integration
@pytest.mark.parametrize("name", sorted(_IMPLEMENTED_FIXTURES))
def test_shakespeare_cli_matches_oracle(name: str) -> None:
    """``./shakedown`` (shakespeare run on committed play) matches fixture oracle."""
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    input_text = input_path.read_text()
    expected = _expected_fixture_output(name, input_path, expected_path)
    norm_expected = _normalize_fixture_output(name, expected)

    result = subprocess.run(
        [str(SHAKEDOWN)],
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"./shakedown failed for '{name}' (rc={result.returncode})\n"
        f"stderr:\n{result.stderr}"
    )
    norm_actual = _normalize_fixture_output(name, result.stdout)
    assert norm_actual == norm_expected, (
        f"Pure shakespeare CLI mismatch for '{name}'\n"
        f"--- expected\n{norm_expected}\n"
        f"+++ actual (./shakedown)\n{norm_actual}"
    )
