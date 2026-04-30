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
