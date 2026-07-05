# Markdown.pl Parity Doc Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the existing Shakedown docs against local `Markdown.pl` behavior and rewrite the planning docs so a detailed architecture spec can target Markdown.pl parity deliberately.

**Architecture:** Add a repeatable Python audit script that compares local `Markdown.pl` output against the checked-in `Markdown.mdtest` expected files at both raw-byte and normalized-contract levels. Use that evidence plus direct `Markdown.pl` function-line inspection to create an oracle mechanics map and update the target, divergence, fixture-risk, and verification docs.

**Tech Stack:** Python 3.14, `uv`, `pytest`, local `~/markdown/Markdown.pl`, local `~/mdtest/Markdown.mdtest`, Markdown docs.

---

## File Structure

- Create `scripts/markdown_pl_parity_audit.py`
  - CLI/operator script for collecting fixture-vs-oracle raw and normalized comparison evidence.
  - Pure functions for normalization, first-diff detection, expected-file selection, and Markdown report rendering.
  - One subprocess boundary for invoking `perl ~/markdown/Markdown.pl`.
- Create `tests/test_markdown_pl_parity_audit.py`
  - Unit tests for pure helper behavior.
  - No real `perl` subprocess calls in tests.
- Create `docs/markdown/oracle-fixture-audit.md`
  - Generated report from `scripts/markdown_pl_parity_audit.py`.
  - Records which mdtest expected files differ from local `Markdown.pl` in raw bytes and whether normalized contract output still matches.
- Create `docs/markdown/oracle-mechanics.md`
  - Human-readable verified map of the local `Markdown.pl` processing order and line ranges.
  - Captures transform order and behavior that detailed architecture must preserve for parity.
- Modify `docs/markdown/target.md`
  - Define parity levels explicitly: normalized mdtest contract, strict local-oracle byte parity, and nondeterministic email-autolink equivalence.
  - Correct the claim that checked-in expected fixture files are raw local-oracle output.
- Modify `docs/markdown/divergences.md`
  - Remove nested-blockquote closing as an accepted divergence for Markdown.pl parity.
  - Reclassify email-autolink randomization as nondeterministic oracle behavior; parity must be entity-normalized unless the project abandons SPL-pure constraints.
- Modify `docs/markdown/fixture-outlook.md`
  - Replace `Divergence` risk language with parity-focused risk language.
  - Mark nested blockquote closing as a parity requirement, not a policy choice.
  - Mark email autolinks as nondeterministic outside the current mdtest corpus.
- Modify `docs/verification-plan.md`
  - Add replay evidence for the strict fixture audit and oracle mechanics map.
  - Remove emphasis and nested-blockquote parity from open policy decisions.
- Modify `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
  - Align carried-forward decisions with the parity goal.
- Modify `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`
  - Replace the nested-blockquote policy decision with a parity requirement.

---

### Task 1: Add Repeatable Oracle Fixture Audit Script

**Files:**
- Create: `scripts/markdown_pl_parity_audit.py`
- Test later in: `tests/test_markdown_pl_parity_audit.py`

- [ ] **Step 1: Create the script**

Create `scripts/markdown_pl_parity_audit.py` with this content:

```python
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


def first_byte_diff(left: bytes, right: bytes) -> tuple[int, int | None, int | None] | None:
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
    normalized_equal = normalize_contract(expected.decode("utf-8")) == normalize_contract(
        oracle.decode("utf-8")
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


def render_report(audits: list[FixtureAudit], fixtures_dir: Path, markdown_pl: Path) -> str:
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
        "| Fixture | Raw bytes | Normalized contract | Expected bytes | Oracle bytes | First raw diff |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for audit in audits:
        first_diff = (
            "none"
            if audit.first_diff_index is None
            else (
                f"{audit.first_diff_index} "
                f"({format_byte(audit.expected_byte)} -> {format_byte(audit.oracle_byte)})"
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
```

- [ ] **Step 2: Run Ruff on the new script**

Run:

```bash
uv run ruff check scripts/markdown_pl_parity_audit.py
```

Expected: `All checks passed!`

- [ ] **Step 3: Commit the script**

Run:

```bash
git add scripts/markdown_pl_parity_audit.py
git commit -m "chore: add Markdown.pl parity audit script"
```

Expected: commit succeeds.

---

### Task 2: Add Unit Tests for the Audit Script

**Files:**
- Create: `tests/test_markdown_pl_parity_audit.py`
- Modify: `scripts/markdown_pl_parity_audit.py` only if tests expose a defect in the script from Task 1.

- [ ] **Step 1: Create the unit test file**

Create `tests/test_markdown_pl_parity_audit.py` with this content:

```python
"""Unit tests for scripts.markdown_pl_parity_audit."""

from pathlib import Path

import pytest

from scripts.markdown_pl_parity_audit import (
    FixtureAudit,
    expected_path_for,
    first_byte_diff,
    normalize_contract,
    render_report,
)


def test_normalize_contract_matches_mdtest_whitespace_rules() -> None:
    text = "  <p>alpha</p>  \n\n\n  <p>beta</p>\n"

    assert normalize_contract(text) == "<p>alpha</p>\n\n<p>beta</p>"


def test_first_byte_diff_reports_value_change() -> None:
    assert first_byte_diff(b"abc", b"axc") == (1, 98, 120)


def test_first_byte_diff_reports_length_change() -> None:
    assert first_byte_diff(b"abc", b"ab") == (2, 99, None)


def test_first_byte_diff_returns_none_for_identical_bytes() -> None:
    assert first_byte_diff(b"abc", b"abc") is None


def test_expected_path_prefers_xhtml(tmp_path: Path) -> None:
    text_path = tmp_path / "Sample.text"
    xhtml_path = tmp_path / "Sample.xhtml"
    html_path = tmp_path / "Sample.html"
    text_path.write_text("input")
    xhtml_path.write_text("xhtml")
    html_path.write_text("html")

    assert expected_path_for(text_path) == xhtml_path


def test_expected_path_falls_back_to_html(tmp_path: Path) -> None:
    text_path = tmp_path / "Sample.text"
    html_path = tmp_path / "Sample.html"
    text_path.write_text("input")
    html_path.write_text("html")

    assert expected_path_for(text_path) == html_path


def test_expected_path_raises_when_no_expected_file(tmp_path: Path) -> None:
    text_path = tmp_path / "Sample.text"
    text_path.write_text("input")

    with pytest.raises(FileNotFoundError):
        expected_path_for(text_path)


def test_render_report_summarizes_raw_and_normalized_mismatches(tmp_path: Path) -> None:
    audit = FixtureAudit(
        name="Code Blocks",
        input_path=tmp_path / "Code Blocks.text",
        expected_path=tmp_path / "Code Blocks.xhtml",
        raw_equal=False,
        normalized_equal=True,
        expected_bytes=312,
        oracle_bytes=310,
        first_diff_index=219,
        expected_byte=32,
        oracle_byte=10,
        diff="--- expected\n+++ oracle\n",
    )

    report = render_report([audit], tmp_path, Path("/home/ec2-user/markdown/Markdown.pl"))

    assert "- **Fixture count:** 1" in report
    assert "- **Raw-byte mismatches:** 1" in report
    assert "- **Normalized-contract mismatches:** 0" in report
    assert "| Code Blocks | fail | pass | 312 | 310 | 219 (32 -> 10) |" in report
    assert "## Raw Mismatch Diffs" in report
```

- [ ] **Step 2: Run the focused tests**

Run:

```bash
uv run pytest tests/test_markdown_pl_parity_audit.py -q
```

Expected: `8 passed`.

- [ ] **Step 3: Run lint and type checks for the new Python files**

Run:

```bash
uv run ruff check scripts/markdown_pl_parity_audit.py tests/test_markdown_pl_parity_audit.py
uv run pyright
```

Expected:

```text
All checks passed!
0 errors, 0 warnings, 0 informations
```

The Pyright version warning may appear; it is not a failure.

- [ ] **Step 4: Commit tests**

Run:

```bash
git add tests/test_markdown_pl_parity_audit.py scripts/markdown_pl_parity_audit.py
git commit -m "test: cover Markdown.pl parity audit helpers"
```

Expected: commit succeeds.

---

### Task 3: Generate and Commit the Fixture Oracle Audit Report

**Files:**
- Create: `docs/markdown/oracle-fixture-audit.md`

- [ ] **Step 1: Generate the report**

Run:

```bash
uv run python scripts/markdown_pl_parity_audit.py --output docs/markdown/oracle-fixture-audit.md
```

Expected: command exits 0 and writes `docs/markdown/oracle-fixture-audit.md`.

- [ ] **Step 2: Verify the report captures current raw-byte drift**

Run:

```bash
rg -n "Raw-byte mismatches|Normalized-contract mismatches|Blockquotes with code blocks|Code Blocks" docs/markdown/oracle-fixture-audit.md
```

Expected output includes:

```text
- **Raw-byte mismatches:** 2
- **Normalized-contract mismatches:** 0
| Blockquotes with code blocks | fail | pass |
| Code Blocks | fail | pass |
```

The exact line numbers from `rg -n` may differ.

- [ ] **Step 3: Commit the report**

Run:

```bash
git add docs/markdown/oracle-fixture-audit.md
git commit -m "docs: record Markdown.pl fixture oracle audit"
```

Expected: commit succeeds.

---

### Task 4: Write the Oracle Mechanics Map

**Files:**
- Create: `docs/markdown/oracle-mechanics.md`

- [ ] **Step 1: Verify local Markdown.pl line map**

Run:

```bash
rg -n "^sub |^# Main|_RunBlockGamut|_RunSpanGamut|_DoHeaders|_DoLists|_DoCodeBlocks|_DoBlockQuotes|_DoItalicsAndBold|_DoAnchors|_DoImages|_DoAutoLinks|_EncodeAmpsAndAngles|_DoCodeSpans|_EncodeBackslashEscapes|_HashHTMLBlocks|_Detab|_Outdent|_StripLinkDefinitions|_FormParagraphs|_TokenizeHTML" ~/markdown/Markdown.pl
```

Expected output includes these anchors:

```text
226:sub Markdown {
274:sub _StripLinkDefinitions {
313:sub _HashHTMLBlocks {
423:sub _RunBlockGamut {
455:sub _RunSpanGamut {
516:sub _DoAnchors {
613:sub _DoImages {
718:sub _DoHeaders {
760:sub _DoLists {
848:sub _ProcessListItems {
916:sub _DoCodeBlocks {
950:sub _DoCodeSpans {
1035:sub _DoItalicsAndBold {
1049:sub _DoBlockQuotes {
1085:sub _FormParagraphs {
1122:sub _EncodeAmpsAndAngles {
1138:sub _EncodeBackslashEscapes {
1167:sub _DoAutoLinks {
1190:sub _EncodeEmailAddress {
1255:sub _TokenizeHTML {
1296:sub _Outdent {
1307:sub _Detab {
```

- [ ] **Step 2: Create the mechanics document**

Create `docs/markdown/oracle-mechanics.md` with this content:

```markdown
# Markdown.pl Oracle Mechanics

This file records the local `~/markdown/Markdown.pl` mechanics that matter for Shakedown parity. Line numbers refer to the local v1.0.1 file verified on 2026-04-23.

## Top-Level Pipeline

| Order | Function | Local lines | Parity requirement |
|---:|---|---:|---|
| 1 | `Markdown` setup | 226-271 | Normalize line endings, replace line-leading spaces with tabs, detab, strip blank leading/trailing lines, hash raw HTML blocks, strip link definitions, run block gamut, unescape special chars. |
| 2 | `_Detab` | 1307-1318 | Expand tabs to four-column tab stops before most parsing. Code and list behavior depend on this. |
| 3 | `_HashHTMLBlocks` | 313-419 | Protect block-level HTML before Markdown block processing, then hash new block-level HTML generated during recursion. |
| 4 | `_StripLinkDefinitions` | 274-311 | Remove reference definitions before block parsing and store case-insensitive URL/title data. |
| 5 | `_RunBlockGamut` | 423-452 | Apply block transforms in Markdown.pl order: headers, horizontal rules, lists, code blocks, blockquotes, HTML block hashing, paragraph formation. |
| 6 | `_UnescapeSpecialChars` | 1242-1251 | Restore hashed special characters after all block/span processing. |

## Block Pipeline

| Order | Function | Local lines | Parity requirement |
|---:|---|---:|---|
| 1 | `_DoHeaders` | 718-757 | Setext headers run before ATX headers; header contents are processed through `_RunSpanGamut`. |
| 2 | horizontal-rule substitutions | 430-435 | `***`, `---`, and `___` rules allow optional spaces and up to two leading spaces. |
| 3 | `_DoLists` | 760-845 | List parsing happens before code blocks and blockquotes. Ordered and unordered list markers share recursive list-level state. |
| 4 | `_ProcessListItems` | 848-913 | Tight/loose output depends on leading blank lines and blank lines within each item. Loose items run `_RunBlockGamut`; tight items run `_RunSpanGamut` after nested-list handling. |
| 5 | `_DoCodeBlocks` | 916-945 | Code blocks are found after list processing. Contents are outdented, encoded, detabbed, stripped of leading/trailing blank lines, then wrapped in `<pre><code>`. |
| 6 | `_DoBlockQuotes` | 1049-1082 | Blockquotes recursively run `_RunBlockGamut` on stripped quote contents and then prefix every output line with two spaces before wrapping in `<blockquote>`. This indentation is part of strict local-oracle byte parity. |
| 7 | `_FormParagraphs` | 1085-1119 | Unhashed chunks become paragraphs after span processing; hashed HTML blocks are restored without paragraph wrapping. |

## Span Pipeline

| Order | Function | Local lines | Parity requirement |
|---:|---|---:|---|
| 1 | `_RunSpanGamut` | 455-484 | Span transforms run in a fixed order; later transforms see earlier HTML substitutions. |
| 2 | `_DoCodeSpans` | 950-993 | Code spans run before escapes, links, auto-links, entity encoding, and emphasis. Backtick runs can delimit content containing shorter backtick runs. |
| 3 | `_EscapeSpecialChars` | 487-513 | HTML tags and backslash escapes are tokenized/hashed before link and emphasis processing. |
| 4 | `_DoImages` | 613-715 | Image syntax is processed before anchor syntax. Reference image lookup uses stripped link definitions. |
| 5 | `_DoAnchors` | 516-610 | Inline, full-reference, collapsed-reference, and shortcut-reference links are processed before auto-links and entity encoding. |
| 6 | `_DoAutoLinks` | 1167-1187 | HTTP/HTTPS/FTP auto-links produce literal link text. Email auto-links call `_EncodeEmailAddress`, which is randomized. |
| 7 | `_EncodeAmpsAndAngles` | 1122-1135 | Ampersands not part of an entity and angle brackets not starting an HTML tag are encoded after links and auto-links. |
| 8 | `_DoItalicsAndBold` | 1035-1047 | Strong substitutions run before emphasis substitutions. This order is required for Markdown.pl's overlapping `<em>/<strong>` behavior. |
| 9 | hard-break substitution | 481 | Two or more spaces before newline become `<br />` after emphasis processing. |

## Reference Definitions

`_StripLinkDefinitions` stores URLs and optional titles in global hashes keyed by lowercased link identifier. Reference definitions are removed from the document before block parsing, so a parity design needs document-scoped reference collection before inline reference resolution.

## Strict Fixture Audit Finding

`docs/markdown/oracle-fixture-audit.md` shows that two checked-in expected files differ from local `Markdown.pl` raw output while still matching the normalized test contract:

| Fixture | Raw status | Normalized status | Reason class |
|---|---|---|---|
| Blockquotes with code blocks | mismatch | match | Local Markdown.pl emits different indentation inside blockquoted code blocks and around the second paragraph. |
| Code Blocks | mismatch | match | Local Markdown.pl output differs in trailing spaces inside a code block. |

Strict local-oracle byte parity must compare against freshly generated local `Markdown.pl` output, not only the checked-in `.xhtml`/`.html` expected files.

## Nondeterministic Email Auto-Links

`_EncodeEmailAddress` uses Perl randomness to encode email auto-links. SPL has no verified randomness primitive. A strict byte-for-byte target cannot promise identical output for email auto-links across repeated oracle runs. The achievable SPL-pure target is entity-normalized email-link equivalence unless the project deliberately adds non-SPL runtime help.
```

- [ ] **Step 3: Commit the mechanics document**

Run:

```bash
git add docs/markdown/oracle-mechanics.md
git commit -m "docs: map Markdown.pl oracle mechanics for parity"
```

Expected: commit succeeds.

---

### Task 5: Update Target and Divergence Docs for Parity

**Files:**
- Modify: `docs/markdown/target.md`
- Modify: `docs/markdown/divergences.md`

- [ ] **Step 1: Update `docs/markdown/target.md`**

Make these content changes:

1. In the **Oracle** section, change the single-source sentence to:

```markdown
`Markdown.pl` is the single source of truth for correct output. Where its behaviour surprises, the oracle is right and Shakedown must match it. The only exception under an SPL-pure parity goal is nondeterministic email-autolink entity selection, because local `Markdown.pl` uses randomness and SPL has no verified randomness primitive.
```

2. In **Test Surface: Markdown.mdtest**, replace the sentence beginning `The 23 fixtures` with:

```markdown
The 23 fixtures at `~/mdtest/Markdown.mdtest/` define the current regression corpus. Each fixture is a pair: `*.text` input and `*.xhtml` (or `*.html`) expected output. `docs/markdown/oracle-fixture-audit.md` records where these checked-in expected files differ from freshly generated local `Markdown.pl` output at the raw-byte level.
```

3. Replace the current correctness sentence with:

```markdown
The default `tests/test_mdtest.py` contract compares normalized fixture output. A strict local-oracle parity check must compare Shakedown output against freshly generated `perl ~/markdown/Markdown.pl` output for the same input, because two checked-in expected files differ from local oracle raw bytes.
```

4. Replace the **Intentional divergences from oracle behaviour** summary with:

```markdown
See `docs/markdown/divergences.md`. Under the Markdown.pl parity goal, nested blockquote closing is not an accepted divergence; Shakedown should reproduce the oracle quirk when strict parity is required. Email autolinks are nondeterministic in Markdown.pl, so SPL-pure parity means entity-normalized equivalence rather than byte-identical random choices.
```

5. Add a new section before **Interface**:

```markdown
## Parity Levels

- **Normalized mdtest contract:** current default regression check. It trims line whitespace, collapses repeated blank lines, and decodes numeric entities only for the Auto links fixture.
- **Strict local-oracle parity:** compare output against freshly generated `perl ~/markdown/Markdown.pl` output for the same input. This is the architecture target for deterministic Markdown.pl behavior.
- **Email-autolink equivalence:** compare decoded email auto-link href/text content rather than exact randomized entity choices. This is the SPL-pure target for Markdown.pl's nondeterministic email encoder.
```

- [ ] **Step 2: Rewrite `docs/markdown/divergences.md`**

Replace the full file with:

```markdown
# Markdown.pl Parity Exceptions

This file documents behavior that cannot be byte-identical under an SPL-pure Markdown.pl parity goal, plus prior divergence candidates that are no longer accepted.

## Active Exception

| Feature | Markdown.pl behaviour | Shakedown parity target | Reason |
|---|---|---|---|
| Email auto-links | Each character is randomly encoded as decimal or hex HTML entity by `_EncodeEmailAddress` | Entity-normalized equivalence for href and visible text | SPL has no verified randomness primitive, so byte-identical random choices are not available in a pure SPL implementation |

## Rejected Divergence Candidates

| Feature | Prior Shakedown behavior | Markdown.pl parity requirement | Reason |
|---|---|---|---|
| Nested blockquote closing | Emit a structurally cleaner bare `</blockquote>` for the outer close | Reproduce the local Markdown.pl output, including malformed paragraph-wrapped close tags where the oracle emits them | SPL can emit the exact byte sequence; choosing valid HTML would be a scope cut, not a language limitation |
| Emphasis backtracking | Treat overlapping `<em>/<strong>` as unsupported by the P2 single-toggle prototype | Implement Markdown.pl's strong-before-emphasis substitution order | The XFAIL is a prototype limitation, not a forced divergence |
```

- [ ] **Step 3: Verify no doc still claims nested blockquote is an accepted divergence**

Run:

```bash
rg -n "Nested blockquote closing|well-formed|correct behaviour|accepted divergence|intentional diverg" docs/markdown docs/superpowers/notes docs/verification-plan.md
```

Expected: matches either point to the new `Markdown.pl Parity Exceptions` wording or to historical notes that explicitly identify the old claim as superseded.

- [ ] **Step 4: Commit target/divergence updates**

Run:

```bash
git add docs/markdown/target.md docs/markdown/divergences.md
git commit -m "docs: define Markdown.pl parity exceptions"
```

Expected: commit succeeds.

---

### Task 6: Update Risk and Verification Docs

**Files:**
- Modify: `docs/markdown/fixture-outlook.md`
- Modify: `docs/verification-plan.md`
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`

- [ ] **Step 1: Update `docs/markdown/fixture-outlook.md` risk language**

Make these specific edits:

1. Replace the `Divergence` risk-tier bullet with:

```markdown
- **Parity exception** — byte-identical Markdown.pl behavior is not available in pure SPL; the target must use a documented equivalence rule.
```

2. Change the Auto Links row to:

```markdown
| Auto Links | Low for mdtest; Parity exception for email autolinks | Email autolink randomization | The mdtest fixture covers URL autolinks only. Email autolinks require entity-normalized equivalence because Markdown.pl randomizes entity choice. |
```

3. Change the Nested Block Structures row to:

```markdown
| Nested Block Structures | High | Exact nested output | Simple blockquote is proven in `./shakedown-dev`; full nested block composition must include Markdown.pl quirks when strict parity is required. |
```

- [ ] **Step 2: Update `docs/verification-plan.md`**

Add these sections after B11:

```markdown
### B12 — Strict fixture oracle audit

- **Command:** `uv run python scripts/markdown_pl_parity_audit.py --output docs/markdown/oracle-fixture-audit.md`
- **Observed:** 23 fixtures audited. Raw-byte mismatches: 2 (`Blockquotes with code blocks`, `Code Blocks`). Normalized-contract mismatches: 0.
- **Disposition:** The checked-in mdtest expected files are valid for the current normalized test contract, but strict local-oracle parity must compare against freshly generated `Markdown.pl` output.

### B13 — Oracle mechanics map

- **Command:** `rg -n "^sub |^# Main|_RunBlockGamut|_RunSpanGamut|_DoHeaders|_DoLists|_DoCodeBlocks|_DoBlockQuotes|_DoItalicsAndBold|_DoAnchors|_DoImages|_DoAutoLinks|_EncodeAmpsAndAngles|_DoCodeSpans|_EncodeBackslashEscapes|_HashHTMLBlocks|_Detab|_Outdent|_StripLinkDefinitions|_FormParagraphs|_TokenizeHTML" ~/markdown/Markdown.pl`
- **Observed:** Function anchors recorded in `docs/markdown/oracle-mechanics.md`.
- **Disposition:** Detailed architecture should treat `docs/markdown/oracle-mechanics.md` as the transform-order checklist for Markdown.pl parity.
```

Then replace the Bucket D list item:

```markdown
- Any remaining policy questions around list exactness. Emphasis backtracking is now classified as a two-pass implementation requirement unless deliberately scoped out.
```

with:

```markdown
- Production details for list exactness and nested block composition. These are implementation risks, not accepted divergence decisions under the Markdown.pl parity goal.
```

- [ ] **Step 3: Update due-diligence and hardening notes**

In `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`:

1. Change the Lists and nested blocks row's design implication to:

```markdown
The design must reproduce tight/loose behavior and nested block quirks needed for Markdown.pl parity.
```

2. Change the same row's status to:

```markdown
open for SPL beyond simple blockquote; the mdtest list fixtures are green only through the current oracle stub
```

3. In **Decisions Carried Forward**, replace any sentence that frames nested block behavior as a divergence choice with a sentence that says:

```markdown
- Carry nested block composition as a strict parity requirement; emitting cleaner HTML is a scope cut, not the default target.
```

In `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`:

1. Replace the final decision register row for nested blockquote closer behavior with:

```markdown
| Nested blockquote closer quirk | parity requirement | `docs/markdown/oracle-mechanics.md` plus `docs/markdown/divergences.md` | Detailed spec must reproduce the local Markdown.pl byte sequence when strict parity is required. |
```

2. Replace the go/no-go paragraph with:

```markdown
Proceed to detailed architecture only if the spec explicitly carries the two-pass emphasis implementation requirement, strict nested-block parity requirement, and email-autolink entity-normalized exception. All other pre-design implementation risks have either executable SPL mechanics evidence or are correctly classified as non-SPL oracle-stub evidence.
```

- [ ] **Step 4: Commit risk and verification doc updates**

Run:

```bash
git add docs/markdown/fixture-outlook.md docs/verification-plan.md docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md
git commit -m "docs: align parity risks with oracle audit"
```

Expected: commit succeeds.

---

### Task 7: Final Consistency Scan and Verification

**Files:**
- Modify only files already touched in earlier tasks if the scan exposes stale language.

- [ ] **Step 1: Scan for stale divergence and oracle-stub claims**

Run:

```bash
rg -n "well-formed|correct behaviour|accepted divergence|intentional divergence|91–96|pass ceiling|Markdown.pl.*expected output generated|oracle-stub green means|SPL passes all 23" docs/markdown docs/verification-plan.md docs/superpowers/notes
```

Expected:

- No stale claim says nested blockquote cleanup is the correct default.
- No stale claim says checked-in expected files are raw-identical local Markdown.pl output.
- Historical `91–96` mentions are either in prior-attempt context or explicitly marked non-transferable.

- [ ] **Step 2: Run focused audit checks**

Run:

```bash
uv run pytest tests/test_markdown_pl_parity_audit.py -q
uv run python scripts/markdown_pl_parity_audit.py --output /tmp/markdown-pl-parity-audit.md
diff -u docs/markdown/oracle-fixture-audit.md /tmp/markdown-pl-parity-audit.md
```

Expected:

```text
8 passed
```

The `diff` command exits 0 and prints no diff.

- [ ] **Step 3: Run full verification**

Run:

```bash
uv run pytest -q
uv run ruff check .
uv run pyright
git status --short
```

Expected:

```text
98 passed, 1 xfailed
All checks passed!
0 errors, 0 warnings, 0 informations
```

The Pyright version warning may appear; it is not a failure. `git status --short` should show only intentional uncommitted edits before the final commit, and no output after the final commit.

- [ ] **Step 4: Final commit if the scan required edits**

If Step 1 required wording fixes, commit them:

```bash
git add docs/markdown docs/verification-plan.md docs/superpowers/notes
git commit -m "docs: remove stale Markdown.pl parity assumptions"
```

Expected: commit succeeds when there are scan-driven edits. If there are no scan-driven edits, skip this commit.

---

## Completion Criteria

- `docs/markdown/oracle-fixture-audit.md` exists and records raw-vs-normalized fixture evidence.
- `docs/markdown/oracle-mechanics.md` exists and records the verified Markdown.pl transform order.
- `docs/markdown/target.md` defines normalized contract, strict local-oracle parity, and email-autolink equivalence.
- `docs/markdown/divergences.md` no longer treats nested blockquote closing or emphasis backtracking as accepted divergences.
- `docs/verification-plan.md` records the audit evidence and points detailed architecture at the mechanics map.
- Tests and checks pass:
  - `uv run pytest tests/test_markdown_pl_parity_audit.py -q`
  - `uv run pytest -q`
  - `uv run ruff check .`
  - `uv run pyright`

## Self-Review Checklist

- Every new Python function has typed parameters and return values.
- Tests do not invoke real `perl`; only the audit CLI does.
- Every documentation claim about parity is traceable to `~/markdown/Markdown.pl`, `docs/markdown/oracle-fixture-audit.md`, or `docs/markdown/oracle-mechanics.md`.
- No current planning doc describes nested blockquote cleanup as an accepted default divergence.
- Email autolink behavior is described as nondeterministic oracle behavior, not as ordinary deterministic Markdown output.
