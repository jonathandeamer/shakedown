# Shakedown SPL Validation Phase 2 Summary

**Date:** 2026-04-17
**Study design:** `docs/superpowers/specs/2026-04-16-shakedown-spl-validation-2-design.md`
> **Reader note:** This summary corrects the round-1 “6-character budget” framing, but it
> still overstates some SPL stage constraints. For planning and architecture work, read this
> document together with `docs/shakedown-spl-feasibility-assumption-corrections.md`.

## Verdict Table

| # | Experiment | Verdict | Key finding |
|---|---|---|---|
| 6 | Runtime: AST cache splitting | **PASS** | Pre-built AST cache reduces per-test cost to ~0.30s at 8,623 lines |
| 7 | Consolidation: combined shared-scene + recursive dispatch | **PASS** | The two patterns coexist cleanly in one act and stay far below the line-count target |
| 8 | Inline spans: emphasis matching | **PARTIAL** | Simple emphasis works; Markdown.pl backtracking semantics still diverge on nested/contextual emphasis |
| 9 | List parsing: tight/loose detection and 2-level nesting | **PARTIAL** | Tight and 2-level nested lists match exactly; loose-list buffering still fails |
| 10 | Recursive dispatch: frame sentinel pattern | **PARTIAL** | Sentinel-delimited frames work mechanically, but exact nested blockquote+list output remains fragile |

## Accepted Trade-Offs

- **Exp-8:** Accept streaming emphasis for the common cases and treat Markdown.pl-style
  backtracking emphasis as a residual incompatibility.
- **Exp-9:** Accept that tight lists and 2-level nesting are validated while loose-list
  exactness remains a likely failure mode.
- **Exp-10:** Accept that sentinel-framed recursion is usable only with careful,
  error-prone bookkeeping; nested block compositions remain higher-risk than the other
  validated patterns.

## Updated Pass-Rate Ceiling vs. Round 1

Round 1 estimated **21 / 23 fixtures (91%)**, with a stretch ceiling around **22 / 23**.
Phase 2 improves confidence in the runtime and consolidation workarounds, but it lowers
confidence in two specific behavioural areas:

1. Loose lists
2. Exact nested blockquote/list compositions

That leaves the realistic ceiling at **20–21 / 23 fixtures**, still roughly the same band
as round 1 but with a sharper understanding of where the misses are likely to land.

## Revised Recommendation

### Recommendation: GO

Per the phase-2 success rule, the result is **GO** because no experiment returned
`BLOCKED`.

This is not an unconditional quality endorsement. It means the architecture is still
technically viable on the Lightsail box if the remaining PARTIALs are accepted as real,
documented trade-offs rather than hand-waved away.

## Architecture Summary

The validated architecture for a Shakedown build is now:

1. **Runtime:** parse once, cache the AST, and run test sessions from the cached AST
   rather than reparsing the SPL file every time.
2. **Consolidation:** use the shared-scene return-address pattern together with buffer-fed
   recursive dispatch inside a single act.
3. **Inline spans:** handle simple emphasis/code spans with streaming logic and accept
   that Markdown.pl's regex-backtracking emphasis behaviour is still only partially
   reproducible.
4. **Lists:** rely on validated tight-list handling and bounded 2-level nesting, while
   treating loose-list exactness as unresolved.
5. **Nested blocks:** use stack sentinels to delimit recursive frames, but expect this
   area to be the most error-prone part of the build.

When using this summary for planning, read its two-character staging language as shorthand
for second-person-pronoun addressing pressure, not as a universal SPL limit on how many
characters may be on stage at once; see
`docs/shakedown-spl-feasibility-assumption-corrections.md`.

## Bottom Line

Validation phase 2 removed the two biggest round-1 uncertainties:

- runtime cost is no longer a blocker
- code-size consolidation is no longer a blocker

What remains are behavioural edge cases, not architectural impossibilities. That is enough
for a **GO**, but only a guarded one: the build should proceed with the expectation that
loose lists, emphasis edge cases, and nested block compositions are the most likely places
to miss exact `Markdown.pl` compatibility.
