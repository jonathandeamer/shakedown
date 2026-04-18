# Feasibility Lessons from the Prior Attempt

> This file consolidates three earlier sources: `feasibility-summary.md` (round 1, five experiments), `feasibility-summary-2.md` (round 2, five experiments), and `shakedown-spl-feasibility-assumption-corrections.md`. The originals are removed by the restructure; their content is preserved and integrated below.

## Context

The ten experiments summarised here were run in a prior `~/shakedown/` checkout that is no longer present in this repository. Round 1 measured against a 4,311-line `shakedown.spl`. Round 2 measured against an 8,623-line projected full port built on top of that work. Neither artifact exists in this repo. Claims of the form "we measured X at Y lines" are evidence from a prior codebase, not facts about the current state.

The consolidated voice below integrates the round-1 assumption corrections inline. Read this file once rather than the three source documents in sequence.

## Experiment Table

| # | Round | Experiment | Verdict | Key finding | Status in this repo |
|---|---|---|---|---|---|
| 1 | 1 | Runtime | PARTIAL | AST cache achieves 1.09s/test at 4,311 lines; degrades past 2s at projected 8,600-line full port | Retrospective: depends on a 4,311-line SPL file not present here |
| 2 | 1 | Single-act consolidation | PARTIAL | Shared-scene return-address pattern works; ~8% reduction, not the 30% target; blockquote reimplementation was 44% of the file | Retrospective: prior-code measurement |
| 3 | 1 | Inline span architecture | PARTIAL | Simple spans (code, basic emphasis) stream cleanly; emphasis matching and reference links need buffered O(n²) processing | Transferable: shape of the inline-vs-buffered choice survives |
| 4 | 1 | List parsing | PARTIAL | Marker detection + one-byte lookahead work; tight/loose feasible but unprototyped; nesting bounded to 2–3 levels | Transferable: list-depth bound is architecture input |
| 5 | 1 | Recursive block reprocessing | PARTIAL | Buffer-fed dispatch proven; one-level nesting works cleanly; multi-level constrained by prior cast design | Transferable: nested-block framing pattern survives |
| 6 | 2 | Runtime: AST cache splitting | PASS | Pre-built AST cache reduces per-test cost to ~0.30s at 8,623 lines | Retrospective: needs a new cheap smoke test in this repo (see `docs/verification-plan.md` replay 7) |
| 7 | 2 | Consolidation: shared-scene + recursive dispatch | PASS | The two patterns coexist cleanly in one act and stay far below the line-count target | Retrospective: prior-code measurement |
| 8 | 2 | Inline spans: emphasis matching | PARTIAL | Simple emphasis works; Markdown.pl backtracking semantics still diverge on nested/contextual emphasis | Transferable: names an open risk |
| 9 | 2 | List parsing: tight/loose and 2-level nesting | PARTIAL | Tight and 2-level nested lists match exactly; loose-list buffering still fails | Transferable: names an open risk |
| 10 | 2 | Recursive dispatch: frame sentinel pattern | PARTIAL | Sentinel-delimited frames work mechanically; exact nested blockquote+list output remains fragile | Transferable: names an open risk |

No round-1 experiment returned BLOCKED. Round 2 returned two PASS verdicts (6, 7) and three PARTIAL (8, 9, 10). The round-2 recommendation was a guarded GO.

## Corrected Assumptions

Three round-1 framings are retracted:

1. **There is no language-level "6-character budget" in SPL.** The local reference does not support that claim. What the reference does support: each character has one value and one stack, and legal names come from the interpreter grammar.
2. **"Two characters on stage" is a pronoun rule, not a universal stage-capacity rule.** Second-person pronouns (`you`, `thou`, `thee`, `yourself`, `thyself`) require exactly one other on-stage character to be unambiguous. The grammar and stage directions accept multi-character entrances and exits.
3. **"No limit on characters" overcorrects.** SPL does not impose a six-character cap, but the set of legal character names is the finite alternatives in the installed grammar. The available cast is finite.

The two-character wording that appears in the round-1 and round-2 summaries should be read as shorthand for second-person-pronoun addressing pressure, not a universal stage cap. See `docs/spl/reference.md` for the verified pronoun rule.

## What Transfers to This Repo

- The shape of the architectural trade-off between streaming and buffered inline handling.
- The list-depth bound (2 levels is enough for `Markdown.mdtest` fixtures).
- The nested-block framing pattern (sentinel-delimited frames on stacks) as a candidate approach.
- The divergence catalogue: email autolink randomisation is permanently unavailable in SPL (no randomness primitive); nested blockquote closer quirk is acceptable to diverge from (see `docs/markdown/divergences.md`).
- The Go/No-Go framing: the architecture is viable if PARTIAL verdicts are accepted as real documented trade-offs.

## What Does Not Transfer

- Specific line counts (4,311 and ~8,623).
- Specific per-test timings (1.09s, 0.30s).
- The ~8% / ~47% consolidation reduction numbers.
- The "~91–96% pass ceiling" estimate — it was predicated on specific architectural choices in the prior build.
- Cast-pressure judgments tied to the prior implementation's specific character set.
- Any "already implemented in Slice 1" claim for specific fixtures (the implementation is not here).

These numbers can be re-derived during architecture planning or a new feasibility pass. Until then, they are not evidence about this repo.

## Bottom Line for Architecture Planning

The prior attempt's ten experiments establish that a Shakedown port is architecturally possible. It does not establish that the specific architecture chosen by the prior attempt (single-act dispatcher with particular cast, AST cache via Python wrapper, recursive dispatch with sentinel frames) is the right choice for a fresh build. Architecture planning in this repo may arrive at the same design by a different route, or at a different design entirely.
