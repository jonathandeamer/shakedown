import contextlib
import hashlib
import io
import os
import subprocess
import sys
from collections.abc import Callable, Generator
from pathlib import Path
from typing import cast

import pytest
from shakespearelang import Shakespeare
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
                        {"40-act4-emit.spl": root / "debug" / "40-act4-token-dump.spl"}
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
                temp_interpreter = Shakespeare(play_text)
                _AST_CACHE[cache_key] = temp_interpreter.parser.parse(play_text, "play")
            play_ast = _AST_CACHE[cache_key]

            input_data = kwargs.get("input", "")
            is_bytes = isinstance(input_data, bytes)
            input_str = (
                input_data.decode("utf-8", errors="replace")
                if is_bytes
                else input_data or ""
            )

            stdin_buf = io.StringIO(cast(str, input_str))
            stdout_buf = io.StringIO()
            stderr_buf = io.StringIO()
            exit_code = 0
            try:
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
                stderr_buf.write(f"SPL runtime error: {error}\n")
                exit_code = 1

            stdout_val = stdout_buf.getvalue()
            stderr_val = stderr_buf.getvalue()
            if is_bytes:
                stdout_res: str | bytes = stdout_val.encode("utf-8")
                stderr_res: str | bytes = stderr_val.encode("utf-8")
            else:
                stdout_res = stdout_val
                stderr_res = stderr_val

            return subprocess.CompletedProcess(
                args=args,
                returncode=exit_code,
                stdout=stdout_res,
                stderr=stderr_res,
            )

        return original_run(args, *p_args, **kwargs)

    subprocess.run = mocked_run  # type: ignore[assignment]
    try:
        yield
    finally:
        subprocess.run = original_run  # type: ignore[assignment]
