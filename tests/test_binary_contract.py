import os
from pathlib import Path


def test_repo_shakedown_entrypoint_exists_and_is_executable() -> None:
    binary = Path(__file__).parent.parent / "shakedown"

    assert binary.is_file(), f"missing repo entrypoint: {binary}"
    assert os.access(binary, os.X_OK), f"repo entrypoint is not executable: {binary}"
