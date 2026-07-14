from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Literal, cast

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


def test_popen_wrapper_reuses_cached_ast_and_preserves_pipe_output(
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
        process = subprocess.Popen(
            [str(Path.cwd() / "shakedown")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "SHAKEDOWN_SPL": str(play_path)},
        )
        stdout, stderr = process.communicate("")

        assert process.returncode == 0
        assert stdout == ""
        assert stderr == ""

    assert parse_calls == 1


def test_popen_wrapper_communicate_timeout_returns_completed_result(
    tmp_path: Path,
) -> None:
    play_path = tmp_path / "valid.spl"
    play_path.write_text(MINIMAL_VALID_PLAY)

    process = subprocess.Popen(
        [str(Path.cwd() / "shakedown")],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "SHAKEDOWN_SPL": str(play_path)},
    )

    stdout, stderr = process.communicate("", timeout=1)

    assert process.returncode == 0
    assert stdout == ""
    assert stderr == ""


def test_popen_wait_after_communicate_returns_existing_returncode(
    tmp_path: Path,
) -> None:
    play_path = tmp_path / "valid.spl"
    play_path.write_text(MINIMAL_VALID_PLAY)

    process = subprocess.Popen(
        [str(Path.cwd() / "shakedown")],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "SHAKEDOWN_SPL": str(play_path)},
    )

    process.communicate("")

    assert process.wait() == 0


def _delegating_wrapper(tmp_path: Path) -> Path:
    marker = tmp_path / "delegated"
    wrapper = tmp_path / "shakedown"
    wrapper.write_text(f"#!/usr/bin/env bash\necho delegated\ntouch {marker}\n")
    wrapper.chmod(0o755)
    (tmp_path / "shakedown.spl").write_text(MINIMAL_VALID_PLAY)
    return wrapper


@pytest.mark.parametrize(
    ("mode", "kwargs"),
    [
        ("cwd", {"cwd": "."}),
        ("stdin", {"stdin": subprocess.DEVNULL}),
        ("shell", {"shell": True}),
        ("env_none", {"env": None}),
        ("devnull", {"stdout": subprocess.DEVNULL}),
    ],
)
def test_unsupported_run_semantics_delegate_to_real_wrapper(
    tmp_path: Path,
    mode: Literal["cwd", "stdin", "shell", "env_none", "devnull"],
    kwargs: dict[str, object],
) -> None:
    wrapper = _delegating_wrapper(tmp_path)
    marker = tmp_path / "delegated"
    command: str | list[str] = [str(wrapper)]
    if mode == "cwd":
        kwargs["cwd"] = tmp_path
    if mode == "shell":
        command = str(wrapper)
    if mode != "devnull":
        kwargs.update(capture_output=True, text=True)

    # The parameter table intentionally exercises incompatible subprocess APIs.
    run = cast(Callable[..., subprocess.CompletedProcess[str]], subprocess.run)
    result = run(command, check=False, **kwargs)

    assert result.returncode == 0
    assert marker.exists()
    if mode != "devnull":
        assert result.stdout == "delegated\n"
        assert result.stderr == ""


def test_run_timeout_fallback_bypasses_in_process_popen(tmp_path: Path) -> None:
    wrapper = _delegating_wrapper(tmp_path)
    marker = tmp_path / "delegated"

    result = subprocess.run(
        [str(wrapper)],
        input="",
        capture_output=True,
        text=True,
        timeout=1,
        check=False,
    )

    assert result.returncode == 0
    assert marker.exists()
    assert result.stdout == "delegated\n"
    assert result.stderr == ""


def test_missing_wrapper_path_delegates_to_subprocess() -> None:
    with pytest.raises(FileNotFoundError):
        subprocess.run(
            [str(Path.cwd() / "does-not-exist" / "shakedown")],
            input="",
            capture_output=True,
            text=True,
            check=False,
            env=os.environ.copy(),
        )


@pytest.mark.parametrize("wrapper_name", ["shakedown-dev", "shakedown-debug"])
def test_dev_and_debug_ignore_external_shakedown_spl(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    wrapper_name: str,
) -> None:
    from scripts import assemble as assemble_module

    wrapper = tmp_path / wrapper_name
    wrapper.write_text("#!/usr/bin/env bash\nexit 99\n")
    wrapper.chmod(0o755)
    invalid_override = tmp_path / "invalid-override.spl"
    invalid_override.write_text("this is not a valid play")

    def write_assembled_play(**kwargs: object) -> None:
        cast(Path, kwargs["output"]).write_text(MINIMAL_VALID_PLAY)

    monkeypatch.setattr(assemble_module, "assemble", write_assembled_play)

    result = subprocess.run(
        [str(wrapper)],
        input="",
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "SHAKEDOWN_SPL": str(invalid_override)},
    )

    assert result.returncode == 0
    assert result.stderr == ""


@pytest.mark.parametrize("wrapper_name", ["shakedown-dev", "shakedown-debug"])
def test_dev_and_debug_assemble_failure_returns_captured_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    wrapper_name: str,
) -> None:
    from scripts import assemble as assemble_module

    wrapper = tmp_path / wrapper_name
    wrapper.write_text("#!/usr/bin/env bash\nexit 99\n")
    wrapper.chmod(0o755)

    def fail_assemble(**kwargs: object) -> None:
        raise RuntimeError("assemble failed")

    monkeypatch.setattr(assemble_module, "assemble", fail_assemble)

    result = subprocess.run(
        [str(wrapper)],
        input="",
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr is not None
    assert "SPL preparation error: assemble failed" in result.stderr
