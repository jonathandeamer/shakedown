# Blockers

This file is the operator's in-repo halt switch for the run-loop. Any line
starting with `- BLOCK:` halts the autonomous agent on the next iteration —
the agent must address it (or, if it cannot, exit cleanly without modifying
code).

The agent itself MAY append `- BLOCK:` lines when it hits a question it
cannot resolve from the universities (`@file` references in
`docs/prompt-shakedown.md`); doing so is the only legal way to surface a
blocker mid-run. The operator removes the line when the block is resolved.

Non-blocking notes (no halt) use `- NOTE:` instead.

- BLOCK: Spike A halted per architecture §8.2 on 2026-07-05. Hand-authoring
  the Act II list pass produced a ~1,300-line diff that never reached a
  parseable state (preserved on branch spike-a-lists-wip). Root cause is
  authoring SPL by hand at scale, not list semantics. Resolution direction:
  revise the architecture so SPL is generated from a small intermediate
  representation (interactive design session required). Do not resume list
  implementation until the revised architecture ships. The same Act I
  handoff change (f45b626) also removed the runtime-error behavior that
  tests/test_binary_contract.py::test_repo_shakedown_entrypoint_reports_spl_runtime_errors
  asserted; that test is xfailed until the redesign restores a deliberate
  error contract.
