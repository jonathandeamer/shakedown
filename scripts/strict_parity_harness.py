"""Run ./shakedown vs. local Markdown.pl on each fixture."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_FIXTURES = Path.home() / "mdtest" / "Markdown.mdtest"
DEFAULT_ORACLE = Path.home() / "markdown" / "Markdown.pl"
DEFAULT_SHAKEDOWN = Path(__file__).parent.parent / "shakedown"


@dataclass(frozen=True)
class FixtureResult:
    name: str
    shakedown_bytes: int
    oracle_bytes: int
    byte_identical: bool
    first_diff_index: int | None


def run_one(executable: Path, input_bytes: bytes) -> bytes:
    if executable.suffix == ".pl" or executable.name.endswith("Markdown.pl"):
        argv = ["perl", str(executable)]
    else:
        argv = [str(executable)]
    result = subprocess.run(
        argv,
        input=input_bytes,
        capture_output=True,
        check=True,
    )
    return result.stdout


def first_diff(a: bytes, b: bytes) -> int | None:
    for i, (x, y) in enumerate(zip(a, b, strict=False)):
        if x != y:
            return i
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def compare(fixture: Path, shakedown: Path, oracle: Path) -> FixtureResult:
    input_bytes = fixture.read_bytes()
    sd = run_one(shakedown, input_bytes)
    or_ = run_one(oracle, input_bytes)
    return FixtureResult(
        name=fixture.stem,
        shakedown_bytes=len(sd),
        oracle_bytes=len(or_),
        byte_identical=(sd == or_),
        first_diff_index=first_diff(sd, or_),
    )


def render(results: list[FixtureResult]) -> str:
    lines = ["# Strict Shakedown-vs-Markdown.pl Parity", ""]
    for r in results:
        verdict = "yes" if r.byte_identical else "no"
        diff = "-" if r.first_diff_index is None else str(r.first_diff_index)
        lines.append(
            f"- {r.name}: byte-identical: {verdict} "
            f"(shakedown={r.shakedown_bytes}, oracle={r.oracle_bytes}, "
            f"first diff: {diff})"
        )
    mismatches = [r for r in results if not r.byte_identical]
    lines.append("")
    passed = len(results) - len(mismatches)
    lines.append(f"summary: {passed}/{len(results)} byte-identical")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shakedown", type=Path, default=DEFAULT_SHAKEDOWN)
    parser.add_argument("--markdown-pl", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--fixtures-dir", type=Path, default=DEFAULT_FIXTURES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixtures = sorted(args.fixtures_dir.glob("*.text"))
    if not fixtures:
        print(f"no fixtures in {args.fixtures_dir}", file=sys.stderr)
        return 2
    results = [compare(f, args.shakedown, args.markdown_pl) for f in fixtures]
    print(render(results))
    return 0 if all(r.byte_identical for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
