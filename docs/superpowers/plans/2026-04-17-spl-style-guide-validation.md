# SPL Style Guide Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a focused validation system for the SPL style lexicon and codegen guide so the repo can distinguish mechanically enforceable claims from demonstrable or advisory guidance.

**Architecture:** This implementation has three outputs that should stay loosely coupled: an evidence note in `docs/spl/`, a focused interpreter-backed pytest harness under `tests/`, and minimal guide wording edits only where validation changes the confidence level of an existing claim. The harness should exercise representative rule families, not attempt exhaustive combinatorics.

**Tech Stack:** Markdown documentation, pytest, subprocess-based execution of the local `shakespearelang` interpreter, existing SPL probe patterns in `docs/spl/probes/`

---

## File Structure

- Create: `docs/spl/style-guide-validation.md`
  - Evidence ledger for claim classification, probe results, and advisory-versus-enforceable outcomes.
- Create: `tests/test_spl_style_guide_validation.py`
  - Focused pytest harness for mechanically enforceable claims from the style and codegen guides.
- Create: `tests/fixtures/spl_style_validation/`
  - Small SPL probe files or fixture inputs if inline program generation becomes unwieldy.
- Modify: `docs/spl/style-lexicon.md`
  - Tighten wording only if validation reveals overstated or invalid claims.
- Modify: `docs/spl/codegen-style-guide.md`
  - Tighten wording only if validation reveals overstated or invalid claims.

## Task 1: Map Claims And Prepare Validation Targets

**Files:**
- Create: `docs/spl/style-guide-validation.md`
- Reference: `docs/spl/style-lexicon.md`
- Reference: `docs/spl/codegen-style-guide.md`
- Reference: `docs/spl/reference.md`

- [ ] **Step 1: Re-read the guides and extract the claim families**

Run:

```bash
sed -n '1,320p' docs/spl/style-lexicon.md
sed -n '1,360p' docs/spl/codegen-style-guide.md
sed -n '90,260p' docs/spl/reference.md
```

Expected:
- clear rule families emerge for legality, sign preservation, magnitude preservation, comparisons, and codegen examples
- any obviously advisory wording is visible before harness design starts

- [ ] **Step 2: Draft the validation note with the claim taxonomy**

Create `docs/spl/style-guide-validation.md` with sections shaped like:

```md
# SPL Style Guide Validation

## Scope

This note validates claims from:
- `docs/spl/style-lexicon.md`
- `docs/spl/codegen-style-guide.md`

## Claim Matrix

| Claim family | Source doc | Example claim | Category | Validation method |
| --- | --- | --- | --- | --- |
| Representative phrase legality | style lexicon | `a noble peaceful golden hero` is valid | mechanically enforceable | pytest + `shakespeare run` |
| Same-sign variation | style lexicon | `a cat` to `a fellow` preserves positive sign | mechanically enforceable | numeric-output probe |
| Same-magnitude variation | codegen guide | `a big cat` to `a red fellow` preserves `+2` | mechanically enforceable | numeric-output probe |
| Sentinel consistency example | codegen guide | stable local sentinel wording is demonstrable | demonstrable | evidence note example |
| “clarity outranks flourish” | codegen guide | advisory preference | advisory only | marked non-enforceable |
```

Expected:
- every important guide rule family has a category
- each category names either harness coverage or evidence-note treatment

- [ ] **Step 3: List representative probe targets before writing tests**

Add a “Representative Probe Targets” section to the note with bullets like:

```md
- positive/neutral phrase legality:
  - `a noble peaceful golden hero`
  - `a beautiful rural morning`
- negative phrase legality:
  - `a vile smelly plague`
  - `a fatherless half-witted coward`
- same-sign substitutions:
  - `a cat` vs `a fellow`
  - `a pig` vs `a wolf`
- same-magnitude substitutions:
  - `a big cat` vs `a red fellow`
  - `an old pig` vs `a big pig`
- representative comparisons:
  - `as noble as a golden hero`
  - `friendlier than a gentle pony`
  - `punier than a dirty pig`
- codegen examples:
  - `You are as good as nothing.`
  - `You are as lovely as a cat.`
  - `You are the sum of a cat and a cat.`
  - `Remember nothing.`
```

Expected:
- the note now defines exactly what the first harness pass must cover
- coverage remains representative, not exhaustive

- [ ] **Step 4: Review the note for category leaks and scope creep**

Run:

```bash
sed -n '1,260p' docs/spl/style-guide-validation.md
rg -n "TBD|TODO|FIXME|exhaustive|all combinations|full dramatic tone" docs/spl/style-guide-validation.md
```

Expected:
- no placeholders
- no accidental shift into exhaustive combinatorics or architecture validation

- [ ] **Step 5: Commit the claim-mapping note**

Run:

```bash
git add docs/spl/style-guide-validation.md
git commit -m "docs: map SPL style guide validation claims"
```

Expected:
- one docs-only commit containing the validation evidence scaffold

## Task 2: Add The Runnable Harness For Mechanical Claims

**Files:**
- Create: `tests/test_spl_style_guide_validation.py`
- Create or reuse: `tests/fixtures/spl_style_validation/`

- [ ] **Step 1: Write the first failing harness test for the simplest mechanical claim**

Create `tests/test_spl_style_guide_validation.py` with an initial test structure like:

```python
from pathlib import Path
import subprocess
import tempfile


def _run_spl(program: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        play_path = Path(tmpdir) / "probe.spl"
        play_path.write_text(program)
        return subprocess.run(
            ["shakespeare", "run", str(play_path)],
            input=stdin,
            capture_output=True,
            text=True,
        )


def test_positive_phrase_example_runs_and_emits_expected_value() -> None:
    program = \"\"\"Title.

Romeo, a man.
Juliet, a woman.

                    Act I: Test.

                    Scene I: Test.

[Enter Romeo and Juliet]

Juliet: You are as noble as a noble peaceful golden hero.
Juliet: Open your heart!

[Exeunt]
\"\"\"
    result = _run_spl(program)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "8"
```

Expected:
- first test exists for one representative mechanically enforceable example
- helper shape is established for subsequent probes

- [ ] **Step 2: Run the new test to verify RED**

Run:

```bash
uv run pytest tests/test_spl_style_guide_validation.py::test_positive_phrase_example_runs_and_emits_expected_value -q
```

Expected:
- FAIL for a real reason in the new harness or probe program, not because the test is malformed

- [ ] **Step 3: Expand to the full representative mechanical matrix**

Extend `tests/test_spl_style_guide_validation.py` to cover:

```python
def test_negative_phrase_example_runs_and_emits_expected_value() -> None: ...

def test_same_sign_positive_substitution_preserves_positive_sign() -> None: ...

def test_same_sign_negative_substitution_preserves_negative_sign() -> None: ...

def test_same_magnitude_substitution_preserves_value() -> None: ...

def test_invalid_magnitude_variation_changes_value() -> None: ...

def test_representative_comparison_examples_parse_and_run() -> None: ...

def test_codegen_assignment_examples_match_documented_values() -> None: ...

def test_stack_adjacent_examples_run_without_semantic_contradiction() -> None: ...
```

Use small SPL programs that prove:

- `a cat` and `a fellow` each emit `1`
- `a pig` and `a wolf` each emit `-1`
- `a big cat` and `a red fellow` each emit `2`
- `a cat` and `a big cat` emit different values
- representative comparison forms parse successfully and can be placed in valid conditional contexts
- documented codegen examples from the guide produce the documented values

Expected:
- each rule family from the mechanical matrix has at least one direct regression test

- [ ] **Step 4: Run the new harness module to verify GREEN**

Run:

```bash
uv run pytest tests/test_spl_style_guide_validation.py -q
```

Expected:
- PASS
- failures, if any, reflect actual contradictions between docs and interpreter behavior

- [ ] **Step 5: Commit the runnable harness**

Run:

```bash
git add tests/test_spl_style_guide_validation.py tests/fixtures/spl_style_validation
git commit -m "test: validate SPL style guide mechanics"
```

Expected:
- one test-only commit containing the focused harness

## Task 3: Record Demonstrations And Tighten Guide Wording

**Files:**
- Modify: `docs/spl/style-guide-validation.md`
- Modify: `docs/spl/style-lexicon.md`
- Modify: `docs/spl/codegen-style-guide.md`

- [ ] **Step 1: Add demonstration-only outcomes to the validation note**

Extend the evidence note with sections shaped like:

```md
## Demonstrable Claims

- sentinel consistency:
  demonstrated with a small repeated-control example; technically coherent but not fully enforceable
- palette-by-purpose:
  demonstrated with valid positive, neutral, and negative examples; remains advisory in strength

## Advisory-Only Claims

- `clarity outranks flourish`
- broad ornament/legibility preferences
```

Expected:
- the evidence note now separates harness-backed facts from softer guidance

- [ ] **Step 2: Tighten the guides only where validation requires it**

If validation reveals overstated language, update the guide sentences directly. Expected kinds of edits:

```md
- change “is safest” to “is usually the safest” if the claim is guidance rather than invariant
- change “should” to “prefer” where the repo cannot enforce the statement mechanically
- preserve hard wording only for claims the harness now verifies
```

Expected:
- only minimal wording changes
- no unrelated prose rewrites

- [ ] **Step 3: Re-read the three docs together**

Run:

```bash
sed -n '1,260p' docs/spl/style-guide-validation.md
sed -n '1,260p' docs/spl/style-lexicon.md
sed -n '1,320p' docs/spl/codegen-style-guide.md
```

Expected:
- mechanically enforced claims read confidently
- demonstrable claims read as demonstrations
- advisory claims read as guidance, not hard invariants

- [ ] **Step 4: Commit the evidence-note completion and any wording fixes**

Run:

```bash
git add docs/spl/style-guide-validation.md docs/spl/style-lexicon.md docs/spl/codegen-style-guide.md
git commit -m "docs: record SPL style guide validation results"
```

Expected:
- one docs commit for the completed evidence ledger and any required wording corrections

## Task 4: Final Verification And Handoff

**Files:**
- Verify: `docs/spl/style-guide-validation.md`
- Verify: `docs/spl/style-lexicon.md`
- Verify: `docs/spl/codegen-style-guide.md`
- Verify: `tests/test_spl_style_guide_validation.py`

- [ ] **Step 1: Run the focused validation suite**

Run:

```bash
uv run pytest tests/test_spl_style_guide_validation.py -q
```

Expected:
- PASS

- [ ] **Step 2: Run the full test suite**

Run:

```bash
uv run pytest -q
```

Expected:
- PASS

- [ ] **Step 3: Check final diff and repo state**

Run:

```bash
git status --short
git diff -- docs/spl/style-guide-validation.md docs/spl/style-lexicon.md docs/spl/codegen-style-guide.md tests/test_spl_style_guide_validation.py
```

Expected:
- no unexpected files
- diff limited to the planned doc and test set

- [ ] **Step 4: Summarize the validation outcome for the user**

Prepare a handoff summary that states:

```md
- which style/codegen claims are now mechanically enforced
- which remain demonstrable but not enforced
- which remain advisory only
- any guide wording changed because validation contradicted or softened a claim
```

Expected:
- the final report makes the confidence boundaries explicit

## Self-Review

Spec coverage:
- claim taxonomy is implemented in Task 1
- focused runnable harness is implemented in Task 2
- evidence-note treatment for demonstrable and advisory claims is implemented in Task 3
- doc tightening is included only where validation requires it

Placeholder scan:
- no `TBD`, `TODO`, or unresolved implementation placeholders appear in the plan steps

Type and naming consistency:
- evidence note path is consistently `docs/spl/style-guide-validation.md`
- harness path is consistently `tests/test_spl_style_guide_validation.py`
- guide paths are consistently `docs/spl/style-lexicon.md` and `docs/spl/codegen-style-guide.md`
