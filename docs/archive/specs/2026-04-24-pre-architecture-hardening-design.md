# Pre-Architecture Hardening — Design

**Date:** 2026-04-24
**Status:** Draft for review
**Author pairing:** interactive Claude session (this spec is one of the documented outputs of the docs/superpowers process)

## Context

A pre-design audit of `docs/` (2026-04-24, via the interactive Claude brainstorming workflow)
identified roughly 14 gaps across three kinds: items that could be *corrected*, items that
needed *clarification*, and items that should be *added or removed* before architecture planning
begins. The audit concluded the docs set is ~90% ready but that four pieces of runtime- and
parity-sensitive evidence are still inference rather than measurement, and that several doc-level
ambiguities exist that will cause churn during the architecture pass if left unresolved.

This spec is the hardening pass that closes those gaps before architecture planning proper.

## Goal

Produce the remaining evidence and doc edits that a fresh architecture-planning session needs in
order to reason from measurement rather than inference, and to engage with inherited prototype
state explicitly rather than inheriting it by default.

The target "done" state is that an architecture-planning session reading `docs/README.md`'s
reading order encounters no unmeasured load-bearing claims, no tacit wrapper/shape assumptions,
and no filesystem state that contradicts the canonical docs.

## Non-goals

- This pass does not produce the architecture itself. Outputs are planning inputs.
- This pass does not write or replace the archived `docs/prompt-shakedown.md` run-loop prompt.
- This pass does not modify `shakedown.spl`, `src/*.spl`, `scripts/assemble.py`, or any
  production code path. Those are architecture decisions.
- This pass does not re-open the Markdown.pl parity target or divergence list.

## Approach — Two stages, one spec

The work splits into an **evidence stage** (run probes, record measurements) and a **fold-back
stage** (update canonical docs to cite the new evidence and resolve latent ambiguities). Stage 2
depends on stage 1 outputs.

The split exists for one reason: several of the doc edits are downstream of probe outcomes.
Writing them first would either commit to hedged language we later revise, or require re-work
once measurements land. Running stage 1 first gives stage 2 real numbers to cite.

A cross-cutting rule: stage 1 touches only probe files, the test harness, measurement scripts,
and append-only measurement records (`verification-plan.md`, pre-design-hardening note). Stage 2
touches canonical markdown / architecture / performance docs. No stage crosses that boundary.

## Stage 1 — Evidence (five probes)

Each probe follows the existing pre-design pattern: `.spl` file under
`docs/spl/probes/pre-design/`, wired into `tests/test_pre_design_probes.py` where applicable,
runtime-wise is `uv run shakespeare run <probe>`. Probes that produce timing rather than
pass/fail assertions use a separate Python harness that reports median + first-run.

### P1 — SPL cost at realistic size

**Purpose.** Anchor the single most load-bearing architecture input: what does `shakespeare run`
actually cost in this repo on a realistically sized SPL file, cold and warm? Today the only two
data points are interpreter startup (~0.1s) and the `./shakedown-dev` prototype (~5s on ~372
lines). The prior attempt's 17–26s cold / 2–3s warm numbers are retrospective; they do not
transfer.

**Artifacts.**

- `scripts/generate_spl_cost_fixtures.py` — deterministic generator. Produces
  `docs/spl/probes/pre-design/spl-cost-1k.spl` (~1000 lines) and `spl-cost-4k.spl` (~4000 lines)
  containing a realistic mix of assignments, arithmetic, stack pushes/pops, and intra-act gotos.
  Not pure boilerplate — the synthesized work should resemble the shape of a plausible Markdown
  port, not an empty-scene stress test.
- `docs/spl/probes/pre-design/spl-cost-1k.spl`, `spl-cost-4k.spl` — checked in, regeneration is
  idempotent.
- `scripts/measure_spl_cost.py` — runs each file 5× cold (fresh subshell / invocation) + 5× warm,
  reports median and first-run timings. Prints a text table suitable for direct paste into
  `verification-plan.md`.

**Recording.** Results land as a new `B14 — Current-repo SPL cost baselines` replay in
`docs/verification-plan.md`. The pre-design-hardening note gets a decision-register row.

**Success criteria.** The harness completes; numbers are recorded; cold and warm timings are
distinguishable from interpreter startup (~0.1s).

### P2 — Emphasis two-pass mechanics probe

**Purpose.** `docs/markdown/divergences.md` upgraded emphasis backtracking from "accepted
divergence" to "parity requirement." The pre-design probes so far cover reference lookup, setext
buffering, and list-state stacking — but not emphasis. Closing this probe demonstrates that SPL
can execute the strong-before-emphasis substitution order on a buffered span.

**Artifacts.**

- `docs/spl/probes/pre-design/emphasis-two-pass.spl` — minimal probe. Given a hardcoded buffered
  input `"*foo **bar** baz*"` stored on a character's stack, run pass 1 (`**` →
  `<strong>`/`</strong>`) then pass 2 (`*` → `<em>`/`</em>`), emit result. Probe closes the
  mechanics question, not the whole feature: emphasis itself remains an architecture decision.

**Wiring.** Parametrized entry in `tests/test_pre_design_probes.py`. Expected stdout:
`emphasis two-pass: pass\n` if the probe's own internal check matches the Markdown.pl-equivalent
target string `<em>foo <strong>bar</strong> baz</em>`.

**Recording.** New `B15 — Emphasis two-pass mechanics` section in verification-plan.md.

**Failure behaviour.** If the probe fails (the mechanic cannot be expressed), stage 2 promotes
emphasis backtracking from its current outlook risk upward and records the failure in the
decision register rather than hiding it.

### P3 — Nested-dispatch mechanics probe

**Purpose.** `fixture-outlook.md` flags "Nested Block Structures" as a High risk, and
`prior-attempt/architecture-lessons.md` records that blockquote reimplementation was ~44% of the
prior attempt's SPL file. Recursive dispatch is the proposed structural fix. Closing this probe
demonstrates that SPL can maintain a nesting stack across frame boundaries.

**Artifacts.**

- `docs/spl/probes/pre-design/nested-dispatch.spl` — minimal probe. Enter outer frame (treat as
  "blockquote"), push sentinel, enter inner frame ("list"), push sentinel, emit content, pop
  inner, pop outer. Assert the emitted sequence matches a synthetic two-level nest trace
  (e.g., `<blockquote><ul><li>x</li></ul></blockquote>` with minimal content, or a token
  equivalent chosen for probe simplicity).

**Wiring.** Parametrized entry in `tests/test_pre_design_probes.py`. Expected stdout:
`nested dispatch: pass\n`.

**Recording.** New `B16 — Nested-dispatch mechanics` section in verification-plan.md.

**Failure behaviour.** If the probe fails, stage 2 documents the failure and leaves the nested
block structure risk tier unchanged or raised.

### P4 — Reference-lookup at fixture scale

**Purpose.** The current reference-lookup probe demonstrates mechanics at small N. The largest
mdtest fixture (`Markdown Documentation - Syntax`) has many reference definitions. Closing this
probe confirms whether linear stack-backed scan remains tractable at fixture scale.

**Artifacts.**

- `scripts/count_reference_defs.py` — counts reference definitions in
  `~/mdtest/Markdown.mdtest/Markdown Documentation - Syntax.text`. Output is used to choose N.
- `docs/spl/probes/pre-design/reference-lookup-scale.spl` — sibling probe to the existing
  `reference-lookup.spl`. Table of N definitions (from the count above); perform a representative
  mix of lookups — half present, half absent — and emit timing or an assertion-style result.
- Harness: reuse `scripts/measure_spl_cost.py` if generic enough, otherwise a small inline
  timer in the probe driver.

**Recording.** New `B17 — Reference lookup at fixture scale` section in verification-plan.md.

### P5 — Scene-count-per-act probe

**Purpose.** The act-local goto rule forces the main SPL loop into one act. The prior attempt
reached ~130 scenes; the current repo has no measured datum for scene-count cost. Closing this
probe shows whether scene count is a significant cost driver or a non-issue at plausible port
sizes.

**Artifacts.**

- `scripts/generate_spl_cost_fixtures.py` may be extended (or a sibling script added) to
  synthesize `docs/spl/probes/pre-design/scene-count.spl` with 200 scenes in one act, each doing
  trivial work and looping via conditional goto.
- `docs/spl/probes/pre-design/scene-count.spl` — checked in; regeneration idempotent.
- Use `measure_spl_cost.py` to time this file vs. a 50-scene baseline and a 5-scene baseline
  (both can be generated or hand-written).

**Recording.** New `B18 — Scene-count-per-act` section in verification-plan.md.

## Stage 2 — Fold-back (three workstreams)

Stage 2 runs after stage 1 completes and touches canonical docs only.

### 2a — Evidence-driven edits (cite stage 1 results)

- **`docs/performance/budget.md`** — "Current Recorded Baselines" updated with P1 numbers. The
  retrospective 17–26s / 2–3s numbers move to a historical-context subsection. The
  `./shakedown-dev` 5s timing moves out of the primary baseline position and into prototype-scale
  context.
- **`docs/verification-plan.md`** — B14–B18 sections appended. Items that probes closed move out
  of bucket D (open) into bucket A-equivalent phrasing referencing the bucket-B evidence.
- **`docs/markdown/fixture-outlook.md`** — emphasis and nested-block risk tiers adjusted on the
  strength of P2/P3. Each change cites the probe ID inline. (Note: this file may be consumed by
  the consolidation workstream — see 2c.)
- **`docs/architecture/runtime-boundary.md`** — "AST-cache feasibility" subsection added. Cites
  P1 cold-vs-warm ratio as motivating cost. Sketches pickle-of-parsed-shakespearelang-AST via the
  Python wrapper as the canonical technique, without committing architecture planning to it.
- **`docs/markdown/fixture-matrix.md` (or its consolidated successor)** — candidate
  first-fixture milestones named, keyed to P2/P3 outcomes. Not a decision; a shortlist with
  reasoning.
- **`docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`** — decision register
  extended with one row per probe (P1–P5).

### 2b — Pure-text clarifications (do not depend on probes)

- **`docs/markdown/target.md`** — replace prose-level normalization description with a reference
  to `tests/test_mdtest.py::_normalize`, plus a 1–2 sentence summary. Add strict-parity⊇
  normalized-contract statement to the parity-levels section.
- **`docs/markdown/divergences.md`** — concretize email-autolink equivalence rule: "decode
  `&#NNN;` and `&#xNN;` on both sides, then byte-compare. The same decoder used by the mdtest
  `Auto links` fixture's `_decode_entities` function."
- **`docs/architecture/runtime-boundary.md`** — "Wrapper toolchain" subsection added. Pins
  Python via `uv` — documenting what `./shakedown-dev` already declares, not deciding it anew.
- **New `docs/architecture/inherited-scaffold.md`** — document the existing prototype scaffold:
  - `./shakedown-dev` (bash entrypoint, self-describes as "the shape the final ./shakedown will
    take")
  - `scripts/assemble.py` (combines `src/*.spl` into `shakedown.spl`)
  - `src/{00-preamble, 10-phase1-read, 20-phase2-block, 30-phase3-inline}.spl` (three-phase
    source layout)
  - `shakedown.spl` (assembled output, not hand-edited)
  
  State explicitly: **this is prototype shape, not adopted architecture.** Architecture planning
  may keep, revise, or replace any element without constraint. The doc exists so planning
  engages with the inherited state as a surfaced choice rather than an invisible default.
- **Update `docs/README.md` and `CLAUDE.md`** to link to `inherited-scaffold.md` in the
  architecture reading order.

### 2c — Consolidation & readability

- **`docs/README.md` reading order** — move style-lexicon, codegen-style-guide, and
  style-guide-validation entries later in the list, annotated "read only if considering
  generated-SPL architecture." Canonical-flow section is untouched. Core architecture reading
  path becomes shorter for a first-time planner.
- **`docs/markdown/fixture-outlook.md` + `fixture-matrix.md` → `docs/markdown/fixtures.md`** —
  merge into a single canonical fixtures document carrying both per-fixture rows (current
  fixture-matrix content) and feature-risk tiers (current fixture-outlook content). Redirect all
  cross-references: `docs/README.md`, `CLAUDE.md`, any architecture doc that currently points at
  either file.

## File layout

### New files

| Path | Purpose | Stage |
|---|---|---|
| `scripts/generate_spl_cost_fixtures.py` | Deterministic generator for P1 + P5 fixtures | 1 |
| `scripts/measure_spl_cost.py` | Timing harness for P1/P4/P5 | 1 |
| `scripts/count_reference_defs.py` | P4 prep: count refs in largest fixture | 1 |
| `docs/spl/probes/pre-design/spl-cost-1k.spl` | P1 input (generated, checked in) | 1 |
| `docs/spl/probes/pre-design/spl-cost-4k.spl` | P1 input (generated, checked in) | 1 |
| `docs/spl/probes/pre-design/emphasis-two-pass.spl` | P2 | 1 |
| `docs/spl/probes/pre-design/nested-dispatch.spl` | P3 | 1 |
| `docs/spl/probes/pre-design/reference-lookup-scale.spl` | P4 | 1 |
| `docs/spl/probes/pre-design/scene-count.spl` | P5 (generated, checked in) | 1 |
| `docs/architecture/inherited-scaffold.md` | Surface the prototype scaffold | 2 |
| `docs/markdown/fixtures.md` | Consolidated fixture reference | 2 |

### Modified files

| Path | Edit kind | Stage |
|---|---|---|
| `tests/test_pre_design_probes.py` | Add parametrize entries for P2, P3, P4 (and P5 if assertion-capable) | 1 |
| `docs/verification-plan.md` | Append B14–B18; move closed items out of bucket D | Both |
| `docs/superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md` | Extend decision register | Both |
| `docs/performance/budget.md` | Refresh baselines | 2 |
| `docs/markdown/target.md` | Pin normalization, add strict-parity sentence | 2 |
| `docs/markdown/divergences.md` | Concrete email-equivalence rule | 2 |
| `docs/architecture/runtime-boundary.md` | Wrapper toolchain + AST-cache feasibility | 2 |
| `docs/README.md` | Reading-order adjustment, fixture-doc ref updates, inherited-scaffold link | 2 |
| `CLAUDE.md` | Fixture-doc ref updates, inherited-scaffold link | 2 |

### Deleted (via consolidation in 2c)

| Path | Disposition |
|---|---|
| `docs/markdown/fixture-outlook.md` | Contents merged into `fixtures.md` |
| `docs/markdown/fixture-matrix.md` | Contents merged into `fixtures.md` |

## Data flow

- Stage 1 probes emit either stdout assertions (P2, P3) or timing data via harness scripts (P1,
  P4, P5). No intermediate JSON or cache files are checked in.
- Harness output is copy-pasted directly into `verification-plan.md`'s B-bucket tables as text.
- Stage 2 edits read from stage 1 outputs already committed to the docs set. There is no runtime
  handoff between stages; each stage's output is plain checked-in text.

## Verification / exit criteria

### Stage 1 done when

- All five probe files exist at their planned paths.
- `uv run pytest tests/test_pre_design_probes.py` passes for assertion probes (P2, P3, and any
  assertion-capable portion of P4/P5).
- Harness scripts produce measurements for P1, P4, P5.
- `verification-plan.md` B14–B18 sections are populated with observed numbers + disposition.
- Pre-design-hardening note has one decision-register row per probe.

### Stage 2 done when

- Every item in the tier-C audit checklist (see Appendix A) maps to a completed doc edit.
- `docs/README.md` reading order and `CLAUDE.md` references resolve to existing paths.
  `rg -n 'fixture-outlook|fixture-matrix' docs/ CLAUDE.md` returns only references in
  historical/archive contexts, not active canonical ones.
- Commit discipline: stage 1 commits use `experiment:` (probe research), `test:` (pytest
  wiring), or `chore:` (scripts / generators). Stage 2 commits use `docs:`. Neither stage uses
  `feat:` or `fix:` because no production-code behaviour changes.

### Honesty rules when probes surprise

- If P2 or P3 fail, stage 2 **raises** (not lowers) the relevant risk tier in
  fixture-outlook/fixtures.md and records the failure in the decision register. Failures surface
  rather than hide.
- If P1 returns alarming numbers (e.g., 4k SPL > 60s cold), stage 2 flags the implication in
  budget.md and runtime-boundary.md. Architecture planning engages the risk explicitly.
- If `count_reference_defs.py` reports fewer definitions than expected, scale N in P4 accordingly
  rather than overtesting to make a point.

### Out of scope

- Architecture planning proper.
- Writing the replacement run-loop prompt (explicitly deferred per `CLAUDE.md`).
- Any change to `shakedown.spl`, `src/*.spl`, `scripts/assemble.py`, or `./shakedown-dev` beyond
  documenting them via `inherited-scaffold.md`.
- New divergences beyond `docs/markdown/divergences.md`.

## Appendix A — Tier-C audit checklist trace

| Audit item | Addressed by |
|---|---|
| Normalized mdtest contract algorithm not pinned | 2b: `target.md` normalization pinning |
| `./shakedown-dev` prototype status ambiguous | 2b: `inherited-scaffold.md` |
| Strict-parity⊇normalized-contract not stated | 2b: `target.md` parity-levels sentence |
| Email-autolink equivalence rule not concrete | 2b: `divergences.md` rule |
| Wrapper language not pinned | 2b: `runtime-boundary.md` wrapper toolchain |
| AST-cache mechanics missing | 2a: `runtime-boundary.md` AST-cache feasibility (cites P1) |
| Current-repo SPL cost at realistic size | P1 + 2a: `budget.md` baselines |
| Emphasis two-pass mechanics probe | P2 |
| Nested-dispatch mechanics probe | P3 |
| Reference-lookup scaling probe | P4 |
| Scene-count-per-act probe | P5 |
| Evidence-based first-fixture milestone suggestion | 2a: `fixtures.md` (or `fixture-matrix.md`) |
| Style docs reading-order placement | 2c: `docs/README.md` |
| `fixture-outlook.md` vs `fixture-matrix.md` redundancy | 2c: consolidation into `fixtures.md` |

## Appendix B — Open questions for the plan step

These are questions the implementation plan (written via `superpowers:writing-plans`) should
resolve, not questions for this spec:

- Exact N for P4's reference-lookup-scale probe — determined by `count_reference_defs.py` output.
- Whether P5's scene-count probe uses the same generator as P1 or a dedicated one.
- Commit granularity for stage 2 (one commit per doc area vs. one commit per workstream).
- Whether `fixtures.md` keeps the `docs/markdown/` location or moves to `docs/architecture/`.
- Ordering within stage 2: run 2c (consolidate fixture-outlook + fixture-matrix into fixtures.md) before 2a's risk-tier edits, so the evidence-driven edits land on the consolidated file. The alternative (2a first, 2c second) requires re-applying risk-tier edits during the merge.
