import contextlib
import hashlib
import io
import locale
import os
import subprocess
import sys
from collections.abc import Callable, Generator
from pathlib import Path
from typing import cast

import pytest
from shakespearelang import Shakespeare
from shakespearelang._parser import shakespeareParser
from tatsu.ast import AST

_AST_CACHE: dict[tuple[Path, str], AST] = {}
_WRAPPER_NAMES = {"shakedown", "shakedown-dev", "shakedown-debug"}
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


@pytest.fixture(autouse=True, scope="session")
def intercept_subprocess(pytestconfig: pytest.Config) -> Generator[None]:
    if pytestconfig.getoption("--real-wrapper"):
        yield
        return

    original_run = cast(Callable[..., object], subprocess.run)

    def mocked_run(args: _Command, *p_args: object, **kwargs: object) -> object:
        cmd = args[0] if isinstance(args, (list, tuple)) else args
        if isinstance(cmd, Path):
            cmd = str(cmd)

        wrapper_name = Path(cmd).name if isinstance(cmd, str) else None
        is_shakedown = wrapper_name in _WRAPPER_NAMES

        import inspect

        blacklist = {
            "test_wrapper_error_channel.py",
            "test_shakedown_run.py",
            "test_empty_input_contract.py",
        }
        is_blacklisted = any(
            any(name in frame.filename for name in blacklist)
            for frame in inspect.stack()
        )

        if is_shakedown and isinstance(cmd, str) and not is_blacklisted:
            capture_stdout = (
                bool(kwargs.get("capture_output"))
                or kwargs.get("stdout") == subprocess.PIPE
            )
            stderr_to_stdout = kwargs.get("stderr") == subprocess.STDOUT
            capture_stderr = (
                bool(kwargs.get("capture_output"))
                or kwargs.get("stderr") == subprocess.PIPE
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
                if wrapper_name in {"shakedown-dev", "shakedown-debug"}:
                    from scripts.assemble import assemble

                    root = Path(cmd).resolve().parent
                    debug = wrapper_name == "shakedown-debug"
                    assembled_path = (
                        root / ".cache" / "shakedown-debug.spl"
                        if debug
                        else root / "shakedown.spl"
                    )
                    assembled_path.parent.mkdir(exist_ok=True)
                    assemble(
                        src_dir=root / "src",
                        manifest=root / "src" / "manifest.toml",
                        output=assembled_path,
                        parse_check=False,
                        replace=(
                            {
                                "40-act4-emit.spl": (
                                    root / "debug" / "40-act4-token-dump.spl"
                                )
                            }
                            if debug
                            else None
                        ),
                    )

                env = cast(dict[str, str], kwargs.get("env", {}))
                env_spl = env.get("SHAKEDOWN_SPL") or os.environ.get("SHAKEDOWN_SPL")
                if env_spl:
                    spl_path = Path(env_spl)
                elif wrapper_name == "shakedown-debug":
                    spl_path = Path(cmd).parent / ".cache" / "shakedown-debug.spl"
                else:
                    spl_path = Path(cmd).parent / "shakedown.spl"

                if not spl_path.exists():
                    return original_run(args, *p_args, **kwargs)

                play_text = spl_path.read_text()
                content_hash = hashlib.sha256(play_text.encode()).hexdigest()
                cache_key = (spl_path, content_hash)
                if cache_key not in _AST_CACHE:
                    _AST_CACHE[cache_key] = shakespeareParser().parse(
                        play_text, rule_name="play"
                    )
                play_ast = _AST_CACHE[cache_key]

                input_data = kwargs.get("input", "")
                input_str = (
                    input_data.decode(encoding, errors=errors)
                    if isinstance(input_data, bytes)
                    else cast(str, input_data or "")
                )
                stdin_buf = io.StringIO(input_str)
                execution_started = True
                with (
                    contextlib.redirect_stdout(stdout_buf),
                    contextlib.redirect_stderr(stderr_buf),
                ):
                    old_stdin = sys.stdin
                    sys.stdin = stdin_buf
                    try:
                        interpreter = Shakespeare(play_ast)
                        interpreter.run()
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
                    stdout_val.encode(encoding, errors=errors)
                    if capture_stdout
                    else None
                )
                stderr_res = (
                    stderr_val.encode(encoding, errors=errors)
                    if capture_stderr
                    else None
                )

            result = subprocess.CompletedProcess(
                args=args,
                returncode=exit_code,
                stdout=stdout_res,
                stderr=stderr_res,
            )
            if exit_code and kwargs.get("check"):
                raise subprocess.CalledProcessError(
                    exit_code, args, output=stdout_res, stderr=stderr_res
                )
            return result

        return original_run(args, *p_args, **kwargs)

    subprocess.run = mocked_run  # type: ignore[assignment]
    try:
        yield
    finally:
        subprocess.run = original_run  # type: ignore[assignment]
