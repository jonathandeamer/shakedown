# Slice 1 Halt Resolution Design

**Date:** 2026-04-29
**Status:** Design note feeding `superpowers:writing-plans`
**Scope:** resolving the Slice 1 line-budget halt before the run-loop may
advance to Spike A or any later fixture work.

## Context

Plan 2 reached the Slice 1 verification gate for `Amps and angle encoding`.
The SPL-owned implementation is byte-identical to `Markdown.pl`, but
`shakedown.spl` is 977 lines. This trips the architecture §8.2 halt trigger:

> Slice 1 assembled `shakedown.spl` exceeds ~600 lines.

The raw line count is not the only concern. The measured Slice 1 fixture run is
about 12.9s median / 14.3s first run via `scripts/measure_spl_cost.py` with the
fixture stdin, which is yellow-zone for a single small fixture. The generated
artifact is also much denser than the synthetic 1k-line baseline:

| Artifact | Lines | Bytes |
|---|---:|---:|
| `shakedown.spl` | 977 | 73,111 |
| B14 `spl-cost-1k.spl` | 1,255 | 25,552 |

The important signal is shape, not the exact numeric threshold. Slice 1 already
contains fixture-specific unrolling in the very features that later slices will
expand.

## Evidence

Current source fragment sizes:

| Fragment | Lines | Notes |
|---|---:|---|
| `src/00-preamble.spl` | 13 | Cast and header only. |
| `src/10-act1-preprocess.spl` | 206 | Includes a 134-line exact tail strip. |
| `src/20-act2-block.spl` | 79 | Paragraph-only block pass. |
| `src/30-act3-span.spl` | 598 | Dominant growth point. |
| `src/40-act4-emit.spl` | 81 | Small final token emitter. |

Specific growth causes:

- `src/10-act1-preprocess.spl` contains `@HECATE_CUT_REFERENCE_TAIL`, a
  134-line scene that pops the exact 65-glyph reference-definition suffix for
  this fixture.
- `src/30-act3-span.spl` contains fixed-length inline-link destination popping
  scenes for 19 and 21 glyphs.
- `src/30-act3-span.spl` contains full hardcoded anchor outputs:
  `@LYRIC_OUTPUT_REFERENCE_ONE` (58 lines), `@LYRIC_OUTPUT_REFERENCE_TWO`
  (59 lines), and `@LYRIC_OUTPUT_INLINE_LINK` (46 lines).
- Act III contains 182 lines with `sum of` expressions and 1,015 total
  `sum of` terms, compared with 124 total `sum of` terms in the synthetic
  1k-line probe.

These are not stable parser forms. They prove that the first fixture can pass,
but they do not prove that the architecture will absorb links, images, code
spans, escapes, emphasis, and raw HTML without repeated size/runtime blowups.

## Hard Constraints

Markdown behavior remains SPL-owned. Python may assemble fragments, generate
literal-byte phrases, and provide tests/harnesses. Python must not decide:

- whether a reference definition is present;
- where a delimiter closes;
- whether an ampersand or angle bracket is encoded;
- whether a link/image/reference resolves;
- what Markdown output structure a parsed construct produces.

Those decisions must remain represented in SPL scenes and stack operations.

The design may reopen the four-act split, but only if the evidence shows that
the Act III / Act IV boundary itself forces the unscalable shape. Repartitioning
is allowed; outsourcing Markdown semantics is not.

## Options Considered

### Option A: Recalibrate the Line Budget and Continue

Accept that 977 lines is the new Slice 1 baseline, document the runtime, remove
the blocker, and continue to Spike A.

**Pros:** fastest path; preserves current passing work.

**Cons:** ignores the exact-length unrolling and hardcoded anchor output
patterns. Later link/image/reference work would likely compound the problem.

**Disposition:** rejected as the default path. It remains available only if a
follow-up proof shows the unrolled scenes are harmless fixed scaffolding, which
the current evidence does not support.

### Option B: Preserve Four Acts, Replace Unscalable Internals

Keep the current Preprocess / Block / Span / Emit split, but require Slice 1 to
use delimiter-driven SPL loops and reusable anchor emission pieces:

- Act I strips reference definitions by scanning line structure and delimiters,
  not by popping an exact fixture suffix.
- Act III parses inline and reference links by consuming until delimiters, not
  by fixed destination lengths.
- Act III pushes an anchor token shape or reusable output pieces instead of
  full fixture-specific anchor HTML literals.
- Act IV owns reusable emission of `<a href="`, escaped URL/title/text payloads,
  optional ` title="..."`, and `</a>`.

**Pros:** directly addresses the observed root causes while preserving most of
the adopted architecture. Keeps Markdown behavior in SPL.

**Cons:** still needs proof that the Act III-to-Act IV contract can represent
anchors without creating a larger token protocol than it saves.

**Disposition:** recommended first replacement plan.

### Option C: Repartition Span and Emit

Collapse or reshape the Span / Emit boundary so span parsing can route directly
through a reusable emitter path instead of building a transformed token stream
that later gets emitted.

**Pros:** may remove duplication if the current boundary is forcing Act III to
pre-render large HTML strings.

**Cons:** broader rewrite; risks weakening the clean four-act handoff before
we prove the local implementation choices are the real cause.

**Disposition:** keep as the fallback if Option B's proof fails.

### Option D: Redesign Around Markdown.pl Transform Stages

Replace the literary four-act pipeline with a pipeline closer to Markdown.pl:
preprocess/reference strip, block gamut, span gamut, final emit.

**Pros:** conceptually aligns with the oracle mechanics.

**Cons:** broadest change; overlaps heavily with the current four-act split in
practice; likely delays Spike A without first testing the smaller fix.

**Disposition:** not justified yet.

## Decision

Proceed with Option B as the next design-to-plan path. The four-act split stays
provisionally accepted, but the replacement plan must contain an explicit proof
checkpoint:

1. Remove exact-length reference-tail stripping from Act I.
2. Remove fixed-length inline destination popping from Act III.
3. Remove full hardcoded fixture anchor HTML outputs from Act III.
4. Preserve byte-identical Slice 1 output.
5. Re-measure `./shakedown` or `shakespeare run shakedown.spl` on the Slice 1
   fixture.

If that proof cannot be completed without moving Markdown decisions into
Python, stop and reopen Option C. If Option C still cannot keep behavior in SPL,
stop and reopen Option D.

## Replacement Plan Requirements

The next implementation plan must supersede the blocked tail of Plan 2. It must
not advance to Spike A until the blocker is resolved.

Required plan checks:

- Add or update tests that prove Slice 1 remains byte-identical to
  `Markdown.pl`.
- Add a structural regression check that rejects the known bad forms:
  exact 65-glyph reference-tail popping, fixed 19/21-glyph inline destination
  popping, and full fixture anchor-output scenes in Act III.
- Keep `.agent/blockers.md` blocked until the replacement proof passes and the
  operator accepts the revised architecture note.
- Update `docs/superpowers/plans/plan-roadmap.md` to mark the original Slice 1
  plan as blocked/superseded or to point at the replacement plan, depending on
  the final plan shape.
- Update `docs/prompt-shakedown.md` to reference the replacement plan before
  restarting the run-loop.

## Acceptance Criteria

The halt is resolved only when all of these are true:

1. `uv run pytest tests/test_slice1_amps_angle.py -q` passes.
2. `uv run python scripts/strict_parity_harness.py "Amps and angle encoding"`
   reports `summary: 1/1 byte-identical`.
3. `./shakedown` contains no `Markdown.pl`, `ORACLE`, or `exec perl`
   delegation.
4. The source no longer relies on exact-length fixture stripping for the two
   reference definitions or the two inline destination forms.
5. Act III no longer hardcodes the full fixture anchor outputs as complete
   byte-literal scenes.
6. Runtime on the Slice 1 fixture is recorded using the protocol in
   `docs/performance/budget.md`.
7. A human/operator explicitly removes the `- BLOCK:` line from
   `.agent/blockers.md`.

The line count may still exceed 600 after the replacement proof. If so, the
architecture spec may be amended with a higher threshold only if the remaining
growth is explained as reusable SPL machinery rather than fixture-specific
unrolling.

## References

- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` —
  current selected architecture and §8.2 halt trigger.
- `docs/superpowers/plans/2026-04-28-slice-1-amps-angle-encoding.md` —
  blocked Slice 1 implementation plan.
- `docs/performance/budget.md` — timing protocol and planning thresholds.
- `docs/markdown/reference-mechanics.md` — reference definition and link
  behavior that must remain SPL-owned.
- `docs/markdown/oracle-mechanics.md` — Markdown.pl transform order.
