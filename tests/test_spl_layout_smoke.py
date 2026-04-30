from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

SHAKESPEARE = shutil.which("shakespeare")
if SHAKESPEARE is None:
    fallback = Path.home() / ".local/bin/shakespeare"
    SHAKESPEARE = str(fallback) if fallback.is_file() else None


def _run_spl(tmp_path: Path, source: str) -> subprocess.CompletedProcess[str]:
    program = tmp_path / "layout.spl"
    program.write_text(source)
    assert SHAKESPEARE is not None
    return subprocess.run(
        [SHAKESPEARE, "run", str(program)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(SHAKESPEARE is None, reason="shakespeare executable not found")
def test_speaker_name_on_own_line_is_parser_accepted(tmp_path: Path) -> None:
    result = _run_spl(
        tmp_path,
        """The Layout Trial.

Romeo, a lad.
Juliet, a lass.

                    Act I: Wherein the test begins.

                    Scene I: The line is spoken.

[Enter Romeo and Juliet]

Romeo:
 You are as good as a cat.

Romeo:
 Speak your mind!

[Exeunt]
""",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "\x01"


@pytest.mark.skipif(SHAKESPEARE is None, reason="shakespeare executable not found")
def test_hanging_indent_inside_value_expression_is_parser_accepted(
    tmp_path: Path,
) -> None:
    result = _run_spl(
        tmp_path,
        """The Hanging Trial.

Romeo, a lad.
Juliet, a lass.

                    Act I: Wherein the test begins.

                    Scene I: The value is split.

[Enter Romeo and Juliet]

Romeo:
 You are as good as the sum of a big cat and
  a cat.

Romeo:
 Speak your mind!

[Exeunt]
""",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "\x03"
