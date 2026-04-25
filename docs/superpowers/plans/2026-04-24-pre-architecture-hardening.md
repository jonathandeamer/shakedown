# Pre-Architecture Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 14 pre-architecture gaps identified in the 2026-04-24 audit by running five new SPL probes and applying evidence-driven + pure-text doc fold-back so architecture planning reads from measurement, not inference.

**Architecture:** Two sequential stages. Stage 1 writes/runs five SPL probes (mechanics assertions + timing measurements) and records results in append-only evidence docs (`verification-plan.md` buckets, pre-design-hardening note). Stage 2 folds the stage-1 evidence back into canonical architecture/markdown/performance docs and applies pure-text clarifications. Within stage 2, consolidation (2c) runs before evidence-driven edits (2a) so the latter land on the consolidated files.

**Tech Stack:** SPL (`shakespearelang` 1.2.1 via `~/.local/bin/shakespeare`), Python 3 via `uv`, pytest, bash. Existing test harness pattern at `tests/test_pre_design_probes.py` is reused. Measurement uses `/usr/bin/time` via Python `subprocess`.

**Spec:** `docs/superpowers/specs/2026-04-24-pre-architecture-hardening-design.md`

---

## Conventions

- **Probe success stdout:** every assertion-style probe emits `"<probe name>: pass\n"` and the pytest parametrize entry asserts that exact string, following the pattern at `docs/spl/probes/pre-design/reference-lookup.spl`.
- **Character emissions in SPL:** use the `Juliet: You are as good as <value>. Juliet: Speak your mind!` pattern. Values are noun-phrase arithmetic (`a big cat` = 2, `the sum of X and Y`, etc.). For strings, emit each character code separately.
- **Commit types:** new probes use `experiment:`; pytest wiring uses `test:`; Python scripts use `chore:`; doc edits use `docs:`.
- **`uv` invocation:** use `uv run` for Python/pytest. Set `UV_CACHE_DIR=/tmp/uv-cache` when timing to match `docs/performance/budget.md`.

---

## Stage 1 — Evidence

### Task 1: Count reference definitions in the largest fixture (P4 prep)

**Files:**
- Create: `scripts/count_reference_defs.py`

- [x] **Step 1: Create the script**

File: `scripts/count_reference_defs.py`

```python
"""Count Markdown reference definitions in the largest mdtest fixture.

Markdown reference definitions match this regex pattern (lifted from
Markdown.pl _StripLinkDefinitions): a line starting with up to three spaces,
followed by `[id]:`, followed by URL and optional title.
"""

from __future__ import annotations

import re
from pathlib import Path


FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Markdown Documentation - Syntax.text"
)

DEF_LINE = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*\S", re.MULTILINE)


def count_definitions(text: str) -> list[str]:
    return [m.group(1) for m in DEF_LINE.finditer(text)]


def main() -> None:
    text = FIXTURE.read_text()
    ids = count_definitions(text)
    print(f"Fixture: {FIXTURE}")
    print(f"Reference definition count: {len(ids)}")
    for identifier in ids:
        print(f"  - {identifier}")


if __name__ == "__main__":
    main()
```

- [x] **Step 2: Run it and record the count**

Run: `uv run python scripts/count_reference_defs.py`

Expected: a line `Reference definition count: N`, where N is a small positive integer. Record `N` — it is the target table size for P4. If N is below 10, pick a floor of 20 for the probe (we want to stress linear scan, not exactly match the fixture).

- [x] **Step 3: Commit**

```bash
git add scripts/count_reference_defs.py
git commit -m "chore: add reference-def counter for P4 probe scaling"
```

---

### Task 2: Build SPL synthesis generator and measurement harness

**Files:**
- Create: `scripts/generate_spl_cost_fixtures.py`
- Create: `scripts/measure_spl_cost.py`
- Create: `tests/test_measure_spl_cost.py`

- [x] **Step 1: Write the generator**

File: `scripts/generate_spl_cost_fixtures.py`

```python
"""Generate representative SPL fixtures for cost and scene-count probes.

Produces three files:
- docs/spl/probes/pre-design/spl-cost-1k.spl  (~1000 lines)
- docs/spl/probes/pre-design/spl-cost-4k.spl  (~4000 lines)
- docs/spl/probes/pre-design/scene-count.spl  (200 scenes in one act)

Line counts are approximate; each scene contributes a fixed line count so we
can target a total.

The synthesized work is a realistic mix of assignments, arithmetic, stack
pushes/pops, and intra-act gotos — not empty boilerplate. The goal is a
representative interpreter cost baseline, not a stress test.
"""

from __future__ import annotations

from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "spl" / "probes" / "pre-design"

HEADER = """SPL Cost Probe.

Romeo, a worker.
Juliet, a driver.

                    Act I: Repeated bounded work.

"""

# Each scene body contributes 6 lines:
# - 1 scene header
# - 1 enter
# - 3 work lines (assignment, remember, recall)
# - 1 exeunt
SCENE_TEMPLATE = """                    Scene {roman}: Bounded work step {n}.

[Enter Romeo and Juliet]

Juliet: You are as good as the sum of a big cat and a cat.
Juliet: Remember yourself.
Romeo: Recall your past.

[Exeunt]

"""

TAIL_TEMPLATE = """                    Scene {roman}: Terminate.

[Enter Juliet]

Juliet: You are as good as a cat.
Juliet: Speak your mind!

[Exeunt]
"""


def to_roman(n: int) -> str:
    numerals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    out = []
    for value, letter in numerals:
        while n >= value:
            out.append(letter)
            n -= value
    return "".join(out)


def build(scene_count: int) -> str:
    parts = [HEADER]
    for i in range(1, scene_count):
        parts.append(SCENE_TEMPLATE.format(roman=to_roman(i), n=i))
    parts.append(TAIL_TEMPLATE.format(roman=to_roman(scene_count)))
    return "".join(parts)


def write(path: Path, scene_count: int) -> None:
    path.write_text(build(scene_count))
    print(f"wrote {path} ({path.stat().st_size} bytes, {scene_count} scenes)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Scene count chosen so line count ≈ target:
    # 7 lines overhead + 8 lines/scene ≈ 8n lines total
    write(OUT_DIR / "spl-cost-1k.spl", scene_count=125)   # ≈ 1000 lines
    write(OUT_DIR / "spl-cost-4k.spl", scene_count=500)   # ≈ 4000 lines
    write(OUT_DIR / "scene-count.spl", scene_count=200)   # exactly 200 scenes


if __name__ == "__main__":
    main()
```

- [x] **Step 2: Write the measurement harness**

File: `scripts/measure_spl_cost.py`

```python
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
        raise RuntimeError(
            f"{path} exited {result.returncode}: {result.stderr.decode(errors='replace')}"
        )
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
```

- [x] **Step 3: Write a smoke test for the harness**

File: `tests/test_measure_spl_cost.py`

```python
"""Smoke test for scripts/measure_spl_cost.py.

Does not measure production SPL — only validates the harness runs and parses.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_measure_spl_cost_runs_on_empty_probe(tmp_path: Path) -> None:
    probe = tmp_path / "noop.spl"
    probe.write_text(
        "Noop.\n\n"
        "Juliet, a speaker.\n\n"
        "                    Act I: Noop.\n\n"
        "                    Scene I: End.\n\n"
        "[Enter Juliet]\n"
        "[Exeunt]\n"
    )

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "measure_spl_cost.py"),
         str(probe), "--runs", "2"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "first:" in result.stdout
    assert "median:" in result.stdout
```

- [x] **Step 4: Run the generator**

Run: `uv run python scripts/generate_spl_cost_fixtures.py`

Expected: three `wrote ...` lines for `spl-cost-1k.spl`, `spl-cost-4k.spl`, `scene-count.spl`.

Check with: `wc -l docs/spl/probes/pre-design/spl-cost-*.spl docs/spl/probes/pre-design/scene-count.spl`

Expected line counts: roughly 1000, 4000, 1600 (scene-count has trivial body so is ~8 lines/scene × 200 = 1600).

- [x] **Step 5: Verify generated SPL parses and runs**

Run: `uv run shakespeare run docs/spl/probes/pre-design/spl-cost-1k.spl`

Expected: exits 0, prints a single character (the final `Speak your mind!` output).

- [x] **Step 6: Run the harness smoke test**

Run: `uv run pytest tests/test_measure_spl_cost.py -q`

Expected: 1 passed.

- [x] **Step 7: Commit**

```bash
git add scripts/generate_spl_cost_fixtures.py scripts/measure_spl_cost.py \
        tests/test_measure_spl_cost.py \
        docs/spl/probes/pre-design/spl-cost-1k.spl \
        docs/spl/probes/pre-design/spl-cost-4k.spl \
        docs/spl/probes/pre-design/scene-count.spl
git commit -m "chore: add SPL cost generator and measurement harness"
```

---

### Task 3: P2 probe — emphasis two-pass mechanics

**Files:**
- Create: `docs/spl/probes/pre-design/emphasis-two-pass.spl`
- Modify: `tests/test_pre_design_probes.py`

**Probe contract:**
- Input: internal buffer representing the string `*foo **bar** baz*` (14 bytes)
- Pass 1 (strong): scan for `**` pairs, replace outer pair with `<strong>` open and close markers
- Pass 2 (emphasis): scan for remaining `*` pairs, replace outer pair with `<em>` open and close markers
- Output: `emphasis two-pass: pass\n` if the transformed buffer equals the expected byte sequence `<em>foo <strong>bar</strong> baz</em>`

The probe demonstrates the *mechanic* of ordered two-pass substitution over a buffered span. It does not implement the full emphasis feature.

- [x] **Step 1: Add the failing pytest entry**

Modify `tests/test_pre_design_probes.py`:

Current parametrize block (around line 12-19):

```python
@pytest.mark.parametrize(
    ("probe_name", "expected"),
    [
        ("reference-lookup.spl", "reference lookup: pass\n"),
        ("setext-buffering.spl", "setext buffering: pass\n"),
        ("list-state-stack.spl", "list state stack: pass\n"),
    ],
)
```

Replace with:

```python
@pytest.mark.parametrize(
    ("probe_name", "expected"),
    [
        ("reference-lookup.spl", "reference lookup: pass\n"),
        ("setext-buffering.spl", "setext buffering: pass\n"),
        ("list-state-stack.spl", "list state stack: pass\n"),
        ("emphasis-two-pass.spl", "emphasis two-pass: pass\n"),
    ],
)
```

- [x] **Step 2: Run the test — expect xfail**

Run: `uv run pytest tests/test_pre_design_probes.py -k emphasis -v`

Expected: 1 xfailed (the existing harness calls `pytest.xfail` when the probe file is missing).

- [x] **Step 3: Write the probe**

File: `docs/spl/probes/pre-design/emphasis-two-pass.spl`

Structure to follow (model after `docs/spl/probes/pre-design/reference-lookup.spl`):

1. **Dramatis personae.** Declare 3-4 characters: one to hold the input buffer byte-by-byte on their stack, one to drive transforms, one to accumulate the output. Example: `Romeo, an input buffer. Juliet, a driver. Hamlet, an output accumulator.`

2. **Act I setup.** Push the input string `*foo **bar** baz*` onto Romeo's stack in reverse order (pop order = forward byte order). Character codes:
   - `*` = 42, `f` = 102, `o` = 111, space = 32, `b` = 98, `a` = 97, `r` = 114, `z` = 122
   - Push reverse order: `*`, `z`, `a`, `b`, ` `, `*`, `*`, `r`, `a`, `b`, `*`, `*`, ` `, `o`, `o`, `f`, `*`
   - After popping, bytes come out in forward order.

3. **Pass 1 (strong substitution).** Pop bytes one at a time. When two consecutive `*` bytes are seen, emit the bytes of `<strong>` (60, 115, 116, 114, 111, 110, 103, 62) or `</strong>` (60, 47, 115, 116, 114, 111, 110, 103, 62) depending on whether we are in a strong-open or strong-close state. Maintain a single toggle (a character's value). Non-star bytes pass through unchanged. Store results in an intermediate buffer (Hamlet's stack).

4. **Pass 2 (emphasis substitution).** Pop the intermediate buffer into a second accumulator. Single `*` toggles between `<em>` (60, 101, 109, 62) and `</em>` (60, 47, 101, 109, 62).

5. **Verification scene.** Compare the final accumulator against the expected byte sequence `<em>foo <strong>bar</strong> baz</em>` (31 bytes). If all bytes match in order, proceed to the pass-emission scene. Any mismatch: the scene chain breaks and pass emission never runs (the test fails on stdout mismatch).

6. **Pass emission scene.** Print `emphasis two-pass: pass\n` one character at a time using the `Juliet: You are as good as <value>. Juliet: Speak your mind!` pattern. Character codes for the literal string `emphasis two-pass: pass\n`:
   - `e`=101, `m`=109, `p`=112, `h`=104, `a`=97, `s`=115, `i`=105, `s`=115
   - ` `=32
   - `t`=116, `w`=119, `o`=111
   - `-`=45
   - `p`=112, `a`=97, `s`=115, `s`=115
   - `:`=58
   - ` `=32
   - `p`=112, `a`=97, `s`=115, `s`=115
   - `\n`=10

   Each character is expressed as a noun phrase. For example:
   - 32 = `a big big big big big cat` (2^5)
   - 101 = `the sum of a big big big big big big cat and the sum of a big big big big big cat and the sum of a big big cat and a cat` (64 + 32 + 4 + 1)
   - 10 = `a big big big cat` = 8, plus... 10 = 8+2 = `the sum of a big big big cat and a big cat`

   Follow `reference-lookup.spl` lines 92-137 as the template for building these expressions.

- [x] **Step 4: Run the test — expect pass**

Run: `uv run pytest tests/test_pre_design_probes.py -k emphasis -v`

Expected: 1 passed.

- [x] **Step 5: Commit**

```bash
git add docs/spl/probes/pre-design/emphasis-two-pass.spl \
        tests/test_pre_design_probes.py
git commit -m "experiment: add emphasis two-pass mechanics probe (P2)"
```

---

### Task 4: P3 probe — nested-dispatch mechanics

**Files:**
- Create: `docs/spl/probes/pre-design/nested-dispatch.spl`
- Modify: `tests/test_pre_design_probes.py`

**Probe contract:**
- Demonstrates: a dispatcher can enter an outer frame (labelled `blockquote`), push a frame sentinel, enter an inner frame (labelled `list`) while the outer remains on the stack, emit content inside the inner, pop back to the outer, and close both.
- Output: `nested dispatch: pass\n` if the emit sequence matches the expected trace. The probe chooses its own simple trace — the minimum that proves frame state is preserved across the nest boundary.

**Expected emit trace:** `BQ-in, LI-in, content, LI-out, BQ-out`, encoded as the 5-byte sequence `(` `[` `.` `]` `)` (ASCII: 40, 91, 46, 93, 41). This is simpler than emitting full HTML tags byte-by-byte and still proves the frame mechanics.

- [x] **Step 1: Add the failing pytest entry**

Modify `tests/test_pre_design_probes.py` parametrize list. Append the new entry after the P2 entry:

```python
        ("emphasis-two-pass.spl", "emphasis two-pass: pass\n"),
        ("nested-dispatch.spl", "nested dispatch: pass\n"),
```

- [x] **Step 2: Run the test — expect xfail**

Run: `uv run pytest tests/test_pre_design_probes.py -k nested -v`

Expected: 1 xfailed.

- [x] **Step 3: Write the probe**

File: `docs/spl/probes/pre-design/nested-dispatch.spl`

Structure:

1. **Dramatis personae.** `Romeo, a frame stack. Juliet, a driver. Hamlet, an output accumulator.`

2. **Act I setup.** Romeo's stack represents the frame stack. Push a sentinel `1` to mark blockquote-frame open, then `2` to mark list-frame open. (Values chosen so 0 can be the empty-frame sentinel.)

3. **Open outer frame scene.** Emit `(` (ASCII 40). Push sentinel `1` onto Romeo's stack.

4. **Open inner frame scene.** Emit `[` (ASCII 91). Push sentinel `2` onto Romeo's stack.

5. **Content emission scene.** Emit `.` (ASCII 46). This represents the innermost content being emitted inside nested context.

6. **Close inner frame scene.** Pop Romeo's top-of-stack. Verify popped value is `2` via a question + conditional goto — if mismatch, jump to a failure scene. If match, emit `]` (ASCII 93).

7. **Close outer frame scene.** Pop Romeo's top-of-stack. Verify popped value is `1` via a question + conditional goto. If match, emit `)` (ASCII 41).

8. **Pass emission scene.** Print `nested dispatch: pass\n`. Character codes:
   - `n`=110, `e`=101, `s`=115, `t`=116, `e`=101, `d`=100
   - ` `=32
   - `d`=100, `i`=105, `s`=115, `p`=112, `a`=97, `t`=116, `c`=99, `h`=104
   - `:`=58
   - ` `=32
   - `p`=112, `a`=97, `s`=115, `s`=115
   - `\n`=10

   Note: bytes `(` `[` `.` `]` `)` from the frame scenes land on stdout BEFORE the `pass` message, so the final stdout will be `([.])nested dispatch: pass\n`. Adjust the pytest expected string to match, OR sink the frame-sequence bytes to a side character's stack and emit `nested dispatch: pass\n` only if all five were captured in order. Choose the second approach: accumulate frame bytes on Hamlet's stack, verify after each frame operation, and emit only the final pass string to stdout.

   **Decision:** use the accumulator approach so stdout is exactly `nested dispatch: pass\n`. This keeps the test assertion simple and matches the other probes' convention.

- [x] **Step 4: Run the test — expect pass**

Run: `uv run pytest tests/test_pre_design_probes.py -k nested -v`

Expected: 1 passed.

- [x] **Step 5: Commit**

```bash
git add docs/spl/probes/pre-design/nested-dispatch.spl \
        tests/test_pre_design_probes.py
git commit -m "experiment: add nested-dispatch mechanics probe (P3)"
```

---

### Task 5: P4 probe — reference-lookup at fixture scale

**Files:**
- Create: `docs/spl/probes/pre-design/reference-lookup-scale.spl`
- Modify: `tests/test_pre_design_probes.py`

**Probe contract:**
- Extends the existing `reference-lookup.spl` to a larger lookup table.
- Target size: `N = max(count_reference_defs result, 20)` — determined by Task 1's output.
- Input: N label/target pairs seeded onto a stack. 10 lookup queries: 5 that hit, 5 that miss.
- Output: `reference lookup scale: pass\n` if all lookups return the expected values.
- This probe is an assertion probe (pass/fail) but it is also timed by the harness in Task 8 to confirm linear scan is tractable.

- [x] **Step 1: Add the failing pytest entry**

Append to parametrize list:

```python
        ("nested-dispatch.spl", "nested dispatch: pass\n"),
        ("reference-lookup-scale.spl", "reference lookup scale: pass\n"),
```

- [x] **Step 2: Run the test — expect xfail**

Run: `uv run pytest tests/test_pre_design_probes.py -k scale -v`

Expected: 1 xfailed.

- [x] **Step 3: Write the probe**

File: `docs/spl/probes/pre-design/reference-lookup-scale.spl`

Structure (model after `reference-lookup.spl`):

1. Retrieve `N` from Task 1. If below 20, use 20. This keeps the table meaningful.
2. Dramatis personae: `Romeo, a reference table. Juliet, a probe driver. Hamlet, a temporary table.` (same as existing probe).
3. **Setup scene.** Push N label/target pairs onto Romeo's stack. Labels can be small integers (1..N), targets can be `label * 2` for easy verification.
4. **Lookup scenes.** For each of 10 queries — 5 labels that are present (pick 1, N/4, N/2, 3N/4, N) and 5 that are absent (pick N+1, N+2, ..., N+5) — run the stack-walk pattern from the existing probe:
   - Pop each pair; if label matches query, store target and continue popping the rest while preserving them on Hamlet's stack; if no match by end of stack, target is -1 (sentinel for "missing").
   - Verify: matched queries return expected `label * 2`; absent queries return -1.
   - After each query, restore Romeo's stack from Hamlet.
5. **Pass emission scene.** Emit `reference lookup scale: pass\n` character-by-character.

- [x] **Step 4: Run the test — expect pass**

Run: `uv run pytest tests/test_pre_design_probes.py -k scale -v`

Expected: 1 passed.

- [x] **Step 5: Commit**

```bash
git add docs/spl/probes/pre-design/reference-lookup-scale.spl \
        tests/test_pre_design_probes.py
git commit -m "experiment: add reference-lookup scale probe (P4)"
```

---

### Task 6: Measure P1 (SPL cost at realistic size) → verification-plan B14

**Files:**
- Modify: `docs/verification-plan.md`

- [x] **Step 1: Run the 1k cold measurement**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py docs/spl/probes/pre-design/spl-cost-1k.spl --runs 5`

Expected output format:

```
file: docs/spl/probes/pre-design/spl-cost-1k.spl
runs: 5
first: X.XXXs
median: X.XXXs
all: ['X.XXX', 'X.XXX', ...]
```

Record all four lines verbatim.

- [x] **Step 2: Run the 4k cold measurement**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py docs/spl/probes/pre-design/spl-cost-4k.spl --runs 5`

Record output verbatim.

- [x] **Step 3: Append B14 to verification-plan.md**

Modify `docs/verification-plan.md`. After the existing `### B13 — Oracle mechanics map` subsection and before `## Bucket C`, insert a new subsection:

```markdown
### B14 — Current-repo SPL cost at realistic size

- **Command:**
  ```
  UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py \
      docs/spl/probes/pre-design/spl-cost-1k.spl --runs 5
  UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py \
      docs/spl/probes/pre-design/spl-cost-4k.spl --runs 5
  ```
- **Purpose:** anchor a current-repo SPL cost baseline at realistic port size. The only prior numbers were interpreter startup (~0.1s) and the `./shakedown-dev` prototype (~5s on ~372 lines). The prior attempt's 17–26s cold / 2–3s warm numbers are retrospective evidence from a prior codebase and do not transfer.
- **Observed (2026-04-24):**

  1k fixture:
  ```
  <paste step 1 output verbatim>
  ```

  4k fixture:
  ```
  <paste step 2 output verbatim>
  ```

- **Disposition:** Each subprocess invocation is a fresh interpreter — every run pays cold startup. The first-run and median timings are therefore both cold-run costs. No warm reuse is measured because the SPL CLI has no persistent-process mode (`docs/verification-plan.md` B7). Architecture planning should treat these numbers as the current-repo baseline for shakespeare-run cost at 1k and 4k lines, and should re-measure on the first realistic production-sized SPL build before making performance-sensitive decisions.
```

- [x] **Step 4: Commit**

```bash
git add docs/verification-plan.md
git commit -m "docs: record B14 current-repo SPL cost baselines"
```

---

### Task 7: Measure P5 (scene-count-per-act) → verification-plan B18

**Files:**
- Modify: `docs/verification-plan.md`

- [x] **Step 1: Measure scene-count probe**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py docs/spl/probes/pre-design/scene-count.spl --runs 5`

Record output verbatim.

- [x] **Step 2: Append B18 to verification-plan.md**

Modify `docs/verification-plan.md`. After the B14 subsection just added, insert:

```markdown
### B18 — Scene-count-per-act baseline

- **Command:**
  ```
  UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py \
      docs/spl/probes/pre-design/scene-count.spl --runs 5
  ```
- **Purpose:** confirm whether scene count within one act is a significant cost driver. The prior attempt reached ~130 scenes in one act; the 200-scene probe provides headroom evidence. Act-local gotos force the main loop into one act, so this number bounds how many distinct dispatch targets a single-act architecture can sustain.
- **Observed (2026-04-24):**

  ```
  <paste step 1 output verbatim>
  ```

- **Disposition:** Compare to B14's 4k-line cost. If the scene-count probe runs comparably to a 4k-line generated SPL (~1600 lines but 200 scenes), scene count is not the dominant cost driver and ~130-scene prior-attempt architectures had headroom. If it runs materially slower per line, scene count matters and architecture planning should account for it.
```

- [x] **Step 3: Commit**

```bash
git add docs/verification-plan.md
git commit -m "docs: record B18 scene-count-per-act baseline"
```

---

### Task 8: Measure P4 (reference-lookup at fixture scale) → verification-plan B17

**Files:**
- Modify: `docs/verification-plan.md`

- [x] **Step 1: Measure the P4 probe**

Run: `UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py docs/spl/probes/pre-design/reference-lookup-scale.spl --runs 5`

Record output verbatim.

- [x] **Step 2: Append B17 to verification-plan.md**

Modify `docs/verification-plan.md`. After the B18 subsection, insert (B17 goes after B18 in order here — order is by completion, not numeric; or swap — order numerically for readability):

Insert between B14 and B18 (so they end up B14, B17, B18 in numeric order):

```markdown
### B17 — Reference-lookup at fixture scale

- **Command:**
  ```
  UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py \
      docs/spl/probes/pre-design/reference-lookup-scale.spl --runs 5
  ```
- **Purpose:** confirm the stack-backed linear scan remains tractable at a reference-definition count scaled to (or exceeding) the largest mdtest fixture. The existing `reference-lookup.spl` probe proves mechanics at small N; B17 proves cost at N = <value from Task 1>.
- **Observed (2026-04-24):**

  ```
  <paste step 1 output verbatim>
  ```

- **Disposition:** Architecture planning can lean on stack-backed linear reference lookup if this timing is within budget for a single-fixture run. If the probe runs materially slower than the 1k-line B14 baseline, planning should consider an alternate lookup structure (indexed or hash-like) and move reference lookup upward in architectural risk.
```

Re-check ordering in the file: after this edit, sections should appear B13, B14, B17, B18, then Bucket C.

- [x] **Step 3: Commit**

```bash
git add docs/verification-plan.md
git commit -m "docs: record B17 reference-lookup scale baseline"
```

---

### Task 9: Extend pre-design-hardening decision register

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`

- [x] **Step 1: Append probe rows to decision register**

Modify `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`. Find the "Final Pre-Design Decision Register" table. After the last row, append:

```markdown
| P1: SPL cost at 1k/4k | closed (measured) | `spl-cost-1k.spl` + `spl-cost-4k.spl` via `measure_spl_cost.py` | Budget ≤ B14's observed numbers for performance-sensitive decisions; re-measure on first realistic port build. |
| P2: emphasis two-pass mechanics | closed | `emphasis-two-pass.spl` | Parity design should implement strong-then-emphasis substitution over a buffered span. |
| P3: nested-dispatch mechanics | closed | `nested-dispatch.spl` | Recursive dispatch with frame-sentinel stack is a supported mechanic; architecture planning may rely on it. |
| P4: reference-lookup at fixture scale | closed | `reference-lookup-scale.spl` + B17 timing | Stack-backed linear scan is tractable at fixture scale; reconsider only if B17 shows alarm. |
| P5: scene-count-per-act | closed | `scene-count.spl` + B18 timing | Single-act scene-count is not a dominant cost driver at ~200 scenes (if B18 confirms); architecture planning may extend prior-attempt's ~130-scene pattern with headroom. |
```

For any row where the observed result is NOT "closed" (e.g., probe fails, timing alarming), change the status cell and rewrite the "Detailed-spec requirement" to reflect the raised risk. This is the honesty rule from the spec: failures surface rather than hide.

- [x] **Step 2: Add a new section below the register**

After the decision register table, before "## Detailed Architecture Go/No-Go", add:

```markdown
## 2026-04-24 Pre-Architecture Hardening Probes

The five pre-architecture hardening probes (P1–P5) have been added to the
pre-design evidence set. See B14, B15, B16, B17, B18 in
`docs/verification-plan.md` for commands, observed numbers, and dispositions.

These probes close the runtime-sensitive and parity-critical evidence gaps
identified in the 2026-04-24 audit. Architecture planning in the next session
should treat their results as current-repo measurements, not prior-attempt
retrospectives.
```

Note: B15 and B16 are for P2 and P3 (mechanics assertions, no timing). Those sections still need to exist in verification-plan.md. Add them in Task 13 as part of the stage 2 verification-plan update (they are simple assertion-passed records).

- [x] **Step 3: Commit**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md
git commit -m "docs: extend pre-design decision register with P1-P5 rows"
```

---

## Stage 2 — Fold-back

Stage 2 runs after stage 1 is complete. Order within stage 2: 2c (consolidation) before 2a (evidence-driven), per the spec's Appendix B. Pure-text clarifications (2b) are independent and can run at any point within stage 2.

### Task 10: Consolidate fixture-outlook + fixture-matrix into fixtures.md

**Files:**
- Create: `docs/markdown/fixtures.md`
- Delete: `docs/markdown/fixture-outlook.md`
- Delete: `docs/markdown/fixture-matrix.md`
- Modify: `docs/README.md`
- Modify: `CLAUDE.md`

- [x] **Step 1: Identify all cross-references**

Run: `rg -n 'fixture-outlook|fixture-matrix' docs/ CLAUDE.md`

Record every match. Categorize each as "active canonical reference" (needs redirecting to `fixtures.md`) or "historical context" (may be left alone, e.g., in archive/ or superpowers/plans/).

- [x] **Step 2: Create the consolidated document**

File: `docs/markdown/fixtures.md`

Structure (merging content from both source docs):

```markdown
# Markdown.mdtest Fixtures

Canonical fixture reference for the 23 `Markdown.mdtest` fixtures. Combines
the per-fixture matrix and the feature-risk outlook — previously split across
`fixture-matrix.md` (per-fixture rows) and `fixture-outlook.md` (risk tiers).

## Fixture Matrix

<paste the full "| Fixture | Expected | Lines | Bytes | ... |" table from
the current fixture-matrix.md verbatim, including the "How to Use This
Matrix" section>

## Feature Risk Outlook for a Fresh Build

<paste the full "| Feature area | Risk tier | Primary risk | Notes |" table
from the current fixture-outlook.md, including "How to Read This File",
"What Would Lower These Risks", and "What This Outlook Does Not Claim"
sections>

## How the Two Views Relate

The matrix is fixture-level (one row per mdtest fixture). The outlook is
feature-level (one row per Markdown feature area). Use the matrix to pick
fixture-sized milestones and to check strict-oracle caveats; use the outlook
to understand which features are mechanics-closed vs still open.
```

Merge content verbatim from the two source docs. Keep both tables intact —
they convey different information and both are referenced in the audit
checklist.

- [x] **Step 3: Delete the old files**

```bash
git rm docs/markdown/fixture-outlook.md
git rm docs/markdown/fixture-matrix.md
```

- [x] **Step 4: Update docs/README.md**

Modify `docs/README.md`. For every active reference to `fixture-outlook.md` or `fixture-matrix.md`, replace with a single reference to `fixtures.md`.

Specifically:
- Item 9 in the reading order ("`markdown/fixture-matrix.md`") — change target and description to point at `markdown/fixtures.md`.
- Item 19 in the reading order ("`markdown/fixture-outlook.md`") — remove this item entirely; the consolidated `fixtures.md` is already linked as item 9.
- Renumber subsequent items.
- Directory map table: replace the two rows for `fixture-outlook.md` and `fixture-matrix.md` with one row: `markdown/fixtures.md | Canonical fixture matrix plus feature-risk outlook.`
- Canonical-flow section: replace any mention with "markdown/fixtures.md".

- [x] **Step 5: Update CLAUDE.md**

Modify `CLAUDE.md`. Find the "Reference materials" section. Remove the two bullets for `docs/markdown/fixture-matrix.md` and `docs/markdown/fixture-outlook.md`. Replace with a single bullet:

```markdown
- `docs/markdown/fixtures.md` — canonical fixture matrix plus feature-risk outlook
```

Also check the "Docs Truth Hierarchy" section — if it mentions either old filename, replace with `fixtures.md`.

- [x] **Step 6: Verify no stale references remain**

Run: `rg -n 'fixture-outlook|fixture-matrix' docs/ CLAUDE.md`

Expected: no matches in active canonical docs. Matches in `docs/superpowers/plans/`, `docs/archive/`, or `docs/superpowers/notes/` older entries are historical and acceptable.

- [x] **Step 7: Commit**

```bash
git add docs/markdown/fixtures.md docs/README.md CLAUDE.md
git commit -m "docs: consolidate fixture-outlook and fixture-matrix into fixtures.md"
```

---

### Task 11: Adjust reading-order for style docs in docs/README.md

**Files:**
- Modify: `docs/README.md`

- [x] **Step 1: Move style-doc entries later in the reading order**

Modify `docs/README.md`. Find the numbered reading-order list. Locate entries 11 (`spl/reference.md`), 12 (`spl/verification-evidence.md`), and 13 (`spl/style-guide-validation.md`).

The style-lexicon, codegen-style-guide, and style-guide-validation entries should be grouped at the end of the reading-order list, annotated as optional-for-codegen reading. Restructure the list so:

- Architecture-critical reading remains in its current early positions (1–10).
- `spl/reference.md` and `spl/verification-evidence.md` stay in their current positions (they are mechanics-critical).
- `spl/style-guide-validation.md`, and if present any direct references to `spl/style-lexicon.md` / `spl/codegen-style-guide.md`, move into a new bottom group labelled:

```markdown
**Optional — read only if architecture planning considers generated SPL:**

N+1. [`spl/style-lexicon.md`](spl/style-lexicon.md) — legal expressive vocabulary.
N+2. [`spl/codegen-style-guide.md`](spl/codegen-style-guide.md) — policy for recurring value phrases.
N+3. [`spl/style-guide-validation.md`](spl/style-guide-validation.md) — which style-guide claims are mechanically enforceable, demonstrable, or advisory.
```

Renumber the main list so it flows continuously up to the "Optional" marker, then the bottom group uses its own numbering starting at N+1.

- [x] **Step 2: Verify reading order is coherent**

Re-read the modified `docs/README.md` section from top to bottom. Each numbered item should still point at an existing doc (you already verified this in Task 10). The "Optional" group should be clearly marked as conditional.

- [x] **Step 3: Commit**

```bash
git add docs/README.md
git commit -m "docs: reorder style-lexicon group to optional reading position"
```

---

### Task 12: Update performance/budget.md with P1 baselines

**Files:**
- Modify: `docs/performance/budget.md`

- [x] **Step 1: Refresh Current Recorded Baselines section**

Modify `docs/performance/budget.md`. Find the "## Current Recorded Baselines" section (currently at end of file).

Replace the existing bullets with:

```markdown
## Current Recorded Baselines

`docs/verification-plan.md` records the current baselines:

- **Interpreter startup** (empty `.spl`): about 0.10s cold (B1).
- **Current-repo SPL cost at 1k lines:** first-run and median per B14.
- **Current-repo SPL cost at 4k lines:** first-run and median per B14.
- **Current-repo scene-count-per-act (200 scenes):** first-run and median per B18.
- **Current-repo reference-lookup at fixture scale:** first-run and median per B17.
- **Current oracle-stub mdtest contract:** 23 passing tests in about 1.44s (B9).

### Historical / retrospective context

- **Prior 4k-line SPL (retrospective):** 17–26s cold and 2–3s warm on a prior codebase not present in this repo. Use B14 for current-repo claims.
- **`./shakedown-dev` prototype (2026-04-24):** about 5.0s on empty input and 4.8s on `tests/prototype/fixtures/p2_blockquote_input.md`. Prototype-scale only; use B14 for realistic-size claims.

Re-measure before making a performance-sensitive architecture decision.
```

- [x] **Step 2: Commit**

```bash
git add docs/performance/budget.md
git commit -m "docs: refresh budget.md baselines with P1 measurements"
```

---

### Task 13: Add B15/B16 records and move closed items out of bucket D

**Files:**
- Modify: `docs/verification-plan.md`

- [x] **Step 1: Append B15 (emphasis two-pass) and B16 (nested-dispatch) records**

Modify `docs/verification-plan.md`. After B14 and before B17, insert:

```markdown
### B15 — Emphasis two-pass mechanics

- **Command:** `uv run pytest tests/test_pre_design_probes.py -k emphasis -v`
- **Purpose:** confirm SPL can execute the strong-before-emphasis substitution order on a buffered span — the mechanic Markdown.pl uses to produce overlapping `<em>/<strong>` behaviour.
- **Observed (2026-04-24):** 1 passed.
- **Disposition:** Confirms the two-pass substitution mechanic. Architecture planning may rely on buffer-then-substitute-strong-then-substitute-emphasis as an SPL-supported pattern. Full emphasis-feature parity remains implementation work; the mechanics risk is now closed.

### B16 — Nested-dispatch mechanics

- **Command:** `uv run pytest tests/test_pre_design_probes.py -k nested -v`
- **Purpose:** confirm a dispatcher can push frame sentinels onto a stack, enter an inner frame while the outer remains active, emit content inside the inner, and pop back cleanly. This is the mechanic prior-attempt architecture memos propose as the fix for the duplicated-blockquote-machinery pressure.
- **Observed (2026-04-24):** 1 passed.
- **Disposition:** Confirms the frame-sentinel nesting mechanic. Architecture planning may rely on recursive-dispatch-with-frame-stack as a supported pattern for nested blockquote/list composition. Full nested-block-composition parity remains implementation work.
```

Place these in numeric order: the file's existing B14 → B15 → B16 → B17 → B18 sequence is the target.

- [x] **Step 2: Move closed items out of bucket D**

Find `## Bucket D — Predictions (Open Items for Architecture Planning)`. Items the new probes closed:

- "Production implementation of reference lookup, setext line buffering, and list looseness/nesting state" — this becomes partially closed by B15/B16 for emphasis/nested mechanics and by B17 for reference lookup at scale. Rewrite the bullet:

  Original: `Production implementation of reference lookup, setext line buffering, and list looseness/nesting state. The mechanics are covered by B10, but feature-level Markdown coverage still belongs to implementation.`

  Replacement: `Feature-level Markdown implementation for reference lookup (mechanics B10 + scale B17), setext line buffering (mechanics B10), list looseness/nesting (mechanics B10), emphasis (mechanics B15), and nested-block composition (mechanics B16). Mechanics are closed; feature-level coverage still belongs to implementation.`

Leave other bucket D items unchanged unless a probe result specifically closes them.

- [x] **Step 3: Commit**

```bash
git add docs/verification-plan.md
git commit -m "docs: record B15, B16 probe results; update bucket D phrasing"
```

---

### Task 14: Update fixtures.md risk tiers citing P2/P3 outcomes

**Files:**
- Modify: `docs/markdown/fixtures.md`

- [x] **Step 1: Adjust emphasis and nested-block risk tiers**

Modify `docs/markdown/fixtures.md`. In the Feature Risk Outlook table:

- Row "Emphasis": append "; mechanics closed by B15" to the Notes column. If the probe PASSED, the risk tier may remain Medium (the feature still requires full implementation) OR you may lower it to Low-Medium — the Notes column is the honest record either way.

- Row "Strong Emphasis": append "; mechanics closed by B15" to the Notes column.

- Row "Nested Block Structures": append "; frame-stack mechanics closed by B16" to the Notes column. Risk remains High (full parity is still implementation work), but the mechanics-level risk is retired.

If P2 or P3 failed in stage 1, instead update the Notes to record the failure and raise (do not lower) the risk tier. Honesty rule from the spec.

- [x] **Step 2: Commit**

```bash
git add docs/markdown/fixtures.md
git commit -m "docs: cite P2/P3 probe outcomes in fixtures.md risk tiers"
```

---

### Task 15: Add AST-cache feasibility subsection to runtime-boundary.md

**Files:**
- Modify: `docs/architecture/runtime-boundary.md`

- [ ] **Step 1: Append AST-cache feasibility subsection**

Modify `docs/architecture/runtime-boundary.md`. After the existing "## Interpreter Constraints That Shape the Boundary" section and before "## Run-Loop Boundary", add:

```markdown
## AST-Cache Feasibility

Prior-attempt round-2 experiment 6 (`docs/prior-attempt/feasibility-lessons.md`) reported that a pre-built AST cache reduced per-test cost from 1.09s to ~0.30s at 8,623 lines. That number is retrospective and does not transfer.

What does transfer:

- **The bottleneck the cache addressed.** B14 records cold `shakespeare run` cost at 1k and 4k lines in this repo. Compare B14's numbers to B1's 0.10s interpreter startup. The gap between startup and run cost is the parse-plus-execute window; caching can only shrink the parse portion.
- **The mechanism.** `shakespeare --help` lists no parse-only subcommand (B7). Any cache therefore lives in a Python wrapper. The canonical technique is to import `shakespeare.parser`, parse the `.spl` once, `pickle.dump` the AST to a side file, and on subsequent runs `pickle.load` and feed the AST to the interpreter. This is a Python-wrapper responsibility, not an SPL-level feature.
- **The decision shape.** Whether to build an AST cache depends on B14's cold-to-re-parse ratio. If cold runs are dominated by parse time (measurable by comparing `shakespeare run` cost to an AST-only parse timing), a cache likely helps. If they are dominated by execution time, a cache is wasted complexity.

Architecture planning should either demonstrate the cache is worth the wrapper complexity (with a current-repo measurement, not the retrospective 1.09 → 0.30 number) or explicitly defer the cache until a bottleneck forces it.
```

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/runtime-boundary.md
git commit -m "docs: add AST-cache feasibility subsection to runtime-boundary"
```

---

### Task 16: Add first-fixture milestone shortlist to fixtures.md

**Files:**
- Modify: `docs/markdown/fixtures.md`

- [ ] **Step 1: Append candidate first-fixture shortlist**

Modify `docs/markdown/fixtures.md`. After the "How the Two Views Relate" section, add:

```markdown
## Candidate First-Fixture Milestones

Architecture planning's rubric scores "names the first fixture milestone" as a strong-answer quality. Given the fixture matrix and feature-risk outlook, the candidate first fixtures are:

- **Tidyness** (5 lines, 78 bytes, Low risk). Exercises output blank-line normalization only — the minimum viable "pipeline produces bytes" proof.
- **Amps and angle encoding** (20 lines, 381 bytes, Low risk). Exercises entity encoding outside code/HTML. A focused first test of the span-encoding stage.
- **Horizontal rules** (67 lines, 270 bytes, Low risk). Single-line pattern, exercises block-level `<hr/>` recognition.

These are candidates, not a decision. Selecting the first fixture depends on which pipeline slice architecture planning chooses to prove first (block pipeline vs span encoding vs I/O wiring). Any of the three is defensible; all three are below the medium-risk feature threshold.

Do not start with `Markdown Documentation - Basics` or `Markdown Documentation - Syntax` — they are aggregate fixtures and should be used after smaller fixtures have proven their constituent features.
```

- [ ] **Step 2: Commit**

```bash
git add docs/markdown/fixtures.md
git commit -m "docs: add candidate first-fixture milestone shortlist"
```

---

### Task 17: target.md — pin normalization + add strict-parity sentence

**Files:**
- Modify: `docs/markdown/target.md`

- [ ] **Step 1: Replace normalization description**

Modify `docs/markdown/target.md`. Find the paragraph in "## Test Surface: Markdown.mdtest":

> The default `tests/test_mdtest.py` contract compares normalized fixture output. A strict local-oracle parity check must compare Shakedown output against freshly generated `perl ~/markdown/Markdown.pl` output for the same input, because two checked-in expected files differ from local oracle raw bytes.

Replace with:

> The default `tests/test_mdtest.py` contract compares normalized fixture output. Normalization is defined by `_normalize` in `tests/test_mdtest.py` (see that function for the canonical algorithm). Summary: each line is `.strip()`-ped, consecutive blank lines are collapsed to a single blank line, and the whole result is `.strip()`-ped. The `Auto links` fixture additionally applies `_decode_entities` (decoding `&#NNN;` and `&#xNN;`) to both sides before comparison. A strict local-oracle parity check must compare Shakedown output against freshly generated `perl ~/markdown/Markdown.pl` output for the same input, because two checked-in expected files differ from local oracle raw bytes.

- [ ] **Step 2: Add strict-parity⊇normalized-contract sentence**

Find the "## Parity Levels" section. Append a new paragraph after the three bullet items:

```markdown
Strict local-oracle parity implies normalized-contract parity: any Shakedown output that is byte-identical to local `Markdown.pl` output also passes the normalized-contract test. The normalized contract is a superset of outputs that includes some non-oracle-identical results; strict parity is a subset.
```

- [ ] **Step 3: Commit**

```bash
git add docs/markdown/target.md
git commit -m "docs: pin normalization by reference, add strict-parity sentence"
```

---

### Task 18: divergences.md — concretize email-equivalence rule

**Files:**
- Modify: `docs/markdown/divergences.md`

- [ ] **Step 1: Expand the email auto-links row with the concrete rule**

Modify `docs/markdown/divergences.md`. Find the active-exception row for "Email auto-links". After the table, insert:

```markdown
## Email Auto-Link Equivalence Rule

The "entity-normalized equivalence" target for email auto-links is defined concretely as:

1. Apply `_decode_entities` from `tests/test_mdtest.py` to both the Shakedown output and the oracle output for the same input. This decodes all `&#NNN;` decimal numeric character references and `&#xNN;` hex numeric character references to their literal characters.
2. Byte-compare the two decoded strings.

If they match, Shakedown passes the email-autolink equivalence check. Because `Markdown.pl` randomizes the entity choice per-character in `_EncodeEmailAddress`, byte-identical output is not available in pure SPL. Decoding before comparison collapses the random entity space to a canonical form.

The mdtest `Auto links` fixture already applies this decoding via the test harness's `_decode_entities` function. Any additional email-autolink parity testing outside that fixture should use the same decoder.
```

- [ ] **Step 2: Commit**

```bash
git add docs/markdown/divergences.md
git commit -m "docs: concretize email auto-link equivalence rule"
```

---

### Task 19: runtime-boundary.md — add wrapper-toolchain subsection

**Files:**
- Modify: `docs/architecture/runtime-boundary.md`

- [ ] **Step 1: Insert wrapper-toolchain subsection**

Modify `docs/architecture/runtime-boundary.md`. After "## Interpreter Constraints That Shape the Boundary" and before the "## AST-Cache Feasibility" section added in Task 15, insert:

```markdown
## Wrapper Toolchain

The project's existing scripts and test harness use Python 3 via `uv` (see `pyproject.toml` and `./run-loop`). The prototype entry-point `./shakedown-dev` is a bash shim that delegates to `uv run python scripts/assemble.py` and `uv run shakespeare run shakedown.spl`. Any wrapper-assisted architecture shape should use Python via `uv` as the wrapper toolchain unless it has a concrete reason to choose otherwise.

This is documentation of the toolchain already in use, not a new decision. Architecture planning may propose a different toolchain, but must justify the change given:

- existing Python scripts in `scripts/` (assembly, audit, measurement)
- existing pytest harness at `tests/test_pre_design_probes.py` and `tests/test_mdtest.py`
- existing `uv` dependency management via `pyproject.toml` and `uv.lock`
- existing `run-loop` Python entrypoint
```

- [ ] **Step 2: Commit**

```bash
git add docs/architecture/runtime-boundary.md
git commit -m "docs: document wrapper toolchain (Python via uv) in runtime-boundary"
```

---

### Task 20: Create inherited-scaffold.md + link from README.md + CLAUDE.md

**Files:**
- Create: `docs/architecture/inherited-scaffold.md`
- Modify: `docs/README.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Create the inherited-scaffold doc**

File: `docs/architecture/inherited-scaffold.md`

```markdown
# Inherited Scaffold

This document describes the prototype scaffold already present in the repository when architecture planning begins. Its purpose is to surface the inherited state so planning engages with it as a surfaced choice, not as an invisible default.

**Important:** this is prototype shape, not adopted architecture. Architecture planning may keep, revise, or replace any element of the scaffold without constraint.

## The Scaffold

The prototype scaffold consists of:

- **`./shakedown`** — the production entry-point. Currently a bash stub that delegates to `~/markdown/Markdown.pl` via `perl`. This is the oracle stub; all 23 mdtest fixtures pass because Markdown.pl is the oracle. This is deliberate: the stub keeps the contract green while the SPL implementation is built up.

- **`./shakedown-dev`** — the prototype entry-point. A bash wrapper that runs `uv run python scripts/assemble.py` (to rebuild `shakedown.spl` from `src/*.spl`) then `uv run shakespeare run shakedown.spl`. Its own comment states "This is the shape the final ./shakedown will take." Treat that comment as aspirational, not decided: architecture planning may choose that shape, choose a different shape, or choose to assemble differently.

- **`scripts/assemble.py`** — a Python script that concatenates `src/*.spl` into the single `shakedown.spl` file. SPL has no import mechanism, so assembly is one way to keep source readable while complying with the single-file constraint.

- **`src/*.spl`** — source fragments, currently split as:
  - `00-preamble.spl` — dramatis personae and act header
  - `10-phase1-read.spl` — phase 1 (read) scenes
  - `20-phase2-block.spl` — phase 2 (block) scenes
  - `30-phase3-inline.spl` — phase 3 (inline) scenes

  The three-phase split (read / block / inline) is a design choice, not a verified requirement. Architecture planning may reorganize, flatten, or replace this split.

- **`shakedown.spl`** — the assembled output. Not hand-edited. Regenerated every time `./shakedown-dev` runs.

## What the Scaffold Does Not Decide

- Whether the final `./shakedown` is bash, Python, or something else.
- Whether SPL source is assembled from fragments or maintained as a single hand-edited file.
- Whether the internal phase split is read/block/inline, pre-scan/dispatch/render, one-pass-streaming, or another shape.
- Whether an AST cache exists between assembly and interpreter run.
- Whether SPL execution happens every invocation or once per cached parse.

These are architecture decisions. This document exists so planning does not inherit them tacitly.

## Relationship to the Architecture Rubric

`docs/architecture/decision-rubric.md` lists observable correctness, documented parity exceptions, fixture-level verification, SPL ownership of Markdown semantics, maintainability, and runtime cost as the scoring axes. The scaffold does not preempt any of those: any candidate architecture must justify its choices on the rubric, even if it adopts the scaffold as-is.
```

- [ ] **Step 2: Link from docs/README.md**

Modify `docs/README.md`. In the "Reading Order for a New Agent" numbered list, add an entry after item 15 (`architecture/encoding-and-scope.md`):

```markdown
16. [`architecture/inherited-scaffold.md`](architecture/inherited-scaffold.md) — prototype scaffold already in the repo; surfaced so planning engages with it as a choice, not a default.
```

Renumber subsequent items.

Also add a row to the Directory Map table under `architecture/`:

```markdown
| `architecture/inherited-scaffold.md` | Prototype scaffold surfacing (not adopted architecture). |
```

Also add a line to the Canonical Flow of Truth section:

```markdown
- **Inherited prototype scaffold:** `architecture/inherited-scaffold.md` documents `./shakedown-dev`, `scripts/assemble.py`, `src/*.spl`, and `shakedown.spl`. These are prototype artifacts, not adopted architecture.
```

- [ ] **Step 3: Link from CLAUDE.md**

Modify `CLAUDE.md`. In the "Reference materials" section, after the line for `docs/architecture/encoding-and-scope.md`, add:

```markdown
- `docs/architecture/inherited-scaffold.md` — prototype scaffold surfacing
```

Also, in the "Docs Truth Hierarchy" section, add a line:

```markdown
- Treat `docs/architecture/inherited-scaffold.md` as inherited prototype state, not as adopted architecture.
```

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/inherited-scaffold.md docs/README.md CLAUDE.md
git commit -m "docs: add inherited-scaffold.md and link from README and CLAUDE"
```

---

### Task 21: Final verification pass

**Files:**
- Read-only checks across the repo

- [ ] **Step 1: Grep for stale fixture-doc references**

Run: `rg -n 'fixture-outlook|fixture-matrix' docs/ CLAUDE.md`

Expected: no matches in canonical docs. Matches allowed in `docs/superpowers/plans/`, `docs/archive/`, and older entries in `docs/superpowers/notes/` (historical context).

- [ ] **Step 2: Verify all cross-references resolve**

Run:

```bash
for f in $(rg -l '\[.*\]\(.*\.md\)' docs/ CLAUDE.md); do
  rg -o '\]\(([^)]+\.md)\)' "$f" -r '$1' | while read -r ref; do
    case "$ref" in
      /*) target="$ref" ;;
      *)  target="$(dirname "$f")/$ref" ;;
    esac
    if [ ! -f "$target" ] && ! rg -q "^$(basename "$target")$" <<< "$target" 2>/dev/null; then
      echo "MISSING: $f -> $ref"
    fi
  done
done
```

Or more simply: grep each newly added / modified doc for markdown links, `ls` the targets, confirm each resolves. Record any misses.

Expected: no `MISSING:` output.

- [ ] **Step 3: Run the full test suite**

Run: `uv run pytest -q`

Expected: all previously passing tests still pass. New tests for probes (P2, P3, P4 via the parametrize list) all pass. `tests/test_measure_spl_cost.py` passes.

- [ ] **Step 4: Verify the tier-C audit checklist is covered**

Check every row of Appendix A in the spec (`docs/superpowers/specs/2026-04-24-pre-architecture-hardening-design.md`) against the committed changes. For each row, confirm the referenced edit or probe landed. If any row is unaddressed, open a follow-up task rather than closing the plan.

- [ ] **Step 5: Commit any final cleanup**

If any of steps 1–4 uncover broken links, typos, or missing updates, fix them inline. Commit as:

```bash
git add <files>
git commit -m "docs: pre-architecture hardening final cleanup"
```

If no cleanup is needed, skip this commit.

---

## Self-Review Checklist

After plan execution:

- [ ] All 5 probes (P1 generator + runs, P2, P3, P4, P5) exist under `docs/spl/probes/pre-design/`
- [ ] `tests/test_pre_design_probes.py` has parametrize entries for P2, P3, P4 and all pass
- [ ] `docs/verification-plan.md` contains B14, B15, B16, B17, B18 sections with observed numbers
- [ ] `docs/markdown/fixtures.md` exists and subsumes the old outlook/matrix docs
- [ ] `docs/architecture/inherited-scaffold.md` exists and is linked from `docs/README.md` + `CLAUDE.md`
- [ ] `docs/markdown/target.md` normalization is pinned by reference to `_normalize`
- [ ] `docs/markdown/divergences.md` has the concrete email-equivalence rule
- [ ] `docs/architecture/runtime-boundary.md` has wrapper-toolchain + AST-cache feasibility subsections
- [ ] `docs/performance/budget.md` baselines refreshed
- [ ] `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md` decision register extended
- [ ] `docs/README.md` reading order reflects new state, style docs moved to optional
- [ ] `rg -n 'fixture-outlook|fixture-matrix' docs/ CLAUDE.md` returns only historical matches
- [ ] `uv run pytest -q` passes
