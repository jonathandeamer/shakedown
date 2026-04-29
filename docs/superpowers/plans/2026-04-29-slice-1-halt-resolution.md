# Slice 1 Halt Resolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the Slice 1 line-budget halt by replacing fixture-specific unrolling and hardcoded full anchor outputs while preserving byte-identical SPL-owned behavior for `Amps and angle encoding`.

**Architecture:** Preserve the four-act split as the first proof path, per `docs/superpowers/specs/2026-04-29-slice-1-halt-resolution-design.md` Option B. Act I must strip/capture reference definitions by delimiter-driven SPL logic, Act III must parse link destinations by delimiters rather than fixed lengths, and Act IV must emit reusable anchor pieces. Markdown behavior remains in SPL; Python may only assemble, test, and generate literal-byte SPL phrases.

**Tech Stack:** Shakespeare Programming Language (`shakespearelang` via `uv run shakespeare`), `scripts/assemble.py`, `scripts/codegen_html.py`, `scripts/strict_parity_harness.py`, pytest, ruff, pyright, local `~/markdown/Markdown.pl` oracle.

---

## Source-of-truth References

- `docs/superpowers/specs/2026-04-29-slice-1-halt-resolution-design.md` — accepted halt-resolution design and acceptance criteria.
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — selected architecture, §7.2 Slice 1 scope, §8.1 gates, and §8.2 halt trigger.
- `docs/superpowers/plans/2026-04-28-slice-1-amps-angle-encoding.md` — superseded Slice 1 implementation history; use for context only.
- `docs/markdown/reference-mechanics.md` — reference definition and reference link mechanics.
- `docs/markdown/oracle-mechanics.md` — Markdown.pl transform order.
- `docs/spl/reference.md` — SPL syntax and interpreter semantics.
- `docs/spl/literary-spec.md` and `src/literary.toml` — legal voice and phrase policy.
- `.agent/blockers.md` — keep the existing Slice 1 line-budget block until this plan's final acceptance step.

## File Map

**Modify in this plan:**

- `tests/test_slice1_amps_angle.py` — add structural checks that reject the known unscalable Slice 1 forms.
- `src/10-act1-preprocess.spl` — replace exact 65-glyph reference-tail stripping with delimiter-driven reference-line recognition.
- `src/30-act3-span.spl` — replace fixed-length inline destination popping and full hardcoded anchor-output scenes with delimiter-driven link parsing and reusable anchor token/piece output.
- `src/40-act4-emit.spl` — emit reusable anchor pieces and payloads instead of relying on Act III full anchor literals.
- `shakedown.spl` — assembled release artifact.
- `docs/performance/budget.md` or `docs/verification-plan.md` — record the post-resolution Slice 1 timing, using the established benchmark protocol.
- `docs/superpowers/plans/plan-roadmap.md` — mark this replacement plan shipped after the halt is resolved.
- `docs/prompt-shakedown.md` — deactivate this plan after it ships.
- `.agent/blockers.md` — remove the Slice 1 line-budget block only in the final acceptance task, after proof and operator acceptance are satisfied.

**Do not modify in this plan:**

- `docs/markdown/divergences.md`; expected outcome is strict parity with no divergence.
- `CHANGELOG.md`, tags, or version metadata; version cuts are operator-only.
- `scripts/shakedown_run.py`; the wrapper already invokes the committed SPL artifact and owns no Markdown behavior.

## Replacement Invariants

The implementation must satisfy all of these before the blocker can be removed:

- No scene named `@HECATE_CUT_REFERENCE_TAIL`.
- No scene named `@LYRIC_INLINE_POP_DIRECT_DESTINATION`.
- No scene named `@LYRIC_INLINE_POP_BRACKETED_DESTINATION`.
- No scene named `@LYRIC_OUTPUT_REFERENCE_ONE`.
- No scene named `@LYRIC_OUTPUT_REFERENCE_TWO`.
- No scene named `@LYRIC_OUTPUT_INLINE_LINK`.
- No `Recall ... glyph 65`, `Recall ... glyph 21`, or `Recall ... glyph 19` sequence used to consume fixture-specific fixed-length content.
- No Python code decides Markdown parsing or output structure.

---

## Task 1: Structural Regression Gate

**Files:**
- Modify: `tests/test_slice1_amps_angle.py`

- [x] **Step 1.1: Add the failing structural checks**

Append these tests to `tests/test_slice1_amps_angle.py`:

```python
SRC = REPO / "src"


def test_slice1_avoids_known_fixture_specific_scene_shapes() -> None:
    source = "\n".join(
        path.read_text()
        for path in (
            SRC / "10-act1-preprocess.spl",
            SRC / "30-act3-span.spl",
        )
    )
    forbidden_labels = {
        "@HECATE_CUT_REFERENCE_TAIL",
        "@LYRIC_INLINE_POP_DIRECT_DESTINATION",
        "@LYRIC_INLINE_POP_BRACKETED_DESTINATION",
        "@LYRIC_OUTPUT_REFERENCE_ONE",
        "@LYRIC_OUTPUT_REFERENCE_TWO",
        "@LYRIC_OUTPUT_INLINE_LINK",
    }
    present = sorted(label for label in forbidden_labels if label in source)
    assert not present, f"fixture-specific scene labels remain: {present}"


def test_slice1_avoids_known_fixed_length_glyph_consumption() -> None:
    source = "\n".join(
        path.read_text()
        for path in (
            SRC / "10-act1-preprocess.spl",
            SRC / "30-act3-span.spl",
        )
    )
    forbidden_fragments = (
        "Recall the bargain glyph 65",
        "Recall the inline path glyph 19",
        "Recall the bracketed path glyph 21",
    )
    present = [fragment for fragment in forbidden_fragments if fragment in source]
    assert not present, f"fixed-length fixture consumption remains: {present}"
```

- [x] **Step 1.2: Run the structural gate and confirm it fails**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py -q
```

Expected: the existing parity tests pass, and the new structural tests fail with labels/fragments from the current implementation.

- [x] **Step 1.3: Commit the failing structural gate**

```bash
git add tests/test_slice1_amps_angle.py
git commit -m "test: guard Slice 1 against fixture-specific unrolling"
```

---

## Task 2: Act I Delimiter-Driven Reference Stripping

**Files:**
- Modify: `src/10-act1-preprocess.spl`
- Modify: `shakedown.spl`

- [x] **Step 2.1: Replace exact tail stripping with line-buffered reference recognition**

Edit `src/10-act1-preprocess.spl` so Act I uses this shape:

- read stdin character-by-character with `Open your mind!`;
- accumulate the current input line on a scratch stack until newline or EOF;
- when a line is complete, inspect the buffered line by delimiters:
  - first glyph is `[`;
  - next label glyph is `1` or `2`;
  - next glyph is `]`;
  - next glyph is `:`;
  - remaining line payload is consumed until newline;
- for matched labels `1` and `2`, seed Rosalind with the same compact records currently used by Slice 1:
  - label `1` -> URL id `101`, title id `0`;
  - label `2` -> URL id `102`, title id `201`;
- for non-reference lines, replay the buffered line into Hecate's normalized-content stack in original order, including the newline that ended the line;
- append the same final blank-line behavior as the current passing implementation.

Remove the entire `@HECATE_CUT_REFERENCE_TAIL` scene and all `Recall the bargain glyph N` fixed suffix popping.

Use fresh scene labels with the `@HECATE_LINE_` prefix. Do not reuse the forbidden label from Task 1.

- [x] **Step 2.2: Assemble and run the structural gate**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py::test_slice1_avoids_known_fixture_specific_scene_shapes tests/test_slice1_amps_angle.py::test_slice1_avoids_known_fixed_length_glyph_consumption -q
```

Expected: the structural tests still fail for Act III labels/fragments, but no longer report `@HECATE_CUT_REFERENCE_TAIL` or `Recall the bargain glyph 65`.

- [x] **Step 2.3: Verify Act I still feeds the fixture through the pipeline**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py "Amps and angle encoding"
```

Expected: this may fail while Act III/IV are still in the old shape, but it must not crash the interpreter. If it fails, the output should show normal Markdown text still flowing to later acts rather than an empty output or SPL runtime error.

- [x] **Step 2.4: Commit Act I replacement**

```bash
git add src/10-act1-preprocess.spl shakedown.spl
git commit -m "refactor: scan Slice 1 references by delimiter"
```

---

## Task 3: Act III Delimiter-Driven Inline Link Parsing

**Files:**
- Modify: `src/30-act3-span.spl`
- Modify: `shakedown.spl`

- [x] **Step 3.1: Replace fixed-length inline destination popping**

Edit `src/30-act3-span.spl` so inline link parsing consumes destinations by delimiters:

- after `[link](`, pop destination glyphs until `)` for the bare form;
- after `[link](<`, pop destination glyphs until `>` and then require `)`;
- while collecting the destination, keep payload glyphs on a destination stack rather than discarding a fixed number of characters;
- preserve the current Slice 1 behavior that both inline forms emit the same URL payload `/script?foo=1&amp;bar=2`;
- keep ampersand encoding inside the destination in SPL by testing `&` and pushing `&amp;` output pieces, not by asking Python to precompute the decision.

Remove both fixed-length scenes:

- `@LYRIC_INLINE_POP_DIRECT_DESTINATION`
- `@LYRIC_INLINE_POP_BRACKETED_DESTINATION`

Use fresh scene labels with the `@LYRIC_INLINE_DEST_` prefix.

- [x] **Step 3.2: Assemble and run the structural gate**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py::test_slice1_avoids_known_fixture_specific_scene_shapes tests/test_slice1_amps_angle.py::test_slice1_avoids_known_fixed_length_glyph_consumption -q
```

Expected: the structural tests still fail only for the full anchor-output scenes. They must no longer report the two fixed inline destination labels or the 19/21 glyph fragments.

- [x] **Step 3.3: Verify inline links still match the oracle**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py "Amps and angle encoding"
```

Expected: strict parity may still fail until Task 4 moves anchor emission, but the two inline-link paragraphs must appear in the output with `<a href="/script?foo=1&amp;bar=2">link</a>`.

- [x] **Step 3.4: Commit delimiter-driven inline parsing**

```bash
git add src/30-act3-span.spl shakedown.spl
git commit -m "refactor: parse Slice 1 inline destinations by delimiter"
```

---

## Task 4: Reusable Anchor Emission Contract

**Files:**
- Modify: `src/30-act3-span.spl`
- Modify: `src/40-act4-emit.spl`
- Modify: `shakedown.spl`

- [x] **Step 4.1: Move full anchor literals out of Act III**

Edit `src/30-act3-span.spl` and `src/40-act4-emit.spl` to use reusable anchor pieces:

- Act III may still decide whether a construct is an inline link, reference link, missing reference fallback, or literal text. That is Markdown behavior and must stay in SPL.
- Act III must not push a complete fixture-specific anchor string as one hardcoded output scene.
- Act III should push a small anchor marker sequence onto Puck's transformed stream:
  - anchor-open marker;
  - URL payload glyphs already entity-encoded by SPL;
  - optional title marker and title payload glyphs already entity-encoded by SPL;
  - label/text marker and link text payload glyphs already entity-encoded by SPL;
  - anchor-close marker.
- Act IV should emit reusable fixed literals around those payload sections:
  - `<a href="`
  - `"`
  - ` title="`
  - `">`
  - `</a>`

Use existing token-code values only if they are already sufficient. If a new inline marker code is required, add it to `docs/spl/token-codes.md` and update `tests/test_token_codes.py` in the same step before using it in SPL.

Remove these Act III scenes entirely:

- `@LYRIC_OUTPUT_REFERENCE_ONE`
- `@LYRIC_OUTPUT_REFERENCE_TWO`
- `@LYRIC_OUTPUT_INLINE_LINK`

- [x] **Step 4.2: Assemble and run the structural gate**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py::test_slice1_avoids_known_fixture_specific_scene_shapes tests/test_slice1_amps_angle.py::test_slice1_avoids_known_fixed_length_glyph_consumption -q
```

Expected: both structural tests pass.

- [x] **Step 4.3: Verify strict Slice 1 parity**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py "Amps and angle encoding"
```

Expected: `summary: 1/1 byte-identical`.

- [x] **Step 4.4: Commit reusable anchor emission**

```bash
git add src/30-act3-span.spl src/40-act4-emit.spl shakedown.spl docs/spl/token-codes.md tests/test_token_codes.py
git commit -m "refactor: emit Slice 1 anchors from reusable pieces"
```

If `docs/spl/token-codes.md` and `tests/test_token_codes.py` did not change, leave them out of `git add`.

---

## Task 5: Full Gate, Runtime Record, and Halt Resolution

**Files:**
- Modify: `docs/performance/budget.md` or `docs/verification-plan.md`
- Modify: `.agent/blockers.md`
- Modify: `docs/superpowers/plans/2026-04-29-slice-1-halt-resolution.md`
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: `docs/prompt-shakedown.md`

- [x] **Step 5.1: Run the full Slice 1 gate**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py -q
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py "Amps and angle encoding"
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k "Amps and angle" -q
```

Expected:

- `tests/test_slice1_amps_angle.py` passes, including structural checks.
- Strict parity reports `summary: 1/1 byte-identical`.
- The selected mdtest fixture passes.

- [x] **Step 5.2: Run setup/unit no-regression checks**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_token_codes.py tests/test_iconic_moments.py tests/test_literary_toml_schema.py tests/test_codegen_html.py tests/test_shakedown_run.py tests/test_strict_parity_harness.py -q
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check scripts/ tests/
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright scripts/codegen_html.py scripts/shakedown_run.py scripts/strict_parity_harness.py scripts/cache_spike.py
```

Expected: all tests/checks pass.

- [ ] **Step 5.3: Measure and record Slice 1 runtime**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/measure_spl_cost.py shakedown.spl --stdin ~/mdtest/Markdown.mdtest/"Amps and angle encoding.text" --runs 5
```

Record the output in `docs/verification-plan.md` as a new dated bucket after B19 or in `docs/performance/budget.md` under "Current Recorded Baselines". Include:

- date `2026-04-29` or the actual run date;
- exact command;
- first and median times;
- all five run times;
- current commit SHA.

- [ ] **Step 5.4: Update roadmap and run-loop prompt**

Edit `docs/superpowers/plans/plan-roadmap.md`:

- mark the original Slice 1 plan row as superseded by this replacement plan;
- mark this replacement plan row as `shipped: <date> at commit <sha>` after the verification commit SHA is known;
- leave Spike A pending.

Edit `docs/prompt-shakedown.md`:

- remove `@docs/superpowers/plans/2026-04-29-slice-1-halt-resolution.md`;
- restore the idle wording that exits when no plan is `in flight`, unless the operator has already written and marked Spike A as in flight.

- [ ] **Step 5.5: Remove the blocker**

Edit `.agent/blockers.md` and remove only this line:

```text
- BLOCK: Slice 1 shakedown.spl exceeds architecture line-budget halt trigger
```

Do not remove unrelated future `- BLOCK:` lines.

- [ ] **Step 5.6: Commit halt resolution**

```bash
git add docs/performance/budget.md docs/verification-plan.md .agent/blockers.md docs/superpowers/plans/2026-04-29-slice-1-halt-resolution.md docs/superpowers/plans/plan-roadmap.md docs/prompt-shakedown.md
git commit -m "docs: mark Slice 1 halt resolved"
```

If either `docs/performance/budget.md` or `docs/verification-plan.md` did not change, leave the unchanged file out of `git add`.

---

## Final Verification Checklist

Before this replacement plan is complete, confirm:

1. `env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py -q` passes.
2. `env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py "Amps and angle encoding"` reports `summary: 1/1 byte-identical`.
3. `env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k "Amps and angle" -q` passes.
4. `./shakedown` contains no `Markdown.pl`, `ORACLE`, or `exec perl` reference.
5. `rg "HECATE_CUT_REFERENCE_TAIL|LYRIC_INLINE_POP_DIRECT_DESTINATION|LYRIC_INLINE_POP_BRACKETED_DESTINATION|LYRIC_OUTPUT_REFERENCE_ONE|LYRIC_OUTPUT_REFERENCE_TWO|LYRIC_OUTPUT_INLINE_LINK|Recall the bargain glyph 65|Recall the inline path glyph 19|Recall the bracketed path glyph 21" src/10-act1-preprocess.spl src/30-act3-span.spl` returns no matches.
6. Runtime is recorded using `scripts/measure_spl_cost.py` with fixture stdin.
7. `.agent/blockers.md` no longer contains the Slice 1 line-budget block.
8. `docs/markdown/divergences.md` is unchanged.

## Self-Review

- **Spec coverage:** This plan implements Option B from the halt-resolution design: structural tests, delimiter-driven Act I reference stripping, delimiter-driven Act III inline parsing, reusable anchor emission, strict parity, runtime recording, roadmap/prompt cleanup, and blocker removal only after proof.
- **Placeholder scan:** No placeholder work is present. The plan names exact files, exact forbidden forms, exact commands, and expected outcomes for each step.
- **Type/name consistency:** The plan consistently uses existing paths and known labels from the current implementation. New scene prefixes are specified as `@HECATE_LINE_` and `@LYRIC_INLINE_DEST_`; no later step depends on a different name.
