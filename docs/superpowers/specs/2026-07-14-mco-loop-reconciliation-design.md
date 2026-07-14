# Design Spec: MCO Loop Reconciliation and Recovery Controls

* **Date:** 2026-07-14
* **Status:** Approved
* **Topic:** account for outstanding branches and planning artifacts before resuming autonomous roadmap execution

## 1. Problem

The MCO loop correctly advances the single active roadmap plan, but it does not
make non-main branch work or unregistered active planning artifacts part of its
durable decision state.  On 2026-07-14 this left one Slice-2 repair commit on an
unmerged worktree branch and one older carrier-observer test commit on another
branch, while a development-efficiency spec and plan were untracked.  The
recorded merge-conflict blocker did not name the branch or commit at issue.

Separately, `apply_failure_action()` changes every previous `backend_failure`
or `no_progress` action to `FIX`.  A `- BLOCK[plan]:` action therefore loses
its planning routing after a planner backend failure and can dispatch an
implementation provider to an architectural/reconciliation problem.

## 2. Goals and non-goals

### Goals

- Preserve the canonical action kind when recovery follows a failed planning
  action.
- Stop ordinary roadmap execution whenever candidate branch work lacks a
  durable disposition.
- Require actionable blockers to identify the exact branch/commit context
  needed for a planner or implementer to resolve them.
- Prevent untracked active plans or specs from silently bypassing the roadmap.
- Reconcile today's outstanding candidate branches and development-efficiency
  artifacts without assuming they should be merged.
- Retain the documented `spike-a-lists-wip` branch as redesign reference.

### Non-goals

- Automatically merge, cherry-pick, delete, rebase, or force-push a branch.
- Turn the loop into a general pull-request manager.
- Change Slice-2 Markdown behaviour as part of the recovery controls.
- Treat ignored runtime state under `.agent/` as an unregistered planning
  artifact.

## 3. Architecture

### 3.1 Recovery routing

`apply_failure_action(action, state)` remains responsible for converting a
substantive failed implementation action into a bounded `FIX` action.  It must
return the original action unchanged when the canonical action is `PLAN`.
Consequently a `BLOCK[plan]` blocker remains assigned to the planning pool
after a planner backend failure; executor selection and escalation then use
the existing planning and escalation rules unchanged.

### 3.2 Durable branch dispositions

Create a tracked, human-authored branch ledger at
`.agent/branch-dispositions.toml`.  Each non-main branch with commits not
reachable from `main` must have one entry keyed by its full local branch name:

```toml
[branches."fix-665750fcbb154a4dadcddbfc55ab3326-codex-implement"]
head = "cd89aa80d8da93793fe9c749754702e3cd10f1c7"
disposition = "review"
reason = "Slice-2 repair from a stale base; compare its carrier changes against main."

[branches."spike-a-lists-wip"]
head = "a31e61cfa18f462ab2028b9428b23ff7eaf640fb"
disposition = "preserve"
reason = "Documented non-parsing pre-splc redesign reference."
```

Allowed dispositions are `review`, `preserve`, `superseded`, and `integrated`.
`review` prevents the loop from performing normal work and produces a
planner-only reconciliation action.  `preserve`, `superseded`, and
`integrated` permit normal execution only when the recorded `head` equals the
current branch head.  A moved branch must be reviewed again.  Remote tracking
refs do not duplicate the local branch requirement; a remote-only branch with
unmerged commits is reported as an error because it has no local disposition
key to bind to.

The inventory uses `git for-each-ref` and `git merge-base --is-ancestor
<branch> main`.  It excludes `main`, branches already merged into `main`, and
the current checked-out main ref.  It neither inspects nor modifies stashes.

### 3.3 Actionable blocker schema

Add a parser and validator for branch-reconciliation blockers.  The required
form is one physical line:

```
- BLOCK[plan]: branch=<name>; head=<40-hex-sha>; base=<40-hex-sha>; request=<review|integrate|supersede>; detail=<nonempty text>
```

The validator checks that the branch exists, `head` is its current commit,
`base` is its current merge base against `main`, and the request is valid.
Invalid structured blockers are treated as an ordinary `FIX` action with an
explicit validation diagnostic; valid ones retain the existing planning
routing.  Existing free-text blockers remain supported, so historical blocker
entries are not retroactively invalidated.

### 3.4 Unregistered planning-artifact fence

Before selecting an executor, inspect non-ignored untracked files under
`docs/superpowers/plans/` and `docs/superpowers/specs/`.  Any such artifact
creates a planner-only reconciliation action that names the file.  The
resolution is to commit and register it in the roadmap as appropriate, or to
remove it through an operator-approved action; the loop must not delete or
stash it itself.  Tracked modifications are allowed and continue to be passed
to the executor as ordinary dirty-worktree context.

### 3.5 One-time reconciliation

The recovery work begins by recording dispositions for:

| Branch/artifact | Required outcome |
|---|---|
| `fix-665750fcbb154a4dadcddbfc55ab3326-codex-implement` | Review its delta against current main.  Integrate only via a fresh, tested, conflict-free change; otherwise mark `superseded` with the replacement commit(s). |
| `codex/implement-a9e381f6` | Compare its carrier-observer coverage with shipped 4S contracts.  Integrate only unique, still-needed coverage; otherwise mark `superseded`. |
| `spike-a-lists-wip` | Record `preserve`; no code integration. |
| `2026-07-14-development-efficiency*.md` | Commit the documents, reconcile their unchecked steps with landed commits and evidence, then add an explicit roadmap record or archive them as operator-directed infrastructure work. |

The generic `Merge conflict when trying to integrate changes into main` blocker
is replaced with a structured, branch-specific blocker until the review
disposition is terminal.

## 4. Roadmap transition

The recovery must not create a second in-flight plan.  Before its implementation
plan is registered, mark Slice 2 as `halted` with a dated governance-recovery
reason and preserve all completed checkboxes.  Register this recovery as the
sole in-flight row.  Once reconciliation and loop safeguards pass their gates,
the follow-up planning decision is explicit: resume Slice 2 with a refreshed
plan or supersede it with a revised Slice-2 plan.  The loop remains stopped
until that decision is committed.

## 5. Verification

- Unit tests prove planner recovery remains `PLAN`, while implementation
  recovery remains `FIX`.
- Unit tests cover clean, stale, missing, remote-only, and moved branch ledger
  cases without invoking destructive Git operations.
- Unit tests validate structured blockers and prove legacy free-text blockers
  retain their current routing.
- Unit tests cover no untracked artifacts, a plan artifact, a spec artifact,
  and ignored `.agent/` state.
- An integration-style dry run with the reconciled repository reports the
  correct planner action while a `review` disposition exists, then normal
  execution only after every candidate is terminally disposed.
- `uv run pytest tests/test_mco_loop.py -q`, `uv run ruff check .`, `uv run
  pyright`, and the default `uv run pytest -q` pass before the recovery plan is
  marked shipped.

## 6. Failure handling

The loop must fail closed for missing, stale, or malformed disposition entries:
it reports a planner-only reconciliation action and makes no branch mutation.
An inability to inspect Git inventory is a `FIX`-class infrastructure error.
No action may remove a user worktree, branch, stash, or untracked artifact.
