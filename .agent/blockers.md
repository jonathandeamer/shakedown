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

- NOTE: [4S Task 3 Step 3] Reserved additional Act III scene titles and Recall keys for the counting sub-machine in src/30-act3-literary.toml, per the SPL literary protocol. Implementation of the buffered code-span/escape scanner is pending.
- NOTE: [4S Task 3 Step 3] A fresh fix iteration (claude-opus-implement, 2026-07-12) independently verified the BLOCK above and confirms it holds; no code change made. Confirmed: validate.py:42-48 raises unless every scene has exactly one character besides the anchor (two on stage max), so a scene can address at most two registers. Markdown.pl matches code spans with `(`+)(.+?)\1` (equal-length backtick backreference); the embedded-single-backtick probe therefore requires opener-count N, candidate-count M, and the current glyph live at once — three registers — which the two-on-stage rule can only spread across Puck/Romeo/Juliet via multiple titled cross-pair + trampoline scenes (cf. existing LYRIC_OPEN_*/LYRIC_OUTPUT_* pairs in src_ir/act3.py), exceeding the reserved 4 active + 4 spare labels. Both unblock paths are planning-time acts an implementation agent may not take: (a) needs a compact design the plan did not supply and which no design fits the counting case, and (b) is authoring new controlled prose, forbidden by the SPL literary protocol and the plan's "if exhausted, stop." Plan left in flight; operator/planner action required.
- NOTE: [4S Task 3 Step 3] A third fix iteration (claude-implement, 2026-07-12) re-checked `scripts/splc/validate.py:participants` (still exactly two characters on stage per scene) and confirms the BLOCK is unchanged and unresolved by any action available to an implementation agent; no code change made, plan left in flight. An untracked draft plan `docs/superpowers/plans/2026-07-12-mco-quota-preservation-restoration.md` exists in the working tree (unrelated to this blocker, not yet committed or added to the roadmap) — left as-is since it looks like in-progress operator/planner work, not touched by this iteration.
- NOTE: [4S Task 3 Step 3] A fourth fix iteration (nemotron-ultra-implement, 2026-07-12) re-verified the BLOCK by running the full test suite: 12 span-spike tests fail as expected (variable_code_spans, escapes_and_overlap, inline_html_and_autolink, links_images_protected, overlapping_emphasis), 621 tests pass. The literary budget constraint (4 active + 4 spare scene labels vs ~12-16 needed for variable-length backtick counting under the two-characters-per-scene SPL rule) is confirmed. No code changes made; plan remains in flight awaiting operator/planner resolution per the SPL literary protocol.

