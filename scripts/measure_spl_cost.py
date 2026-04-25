"""Measure shakespeare run cost for a given SPL file.

Runs the file N times sequentially (each run is a fresh subprocess, so each
invocation pays cold interpreter startup cost). Reports first-run and median.
Writes a text table to stdout suitable for direct paste into verification-plan.md.
"""

from __future__ import annotations

import argparse
import statistics
import subprocess
import time
from pathlib import Path


def time_run(path: Path, stdin: bytes | None) -> float:
    start = time.monotonic()
    result = subprocess.run(
        ["uv", "run", "shakespeare", "run", str(path)],
        input=stdin,
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - start
    if result.returncode != 0:
        stderr_text = result.stderr.decode(errors="replace")
        raise RuntimeError(f"{path} exited {result.returncode}: {stderr_text}")
    return elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument(
        "--stdin",
        type=Path,
        default=None,
        help="Optional stdin fixture to pipe into the run",
    )
    args = parser.parse_args()

    stdin_bytes: bytes | None = None
    if args.stdin is not None:
        stdin_bytes = args.stdin.read_bytes()

    times = [time_run(args.path, stdin_bytes) for _ in range(args.runs)]
    print(f"file: {args.path}")
    print(f"runs: {args.runs}")
    print(f"first: {times[0]:.3f}s")
    print(f"median: {statistics.median(times):.3f}s")
    print(f"all: {[f'{t:.3f}' for t in times]}")


if __name__ == "__main__":
    main()
