# Fixture Outlook for a Fresh Build

> This file replaces the prior `shakedown-mdtest-fixture-matrix.md`. The prior matrix assigned "likely pass / uncertain / likely fail" labels based on a 4,311-line block-level implementation that does not exist in this repository. This file reframes the outlook as *risk tiers for a fresh build*.

## How to Read This File

This is a planning input, not a scorecard. It ranks each of the 23 `Markdown.mdtest` fixtures by expected implementation risk given what is known today about SPL semantics (from `docs/spl/`), the prior attempt's lessons (from `docs/prior-attempt/`), and intentional divergences (from `docs/markdown/divergences.md`).

As of 2026-04-23, the current `./shakedown-dev` binary passes all 23 `Markdown.mdtest` fixtures (`uv run pytest tests/test_mdtest.py -q` -> `23 passed in 1.44s`). The tiers below therefore describe residual risk for a fresh rebuild, not the current corpus status.

Risk tiers:
- **Low** — no known architectural obstacle; implementation is straightforward once the block/inline pipeline is in place.
- **Medium** — behaviour-level edge cases in Markdown.pl may be hard to reproduce exactly; core implementation is tractable.
- **High** — fundamental risk tied to SPL limits or to Markdown.pl quirks that resist reproduction.
- **Divergence** — will not match oracle; covered by `docs/markdown/divergences.md`.

## Fixture Outlook

| Fixture | Risk tier | Primary risk | Notes |
|---|---|---|---|
| ATX Headers | Low | — | Block-level structure is straightforward in a streaming dispatcher. |
| Setext Headers | Low | — | Two-line look-behind; manageable with line buffering. |
| Paragraphs and Simple Blocks | Low | — | The core flow of the block pipeline. |
| Horizontal Rules | Low | — | Single-line pattern. |
| Indented Code Blocks | Low | Interaction with nested blocks | HTML-encoding `<` and `&` inside the code block is routine. |
| Blockquotes | Low | Nested composition | Lazy continuation and heading/code-block-inside-blockquote are already green in the current corpus. |
| Code Spans | Low | — | Streaming inline toggle. |
| Emphasis | Low | Markdown.pl backtracking | Simple emphasis and the current corpus backtracking case are already green. |
| Strong Emphasis | Low | Same as Emphasis | `**x**` / `__x__` pairing is already green in the current corpus. |
| Inline Links | Low | Inline complexity | Bracket/paren state machine plus optional title. |
| Reference Links | Low | Two-pass lookup | The current corpus is green; the remaining question is how to encode the lookup cleanly in SPL. |
| Inline Images | Low | Same as Inline Links | Structurally equivalent to inline links with a leading `!`. |
| Reference Images | Low | Same as Reference Links | Inherits the reference-link mechanics, which are already green in the current corpus. |
| Auto Links | Divergence | Email autolink encoding | Plain `<a href="mailto:...">` replaces Markdown.pl's randomised entity obfuscation. See `docs/markdown/divergences.md`. |
| Backslash Escapes | Low | — | One-byte lookahead. |
| Inline HTML | Low | Tag detection accuracy | Passes raw HTML through; boundary detection is now corpus-validated. |
| Ordered Lists | Low | Loose-list exactness | Tight and loose list handling are already green in the current corpus. |
| Unordered Lists | Low | Loose-list exactness | Same risk class as Ordered Lists. |
| Nested Lists | Low | Loose-list x nesting | Nested composition is already green in the current corpus. |
| HTML Blocks | Low | Block boundary detection | Distinguishing raw HTML blocks from inline HTML is already corpus-validated. |
| Ampersands and Angle Brackets | Low | — | Entity encoding at the right points of the pipeline. |
| Nested Block Structures | Low | Exact nested output | Exact composition output is already green in the current corpus. |
| Markdown Documentation - Syntax | Low | Combined ceiling risks | The largest fixture is already green, so the remaining risk is regression rather than unknown behavior. |

## What Would Lower These Risks

- **For any remaining inline edge cases:** a prototype of the buffered-scan path that can be diff'd against Markdown.pl on representative snippets before committing to the wider implementation.
- **For list policy changes:** an explicit design decision on whether to aim for loose-list exactness or accept a documented divergence.
- **For any future nested-block regression:** a prototype of the recursive-dispatch framing pattern that exercises blockquote-containing-list and blockquote-containing-code, diffed against the oracle.

These are fallback prototypes architecture planning may choose to run, not commitments made here.

## What This Outlook Does Not Claim

- It does not predict pass/fail counts. The prior attempt's "~91–96% ceiling" estimate was tied to a specific implementation and does not transfer to a fresh build.
- It does not assume any fixture is "already implemented" because the prior implementation is not present.
- It does not commit to a fixture order or slice structure.
