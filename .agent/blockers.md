# MCO Agent Blockers Log

Resolved 2026-07-15 by Slice-3 plan/design Amendment A6: Act I detabs quote
prefixes before Act II, so Task 6 now tests the normalized one-ASCII-space
route; the local Markdown.pl oracle requires the fixture's Act-IV code output
to use `0/2/0` indentation from the raw `4/8/4` carrier.
Resolved 2026-07-17 by Slice-3 plan/design Amendment A7: Task 6 now owns a
four-scene, quote-only prefix bridge plus three reserved spares; it preserves
the raw `4/8/4` carrier, leaves protected Spike-B routes untouched, and adds
focused nested-block composition evidence before the final gate.
Resolved 2026-07-17 by the Slice-3 closeout fix: the quote/list bridge now
preserves Spike-B nested-block behavior, Act II lowering validates again, and
the regenerated release path plus shipped-fixture gate are green.

Resolved 2026-07-17 by Slice-4 design Amendment A1 and Task 3 clarification:
the installed Markdown.pl 1.0.2b8 executable is the strict-byte authority;
Task 3 retains its balanced quote stream but emits the oracle's layout, not
the checked fixture's Markdown-1.0.1 four-space inner indentation.  The
focused literal-output contract and strict-parity harness now make that
choice executable while mdtest retains its existing normalized regression
comparison.

Resolved 2026-07-17 by Slice-4 design Amendment A2 and the matching Task-4-Step-2
amendment: the already allocated `HEADER = 2` is now explicitly authorized as
the bounded `HEADER(level, text)` leaf needed by the full-list fixture.  The
amendment reserves its Act-II/IV controlled surfaces and spares, requires
matching arity/decoder/validator coverage, retains every list token number and
structural role, and keeps any broader header surface as `BLOCK[plan]`.

Historical planning blocker (resolved): Slice-4 Task 3 Step 2
(`docs/superpowers/plans/2026-07-17-slice-4-high-risk-fixtures.md`)
  cannot be executed as written: the accepted design carries two mutually
  exclusive acceptance criteria for `Nested blockquotes`, because the local
  oracle is **not** the version the project targets. Only a planning amendment
  can choose the authority. No production code was changed.

  **Verified evidence (2026-07-17):**
  - `~/markdown/Markdown.pl` declares `$VERSION = '1.0.2b8'` (line 18), but
    `CLAUDE.md:7` and `docs/markdown/target.md:3,8` state the port targets
    v1.0.1 — and `target.md:8` claims that version is "confirmed by the version
    header in that file", which the header today falsifies.
  - Root cause is one flag. Local `_DoBlockQuotes` (line 1149) applies
    `$bq =~ s/^/  /g;` without `/m`, so `^` matches only at string start and
    exactly one line is indented. Markdown 1.0.1 used `s/^/  /mg`, indenting
    every line, which is what produces two-space-per-depth nesting.
  - Patching only that flag on a copy makes the oracle reproduce
    `Nested blockquotes.xhtml` **byte-for-byte** (`diff` exit 0). This
    single-flag change fully explains the divergence.
  - Blast radius across all 23 fixtures — the two oracle versions disagree on
    exactly three: `Nested blockquotes`, `Blockquotes with code blocks`
    (already shipped, roadmap row 6), and `Tidyness` (already shipped, row 5).

  **The contradiction.** Step 2 orders Act IV to emit "the fixture's exact
  two-space-per-depth layout" (design acceptance inventory likewise requires
  "four-space inner HTML indentation"), yet the same step gates on
  `strict_parity_harness.py 'Nested blockquotes'` reporting `1/1
  byte-identical`. That harness compares `./shakedown` against a live run of
  the **1.0.2b8** oracle, which emits the *unindented* nested layout. Building
  the ordered layout guarantees the ordered gate fails; passing the gate
  requires disobeying the layout instruction. The design's claim that these
  fixtures are "strict byte-identical to a fresh local Markdown.pl run" with no
  normalization exception is false for this fixture as specified.

  **Why the suite never caught this.** `tests/test_mdtest.py::_normalize`
  applies `line.strip()` to every line, so mdtest is entirely
  indentation-insensitive; `normalize(oracle) == normalize(fixture)` is True for
  both `Nested blockquotes` and `Blockquotes with code blocks`. mdtest therefore
  passes under *either* layout and cannot arbitrate. Strict parity is the only
  gate that sees indentation, which is how `Blockquotes with code blocks`
  shipped green while its committed `.xhtml` disagrees with the local oracle.

  **Resolution options for the planner (pick one; each changes what Act IV
  emits, so implementation cannot proceed by guess):**
  1. *Oracle is authority.* Keep the 1.0.2b8 oracle, drop the
     two-space-per-depth instruction, and have Act IV reproduce the local
     unindented nested layout. Cheapest: current Act IV already matches the
     oracle except for the missing inner `</blockquote>`, so Task 3 reduces to
     the Act-II balanced-close work. Requires correcting the v1.0.1 claims in
     `CLAUDE.md`/`target.md` and accepting that fixture `.xhtml` bytes are not
     the target for these three fixtures.
  2. *Fixtures/v1.0.1 are authority.* Repoint the oracle at a true v1.0.1
     `Markdown.pl` (the fixtures' provenance). Then oracle == fixture for all
     three, the ordered layout is correct, and strict parity is meaningful
     again — but `Tidyness` and `Blockquotes with code blocks` must be
     re-proved against the new oracle, and their shipped status re-verified.

  Both options need a decision on whether `_normalize`'s per-line `strip()`
  should keep hiding indentation from mdtest; while it does, no fixture gate
  actually verifies blockquote layout. Note the Act-II half (emit a balanced
  `BLOCKQUOTE_CLOSE` on outdent) is required identically under both options and
  is the substance of the step; only the Act-IV layout is contested.
