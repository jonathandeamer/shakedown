from __future__ import annotations

import contextlib
import hashlib
import inspect
import io
import locale
import os
import subprocess
import sys
from collections.abc import Callable, Generator
from contextvars import ContextVar
from pathlib import Path
from typing import cast

import pytest
from shakespearelang import Shakespeare
from shakespearelang._parser import shakespeareParser
from tatsu.ast import AST

_AST_CACHE: dict[tuple[Path, str], AST] = {}
_BYPASS_INTERCEPTION: ContextVar[bool] = ContextVar(
    "bypass_subprocess_interception", default=False
)
_WRAPPER_NAMES = {"shakedown", "shakedown-dev", "shakedown-debug"}
_BLACKLIST = {
    "test_wrapper_error_channel.py",
    "test_shakedown_run.py",
    "test_empty_input_contract.py",
}
_Command = (
    str | bytes | Path | list[str | bytes | Path] | tuple[str | bytes | Path, ...]
)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--real-wrapper",
        action="store_true",
        default=False,
        help="Disable in-process AST caching and run real subprocess shakedown wrapper",
    )


def _command_path(args: _Command) -> tuple[str, str] | None:
    cmd = args[0] if isinstance(args, (list, tuple)) else args
    if isinstance(cmd, Path):
        cmd = str(cmd)
    if not isinstance(cmd, str):
        return None
    wrapper_name = Path(cmd).name
    if wrapper_name not in _WRAPPER_NAMES or not Path(cmd).exists():
        return None
    return cmd, wrapper_name


def _is_blacklisted() -> bool:
    return any(
        any(name in frame.filename for name in _BLACKLIST) for frame in inspect.stack()
    )


def _supports_in_process_run(kwargs: dict[str, object]) -> bool:
    return (
        "input" in kwargs
        and kwargs.get("cwd") is None
        and kwargs.get("timeout") is None
        and "stdin" not in kwargs
        and not kwargs.get("shell")
        and kwargs.get("stdout") != subprocess.DEVNULL
        and kwargs.get("stderr") != subprocess.DEVNULL
        and ("env" not in kwargs or kwargs["env"] is not None)
    )


def _supports_in_process_popen(kwargs: dict[str, object]) -> bool:
    return (
        kwargs.get("stdin") == subprocess.PIPE
        and kwargs.get("stdout") == subprocess.PIPE
        and kwargs.get("stderr") == subprocess.PIPE
        and kwargs.get("cwd") is None
        and not kwargs.get("shell")
        and ("env" not in kwargs or kwargs["env"] is not None)
    )


def _target_play(cmd: str, wrapper_name: str, kwargs: dict[str, object]) -> Path:
    root = Path(cmd).resolve().parent
    if wrapper_name in {"shakedown-dev", "shakedown-debug"}:
        from scripts.assemble import assemble

        debug = wrapper_name == "shakedown-debug"
        assembled_path = (
            root / ".cache" / "shakedown-debug.spl" if debug else root / "shakedown.spl"
        )
        assembled_path.parent.mkdir(exist_ok=True)
        assemble(
            src_dir=root / "src",
            manifest=root / "src" / "manifest.toml",
            output=assembled_path,
            parse_check=False,
            replace=(
                {"40-act4-emit.spl": root / "debug" / "40-act4-token-dump.spl"}
                if debug
                else None
            ),
        )
        return assembled_path

    env = cast(dict[str, str] | None, kwargs.get("env"))
    env_spl = (
        env.get("SHAKEDOWN_SPL") if env is not None else os.environ.get("SHAKEDOWN_SPL")
    )
    return Path(env_spl) if env_spl else root / "shakedown.spl"


def _run_in_process(
    args: _Command,
    cmd: str,
    wrapper_name: str,
    kwargs: dict[str, object],
    spl_path: Path | None = None,
) -> subprocess.CompletedProcess[str | bytes | None]:
    capture_stdout = (
        bool(kwargs.get("capture_output")) or kwargs.get("stdout") == subprocess.PIPE
    )
    stderr_to_stdout = kwargs.get("stderr") == subprocess.STDOUT
    capture_stderr = (
        bool(kwargs.get("capture_output")) or kwargs.get("stderr") == subprocess.PIPE
    ) and not stderr_to_stdout
    text_mode = bool(
        kwargs.get("text")
        or kwargs.get("universal_newlines")
        or kwargs.get("encoding")
        or kwargs.get("errors")
    )
    encoding = cast(str | None, kwargs.get("encoding")) or locale.getencoding()
    errors = cast(str | None, kwargs.get("errors")) or "strict"
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    execution_started = False
    try:
        spl_path = spl_path or _target_play(cmd, wrapper_name, kwargs)
        if not spl_path.exists():
            raise FileNotFoundError(spl_path)
        play_text = spl_path.read_text()
        content_hash = hashlib.sha256(play_text.encode()).hexdigest()
        cache_key = (spl_path, content_hash)
        if cache_key not in _AST_CACHE:
            _AST_CACHE[cache_key] = shakespeareParser().parse(
                play_text, rule_name="play"
            )
        input_data = kwargs["input"]
        input_str = (
            input_data.decode(encoding, errors=errors)
            if isinstance(input_data, bytes)
            else cast(str, input_data or "")
        )
        execution_started = True
        with (
            contextlib.redirect_stdout(stdout_buf),
            contextlib.redirect_stderr(stderr_buf),
        ):
            old_stdin = sys.stdin
            sys.stdin = io.StringIO(input_str)
            try:
                Shakespeare(_AST_CACHE[cache_key]).run()
            finally:
                sys.stdin = old_stdin
    except Exception as error:
        phase = "runtime" if execution_started else "preparation"
        stderr_buf.write(f"SPL {phase} error: {error}\n")
        exit_code = 1

    stdout_val = stdout_buf.getvalue()
    stderr_val = stderr_buf.getvalue()
    if stderr_to_stdout:
        stdout_val += stderr_val
        stderr_val = ""
    if not capture_stdout:
        sys.stdout.write(stdout_val)
    if not capture_stderr:
        sys.stderr.write(stderr_val)
    if text_mode:
        stdout_res: str | bytes | None = stdout_val if capture_stdout else None
        stderr_res: str | bytes | None = stderr_val if capture_stderr else None
    else:
        stdout_res = (
            stdout_val.encode(encoding, errors=errors) if capture_stdout else None
        )
        stderr_res = (
            stderr_val.encode(encoding, errors=errors) if capture_stderr else None
        )
    return subprocess.CompletedProcess(args, exit_code, stdout_res, stderr_res)


class _InProcessPopen:
    def __init__(
        self,
        args: _Command,
        cmd: str,
        wrapper_name: str,
        kwargs: dict[str, object],
        spl_path: Path | None,
    ) -> None:
        self.args = args
        self._cmd = cmd
        self._wrapper_name = wrapper_name
        self._kwargs = kwargs
        self._spl_path = spl_path
        self.returncode: int | None = None

    def communicate(
        self, input: str | bytes | None = None, timeout: float | None = None
    ) -> tuple[str | bytes | None, str | bytes | None]:
        if self.returncode is not None:
            raise ValueError("Cannot communicate with a completed process")
        result = _run_in_process(
            self.args,
            self._cmd,
            self._wrapper_name,
            {**self._kwargs, "input": input},
            self._spl_path,
        )
        self.returncode = result.returncode
        return result.stdout, result.stderr

    def poll(self) -> int | None:
        return self.returncode

    def wait(self, timeout: float | None = None) -> int:
        if self.returncode is None:
            self.communicate(timeout=timeout)
        return cast(int, self.returncode)

    def __enter__(self) -> _InProcessPopen:
        return self

    def __exit__(self, *args: object) -> None:
        if self.returncode is None:
            self.communicate()


@pytest.fixture(autouse=True, scope="session")
def intercept_subprocess(pytestconfig: pytest.Config) -> Generator[None]:
    if pytestconfig.getoption("--real-wrapper"):
        yield
        return

    original_run = cast(Callable[..., object], subprocess.run)
    original_popen = cast(Callable[..., object], subprocess.Popen)

    def run_without_interception(
        args: _Command, p_args: tuple[object, ...], kwargs: dict[str, object]
    ) -> object:
        token = _BYPASS_INTERCEPTION.set(True)
        try:
            return original_run(args, *p_args, **kwargs)
        finally:
            _BYPASS_INTERCEPTION.reset(token)

    def mocked_run(args: _Command, *p_args: object, **kwargs: object) -> object:
        command = _command_path(args)
        run_kwargs = dict(kwargs)
        if (
            command is not None
            and not _is_blacklisted()
            and _supports_in_process_run(run_kwargs)
        ):
            try:
                spl_path = _target_play(*command, run_kwargs)
            except Exception:
                return _run_in_process(args, *command, run_kwargs)
            if not spl_path.exists():
                return run_without_interception(args, p_args, kwargs)
            result = _run_in_process(args, *command, run_kwargs, spl_path)
            if result.returncode and run_kwargs.get("check"):
                raise subprocess.CalledProcessError(
                    result.returncode, args, output=result.stdout, stderr=result.stderr
                )
            return result
        return run_without_interception(args, p_args, kwargs)

    def mocked_popen(args: _Command, *p_args: object, **kwargs: object) -> object:
        if _BYPASS_INTERCEPTION.get():
            return original_popen(args, *p_args, **kwargs)
        command = _command_path(args)
        popen_kwargs = dict(kwargs)
        if (
            command is not None
            and not p_args
            and not _is_blacklisted()
            and _supports_in_process_popen(popen_kwargs)
        ):
            try:
                spl_path = _target_play(*command, popen_kwargs)
            except Exception:
                return _InProcessPopen(args, *command, popen_kwargs, None)
            if spl_path.exists():
                return _InProcessPopen(args, *command, popen_kwargs, spl_path)
        return original_popen(args, *p_args, **kwargs)

    subprocess.run = mocked_run  # type: ignore[assignment]
    subprocess.Popen = mocked_popen  # type: ignore[assignment]
    try:
        yield
    finally:
        subprocess.run = original_run  # type: ignore[assignment]
        subprocess.Popen = original_popen  # type: ignore[assignment]
