# Markdown.pl Target Surface

Shakedown ports John Gruber's `Markdown.pl` v1.0.1 to SPL. This file describes the behavioural surface that port must cover.

## Oracle

- Location: `~/markdown/Markdown.pl` on this machine.
- Version: v1.0.1 (confirmed by the version header in that file).
- Invocation: `perl ~/markdown/Markdown.pl < input.md > output.html`.

`Markdown.pl` is the single source of truth for correct output. Where its behaviour surprises, the oracle is right and Shakedown must match it — except for the intentional divergences in `docs/markdown/divergences.md`.

## Test Surface: Markdown.mdtest

The 23 fixtures at `~/mdtest/Markdown.mdtest/` define "done" for Shakedown. Each fixture is a pair: `*.text` input and `*.xhtml` (or `*.html`) expected output generated against Markdown.pl.

Fixture names (alphabetical):

- Amps and angle encoding
- Auto links
- Backslash escapes
- Blockquotes with code blocks
- Code Blocks
- Code Spans
- Hard-wrapped paragraphs with list-like lines
- Horizontal rules
- Images
- Inline HTML (Advanced)
- Inline HTML (Simple)
- Inline HTML comments
- Links, inline style
- Links, reference style
- Links, shortcut references
- Literal quotes in titles
- Markdown Documentation - Basics
- Markdown Documentation - Syntax
- Nested blockquotes
- Ordered and unordered lists
- Strong and em together
- Tabs
- Tidyness

A Shakedown run is considered correct when its output, normalised through the same whitespace and entity handling the harness uses, matches the oracle's output for each fixture — again with the exceptions in `docs/markdown/divergences.md`.

## Feature Surface

Markdown.pl v1.0.1 implements (at a high level):

### Block-level
- Paragraphs separated by blank lines.
- ATX headings (`#` through `######`).
- Setext headings (`=` and `-` underlines).
- Horizontal rules (`***`, `---`, `___` with optional spaces).
- Indented code blocks (4-space or tab indent).
- Blockquotes (`>` prefix, with lazy continuation and nested variants).
- Unordered lists (`*`, `+`, `-` markers).
- Ordered lists (digits followed by `.`).
- Loose vs tight list detection based on blank-line presence.
- Raw HTML blocks passed through without transformation.

### Inline
- Emphasis (`*text*`, `_text_`) and strong emphasis (`**text**`, `__text__`).
- Code spans (`` `text` `` including double-backtick form for literal backticks).
- Inline links (`[text](url "title")`).
- Reference links (`[text][id]` resolved to a named reference).
- Inline images (`![alt](url "title")`) and reference images.
- Auto-links (`<http://...>` and `<email@domain>`).
- Backslash escapes (`\*`, `\\`, `\[`, etc.).
- `&` and `<` entity escaping outside of code and HTML spans.
- Inline HTML tags passed through.

### Intentional divergences from oracle behaviour

See `docs/markdown/divergences.md`. Summary: email autolinks emit plain `mailto:` links (no per-character entity obfuscation; SPL has no randomness primitive); the outer close tag on nested blockquotes emits as a well-formed `</blockquote>` rather than Markdown.pl's `<p></blockquote></p>` quirk.

## Interface

`./shakedown` is invoked as a subprocess with Markdown on stdin and HTML on stdout. The test harness at `tests/test_mdtest.py` pipes each fixture through it and diffs against the oracle output.

## What This Document Does Not Decide

- How the SPL program is structured (acts, scenes, dispatch shape).
- Whether the implementation is a single `.spl` file, a shell wrapper, a Python harness, or a combination.
- Which fixtures to tackle in what order.
- Which Markdown.pl quirks beyond the two listed above (if any) to treat as acceptable divergences.

Those are architecture-planning questions. This file only defines the target.
