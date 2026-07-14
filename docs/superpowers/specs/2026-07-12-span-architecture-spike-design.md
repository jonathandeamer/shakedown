# Span Architecture Spike — Accepted Design

**Date:** 2026-07-12  
**Status:** accepted for implementation by plan `2026-07-12-span-architecture-spike.md`  
**Authority:** `docs/superpowers/specs/2026-07-11-completability-hardening-design.md` §4; architecture §4.3, §7.5, and §8.2.

## Decision

Act III will transform each eligible text-bearing block through a **one-way,
buffered span scan**. It reads a complete `PARA` glyph run from Puck, keeps
unconsumed source glyphs in a bounded work buffer above a private floor, and
writes only final output glyphs to Juliet. Generated HTML is output data: it
is never put back into the source buffer and is never reinterpreted as
Markdown. Act III continues to copy structural token codes, payloads, and
non-text leaves unchanged.

The work buffer has explicit region modes:

| Mode | Source boundary | Required treatment |
|---|---|---|
| code | matching backtick run of the same length | trim one balanced outer space pair, encode `&`, `<`, `>`, then emit `<code>…</code>` literally |
| escaped glyph | backslash followed by Markdown escapable punctuation | emit the following source glyph literally; do not treat it as a delimiter |
| inline HTML tag | `<` through its matching `>` outside code | copy the tag literally; do not turn its contents into emphasis or an entity |
| link/image | balanced `[]` label plus balanced destination/title syntax | scan label/alt text as a child source region, retain destination/title as protected literal fields, and emit the completed HTML only once |
| ordinary text | all other source glyphs | process in the fixed Markdown.pl order: amp/angle encoding, then strong, then emphasis |

Protection is therefore an Act-III work-buffer invariant, not a new final
block token. The final inter-act stream still contains `PARA(text)` with a
single `TEXT_END`, whose text has already become literal HTML glyphs. This
preserves the existing Act IV renderer and avoids introducing inline markers
that a block-level structural validator could mistake for children of a list
or quote.

## Boundaries and invariants

- A scan starts only for `TokenArity(..., has_text=True)` leaves. It never
  scans `CODE_BLOCK`, `RAW_HTML_HASH`, framing sentinels, token codes, or
  container payloads.
- A backtick opener is a maximal run. Only a later maximal run of the same
  length closes it; shorter runs are content. Multiple spans in a paragraph
  are separate regions.
- The input carrier sentinel is consumed exactly once when traversal reaches
  the end of the Act-II stream. At that point the borrowed Puck prefix is
  intact and Puck has no scan-source values above it. Act III then performs
  its required, distinct reverse handoff: it seeds a new `STREAM_END` on
  Puck and transfers the completed Juliet stream onto it for Act IV. Thus an
  Act-III exit necessarily has a non-empty Puck region above the borrowed
  prefix; that region is the output carrier, not a source buffer.
- The one-way rule is phase-scoped: before `LYRIC_OPEN_REVERSE`, no generated
  HTML may be pushed onto Puck. The only permitted Juliet-to-Puck transfer is
  `LYRIC_REVERSE_POP`, after that boundary, to establish the Act-III→Act-IV
  carrier. Requeuing original raw label/alt/emphasis glyphs and their private
  resume sentinel remains permitted before the boundary.
- Tests must snapshot the interpreter at entry to `LYRIC_OPEN_REVERSE` and
  prove Puck is exactly the borrowed prefix while Juliet owns the completed
  stream. They must separately inspect Act III's IR and allow
  `push(PUCK, val(JULIET))` only in `LYRIC_REVERSE_POP`; an empty-Puck
  assertion after Act III halts is invalid because it rejects the required
  handoff.
- The recognition order is exactly `_DoCodeSpans`, `_EscapeSpecialChars`,
  images, anchors, autolinks, amp/angle encoding, strong, emphasis, hard
  breaks. The spike implements only its stated probe forms, but it may not
  reorder them.
- The broad Slice 2 fixture scope remains unchanged. This spike may add only
  its named probes and minimal renderer support required to prove them.

## Probe corpus and oracle observations

The plan adds fixed inputs under
`tests/fixtures/architecture_spikes/spans/`, compares them byte-for-byte to
fresh `Markdown.pl`, and records the exact Act-III debug dump for each.

| Stem | Input | Architectural assertion |
|---|---|---|
| `variable_code_spans` | ```` `` a ` b `` and `x & <y>`\n ```` | equal-run matching, shorter embedded run, code encoding, and a second region |
| `escapes_and_overlap` | `\\*literal* and \\[bracket\\] \\`tick\\` and ***both***\n` | escapes suppress delimiters; strong runs before emphasis |
| `inline_html_and_autolink` | `<span>*raw*</span> and <http://example.com/a?x=1&y=2>\n` | an HTML tag is opaque while an autolink remains active and its URL is encoded once |
| `links_images_protected` | `[a *b*](http://e/x_(y) "t") and ![c *d*](img.png "i")\n` | balanced punctuation-rich fields survive; label/alt child scans may emphasize without destination/title rescanning |
| `overlapping_emphasis` | `***both*** and **outer *inner* outer**\n` | output nesting is `<strong><em>…</em></strong>` and strong precedes emphasis |

Each `.expected` file is generated from the local oracle before production
implementation and is a reviewed byte contract, not a checked-in mdtest
normalization surrogate.

## Rejected alternatives

- **Streaming toggle state over the original glyph stack:** cannot retain a
  variable backtick-run length, balanced link parentheses, or protected
  fields while preserving a deterministic fallback.
- **Emit HTML then run later span passes over it:** makes generated tags and
  attributes visible to escapes/emphasis/entity encoding and violates the
  protected-region requirement.
- **Persist inline markers in the block stream:** expands the recursive
  container grammar and Act IV dispatch before the spike has demonstrated a
  need. The buffered final-glyph result gives the same protection without
  destabilizing Spike B's accepted container stream.

## IR scene-capacity amendment (2026-07-13)

The one-way buffered design is unchanged. Its implementation is nevertheless
a scene-per-state `splc` control-flow graph: the validator requires each scene
to have exactly one non-anchor participant, and loop/count/replay transitions
cannot be collapsed into a single scene. The implementation plan therefore
must reserve controlled Act III titles at the observed density of the existing
link/reference scanner, before any IR change: 23 working plus six spare titles
for the Task 3 buffer/code/escape state machine, and 23 working plus six spare
titles for Task 4 protected regions and emphasis. These are capacity budgets,
not a broadened Markdown scope. If either pool proves insufficient, pause for
another planning amendment; implementation agents must not invent literary
surfaces or weaken the validator.

## Halt rule

Halt and reopen Act III's transformation model if any probe requires emitted
HTML to be re-read, if a protected source region cannot be restored without
losing bytes, if the scanner cannot consume its floor while preserving the
borrowed prefix, or if the reviewed Act-III dumps are structurally invalid.
Do not compensate by broadening Act IV or adding fixture-specific scenes.

## Carrier-safe protected-region amendment (2026-07-13)

This amendment is binding for Task 4 Step 2. It replaces the ambiguous
"private resume sentinel" wording in the original design and Amendment A2.
No new token code is allocated: a nested, private `TEXT_END` is the only
resume boundary placed on Puck. It is distinguishable from the paragraph's
real `TEXT_END` by an off-stage continuation record. The record lives above a
private `STREAM_END` on Lady Macbeth's stack; Hecate's value is only the
currently active field/call-site code. Therefore no scene uses Puck as a
field-output carrier or Juliet as requeued source.

### Binding ownership and floors

| Holder | Permitted Task 4 content | Floor / lifecycle |
|---|---|---|
| Puck | Unconsumed paragraph source; raw requeued label/alt/emphasis glyphs; nested private `TEXT_END` | The real paragraph `TEXT_END` remains lowest. A requeue pushes its private `TEXT_END`, then its raw glyphs in reverse order. No `STREAM_END`, HTML glyph sequence, or `val(JULIET)` is pushed before `LYRIC_OPEN_REVERSE`. |
| Juliet | Final forward token stream and final HTML glyphs only | Its existing Act-III `STREAM_END` is never popped by a protected-region scene. |
| Romeo | One raw field capture | Every `LYRIC_FIELD_OPEN` pushes one private `STREAM_END`; every success and fallback drains through that exact floor before its continuation. |
| Hecate stack | One reversed field ready for output | `LYRIC_FIELD_REV` first pushes its private `STREAM_END`; `LYRIC_FIELD_HEAD/NEXT` drains it exactly once. Amendment A7 makes Hecate's value the popped glyph register, not the call-site code. |
| Horatio | Raw link label, image alt, or emphasis body | One private `STREAM_END` per held region. It is drained only by `LYRIC_REGION_RESUME` / `LYRIC_EMPHASIS_RESUME` into Puck. |
| Lady Macbeth | Continuation records and the duplicate autolink field | Each record is `[STREAM_END, saved Hecate code, saved Macbeth delimiter length]`; autolink's duplicate buffer has a separate `STREAM_END` above that record. A continuation is popped before its next shared-field entry. |
| Macbeth value | Parenthesis depth while a destination is captured, or the matched emphasis run length | It is never used as a glyph register. `LYRIC_EMPHASIS_*` must not overwrite it between `MATCH` and the corresponding close. |

The checked IR-shape test must reject any pre-handoff `Push(PUCK, ...)` that
is not `val(PUCK)`, `val(ROMEO)`, `val(HORATIO)`, `const(TEXT_END)`, or a
raw delimiter constant (`*`/`_`) used solely to construct the triple-emphasis
child. It must retain the singleton `Push(PUCK, val(JULIET))` allowance in
`LYRIC_REVERSE_POP` only.

### Continuation codes and resume rule

Use these small values with named constants local to `act3.py`: callers set
`FIELD_*` in Hecate only long enough for `LYRIC_FIELD_RETRY` to copy it to
Prospero; `RESUME_*` remains in Hecate until `LYRIC_RESUME_DISPATCH` freezes
it in Prospero:
`FIELD_TAG=1`, `FIELD_AUTO_HREF=2`, `FIELD_AUTO_TEXT=3`,
`FIELD_LINK_DEST=4`, `FIELD_LINK_TITLE=5`, `FIELD_IMAGE_DEST=6`,
`FIELD_IMAGE_TITLE=7`, `RESUME_LINK=8`, `RESUME_IMAGE=9`,
`RESUME_EMPH=10`, and `RESUME_TRIPLE_EMPH=11`. Values are state tags, not
token codes. Each branch into a shared `LYRIC_FIELD_*` scene must set exactly
one field tag first and enter `LYRIC_FIELD_RETRY`. `LYRIC_POP_GLYPH` handles a
popped `TEXT_END` as follows:

1. if Hecate is one of `RESUME_*`, jump to `LYRIC_RESUME_DISPATCH` without
   emitting or copying the zero; pop the Lady-Macbeth continuation record;
2. otherwise it is the real paragraph terminator and follows the existing
   `TRAVERSE_COPY_TERMINATOR` path.

`LYRIC_RESUME_DISPATCH` is the sole owner of a requeue completion. It restores
the saved Hecate/Macbeth values before taking the link/image/emphasis close
continuation. A nested requeue saves its parent record first, so a child
emphasis can return to a label or outer emphasis without confusing the real
paragraph terminator.

### Required scene choreography

The plan's implementation table is intentionally scene-level: an implementer
may split a listed transition only by consuming an unused Amendment A2 spare
and recording it in the plan, but may not merge holders or invent another
carrier. All `FIELD_*` rows below preserve the pair conventions already
validated by splc: source/capture rows use `(ROMEO, PUCK)`, capture/reverse
rows use `(ROMEO, HECATE)`, output rows use `(JULIET, HECATE)`, and hold rows
use `(HORATIO, PUCK)` or `(HORATIO, LADY_MACBETH)`.

| Entry / scene family | Exact state transition and carrier effect |
|---|---|
| `LYRIC_ANGLE_TEST` → `LYRIC_HTML_OPEN` / `LYRIC_AUTOLINK_OPEN` | After `<` is popped, consume one lookahead. `http`, `https`, and `ftp` probe prefixes take the autolink path; every other probe form takes opaque tag mode. Seed Romeo with `STREAM_END`; retain `<` only for tag mode and retain no angle brackets for an autolink. A failed probe replays only captured raw source plus `<` to Juliet, then resumes ordinary scan. |
| `LYRIC_FIELD_OPEN`, `SCAN`, `UNTERMINATED` | `OPEN` creates Romeo's floor. `SCAN` pops only Puck and pushes non-terminators to Romeo. Tag mode stops at and captures `>`; URL mode stops at but does not capture `>`; destination mode increments/decrements Macbeth on `(`/`)` and stops only when the outer depth returns to zero; title mode stops at its opening quote's mate. `UNTERMINATED` drains Romeo to Juliet as literal source, restores the private boundary if it was consumed, and never jumps to a generated-output scene. |
| `LYRIC_FIELD_RETRY`, `REV_KEEP`, `REV`, `HEAD`, `GLYPH`, `PLAIN`, `AMP/LT/GT`, `NEXT`, `DRAIN_CLOSE` | `RETRY` copies the caller's Hecate tag to Prospero. Reverse Romeo onto Hecate's private-floor stack. In `FIELD_AUTO_HREF`, also copy each popped raw glyph to Lady Macbeth's duplicate-floor stack. `HEAD/NEXT` drain Hecate to Juliet; tag mode uses `PLAIN` only, all other modes use the existing entity triples. `DRAIN_CLOSE` dispatches solely by Prospero's unchanged field tag. |
| Autolink close | `FIELD_AUTO_HREF` emits `<a href=\"`, drains the first field, emits `\">`, restores the duplicate into Hecate through the same reverse/head family under `FIELD_AUTO_TEXT`, drains it as text, emits `</a>`, then resumes Puck. The closing `>` was consumed once and is never pushed to Juliet. |
| `LYRIC_LINK_REGION` / `LYRIC_IMAGE_TEST` → `LYRIC_LABEL_OPEN` / `LYRIC_ALT_OPEN` | A `[` or `![` starts Horatio's private floor. Capture raw label/alt through its matching `]`; reject missing `]` or `(` by replaying the exact raw opener and held bytes literally. On success, push a Lady-Macbeth continuation record (`RESUME_LINK` or `RESUME_IMAGE`) before entering destination capture. |
| `LYRIC_DEST_OPEN`, `DEST_BALANCE`, `LYRIC_TITLE_OPEN` | Emit `<a href=\"` or `<img src=\"` to Juliet before `FIELD_LINK_DEST` / `FIELD_IMAGE_DEST`. Balanced destination capture owns Macbeth depth. A quoted title sets the matching title field code; no title goes directly to `LYRIC_REGION_TAG_OPEN`. Destination/title glyphs remain opaque except the shared field's required entity encoding. |
| `LYRIC_REGION_TAG_OPEN` → `LYRIC_REGION_RESUME` | After the final destination/title drain, emit `\">` for link or `\" alt=\"` for image as appropriate; for images emit the held-alt attribute closing and optional title before ` />`. Before rescanning the held label/alt, push one private `TEXT_END` to Puck, drain Horatio to Puck (raw values only), set Hecate to the saved `RESUME_*`, and jump to `LYRIC_POP_GLYPH`. At that boundary, `LYRIC_RESUME_DISPATCH` emits `</a>` or the image suffix and restores the previous continuation. |
| `LYRIC_EMPHASIS_OPEN` through `MATCH` | Count a maximal `*` or `_` opener in Hecate only until a match is found; copy the matched length into Macbeth before changing Hecate to a resume state. Capture raw body to Horatio under a private floor. Candidate mismatch replay restores only raw delimiter glyphs to the current body capture. |
| `LYRIC_EMPHASIS_RESUME` / close | Emit `<strong>` for a two-run or the outer layer of a three-run, otherwise `<em>`. Save the parent continuation, push one private `TEXT_END`, and requeue Horatio's raw body. For a three-run, surround the requeued raw body with one synthetic raw delimiter pair; this is a control delimiter, not generated HTML, and makes the ordinary scan produce the nested `<em>`. `LYRIC_RESUME_DISPATCH` restores Macbeth, emits the matching `</em>` or `</strong>`, then returns to the saved parent / ordinary scan. |
| `LYRIC_REGION_FALLBACK`, `LYRIC_EMPHASIS_FALLBACK`, `REPLAY` | Drain only the relevant private capture to Juliet as literal raw Markdown and then resume Puck. The fallback must consume every temporary `STREAM_END`; it must not leave a Romeo/Horatio/Lady-Macbeth floor for the next paragraph. |

This choreography is valid only if a focused interpreter test observes each
private Puck `TEXT_END` transition and proves that its next scene is
`LYRIC_RESUME_DISPATCH`, while the real paragraph terminator reaches
`TRAVERSE_COPY_TERMINATOR`. That test is the carrier-validity gate before
the production implementation is considered complete.

## A4 reconstruction sequence (2026-07-13)

The first Task 4 Step 2 attempt is evidence that the former per-feature
implementation shape is not a viable incremental starting point: it leaks a
`TEXT_END` into the completed paragraph carrier, lacks the three shared A4
families, and lets its emphasis close branch inspect a glyph-clobbered value.
Those scenes are not a partial implementation of this design. Preserve that
uncommitted WIP for diagnosis, but do not extend, rename, or merge it into the
shipping Act III graph.

The replacement must be reconstructed in this order, with the A4 observer
gate kept enabled throughout:

1. From the committed Task 3 graph, install the A4 verification observer and
   the exact `LYRIC_FIELD_OPEN`, `LYRIC_FIELD_DRAIN_CLOSE`, and
   `LYRIC_RESUME_DISPATCH` scene labels from the Amendment A2 reservation.
   No retired `LYRIC_HTML_*`, `LYRIC_LABEL_SCAN`, `LYRIC_DESTINATION_*`, or
   `LYRIC_EMPHASIS_EMIT_*` scene may remain reachable.
2. Build the shared field pipeline completely before routing any Markdown
   opener into it: Romeo floor and capture; Hecate reverse/output floor;
   entity/plain drain; and field-tag-only close dispatch. A successful field
   exits only through `LYRIC_FIELD_DRAIN_CLOSE`; an unsuccessful field drains
   its own Romeo floor literally and restores its consumed source boundary.
3. Add angle/tag/autolink routing, then link/image capture and requeue, then
   emphasis requeue. Each caller must set its field or resume code before the
   shared scene entry. Each requeue writes one Lady-Macbeth record before its
   Puck-private `TEXT_END`, and only `LYRIC_RESUME_DISPATCH` may consume that
   boundary.
4. Do not write a direct emphasis body-emitter. `MACBETH` retains the matched
   delimiter run while ordinary scanning processes the requeued raw body; the
   resume dispatcher, after restoring the parent record, emits the close.
   This removes the failed `LYRIC_EMPHASIS_EMIT_CLOSE` value-clobber path.

The first runnable checkpoint after reconstruction is not output parity. It
is the three protected probes traversing exactly one real paragraph terminator
and every private terminator through the resume dispatcher, without underflow
or a stray `TEXT_END` in the decoded carrier. Only after that checkpoint is
green may the implementation refine output differences or add a reserved
spare scene. This sequence consumes only the Amendment A2 working pool and
its ten recorded spares; new literary prose still requires a planning
amendment.

## A6 continuation-record reset and event-order gate (2026-07-13)

This clears the second Task 4 Step 2 planning blocker. The uncommitted attempt
still combines a partial A4 graph with retired flow: it consumes Lady Macbeth
at `LYRIC_RESUME_RESTORE_MACBETH` without a record, while its altered ordinary
terminator route underflows Puck on `escapes_and_overlap`. These are carrier
failures, not output-parity defects. Preserve the WIP unchanged as diagnostic
evidence; do not repair it in place or copy production scenes from it.

### Reset and continuation-record protocol

In an isolated worktree, reconstruct from committed Task 3 `src_ir/act3.py`.
Before connecting a protected opener, the Task 1--3 contracts (including
`escapes_and_overlap`) must pass.

Every requeue creates exactly one Lady-Macbeth record, above older contents:

```text
push(LADY_MACBETH, STREAM_END)       # record floor
push(LADY_MACBETH, val(HECATE))      # parent field/resume state
push(LADY_MACBETH, val(MACBETH))     # parent delimiter/depth
let(HECATE, RESUME_*)                # only after saving both parent values
push(PUCK, TEXT_END)                 # then create the private boundary
```

Drain raw Horatio content to Puck above that boundary. An autolink duplicate
has its own floor above all records and is fully drained before any record is
created. Titles and transient field values never occupy the continuation
region.

Only `LYRIC_RESUME_DISPATCH` consumes a record, in this order:

```text
let(PROSPERO, val(HECATE))           # freeze the RESUME_* close choice
pop(LADY_MACBETH) -> MACBETH
pop(LADY_MACBETH) -> HECATE
pop(LADY_MACBETH) == STREAM_END      # consume and verify the record floor
branch(PROSPERO, RESUME_* close)     # close scenes do not pop Lady Macbeth
goto(LYRIC_POP_GLYPH)
```

Thus nested requeues restore a parent `RESUME_*` and the next private
terminator resumes that parent. The real paragraph terminator is never
preceded by `RESUME_*`; after its existing `LYRIC_POP_GLYPH` pop it proceeds
directly to `TRAVERSE_COPY_TERMINATOR`. Do not insert an intermediate
terminator scene or perform a second Puck pop.

### Binding observer event contract

The observer records scene entry plus each Puck pop with its active scene and
Hecate value. For every `TEXT_END` popped by `LYRIC_POP_GLYPH`, assert the
next scene is `LYRIC_RESUME_DISPATCH` when Hecate is `RESUME_*`, otherwise
`TRAVERSE_COPY_TERMINATOR`. Each protected probe has exactly one non-resume
real terminator and zero or more private terminators. Each resume must consume
one complete three-pop Lady-Macbeth record; no other Lady-Macbeth pop is
allowed except the declared autolink-duplicate drain. This event-order test
replaces any loose ``labels contains`` assertion.

At the first production checkpoint run:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q
```

It must pass with no underflow, scene fall-through, carrier decode error,
duplicate real terminator, or leaked `TEXT_END`. Any failure is a
`BLOCK[plan]`, not permission for a recovery scene or spare title.

## A7 field-tag holder and two-character restore adapters (2026-07-13)

A6 is amended because `pop(HECATE)` changes Hecate's value: Hecate cannot
retain a `FIELD_*` tag through `LYRIC_FIELD_HEAD` / `LYRIC_FIELD_NEXT`.
Prospero owns the active field tag from field entry through
`LYRIC_FIELD_DRAIN_CLOSE`; after that close selects its continuation the tag
is dead. Hecate owns only a drained field glyph or the active `RESUME_*`
before a private `TEXT_END`. At resume, Prospero is safely overwritten with
the frozen close code. Thus the two Prospero uses never overlap.

Every field caller sets Hecate to its `FIELD_*` code then enters the
already-reserved `LYRIC_FIELD_RETRY`, pair `(HECATE, PROSPERO)`:

```text
let(PROSPERO, val(HECATE))
goto(LYRIC_FIELD_OPEN)
```

All shared field scan, reverse, entity/plain, duplicate, and drain-close
branches inspect off-stage `val(PROSPERO)`; none copies the tag back to
Hecate. This consumes `LYRIC_FIELD_RETRY` from A2's spare pool.

The A6 resume is split into these binding adapters, because a Lady-Macbeth
pop leaves its result on Lady Macbeth before a later two-character scene can
copy it to its destination:

```text
# LYRIC_RESUME_DISPATCH (HECATE, PROSPERO)
let(PROSPERO, val(HECATE)); goto(LYRIC_RESUME_POP_MACBETH)
# LYRIC_RESUME_POP_MACBETH (LADY_MACBETH, ROMEO)
pop(LADY_MACBETH); goto(LYRIC_RESUME_RESTORE_MACBETH)
# LYRIC_RESUME_RESTORE_MACBETH (LADY_MACBETH, MACBETH)
let(MACBETH, val(LADY_MACBETH)); goto(LYRIC_RESUME_POP_HECATE)
# LYRIC_RESUME_POP_HECATE (LADY_MACBETH, ROMEO)
pop(LADY_MACBETH); goto(LYRIC_RESUME_RESTORE_HECATE)
# LYRIC_RESUME_RESTORE_HECATE (LADY_MACBETH, HECATE)
let(HECATE, val(LADY_MACBETH)); goto(LYRIC_RESUME_VERIFY_FLOOR)
# LYRIC_RESUME_VERIFY_FLOOR (LADY_MACBETH, ROMEO)
pop(LADY_MACBETH); branch(non-STREAM_END, LYRIC_RESUME_FLOOR_FAIL)
branch(val(PROSPERO), RESUME_* close scenes)
```

`LYRIC_RESUME_FLOOR_FAIL` is terminal (`halt_act()`), forbidden on valid
probes. Close scenes branch only on frozen off-stage Prospero, pop no Lady
Macbeth value, and return to `LYRIC_POP_GLYPH`. This preserves A6's semantic
order: freeze; restore Macbeth; restore Hecate; consume/verify floor; close.

A7 supersedes A6's no-spare rule only for the six exact labels below. Together
with `LYRIC_FIELD_RETRY`, this allocates seven of A2's ten spares; the other
three stay reserved. No other holder, sentinel, Recall phrase, or label is
authorized.

```toml
[scenes.LYRIC_RESUME_POP_MACBETH]
title = "Lady Macbeth lifts the first held stone."
pattern = "scene_of_character"
[scenes.LYRIC_RESUME_RESTORE_MACBETH]
title = "Macbeth receives the first held stone."
pattern = "cross_character"
[scenes.LYRIC_RESUME_POP_HECATE]
title = "Lady Macbeth lifts the second held stone."
pattern = "scene_of_character"
[scenes.LYRIC_RESUME_RESTORE_HECATE]
title = "Hecate receives the second held stone."
pattern = "cross_character"
[scenes.LYRIC_RESUME_VERIFY_FLOOR]
title = "Lady Macbeth tests the record's bedrock."
pattern = "scene_of_character"
[scenes.LYRIC_RESUME_FLOOR_FAIL]
title = "The broken record leaves no road behind."
pattern = "bare_statement"
```

At the first production checkpoint run:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q
```

It must prove this adapter order, exactly three Lady-Macbeth pops, no
`LYRIC_RESUME_FLOOR_FAIL`, and A6's real/private terminator contract. After
each Act III/TOML edit also run the plan's exact literary gate.

## A8 source-end and requeue-drainer correction (2026-07-13)

The preserved A7 diagnostic graph establishes a narrower, reproducible fault:
`LYRIC_FIELD_SCAN` and `LYRIC_EMPHASIS_SEEK` treat a popped real `TEXT_END`
as though it were a malformed private continuation.  Their fail route then
returns to a scene which pops Puck again.  On the link/image and overlapping
emphasis probes that is a pop below Puck's paragraph floor.  This is not a
new terminator kind and must not be patched by adding a recovery pop.

The following protocol supersedes A4's field-unterminated and A2's generic
requeue wording.  It keeps all A4/A6/A7 ownership rules and the A7 restore
adapters intact.

### Binding source-end rule

Every scene that directly `pop(PUCK)` while it owns a temporary field or
emphasis capture must branch on `TEXT_END` *before* it pushes, counts, or
dispatches the popped value.  That branch enters the relevant source-end
unwind.  The unwind must:

1. push that same `TEXT_END` back onto Puck exactly once;
2. make no further `pop(PUCK)` before returning to `LYRIC_POP_GLYPH`;
3. drain its own private capture floor as literal source to Juliet in original
   order, including its consumed opener/delimiters; and
4. consume every Romeo/Horatio private `STREAM_END` it created.

The next top-level pop therefore sees the restored real terminator and takes
only `TRAVERSE_COPY_TERMINATOR`.  `LYRIC_RESUME_FLOOR_FAIL` remains reserved
for a malformed Lady-Macbeth record and is forbidden as a field/emphasis
source-end target.

### Binding field, title, and raw-requeue choreography

The scene table below is the complete correction.  `FIELD_LINK_DEST` and
`FIELD_IMAGE_DEST` own the source `)` that closes the destination; a quoted
title is entered only after the destination drain and owns its matching quote,
then verifies and consumes the following `)`.  The final `)` is never put on
Romeo, Horatio, or Puck.  A missing quote or `)` takes the source-end/literal
unwind above.

| Family | Required operations and next scene |
|---|---|
| `LYRIC_FIELD_SCAN` | Pop Puck once. `TEXT_END -> LYRIC_FIELD_SOURCE_END`. Otherwise test the active Prospero field tag's terminator before capture. A matching tag/destination/title terminator enters `LYRIC_FIELD_CLOSE_DISPATCH`; every other raw glyph is pushed to Romeo exactly once. |
| `LYRIC_FIELD_SOURCE_END` | Push `TEXT_END` back to Puck; move Romeo's capture through its private floor into the literal-reverse family; emit the caller's saved raw opener before the reversed capture; then `goto(LYRIC_POP_GLYPH)`. It never targets a resume scene. |
| destination/title hand-off | After a successful destination drain, inspect only the next source glyph: `)` emits the attribute transition; space followed by `"` sets the corresponding title tag and enters the shared field pipeline; all other glyphs are restored and use `LYRIC_FIELD_SOURCE_END`. After a title drain, consume exactly one `)` or take the same literal unwind. |
| `LYRIC_REQUEUE_OPEN` | Before touching Horatio: push Lady Macbeth's `[STREAM_END, parent Hecate, parent Macbeth]` record; set Hecate to the child `RESUME_*`; push Puck's private `TEXT_END`; then `goto(LYRIC_REQUEUE_DRAIN)`. The record is created before the private Puck boundary. |
| `LYRIC_REQUEUE_DRAIN` | Pop Horatio. If it is the Horatio `STREAM_END`, consume it and `goto(LYRIC_POP_GLYPH)` without pushing it to Puck. Otherwise push `val(HORATIO)` to Puck and loop. Because Horatio is popped last-to-first above a Puck floor, the next Puck pop is the first captured raw glyph. |
| `LYRIC_EMPHASIS_SEEK` | Pop Puck once. `TEXT_END -> LYRIC_EMPHASIS_SOURCE_END`; a nonmatching candidate delimiter is copied as raw source into Horatio and the seek continues; no candidate path writes a delimiter directly to Juliet or Puck. A matching maximal run is copied to Macbeth before any requeue state is set. |
| `LYRIC_EMPHASIS_SOURCE_END` | Push the real `TEXT_END` back to Puck; literal-reverse the opener plus Horatio body to Juliet; consume Horatio's floor; `goto(LYRIC_POP_GLYPH)`. No Lady-Macbeth record exists on this path. |
| matched emphasis requeue | Emit the outer opener chosen from Macbeth, then use `LYRIC_REQUEUE_OPEN` / `LYRIC_REQUEUE_DRAIN`. For a three-run, push the synthetic closing raw delimiter to Puck immediately after the private `TEXT_END`, drain Horatio, then push the synthetic opening delimiter immediately before entering the drain's completion. This makes the requeued source order `*`, body, `*`, private `TEXT_END`; the child ordinary scan emits `<em>`, and the restored parent emits `</strong>`. |

No new numeric sentinel, holder, or Recall phrase is introduced.  The source
end is a real paragraph `TEXT_END`; the requeue end is a private `TEXT_END`
whose preceding `RESUME_*` causes the existing A7 restore graph to run.

### A8 literary reservation (ready to paste)

The three uncommitted A2 spare labels used by the diagnostic attempt are
retired along with that attempt.  This correction has 10 working scenes and
four spares (40%, above the mandatory 20% floor).  Add only labels reached by
the reconstructed IR; do not reuse a retired A2 spare or invent prose.

```toml
# src/30-act3-literary.toml — Amendment A8 correction pool
[scenes.LYRIC_FIELD_SOURCE_END]
title = "The field returns its lost gate to morning."
pattern = "bare_statement"
[scenes.LYRIC_FIELD_LITERAL_REVERSE]
title = "Romeo turns the unclosed field toward daylight."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_LITERAL_EMIT]
title = "Juliet lets the unclosed field pass whole."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_TITLE_TEST]
title = "Romeo asks whether the road keeps a name."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_TITLE_CLOSE]
title = "The road's quiet name meets its round gate."
pattern = "bare_statement"
[scenes.LYRIC_REQUEUE_OPEN]
title = "Horatio prepares the held petals for return."
pattern = "scene_of_character"
[scenes.LYRIC_REQUEUE_DRAIN]
title = "Horatio sends one held petal back to Puck."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_SOURCE_END]
title = "The unpaired star returns before the hedge."
pattern = "bare_statement"
[scenes.LYRIC_EMPHASIS_LITERAL_REVERSE]
title = "Romeo turns the loose starlight home."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_LITERAL_EMIT]
title = "Juliet lets the loose starlight pass unchanged."
pattern = "scene_of_character"

# Amendment A8 spare pool — do not use without recording its exact transition.
[scenes.LYRIC_FIELD_TITLE_RESTORE]
title = "Romeo restores the road's waiting mark."
pattern = "scene_of_character"
[scenes.LYRIC_REQUEUE_TRIPLE_CLOSE]
title = "Horatio lays the star beneath the held petals."
pattern = "scene_of_character"
[scenes.LYRIC_REQUEUE_TRIPLE_OPEN]
title = "Horatio crowns the held petals with a star."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_LITERAL_CLOSE]
title = "The loose star comes safely into daylight."
pattern = "bare_statement"
```

### A8 mandatory first checkpoint

Before any byte-parity adjustment, extend the observer contract and run:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q
```

The test must record, for every protected fixture, that a scanner-owned real
`TEXT_END` is restored then reaches `TRAVERSE_COPY_TERMINATOR` on the next
top-level pop; that each private requeue terminator reaches the A7 restore
sequence; that `LYRIC_FIELD_SOURCE_END` and `LYRIC_EMPHASIS_SOURCE_END` make
no second Puck pop; and that neither `LYRIC_FIELD_SCAN` nor
`LYRIC_EMPHASIS_SEEK` underflows.  Failure is a fresh `BLOCK[plan]`.

## A9 continuation ownership and field-capture separation (2026-07-13)

The A8 reconstruction reached the intended private boundaries but fails the
carrier gate in three reproducible ways: a triple-emphasis requeue drains
Puck below its floor, a link/image destination later underflows Romeo at
`LYRIC_FIELD_REV`, and the observer sees `-1` or a changed code at a resume
close.  These are one ownership error, not three output defects.  A8 leaves
the live `RESUME_*` selector in Hecate even though ordinary child scanning
legitimately clobbers Hecate; it also permits planned close HTML to share
Romeo with a field capture.  The current WIP is diagnostic evidence only.
Do not repair it in place: reconstruct Task 4 Step 2 from committed Task 3
under the rules below.

### Binding lifetime model

`LADY_MACBETH`'s **value**, not Hecate's value, is the sole live private
continuation selector.  It is `CONT_NONE=0` outside a requeue and exactly one
of `RESUME_LINK=8`, `RESUME_IMAGE=9`, `RESUME_EMPH=10`, or
`RESUME_TRIPLE_EMPH=11` while raw requeued glyphs sit above Puck's private
`TEXT_END`.  Hecate remains a disposable field glyph/count register; Prospero
continues to own a field tag and, during resume only, the frozen child close
code.  Horatio's value is a restore scratch only after its held stack reaches
its private floor.

Each continuation record is pushed in this exact order (bottom to top):

```text
push(LADY_MACBETH, STREAM_END)          # record floor
push(LADY_MACBETH, val(HECATE))         # parent Hecate
push(LADY_MACBETH, val(MACBETH))        # parent Macbeth
push(LADY_MACBETH, val(LADY_MACBETH))   # parent continuation selector
let(LADY_MACBETH, RESUME_*)             # child selector
push(PUCK, TEXT_END)                    # child private boundary
```

`LYRIC_POP_GLYPH` must branch on `TEXT_END` *before* any continuation-code
test, to `LYRIC_TEXT_END_DISPATCH`.  That scene tests only
`val(LADY_MACBETH)`: a `RESUME_*` value enters `LYRIC_RESUME_DISPATCH`; only
`CONT_NONE` enters `TRAVERSE_COPY_TERMINATOR`.  It performs no pop.  This
supersedes A6's direct-pop-to-resume rule; it eliminates the false-positive
square-plus-register test and makes the selector's lifetime explicit.

The resume family is binding:

```text
LYRIC_RESUME_DISPATCH:
    let(PROSPERO, val(LADY_MACBETH))        # freeze child close selector
    goto(LYRIC_RESUME_POP_PARENT_SELECTOR)
LYRIC_RESUME_POP_PARENT_SELECTOR:
    pop(LADY_MACBETH)
    goto(LYRIC_RESUME_SAVE_PARENT_SELECTOR)
LYRIC_RESUME_SAVE_PARENT_SELECTOR:
    let(HORATIO, val(LADY_MACBETH))         # held stack is already drained
    goto(LYRIC_RESUME_POP_MACBETH)
# retain A7's pop/restore Macbeth, pop/restore Hecate, and floor verification
LYRIC_RESUME_VERIFY_FLOOR:
    pop(LADY_MACBETH); branch(non-STREAM_END, LYRIC_RESUME_FLOOR_FAIL)
    goto(LYRIC_RESUME_RESTORE_PARENT_SELECTOR)
LYRIC_RESUME_RESTORE_PARENT_SELECTOR:
    let(LADY_MACBETH, val(HORATIO))
    goto(LYRIC_RESUME_CLOSE_DISPATCH)
LYRIC_RESUME_CLOSE_DISPATCH:
    branch(val(PROSPERO), RESUME_* close scenes)
```

Close scenes inspect only frozen Prospero, emit their literal close directly
to Juliet, and return to `LYRIC_POP_GLYPH`.  They never pop Romeo, Horatio,
or Lady Macbeth.  A nested requeue therefore restores the parent selector
before its later private `TEXT_END`; the real paragraph terminator always sees
`CONT_NONE`.

### Binding field and requeue restrictions

- Romeo is a field-capture stack only between `LYRIC_FIELD_OPEN` and the
  matching `LYRIC_FIELD_DRAIN_CLOSE`/literal unwind.  No `_stack_text(ROMEO,
  ...)`, deferred close, label output, or resume scene may use it.  Successful
  link/image resume closes emit `</a>` or the image suffix directly from the
  frozen Prospero code; `LYRIC_REGION_RESUME` must not pop Romeo.
- `FIELD_TAG` has its own drain-close branch: emit the consumed literal `>`
  and return to the ordinary scan.  `FIELD_AUTO_HREF` alone starts the
  duplicate-text drain; neither tag nor autolink may fall through to title or
  link/image completion.
- `LYRIC_REQUEUE_DRAIN` pushes each non-floor Horatio glyph to Puck exactly
  once.  The triple-emphasis path may add only its one synthetic opening and
  one synthetic closing `*`, positioned as A8 specifies; it must never
  duplicate a held raw glyph.  The Horatio floor is consumed and is never
  copied to Puck.
- Before every `LYRIC_FIELD_REV`, assert by construction that the immediately
  preceding `LYRIC_FIELD_OPEN` pushed Romeo's private `STREAM_END` and no
  non-field code has popped Romeo.  A destination/title transition that needs
  a later close uses the continuation record, not Romeo.

### A9 mandatory reconstruction checkpoint

First add/update the observer contract, then reconstruct the protected graph
from Task 3 and run this gate before adjusting any output bytes:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q -k \
  "protected_modes_do_not_underflow or pre_handoff_source_is_empty_and_output_is_forward or text_end_event_order_is_carrier_safe"
```

It must pass all eleven selected cases.  The observer must prove: every
`LYRIC_POP_GLYPH` `TEXT_END` enters `LYRIC_TEXT_END_DISPATCH`; each private
boundary then enters the complete A9 resume adapter and freezes a `RESUME_*`
code unchanged through the close; exactly one final boundary enters
`TRAVERSE_COPY_TERMINATOR` with `CONT_NONE`; every field reverse has one
Romeo floor; and each requeue drains every raw Horatio glyph once.  A failure
is a `BLOCK[plan]`; it does not authorize a recovery pop, a new token code,
or an unreserved scene.

After each Act III/TOML edit, also run the plan's exact literary gate:

```bash
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
```

### A9 literary reservation (ready to paste)

This correction needs five working labels and three spares.  It does not add a
Recall phrase.  Add only reached working labels; do not use a spare without a
new planning amendment.

```toml
[scenes.LYRIC_TEXT_END_DISPATCH]
title = "Lady Macbeth names the returning garden gate."
pattern = "scene_of_character"
[scenes.LYRIC_RESUME_POP_PARENT_SELECTOR]
title = "Lady Macbeth lifts the hidden path's sign."
pattern = "scene_of_character"
[scenes.LYRIC_RESUME_SAVE_PARENT_SELECTOR]
title = "Horatio keeps the elder path's sign."
pattern = "scene_of_character"
[scenes.LYRIC_RESUME_RESTORE_PARENT_SELECTOR]
title = "Lady Macbeth receives the elder path's sign."
pattern = "cross_character"
[scenes.LYRIC_RESUME_CLOSE_DISPATCH]
title = "Prospero chooses the garden's closing gate."
pattern = "scene_of_character"

# A9 spare pool — do not use without another planning amendment.
[scenes.LYRIC_FIELD_REVERSE_GUARD]
title = "Romeo finds the field's rooted stone."
pattern = "scene_of_character"
[scenes.LYRIC_REQUEUE_SINGLE_KEEP]
title = "Horatio returns one petal without echo."
pattern = "scene_of_character"
[scenes.LYRIC_RESUME_PARENT_FAIL]
title = "The elder path refuses a broken sign."
pattern = "bare_statement"
```

## A10 image-title ordering and nested-floor correction (2026-07-14)

The A2 field table incorrectly said that every destination and title drains to
Juliet before the held label/alt requeue.  That preserves source order for a
link (`href`, `title`, then label), but cannot preserve Markdown.pl's image
attribute order.  The checked oracle contract for
`links_images_protected.expected` requires:

```html
<img src="img.png" alt="c <em>d</em>" title="i" />
```

The image alt is source-earlier than its title but is emitted only after the
destination.  Therefore `FIELD_IMAGE_TITLE` is the sole field mode that must
defer its successful drain until after the alt requeue.  This correction
supersedes A2's universal immediate-title-drain wording and A9's categorical
ban on a resume close using Romeo; all other A2/A9 ownership rules remain
binding.

### Binding image-title choreography

1. `LYRIC_TITLE_OPEN` captures an image title exactly as the shared field
   scanner otherwise would: it pushes Romeo's private `STREAM_END`, captures
   raw title glyphs above it, consumes the matching quote and final `)`, and
   validates the source-end/literal-unwind path.  For `FIELD_IMAGE_TITLE` it
   **does not** enter `LYRIC_FIELD_RETRY`, `REV`, or any Juliet-emission
   scene at capture time.  The title floor remains intact and Romeo is then
   quiescent.
2. `LYRIC_REGION_TAG_OPEN` emits `" alt="`, sets the child continuation to
   `RESUME_IMAGE_TITLE=12`, and performs the ordinary A8/A9 alt requeue.
   The Horatio floor and its private Puck `TEXT_END` are independent of the
   held Romeo title floor.  No alt operation may pop Romeo.
3. The private terminator reaches the complete A9 adapter.  With `12` frozen
   in Prospero, `LYRIC_RESUME_CLOSE_DISPATCH` enters the new close-only
   `LYRIC_IMAGE_TITLE_CLOSE` scene.  That scene sets Hecate to
   `FIELD_IMAGE_TITLE` and enters the existing `LYRIC_FIELD_RETRY` family.
   The family reverses and entity-encodes the held Romeo title exactly once;
   its `FIELD_IMAGE_TITLE` drain-close branch emits `" />` and returns to
   `LYRIC_POP_GLYPH`.  It must not create another continuation record or
   private Puck boundary.
4. An image with no title continues to use `RESUME_IMAGE=9` and emits `" />`
   after the alt requeue.  Links retain their immediate title drain and
   `RESUME_LINK=8`; this correction changes neither link ordering nor
   autolink behavior.

This creates no new token code and no third on-stage character.  It adds only
the state-tag value `RESUME_IMAGE_TITLE=12`, which is a local Act III value
and must be included in the `RESUME_*` membership checks and observer
assertions.

### Nested-floor proof and required regression

The composition is legal: stacks are per-character and `run_act` pops only
the operation's target stack.  A focused IR-interpreter probe on 2026-07-14
held `[STREAM_END, 'i']` on Romeo while it created and completely drained an
independent `[STREAM_END, 'c', 'd']` Horatio requeue floor; the Romeo title
remained available, then both floors drained without `StackUnderflow`.

Before production scenes, add
`test_image_title_floor_survives_alt_requeue` to
`tests/test_splc_interpret.py`.  Construct a four-scene, two-character IR
act that: (a) pushes Romeo's title floor and `ord("i")`; (b) pushes Horatio's
alt floor and `ord("c"), ord("d")`; (c) drains only Horatio through its
floor; then (d) drains Romeo's title through its floor.  Assert both stacks
are empty and the final values on both characters are `tokens.STREAM_END`.
Run:

```bash
uv run pytest tests/test_splc_interpret.py::test_image_title_floor_survives_alt_requeue -q
```

Expected: `1 passed`.  The Task 4 observer test must additionally assert for
`links_images_protected` that the alt private boundary freezes `12`, enters
`LYRIC_IMAGE_TITLE_CLOSE`, does not pop Romeo before that scene, and reaches
exactly one `FIELD_IMAGE_TITLE` reverse/drain before emitting `" />`.

### A10 literary reservation (ready to paste)

One working scene is derived from the one new A10 transition above.  Its four
spares meet the required minimum spare pool for this act; none grants
authority unless a later planning amendment records its exact transition. No
new Recall phrase is required.

```toml
[scenes.LYRIC_IMAGE_TITLE_CLOSE]
title = "Romeo releases the portrait's quiet name."
pattern = "scene_of_character"

# A10 spare pool — do not use without another planning amendment.
[scenes.LYRIC_IMAGE_TITLE_REVERSE_GUARD]
title = "Romeo finds the portrait name's rooted stone."
pattern = "scene_of_character"
[scenes.LYRIC_IMAGE_TITLE_DRAIN_GUARD]
title = "Juliet keeps the portrait name's clear course."
pattern = "scene_of_character"
[scenes.LYRIC_IMAGE_TITLE_FLOOR_FAIL]
title = "The portrait name refuses a broken gate."
pattern = "bare_statement"
[scenes.LYRIC_IMAGE_TITLE_RETURN]
title = "The portrait leaves its quiet garden whole."
pattern = "bare_statement"
```

## A11 emphasis candidate lookahead ownership (2026-07-14)

The A9/A10 reconstruction diagnostic makes the remaining first-gate failure
precise. On `escapes_and_overlap`, an unmatched one-star opener eventually
sees a maximal `***` candidate at the real paragraph boundary.
`LYRIC_EMPHASIS_COMPARE` pops the first non-star after that candidate before
it decides whether the run matches. The diagnostic graph sends that popped
`TEXT_END` through ordinary fallback, loses the only real terminator, and then
`LYRIC_EMPHASIS_SEEK` pops Puck below its private floor. The same shape would
silently drop a non-terminator lookahead after any mismatched candidate run.
This is an emphasis-local ownership error; it does not authorize a change to
A8's requeue protocol, A9's continuation records, or the carrier model.

### Binding comparator rule

`LYRIC_EMPHASIS_COMPARE` owns precisely one post-candidate lookahead. It must
branch in this order after its `pop(PUCK, ...)`:

| Lookahead | Required action | Next scene |
|---|---|---|
| `*` | Increment `MACBETH`; continue counting the maximal candidate run. | `LYRIC_EMPHASIS_MATCH_MORE` |
| `TEXT_END` | Restore exactly one real `TEXT_END` to Puck; begin literal opener/body unwind without returning to seek. | `LYRIC_EMPHASIS_CAND_SOURCE_END` |
| Any other glyph | Push that glyph to Horatio above the held-body floor, then replay the candidate stars to Horatio. | `LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD` → existing `LYRIC_EMPHASIS_FALLBACK` |

`LYRIC_EMPHASIS_CAND_SOURCE_END` pushes the restored real terminator and goes
to the pre-existing literal-unwind entry. Refactor the pre-existing
`LYRIC_EMPHASIS_SOURCE_END` to be the one owner of literal-unwind setup (the
Hecate floor and literal opener emission) after its caller has restored the
terminator. It must not push a second `TEXT_END`. Thus both source-end arrivals
have exactly one terminator before `LYRIC_EMPHASIS_LITERAL_REVERSE`.

`LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD` performs only
`push(HORATIO, val(PUCK)); goto(LYRIC_EMPHASIS_FALLBACK)`. Because Horatio is
drained into Puck in reverse-stack order, the held body, candidate stars, and
lookahead are subsequently rescanned in their original left-to-right order.
No branch in this correction writes a candidate delimiter or lookahead to
Juliet, creates a continuation record, or pops Lady Macbeth/Romeo.

### Mandatory test-first checkpoint

Before touching `src_ir/act3.py`, add these observer-level tests to
`tests/test_act3_contracts.py`:

1. `test_act3_emphasis_candidate_keeps_nonmatching_lookahead` runs
   `escapes_and_overlap` and asserts that each entry to
   `LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD` is immediately followed by the
   existing fallback/replay family, and that the eventual decoded paragraph
   still contains the byte sequence `" and "` that follows the unmatched
   candidate. It must also assert no `StackUnderflow`.
2. `test_act3_emphasis_candidate_restores_real_text_end_once` runs the same
   fixture and asserts the order `LYRIC_EMPHASIS_COMPARE`,
   `LYRIC_EMPHASIS_CAND_SOURCE_END`, `LYRIC_EMPHASIS_SOURCE_END`,
   `LYRIC_EMPHASIS_LITERAL_REVERSE`, then `LYRIC_POP_GLYPH`,
   `LYRIC_TEXT_END_DISPATCH`; assert there is no later
   `LYRIC_EMPHASIS_SEEK` before that text-end dispatch and exactly one final
   `TRAVERSE_COPY_TERMINATOR` route with `CONT_NONE`.

Run this focused gate after the test is red and again after the two working
scenes land:

```bash
uv run pytest tests/test_act3_contracts.py -q -k \
  "emphasis_candidate_keeps_nonmatching_lookahead or emphasis_candidate_restores_real_text_end_once or protected_modes_do_not_underflow or text_end_event_order_is_carrier_safe"
```

Expected after implementation: all selected cases pass, including
`escapes_and_overlap`; no `StackUnderflow`, duplicate `TEXT_END`, or source
pop follows the real terminator. Then run the plan's exact literary gate.

### A11 literary reservation (ready to paste)

The table derives two new scenes. Four spares satisfy the protocol's minimum
proportional spare pool. Add only the two working entries with corresponding
IR scenes; no Recall line or recurring phrase is needed.

```toml
[scenes.LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD]
title = "Horatio shelters the star's following petal."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_CAND_SOURCE_END]
title = "The last star restores the garden gate."
pattern = "bare_statement"

# A11 spare pool — do not use without another planning amendment.
[scenes.LYRIC_EMPHASIS_CAND_REPLAY_GUARD]
title = "Horatio finds the star's rooted path."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_CAND_END_GUARD]
title = "The star refuses a second garden gate."
pattern = "bare_statement"
[scenes.LYRIC_EMPHASIS_CAND_ORDER_GUARD]
title = "Juliet keeps the stars in faithful order."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_CAND_RETURN]
title = "The wandering star returns to the hedge."
pattern = "bare_statement"
```

## A12 emphasis replay order and protected-mode sequencing (2026-07-14)

The preserved A11 reconstruction exposes an ordering defect in A11's
non-terminator prose, not a new carrier architecture problem. Horatio is a
LIFO capture: when later popped to Puck, its last value is scanned first.
A11's original wording put the lookahead on Horatio before replaying candidate
stars, which requeues `lookahead, stars, body` instead of original `body,
stars, lookahead` source order. That can consume the real terminator before
`LYRIC_EMPHASIS_SEEK` reads it. This supersedes only that ordering; A8's drain,
A9's continuation record, A10's image-title floor, and A11's real-end rule
remain binding.

### Binding nonmatching-candidate choreography

`LYRIC_EMPHASIS_COMPARE` retains its popped non-star lookahead in Puck and
enters the existing `LYRIC_EMPHASIS_FALLBACK`; it must not write the value to
Horatio yet. The fallback/replay loop appends exactly `MACBETH` candidate stars
to Horatio while Puck retains the lookahead. Its `MACBETH == 1` exit enters the
already-reserved `LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD`, which performs exactly:

```python
push(HORATIO, val(PUCK))
goto("LYRIC_EMPHASIS_SEEK")
```

Horatio therefore holds body, candidate stars, then lookahead; the A8 requeue
returns original left-to-right source order. `CAND_KEEP_LOOKAHEAD` is the
replay-loop exit, not an entry into fallback. No scene, TOML entry, holder,
floor, or continuation record is added.

For `TEXT_END`, retain A11's separate branch: restore one terminator to Puck,
enter `LYRIC_EMPHASIS_CAND_SOURCE_END`, then initialize literal unwind through
`LYRIC_EMPHASIS_SOURCE_END`. That initializer neither restores a second
terminator nor returns to seek. Neither route may pop Puck after the restored
real terminator is dispatched.

### Mandatory staged evidence

Before any HTML, autolink, link, or image opener, extend the A11 observers to
prove (1) compare → fallback/replay → `CAND_KEEP_LOOKAHEAD` → seek, with
literal `***both***` in decoded source order on the unmatched path; and (2)
the A11 source-end sequence, exactly one `TRAVERSE_COPY_TERMINATOR`, and no
seek/Puck pop between `CAND_SOURCE_END` and that route. Run:

```bash
uv run pytest tests/test_act3_contracts.py -q -k \
  "emphasis_candidate_keeps_nonmatching_lookahead or emphasis_candidate_restores_real_text_end_once or protected_modes_do_not_underflow or text_end_event_order_is_carrier_safe"
```

Expected: selected cases pass with no underflow, and no protected opener is
reachable. Then run the plan's exact literary gate. Only then may A10's
unchanged image-title path proceed: its nested-floor regression must pass,
followed by observer proof of selector `12`, `LYRIC_IMAGE_TITLE_CLOSE`, no
early Romeo pop, and one delayed title drain. Any miss is `BLOCK[plan]`; no
spare scene or recovery pop is authorized.

## A13 terminal-match ownership and held-title drain (2026-07-14)

The Task 4 Step 2 checkpoint leaves two successful-boundary cases
underspecified. This correction changes neither A8's raw-requeue order, A9's
continuation records, nor A10's independent Romeo/Horatio floors.

### Terminal emphasis is a match, not literal fallback

`LYRIC_EMPHASIS_COMPARE` owns one post-candidate lookahead in Puck. Count a
maximal candidate run first. When that run ends, compare `MACBETH` with the
opener length in `HECATE` **before** testing the lookahead for `TEXT_END`.
Equality enters `LYRIC_EMPHASIS_MATCH` for every lookahead, including real
`TEXT_END`; only a non-equal `TEXT_END` uses A11 literal unwind and only a
non-equal ordinary glyph uses A12 replay.

The matched route first restores its exact lookahead to Puck, then builds the
existing A8 child boundary and requeues the held body. Its next-pop order is
raw body, private `TEXT_END`, restored lookahead. Thus a terminal match closes
before ordinary `LYRIC_POP_GLYPH -> LYRIC_TEXT_END_DISPATCH` consumes the one
real terminator. It may not visit unmatched-source-end or seek first.

Length one emits `<em>` / `</em>`; length two emits `<strong>` / `</strong>`;
length three emits `<strong><em>` / `</em></strong>`. Triple synthetic stars
are child source only and never reach Juliet. Preserve the matched length
until close selection; do not use it as a body-draining register.

### A held image title resumes at drain, never capture

After alt requeue selector `12`, `LYRIC_IMAGE_TITLE_CLOSE` sets the field tag
in `PROSPERO`, seeds only the existing Hecate reverse floor, and enters the
shared reverse/drain stage. It must not enter `LYRIC_FIELD_RETRY`,
`LYRIC_FIELD_OPEN`, or `LYRIC_FIELD_SCAN`: those create a second Romeo floor
and later pop Puck after the alt boundary is consumed. Its one drain-close
emits `" />`, returns to `LYRIC_POP_GLYPH`, and creates no record or private
`TEXT_END`.

Destinations stop before their first ASCII space or closing `)`; a quoted
title owns its quote and final `)`. Link titles drain before label requeue.
Image titles are held on Romeo until selector `12`. None of the delimiters is
captured as field text.

### Mandatory reconstruction and evidence

Reconstruct from committed Task 3 plus accepted A10/A11/A12 shapes. Before
production edits, add observers proving: (1) terminal `***both***` matches,
closes, and reaches exactly one real terminator route; (2) nested
`**outer *inner* outer**` preserves the outer close and emits no synthetic
star; and (3) link/image title order, selector `12`, no early Romeo pop, and
one delayed image-title drain. Run:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q -k \
  "terminal_emphasis_match or overlapping_emphasis or links_images_protected or protected_modes_do_not_underflow or text_end_event_order_is_carrier_safe"
```

Expected: PASS. Then run the plan's exact literary gate. No new scene, Recall
key, token code, stack, or controlled prose is authorized; use only existing
A2/A10/A11 working labels. Any underflow, duplicate real terminator, early
Romeo pop, or literal synthetic delimiter is `BLOCK[plan]`.
