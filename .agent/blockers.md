# Active blockers

None. Task 2L Step 2d (candidate capture + drop, commit 719a37e / edf712d)
landed 2026-07-20: body-strip assertions pass for the three target fixtures
(`test_simple_definition_*`, `test_up_to_three_leading_spaces_*`,
`test_defs_plus_paragraph_*`); those tests still fail on the empty Rosalind
table, which is Step 2e's scope, as A4.6 anticipated. No regressions —
verified against the pre-2d commit (bbd2857): the full suite only lost 3
failures, gained none.

Next unchecked step: **Task 2L Step 2e — table build** (`FOLD`/`ENCODE`/`STORE`
per A3.4 + A4.4). Success: `tests/test_act1_references.py` 8 passed, completing
Task 2L Step 2 and unblocking Step 3.
`USE_ACT1_REF_INTRINSIC` remains False.
