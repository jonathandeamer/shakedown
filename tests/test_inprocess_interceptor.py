from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from shakespearelang import Shakespeare
from tatsu.ast import AST

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


def test_repository_path_substring_does_not_trigger_interception(
    tmp_path: Path,
) -> None:
    fake_play = tmp_path / "override.spl"
    fake_play.write_text("this is not a valid play")
    misleading_dir = tmp_path / "contains-shakedown"
    misleading_dir.mkdir()
    python_link = misleading_dir / "python"
    python_link.symlink_to(sys.executable)

    result = subprocess.run(
        [str(python_link), "-c", "print('python subprocess')"],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "SHAKEDOWN_SPL": str(fake_play)},
    )

    assert result.returncode == 0
    assert result.stdout == "python subprocess\n"
    assert result.stderr == ""


def test_repeated_wrapper_calls_parse_each_play_hash_once(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    parse_calls = 0
    original_parse = Shakespeare.parse

    def counting_parse(self: Shakespeare, item: str, rule_name: str) -> AST:
        nonlocal parse_calls
        parse_calls += 1
        return original_parse(self, item, rule_name)

    monkeypatch.setattr(Shakespeare, "parse", counting_parse)
    play_path = tmp_path / "valid.spl"
    play_path.write_text(MINIMAL_VALID_PLAY)

    for _ in range(2):
        result = subprocess.run(
            [str(Path.cwd() / "shakedown")],
            input="",
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "SHAKEDOWN_SPL": str(play_path)},
        )

        assert result.returncode == 0

    assert parse_calls == 1
