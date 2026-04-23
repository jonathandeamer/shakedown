# Fixture Outlook for a Fresh Build

> This file replaces the prior `shakedown-mdtest-fixture-matrix.md`. The prior matrix assigned pass-oriented labels based on a 4,311-line block-level implementation that does not exist in this repository. This file reframes the outlook as *risk tiers for a fresh build*.

## How to Read This File

This is a planning input, not a scorecard. It ranks each of the 23 `Markdown.mdtest` fixtures by expected implementation risk given what is known today about SPL semantics (from `docs/spl/`), the prior attempt's lessons (from `docs/prior-attempt/`), and intentional divergences (from `docs/markdown/divergences.md`).

As of 2026-04-23, the current `./shakedown` entry point passes all 23 `Markdown.mdtest` fixtures because it delegates to `~/markdown/Markdown.pl`. That is useful contract evidence, but it is not SPL implementation evidence. The tiers below describe residual SPL implementation risk for a fresh build.

Risk tiers:
- **Low** — no known architectural obstacle; implementation is straightforward once the block/inline pipeline is in place.
- **Medium** — behaviour-level edge cases in Markdown.pl may be hard to reproduce exactly; core implementation is tractable.
- **High** — fundamental risk tied to SPL limits or to Markdown.pl quirks that resist reproduction.
- **Divergence** — will not match oracle; covered by `docs/markdown/divergences.md`.

## Fixture Outlook

| Fixture | Risk tier | Primary risk | Notes |
|---|---|---|---|
| ATX Headers | Low | — | Block-level structure is straightforward in a streaming dispatcher. |
| Setext Headers | Low | — | Two-line look-behind is supported by the standalone delayed-line probe. |
| Paragraphs and Simple Blocks | Low | — | The core flow of the block pipeline. |
| Horizontal Rules | Low | — | Single-line pattern. |
| Indented Code Blocks | Low | Interaction with nested blocks | HTML-encoding `<` and `&` inside the code block is routine. |
| Blockquotes | Low-Medium | Nested composition | Simple blockquote is proven in `./shakedown-dev`; richer nested blockquote composition remains design risk. |
| Code Spans | Low | — | Streaming inline toggle. |
| Emphasis | Medium | Markdown.pl backtracking | Simple emphasis is proven in `./shakedown-dev`; exact overlap remains a design choice. |
| Strong Emphasis | Medium | Same as Emphasis | The prototype does not yet prove full Markdown.pl strong/em overlap parity. |
| Inline Links | Low | Inline complexity | Bracket/paren state machine plus optional title. |
| Reference Links | Medium | SPL lookup mechanics | The standalone lookup probe supports a stack-backed linear strategy; full Markdown syntax is still unimplemented. |
| Inline Images | Low | Same as Inline Links | Structurally equivalent to inline links with a leading `!`. |
| Reference Images | Medium | Same as Reference Links | Inherits the reference-link lookup risk and should reuse the same stack-backed strategy. |
| Auto Links | Divergence | Email autolink encoding | Plain `<a href="mailto:...">` replaces Markdown.pl's randomised entity obfuscation. See `docs/markdown/divergences.md`. |
| Backslash Escapes | Low | — | One-byte lookahead. |
| Inline HTML | Low-Medium | Tag detection accuracy | Passes raw HTML through; boundary detection has edge cases. |
| Ordered Lists | Medium | Loose-list exactness | The standalone list-state probe supports a dedicated looseness carrier; full list syntax is still unimplemented. |
| Unordered Lists | Medium | Loose-list exactness | Same risk class as Ordered Lists. |
| Nested Lists | Medium | Loose-list x nesting | The standalone list-state probe lowers the mechanics risk; full nested list output remains unimplemented. |
| HTML Blocks | Low-Medium | Block boundary detection | Distinguishing raw HTML blocks from inline HTML requires careful lookahead. |
| Ampersands and Angle Brackets | Low | — | Entity encoding at the right points of the pipeline. |
| Nested Block Structures | High | Exact nested output | Simple blockquote is proven in `./shakedown-dev`; full nested block composition is not. |
| Markdown Documentation - Syntax | High | Combined ceiling risks | The largest fixture is oracle-stub green but not SPL-proven. |

## What Would Lower These Risks

- **For inline edge cases:** a prototype of the buffered-scan path that can be diff'd against Markdown.pl on representative snippets before committing to the wider implementation.
- **For Reference Links:** a production slice that applies the standalone stack-backed lookup mechanics to real Markdown labels.
- **For List risks:** a production slice that applies the standalone stack-backed list-frame mechanics to real tight/loose list syntax, plus an explicit decision on exact loose-list parity.
- **For Nested Block High risks:** a prototype of the recursive-dispatch framing pattern that exercises blockquote-containing-list and blockquote-containing-code, diffed against the oracle.

These are fallback prototypes architecture planning may choose to run, not commitments made here.

## What This Outlook Does Not Claim

- It does not predict pass/fail counts. The prior attempt's "~91–96% ceiling" estimate was tied to a specific implementation and does not transfer to a fresh build.
- It does not assume any fixture is "already implemented" because the prior implementation is not present and the current mdtest pass runs through the oracle stub.
- It does not commit to a fixture order or slice structure.
