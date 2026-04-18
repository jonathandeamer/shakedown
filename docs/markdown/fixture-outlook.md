# Fixture Outlook for a Fresh Build

> This file replaces the prior `shakedown-mdtest-fixture-matrix.md`. The prior matrix assigned "likely pass / uncertain / likely fail" labels based on a 4,311-line block-level implementation that does not exist in this repository. This file reframes the outlook as *risk tiers for a fresh build*.

## How to Read This File

This is a planning input, not a scorecard. It ranks each of the 23 `Markdown.mdtest` fixtures by expected implementation risk given what is known today about SPL semantics (from `docs/spl/`), the prior attempt's lessons (from `docs/prior-attempt/`), and intentional divergences (from `docs/markdown/divergences.md`).

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
| Blockquotes | Low–Medium | Nested composition | Lazy continuation and heading/code-block-inside-blockquote were proven in the prior attempt. |
| Code Spans | Low | — | Streaming inline toggle. |
| Emphasis | Medium | Markdown.pl backtracking | Simple emphasis streams cleanly; exact backtracking semantics may diverge on nested/contextual cases. |
| Strong Emphasis | Medium | Same as Emphasis | `**x**` / `__x__` pairing inherits the same risk class. |
| Inline Links | Low–Medium | Inline complexity | Bracket/paren state machine plus optional title. |
| Reference Links | Medium | Two-pass lookup | Requires collecting definitions on a first pass; O(n×m) lookup acceptable at fixture sizes. |
| Inline Images | Low–Medium | Same as Inline Links | Structurally equivalent to inline links with a leading `!`. |
| Reference Images | Medium | Same as Reference Links | Inherits the reference-link risks. |
| Auto Links | Divergence | Email autolink encoding | Plain `<a href="mailto:...">` replaces Markdown.pl's randomised entity obfuscation. See `docs/markdown/divergences.md`. |
| Backslash Escapes | Low | — | One-byte lookahead. |
| Inline HTML | Low–Medium | Tag detection accuracy | Passes raw HTML through; boundary detection has edge cases. |
| Ordered Lists | Medium | Loose-list exactness | Tight lists are tractable; loose-list buffering was a PARTIAL in the prior attempt. |
| Unordered Lists | Medium | Loose-list exactness | Same risk class as Ordered Lists. |
| Nested Lists | Medium–High | Loose-list × nesting | Two-level nesting is tractable; interaction with loose-list semantics is the highest-risk inline area. |
| HTML Blocks | Low–Medium | Block boundary detection | Distinguishing raw HTML blocks from inline HTML requires careful lookahead. |
| Ampersands and Angle Brackets | Low | — | Entity encoding at the right points of the pipeline. |
| Nested Block Structures | High | Exact nested output | Sentinel-framed recursive dispatch works mechanically; exact composition output was fragile in the prior attempt. |
| Markdown Documentation - Syntax | High | Combined ceiling risks | The largest fixture; exercises every feature including emphasis edge cases and deeply nested structures. |

## What Would Lower These Risks

- **For Medium inline risks (Emphasis, Reference Links):** a prototype of the buffered-scan path that can be diff'd against Markdown.pl on representative snippets before committing to the wider implementation.
- **For List risks:** an explicit design decision on whether to aim for loose-list exactness or accept a documented divergence (list risks would drop a tier under divergence).
- **For Nested Block High risks:** a prototype of the recursive-dispatch framing pattern that exercises blockquote-containing-list and blockquote-containing-code, diffed against the oracle.

These are prototypes architecture planning may choose to run, not commitments made here.

## What This Outlook Does Not Claim

- It does not predict pass/fail counts. The prior attempt's "~91–96% ceiling" estimate was tied to a specific implementation and does not transfer to a fresh build.
- It does not assume any fixture is "already implemented" because the prior implementation is not present.
- It does not commit to a fixture order or slice structure.
