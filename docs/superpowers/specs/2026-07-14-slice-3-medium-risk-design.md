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

## Amendment A1 (2026-07-14): Existing hard-wrap behavior is a promotion, not a repair

The exact two probes (`Paragraph\n8. Oops\n` and `\n\n8. List\n`) and the
complete `Hard-wrapped paragraphs with list-like lines` fixture already have
the required behavior in both the fast interpreter and committed release
binary. Therefore Slice-3 Task 2 must promote and preserve this proved
baseline; it must not manufacture a red test or alter Act II merely to make
one fail.

Task 2 Step 1 makes the two probes and full-fixture contract green, enables
only that fixture, and proves the direct mdtest node plus strict parity. Its
pytest selectors must use either Python test identifiers or a fully quoted
node id; `-k 'Hard-wrapped paragraphs'` is invalid pytest syntax because the
hyphen is parsed as an operator. Task 2 then runs its normal generated/literary
and regression checkpoint without changing production SPL, TOML, or generated
artifacts unless the green characterization exposes an actual divergence.

This amendment changes only the Task-2 execution shape. It does not relax
strict parity, grant an Auto-links-style normalization exception, or authorize
any later Slice-3 fixture.
