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

- BLOCK: Span Step 5 exhausts the reserved Task 3 scene pool because generated SPL needs same-stage branch adapter scenes for code comparison and body entity/close emission; IR tests pass, but the byte-exact `variable_code_spans` gate fails with `Juliet is not on stage`, so the active plan needs a literary/scene-capacity amendment before implementation can continue. A prior uncommitted attempt tried two workarounds instead of a planning amendment: (1) inventing new `LYRIC_ADAPTER_*` scene titles outside the plan's approved literary pools (violates the plan's explicit "stop and request a planning amendment instead of inventing prose" rule, and the IR still referenced an undefined `LYRIC_ADAPTER_ENTITY_TO_ORDINARY` scene, so `scripts.splc` crashed); (2) a `scripts/splc/lower.py` goto-speaker-selection change that made splc succeed and kept Acts I/III/IV byte-identical, but altered Act II's stage-direction placement as a side effect, regressing previously-shipped spikes (`echo '* item' | ./shakedown` now raises `SPL runtime error: Juliet is not on stage!`). Neither workaround is safe to land. Both attempts were discarded from the working tree (preserved only in local git stash entries on this machine, not pushed) and HEAD was left at the last known-good commit (`d06727d`, Task 3 Step 4 evidence). Resolving this requires an interactive planning session to either grow the Task 3/4 scene budget or redesign the buffered scanner's same-stage transition shape — not another autonomous fix attempt.
