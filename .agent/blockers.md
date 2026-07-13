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

- BLOCK: [4S Task 3 Step 3] 2026-07-13 fix-7f0a5e4921824a90a6885fae7f374a6f-claude-implement independently re-verified the blocker: `scripts/splc/validate.py:42-48` (`participants()`) still hard-requires exactly one non-anchor character per scene, and `docs/superpowers/plans/2026-07-12-span-architecture-spike.md:199` still restricts Task 3 Step 3 to exactly four new scene labels (`LYRIC_BUFFER_OPEN`, `LYRIC_CODE_RUN`, `LYRIC_ESCAPE_GLYPH`, `LYRIC_BUFFER_CLOSE`) plus the four spares already reserved in `src/30-act3-literary.toml`. That budget cannot express the required buffered scan (drain-to-`TEXT_END`, maximal same-length backtick-run matching against a variable-length source buffer, byte-exact unmatched-opener fallback, and escape handling) without additional counting/looping scene machinery — the existing link/reference scanner in `src_ir/act3.py` needed ~50 scenes for comparatively simpler fixed-token matching. This matches the conclusion of at least seven prior independent fix iterations (claude-implement, claude-opus-implement, codex-implement) across 2026-07-12–13. No further re-verification is productive without either additional planning-time scene-title reservations or a revised IR/control-flow design for Task 3 Step 3; this is planner/operator scope, not implementation scope. Loop halts here; no code changed this iteration.
- BLOCK: [4S Task 3 Step 3] Insufficient scene labels for buffered scan implementation; requires additional scene-title reservations or IR/control-flow redesign (see docs/superpowers/plans/2026-07-12-span-architecture-spike.md:199 and scripts/splc/validate.py:42-48).
