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
| Hecate stack | One reversed field ready for output | `LYRIC_FIELD_REV` first pushes its private `STREAM_END`; `LYRIC_FIELD_HEAD/NEXT` drains it exactly once. Hecate's *value* remains the call-site code throughout. |
| Horatio | Raw link label, image alt, or emphasis body | One private `STREAM_END` per held region. It is drained only by `LYRIC_REGION_RESUME` / `LYRIC_EMPHASIS_RESUME` into Puck. |
| Lady Macbeth | Continuation records and the duplicate autolink field | Each record is `[STREAM_END, saved Hecate code, saved Macbeth delimiter length]`; autolink's duplicate buffer has a separate `STREAM_END` above that record. A continuation is popped before its next shared-field entry. |
| Macbeth value | Parenthesis depth while a destination is captured, or the matched emphasis run length | It is never used as a glyph register. `LYRIC_EMPHASIS_*` must not overwrite it between `MATCH` and the corresponding close. |

The checked IR-shape test must reject any pre-handoff `Push(PUCK, ...)` that
is not `val(PUCK)`, `val(ROMEO)`, `val(HORATIO)`, `const(TEXT_END)`, or a
raw delimiter constant (`*`/`_`) used solely to construct the triple-emphasis
child. It must retain the singleton `Push(PUCK, val(JULIET))` allowance in
`LYRIC_REVERSE_POP` only.

### Continuation codes and resume rule

Use these small values in Hecate, with named constants local to `act3.py`:
`FIELD_TAG=1`, `FIELD_AUTO_HREF=2`, `FIELD_AUTO_TEXT=3`,
`FIELD_LINK_DEST=4`, `FIELD_LINK_TITLE=5`, `FIELD_IMAGE_DEST=6`,
`FIELD_IMAGE_TITLE=7`, `RESUME_LINK=8`, `RESUME_IMAGE=9`,
`RESUME_EMPH=10`, and `RESUME_TRIPLE_EMPH=11`. Values are state tags, not
token codes. Each branch into a shared `LYRIC_FIELD_*` scene must set exactly
one field tag first. `LYRIC_POP_GLYPH` handles a popped `TEXT_END` as follows:

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
| `LYRIC_FIELD_REV_KEEP`, `REV`, `HEAD`, `GLYPH`, `PLAIN`, `AMP/LT/GT`, `NEXT`, `DRAIN_CLOSE` | Reverse Romeo onto Hecate's private-floor stack. In `FIELD_AUTO_HREF`, also copy each popped raw glyph to Lady Macbeth's duplicate-floor stack. `HEAD/NEXT` drain Hecate to Juliet; tag mode uses `PLAIN` only, all other modes use the existing entity triples. `DRAIN_CLOSE` dispatches solely by Hecate's unchanged field tag. |
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
