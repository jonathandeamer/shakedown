# Shakedown Architecture Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two throwaway prototypes — P1 (walking skeleton) and P2 (inline stressor) — that validate the buffered multi-phase SPL architecture committed to in `docs/superpowers/specs/2026-04-18-shakedown-architecture-outline-design.md`. The code is disposable; the evidence documents are the real deliverable.

**Architecture:** Fragment-assembled SPL in a buffered multi-phase shape. A Python build script concatenates `src/*.spl` fragments per a manifest and resolves scene labels into Roman numerals, producing `shakedown.spl`. A development-only wrapper (`./shakedown-dev`) runs the build then invokes `uv run shakespeare run shakedown.spl`. The production `./shakedown` stub (which currently delegates to the Markdown.pl oracle) is deliberately untouched during the prototype phase.

**Tech Stack:** SPL (shakespearelang interpreter, invoked via uv), Python 3.12, uv, pytest, Python stdlib (including `tomllib`).

---

## File Structure

**Created:**
- `scripts/assemble.py` — fragment assembler (ordered concatenation + scene-label resolution)
- `tests/test_assemble.py` — unit tests for the assembler
- `src/manifest.toml` — ordered fragment list
- `src/00-preamble.spl` — play title + dramatis personae
- `src/10-phase1-read.spl` — Phase 1: read stdin into a buffer (Act I)
- `src/20-phase2-block.spl` — Phase 2: block identification (Act II)
- `src/30-phase3-inline.spl` — Phase 3: inline processing + HTML emission (Act III)
- `shakedown-dev` — prototype wrapper script (build + run)
- `tests/prototype/__init__.py` — empty
- `tests/prototype/conftest.py` — shared fixtures (normalization helpers, wrapper path)
- `tests/prototype/test_p1.py` — P1 test
- `tests/prototype/test_p2.py` — P2 tests
- `tests/prototype/fixtures/p1_input.md` — P1 hand-crafted input
- `tests/prototype/fixtures/p1_expected.html` — P1 expected output
- `tests/prototype/fixtures/p2_emphasis_input.md` — P2 simple emphasis input
- `tests/prototype/fixtures/p2_emphasis_expected.html` — P2 expected output
- `tests/prototype/fixtures/p2_blockquote_input.md` — emphasis-in-blockquote input
- `tests/prototype/fixtures/p2_blockquote_expected.html` — expected output
- `tests/prototype/fixtures/p2_backtrack_input.md` — one backtracking case
- `tests/prototype/fixtures/p2_backtrack_expected.html` — expected output
- `docs/superpowers/notes/2026-04-18-p1-evidence.md` — P1 evidence
- `docs/superpowers/notes/2026-04-18-p2-evidence.md` — P2 evidence

**Modified:**
- `pyproject.toml` — add `shakespearelang` as a runtime dependency
- `.gitignore` — add `shakedown.spl` (build artifact)

**Deliberately untouched:**
- `shakedown` (stub wrapper delegating to Markdown.pl)
- `tests/test_mdtest.py`, `tests/test_binary_contract.py`, `tests/test_run_loop.py`

---

## Phase 0 — Setup

### Task 1: Declare `shakespearelang` as a runtime dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add the dependency**

Change the `dependencies` line in `pyproject.toml` from `dependencies = []` to:

```toml
dependencies = [
    "shakespearelang>=0.6",
]
```

(Use whatever version matches what's currently installed on the system — check with `~/.local/bin/shakespeare --help` or `pip show shakespearelang` if needed; `>=0.6` is a defensive lower bound.)

- [ ] **Step 2: Sync the venv**

Run: `uv sync`
Expected: install completes without error, `shakespearelang` appears in `.venv/`.

- [ ] **Step 3: Verify `uv run shakespeare` works**

Run: `uv run shakespeare --help`
Expected: help text listing `console`, `debug`, `run`.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: declare shakespearelang as runtime dependency"
```

---

### Task 2: Gitignore the build artifact

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Append the build artifact**

Add these lines to the end of `.gitignore`:

```
# Build artifact — assembled from src/ fragments by scripts/assemble.py
shakedown.spl
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: gitignore shakedown.spl build artifact"
```

---

### Task 3: Assembler — failing test for ordered concatenation

**Files:**
- Create: `tests/test_assemble.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for the src/ → shakedown.spl assembler."""

from pathlib import Path

import pytest


def test_assemble_orders_fragments_per_manifest(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.spl").write_text("fragment-a\n")
    (src / "b.spl").write_text("fragment-b\n")
    (src / "manifest.toml").write_text(
        'fragments = ["b.spl", "a.spl"]\n'
    )

    output = tmp_path / "out.spl"
    assemble(src_dir=src, manifest=src / "manifest.toml", output=output)

    assert output.read_text() == "fragment-b\nfragment-a\n"
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `uv run pytest tests/test_assemble.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts'` or `ImportError`.

---

### Task 4: Assembler — minimal implementation

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/assemble.py`

- [ ] **Step 1: Create package marker**

Write an empty `scripts/__init__.py`:

```python
```

- [ ] **Step 2: Implement the assembler**

Write `scripts/assemble.py`:

```python
"""Assemble src/*.spl fragments into shakedown.spl per manifest."""

from __future__ import annotations

import tomllib
from pathlib import Path


def assemble(src_dir: Path, manifest: Path, output: Path) -> None:
    """Concatenate fragments listed in manifest into output, in order."""
    with manifest.open("rb") as f:
        config = tomllib.load(f)

    fragments: list[str] = config["fragments"]

    parts: list[str] = []
    for name in fragments:
        parts.append((src_dir / name).read_text())

    output.write_text("".join(parts))


def main() -> None:
    root = Path(__file__).parent.parent
    assemble(
        src_dir=root / "src",
        manifest=root / "src" / "manifest.toml",
        output=root / "shakedown.spl",
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run test and confirm it passes**

Run: `uv run pytest tests/test_assemble.py::test_assemble_orders_fragments_per_manifest -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add scripts/__init__.py scripts/assemble.py tests/test_assemble.py
git commit -m "feat: add minimal src/ fragment assembler"
```

---

### Task 5: Assembler — failing test for scene-label resolution

**Files:**
- Modify: `tests/test_assemble.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_assemble.py`:

```python
def test_assemble_resolves_scene_labels_to_roman_within_acts(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "act1.spl").write_text(
        "Act I: The first act.\n"
        "Scene @READ: Reading input.\n"
        "Scene @DONE: Finished.\n"
    )
    (src / "act2.spl").write_text(
        "Act II: The second act.\n"
        "Scene @START: Entry point.\n"
        "Let us proceed to scene @START.\n"
    )
    (src / "manifest.toml").write_text(
        'fragments = ["act1.spl", "act2.spl"]\n'
    )

    output = tmp_path / "out.spl"
    assemble(src_dir=src, manifest=src / "manifest.toml", output=output)

    result = output.read_text()
    assert "Scene I: Reading input." in result
    assert "Scene II: Finished." in result
    assert "Scene I: Entry point." in result
    assert "Let us proceed to scene I." in result
    assert "@READ" not in result
    assert "@DONE" not in result
    assert "@START" not in result


def test_assemble_scene_label_collision_within_act_raises(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "act1.spl").write_text(
        "Act I: Duplicate label act.\n"
        "Scene @FOO: First.\n"
        "Scene @FOO: Second.\n"
    )
    (src / "manifest.toml").write_text(
        'fragments = ["act1.spl"]\n'
    )

    output = tmp_path / "out.spl"
    with pytest.raises(ValueError, match="@FOO"):
        assemble(src_dir=src, manifest=src / "manifest.toml", output=output)
```

- [ ] **Step 2: Run tests and confirm the new ones fail**

Run: `uv run pytest tests/test_assemble.py -v`
Expected: first test still PASSes; `test_assemble_resolves_scene_labels_to_roman_within_acts` and `test_assemble_scene_label_collision_within_act_raises` FAIL.

---

### Task 6: Assembler — implement scene-label resolution

**Files:**
- Modify: `scripts/assemble.py`

- [ ] **Step 1: Replace `assemble` with a version that resolves labels**

Replace the body of `assemble` and add a helper `_resolve_scene_labels`:

```python
"""Assemble src/*.spl fragments into shakedown.spl per manifest."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path


_ROMAN_ONES = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
_ROMAN_TENS = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
_ROMAN_HUNDREDS = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]


def _int_to_roman(n: int) -> str:
    if n < 1 or n >= 1000:
        raise ValueError(f"scene number out of range: {n}")
    return _ROMAN_HUNDREDS[n // 100] + _ROMAN_TENS[(n // 10) % 10] + _ROMAN_ONES[n % 10]


_ACT_RE = re.compile(r"^\s*Act\s+[IVXLCDM]+\s*:", re.MULTILINE)
_SCENE_DECL_RE = re.compile(r"Scene\s+@([A-Z_][A-Z0-9_]*)\s*:")
_SCENE_REF_RE = re.compile(r"scene\s+@([A-Z_][A-Z0-9_]*)")


def _resolve_scene_labels(source: str) -> str:
    """Replace `@LABEL` scene references with Roman numerals, act-local."""
    # Split source into segments by Act headers, keeping the headers.
    # Labels are resolved per act.
    act_positions = [m.start() for m in _ACT_RE.finditer(source)]
    if not act_positions:
        # No acts: treat the whole source as a single scope.
        return _resolve_in_segment(source)

    segments: list[str] = []
    # Prelude before the first Act header — typically preamble with no scenes.
    segments.append(source[: act_positions[0]])
    for idx, start in enumerate(act_positions):
        end = act_positions[idx + 1] if idx + 1 < len(act_positions) else len(source)
        segments.append(_resolve_in_segment(source[start:end]))

    return "".join(segments)


def _resolve_in_segment(segment: str) -> str:
    """Resolve labels for a single act segment: declarations in order get I, II, III, ..."""
    label_to_roman: dict[str, str] = {}
    counter = 0

    def assign(match: re.Match[str]) -> str:
        nonlocal counter
        label = match.group(1)
        if label in label_to_roman:
            raise ValueError(f"duplicate scene label @{label} in act")
        counter += 1
        label_to_roman[label] = _int_to_roman(counter)
        return f"Scene {label_to_roman[label]}:"

    # First pass: assign Roman numerals to declarations in order.
    with_decls_resolved = _SCENE_DECL_RE.sub(assign, segment)

    # Second pass: resolve references using the assignment table.
    def lookup(match: re.Match[str]) -> str:
        label = match.group(1)
        if label not in label_to_roman:
            raise ValueError(f"unresolved scene reference @{label}")
        return f"scene {label_to_roman[label]}"

    return _SCENE_REF_RE.sub(lookup, with_decls_resolved)


def assemble(src_dir: Path, manifest: Path, output: Path) -> None:
    """Concatenate fragments per manifest and resolve scene labels."""
    with manifest.open("rb") as f:
        config = tomllib.load(f)

    fragments: list[str] = config["fragments"]
    combined = "".join((src_dir / name).read_text() for name in fragments)
    resolved = _resolve_scene_labels(combined)
    output.write_text(resolved)


def main() -> None:
    root = Path(__file__).parent.parent
    assemble(
        src_dir=root / "src",
        manifest=root / "src" / "manifest.toml",
        output=root / "shakedown.spl",
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run tests and confirm all pass**

Run: `uv run pytest tests/test_assemble.py -v`
Expected: all three tests PASS.

- [ ] **Step 3: Commit**

```bash
git add scripts/assemble.py tests/test_assemble.py
git commit -m "feat: resolve scene labels to Roman numerals per act"
```

---

### Task 7: Smoke fragment — hello world SPL

**Files:**
- Create: `src/manifest.toml`
- Create: `src/00-preamble.spl`
- Create: `src/99-smoke.spl`

- [ ] **Step 1: Write the manifest**

Write `src/manifest.toml`:

```toml
# Ordered list of fragments assembled into shakedown.spl.
# During the prototype phase this manifest evolves as phases are added.
fragments = [
    "00-preamble.spl",
    "99-smoke.spl",
]
```

- [ ] **Step 2: Write the preamble fragment**

Write `src/00-preamble.spl`:

```
The Shakedown Prototype.

Romeo, a reader of input.
Juliet, a speaker of output.
```

(Title ends with a period, dramatis personae one per line.)

- [ ] **Step 3: Write a hello-world smoke fragment**

Write `src/99-smoke.spl`:

```
                    Act I: Hello.

                    Scene @GREET: Speak.

[Enter Romeo and Juliet]

Romeo: You are as good as the sum of a big big big big big big cat and twice the sum of a big cat and a cat.
Juliet: Speak your mind!
Romeo: You are as good as the sum of a big big big big big big big big cat and a big cat.
Juliet: Speak your mind!

[Exeunt]
```

(Two pushes of numeric values via `Speak your mind!`. The exact ASCII output doesn't matter — the smoke test just verifies the build → run pipeline works end-to-end without error. If either arithmetic phrase trips over an SPL parsing detail during manual run, substitute any known-legal value phrase from `docs/spl/style-lexicon.md`.)

- [ ] **Step 4: Assemble and run manually to confirm the pipeline works**

Run:
```bash
uv run python scripts/assemble.py
uv run shakespeare run shakedown.spl
```
Expected: exits cleanly, prints two characters to stdout.

- [ ] **Step 5: Commit**

```bash
git add src/
git commit -m "feat: add preamble and smoke SPL fragments for build pipeline check"
```

---

### Task 8: Prototype wrapper — `./shakedown-dev`

**Files:**
- Create: `shakedown-dev`

- [ ] **Step 1: Write the wrapper**

Write `shakedown-dev`:

```bash
#!/usr/bin/env bash
# Prototype wrapper: rebuild shakedown.spl from src/ then execute via uv.
# This is the shape the final ./shakedown will take. It exists as a
# separate entry point during the prototype phase so the stub ./shakedown
# (currently delegating to Markdown.pl) keeps the existing mdtest suite
# passing.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"

uv run --project "$DIR" python "$DIR/scripts/assemble.py"
exec uv run --project "$DIR" shakespeare run "$DIR/shakedown.spl"
```

- [ ] **Step 2: Mark it executable**

Run: `chmod +x shakedown-dev`
Expected: no output; file is now executable.

- [ ] **Step 3: Smoke-test the wrapper**

Run: `echo "" | ./shakedown-dev`
Expected: exits cleanly, prints two characters to stdout.

- [ ] **Step 4: Commit**

```bash
git add shakedown-dev
git commit -m "feat: add shakedown-dev prototype wrapper"
```

---

## Phase 1 — Prototype 1: Walking Skeleton

**Goal of this phase:** prove Option B end-to-end with three phases, for the simplest meaningful content: two paragraphs, one containing a code span.

### Task 9: P1 test scaffolding — fixture and failing test

**Files:**
- Create: `tests/prototype/__init__.py`
- Create: `tests/prototype/conftest.py`
- Create: `tests/prototype/fixtures/p1_input.md`
- Create: `tests/prototype/fixtures/p1_expected.html`
- Create: `tests/prototype/test_p1.py`

- [ ] **Step 1: Empty package marker**

Write an empty `tests/prototype/__init__.py`:

```python
```

- [ ] **Step 2: Write shared conftest**

Write `tests/prototype/conftest.py`:

```python
"""Shared helpers for prototype fixture tests."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "shakedown-dev"
FIXTURES = Path(__file__).parent / "fixtures"


def normalize(text: str) -> str:
    """Trim each line, collapse consecutive blank lines, strip whole result."""
    lines = text.split("\n")
    out: list[str] = []
    prev_blank = False
    for line in lines:
        line = line.strip()
        if line == "":
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(line)
            prev_blank = False
    return "\n".join(out).strip()
```

- [ ] **Step 3: Write the P1 input fixture**

Write `tests/prototype/fixtures/p1_input.md`:

```
First paragraph with `code` in it.

Second paragraph.
```

- [ ] **Step 4: Write the P1 expected fixture**

Write `tests/prototype/fixtures/p1_expected.html`:

```
<p>First paragraph with <code>code</code> in it.</p>

<p>Second paragraph.</p>
```

- [ ] **Step 5: Write the failing test**

Write `tests/prototype/test_p1.py`:

```python
"""Prototype 1 — walking skeleton: paragraphs + code spans."""

import subprocess

from tests.prototype.conftest import FIXTURES, WRAPPER, normalize


def test_p1_walking_skeleton() -> None:
    input_md = (FIXTURES / "p1_input.md").read_text()
    expected = (FIXTURES / "p1_expected.html").read_text()

    result = subprocess.run(
        [str(WRAPPER)],
        input=input_md,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"./shakedown-dev exited {result.returncode}\nstderr:\n{result.stderr}"
    )

    assert normalize(result.stdout) == normalize(expected), (
        f"output mismatch\n--- expected\n{normalize(expected)}\n"
        f"+++ actual\n{normalize(result.stdout)}"
    )
```

- [ ] **Step 6: Run test, confirm it fails**

Run: `uv run pytest tests/prototype/test_p1.py -v`
Expected: FAIL (the smoke fragment doesn't process stdin, so output is wrong).

---

### Task 10: Replace the smoke fragment with the three phase fragments (empty shells)

**Files:**
- Modify: `src/manifest.toml`
- Delete: `src/99-smoke.spl`
- Create: `src/10-phase1-read.spl`
- Create: `src/20-phase2-block.spl`
- Create: `src/30-phase3-inline.spl`

- [ ] **Step 1: Delete the smoke fragment**

Run: `git rm src/99-smoke.spl`
Expected: file removed.

- [ ] **Step 2: Update the manifest**

Replace `src/manifest.toml` with:

```toml
# Ordered list of fragments assembled into shakedown.spl.
# During Prototype 1 we have exactly three processing phases plus preamble.
fragments = [
    "00-preamble.spl",
    "10-phase1-read.spl",
    "20-phase2-block.spl",
    "30-phase3-inline.spl",
]
```

- [ ] **Step 3: Create empty-shell Act I (Phase 1)**

Write `src/10-phase1-read.spl`:

```
                    Act I: Read stdin into a buffer.

                    Scene @READ: Placeholder — replaced in later task.

[Enter Romeo and Juliet]

[Exeunt]
```

- [ ] **Step 4: Create empty-shell Act II (Phase 2)**

Write `src/20-phase2-block.spl`:

```
                    Act II: Identify blocks from the buffer.

                    Scene @BLOCK_START: Placeholder — replaced in later task.

[Enter Romeo and Juliet]

[Exeunt]
```

- [ ] **Step 5: Create empty-shell Act III (Phase 3)**

Write `src/30-phase3-inline.spl`:

```
                    Act III: Inline processing and HTML emission.

                    Scene @INLINE_START: Placeholder — replaced in later task.

[Enter Romeo and Juliet]

[Exeunt]
```

- [ ] **Step 6: Verify the shells assemble and run without error**

Run:
```bash
echo "" | ./shakedown-dev
```
Expected: exits cleanly, produces no output (three empty acts).

- [ ] **Step 7: Commit**

```bash
git add src/ tests/prototype/
git commit -m "test: add P1 fixture + three-act fragment shells"
```

---

### Task 11: Phase 1 — read stdin into a buffer

**Files:**
- Modify: `src/10-phase1-read.spl`

**Key SPL techniques used:**
- `Open your mind!` reads one character from stdin; returns −1 at EOF
- `Remember X!` pushes onto the listener's stack (LIFO)
- Stack pushes in read order produce a reversed-order buffer; Phase 2 will reverse it back by popping into a second stack
- EOF check: `Are you as good as a pig?` (−1 == "a pig")

- [ ] **Step 1: Replace Act I with a working read-to-buffer loop**

Replace the contents of `src/10-phase1-read.spl` with:

```
                    Act I: Read stdin into a buffer.

                    Scene @READ: Read one character into Romeo and push it.

[Enter Romeo and Juliet]

Juliet: Open your mind!
Romeo: Are you as good as a pig?
Juliet: If so, let us proceed to scene @DONE.
Juliet: Remember yourself!
Juliet: Let us return to scene @READ.

                    Scene @DONE: End of Act I.

[Exeunt]
```

Notes:
- `Juliet: Open your mind!` → Romeo = next char (or −1 at EOF).
- `Romeo: Are you as good as a pig?` → sets the global boolean; `a pig` = −1.
- `If so, let us proceed to scene @DONE.` → jump out if EOF.
- `Juliet: Remember yourself!` → pushes Romeo's value onto Romeo's own stack.

After Act I falls through, Romeo's stack contains the input in reverse order (last char on top).

- [ ] **Step 2: Verify Act I builds and runs without error**

Run:
```bash
echo "hi" | ./shakedown-dev
```
Expected: exits cleanly, no output (nothing emits yet). If any SPL error appears, fix before continuing.

- [ ] **Step 3: Commit**

```bash
git add src/10-phase1-read.spl
git commit -m "feat(p1): Phase 1 reads stdin into Romeo's stack"
```

---

### Task 12: Phase 2 — paragraph identification into intermediate buffer

**Files:**
- Modify: `src/00-preamble.spl`
- Modify: `src/20-phase2-block.spl`

**Design for P1 intermediate representation:**
- Romeo holds the reversed-input buffer on his stack.
- A second character (Hamlet) will hold a forward-order buffer with block markers interleaved, pushed onto Hamlet's stack during Phase 2.
- Block marker encoding (prototype-level, may change for P2): code point 1 = paragraph open, code point 2 = paragraph close. Real characters are encoded as their ASCII values (all ≥ 32 except for newline = 10).
- Paragraph detection: consume chars from Romeo's stack (in reverse order, so need to reverse again into a third holder first) — actually, simpler pattern: Phase 2 pops Romeo, which yields input in forward order (because push-reverse + pop-reverse = forward). That's the magic of the two-step LIFO buffer. It also destroys Romeo's buffer, which is fine since we're moving to the next phase.

Pattern: a paragraph is a non-blank-line run separated from other paragraphs by one or more blank lines (two consecutive newlines). For P1, we need to detect:
- Start of non-blank content → emit `1` (paragraph open)
- Single newline inside a paragraph → keep as space or leave newline
- Double newline → emit `2` (close), then on next non-blank → emit `1`

For prototype simplicity: emit exactly one paragraph open at start, one paragraph close at EOF, and emit paragraph-close-then-open when a blank line is seen.

- [ ] **Step 1: Add Hamlet to the cast**

Edit `src/00-preamble.spl` to:

```
The Shakedown Prototype.

Romeo, a reader of input.
Juliet, a speaker of output.
Hamlet, a holder of block-annotated buffer.
```

- [ ] **Step 2: Replace Act II with a discovery-driven paragraph-splitter**

This step is discovery work. The starting scaffold below gives you the shape (seed → consume → emit → finish). The `@MAYBE_BLANK` scene and its lookahead/marker-insertion logic are the part you discover — pick the simplest approach that makes the P1 test pass in Step 4, and record what you chose in the evidence doc.

Starting scaffold for `src/20-phase2-block.spl`:

```
                    Act II: Identify paragraphs.

                    Scene @SEED: Push paragraph-open marker (value 1) onto Hamlet's stack.

[Enter Romeo and Hamlet]

Romeo: You are as good as a cat!
Hamlet: Remember yourself!

                    Scene @CONSUME: Pop one char from Romeo into his value; process.

Romeo: Recall your past.
Hamlet: Are you as good as nothing?
Romeo: If so, let us proceed to scene @FINISH.

                    Scene @EMIT_CHAR: Push current char onto Hamlet's stack as a normal char.

Hamlet: You are as good as Romeo.
Romeo: Remember yourself!
Hamlet: Let us return to scene @CONSUME.

                    Scene @FINISH: Push paragraph-close marker (value 2).

Hamlet: You are as good as the sum of a cat and a cat.
Romeo: Remember yourself!

[Exeunt]
```

This scaffold buffers every input char but emits no paragraph boundary beyond the leading open and trailing close — so a single-paragraph input will pass the one-paragraph case but the two-paragraph P1 fixture won't. Your job in Step 4 is to add the blank-line detection that splits paragraphs.

Options to consider (pick one; evidence doc records which and why):
- **Newline-counter on Romeo**: track consecutive newlines seen in a helper character's value; when the count hits 2, emit close-then-open markers.
- **Single-blank-is-boundary heuristic**: simpler to implement but may fail some fixtures later; acceptable for P1 if noted.
- **Recall-based pushback**: harder, but matches the eventual full architecture.

Marker value conventions:
- `a cat` = 1 (paragraph-open marker)
- `the sum of a cat and a cat` = 2 (paragraph-close marker)

You'll also need a numeric constant for newline (ASCII 10) in the comparison check. Derive the value phrase yourself using `docs/spl/style-lexicon.md` — record the phrase you used in the evidence doc.

- [ ] **Step 3: Verify the test now emits *something*, even if wrong**

Run: `uv run pytest tests/prototype/test_p1.py -v`
Expected: still FAILs, but the failure message should show actual stdout content (wrong but present). If SPL raises a runtime error, fix before continuing.

- [ ] **Step 4: Iterate on Phase 2 until paragraph markers are correct**

Repeat this loop:
1. Inspect the failing diff in the pytest output.
2. Adjust `src/20-phase2-block.spl`.
3. Re-run `uv run pytest tests/prototype/test_p1.py -v`.

Success at this step: Hamlet's stack contains a forward-order stream of `[paragraph-open, chars, paragraph-close, paragraph-open, chars, paragraph-close]`. Phase 3 will verify this by consuming and emitting.

- [ ] **Step 5: Commit Phase 2**

```bash
git add src/00-preamble.spl src/20-phase2-block.spl
git commit -m "feat(p1): Phase 2 inserts paragraph markers into Hamlet's buffer"
```

---

### Task 13: Phase 3 — inline processing + HTML emission

**Files:**
- Modify: `src/00-preamble.spl`
- Modify: `src/30-phase3-inline.spl`

**Design:**
- Phase 3 consumes Hamlet's buffer (which was built push-reversed in Phase 2, so pop yields reversed order — need a rereverse into a fourth holder, or design Phase 2 to push in the correct reversed order so Phase 3 pops forward; the implementer decides which).
- When a paragraph-open marker (value 1) is popped: emit literal `<p>`.
- When a paragraph-close marker (value 2) is popped: emit literal `</p>\n\n`.
- When a backtick character is popped: toggle a "inside code span" flag (held in another character's value) and emit `<code>` or `</code>`.
- Otherwise: emit the char via `Speak your mind!`.

- [ ] **Step 1: Add the inline-state character to the cast**

Edit `src/00-preamble.spl` to:

```
The Shakedown Prototype.

Romeo, a reader of input.
Juliet, a speaker of output.
Hamlet, a holder of block-annotated buffer.
Ophelia, a tracker of inline state.
```

- [ ] **Step 2: Replace Act III with a working inline + emit pass**

Replace `src/30-phase3-inline.spl` with a scene structure that:

1. Reverses Hamlet's buffer into another character's stack so pops yield forward order (if Phase 2 didn't already arrange this).
2. Loops: pops one value from that stack, branches on value (1 → `<p>`, 2 → `</p>\n\n`, backtick → toggle + emit `<code>` or `</code>`, else → Speak).
3. Exits when the stack is empty.

Implement the simplest version that makes the test pass. Emit each literal character string (`<`, `p`, `>`, `/`, `c`, `o`, `d`, `e`, newline) via a dedicated helper scene or inline value phrases — this is exactly the duplication problem the shared-scene pattern addresses, and whether the prototype exercises that pattern or not is one of the evidence-doc questions.

- [ ] **Step 3: Iterate until the P1 test passes**

Repeat:
1. Run: `uv run pytest tests/prototype/test_p1.py -v`.
2. Read the diff.
3. Adjust Phase 3.
4. Repeat.

Success: the test passes.

- [ ] **Step 4: Run the full test suite**

Run: `uv run pytest -v`
Expected: all tests pass, including the existing `test_mdtest.py`, `test_binary_contract.py`, `test_run_loop.py`, and the new `test_p1.py` and `test_assemble.py`.

- [ ] **Step 5: Commit Phase 3**

```bash
git add src/00-preamble.spl src/30-phase3-inline.spl
git commit -m "feat(p1): Phase 3 emits HTML for paragraphs and code spans"
```

---

### Task 14: Write Prototype 1 evidence document

**Files:**
- Create: `docs/superpowers/notes/2026-04-18-p1-evidence.md`

- [ ] **Step 1: Write the evidence document**

Write `docs/superpowers/notes/2026-04-18-p1-evidence.md` with this structure (fill in real answers from the implementation):

```markdown
# Prototype 1 Evidence — Walking Skeleton

**Date:** 2026-04-18
**Spec:** `docs/superpowers/specs/2026-04-18-shakedown-architecture-outline-design.md`
**Result:** PASS / PASS-WITH-CAVEATS / FAIL (pick one; if FAIL, stop and revisit the outline spec)

## What P1 Covered

- Phase 1: `<concrete description of how stdin was buffered>`
- Phase 2: `<concrete description of how paragraph markers were inserted>`
- Phase 3: `<concrete description of how HTML was emitted, including code spans>`

## Intermediate Representation

Describe the exact representation that survived between acts. Include:
- The buffer-holder character(s)
- The marker values used (e.g. 1 = paragraph-open, 2 = paragraph-close)
- How chars and markers were distinguished
- Stack-reversal patterns applied (how many reverses, where)

## Cast

| Character | Role |
|---|---|
| Romeo | ... |
| Juliet | ... |
| Hamlet | ... |
| Ophelia | ... |
| ... | ... |

## Stack Mechanics

- How many times was a buffer reversed? Why?
- Was the two-character trade-and-reverse pattern needed? If so, between which acts?
- Any surprises?

## Timing

- Cold `./shakedown-dev` on empty stdin: __s
- Warm (second run): __s
- On P1 fixture: __s

## Line Counts

| Fragment | Lines |
|---|---|
| 00-preamble.spl | |
| 10-phase1-read.spl | |
| 20-phase2-block.spl | |
| 30-phase3-inline.spl | |
| **assembled shakedown.spl** | |

## Surprises

Anything that was harder or easier than expected. Include both directions.

## Items Fed Forward to the Detailed Spec

List decisions that the prototype made informally and that the detailed spec must make explicitly:
- Phase count: 3 — confirm / extend to 4?
- Intermediate representation format
- Cast role assignments
- Stack-reversal convention
- Whether the shared-scene (return-address) pattern is needed

## P1 Gate Decision

- [ ] P1 passed — proceed to Prototype 2.
- [ ] P1 passed with caveats — proceed but flag in detailed spec: `<caveats>`.
- [ ] P1 failed — stop and revise `2026-04-18-shakedown-architecture-outline-design.md`. Do not continue to Phase 2.
```

- [ ] **Step 2: Fill it in with the real answers**

Edit the document to replace every `<placeholder>` and blank value with real findings from the implementation. This is the part that feeds the detailed spec — take it seriously.

- [ ] **Step 3: Commit the evidence doc**

```bash
git add docs/superpowers/notes/2026-04-18-p1-evidence.md
git commit -m "docs: add Prototype 1 evidence document"
```

---

## Gate — Evaluate P1 Before Continuing

Read the P1 evidence doc. Answer, in writing if possible:

1. Did Option B (buffered multi-phase, each phase its own act) work mechanically?
2. Is the intermediate representation something the detailed spec can sign off on, or does it feel fragile?
3. Did stack mechanics require anything that genuinely threatens the design (like unbounded reversing passes), or just verbose-but-routine patterns?

**If any answer is "no / yes / yes":** stop executing this plan. Return to the outline spec brainstorm with the evidence doc. Do **not** proceed to Phase 2.

**If all answers support continuation:** proceed to Phase 2.

---

## Phase 2 — Prototype 2: Inline Stressor

**Goal of this phase:** catch the prior-attempt's failure mode by stress-testing inline inside a blockquote and at least one Markdown.pl emphasis-backtracking edge case.

### Task 15: P2 test scaffolding — three fixtures and tests

**Files:**
- Create: `tests/prototype/fixtures/p2_emphasis_input.md`
- Create: `tests/prototype/fixtures/p2_emphasis_expected.html`
- Create: `tests/prototype/fixtures/p2_backtrack_input.md`
- Create: `tests/prototype/fixtures/p2_backtrack_expected.html`
- Create: `tests/prototype/fixtures/p2_blockquote_input.md`
- Create: `tests/prototype/fixtures/p2_blockquote_expected.html`
- Create: `tests/prototype/test_p2.py`

- [ ] **Step 1: Write the simple-emphasis fixture**

Write `tests/prototype/fixtures/p2_emphasis_input.md`:

```
A paragraph with *emphasis* and _more_.
```

Generate the expected output by running the oracle:

```bash
perl ~/markdown/Markdown.pl < tests/prototype/fixtures/p2_emphasis_input.md > tests/prototype/fixtures/p2_emphasis_expected.html
```

- [ ] **Step 2: Write the backtracking fixture**

Write `tests/prototype/fixtures/p2_backtrack_input.md`:

```
One *foo **bar* baz** here.
```

Generate the expected output:

```bash
perl ~/markdown/Markdown.pl < tests/prototype/fixtures/p2_backtrack_input.md > tests/prototype/fixtures/p2_backtrack_expected.html
```

(Record whatever Markdown.pl actually emits — that is the oracle. If the prototype cannot match it, this is a candidate divergence to document.)

- [ ] **Step 3: Write the emphasis-in-blockquote fixture**

Write `tests/prototype/fixtures/p2_blockquote_input.md`:

```
> A quoted *emphasized* sentence.
```

Generate the expected output:

```bash
perl ~/markdown/Markdown.pl < tests/prototype/fixtures/p2_blockquote_input.md > tests/prototype/fixtures/p2_blockquote_expected.html
```

- [ ] **Step 4: Write the three tests**

Write `tests/prototype/test_p2.py`:

```python
"""Prototype 2 — inline stressor: emphasis, backtracking, emphasis-in-blockquote."""

import subprocess

import pytest

from tests.prototype.conftest import FIXTURES, WRAPPER, normalize


def _run_shakedown_dev(input_md: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [str(WRAPPER)],
        input=input_md,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


@pytest.mark.parametrize(
    "name",
    ["p2_emphasis", "p2_backtrack", "p2_blockquote"],
)
def test_p2_fixture(name: str) -> None:
    input_md = (FIXTURES / f"{name}_input.md").read_text()
    expected = (FIXTURES / f"{name}_expected.html").read_text()

    rc, out, err = _run_shakedown_dev(input_md)
    assert rc == 0, f"./shakedown-dev exited {rc}\nstderr:\n{err}"

    assert normalize(out) == normalize(expected), (
        f"{name} mismatch\n--- expected\n{normalize(expected)}\n"
        f"+++ actual\n{normalize(out)}"
    )
```

- [ ] **Step 5: Run the tests and confirm they fail**

Run: `uv run pytest tests/prototype/test_p2.py -v`
Expected: all three tests FAIL (the fragments don't handle emphasis or blockquote yet).

- [ ] **Step 6: Commit scaffolding**

```bash
git add tests/prototype/
git commit -m "test: add P2 fixtures and failing tests"
```

---

### Task 16: Extend inline processor for emphasis

**Files:**
- Modify: `src/30-phase3-inline.spl`

**Design:**
- Add handling for `*` and `_` in the inline loop: toggle an emphasis-state flag (in another character's value, or reuse Ophelia), emit `<em>` or `</em>`.
- For the simple case this is equivalent to the code-span toggle pattern.
- The backtracking case is the hard one — Markdown.pl's behaviour is subtle and may or may not be reproducible in a simple toggle design.

- [ ] **Step 1: Extend Phase 3 to handle simple `*` emphasis**

Edit `src/30-phase3-inline.spl` to add `*` handling (toggle emphasis state, emit `<em>` / `</em>`).

- [ ] **Step 2: Extend Phase 3 to handle `_` emphasis**

Same pattern applied to `_`.

- [ ] **Step 3: Run the simple emphasis test, iterate until it passes**

Run: `uv run pytest tests/prototype/test_p2.py::test_p2_fixture[p2_emphasis] -v`
Iterate until PASS.

- [ ] **Step 4: Commit**

```bash
git add src/30-phase3-inline.spl
git commit -m "feat(p2): inline emphasis via toggle state"
```

---

### Task 17: Attempt to handle emphasis-backtracking

**Files:**
- Modify: `src/30-phase3-inline.spl`

- [ ] **Step 1: Attempt to make `p2_backtrack` pass**

Iterate on Phase 3 until either:
(a) The test passes, or
(b) You have convinced yourself the specific case is not reproducible in this architecture without materially changing it.

Document whichever outcome you reach — both are acceptable evidence.

- [ ] **Step 2: If (b), mark the test as an expected-divergence candidate**

Add a `pytest.mark.xfail` (with a comment naming the candidate divergence) to the `p2_backtrack` parametrize entry, and record it for `docs/markdown/divergences.md` evaluation in the evidence doc. Example:

```python
@pytest.mark.parametrize(
    "name",
    [
        "p2_emphasis",
        pytest.param(
            "p2_backtrack",
            marks=pytest.mark.xfail(
                reason="Markdown.pl emphasis backtracking — divergence candidate, see p2 evidence doc",
            ),
        ),
        "p2_blockquote",
    ],
)
```

- [ ] **Step 3: Commit**

```bash
git add src/30-phase3-inline.spl tests/prototype/test_p2.py
git commit -m "feat(p2): attempt emphasis backtracking; document result"
```

---

### Task 18: Extend the block phase to handle blockquotes

**Files:**
- Modify: `src/20-phase2-block.spl`
- Modify: `src/30-phase3-inline.spl`

**Design:**
- Phase 2 must recognise a line starting with `> ` as a blockquote line, strip the marker, and emit a new block marker value for `<blockquote>` open / close surrounding the inner paragraph.
- Phase 3 must emit `<blockquote>` and `</blockquote>` around the inner content when it encounters those new marker values.
- New marker values (suggestion; implementer picks exact): 3 = blockquote-open, 4 = blockquote-close.

- [ ] **Step 1: Extend Phase 2 to emit blockquote markers**

Edit `src/20-phase2-block.spl` to recognise `>` at the start of a line and wrap the enclosed paragraph with blockquote-open and blockquote-close markers.

- [ ] **Step 2: Extend Phase 3 to emit blockquote tags**

Edit `src/30-phase3-inline.spl` to handle the two new marker values by emitting `<blockquote>\n` and `</blockquote>\n`.

- [ ] **Step 3: Iterate on the blockquote test until it passes**

Run: `uv run pytest tests/prototype/test_p2.py::test_p2_fixture[p2_blockquote] -v`
Iterate until PASS.

- [ ] **Step 4: Run the full suite once more**

Run: `uv run pytest -v`
Expected: all tests pass (with any `xfail` from Task 17 marked as expected-to-fail).

- [ ] **Step 5: Commit**

```bash
git add src/20-phase2-block.spl src/30-phase3-inline.spl
git commit -m "feat(p2): emphasis inside blockquote via block markers + inline toggle"
```

---

### Task 19: Write Prototype 2 evidence document

**Files:**
- Create: `docs/superpowers/notes/2026-04-18-p2-evidence.md`

- [ ] **Step 1: Write the evidence document**

Write `docs/superpowers/notes/2026-04-18-p2-evidence.md`:

```markdown
# Prototype 2 Evidence — Inline Stressor

**Date:** 2026-04-18
**Spec:** `docs/superpowers/specs/2026-04-18-shakedown-architecture-outline-design.md`
**Builds on:** `docs/superpowers/notes/2026-04-18-p1-evidence.md`
**Result:** PASS / PASS-WITH-CAVEATS / PARTIAL / FAIL (pick one)

## What P2 Added

- Simple emphasis (`*`, `_`): PASS / FAIL
- Emphasis backtracking edge case: PASS / DIVERGENCE-CANDIDATE / FAIL
- Emphasis inside a blockquote: PASS / FAIL

## Did P1's Intermediate Representation Survive?

- YES — what P2 needed was already expressible.
- NO — describe exactly what changed and why.

## Block/Inline Context Handoff

Describe how the block phase communicated enough context to the inline phase for inline to render correctly inside nested structures. Specifically: how did the inline processor know it was "inside a blockquote" when it encountered the emphasis marker?

## Emphasis Backtracking Verdict

One of:
- MATCHED: the prototype reproduces Markdown.pl's output for `*foo **bar* baz**`-style input. Describe how.
- DIVERGED: the prototype does not match. Describe what it produced and why. Recommend whether to accept a divergence in `docs/markdown/divergences.md`.

## Updated Timing

Re-measure on this realistic-size program:
- Cold start: __s
- Warm: __s
- P2 blockquote fixture: __s

## Line Counts

| Fragment | P1 lines | P2 lines | Delta |
|---|---|---|---|
| 00-preamble.spl | | | |
| 10-phase1-read.spl | | | |
| 20-phase2-block.spl | | | |
| 30-phase3-inline.spl | | | |
| **assembled** | | | |

## Items Fed Forward to the Detailed Spec

Everything the detailed architecture spec now has to pin down, based on both prototypes:
- Final phase count (3 or 4)
- Final intermediate representation
- Final cast
- Whether the shared-scene (return-address) pattern is required for the real build
- List of divergence candidates discovered
- Fixture build order (which fixtures look tractable under this shape and which are at risk)

## P2 Gate Decision

- [ ] P2 passed — proceed to detailed architecture spec brainstorm.
- [ ] P2 passed with documented divergences — proceed; divergences go into the detailed spec's evaluation.
- [ ] P2 failed — stop and revisit the outline spec.
```

- [ ] **Step 2: Fill it in with real findings**

Complete every field with concrete answers from the P2 implementation.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/notes/2026-04-18-p2-evidence.md
git commit -m "docs: add Prototype 2 evidence document"
```

---

## Final — Verify and Hand Off

### Task 20: Full suite + lint + typecheck

**Files:**
- None (read-only verification)

- [ ] **Step 1: Full test suite**

Run: `uv run pytest -v`
Expected: all tests pass (with any documented `xfail` from P2 marked expected-to-fail).

- [ ] **Step 2: Lint**

Run: `uv run ruff check .`
Expected: no errors.

- [ ] **Step 3: Format check**

Run: `uv run ruff format --check .`
Expected: no changes needed.

- [ ] **Step 4: Typecheck**

Run: `uv run pyright`
Expected: no errors.

- [ ] **Step 5: Verify existing mdtest suite was not regressed**

Run: `uv run pytest tests/test_mdtest.py -v`
Expected: same pass/fail state as before the prototype work (the stub `./shakedown` is untouched, so this should be identical to the pre-prototype baseline).

---

### Task 21: Summary commit

**Files:**
- None (verification only; no new commit unless something was missed in Task 20)

- [ ] **Step 1: Confirm both evidence docs are committed**

Run: `git log --oneline -20`
Expected: commits include both `docs: add Prototype 1 evidence document` and `docs: add Prototype 2 evidence document`.

- [ ] **Step 2: Confirm working tree is clean**

Run: `git status`
Expected: `nothing to commit, working tree clean`.

- [ ] **Step 3: Hand off**

Report to the user:
- P1 result + pointer to P1 evidence doc
- P2 result + pointer to P2 evidence doc
- Any divergences flagged
- Recommendation: proceed to a detailed architecture spec brainstorm (which will use both evidence docs as inputs), or loop back to revise the outline spec if either prototype failed.

---

## What This Plan Deliberately Does Not Do

- It does not modify `./shakedown` (the stub wrapper delegating to Markdown.pl). That replacement happens after the detailed spec.
- It does not touch `tests/test_mdtest.py` or the existing fixture suite.
- It does not cut a version tag or push anything — the workflow-guardrail from the outline spec applies: no `cz bump` during prototype work.
- It does not optimise the SPL for size, cast discipline, or codegen-guide adherence. Prototypes are throwaway.
- It does not cover the detailed architecture spec, the real `shakedown.spl` implementation plan, or the run-loop prompt. Those are downstream artifacts.
