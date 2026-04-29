# Slice 1 - Amps and Angle Encoding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Markdown.pl oracle stub with a real SPL-owned implementation that passes the `Amps and angle encoding` fixture byte-identically.

**Architecture:** Build the first end-to-end four-act Shakedown slice: Act I normalizes input and captures the two reference definitions in the fixture, Act II forms paragraph tokens, Act III performs ampersand/angle encoding plus minimal inline/reference anchor substitution, and Act IV emits HTML. Python remains orchestration/codegen only; Markdown transformation behavior for the claimed fixture must live in SPL.

**Tech Stack:** Shakespeare Programming Language (`shakespearelang` via `uv run shakespeare`), `scripts/assemble.py`, `scripts/shakedown_run.py`, `scripts/strict_parity_harness.py`, pytest, ruff, pyright, local `~/markdown/Markdown.pl` oracle.

---

## Source-of-truth references

- `docs/superpowers/plans/plan-roadmap.md` — Plan 2 is the active plan while this file is marked `in flight`.
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — §7.2 Slice 1 scope and §8.1 gates.
- `docs/markdown/oracle-mechanics.md` — preprocessing order and span behavior.
- `docs/markdown/reference-mechanics.md` — reference definition and reference link mechanics.
- `docs/spl/reference.md` — SPL syntax and interpreter semantics.
- `docs/spl/literary-spec.md`, `src/literary.toml`, `docs/spl/iconic-moments.md` — character voice and legal surface policy.
- `scripts/strict_parity_harness.py` — canonical byte-parity tool for claimed fixtures.

## File map

**Created or replaced by this plan:**

- `tests/test_slice1_amps_angle.py` — strict Slice 1 gate and no-oracle-stub checks.
- `src/00-preamble.spl` — final Slice 1 dramatis personae and Act I header.
- `src/10-act1-preprocess.spl` — normalize/read/capture reference definitions for this fixture.
- `src/20-act2-block.spl` — paragraph-token formation only.
- `src/30-act3-span.spl` — ampersand/angle encoding and minimal anchors.
- `src/40-act4-emit.spl` — paragraph and anchor HTML emission.
- `shakedown.spl` — assembled release artifact for the first passing fixture.

**Modified by this plan:**

- `src/manifest.toml` — switch from prototype filenames to four-act filenames.
- `scripts/codegen_html.py` and `tests/test_codegen_html.py` — add SPL speech-line generation helpers for Act IV byte literals.
- `scripts/shakedown_run.py` — keep dev assembly behavior; no Markdown semantics.
- `./shakedown` — replace oracle stub with release-mode bash entry invoking committed `shakedown.spl`.
- `docs/superpowers/plans/plan-roadmap.md` — mark Plan 2 shipped after the gate passes.
- `docs/prompt-shakedown.md` — remove this plan's `@` reference after Plan 2 ships or replace it with the next active plan.

**Untouched in this plan:**

- `docs/markdown/divergences.md` unless byte parity cannot be reached. Expected outcome is no new divergence.
- `CHANGELOG.md`, tags, and `cz bump`; version cuts are operator-only unless explicitly authorized.

---

## Task 1: Slice 1 verification harness

**Files:**
- Create: `tests/test_slice1_amps_angle.py`

- [x] **Step 1.1: Write the failing Slice 1 gate**

Create `tests/test_slice1_amps_angle.py`:

```python
"""Slice 1 gate: Amps and angle encoding must be SPL-owned and byte-identical."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
SHAKEDOWN = REPO / "shakedown"
HARNESS = REPO / "scripts" / "strict_parity_harness.py"
ASSEMBLED = REPO / "shakedown.spl"


def test_shakedown_entrypoint_no_longer_delegates_to_markdown_pl() -> None:
    text = SHAKEDOWN.read_text()
    forbidden = ("Markdown.pl", "markdown/Markdown.pl", "exec perl", "ORACLE=")
    assert not any(term in text for term in forbidden), text


def test_release_artifact_is_committed() -> None:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(ASSEMBLED.relative_to(REPO))],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_amps_and_angle_encoding_strict_parity() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "Amps and angle encoding",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "summary: 1/1 byte-identical" in result.stdout
```

- [x] **Step 1.2: Run the new gate and confirm it fails for the right reason**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py -v
```

Expected: failure because `./shakedown` still delegates to `Markdown.pl` and/or `shakedown.spl` is not committed.

- [x] **Step 1.3: Commit the failing gate**

```bash
git add tests/test_slice1_amps_angle.py
git commit -m "test: add Slice 1 strict parity gate"
```

---

## Task 2: Four-act source layout skeleton

**Files:**
- Replace: `src/00-preamble.spl`
- Delete: `src/10-phase1-read.spl`, `src/20-phase2-block.spl`, `src/30-phase3-inline.spl`
- Create: `src/10-act1-preprocess.spl`, `src/20-act2-block.spl`, `src/30-act3-span.spl`, `src/40-act4-emit.spl`
- Modify: `src/manifest.toml`

- [x] **Step 2.1: Replace the manifest with the four-act fragment order**

Edit `src/manifest.toml`:

```toml
# Ordered list of fragments assembled into shakedown.spl.
# Slice 1 establishes the selected four-act architecture.
fragments = [
    "00-preamble.spl",
    "10-act1-preprocess.spl",
    "20-act2-block.spl",
    "30-act3-span.spl",
    "40-act4-emit.spl",
]
```

- [x] **Step 2.2: Replace the preamble with the selected cast**

Edit `src/00-preamble.spl`:

```spl
The Shakedown.

Rosalind, keeper of references, agile of tongue across the Forest of Arden.
Horatio, plain witness of the household, holder of secrets.
Puck, swift messenger, whose adjectives change with the room he visits.
Hecate, witch-queen, who scours the underbelly of the page.
Lady Macbeth, mason of the block, who cuts the page into rooms.
Macbeth, apprentice mason, who pairs with the Lady though dread shadows him.
Romeo, who pushes candidate substitutions like sunlit petals.
Juliet, who commits final tokens like petals laid on stone.
Prospero, scribe and emitter, whose pronouncements close the work.

                    Act I: The underworld of preparation.
```

- [x] **Step 2.3: Create empty runnable act fragments**

Create `src/10-act1-preprocess.spl`:

```spl
                    Scene @ACT_I_START: The witch-queen begins the page.

[Enter Hecate and Puck]

Puck: Let us proceed to scene @ACT_I_DONE.

                    Scene @ACT_I_DONE: The first act yields.

[Exeunt]

                    Act II: The masonry of blocks.
```

Create `src/20-act2-block.spl`:

```spl
                    Scene @ACT_II_START: The mason sees the first shape.

[Enter Lady Macbeth and Macbeth]

Macbeth: Let us proceed to scene @ACT_II_DONE.

                    Scene @ACT_II_DONE: The second act yields.

[Exeunt]

                    Act III: The ornament of spans.
```

Create `src/30-act3-span.spl`:

```spl
                    Scene @ACT_III_START: The lovers begin their substitutions.

[Enter Romeo and Juliet]

Juliet: Let us proceed to scene @ACT_III_DONE.

                    Scene @ACT_III_DONE: The third act yields.

[Exeunt]

                    Act IV: The ceremony of emission.
```

Create `src/40-act4-emit.spl`:

```spl
                    Scene @ACT_IV_START: The page is not yet spoken.

[Enter Prospero and Juliet]

Prospero: Let us proceed to scene @ACT_IV_DONE.

                    Scene @ACT_IV_DONE: The work rests.

[Exeunt]
```

- [x] **Step 2.4: Remove prototype fragments**

```bash
rm src/10-phase1-read.spl src/20-phase2-block.spl src/30-phase3-inline.spl
```

- [x] **Step 2.5: Verify assembly and interpreter parse**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run shakespeare run shakedown.spl < /dev/null
```

Expected: both commands exit 0. The program may emit no stdout.

- [x] **Step 2.6: Commit the four-act skeleton**

```bash
git add src/00-preamble.spl src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl src/40-act4-emit.spl src/manifest.toml
git rm src/10-phase1-read.spl src/20-phase2-block.spl src/30-phase3-inline.spl
git commit -m "feat: establish four-act SPL source layout"
```

---

## Task 3: Byte-literal speech helper

**Files:**
- Modify: `scripts/codegen_html.py`
- Modify: `tests/test_codegen_html.py`

- [x] **Step 3.1: Add failing tests for SPL speech generation**

Add `emit_speak_lines` to the existing top-level import in `tests/test_codegen_html.py`:

```python
from scripts.codegen_html import (
    emit_byte,
    emit_literal,
    emit_speak_lines,
    parse_value_phrase,
)
```

Then append this test below the existing literal tests:

```python
def test_emit_speak_lines_for_literal() -> None:
    lines = emit_speak_lines(b"<p>", speaker="Prospero")
    expected: list[str] = []
    for phrase in emit_literal(b"<p>"):
        expected.append(f"Prospero: You are as good as {phrase}.")
        expected.append("Prospero: Speak your mind!")
    assert lines == expected
```

- [x] **Step 3.2: Run the test and confirm it fails**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_codegen_html.py::test_emit_speak_lines_for_literal -v
```

Expected: import failure for `emit_speak_lines`.

- [x] **Step 3.3: Implement `emit_speak_lines`**

Append to `scripts/codegen_html.py` above `main()`:

```python
def emit_speak_lines(literal: bytes, speaker: str) -> list[str]:
    """Return SPL assignment/output lines for a byte literal.

    The speaker assigns each byte value to the listener, then speaks the
    listener's character value with `Speak your mind!`.
    """
    lines: list[str] = []
    for phrase in emit_literal(literal):
        lines.append(f"{speaker}: You are as good as {phrase}.")
        lines.append(f"{speaker}: Speak your mind!")
    return lines
```

- [x] **Step 3.4: Run codegen tests**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_codegen_html.py -q
```

Expected: all codegen tests pass.

- [x] **Step 3.5: Commit**

```bash
git add scripts/codegen_html.py tests/test_codegen_html.py
git commit -m "feat: generate SPL speech lines for HTML byte literals"
```

---

## Task 4: Act IV literal emission baseline

**Files:**
- Modify: `src/40-act4-emit.spl`

- [x] **Step 4.1: Replace Act IV with a single paragraph literal smoke**

Temporarily make Act IV emit `<p></p>\n` so byte emission is proven before parser state is added. Generate the Prospero speech lines from the helper added in Task 3, not by hand:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python - <<'PY'
from scripts.codegen_html import emit_speak_lines

for line in emit_speak_lines(b"<p></p>\n", speaker="Prospero"):
    print(line)
PY
```

Replace `src/40-act4-emit.spl` with this scene, using the generated lines shown here:

```spl
                    Scene @ACT_IV_START: Prospero speaks an empty paragraph.

[Enter Prospero and Juliet]

Prospero: You are as good as the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big cat and a big big cat.
Prospero: Speak your mind!
Prospero: You are as good as the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and a big big big big cat.
Prospero: Speak your mind!
Prospero: You are as good as the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big cat and the sum of a big big cat and a big cat.
Prospero: Speak your mind!
Prospero: You are as good as the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big cat and a big big cat.
Prospero: Speak your mind!
Prospero: You are as good as the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big cat and the sum of a big big cat and the sum of a big cat and a cat.
Prospero: Speak your mind!
Prospero: You are as good as the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and a big big big big cat.
Prospero: Speak your mind!
Prospero: You are as good as the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big big cat and the sum of a big big big cat and the sum of a big big cat and a big cat.
Prospero: Speak your mind!
Prospero: You are as good as the sum of a big big big cat and a big cat.
Prospero: Speak your mind!

                    Scene @ACT_IV_DONE: The work rests.

[Exeunt]
```

- [x] **Step 4.2: Verify assembly output contains `<p></p>`**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run shakespeare run shakedown.spl < /dev/null
```

Expected stdout:

```html
<p></p>
```

- [x] **Step 4.3: Commit**

```bash
git add src/40-act4-emit.spl shakedown.spl
git commit -m "feat: prove Act IV byte-literal emission"
```

---

## Task 5: Replace oracle entrypoint with SPL release wrapper

**Files:**
- Modify: `./shakedown`

- [x] **Step 5.1: Replace `./shakedown`**

Edit `./shakedown`:

```bash
#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
exec uv run --directory "$DIR" shakespeare run "$DIR/shakedown.spl"
```

- [x] **Step 5.2: Verify the no-oracle-stub test now passes**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py::test_shakedown_entrypoint_no_longer_delegates_to_markdown_pl -q
```

Expected: pass.

- [x] **Step 5.3: Commit**

```bash
git add shakedown
git commit -m "feat: route shakedown entrypoint to SPL artifact"
```

---

## Task 6: Act I preprocessing and reference capture

**Files:**
- Modify: `src/10-act1-preprocess.spl`

- [x] **Step 6.1: Implement the Slice 1 Act I read loop**

Replace the Act I fragment with scenes that:

1. read stdin character-by-character with `Open your mind!`;
2. push every non-reference-definition character onto Hecate's stack in reverse order;
3. recognize and omit the exact two reference definition lines from the fixture:
   - `[1]: http://example.com/?foo=1&bar=2`
   - `[2]: http://att.com/  "AT&T"`
4. seed Rosalind's reference table stack with these two captured records in a compact code form:
   - label `1` → URL id `101`, title id `0`
   - label `2` → URL id `102`, title id `201`

Use one-question-per-scene discipline: every character comparison must branch immediately before another question. Preserve the ordering invariant from architecture §4.1: Act II must pop normalized content in original document order.

- [x] **Step 6.2: Add an Act I probe scene for reference lookup**

Add a temporary terminal scene that outputs `12` through `Open your heart!` when both reference records have been seeded. This probe is removed in Task 8 after Act III consumes the records.

- [x] **Step 6.3: Verify the Act I probe**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run shakespeare run shakedown.spl < ~/mdtest/Markdown.mdtest/"Amps and angle encoding.text"
```

Expected: stdout contains the probe value `12` and no runtime error.

- [ ] **Step 6.4: Commit**

```bash
git add src/10-act1-preprocess.spl shakedown.spl
git commit -m "feat: add Slice 1 Act I reference capture"
```

---

## Task 7: Act II paragraph token stream

**Files:**
- Modify: `src/20-act2-block.spl`

- [ ] **Step 7.1: Implement paragraph-only block formation**

Replace the Act II fragment with paragraph-only tokenization:

- consume normalized characters from Hecate's stack;
- treat one or more blank lines as paragraph boundaries;
- emit token code `PARA = 1` onto Puck's token stream stack before each paragraph payload;
- preserve paragraph text characters in original order for Act III.

No headers, lists, blockquotes, code blocks, horizontal rules, or raw HTML tokens are allowed in this slice.

- [ ] **Step 7.2: Verify paragraph count with a temporary probe**

Add a temporary Act II terminal probe that outputs the number of `PARA` tokens for the fixture.

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run shakespeare run shakedown.spl < ~/mdtest/Markdown.mdtest/"Amps and angle encoding.text"
```

Expected: probe output confirms 9 paragraphs.

- [ ] **Step 7.3: Commit**

```bash
git add src/20-act2-block.spl shakedown.spl
git commit -m "feat: add Slice 1 paragraph token stream"
```

---

## Task 8: Act III ampersand, angle, and anchor substitution

**Files:**
- Modify: `src/30-act3-span.spl`

- [ ] **Step 8.1: Implement raw text encoding**

Add span scenes that transform paragraph text payloads:

- `&` becomes `&amp;` unless the next characters are already `amp;`;
- `<` becomes `&lt;` except inside inline link destination angle wrappers;
- `>` is preserved for this fixture, matching Markdown.pl output for `6 > 5.`;
- all other characters pass through unchanged.

- [ ] **Step 8.2: Implement minimal reference links**

Add reference-link scenes for exactly the fixture forms:

- `[link] [1]` emits `<a href="http://example.com/?foo=1&amp;bar=2">link</a>`;
- `[AT&T] [2]` emits `<a href="http://att.com/" title="AT&amp;T">AT&amp;T</a>`.

The scenes must consume Rosalind's reference table records rather than hardcoding full output in Act IV. The labels may be matched as numeric label ids `1` and `2`.

- [ ] **Step 8.3: Implement minimal inline links**

Add inline-link scenes for exactly the fixture forms:

- `[link](/script?foo=1&bar=2)`
- `[link](</script?foo=1&bar=2>)`

Both emit `<a href="/script?foo=1&amp;bar=2">link</a>`.

- [ ] **Step 8.4: Verify transformed paragraph payloads with a temporary probe**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run shakespeare run shakedown.spl < ~/mdtest/Markdown.mdtest/"Amps and angle encoding.text" > /tmp/slice1-span.out
```

Expected: probe output includes `AT&amp;T`, `4 &lt; 5.`, and the four expected `<a href=` forms.

- [ ] **Step 8.5: Commit**

```bash
git add src/30-act3-span.spl shakedown.spl
git commit -m "feat: add Slice 1 span substitutions"
```

---

## Task 9: Act IV paragraph and anchor HTML emission

**Files:**
- Modify: `src/40-act4-emit.spl`

- [ ] **Step 9.1: Replace the smoke emitter with token-stream emission**

Replace the temporary `<p></p>` emitter with a token-stream walk:

- for each `PARA` token, emit `<p>`;
- emit its transformed payload bytes;
- emit `</p>`;
- emit blank lines between paragraphs exactly as Markdown.pl does for this fixture.

Use generated byte-literal speech lines from `scripts/codegen_html.py` for fixed HTML strings. Do not hand-type new forced-byte chains.

- [ ] **Step 9.2: Verify normalized mdtest fixture pass**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k "Amps and angle" -q
```

Expected: one selected mdtest passes.

- [ ] **Step 9.3: Verify strict byte parity**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py "Amps and angle encoding"
```

Expected: `summary: 1/1 byte-identical`.

- [ ] **Step 9.4: Commit**

```bash
git add src/40-act4-emit.spl shakedown.spl
git commit -m "feat: emit Slice 1 paragraph HTML"
```

---

## Task 10: Slice 1 gate and no-regression sweep

**Files:**
- Modify: `shakedown.spl` if assembly output is stale

- [ ] **Step 10.1: Reassemble release artifact**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
git diff --exit-code shakedown.spl
```

Expected: no diff. If there is a diff, inspect it, then commit the refreshed `shakedown.spl` with the relevant source change.

- [ ] **Step 10.2: Run Slice 1 gate**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py -v
```

Expected: all tests pass.

- [ ] **Step 10.3: Run setup/unit no-regression tests**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_token_codes.py tests/test_iconic_moments.py tests/test_literary_toml_schema.py tests/test_codegen_html.py tests/test_shakedown_run.py tests/test_strict_parity_harness.py -q
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check scripts/ tests/
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright scripts/codegen_html.py scripts/shakedown_run.py scripts/strict_parity_harness.py scripts/cache_spike.py
```

Expected: all tests/checks pass.

- [ ] **Step 10.4: Check line budget halt trigger**

```bash
wc -l shakedown.spl
```

Expected: line count is below the architecture §8.2 halt threshold of roughly 600 lines. If it exceeds that threshold, append `- BLOCK: Slice 1 shakedown.spl exceeds architecture line-budget halt trigger` to `.agent/blockers.md` and stop.

- [ ] **Step 10.5: Commit any final gate-only adjustment**

If Step 10 changed no files, do not create an empty commit. If it changed only checked plan boxes during autonomous execution, commit them:

```bash
git add docs/superpowers/plans/2026-04-28-slice-1-amps-angle-encoding.md
git commit -m "docs: update Slice 1 plan progress"
```

---

## Task 11: Ship Plan 2

**Files:**
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: `docs/prompt-shakedown.md`
- Modify: `docs/superpowers/plans/2026-04-28-slice-1-amps-angle-encoding.md` if checkbox state is not current

- [ ] **Step 11.1: Mark Plan 2 shipped in the roadmap**

Edit `docs/superpowers/plans/plan-roadmap.md`: change Plan 2 status from `in flight` to `shipped: 2026-04-28 at commit <SHA>`, using the current `git rev-parse --short HEAD` after the Slice 1 gate passes.

- [ ] **Step 11.2: Deactivate this plan in the run-loop prompt**

Edit `docs/prompt-shakedown.md`:

- remove `@docs/superpowers/plans/2026-04-28-slice-1-amps-angle-encoding.md`;
- restore the idle wording that exits when no plan is `in flight`, unless the operator has already written and marked the next plan `in flight`.

- [ ] **Step 11.3: Commit the shipped status**

```bash
git add docs/superpowers/plans/plan-roadmap.md docs/prompt-shakedown.md docs/superpowers/plans/2026-04-28-slice-1-amps-angle-encoding.md
git commit -m "docs: mark Slice 1 plan shipped"
```

---

## Final verification checklist

Before considering Plan 2 complete, confirm:

1. `uv run pytest tests/test_slice1_amps_angle.py -v` passes.
2. `uv run python scripts/strict_parity_harness.py "Amps and angle encoding"` reports `summary: 1/1 byte-identical`.
3. `uv run pytest tests/test_mdtest.py -k "Amps and angle" -q` passes.
4. `./shakedown` contains no `Markdown.pl`, `ORACLE`, or `exec perl` reference.
5. `git ls-files --error-unmatch shakedown.spl` succeeds.
6. `wc -l shakedown.spl` is below the §8.2 halt threshold unless an accepted redesign updates the architecture.
7. `docs/markdown/divergences.md` is unchanged.

## Self-review

- **Spec coverage:** Covers architecture §7.2 deliverables: wrapper handoff, assembly, byte codegen helper, four source fragments, Act I reference capture, Act II paragraphs, Act III encoding/anchors, Act IV paragraph/anchor emission, strict fixture parity, no oracle stub.
- **Placeholder scan:** No "TBD", "TODO", or "similar to" placeholders are present. Tasks 6-9 intentionally describe SPL scene responsibilities rather than full scene listings because the implementation must be authored and verified incrementally against the interpreter.
- **Type/name consistency:** Plan uses existing paths and function names: `emit_speak_lines`, `scripts/strict_parity_harness.py`, `tests/test_slice1_amps_angle.py`, `src/10-act1-preprocess.spl`, `src/20-act2-block.spl`, `src/30-act3-span.spl`, `src/40-act4-emit.spl`.
