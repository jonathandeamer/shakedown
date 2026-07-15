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

## Amendment A4 (2026-07-15): Quote-code normalization is an Act-IV, stack-carried decision

Task 6's former Act-II quote-code handoff is not legal in the current IR
shape. A scene may name only its anchor and one companion. The attempted
handoff needs Hecate for the staged glyph, Lady Macbeth for mixed-stream
output, and Horatio for quote mode; assigning all three is rejected by
`scripts.splc.validate.participants`. Do not relax that two-participant
invariant or add a third character.

Normalize later instead. Act II preserves the quote payload: after `>` it
consumes at most one optional Markdown marker space (or one tab), then keeps
every remaining source space in the ordinary paragraph payload. The same
one-space rule applies at a quoted continuation line. Thus a code candidate
reaches Act IV as a `PARA` leaf whose text begins with exactly four spaces; it
is deliberately not an Act-II `CODE_BLOCK` token. The ordinary `Example:` and
`Or:` leaves remain `PARA` leaves. This is a narrow correction to existing
quote-prefix routes, not support for nested quotes, lists, tab expansion, or
general code-block parsing.

At an existing blockquote frame, Act IV probes the first four glyphs of a
`PARA` leaf before emitting its paragraph open. It uses only Prospero and
Puck: Prospero pops and restores the quote frame, then holds a bounded probe
count above that frame while Puck supplies the glyphs. Four ASCII spaces
followed by a non-terminator select the existing code-leaf emitter, discard
those four spaces, and preserve every remaining glyph including the terminal
code newline. On EOF, a non-space, or fewer than four spaces, reverse-push
every probed glyph onto Puck and resume the normal paragraph path in source
order. The probe marker is popped before output-frame handling; the existing
code-leaf return route then records `QUOTE_USED`. No token code, Act-II state
register, table ownership change, or new parser is authorized.

This replaces the former Task-6 stream contract with `BLOCKQUOTE_OPEN`, then
`PARA("Example:")`, `PARA("    sub status {\\n    print \"working\";\\n}\\n")`,
`PARA("Or:")`, `PARA("    sub status {\\n    return \"working\";\\n}\\n")`,
then `BLOCKQUOTE_CLOSE`. The Act-IV byte contract is unchanged. Task 6 must
replace its obsolete Act-II `CODE_BLOCK` expectation, add one-to-three-space
and EOF replay contracts, retain the standalone `CODE_BLOCK` regression, and
run its existing exact generated/literary, strict-oracle, spike, and final
verification gates.

## Amendment A5 (2026-07-15): Preserve quote source indent; deindent code per line in Act IV

Amendment A4's phrase “whose text begins with exactly four spaces” describes
the candidate's first physical line only. The quote-prefix rule remains
literal: remove `>` and at most one immediately following marker space or
tab, then preserve every remaining source glyph. Consequently the fixture's
two Act-II `PARA` payloads are exactly
`    sub status {\\n        print "working";\\n    }\\n` and
`    sub status {\\n        return "working";\\n    }\\n` (`4/8/4` leading
spaces). The earlier illustrative `4/4/0` stream text is superseded because
it conflated Act II's raw carrier with Act IV's code payload.

Once the existing Act-IV quote-frame probe accepts an initial four ASCII
spaces followed by a non-terminator, Act IV removes exactly four ASCII spaces
at the start of every physical line of that one qualifying `PARA` before the
existing code emitter receives it. Thus the emitter receives `sub status
{\\n    print "working";\\n}\\n` (and its `return` analogue): the outer
indent is removed from each line, inner indentation is retained, and the
terminal newline is retained. Probe failures, including four spaces at EOF,
must still reverse-replay byte-for-byte into the normal quoted paragraph
route.

This clarification does not broaden scope. It remains a bounded adapter for
a qualifying paragraph at `QUOTE_EMPTY`/`QUOTE_USED`, using only Prospero,
Puck, and the already reserved `SCRIBE_QUOTE_CODE*` surfaces; no new token,
participant, tab expansion, nested blockquote, or general code-block grammar
is authorized. The Task-6 contracts must assert raw `4/8/4` Act-II stream
payloads separately from normalized `0/4/0` Act-IV output payloads.

## Amendment A6 (2026-07-15): Detab-normalized quote prefixes and oracle-exact quote-code indentation

Amendment A5's source-level tab wording and its `0/4/0` emitted-payload
example are both superseded. Act I's established Markdown-order detab pass
runs before Act II. Act II therefore cannot observe a tab in a quote prefix:
the source probe `>\t    code line\n` reaches it as `>       code line\n`.
`PASS_QUOTE_PREFIX` and `PASS_QUOTE_CONTINUE_PREFIX` must consume at most one
**ASCII space** from that normalized carrier, then copy all remaining glyphs
unchanged. The corresponding fast-stream contract is six leading spaces, not
four. A source `>     code line\n` still produces four leading payload spaces,
and ordinary quoted text remains unchanged. This is faithful to the Act-I
detab invariant; it does not authorize a second detab pass, a tab register, or
an Act-II tab-sensitive branch.

The local `Markdown.pl` v1.0.1 oracle is authoritative for the fixture. Its
`Blockquotes with code blocks` HTML has `0/2/0` leading spaces in each code
leaf (`sub status {`, two spaces before `print`/`return`, and `}`). The
accepted adapter must therefore transform each fixture `4/8/4` Act-II carrier
to the oracle-exact `0/2/0` code payload: remove four ASCII spaces from the
first and closing physical lines and six from the middle physical line. The
adapter remains bounded to the two known three-line code leaves inside a
top-level `QUOTE_EMPTY` or `QUOTE_USED` frame. It must reject/replay any other
line shape, including a trailing newline in the Act-II leaf: the real Act-II
stream carries no terminal newline, while Act IV supplies the single terminal
code newline required by the existing code emitter.

Task-6 tests must use source-level tab probes through Act I and assert the
six-space normalized payload. Their synthetic Act-IV fixture stream must match
the actual carrier without a final newline and assert the exact
oracle-derived `0/2/0` HTML. Retain the standalone `CODE_BLOCK` regression,
the one-to-three-space/four-space-EOF replay contracts, and every existing
generated-fragment, SPL parse, splc validation, literary, strict-parity,
spike, and final-suite gate. No token, scene surface, participant, general
code-block grammar, nested-blockquote behavior, or tab expansion is
authorized.
