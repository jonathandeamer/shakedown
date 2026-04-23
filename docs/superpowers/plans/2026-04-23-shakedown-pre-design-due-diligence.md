# Shakedown Pre-Design Due Diligence Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the remaining Shakedown architecture unknowns into a ranked evidence register so the detailed implementation design starts from decisions, not assumptions.

**Architecture:** This is a docs-and-probe pass, not an implementation pass. It freezes the current decision surface, runs targeted corpus and timing checks against the current binary and the Markdown.pl oracle, and records the results in a single synthesis note. The note is then reconciled against the repo's truth docs so any status changes are reflected once, in the right place.

**Tech Stack:** Markdown docs, `pytest`, `shakespeare` / `Markdown.pl`, `rg`, `sed`, `perl`, `time`, `git`

---

## File Structure

- Create: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
  - A live investigation matrix, invariant inventory, and final synthesis note for the remaining architecture questions.
- Modify: `docs/verification-plan.md`
  - Reclassify claims if a probe moves anything between verified, retrospective, predicted, or open.
- Modify: `docs/markdown/fixture-outlook.md`
  - Narrow or refine risk tiers only if evidence materially changes the outlook.
- Modify: `docs/markdown/divergences.md`
  - Update the accepted-divergence list only if evidence changes an actual design decision.

## Scope

In scope:

- invariant inventory for the design surface
- failure-mode register for the major architecture risks
- reference-link strategy
- list exactness, loose/tight behavior, and nested block composition
- setext headings and line-level lookahead
- raw HTML blocks and inline HTML boundaries
- emphasis backtracking policy
- interpreter/build timing on the assembled prototype
- final synthesis into a ranked decision register

Out of scope:

- SPL implementation work
- new runtime code
- new probes beyond the targeted checks in this plan
- the detailed architecture spec itself
- the implementation plan for `shakedown.spl`

## Task 1: Freeze The Decision Surface

**Files:**
- Create: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Reference: `docs/verification-plan.md`
- Reference: `docs/markdown/fixture-outlook.md`
- Reference: `docs/markdown/divergences.md`
- Reference: `docs/superpowers/notes/2026-04-18-p1-evidence.md`
- Reference: `docs/superpowers/notes/2026-04-18-p2-evidence.md`
- Reference: `docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md`
- Reference: `docs/superpowers/specs/2026-04-18-shakedown-architecture-outline-design.md`

- [ ] **Step 1: Re-read the current decision surface and capture the remaining unknowns**

Run:

```bash
sed -n '1,260p' docs/verification-plan.md
sed -n '1,260p' docs/markdown/fixture-outlook.md
sed -n '1,220p' docs/markdown/divergences.md
sed -n '1,220p' docs/superpowers/notes/2026-04-18-p1-evidence.md
sed -n '1,240p' docs/superpowers/notes/2026-04-18-p2-evidence.md
sed -n '1,260p' docs/superpowers/notes/2026-04-19-findings-for-detailed-spec.md
sed -n '1,260p' docs/superpowers/specs/2026-04-18-shakedown-architecture-outline-design.md
```

Expected:

- the remaining architectural unknowns are visible in one pass
- the open items are clearly separable into "must decide now", "probe now", and "defer to detailed spec"

- [ ] **Step 2: Write the invariant inventory into the note**

Add a section titled `## Invariant Inventory` to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md` with this table:

```md
| Invariant | Status | Why it matters |
|---|---|---|
| `./shakedown` reads stdin and writes stdout | verified | This is the target interface every later design must preserve. |
| 23 `Markdown.mdtest` fixtures are the corpus boundary | verified | The design should optimize for the real success surface, not a guessed one. |
| One SPL runtime file remains the execution target | verified | The runtime shape constrains phase count, cast pressure, and build tooling. |
| State-carrying characters must have set / consume / reset lifetimes | design rule | This prevents cross-phase leakage like the P2 Mercutio bug. |
| Scene tails must not rely on implicit fall-through | design rule | Explicit control flow is easier to reason about and lint. |
| Marker values must be budgeted before implementation begins | design rule | The phase IR must not evolve ad hoc. |
| Email autolink randomization remains a deliberate divergence | documented divergence | SPL has no randomness primitive. |
| Nested blockquote closer validity is a policy choice | open choice | The detailed design must choose parity or structural validity explicitly. |
```

Expected:

- the note states the design's non-negotiable assumptions in one place
- the table makes explicit which facts are verified versus which are still design choices

- [ ] **Step 3: Write the failure-mode register into the note**

Add a section titled `## Failure-Mode Register` with this table:

```md
| Risk area | Failure mode | Early symptom | Probe that catches it |
|---|---|---|---|
| Reference links | Label lookup becomes a hidden global state problem | The design needs a hash-like runtime cache or an unbounded backtracking scan | `uv run pytest tests/test_mdtest.py -k 'reference' -q` |
| Lists and nesting | Tight / loose list semantics drift from the oracle | Correct list structure but wrong paragraph boundaries | `uv run pytest tests/test_mdtest.py -k 'list or blockquote' -q` |
| Setext headings | Single-line peeking is not enough | A line that later becomes a heading has already been emitted as a paragraph | `uv run pytest tests/test_mdtest.py -k 'setext or html' -q` |
| HTML boundaries | Raw HTML leaks into normal parsing or vice versa | Block HTML gets wrapped as text or inline HTML gets escaped | `uv run pytest tests/test_mdtest.py -k 'setext or html' -q` |
| Emphasis backtracking | Overlapping emphasis cannot be represented cleanly | The prototype stays xfailed on overlapping emphasis | `uv run pytest tests/prototype -q` |
| Build / assembly | `shakedown.spl` drifts from the fragments | The assembled output does not match the source fragments | `git diff --check` and `uv run python scripts/assemble.py` |
| Timing budget | The loop is too slow for fixture-by-fixture iteration | Per-run costs are so high that every change becomes expensive | `time ./shakedown-dev < /dev/null` and a representative fixture run |
```

Expected:

- each major implementation hazard has a concrete failure mode
- each failure mode has a probe, not just a prose warning

- [ ] **Step 4: Commit the register**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
git commit -m "docs: add shakedown pre-design due diligence register"
```

Expected:

- the note exists as a baseline before any probe results are recorded

## Task 2: Probe The Corpus And Oracle

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Reference: `tests/test_mdtest.py`
- Reference: `docs/markdown/target.md`

- [ ] **Step 1: Run the full mdtest suite and the high-risk subsets**

Run:

```bash
uv run pytest tests/test_mdtest.py -q
uv run pytest tests/test_mdtest.py -k 'reference or list or blockquote or setext or html or strong' -q
uv run pytest tests/prototype -q
```

Expected:

- the full corpus stays green
- the high-risk subsets complete cleanly
- the prototype suite still exposes the emphasis-backtracking caveat as an xfail

- [ ] **Step 2: Generate oracle outputs for the highest-risk fixtures**

Run:

```bash
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Links, reference style.text" > /tmp/links-reference-oracle.xhtml
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Ordered and unordered lists.text" > /tmp/lists-oracle.xhtml
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Nested blockquotes.text" > /tmp/nested-blockquotes-oracle.xhtml
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Setext Headers.text" > /tmp/setext-oracle.xhtml
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"HTML Blocks.text" > /tmp/html-blocks-oracle.xhtml
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Strong and em together.text" > /tmp/strong-em-oracle.xhtml
```

Expected:

- the oracle outputs exist for direct comparison
- the remaining design choices are anchored to real fixture behavior instead of memory

- [ ] **Step 3: Record probe outcomes in the note**

Add an `## Evidence Notes` section with one short paragraph per probe family:

```md
- Full corpus run: `uv run pytest tests/test_mdtest.py -q` -> `23 passed in 1.44s`
- Reference / list / blockquote / setext / html / strong subset run: `uv run pytest tests/test_mdtest.py -k 'reference or list or blockquote or setext or html or strong' -q` -> `8 passed, 15 deselected in 0.31s`
- Prototype run: `uv run pytest tests/prototype -q` -> `3 passed, 1 xfailed in 10.07s`
- Oracle generation: the six `/tmp/*.xhtml` files above were produced successfully.
```

Expected:

- the note states what was run, what mattered, and what the result implies

- [ ] **Step 4: Commit the probe results**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
git commit -m "docs: record shakedown pre-design probe results"
```

Expected:

- the evidence note captures the current corpus and oracle state

## Task 3: Verify Toolchain Integrity And Timing Budget

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Reference: `shakedown-dev`
- Reference: `scripts/assemble.py`

- [ ] **Step 1: Refresh the environment and verify the build path**

Run:

```bash
uv sync
git status --short
```

Expected:

- `uv sync` completes without breaking the environment
- `git status --short` does not show unintended source churn from the sync

- [ ] **Step 2: Measure startup and representative fixture cost**

Run:

```bash
time ./shakedown-dev < /dev/null
time ./shakedown-dev < tests/prototype/fixtures/p2_blockquote_input.md
```

Expected:

- the note records the startup cost separately from the representative fixture cost
- the numbers are low enough to support fixture-by-fixture iteration

- [ ] **Step 3: Re-run the full corpus after the environment refresh**

Run:

```bash
uv run pytest tests/test_mdtest.py -q
```

Expected:

- the current binary still passes the full corpus after the refresh

- [ ] **Step 4: Record the timing budget in the note**

Add a `## Timing And Loop Viability` section with one declarative paragraph that states:

- the empty-input runtime
- the representative-fixture runtime
- whether the loop is workable without hand-waving

Expected:

- the plan has a concrete iteration budget, not a vague confidence statement

- [ ] **Step 5: Commit the timing findings**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
git commit -m "docs: record shakedown timing findings"
```

Expected:

- the timing budget is preserved for the detailed design stage

## Task 4: Reconcile The Truth Docs And Finalize The Register

**Files:**
- Modify: `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md`
- Modify: `docs/verification-plan.md`
- Modify: `docs/markdown/fixture-outlook.md`
- Modify: `docs/markdown/divergences.md`

- [ ] **Step 1: Convert the evidence matrix into a ranked decision register**

Add a final section to `docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md` titled `## Detailed-Design Inputs` with this numbered list:

```md
1. decisions that must be fixed before architecture drafting
2. decisions that can stay open until the detailed spec
3. claims that should move buckets in `docs/verification-plan.md`
4. fixture risks that should be reprioritized in `docs/markdown/fixture-outlook.md`
5. divergences that must be documented now in `docs/markdown/divergences.md`
```

Expected:

- the note ends with a concrete handoff, not a loose summary

- [ ] **Step 2: Update the claim inventory if any claim changes status**

If the probe results confirm, narrow, or invalidate a claim bucket in `docs/verification-plan.md`, update the bucket table and keep the labels honest.

Expected:

- the verification-plan file still tells the truth about what is verified, retrospective, predicted, and open

- [ ] **Step 3: Update the risk tiers only where evidence supports it**

If the investigation narrows or widens a fixture risk, update `docs/markdown/fixture-outlook.md` to match the result.

Expected:

- the risk outlook remains predictive rather than stale

- [ ] **Step 4: Update divergences only if the choice actually changed**

If the investigation changes the reference-link, nested-block, or emphasis policy, update `docs/markdown/divergences.md` so the accepted-divergence list matches the final decision.

Expected:

- the divergence doc stays aligned with the actual architecture decision

- [ ] **Step 5: Run a placeholder scan and final diff check**

Run:

```bash
sed -n '1,260p' docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md
rg -n "TBD|TODO|FIXME|maybe|probably|likely" docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md docs/verification-plan.md docs/markdown/fixture-outlook.md docs/markdown/divergences.md
git diff --check
```

Expected:

- no placeholders remain
- no silent implementation commitments leaked into the docs
- the diff is whitespace-clean

- [ ] **Step 6: Commit the synthesis**

```bash
git add docs/superpowers/notes/2026-04-23-shakedown-pre-design-due-diligence.md docs/verification-plan.md docs/markdown/fixture-outlook.md docs/markdown/divergences.md
git commit -m "docs: synthesize shakedown pre-design due diligence"
```

Expected:

- one final docs commit hands the detailed architecture spec a closed, ranked question set

## Exit Criteria

This plan is done when:

- the due-diligence note exists and contains an invariant inventory, failure-mode register, evidence notes, timing budget, and ranked decision register
- the remaining open questions are classified as fixed, probed, deferred, or intentionally divergent
- the verification-plan, fixture outlook, and divergences docs are only changed where evidence supports the change
- the next step can be a detailed Shakedown architecture spec without reopening the same evidence search
