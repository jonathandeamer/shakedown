# Slice 5 Documentation Aggregates — Design

**Date:** 2026-07-18  
**Status:** accepted for roadmap row 8 planning  
**Authority:** architecture §7.8, §7.8a, §8.1–§8.3; `docs/performance/budget.md`; the four-act IR contract.

## Decision

Slice 5 is the release-integration slice.  It enables the four already
strict-parity-capable skipped fixtures (`Auto links`, `Backslash escapes`, and
`Code Spans` immediately; `Tidyness` only after its real nested-list crash is
repaired), then makes `Markdown Documentation - Basics` and `Markdown
Documentation - Syntax` strict local-Markdown.pl byte gates.  No checked-in
fixture is changed and no normalizer is added for either aggregate.  `Auto
links` remains the sole mdtest entity-normalized comparison, while its strict
harness gate remains raw-byte comparison.

The 2026-07-18 baseline is binding evidence, not a proposed workaround:

| Case | Observed result | Required disposition |
|---|---|---|
| `Auto links`, `Backslash escapes`, `Code Spans` | each is raw byte-identical to the installed oracle | enable with focused IR/binary contracts; do not alter production behavior |
| `Tidyness` | Act II `PASS_LISTS_BLOCK_START` underflows Hecate | repair the existing quote/list handoff and prove the prior Spike A/B streams unchanged |
| Basics | 9,339 emitted bytes vs 9,384 oracle bytes | recover Setext, generic raw-HTML blocks, and ATX closing-hash handling through general pipeline paths |
| Syntax | release and probe exceed the 500,000-per-act limit; at 3,000,000, Acts I–IV take 542,872 / 508,228 / 615,608 / 546,921 interpreter steps and emit 31,357 bytes vs 31,785 oracle bytes | lift the release/aggregate-test safety limit to a measured finite ceiling, then repair the same general interaction paths and any separately evidenced remaining category |

## Bounded implementation shape

1. A shared `DOCUMENTATION_STEP_LIMIT = 1_000_000` is sufficient for every
measured Syntax act with headroom and remains a diagnostic guard, not an
unbounded retry.  The release runner, aggregate probe, and mdtest fast path
must use the same named limit where they execute documentation inputs.
2. Act II owns setext recognition and raw-block admission; Act III must retain
text and `RAW_HTML_HASH` opacity; Act IV already owns rendering.  Repairs must
extend the token stream rather than inject HTML output or branch on fixture
names.
3. Existing `HEADER`, `RAW_HTML_HASH`, list, quote, reference, and span token
roles are frozen.  No token number, new token, parser bypass, wrapper-side
Markdown transformation, or Markdown.pl runtime invocation is authorized.
4. Each new mismatch category is first captured by a minimal fixture extracted
from the aggregate and a fast-IR/release/strict-oracle assertion.  A category
that needs a new structural token, a new Act III/IV rendering role, or more
than the reserved Act-II scene pool below is a `- BLOCK[plan]:` and requires a
design amendment before implementation continues.

## Literary reservation

Only Act II may need new controlled scenes. The derived Setext scanner needs
nine labels (candidate, underline classification, equals emit, dash emit,
failed-underline requeue, Lady-Macbeth-to-Hecate finalization,
Hecate-to-Puck replay, Puck-to-Horatio bridge, and Lady-Macbeth close);
existing raw-HTML/header scenes are amended in place. The four-title spare
minimum remains greater than 20% of nine. Add a working entry only with the
identically named IR scene; do not draw a spare without a plan amendment.

```toml
# Slice 5 Act-II working pool (9)
[scenes.PASS_SETEXT_CANDIDATE]
title = "Lady Macbeth keeps the unmarked line before its warrant."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_UNDERLINE]
title = "Lady Macbeth weighs the underlining rank."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_EQUALS]
title = "Lady Macbeth crowns the gathered line."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_DASH]
title = "Lady Macbeth lowers the gathered line one rank."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_REQUEUE]
title = "Horatio restores the unproved underline to its source."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_FINALIZE]
title = "Lady Macbeth seals the gathered line for its return."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_REPLAY]
title = "Puck receives the sealed line in order."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_BRIDGE]
title = "Puck entrusts the gathered line to Horatio."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_CLOSE]
title = "Lady Macbeth seals the proven heading."
pattern = "scene_of_character"

# Slice 5 Act-II spare pool (4; unused unless an amendment assigns it)
[scenes.PASS_SETEXT_GUARD]
title = "The measured underline keeps one guarded proof."
pattern = "bare_statement"
[scenes.PASS_SETEXT_BOUNDARY_GUARD]
title = "The boundary keeps one guarded return."
pattern = "bare_statement"
[scenes.PASS_SETEXT_HTML_GUARD]
title = "The open mark keeps one guarded threshold."
pattern = "bare_statement"
[scenes.PASS_SETEXT_REPLAY_GUARD]
title = "The unproved line keeps one guarded passage."
pattern = "bare_statement"
```

## Verification and release decision

Every checkpoint runs generated-fragment, SPL parse, splc validation,
literary-schema/compliance, immutable token/spike, strict local-oracle, and
no-regression gates.  Completion requires `uv run pytest -q`, all 23 mdtest
parameters enabled, a strict harness `summary: 23/23 byte-identical`, and a
differential smoke report requiring both aggregates.  Measure `Basics` and
`Syntax` five times through `./shakedown`; Syntax is the headline release
number.  A single large-fixture result above 120 seconds or full contract
above 15 minutes triggers the architecture §8.2 performance halt.

## Amendment A1 (2026-07-18): Tidyness uses the installed deterministic oracle

The checked-in `Tidyness.xhtml` is a 133-byte legacy corpus artifact that
omits the blank line emitted by the installed local Markdown.pl for the same
input.  It is not authoritative for this deterministic fixture and must not
be changed as part of Slice 5.  The installed local Markdown.pl output is 136
bytes and is the authoritative expected output for every Tidyness parity
assertion.

The focused Tidyness contract must run the local oracle once, assert that the
unchanged checked-in fixture differs from those raw bytes, and then require
both fast-IR output encoded as bytes and release stdout to equal the raw
oracle bytes.  It must not use `_normalize_fixture_output` or compare either
implementation output to `Tidyness.xhtml`.

When Task 2 enables Tidyness in `tests/test_mdtest.py`, add a narrowly scoped
test-only expected-output helper: for `Tidyness` it runs the same local oracle
on the fixture input and returns the decoded raw output after a zero-return
assertion; every other fixture continues to read its checked-in expected file.
The common mdtest fast-IR and binary comparisons then consume that helper's
result.  This is test evidence only: production code never invokes Markdown.pl
and no mdtest normalizer is added.  `Auto links` remains the sole
entity-normalized comparator.  The exact focused and release evidence remains
`uv run pytest tests/test_act2_slice2.py tests/test_slice5_documentation_aggregates.py -k Tidyness -q`,
`uv run pytest tests/test_mdtest.py -k Tidyness -q`, and
`uv run python scripts/strict_parity_harness.py Tidyness`, all requiring
136/136 raw-byte equality where the output is compared to the oracle.

## Amendment A2 (2026-07-18): Setext carrier bridge and eight-label ledger

The original seven-label reservation omitted a legal two-participant path for
replaying the candidate when its next line is not a Setext underline. Act II
is anchored on Lady Macbeth, and `splc` permits exactly one other participant
per scene. A scene that directly reads Hecate's captured glyphs, stages Puck,
and writes Horatio would therefore be rejected before lowering. This
amendment reserves `PASS_SETEXT_BRIDGE` as the eighth working label; it does
not consume any of the four named spares.

The following state table is binding. A scene may touch only the pair shown;
the arrows are stack transfers, not value aliases. The candidate stack holds
the title bytes in capture order and, on a failed underline, every consumed
underline byte including its terminating newline. The three transfer legs
restore those bytes to Lady Macbeth in source order. Thus the failed route
replays the exact raw sequence, while the proved route omits the underline and
has already staged exactly one existing `HEADER(level)` record ahead of its
title bytes.

| Label | Stage pair / anchor | Stack action and exit |
|---|---|---|
| `PASS_SETEXT_CANDIDATE` | Lady Macbeth + Hecate / Lady Macbeth | Read one source glyph; capture title glyphs on Hecate. On the first newline, enter `PASS_SETEXT_UNDERLINE` with Hecate retaining the candidate stack. |
| `PASS_SETEXT_UNDERLINE` | Lady Macbeth + Hecate / Lady Macbeth | Read and classify the next line; retain its bytes on Hecate only until `PASS_SETEXT_EQUALS` or `PASS_SETEXT_DASH` proves it, otherwise retain them for raw replay. |
| `PASS_SETEXT_EQUALS` | Lady Macbeth + Hecate / Lady Macbeth | Require only `=` and permitted horizontal whitespace through newline; discard the proved underline, push existing `HEADER(1)` on Lady Macbeth, then enter `PASS_SETEXT_REPLAY`. |
| `PASS_SETEXT_DASH` | Lady Macbeth + Hecate / Lady Macbeth | Require only `-` and permitted horizontal whitespace through newline; discard the proved underline, push existing `HEADER(2)` on Lady Macbeth, then enter `PASS_SETEXT_REPLAY`. |
| `PASS_SETEXT_REPLAY` | Hecate + Puck / Hecate | Pop every retained candidate/replay glyph from Hecate and push it onto Puck; when Hecate's private floor is reached, enter `PASS_SETEXT_BRIDGE`. |
| `PASS_SETEXT_BRIDGE` | Puck + Horatio / Puck | Pop every replay glyph from Puck and push it onto Horatio; when Puck's private floor is reached, enter `PASS_SETEXT_CLOSE`. |
| `PASS_SETEXT_CLOSE` | Lady Macbeth + Horatio / Lady Macbeth | Pop every glyph from Horatio and push it onto Lady Macbeth. At Horatio's floor, return to the existing block dispatcher; the success route has `HEADER(level)` before the restored title, and the failed route has only its raw bytes. |
| `PASS_SETEXT_EOF` | Lady Macbeth + Hecate / Lady Macbeth | Treat an EOF candidate as unproved and enter the same replay route without reading beyond EOF. |

`PASS_SETEXT_REPLAY` and `PASS_SETEXT_BRIDGE` are the sole pair-transition
chain: `Hecate/Lady Macbeth -> Hecate/Puck -> Puck/Horatio -> Lady
Macbeth/Horatio`. No label may mention all of Hecate, Puck, and Horatio; no
selector, token, Act-III/IV role, compiler behavior, or fixture branch is
authorized. Before implementing this amendment, add the eight working TOML
entries (including the new bridge entry) from this design to
`src/20-act2-literary.toml`, then run the plan's exact SPL-facing compliance
gate:

```bash
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
```

## Amendment A3 (2026-07-18): source-safe Setext finalization

The A2 ledger is superseded because its candidate stack was placed on Hecate,
which is also Act II's unread-source stack.  `_read()` pops Hecate, so a
retained candidate would be reread as input and cannot make forward progress.
This amendment authorizes one additional working scene,
`PASS_SETEXT_FINALIZE`, and replaces the unused `PASS_SETEXT_EOF` working
entry with `PASS_SETEXT_REQUEUE`.  The working pool is therefore nine labels;
the four named spares remain untouched.

`PASS_SETEXT_CANDIDATE` first places a private sentinel on Lady Macbeth above
the already-emitted stream, then pushes the candidate title bytes (including
its terminating newline) above that sentinel while `_read()` continues to
consume Hecate.  `PASS_SETEXT_UNDERLINE` places a separate private sentinel on
Horatio and holds only the look-ahead underline bytes there.  It must never
push a retained glyph onto Hecate.  An EOF candidate is an unproved candidate
and enters `PASS_SETEXT_FINALIZE` directly; it does not require a dedicated
scene.

| Label | Stage pair / anchor | Stack action and exit |
|---|---|---|
| `PASS_SETEXT_CANDIDATE` | Lady Macbeth + Hecate / Lady Macbeth | Seed Lady Macbeth's candidate floor, read source through its first newline, and capture title bytes above that floor. At EOF enter `PASS_SETEXT_FINALIZE` in raw mode; otherwise enter `PASS_SETEXT_UNDERLINE`. |
| `PASS_SETEXT_UNDERLINE` | Hecate + Horatio / Hecate | Seed Horatio's underline floor; read and classify the next line while retaining its bytes on Horatio. A valid all-`=` or all-`-` line enters the matching proof scene. Any other byte or boundary enters `PASS_SETEXT_REQUEUE`; no input glyph is pushed to Hecate here. |
| `PASS_SETEXT_EQUALS` | Lady Macbeth + Horatio / Lady Macbeth | Discard Horatio's provisional underline through its floor, push existing `HEADER(1)` below the eventual restored title, set finalize mode to proved, and enter `PASS_SETEXT_FINALIZE`. |
| `PASS_SETEXT_DASH` | Lady Macbeth + Horatio / Lady Macbeth | Discard Horatio's provisional underline through its floor, push existing `HEADER(2)` below the eventual restored title, set finalize mode to proved, and enter `PASS_SETEXT_FINALIZE`. |
| `PASS_SETEXT_REQUEUE` | Hecate + Horatio / Hecate | Pop Horatio's provisional underline bytes back onto Hecate until its private floor, discard that floor, set finalize mode to raw, and enter `PASS_SETEXT_FINALIZE`. This restores the first look-ahead glyph to the top of unread input without decrementing the source countdown. |
| `PASS_SETEXT_FINALIZE` | Lady Macbeth + Hecate / Lady Macbeth | Pop candidate bytes from Lady Macbeth to Hecate until Lady Macbeth's candidate floor, discard that floor, and place a private Hecate floor below those bytes. It performs no `_read()` and therefore does not consume or reorder the unread source below the floor; then enter `PASS_SETEXT_REPLAY`. |
| `PASS_SETEXT_REPLAY` | Hecate + Puck / Hecate | Seed Puck's private replay floor, transfer finalized title bytes from Hecate to Puck until Hecate's private floor, discard that floor, then enter `PASS_SETEXT_BRIDGE`. |
| `PASS_SETEXT_BRIDGE` | Puck + Horatio / Puck | Seed Horatio's private restore floor, transfer title bytes from Puck to Horatio until Puck's replay floor, discard that floor, then enter `PASS_SETEXT_CLOSE`. |
| `PASS_SETEXT_CLOSE` | Lady Macbeth + Horatio / Lady Macbeth | Transfer title bytes from Horatio to Lady Macbeth until Horatio's restore floor, discard that floor, and return to the existing block dispatcher. Proved mode has its `HEADER(level)` beneath restored title bytes; raw mode has title bytes restored while the look-ahead underline remains unread on Hecate. |

The only candidate-transfer chain is now
`Lady Macbeth/Hecate -> Lady Macbeth/Hecate (finalize) -> Hecate/Puck ->
Puck/Horatio -> Lady Macbeth/Horatio`; the failed underline requeue is the
separate `Hecate/Horatio` leg before finalization.  Each private floor is
pushed, observed, and discarded by its named owning scene family; it is never
allowed into Act III's stream.  No scene names Hecate, Puck, and Horatio
together.  This amendment changes no token, selector, Act-III/IV role,
compiler behavior, fixture branch, or raw-HTML/header scope.

Before implementation, replace the old eight-entry TOML reservation with the
nine ready-to-paste entries above, including `PASS_SETEXT_REQUEUE` and
`PASS_SETEXT_FINALIZE`, then run:

```bash
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
```
