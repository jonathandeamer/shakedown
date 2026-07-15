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

## Amendment A2 (2026-07-15): Strong/em requires a bounded Act-II HR-replay prerequisite

Task 4's mixed strong/em fixture establishes that the present Act-II
horizontal-rule fallback leaks Macbeth's temporary repeated-marker count into
the next block classification. `***text` and `___text` correctly fail the HR
recognizer and replay as paragraph glyphs, but the failed scan leaves Macbeth
positive. At the following ordinary line, `PASS_LISTS_GATE_ORDERED` mistakes
that stale value for an open-list depth; a later blank line then enters
`PASS_CONTAINERS_OPEN` without an `ITEM_START` floor and underflows Lady
Macbeth. This occurs before Act III, so an Act-III-only resume requeue change
cannot satisfy the Task-4 gate.

Task 4 therefore owns one narrowly bounded predecessor repair in
`src_ir/act2.py`, before its Act-III delimiter change: on the failed-HR replay
path, restore Macbeth to the zero/no-open-list state before raw glyph copying
resumes. Retain `PASS_HR_SPACE`'s existing single-marker (`*` or `-`) plus
space/tab handoff to `PASS_HR_FALLBACK_LIST_HANDOFF`; do not route a failed
no-space marker run to that handoff. This preserves the shipped rejected-HR
list regression while ensuring `***text`, `___text`, and ordinary text after
either run are raw paragraph input, not list-item input.

No token, table ownership, new scene, or literary surface is authorized by
this prerequisite: it edits only branches/assignments in existing Act-II
scenes and uses their already-reserved TOML labels. The implementation must
first add focused fast-Act-II stream/state contracts that prove (1) a failed
`***` and `___` run leaves no open list frame or positive list-depth state,
(2) the following plain paragraph remains a `PARA`, and (3) `* item` and
`- item` still enter the existing list handoff. It then runs the existing
strong/em Act-III contracts and fresh-oracle strict fixture proof. This is a
prerequisite within Task 4, not Slice-4 expansion or a second parser.

## Amendment A3 (2026-07-15): Integrated Task-5 Step-1 branch reconciliation

The branch
`implement-1fc3c17d5ed7433dbbae26ed447a8bb0-codex-implement` is not pending
work: its head `e60e0fe7676f7e5e1e1f89e36c9a84c953f96dfd` is exactly `main`
and `origin/main`. Its sole commit marks Task 5 Step 1's already-landed red
HTML contracts complete. The branch ledger records `integrated` with this
head; `git merge-base --is-ancestor <branch> main` succeeds, and both the
reachable-commit log and three-dot diff are empty.

This reconciliation changes no Slice-3 behavior, implementation authority,
literary reservation, or evidence requirement. Task 5 remains at its first
unchecked step, bounded matching. The existing literary protocol and the
exact generated-fragment, parse-smoke, splc-validation, TOML-schema, and
literary-compliance commands in the plan remain binding before an SPL-facing
checkpoint.
