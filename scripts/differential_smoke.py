"""All-fixture differential smoke report: parity entry vs. local Markdown.pl.

Runs every local mdtest `.text` input through both the fast parity entry
(``./shakedown-parity`` by default) and the oracle with a per-case timeout,
and reports byte-identical/mismatch/crash/timeout status, the first differing
byte, return codes, bounded stderr excerpts, and elapsed time for each.
Default mode is observational: it exits nonzero only on harness/configuration
failure. Pass ``--require NAME`` (repeatable) to make specific already-shipped
fixtures a gate. Override paths with ``SHAKEDOWN_MDTEST`` /
``SHAKEDOWN_MARKDOWN_PL``, or ``--shakedown ./shakedown`` for the public entry.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.paths import markdown_pl, mdtest_fixtures_dir  # noqa: E402

DEFAULT_FIXTURES = mdtest_fixtures_dir()
DEFAULT_ORACLE = markdown_pl()
DEFAULT_SHAKEDOWN = _REPO / "shakedown-parity"
DEFAULT_TIMEOUT_SECONDS = 30.0
STDERR_EXCERPT_LIMIT = 500


class CaseStatus(Enum):
    BYTE_IDENTICAL = "byte_identical"
    MISMATCH = "mismatch"
    SHAKEDOWN_CRASH = "shakedown_crash"
    ORACLE_CRASH = "oracle_crash"
    SHAKEDOWN_TIMEOUT = "shakedown_timeout"
    ORACLE_TIMEOUT = "oracle_timeout"


@dataclass(frozen=True)
class RunOutcome:
    """One subprocess invocation's observable result."""

    returncode: int | None
    stdout: bytes
    stderr_excerpt: str
    elapsed_seconds: float
    timed_out: bool


@dataclass(frozen=True)
class CaseResult:
    """Differential smoke result for a single fixture."""

    name: str
    status: CaseStatus
    first_diff_index: int | None
    shakedown_returncode: int | None
    oracle_returncode: int | None
    shakedown_stderr: str
    oracle_stderr: str
    shakedown_elapsed_seconds: float
    oracle_elapsed_seconds: float
    shakedown_bytes: int
    oracle_bytes: int

    def to_json(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


def bound_stderr(raw: bytes) -> str:
    """Decode and truncate a subprocess's stderr for reporting."""
    text = raw.decode("utf-8", errors="replace")
    if len(text) > STDERR_EXCERPT_LIMIT:
        return text[:STDERR_EXCERPT_LIMIT] + "...(truncated)"
    return text


def run_with_timeout(argv: list[str], input_bytes: bytes, timeout: float) -> RunOutcome:
    """Run one subprocess, capturing output and timing without raising."""
    start = time.monotonic()
    try:
        result = subprocess.run(
            argv,
            input=input_bytes,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else b""
        return RunOutcome(
            returncode=None,
            stdout=b"",
            stderr_excerpt=bound_stderr(stderr),
            elapsed_seconds=elapsed,
            timed_out=True,
        )
    elapsed = time.monotonic() - start
    return RunOutcome(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr_excerpt=bound_stderr(result.stderr),
        elapsed_seconds=elapsed,
        timed_out=False,
    )


def first_diff(a: bytes, b: bytes) -> int | None:
    """Return the index of the first differing byte, or None if identical."""
    for i, (x, y) in enumerate(zip(a, b, strict=False)):
        if x != y:
            return i
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def oracle_argv(oracle: Path) -> list[str]:
    """Build the argv for invoking the Perl oracle."""
    return ["perl", str(oracle)]


def shakedown_argv(shakedown: Path) -> list[str]:
    """Build the argv for invoking the shakedown binary under test."""
    return [str(shakedown)]


def run_case(
    fixture: Path, shakedown: Path, oracle: Path, timeout: float
) -> CaseResult:
    """Run one fixture through both implementations and classify the result."""
    input_bytes = fixture.read_bytes()
    sd = run_with_timeout(shakedown_argv(shakedown), input_bytes, timeout)
    or_ = run_with_timeout(oracle_argv(oracle), input_bytes, timeout)

    if sd.timed_out:
        status = CaseStatus.SHAKEDOWN_TIMEOUT
    elif or_.timed_out:
        status = CaseStatus.ORACLE_TIMEOUT
    elif sd.returncode != 0:
        status = CaseStatus.SHAKEDOWN_CRASH
    elif or_.returncode != 0:
        status = CaseStatus.ORACLE_CRASH
    elif sd.stdout == or_.stdout:
        status = CaseStatus.BYTE_IDENTICAL
    else:
        status = CaseStatus.MISMATCH

    diff_index = None
    if status in (CaseStatus.BYTE_IDENTICAL, CaseStatus.MISMATCH):
        diff_index = first_diff(sd.stdout, or_.stdout)

    return CaseResult(
        name=fixture.stem,
        status=status,
        first_diff_index=diff_index,
        shakedown_returncode=sd.returncode,
        oracle_returncode=or_.returncode,
        shakedown_stderr=sd.stderr_excerpt,
        oracle_stderr=or_.stderr_excerpt,
        shakedown_elapsed_seconds=sd.elapsed_seconds,
        oracle_elapsed_seconds=or_.elapsed_seconds,
        shakedown_bytes=len(sd.stdout),
        oracle_bytes=len(or_.stdout),
    )


def collect_fixtures(fixtures_dir: Path) -> list[Path]:
    """Return every `.text` fixture in the directory, sorted by name."""
    return sorted(fixtures_dir.glob("*.text"))


def render_markdown(results: list[CaseResult]) -> str:
    """Render the differential smoke report as Markdown."""
    lines = [
        "# Differential Smoke Report",
        "",
        "Generated by `uv run python scripts/differential_smoke.py`. "
        "Observational unless run with `--require`.",
        "",
        "| Fixture | Status | First diff | shakedown rc | oracle rc | "
        "shakedown s | oracle s |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        diff = "-" if r.first_diff_index is None else str(r.first_diff_index)
        lines.append(
            f"| {r.name} | {r.status.value} | {diff} | "
            f"{r.shakedown_returncode} | {r.oracle_returncode} | "
            f"{r.shakedown_elapsed_seconds:.3f} | {r.oracle_elapsed_seconds:.3f} |"
        )

    non_identical = [r for r in results if r.status != CaseStatus.BYTE_IDENTICAL]
    lines.append("")
    lines.append(
        f"summary: {len(results) - len(non_identical)}/{len(results)} byte-identical"
    )

    if non_identical:
        lines.extend(["", "## Non-identical cases", ""])
        for r in non_identical:
            lines.extend(
                [
                    f"### {r.name}",
                    "",
                    f"- status: {r.status.value}",
                    f"- first diff index: {r.first_diff_index}",
                    f"- shakedown stderr: `{r.shakedown_stderr}`",
                    f"- oracle stderr: `{r.oracle_stderr}`",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def render_json(results: list[CaseResult]) -> str:
    """Render the differential smoke report as JSON."""
    return json.dumps([r.to_json() for r in results], indent=2, sort_keys=True)


def resolve_require_name(fixtures_dir: Path, name: str) -> Path:
    """Resolve a `--require` fixture name to its `.text` path.

    Follows the strict parity harness's selection convention: the suffix is
    optional and defaults to `.text`.
    """
    path = fixtures_dir / name
    if path.suffix != ".text":
        path = path.with_suffix(".text")
    if not path.exists():
        raise FileNotFoundError(f"required fixture not found in {fixtures_dir}: {name}")
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shakedown", type=Path, default=DEFAULT_SHAKEDOWN)
    parser.add_argument("--markdown-pl", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--fixtures-dir", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument(
        "--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional Markdown report path; stdout is used when omitted",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        type=Path,
        default=None,
        help="Optional path to also write the JSON result records",
    )
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        help="Fixture name that must be byte-identical (repeatable)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the differential smoke CLI."""
    args = parse_args(argv)

    if not args.fixtures_dir.is_dir():
        print(f"fixtures directory not found: {args.fixtures_dir}", file=sys.stderr)
        return 2
    if not args.markdown_pl.exists():
        print(f"oracle not found: {args.markdown_pl}", file=sys.stderr)
        return 2
    if not args.shakedown.exists():
        print(f"shakedown binary not found: {args.shakedown}", file=sys.stderr)
        return 2

    fixtures = collect_fixtures(args.fixtures_dir)
    if not fixtures:
        print(f"no fixtures in {args.fixtures_dir}", file=sys.stderr)
        return 2

    try:
        required_paths = {
            name: resolve_require_name(args.fixtures_dir, name) for name in args.require
        }
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    results = [
        run_case(f, args.shakedown, args.markdown_pl, args.timeout_seconds)
        for f in fixtures
    ]

    report = render_markdown(results)
    if args.output is None:
        print(report, end="")
    else:
        args.output.write_text(report, encoding="utf-8")

    if args.json_output is not None:
        args.json_output.write_text(render_json(results), encoding="utf-8")

    results_by_name = {r.name: r for r in results}
    failed_required = [
        name
        for name, path in required_paths.items()
        if results_by_name[path.stem].status != CaseStatus.BYTE_IDENTICAL
    ]
    if failed_required:
        print(
            f"required fixture(s) not byte-identical: {', '.join(failed_required)}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
