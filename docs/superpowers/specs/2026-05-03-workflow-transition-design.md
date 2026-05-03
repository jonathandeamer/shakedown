---
title: Workflow Transition — Run-loop to Supervised Superpowers Sessions
date: 2026-05-03
status: approved
---

# Workflow Transition Design

## Goal

Replace all forward-facing references to the `run-loop` autonomous executor with
the new supervised implementation model, so that new agents reading `CLAUDE.md`
and the docs understand the correct way to advance implementation work.

The run-loop code, prompt, and `.agent/` state are preserved as historical
artifacts. Only forward-facing instructions change.

## Scope

Three files change. No plan files, no SPL source, no tests.

| File | What changes |
|---|---|
| `CLAUDE.md` | "Intended workflow" blurb; `## run-loop` section replaced by `## Implementation workflow`; `## Operator halt switch` section removed |
| `docs/README.md` | One line: "active `run-loop` prompt" → "legacy `run-loop` prompt (archived)" |
| `docs/superpowers/plans/plan-roadmap.md` | References entry: drop "`run-loop` contract" |

## New workflow description

When a plan is marked `in flight` in the roadmap, an operator starts a
supervised implementation session manually:

1. Open a new Claude Code session in the repo.
2. Invoke `superpowers:executing-plans` or `superpowers:subagent-driven-development`.
3. Work through the active plan task by task with the operator present throughout.

The operator is the halt mechanism. There is no autonomous loop and no in-repo
kill switch.

## CLAUDE.md — exact changes

### "Intended workflow" paragraph

**Before:**
> Interactive Claude sessions (with superpowers) are used for bootstrapping,
> design, and planning. Huntley/run-loop autonomous loops are used for the
> actual implementation of `shakedown.spl` once a concrete plan is marked in
> flight in `docs/superpowers/plans/plan-roadmap.md`.

**After:**
> Interactive Claude sessions (with superpowers) are used for bootstrapping,
> design, and planning. Implementation sessions are operator-triggered and
> supervised: start a new session, invoke `superpowers:executing-plans` (or
> `superpowers:subagent-driven-development`), and work through the active plan
> task by task with the operator present.

### `## run-loop` section

**Replaced by:**

```markdown
## Implementation workflow

When a plan is marked `in flight` in `docs/superpowers/plans/plan-roadmap.md`,
start a supervised implementation session:

1. Read the roadmap and identify the active plan.
2. Invoke `superpowers:executing-plans` or `superpowers:subagent-driven-development`
   to work through the plan task by task.
3. The operator triggers each session manually and is present throughout.

### Legacy: run-loop

The earlier approach used `run-loop`, a Python executor that drove autonomous
agent sessions via `docs/prompt-shakedown.md`. The code and prompt are
preserved for history but are no longer the active workflow.

```bash
./run-loop                            # legacy: use the active default prompt
./run-loop docs/some-other-prompt.md  # legacy: alternate prompt
```

State: `.agent/run-loop-state.json`. Completion marker: `.agent/complete-<name>.md`.
```

### `## Operator halt switch (.agent/blockers.md)` section

**Removed entirely.** This section described a run-loop-specific mechanism (an
in-repo kill switch the autonomous agent polled each iteration). With a
supervised session the operator is present and can halt directly; the mechanism
is obsolete. The `.agent/blockers.md` file is left in place as a legacy
artifact but is no longer a forward-facing convention.

## docs/README.md — exact change

In the optional-context bullet at the bottom of the reading list:

**Before:**
```
- [`prompt-shakedown.md`](prompt-shakedown.md) — active `run-loop` prompt; currently exits when the roadmap has no plan marked `in flight`.
```

**After:**
```
- [`prompt-shakedown.md`](prompt-shakedown.md) — legacy `run-loop` prompt (archived); no longer the active implementation workflow.
```

And the "Canonical Flow of Truth" section line:

**Before:**
```
- **Operational process artifacts:** `docs/superpowers/plans/plan-roadmap.md` tracks live plan status, and `docs/prompt-shakedown.md` is the active run-loop prompt. Other `docs/superpowers/` content is supporting context only, except for the selected architecture spec linked from `architecture/selected-architecture.md`.
```

**After:**
```
- **Operational process artifacts:** `docs/superpowers/plans/plan-roadmap.md` tracks live plan status. `docs/prompt-shakedown.md` is the legacy run-loop prompt (archived). Other `docs/superpowers/` content is supporting context only, except for the selected architecture spec linked from `architecture/selected-architecture.md`.
```

## plan-roadmap.md — exact change

In the References section, final bullet:

**Before:**
```
- `CLAUDE.md` — commit conventions, version cadence, target interface, `run-loop` contract.
```

**After:**
```
- `CLAUDE.md` — commit conventions, version cadence, target interface, implementation workflow.
```

## CLAUDE.md — version-cut operator-only note

In the "When to cut a version" section, the operator-only note (line 238):

**Before:**
```
**Operator-only.** Autonomous run-loop agents must NOT run `cz bump`,
`git tag`, `git push --tags`, or update `CHANGELOG.md` unless the current
plan step explicitly authorises it. Version cuts are operator decisions per
architecture spec §7.9.
```

**After:**
```
**Operator-only.** Implementation agents must NOT run `cz bump`,
`git tag`, `git push --tags`, or update `CHANGELOG.md` unless the current
plan step explicitly authorises it. Version cuts are operator decisions per
architecture spec §7.9.
```

## What is not changed

- `docs/prompt-shakedown.md` — preserved as-is; it is a legacy artifact.
- `.agent/blockers.md`, `.agent/run-loop-state.json`, `.agent/run-loop.log` — preserved.
- `run-loop` executable — preserved.
- Spike A plan (`docs/superpowers/plans/2026-05-01-spike-a-lists.md`) — already has the correct superpowers skill header; no change needed.
- Any shipped or superseded plan entries in the roadmap — historical record, not touched.
