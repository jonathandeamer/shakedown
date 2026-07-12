# Cache Feasibility Spike Outcome

**Status:** Pre-Slice-1 deliverable per architecture spec §7.1 #4 / §5.3a.

Re-run with `uv run python scripts/cache_spike.py`.

## Result

```json
{
  "cache_key": "363725a22a581aaf4ae03ec3f2beec82a7f2da9f7f40f2ac308de326d6100a06:3.14.4:1.0.0:v1",
  "cache_key_inputs": {
    "cache_shape_version": 1,
    "python_version": "3.14.4",
    "shakespearelang_version": "1.0.0",
    "spl_hash": "363725a22a581aaf4ae03ec3f2beec82a7f2da9f7f40f2ac308de326d6100a06"
  },
  "cache_proven_reason": "not proven; byte-identity and overhead criteria were not exercised",
  "decision": "direct_assemble_and_run",
  "direct_run_returncode": 0,
  "direct_run_seconds": 2.51,
  "direct_run_stderr_excerpt": "",
  "direct_run_stdout_bytes": 29,
  "pickle_candidate_succeeded": false,
  "pickle_path_outcome": "pickle-dumps-failed:PicklingError:Can't pickle <function Question.<lambda> at 0x7fb43eec92d0>: it's not found as shakespearelang._operation.Question.<lambda>"
}
```

## Decision

**Dev-mode shape:** direct_assemble_and_run

The spike does not prove a reusable cache target. The dev wrapper must use
direct assemble-and-run mode until a future spike proves all §5.3a cache
criteria: reusable representation, byte-identical cached execution,
separate wrapper-overhead measurement, and versioned invalidation key.

## Follow-up: in-process interpreter reuse (2026-07-12, plan 3M Task 5)

A session-scoped in-process `shakespearelang.Shakespeare(...)` runner —
effectively a hand reuse of the parsed play across calls, the same shape this
spike originally probed for a pickled-AST cache — was prototyped as a
regression-loop acceleration candidate (`docs/verification-plan.md` B21).
State isolation held across repeated/reordered inputs and error cases, and
output matched a fresh `./shakedown` subprocess. But construction cost per
`Shakespeare()` call was ~11s-13s, statistically identical to a fresh
subprocess invocation, because both pay the same `shakedown.spl`
parse/compile cost this spike measured at 2.51s for a much smaller play.
**Not adopted** for acceleration; `pytest-xdist` was adopted instead for the
long regression suite. This reinforces rather than reverses the
`direct_assemble_and_run` decision above: reusing a constructed interpreter
in-process does not avoid the dominant cost, so there is still no proven
cache target.

## References

- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §5.3a, §7.1 #4.
- `docs/verification-plan.md` baseline B14 cold-cost figure, baseline B21
  regression-acceleration measurement.
