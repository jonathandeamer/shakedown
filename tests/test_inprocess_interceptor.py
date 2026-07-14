from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from shakespearelang._parser import shakespeareParser
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
    original_parse = shakespeareParser.parse

    def counting_parse(
        self: shakespeareParser, item: str, rule_name: str = "start"
    ) -> AST:
        nonlocal parse_calls
        parse_calls += 1
        return original_parse(self, item, rule_name=rule_name)

    monkeypatch.setattr(shakespeareParser, "parse", counting_parse)
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


def test_invalid_override_play_returns_captured_preparation_error(
    tmp_path: Path,
) -> None:
    invalid_play = tmp_path / "invalid.spl"
    invalid_play.write_text("this is not a valid play")

    result = subprocess.run(
        [str(Path.cwd() / "shakedown")],
        input="",
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "SHAKEDOWN_SPL": str(invalid_play)},
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr is not None
    assert "SPL preparation error:" in result.stderr


def test_nonexistent_override_falls_through_to_real_wrapper(tmp_path: Path) -> None:
    missing_play = tmp_path / "missing.spl"

    result = subprocess.run(
        [str(Path.cwd() / "shakedown")],
        input="",
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "SHAKEDOWN_SPL": str(missing_play)},
    )

    assert result.returncode != 0
    assert result.stderr is not None
    assert "SPL preparation error:" not in result.stderr
    assert "FileNotFoundError" in result.stderr


@pytest.mark.parametrize(
    ("text_mode", "expected_error"),
    [(True, "SPL preparation error:"), (False, b"SPL preparation error:")],
)
def test_stderr_stdout_merges_interceptor_errors_into_stdout(
    tmp_path: Path, text_mode: bool, expected_error: str | bytes
) -> None:
    invalid_play = tmp_path / "invalid.spl"
    invalid_play.write_text("this is not a valid play")

    result = subprocess.run(
        [str(Path.cwd() / "shakedown")],
        input="",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=text_mode,
        check=False,
        env={**os.environ, "SHAKEDOWN_SPL": str(invalid_play)},
    )

    assert result.returncode == 1
    assert result.stdout is not None
    assert expected_error in result.stdout
    assert result.stderr is None


def test_captured_result_type_follows_subprocess_text_mode(tmp_path: Path) -> None:
    play_path = tmp_path / "valid.spl"
    play_path.write_text(MINIMAL_VALID_PLAY)

    text_result = subprocess.run(
        [str(Path.cwd() / "shakedown")],
        input=b"",
        check=False,
        env={**os.environ, "SHAKEDOWN_SPL": str(play_path)},
        capture_output=True,
        text=True,
    )
    bytes_result = subprocess.run(
        [str(Path.cwd() / "shakedown")],
        input="",
        check=False,
        env={**os.environ, "SHAKEDOWN_SPL": str(play_path)},
        capture_output=True,
    )

    assert isinstance(text_result.stdout, str)
    assert isinstance(text_result.stderr, str)
    assert isinstance(bytes_result.stdout, bytes)
    assert isinstance(bytes_result.stderr, bytes)


def test_uncaptured_wrapper_result_does_not_fabricate_output(tmp_path: Path) -> None:
    play_path = tmp_path / "valid.spl"
    play_path.write_text(MINIMAL_VALID_PLAY)

    result = subprocess.run(
        [str(Path.cwd() / "shakedown")],
        input="",
        text=True,
        check=False,
        env={**os.environ, "SHAKEDOWN_SPL": str(play_path)},
    )

    assert result.returncode == 0
    assert result.stdout is None
    assert result.stderr is None
