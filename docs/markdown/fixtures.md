# Markdown.mdtest Fixtures

Canonical fixture reference for the 23 `Markdown.mdtest` fixtures. Combines the
per-fixture matrix and the feature-risk outlook that were previously split
across two separate docs.

## Fixture Matrix

| Fixture | Expected | Lines | Bytes | Primary mechanics | Fresh-build risk | Strict local-oracle caveat |
|---|---|---:|---:|---|---|---|
| Amps and angle encoding | `.xhtml` | 20 | 381 | Entity encoding outside code/HTML. | Low | None known. |
| Auto links | `.xhtml` | 12 | 263 | URL auto-links in paragraphs, lists, blockquotes, code. | Low | Fixture does not cover randomized email auto-links. |
| Backslash escapes | `.xhtml` | 120 | 1250 | Escape table across punctuation and Markdown syntax. | Low | None known. |
| Blockquotes with code blocks | `.xhtml` | 11 | 135 | Blockquote recursion and code-block indentation repair. | Medium | Checked-in expected differs from fresh local oracle raw bytes but matches normalized contract. |
| Code Blocks | `.xhtml` | 13 | 199 | Indented code blocks and trailing-space preservation. | Low | Checked-in expected differs from fresh local oracle raw bytes but matches normalized contract. |
| Code Spans | `.xhtml` | 4 | 165 | Backtick-run span parsing and entity encoding inside code spans. | Low | None known. |
| Hard-wrapped paragraphs with list-like lines | `.xhtml` | 8 | 197 | Paragraph continuation versus ordered-list ambiguity. | Medium | None known. |
| Horizontal rules | `.xhtml` | 67 | 270 | `*`, `-`, `_` rule recognition with spacing. | Low | None known. |
| Images | `.xhtml` | 25 | 440 | Inline images, reference images, title/alt escaping. | Medium | Depends on reference mechanics. |
| Inline HTML (Advanced) | `.xhtml` | 30 | 312 | Nested/attributed raw HTML block boundaries. | Medium | None known. |
| Inline HTML (Simple) | `.html` | 69 | 553 | Inline tags, block tags, paragraph interaction. | Medium | Uses `.html` expected file. |
| Inline HTML comments | `.html` | 13 | 164 | Standalone HTML comments and paragraph interaction. | Medium | Uses `.html` expected file. |
| Links, inline style | `.xhtml` | 24 | 578 | Inline anchors, optional titles, nested brackets. | Low-Medium | None known. |
| Links, reference style | `.xhtml` | 71 | 791 | Definitions, full/collapsed/shortcut refs, nested brackets. | Medium | Depends on document-scoped reference table. |
| Links, shortcut references | `.xhtml` | 20 | 236 | Spaced full references and bare bracket non-links. | Medium | Fixture name does not imply bare `[text]` links in the local oracle. |
| Literal quotes in titles | `.xhtml` | 7 | 108 | Link/image title quote escaping. | Low-Medium | None known. |
| Markdown Documentation - Basics | `.xhtml` | 306 | 8064 | Broad documentation examples across basic block/span features. | High | Aggregate fixture should not be first proof of any risky feature. |
| Markdown Documentation - Syntax | `.xhtml` | 888 | 27428 | Largest mixed fixture: blocks, spans, HTML, references, lists. | High | Aggregate fixture should be used after smaller feature fixtures. |
| Nested blockquotes | `.xhtml` | 5 | 24 | Nested blockquote recursion and closing-tag quirks. | High | Nested blockquote closing is not an accepted divergence. |
| Ordered and unordered lists | `.xhtml` | 131 | 903 | Tight/loose lists, nesting, marker families, multi-paragraph items. | High | Exact loose-list output is a known open risk. |
| Strong and em together | `.xhtml` | 7 | 107 | Strong-before-emphasis substitution order. | Medium | Prototype XFAIL is not a forced divergence. |
| Tabs | `.xhtml` | 21 | 311 | Detab before block parsing, code/list interactions. | Medium | None known. |
| Tidyness | `.xhtml` | 5 | 78 | Output blank-line normalization/tidiness. | Low | None known. |

### How to Use This Matrix

- Use it to pick fixture-sized milestones.
- Use `docs/markdown/oracle-fixture-audit.md` before making strict raw-byte claims.
- Use `docs/markdown/reference-mechanics.md`, `html-block-boundaries.md`, and `list-mechanics.md`
  for the high-risk mechanics behind the fixture rows.
- Do not treat the current oracle-stub `./shakedown` pass as SPL implementation coverage.

## Feature Risk Outlook for a Fresh Build

### How to Read This File

This is a planning input, not a scorecard and not a fixture matrix. It ranks Markdown feature areas by expected implementation risk given what is known today about SPL semantics (from `docs/spl/`), the prior attempt's lessons (from `docs/prior-attempt/`), and the parity exceptions in `docs/markdown/divergences.md`.

As of 2026-04-23, the current `./shakedown` entry point passes all 23 `Markdown.mdtest` fixtures because it delegates to `~/markdown/Markdown.pl`. That is useful contract evidence, but it is not SPL implementation evidence. The tiers below describe residual SPL implementation risk for a fresh build.

Risk tiers:
- **Low** — no known architectural obstacle; implementation is straightforward once the block/inline pipeline is in place.
- **Medium** — behaviour-level edge cases in Markdown.pl may be hard to reproduce exactly; core implementation is tractable.
- **High** — fundamental risk tied to SPL limits or to Markdown.pl quirks that resist reproduction.
- **Parity exception** — byte-identical Markdown.pl behavior is not available in pure SPL; the target must use a documented equivalence rule.

### Feature Outlook

| Feature area | Risk tier | Primary risk | Notes |
|---|---|---|---|
| ATX Headers | Low | — | Block-level structure is straightforward in a streaming dispatcher. |
| Setext Headers | Low | — | Two-line look-behind is supported by the standalone delayed-line probe. |
| Paragraphs and Simple Blocks | Low | — | The core flow of the block pipeline. |
| Horizontal Rules | Low | — | Single-line pattern. |
| Indented Code Blocks | Low | Interaction with nested blocks | HTML-encoding `<` and `&` inside the code block is routine. |
| Blockquotes | Low-Medium | Nested composition | Simple blockquote is proven in `./shakedown-dev`; richer nested blockquote composition remains design risk. |
| Code Spans | Low | — | Streaming inline toggle. |
| Emphasis | Medium | Markdown.pl backtracking | Simple emphasis is proven in `./shakedown-dev`; exact overlap requires Markdown.pl's strong-then-emphasis order; mechanics closed by B15. |
| Strong Emphasis | Medium | Same as Emphasis | The prototype does not yet prove full Markdown.pl strong/em overlap parity; the detailed spec should use a two-pass inline design; mechanics closed by B15. |
| Inline Links | Low | Inline complexity | Bracket/paren state machine plus optional title. |
| Reference Links | Medium | SPL lookup mechanics | The standalone lookup probe supports a stack-backed linear strategy; full Markdown syntax is still unimplemented. |
| Inline Images | Low | Same as Inline Links | Structurally equivalent to inline links with a leading `!`. |
| Reference Images | Medium | Same as Reference Links | Inherits the reference-link lookup risk and should reuse the same stack-backed strategy. |
| Auto Links | Low for mdtest; Parity exception for email autolinks | Email autolink randomization | The mdtest fixture covers URL autolinks only. Email autolinks require entity-normalized equivalence because Markdown.pl randomizes entity choice. |
| Backslash Escapes | Low | — | One-byte lookahead. |
| Inline HTML | Low-Medium | Tag detection accuracy | Passes raw HTML through; boundary detection has edge cases. |
| Ordered Lists | Medium | Loose-list exactness | The standalone list-state probe supports a dedicated looseness carrier; full list syntax is still unimplemented. |
| Unordered Lists | Medium | Loose-list exactness | Same risk class as Ordered Lists. |
| Nested Lists | Medium | Loose-list x nesting | The standalone list-state probe lowers the mechanics risk; full nested list output remains unimplemented. |
| HTML Blocks | Low-Medium | Block boundary detection | Distinguishing raw HTML blocks from inline HTML requires careful lookahead. |
| Ampersands and Angle Brackets | Low | — | Entity encoding at the right points of the pipeline. |
| Nested Block Structures | High | Exact nested output | Simple blockquote is proven in `./shakedown-dev`; full nested block composition must include Markdown.pl quirks when strict parity is required; frame-stack mechanics closed by B16. |
| Markdown Documentation - Syntax | High | Combined ceiling risks | The largest fixture is oracle-stub green but not SPL-proven. |

### What Would Lower These Risks

- **For inline edge cases:** a prototype of the buffered-scan path that can be diff'd against Markdown.pl on representative snippets before committing to the wider implementation.
- **For Reference Links:** a production slice that applies the standalone stack-backed lookup mechanics to real Markdown labels.
- **For List risks:** a production slice that applies the standalone stack-backed list-frame mechanics to real tight/loose list syntax, plus an explicit decision on exact loose-list parity.
- **For Nested Block High risks:** a prototype of the recursive-dispatch framing pattern that exercises blockquote-containing-list and blockquote-containing-code, diffed against the oracle.

These are fallback prototypes architecture planning may choose to run, not commitments made here.

### What This Outlook Does Not Claim

- It does not predict pass/fail counts. The prior attempt's "~91–96% ceiling" estimate was tied to a specific implementation and does not transfer to a fresh build.
- It does not assume any fixture is "already implemented" because the prior implementation is not present and the current mdtest pass runs through the oracle stub.
- It does not commit to a fixture order or slice structure.

## How the Two Views Relate

The matrix is fixture-level (one row per mdtest fixture). The outlook is
feature-level (one row per Markdown feature area). Use the matrix to pick
fixture-sized milestones and to check strict-oracle caveats; use the outlook
to understand which features are mechanics-closed vs still open.
