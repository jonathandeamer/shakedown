"""Audit local Markdown.pl output against Markdown.mdtest expected files."""

from __future__ import annotations

import argparse
import difflib
import subprocess
from dataclasses import dataclass
from pathlib import Path

DEFAULT_FIXTURES_DIR = Path.home() / "mdtest" / "Markdown.mdtest"
DEFAULT_MARKDOWN_PL = Path.home() / "markdown" / "Markdown.pl"


@dataclass(frozen=True)
class FixtureAudit:
    """Comparison result for one Markdown.mdtest fixture."""

    name: str
    input_path: Path
    expected_path: Path
    raw_equal: bool
    normalized_equal: bool
    expected_bytes: int
    oracle_bytes: int
    first_diff_index: int | None
    expected_byte: int | None
    oracle_byte: int | None
    diff: str


def normalize_contract(text: str) -> str:
    """Match tests/test_mdtest.py's whitespace normalization."""
    lines = text.split("\n")
    out: list[str] = []
    previous_blank = False
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            if not previous_blank:
                out.append("")
            previous_blank = True
        else:
            out.append(stripped)
            previous_blank = False
    return "\n".join(out).strip()


def expected_path_for(text_path: Path) -> Path:
    """Return the preferred expected-output file for a fixture input."""
    xhtml = text_path.with_suffix(".xhtml")
    html = text_path.with_suffix(".html")
    if xhtml.exists():
        return xhtml
    if html.exists():
        return html
    raise FileNotFoundError(f"No .xhtml or .html expected output for {text_path}")


def first_byte_diff(
    left: bytes, right: bytes
) -> tuple[int, int | None, int | None] | None:
    """Return first differing byte index and values, or None if byte-identical."""
    for index, (left_byte, right_byte) in enumerate(zip(left, right, strict=False)):
        if left_byte != right_byte:
            return index, left_byte, right_byte
    if len(left) != len(right):
        index = min(len(left), len(right))
        left_byte = left[index] if index < len(left) else None
        right_byte = right[index] if index < len(right) else None
        return index, left_byte, right_byte
    return None


def unified_text_diff(expected_path: Path, expected: bytes, oracle: bytes) -> str:
    """Render a unified text diff for human audit notes."""
    expected_text = expected.decode("utf-8")
    oracle_text = oracle.decode("utf-8")
    return "".join(
        difflib.unified_diff(
            expected_text.splitlines(keepends=True),
            oracle_text.splitlines(keepends=True),
            fromfile=str(expected_path),
            tofile="local Markdown.pl",
        )
    )


def run_markdown_pl(markdown_pl: Path, input_bytes: bytes) -> bytes:
    """Run local Markdown.pl for one input buffer."""
    result = subprocess.run(
        ["perl", str(markdown_pl)],
        input=input_bytes,
        capture_output=True,
        check=True,
    )
    return result.stdout


def audit_fixture(text_path: Path, markdown_pl: Path) -> FixtureAudit:
    """Audit one fixture against local Markdown.pl."""
    expected_path = expected_path_for(text_path)
    input_bytes = text_path.read_bytes()
    expected = expected_path.read_bytes()
    oracle = run_markdown_pl(markdown_pl, input_bytes)

    raw_equal = expected == oracle
    expected_text = expected.decode("utf-8")
    oracle_text = oracle.decode("utf-8")
    normalized_equal = normalize_contract(expected_text) == normalize_contract(
        oracle_text
    )
    diff_info = first_byte_diff(expected, oracle)
    if diff_info is None:
        first_diff_index = None
        expected_byte = None
        oracle_byte = None
    else:
        first_diff_index, expected_byte, oracle_byte = diff_info

    return FixtureAudit(
        name=text_path.stem,
        input_path=text_path,
        expected_path=expected_path,
        raw_equal=raw_equal,
        normalized_equal=normalized_equal,
        expected_bytes=len(expected),
        oracle_bytes=len(oracle),
        first_diff_index=first_diff_index,
        expected_byte=expected_byte,
        oracle_byte=oracle_byte,
        diff="" if raw_equal else unified_text_diff(expected_path, expected, oracle),
    )


def collect_audits(fixtures_dir: Path, markdown_pl: Path) -> list[FixtureAudit]:
    """Audit every fixture with an expected output file."""
    audits: list[FixtureAudit] = []
    for text_path in sorted(fixtures_dir.glob("*.text")):
        try:
            expected_path_for(text_path)
        except FileNotFoundError:
            continue
        audits.append(audit_fixture(text_path, markdown_pl))
    return audits


def format_byte(value: int | None) -> str:
    """Format optional byte values for Markdown tables."""
    return "EOF" if value is None else str(value)


def render_report(
    audits: list[FixtureAudit], fixtures_dir: Path, markdown_pl: Path
) -> str:
    """Render the audit as a Markdown document."""
    raw_mismatches = [audit for audit in audits if not audit.raw_equal]
    normalized_mismatches = [audit for audit in audits if not audit.normalized_equal]

    lines = [
        "# Markdown.pl Fixture Oracle Audit",
        "",
        "Generated by `uv run python scripts/markdown_pl_parity_audit.py`.",
        "",
        f"- **Fixtures:** `{fixtures_dir}`",
        f"- **Oracle:** `{markdown_pl}`",
        f"- **Fixture count:** {len(audits)}",
        f"- **Raw-byte mismatches:** {len(raw_mismatches)}",
        f"- **Normalized-contract mismatches:** {len(normalized_mismatches)}",
        "",
        "## Summary",
        "",
        (
            "| Fixture | Raw bytes | Normalized contract | Expected bytes | "
            "Oracle bytes | First raw diff |"
        ),
        "|---|---:|---:|---:|---:|---|",
    ]
    for audit in audits:
        first_diff = (
            "none"
            if audit.first_diff_index is None
            else (
                f"{audit.first_diff_index} "
                f"({format_byte(audit.expected_byte)} -> "
                f"{format_byte(audit.oracle_byte)})"
            )
        )
        lines.append(
            "| "
            f"{audit.name} | "
            f"{'pass' if audit.raw_equal else 'fail'} | "
            f"{'pass' if audit.normalized_equal else 'fail'} | "
            f"{audit.expected_bytes} | "
            f"{audit.oracle_bytes} | "
            f"{first_diff} |"
        )

    if raw_mismatches:
        lines.extend(["", "## Raw Mismatch Diffs", ""])
        for audit in raw_mismatches:
            lines.extend(
                [
                    f"### {audit.name}",
                    "",
                    "```diff",
                    audit.diff.rstrip(),
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=DEFAULT_FIXTURES_DIR,
        help="Directory containing Markdown.mdtest fixtures",
    )
    parser.add_argument(
        "--markdown-pl",
        type=Path,
        default=DEFAULT_MARKDOWN_PL,
        help="Path to Markdown.pl oracle",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional Markdown report path; stdout is used when omitted",
    )
    return parser.parse_args()


def main() -> int:
    """Run the audit CLI."""
    args = parse_args()
    audits = collect_audits(args.fixtures_dir, args.markdown_pl)
    report = render_report(audits, args.fixtures_dir, args.markdown_pl)
    if args.output is None:
        print(report, end="")
    else:
        args.output.write_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
