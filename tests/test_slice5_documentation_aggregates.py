"""Slice-5 documentation aggregate pre-enable contracts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.runtime_constants import DOCUMENTATION_STEP_LIMIT
from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4
from tests.test_mdtest import (
    _FIXTURES_BY_NAME,
    _IMPLEMENTED_FIXTURES,
    _SLICE5_STRICT_READY_FIXTURES,
    BINARY,
    _normalize_fixture_output,
    _run_acts,
)

REPO = Path(__file__).parent.parent
HARNESS = REPO / "scripts" / "strict_parity_harness.py"
MARKDOWN_PL = Path.home() / "markdown" / "Markdown.pl"
TIDYNESS_INPUT = (
    "> A list within a blockquote:\n"
    "> \n"
    "> *\tasterisk 1\n"
    "> *\tasterisk 2\n"
    "> *\tasterisk 3\n"
)


def _run_acts_with_limit(
    input_text: str, *, through_act: int, step_limit: int
) -> str | list[int]:
    from scripts.splc.ir import Char
    from src_ir import tokens

    state = InterpreterState(input_text=input_text)
    acts = (ACT1, ACT2, ACT3, ACT4)
    for act in acts[:through_act]:
        state = run_act(act, state, step_limit=step_limit).state
    if through_act == 4:
        return state.output_text()
    stream = list(reversed(state.stacks[Char.PUCK]))
    if stream and stream[-1] == tokens.STREAM_END:
        stream.pop()
    return stream


def _fixture_paths(name: str) -> tuple[Path, Path]:
    return _FIXTURES_BY_NAME[name]


@pytest.mark.parametrize("through_act", [1, 2, 3, 4])
def test_syntax_fits_within_documentation_step_limit_per_act(through_act: int) -> None:
    input_path, _ = _fixture_paths("Markdown Documentation - Syntax")
    actual = _run_acts_with_limit(
        input_path.read_text(),
        through_act=through_act,
        step_limit=DOCUMENTATION_STEP_LIMIT,
    )
    if through_act == 4:
        assert isinstance(actual, str)
        return
    assert isinstance(actual, list)


def test_syntax_release_binary_returns_zero() -> None:
    input_path, _ = _fixture_paths("Markdown Documentation - Syntax")
    result = subprocess.run(
        [str(BINARY)],
        input=input_path.read_text(),
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("fixture_name", sorted(_SLICE5_STRICT_READY_FIXTURES))
def test_slice5_strict_ready_fixture_enablement_contracts(fixture_name: str) -> None:
    input_path, expected_path = _fixture_paths(fixture_name)

    assert fixture_name in _IMPLEMENTED_FIXTURES

    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize_fixture_output(fixture_name, actual) == _normalize_fixture_output(
        fixture_name, expected_path.read_text()
    )

    result = subprocess.run(
        [str(BINARY)],
        input=input_path.read_text(),
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert _normalize_fixture_output(
        fixture_name, result.stdout
    ) == _normalize_fixture_output(fixture_name, expected_path.read_text())

    harness = subprocess.run(
        [sys.executable, str(HARNESS), fixture_name],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    assert harness.returncode == 0, harness.stderr
    assert "summary: 1/1 byte-identical" in harness.stdout


def test_tidyness_exact_fixture_matches_fast_release_and_raw_oracle() -> None:
    fixture_name = "Tidyness"
    input_path, expected_path = _fixture_paths(fixture_name)
    assert input_path.read_text() == TIDYNESS_INPUT
    input_bytes = TIDYNESS_INPUT.encode()
    oracle = subprocess.run(
        ["perl", str(MARKDOWN_PL)],
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=False,
    )
    assert oracle.returncode == 0, oracle.stderr.decode()

    # The checked-in mdtest expectation is a legacy 133-byte corpus artifact.
    # Tidyness is deterministic, so the installed Markdown.pl bytes are the
    # authoritative parity contract without mutating that fixture.
    assert expected_path.read_bytes() != oracle.stdout

    fast_actual = _run_acts(TIDYNESS_INPUT, through_act=4)
    assert isinstance(fast_actual, str)
    assert fast_actual.encode() == oracle.stdout

    release = subprocess.run(
        [str(BINARY)],
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=False,
    )

    assert fixture_name not in _IMPLEMENTED_FIXTURES
    assert release.returncode == 0, release.stderr.decode()
    assert release.stdout == oracle.stdout
