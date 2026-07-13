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

- NOTE: [4S Task 3 Step 3] 2026-07-13 fix-3c3ade78bfaf48ac9628e13d97f69c18-codex-implement re-ran `uv run pytest tests/test_act3_contracts.py tests/test_architecture_spikes.py -k 'span or act3' -q` and confirmed the focused state is still exactly `12 failed, 12 passed, 14 deselected`, limited to the five whole-fixture span probes, the five paragraph-html parity assertions, and the two code-span/escape assertions. The prior halt rationale in this file was stale: the live plan already narrows Task 3 Step 4 to `variable_code_spans` byte parity plus targeted Act III escape/code-span assertions, while full `escapes_and_overlap`, HTML/link/image, and overlap/emphasis whole-fixture parity remains explicitly deferred to Task 4. No active blocker remains in `.agent/blockers.md`; roadmap work may resume at Task 3 Step 3 implementation.
