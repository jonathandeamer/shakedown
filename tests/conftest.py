import subprocess
from collections.abc import Callable
from typing import cast

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--real-wrapper",
        action="store_true",
        default=False,
        help="Disable in-process AST caching and run real subprocess shakedown wrapper",
    )


@pytest.fixture(autouse=True, scope="session")
def intercept_subprocess(pytestconfig: pytest.Config) -> None:
    if pytestconfig.getoption("--real-wrapper"):
        return

    original_run = cast(Callable[..., object], subprocess.run)

    def mocked_run(args: object, *p_args: object, **kwargs: object) -> object:
        # Skeleton check
        return original_run(args, *p_args, **kwargs)

    subprocess.run = mocked_run  # type: ignore[assignment]
