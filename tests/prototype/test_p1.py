"""Prototype 1 — walking skeleton: paragraphs + code spans."""

import subprocess

import pytest

from tests.prototype.conftest import FIXTURES, WRAPPER, normalize

pytestmark = pytest.mark.skip(
    reason="obsolete prototype scaffold; production roadmap uses ./shakedown"
)


def test_p1_walking_skeleton() -> None:
    input_md = (FIXTURES / "p1_input.md").read_text()
    expected = (FIXTURES / "p1_expected.html").read_text()

    result = subprocess.run(
        [str(WRAPPER)],
        input=input_md,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"./shakedown-dev exited {result.returncode}\nstderr:\n{result.stderr}"
    )

    assert normalize(result.stdout) == normalize(expected), (
        f"output mismatch\n--- expected\n{normalize(expected)}\n"
        f"+++ actual\n{normalize(result.stdout)}"
    )
