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

- BLOCK: Spike A remains suspended pending the resumed list plan. The §8.2
  halt of 2026-07-05 (hand-authoring SPL at scale) is resolved: plans 3G-3J
  ported all four acts to the splc IR (`src_ir/` + `src/literary.toml` are
  the authored sources). P1 (tokenized stream + dispatcher skeleton)
  shipped; do not resume list implementation until the P2 list plan is
  written in IR from an interactive planning session (see
  docs/superpowers/plans/plan-roadmap.md).
