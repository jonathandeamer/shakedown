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
