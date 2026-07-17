Resolved 2026-07-17 by Slice-4 design Amendment A5 and the matching Task-4-Step-2
amendment: the tab-depth scanner is now a two-scene tally/read split, so
`_read()` remains confined to Hecate and Lady Macbeth while the existing tab
entry owns the indentation tally.  The accepted scope reserves
`PASS_LISTS_INDENT_TAB_READ` and five unused `PASS_LISTS_INDENT_*_GUARD`
spares (21 working list labels, five spares), fixes the one-tab sibling versus
two-tab deeper boundary with explicit fast-IR/release contracts, and keeps
Acts III/IV and the list-token grammar frozen.
