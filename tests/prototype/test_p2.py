"""Prototype 2 — inline stressor: emphasis, backtracking, emphasis-in-blockquote."""

import subprocess

import pytest

from tests.prototype.conftest import FIXTURES, WRAPPER, normalize


def _run_shakedown_dev(input_md: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [str(WRAPPER)],
        input=input_md,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


@pytest.mark.parametrize(
    "name",
    ["p2_emphasis", "p2_backtrack", "p2_blockquote"],
)
def test_p2_fixture(name: str) -> None:
    input_md = (FIXTURES / f"{name}_input.md").read_text()
    expected = (FIXTURES / f"{name}_expected.html").read_text()

    rc, out, err = _run_shakedown_dev(input_md)
    assert rc == 0, f"./shakedown-dev exited {rc}\nstderr:\n{err}"

    assert normalize(out) == normalize(expected), (
        f"{name} mismatch\n--- expected\n{normalize(expected)}\n"
        f"+++ actual\n{normalize(out)}"
    )
