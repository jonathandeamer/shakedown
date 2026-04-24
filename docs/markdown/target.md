# Markdown.pl Target Surface

Shakedown ports John Gruber's `Markdown.pl` v1.0.1 to SPL. This file describes the behavioural surface that port must cover.

## Oracle

- Location: `~/markdown/Markdown.pl` on this machine.
- Version: v1.0.1 (confirmed by the version header in that file).
- Invocation: `perl ~/markdown/Markdown.pl < input.md > output.html`.

`Markdown.pl` is the single source of truth for correct output. Where its behaviour surprises, the oracle is right and Shakedown must match it. The only exception under an SPL-pure parity goal is nondeterministic email-autolink entity selection, because local `Markdown.pl` uses randomness and SPL has no verified randomness primitive.

## Test Surface: Markdown.mdtest

The 23 fixtures at `~/mdtest/Markdown.mdtest/` define the current regression corpus. Each fixture is a pair: `*.text` input and `*.xhtml` (or `*.html`) expected output. `docs/markdown/oracle-fixture-audit.md` records where these checked-in expected files differ from freshly generated local `Markdown.pl` output at the raw-byte level.

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

The default `tests/test_mdtest.py` contract compares normalized fixture output. A strict local-oracle parity check must compare Shakedown output against freshly generated `perl ~/markdown/Markdown.pl` output for the same input, because two checked-in expected files differ from local oracle raw bytes.

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

See `docs/markdown/divergences.md`. Under the Markdown.pl parity goal, nested blockquote closing is not an accepted divergence; Shakedown should reproduce the oracle quirk when strict parity is required. Email autolinks are nondeterministic in Markdown.pl, so SPL-pure parity means entity-normalized equivalence rather than byte-identical random choices.

## Parity Levels

- **Normalized mdtest contract:** current default regression check. It trims line whitespace, collapses repeated blank lines, and decodes numeric entities only for the Auto links fixture.
- **Strict local-oracle parity:** compare output against freshly generated `perl ~/markdown/Markdown.pl` output for the same input. This is the architecture target for deterministic Markdown.pl behavior.
- **Email-autolink equivalence:** compare decoded email auto-link href/text content rather than exact randomized entity choices. This is the SPL-pure target for Markdown.pl's nondeterministic email encoder.

## Interface

`./shakedown` is invoked as a subprocess with Markdown on stdin and HTML on stdout. The default test harness at `tests/test_mdtest.py` pipes each fixture through it and compares normalized output against the checked-in `.xhtml` or `.html` expected file for that fixture. It does not regenerate oracle output during the test run.

## What This Document Does Not Decide

- How the SPL program is structured (acts, scenes, dispatch shape).
- Whether the implementation is a single `.spl` file, a shell wrapper, a Python harness, or a combination.
- Which fixtures to tackle in what order.
- Which Markdown.pl quirks beyond the two listed above (if any) to treat as acceptable divergences.

Those are architecture-planning questions. This file only defines the target.
