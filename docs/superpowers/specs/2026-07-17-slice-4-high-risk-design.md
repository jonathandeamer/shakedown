# Slice 4 High-Risk Fixtures — Design

**Date:** 2026-07-17
**Status:** accepted for roadmap row 7 planning
**Authority:** architecture §7.7, §7.8a, §8.1–§8.3; Spike A and Spike B accepted designs.

## Amendment A1 — installed-oracle authority for nested blockquotes (2026-07-17)

The executable used by the repository's strict-parity harness is
`~/markdown/Markdown.pl`, whose version header is currently `1.0.2b8`.
For Slice 4's deterministic strict-parity gates, that executable is the
authority.  A fixture file remains the normalized-mdtest regression corpus;
it is not a competing raw-byte authority when it disagrees with this
executable.  Auto links remains the sole entity-normalized exception.

This resolves the documented one-flag `_DoBlockQuotes` drift: the installed
oracle uses `$bq =~ s/^/  /g;`, without `/m`.  Task 3 must therefore emit its
exact layout: the outer body's first line and the nested opening begin with
two spaces, while the nested paragraph and its close are not additionally
indented.  It must not emit the Markdown 1.0.1 / checked-fixture four-space
inner layout.  The required balanced `BLOCKQUOTE_CLOSE` stream and the
Spike-B list grammar are unchanged.

`tests/test_mdtest.py` keeps its established normalized fixture comparison;
Task 3's focused exact-output contract and the strict parity harness are the
indentation-sensitive acceptance gates.  This is a Slice-4 planning decision,
not authorization to change checked-in fixtures, to invoke Markdown.pl at
runtime, or to weaken strict parity.

## Amendment A2 — activate the allocated header leaf for the full-list gate (2026-07-17)

The `Ordered and unordered lists` input starts with `## Unordered`,
`## Ordered`, and `## Nested`; the strict oracle emits three `<h2>` leaves.
The release binary instead emits `<p>## Unordered</p>` at byte 1.  `HEADER =
2` is already allocated and has an existing `LEAF_BLOCK` role, but it has no
`ARITY` row, Act II does not emit it, and Act IV does not render it.  The
previous list-only Task-4-Step-2 authority therefore cannot satisfy its own
complete-fixture strict-parity gate.

This amendment authorizes the smallest semantic header path needed by that
fixture, as a prerequisite within Task 4 Step 2—not a new plan or a separate
fixture feature.  It activates the existing `HEADER` leaf with one fixed
integer payload (`level`, 1 through 6) followed by a `TEXT_END`-terminated
glyph run.  Its numeric code stays `2`, its role stays `LEAF_BLOCK`, and no
participant or container grammar changes.  `src_ir/tokens.py` and
`docs/spl/token-codes.md` gain the matching `HEADER: TokenArity(1, True)` row;
decoder and structural-validator tests move from their current “not yet
shipped” assertions to positive header coverage.  Act III may only traverse
the new declared arity; it must not rewrite its level or glyphs.

Act II recognizes only top-level ATX headers in the bounded Markdown.pl shape:
one to six leading `#` glyphs, required following space or tab, and non-empty
text through line end; a closing `#` run preceded by whitespace is stripped.
Malformed, indented, or unterminated candidates replay byte-for-byte to the
existing paragraph route.  Setext headers, headers inside containers, and any
broader block-pass generalization are out of scope.  Act IV validates levels
1–6, emits `<h{level}>`, span-processed text, and `</h{level}>` with the
normal block separator, then returns to its existing frame path.

The explicit authority replaces Task 4 Step 2's former blanket
arity-unchanged rule only for this existing allocated leaf.  It does not
authorize a new token, renumbering, structural-role change, arbitrary header
syntax, or fixture-specific output path.  The `LIST_OPEN(kind)`,
`LIST_ITEM(looseness)`, `ITEM_CLOSE`, and `LIST_CLOSE` grammar remains frozen;
all Spike-A/B stream expectations remain immutable.  Any need beyond this
bounded header leaf remains `BLOCK[plan]`.

## Amendment A3 — reserve the final-blank tight-list rollback (2026-07-17)

Task 4 Step 2 has consumed the original three Act-II list spares
(`PASS_LISTS_INDENT_GUARD`, `PASS_LISTS_NEST_GUARD`, and
`PASS_LISTS_FULL_GUARD`) while completing the multi-level blank-line route.
The remaining fixture-tail defect is narrower: after a blank line, Act II
must not leave the final nested tab-delimited item marked loose when that
blank ends the entire list.  The token grammar, all token numbers and roles,
participants, Act III traversal, and Act-IV rendering remain frozen.

This amendment authorizes an Act-II-only provisional-looseness transaction:
stage the item's prior tight payload and list-frame state when the blank is
seen; commit the loose classification only when a real continuation or sibling
is accepted; and, at EOF/list termination, restore the staged tight payload
before emitting the existing explicit `TEXT_END`, `ITEM_CLOSE`, and
`LIST_CLOSE` sequence.  The rollback must requeue every staged glyph in source
order and must not synthesize a paragraph, `HR`, token, or Act-IV special case.
The existing `PASS_LISTS_*` close routes own final frame closure.

The following five labels are the derived working ledger for that transaction:

| Label | State transition |
|---|---|
| `PASS_LISTS_LOOSE_PROVISION` | Stage the prior item payload and frame state when a blank first makes looseness possible. |
| `PASS_LISTS_LOOSE_COMMIT` | Commit the staged loose state only after an accepted indented continuation or sibling marker. |
| `PASS_LISTS_LOOSE_EOF` | Detect that the provisional blank reaches EOF or the terminating list boundary. |
| `PASS_LISTS_LOOSE_ROLLBACK` | Restore the staged tight payload before the existing explicit close sequence. |
| `PASS_LISTS_LOOSE_REPLAY` | Requeue the saved boundary glyphs in source order and re-enter the existing list-close route. |

Act II's list ledger is consequently 18 working scenes (the original ten,
the three previously spare guards now in use, and these five) and four fresh
spares.  Four is both the required minimum and more than 20% of the 18-scene
working pool.  No Act-IV surface is added because the rollback preserves the
existing explicit grammar before Act IV receives it.  Any need for an
additional state beyond the five working labels or four spares is again
`BLOCK[plan]`.

## Amendment A4 — separate accepted nested-after-blank from provisional rollback (2026-07-17)

The A3 transaction correctly protects a list-ending blank, but its five-state
ledger conflates two different accepted post-blank paths: an indented
continuation that becomes paragraph text and an indented nested-list marker.
The latter must retain its marker while the former enters the existing
`PASS_LISTS_BLANK_JOIN` route.  Routing both through the continuation route
turns the nested marker into paragraph glyphs (for example, `*   sub`).  This
is an Act-II dispatch distinction; it does not require a token, a grammar
change, a participant, an Act-III traversal change, or an Act-IV branch.

This amendment replaces A3's five-label transaction ledger with the following
six-label ledger.  It explicitly reuses the shipped routes named in the last
column; those routes are not new controlled surfaces and are not counted as
working labels.

| Label | State transition | Existing destination retained |
|---|---|---|
| `PASS_LISTS_LOOSE_PROVISION` | On the first blank after an open item, stage its prior tight payload, frame state, and consumed boundary glyphs without yet changing `LIST_ITEM` looseness. | `PASS_LISTS_BLANK*` scanner |
| `PASS_LISTS_LOOSE_COMMIT` | After a validated ordinary indented continuation or sibling, commit the staged loose item and dispatch to the already-owned continuation or sibling route. | `PASS_LISTS_BLANK_JOIN` or `PASS_LISTS_BSIB_EMIT` |
| `PASS_LISTS_LOOSE_NESTED` | After an indented unordered/ordered marker and its required separator are validated, commit the staged loose item, preserve the marker in `PUCK`, and re-enter the existing nested-marker open path. | `PASS_LISTS_NEST_EMIT_UL` or `PASS_LISTS_NEST_EMIT_OL` |
| `PASS_LISTS_LOOSE_EOF` | On EOF or a rejected/list-terminating candidate before either accepted path, select rollback. | `PASS_LISTS_LOOSE_ROLLBACK` |
| `PASS_LISTS_LOOSE_ROLLBACK` | Restore the staged tight payload and frame state before the existing explicit close sequence. | `PASS_LISTS_LOOSE_REPLAY` |
| `PASS_LISTS_LOOSE_REPLAY` | Requeue the saved boundary glyphs in source order, then re-enter the existing list-close route. | `PASS_LISTS_LIST_END_REPLAY` |

`PASS_LISTS_LOOSE_NESTED` is the sole additional controlled Act-II scene
authorized by this amendment.  The A3 four-label `*_GUARD` pool remains
unused and remains the sole spare pool.  The list ledger is therefore 19
working scenes and four spares; four is `ceil(19 * 20%)` and also meets the
four-title minimum.  Add the ready-to-paste title below to
`src/20-act2-literary.toml` in the same checkpoint that introduces the IR
scene.  No other new controlled prose is authorized.

```toml
# Amendment A4 nested-after-blank working label
[scenes.PASS_LISTS_LOOSE_NESTED]
title = "Lady Macbeth turns the waiting rank within its ordered host."
pattern = "scene_of_character"
```

Required focused evidence extends Task 4 Step 2 with these three disjoint
Act-II/release contracts, in addition to its existing fixture and regression
gates:

1. `* parent\n\n\t* sub\n` yields an outer loose item containing a nested
   tight unordered list, never a paragraph whose text begins `*   sub`.
2. `* parent\n\n* sibling\n` yields two loose sibling items and does not enter
   `PASS_LISTS_LOOSE_NESTED`.
3. `* parent\n\n` yields a tight single item (no `<p>` wrapper), restores the
   staged payload before `ITEM_CLOSE`/`LIST_CLOSE`, and never enters either
   accepted commit path.

The six existing List Spike-A fixtures and four nested-block Spike-B fixtures
remain immutable stream and byte boundaries.  Any need for a seventh
transaction state, a fifth spare, a change to the listed existing
destinations, or an Act-III/IV/list-token modification is `BLOCK[plan]`.

## Amendment A5 — split tab-depth tally from glyph reads (2026-07-17)

The remaining full-list defect is a depth-boundary distinction in Act II, not
a new Markdown construct: `1. a\n\t* b\n\t* c\n` keeps `b` and `c` as
sibling items of one nested unordered list, while
`* a\n\t* b\n\t\t* c\n` opens a further nested list for `c`.  The existing
tab route needs to retain an indentation-unit tally while it reads the next
glyph.  `_read()` already owns Hecate's pop and Lady Macbeth's input-countdown
write, so splc's two-participant rule forbids updating the tally register in
that same scene.

This amendment authorizes exactly a two-scene Act-II helper split.  The
existing tab entry performs only the tally update and then enters
`PASS_LISTS_INDENT_TAB_READ`; that new scene performs only `_read()`, loops
back through the tally entry for each following tab, and dispatches the first
non-tab glyph to the existing four-unit classifier.  The tally is reset at
each line boundary before its first tab and is compared with the current
open-list depth before any marker-save route overwrites `PUCK`.  Equal
effective indentation selects the existing sibling-item route; a strictly
deeper indentation selects the existing nested-open route.  Rejected markers
retain the current byte-for-byte replay behavior.  The split changes neither
the input carrier nor the existing `LIST_OPEN`, `LIST_ITEM`, `ITEM_CLOSE`, or
`LIST_CLOSE` grammar; it adds no participant, Act III work, Act IV branch, or
token change.

The A4 four guards are now consumed by the already-started list work.  The
list ledger is therefore 21 working labels (A4's 19 plus the two helper
states) and five fresh spares: `ceil(21 * 20%) = 5`, which also exceeds the
four-title floor.  The following is the complete ready-to-paste A5 pool; add
the working entry only with its IR scene, and leave every `*_GUARD` entry
unused unless a later plan amendment assigns it.

```toml
# Amendment A5 tab-depth helper and Act-II spare pool
[scenes.PASS_LISTS_INDENT_TAB_READ]
title = "Lady Macbeth reads beyond the measured marching step."
pattern = "scene_of_character"

[scenes.PASS_LISTS_INDENT_TAB_GUARD]
title = "The measured step keeps one guarded return."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_DEPTH_GUARD]
title = "The inward tally keeps one guarded border."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_SIBLING_GUARD]
title = "The equal rank keeps one guarded march."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_DEEP_GUARD]
title = "The deeper rank keeps one guarded descent."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_REPLAY_GUARD]
title = "The false step keeps its guarded return."
pattern = "bare_statement"
```

Task 4 Step 2 must add red-then-green focused fast-IR and release contracts
for both witness inputs above.  The first must contain one nested unordered
list with two sibling items and must not emit a second nested `LIST_OPEN`; the
second must contain a second nested `LIST_OPEN` for `c`.  Both release outputs
must be strict Markdown.pl bytes.  Run the existing full-list, Spike-A/B,
generated-fragment, parser, validator, literary, Amps, and strict-parity gates
named in the active plan.  Any need for a third helper scene, a sixth spare,
a different register ownership, an Act-III/IV change, or a token/grammar
change is `BLOCK[plan]`.

## Amendment A6 — close only the exceeded nested depth on a blank-then-ancestor-indent continuation (2026-07-17)

Task 4 Step 2's remaining defect is the fixture-tail case
`*\tthis\n\n\t*\tsub\n\n\tthat\n`: after the nested item `sub` and a blank
line, `that` is indented to exactly the *outer* item's content depth, not the
nested item's.  Neither existing post-blank route fits.  The plain-text
continuation guards (`PASS_LISTS_CONTINUE_GUARD` for space indentation and
`PASS_LISTS_INDENT_FOUR_GUARD` for tab indentation) commit the provisional
loose item and rejoin `PASS_LISTS_BLANK_JOIN` without ever comparing the
scanned indentation tally (`PUCK`) against the open-frame depth (`MACBETH`);
they always attach the continuation to whichever item is currently innermost.
That mislabels the still-open nested list/item as loose and keeps it open.
The marker-driven blank-sibling guards (`PASS_LISTS_INDENT_GUARD` /
`PASS_LISTS_NEST_GUARD` / `PASS_LISTS_FULL_GUARD`) are the only existing
routes that close a frame after a blank, but they exist for a rejected
marker candidate and close every open frame down to zero via
`PASS_LISTS_FULL_GUARD`'s HR-collapse path — the wrong shape for landing on
one specific open ancestor.

This amendment authorizes exactly one new Act-II working scene,
`PASS_LISTS_LOOSE_OUTDENT`, plus a comparison this amendment adds to the two
existing continuation guards named above.  It adds no token, no participant,
no Act-III/IV change, and no change to `LIST_OPEN`, `LIST_ITEM`,
`ITEM_CLOSE`, or `LIST_CLOSE` semantics — it only sequences the existing
close primitive across more than one frame before handing off to the
existing join.

- `PASS_LISTS_CONTINUE_GUARD` and `PASS_LISTS_INDENT_FOUR_GUARD` gain one
  additional comparison, evaluated before their current `HORATIO < 0`
  provisional check: if the scanned indentation tally (`PUCK`) is less than
  the open-frame depth (`MACBETH`), route to `PASS_LISTS_LOOSE_OUTDENT`
  instead of `PASS_LISTS_BLANK_JOIN`. The existing `HORATIO < 0` branch and
  its non-provisional fallthrough are otherwise unchanged, and the equal-depth
  case (`PUCK == MACBETH`) keeps its current behavior exactly.
- `PASS_LISTS_LOOSE_OUTDENT` closes exactly one open frame using the same
  `TEXT_END` / `ITEM_CLOSE` / `LIST_CLOSE` emission idiom already used by
  `PASS_LISTS_SIB_OUTDENT` and `PASS_LISTS_BSIB_OUTDENT`, decrements
  `MACBETH` by one frame, and loops back to itself while `PUCK` remains less
  than `MACBETH`. When `PUCK` reaches parity with `MACBETH`, it falls
  through to the existing `PASS_LISTS_BLANK_JOIN` route, which then commits
  the loose continuation paragraph onto the now-current ancestor item exactly
  as it already does for a same-depth continuation. No new close-sequence
  shape, HR emission, or full-list collapse is authorized; `PASS_LISTS_FULL_GUARD`
  and its HR path are untouched and remain reserved for the rejected-marker
  case they already own.

Required focused evidence extends Task 4 Step 2 with:

1. `*\tthis\n\n\t*\tsub\n\n\tthat\n` (the fixture-tail witness): `sub`'s
   nested list closes exactly once, `this` remains open and becomes loose,
   `that` joins `this`'s text as a second paragraph, and the release output
   is strict Markdown.pl bytes.
2. A two-level variant such as `1. a\n\t* b\n\t\t* c\n\n1. a\n` reduced to its
   blank-then-return shape, confirming the loop closes more than one frame
   when the fixture requires it and stops exactly at the matching ancestor
   depth.
3. The three Amendment A4 contracts and the two Amendment A5 contracts remain
   green unchanged, proving the new comparison does not alter the equal-depth
   or deeper-depth paths.

Act II's list ledger gains this one new working scene: 22 working labels
(A5's 21 plus `PASS_LISTS_LOOSE_OUTDENT`). The five `PASS_LISTS_INDENT_*_GUARD`
spares reserved by A5 remain unused and are not consumed by this amendment;
they already satisfy `ceil(22 * 20%) = 5` for the new working count, so no
further spare is reserved here. Add the ready-to-paste title below to
`src/20-act2-literary.toml` in the same checkpoint that introduces the scene.

```toml
# Amendment A6 blank-then-ancestor-indent outdent
[scenes.PASS_LISTS_LOOSE_OUTDENT]
title = "The nested troop yields its ground to the waiting captain."
pattern = "bare_statement"
```

Any need for a second new working scene, a change to `PASS_LISTS_FULL_GUARD`'s
HR-collapse path, an Act-III/IV change, a token/grammar change, or consumption
of an A5 spare beyond this amendment's scope is `BLOCK[plan]`.

## Amendment A7 — make the loose outdent loop to the ancestor and never pop the frame sentinel (2026-07-18)

Task 4 Step 2's remaining blocker is a Macbeth frame-stack underflow inside
`PASS_LISTS_CLOSE_ALL` that appears only when the ordered-list `Multiple
paragraphs` subsection precedes the fixture-tail witness
(`*\tthis\n\n\t*\tsub\n\n\tthat\n`). Each fragment passes alone; the combined
suffix underflows. Static inspection of the shipped Act-II source
(`src_ir/act2.py`) locates two divergences between the A6 authorization and the
A6 implementation, both inside the loose-outdent cluster and both fixable
without any new budget:

1. **The close does not loop.** A6 authorized `PASS_LISTS_LOOSE_OUTDENT` to
   close one frame, decrement `MACBETH`, and "loop back to itself while `PUCK`
   remains less than `MACBETH`," stopping at parity. The shipped code instead
   routes `PASS_LISTS_LOOSE_OUTDENT` → `PASS_LISTS_LOOSE_OUTDENT_CLOSE` →
   `PASS_LISTS_LOOSE_OUTDENT_JOIN`, and `_CLOSE` jumps to `_JOIN` after closing
   exactly one frame. It never re-tests `PUCK` against `MACBETH`, so a
   continuation that must cross more than one open frame closes only the
   innermost one and leaves the surplus frames open.
2. **The close has no frame-sentinel floor.** `PASS_LISTS_SIB_OUTDENT` and
   `PASS_LISTS_BSIB_OUTDENT` are both reached only under `MACBETH > 1`, so their
   `pop(MACBETH)` + `let(MACBETH, MACBETH - 1)` idiom can never disturb the
   `_END` sentinel that seats the bottom of Macbeth's open-frame stack.
   `PASS_LISTS_LOOSE_OUTDENT` fires on the bare test `PUCK < MACBETH` with no
   `MACBETH > 1` floor. When the ordered `Multiple paragraphs` subsection has
   already unwound the frame depth to its floor and a following loose outdent
   fires there, `_CLOSE` pops and overwrites the `_END` sentinel, so the later
   `PASS_LISTS_CLOSE_ALL` walk never sees `_END` and pops past the bottom of the
   stack — the reported underflow.

This amendment authorizes correcting the **existing** loose-outdent cluster
(`PASS_LISTS_LOOSE_OUTDENT`, `PASS_LISTS_LOOSE_OUTDENT_CLOSE`,
`PASS_LISTS_LOOSE_OUTDENT_JOIN`) to honor A6's already-reserved
loop-and-floor semantics:

- After `_CLOSE` closes one frame and decrements `MACBETH`, it re-enters
  `PASS_LISTS_LOOSE_OUTDENT` (the loop A6 authorized) rather than jumping
  straight to the join. `PASS_LISTS_LOOSE_OUTDENT` continues to route to
  `PASS_LISTS_LOOSE_OUTDENT_CLOSE` while `PUCK < MACBETH` and falls through to
  `PASS_LISTS_LOOSE_OUTDENT_JOIN` → `PASS_LISTS_BLANK_JOIN` at parity, exactly
  as A6 specified.
- `PASS_LISTS_LOOSE_OUTDENT` gains the same frame-floor discipline that already
  guards `PASS_LISTS_SIB_OUTDENT` and `PASS_LISTS_BSIB_OUTDENT`: it closes a
  frame only while the open-frame depth is above the floor, so the loop can
  never pop or overwrite Macbeth's `_END` sentinel. At the floor it hands off to
  the existing join without a further close. The single-source of the open-frame
  depth (`MACBETH`) is preserved; no `let(MACBETH, ...)` may write over the
  sentinel.

This is a control-flow and guard correction of scenes that already exist. It
adds **no** new working scene, token, participant, structural role, Act-III/IV
surface, or `src/literary.toml` entry, and it consumes **none** of A5's five
reserved `PASS_LISTS_INDENT_*_GUARD` spares. Because no scene is added, the
22-working / 5-spare ledger from A6 is unchanged and no controlled prose is
reserved here. `PASS_LISTS_FULL_GUARD`'s HR-collapse path stays untouched.

Required focused evidence extends Task 4 Step 2 with:

1. A red-then-green fast-IR **and** release contract for the combined repro —
   the ordered `Multiple paragraphs` subsection immediately followed by the
   fixture-tail witness — that reproduces the `PASS_LISTS_CLOSE_ALL` underflow
   before the fix and produces strict Markdown.pl bytes after it.
2. A frame-floor assertion in `tests/test_act2_frame_floors.py` proving Macbeth's
   `_END` sentinel survives a loose outdent that unwinds to the floor.
3. The three Amendment A4 contracts, the two Amendment A5 contracts, and the two
   Amendment A6 contracts remain green unchanged, proving the loop and floor
   guard do not alter the single-level or equal-depth paths.

Stopping condition unchanged: if, after this reserved-scope correction, the full
`Ordered and unordered lists` fixture still cannot validate under the frozen
grammar without a new token, participant, working scene, structural role,
Act-III/IV change, or compiler/validator change, that is an architecture halt —
record it as `BLOCK[plan]` with the exact operator decision required and stop,
per the A6 escape clause. Do not add budget locally.

## Amendment A8 — count detabbed blank-line indentation through the existing depth guard (2026-07-18)

A7 removes the frame-stack crash but exposes the remaining output defect in
the full-list fixture: Act I detabs every source tab before Act II receives it.
Consequently, a blank-then-tab-indented continuation such as
`1.\tx\n\n\ty\n` enters `PASS_LISTS_BLANK_INDENT_1` through
`PASS_LISTS_BLANK_INDENT_4` as four literal spaces.  The ordinary indented-line
path already represents each four-space group as one list-depth unit: after
its fourth-space scan it enters `PASS_LISTS_INDENT_DEPTH_GUARD`, which alone
increments `PUCK` and then reuses `PASS_LISTS_INDENT_CLASSIFY_FOUR`.  The
blank-line path currently bypasses that existing guard, leaving `PUCK == 0`
where the open depth is `MACBETH == 1`; A6's `PUCK < MACBETH` test then
mistakes a same-depth continuation for an outdent.

This amendment authorizes one existing-scene handoff only.  After
`PASS_LISTS_BLANK_INDENT_4` has read the glyph following the fourth leading
space, it must enter the existing `PASS_LISTS_INDENT_DEPTH_GUARD` rather than
directly entering `PASS_LISTS_INDENT_CLASSIFY_FOUR`.  The existing guard adds
exactly one to `PUCK`, preserves the already-read glyph in Hecate, and reaches
the unchanged classifier.  Repeated four-space groups retain the existing
classifier loop and therefore add one unit per group.  Literal-tab input keeps
the A5 `PASS_LISTS_INDENT_TAB` / `PASS_LISTS_INDENT_TAB_READ` route unchanged.

The handoff is deliberately shared with the existing marker classifier: after
the depth increment, `PASS_LISTS_INDENT_FOUR_ROUTE_UL` and
`PASS_LISTS_INDENT_ORDERED_FOUR` continue to distinguish an equal-depth
sibling from a strictly deeper nested marker using their existing `PUCK` versus
`MACBETH` comparison.  No new scene, token, participant, structural role,
frame representation, Act III/IV branch, compiler/validator change, TOML
surface, or A5 spare is authorized.  The list ledger remains 22 working labels
and five reserved spares.

Task 4 Step 2 must first add red contracts, then make them green, for all of
the following:

1. Fast IR and release output for `1.\tx\n\n\ty\n` must retain one ordered
   list/item with two paragraph leaves and exactly match the local
   Markdown.pl bytes:
   `<ol>\n<li><p>x</p>\n\n<p>y</p></li>\n</ol>\n`.
2. The corresponding unordered witness `*\ta\n\n\tb\n` must have one loose
   item with two paragraphs and strict Markdown.pl bytes, proving the fix is
   not ordered-marker-specific.
3. `1.\ta\n\n\t* b\n` must retain its existing loose outer ordered item and
   nested tight unordered list, proving that the shared post-four-space
   classifier still selects the established marker route.
4. The A4/A5/A6/A7 focused contracts, all six Spike-A list cases, all four
   Spike-B nested-block cases, `loose_second_paragraph`, and
   `nested_one_level` interpreter/token-dump baselines remain unchanged; the
   full fixture's fast-IR, release-binary, strict-parity, generated-fragment,
   parser, validator, literary, Amps, and full-suite gates must pass.

If this one-handoff correction needs any further scene, a different register
owner, changed marker routing, token/grammar change, Act-III/IV work, or a
new controlled surface, record `- BLOCK[plan]:` with that exact need and stop.

## Amendment A9 — stage-pair-safe loose commit after a nested list (2026-07-18)

The remaining full-list failures divide across two distinct Act-II stage
pairs.  A top-level blank continuation, such as `1.\tItem 1\n\n\tItem 2\n`,
arrives through the established Horatio-stage provisional-looseness route and
must rewrite its current item to loose before opening the second paragraph.
By contrast, a blank-separated outer sibling after a nested list, such as
`2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\n3. Third\n`, arrives while Hecate
still owns the scanned marker and has a completed tight nested tail above the
outer item.  Sending both arrivals to `PASS_LISTS_LOOSE_COMMIT` gives that
scene inconsistent branch predecessor pairs; sending the latter through the
ordinary outdent/sibling route either rewrites `Foe` loose or produces an
unbalanced Act-IV close sequence.

This amendment authorizes exactly one Act-II working scene,
`PASS_LISTS_LOOSE_COMMIT_HECATE`.  It is an adapter, not a new grammar rule:

1. Only from the recognized blank-separated nested-to-outer-sibling branch,
   it emits the completed nested tail's existing `TEXT_END`, `ITEM_CLOSE`,
   `LIST_CLOSE` sequence and decrements the frame depth once.  It does not
   touch the outer item's payload and never loops.
2. With the outer `LIST_ITEM` now exposed, it stores `_LOOSE_COMMIT_SIB` in
   `HORATIO` and enters the existing `PASS_CONTAINERS_OPEN` transaction.  That
   transaction is therefore permitted to rewrite **only the outer item** to
   loose; it must not encounter or rewrite `Foe`.
3. Its existing `PASS_CONTAINERS_CLOSE_BRANCH` exit reaches the existing
   Horatio-stage `PASS_LISTS_LOOSE_COMMIT`, then `PASS_LISTS_BSIB_EMIT`.  That
   owned path closes the exposed outer item and opens the outer loose sibling.

The ordinary blank-continuation path remains
`PASS_LISTS_BLANK_JOIN` → `PASS_LISTS_LOOSE_JOIN` →
`PASS_CONTAINERS_OPEN`; it must never enter the new adapter.  Conversely, the
Hecate-stage predecessor must never branch directly to
`PASS_LISTS_LOOSE_COMMIT`, and the nested-to-outer sibling must not reuse
`PASS_LISTS_LOOSE_OUTDENT`.  These restrictions make every branch target have
one compatible predecessor-stage pair and preserve the existing explicit
`ITEM_CLOSE`/`LIST_CLOSE` ownership.

The amendment adds the working title below and retains A5's five unused
`PASS_LISTS_INDENT_*_GUARD` spares.  The live list ledger becomes 23 working
scenes and five unused spares, satisfying `ceil(23 * 20%) = 5` and the
four-title minimum.  No token, token number, structural role, participant,
container grammar, Act III or IV surface, compiler/validator behavior, or A5
spare is authorized.

```toml
# Amendment A9 Hecate-stage loose-commit adapter
[scenes.PASS_LISTS_LOOSE_COMMIT_HECATE]
title = "Hecate yields the inner rank to its elder march."
pattern = "scene_of_character"
```

Task 4 Step 2 must first make, then satisfy, these exact contracts in both the
fast interpreter and release binary:

1. `1.\tItem 1\n\n\tItem 2\n` has one loose ordered item and two paragraph
   leaves, proving the existing Horatio-stage continuation remains intact.
2. `2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\n3. Third\n` has a loose outer
   `Second:` item, a tight nested list with tight `Fee`, `Fie`, and `Foe`
   items, and a loose outer `Third` sibling.  It must be byte-identical to the
   local oracle:

   ```html
   <ol>
   <li><p>Second:</p>

   <ul><li>Fee</li>
   <li>Fie</li>
   <li>Foe</li></ul></li>
   <li><p>Third</p></li>
   </ol>
   ```

All A4–A8 witnesses, the six Spike-A list fixtures, four Spike-B
nested-block fixtures, list token-dump baselines, generated-fragment/parser/
validator/literary gates, and the Amps proof remain required.  A need to
close more than one nested frame, rewrite any nested tail, add another working
scene, consume another spare, alter Acts III/IV, or change a token/grammar is
`BLOCK[plan]` with the exact need recorded; stop rather than locally widening
this adapter.

## Decision

Slice 4 extends the existing four-act IR parser and its explicit token grammar;
it does not add a parser, an oracle fallback, a token code, or an on-stage
participant.  Act II remains the owner of block recognition and balanced
container-token production, Act III copies structural and `RAW_HTML_HASH`
leaves unchanged, and Act IV renders containers from Prospero's existing frame
stack.

The work is sequenced by interaction risk:

1. Advanced HTML widens the existing left-margin raw-HTML recognizer from its
   simple `div` shape to the fixture's attributed and nested `div` blocks.  A
   `RAW_HTML_HASH` leaf contains the original block bytes, excluding only the
   block-delimiting blank boundary; Act IV emits it without paragraph wrapping.
2. Nested blockquotes make Act II emit one balanced `BLOCKQUOTE_OPEN` /
   `BLOCKQUOTE_CLOSE` pair per marker depth.  Blank quoted lines remain within
   their current depth and an outdented line closes exactly the required quote
   frames.  Act IV reproduces the installed-oracle layout fixed by Amendment
   A1 while preserving one frame per token nesting.
3. Full lists lift the Spike-A narrowings: multi-digit ordered markers,
   top-level indentation up to three spaces, tab/space marker separation,
   arbitrary fixture-required nesting, loose multi-paragraph items, and the
   documented Markdown-1.0.1 oddity at the fixture tail.  The existing
   `LIST_OPEN`, `LIST_ITEM`, `ITEM_CLOSE`, and `LIST_CLOSE` grammar remains
   the sole cross-act representation.

## Invariants and stopping conditions

- The three named fixtures must be strict byte-identical to a fresh local
  `Markdown.pl` run.  Unlike Auto links, none has a normalization exception.
- Existing fixture expected files stay unchanged; `tests/test_mdtest.py`
  enablement occurs only after a fixture's focused strict-parity proof.
- The six list and four nested-block spike fixtures remain oracle-byte-exact;
  their reviewed stream grammar is a regression boundary, not an optional
  example.
- Raw HTML handling remains Markdown.pl v1.0.1's fixed block-tag/boundary
  surface, not a general HTML parser.  The Slice-4 fixture requires `div`
  only; a need for a new tag family is a `BLOCK[plan]` unless an oracle probe
  proves that it is needed by the fixture.
- A need for a new token, third participant, a changed structural grammar,
  unreserved prose, or a non-reproducible binary/IR divergence is a
  `BLOCK[plan]`.  A full-list fixture stream that cannot be rendered by the
  Spike-B grammar is an architecture §8.2 halt, not a local workaround.

## Interfaces

| Boundary | Contract |
|---|---|
| Act II → III | `PARA`, activated `HEADER(level, text)`, `HR`, `LIST_OPEN`, `LIST_ITEM`, `ITEM_CLOSE`, `LIST_CLOSE`, `BLOCKQUOTE_OPEN`, `BLOCKQUOTE_CLOSE`, `CODE_BLOCK`, and `RAW_HTML_HASH` cross the boundary. Amendment A2 adds only the pre-allocated `HEADER` arity row; every other token arity remains unchanged. |
| Act III → IV | Structural codes and `RAW_HTML_HASH` payload bytes pass through unchanged; span processing is restricted to text-bearing Markdown leaves. |
| Act IV | Prospero's frame stack is balanced for every container token; nested quote output follows Amendment A1's installed-oracle indentation layout, and list item ownership remains explicit through `ITEM_CLOSE`. |
| Tests | Fast IR tests expose streams and HTML; mdtest runs fast IR and release `./shakedown`; `scripts/strict_parity_harness.py` is the implementation parity authority. |

## Fixture-derived acceptance inventory

| Fixture | Required cases |
|---|---|
| Inline HTML (Advanced) | one-line `div`; three-level nested `div`; `style=\">\"`; indented attributed inner `div`; blank-boundary preservation; final attributed nested pair. |
| Nested blockquotes | outer paragraph, quoted blank lines, a second-depth quote, return to outer depth, matched closures, and Amendment A1's installed-oracle indentation layout. |
| Ordered and unordered lists | `*`/`+`/`-`; ordered tab and space separators; loose/tight distinction; multiple paragraphs; three-level nesting; ordered-to-unordered nesting; loose nested list; and the fixture's final Markdown-1.0.1 oddity. |

## Literary reservation

The implementation must reuse existing `PASS_LISTS_*`, `PASS_QUOTE_*`,
`SCRIBE_LIST_*`, and `SCRIBE_BLOCKQUOTE_*` surfaces wherever their current
meaning remains exact.  The following is the complete new controlled pool.
Its working count is derived from the scene ledger below: Act II has 31
working scenes and 6 spares; Act IV has 16 working scenes and 4 spares.  This
meets the required at-least-20%-and-four spare rule.  Add Act-II entries to
`src/20-act2-literary.toml` and Act-IV entries to
`src/40-act4-literary.toml` in the same checkpoint that first introduces the
label.

| Act | Family | Working labels | Spare labels |
|---|---|---|---|
| II | HTML 6; quote 6; list 19 | `PASS_HTML_BLOCK_OPEN`, `PASS_HTML_BLOCK_NAME`, `PASS_HTML_BLOCK_ATTR`, `PASS_HTML_BLOCK_DEPTH_OPEN`, `PASS_HTML_BLOCK_DEPTH_CLOSE`, `PASS_HTML_BLOCK_FINISH`; `PASS_QUOTE_NEST_OPEN`, `PASS_QUOTE_NEST_CLOSE`, `PASS_QUOTE_NEST_DEPTH`, `PASS_QUOTE_NEST_BLANK`, `PASS_QUOTE_NEST_REPLAY`, `PASS_QUOTE_NEST_FINISH`; `PASS_LISTS_INDENT_ONE`, `PASS_LISTS_INDENT_TWO`, `PASS_LISTS_INDENT_THREE`, `PASS_LISTS_MARKER_DIGIT`, `PASS_LISTS_MARKER_DOT`, `PASS_LISTS_CONTINUE`, `PASS_LISTS_NEST_OPEN`, `PASS_LISTS_NEST_CLOSE`, `PASS_LISTS_LOOSE`, `PASS_LISTS_FULL_FINISH`, `PASS_LISTS_INDENT_GUARD`, `PASS_LISTS_NEST_GUARD`, `PASS_LISTS_FULL_GUARD`, `PASS_LISTS_LOOSE_PROVISION`, `PASS_LISTS_LOOSE_COMMIT`, `PASS_LISTS_LOOSE_NESTED`, `PASS_LISTS_LOOSE_EOF`, `PASS_LISTS_LOOSE_ROLLBACK`, `PASS_LISTS_LOOSE_REPLAY` | `PASS_HTML_BLOCK_GUARD`, `PASS_QUOTE_NEST_GUARD`, `PASS_LISTS_LOOSE_GUARD`, `PASS_LISTS_LOOSE_EOF_GUARD`, `PASS_LISTS_LOOSE_ROLLBACK_GUARD`, `PASS_LISTS_LOOSE_REPLAY_GUARD` |
| IV | HTML 3; quote 5; list 8 | `SCRIBE_RAW_HTML_ADVANCED`, `SCRIBE_RAW_HTML_ADVANCED_SEP`, `SCRIBE_RAW_HTML_ADVANCED_CLOSE`; `SCRIBE_QUOTE_NEST_OPEN`, `SCRIBE_QUOTE_NEST_CLOSE`, `SCRIBE_QUOTE_NEST_INDENT`, `SCRIBE_QUOTE_NEST_RETURN`, `SCRIBE_QUOTE_NEST_FINISH`; `SCRIBE_LIST_DEPTH_OPEN`, `SCRIBE_LIST_DEPTH_CLOSE`, `SCRIBE_LIST_LOOSE_BEGIN`, `SCRIBE_LIST_LOOSE_CLOSE`, `SCRIBE_LIST_NEST_RETURN`, `SCRIBE_LIST_ITEM_PARAGRAPH`, `SCRIBE_LIST_ITEM_CLOSE_FINAL`, `SCRIBE_LIST_FULL_FINISH` | `SCRIBE_RAW_HTML_ADVANCED_GUARD`, `SCRIBE_QUOTE_NEST_GUARD`, `SCRIBE_LIST_DEPTH_GUARD`, `SCRIBE_LIST_FULL_GUARD` |

```toml
[scenes.PASS_HTML_BLOCK_OPEN]
title = "Lady Macbeth opens the court's unbroken wall."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_NAME]
title = "Macbeth names the wall's guarded stone."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_ATTR]
title = "Lady Macbeth keeps the wall's private sign."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_DEPTH_OPEN]
title = "Macbeth enters the wall's inward chamber."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_DEPTH_CLOSE]
title = "The inward chamber yields its settled wall."
pattern = "bare_statement"
[scenes.PASS_HTML_BLOCK_FINISH]
title = "Lady Macbeth releases the courtly wall."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_GUARD]
title = "The courtly wall keeps one sure threshold."
pattern = "bare_statement"

[scenes.PASS_QUOTE_NEST_OPEN]
title = "Lady Macbeth opens the echo within the echo."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_CLOSE]
title = "Macbeth closes the echo's inner chamber."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_DEPTH]
title = "Lady Macbeth counts the echo's shadowed rooms."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_BLANK]
title = "The echo keeps its measured silent room."
pattern = "bare_statement"
[scenes.PASS_QUOTE_NEST_REPLAY]
title = "Macbeth restores the echo's outer word."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_FINISH]
title = "Lady Macbeth frees the finished echo."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_GUARD]
title = "The echo keeps one guarded return."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_ONE]
title = "Macbeth marks the first low marching step."
pattern = "scene_of_character"
[scenes.PASS_LISTS_INDENT_TWO]
title = "Lady Macbeth measures the second marching step."
pattern = "scene_of_character"
[scenes.PASS_LISTS_INDENT_THREE]
title = "Macbeth keeps the third marching step."
pattern = "scene_of_character"
[scenes.PASS_LISTS_MARKER_DIGIT]
title = "Lady Macbeth gathers the numbered standard."
pattern = "scene_of_character"
[scenes.PASS_LISTS_MARKER_DOT]
title = "Macbeth seals the numbered standard's point."
pattern = "scene_of_character"
[scenes.PASS_LISTS_CONTINUE]
title = "Lady Macbeth bears the marching line onward."
pattern = "scene_of_character"
[scenes.PASS_LISTS_NEST_OPEN]
title = "Macbeth opens the army's inner rank."
pattern = "scene_of_character"
[scenes.PASS_LISTS_NEST_CLOSE]
title = "Lady Macbeth recalls the army's outer rank."
pattern = "scene_of_character"
[scenes.PASS_LISTS_LOOSE]
title = "Macbeth grants the rank its breathing field."
pattern = "scene_of_character"
[scenes.PASS_LISTS_FULL_FINISH]
title = "Lady Macbeth dismisses the ordered host."
pattern = "scene_of_character"
[scenes.PASS_LISTS_INDENT_GUARD]
title = "The marching step keeps one certain measure."
pattern = "bare_statement"
[scenes.PASS_LISTS_NEST_GUARD]
title = "The inner rank keeps its faithful border."
pattern = "bare_statement"
[scenes.PASS_LISTS_FULL_GUARD]
title = "The ordered host keeps one final watch."
pattern = "bare_statement"

# Amendment A3 final-blank tight-list rollback working pool
[scenes.PASS_LISTS_LOOSE_PROVISION]
title = "Lady Macbeth holds the rank before its silence."
pattern = "scene_of_character"
[scenes.PASS_LISTS_LOOSE_COMMIT]
title = "Macbeth lets the waiting rank take breath."
pattern = "scene_of_character"
[scenes.PASS_LISTS_LOOSE_EOF]
title = "The silent rank meets the page's last watch."
pattern = "bare_statement"
[scenes.PASS_LISTS_LOOSE_ROLLBACK]
title = "Lady Macbeth restores the rank's close order."
pattern = "scene_of_character"
[scenes.PASS_LISTS_LOOSE_REPLAY]
title = "Macbeth returns the held border to the host."
pattern = "scene_of_character"

# Amendment A3 Act-II spare pool; do not use without a further plan amendment.
[scenes.PASS_LISTS_LOOSE_GUARD]
title = "The waiting rank keeps one sure watch."
pattern = "bare_statement"
[scenes.PASS_LISTS_LOOSE_EOF_GUARD]
title = "The last rank keeps its faithful border."
pattern = "bare_statement"
[scenes.PASS_LISTS_LOOSE_ROLLBACK_GUARD]
title = "The restored rank keeps its settled line."
pattern = "bare_statement"
[scenes.PASS_LISTS_LOOSE_REPLAY_GUARD]
title = "The held border keeps its homeward course."
pattern = "bare_statement"

[scenes.SCRIBE_RAW_HTML_ADVANCED]
title = "Prospero inscribes the court's whole wall."
pattern = "scene_of_character"
[scenes.SCRIBE_RAW_HTML_ADVANCED_SEP]
title = "The courtly wall receives its clear interval."
pattern = "bare_statement"
[scenes.SCRIBE_RAW_HTML_ADVANCED_CLOSE]
title = "Prospero seals the courtly wall in light."
pattern = "scene_of_character"
[scenes.SCRIBE_RAW_HTML_ADVANCED_GUARD]
title = "The courtly wall keeps its radiant edge."
pattern = "bare_statement"

[scenes.SCRIBE_QUOTE_NEST_OPEN]
title = "Prospero opens the echo's inward hall."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_CLOSE]
title = "Prospero closes the echo's inward hall."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_INDENT]
title = "Puck lays two pale steps beneath the echo."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_RETURN]
title = "Puck returns the echo to its outer shore."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_FINISH]
title = "Prospero releases the layered echo."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_GUARD]
title = "The layered echo keeps one noble measure."
pattern = "bare_statement"

[scenes.SCRIBE_LIST_DEPTH_OPEN]
title = "Prospero opens the host's inward order."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_DEPTH_CLOSE]
title = "Prospero closes the host's inward order."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_LOOSE_BEGIN]
title = "Puck grants the host a spacious interval."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_LOOSE_CLOSE]
title = "The spacious host gathers its settled line."
pattern = "bare_statement"
[scenes.SCRIBE_LIST_NEST_RETURN]
title = "Puck restores the host's outer file."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_ITEM_PARAGRAPH]
title = "Prospero inscribes the host's inner speech."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_ITEM_CLOSE_FINAL]
title = "Prospero seals the host's last brave file."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_FULL_FINISH]
title = "Puck releases the ordered host to dawn."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_DEPTH_GUARD]
title = "The inward host keeps one radiant border."
pattern = "bare_statement"
[scenes.SCRIBE_LIST_FULL_GUARD]
title = "The ordered host keeps one noble watch."
pattern = "bare_statement"
```

### Amendment A2 header reservation

The header prerequisite has seven working Act-II scenes and four working
Act-IV scenes.  Each touched act has four pre-approved spares, satisfying the
at-least-20%-and-four-spare rule.  These are controlled scene titles; the
existing Critical `HEADER = 2`, level values, and `TEXT_END` surfaces need no
new prose.

| Act | Working-label ledger | Spares |
|---|---|---|
| II | `PASS_HEADER_START` (candidate entry); `PASS_HEADER_MARK` (count one through six hashes); `PASS_HEADER_SEPARATOR` (require space/tab); `PASS_HEADER_TEXT` (stage text); `PASS_HEADER_CLOSER` (strip legal closer); `PASS_HEADER_EMIT` (emit code, level, text); `PASS_HEADER_REPLAY` (restore rejected candidate) | `PASS_HEADER_GUARD`, `PASS_HEADER_DEPTH_GUARD`, `PASS_HEADER_TEXT_GUARD`, `PASS_HEADER_REPLAY_GUARD` |
| IV | `SCRIBE_HEADER_OPEN` (validate and emit opening tag); `SCRIBE_HEADER_TEXT` (emit span-processed text); `SCRIBE_HEADER_CLOSE` (emit matching close); `SCRIBE_HEADER_RETURN` (restore block dispatch) | `SCRIBE_HEADER_GUARD`, `SCRIBE_HEADER_LEVEL_GUARD`, `SCRIBE_HEADER_TEXT_GUARD`, `SCRIBE_HEADER_RETURN_GUARD` |

```toml
[scenes.PASS_HEADER_START]
title = "Lady Macbeth marks the page's raised standard."
pattern = "scene_of_character"
[scenes.PASS_HEADER_MARK]
title = "Macbeth counts the standard's dark strokes."
pattern = "scene_of_character"
[scenes.PASS_HEADER_SEPARATOR]
title = "Lady Macbeth keeps the standard's measured space."
pattern = "scene_of_character"
[scenes.PASS_HEADER_TEXT]
title = "Macbeth bears the standard's spoken burden."
pattern = "scene_of_character"
[scenes.PASS_HEADER_CLOSER]
title = "Lady Macbeth trims the standard's closing edge."
pattern = "scene_of_character"
[scenes.PASS_HEADER_EMIT]
title = "Macbeth sends the raised standard onward."
pattern = "scene_of_character"
[scenes.PASS_HEADER_REPLAY]
title = "Lady Macbeth restores the fallen standard."
pattern = "scene_of_character"
[scenes.PASS_HEADER_GUARD]
title = "The raised standard keeps one sure watch."
pattern = "bare_statement"
[scenes.PASS_HEADER_DEPTH_GUARD]
title = "The standard keeps its counted height."
pattern = "bare_statement"
[scenes.PASS_HEADER_TEXT_GUARD]
title = "The standard keeps its faithful word."
pattern = "bare_statement"
[scenes.PASS_HEADER_REPLAY_GUARD]
title = "The fallen standard keeps its former place."
pattern = "bare_statement"

[scenes.SCRIBE_HEADER_OPEN]
title = "Prospero opens the standard's radiant face."
pattern = "scene_of_character"
[scenes.SCRIBE_HEADER_TEXT]
title = "Puck bears the standard's bright word."
pattern = "scene_of_character"
[scenes.SCRIBE_HEADER_CLOSE]
title = "Prospero seals the standard's radiant face."
pattern = "scene_of_character"
[scenes.SCRIBE_HEADER_RETURN]
title = "Puck returns the standard to the page."
pattern = "scene_of_character"
[scenes.SCRIBE_HEADER_GUARD]
title = "The radiant standard keeps one noble edge."
pattern = "bare_statement"
[scenes.SCRIBE_HEADER_LEVEL_GUARD]
title = "The radiant standard keeps its counted height."
pattern = "bare_statement"
[scenes.SCRIBE_HEADER_TEXT_GUARD]
title = "The radiant standard keeps its faithful word."
pattern = "bare_statement"
[scenes.SCRIBE_HEADER_RETURN_GUARD]
title = "The radiant standard keeps its homeward course."
pattern = "bare_statement"
```

## Verification

Each fixture follows architecture §8.1's four gates: focused mdtest pass,
fresh-oracle strict parity, all already-enabled fixtures plus both spike suites,
and proof that the release SPL—not Markdown.pl—performed the transform.  Every
SPL/TOML checkpoint also runs:

```bash
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

The completion checkpoint runs `uv run pytest -q`, `uv run ruff check .`,
`uv run ruff format --check .`, `uv run pyright`, a 23-case differential smoke
report, and the performance measurement procedure in `docs/performance/budget.md`.
