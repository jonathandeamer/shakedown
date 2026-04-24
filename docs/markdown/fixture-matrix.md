# Markdown.mdtest Fixture Matrix

This is the fixture-by-fixture matrix for the 23 local `Markdown.mdtest` fixtures. It complements
`docs/markdown/fixture-outlook.md`, which is a feature-risk outlook rather than a fixture matrix.

The input line and byte counts are from `~/mdtest/Markdown.mdtest/*.text` on this machine.
Expected files are the checked-in `.xhtml` or `.html` files used by `tests/test_mdtest.py`.

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

## How to Use This Matrix

- Use it to pick fixture-sized milestones.
- Use `docs/markdown/oracle-fixture-audit.md` before making strict raw-byte claims.
- Use `docs/markdown/reference-mechanics.md`, `html-block-boundaries.md`, and `list-mechanics.md`
  for the high-risk mechanics behind the fixture rows.
- Do not treat the current oracle-stub `./shakedown` pass as SPL implementation coverage.
