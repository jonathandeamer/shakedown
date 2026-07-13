# Blockers

This file is the operator's in-repo halt switch for the MCO autonomous loop
(`./agent-loop` / `scripts/mco_loop.py`). Any line starting with `- BLOCK:`
halts the loop on the next iteration — the dispatched agent must address it
(or, if it cannot, exit cleanly without modifying code).

The agent itself MAY append `- BLOCK:` lines when it hits a question it
cannot resolve from the roadmap, the active plan, or the canonical docs
(`docs/README.md`); doing so is the only legal way to surface a blocker
mid-run. The operator removes the line when the block is resolved.

Non-blocking notes (no halt) use `- NOTE:` instead.
