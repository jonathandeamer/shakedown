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
Resolved 2026-07-18 by Slice-4 design Amendment A7, implemented exactly as
scoped: `PASS_LISTS_LOOSE_OUTDENT` now carries the `MACBETH == 1` frame-floor
guard already used by `PASS_LISTS_SIB_OUTDENT`/`PASS_LISTS_BSIB_OUTDENT`, and
`PASS_LISTS_LOOSE_OUTDENT_CLOSE` loops back to `PASS_LISTS_LOOSE_OUTDENT`
(via `goto`, not a self-branch, to satisfy the IR's branch-predecessor
stage-pair check) instead of jumping straight to
`PASS_LISTS_LOOSE_OUTDENT_JOIN`. No new working scene, token, participant,
Act-III/IV surface, or `src/literary.toml` entry was added; guards
(`PASS_LISTS_CONTINUE_GUARD`, `PASS_LISTS_INDENT_FOUR_GUARD`) are unchanged.
This clears the reported `PASS_LISTS_CLOSE_ALL` stack underflow: the release
binary now returns 0 on the full `Ordered and unordered lists` fixture
instead of crashing. Regression coverage:
`tests/test_act2_slice4.py::test_full_list_top_level_loose_outdent_leaves_sentinel_for_next_list`
(new, green) plus a minimal delta-debugged repro
(`1.\tx\n\n\ty\n\n# z\n*\tw\n`, six lines, far smaller than the fixture-tail
combination the original blocker named) confirming the underflow's actual
trigger is any depth-1 loose list whose blank-then-same-depth continuation
reaches `PASS_LISTS_LOOSE_OUTDENT` at all — not specifically the ordered
`Multiple paragraphs` + tail-witness combination.

Resolved 2026-07-18 by Slice-4 design Amendment A8 and the matching Task-4-Step-2
amendment: after Act I detabs a source tab, `PASS_LISTS_BLANK_INDENT_4` now
hands the already-read glyph to the existing `PASS_LISTS_INDENT_DEPTH_GUARD`.
That guard is the established sole owner of the one-unit `PUCK` increment for
a four-space indentation group, then reaches the unchanged classifier. The
amendment freezes literal-tab handling, marker routing, tokens, participants,
Acts III/IV, controlled prose, and the 22-working/5-spare list ledger; it
requires red-then-green fast-IR, release, strict-oracle, spike, token-dump,
generated/literary, Amps, and full-suite evidence before any implementation
claim.
