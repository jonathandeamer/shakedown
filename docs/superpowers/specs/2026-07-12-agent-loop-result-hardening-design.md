# Agent Loop Result Hardening Design

**Date:** 2026-07-12
**Status:** Accepted for implementation
**Scope:** Completion Safety Rails plan 3M, autonomous-loop hardening

## Problem

MCO can report `PASS` when a provider returned successfully but did not perform
the roadmap task. The supervisor already detects an unchanged repository as
`no_progress`, but its persisted state does not distinguish one action's
attempts from historical failures. After every executor enters cooldown, the
loop waits and eventually recycles the same ineffective chain indefinitely.

Provider session behavior also differs. Claude and Pi expose explicit
non-persistent session controls, while the installed Antigravity CLI does not.
Two Antigravity runs returned an unrelated explanation of
`--dangerously-skip-permissions`, demonstrating that prompt text alone is not a
sufficient isolation boundary.

## Goals

- Treat MCO transport completion separately from supervisor-confirmed roadmap
  progress.
- Preserve partial working-tree handoffs as legitimate progress.
- Retry trusted Claude and Codex executors after rate-limit or transient
  cooldowns.
- Stop recycling executors after substantive failures against the same
  unchanged roadmap action.
- Make automatic provider sessions stateless where the installed CLI supports
  it.
- Remove providers without a reliable stateless boundary from automatic
  routing.
- Emit a durable, structured exhaustion diagnostic and exit nonzero.

## Non-Goals

- Replacing MCO as the orchestration layer.
- Requiring every successful iteration to commit before partial work can be
  handed to the next executor.
- Inferring semantic relevance from provider prose.
- Changing planning or implementation ordering in the roadmap.
- Automatically invoking the expensive Fable governor.

## Provider Policy

Claude and Codex are trusted automatic executors. A rate limit or recognized
transient backend failure places the affected quota group on cooldown but does
not consume a substantive attempt. If no executor is currently available and a
trusted executor is waiting only on such a cooldown, the loop waits until the
earliest trusted executor becomes available and retries it.

Pi-backed Grok, Hy3, and Nemotron remain last-resort automatic fallbacks. Their
commands must use Pi's ephemeral `--no-session` mode. Implement this with
project-local shim entries in `.mco/agents.yaml`, one for each configured Pi
model, and route `agent-loop.toml` executors through those shim names instead of
MCO's built-in `pi` adapter. A substantive failure by a Pi fallback is recorded
for the current action, but does not prevent the loop from waiting for a trusted
Claude or Codex transient cooldown.

Antigravity Flash and Pro are removed from the automatic implementation pool.
They may return only after their CLI offers a verified stateless execution mode
or a project-owned wrapper provides an equivalent isolation guarantee.

Claude shim commands must add `--no-session-persistence`. Codex invocations
continue to use MCO's non-resume execution path; no Codex session flag is
required unless its adapter later introduces persistence.

## Action Identity

The supervisor captures a canonical action immediately after roadmap and
completion-gate classification, before `apply_failure_action` or
`apply_governor_directive` can rewrite its role or summary. It derives the
stable action key from that pre-rewrite action's durable routing inputs:

- action kind;
- active-plan repository-relative path, or `none`;
- first unchecked step, or `none`;
- action summary; and
- active blocker lines.

Persisted attempt state belongs only to that key. When the key changes, stale
attempts are discarded. Repository progress also clears the current attempt
cycle because the next iteration must re-read the roadmap and working tree
before deciding what remains.

Recovery routing from `IMPLEMENT` to `FIX` and governor routing from the
canonical action do not change the key. A genuine roadmap, step, blocker, or
pre-rewrite classification change does. The canonical action and execution
action are therefore separate values throughout selection and result handling.

## Result Classification

Result classification remains evidence-based:

- progress: tracked commit/diff or non-ignored untracked content changed;
- `blocked`: the invocation added a new `- BLOCK:` line under `.agent/`;
- `supervisor_timeout`: the Python supervisor terminated the MCO process group
  and assigned exit code `124`;
- `rate_limit`: recognized quota marker after excluding the cases above;
- `transient`: recognized temporary backend marker;
- `backend_failure`: nonzero process exit without a more specific marker;
- `no_progress`: zero process exit with an unchanged repository fingerprint.

The repository fingerprint remains the progress authority so interrupted work
can be handed off without a commit. MCO's `PASS` or `COMPLETED` label is
transport metadata, not task completion. The supervisor must print its own
classification explicitly after every invocation.

Progress is checked first, so provider prose that merely discusses a rate limit
cannot cool a quota group after the provider changed the repository. Marker
matching remains a compatibility fallback for unstructured MCO/provider
failures; it never overrides observed progress, a newly recorded blocker, or
the supervisor's explicit timeout exit code.

`supervisor_timeout`, `backend_failure`, and `no_progress` are substantive
failures for the current action. `rate_limit` and `transient` are availability
failures and do not add the executor to the action's substantive-attempt set.
A newly recorded blocker is a non-substantive `blocked` outcome: it adds no
cooldown or attempt, clears the prior attempt cycle, and lets the next iteration
derive the blocker-driven `FIX` action.

The fingerprint intentionally treats any non-ignored repository file as
partial progress. A provider can therefore postpone exhaustion by repeatedly
creating scratch files. This is an accepted limitation of preserving partial
handoffs; semantic or path-based relevance inference remains out of scope. The
operator-visible working-tree status and subsequent agent handoff provide the
recovery surface for such pollution.

## Exhaustion Rules

For an unchanged action:

1. Select available executors in configured priority order.
2. Skip executors already recorded with a substantive failure for that action.
3. Continue through unattempted fallback executors.
4. If no unattempted executor is available but a trusted Claude or Codex
   executor has only a transient quota-group cooldown, wait until the earliest
   such cooldown expires.
5. Otherwise write an exhaustion diagnostic, print a loud final
   `agent-loop: exhausted` line to stderr, and exit with status `5`.

The loop intentionally does not wait for an untrusted Pi fallback's cooldown,
even when that executor has not yet made a substantive attempt. Exhaustion
favors a durable operator diagnostic over waiting on a last-resort executor;
the diagnostic still records that executor's cooldown expiry.

The diagnostic is printed as JSON and persisted under `.agent/` in the loop
state. It contains the action key and human-readable action fields, attempted
executor names and failure kinds, active cooldown expiry times, trusted
executors eligible for retry, and the next-ready timestamp when one exists. It
must not contain provider output, prompt text, environment values, or secrets.

`--once` retains its current bounded behavior: one provider invocation at most.
If selection is already exhausted, it prints the same diagnostic and exits
with status `5`. `--status` and `--dry-run` expose the current attempt-cycle and
selection data without mutating it.

The operational guide documents the supervisor exit statuses after this
change:

- `0`: successful invocation, completed roadmap, status, or dry run;
- `1`: `--once` invocation returned a non-success outcome;
- `2`: setup, configuration, or MCO availability failure;
- `3`: `--once` found no executor currently available but a trusted transient
  cooldown remains retryable;
- `4`: explicit Fable governor stop;
- `5`: substantive executor chain exhausted for the unchanged action;
- `124`: explicit governor invocation reached the Python supervisor timeout;
  ordinary continuous invocations classify this internally instead;
- `130`: operator interrupt.

No external notification integration is added. Background operators receive
the final stderr line in `.agent/loop.log`, and the structured diagnostic
survives under `.agent/` for postmortem inspection.

## State Compatibility

The existing `cooldowns`, `failures`, and `last_failure` fields remain readable.
A new optional action-attempt record is added. Missing, malformed, or obsolete
records default to an empty attempt set for the newly derived action key.
Existing state files therefore require no migration command.

Successful repository progress clears the action-attempt record and the latest
substantive failure. Historical per-executor failure counters may remain for
operator visibility but cannot independently cause action exhaustion.

## Prompt Boundary

Every prompt begins with a unique invocation identifier and an explicit rule
that the provider must treat the supplied file as the complete task for a new
session. This is defense in depth, not the primary isolation mechanism.

The prompt continues to include only durable repository state: roadmap action,
active plan and step, blockers, working-tree status, last supervisor failure,
and the optional governor directive. It must not include prior provider prose.

## Verification

Unit tests with mocked subprocesses and time cover:

- action keys changing when any durable routing input changes;
- recovery and governor rewrites preserving the pre-rewrite action key;
- partial repository changes clearing the attempt cycle;
- MCO `PASS` plus no repository change becoming `no_progress`;
- progress plus rate-limit wording in provider prose classifying as progress;
- Python supervisor timeout `124` counting as a substantive attempt;
- a newly recorded blocker producing `blocked` without penalizing the executor;
- substantive failures skipping an executor for the unchanged action;
- rate limits and transient failures remaining retryable after cooldown;
- fallback attempts continuing while a trusted provider cools down;
- exhaustion exiting `5` without sleeping indefinitely;
- `--once` returning `3` only for a trusted retryable cooldown and returning
  `5` when only an untrusted fallback cooldown remains;
- `--once`, `--status`, and `--dry-run` diagnostics;
- backward-compatible state loading;
- Claude and Pi stateless command configuration;
- Antigravity absence from automatic implementation routing; and
- secret-free structured diagnostics and the documented exit-status table.

The evidence gate is:

```bash
uv run pytest tests/test_mco_loop.py
uv run ruff check scripts/mco_loop.py tests/test_mco_loop.py
uv run pyright scripts/mco_loop.py
uv run pytest
```

No SPL source, generated fragment, or Markdown behavior changes as part of this
work.
