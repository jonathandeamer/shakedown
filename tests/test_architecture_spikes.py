from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
SHAKEDOWN = REPO / "shakedown"
MARKDOWN_PL = Path.home() / "markdown" / "Markdown.pl"
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"


def _first_diff(a: bytes, b: bytes) -> int | None:
    for idx, (left, right) in enumerate(zip(a, b, strict=False)):
        if left != right:
            return idx
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def _run(argv: list[str], input_bytes: bytes) -> bytes:
    result = subprocess.run(
        argv,
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=True,
    )
    return result.stdout


def _list_cases() -> list[Path]:
    return sorted(LIST_FIXTURES.glob("*.text"))


_SPIKE_A_HALT_REASON = (
    "List semantics not yet implemented: the SPL-from-IR architecture "
    "revision (plans 3G-3J) resolved the Spike A hand-authoring halt; "
    "the resumed list plan is written in IR against the fully ported play "
    "(docs/superpowers/plans/plan-roadmap.md)"
)


@pytest.mark.parametrize(
    "fixture",
    [
        pytest.param(
            path,
            id=path.stem,
            marks=pytest.mark.xfail(reason=_SPIKE_A_HALT_REASON, strict=False),
        )
        for path in _list_cases()
    ],
)
def test_list_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
    input_bytes = fixture.read_bytes()
    actual = _run([str(SHAKEDOWN)], input_bytes)
    expected = _run(["perl", str(MARKDOWN_PL)], input_bytes)

    assert actual == expected, (
        f"Output mismatch for {fixture.name}; first diff: "
        f"{_first_diff(actual, expected)}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual\n{actual.decode(errors='replace')}"
    )
