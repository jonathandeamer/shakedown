# Reference Link Mechanics

This document expands the Markdown.pl reference-definition and reference-link behaviour that
architecture planning must account for. It is based on local `~/markdown/Markdown.pl` v1.0.1,
especially `_StripLinkDefinitions`, `_DoImages`, and `_DoAnchors`.

## Pipeline Position

Reference definitions are stripped near the top of the document pipeline, before block parsing.
Reference links and images are resolved later in the span pipeline:

1. `_StripLinkDefinitions` removes definition lines from the document and stores URL/title data.
2. `_RunBlockGamut` forms blocks without seeing those definition lines.
3. `_RunSpanGamut` runs images before anchors.
4. Reference images and links look up the document-scoped definition table.

This means a parity design needs document-scoped reference collection before inline resolution.

## Definition Syntax

Markdown.pl accepts reference definitions with these mechanics:

- Up to three leading spaces before `[id]:`.
- Link IDs are case-insensitive; the stored key is lowercased.
- The URL may be preceded by optional whitespace and at most one newline after the colon.
- The URL may be wrapped in angle brackets.
- An optional title may appear after whitespace, with optional one-line wrapping.
- Stored URLs are run through ampersand/angle encoding.
- Stored titles escape double quotes as `&quot;`.
- Definition lines are removed from the document before block parsing.

The title delimiter handling follows Markdown.pl's regex, not a modern Markdown parser's
cleaner grammar. Architecture work should test against the oracle rather than "fixing" that
grammar by preference.

## Reference Image Resolution

Images are processed before anchors. Reference image syntax uses:

- `![alt text][id]`
- `![alt text][]`, where an empty ID uses the alt text as the ID

If the ID resolves, Markdown.pl emits an `<img>` tag with `src`, `alt`, optional `title`, and
the configured empty-element suffix. Double quotes in alt text and titles are escaped. Literal
`*` and `_` in URLs and titles are escaped internally before later emphasis processing.

If the ID is missing, Markdown.pl leaves the original image markup intact.

## Reference Link Resolution

Reference links use:

- `[link text][id]`
- `[link text][]`, where an empty ID uses the link text as the ID
- spaced full references such as `[link text] [id]`

Full reference syntax allows one optional space and one optional newline between the closing
link-text bracket and the opening ID bracket. Link text can contain nested brackets using the
same nested-bracket pattern as inline links.

The local v1.0.1 oracle does not turn a bare `[link text]` into a link. The fixture named
`Links, shortcut references` is therefore a fixture name to preserve, not proof that bare
shortcut references are active in this oracle.

If the ID resolves, Markdown.pl emits an `<a>` tag with `href`, optional `title`, and the
original link text. Literal `*` and `_` in URLs and titles are escaped internally before later
emphasis processing.

If the ID is missing, Markdown.pl leaves the original link markup intact.

## Fixtures That Exercise This Area

| Fixture | Coverage |
|---|---|
| `Links, reference style` | Full, spaced full, collapsed, case/indent definitions, nested brackets, broken-line link text, bare bracket non-links. |
| `Links, shortcut references` | Spaced full references and bare bracket non-links despite the fixture name. |
| `Images` | Inline and reference image syntax. |
| `Markdown Documentation - Syntax` | Large mixed examples with definitions, links, images, and HTML. |

## Architecture Inputs

Reference support needs:

- a document-scoped lookup table or equivalent stack-backed structure;
- case-insensitive keys;
- a way to remove definitions before block parsing;
- span-time lookup for images before links;
- exact missing-reference fallback behaviour.

`tests/test_pre_design_probes.py` confirms a stack-backed lookup mechanic, but full Markdown
reference parsing remains production work.
