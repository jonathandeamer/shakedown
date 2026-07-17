# Slice 4 High-Risk Fixtures — Design

**Date:** 2026-07-17
**Status:** accepted for roadmap row 7 planning
**Authority:** architecture §7.7, §7.8a, §8.1–§8.3; Spike A and Spike B accepted designs.

## Amendment A1 — installed-oracle authority for nested blockquotes (2026-07-17)

The executable used by the repository's strict-parity harness is
`~/markdown/Markdown.pl`, whose version header is currently `1.0.2b8`.
For Slice 4's deterministic strict-parity gates, that executable is the
authority.  A fixture file remains the normalized-mdtest regression corpus;
it is not a competing raw-byte authority when it disagrees with this
executable.  Auto links remains the sole entity-normalized exception.

This resolves the documented one-flag `_DoBlockQuotes` drift: the installed
oracle uses `$bq =~ s/^/  /g;`, without `/m`.  Task 3 must therefore emit its
exact layout: the outer body's first line and the nested opening begin with
two spaces, while the nested paragraph and its close are not additionally
indented.  It must not emit the Markdown 1.0.1 / checked-fixture four-space
inner layout.  The required balanced `BLOCKQUOTE_CLOSE` stream and the
Spike-B list grammar are unchanged.

`tests/test_mdtest.py` keeps its established normalized fixture comparison;
Task 3's focused exact-output contract and the strict parity harness are the
indentation-sensitive acceptance gates.  This is a Slice-4 planning decision,
not authorization to change checked-in fixtures, to invoke Markdown.pl at
runtime, or to weaken strict parity.

## Amendment A2 — activate the allocated header leaf for the full-list gate (2026-07-17)

The `Ordered and unordered lists` input starts with `## Unordered`,
`## Ordered`, and `## Nested`; the strict oracle emits three `<h2>` leaves.
The release binary instead emits `<p>## Unordered</p>` at byte 1.  `HEADER =
2` is already allocated and has an existing `LEAF_BLOCK` role, but it has no
`ARITY` row, Act II does not emit it, and Act IV does not render it.  The
previous list-only Task-4-Step-2 authority therefore cannot satisfy its own
complete-fixture strict-parity gate.

This amendment authorizes the smallest semantic header path needed by that
fixture, as a prerequisite within Task 4 Step 2—not a new plan or a separate
fixture feature.  It activates the existing `HEADER` leaf with one fixed
integer payload (`level`, 1 through 6) followed by a `TEXT_END`-terminated
glyph run.  Its numeric code stays `2`, its role stays `LEAF_BLOCK`, and no
participant or container grammar changes.  `src_ir/tokens.py` and
`docs/spl/token-codes.md` gain the matching `HEADER: TokenArity(1, True)` row;
decoder and structural-validator tests move from their current “not yet
shipped” assertions to positive header coverage.  Act III may only traverse
the new declared arity; it must not rewrite its level or glyphs.

Act II recognizes only top-level ATX headers in the bounded Markdown.pl shape:
one to six leading `#` glyphs, required following space or tab, and non-empty
text through line end; a closing `#` run preceded by whitespace is stripped.
Malformed, indented, or unterminated candidates replay byte-for-byte to the
existing paragraph route.  Setext headers, headers inside containers, and any
broader block-pass generalization are out of scope.  Act IV validates levels
1–6, emits `<h{level}>`, span-processed text, and `</h{level}>` with the
normal block separator, then returns to its existing frame path.

The explicit authority replaces Task 4 Step 2's former blanket
arity-unchanged rule only for this existing allocated leaf.  It does not
authorize a new token, renumbering, structural-role change, arbitrary header
syntax, or fixture-specific output path.  The `LIST_OPEN(kind)`,
`LIST_ITEM(looseness)`, `ITEM_CLOSE`, and `LIST_CLOSE` grammar remains frozen;
all Spike-A/B stream expectations remain immutable.  Any need beyond this
bounded header leaf remains `BLOCK[plan]`.

## Decision

Slice 4 extends the existing four-act IR parser and its explicit token grammar;
it does not add a parser, an oracle fallback, a token code, or an on-stage
participant.  Act II remains the owner of block recognition and balanced
container-token production, Act III copies structural and `RAW_HTML_HASH`
leaves unchanged, and Act IV renders containers from Prospero's existing frame
stack.

The work is sequenced by interaction risk:

1. Advanced HTML widens the existing left-margin raw-HTML recognizer from its
   simple `div` shape to the fixture's attributed and nested `div` blocks.  A
   `RAW_HTML_HASH` leaf contains the original block bytes, excluding only the
   block-delimiting blank boundary; Act IV emits it without paragraph wrapping.
2. Nested blockquotes make Act II emit one balanced `BLOCKQUOTE_OPEN` /
   `BLOCKQUOTE_CLOSE` pair per marker depth.  Blank quoted lines remain within
   their current depth and an outdented line closes exactly the required quote
   frames.  Act IV reproduces the installed-oracle layout fixed by Amendment
   A1 while preserving one frame per token nesting.
3. Full lists lift the Spike-A narrowings: multi-digit ordered markers,
   top-level indentation up to three spaces, tab/space marker separation,
   arbitrary fixture-required nesting, loose multi-paragraph items, and the
   documented Markdown-1.0.1 oddity at the fixture tail.  The existing
   `LIST_OPEN`, `LIST_ITEM`, `ITEM_CLOSE`, and `LIST_CLOSE` grammar remains
   the sole cross-act representation.

## Invariants and stopping conditions

- The three named fixtures must be strict byte-identical to a fresh local
  `Markdown.pl` run.  Unlike Auto links, none has a normalization exception.
- Existing fixture expected files stay unchanged; `tests/test_mdtest.py`
  enablement occurs only after a fixture's focused strict-parity proof.
- The six list and four nested-block spike fixtures remain oracle-byte-exact;
  their reviewed stream grammar is a regression boundary, not an optional
  example.
- Raw HTML handling remains Markdown.pl v1.0.1's fixed block-tag/boundary
  surface, not a general HTML parser.  The Slice-4 fixture requires `div`
  only; a need for a new tag family is a `BLOCK[plan]` unless an oracle probe
  proves that it is needed by the fixture.
- A need for a new token, third participant, a changed structural grammar,
  unreserved prose, or a non-reproducible binary/IR divergence is a
  `BLOCK[plan]`.  A full-list fixture stream that cannot be rendered by the
  Spike-B grammar is an architecture §8.2 halt, not a local workaround.

## Interfaces

| Boundary | Contract |
|---|---|
| Act II → III | `PARA`, activated `HEADER(level, text)`, `HR`, `LIST_OPEN`, `LIST_ITEM`, `ITEM_CLOSE`, `LIST_CLOSE`, `BLOCKQUOTE_OPEN`, `BLOCKQUOTE_CLOSE`, `CODE_BLOCK`, and `RAW_HTML_HASH` cross the boundary. Amendment A2 adds only the pre-allocated `HEADER` arity row; every other token arity remains unchanged. |
| Act III → IV | Structural codes and `RAW_HTML_HASH` payload bytes pass through unchanged; span processing is restricted to text-bearing Markdown leaves. |
| Act IV | Prospero's frame stack is balanced for every container token; nested quote output follows Amendment A1's installed-oracle indentation layout, and list item ownership remains explicit through `ITEM_CLOSE`. |
| Tests | Fast IR tests expose streams and HTML; mdtest runs fast IR and release `./shakedown`; `scripts/strict_parity_harness.py` is the implementation parity authority. |

## Fixture-derived acceptance inventory

| Fixture | Required cases |
|---|---|
| Inline HTML (Advanced) | one-line `div`; three-level nested `div`; `style=\">\"`; indented attributed inner `div`; blank-boundary preservation; final attributed nested pair. |
| Nested blockquotes | outer paragraph, quoted blank lines, a second-depth quote, return to outer depth, matched closures, and Amendment A1's installed-oracle indentation layout. |
| Ordered and unordered lists | `*`/`+`/`-`; ordered tab and space separators; loose/tight distinction; multiple paragraphs; three-level nesting; ordered-to-unordered nesting; loose nested list; and the fixture's final Markdown-1.0.1 oddity. |

## Literary reservation

The implementation must reuse existing `PASS_LISTS_*`, `PASS_QUOTE_*`,
`SCRIBE_LIST_*`, and `SCRIBE_BLOCKQUOTE_*` surfaces wherever their current
meaning remains exact.  The following is the complete new controlled pool.
Its working count is derived from the scene ledger below: Act II has 22
working scenes and 5 spares; Act IV has 16 working scenes and 4 spares.  This
meets the required at-least-20%-and-four spare rule.  Add these entries to
`src/literary.toml` in the same checkpoint that first introduces the label.

| Act | Family | Working labels | Spare labels |
|---|---|---|---|
| II | HTML 6; quote 6; list 10 | `PASS_HTML_BLOCK_OPEN`, `PASS_HTML_BLOCK_NAME`, `PASS_HTML_BLOCK_ATTR`, `PASS_HTML_BLOCK_DEPTH_OPEN`, `PASS_HTML_BLOCK_DEPTH_CLOSE`, `PASS_HTML_BLOCK_FINISH`; `PASS_QUOTE_NEST_OPEN`, `PASS_QUOTE_NEST_CLOSE`, `PASS_QUOTE_NEST_DEPTH`, `PASS_QUOTE_NEST_BLANK`, `PASS_QUOTE_NEST_REPLAY`, `PASS_QUOTE_NEST_FINISH`; `PASS_LISTS_INDENT_ONE`, `PASS_LISTS_INDENT_TWO`, `PASS_LISTS_INDENT_THREE`, `PASS_LISTS_MARKER_DIGIT`, `PASS_LISTS_MARKER_DOT`, `PASS_LISTS_CONTINUE`, `PASS_LISTS_NEST_OPEN`, `PASS_LISTS_NEST_CLOSE`, `PASS_LISTS_LOOSE`, `PASS_LISTS_FULL_FINISH` | `PASS_HTML_BLOCK_GUARD`, `PASS_QUOTE_NEST_GUARD`, `PASS_LISTS_INDENT_GUARD`, `PASS_LISTS_NEST_GUARD`, `PASS_LISTS_FULL_GUARD` |
| IV | HTML 3; quote 5; list 8 | `SCRIBE_RAW_HTML_ADVANCED`, `SCRIBE_RAW_HTML_ADVANCED_SEP`, `SCRIBE_RAW_HTML_ADVANCED_CLOSE`; `SCRIBE_QUOTE_NEST_OPEN`, `SCRIBE_QUOTE_NEST_CLOSE`, `SCRIBE_QUOTE_NEST_INDENT`, `SCRIBE_QUOTE_NEST_RETURN`, `SCRIBE_QUOTE_NEST_FINISH`; `SCRIBE_LIST_DEPTH_OPEN`, `SCRIBE_LIST_DEPTH_CLOSE`, `SCRIBE_LIST_LOOSE_BEGIN`, `SCRIBE_LIST_LOOSE_CLOSE`, `SCRIBE_LIST_NEST_RETURN`, `SCRIBE_LIST_ITEM_PARAGRAPH`, `SCRIBE_LIST_ITEM_CLOSE_FINAL`, `SCRIBE_LIST_FULL_FINISH` | `SCRIBE_RAW_HTML_ADVANCED_GUARD`, `SCRIBE_QUOTE_NEST_GUARD`, `SCRIBE_LIST_DEPTH_GUARD`, `SCRIBE_LIST_FULL_GUARD` |

```toml
[scenes.PASS_HTML_BLOCK_OPEN]
title = "Lady Macbeth opens the court's unbroken wall."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_NAME]
title = "Macbeth names the wall's guarded stone."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_ATTR]
title = "Lady Macbeth keeps the wall's private sign."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_DEPTH_OPEN]
title = "Macbeth enters the wall's inward chamber."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_DEPTH_CLOSE]
title = "The inward chamber yields its settled wall."
pattern = "bare_statement"
[scenes.PASS_HTML_BLOCK_FINISH]
title = "Lady Macbeth releases the courtly wall."
pattern = "scene_of_character"
[scenes.PASS_HTML_BLOCK_GUARD]
title = "The courtly wall keeps one sure threshold."
pattern = "bare_statement"

[scenes.PASS_QUOTE_NEST_OPEN]
title = "Lady Macbeth opens the echo within the echo."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_CLOSE]
title = "Macbeth closes the echo's inner chamber."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_DEPTH]
title = "Lady Macbeth counts the echo's shadowed rooms."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_BLANK]
title = "The echo keeps its measured silent room."
pattern = "bare_statement"
[scenes.PASS_QUOTE_NEST_REPLAY]
title = "Macbeth restores the echo's outer word."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_FINISH]
title = "Lady Macbeth frees the finished echo."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_NEST_GUARD]
title = "The echo keeps one guarded return."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_ONE]
title = "Macbeth marks the first low marching step."
pattern = "scene_of_character"
[scenes.PASS_LISTS_INDENT_TWO]
title = "Lady Macbeth measures the second marching step."
pattern = "scene_of_character"
[scenes.PASS_LISTS_INDENT_THREE]
title = "Macbeth keeps the third marching step."
pattern = "scene_of_character"
[scenes.PASS_LISTS_MARKER_DIGIT]
title = "Lady Macbeth gathers the numbered standard."
pattern = "scene_of_character"
[scenes.PASS_LISTS_MARKER_DOT]
title = "Macbeth seals the numbered standard's point."
pattern = "scene_of_character"
[scenes.PASS_LISTS_CONTINUE]
title = "Lady Macbeth bears the marching line onward."
pattern = "scene_of_character"
[scenes.PASS_LISTS_NEST_OPEN]
title = "Macbeth opens the army's inner rank."
pattern = "scene_of_character"
[scenes.PASS_LISTS_NEST_CLOSE]
title = "Lady Macbeth recalls the army's outer rank."
pattern = "scene_of_character"
[scenes.PASS_LISTS_LOOSE]
title = "Macbeth grants the rank its breathing field."
pattern = "scene_of_character"
[scenes.PASS_LISTS_FULL_FINISH]
title = "Lady Macbeth dismisses the ordered host."
pattern = "scene_of_character"
[scenes.PASS_LISTS_INDENT_GUARD]
title = "The marching step keeps one certain measure."
pattern = "bare_statement"
[scenes.PASS_LISTS_NEST_GUARD]
title = "The inner rank keeps its faithful border."
pattern = "bare_statement"
[scenes.PASS_LISTS_FULL_GUARD]
title = "The ordered host keeps one final watch."
pattern = "bare_statement"

[scenes.SCRIBE_RAW_HTML_ADVANCED]
title = "Prospero inscribes the court's whole wall."
pattern = "scene_of_character"
[scenes.SCRIBE_RAW_HTML_ADVANCED_SEP]
title = "The courtly wall receives its clear interval."
pattern = "bare_statement"
[scenes.SCRIBE_RAW_HTML_ADVANCED_CLOSE]
title = "Prospero seals the courtly wall in light."
pattern = "scene_of_character"
[scenes.SCRIBE_RAW_HTML_ADVANCED_GUARD]
title = "The courtly wall keeps its radiant edge."
pattern = "bare_statement"

[scenes.SCRIBE_QUOTE_NEST_OPEN]
title = "Prospero opens the echo's inward hall."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_CLOSE]
title = "Prospero closes the echo's inward hall."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_INDENT]
title = "Puck lays two pale steps beneath the echo."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_RETURN]
title = "Puck returns the echo to its outer shore."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_FINISH]
title = "Prospero releases the layered echo."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_NEST_GUARD]
title = "The layered echo keeps one noble measure."
pattern = "bare_statement"

[scenes.SCRIBE_LIST_DEPTH_OPEN]
title = "Prospero opens the host's inward order."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_DEPTH_CLOSE]
title = "Prospero closes the host's inward order."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_LOOSE_BEGIN]
title = "Puck grants the host a spacious interval."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_LOOSE_CLOSE]
title = "The spacious host gathers its settled line."
pattern = "bare_statement"
[scenes.SCRIBE_LIST_NEST_RETURN]
title = "Puck restores the host's outer file."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_ITEM_PARAGRAPH]
title = "Prospero inscribes the host's inner speech."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_ITEM_CLOSE_FINAL]
title = "Prospero seals the host's last brave file."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_FULL_FINISH]
title = "Puck releases the ordered host to dawn."
pattern = "scene_of_character"
[scenes.SCRIBE_LIST_DEPTH_GUARD]
title = "The inward host keeps one radiant border."
pattern = "bare_statement"
[scenes.SCRIBE_LIST_FULL_GUARD]
title = "The ordered host keeps one noble watch."
pattern = "bare_statement"
```

### Amendment A2 header reservation

The header prerequisite has seven working Act-II scenes and four working
Act-IV scenes.  Each touched act has four pre-approved spares, satisfying the
at-least-20%-and-four-spare rule.  These are controlled scene titles; the
existing Critical `HEADER = 2`, level values, and `TEXT_END` surfaces need no
new prose.

| Act | Working-label ledger | Spares |
|---|---|---|
| II | `PASS_HEADER_START` (candidate entry); `PASS_HEADER_MARK` (count one through six hashes); `PASS_HEADER_SEPARATOR` (require space/tab); `PASS_HEADER_TEXT` (stage text); `PASS_HEADER_CLOSER` (strip legal closer); `PASS_HEADER_EMIT` (emit code, level, text); `PASS_HEADER_REPLAY` (restore rejected candidate) | `PASS_HEADER_GUARD`, `PASS_HEADER_DEPTH_GUARD`, `PASS_HEADER_TEXT_GUARD`, `PASS_HEADER_REPLAY_GUARD` |
| IV | `SCRIBE_HEADER_OPEN` (validate and emit opening tag); `SCRIBE_HEADER_TEXT` (emit span-processed text); `SCRIBE_HEADER_CLOSE` (emit matching close); `SCRIBE_HEADER_RETURN` (restore block dispatch) | `SCRIBE_HEADER_GUARD`, `SCRIBE_HEADER_LEVEL_GUARD`, `SCRIBE_HEADER_TEXT_GUARD`, `SCRIBE_HEADER_RETURN_GUARD` |

```toml
[scenes.PASS_HEADER_START]
title = "Lady Macbeth marks the page's raised standard."
pattern = "scene_of_character"
[scenes.PASS_HEADER_MARK]
title = "Macbeth counts the standard's dark strokes."
pattern = "scene_of_character"
[scenes.PASS_HEADER_SEPARATOR]
title = "Lady Macbeth keeps the standard's measured space."
pattern = "scene_of_character"
[scenes.PASS_HEADER_TEXT]
title = "Macbeth bears the standard's spoken burden."
pattern = "scene_of_character"
[scenes.PASS_HEADER_CLOSER]
title = "Lady Macbeth trims the standard's closing edge."
pattern = "scene_of_character"
[scenes.PASS_HEADER_EMIT]
title = "Macbeth sends the raised standard onward."
pattern = "scene_of_character"
[scenes.PASS_HEADER_REPLAY]
title = "Lady Macbeth restores the fallen standard."
pattern = "scene_of_character"
[scenes.PASS_HEADER_GUARD]
title = "The raised standard keeps one sure watch."
pattern = "bare_statement"
[scenes.PASS_HEADER_DEPTH_GUARD]
title = "The standard keeps its counted height."
pattern = "bare_statement"
[scenes.PASS_HEADER_TEXT_GUARD]
title = "The standard keeps its faithful word."
pattern = "bare_statement"
[scenes.PASS_HEADER_REPLAY_GUARD]
title = "The fallen standard keeps its former place."
pattern = "bare_statement"

[scenes.SCRIBE_HEADER_OPEN]
title = "Prospero opens the standard's radiant face."
pattern = "scene_of_character"
[scenes.SCRIBE_HEADER_TEXT]
title = "Puck bears the standard's bright word."
pattern = "scene_of_character"
[scenes.SCRIBE_HEADER_CLOSE]
title = "Prospero seals the standard's radiant face."
pattern = "scene_of_character"
[scenes.SCRIBE_HEADER_RETURN]
title = "Puck returns the standard to the page."
pattern = "scene_of_character"
[scenes.SCRIBE_HEADER_GUARD]
title = "The radiant standard keeps one noble edge."
pattern = "bare_statement"
[scenes.SCRIBE_HEADER_LEVEL_GUARD]
title = "The radiant standard keeps its counted height."
pattern = "bare_statement"
[scenes.SCRIBE_HEADER_TEXT_GUARD]
title = "The radiant standard keeps its faithful word."
pattern = "bare_statement"
[scenes.SCRIBE_HEADER_RETURN_GUARD]
title = "The radiant standard keeps its homeward course."
pattern = "bare_statement"
```

## Verification

Each fixture follows architecture §8.1's four gates: focused mdtest pass,
fresh-oracle strict parity, all already-enabled fixtures plus both spike suites,
and proof that the release SPL—not Markdown.pl—performed the transform.  Every
SPL/TOML checkpoint also runs:

```bash
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

The completion checkpoint runs `uv run pytest -q`, `uv run ruff check .`,
`uv run ruff format --check .`, `uv run pyright`, a 23-case differential smoke
report, and the performance measurement procedure in `docs/performance/budget.md`.
