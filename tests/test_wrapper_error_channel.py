"""The ./shakedown wrapper must fail loudly when the play cannot parse."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from scripts.paths import mdtest_fixtures_dir
from tests.test_mdtest import _interpret_ir

REPO = Path(__file__).parent.parent
WRAPPER = REPO / "shakedown"
FIXTURES_DIR = mdtest_fixtures_dir()

MINIMAL_VALID_PLAY = """\
A quiet probe.

Romeo, a probe.
Juliet, a probe.

                    Act I: The probe.

                    Scene I: The probe.

[Enter Romeo and Juliet]

Romeo:
 You are as fair as nothing.

[Exeunt]
"""


def _run_wrapper(spl_path: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(WRAPPER)],
        input=b"",
        capture_output=True,
        env={**os.environ, "SHAKEDOWN_SPL": str(spl_path)},
        check=False,
    )


def test_wrapper_fails_on_parse_error(tmp_path: Path) -> None:
    broken = tmp_path / "broken.spl"
    broken.write_text("this is not a play\n")
    result = _run_wrapper(broken)
    assert result.returncode != 0
    assert b"SPL parse error" in result.stderr
    assert result.stdout == b""


def test_wrapper_succeeds_on_valid_play(tmp_path: Path) -> None:
    valid = tmp_path / "valid.spl"
    valid.write_text(MINIMAL_VALID_PLAY)
    result = _run_wrapper(valid)
    assert result.returncode == 0, result.stderr.decode()


MINIMAL_RUNTIME_ERROR_PLAY = """\
A hungry probe.

Romeo, a probe.
Juliet, a probe.

                    Act I: The probe.

                    Scene I: The probe.

[Enter Romeo and Juliet]

Romeo:
 Recall your empty larder.

[Exeunt]
"""


def test_wrapper_fails_on_runtime_error(tmp_path: Path) -> None:
    erroring = tmp_path / "runtime_error.spl"
    erroring.write_text(MINIMAL_RUNTIME_ERROR_PLAY)
    result = _run_wrapper(erroring)
    assert result.returncode != 0
    assert b"SPL runtime error:" in result.stderr


def test_wrapper_prefers_shakespeare_on_path(tmp_path: Path) -> None:
    fake_shakespeare = tmp_path / "shakespeare"
    fake_shakespeare.write_text(
        """#!/usr/bin/env python3
import sys
if len(sys.argv) >= 2 and sys.argv[1] == "run":
    sys.stdout.write("path-shakespeare\\n")
    raise SystemExit(0)
raise SystemExit(99)
""",
        encoding="utf-8",
    )
    fake_shakespeare.chmod(0o755)
    fake_uv = tmp_path / "uv"
    fake_uv.write_text("#!/bin/sh\nexit 98\n", encoding="utf-8")
    fake_uv.chmod(0o755)

    result = subprocess.run(
        [str(WRAPPER)],
        input=b"sample\n",
        capture_output=True,
        check=False,
        env={**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}"},
    )

    assert result.returncode == 0, result.stderr.decode()
    assert result.stdout == b"path-shakespeare\n"


def test_wrapper_falls_back_to_uv_when_shakespeare_missing(
    tmp_path: Path,
) -> None:
    calls = tmp_path / "uv-calls.log"
    fake_uv = tmp_path / "uv"
    fake_uv.write_text(
        """#!/usr/bin/env python3
import os
import sys

calls = __import__("pathlib").Path(os.environ["UV_CALLS"])
calls.open("a", encoding="utf-8").write(" ".join(sys.argv[1:]) + "\\n")
args = sys.argv[1:]
if "shakespeare" in args and "run" in args:
    sys.stdout.write("uv-shakespeare\\n")
    raise SystemExit(0)
raise SystemExit(99)
""",
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)

    # Prefer fake bin over the host, but keep /usr/bin for env/bash; omit any
    # host `shakespeare` by not appending the full user PATH.
    result = subprocess.run(
        [str(WRAPPER)],
        input=b"sample\n",
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
            "UV_CALLS": str(calls),
        },
    )

    assert result.returncode == 0, result.stderr.decode()
    assert result.stdout == b"uv-shakespeare\n"
    logged = calls.read_text(encoding="utf-8").splitlines()
    expected_cmd = f"run --directory {REPO} shakespeare run {REPO / 'shakedown.spl'}"
    assert logged == [expected_cmd]


def test_parity_entry_finishes_under_capture_output_timeout() -> None:
    """Fast IR parity path (not the public shakespeare entry) stays quick."""
    fixture = FIXTURES_DIR / "Amps and angle encoding.text"
    expected = _interpret_ir(fixture.read_text()).encode()
    parity = REPO / "shakedown-parity"

    result = subprocess.run(
        [str(parity)],
        input=fixture.read_bytes(),
        capture_output=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0, result.stderr.decode()
    assert result.stdout == expected
