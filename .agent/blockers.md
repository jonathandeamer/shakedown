Resolved 2026-07-17 by Slice-4 design Amendment A5 and the matching Task-4-Step-2
amendment: the tab-depth scanner is now a two-scene tally/read split, so
`_read()` remains confined to Hecate and Lady Macbeth while the existing tab
entry owns the indentation tally.  The accepted scope reserves
`PASS_LISTS_INDENT_TAB_READ` and five unused `PASS_LISTS_INDENT_*_GUARD`
spares (21 working list labels, five spares), fixes the one-tab sibling versus
two-tab deeper boundary with explicit fast-IR/release contracts, and keeps
Acts III/IV and the list-token grammar frozen.
Resolved 2026-07-17 by Slice-4 design Amendment A6 and the matching
Task-4-Step-2 amendment: the blank-then-indented-text continuation guards
(`PASS_LISTS_CONTINUE_GUARD`, `PASS_LISTS_INDENT_FOUR_GUARD`) now compare the
scanned indentation tally against the open-frame depth before joining, and
route a shallower indentation through one new working scene,
`PASS_LISTS_LOOSE_OUTDENT`, which closes exactly the exceeded nested frame(s)
with the existing single-level outdent idiom and loops until the depths
match, then falls through to the existing `PASS_LISTS_BLANK_JOIN` route. This
closes only the nested item/list on the fixture-tail witness
(`*\tthis\n\n\t*\tsub\n\n\tthat\n`) and re-enters the still-open parent item
as a loose continuation. The accepted scope adds no token, participant, or
Act-III/IV surface, consumes none of A5's five reserved spares (they already
satisfy the ratio rule for the new 22-scene working ledger), and leaves
`PASS_LISTS_FULL_GUARD`'s HR-collapse path untouched.
