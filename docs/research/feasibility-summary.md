# Shakedown SPL Feasibility Summary

**Date:** 2026-04-16
**Study design:** `docs/superpowers/specs/2026-04-14-shakedown-spl-feasibility-design.md`
> **Reader note:** This summary contains outdated SPL-constraint framing from round 1,
> especially around the claimed “6-character budget.” For planning and architecture work,
> read this document together with
> `docs/shakedown-spl-feasibility-assumption-corrections.md`.

## Verdict Table

| # | Experiment | Verdict | Key finding |
|---|---|---|---|
| 1 | Runtime | **PARTIAL** | AST cache achieves 1.09s/test at 4,311 lines; degrades past 2s at projected full-port size (~8,600 lines) |
| 2 | Single-act consolidation | **PARTIAL** | Shared-scene return-address pattern works; achieves ~8% reduction, not 30% — blockquote reimplementation (44% of file) needs recursive dispatch |
| 3 | Inline span architecture | **PARTIAL** | Simple spans (code, basic emphasis) work streaming; emphasis matching and reference links require O(n²) buffered processing |
| 4 | List parsing | **PARTIAL** | Marker detection + one-byte lookahead work; tight/loose feasible but unprototyped; nesting bounded to 2–3 levels |
| 5 | Recursive block reprocessing | **PARTIAL** | Buffer-fed dispatch proven (dispatcher reads from stack instead of stdin); one-level nesting works cleanly; multi-level constrained by prior cast design pressure |

**No experiment returned BLOCKED.** All five returned PARTIAL — the features work within
documented limits but none achieved an unqualified PASS.
Round-1 references to a “6-character budget” in this document describe the prior
Shakedown implementation’s cast pressure, not a language-level SPL limit; see
`docs/shakedown-spl-feasibility-assumption-corrections.md`.

## Workaround Assessment

| Experiment | PARTIAL limitation | Workaround available? |
|---|---|---|
| 1 — Runtime | Per-test cost exceeds 2s at full-port size | **Yes** — accept 2–3s/test (suite in 46–69s); or split AST cache across sessions to avoid re-parse |
| 2 — Consolidation | Only 8% reduction vs. 30% target | **Yes** — combine with recursive dispatch (Exp 5) for ~47% reduction |
| 3 — Inline spans | Emphasis/reference links need O(n²) buffer scan | **Unknown** — no simpler algorithm exists for Markdown.pl's regex semantics in a streaming model |
| 4 — List parsing | Nesting bounded to 2–3 levels | **Yes** — `Markdown.mdtest` fixtures only test 2 levels; bounded depth is sufficient |
| 5 — Recursive dispatch | Multi-level recursion needs frame management | **Yes** — frame sentinels on stacks; max 2 levels needed for test fixtures |

## Estimated Pass-Rate Ceiling

### Block structure (paragraphs, headings, HR, code blocks)

All block-level features from Slice 1 are already implemented in the recovered
`shakedown.spl` (4,311 lines). Simple tests pass (ATX h1–h6, setext h1–h2, paragraphs,
HR). The full `Markdown.mdtest` block-level fixtures fail on features that Slice 1 didn't
implement (lists, nested blocks, inline processing), not on architectural limitations.

**Ceiling: 100%** of block-level features are achievable.

### Inline processing (emphasis, code spans, links, escapes, HTML)

| Feature | Approach | Ceiling |
|---|---|---|
| Code spans | Streaming toggle | 100% |
| Basic emphasis (`*word*`) | Streaming toggle | 100% |
| Emphasis with context (`*foo *bar* baz*`) | Buffered regex-like scan | ~90% — edge cases in Markdown.pl's regex backtracking may not be perfectly reproducible |
| Reference links | Two-pass with linear lookup | 100% (functional), but O(n×m) performance |
| Inline HTML | Streaming detect | 100% |
| Backslash escapes | One-byte lookahead | 100% |
| Images | Same as links | 100% |

**Ceiling: ~95%** — emphasis edge cases may diverge from Markdown.pl's regex behaviour.

### Lists

| Feature | Approach | Ceiling |
|---|---|---|
| Simple unordered/ordered | Column tracking + marker detect | 100% |
| Tight vs. loose | Multi-line buffer lookahead | 100% |
| Nested lists (2 levels) | Indentation tracking + stack | 100% |
| Deeply nested lists (3+ levels) | Character multiplexing | ~80% — feasible but error-prone |

**Ceiling: ~95%** — all `Markdown.mdtest` list fixtures are within the 2-level bound.

### Nested-block compositions (blockquote + list, blockquote + code, etc.)

| Feature | Approach | Ceiling |
|---|---|---|
| Blockquote containing paragraphs | Recursive dispatch | 100% |
| Blockquote containing headings | Recursive dispatch | 100% |
| Blockquote containing code blocks | Recursive dispatch | 100% |
| Blockquote containing lists | Recursive dispatch | 100% |
| Nested blockquotes (2 levels) | Recursive dispatch × 2 | 100% |
| Deeply nested blockquotes (3+ levels) | Frame management | ~80% |

**Ceiling: ~95%** — all `Markdown.mdtest` nesting fixtures are within the 2-level bound.

### Inherited divergences (permanent)

| Feature | Markdown.pl behaviour | SPL behaviour | Impact |
|---|---|---|---|
| Email autolinks | Randomised entity encoding | Plain `mailto:` link | 1 fixture affected |
| Nested blockquote closer | `<p></blockquote></p>` quirk | Well-formed close tag | 0 fixtures affected (structural improvement) |

### Overall ceiling

**Estimated: 21/23 fixtures (91%)** passing against `Markdown.mdtest`.

The two likely failures:
1. **Auto links** — email autolink encoding divergence (permanent, inherent SPL limitation)
2. **Markdown Documentation - Syntax** — the largest fixture, exercises every feature
   including emphasis edge cases and deeply nested structures that may exceed the bounded-depth
   and emphasis-matching constraints

A 22/23 outcome (96%) is achievable if emphasis matching is implemented carefully. A 23/23
outcome would require either solving the email autolink encoding (impossible without
randomness) or the fixture happening to accept plain `mailto:` links (unlikely given
Markdown.pl's entity encoding).

## Go/No-Go Recommendation

### Recommendation: CONDITIONAL GO

A greenfield SPL `Markdown.pl` port is **technically feasible** on the Lightsail 2GB/2vCPU
box. No fundamental SPL-semantics blocker was discovered. The architecture that would
underpin a "go":

1. **Runtime:** AST cache with `shakespearelang` Python interpreter. Accept 2–3s/test
   amortised cost at full-port size (~8,600+ lines). Full suite in 46–69 seconds.
2. **Architecture:** Single-act, single block dispatcher with:
   - Shared-scene return-address register pattern (Exp 2) for utility deduplication
   - Buffer-fed recursive dispatch (Exp 5) for nested-block compositions
   - Buffered inline sub-dispatch (Exp 3) invoked from paragraph/heading content emission
3. **Projected file size:** ~2,300 lines (vs. 4,311 for the Slice-1-only `shakedown.spl`)
   thanks to recursive dispatch eliminating the 1,903-line blockquote reimplementation.

### Conditions

The "go" is conditional on accepting these trade-offs:

| Trade-off | Impact | Mitigation |
|---|---|---|
| 2–3s per test at full size | Slower iteration than DuckDB (~0.5s) | AST cache amortises parse cost; still under 70s for full suite |
| O(n²) emphasis matching | Slow on large documents | Acceptable for `Markdown.mdtest` fixture sizes |
| O(n×m) reference link lookup | Slow with many references | Acceptable for fixture sizes (≤10 references) |
| Prior six-character cast pressure limits nesting ergonomics | Extra character roles and frame bookkeeping may still be needed in practice | See `docs/shakedown-spl-feasibility-assumption-corrections.md` for the corrected SPL-semantics framing |
| ~91–96% pass rate ceiling | Not 100% oracle-compatible | Email autolink divergence is permanent and accepted |

### Why "conditional" not "unconditional"

1. **No experiment achieved an unqualified PASS.** Every one returned PARTIAL, meaning
   the features work within limits but not without caveats.
2. **The runtime is borderline.** At projected full-port size, per-test cost slightly
   exceeds the 2s threshold. The Huntley loop will be slower than with DuckDB.
3. **Emphasis matching is unprototyped at scale.** The streaming approach works for simple
   cases; the buffered regex-equivalent has not been tested against Markdown.pl's full
   emphasis test surface.
4. **The prior cast design was tight.** The recovered implementation heavily multiplexed
   a small cast across block, inline, and recursive-dispatch phases. That is a real design
   pressure, but it should not be read as an SPL-level six-character limit; see
   `docs/shakedown-spl-feasibility-assumption-corrections.md`.

### Comparison to quackdown (DuckDB)

| Dimension | Shakedown (SPL) | Quackdown (DuckDB) |
|---|---|---|
| Per-test cost | 2–3s (projected) | ~0.5s |
| Full suite time | 46–69s | ~12s |
| Code size (full port) | ~2,300 lines (projected) | ~1,500 lines (Phase 2 actual) |
| Pass-rate ceiling | ~91–96% | 100% (all 23 pass) |
| Esoteric-language value | ✓ (Shakespeare Programming Language) | Moderate (SQL is unusual but not esoteric) |
| Implementation risk | High (many PARTIAL verdicts) | Low (proven, all tests passing) |

A shakedown port would be a technically impressive achievement but offers a worse
developer experience, lower pass rate, and higher risk than the existing quackdown
implementation. The primary value proposition is the novelty of a Markdown processor
written in the Shakespeare Programming Language.
