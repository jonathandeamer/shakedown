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
