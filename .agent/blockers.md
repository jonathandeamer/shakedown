# Active blockers

None. The Task 2L Step 2 blocker (recorded 2026-07-20, three iterations unchanged) is
cleared at plan level by **Amendment A4** in
`docs/superpowers/plans/2026-07-19-spl-pure-release-path.md`.

Next unchecked step: **Task 2L Step 2a** (A4.6 ladder) — apply the A4.2 orientation fix
to `src_ir/act1_ref_pure.py`: delete the `Puck → Horatio → Hecate` triple transfer, move
the trailing-newline policy onto `Puck.stack` where the last glyph is on top, and count
body length in `Hecate.value` during the single `Puck → Hecate` drain.

Success for 2a is `tests/test_act1_references.py` back to **2 passed, 6 failed** with
body text no longer reversed (today it is 8 failed because the body arrives as `arap`).
Keep `USE_ACT1_REF_INTRINSIC = False`. Do not re-enable the Act I intrinsic to reach green.

The prior implementation findings that motivated A4 are preserved verbatim in the git
history at commit 6794d18 and are restated, corrected, and made binding in A4.1–A4.5.
