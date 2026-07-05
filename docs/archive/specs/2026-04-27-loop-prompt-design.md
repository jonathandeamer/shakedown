# Run-Loop Prompt Design

**Date:** 2026-04-27
**Status:** Design note feeding `superpowers:writing-plans`
**Scope:** decisions about the shape, content, and safeguards of
`docs/prompt-shakedown.md` — the prompt the `run-loop` driver feeds to
each autonomous iteration during implementation.

This note is *not* the prompt itself. The prompt is written as part of
the implementation plan (architecture spec §7.1 #9). This note records
the design decisions writing-plans should honour, so the resulting plan
shape and the resulting prompt fit each other.

## Context

The architecture spec is locked. The literary spec is locked. The next
step is `superpowers:writing-plans`, which produces an implementation
plan checklist. That plan is then driven by the Huntley/Ralph loop
documented in `docs/ralph-loop.md`.

The loop driver (`run-loop` at the repo root) already absorbs four
operational concerns:
- Backend auto-switch (Claude ↔ Codex) on usage limits.
- Sleep-on-double-limit.
- Operator-set completion marker (`.agent/complete-shakedown.md`).
- OOM preflight + post-exit classifier.

It also detects no-progress iterations: `has_useful_repo_progress()`
compares git state before/after, ignoring the marker and state files;
output fingerprinting catches identical-output spins; two consecutive
recoverable failures rotate backends and enter cooldown. The prompt
must cooperate with these, not duplicate them.

## Decisions

### 1. Prompt shape: plan-driven, single prompt

Per `docs/ralph-loop.md` there are three viable shapes. Use shape #2,
**plan-driven**:

> Find the first task in the plan with any unchecked step. Complete that
> step. Check it off. Commit.

**Why not test-driven (#1):** the pre-Slice-1 deliverables (architecture
§7.1: parity harness, wrapper, assembler, codegen, literary.toml, token
allocation, cache spike) are not "make a failing test pass" units. A
test-driven prompt would need a phase switch. Plan-driven covers both
phases with a single instruction.

**Why not experiment-gated (#3):** experiments are feasibility work; we
are past that.

**Why one prompt, not two:** the plan already encodes the phase order
(setup tasks before Slice 1 tasks before Spike A tasks). The agent
doesn't choose phase; the plan does. A single prompt keeps the loop
simple and avoids drift between phase prompts.

### 2. Iteration scope: one plan step per iteration

A "plan step" is the granularity writing-plans already produces:
2–5 minutes of work, single concrete change, ending in a commit.
Examples: "write the failing test for X", "implement the minimal code
to pass X", "commit". *Not* "implement Slice 1".

**Implication for writing-plans:** every plan step must be a
self-contained one-iteration unit with a single commit at its end,
matching the writing-plans skill's own discipline. Slice-level rollups
exist as headings, not as iteration units.

### 3. Universities (`@file` set)

The prompt stack-allocates these via `@path` references (the `run-loop`
driver expands them into the prompt before invocation, per
`docs/ralph-loop.md` §"the @file stack-allocation pattern"):

- `@docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`
  — what to build, in what order, with what verification gates.
- `@docs/superpowers/plans/<plan>.md` — checkbox state. Resolves to the
  current plan; renamed in the prompt when writing-plans produces it.
- `@docs/spl/literary-spec.md` — voice, palette, and decorative-surface
  policy. The aesthetic gate is enforced at code review, but the agent
  should reach for the policy first rather than discovering it after.
- `@docs/spl/reference.md` — SPL legality.
- `@docs/markdown/target.md` and `@docs/markdown/divergences.md` —
  oracle behaviour surface and intentional exceptions.
- `@CLAUDE.md` — commit conventions, version cadence, target interface.
- `@.agent/blockers.md` — operator-managed signal file (see §5).

No citation spec for `Markdown.pl`. `docs/markdown/oracle-mechanics.md`,
`reference-mechanics.md`, `html-block-boundaries.md`, and
`list-mechanics.md` already serve that role and are the canonical
mechanics docs per `CLAUDE.md`. Revisit if Slice 3+ stalls on parity.

### 4. Standing instructions

The prompt body itself is short — target ~200 words of standing
instructions, per the RepoMirror "short prompt beats long prompt"
finding (`docs/ralph-loop.md`). The instructions encode:

- **One step per iteration.** No batching.
- **No placeholders.** Real implementations only.
- **Conventional commits required.** `.githooks/commit-msg` enforces it
  locally; the agent must not bypass with `--no-verify`.
- **Aesthetic policy is in `@docs/spl/literary-spec.md`.** Reach for it
  before writing decorative surfaces, not after.
- **No autonomous version bumps or releases.** Per architecture spec
  §7.9, the agent must not run `cz bump`, `git tag`, `git push --tags`,
  or update `CHANGELOG.md` unless the current plan step explicitly
  authorises it. Version cuts are operator decisions.
- **Stuck → write to blockers.md, exit cleanly.** If the next unchecked
  step needs information the agent does not have, append the question
  to `.agent/blockers.md` and exit *without modifying code*. This
  cooperates with `has_useful_repo_progress()` — the modified
  `blockers.md` counts as progress, the operator sees the question on
  next loop start.
- **Respect blockers.md.** If `.agent/blockers.md` has any open
  entries, address them first, or, if blocked from doing so, exit
  without changes.

### 5. Operator-detected halt mechanism: `.agent/blockers.md`

Architecture spec §8.2 lists halt-and-redesign triggers (cost/test-time
blowups, Spike A/B failures). The agent does **not** self-detect these.
The operator reads diffs and decides.

Operator authority is exercised through one file:
`.agent/blockers.md`. Conventions:

- The file exists in the repo (writing-plans creates it empty during
  the pre-Slice-1 setup task).
- Each entry is a single-line bullet: `- BLOCK: <one-line reason>`.
- The agent reads it on every iteration via the `@.agent/blockers.md`
  university reference.
- If any line starts with `- BLOCK:` the agent must not advance the
  plan; it may only edit `blockers.md` (e.g., to add a clarifying
  question) or exit cleanly.
- The operator removes the line when the block is resolved.

This gives the operator a single, in-repo, version-controlled halt
switch with no separate process or signalling channel.

### 6. Completion criteria

The agent writes `.agent/complete-shakedown.md` only when **both**:

1. Every step in the plan is checked off.
2. `uv run pytest tests/test_mdtest.py -q` passes 23/23 *and* the strict
   Shakedown-vs-Markdown.pl parity harness (architecture spec §7.1 #6)
   reports zero byte-level mismatches.

`scripts/markdown_pl_parity_audit.py` is **not** sufficient — it audits
checked-in expected files, not `./shakedown` output (architecture spec
§7.1 #6 / §8.1).

### 7. No-progress / token-waste safeguards (summary)

| Layer | Mechanism |
|---|---|
| Driver | `has_useful_repo_progress()` rotates backends after 2 consecutive no-progress iterations |
| Driver | Output fingerprinting catches identical-output spins |
| Driver | Cooldown after both backends limited; OOM preflight |
| Prompt | "Stuck → write blockers.md, exit cleanly" turns dead-ends into operator-visible signal in one iteration, not silent burn |
| Prompt | "Respect blockers.md" prevents the loop from speeding past a block the operator already raised |
| Prompt | "No autonomous version bumps" prevents large irreversible side effects under operator-absent conditions |
| Plan | Single-iteration steps with explicit code/test content prevent the agent from spinning on under-specified tasks |
| Plan | Per-slice verification gate (architecture §8.1) is its own plan step, not a thing the agent decides to run when it feels done |

## Inputs to writing-plans

When invoking `superpowers:writing-plans`, the plan author should:

1. Produce checkbox-shaped single-iteration steps as the writing-plans
   skill already requires; this design depends on that discipline.
2. Include the pre-Slice-1 architecture §7.1 deliverables as the first
   tasks, with `docs/prompt-shakedown.md` itself created as part of #9.
3. Include a task to create `.agent/blockers.md` (empty) and to
   document its convention in `CLAUDE.md`.
4. Schedule "run the strict parity harness" (§7.1 #6) as a sub-step of
   every slice's verification gate, not only at the end.
5. Treat version bumps (`cz bump`) as operator-authorised plan steps,
   not autonomous ones — the corresponding plan checkbox is checked by
   the operator, not the agent.

## Open items deferred to plan-time

These are intentionally not decided here; they fall out naturally
during writing-plans:

- The exact wording of the prompt's standing instructions (drafted as
  the §7.1 #9 deliverable, against this note as input).
- Whether `.agent/blockers.md` should also carry a non-blocking
  `- NOTE:` line type (lean: yes, but decide when first needed).
- Per-step time/iteration budgets (writing-plans skill addresses).

## References

- `docs/ralph-loop.md` — methodology, prompt patterns, `@file` pattern.
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`
  — §7.1 #6 (strict parity harness), §7.1 #9 (run-loop prompt
  deliverable), §7.9 (no autonomous version bumps), §8.2
  (halt-and-redesign triggers).
- `docs/spl/literary-spec.md` — aesthetic policy.
- `run-loop` (repo root) — `has_useful_repo_progress()`,
  `consecutive_recoverable_failures`, output fingerprinting, OOM guard.
- `CLAUDE.md` — `run-loop` contract, completion-marker convention.
