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

## Amendment A18 (2026-07-14): branch-entry pair normalization

The completed A17 binary-scene reconstruction exposes a separate lowering
constraint: every branch arrival at a shared scene must leave the same
two-character set.  `entry_pairs()` correctly rejects the first conflict at
`LYRIC_FIELD_CLOSE_DISPATCH`: ordinary field scanning arrives from
`(ROMEO, PUCK)`, while the balanced-destination close arrives from
`(MACBETH, ROMEO)`.  Redirecting that branch alone exposes nine more existing
join conflicts.  This is stage-direction normalization only; it does not
change the A8--A17 ownership, stack, sentinel, selector, byte-order, or
continuation-record model.

The following ledger is exhaustive against the current post-A17 graph.  Each
adapter has no operation except `goto` to the named existing target.  Its
declared pair is the target's already-established branch-entry pair, so the
lowerer emits the change of stage at the adapter and every branch entering the
shared target agrees.  Redirect only the named branch; retain all other
branches and gotos unchanged.

| Redirect this branch | Through adapter | Adapter pair | Then goto |
|---|---|---|---|
| `LYRIC_DEST_BALANCE` → `LYRIC_FIELD_CLOSE_DISPATCH` | `LYRIC_DEST_CLOSE_PAIR` | `(ROMEO, PUCK)` | `LYRIC_FIELD_CLOSE_DISPATCH` |
| `LYRIC_FIELD_DRAIN_CLOSE` → `LYRIC_FIELD_TITLE_CAPTURE` | `LYRIC_FIELD_TITLE_ENTRY_PAIR` | `(HECATE, ROMEO)` | `LYRIC_FIELD_TITLE_CAPTURE` |
| `LYRIC_AUTOLINK_TEXT_OPEN` → `LYRIC_FIELD_HEAD` | `LYRIC_AUTOLINK_FIELD_HEAD_PAIR` | `(ROMEO, HECATE)` | `LYRIC_FIELD_HEAD` |
| `LYRIC_FIELD_LITERAL_EMIT` → `LYRIC_POP_GLYPH` | `LYRIC_FIELD_LITERAL_POP_PAIR` | `(JULIET, ROMEO)` | `LYRIC_POP_GLYPH` |
| `LYRIC_FIELD_TITLE_CLOSE` → `LYRIC_FIELD_UNTERMINATED` | `LYRIC_FIELD_UNTERMINATED_PAIR` | `(JULIET, PUCK)` | `LYRIC_FIELD_UNTERMINATED` |
| `LYRIC_FIELD_TITLE_CAPTURE` → `LYRIC_REQUEUE_OPEN` | `LYRIC_FIELD_TITLE_REQUEUE_PAIR` | `(PUCK, PROSPERO)` | `LYRIC_REQUEUE_OPEN` |
| `LYRIC_REQUEUE_DRAIN` → `LYRIC_POP_GLYPH` | `LYRIC_REQUEUE_POP_PAIR` | `(JULIET, ROMEO)` | `LYRIC_POP_GLYPH` |
| `LYRIC_EMPHASIS_COUNT_HOLD` → `LYRIC_EMPHASIS_SOURCE_END` | `LYRIC_EMPHASIS_SOURCE_END_PAIR` | `(PUCK, HECATE)` | `LYRIC_EMPHASIS_SOURCE_END` |
| `LYRIC_EMPHASIS_LITERAL_EMIT` → `LYRIC_POP_GLYPH` | `LYRIC_EMPHASIS_LITERAL_POP_PAIR` | `(JULIET, ROMEO)` | `LYRIC_POP_GLYPH` |
| `LYRIC_RESUME_CLOSE_DISPATCH` → `LYRIC_REGION_RESUME` | `LYRIC_REGION_RESUME_PAIR` | `(JULIET, PUCK)` | `LYRIC_REGION_RESUME` |

### A18 controlled reservation (ready to paste)

These ten working labels and four spares are the complete A18 pool.  The
spares are unavailable without a further planning amendment.  No adapter has
a `Pop`, so no Recall entry is required.

```toml
[scenes.LYRIC_DEST_CLOSE_PAIR]
title = "Romeo leads the balanced road to its true gate."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_TITLE_ENTRY_PAIR]
title = "Hecate brings the field-name to Romeo."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_FIELD_HEAD_PAIR]
title = "Romeo yields the shining road's first leaf to Hecate."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_LITERAL_POP_PAIR]
title = "Juliet returns the loose field-mark to Romeo."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_UNTERMINATED_PAIR]
title = "Juliet carries the unfinished field to Puck."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_TITLE_REQUEUE_PAIR]
title = "Puck bears the quiet field-name to Prospero."
pattern = "scene_of_character"
[scenes.LYRIC_REQUEUE_POP_PAIR]
title = "Juliet sends the requeued petal back to Romeo."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_SOURCE_END_PAIR]
title = "Puck brings the star's last mark to Hecate."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_LITERAL_POP_PAIR]
title = "Juliet returns the loose star-mark to Romeo."
pattern = "scene_of_character"
[scenes.LYRIC_REGION_RESUME_PAIR]
title = "Juliet carries the finished rose-path to Puck."
pattern = "scene_of_character"

# A18 spare pool — do not use without another planning amendment.
[scenes.LYRIC_FIELD_ENTRY_GUARD]
title = "The field's road keeps its faithful pair."
pattern = "bare_statement"
[scenes.LYRIC_REQUEUE_ENTRY_GUARD]
title = "The private path keeps its faithful pair."
pattern = "bare_statement"
[scenes.LYRIC_EMPHASIS_ENTRY_GUARD]
title = "The starry path keeps its faithful pair."
pattern = "bare_statement"
[scenes.LYRIC_REGION_ENTRY_GUARD]
title = "The rose-path keeps its faithful pair."
pattern = "bare_statement"
```

### Required proof before regeneration

Extend the existing A17 contract fixture rather than creating a second shape
test.  Its adapter-pair map must include all ten A18 working labels and their
exact pairs above; its spare set must include all four A18 guards.  Add a
focused entry-pair assertion that calls `entry_pairs(ACT3)` and verifies no
`IrError` is raised.  First run the test red on the current graph, then make
only the ledgered redirects and adapter scenes in `src_ir/act3.py` plus the
working TOML entries.

Run exactly:

```bash
uv run pytest tests/test_splc_validate.py tests/test_act3_contracts.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_splc_generated_fragments.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: PASS.  If another `entry_pairs` conflict appears, or any adapter
requires an operation beyond a terminal `goto`, record `BLOCK[plan]`; do not
consume an A18 spare, alter the validator, or hand-edit generated SPL.

## Amendment A19 (2026-07-14): source-aware goto staging and disconnected-entry bridges

The A18 graph validates and renders, but its generated SPL reaches a runtime
stage error.  The cause is a compiler contract that A18 did not cover:
`goto` transfers control immediately, so directions emitted after its speech
are unreachable; directions emitted before it may not remove the character
who must speak the jump.  The failed post-A18 experiment demonstrated both
halves (`Juliet is not on stage!` with post-goto directions, then `Puck is not
on stage!` with unconditional pre-goto directions).  This amendment changes
only splc's stage choreography and adds no Markdown, stack, token, selector,
or carrier behavior.

### Binding lowering contract

`entry_pairs()` remains the static stage pair at the first executable line of
a target scene.  A branch arrives with its source pair (hence A18's
normalization requirement).  A goto arrives with the target's recorded entry
pair.  For every goto with distinct source and entry pairs, lower the
directions **before** the jump sentence, choose a currently staged speaker
that survives into the entry pair, and then emit that speaker's jump.  Prefer
the source scene anchor when it survives; otherwise choose the surviving
source-pair member in declaration order.  Scene-start directions still adapt
the recorded entry pair to the target scene's own operation pair.

`validate.py` must reject every goto whose source pair and target entry pair
are disjoint, naming both labels and pairs.  It must make this check only
after branch entries and goto-only defaults have been established, so the
diagnostic describes the lowered graph rather than a partial traversal.
`lower.py` must consume the validated entry mapping; it must not recompute a
target pair or emit directions after any jump sentence.

### A19 disconnected-entry ledger

The following are the exhaustive disjoint goto edges in the current post-A18
Act III graph.  Each source is redirected to its `HEAD`; `HEAD` is a no-op
terminal-goto scene whose pair retains the source anchor and introduces the
first character of the target entry pair.  `TAIL` is another no-op
terminal-goto scene with the target entry pair and jumps to the original
target.  This creates two legal pre-jump handoffs without changing data.
The two `LYRIC_*_REQUEUE` sources share the same FIELD_RETRY chain.

| Redirect source goto(s) | HEAD pair | TAIL pair / original target |
|---|---|---|
| `LYRIC_CODE_TICKS` → `LYRIC_CODE_TICKS` | `LYRIC_GOTO_CODE_TICKS_HEAD` `(JULIET, ROMEO)` | `LYRIC_GOTO_CODE_TICKS_TAIL` `(ROMEO, PUCK)` → `LYRIC_CODE_TICKS` |
| `LYRIC_HTML_OPEN` → `LYRIC_HTML_OPEN_REQUEUE` | `LYRIC_GOTO_HTML_REQUEUE_HEAD` `(JULIET, PUCK)` | `LYRIC_GOTO_HTML_REQUEUE_TAIL` `(PUCK, ROMEO)` → `LYRIC_HTML_OPEN_REQUEUE` |
| `LYRIC_HTML_OPEN_REQUEUE`, `LYRIC_AUTOLINK_OPEN_REQUEUE` → `LYRIC_FIELD_RETRY` | `LYRIC_GOTO_FIELD_RETRY_HEAD` `(PUCK, HECATE)` | `LYRIC_GOTO_FIELD_RETRY_TAIL` `(HECATE, PROSPERO)` → `LYRIC_FIELD_RETRY` |
| `LYRIC_AUTOLINK_OPEN` → `LYRIC_AUTOLINK_OPEN_DUPLICATE` | `LYRIC_GOTO_AUTOLINK_DUP_HEAD` `(JULIET, LADY_MACBETH)` | `LYRIC_GOTO_AUTOLINK_DUP_TAIL` `(LADY_MACBETH, ROMEO)` → `LYRIC_AUTOLINK_OPEN_DUPLICATE` |
| `LYRIC_FIELD_RETRY` → `LYRIC_FIELD_OPEN` | `LYRIC_GOTO_FIELD_OPEN_HEAD` `(HECATE, ROMEO)` | `LYRIC_GOTO_FIELD_OPEN_TAIL` `(ROMEO, MACBETH)` → `LYRIC_FIELD_OPEN` |
| `LYRIC_FIELD_UNTERMINATED` → `LYRIC_FIELD_UNTERMINATED_LINK` | `LYRIC_GOTO_FIELD_UNTERMINATED_HEAD` `(PUCK, JULIET)` | `LYRIC_GOTO_FIELD_UNTERMINATED_TAIL` `(JULIET, HECATE)` → `LYRIC_FIELD_UNTERMINATED_LINK` |
| `LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD` → `LYRIC_EMPHASIS_SEEK` | `LYRIC_GOTO_EMPHASIS_SEEK_HEAD` `(ROMEO, PUCK)` | `LYRIC_GOTO_EMPHASIS_SEEK_TAIL` `(PUCK, HECATE)` → `LYRIC_EMPHASIS_SEEK` |

### A19 controlled reservation (ready to paste)

Add exactly these fourteen working labels to `src/30-act3-literary.toml`.
They are stage-only scenes: no Recall entries are required.  The five spares
are unavailable without a further planning amendment.

```toml
[scenes.LYRIC_GOTO_CODE_TICKS_HEAD]
title = "Juliet yields the silver mark to Romeo."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_CODE_TICKS_TAIL]
title = "Romeo bears the silver mark to Puck."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_HTML_REQUEUE_HEAD]
title = "Juliet carries the moonlit gate to Puck."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_HTML_REQUEUE_TAIL]
title = "Puck bears the moonlit gate to Romeo."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_FIELD_RETRY_HEAD]
title = "Puck leads the guarded field to Hecate."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_FIELD_RETRY_TAIL]
title = "Hecate bears the guarded field to Prospero."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_AUTOLINK_DUP_HEAD]
title = "Juliet gives the shining road to Lady Macbeth."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_AUTOLINK_DUP_TAIL]
title = "Lady Macbeth bears the shining road to Romeo."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_FIELD_OPEN_HEAD]
title = "Hecate opens the guarded field to Romeo."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_FIELD_OPEN_TAIL]
title = "Romeo brings the guarded field to Macbeth."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_FIELD_UNTERMINATED_HEAD]
title = "Puck carries the unfinished field to Juliet."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_FIELD_UNTERMINATED_TAIL]
title = "Juliet brings the unfinished field to Hecate."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_EMPHASIS_SEEK_HEAD]
title = "Romeo yields the wandering star to Puck."
pattern = "scene_of_character"
[scenes.LYRIC_GOTO_EMPHASIS_SEEK_TAIL]
title = "Puck bears the wandering star to Hecate."
pattern = "scene_of_character"

# A19 spare pool — do not use without another planning amendment.
[scenes.LYRIC_GOTO_FIELD_GUARD]
title = "The guarded field keeps its gentle passage."
pattern = "bare_statement"
[scenes.LYRIC_GOTO_REQUEUE_GUARD]
title = "The private path keeps its gentle passage."
pattern = "bare_statement"
[scenes.LYRIC_GOTO_EMPHASIS_GUARD]
title = "The wandering star keeps its gentle passage."
pattern = "bare_statement"
[scenes.LYRIC_GOTO_REGION_GUARD]
title = "The rose-path keeps its gentle passage."
pattern = "bare_statement"
[scenes.LYRIC_GOTO_LAST_GUARD]
title = "The last bright path keeps its gentle passage."
pattern = "bare_statement"
```

### Required implementation and proof

1. In `tests/test_splc_validate.py`, add a minimal two-scene mixed-entry act
   that makes a goto source anchor non-surviving but leaves its companion in
   the target entry pair.  Assert the lowered fragment orders the exit/enter
   directions before `Puck:`'s goto line and never gives that line to the
   exited anchor.  Add a disjoint-pair fixture that `validate()` rejects with
   both source and target labels.  Keep the existing mixed branch/goto test.
2. Update `scripts/splc/validate.py` and `scripts/splc/lower.py` to implement
   the binding contract; this is compiler behavior, not an Act III exception.
   Add the fourteen ledgered no-op scenes and only the seven listed source
   redirects in `src_ir/act3.py`, plus the fourteen working TOML entries.
   Extend the existing A17/A18 contract map with all A19 pairs and assert all
   five A19 spares are absent.
3. Run exactly:

```bash
uv run pytest tests/test_splc_validate.py tests/test_act3_contracts.py tests/test_splc_interpret_parity.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_token_dump.py::test_debug_target_dumps_integer_token_stream tests/test_splc_generated_fragments.py -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: the unit tests prove pre-jump staging and safe speaker selection;
the debug target produces integer output without a stage runtime error; all
generated-artifact and Amps gates pass.  Then, and only then, resume the
unchanged Task 4 Step 3 full spike evidence.  Any newly discovered disjoint
edge, a required data-moving bridge, or a failed carrier/byte invariant is a
new `BLOCK[plan]`; it does not authorize an A19 spare, a generated-SPL edit,
or an unplanned compiler rewrite.
