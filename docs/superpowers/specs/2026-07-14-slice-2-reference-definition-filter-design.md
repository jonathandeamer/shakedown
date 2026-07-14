# Slice 2 Reference-Definition Filter — Design

**Date:** 2026-07-14
**Status:** accepted for Slice 2 Task 2 Step 3 recovery
**Amends:** `docs/superpowers/plans/2026-07-14-slice-2-low-risk-fixtures.md`

## Decision

Task 1 correctly stopped deleting trailing input lines, but the Slice-1
reference-link scenes still use their fixed librarian payloads.  Consequently,
the trailing reference-definition paragraph in `Amps and angle encoding` now
reaches Act IV as ordinary paragraph text.  This recovery installs a temporary,
generic Act-III filter for a *definition-only paragraph*.  It is not the Slice-3
reference table: it neither stores a label nor resolves a destination.

The filter runs only on a `PARA` payload before the existing `[` reference/link
route.  It accepts a paragraph only when every nonblank physical line has a
nonempty bracketed label immediately followed by `:` and at least one
non-space destination glyph.  It discards the complete payload and its
`TEXT_END` only after that full proof.  Any malformed candidate, prose line,
inline link, image, or mixed paragraph replays its buffered glyphs in their
original order to the existing span scanner.  Thus `[link] [1]`, `[AT&T] [2]`,
and both inline-link paragraphs keep their current Slice-1 routes.

The filter deliberately expires when Slice 3 introduces the actual reference
table: that slice replaces the discard close with table insertion.  No Act I
or Act II grammar, token code, carrier ownership, generated-SPL file, or
compiler rule changes in this recovery.

## Binary-scene ledger

All scenes are `(ROMEO, PUCK)`.  Each pop uses the already-configured Romeo
Recall `brackets_first_petal`; the phrase is a reused local glyph recall, not
a new controlled surface.  The filter owns a private Romeo candidate stack
and returns to the existing scan only through the listed replay/discard exits.

| Scene | Operation and terminal route |
|---|---|
| `LYRIC_DEFINITION_GUARD` | Receive the opening `[` from the existing scan; initialize the candidate stack and read the first label glyph.  Empty label or `TEXT_END` routes to replay. |
| `LYRIC_DEFINITION_LABEL` | Copy non-`]` label glyphs to the candidate stack; `]` routes to close; newline/`TEXT_END` routes to replay. |
| `LYRIC_DEFINITION_COLON` | Read exactly `:` after `]`; any other glyph routes to replay. |
| `LYRIC_DEFINITION_DESTINATION` | Require one non-space, non-newline destination glyph, then consume the remainder of that physical line. |
| `LYRIC_DEFINITION_NEXT_LINE` | At newline, accept another bracketed definition line or the final `TEXT_END`; any ordinary/blank/malformed line routes to replay. |
| `LYRIC_DEFINITION_DISCARD` | Drain the proven paragraph and its terminator without emitting a `PARA`; return to token traversal. |

The replay path may reuse existing `LYRIC_LINK_REGION` only after it restores
the opening bracket and every held candidate glyph in forward order.  It must
not enter a hard-coded reference-anchor scene, change `ROMEO`'s scan-count
decrement, or emit HTML while the candidate remains undecided.  If satisfying
that replay contract needs a seventh scene or a new recall key, stop and add
`BLOCK[plan]`; the spare pool is not implementation authority.

## Controlled-surface reservation

These are Incidental Act-III scene titles, evaluated against the Pastoral /
Natural palette.  Six working labels plus four spares meet the protocol's
minimum reserve (four and at least 20%).

```toml
# src/30-act3-literary.toml — Slice 2 definition-only filter working pool
[scenes.LYRIC_DEFINITION_GUARD]
title = "Romeo tests the bracketed garden threshold."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_LABEL]
title = "Juliet gathers the bracketed garden name."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_COLON]
title = "Romeo seeks the garden name's quiet seal."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DESTINATION]
title = "Juliet follows the garden path beyond the seal."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_NEXT_LINE]
title = "Romeo asks whether the garden ledger continues."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DISCARD]
title = "The garden ledger leaves no petal for the song."
pattern = "bare_statement"

# Slice 2 definition-only filter spare pool — unavailable without an amendment.
[scenes.LYRIC_DEFINITION_REPLAY_GUARD]
title = "The unproved garden name returns to daylight."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_LINE_GUARD]
title = "The garden ledger keeps one faithful line."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_PATH_GUARD]
title = "The garden path keeps its faithful mark."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_CLOSE_GUARD]
title = "The garden ledger closes beneath clear moonlight."
pattern = "bare_statement"
```

## Required proof and stop condition

First add red fast-IR tests in `tests/test_act3_contracts.py` for the exact
two-line trailing definition paragraph from `Amps and angle encoding`, a
single valid generic definition, a two-line valid generic definition block,
`[not]: prose` with no destination, `[x] : destination`, and a mixed
definition-plus-prose paragraph.  The valid cases must produce no `PARA`; the
invalid/mixed cases must preserve their source bytes through Act III.  Add a
scene-observer assertion that the fixture's four non-definition link
paragraphs never visit `LYRIC_DEFINITION_DISCARD`.

Before regeneration, extend `test_act3_scenes_are_binary_and_reserved_adapters_match_pairs`
with the six working labels mapped to `(Char.ROMEO, Char.PUCK)` and the four
unreachable spares.  Run the red focused test, then implement only the ledger
and append the ten TOML entries above.  Regenerate and assemble; never edit a
generated fragment by hand.

```bash
uv run pytest tests/test_act3_contracts.py tests/test_splc_validate.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_act3_contracts.py tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -k 'Amps and angle or Horizontal rules' -q
uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Horizontal rules'
```

The final harness output must contain `summary: 2/2 byte-identical`.  A fast
interpreter-only pass, real-wrapper truncation, pair/entry-pair failure,
missing controlled surface, altered non-definition bytes, or any need beyond
the six working scenes is `BLOCK[plan]`; do not consume a spare, alter the
compiler, or hand-edit generated SPL.

## Amendment A1 (2026-07-14): carrier-safe replay and protected code leaves

**Status:** accepted; supersedes the preceding six-working-scene ledger and its ten-entry reservation. The predicate remains correct, but its choreography is not implementable: `PARA` is already pushed to Juliet before text opens, so accepted discard must remove that provisional token, while rejected source must be rebuilt above a private `TEXT_END` before `LYRIC_POP_GLYPH`. Also, `CODE_BLOCK` is currently routed through `LYRIC_BUFFER_OPEN`; it must bypass all span scenes.

`_traverse_dispatch()` continues to push the token code to Juliet first. It routes `tokens.PARA` to `LYRIC_DEFINITION_OPEN`, `tokens.CODE_BLOCK` to `TRAVERSE_COPY_CODE_TEXT`, and every other text token to the existing `TRAVERSE_OPEN_TEXT`. The two protected-code scenes copy each glyph and its `TEXT_END` directly Puck-to-Juliet, then return to `TRAVERSE_NEXT_TOKEN`; they never visit `LYRIC_BUFFER_OPEN` or `LYRIC_POP_GLYPH`.

The paragraph filter is binding: seed Romeo with `STREAM_END`; drain the Puck run to Romeo while consuming its source terminator; restore a private Puck `TEXT_END` and unwind Romeo back to Puck; then pop Puck forward while copying every real glyph to Hecate. Accept one or more lines only when each is `[nonempty-label]:` followed immediately by a non-space, non-newline destination glyph. On accepted private terminator, drain Hecate, pop Juliet's provisional `PARA`, and traverse the next token. On any rejection, push a private `TEXT_END` to Puck first, pop Hecate to Puck to restore forward bytes, then enter `LYRIC_POP_GLYPH`. No scene may combine a Romeo/Puck transfer with Hecate work or the Juliet provisional-token pop.

### Complete binary-scene ledger

All 21 labels below are working authority. The pairs must be asserted in `test_act3_scenes_are_binary_and_reserved_adapters_match_pairs`; `*_KEEP` entries are required split adapters.

| Label | Pair | Responsibility |
|---|---|---|
| `TRAVERSE_COPY_CODE_TEXT` | `(JULIET, PUCK)` | Pop code glyph; route terminator to existing copier or code-copy push. |
| `TRAVERSE_COPY_CODE_GLYPH` | `(JULIET, PUCK)` | Push protected glyph to Juliet and loop. |
| `LYRIC_DEFINITION_OPEN` | `(ROMEO, PUCK)` | Seed Romeo sentinel and enter drain. |
| `LYRIC_DEFINITION_DRAIN` | `(ROMEO, PUCK)` | Pop Puck; select source-end close or Romeo push. |
| `LYRIC_DEFINITION_DRAIN_KEEP` | `(ROMEO, PUCK)` | Push source glyph to Romeo and loop. |
| `LYRIC_DEFINITION_DRAIN_CLOSE` | `(ROMEO, PUCK)` | Restore private Puck terminator and begin unwind. |
| `LYRIC_DEFINITION_UNWIND` | `(ROMEO, PUCK)` | Pop Romeo; select verifier entry or Puck restore. |
| `LYRIC_DEFINITION_UNWIND_KEEP` | `(ROMEO, PUCK)` | Push glyph to Puck and loop. |
| `LYRIC_DEFINITION_LINE_OPEN` | `(HECATE, PUCK)` | Copy required line opener; only `[` continues. |
| `LYRIC_DEFINITION_LABEL_FIRST` | `(HECATE, PUCK)` | Copy and require first nonempty label glyph. |
| `LYRIC_DEFINITION_LABEL_REST` | `(HECATE, PUCK)` | Copy until `]`; reject malformed/end. |
| `LYRIC_DEFINITION_COLON` | `(HECATE, PUCK)` | Copy and require immediate colon. |
| `LYRIC_DEFINITION_DESTINATION` | `(HECATE, PUCK)` | Copy and require non-space/non-newline destination start. |
| `LYRIC_DEFINITION_DESTINATION_TAIL` | `(HECATE, PUCK)` | Copy tail; newline restarts line, terminator accepts. |
| `LYRIC_DEFINITION_DISCARD_DRAIN` | `(HECATE, JULIET)` | Drain proven record to sentinel. |
| `LYRIC_DEFINITION_DISCARD_KEEP` | `(HECATE, JULIET)` | Continue discard drain. |
| `LYRIC_DEFINITION_DISCARD_CLOSE` | `(HECATE, JULIET)` | Pop provisional `PARA` and resume traversal. |
| `LYRIC_DEFINITION_REPLAY_BEGIN` | `(HECATE, PUCK)` | Restore private Puck terminator. |
| `LYRIC_DEFINITION_REPLAY_POP` | `(HECATE, PUCK)` | Pop Hecate; select close or restore. |
| `LYRIC_DEFINITION_REPLAY_KEEP` | `(HECATE, PUCK)` | Push rejected glyph to Puck and loop. |
| `LYRIC_DEFINITION_REPLAY_CLOSE` | `(HECATE, PUCK)` | Enter `LYRIC_POP_GLYPH` on reconstructed source. |

### Controlled-surface reservation

The earlier six-working/four-spare block is retired and must not be copied. This replacement has 21 working labels plus five unavailable spares (24%, exceeding the 20% and four-title floors). They are Incidental Act-III Pastoral/Natural titles; no new Recall is needed.

```toml
[scenes.TRAVERSE_COPY_CODE_TEXT]
title = "Juliet keeps the sheltered chamber line."
pattern = "scene_of_character"
[scenes.TRAVERSE_COPY_CODE_GLYPH]
title = "Romeo carries one sheltered chamber mark."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_OPEN]
title = "Romeo opens the garden ledger's quiet gate."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DRAIN]
title = "Juliet gathers the garden ledger's leaves."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DRAIN_KEEP]
title = "Romeo keeps one unproved garden leaf."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DRAIN_CLOSE]
title = "The garden ledger reaches its shaded hedge."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_UNWIND]
title = "Juliet returns the garden ledger in order."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_UNWIND_KEEP]
title = "Romeo restores one garden leaf to daylight."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_LINE_OPEN]
title = "Juliet seeks the garden ledger's opening mark."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_LABEL_FIRST]
title = "Romeo tests the first leaf of a garden name."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_LABEL_REST]
title = "Juliet gathers the garden name's remaining leaves."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_COLON]
title = "Romeo seeks the garden name's quiet seal."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DESTINATION]
title = "Juliet finds the garden path beyond the seal."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DESTINATION_TAIL]
title = "Romeo follows the garden path through morning dew."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DISCARD_DRAIN]
title = "Juliet clears the proven garden ledger."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DISCARD_KEEP]
title = "Romeo frees one proven garden leaf."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_DISCARD_CLOSE]
title = "The proven garden ledger leaves no song behind."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_REPLAY_BEGIN]
title = "Juliet returns the unproved garden path."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_REPLAY_POP]
title = "Romeo recalls the unproved garden leaf."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_REPLAY_KEEP]
title = "Juliet restores one garden leaf to the song."
pattern = "scene_of_character"
[scenes.LYRIC_DEFINITION_REPLAY_CLOSE]
title = "The unproved garden ledger returns to daylight."
pattern = "bare_statement"

# Spares — unavailable without amendment.
[scenes.LYRIC_DEFINITION_GARDEN_GUARD]
title = "The garden ledger keeps one patient hedge."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_REPLAY_GUARD]
title = "The garden path waits beneath the morning light."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_CHAMBER_GUARD]
title = "The sheltered chamber keeps its silver door."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_LEAF_GUARD]
title = "One loose garden leaf rests beside the rose."
pattern = "bare_statement"
[scenes.LYRIC_DEFINITION_CLOSE_GUARD]
title = "The garden ledger closes beneath one clear moon."
pattern = "bare_statement"
```

### Required proof and stop condition

Replace retired six-label assertions with all 21 pairs and five unreachable spares. Add fast-IR contracts for the trailing two-line fixture definition; valid one- and two-line generic blocks; `[not]:`, `[not]:   `, `[x] : destination`, `[]: destination`, prose, blank second line, and mixed definition/prose (each replayed byte-for-byte); fixture reference/inline paragraphs never visiting `LYRIC_DEFINITION_DISCARD_CLOSE`; and a `CODE_BLOCK` containing `\\*`, backticks, and `<http://example.com/>` never visiting `LYRIC_BUFFER_OPEN` or `LYRIC_POP_GLYPH` before `TEXT_END`.

```bash
uv run pytest tests/test_act3_contracts.py tests/test_splc_validate.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_act3_contracts.py tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -k "(Amps and angle and encoding) or (Horizontal and rules)" -q
uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Horizontal rules'
```

Require `summary: 2/2 byte-identical`. Any altered rejected byte, missing private terminator, span-scene visit from `CODE_BLOCK`, binary/entry-pair failure, title mismatch, or need beyond these 21 labels is `BLOCK[plan]`; do not consume a spare, alter the compiler, or hand-edit generated SPL.

## Amendment A2 (2026-07-14): baseline-first routing and observable replay

**Status:** accepted; this narrows A1 rather than extending its 21-scene
pool.  The dirty A1 attempt established two facts that A1 did not state
plainly enough: a `PARA` branch must actually enter the verifier, and rendered
Act-III text is not evidence that a rejected candidate replayed byte-for-byte
because the ordinary scanner deliberately consumes Markdown punctuation.

Before touching the definition scenes, restore the Span Spike baseline through
the Act-II HR repair in the companion binary-gate Amendment C.  `***both***
and **outer *inner* outer**` must reach Act III with all three opening stars;
this is a prerequisite, not a new span change.  The Act-III repair must then
make these exact dispatch choices in `_traverse_dispatch()` after copying the
token code to Juliet:

1. `tokens.CODE_BLOCK` goes to `TRAVERSE_COPY_CODE_TEXT`.
2. `tokens.PARA` goes to `LYRIC_DEFINITION_OPEN`.
3. every other text-bearing token goes to `TRAVERSE_OPEN_TEXT`.

Remove the disconnected A1 scaffolding and its three reachable former-spare
guards (`LYRIC_DEFINITION_LEAF_GUARD`, `LYRIC_DEFINITION_GARDEN_GUARD`, and
`LYRIC_DEFINITION_CHAMBER_GUARD`).  The 21 working labels remain the entire
authority; the five listed spares remain unreachable.  `LYRIC_DEFINITION_OPEN`
may be reached only from the `PARA` dispatch branch, never from a requeue,
link/image route, or code leaf.

For a rejected candidate, A1's replay sequence is binding but its test oracle
is corrected: immediately before `LYRIC_POP_GLYPH`, Puck's private floor must
be followed, pop-first, by the original candidate glyphs in source order and
one private `TEXT_END`.  Extend `_SceneObserver` with a source-pop ledger that
records values popped by `LYRIC_POP_GLYPH` until that terminator.  The invalid
and mixed cases assert this ledger equals the original paragraph bytes plus
`TEXT_END`; they must not assert decoded Act-III output equals Markdown source.
The existing ordinary scanner remains responsible for the resulting Markdown
interpretation.  Valid definition-only paragraphs still decode to no `PARA`.

The focused red/green sequence is:

```bash
uv run pytest tests/test_act2_slice2.py -q
uv run pytest tests/test_act3_contracts.py tests/test_splc_validate.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_act3_contracts.py tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
```

The first command must prove both rejected HR candidates and the overlapping
emphasis carrier prefix.  The second must prove all protected-region fixtures
without underflow before definition assertions are treated as green.  Any
remaining lost candidate byte, missing private terminator, span underflow, new
Act-III title, or scene outside A1's 21-label pool is `BLOCK[plan]`.

## Amendment A3 (2026-07-14): two-floor definition replay after Span-Spike restoration

**Status:** accepted; supersedes A2 only where A2 left the definition-scenes'
operation order implicit.  It consumes none of the five A1 spares and adds no
Act-III title, Recall key, token, compiler change, or generated-SPL edit.

The A5 recovery gate establishes two separate facts.  First,
`overlapping_emphasis` underflows in `LYRIC_EMPHASIS_SEEK` before a definition
candidate is involved; this is the already-authorized A14/A15 matched-requeue
repair, and it must be restored before the definition filter is evaluated.
Second, the dirty `LYRIC_DEFINITION_OPEN -> LYRIC_BUFFER_OPEN` adapter proves
that the 21-label reservation alone is not an implementation choreography.
The recovery must not use a direct buffer path, rendered paragraph text, or a
new guard label as a substitute for either proof.

### Gate 0: restore the accepted protected-span baseline

Before routing any `PARA` through a definition scene, reconstruct the
emphasis/requeue portion of `src_ir/act3.py` from the committed Task-3 graph
using Span-Architecture Spike A14 and A15 verbatim.  This is a narrow
correctness repair inside the existing accepted working labels, not Slice-3
work: a successful match restores its already-popped parent lookahead to Puck,
creates exactly one A9 continuation record, and enters
`LYRIC_REQUEUE_TRIPLE_CLOSE` only for `RESUME_TRIPLE_EMPH`; ordinary strong
uses `RESUME_STRONG` and enters `LYRIC_REQUEUE_DRAIN` without a synthetic
delimiter.  The drainer consumes only Horatio through its private floor, and
`LYRIC_REQUEUE_TRIPLE_OPEN` is the only scene that adds the synthetic opening
star.  In every child scan, the private `TEXT_END` is consumed before the
restored parent lookahead.

Run this gate before adding definition contracts:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q -k \
  "matched_emphasis_requeue_preserves_parent_lookahead or triple_emphasis_requeue_order or overlapping_emphasis or links_images_protected or protected_modes_do_not_underflow or text_end_event_order_is_carrier_safe"
```

Expected: PASS.  An underflow, a second continuation record, a literal
synthetic star, or a consumed parent lookahead is `BLOCK[plan]`; it does not
authorize a definition-scene change, an A1 spare, or a new literary surface.

### Binding two-floor verifier and replay choreography

After Gate 0 is green, retain A2's dispatch exactly: after copying the token
code to Juliet, `CODE_BLOCK` takes `TRAVERSE_COPY_CODE_TEXT`, `PARA` takes
`LYRIC_DEFINITION_OPEN`, and all other text-bearing tokens take
`TRAVERSE_OPEN_TEXT`.  `LYRIC_DEFINITION_OPEN` is not a forwarding adapter.
It and the following existing 21 A1 working labels perform this exact
sequence:

1. `LYRIC_DEFINITION_OPEN` pushes Romeo's `STREAM_END`.  The
   `DRAIN`/`DRAIN_KEEP` loop pops Puck and copies every paragraph glyph to
   Romeo.  On the real source `TEXT_END`, `DRAIN_CLOSE` consumes that real
   end, pushes exactly one private `TEXT_END` to Puck, and begins
   `UNWIND`/`UNWIND_KEEP`.  Unwind restores the complete paragraph to Puck in
   forward pop order; when Romeo's floor is consumed, Romeo holds
   `STREAM_END`, matching the ordinary buffered scanner's entry state.
2. `LYRIC_DEFINITION_LINE_OPEN` is the verifier's only entry.  In its legal
   `(HECATE, PUCK)` pair it first pushes Hecate's `STREAM_END`, then pops the
   first Puck glyph, copies that real glyph to Hecate, and accepts only `[`
   into `LABEL_FIRST`.  Every subsequent verifier read copies its non-end
   glyph to Hecate *before* testing it.  `LABEL_FIRST` requires a non-`]`,
   non-newline glyph; `LABEL_REST` requires `]`; `COLON` requires the
   immediate `:`; `DESTINATION` requires one non-space, non-newline glyph.
   `DESTINATION_TAIL` copies its tail, copies a newline before returning to
   `LINE_OPEN`, and accepts only its private Puck `TEXT_END`.  A private end
   is never copied to Hecate.
3. On every rejection, including ordinary prose at `LINE_OPEN`, branch to
   `LYRIC_DEFINITION_REPLAY_BEGIN` with Hecate containing exactly
   `[STREAM_END, original-source-glyphs]` bottom-to-top and Puck empty above
   the outer carrier floor.  `REPLAY_BEGIN` pushes one private Puck
   `TEXT_END`.  `REPLAY_POP` drains Hecate; each non-floor value goes through
   `REPLAY_KEEP` to Puck.  This LIFO transfer makes Puck's next pop sequence
   the original source glyphs in forward order followed by that one private
   `TEXT_END`.  On Hecate's floor, `REPLAY_CLOSE` goes directly to
   `LYRIC_POP_GLYPH`; it does not call `TRAVERSE_OPEN_TEXT`, does not create a
   second buffer floor, and does not pop Juliet's provisional `PARA`.
4. On accepted private Puck `TEXT_END`, `DISCARD_DRAIN`/`DISCARD_KEEP` drain
   Hecate through its one floor without emitting any glyph.  Only after that
   floor is consumed may `DISCARD_CLOSE`, in its `(HECATE, JULIET)` pair, pop
   Juliet's provisional `PARA` and return to `TRAVERSE_NEXT_TOKEN`.  It never
   sees or restores the real source terminator.

The only allowed `TEXT_END` counts are therefore: one real terminator consumed
by `DRAIN_CLOSE`; one private terminator reconstructed by `REPLAY_BEGIN` on a
reject; and no terminator re-emitted on an accepted discard.  The code-block
copy route remains outside this choreography and never visits any definition,
buffer, or glyph-pop scene.

### Required red/green proof

Replace the dirty decoded-output rejected-candidate assertions with a
`_SceneObserver` source-pop ledger.  For every rejected candidate, record
Puck values popped by `LYRIC_POP_GLYPH` from the first replay pop through its
private `TEXT_END`; assert that sequence is
`[ord(glyph) for glyph in original_text.removesuffix("\\n")] + [TEXT_END]`
for a one-line paragraph, retaining embedded newlines for mixed candidates.
The observer must separately prove that valid one- and two-line definitions
reach `LYRIC_DEFINITION_DISCARD_CLOSE`, leave no `PARA`, and that a code block
does not enter `LYRIC_BUFFER_OPEN`, `LYRIC_POP_GLYPH`, or any
`LYRIC_DEFINITION_*` label.

Run the following in order after Gate 0 and before regeneration:

```bash
uv run pytest tests/test_act2_slice2.py -q
uv run pytest tests/test_act3_contracts.py tests/test_splc_validate.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_act3_contracts.py tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
```

The Act-III reservation test must name exactly A1's 21 working labels and
five unreachable spares; `LYRIC_DEFINITION_GARDEN_GUARD`,
`LYRIC_DEFINITION_REPLAY_GUARD`, `LYRIC_DEFINITION_CHAMBER_GUARD`,
`LYRIC_DEFINITION_LEAF_GUARD`, and `LYRIC_DEFINITION_CLOSE_GUARD` remain TOML
reservations only and must be absent from `ACT.scenes`.  Any deviation from
the two-floor order, a failed Gate 0, a source-pop mismatch, missing private
end, binary/entry-pair failure, or need for an unreserved label is
`BLOCK[plan]`.
