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
