# Shakedown Pre-Design Due Diligence Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the remaining Shakedown architecture unknowns into a ranked evidence matrix so the detailed implementation design can start from decisions, not assumptions.

**Architecture:** This is a docs-and-probe pass, not an implementation pass. It gathers the current open questions from the prototype evidence and the living docs, runs targeted oracle/interpreter checks where the answer is still unclear, and records the result in a single synthesis note that feeds the detailed architecture spec.

**Tech Stack:** Markdown docs, `shakespeare` / `Markdown.pl`, `pytest`, `rg`, `sed`, `perl`, `git`

---

## File Structure

- Create: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
  - A live investigation matrix and final synthesis note for the remaining architecture questions.
- Modify: `docs/verification-plan.md`
  - Reclassify any claims whose status changes because of the due-diligence pass.
- Modify: `docs/markdown/fixture-outlook.md`
  - Narrow or refine risk tiers if the investigation closes one of the predicted hard cases.
- Modify: `docs/markdown/divergences.md`
  - Update the accepted-divergence list only if the investigation changes the decision.

## Scope

In scope:

- reference-link strategy
- list exactness, loose/tight behavior, and nested block composition
- setext headings and line-level lookahead
- raw HTML blocks and inline HTML boundaries
- emphasis backtracking policy
- realistic interpreter/build timing on the assembled prototype
- final synthesis into a ranked decision register

Out of scope:

- SPL implementation work
- new runtime code or new probes beyond the targeted checks in this plan
- the detailed architecture spec itself
- the implementation plan for `shakedown.spl`

## Task 1: Build The Open-Questions Register

**Files:**
- Create: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`

- [ ] **Step 1: Re-read the current decision surface and capture the remaining unknowns**

Run:

```bash
sed -n '1,260p' docs/verification-plan.md
sed -n '1,260p' docs/markdown/target.md
sed -n '1,220p' docs/markdown/fixture-outlook.md
sed -n '1,260p' docs/prior-attempt/architecture-lessons.md
sed -n '1,260p' docs/prior-attempt/feasibility-lessons.md
sed -n '1,220p' docs/superpowers/notes/2026-04-18-p1-evidence.md
sed -n '1,220p' docs/superpowers/notes/2026-04-18-p2-evidence.md
sed -n '1,220p' docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md
sed -n '1,260p' docs/superpowers/specs/2026-04-18-shakedown-architecture-outline-design.md
```

Expected:
- the remaining architectural unknowns are visible in one pass
- the open items are clearly separable into "must decide now", "probe now", and "defer to detailed spec"

- [ ] **Step 2: Write the matrix note skeleton**

Create `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md` with this structure:

```md
# Shakedown Pre-Design Due Diligence

## Questions To Close

| Question | Why it matters | Evidence sources | Probe command(s) | Decision threshold | Status |
|---|---|---|---|---|---|
| Reference-link strategy | Reference links are the biggest remaining architectural risk | `docs/markdown/target.md`; `docs/prior-attempt/architecture-lessons.md`; `docs/verification-plan.md` | `uv run pytest tests/test_mdtest.py -k "reference style or shortcut references or inline style" -q` | the selected strategy must explain how labels are resolved without a hand-wavy global lookup | open |
| Lists and nesting | Tight/loose exactness and nested composition can break the block pipeline | `docs/markdown/fixture-outlook.md`; `docs/prior-attempt/feasibility-lessons.md` | `uv run pytest tests/test_mdtest.py -k "Ordered and unordered lists or Nested blockquotes or Blockquotes with code blocks or Markdown Documentation - Syntax" -q` | the design must state whether exact loose-list behavior is required or a documented divergence | open |
| Setext lookahead | Setext headings require line-level buffering instead of single-line peeking | `docs/markdown/target.md`; `docs/markdown/fixture-outlook.md` | `uv run pytest tests/test_mdtest.py -k "Setext Headers or Markdown Documentation - Syntax" -q` | the design must say where line lookahead lives and how far it reaches | open |
| HTML boundaries | Raw HTML blocks and inline HTML can bypass or confuse the normal parser | `docs/markdown/target.md` | `uv run pytest tests/test_mdtest.py -k "HTML Blocks or Inline HTML or Inline HTML comments" -q` | the design must distinguish raw HTML passthrough from inline HTML token handling | open |
| Emphasis backtracking | Markdown.pl overlap semantics may require a deliberate divergence decision | `docs/superpowers/notes/2026-04-18-p2-evidence.md`; `docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md`; `docs/markdown/divergences.md` | `uv run pytest tests/test_mdtest.py -k "Strong and em together or Markdown Documentation - Syntax" -q` | the design must pick either exact overlap reproduction or an explicit divergence | open |
| Timing budget | The loop only matters if the assembled SPL stays workable on this machine | `docs/superpowers/notes/2026-04-18-p1-evidence.md`; `docs/superpowers/notes/2026-04-18-p2-evidence.md` | `time ./shakedown-dev < /dev/null`; `time ./shakedown-dev < tests/prototype/fixtures/p2_blockquote_input.md` | the measured runtime must be low enough for a fixture-by-fixture loop | open |

## Evidence Notes
Record each probe result as a short paragraph: what command ran, what output mattered, and what the result implies for the architecture.

## Decisions Carried Forward
Write one declarative bullet per final decision. Each bullet should name the chosen strategy and the reason it survives the alternatives.
```

Expected:
- the note is ready to record concrete evidence
- the decision register has one row per unresolved risk area

- [ ] **Step 3: Review the matrix for scope drift**

Run:

```bash
sed -n '1,220p' docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
rg -n "TBD|TODO|FIXME|maybe|probably|likely" docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
```

Expected:
- no placeholders
- no silent commitment to implementation details

- [ ] **Step 4: Commit the register**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
git commit -m "docs: add Shakedown pre-design due diligence register"
```

Expected:
- a docs-only commit with the matrix note scaffold

## Task 2: Resolve Reference-Link And Reference-Style Link Strategy

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Reference: `tests/test_mdtest.py`
- Reference: `docs/markdown/target.md`

- [ ] **Step 1: Run the target fixtures that exercise cross-reference lookup**

Run:

```bash
uv run pytest tests/test_mdtest.py -k "reference style or shortcut references or inline style" -q
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Links, reference style.text" > /tmp/links-reference-oracle.xhtml
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Links, shortcut references.text" > /tmp/links-shortcut-oracle.xhtml
```

Expected:
- the mdtest subset runs cleanly against the current binary contract
- the oracle outputs are available for direct comparison

- [ ] **Step 2: Record the lookup strategy decision**

Add to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`:

```md
## Reference-Link Decision

Write one declarative sentence that names the chosen lookup strategy, explains why it fits SPL, and says whether it changes phase count or cast pressure.
```

Expected:
- the note captures whether reference links require a new phase, a linear scan, or a separate lookup pass

- [ ] **Step 3: Commit the strategy note update**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
git commit -m "docs: record Shakedown reference-link strategy"
```

Expected:
- the reference-link choice is captured in the investigation note

## Task 3: Resolve Lists, Tight/Loose Behavior, And Nested Block Composition

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Reference: `tests/test_mdtest.py`
- Reference: `docs/markdown/fixture-outlook.md`
- Reference: `docs/prior-attempt/feasibility-lessons.md`

- [ ] **Step 1: Run the list and nested-block fixtures that represent the hard case**

Run:

```bash
uv run pytest tests/test_mdtest.py -k "Ordered and unordered lists or Nested blockquotes or Blockquotes with code blocks or Markdown Documentation - Syntax" -q
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Ordered and unordered lists.text" > /tmp/lists-oracle.xhtml
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Nested blockquotes.text" > /tmp/nested-blockquotes-oracle.xhtml
```

Expected:
- the fixtures identify whether the current implementation shape can tolerate nested block composition
- the oracle outputs make the tight/loose and nesting pressure visible

- [ ] **Step 2: Record the list architecture choice**

Add to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`:

```md
## Lists And Nested Blocks Decision

Write one declarative paragraph that states the list policy, the nesting policy, and whether a dedicated list-state carrier is required.
```

Expected:
- the note separates list exactness from nesting mechanics instead of blending them together

- [ ] **Step 3: Update risk tiers if evidence changes them**

If the investigation narrows or widens the list risk, update `docs/markdown/fixture-outlook.md` to match the result.

Expected:
- the risk outlook remains predictive rather than stale

- [ ] **Step 4: Commit the list decision**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md docs/markdown/fixture-outlook.md
git commit -m "docs: record Shakedown list and nested-block findings"
```

Expected:
- the list and nesting decision is recorded once, in one place

## Task 4: Resolve Setext Headings, HTML Blocks, And Inline HTML Boundaries

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Reference: `tests/test_mdtest.py`
- Reference: `docs/markdown/target.md`

- [ ] **Step 1: Run the fixtures that stress line-level lookahead and HTML pass-through**

Run:

```bash
uv run pytest tests/test_mdtest.py -k "Setext Headers or HTML Blocks or Inline HTML or Markdown Documentation - Syntax" -q
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Setext Headers.text" > /tmp/setext-oracle.xhtml
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"HTML Blocks.text" > /tmp/html-blocks-oracle.xhtml
```

Expected:
- the line-level lookahead requirement is visible
- raw HTML boundaries are exercised against the oracle

- [ ] **Step 2: Record the boundary rules**

Add to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`:

```md
## Lookahead And HTML Boundary Decision

Write one declarative paragraph that states the setext lookahead rule and the HTML boundary rule, then names the phase boundary if one is needed.
```

Expected:
- the note distinguishes block-level line lookahead from inline HTML passthrough

- [ ] **Step 3: Commit the lookahead and boundary findings**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
git commit -m "docs: record Shakedown lookahead and HTML boundary findings"
```

Expected:
- the lookahead and HTML decisions are captured for the detailed spec

## Task 5: Resolve Emphasis Backtracking And Final Divergence Policy

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Reference: `docs/superpowers/notes/2026-04-18-p2-evidence.md`
- Reference: `docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md`
- Reference: `docs/markdown/divergences.md`
- Reference: `tests/test_mdtest.py`

- [ ] **Step 1: Re-read the current prototype evidence and the divergence note**

Run:

```bash
sed -n '1,220p' docs/superpowers/notes/2026-04-18-p2-evidence.md
sed -n '1,260p' docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md
sed -n '1,220p' docs/markdown/divergences.md
uv run pytest tests/test_mdtest.py -k "Strong and em together or Markdown Documentation - Syntax" -q
```

Expected:
- the backtracking question is framed as a policy decision, not a fuzzy implementation preference
- the current divergence list is visible alongside the prototype evidence

- [ ] **Step 2: Record the backtracking decision explicitly**

Add to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`:

```md
## Emphasis Backtracking Decision

Write one declarative paragraph that picks exact backtracking reproduction or a documented divergence, and explains the architectural consequence.
```

Expected:
- the note states the decision in a single sentence the detailed spec can quote

- [ ] **Step 3: Update the divergence doc only if the decision changes it**

If the investigation flips the choice, update `docs/markdown/divergences.md` so the divergence list matches the final policy.

Expected:
- the divergence doc stays aligned with the actual architecture decision

- [ ] **Step 4: Commit the backtracking decision**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md docs/markdown/divergences.md
git commit -m "docs: record Shakedown emphasis backtracking decision"
```

Expected:
- the decision is recorded once and only once

## Task 6: Re-Measure The Prototype On A Realistic Workload

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Reference: `shakedown-dev`
- Reference: `tests/prototype/`

- [ ] **Step 1: Measure the assembled prototype on empty input and a representative fixture**

Run:

```bash
time ./shakedown-dev < /dev/null
time ./shakedown-dev < tests/prototype/fixtures/p1_input.md
time ./shakedown-dev < tests/prototype/fixtures/p2_blockquote_input.md
```

Expected:
- the measurement distinguishes startup cost from per-fixture cost
- the result is strong enough to say whether the eventual loop has a workable feedback cadence

- [ ] **Step 2: Re-run the prototype test subset as a sanity check**

Run:

```bash
uv run pytest tests/prototype -q
```

Expected:
- the prototype evidence remains stable after the repo merge

- [ ] **Step 3: Record the performance budget**

Add to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`:

```md
## Timing And Loop Viability

Write one declarative paragraph that records the empty-input runtime, the representative-fixture runtime, and the resulting loop viability judgment.
```

Expected:
- the note states whether the feedback loop is workable without hand-waving

- [ ] **Step 4: Commit the performance findings**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
git commit -m "docs: record Shakedown prototype timing findings"
```

Expected:
- the due-diligence note captures the timing baseline for the design session

## Task 7: Synthesize The Findings Into Detailed-Design Inputs

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Modify: `docs/verification-plan.md`
- Modify: `docs/markdown/fixture-outlook.md`
- Modify: `docs/markdown/divergences.md`

- [ ] **Step 1: Convert the evidence matrix into a ranked decision register**

Add a final section to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`:

```md
## Detailed-Design Inputs

1. decisions that must be fixed before architecture drafting
2. decisions that can stay open until the detailed spec
3. claims that should move buckets in docs/verification-plan.md
4. fixture risks that should be reprioritized in docs/markdown/fixture-outlook.md
5. divergences that must be documented now in docs/markdown/divergences.md
```

Expected:
- the note ends with a concrete handoff, not a loose summary

- [ ] **Step 2: Update the claim inventory if any claim changes status**

If the investigation confirms, narrows, or invalidates a claim bucket in `docs/verification-plan.md`, update the table and keep the bucket labels honest.

Expected:
- the verification-plan file still tells the truth about what is verified, retrospective, predicted, and open

- [ ] **Step 3: Commit the final synthesis**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md docs/verification-plan.md docs/markdown/fixture-outlook.md docs/markdown/divergences.md
git commit -m "docs: synthesize Shakedown pre-design due diligence"
```

Expected:
- one final docs commit that hands the detailed architecture spec a closed question set

## Exit Criteria

This plan is done when:

- the due-diligence note exists and contains a question-by-question register
- the remaining open questions are classified as fixed, probed, or deferred
- the verification-plan, fixture outlook, and divergences docs are only changed where the evidence supports the change
- the next step can be a detailed Shakedown architecture spec without reopening the same evidence search
