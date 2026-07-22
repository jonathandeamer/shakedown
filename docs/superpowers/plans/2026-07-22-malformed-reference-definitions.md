# Malformed Reference Definitions Match the Oracle — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make three malformed reference-definition forms render as literal paragraphs from `./shakedown`, matching the Markdown.pl oracle.

**Architecture:** Fix the SPL/IR reference-strip machine. Bugs 1–2 tighten Act I's candidate detector (`src_ir/act1_ref_pure.py` scenes) to require a non-empty label and a non-empty URL. Bug 3 addresses Act III's redundant definition re-detector (`src_ir/act3.py` `LYRIC_DEFINITION_*`): a spike task first proves whether it is redundant given a correct Act I, then either bypasses it or fixes its lossy replay. The IR is regenerated to `shakedown.spl` and judged on the real binary + 23-fixture oracle parity.

**Tech Stack:** Python 3 IR modules (`src_ir/`), the `splc` compiler (`scripts/splc/`), `shakespearelang` interpreter, `uv`/`pytest`, `perl` oracle (`~/markdown/Markdown.pl`).

## Global Constraints

- **The SPL is the deliverable.** Correctness is judged on `./shakedown` output and `tests/test_mdtest.py`. No Python-intrinsic-only change resolves any bug; every fix must survive a regen and run on the real binary.
- **Oracle is the judge.** `~/markdown/Markdown.pl` is ground truth. Definition-strip rule: `^[ ]{0,3}\[(.+)\]:` (non-empty label, colon immediately after `]`) **and** a non-empty URL `<?(\S+?)>?`.
- **Literary protocol.** Any new scene requires a scene-title reserved in `src/10-act1-literary.toml` up front (Task 0). Implementation agents never invent titles. All 26 existing Act I ref titles are consumed; Task 0 authors exactly two new ones.
- **SPL Literary Protocol Compliance:** This plan complies with the requirements in `docs/superpowers/notes/spl-literary-protocol.md`. The compliance validation requires verifying the following tests:
  - `tests/test_literary_compliance.py`
  - `tests/test_literary_toml_schema.py`
  - `tests/test_assemble.py`
  - `tests/test_codegen_html.py`
  - `tests/test_mdtest.py -k 'Amps and angle'`
- **SPL structural rules.** Two-person-per-scene rule; ≤4 arithmetic operators per statement.
- **Regen command (run after any `src_ir/` change):** `uv run python -m scripts.splc && uv run python scripts/assemble.py`.
- **Branch:** `fix/malformed-reference-definitions` (already created, based on the ampersand-PR tip so the three `xfail(strict=True)` markers form the seam this plan closes).

---

### Task 0: Reserve the two new Act I guard-scene titles

**Files:**
- Modify: `src/10-act1-literary.toml` (append two `[scenes.*]` blocks after `HECATE_REF_REPLAY_GUARD`)

**Interfaces:**
- Produces: scene titles for labels `HECATE_REF_LABEL_FIRST` and `HECATE_REF_URL_CONTENT`, consumed by Tasks 2–3 when the IR first references those labels.

Two guard scenes are anticipated (empty-label reject; empty-URL reject). Reserving their titles now is the sanctioned planning-time activity that A4.5 forbids at implementation time. If a fix turns out to fit inside an existing scene and a reserved title goes unused, that is acceptable (spare reservation is allowed) — but do **not** delete the reservation in that case; leave it for the sibling fix.

- [ ] **Step 1: Append the two title blocks**

Add to `src/10-act1-literary.toml`:

```toml
[scenes.HECATE_REF_LABEL_FIRST]
title = "The empty name forfeits the shelf."
pattern = "bare_statement"

[scenes.HECATE_REF_URL_CONTENT]
title = "The river road demands one honest mark."
pattern = "bare_statement"
```

- [ ] **Step 2: Verify literary compliance still passes**

Run: `uv run pytest tests/test_literary_compliance.py -q`
Expected: PASS (titles are data; adding unused reservations must not regress).

- [ ] **Step 3: Commit**

```bash
git add src/10-act1-literary.toml
git commit -m "docs: reserve two Act I ref guard-scene titles for malformed-def fix"
```

---

### Task 1: Failing oracle-parity regression tests for all four inputs

**Files:**
- Create: `tests/test_malformed_reference_definitions.py`
- Test: the same file

**Interfaces:**
- Consumes: `scripts.splc.interpret.run_act`, `InterpreterState`; the four act modules `src_ir.act{1,2,3,4}`.
- Produces: `test_malformed_reference_definition_renders_literally` (parametrized), the end-to-end gate every later task must turn green.

These assert the **rendered HTML** through Act IV — the true deliverable surface — independent of the internal `test_act3_contracts.py` xfails. Expected strings are the verified oracle outputs.

- [ ] **Step 1: Write the failing test**

```python
"""Malformed reference definitions must render as literal paragraphs (oracle parity)."""

from __future__ import annotations

import pytest

from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4

STEP_LIMIT = 200_000

# Verified against `perl ~/markdown/Markdown.pl` on 2026-07-22.
CASES = [
    pytest.param("[not]:\n", "<p>[not]:</p>\n", id="empty-url"),
    pytest.param("[not]:   \n", "<p>[not]:   </p>\n", id="empty-url-spaces"),
    pytest.param("[]: destination\n", "<p>[]: destination</p>\n", id="empty-label"),
    pytest.param("[x] : destination\n", "<p>[x] : destination</p>\n", id="space-before-colon"),
]


def _render(src: str) -> str:
    state = InterpreterState(input_text=src)
    for act in (ACT1, ACT2, ACT3, ACT4):
        state = run_act(act, state, step_limit=STEP_LIMIT).state
    return state.output_text()


@pytest.mark.parametrize("src,expected", CASES)
def test_malformed_reference_definition_renders_literally(src: str, expected: str) -> None:
    assert _render(src) == expected
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_malformed_reference_definitions.py -q`
Expected: FAIL — `empty-url`, `empty-url-spaces`, `empty-label` return `"\n"`; `space-before-colon` returns `"<p>x: destination</p>\n"`.

- [ ] **Step 3: Cross-check expected values against the oracle**

Run: `printf '[not]:\n' | perl ~/markdown/Markdown.pl`
Expected: `<p>[not]:</p>` (repeat for each case; confirm the hardcoded expectations before implementing).

- [ ] **Step 4: Commit**

```bash
git add tests/test_malformed_reference_definitions.py
git commit -m "test: failing oracle-parity gate for malformed reference definitions"
```

---

### Task 2: Bug 1 — reject empty label `[]:` in Act I

**Files:**
- Modify: `src_ir/act1_ref_pure.py` (candidate machine: `HECATE_REF_BRACKET` / `HECATE_REF_LABEL`, add `HECATE_REF_LABEL_FIRST`)
- Test: `tests/test_malformed_reference_definitions.py::...[empty-label]`, `tests/test_act1_ref*` if present

**Interfaces:**
- Consumes: reserved title `HECATE_REF_LABEL_FIRST` (Task 0).
- Produces: an Act I candidate machine that keeps `[]:`-leading lines as body.

**Root cause (verified):** `HECATE_REF_LABEL` accepts `]` on its first iteration, so a zero-length label is treated as valid. **Fix:** the first glyph after `[` must be a real label char. Route `HECATE_REF_BRACKET` to a new first-glyph guard `HECATE_REF_LABEL_FIRST` that pops the next glyph and, if it is `]` (`_RB`), `NL` (`_NL`), or EOF, falls through to `HECATE_REF_KEEP` (keep as body); otherwise it keeps the glyph and enters the existing `HECATE_REF_LABEL` loop. Register model unchanged: `Hecate.value` = remaining count, `Puck.stack` = candidate/body glyphs (top = last), `Horatio.value` = BASE. The guard is a `(Hecate, Puck)` scene (it pops from Puck and branches on the glyph), matching `HECATE_REF_LABEL`'s companion.

- [ ] **Step 1: Confirm the failing case in isolation**

Run: `uv run pytest "tests/test_malformed_reference_definitions.py::test_malformed_reference_definition_renders_literally[empty-label]" -q`
Expected: FAIL — returns `"\n"`.

- [ ] **Step 2: Implement the first-label-glyph guard**

In `src_ir/act1_ref_pure.py`, retarget `HECATE_REF_BRACKET`'s `goto` from `HECATE_REF_URL_GUARD` to `HECATE_REF_LABEL_FIRST` (BASE is still set on the path into the label loop — preserve the existing `HECATE_REF_URL_GUARD` BASE computation by having `HECATE_REF_LABEL_FIRST` fall into it, or fold the BASE `let` into the new scene; keep BASE = `ov + rem + 1` semantics identical). Add:

```python
scene(
    "HECATE_REF_LABEL_FIRST",
    # rem == 0 → EOF with only '[' seen: keep as body.
    branch(eq(val(HECATE), _0), then="HECATE_REF_ENCODE"),
    let(PUCK, val(HECATE)),
    pop(HECATE, recall=_RECALL_PUCK),
    # Immediate ']' or NL ⇒ empty label ⇒ not a definition; keep as body.
    branch(eq(val(HECATE), _RB), then="HECATE_REF_KEEP"),
    branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
    push(PUCK, val(HECATE)),  # keep the first real label glyph
    let(HECATE, sub(val(PUCK), _1)),
    goto("HECATE_REF_LABEL"),
    companion=PUCK,
),
```

The exact op tuples (recall names, `_RB`/`_NL` constants, BASE relay) must be developed against the interpreter so `HECATE_REF_KEEP` receives the same register/stack shape it already expects from its other predecessors. Match the surrounding scenes' conventions exactly; the branch-on-`]` before entering the loop is the whole fix.

- [ ] **Step 3: Regenerate and run the target test**

Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py`
Run: `uv run pytest "tests/test_malformed_reference_definitions.py::test_malformed_reference_definition_renders_literally[empty-label]" -q`
Expected: PASS — returns `"<p>[]: destination</p>\n"`.

- [ ] **Step 4: Guard against regressions**

Run: `uv run pytest tests/test_mdtest.py tests/test_splc_generated_fragments.py -q`
Expected: PASS (23 fixtures unchanged; committed fragments match fresh render).

- [ ] **Step 5: Verify on the real binary**

Run: `printf '[]: destination\n' | ./shakedown`
Expected: `<p>[]: destination</p>`

- [ ] **Step 6: Commit**

```bash
git add src_ir/act1_ref_pure.py src/10-act1-literary.toml src/*.spl shakedown.spl
git commit -m "fix: keep empty-label reference lines as body (Act I)"
```

---

### Task 3: Bug 2 — reject empty URL `[not]:` in Act I

**Files:**
- Modify: `src_ir/act1_ref_pure.py` (`HECATE_REF_COLON` / `HECATE_REF_URL_WS`, add `HECATE_REF_URL_CONTENT`)
- Test: `tests/test_malformed_reference_definitions.py::...[empty-url]`, `...[empty-url-spaces]`

**Interfaces:**
- Consumes: reserved title `HECATE_REF_URL_CONTENT` (Task 0).
- Produces: an Act I candidate machine that keeps `[label]:`-with-no-URL lines as body.

**Root cause (verified):** `HECATE_REF_URL_WS` permits the drop when it reaches `NL`/EOF having consumed only whitespace, so `[not]:` and `[not]:   ` drop with an empty URL. **Fix:** the candidate becomes drop-eligible only after ≥1 non-whitespace URL glyph is seen. Split the URL scan into two phases: leading-whitespace consumption stays in `HECATE_REF_URL_WS`, but reaching `NL`/EOF there now routes to `HECATE_REF_KEEP` (keep as body — no URL seen) instead of the drop scene `HECATE_REF_URL`. The first non-whitespace glyph transitions to the new `HECATE_REF_URL_CONTENT`, which consumes the remainder of the destination/title to end-of-line and only *then* permits the drop via `HECATE_REF_URL`. `<` still bridges through `HECATE_REF_ANGLE`.

- [ ] **Step 1: Confirm the failing cases in isolation**

Run: `uv run pytest "tests/test_malformed_reference_definitions.py" -k "empty-url" -q`
Expected: FAIL — both return `"\n"`.

- [ ] **Step 2: Split whitespace-scan from content-scan**

In `HECATE_REF_URL_WS`, change the `NL` (and EOF) branch target from `HECATE_REF_URL` (drop) to `HECATE_REF_KEEP` (keep as body). On the first non-`NL`, non-space glyph, `goto("HECATE_REF_URL_CONTENT")`. Add:

```python
scene(
    "HECATE_REF_URL_CONTENT",
    # At least one URL glyph has been seen; consume to end of line, then drop.
    let(HECATE, sub(val(PUCK), _1)),
    branch(eq(val(HECATE), _0), then="HECATE_REF_URL"),
    let(PUCK, val(HECATE)),
    pop(HECATE, recall=_RECALL_PUCK),
    push(PUCK, val(HECATE)),  # keep glyph (candidate; dropped on match)
    branch(eq(val(HECATE), _NL), then="HECATE_REF_URL"),
    goto("HECATE_REF_URL_CONTENT"),
    companion=PUCK,
),
```

Preserve the existing `rem+1` EOF-safe counter that `HECATE_REF_URL` reads as `BASE - remaining`. The exact register relay (the `PUCK`/`HECATE` scratch on entry from `HECATE_REF_URL_WS`) must be verified against the interpreter so `HECATE_REF_URL`'s `count = BASE - rem` still yields the correct candidate length. The whitespace-only path must reach `HECATE_REF_KEEP` with the same stack shape its other predecessors provide.

- [ ] **Step 3: Regenerate and run the target tests**

Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py`
Run: `uv run pytest "tests/test_malformed_reference_definitions.py" -k "empty-url" -q`
Expected: PASS — `"<p>[not]:</p>\n"` and `"<p>[not]:   </p>\n"`.

- [ ] **Step 4: Guard against regressions (valid defs must still strip)**

Run: `printf '[ref]: /dest/\n\nUse [ref].\n' | ./shakedown` (after regen)
Expected: valid definition still consumed — `<p>Use <a href="/dest/">ref</a>.</p>` (or oracle equivalent; cross-check with `perl`).
Run: `uv run pytest tests/test_mdtest.py tests/test_splc_generated_fragments.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src_ir/act1_ref_pure.py src/10-act1-literary.toml src/*.spl shakedown.spl
git commit -m "fix: keep reference lines with no URL as body (Act I)"
```

---

### Task 4: Bug 3 — Act III lossy definition-replay for `[x] : destination`

**Files:**
- Modify: `src_ir/act3.py` (`LYRIC_DEFINITION_*` scenes) — exact scenes chosen by the Step 1 spike
- Modify: `tests/test_act3_contracts.py` (remove the three `xfail(strict=True)` marks once green)
- Test: `tests/test_malformed_reference_definitions.py::...[space-before-colon]`

**Interfaces:**
- Consumes: a correct Act I from Tasks 2–3 (single source of truth for definition stripping).
- Produces: Act III that never corrupts non-definition paragraph text; the three `test_act3_replays_rejected_definition_candidates_byte_for_byte` cases pass without `xfail`.

**Root cause (verified):** Act I keeps `[x] : destination` as body; Act III's redundant `LYRIC_DEFINITION_*` detector rejects it (space before colon) but its `LYRIC_DEFINITION_REPLAY_*` restoration drops `[`/`]` and collapses ` :`→`:`. The spec left the strategy to evidence.

- [ ] **Step 1: Spike — is Act III's detector redundant given a correct Act I?**

Add a temporary probe (scratch script, not committed) that, for all 23 fixtures in `~/mdtest/Markdown.mdtest/` plus the four Task 1 inputs, runs Acts I–IV with `resolve_short_circuit=False` and records whether any `LYRIC_DEFINITION_*` scene ever removes bytes that would otherwise reach output. Compare rendered output with the Act III definition-detector bypassed (route `LYRIC_DEFINITION_OPEN`'s entry straight to span traversal) versus present.
Decision gate:
- **If output is identical across all 27 inputs with the detector bypassed** → the detector is redundant. Proceed with Step 2a (bypass).
- **Else** → proceed with Step 2b (fix the replay). Record the fixture(s) that differ in the commit message.

- [ ] **Step 2a (if redundant): Bypass the Act III definition-detector**

Route the paragraph-leading `[` case away from `LYRIC_DEFINITION_OPEN` so text flows directly into span traversal (`TRAVERSE_*`). Remove the now-unreachable `LYRIC_DEFINITION_*` scenes and their titles from `src_ir/act3.py` and the Act III literary TOML in the same change (title-budget relief). Keep the change minimal and verified by the Step 3 gate.

- [ ] **Step 2b (if not redundant): Restore the rejected candidate verbatim**

In the `LYRIC_DEFINITION_REPLAY_*` path, emit the buffered candidate glyphs (currently on `ROMEO`) back to the span stream **byte-for-byte**, including the `[`, `]`, and the space run, instead of the current lossy restoration. The replay already buffers the source region; the fix is to replay all buffered bytes without the label/colon normalization. Verify the exact `ROMEO`→stream drain preserves order and count.

- [ ] **Step 3: Regenerate and run the target test**

Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py`
Run: `uv run pytest "tests/test_malformed_reference_definitions.py::test_malformed_reference_definition_renders_literally[space-before-colon]" -q`
Expected: PASS — `"<p>[x] : destination</p>\n"`.

- [ ] **Step 4: Remove the three `xfail` marks (they now XPASS-strict)**

In `tests/test_act3_contracts.py`, delete the `_DEFINITION_REPLAY_UNREACHED` marks from the `missing-destination`, `space-only-destination`, and `empty-label` params (and the now-unused `_DEFINITION_REPLAY_UNREACHED` definition if no longer referenced).

Run: `uv run pytest tests/test_act3_contracts.py -q`
Expected: PASS with 0 xfailed (all four `...byte_for_byte` params pass).

- [ ] **Step 5: Verify on the real binary**

Run: `printf '[x] : destination\n' | ./shakedown`
Expected: `<p>[x] : destination</p>`

- [ ] **Step 6: Commit**

```bash
git add src_ir/act3.py tests/test_act3_contracts.py src/*.spl shakedown.spl
# include Act III literary TOML if Step 2a removed scenes
git commit -m "fix: stop Act III corrupting non-definition paragraph text"
```

---

### Task 5: Final integration — full parity, real binary, roadmap

**Files:**
- Modify: `docs/superpowers/plans/plan-roadmap.md` (record this plan shipped)

- [ ] **Step 1: Full regen and full suite**

Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py`
Run: `uv run pytest -q`
Expected: PASS — 0 failed, 0 xfailed among the four target cases and the three `test_act3_contracts` cases.

- [ ] **Step 2: Real-binary oracle parity for all four inputs**

Run, for each of `[not]:`, `[not]:   `, `[]: destination`, `[x] : destination`:
`printf '<input>\n' | ./shakedown` and `printf '<input>\n' | perl ~/markdown/Markdown.pl`
Expected: identical output for every input.

- [ ] **Step 3: Lint and type-check**

Run: `uv run ruff check . && uv run ruff format --check . && uv run pyright`
Expected: clean.

- [ ] **Step 4: Update the roadmap**

Add a row recording this plan shipped (branch `fix/malformed-reference-definitions`), matching the roadmap's existing row format.

- [ ] **Step 5: Commit and open PR**

```bash
git add docs/superpowers/plans/plan-roadmap.md
git commit -m "docs: record malformed-reference-definitions plan shipped"
```
Open a PR from `fix/malformed-reference-definitions` (base: the ampersand PR branch, or `main` after that PR merges — this branch is stacked on it).

---

## Self-Review

**Spec coverage:** Bug 1 → Task 2; Bug 2 → Task 3; Bug 3 (evidence-led) → Task 4 (spike + branch); oracle-parity gate → Task 1; literary reservation → Task 0; regen + real-binary + full parity → Tasks 2–5; xfail seam closed → Task 4 Step 4. All spec sections covered.

**Placeholder scan:** IR op tuples in Tasks 2–3 are given as concrete scene definitions with an explicit note that exact register relays are verified test-first against the interpreter — this is TDD structure for stack-machine work, not a deferred requirement; the guard *semantics* and control-flow targets are exact. Task 4's two branches are fully specified with a decision gate. No "TBD"/"handle edge cases"/"similar to" placeholders.

**Type consistency:** Scene labels are consistent across tasks (`HECATE_REF_LABEL_FIRST`, `HECATE_REF_URL_CONTENT` reserved in Task 0, used in Tasks 2–3). `_render`/`CASES`/test id names are stable across Tasks 1–5. Regen command identical everywhere.
