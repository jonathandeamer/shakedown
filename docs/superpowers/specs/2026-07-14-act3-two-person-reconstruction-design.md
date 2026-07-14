# Act III Protected-Region Two-Person Reconstruction — Design

**Date:** 2026-07-14
**Status:** accepted for Plan 4S Task 4 Step 3
**Amends:** `docs/superpowers/specs/2026-07-12-span-architecture-spike-design.md` §A16

## Decision

The protected-region graph at `138cdd1` cannot be regenerated because it
combines writes to more than one holder in 27 scenes after the mechanical
`ACT_III_START` correction.  This is a lowering legality defect, not evidence
against the A8--A15 carrier model.  Keep every A8--A15 owner, floor,
continuation record, selector, and byte-order rule.  Reconstruct the graph so
each scene has exactly its declared anchor and one other participant.

The reconstruction uses two mechanisms only:

1. Retarget a scene's anchor when its operations already touch one legal pair;
   it adds no scene or controlled prose.
2. Split a cross-holder handoff into the reserved adapter labels below.  An
   adapter may move state between exactly one pair and then `goto` the next
   listed scene.  It may not introduce a holder, sentinel, selector, output
   representation, or recovery branch.

`ACT_III_START` is the sole mechanical correction: remove `companion=PUCK`.
Its existing `(JULIET, LADY_MACBETH)` operations are legal because Lady
Macbeth initialization is off-stage.

## Binding scene reconstruction ledger

The following ledger is exhaustive for every additional invalid scene reported
by `scripts.splc.validate.participants` at commit `138cdd1`.  “Retarget” means
retain the label and operations but use the specified pair.  “Split” means
retain the entry label for the first listed pair and insert only the named
adapters in the stated order.  Branches retain their existing targets unless a
listed adapter is the necessary handoff target.

| Invalid entry | Reconstruction | Legal pair(s), in order |
|---|---|---|
| `LYRIC_HTML_OPEN` | Split tag output/tag selection from raw `<` requeue. | existing `(JULIET, HECATE)` → `LYRIC_HTML_OPEN_REQUEUE` `(PUCK, ROMEO)` → `LYRIC_FIELD_RETRY` |
| `LYRIC_AUTOLINK_OPEN` | Split opening output/tag selection, duplicate-floor creation, and raw `<` requeue. | existing `(JULIET, HECATE)` → `LYRIC_AUTOLINK_OPEN_DUPLICATE` `(LADY_MACBETH, ROMEO)` → `LYRIC_AUTOLINK_OPEN_REQUEUE` `(PUCK, ROMEO)` |
| `LYRIC_FIELD_OPEN` | Retarget; Romeo owns the capture floor and Macbeth owns depth. | `(ROMEO, MACBETH)` |
| `LYRIC_AUTOLINK_CLOSE` | Split close selection/output from duplicate-field setup. | existing `(JULIET, PROSPERO)` → `LYRIC_AUTOLINK_CLOSE_DUPLICATE` `(HECATE, PROSPERO)` |
| `LYRIC_FIELD_SOURCE_END` | Split restored real end from Hecate literal-output floor creation. | existing `(PUCK, ROMEO)` → `LYRIC_FIELD_SOURCE_END_LITERAL` `(HECATE, ROMEO)` |
| `LYRIC_LABEL_OPEN` | Retarget the source pop and Horatio payload hold. | `(PUCK, HORATIO)` |
| `LYRIC_REGION_TAG_OPEN` | Retarget emitted link prefix and field tag. | `(JULIET, HECATE)` |
| `LYRIC_IMAGE_TEST_LABEL` | Retarget the source pop and Horatio payload hold. | `(PUCK, HORATIO)` |
| `LYRIC_IMAGE_DEST_OPEN` | Retarget emitted image prefix and field tag. | `(JULIET, HECATE)` |
| `LYRIC_FIELD_UNTERMINATED` | Split Puck/Prospero close classification from image-title selection and link-title output. | existing `(PUCK, PROSPERO)` → `LYRIC_FIELD_UNTERMINATED_IMAGE` `(HECATE, PROSPERO)` or `LYRIC_FIELD_UNTERMINATED_LINK` `(JULIET, HECATE)` |
| `LYRIC_LABEL_REQUEUE` | Split emitted `">`/link selector from private Puck end. | existing `(JULIET, LADY_MACBETH)` → `LYRIC_LABEL_REQUEUE_END` `(LADY_MACBETH, PUCK)` |
| `LYRIC_ALT_REQUEUE` | Split emitted `" alt="`/title test, selector assignment, and private Puck end. | existing `(JULIET, PROSPERO)` → `LYRIC_ALT_REQUEUE_SELECT` `(LADY_MACBETH, PROSPERO)` → `LYRIC_ALT_REQUEUE_END` `(LADY_MACBETH, PUCK)` |
| `LYRIC_ALT_REQUEUE_WITH_TITLE` | Retarget selector assignment and private end. | `(LADY_MACBETH, PUCK)` |
| `LYRIC_REQUEUE_DRAIN` | Retarget Horatio pop and raw Puck push. | `(HORATIO, PUCK)` |
| `LYRIC_EMPHASIS_OPEN` | Split preserved opener glyph from opener-run initialization and Horatio floor. | existing `(HECATE, PROSPERO)` → `LYRIC_EMPHASIS_OPEN_BUFFER` `(HECATE, HORATIO)` |
| `LYRIC_EMPHASIS_COUNT_MORE` | Split Puck/Hecate classification from the Horatio payload hold. | existing `(PUCK, HECATE)` → `LYRIC_EMPHASIS_COUNT_HOLD` `(PUCK, HORATIO)` |
| `LYRIC_EMPHASIS_CAND_MORE` | Retarget candidate-run increment. | `(HECATE, PUCK)` |
| `LYRIC_EMPHASIS_SEEK` | Split Puck/Hecate classification from the Horatio payload hold. | existing `(PUCK, HECATE)` → `LYRIC_EMPHASIS_SEEK_HOLD` `(PUCK, HORATIO)` |
| `LYRIC_EMPHASIS_CAND_COUNT` | Retarget candidate initialization. | `(MACBETH, PUCK)` |
| `LYRIC_EMPHASIS_MATCH_MORE` | Retarget candidate increment. | `(MACBETH, PUCK)` |
| `LYRIC_EMPHASIS_REPLAY` | Retarget candidate decrement and Horatio star replay. | `(MACBETH, HORATIO)` |
| `LYRIC_EMPHASIS_MATCH` | Split restored lookahead/classification, strong selector, and strong output. | existing `(PUCK, HECATE)` → `LYRIC_EMPHASIS_MATCH_STRONG` `(PUCK, PROSPERO)` → `LYRIC_EMPHASIS_MATCH_OUTPUT` `(JULIET, PUCK)` |
| `LYRIC_EMPHASIS_TRIPLE_CLOSE` | Split triple selector from `<strong>` output. | existing `(PUCK, PROSPERO)` → `LYRIC_EMPHASIS_TRIPLE_OUTPUT` `(JULIET, PUCK)` |
| `LYRIC_EMPHASIS_EMIT_OPEN` | Split em selector from `<em>` output. | existing `(PUCK, PROSPERO)` → `LYRIC_EMPHASIS_EMIT_OUTPUT` `(JULIET, PUCK)` |
| `LYRIC_EMPHASIS_SOURCE_END` | Retarget literal `*` output and Hecate floor creation. | `(JULIET, HECATE)` |
| `LYRIC_EMPHASIS_LITERAL_REVERSE` | Retarget Horatio-to-Hecate reverse. | `(HORATIO, HECATE)` |
| `LYRIC_IMAGE_TITLE_CLOSE` | Retarget image-title prefix and Hecate reverse floor creation. | `(JULIET, HECATE)` |

All branch tests of off-stage values remain legal.  The pairs above are
derived from write targets; a companion exists only where the pair has one
write target or needs an on-stage speaker.

## Adapter reservation (ready to paste)

Seventeen adapters are required by the ledger.  Five spares (29.4%) satisfy
the literary protocol and are unavailable without another planning amendment.
No Recall phrase is added: every new `Pop` remains in an existing scene with
its previously reserved Recall key.

```toml
# src/30-act3-literary.toml — A17 two-person reconstruction adapters
[scenes.LYRIC_HTML_OPEN_REQUEUE]
title = "Romeo returns the moonlit gate's first mark."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_OPEN_DUPLICATE]
title = "Lady Macbeth lays the shining road's second bed."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_OPEN_REQUEUE]
title = "Romeo returns the shining road's first mark."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_CLOSE_DUPLICATE]
title = "Hecate readies the shining road's echo."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_SOURCE_END_LITERAL]
title = "Hecate gathers the field's last loose mark."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_UNTERMINATED_IMAGE]
title = "Hecate keeps the portrait's delayed name."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_UNTERMINATED_LINK]
title = "Juliet opens the rose-path's quiet name."
pattern = "scene_of_character"
[scenes.LYRIC_LABEL_REQUEUE_END]
title = "Lady Macbeth sets the rose-name's private gate."
pattern = "scene_of_character"
[scenes.LYRIC_ALT_REQUEUE_SELECT]
title = "Lady Macbeth chooses the portrait's return."
pattern = "scene_of_character"
[scenes.LYRIC_ALT_REQUEUE_END]
title = "Lady Macbeth sets the portrait-name's private gate."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_OPEN_BUFFER]
title = "Hecate gathers the star's first hidden leaf."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_COUNT_HOLD]
title = "Horatio holds the answering star's first leaf."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_SEEK_HOLD]
title = "Horatio holds each wandering star-leaf."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_MATCH_STRONG]
title = "Prospero chooses the sunlit strong seal."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_MATCH_OUTPUT]
title = "Juliet sends the sunlit strong seal onward."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_TRIPLE_OUTPUT]
title = "Juliet sends the triple star's strong seal onward."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_EMIT_OUTPUT]
title = "Juliet sends the single star's seal onward."
pattern = "scene_of_character"

# A17 spare pool — do not use without another planning amendment.
[scenes.LYRIC_FIELD_TWO_PERSON_GUARD]
title = "The guarded field keeps its faithful pair."
pattern = "bare_statement"
[scenes.LYRIC_REQUEUE_TWO_PERSON_GUARD]
title = "The private gate keeps its faithful pair."
pattern = "bare_statement"
[scenes.LYRIC_EMPHASIS_TWO_PERSON_GUARD]
title = "The answering star keeps its faithful pair."
pattern = "bare_statement"
[scenes.LYRIC_AUTOLINK_TWO_PERSON_GUARD]
title = "The shining road keeps its faithful pair."
pattern = "bare_statement"
[scenes.LYRIC_REGION_TWO_PERSON_GUARD]
title = "The rose-path keeps its faithful pair."
pattern = "bare_statement"
```

The title pool is 17 working labels plus five spares (29.4%), which exceeds
the required 20% floor.  `LYRIC_FIELD_UNTERMINATED_IMAGE` and
`LYRIC_FIELD_UNTERMINATED_LINK` are two of those 17 adapters; the ledger's
other stages retain their pre-existing labels.

## Required proof before regeneration

Add a focused IR-shape test that imports `src_ir.act3.ACT`, runs
`participants(scene, ACT.anchor)` for every scene, and fails with the
offending label if any scene is not binary.  It must also assert that every
new A17 adapter has the exact pair from the ledger and that no A17 spare is
reachable.  This test precedes all production reconstruction.

Before regenerating, run:

```bash
uv run pytest tests/test_splc_validate.py tests/test_act3_contracts.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_splc_generated_fragments.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
```

Then run Task 4 Step 3's full spike command unchanged.  Any binary-pair,
entry-pair, carrier-event, or literary-registration failure remains a
`BLOCK[plan]`; it does not authorize an A17 spare, a third participant, or a
hand-edited generated fragment.
