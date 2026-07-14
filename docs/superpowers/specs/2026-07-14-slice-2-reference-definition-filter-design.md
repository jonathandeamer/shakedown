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
