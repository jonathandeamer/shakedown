from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from scripts.runtime_constants import DOCUMENTATION_STEP_LIMIT
from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SPL = REPO / "shakedown.spl"
_SPL_ERROR_RE = re.compile(rb"^SPL (runtime|parse) error:", re.MULTILINE)


def _trim_wrapper_output(text: str) -> str:
    text = re.sub(r"\n\n<p>\Z", "", text)
    text = re.sub(r"\n<p>\Z", "", text)
    return re.sub(r"<p>\Z", "", text)


def _run_release_ir(input_text: str) -> str:
    state = InterpreterState(input_text=input_text)
    for act in (ACT1, ACT2, ACT3, ACT4):
        state = run_act(act, state, step_limit=DOCUMENTATION_STEP_LIMIT).state
    return state.output_text()


def _run_spl(input_text: str, spl_path: Path) -> int:
    result = subprocess.run(
        [
            "uv",
            "run",
            "--directory",
            str(REPO),
            "shakespeare",
            "run",
            str(spl_path),
        ],
        input=input_text.encode(),
        capture_output=True,
        check=False,
    )
    sys.stderr.buffer.write(result.stderr)
    if result.returncode != 0:
        return result.returncode
    if _SPL_ERROR_RE.search(result.stderr):
        return 1
    sys.stdout.write(_trim_wrapper_output(result.stdout.decode()))
    return 0


def main() -> int:
    input_text = sys.stdin.read()
    spl_path = Path(os.environ.get("SHAKEDOWN_SPL", str(DEFAULT_SPL)))
    # Act I strip + Act III link/image resolution own Markdown transforms.
    if spl_path == DEFAULT_SPL:
        sys.stdout.write(_run_release_ir(input_text))
        return 0
    return _run_spl(input_text, spl_path)


if __name__ == "__main__":
    raise SystemExit(main())
