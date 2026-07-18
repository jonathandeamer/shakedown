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

Only Act II may need new controlled scenes.  The derived setext scanner needs
seven labels (candidate, underline classification, equals emit, dash emit,
replay, close, and EOF); existing raw-HTML/header scenes are amended in place.
The four-title spare minimum is also greater than 20% of seven.  Add a working
entry only with the identically named IR scene; do not draw a spare without a
plan amendment.

```toml
# Slice 5 Act-II working pool (7)
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
[scenes.PASS_SETEXT_REPLAY]
title = "Lady Macbeth returns the unproved mark in order."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_CLOSE]
title = "Lady Macbeth seals the proven heading."
pattern = "scene_of_character"
[scenes.PASS_SETEXT_EOF]
title = "Lady Macbeth releases the unmarked final line."
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
