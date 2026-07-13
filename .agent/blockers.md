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

- NOTE: [2026-07-13 operator/planner] The twenty consecutive Span Step 5
  (plan 4S) halt records are resolved by Amendment A1 in
  `docs/superpowers/plans/2026-07-12-span-architecture-spike.md`. The
  "ROMEO+JULIET+PUCK in one scene" wall was a design gap, not a compiler
  limit: off-stage value references (verified in `docs/spl/reference.md` and
  implemented in `scripts/splc/lower.py`) let run-length registers live in
  idle characters (HECATE, MACBETH), so every scene stages exactly two
  characters and `validate.py` is untouched. Amendment A1 contains the
  binding register map, the full 30-scene table, and the expanded reserved
  scene-title and recall-key pools. Fix/implement executors may resume
  Task 3 Step 5 against the amended plan. The halt history survives in git
  (commits `8bb31bc`…`7940b24`).
