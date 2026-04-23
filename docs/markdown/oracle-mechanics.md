# Markdown.pl Oracle Mechanics

This file records the local `~/markdown/Markdown.pl` mechanics that matter for Shakedown parity. Line numbers refer to the local v1.0.1 file verified on 2026-04-23.

## Top-Level Pipeline

| Order | Function | Local lines | Parity requirement |
|---:|---|---:|---|
| 1 | `Markdown` setup | 226-271 | Normalize line endings, append `\n\n`, detab via `_Detab`, strip whitespace-only leading/trailing lines, hash block HTML, strip link definitions, run block gamut, unescape special chars. |
| 2 | `_Detab` | 1307-1318 | Expand tabs to four-column tab stops before most parsing. Code and list behavior depend on this. |
| 3 | `_HashHTMLBlocks` | 313-419 | Protect block-level HTML before Markdown block processing, then hash new block-level HTML generated during recursion. |
| 4 | `_StripLinkDefinitions` | 274-311 | Remove reference definitions before block parsing and store case-insensitive URL/title data. |
| 5 | `_RunBlockGamut` | 423-452 | Apply block transforms in Markdown.pl order: headers, horizontal rules, lists, code blocks, blockquotes, HTML block hashing, paragraph formation. |
| 6 | `_UnescapeSpecialChars` | 1242-1251 | Restore hashed special characters after all block/span processing. |

## Block Pipeline

| Order | Function | Local lines | Parity requirement |
|---:|---|---:|---|
| 1 | `_DoHeaders` | 718-757 | Setext headers run before ATX headers; header contents are processed through `_RunSpanGamut`. |
| 2 | horizontal-rule substitutions | 430-435 | `***`, `---`, and `___` rules allow optional spaces and up to two leading spaces. |
| 3 | `_DoLists` | 760-845 | List parsing happens before code blocks and blockquotes. Ordered and unordered list markers share recursive list-level state. |
| 4 | `_ProcessListItems` | 848-913 | Tight/loose output depends on leading blank lines and blank lines within each item. Loose items run `_RunBlockGamut`; tight items run `_RunSpanGamut` after nested-list handling. |
| 5 | `_DoCodeBlocks` | 916-945 | Code blocks are found after list processing. Contents are outdented, encoded, detabbed, stripped of leading/trailing blank lines, then wrapped in `<pre><code>`. |
| 6 | `_DoBlockQuotes` | 1049-1082 | Blockquotes recursively run `_RunBlockGamut` on stripped quote contents, prefix every output line with two spaces, and then remove that added indent inside embedded `<pre>` blocks before wrapping in `<blockquote>`. That code-block-in-blockquote indent fix is part of strict local-oracle byte parity. |
| 7 | `_FormParagraphs` | 1085-1119 | Unhashed chunks become paragraphs after span processing; hashed HTML blocks are restored without paragraph wrapping. |

## Span Pipeline

| Order | Function | Local lines | Parity requirement |
|---:|---|---:|---|
| 1 | `_RunSpanGamut` | 455-484 | Span transforms run in a fixed order; later transforms see earlier HTML substitutions. |
| 2 | `_DoCodeSpans` | 950-993 | Code spans run before escapes, links, auto-links, entity encoding, and emphasis. Backtick runs can delimit content containing shorter backtick runs. |
| 3 | `_EscapeSpecialChars` | 487-513 | HTML tags and backslash escapes are tokenized/hashed before link and emphasis processing. |
| 4 | `_DoImages` | 613-715 | Image syntax is processed before anchor syntax. Reference image lookup uses stripped link definitions. |
| 5 | `_DoAnchors` | 516-610 | Inline, full-reference, collapsed-reference, and shortcut-reference links are processed before auto-links and entity encoding. |
| 6 | `_DoAutoLinks` | 1167-1187 | HTTP/HTTPS/FTP auto-links produce literal link text. Email auto-links call `_EncodeEmailAddress`, which is randomized. |
| 7 | `_EncodeAmpsAndAngles` | 1122-1135 | Ampersands not part of an entity and angle brackets not starting an HTML tag are encoded after links and auto-links. |
| 8 | `_DoItalicsAndBold` | 1035-1047 | Strong substitutions run before emphasis substitutions. This order is required for Markdown.pl's overlapping `<em>/<strong>` behavior. |
| 9 | hard-break substitution | 481 | Two or more spaces before newline become `<br />` after emphasis processing. |

## Reference Definitions

`_StripLinkDefinitions` stores URLs and optional titles in global hashes keyed by lowercased link identifier. Reference definitions are removed from the document before block parsing, so a parity design needs document-scoped reference collection before inline reference resolution.

## Strict Fixture Audit Finding

`docs/markdown/oracle-fixture-audit.md` shows that two checked-in expected files differ from local `Markdown.pl` raw output while still matching the normalized test contract:

| Fixture | Raw status | Normalized status | Reason class |
|---|---|---|---|
| Blockquotes with code blocks | mismatch | match | Local Markdown.pl emits different indentation inside blockquoted code blocks and around the second paragraph. |
| Code Blocks | mismatch | match | Local Markdown.pl output differs in trailing spaces inside a code block. |

Strict local-oracle byte parity must compare against freshly generated local `Markdown.pl` output, not only the checked-in `.xhtml`/`.html` expected files.

## Nondeterministic Email Auto-Links

`_EncodeEmailAddress` uses Perl randomness to encode email auto-links. SPL has no verified randomness primitive. A strict byte-for-byte target cannot promise identical output for email auto-links across repeated oracle runs. The achievable SPL-pure target is entity-normalized email-link equivalence unless the project deliberately adds non-SPL runtime help.
