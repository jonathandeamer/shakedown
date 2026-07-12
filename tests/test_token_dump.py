"""The debug target dumps the inter-act token stream as integers."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
DEBUG_WRAPPER = REPO / "shakedown-debug"
AMPS_FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Amps and angle encoding.text"
)


def test_debug_target_dumps_integer_token_stream() -> None:
    result = subprocess.run(
        [str(DEBUG_WRAPPER)],
        input=AMPS_FIXTURE.read_bytes(),
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    lines = result.stdout.decode().strip().splitlines()
    assert len(lines) > 10
    values = [int(line) for line in lines]
    # Production Act IV emits <p> first for this fixture (Slice 1 is
    # byte-identical), so the first popped stream value must be the
    # PARAGRAPH_OPEN token.
    assert values[0] == 1


BASELINES = REPO / "tests" / "fixtures" / "token_stream"
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"
LIST_BASELINES = BASELINES / "lists"
NESTED_BLOCK_FIXTURES = (
    REPO / "tests" / "fixtures" / "architecture_spikes" / "nested_blocks"
)
NESTED_BLOCK_BASELINES = BASELINES / "nested_blocks"


def _dump(input_bytes: bytes) -> bytes:
    result = subprocess.run(
        [str(DEBUG_WRAPPER)],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    return result.stdout


def test_dump_matches_blessed_amps_baseline() -> None:
    """G2 gate: blessed by the P1 plan; P2 and later slices re-bless
    deliberately when the vocabulary grows, never casually."""
    assert _dump(AMPS_FIXTURE.read_bytes()) == (BASELINES / "amps.dump").read_bytes()


def test_dump_matches_blessed_short_baseline() -> None:
    assert _dump(b"hello\n\nworld\n") == (BASELINES / "short.dump").read_bytes()


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in LIST_FIXTURES.glob("*.text")),
)
def test_dump_matches_blessed_list_baseline(stem: str) -> None:
    """G2 gate over the P2 list vocabulary: blessed by the P2 plan after
    hand-review; later slices re-bless deliberately, never casually."""
    fixture = LIST_FIXTURES / f"{stem}.text"
    assert _dump(fixture.read_bytes()) == (LIST_BASELINES / f"{stem}.dump").read_bytes()


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in NESTED_BLOCK_FIXTURES.glob("*.text")),
)
def test_dump_matches_blessed_nested_block_baseline(stem: str) -> None:
    fixture = NESTED_BLOCK_FIXTURES / f"{stem}.text"
    assert _dump(fixture.read_bytes()) == (
        NESTED_BLOCK_BASELINES / f"{stem}.dump"
    ).read_bytes()
