# Slice 3 Medium-Risk Fixtures — Design

**Date:** 2026-07-14
**Status:** accepted for roadmap row 6 planning
**Scope:** architecture §7.6 and §7.8a.

## Decision

Slice 3 extends the proved four-act IR pipeline; it does not add a second parser.
Act I collects valid reference definitions into a private, document-scoped,
case-folded table and removes their source lines. Acts II and III preserve that
carrier. Act III resolves images before anchors using a non-destructive table
scan; missing references replay their original Markdown bytes. The temporary
Slice-2 definition-discard route is replaced in the same checkpoint.

Inline HTML tags/comments stay protected glyph regions inside a paragraph.
Simple left-margin HTML blocks and standalone comments use the already
allocated `RAW_HTML_HASH = 10` text leaf and Act IV emits them outside
paragraph tags. Advanced nested/attributed HTML remains Slice 4. Act II adds
only the top-level hard-wrap/list ambiguity and quote-to-code-leaf formation;
Act IV renders the existing quote/code frame composition.

## Invariants

- No runtime Markdown.pl fallback, changed fixture expected bytes, or new parser.
- Every enabled fixture has a focused mdtest pass, strict parity
  `summary: 1/1 byte-identical`, prior-fixture regression, and spike regression.
- `Auto links` keeps its documented entity-normalized mdtest comparison only;
  it grants no strict-parity exception to Slice 3.
- A required new token, third participant, unreserved literary surface, or
  changed table ownership is `BLOCK[plan]` and stops the task.

## Order

1. Establish tests and prove the currently declared shipped baseline.
2. Hard-wrapped paragraph/list ambiguity.
3. Reference collection, links, images, and title quotes.
4. Strong/em nesting.
5. Simple HTML/comments.
6. Blockquotes with code leaves and complete Slice-3 verification.
