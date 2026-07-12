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

- BLOCK: [4S Task 3 Step 3] The buffered code-span/escape scanner cannot be implemented within the plan's reserved Act III literary budget without inventing prose (forbidden by CLAUDE.md + the plan's "if exhausted, stop"). Task 3 reserves only 4 active scene labels (LYRIC_BUFFER_OPEN, LYRIC_CODE_RUN, LYRIC_ESCAPE_GLYPH, LYRIC_BUFFER_CLOSE) plus 4 shared spares, but a correct variable-length backtick matcher needs ~12-16 new scenes. Root cause: scripts/splc/validate.py:participants allows exactly two characters on stage per scene, so the (Puck, Romeo) scan pair exposes only one free register while the `variable_code_spans` probe requires two simultaneous counts (opener run N vs each candidate close run M) to distinguish an embedded single backtick inside a double-backtick span. Comparing N and M forces cross-pair (Puck/Romeo/Juliet) scenes, and in-span content must additionally encode `>` -> `&gt;` (the existing scan encodes only `&`/`<`), each variant a separate (Puck, Juliet) emit scene. tests/test_literary_compliance.py::test_scene_ledger_matches_source_scene_labels + test_scene_titles_have_toml_entries_and_match_source (run in Step 4's gate) fail unless every source scene has a reserved TOML title. To unblock, the operator/planner should either (a) supply the intended compact <=4-scene code-span design, or (b) reserve the additional Act III scene titles + Recall keys the counting sub-machine needs, in src/30-act3-literary.toml, per the SPL literary protocol.

