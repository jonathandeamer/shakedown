# Run-Loop Hardening Design

**Date:** 2026-04-18

## Goal

Harden `run-loop` so it fails gracefully, avoids token-burning retry loops, self-heals where
possible, and retries with a one-hour cooldown when repeated failures indicate the loop is stuck.

The design must cover:

- unexpected backend behavior
- Claude memory-pressure failures before and after launch
- repeated iterations that consume tokens but make no useful repo progress
- repo-progress detection that counts both tracked changes and newly created untracked files
- bounded self-healing for oversized Claude temp data under `/tmp/claude-*`

## Non-Goals

- redesigning the prompt format or loop methodology
- changing backend CLI choices
- adding a persistent run log file
- auto-fixing arbitrary backend output errors

## Design Summary

`run-loop` becomes a small persisted state machine. Each iteration gathers pre/post-run signals,
classifies the result, updates recovery state, and chooses one next action:

- continue on the same backend
- switch to the other backend immediately
- sleep for one hour before retrying
- exit only for completion marker or operator interrupt

The script must stop treating `exit_code == 0` as equivalent to success. Success is defined by
useful repo progress or explicit completion-marker exit.

## Iteration Signals

Each iteration should collect:

- backend name
- backend exit code
- captured output
- output fingerprint
- repo snapshot before the run
- repo snapshot after the run
- whether useful repo progress occurred
- whether a limit/resource failure was detected

## Useful Progress

Useful progress means a repo change outside the loop's own bookkeeping paths.

Count as progress:

- tracked file modifications
- tracked file additions, deletions, and renames
- newly created untracked files inside the repo

Ignore as progress:

- `.agent/run-loop-state.json`
- `.agent/complete-*.md` as ordinary progress signals

Completion markers remain special:

- if a completion marker exists at loop start, exit immediately
- if a completion marker is created during an iteration, the next top-of-loop check exits cleanly

`no files changed` counts as `no_progress` even if the backend emitted substantial output.

## Output Heuristics

Stdout/stderr are secondary signals, not the primary progress measure.

The loop should still record:

- empty output
- very short output
- repeated identical output across iterations

These signals should strengthen the classification that the loop is stuck when combined with no
useful repo changes, but should not by themselves override a real repo diff.

## Classification

Each iteration must classify into one of:

- `useful_progress`
- `recoverable_failure`
- `hard_failure`

### Useful Progress

Use when useful repo progress occurred, regardless of whether the backend also printed warnings.

Effects:

- clear recoverable-failure counters
- clear Claude resource-failure counter unless the iteration itself was a Claude resource failure
- continue using the current backend by default

### Recoverable Failure

Use for failures that should trigger backend switching and then cooldown:

- backend usage-limit message
- Claude preflight memory-pressure refusal
- Claude post-exit resource-pressure failure
- backend nonzero exit
- prompt read/expand failure
- no useful repo progress
- repeated identical weak output with no useful repo progress

Effects:

- increment recoverable-failure counters
- switch backend on the first consecutive recoverable failure
- sleep one hour on the second consecutive recoverable failure when the alternate backend also
  failed to make useful progress

### Hard Failure

Use for failures inside the driver itself:

- repo snapshot failure
- internal bookkeeping/state-update exception
- other run-loop-internal errors that prevent safe classification

Effects:

- emit a clear stderr diagnostic
- sleep one hour before retrying
- avoid tight failure loops

## Retry Policy

The recovery rule is:

1. first consecutive recoverable failure: switch backend immediately
2. second consecutive recoverable failure on the alternate backend: sleep one hour
3. after cooldown, retry from persisted state rather than exiting permanently

This policy applies equally to:

- no-progress loops
- explicit limit messages
- backend crashes
- Claude resource-pressure failures

The loop must not spin indefinitely on repeated immediate failures without either switching
backend or sleeping.

## Claude Resource-Pressure Handling

Claude-specific memory handling stays explicit and bounded.

### Existing Behavior To Preserve

- preflight host checks for low memory, missing swap under marginal memory, and `/tmp` pressure
- post-exit classification for Claude resource-pressure exits

### New Behavior

Claude memory-pressure conditions must no longer terminate the loop permanently. They become
recoverable failures handled by the switch/sleep policy.

The loop must also track:

- `consecutive_claude_resource_failures`

On the third consecutive Claude resource-pressure failure:

1. scan `/tmp/claude-*`
2. if any matching path exceeds `700 MiB`, delete **all** `/tmp/claude-*`
3. emit a stderr message showing why cleanup happened and what was removed
4. sleep one hour before retrying

Cleanup should trigger only for Claude resource-pressure failures, not for:

- usage-limit messages
- generic nonzero exits
- no-progress classifications

If deletion itself fails, that failure should be reported and treated as recoverable unless the
driver can no longer continue safely.

## Persisted State

Extend `.agent/run-loop-state.json` with fields such as:

- `last_used`
- `cooldown_until`
- `consecutive_recoverable_failures`
- `consecutive_claude_resource_failures`
- `last_failure_kind`
- `last_output_fingerprint`

The state file remains local driver state and is never counted as useful progress.

Corrupt or missing state should reset to defaults with a warning rather than crashing the loop.

## Repo Snapshot Mechanism

Progress detection needs a stable pre/post iteration snapshot of repo state.

The implementation should compute a normalized repo snapshot containing:

- tracked file status relevant to content/path changes
- untracked files currently present

Then filter ignored paths before comparing snapshots.

The implementation should not rely on `stdout` text to infer file mutations.

## Failure Escalation Boundaries

The loop should be self-healing, but bounded:

- switch once before sleeping
- sleep for one hour before reattempting repeated failures
- auto-delete `/tmp/claude-*` only after three consecutive Claude resource-pressure failures and
  only when at least one matching path exceeds `700 MiB`

This avoids both tight loops and over-aggressive cleanup.

## Testing Strategy

Add tests for:

- repo snapshot detects tracked modifications
- repo snapshot counts newly created untracked files
- ignored paths such as `.agent/run-loop-state.json` do not count as progress
- no repo change counts as no progress even with output
- first recoverable failure switches backend
- second consecutive recoverable failure sleeps for one hour
- Claude preflight failures enter switch/sleep behavior instead of exiting permanently
- Claude post-exit resource failures enter switch/sleep behavior instead of exiting permanently
- repeated identical output plus no repo change is treated as a stuck loop
- third consecutive Claude resource-pressure failure triggers `/tmp/claude-*` cleanup when any
  matching path exceeds `700 MiB`
- no cleanup occurs for Claude usage-limit messages or generic failures
- completion marker still exits immediately

## Risks And Tradeoffs

- Repo-diff-based progress detection is stricter than stdout-based success and may classify some
  read-only analysis iterations as failures. This is intentional to avoid token-burning no-op
  loops.
- Output heuristics should remain secondary because backend wording can change.
- Automatic `/tmp/claude-*` cleanup is deliberately narrow because deletion is destructive.

## Recommended Implementation Shape

Keep `run-loop` as a single script, but factor the new behavior into small helper functions for:

- repo snapshot collection and comparison
- iteration classification
- cooldown calculation
- Claude temp cleanup
- state loading/updating defaults

This keeps the script testable without requiring a full architectural rewrite.
