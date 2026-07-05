# Shakedown Pre-Design Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the oracle-stub evidence mistake, run three targeted SPL micro-prototypes for the remaining implementation risks, and produce a final pre-design risk register that the detailed architecture spec can trust.

**Architecture:** This is a pre-design hardening pass. It does not build production Markdown support. It separates oracle-stub evidence from SPL evidence, adds an explicit dev-path validation gate, runs isolated micro-prototypes for reference lookup, setext buffering, and list/nesting state, then reconciles the findings into the repo truth docs.

**Tech Stack:** Markdown docs, Python test harnesses, pytest, `shakespeare` / SPL probe programs, `Markdown.pl`, `rg`, `sed`, `time`, `git`

---

## File Structure

- Create: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`
  - Final risk-closure note for the oracle-stub correction and three micro-prototypes.
- Create: `docs/spl/probes/pre-design/reference-lookup.spl`
  - Standalone SPL probe for stack-backed reference lookup and restoration.
- Create: `docs/spl/probes/pre-design/setext-buffering.spl`
  - Standalone SPL probe for delayed line commitment.
- Create: `docs/spl/probes/pre-design/list-state-stack.spl`
  - Standalone SPL probe for nested list looseness/state push-pop.
- Create: `tests/test_pre_design_probes.py`
  - Python tests that execute the three standalone SPL probes and assert exact stdout.
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
  - Correct any statements that treat `./shakedown` oracle-stub success as SPL implementation evidence.
- Modify: `docs/verification-plan.md`
  - Reclassify the 23/23 mdtest pass as oracle-stub contract evidence, not SPL implementation evidence.
- Modify: `docs/markdown/fixture-outlook.md`
  - Restore risk tiers that were lowered solely because `./shakedown` delegates to Markdown.pl.
- Modify: `docs/markdown/divergences.md`
  - Update only if the micro-prototypes change an accepted divergence decision.

## Scope

In scope:

- correcting the evidence classification for `./shakedown` versus `./shakedown-dev`
- adding direct tests for standalone SPL probes
- proving or rejecting the mechanics needed for reference lookup, setext buffering, and list/nesting state
- recording exact commands, outputs, implications, and design decisions
- updating truth docs only where the new evidence supports the change

Out of scope:

- replacing the oracle-backed `./shakedown` stub
- making full mdtest run through `./shakedown-dev`
- production reference-link, setext, or list implementation
- writing the detailed architecture spec
- writing the run-loop prompt

## Task 1: Correct The Oracle-Stub Evidence Classification

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Modify: `docs/verification-plan.md`
- Modify: `docs/markdown/fixture-outlook.md`
- Reference: `shakedown`
- Reference: `shakedown-dev`
- Reference: `tests/test_mdtest.py`

- [ ] **Step 1: Verify the two entry points**

Run:

```bash
sed -n '1,120p' shakedown
sed -n '1,160p' shakedown-dev
sed -n '1,120p' tests/test_mdtest.py
```

Expected:

- `./shakedown` delegates to `~/markdown/Markdown.pl`
- `./shakedown-dev` rebuilds `shakedown.spl` and runs `shakespeare`
- `tests/test_mdtest.py` invokes `./shakedown`, not `./shakedown-dev`

- [ ] **Step 2: Patch the due-diligence note**

Update `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md` so it states:

```md
The `uv run pytest tests/test_mdtest.py -q` result validates the current `./shakedown` oracle-stub contract. It does not prove the SPL prototype handles the full mdtest corpus, because `./shakedown` currently execs `~/markdown/Markdown.pl`. SPL evidence comes from `./shakedown-dev`, `tests/prototype`, and the standalone probes listed below.
```

Expected:

- no sentence claims that the current SPL binary passes all 23 mdtest fixtures
- reference links, lists, setext, and HTML are described as corpus-green through the oracle stub but still requiring SPL design confidence

- [ ] **Step 3: Patch the verification plan**

Update `docs/verification-plan.md` section `B9` so its title and disposition say:

```md
### B9 — Current oracle-stub mdtest contract pass

- **Command:** `uv run pytest tests/test_mdtest.py -q`
- **Observed:**
  ```
  23 passed in 1.44s
  ```
- **Disposition:** Confirmed only for the current `./shakedown` oracle stub. This proves the repo contract and fixture wiring, not SPL implementation coverage. Do not cite this as evidence that `./shakedown-dev` or `shakedown.spl` handles the full mdtest corpus.
```

Expected:

- bucket B keeps the useful contract check
- bucket D keeps SPL implementation risks open where they are not proved by `./shakedown-dev`

- [ ] **Step 4: Restore fixture outlook risk tiers lowered only by oracle-stub evidence**

Update `docs/markdown/fixture-outlook.md` so these tiers reflect SPL implementation risk, not oracle-stub pass status:

```md
| Emphasis | Medium | Markdown.pl backtracking | Simple emphasis is proven in `./shakedown-dev`; exact overlap remains a design choice. |
| Strong Emphasis | Medium | Same as Emphasis | The prototype does not yet prove full Markdown.pl strong/em overlap parity. |
| Reference Links | Medium | SPL lookup mechanics | The oracle-stub corpus is green; SPL still needs a reference lookup strategy. |
| Reference Images | Medium | Same as Reference Links | Inherits the reference-link lookup risk. |
| Ordered Lists | Medium | Loose-list exactness | The oracle-stub corpus is green; SPL still needs an explicit looseness/nesting strategy. |
| Unordered Lists | Medium | Loose-list exactness | Same risk class as Ordered Lists. |
| Nested Lists | Medium-High | Loose-list x nesting | SPL still needs evidence for nested list state handling. |
| Nested Block Structures | High | Exact nested output | Simple blockquote is proven in `./shakedown-dev`; full nested block composition is not. |
| Markdown Documentation - Syntax | High | Combined ceiling risks | The largest fixture is oracle-stub green but not SPL-proven. |
```

Expected:

- the outlook describes residual SPL implementation risk honestly
- oracle-stub success remains documented but does not collapse risk tiers

- [ ] **Step 5: Commit the evidence correction**

Run:

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md docs/verification-plan.md docs/markdown/fixture-outlook.md
git commit -m "docs: correct shakedown oracle-stub evidence classification"
```

Expected:

- the repository no longer overstates SPL implementation evidence

## Task 2: Add A Standalone SPL Probe Harness

**Files:**
- Create: `docs/spl/probes/pre-design/.gitkeep`
- Create: `tests/test_pre_design_probes.py`
- Reference: `docs/spl/probes/`
- Reference: `pyproject.toml`

- [ ] **Step 1: Create the probe directory**

Run:

```bash
mkdir -p docs/spl/probes/pre-design
touch docs/spl/probes/pre-design/.gitkeep
```

Expected:

- `docs/spl/probes/pre-design/` exists as the home for throwaway pre-design SPL probes

- [ ] **Step 2: Add the Python probe test harness**

Create `tests/test_pre_design_probes.py` with:

```python
"""Executable pre-design SPL probes for architecture-risk closure."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = ROOT / "docs" / "spl" / "probes" / "pre-design"


@pytest.mark.parametrize(
    ("probe_name", "expected"),
    [
        ("reference-lookup.spl", "reference lookup: pass\n"),
        ("setext-buffering.spl", "setext buffering: pass\n"),
        ("list-state-stack.spl", "list state stack: pass\n"),
    ],
)
def test_pre_design_spl_probe(probe_name: str, expected: str) -> None:
    probe_path = PROBE_DIR / probe_name
    if not probe_path.exists():
        pytest.xfail(f"{probe_name} not implemented yet")

    result = subprocess.run(
        ["uv", "run", "shakespeare", "run", str(probe_path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )

    assert result.returncode == 0, (
        f"{probe_name} failed with {result.returncode}\nstderr:\n{result.stderr}"
    )
    assert result.stdout == expected
```

Expected:

- the test harness is explicit about probe names and expected output
- missing probes are reported as xfail until each SPL probe file exists

- [ ] **Step 3: Run the new test to verify missing probes are visible**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q
```

Expected:

- `3 xfailed`, one for each missing probe

- [ ] **Step 4: Commit the harness**

Run:

```bash
git add docs/spl/probes/pre-design/.gitkeep tests/test_pre_design_probes.py
git commit -m "test: add pre-design SPL probe harness"
```

Expected:

- a focused test commit establishes the executable gate for the micro-prototypes without breaking the default suite

## Task 3: Run The Reference Lookup Micro-Prototype

**Files:**
- Create: `docs/spl/probes/pre-design/reference-lookup.spl`
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`
- Test: `tests/test_pre_design_probes.py`

- [ ] **Step 1: Write the reference lookup probe**

Create `docs/spl/probes/pre-design/reference-lookup.spl`.

Probe requirement:

- It must be a standalone SPL program.
- It must model the architecture-relevant mechanic, not full Markdown syntax.
- It must push at least two reference records onto a stack-like carrier.
- It must scan for a requested label.
- It must restore or preserve non-matching records well enough to prove lookup is not destructive.
- It must emit exactly `reference lookup: pass\n` when the requested label resolves and the non-matching record is still recoverable.

Implementation guidance:

- Keep the probe intentionally tiny and readable.
- Use literal output as the success signal; do not parse Markdown.
- Prefer one carrier character for reference records and one temporary carrier for scan/restoration.
- If the probe cannot preserve the non-matching record, record that as a design warning instead of weakening the test.

Expected:

- the probe compiles and models the minimum SPL stack behavior needed by a document-scoped reference lookup strategy

- [ ] **Step 2: Run only the reference probe test**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q -k reference
```

Expected:

- PASS with `1 passed, 2 deselected`

- [ ] **Step 2b: Run the complete probe harness**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q
```

Expected:

- `1 passed, 2 xfailed`

- [ ] **Step 3: Record reference lookup evidence**

Create or update `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md` with:

```md
# Shakedown Pre-Design Hardening

## Reference Lookup Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k reference` passed. The standalone SPL probe demonstrates that a document-scoped linear lookup can scan a stack-backed reference table and preserve non-matching records. This supports a no-wrapper strategy for reference links, with the expected trade-off that lookup is linear in the number of definitions.
```

Expected:

- the note states the exact command, result, and architecture implication

- [ ] **Step 4: Commit the reference probe**

Run:

```bash
git add docs/spl/probes/pre-design/reference-lookup.spl docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md
git commit -m "experiment: prove SPL reference lookup mechanics"
```

Expected:

- the reference lookup risk has executable SPL evidence

## Task 4: Run The Setext Buffering Micro-Prototype

**Files:**
- Create: `docs/spl/probes/pre-design/setext-buffering.spl`
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`
- Test: `tests/test_pre_design_probes.py`

- [ ] **Step 1: Write the setext buffering probe**

Create `docs/spl/probes/pre-design/setext-buffering.spl`.

Probe requirement:

- It must be a standalone SPL program.
- It must model delayed line commitment.
- It must hold a candidate text line without emitting it.
- It must inspect a following underline-like line marker.
- It must emit exactly `setext buffering: pass\n` only after the second line decides the first line's block type.

Implementation guidance:

- The probe does not need to parse arbitrary input; hard-code the candidate and underline mechanics if that is enough to prove delayed commitment.
- The important evidence is that SPL can carry pending line state across the lookahead boundary without emitting early.
- If the probe requires a second buffer reversal, record that cost explicitly.

Expected:

- the probe compiles and proves that setext headings can live in Phase 2 line buffering rather than in the inline phase

- [ ] **Step 2: Run only the setext probe test**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q -k setext
```

Expected:

- PASS with `1 passed, 2 deselected`

- [ ] **Step 2b: Run the complete probe harness**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q
```

Expected:

- `2 passed, 1 xfailed`

- [ ] **Step 3: Record setext buffering evidence**

Append to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`:

```md
## Setext Buffering Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k setext` passed. The standalone SPL probe demonstrates that Phase 2 can delay committing a line until the next line is inspected. The detailed architecture spec should place setext recognition in the block phase and account for the buffering/reversal cost.
```

Expected:

- the note states where setext lookahead belongs and what cost it introduces

- [ ] **Step 4: Commit the setext probe**

Run:

```bash
git add docs/spl/probes/pre-design/setext-buffering.spl docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md
git commit -m "experiment: prove SPL setext buffering mechanics"
```

Expected:

- the setext lookahead risk has executable SPL evidence

## Task 5: Run The List State And Nested Composition Micro-Prototype

**Files:**
- Create: `docs/spl/probes/pre-design/list-state-stack.spl`
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`
- Test: `tests/test_pre_design_probes.py`

- [ ] **Step 1: Write the list state stack probe**

Create `docs/spl/probes/pre-design/list-state-stack.spl`.

Probe requirement:

- It must be a standalone SPL program.
- It must model nested list state without parsing full Markdown list syntax.
- It must push two list-frame states onto a dedicated carrier stack.
- It must read the inner frame, then restore or pop back to the outer frame.
- It must distinguish tight and loose frames by value.
- It must emit exactly `list state stack: pass\n` only if the inner and outer frame values are both observed in the correct order.

Implementation guidance:

- Use a dedicated cast member analogous to the proposed `Cordelia` looseness stack.
- Keep output binary: pass string on success, interpreter error or wrong output on failure.
- Record whether the probe needs one carrier per state class or whether one carrier stack is enough.

Expected:

- the probe compiles and proves whether stack-backed list frame state is mechanically viable in SPL

- [ ] **Step 2: Run only the list-state probe test**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q -k list
```

Expected:

- PASS with `1 passed, 2 deselected`

- [ ] **Step 2b: Run the complete probe harness**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q
```

Expected:

- `3 passed`

- [ ] **Step 3: Record list/nesting evidence**

Append to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`:

```md
## List State Stack Micro-Prototype

`uv run pytest tests/test_pre_design_probes.py -q -k list` passed. The standalone SPL probe demonstrates that a dedicated stack-backed carrier can represent nested list frame state and distinguish tight from loose frames. The detailed architecture spec should use an explicit list-state carrier instead of encoding all list state into scalar phase flags.
```

Expected:

- the note states whether the `Cordelia`-style stack is viable and what design shape it supports

- [ ] **Step 4: Commit the list-state probe**

Run:

```bash
git add docs/spl/probes/pre-design/list-state-stack.spl docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md
git commit -m "experiment: prove SPL list state stack mechanics"
```

Expected:

- the list/nesting risk has executable SPL evidence

## Task 6: Reconcile Hardening Evidence Into The Truth Docs

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`
- Modify: `docs/verification-plan.md`
- Modify: `docs/markdown/fixture-outlook.md`
- Modify: `docs/markdown/divergences.md`
- Test: `tests/test_pre_design_probes.py`

- [ ] **Step 1: Run the complete verification set for this hardening pass**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q
uv run pytest tests/prototype -q
uv run pytest tests/test_mdtest.py -q
git diff --check
```

Expected:

- the three pre-design probes pass
- the existing prototype tests still pass with the known xfail
- the oracle-stub mdtest contract still passes
- the diff is whitespace-clean

- [ ] **Step 2: Add a final decision register to the hardening note**

Append to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`:

```md
## Final Pre-Design Decision Register

| Decision | Status | Evidence | Detailed-spec requirement |
|---|---|---|---|
| `./shakedown` mdtest pass is oracle-stub evidence, not SPL evidence | closed | entrypoint inspection plus mdtest target | The spec must not cite oracle-stub success as implementation proof. |
| Reference lookup | closed for mechanics | `reference-lookup.spl` | Use document-scoped linear lookup unless a later implementation proves it too slow. |
| Setext lookahead | closed for mechanics | `setext-buffering.spl` | Keep setext recognition in the block phase with delayed line commitment. |
| List looseness / nesting state | closed for mechanics | `list-state-stack.spl` | Use a dedicated stack-backed list-state carrier. |
| Emphasis backtracking | policy decision remains | `tests/prototype` known xfail plus prior two-pass finding | Detailed spec must choose two-pass parity or documented divergence before implementation planning. |
| Nested blockquote closer quirk | policy decision remains | `docs/markdown/divergences.md` | Detailed spec must choose byte parity or structural validity. |
```

Expected:

- every known pre-design risk is either closed by evidence or explicitly carried into the detailed spec

- [ ] **Step 3: Update the verification plan**

Add a new bucket-B entry to `docs/verification-plan.md`:

```md
### B10 — Pre-design SPL mechanics probes

- **Command:** `uv run pytest tests/test_pre_design_probes.py -q`
- **Observed:** all three standalone SPL probes passed.
- **Disposition:** Confirms the SPL mechanics for stack-backed reference lookup, delayed setext line commitment, and nested list-state push/pop. These probes do not implement full Markdown features; they are architecture evidence for the detailed spec.
```

Expected:

- the verification plan distinguishes mechanics evidence from production feature coverage

- [ ] **Step 4: Update fixture outlook only where the probes reduce risk**

Update `docs/markdown/fixture-outlook.md` so:

- Reference Links remain at most Medium and cite the standalone lookup probe.
- Setext Headers remain Low and cite the delayed-line probe.
- Ordered Lists, Unordered Lists, and Nested Lists cite the list-state-stack probe but stay honest about full syntax not being implemented.
- Markdown Documentation - Syntax remains High until the full SPL implementation, because combined behavior is still not proven.

Expected:

- probe evidence reduces uncertainty without overstating implementation coverage

- [ ] **Step 5: Update divergences only for policy changes**

If the hardening pass chooses a new emphasis or nested-blockquote policy, update `docs/markdown/divergences.md`.

If no policy changes were made, add no divergence entry.

Expected:

- divergence documentation reflects only decisions, not unresolved risks

- [ ] **Step 6: Commit the synthesis**

Run:

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md docs/verification-plan.md docs/markdown/fixture-outlook.md docs/markdown/divergences.md
git commit -m "docs: synthesize shakedown pre-design hardening findings"
```

Expected:

- the hardening evidence is integrated into the repo truth docs

## Task 7: Final Precautionary Review Before Detailed Architecture

**Files:**
- Reference: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`
- Reference: `docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md`
- Reference: `docs/verification-plan.md`
- Reference: `docs/markdown/fixture-outlook.md`
- Reference: `docs/markdown/divergences.md`

- [ ] **Step 1: Scan for placeholders and ambiguous evidence language**

Run:

```bash
rg -n "TBD|TODO|FIXME|maybe|probably|likely|current binary passes|SPL passes all 23|oracle-stub green means" docs/superpowers/notes docs/verification-plan.md docs/markdown/fixture-outlook.md docs/markdown/divergences.md
```

Expected:

- no unresolved placeholders
- no wording that conflates oracle-stub evidence with SPL implementation evidence

- [ ] **Step 2: Run the final pre-design verification set**

Run:

```bash
uv run pytest tests/test_pre_design_probes.py -q
uv run pytest tests/prototype -q
uv run pytest tests/test_mdtest.py -q
uv run ruff check .
uv run pyright
git status --short
```

Expected:

- pre-design probes pass
- prototype tests pass with the known xfail
- mdtest contract passes through the oracle stub
- ruff and pyright pass
- `git status --short` is clean

- [ ] **Step 3: Write the final go/no-go line**

Append to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`:

```md
## Detailed Architecture Go/No-Go

Proceed to detailed architecture only if the spec explicitly carries the two remaining policy decisions: emphasis backtracking and nested blockquote closer behavior. All other pre-design implementation risks have either executable SPL mechanics evidence or are correctly classified as non-SPL oracle-stub evidence.
```

Expected:

- the next session can start the detailed architecture spec without reopening evidence classification

- [ ] **Step 4: Commit the final review note**

Run:

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md
git commit -m "docs: record shakedown detailed-architecture go-no-go"
```

Expected:

- the repository contains a clear gate for starting the detailed architecture spec

## Exit Criteria

This plan is complete when:

- the due-diligence docs no longer overstate oracle-stub evidence as SPL evidence
- the three standalone SPL micro-prototypes pass under `uv run pytest tests/test_pre_design_probes.py -q`
- the verification plan classifies probe evidence as mechanics evidence, not feature coverage
- the fixture outlook reflects reduced uncertainty without pretending production features exist
- emphasis backtracking and nested blockquote closer behavior are the only remaining policy choices before the detailed architecture spec
- the final verification set is clean
