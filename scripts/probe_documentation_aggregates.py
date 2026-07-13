"""Probe script for early execution of Slice-5 Markdown Documentation aggregates.

Runs the two large fixtures through the IR interpreter and checks for crashes
or execution times exceeding 5 seconds.
"""

import sys
import time
from pathlib import Path

from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4

REPO = Path(__file__).parent.parent
FIXTURES_DIR = Path.home() / "mdtest" / "Markdown.mdtest"
TIMEOUT_LIMIT_SECONDS = 5.0


def interpret_ir(input_text: str) -> str:
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=500_000).state
    state = run_act(ACT2, state, step_limit=500_000).state
    state = run_act(ACT3, state, step_limit=500_000).state
    state = run_act(ACT4, state, step_limit=500_000).state
    return state.output_text()


def main() -> int:
    stems = ["Markdown Documentation - Basics", "Markdown Documentation - Syntax"]
    failures = 0
    for stem in stems:
        txt_path = FIXTURES_DIR / f"{stem}.text"
        if not txt_path.exists():
            print(f"Skipping {stem}: fixture not found", file=sys.stderr)
            continue

        input_text = txt_path.read_text(encoding="utf-8")
        print(f"Probing {stem} via IR Interpreter...")
        start = time.monotonic()
        try:
            output = interpret_ir(input_text)
            elapsed = time.monotonic() - start
            print(f"  IR finished in {elapsed:.3f}s (output size: {len(output)} chars)")
            if elapsed > TIMEOUT_LIMIT_SECONDS:
                print(
                    f"  ERROR: {stem} exceeded time limit of {TIMEOUT_LIMIT_SECONDS}s",
                    file=sys.stderr,
                )
                failures += 1
        except Exception as exc:
            print(f"  CRASH: {stem} failed in IR interpreter: {exc}", file=sys.stderr)
            failures += 1

    return 1 if failures > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
