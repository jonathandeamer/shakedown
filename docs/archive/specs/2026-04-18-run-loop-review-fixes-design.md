# Run-Loop Review Fixes Design

**Date:** 2026-04-18

## Goal

Address the review-identified contract regressions in `run-loop` without redesigning the broader
hardening state machine.

This patch restores the documented unattended-loop behavior by:

- failing fast when the default prompt path is intentionally unavailable
- treating cooldown as a temporary backoff before retry, not driver termination
- resetting Claude resource-failure streaks on any useful progress
- making the on-disk state file authoritative between iterations

## Non-Goals

- changing backend selection policy beyond the cooldown fix
- introducing new retry heuristics
- adding new persisted state fields unless required for schema hygiene
- redesigning prompt handling for explicit prompt arguments

## Problem Summary

The current implementation has three contract-level issues:

1. `./run-loop` with no arguments still points at `docs/prompt-shakedown.md`, which is
   intentionally absent. Instead of failing clearly, the loop falls into recoverable-failure
   handling.
2. Cooldown branches sleep for one hour and then exit the driver, which breaks unattended retry
   behavior.
3. `consecutive_claude_resource_failures` can survive across useful progress and therefore stop
   being truly consecutive.

There is also a state-freshness concern: after any long wait, the next decision should be made
from freshly loaded normalized on-disk state rather than whatever was in memory before sleep.

## Design Summary

This is a narrow repair patch. Keep the current state-machine structure, but tighten four places:

- default-prompt validation before the loop begins
- cooldown control flow
- success-path counter reset
- state normalization and reload discipline

## Default Prompt Contract

When `run-loop` is invoked with no explicit prompt argument, it uses the repo default prompt path.
That path is currently intentionally missing.

New behavior:

- if no explicit prompt argument was given and `PROMPT_FILE` does not exist, print a clear
  operator-facing stderr message
- exit nonzero immediately
- the message must tell the operator to pass an explicit prompt path

Explicit prompt arguments keep current behavior. If the operator names a prompt path, `run-loop`
may continue to treat read failures for that explicit file as recoverable iteration failures if
that remains consistent with the broader hardening design.

## Cooldown Semantics

Cooldown is a temporary backoff, not termination.

New behavior:

- any branch that enters cooldown must save normalized state first
- then sleep for one hour
- then `continue` to the top of the loop

The next top-of-loop pass must:

- re-check completion marker
- reload normalized state from disk
- observe any manual edits made during cooldown

This restores the intended unattended-loop contract and removes stale in-memory decision-making
after long sleeps.

## Claude Resource-Failure Streak

`consecutive_claude_resource_failures` must represent truly consecutive Claude resource-pressure
failures in loop terms.

New behavior:

- increment it only when a Claude iteration is classified as a resource-pressure failure
- reset it on any useful progress, regardless of backend
- keep the existing reset on Claude non-resource iterations if still useful, but useful progress is
  the required reset point

This prevents a later single Claude OOM from being mistaken as the third consecutive resource
failure after unrelated successful work happened in between.

## State Freshness And Schema Discipline

The state file is authoritative between iterations.

Rules:

- `default_state()` defines the complete allowed schema
- `load_state()` normalizes loaded JSON against `default_state()`
- unknown keys are silently dropped
- `save_state()` writes normalized state only
- no state should remain authoritative across iteration boundaries after sleep

The intended control flow is:

1. load normalized state
2. make decisions for the current iteration
3. save normalized state
4. if sleeping, sleep and then `continue`
5. start the next iteration by reloading from disk

No TTL is needed. Freshness comes from reloading on every iteration boundary instead of caching
state across sleeps.

## Recommended Helper Shape

Add or refine small helpers rather than duplicating inline logic:

- `validate_default_prompt_path()` or equivalent fail-fast check
- `enter_cooldown(...)` helper that saves state, sleeps, and returns control to the caller so the
  caller can `continue`
- `reset_success_counters(...)` helper or equivalent success-path logic
- state normalization invoked in both `load_state()` and `save_state()`

The patch should stay small and local to `run-loop` plus `tests/test_run_loop.py`.

## Tests

Add or update tests for:

- default invocation with missing default prompt exits nonzero and emits a clear operator message
- cooldown after both-limited backends sleeps and then retries rather than exiting
- cooldown after second recoverable failure sleeps and then retries rather than exiting
- useful progress resets `consecutive_claude_resource_failures`
- unknown keys in the state file are silently dropped on load/save normalization
- post-cooldown iteration reloads state from disk rather than continuing with stale in-memory state

## Risks And Tradeoffs

- Explicit-prompt read failures and default-prompt validation should remain distinct; otherwise the
  intentionally missing default prompt keeps looking like a transient runtime issue.
- Allowing manual state-file edits during cooldown trades a small amount of determinism for a large
  gain in operator control and recoverability.
- Silent dropping of unknown state keys reduces operator feedback but keeps the state schema stable
  and drift-resistant.

## Scope Check

This patch is intentionally limited to the review findings and the closely related state-freshness
concern. It should not reopen the broader run-loop hardening design.
