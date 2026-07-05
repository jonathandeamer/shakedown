# Agent Feedback Rails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make SPL failures visible and debuggable — fail loudly on parse errors, expose the inter-act token stream, take literary authorship out of the implementation loop, and record the Spike A halt — so implementation agents stop thrashing blind.

**Architecture:** Three tooling rails (wrapper error guard, assembler parse gate, token-stream debug target built by swapping Act IV for a dump loop at assembly time), plus two process changes (correctness-first literary workflow note; Spike A recorded as a §8.2 halt with its non-parsing WIP preserved on a branch). No production SPL surface changes: `src/*.spl` fragments and `src/literary.toml` are untouched by this plan except that Task 1 moves uncommitted WIP off the main working tree.

**Tech Stack:** Bash wrappers, Python 3.12 (`scripts/assemble.py`, pytest), `shakespearelang` as a library for in-process parse checks, one hand-authored non-production SPL fragment under `debug/`.

## Required Reading

- `docs/superpowers/plans/plan-roadmap.md`
- `docs/superpowers/notes/spl-literary-protocol.md`
- `docs/spl/literary-spec.md`
- `docs/spl/style-lexicon.md`
- `docs/spl/codegen-style-guide.md`
- `src/literary.toml`
- `docs/spl/reference.md` (§ on `Open your heart!` / `Speak your mind!` / `Recall`)

## Global Constraints

- **No production SPL surface changes.** This plan must not modify `src/*.spl` fragments, `src/literary.toml`, or `scripts/codegen_html.py`. The committed `shakedown.spl` must be byte-identical at the end of every task (Task 1 restores it from HEAD; nothing after that regenerates it with different content).
- **Literary protocol applies** (`docs/superpowers/notes/spl-literary-protocol.md`) because `scripts/assemble.py` changes. The new `debug/40-act4-token-dump.spl` fragment is a **non-production debug artifact**: it lives outside `src/`, is excluded from the compliance scan (`src/[0-9]*.spl` glob), uses no `@LIT.` placeholders, and adds no entries to `src/literary.toml`. Its prose is Incidental-class, copied from already-shipped resolved production lines wherever possible.
- **Literary compliance regression gates** for this plan, run in Task 6: `tests/test_literary_compliance.py`, `tests/test_literary_toml_schema.py`, `tests/test_assemble.py`, `tests/test_codegen_html.py`, and `tests/test_mdtest.py -k 'Amps and angle'`.
- Conventional commits per `CLAUDE.md` (`chore:` for tooling, `test:` for test-only changes, `docs:` for docs, `fix:` for the wrapper bug). No `cz bump`, no tags — operator-only.
- Python conventions per `CLAUDE.md`: type hints on all signatures, no bare `Any`, no `print()` in library code (a `ValueError` raised from `assemble` is the error channel, not prints).
- Wrapper line budget: `./shakedown` must stay ≤ 100 lines (`tests/test_shakedown_run.py::test_wrapper_line_budget`).
- The roadmap must never show more than one `in flight` plan (`tests/test_roadmap_contract.py`); Task 6 flips Spike A to halted and this plan to in flight in the same edit.

---

## Task 1: Salvage the Non-Parsing WIP off the Main Working Tree

The working tree on `main` carries a ~2,600-line uncommitted diff (partial Spike A list implementation) whose assembled `shakedown.spl` **does not parse** (`SPL parse error ... at line 301, negative_if`). Every session that starts here inherits a broken program. Preserve the WIP on a branch, restore a clean `main`, and archive the already-shipped token-efficiency plan file left untracked.

**Files:**
- Branch (new): `spike-a-lists-wip` receives the dirty state of `shakedown.spl`, `src/00-preamble.spl`, `src/20-act2-block.spl`, `src/20-act2-literary.toml`
- Move: `docs/superpowers/plans/2026-07-05-token-efficiency.md` → `docs/archive/plans/2026-07-05-token-efficiency.md`

**Interfaces:**
- Produces: a clean `main` working tree where the committed `shakedown.spl` parses and the Slice 1 fixture passes; branch `spike-a-lists-wip` holding the abandoned hand-authored list attempt for the future IR-codegen redesign to mine.

- [ ] **Step 1: Confirm the expected dirty state**

Run: `git status --porcelain`
Expected (order may vary; `2026-07-05-agent-feedback-rails.md` is this plan itself):

```text
 M shakedown.spl
 M src/00-preamble.spl
 M src/20-act2-block.spl
 M src/20-act2-literary.toml
?? docs/superpowers/plans/2026-07-05-agent-feedback-rails.md
?? docs/superpowers/plans/2026-07-05-token-efficiency.md
```

If other tracked files are modified, STOP and report — do not guess at intent.

- [ ] **Step 2: Commit the WIP to a preservation branch**

```bash
git switch -c spike-a-lists-wip
git add shakedown.spl src/00-preamble.spl src/20-act2-block.spl src/20-act2-literary.toml
git commit -m "chore: preserve non-parsing spike a list WIP for redesign reference"
git switch main
```

- [ ] **Step 3: Verify main is clean and the committed play parses**

Run: `git status --porcelain`
Expected: only the two `??` plan files remain.

Run: `uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q`
Expected: `1 passed, 22 deselected` — the committed `shakedown.spl` works again.

- [ ] **Step 4: Archive the shipped token-efficiency plan**

Its five commits already landed (see `git log 143a9e0~5..143a9e0`); the plan file was simply never committed.

```bash
mv docs/superpowers/plans/2026-07-05-token-efficiency.md docs/archive/plans/2026-07-05-token-efficiency.md
git add docs/archive/plans/2026-07-05-token-efficiency.md
git commit -m "docs: archive shipped token-efficiency plan"
```

---

## Task 2: Fail the `./shakedown` Wrapper on SPL Parse Errors

`shakespeare run` exits **0** on a parse error, printing `SPL parse error: ...` to stderr. The wrapper only greps stderr for `^SPL runtime error:`, so a non-parsing play yields exit 0 with empty stdout — tests then report a byte mismatch against empty output instead of the actual syntax error. Fix the guard and add an env override so the failure mode is testable.

**Files:**
- Modify: `./shakedown` (bash wrapper, repo root)
- Test: `tests/test_wrapper_error_channel.py` (create)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `SHAKEDOWN_SPL` environment variable — overrides the play file the wrapper runs (defaults to `$DIR/shakedown.spl`). Task 4's `./shakedown-debug` relies on this exact variable name.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_wrapper_error_channel.py`:

```python
"""The ./shakedown wrapper must fail loudly when the play cannot parse."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent
WRAPPER = REPO / "shakedown"

MINIMAL_VALID_PLAY = """\
A quiet probe.

Romeo, a probe.
Juliet, a probe.

                    Act I: The probe.

                    Scene I: The probe.

[Enter Romeo and Juliet]

Romeo:
 You are as fair as nothing.

[Exeunt]
"""


def _run_wrapper(spl_path: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(WRAPPER)],
        input=b"",
        capture_output=True,
        env={**os.environ, "SHAKEDOWN_SPL": str(spl_path)},
        check=False,
    )


def test_wrapper_fails_on_parse_error(tmp_path: Path) -> None:
    broken = tmp_path / "broken.spl"
    broken.write_text("this is not a play\n")
    result = _run_wrapper(broken)
    assert result.returncode != 0
    assert b"SPL parse error" in result.stderr
    assert result.stdout == b""


def test_wrapper_succeeds_on_valid_play(tmp_path: Path) -> None:
    valid = tmp_path / "valid.spl"
    valid.write_text(MINIMAL_VALID_PLAY)
    result = _run_wrapper(valid)
    assert result.returncode == 0, result.stderr.decode()
```

- [ ] **Step 2: Run the tests to verify current behavior fails**

Run: `uv run pytest tests/test_wrapper_error_channel.py -v`
Expected: `test_wrapper_fails_on_parse_error` FAILS (wrapper exits 0 today — it neither honours `SHAKEDOWN_SPL` nor catches parse errors); `test_wrapper_succeeds_on_valid_play` also fails for the same `SHAKEDOWN_SPL` reason.

- [ ] **Step 3: Fix the wrapper**

Replace the full contents of `./shakedown` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
SPL_FILE="${SHAKEDOWN_SPL:-$DIR/shakedown.spl}"
stderr_file="$(mktemp)"
trap 'rm -f "$stderr_file"' EXIT

set +e
uv run --directory "$DIR" shakespeare run "$SPL_FILE" 2>"$stderr_file"
rc=$?
set -e

cat "$stderr_file" >&2

if [ "$rc" -ne 0 ]; then
  exit "$rc"
fi

if grep -qE '^SPL (runtime|parse) error:' "$stderr_file"; then
  exit 1
fi
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_wrapper_error_channel.py tests/test_shakedown_run.py tests/test_mdtest.py -k 'Amps and angle or wrapper' -v`
Expected: all selected tests PASS (line budget: the new wrapper is ~21 lines, well under 100).

- [ ] **Step 5: Commit**

```bash
git add shakedown tests/test_wrapper_error_channel.py
git commit -m "fix: fail the shakedown wrapper on SPL parse errors"
```

---

## Task 3: Parse Gate in the Assembler and a Parse Smoke Test

An agent should learn its SPL is illegal **at assemble time**, seconds after the edit — not minutes later via an empty byte-diff. Add an opt-in in-process parse check to `assemble()` (on by default at both real entry points), and a smoke test that fails first when the committed play is broken.

**Files:**
- Modify: `scripts/assemble.py`
- Modify: `scripts/shakedown_run.py` (the `_assemble` helper)
- Test: `tests/test_assemble.py` (add two tests)
- Test: `tests/test_spl_parse_smoke.py` (create)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: `assemble(src_dir: Path, manifest: Path, output: Path, parse_check: bool = False) -> None` — the new keyword defaults to `False` so existing unit tests that assemble non-play fragments keep passing; `main()` and `scripts/shakedown_run.py::_assemble` pass `parse_check=True`. Task 4 extends this same signature with `replace`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_assemble.py`:

```python
MINIMAL_VALID_PLAY = """\
A quiet probe.

Romeo, a probe.
Juliet, a probe.

                    Act I: The probe.

                    Scene I: The probe.

[Enter Romeo and Juliet]

Romeo:
 You are as fair as nothing.

[Exeunt]
"""


def test_assemble_parse_check_rejects_unparseable_output(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.spl").write_text("this is not a play\n")
    (src / "manifest.toml").write_text('fragments = ["a.spl"]\n')

    with pytest.raises(ValueError, match="does not parse"):
        assemble(
            src_dir=src,
            manifest=src / "manifest.toml",
            output=tmp_path / "out.spl",
            parse_check=True,
        )


def test_assemble_parse_check_accepts_valid_play(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "play.spl").write_text(MINIMAL_VALID_PLAY)
    (src / "manifest.toml").write_text('fragments = ["play.spl"]\n')

    output = tmp_path / "out.spl"
    assemble(
        src_dir=src,
        manifest=src / "manifest.toml",
        output=output,
        parse_check=True,
    )
    assert output.read_text() == MINIMAL_VALID_PLAY
```

Create `tests/test_spl_parse_smoke.py`:

```python
"""Fail fast, with the real parse error, when the committed play is broken.

Without this, a non-parsing shakedown.spl surfaces as byte-mismatch
failures against empty output across the whole suite.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).parent.parent


def test_committed_shakedown_spl_parses() -> None:
    from shakespearelang import Shakespeare

    Shakespeare((REPO / "shakedown.spl").read_text())
```

- [ ] **Step 2: Run the new tests to verify the right ones fail**

Run: `uv run pytest tests/test_assemble.py tests/test_spl_parse_smoke.py -v`
Expected: `test_assemble_parse_check_rejects_unparseable_output` and `test_assemble_parse_check_accepts_valid_play` FAIL with `TypeError: assemble() got an unexpected keyword argument 'parse_check'`; `test_committed_shakedown_spl_parses` PASSES (Task 1 restored a valid committed play); pre-existing assemble tests PASS.

- [ ] **Step 3: Implement the parse gate**

In `scripts/assemble.py`, add below `_resolve_in_segment`:

```python
def _parse_check(source: str, output: Path) -> None:
    from shakespearelang import Shakespeare
    from shakespearelang.errors import ShakespeareParseError

    try:
        Shakespeare(source)
    except ShakespeareParseError as exc:
        raise ValueError(
            f"assembled SPL at {output} does not parse:\n{exc}"
        ) from exc
```

Change the `assemble` signature and tail:

```python
def assemble(
    src_dir: Path,
    manifest: Path,
    output: Path,
    parse_check: bool = False,
) -> None:
    """Concatenate fragments per manifest and resolve scene labels."""
    with manifest.open("rb") as f:
        config = tomllib.load(f)

    fragments: list[str] = config["fragments"]
    combined = "".join((src_dir / name).read_text() for name in fragments)
    with_literary = _resolve_literary_placeholders(
        combined,
        src_dir / "literary.toml",
    )
    resolved = _resolve_scene_labels(with_literary)
    if parse_check:
        _parse_check(resolved, output)
    output.write_text(resolved)
```

(Parse before writing, so a broken build never replaces a working `shakedown.spl`.)

In `main()`, pass `parse_check=True` to the `assemble(...)` call.

In `scripts/shakedown_run.py::_assemble`, pass `parse_check=True` to its `assemble(...)` call.

- [ ] **Step 4: Run the tests and the real assembler**

Run: `uv run pytest tests/test_assemble.py tests/test_spl_parse_smoke.py tests/test_shakedown_run.py -v`
Expected: all PASS.

Run: `uv run python scripts/assemble.py && git diff --stat shakedown.spl`
Expected: no diff output — the rebuild is byte-identical to the committed file.

- [ ] **Step 5: Commit**

```bash
git add scripts/assemble.py scripts/shakedown_run.py tests/test_assemble.py tests/test_spl_parse_smoke.py
git commit -m "chore: add assemble-time SPL parse gate and parse smoke test"
```

---

## Task 4: Token-Stream Debug Target

The four acts communicate through a token stream on Puck's stack, but the only observable today is final HTML bytes. Build `shakedown-debug`: the same play with Act IV swapped for a loop that prints each stream value as an integer, one per line. Act II/III work then becomes verifiable against an expected token sequence directly, without touching Act IV emission.

**Files:**
- Create: `debug/40-act4-token-dump.spl`
- Modify: `scripts/assemble.py` (add `replace` parameter and `--debug` mode)
- Create: `./shakedown-debug` (bash wrapper, repo root, executable)
- Test: `tests/test_assemble.py` (one test)
- Test: `tests/test_token_dump.py` (create)

**Interfaces:**
- Consumes: `SHAKEDOWN_SPL` env override from Task 2; `parse_check` keyword from Task 3.
- Produces: `assemble(src_dir, manifest, output, parse_check=False, replace: dict[str, Path] | None = None)` where `replace` maps a manifest fragment name to a substitute file path; `python scripts/assemble.py --debug` writes `.cache/shakedown-debug.spl` (git-ignored via the existing `.cache/` rule); `./shakedown-debug` assembles and runs it (stdin Markdown → stdout integers, one per line).

- [ ] **Step 1: Write the failing assembler test**

Append to `tests/test_assemble.py`:

```python
def test_assemble_replace_substitutes_fragment(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.spl").write_text("original\n")
    (src / "manifest.toml").write_text('fragments = ["a.spl"]\n')
    substitute = tmp_path / "substitute.spl"
    substitute.write_text("substituted\n")

    output = tmp_path / "out.spl"
    assemble(
        src_dir=src,
        manifest=src / "manifest.toml",
        output=output,
        replace={"a.spl": substitute},
    )
    assert output.read_text() == "substituted\n"
```

Run: `uv run pytest tests/test_assemble.py::test_assemble_replace_substitutes_fragment -v`
Expected: FAIL with `TypeError: assemble() got an unexpected keyword argument 'replace'`.

- [ ] **Step 2: Implement `replace` and `--debug` in the assembler**

In `scripts/assemble.py`, change `assemble` to:

```python
def assemble(
    src_dir: Path,
    manifest: Path,
    output: Path,
    parse_check: bool = False,
    replace: dict[str, Path] | None = None,
) -> None:
    """Concatenate fragments per manifest and resolve scene labels."""
    with manifest.open("rb") as f:
        config = tomllib.load(f)

    replacements = replace or {}
    fragments: list[str] = config["fragments"]
    combined = "".join(
        replacements.get(name, src_dir / name).read_text() for name in fragments
    )
    with_literary = _resolve_literary_placeholders(
        combined,
        src_dir / "literary.toml",
    )
    resolved = _resolve_scene_labels(with_literary)
    if parse_check:
        _parse_check(resolved, output)
    output.write_text(resolved)
```

Replace `main()` with:

```python
def main() -> None:
    root = Path(__file__).parent.parent
    if "--debug" in sys.argv[1:]:
        output = root / ".cache" / "shakedown-debug.spl"
        output.parent.mkdir(exist_ok=True)
        assemble(
            src_dir=root / "src",
            manifest=root / "src" / "manifest.toml",
            output=output,
            parse_check=True,
            replace={
                "40-act4-emit.spl": root / "debug" / "40-act4-token-dump.spl",
            },
        )
    else:
        assemble(
            src_dir=root / "src",
            manifest=root / "src" / "manifest.toml",
            output=root / "shakedown.spl",
            parse_check=True,
        )
```

Run: `uv run pytest tests/test_assemble.py -v`
Expected: all PASS.

- [ ] **Step 3: Write the debug Act IV fragment**

Create `debug/40-act4-token-dump.spl`. The stream-count scenes (`@DBG_START`, `@DBG_OLD_MEASURE`, `@DBG_SHORT_MEASURE`, `@DBG_LOOP`, and the pop mechanics in `@DBG_POP`) are copied line-for-line from the **resolved** production Act IV in the committed `shakedown.spl` (Act IV Scenes I–V); only the dispatch chain is replaced by print-integer + print-newline + loop. `Open your heart!` prints the addressed character's value as an integer; the sum of a little furry black cat and a black cat is 10 (newline) for `Speak your mind!`. This file is a non-production debug artifact: no `@LIT.` placeholders, no `src/literary.toml` entries, plain literal scene titles.

```text
                    Act IV: The scribe counts the herald's words aloud.

                    Scene @DBG_START: The scribe weighs the stream measure.

[Enter Puck and Prospero]

Puck:
 Is Horatio jollier than the product of a little green sweet flower and a rural little green
  sweet flower?

Prospero:
 If so, let us proceed to scene @DBG_OLD_MEASURE.

Prospero:
 If not, let us proceed to scene @DBG_SHORT_MEASURE.


                    Scene @DBG_OLD_MEASURE: The old cell keeps its measure.

Puck:
 You are as noble as the product of the sum of a flower and a sweet flower and the sum of a
  flower and the product of a little green sweet flower and a rural little green sweet
  flower.

Prospero:
 We shall proceed to scene @DBG_LOOP.


                    Scene @DBG_SHORT_MEASURE: The short cell takes Horatio's measure.

Puck:
 You are as noble as Horatio.

Prospero:
 We shall proceed to scene @DBG_LOOP.


                    Scene @DBG_LOOP: The scribe asks if words remain.

Prospero:
 Am I as noble as nothing?

Puck:
 If so, let us proceed to scene @DBG_DONE.

Puck:
 If not, let us proceed to scene @DBG_POP.


                    Scene @DBG_POP: The herald yields one word and it is counted aloud.

Prospero:
 Recall the herald's present word.

Puck:
 You are as noble as the difference between Prospero and a cat.

Prospero:
 Open your heart!

Prospero:
 You are as noble as the sum of a little furry black cat and a black cat.

Prospero:
 Speak your mind!

Puck:
 Let us return to scene @DBG_LOOP.


                    Scene @DBG_DONE: The counting is done.

[Exeunt]
```

Run: `uv run python scripts/assemble.py --debug`
Expected: exits 0 and `.cache/shakedown-debug.spl` exists. If it exits nonzero with a parse error, the error message now points at the exact line — fix the debug fragment (not the assembler) until it parses. Do not proceed past this step with a non-parsing debug play.

- [ ] **Step 4: Create the debug wrapper**

Create `./shakedown-debug`:

```bash
#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
uv run --directory "$DIR" python scripts/assemble.py --debug
SHAKEDOWN_SPL="$DIR/.cache/shakedown-debug.spl" exec "$DIR/shakedown"
```

```bash
chmod +x shakedown-debug
```

- [ ] **Step 5: Write the token-dump test**

Create `tests/test_token_dump.py`:

```python
"""The debug target dumps the inter-act token stream as integers."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent
DEBUG_WRAPPER = REPO / "shakedown-debug"
AMPS_FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Amps and angle encoding.text"
)


def test_debug_target_dumps_integer_token_stream() -> None:
    result = subprocess.run(
        [str(DEBUG_WRAPPER)],
        input=AMPS_FIXTURE.read_bytes(),
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    lines = result.stdout.decode().strip().splitlines()
    assert len(lines) > 10
    values = [int(line) for line in lines]
    # Production Act IV emits <p> first for this fixture (Slice 1 is
    # byte-identical), so the first popped stream value must be the
    # PARAGRAPH_OPEN token.
    assert values[0] == 1
```

- [ ] **Step 6: Run the token-dump test**

Run: `uv run pytest tests/test_token_dump.py -v`
Expected: PASS (takes a few seconds — one cold interpreter run). If `values[0] == 1` fails while every line parsed as an integer, the dump loop works but the copied stream-count scenes drifted from production — re-copy Scenes I–V of Act IV from the committed `shakedown.spl` exactly.

- [ ] **Step 7: Regression-check the production build is untouched**

Run: `uv run python scripts/assemble.py && git diff --stat shakedown.spl && uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q`
Expected: no diff; `1 passed, 22 deselected`.

- [ ] **Step 8: Commit**

```bash
git add debug/40-act4-token-dump.spl scripts/assemble.py shakedown-debug tests/test_assemble.py tests/test_token_dump.py
git commit -m "chore: add token-stream debug target via act four swap"
```

---

## Task 5: Correctness-First Literary Workflow Note

Spike A's plan devoted roughly 40% of its text to literary compliance, and implementation agents were expected to author compliant prose while also solving list parsing. Codify the fix: literary authorship happens at **planning time**; implementation agents consume pre-reserved prose and never invent controlled surfaces mid-task.

**Files:**
- Create: `docs/superpowers/notes/correctness-first-spl-workflow.md`
- Modify: `docs/superpowers/notes/spl-literary-protocol.md` (append one rule)
- Modify: `CLAUDE.md` (append one paragraph to the literary protocol section)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: the workflow note path `docs/superpowers/notes/correctness-first-spl-workflow.md`, referenced by future SPL-changing plans.

- [ ] **Step 1: Write the workflow note**

Create `docs/superpowers/notes/correctness-first-spl-workflow.md`:

```markdown
# Correctness-First SPL Workflow

Literary authorship happens at planning time, not implementation time.
Implementation agents solve byte parity; they never invent controlled
prose mid-task. This note is normative for every SPL-changing plan,
alongside `docs/superpowers/notes/spl-literary-protocol.md`.

## Rules for plan authors

1. **Reserve all controlled surfaces in the plan.** Every scene title,
   Recall line, and recurring value phrase the implementation will need
   is written into the plan as ready-to-paste `src/literary.toml`
   blocks, validated against `docs/spl/literary-spec.md` and
   `docs/spl/style-lexicon.md` during planning (Spike A Task 2 is the
   model — that part of Spike A worked).
2. **Reserve spares.** Include at least four spare pre-approved scene
   titles per act touched, clearly marked as the spare pool, so a
   mid-task structural surprise does not force an agent to author prose.
3. **Sequence polish after parity.** Voice, motif, and palette
   improvements beyond the reserved surfaces land as separate commits
   after the plan's parity gates pass — never in the same commit as a
   correctness change.

## Rules for implementation agents

1. Take scene titles only from the plan's reserved blocks or spare pool.
2. If the spare pool runs out, that is a plan defect: stop the task and
   report it. Do not improvise literary prose.
3. Keep the scene ledger in sync per commit: a new `Scene @LABEL:` in
   `src/*.spl` and its `[scenes.LABEL]` entry (from the reserved blocks)
   land in the same commit.
4. Debug artifacts (`debug/*.spl`, anything under `.cache/`) are outside
   literary scope: no `@LIT.` placeholders, no `src/literary.toml`
   entries, plain literal titles.
```

- [ ] **Step 2: Reference the note from the protocol**

In `docs/superpowers/notes/spl-literary-protocol.md`, append to the `Rules:` list (do not modify existing lines — tests assert on their exact wording):

```markdown
- Reserve every controlled surface the implementation will need — plus a
  spare scene-title pool — at plan time, per
  `docs/superpowers/notes/correctness-first-spl-workflow.md`.
  Implementation agents must not author new controlled prose mid-task.
```

- [ ] **Step 3: Reference the note from CLAUDE.md**

In `CLAUDE.md`, append this paragraph to the end of the `## SPL literary protocol for prompts and plans` section (after the "Do not hand-edit `shakedown.spl` ..." paragraph, adding — not rewording — existing text, which tests assert on):

```markdown
Literary authorship happens at planning time, not implementation time:
see `docs/superpowers/notes/correctness-first-spl-workflow.md`. Plans
reserve all controlled prose (plus spare scene titles) up front, and
implementation agents never invent literary surfaces mid-task.
```

- [ ] **Step 4: Run the docs-contract tests**

Run: `uv run pytest tests/test_prompt_literary_protocol.py tests/test_roadmap_contract.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/notes/correctness-first-spl-workflow.md docs/superpowers/notes/spl-literary-protocol.md CLAUDE.md
git commit -m "docs: add correctness-first SPL workflow note"
```

---

## Task 6: Record the Spike A Halt and Hand Off the Roadmap

Spike A hit the architecture's own §8.2 halt condition: hand-authoring the Act II list pass produced a ~1,300-line diff that never reached a parseable state, and work stalled for two months. Record the halt, xfail the spike tests so the suite signal stays clean, mark this plan in flight, and point the halt resolution at the SPL-from-IR generator redesign (an interactive design session — explicitly out of scope for this plan).

**Files:**
- Modify: `.agent/blockers.md`
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: `tests/test_architecture_spikes.py`
- Commit: `docs/superpowers/plans/2026-07-05-agent-feedback-rails.md` (this plan)

**Interfaces:**
- Consumes: branch name `spike-a-lists-wip` from Task 1.
- Produces: roadmap with exactly one `in flight` row (this plan); a green default test suite.

- [ ] **Step 1: xfail the halted spike tests**

In `tests/test_architecture_spikes.py`, replace the parametrized test's decorator so each case carries an xfail mark (keep the test body unchanged):

```python
_SPIKE_A_HALT_REASON = (
    "Spike A halted per architecture §8.2 on 2026-07-05; "
    "see docs/superpowers/plans/plan-roadmap.md and .agent/blockers.md"
)


@pytest.mark.parametrize(
    "fixture",
    [
        pytest.param(
            path,
            id=path.stem,
            marks=pytest.mark.xfail(reason=_SPIKE_A_HALT_REASON, strict=False),
        )
        for path in _list_cases()
    ],
)
def test_list_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
```

Run: `uv run pytest tests/test_architecture_spikes.py -q`
Expected: no failures — only `xfailed` (and possibly `xpassed`) outcomes.

- [ ] **Step 2: Record the halt in blockers**

Append to `.agent/blockers.md`:

```markdown
- BLOCK: Spike A halted per architecture §8.2 on 2026-07-05. Hand-authoring
  the Act II list pass produced a ~1,300-line diff that never reached a
  parseable state (preserved on branch spike-a-lists-wip). Root cause is
  authoring SPL by hand at scale, not list semantics. Resolution direction:
  revise the architecture so SPL is generated from a small intermediate
  representation (interactive design session required). Do not resume list
  implementation until the revised architecture ships.
```

- [ ] **Step 3: Update the roadmap**

In `docs/superpowers/plans/plan-roadmap.md`:

1. In the plan-ladder table, change row 3's Status cell from `in flight` to:

```text
halted: 2026-07-05 per §8.2 — hand-authored Act II list SPL never reached a parseable state; WIP preserved on branch spike-a-lists-wip; resume after the SPL-from-IR architecture revision
```

2. Insert a new row directly after row 3:

```text
| 3F | Agent Feedback Rails (`docs/superpowers/plans/2026-07-05-agent-feedback-rails.md`) | §8.2 halt support / tooling | Wrapper parse-error guard, assemble-time parse gate, parse smoke test, token-stream debug target (`./shakedown-debug`), correctness-first literary workflow note, Spike A halt recorded | Default pytest suite green (spike list cases xfail with halt reason); wrapper exits nonzero on parse errors; debug target dumps an integer token stream for the Amps fixture | in flight |
```

3. Append to the `## Halt-and-redesign` section:

```markdown
Active halt: Spike A (2026-07-05). The accepted resolution direction is to
stop hand-authoring SPL and generate it from a small intermediate
representation (scenes as states; operations for character tests, stack
push/pop, jumps, and token emission), extending the existing
assembler/codegen pipeline. This requires re-opening
`docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` in an
interactive design session before any replacement list plan is written.
```

4. Update the `**Last updated:**` line to `2026-07-05`.

- [ ] **Step 4: Run the roadmap and protocol contract tests**

Run: `uv run pytest tests/test_roadmap_contract.py tests/test_prompt_literary_protocol.py -v`
Expected: all PASS — exactly one in-flight row, and this plan file contains the protocol reference and the named compliance-test commands.

- [ ] **Step 5: Run the full literary and parity regression gates**

Run:

```bash
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: all PASS; `1 passed, 22 deselected` for the fixture gate.

- [ ] **Step 6: Run the full default suite**

Run: `uv run pytest`
Expected: green — no failures; spike list cases report xfail/xpass.

- [ ] **Step 7: Commit**

```bash
git add .agent/blockers.md docs/superpowers/plans/plan-roadmap.md tests/test_architecture_spikes.py docs/superpowers/plans/2026-07-05-agent-feedback-rails.md
git commit -m "docs: record spike a halt and mark agent feedback rails in flight"
```

---

## Out of Scope (Deliberately)

- **The SPL-from-IR generator itself.** That is the Spike A halt resolution and needs an interactive `superpowers:brainstorming` + architecture-spec revision session first (per the roadmap's halt-and-redesign process). This plan records the direction; it does not design or build it.
- **In-process test harness speedup** (reusing a parsed `shakespearelang` AST across fixtures). Worth a spike after the IR design session; not a rail.
- **Any change to Markdown behavior.** `shakedown.spl` output is byte-identical before and after this plan.

## Completion Criteria

- `main` working tree is clean; the Spike A WIP lives on `spike-a-lists-wip`.
- `./shakedown` exits nonzero (with the error on stderr) when the play has a parse error.
- `scripts/assemble.py` refuses to write a non-parsing `shakedown.spl`, and `uv run pytest` fails fast with the real parse error if the committed play is broken.
- `printf '* alpha\n' | ./shakedown-debug` style invocations print an integer token stream instead of silence.
- `docs/superpowers/notes/correctness-first-spl-workflow.md` exists and is referenced from the protocol note and `CLAUDE.md`.
- The roadmap shows Spike A halted with the IR-codegen resolution direction recorded, this plan in flight, and `uv run pytest` fully green.
