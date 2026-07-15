"""The ./shakedown wrapper must fail loudly when the play cannot parse."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent
WRAPPER = REPO / "shakedown"

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


def test_wrapper_default_release_path_uses_preprocess_then_spl_pipeline(
    tmp_path: Path,
) -> None:
    calls = tmp_path / "uv-calls.log"
    fake_uv = tmp_path / "uv"
    fake_uv.write_text(
        """#!/usr/bin/env python3
import os
import sys
from pathlib import Path

calls = Path(os.environ["UV_CALLS"])
calls.open("a", encoding="utf-8").write(" ".join(sys.argv[1:]) + "\\n")
args = sys.argv[1:]
stdin = sys.stdin.read()
if "scripts.release_entry" in args:
    sys.stdout.write("release-entry\\n")
    raise SystemExit(0)
if "scripts.preprocess_input" in args:
    sys.stdout.write(stdin)
    raise SystemExit(0)
if "shakespeare" in args and "run" in args:
    sys.stdout.write("pipeline-output\\n")
    raise SystemExit(0)
raise SystemExit(99)
""",
        encoding="utf-8",
    )
    fake_uv.chmod(0o755)

    result = subprocess.run(
        [str(WRAPPER)],
        input=b"sample\n",
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "UV_CALLS": str(calls),
        },
    )

    assert result.returncode == 0, result.stderr.decode()
    assert result.stdout == b"pipeline-output\n"
    logged = calls.read_text(encoding="utf-8").splitlines()
    assert len(logged) == 2
    assert any("python -m scripts.preprocess_input" in line for line in logged)
    assert any(f"shakespeare run {REPO / 'shakedown.spl'}" in line for line in logged)
    assert all("scripts.release_entry" not in line for line in logged)
