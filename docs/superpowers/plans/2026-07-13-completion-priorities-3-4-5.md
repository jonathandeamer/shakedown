# Completion Priorities 3, 4, and 5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement completion priorities 3, 4, and 5 to accelerate the loop's test cycles, verify large documentation aggregates early, and extract reusable splc IR compilation idioms.

**Architecture:** 
1. Create `scripts/probe_documentation_aggregates.py` to run the two Slice-5 aggregates through the IR interpreter and fail early on crashes or execution times exceeding 5 seconds.
2. Update `tests/test_mdtest.py` and `tests/test_architecture_spikes.py` to run the fast IR interpreter first for every test case.
3. Extract shared IR building blocks (pop_glyph, stream_literal, entity_encode) to `scripts/splc/idioms.py` and document them in `docs/superpowers/notes/spl-shared-idioms.md`.

**Tech Stack:** Python 3.12, splc compiler, pytest, local mdtest corpus, splc IR interpreter.

---

### Task 1: Create the Slice-5 documentation aggregates probe

**Files:**
- Create: `scripts/probe_documentation_aggregates.py`
- Create: `tests/test_documentation_probes.py`

- [ ] **Step 1: Write the probe script**

  Create `scripts/probe_documentation_aggregates.py` with:

  ```python
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
                  print(f"  ERROR: {stem} exceeded time limit of {TIMEOUT_LIMIT_SECONDS}s", file=sys.stderr)
                  failures += 1
          except Exception as exc:
              print(f"  CRASH: {stem} failed in IR interpreter: {exc}", file=sys.stderr)
              failures += 1
              
      return 1 if failures > 0 else 0

  if __name__ == "__main__":
      sys.exit(main())
  ```

- [ ] **Step 2: Create the integration test**

  Create `tests/test_documentation_probes.py` with:

  ```python
  """Integration test for the Slice-5 documentation aggregates probe."""

  import pytest
  from scripts.probe_documentation_aggregates import main

  @pytest.mark.integration
  def test_documentation_probes_run_successfully() -> None:
      rc = main()
      assert rc == 0, "Slice-5 documentation probe failed or exceeded time limits"
  ```

- [ ] **Step 3: Run the tests**

  Run: `uv run pytest tests/test_documentation_probes.py -v` (Note: skip if no local fixtures directory is available).
  Expected: PASS or skipped.

- [ ] **Step 4: Commit**

  ```bash
  git add scripts/probe_documentation_aggregates.py tests/test_documentation_probes.py
  git commit -m "chore: add Slice-5 documentation aggregates probe"
  ```

---

### Task 2: Make the fast IR interpreter the default inner loop in tests

**Files:**
- Modify: `tests/test_mdtest.py`
- Modify: `tests/test_architecture_spikes.py`

- [ ] **Step 1: Update `tests/test_mdtest.py` to run the IR interpreter first**

  Replace the `test_mdtest` implementation with the following. We import the acts and interpreter on demand to avoid module startup overhead when tests are skipped:

  ```python
  def _interpret_ir(input_text: str) -> str:
      from src_ir.act1 import ACT as ACT1
      from src_ir.act2 import ACT as ACT2
      from src_ir.act3 import ACT as ACT3
      from src_ir.act4 import ACT as ACT4
      from scripts.splc.interpret import InterpreterState, run_act
      
      state = InterpreterState(input_text=input_text)
      state = run_act(ACT1, state, step_limit=500_000).state
      state = run_act(ACT2, state, step_limit=500_000).state
      state = run_act(ACT3, state, step_limit=500_000).state
      state = run_act(ACT4, state, step_limit=500_000).state
      return state.output_text()


  @pytest.mark.parametrize("name,input_path,expected_path", _fixture_params())
  def test_mdtest(name: str, input_path: Path, expected_path: Path) -> None:
      input_text = input_path.read_text()
      expected = expected_path.read_text()
      norm_expected = _normalize(expected)
      if name == "Auto links":
          norm_expected = _decode_entities(norm_expected)

      # 1. Run the fast IR interpreter first
      interpret_actual = _interpret_ir(input_text)
      norm_interpret = _normalize(interpret_actual)
      if name == "Auto links":
          norm_interpret = _decode_entities(norm_interpret)
      assert norm_interpret == norm_expected, (
          f"IR Interpreter output mismatch for '{name}'\n"
          f"--- expected\n{norm_expected}\n"
          f"+++ actual (IR)\n{norm_interpret}"
      )

      # 2. Run the real binary to prove parity
      result = subprocess.run(
          [str(BINARY)],
          input=input_text,
          capture_output=True,
          text=True,
      )
      actual = result.stdout
      norm_actual = _normalize(actual)
      if name == "Auto links":
          norm_actual = _decode_entities(norm_actual)

      assert norm_actual == norm_expected, (
          f"Binary output mismatch for '{name}'\n"
          f"--- expected\n{norm_expected}\n"
          f"+++ actual (Binary)\n{norm_actual}"
      )
  ```

- [ ] **Step 2: Update `tests/test_architecture_spikes.py` to run the IR interpreter first**

  Add the `_interpret_ir_bytes` helper and update the test case functions in `tests/test_architecture_spikes.py`:

  ```python
  def _interpret_ir_bytes(input_bytes: bytes) -> bytes:
      from src_ir.act1 import ACT as ACT1
      from src_ir.act2 import ACT as ACT2
      from src_ir.act3 import ACT as ACT3
      from src_ir.act4 import ACT as ACT4
      from scripts.splc.interpret import InterpreterState, run_act
      
      input_text = input_bytes.decode("utf-8")
      state = InterpreterState(input_text=input_text)
      state = run_act(ACT1, state, step_limit=500_000).state
      state = run_act(ACT2, state, step_limit=500_000).state
      state = run_act(ACT3, state, step_limit=500_000).state
      state = run_act(ACT4, state, step_limit=500_000).state
      return state.output_text().encode("utf-8")


  @pytest.mark.parametrize("fixture", _list_cases(), ids=lambda path: path.stem)
  def test_list_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
      input_bytes = fixture.read_bytes()
      expected = _run(["perl", str(MARKDOWN_PL)], input_bytes)

      # 1. Run IR interpreter
      interpret_actual = _interpret_ir_bytes(input_bytes)
      assert interpret_actual == expected, (
          f"IR Interpreter mismatch for list fixture {fixture.name}\n"
          f"--- expected\n{expected.decode(errors='replace')}\n"
          f"+++ actual (IR)\n{interpret_actual.decode(errors='replace')}"
      )

      # 2. Run real binary
      actual = _run([str(SHAKEDOWN)], input_bytes)
      assert actual == expected, (
          f"Output mismatch for {fixture.name}; first diff: "
          f"{_first_diff(actual, expected)}\n"
          f"--- expected\n{expected.decode(errors='replace')}\n"
          f"+++ actual\n{actual.decode(errors='replace')}"
      )


  @pytest.mark.parametrize("fixture", _nested_block_cases(), ids=lambda path: path.stem)
  def test_nested_block_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
      input_bytes = fixture.read_bytes()
      expected = _run(["perl", str(MARKDOWN_PL)], input_bytes)

      # 1. Run IR interpreter
      interpret_actual = _interpret_ir_bytes(input_bytes)
      assert interpret_actual == expected, (
          f"IR Interpreter mismatch for nested block fixture {fixture.name}\n"
          f"--- expected\n{expected.decode(errors='replace')}\n"
          f"+++ actual (IR)\n{interpret_actual.decode(errors='replace')}"
      )

      # 2. Run real binary
      actual = _run([str(SHAKEDOWN)], input_bytes)
      assert actual == expected, (
          f"Output mismatch for {fixture.name}; first diff: "
          f"{_first_diff(actual, expected)}\n"
          f"--- expected\n{expected.decode(errors='replace')}\n"
          f"+++ actual\n{actual.decode(errors='replace')}"
      )


  @pytest.mark.parametrize(
      ("input_bytes", "expected"),
      [(input_bytes, expected) for _, input_bytes, expected in NESTED_BLOCK_BYTE_CASES],
      ids=[stem for stem, _, _ in NESTED_BLOCK_BYTE_CASES],
  )
  def test_nested_block_architecture_spike_emits_expected_bytes(
      input_bytes: bytes,
      expected: bytes,
  ) -> None:
      # 1. Run IR interpreter
      assert _interpret_ir_bytes(input_bytes) == expected
      # 2. Run real binary
      assert _run([str(SHAKEDOWN)], input_bytes) == expected


  @pytest.mark.parametrize("fixture", _span_cases(), ids=lambda path: path.stem)
  def test_span_architecture_spike_matches_checked_in_oracle_bytes(
      fixture: Path,
  ) -> None:
      input_bytes = fixture.read_bytes()
      expected = fixture.with_suffix(".expected").read_bytes()
      
      # 1. Run IR interpreter
      interpret_actual = _interpret_ir_bytes(input_bytes)
      assert interpret_actual == expected, (
          f"IR Interpreter mismatch for span fixture {fixture.name}\n"
          f"--- expected\n{expected.decode(errors='replace')}\n"
          f"+++ actual (IR)\n{interpret_actual.decode(errors='replace')}"
      )

      # 2. Run real binary
      shakedown_output = _run([str(SHAKEDOWN)], input_bytes)
      assert shakedown_output == expected, (
          f"Output mismatch for {fixture.name}; first diff: "
          f"{_first_diff(shakedown_output, expected)}\n"
          f"--- expected\n{expected.decode(errors='replace')}\n"
          f"+++ actual\n{shakedown_output.decode(errors='replace')}"
      )
  ```

- [ ] **Step 3: Run the test suite**

  Run: `uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py -v`
  Expected: PASS

- [ ] **Step 4: Commit**

  ```bash
  git add tests/test_mdtest.py tests/test_architecture_spikes.py
  git commit -m "chore: run fast IR interpreter first in pytest inner loop"
  ```

---

### Task 3: Extract and document reusable splc IR idioms

**Files:**
- Create: `scripts/splc/idioms.py`
- Create: `docs/superpowers/notes/spl-shared-idioms.md`

- [ ] **Step 1: Extract reusable compilation helpers**

  Create `scripts/splc/idioms.py` containing:

  ```python
  """Reusable splc IR compilation idioms and helper functions.

  Provides helper functions for common Act III / Act IV choreography patterns.
  """

  from scripts.splc.ir import (
      Op,
      Char,
      let,
      const,
      push,
      pop,
      sub,
      val,
      Expr,
  )

  def pop_glyph(target_char: Char, scan_char: Char, recall_key: str) -> list[Op]:
      """Pop the next glyph into target_char and decrement scan_char's scan count."""
      return [
          pop(target_char, recall=recall_key),
          let(scan_char, sub(val(scan_char), const(1))),
      ]

  def stream_literal(target_char: Char, *codes: int) -> list[Op]:
      """Push token codes / payload bytes onto a character's forward stream."""
      return [push(target_char, const(code)) for code in codes]

  def entity_encode(target_char: Char, *codes: int) -> list[Op]:
      """Let+push pairs on target_char (entity-emission idiom)."""
      ops: list[Op] = []
      for code in codes:
          ops.append(let(target_char, const(code)))
          ops.append(push(target_char, val(target_char)))
      return ops
  ```

- [ ] **Step 2: Document the idioms**

  Create `docs/superpowers/notes/spl-shared-idioms.md` with:

  ```markdown
  # Shared splc IR Compilation Idioms

  This document summarizes the core compilation idioms established by Amendment A2 to fit complex Acts inside Shakespeare Programming Language (SPL) constraints.

  ## 1. Bounded Scan Pipeline (`LYRIC_FIELD_*`)
  HTML tags, autolink URLs, link destinations, and titles are compiled via a shared scan pipeline. 
  Instead of dedicating separate scenes for each call site, we parameterize a single scanner on Juliet using a call-site register (`HECATE`).
  * The caller sets a unique call-site code in `HECATE` and jumps to `LYRIC_FIELD_OPEN`.
  * The shared pipeline processes characters and uses conditional branches based on `HECATE` to exit back to the correct caller continuation.

  ## 2. Capture-Hold-Requeue (Horatio Hold)
  When content must be processed (e.g., strong/emphasis scans inside link label text) but output in a different order (e.g., link label appears after the `href` attribute in HTML), we capture raw input characters onto `HORATIO`'s stack first.
  * Destination and titles are processed and written directly to `JULIET`.
  * The held raw characters are then pushed back onto `PUCK`'s source buffer under a private resume sentinel.
  * Ordinary top-level scan dispatch is resumed, processing entities and emphasis for free without duplicating any logic.

  ## 3. Duplicate-on-Reverse
  For autolinks, the URL is emitted twice (once into `href`, once into the link text).
  During the stack reverse operation in `LYRIC_FIELD_REV_KEEP`, a second copy is pushed back onto `ROMEO`'s stack when the call-site code specifies it. This allows re-draining the capture buffer without executing a second scan of the source.
  ```

- [ ] **Step 3: Run pyright to ensure type safety**

  Run: `uv run pyright scripts/splc/idioms.py`
  Expected: 0 errors

- [ ] **Step 4: Commit**

  ```bash
  git add scripts/splc/idioms.py docs/superpowers/notes/spl-shared-idioms.md
  git commit -m "docs: extract and document shared splc IR idioms"
  ```
