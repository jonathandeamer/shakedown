# SPL Reference Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the high-risk inferred SPL semantics against the local Python `shakespearelang` interpreter and fold the results into the canonical Shakedown SPL reference.

**Architecture:** Treat `docs/research/shakedown-spl-reference.md` as the canonical reader-facing document and add a compact supporting verification note for raw probe evidence. Use minimal SPL probe programs and direct `shakespeare run` executions to confirm or correct only the interpreter behaviors that materially affect Shakedown planning and implementation.

**Tech Stack:** Markdown docs, local `shakespearelang` Python interpreter, shell commands, git

---

### Task 1: Inventory And Classify Existing Claims

**Files:**
- Modify: `docs/research/shakedown-spl-reference.md`
- Reference: `docs/research/shakedown-spl-feasibility-assumption-corrections.md`
- Reference: `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf`

- [ ] **Step 1: Read the current reference and capture the project-relevant claims**

Run: `nl -ba docs/research/shakedown-spl-reference.md | sed -n '1,340p'`
Expected: the current reference sections with line numbers for program structure, pronouns, operations, stage directions, control flow, constraints, and CLI notes.

- [ ] **Step 2: Read the correction note and grammar sections that affect disputed claims**

Run: `nl -ba docs/research/shakedown-spl-feasibility-assumption-corrections.md | sed -n '1,220p'`
Expected: the correction note text, especially the stage-capacity and finite-character-name corrections.

Run: `rg -n "first_person|second_person|character =|Enter|Exit|Exeunt|proceed|return|question|speak your mind|open your mind|listen to your heart|remember|recall" /home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf`
Expected: grammar hits for pronouns, character names, stage directions, goto/control phrases, and other probe-relevant productions.

- [ ] **Step 3: Classify claims into verification buckets in working notes**

Use this working checklist while reviewing the docs:

```text
grammar-confirmed:
- valid character names come from the installed grammar
- the interpreter grammar accepts multi-character Enter/Exeunt forms

runtime-verify:
- second-person ambiguity behavior with 1, 2, and 3 characters on stage
- global boolean overwrite behavior
- act-local goto restriction at runtime
- stdin/output edge cases
- runtime errors for bad stage operations and empty-stack recall

corrected-project-assumption:
- "exactly 2 characters on stage" is a pronoun rule, not a universal stage-capacity rule
```

- [ ] **Step 4: Confirm the inventory is complete before probe authoring**

Run: `rg -n "Exactly 2 characters on stage|EOF returns|Speak your mind|Listen to your heart|Gotos can only jump within the current act|One global boolean" docs/research/shakedown-spl-reference.md`
Expected: the high-risk claims appear in the current reference and are therefore in scope for verification or correction.

- [ ] **Step 5: Commit the claim inventory checkpoint**

```bash
git status --short
git add docs/superpowers/plans/2026-04-17-spl-reference-verification.md
git commit -m "docs: add SPL reference verification plan"
```

Expected: a clean commit containing the implementation plan only.

### Task 2: Build Probe Programs For Runtime Verification

**Files:**
- Create: `docs/research/tmp-spl-probes/pronoun-stage-rules.spl`
- Create: `docs/research/tmp-spl-probes/global-boolean-overwrite.spl`
- Create: `docs/research/tmp-spl-probes/goto-across-acts.spl`
- Create: `docs/research/tmp-spl-probes/io-edge-cases.spl`
- Create: `docs/research/tmp-spl-probes/runtime-errors.spl`

- [ ] **Step 1: Create the probe directory**

Run: `mkdir -p docs/research/tmp-spl-probes`
Expected: the temporary probe directory exists.

- [ ] **Step 2: Write the pronoun and stage-capacity probe**

Create `docs/research/tmp-spl-probes/pronoun-stage-rules.spl` with a minimal play that:

```spl
Pronoun Stage Rules.

Romeo, a test character.
Juliet, another test character.
Hamlet, a third test character.

                    Act I: Pronouns.

                    Scene I: Two characters.

[Enter Romeo and Juliet]
Romeo: You are as good as a cat.
Juliet: Open your heart!
[Exit Juliet]

                    Scene II: One character.

Romeo: I am as good as a cat.
[Enter Juliet and Hamlet]

                    Scene III: Three characters.

Romeo: You are as good as a cat.
```

Expected: the two-character second-person use succeeds, first-person use with one on-stage character succeeds, and the three-character second-person use produces a runtime failure or ambiguity error.

- [ ] **Step 3: Write the global boolean overwrite probe**

Create `docs/research/tmp-spl-probes/global-boolean-overwrite.spl` with a minimal play that:

```spl
Boolean Overwrite.

Romeo, a test character.
Juliet, another test character.

                    Act I: Questions.

                    Scene I: Overwrite.

[Enter Romeo and Juliet]
Romeo: You are as good as a cat.
Juliet: Are you as good as a cat?
Juliet: Are you better than a cat?
Romeo: If so, open your heart!
Romeo: If not, speak your mind!
```

Expected: only the second question controls the conditional outcome, proving the boolean is global and overwritten by the most recent question.

- [ ] **Step 4: Write the act-boundary goto probe**

Create `docs/research/tmp-spl-probes/goto-across-acts.spl` with a minimal play that:

```spl
Goto Across Acts.

Romeo, a test character.
Juliet, another test character.

                    Act I: First act.

                    Scene I: Illegal jump.

[Enter Romeo and Juliet]
Romeo: Let us proceed to scene I.
Romeo: Let us proceed to scene II.

                    Act II: Second act.

                    Scene I: Destination.
Juliet: Open your heart!
```

Then adjust the play if needed so one branch attempts to jump from Act I to an Act II scene.
Expected: the interpreter rejects or fails the cross-act jump rather than treating acts as callable phases.

- [ ] **Step 5: Write the I/O and runtime-error probe files**

Create `docs/research/tmp-spl-probes/io-edge-cases.spl` and `docs/research/tmp-spl-probes/runtime-errors.spl` with probes that cover:

```text
io-edge-cases.spl:
- Open your mind! at EOF
- Listen to your heart! with simple integer input and EOF/no-token input
- Speak your mind! with negative or out-of-range values

runtime-errors.spl:
- Recall from an empty stack
- Exit or Exeunt for characters not on stage
- Enter a character already on stage
```

Expected: each file isolates one category of runtime behavior so command output can be attributed cleanly in the verification note.

- [ ] **Step 6: Commit the probe definitions**

```bash
git status --short
git add docs/research/tmp-spl-probes
git commit -m "docs: add SPL interpreter verification probes"
```

Expected: the repo contains only the probe programs added in this task.

### Task 3: Run Probes And Record Evidence

**Files:**
- Create: `docs/research/2026-04-17-spl-reference-verification.md`
- Reference: `docs/research/tmp-spl-probes/pronoun-stage-rules.spl`
- Reference: `docs/research/tmp-spl-probes/global-boolean-overwrite.spl`
- Reference: `docs/research/tmp-spl-probes/goto-across-acts.spl`
- Reference: `docs/research/tmp-spl-probes/io-edge-cases.spl`
- Reference: `docs/research/tmp-spl-probes/runtime-errors.spl`

- [ ] **Step 1: Run the pronoun/stage probe and capture the actual interpreter behavior**

Run: `shakespeare run docs/research/tmp-spl-probes/pronoun-stage-rules.spl`
Expected: successful output for the valid cases and a runtime error for the ambiguous three-character second-person case.

- [ ] **Step 2: Run the global boolean probe**

Run: `shakespeare run docs/research/tmp-spl-probes/global-boolean-overwrite.spl`
Expected: output consistent only with the second question's truth value.

- [ ] **Step 3: Run the act-boundary goto probe**

Run: `shakespeare run docs/research/tmp-spl-probes/goto-across-acts.spl`
Expected: an interpreter rejection or runtime failure for the cross-act jump.

- [ ] **Step 4: Run the I/O probes with explicit stdin cases**

Run: `shakespeare run docs/research/tmp-spl-probes/io-edge-cases.spl < /dev/null`
Expected: deterministic EOF behavior for `Open your mind!` and documented failure or sentinel behavior for `Listen to your heart!`.

Run: `printf '42\n' | shakespeare run docs/research/tmp-spl-probes/io-edge-cases.spl`
Expected: integer token parsing behavior is visible in the output.

- [ ] **Step 5: Run the runtime-error probe**

Run: `shakespeare run docs/research/tmp-spl-probes/runtime-errors.spl`
Expected: a specific runtime error for the first intentionally invalid operation reached by the program.

- [ ] **Step 6: Write the supporting verification note with claim-by-claim dispositions**

Create `docs/research/2026-04-17-spl-reference-verification.md` with this structure:

```md
# SPL Reference Verification

## Scope
- local Python `shakespearelang` interpreter only

## Results Table
| Claim | Prior status | Evidence | Result | Notes |

## Probe Details
### Pronoun and stage rules
- Program:
- Command:
- Observed result:
- Disposition:

### Global boolean overwrite
...

## Remaining uncertainties
- none, or a short explicit list
```

- [ ] **Step 7: Commit the verification evidence**

```bash
git status --short
git add docs/research/2026-04-17-spl-reference-verification.md docs/research/tmp-spl-probes
git commit -m "docs: record SPL interpreter verification results"
```

Expected: the verification note and probe artifacts are committed together.

### Task 4: Rewrite The Canonical Reference

**Files:**
- Modify: `docs/research/shakedown-spl-reference.md`
- Modify: `docs/research/shakedown-spl-feasibility-assumption-corrections.md`
- Reference: `docs/research/2026-04-17-spl-reference-verification.md`

- [ ] **Step 1: Add a provenance framing section near the top of the reference**

Update `docs/research/shakedown-spl-reference.md` so the introduction states:

```md
This reference targets the local Python `shakespearelang` interpreter used by Shakedown.
Claims in this document are identified as grammar-confirmed, empirically confirmed, or
corrected project assumptions where that distinction changes planning decisions.
```

- [ ] **Step 2: Correct the stage-capacity wording in the pronouns and constraints sections**

Replace the current universal wording with text equivalent to:

```md
Second-person pronouns require exactly one other on-stage character.
This is a pronoun-resolution rule, not a language-level limit of two characters on stage.
Multi-character stage directions are grammar-confirmed.
```

- [ ] **Step 3: Add concise evidence notes to the high-risk sections**

Update the control-flow and I/O sections so they explicitly mark:

```md
- global boolean overwrite behavior as empirically confirmed
- act-local goto restriction as grammar-confirmed and runtime-confirmed
- EOF and integer-input behavior according to probe results
- any `Speak your mind!` edge-case findings that matter for HTML emission
```

- [ ] **Step 4: Link the supporting verification note from the main reference**

Add a short pointer such as:

```md
For probe programs and observed interpreter output, see
`docs/research/2026-04-17-spl-reference-verification.md`.
```

- [ ] **Step 5: Trim or update the correction note if it becomes redundant**

If `docs/research/shakedown-spl-feasibility-assumption-corrections.md` still adds unique
planning value, keep it and update only stale path or wording references. If its main
correction is now directly captured in the canonical reference, reduce it to a short note
that points readers at the updated reference instead of duplicating semantics.

- [ ] **Step 6: Review the edited docs for coherence**

Run: `sed -n '1,340p' docs/research/shakedown-spl-reference.md`
Expected: the reference reads as a practical language guide, not a transcript of experiments.

Run: `sed -n '1,220p' docs/research/2026-04-17-spl-reference-verification.md`
Expected: the verification note contains enough detail to rerun the probes.

- [ ] **Step 7: Commit the reference rewrite**

```bash
git status --short
git add docs/research/shakedown-spl-reference.md docs/research/shakedown-spl-feasibility-assumption-corrections.md docs/research/2026-04-17-spl-reference-verification.md
git commit -m "docs: verify and tighten SPL reference claims"
```

Expected: the canonical reference, supporting note, and any correction-note cleanup are committed together.

### Task 5: Final Verification And Cleanup

**Files:**
- Reference: `docs/research/shakedown-spl-reference.md`
- Reference: `docs/research/2026-04-17-spl-reference-verification.md`
- Reference: `docs/research/tmp-spl-probes/`

- [ ] **Step 1: Verify there are no unresolved placeholders in the new docs**

Run: `rg -n "TBD|TODO|Unverified|placeholder|later" docs/research/shakedown-spl-reference.md docs/research/2026-04-17-spl-reference-verification.md docs/research/shakedown-spl-feasibility-assumption-corrections.md`
Expected: no stray placeholders remain, unless a claim is intentionally marked unresolved with an explicit explanation.

- [ ] **Step 2: Check whether probe artifacts should remain in the repo**

Run: `ls docs/research/tmp-spl-probes`
Expected: a small set of probe files exists.

Decision rule:
- if the probes are useful as durable reproducibility artifacts, keep them
- if they are noisy and fully captured in the verification note, remove them before the final commit

- [ ] **Step 3: Review the final diff**

Run: `git diff -- docs/research/shakedown-spl-reference.md docs/research/2026-04-17-spl-reference-verification.md docs/research/shakedown-spl-feasibility-assumption-corrections.md docs/research/tmp-spl-probes`
Expected: the diff is documentation-focused and matches the approved design scope.

- [ ] **Step 4: Produce the final status summary**

The closeout should state:

```text
- which claims were confirmed
- which claims were corrected
- whether any claim remains unresolved
- where the canonical reference and supporting evidence now live
```

- [ ] **Step 5: Commit final cleanup if needed**

```bash
git status --short
git commit -m "docs: clean up SPL verification artifacts"
```

Expected: only needed if Task 5 changed tracked files after the main reference rewrite commit.
