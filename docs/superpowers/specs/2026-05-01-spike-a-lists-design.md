# Spike A Lists Design

**Date:** 2026-05-01
**Status:** Draft for review
**Scope:** design for roadmap item 3, "Spike A - Lists at minimum viable scope"

## Context

The active roadmap currently has `docs/superpowers/plans/2026-04-30-literary-prevention-rails.md`
in flight. This document is design-only preparation for the next stage. It does
not advance `docs/superpowers/plans/plan-roadmap.md`, does not create an
implementation plan, and does not change the run-loop prompt.

The durable architecture spec defines Spike A as the first list validation
point after Slice 1. Its purpose is to validate the multi-pass dispatcher and
frame-sentinel nesting before later fixture slices depend on that shape.
`docs/markdown/list-mechanics.md` names the list-specific decisions that the
design must make: list-level state storage, item buffering, tight/loose
classification, nested-list return, and the fixture path that proves exactness.

## Decision Summary

Spike A should be a production-shaped architecture spike. It should build the
smallest real list path that proves the durable parser, token, nesting, and
emission contracts. It should not attempt complete Markdown.pl list coverage.

The implementation plan that follows this design should:

- add custom architecture spike snippets for list behavior;
- add an oracle-backed spike harness comparing `./shakedown` to
  `~/markdown/Markdown.pl` byte-for-byte;
- implement real `LIST_OPEN`, `LIST_ITEM`, and `LIST_CLOSE` token flow in Act II;
- implement real list HTML emission in Act IV;
- represent list kind and item looseness as token payloads;
- use frame-sentinel state for one nested list level;
- preserve existing Slice 1 parity;
- leave the full `Ordered and unordered lists` mdtest fixture skipped until
  Slice 4.

## Goals

1. Validate that the multi-pass block dispatcher can add a list pass before
   paragraph formation without regressing existing paragraph behavior.
2. Validate that frame-sentinel state can enter a nested list and return to the
   enclosing item at fixture-relevant scope.
3. Establish a durable token contract for list kind and item looseness so later
   slices do not rediscover source-level Markdown structure in Act IV.
4. Add permanent architecture spike snippets that remain part of the regression
   gate after Spike A ships.
5. Protect the top-level paragraph/list ambiguity that later affects the
   `Hard-wrapped paragraphs with list-like lines` fixture.

## Non-Goals

- Do not enable the full `Ordered and unordered lists` mdtest fixture.
- Do not implement every unordered marker family. The spike may choose one
  unordered marker, preferably `*`, as the minimum proof.
- Do not implement exhaustive ordered-list variants beyond digits followed by
  `.` and required whitespace.
- Do not implement list-with-blockquote composition. That belongs to Spike B.
- Do not cover every nested loose-list combination. Slice 4 owns full list
  exactness.
- Do not add a new run-loop prompt. The current plan-driven prompt is sufficient
  once the roadmap marks a Spike A plan in flight.

## Snippet Coverage

Create committed snippet fixtures under:

```text
tests/fixtures/architecture_spikes/lists/
```

The minimum snippet set is:

1. Flat unordered tight list with three items.
2. Flat ordered tight list with three items.
3. One nested list level.
4. One loose list item with a second paragraph.
5. One item with an indented continuation/code-block candidate.
6. Boundary case: a hard-wrapped paragraph line that looks like an ordered list
   marker but remains paragraph text under Markdown.pl top-level boundary rules.

The snippets should be short enough that byte diffs are readable when the spike
harness fails.

## Harness

Add a dedicated architecture spike test module, likely:

```text
tests/test_architecture_spikes.py
```

The harness should:

- discover or explicitly enumerate the list snippets;
- feed each snippet to `./shakedown`;
- feed the same snippet to `perl ~/markdown/Markdown.pl`;
- compare raw stdout bytes;
- report the snippet name and first byte difference on mismatch.

This harness is not a replacement for `tests/test_mdtest.py`. It is the
verification surface for architecture snippets that are smaller than full
Markdown.mdtest fixtures.

## Act II Contract

Act II owns list recognition, item buffering, nesting state, and tight/loose
classification. Act IV should not infer any of those facts from raw Markdown
text.

The list pass runs after headers and horizontal rules and before code blocks,
matching the architecture's `_RunBlockGamut` order. In current source terms,
the first Spike A implementation may add the list pass directly to
`src/20-act2-block.spl` before paragraph formation. Later slices may split
large scenes only if line pressure demands it.

The Act II output contract is:

- `LIST_OPEN` followed by a payload indicating list kind;
- one or more `LIST_ITEM` tokens, each followed by a payload indicating
  tightness or looseness;
- item body payload using the existing text stream machinery where possible;
- nested lists represented by nested `LIST_OPEN` / `LIST_CLOSE` pairs;
- `LIST_CLOSE` to close the current frame.

List kind payloads should be small stable values:

- `1` for unordered lists;
- `2` for ordered lists.

Item looseness payloads should be small stable values:

- `1` for tight;
- `2` for loose.

The existing token-code table already contains `LIST_OPEN`, `LIST_ITEM`, and
`LIST_CLOSE`. The design should reuse those token types unless implementation
proves that an additional token is unavoidable.

## State And Frames

The design should use explicit frame-sentinel state for list nesting. The
implementation plan should name the exact character that owns this state after
reviewing the post-literary-rails source, but the responsibility is fixed:

- push a list frame when entering a list;
- record list kind on or next to the frame;
- record enough item boundary state to close an item before opening the next;
- push a nested frame when a nested list begins;
- pop the nested frame and resume the enclosing item when the nested list ends.

This spike validates one nested level. The data shape should not intentionally
prevent deeper nesting, but arbitrary-depth proof is not a Spike A requirement.

## Tight And Loose Items

Act II classifies each item as tight or loose. The classification should mirror
the Markdown.pl mechanics summarized in `docs/markdown/list-mechanics.md`:

- an item with a leading blank line or blank lines inside the item is loose;
- otherwise it is tight;
- loose items preserve paragraph block structure inside `<li>`;
- tight items emit inline item content without paragraph wrappers.

The exact output newline shape should be taken from `Markdown.pl` output for
the snippet fixtures, not hand-derived from memory.

## Act III Contract

Act III should not need list-specific parsing. Text-bearing list item payloads
should flow through the same span substitution path used for paragraph text.

If the current token stream cannot express "span-process this list item body"
without special Act III cases, the Spike A plan should treat that as an
implementation finding and keep the special case narrow. The design preference
is that list bodies reuse existing text payload behavior.

## Act IV Contract

Act IV emits list HTML from the token stream:

- `LIST_OPEN` with unordered kind emits `<ul>`;
- `LIST_OPEN` with ordered kind emits `<ol>`;
- `LIST_ITEM` with tight kind emits item text as `<li>text</li>`;
- `LIST_ITEM` with loose kind emits item body with paragraph structure inside
  `<li>`;
- `LIST_CLOSE` emits `</ul>` or `</ol>` according to the current list frame.

Act IV may maintain a small emission-side list-kind stack if needed to choose
the correct closing tag. That stack mirrors the token stream; it must not
recover list structure from source text.

Forced-byte HTML emission remains governed by `scripts/codegen_html.py` and the
SPL literary protocol. If new generated HTML literal scenes are needed for list
tags, they should be added through the existing codegen path rather than
hand-authored as repeated byte output.

## Literary Surface Implications

Spike A will likely add Act II and Act IV scenes. After the literary prevention
rails plan lands, those scenes should follow:

- `docs/superpowers/notes/spl-literary-protocol.md`;
- `docs/spl/literary-spec.md`;
- `docs/spl/style-lexicon.md`;
- `docs/spl/codegen-style-guide.md`;
- `src/literary.toml`.

Controlled scene titles, recurring recall lines, and generated value atoms
should come from `src/literary.toml` through the mechanisms established by the
literary prevention rails plan.

## Verification

The Spike A implementation plan should require these gates:

1. `uv run pytest tests/test_architecture_spikes.py -q`
2. `uv run pytest tests/test_mdtest.py -k "Amps and angle" -q`
3. `uv run pytest tests/test_token_codes.py -q`
4. literary compliance tests named by the active literary protocol if SPL
   scenes, assembler behavior, codegen behavior, or `src/literary.toml` change
5. strict Shakedown-vs-Markdown.pl parity for the implemented Slice 1 fixture

The full `uv run pytest` suite is desirable before marking the spike shipped,
but the implementation plan should still name the narrower gates at the steps
where they first become relevant.

## Halt Conditions

Spike A is a validation gate. The implementation should halt and reopen the
architecture rather than push forward if any of these occur:

- the list pass cannot be added without duplicating broad block-dispatch
  prefixes across many scenes;
- frame-sentinel state cannot return from the nested list to the enclosing item
  in a way that stays readable and testable;
- tight/loose classification requires Act IV to inspect raw Markdown source;
- the spike needs broad full-fixture behavior to pass the minimum snippets;
- generated `shakedown.spl` line growth shows the same duplicated-pattern
  pressure that caused the prior Slice 1 halt.

## Follow-On Work

After Spike A ships:

- Spike B validates list/blockquote composition with separate nested-block
  snippets.
- Slice 2 proceeds through low-risk fixtures while preserving Spike A snippets
  as a regression gate.
- Slice 3 can tackle `Hard-wrapped paragraphs with list-like lines` with the
  boundary rule already protected by a small Spike A snippet.
- Slice 4 expands list support to the full `Ordered and unordered lists` mdtest
  fixture.
