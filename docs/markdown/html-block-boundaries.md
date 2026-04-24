# HTML Block Boundaries

This document records Markdown.pl's raw HTML block boundary mechanics for architecture planning.
It is based on local `~/markdown/Markdown.pl` v1.0.1, especially `_HashHTMLBlocks`.

## Pipeline Position

Markdown.pl protects block-level HTML before normal Markdown block processing, then hashes HTML
blocks again near the end of `_RunBlockGamut`. Protected blocks are restored during paragraph
formation instead of being wrapped in `<p>`.

Inline HTML is different: span processing tokenizes tags so inline tags can pass through inside
paragraphs.

## Block Tag Sets

Markdown.pl hard-codes block tags. The broad set includes:

`p`, `div`, `h1`-`h6`, `blockquote`, `pre`, `table`, `dl`, `ol`, `ul`, `script`,
`noscript`, `form`, `fieldset`, `iframe`, `math`, `ins`, and `del`.

A second matching pass uses the same set except `ins` and `del`.

This hard-coded list is the target surface. Architecture planning should not substitute a
modern HTML block parser without checking fixture and oracle behaviour.

## Boundary Rules

Markdown.pl has several distinct block-HTML cases:

1. **Nested block tags.** A block tag that starts at the left margin can protect content through
   a matching closing tag. The special nested pass runs before the more liberal pass.
2. **Liberal block tags.** A later pass protects from a left-margin opening block tag through a
   matching closing tag followed by a blank line or end of document.
3. **Raw `<hr>` tags.** Standalone HTML `hr` tags are special-cased. They can have up to three
   leading spaces and must start after a blank line or at the beginning of the document.
4. **Standalone HTML comments.** Comments are special-cased with the same blank-line/start and
   up-to-three-spaces boundary shape as raw `<hr>` tags.

The block-tag passes require the opening tag at the left margin. The `hr` and comment special
cases allow indentation up to one less than the tab width.

## Why This Is Risky

HTML block hashing happens before reference definition stripping and before normal block
processing. It can therefore change whether nearby text becomes a paragraph, raw HTML, or
Markdown content. It also uses Markdown.pl's fixed tag list and regex boundaries rather than
the CommonMark HTML block rules.

## Fixtures That Exercise This Area

| Fixture | Coverage |
|---|---|
| `Inline HTML (Simple)` | Inline tags and simple block tags. |
| `Inline HTML (Advanced)` | Nested and attributed `div` blocks. |
| `Inline HTML comments` | Standalone comments and paragraph interaction. |
| `Markdown Documentation - Syntax` | Mixed raw HTML examples inside the large documentation fixture. |

## Architecture Inputs

A future design should state:

- how HTML block protection is represented;
- whether protected blocks are stored by hash, token, sentinel, or another mechanism;
- how raw HTML blocks are kept out of paragraph wrapping;
- how the second `_RunBlockGamut` HTML hashing point is reproduced or justified.
