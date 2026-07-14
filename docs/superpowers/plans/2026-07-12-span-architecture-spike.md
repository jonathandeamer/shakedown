# Span Architecture Spike Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish and prove Act III's protected-region, buffered-scan shape for code spans, escapes, HTML, links/images, and representative strong/emphasis before Slice 2 expands span behavior.

**Architecture:** Follow [the accepted span design](../specs/2026-07-12-span-architecture-spike-design.md): Act III copies the structural stream but reads each eligible paragraph into a private, floor-bounded source buffer and writes final glyphs once to Juliet. Protected regions are scanner modes rather than persistent inline tokens; output HTML is never treated as later Markdown input. Oracle-backed probe fixtures and reviewed debug dumps are both gates.

**Tech Stack:** Python 3.12 typed splc IR, generated SPL fragments, TOML-controlled literary surfaces, pytest, local Markdown.pl v1.0.1 oracle, shakespearelang.

## Global Constraints

- First read `docs/superpowers/plans/plan-roadmap.md`, architecture §4.3/§7.5/§8.2, the accepted design above, `docs/markdown/oracle-mechanics.md`, and `docs/superpowers/notes/spl-literary-protocol.md`; this is the sole in-flight plan.
- Before SPL-facing edits read `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`, `docs/spl/codegen-style-guide.md`, and `src/literary.toml`. New Act III prose is controlled TOML-owned prose; use only the reservations below.
- Do not hand-edit `src/30-act3-span.spl`, `debug/40-act4-token-dump.spl`, or `shakedown.spl`. Edit `src_ir/*.py` and `src/30-act3-literary.toml`, then run `uv run python -m scripts.splc` and `uv run python scripts/assemble.py`.
- Do not add final inline token codes, change the accepted list/blockquote grammar, widen mdtest's shipped-fixture set, implement reference links, or broaden the scope to general HTML-block, hard-break, or full image/title syntax beyond the named probes.
- The exact literary compliance gate after every Act III/TOML change is: `uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q`.
- At each task boundary run its evidence gate; make a small conventional commit with the required MCO provenance trailers, then `git push`. If pushing fails, append one `- BLOCK:` line to `.agent/blockers.md` and exit without force-pushing.

## File map

| Path | Responsibility |
|---|---|
| `src_ir/act3.py` | Buffered source-region scan, protected-region dispatch, and Act III carrier-floor choreography. |
| `src/30-act3-literary.toml` | Every newly generated Act III scene title and Recall phrase. |
| `tests/fixtures/architecture_spikes/spans/*.text` | Five narrowly scoped Markdown inputs. |
| `tests/fixtures/architecture_spikes/spans/*.expected` | Fresh Markdown.pl byte contracts. |
| `tests/fixtures/token_stream/spans/*.dump` | Reviewed final Act-III streams, one integer per line including terminal `STREAM_END`. |
| `tests/test_architecture_spikes.py` | Oracle and literal-byte probe parity. |
| `tests/test_token_dump.py` | Debug-target baselines and interpreter carrier/sentinel checks. |
| `tests/test_act3_contracts.py` | Act-III interpreter-level protected-region and borrowed-stack contracts. |
| `tests/test_splc_interpret_parity.py` | Generated-SPL/interpreter parity coverage when new control-flow shapes require it. |

## Literary reservations (ready to paste)

These are Act III pastoral/natural controlled titles and Recall surfaces.
The buffered scanner is a scene-per-state IR machine, so its title budget is
sized from the existing link/reference scanner rather than from the number of
user-visible Markdown features: Task 3 reserves 23 working labels and six
spares; Task 4 reserves 23 working labels and six spares. Add only labels
actually used in the IR, but take every title exclusively from these pools. If
either spare pool is exhausted, stop and request a planning amendment instead
of inventing prose. No new Critical or Stable Utility phrase is needed.

```toml
# src/30-act3-literary.toml
[scenes.LYRIC_BUFFER_OPEN]
title = "Romeo gathers the unspent morning line."
pattern = "scene_of_character"
[scenes.LYRIC_BUFFER_DRAIN]
title = "Romeo gathers each dew-bright mark."
pattern = "scene_of_character"
[scenes.LYRIC_BUFFER_KEEP]
title = "Juliet keeps the gathered garden mark."
pattern = "scene_of_character"
[scenes.LYRIC_BUFFER_DRAIN_CLOSE]
title = "The morning line reaches its quiet hedge."
pattern = "bare_statement"
[scenes.LYRIC_SCAN_NEXT]
title = "Romeo seeks the next unspent petal."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_RUN]
title = "Juliet shelters the silver backtick measure."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_COUNT]
title = "Romeo counts the silver measure's leaves."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_SEEK]
title = "Juliet seeks the answering silver measure."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_COMPARE]
title = "The lovers weigh two moonlit measures."
pattern = "cross_character"
[scenes.LYRIC_CODE_MATCH]
title = "Romeo finds the measure's faithful mate."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_BODY]
title = "Juliet keeps the sheltered silver text."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_CLOSE]
title = "The silver measure closes in the dawn."
pattern = "bare_statement"
[scenes.LYRIC_CODE_FALLBACK]
title = "The unmatched silver mark returns to grass."
pattern = "bare_statement"
[scenes.LYRIC_CODE_REPLAY]
title = "Romeo restores the loose moonlit marks."
pattern = "scene_of_character"
[scenes.LYRIC_ESCAPE_TEST]
title = "Juliet tests the thorn before the rose."
pattern = "scene_of_character"
[scenes.LYRIC_ESCAPE_GLYPH]
title = "Romeo frees one guarded garden mark."
pattern = "scene_of_character"
[scenes.LYRIC_ESCAPE_LITERAL]
title = "Juliet lets the guarded petal pass unchanged."
pattern = "scene_of_character"
[scenes.LYRIC_ORDINARY_GLYPH]
title = "Romeo tends the unguarded garden mark."
pattern = "scene_of_character"
[scenes.LYRIC_BUFFER_ENTITY_AMP]
title = "Juliet names the stream's small riverbend."
pattern = "scene_of_character"
[scenes.LYRIC_BUFFER_ENTITY_ANGLE]
title = "Romeo softens the hedge's bright corner."
pattern = "scene_of_character"
[scenes.LYRIC_BUFFER_UNWIND]
title = "The gathered line returns by the garden gate."
pattern = "bare_statement"
[scenes.LYRIC_BUFFER_CLOSE]
title = "The lovers return the finished line."
pattern = "cross_character"
[scenes.LYRIC_BUFFER_RETURN]
title = "Romeo returns the finished garden line."
pattern = "scene_of_character"

# Task 3 spare pool — do not use unless an extra generated scene is necessary.
[scenes.LYRIC_BUFFER_FALLBACK]
title = "The loose rose returns to daylight."
pattern = "bare_statement"
[scenes.LYRIC_BUFFER_REVERSE]
title = "Juliet turns the gathered petals home."
pattern = "scene_of_character"
[scenes.LYRIC_BUFFER_SENTINEL]
title = "The garden gate keeps the borrowed path."
pattern = "bare_statement"
[scenes.LYRIC_CODE_TRIM]
title = "Romeo lifts one balanced pair of dew."
pattern = "scene_of_character"
[scenes.LYRIC_ESCAPE_FALLBACK]
title = "The thorn remains beside the rose."
pattern = "bare_statement"
[scenes.LYRIC_BUFFER_FINISH]
title = "Juliet seals the line beneath the moon."
pattern = "scene_of_character"

# Task 4 protected-region pool — reserve before implementation.
[scenes.LYRIC_HTML_TAG]
title = "Juliet keeps the moonlit tag whole."
pattern = "scene_of_character"
[scenes.LYRIC_HTML_OPEN]
title = "Romeo opens the quiet moonlit gate."
pattern = "scene_of_character"
[scenes.LYRIC_HTML_SCAN]
title = "Juliet guards each mark within the gate."
pattern = "scene_of_character"
[scenes.LYRIC_HTML_KEEP]
title = "Romeo bears the guarded tag unchanged."
pattern = "scene_of_character"
[scenes.LYRIC_HTML_CLOSE]
title = "The moonlit gate closes without a thorn."
pattern = "bare_statement"
[scenes.LYRIC_AUTOLINK_TEST]
title = "Juliet asks whether the bright path is named."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_BODY]
title = "Romeo follows the river's shining road."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_CLOSE]
title = "The shining road meets its silver gate."
pattern = "bare_statement"
[scenes.LYRIC_LINK_REGION]
title = "Romeo binds the rose to its bright path."
pattern = "scene_of_character"
[scenes.LYRIC_IMAGE_TEST]
title = "Juliet sees the little garden portrait."
pattern = "scene_of_character"
[scenes.LYRIC_LABEL_OPEN]
title = "Romeo opens the rose's tender name."
pattern = "scene_of_character"
[scenes.LYRIC_LABEL_SCAN]
title = "Juliet tends the petals within the name."
pattern = "scene_of_character"
[scenes.LYRIC_LABEL_CLOSE]
title = "The rose's tender name reaches daylight."
pattern = "bare_statement"
[scenes.LYRIC_DESTINATION_OPEN]
title = "Romeo enters the winding garden road."
pattern = "scene_of_character"
[scenes.LYRIC_DESTINATION_SCAN]
title = "Juliet keeps the winding road's marks."
pattern = "scene_of_character"
[scenes.LYRIC_DESTINATION_BALANCE]
title = "The lovers balance each round garden turn."
pattern = "cross_character"
[scenes.LYRIC_DESTINATION_CLOSE]
title = "The winding road closes by the rose."
pattern = "bare_statement"
[scenes.LYRIC_TITLE_OPEN]
title = "Juliet opens the path's quiet name."
pattern = "scene_of_character"
[scenes.LYRIC_TITLE_SCAN]
title = "Romeo keeps the quiet name unbroken."
pattern = "scene_of_character"
[scenes.LYRIC_TITLE_CLOSE]
title = "The quiet name returns to moonlight."
pattern = "bare_statement"
[scenes.LYRIC_REGION_EMIT]
title = "Juliet sends the finished rose-path onward."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_STRONG]
title = "Juliet lays the star within the sunlit seal."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_SCAN]
title = "Romeo follows the star through the leaves."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_CLOSE]
title = "The sunlit seal closes around the star."
pattern = "bare_statement"

# Task 4 spare pool — do not use unless an extra generated scene is necessary.
[scenes.LYRIC_HTML_FALLBACK]
title = "The loose moonlit gate remains a gate."
pattern = "bare_statement"
[scenes.LYRIC_AUTOLINK_FALLBACK]
title = "The unmarked road returns to the field."
pattern = "bare_statement"
[scenes.LYRIC_LABEL_REPLAY]
title = "Romeo sends the bound petals onward."
pattern = "scene_of_character"
[scenes.LYRIC_DESTINATION_REPLAY]
title = "Juliet restores the winding path's petals."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_FALLBACK]
title = "The unpaired star remains in the garden."
pattern = "bare_statement"
[scenes.LYRIC_REGION_FINISH]
title = "The lovers leave the finished garden whole."
pattern = "cross_character"

[characters.romeo.recall]
buffered_first_glyph = "Recall the morning buffer's first glyph."
protected_run_measure = "Recall the guarded measure."
link_label_mark = "Recall the bound rose's mark."
[characters.juliet.recall]
buffered_last_glyph = "Recall the night's final glyph."
protected_tag_mark = "Recall the silver tag's mark."
```

## Amendment A1 (2026-07-13): Step 5 code-span machine — two-character choreography, expanded pool

This amendment resolves the twenty recorded Step 5 halts (`.agent/blockers.md`
history, commits `8bb31bc`…`7940b24`). It authorizes a combination of halt
options (a) and (c): a **two-character scanner design** that needs **no change
to `scripts/splc/validate.py`, `scripts/splc/lower.py`, or the IR instruction
set**, plus a **scene-title and recall-key budget increase** reserved below.
Option (b) (three-character scenes) is rejected: SPL second-person semantics
make a third on-stage character ambiguous, which is why the validator forbids
it. Fix/implement executors may resume Step 5 under this amendment.

### Why no scene ever needs three characters

The halted analyses assumed maximal backtick matching requires ROMEO, JULIET,
and PUCK on stage at once. It does not, because of two verified compiler and
interpreter facts:

1. **Off-stage value references are legal SPL and already implemented.**
   `docs/spl/reference.md` (state table: "Character name — that character's
   current value, even if off stage"; finding 8: "Characters retain values
   off-stage") is the canonical semantics. `scripts/splc/lower.py` renders
   `val(CHAR)` of a non-participant as the character's name in third person,
   and `Branch` supports testing an off-stage character ("Is Macbeth as fair
   as Hecate?" asked by the anchor, with the companion answering the Ifs).
2. **Registers live in idle characters' values; buffers live in idle stacks.**
   HECATE, MACBETH, LADY_MACBETH, HORATIO, and PROSPERO do nothing in Act III.
   A run-length comparison therefore never shares a scene with the source,
   output, and buffer stacks at once — each scene touches at most two
   characters, and the stage pairs rotate between scenes exactly as the
   existing `LYRIC_OPEN_*` idiom already does.

A skeleton of the machine below (opener counting into HECATE, candidate
counting into MACBETH, the off-stage `eq(val(MACBETH), val(HECATE))` branch,
and Juliet-paired emission) was passed through `validate()` and `lower_act()`
on 2026-07-13 and lowered cleanly with two characters on stage in every scene.

### Register and stack map (binding for Step 5)

| Holder | Role during one code-span attempt |
|---|---|
| PUCK (stack) | Source glyphs, top = next glyph, terminated by `TEXT_END` (unchanged) |
| JULIET (stack) | One-way output stream (unchanged) |
| ROMEO (stack) | Speculative consumed source above a private `STREAM_END` sentinel; below the sentinel the Slice-1 discard pile is untouched |
| HECATE (value) | Opener run length N |
| HECATE (stack) | Reversed, tail-trimmed span content above a private `STREAM_END` sentinel |
| MACBETH (value) | Candidate closer run length M |
| ROMEO/HECATE/MACBETH (values) | Freely clobbered by later pops once their phase is over; nothing in Act III branches on them outside this machine |

ROSALIND is off-limits: her four goto lines must remain the play's only
Rosalind speeches (`test_reference_librarian_is_visible_in_reference_scenes`).

### Oracle semantics correction

Markdown.pl v1.0.1 `_DoCodeSpans` strips **all** leading and trailing spaces
and tabs from span content (`s/^[ \t]*//g`, `s/[ \t]*$//g`), not "one balanced
outer space pair" as Step 5 previously said. The closer is the **first**
maximal backtick run of exactly the opener's length (`(?<!`)\1(?!`)`); maximal
runs of any other length are span content. This amendment's wording wins.

### Scene table (binding for Step 5)

Entry hook: in `LYRIC_POP_GLYPH`, insert
`branch(eq(val(PUCK), _k(96)), then="LYRIC_CODE_RUN")` between the `TEXT_END`
branch and the `'['` branch. (96 decomposes as 64+32 within the 4-operator
bound; add a `RECIPES[96] = mul(const(8), add(const(8), const(4)))` entry in
`src_ir/stream.py` only if `test_numeric_recipe_complexity_stays_bounded` or
the big-cat atom test rejects the default decomposition.)

Every scene below lists its ops in order; `pair` is what
`validate.participants` derives. Recall keys name the speaker whose TOML pool
holds them (see reservations below). Self-loops close with `goto`, never a
branch, so `entry_pairs` stays consistent.

| Scene | Ops (in order) | pair (anchor first) |
|---|---|---|
| `LYRIC_CODE_RUN` | `let(HECATE, const(1))`; `goto LYRIC_CODE_COUNT` | (ROMEO, HECATE) |
| `LYRIC_CODE_COUNT` | `pop(PUCK, recall="silver_measures_leaf")` [romeo]; `branch(96 → LYRIC_CODE_COUNT_MORE)`; `goto LYRIC_CODE_SEEK_OPEN` | (ROMEO, PUCK) |
| `LYRIC_CODE_COUNT_MORE` | `let(HECATE, add(val(HECATE), const(1)))`; `goto LYRIC_CODE_COUNT` | (ROMEO, HECATE) |
| `LYRIC_CODE_SEEK_OPEN` | `push(ROMEO, const(tokens.STREAM_END))`; `branch(eq(val(PUCK), const(tokens.TEXT_END)) → LYRIC_CODE_FALLBACK)`; `goto LYRIC_CODE_KEEP`; `companion=PUCK` | (ROMEO, PUCK) |
| `LYRIC_CODE_KEEP` | `push(ROMEO, val(PUCK))`; `goto LYRIC_CODE_SEEK`; `companion=PUCK` | (ROMEO, PUCK) |
| `LYRIC_CODE_SEEK` | `pop(PUCK, recall="sought_moonlit_glyph")` [romeo]; `branch(TEXT_END → LYRIC_CODE_FALLBACK)`; `branch(96 → LYRIC_CODE_CAND_OPEN)`; `goto LYRIC_CODE_KEEP` | (ROMEO, PUCK) |
| `LYRIC_CODE_CAND_OPEN` | `let(MACBETH, const(1))`; `goto LYRIC_CODE_CAND_COUNT` | (ROMEO, MACBETH) |
| `LYRIC_CODE_CAND_COUNT` | `pop(PUCK, recall="answering_measures_leaf")` [romeo]; `branch(96 → LYRIC_CODE_CAND_MORE)`; `goto LYRIC_CODE_COMPARE` | (ROMEO, PUCK) |
| `LYRIC_CODE_CAND_MORE` | `let(MACBETH, add(val(MACBETH), const(1)))`; `goto LYRIC_CODE_CAND_COUNT` | (ROMEO, MACBETH) |
| `LYRIC_CODE_COMPARE` | `branch(eq(val(MACBETH), val(HECATE)), then=LYRIC_CODE_MATCH, else_=LYRIC_CODE_CAND_REPLAY)`; `companion=PUCK` — off-stage test, third-person question | (ROMEO, PUCK) |
| `LYRIC_CODE_CAND_REPLAY` | `branch(eq(val(MACBETH), const(0)) → LYRIC_CODE_CAND_DONE)`; `push(ROMEO, _k(96))`; `let(MACBETH, sub(val(MACBETH), const(1)))`; `goto LYRIC_CODE_CAND_REPLAY` | (ROMEO, MACBETH) |
| `LYRIC_CODE_CAND_DONE` | `branch(eq(val(PUCK), const(tokens.TEXT_END)) → LYRIC_CODE_FALLBACK)`; `goto LYRIC_CODE_KEEP`; `companion=PUCK` | (ROMEO, PUCK) |
| `LYRIC_CODE_MATCH` | `push(PUCK, val(PUCK))` (return lookahead); `push(HECATE, const(tokens.STREAM_END))`; `goto LYRIC_CODE_TRIM`; `anchor=HECATE` | (HECATE, PUCK) |
| `LYRIC_CODE_TRIM` | `pop(ROMEO, recall="dew_hemmed_edge")` [hecate]; `branch(32 → LYRIC_CODE_TRIM)`; `branch(9 → LYRIC_CODE_TRIM)`; `branch(STREAM_END → LYRIC_CODE_BODY)`; `goto LYRIC_CODE_REV_KEEP`; `companion=HECATE` | (ROMEO, HECATE) |
| `LYRIC_CODE_REV_KEEP` | `push(HECATE, val(ROMEO))`; `goto LYRIC_CODE_REV` | (ROMEO, HECATE) |
| `LYRIC_CODE_REV` | `pop(ROMEO, recall="gathered_nettle")` [hecate]; `branch(STREAM_END → LYRIC_CODE_BODY)`; `goto LYRIC_CODE_REV_KEEP`; `companion=HECATE` | (ROMEO, HECATE) |
| `LYRIC_CODE_BODY` | `*_stream(*b"<code>")`; `goto LYRIC_CODE_HEAD`; `anchor=JULIET, companion=HECATE` | (JULIET, HECATE) |
| `LYRIC_CODE_HEAD` | `pop(HECATE, recall="sheltered_first_glyph")` [juliet]; `branch(32 → LYRIC_CODE_HEAD)`; `branch(9 → LYRIC_CODE_HEAD)`; `branch(STREAM_END → LYRIC_CODE_CLOSE)`; `goto LYRIC_CODE_GLYPH`; `anchor=JULIET` | (JULIET, HECATE) |
| `LYRIC_CODE_GLYPH` | `branch(38 → LYRIC_CODE_AMP)`; `branch(60 → LYRIC_CODE_LT)`; `branch(62 → LYRIC_CODE_GT)`; `goto LYRIC_CODE_PLAIN`; `anchor=JULIET, companion=HECATE` (branches test `val(HECATE)`) | (JULIET, HECATE) |
| `LYRIC_CODE_PLAIN` | `push(JULIET, val(HECATE))`; `goto LYRIC_CODE_NEXT`; `anchor=JULIET, companion=HECATE` | (JULIET, HECATE) |
| `LYRIC_CODE_AMP` | `*_entity(*b"&amp;")`; `goto LYRIC_CODE_NEXT`; `anchor=JULIET, companion=HECATE` | (JULIET, HECATE) |
| `LYRIC_CODE_LT` | `*_entity(*b"&lt;")`; `goto LYRIC_CODE_NEXT`; `anchor=JULIET, companion=HECATE` | (JULIET, HECATE) |
| `LYRIC_CODE_GT` | `*_entity(*b"&gt;")`; `goto LYRIC_CODE_NEXT`; `anchor=JULIET, companion=HECATE` | (JULIET, HECATE) |
| `LYRIC_CODE_NEXT` | `pop(HECATE, recall="sheltered_next_glyph")` [juliet]; `branch(STREAM_END → LYRIC_CODE_CLOSE)`; `goto LYRIC_CODE_GLYPH`; `anchor=JULIET` | (JULIET, HECATE) |
| `LYRIC_CODE_CLOSE` | `*_stream(*b"</code>")`; `goto LYRIC_RETURN_TO_SCAN`; `anchor=JULIET, companion=HECATE` | (JULIET, HECATE) |
| `LYRIC_CODE_FALLBACK` | `push(PUCK, const(tokens.TEXT_END))`; `goto LYRIC_CODE_REPLAY` | (ROMEO, PUCK) |
| `LYRIC_CODE_REPLAY` | `pop(ROMEO, recall="returned_petal")` [puck]; `branch(STREAM_END → LYRIC_CODE_TICKS)`; `goto LYRIC_CODE_REPLAY_KEEP`; `companion=PUCK` | (ROMEO, PUCK) |
| `LYRIC_CODE_REPLAY_KEEP` | `push(PUCK, val(ROMEO))`; `goto LYRIC_CODE_REPLAY` | (ROMEO, PUCK) |
| `LYRIC_CODE_TICKS` | `branch(eq(val(HECATE), const(0)) → LYRIC_CODE_TICKS_DONE)`; `push(JULIET, _k(96))`; `let(HECATE, sub(val(HECATE), const(1)))`; `goto LYRIC_CODE_TICKS`; `anchor=JULIET` | (JULIET, HECATE) |
| `LYRIC_CODE_TICKS_DONE` | `goto LYRIC_RETURN_TO_SCAN`; `anchor=JULIET, companion=HECATE` | (JULIET, HECATE) |

Invariants the implementer must preserve:

- The fallback pushes `TEXT_END` back onto PUCK **before** replaying content,
  so replayed glyphs are rescanned in source order ahead of the terminator;
  the opener's literal backticks are emitted to JULIET before the rescan
  resumes, matching source order. Each fallback consumes at least the opener
  run, so rescanning terminates.
- Content is never emitted from ROMEO directly: match → tail-trim while
  popping ROMEO (`LYRIC_CODE_TRIM` skips trailing spaces/tabs first because
  ROMEO's top is the last content glyph) → reverse into HECATE → head-trim in
  `LYRIC_CODE_HEAD` → encode `&`, `<`, `>` (and only those) → JULIET.
- No generated output is ever pushed back onto PUCK or ROMEO.
- Branch arrivals into a scene must all leave the same stage pair (they do in
  the table above); any new transition an implementer adds between different
  pairs must go through a `goto`, mirroring the existing `LYRIC_OPEN_*` idiom.

### Amendment A1 literary reservations (ready to paste)

Twenty new working scene titles plus six spares for `src/30-act3-literary.toml`
(the ten Step 5 titles already reserved above — `LYRIC_CODE_RUN`,
`LYRIC_CODE_COUNT`, `LYRIC_CODE_SEEK`, `LYRIC_CODE_COMPARE`,
`LYRIC_CODE_MATCH`, `LYRIC_CODE_BODY`, `LYRIC_CODE_CLOSE`,
`LYRIC_CODE_FALLBACK`, `LYRIC_CODE_REPLAY`, `LYRIC_CODE_TRIM` — remain in
force). Add only labels the IR actually uses. If this expanded spare pool is
exhausted, stop and request a planning amendment.

```toml
# src/30-act3-literary.toml — Amendment A1 pool
[scenes.LYRIC_CODE_COUNT_MORE]
title = "Hecate lengthens the silver tally."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_SEEK_OPEN]
title = "Romeo stakes the hedge before the search."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_KEEP]
title = "Romeo pockets one unproven petal."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_CAND_OPEN]
title = "Macbeth begins the answering tally."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_CAND_COUNT]
title = "Macbeth counts the answering silver leaves."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_CAND_MORE]
title = "Macbeth lengthens the answering tally."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_CAND_REPLAY]
title = "Macbeth returns the short measure to grass."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_CAND_DONE]
title = "The short measure lies among the petals."
pattern = "bare_statement"
[scenes.LYRIC_CODE_REV_KEEP]
title = "Hecate gathers one sheltered glyph."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_REV]
title = "Hecate turns the sheltered line about."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_HEAD]
title = "Juliet lifts the morning dew from the line."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_GLYPH]
title = "Juliet weighs the sheltered glyph."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_PLAIN]
title = "Juliet lays the sheltered glyph plain."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_AMP]
title = "Juliet names the sheltered riverbend."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_LT]
title = "Juliet softens the sheltered bright corner."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_GT]
title = "Juliet softens the sheltered far corner."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_NEXT]
title = "Juliet tends the sheltered line's next glyph."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_REPLAY_KEEP]
title = "Puck bears one petal back to daylight."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_TICKS]
title = "Juliet returns the lonely silver marks."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_TICKS_DONE]
title = "The lonely silver marks rest in daylight."
pattern = "bare_statement"

# Amendment A1 spare pool — do not use unless an extra generated scene is necessary.
[scenes.LYRIC_CODE_HOLD]
title = "Romeo holds the unproven line still."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_MEND]
title = "Hecate mends the broken silver tally."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_TURN]
title = "Puck turns the borrowed petal home."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_GATE]
title = "The sheltered line passes the garden gate."
pattern = "bare_statement"
[scenes.LYRIC_CODE_REST]
title = "The silver measure rests beneath the hedge."
pattern = "bare_statement"
[scenes.LYRIC_CODE_WAKE]
title = "Juliet wakes the waiting silver line."
pattern = "scene_of_character"
```

New recall keys for `src/literary.toml` (recall keys live in the pool of the
**speaker** — the character who says the Recall line, per
`lower.py::_roles`; the bracketed speaker in the scene table above names the
pool). One spare per speaker; do not invent others.

```toml
# src/literary.toml additions — Amendment A1
[characters.romeo.recall]  # merge into the existing table
silver_measures_leaf = "Recall the silver measure's leaf."
sought_moonlit_glyph = "Recall the sought moonlit glyph."
answering_measures_leaf = "Recall the answering measure's leaf."
hedges_kept_glyph = "Recall the hedge's kept glyph."

[characters.juliet.recall]  # merge into the existing table
sheltered_first_glyph = "Recall the sheltered line's first glyph."
sheltered_next_glyph = "Recall the sheltered line's next glyph."
sheltered_kept_glyph = "Recall the sheltered kept glyph."

[characters.hecate.recall]  # merge into the existing table
dew_hemmed_edge = "Recall the dew-hemmed edge."
gathered_nettle = "Recall the gathered nettle."
turned_leaf = "Recall the turned leaf."

[characters.puck.recall]  # merge into the existing table
returned_petal = "Recall the returned petal."
borrowed_petal = "Recall the borrowed petal."
```

The same two-character register choreography (idle-character values as
registers, idle stacks as sentinel-bounded buffers, off-stage branch tests) is
pre-authorized for Task 4's protected-region scanner should the same wall
reappear there; Task 4 prose must still come only from its reserved pools.

## Amendment A2 (2026-07-13): Task 4 shared-idiom redesign, expanded pool

This amendment clears the `BLOCK[plan]` recorded 2026-07-13: a stashed,
uncommitted Task 4 Step 2 attempt (`git stash list` entry "Task 4 Step 2 WIP:
HTML/autolink/link/image/emphasis scanner, 91 scenes vs 29 reserved budget")
implemented every protected mode correctly but needed 91 distinct `LYRIC_*`
scene labels — over 3x the 23-working/6-spare pool reserved below the base
literary reservations. Root cause: the WIP gave HTML tag emit, autolink
href, autolink text, link/image destination, link/image title, and emphasis
body each their own amp/lt/gt entity-encode triple, and gave label,
alt, destination, and title each their own open/scan/keep/close/fallback
quintet, instead of sharing one of each. This amendment supersedes the Task 4
pool above (the 23 working + 6 spare titles under "Task 4 protected-region
pool" / "Task 4 spare pool" are retired — do not use them) with a smaller
shared-idiom design plus its own reserved pool, sized from the design below
rather than from feature count.

### Why one scan pipeline and one requeue trick cover every protected mode

Three techniques eliminate essentially all of the WIP's duplication:

1. **One shared field pipeline (`LYRIC_FIELD_*`), anchored on Juliet,
   parameterized by an idle call-site register.** HTML tags, autolink
   href/text, link/image destinations, and link/image titles all reduce to
   "capture raw glyphs from Puck up to a terminator, optionally reverse and
   entity-encode, emit to Juliet, then dispatch to a per-call-site
   continuation." The dispatch and the terminator are both selected by a
   single idle value register (Hecate, reused the same way Amendment A1
   already established: "idle once phase is over") holding a small integer
   call-site code set by the caller before jumping into `LYRIC_FIELD_OPEN`.
   `branch` chains (already used for the amp/lt/gt tests) select the right
   terminator and the right post-drain continuation from that one code, the
   same way `LYRIC_CODE_GLYPH` already chains three branches for amp/lt/gt.
   HTML tag content takes the same pipeline with entity-encoding skipped
   (the call-site code doubles as the opaque-copy flag), so it needs no
   separate scan/keep/close trio.
2. **Capture-hold-then-requeue for content that must itself be rescanned.**
   Link/image label and alt text must receive entity encoding *and* nested
   strong/emphasis (`test_act3_renders_links_images_protected` expects
   `<a href="http://e/x_(y)" title="t">a <em>b</em></a>`), but that content
   is scanned *before* the destination/title that must precede it in
   HTML-attribute-order output. Rather than duplicate the emphasis/entity
   pipeline anchored at a second output character, capture the raw
   label/alt glyphs onto Horatio's stack (newly brought on stage in Act III
   for this hold only) without processing them, emit `<a href="`/`<img
   src="`, run destination and title through the shared field pipeline
   directly to Juliet, emit the closing `>`, then push the held label/alt
   glyphs back onto Puck above a private `TEXT_END` boundary and fall through
   to the play's ordinary top-level scan dispatch — the same dispatch that
   already handles entities, code spans, and emphasis for ordinary body
   text. This reuses the entire existing pipeline for free instead of
   duplicating it, and composes automatically with the emphasis machine
   added by this amendment (technique 3), which is why nested `<em>` inside
   a link label needs no dedicated scene. When the private boundary is popped
   back off, `LYRIC_RESUME_DISPATCH` (added to the existing glyph-dispatch
   entry point) hands control to whichever region is pending. This is
   requeuing *original, unprocessed* source glyphs, not generated output, so
   it does not violate
   `test_act3_source_buffer_never_receives_generated_output`: that test only
   checks Puck's source region is empty *after* the scan completes, which
   still holds since every requeued glyph is fully re-consumed before the
   paragraph scan ends.
3. **Duplicate-on-reverse for autolink's two emits.** An autolink's captured
   URL is drained twice — once amp-encoded into the `href` attribute, once
   amp/lt/gt-encoded into the link text — from the *same* capture, by having
   `LYRIC_FIELD_REV_KEEP` copy a second raw field onto Lady Macbeth's
   duplicate-floor stack when the call-site code says "keep source"
   (autolink href only), so a second `LYRIC_AUTOLINK_TEXT_OPEN` pass can
   re-drain it without rescanning Puck. This keeps `amp_count == 2` exactly
   as `test_act3_renders_inline_html_and_autolink` requires, with one
   capture instead of two.

Strong-then-emphasis reuses the code-span run-length technique from
Amendment A1 directly (opener count into an idle value register, candidate
count into a second idle value register, off-stage `eq` compare), with one
correction carried over from the stashed WIP's real bug: emit-open and
emit-close must branch on the register holding the **matched run length**
(Macbeth), never on the register also used to drain body content glyph by
glyph (Hecate) — the WIP's `LYRIC_EMPHASIS_EMIT_CLOSE` fell off the scene
because draining Hecate's content buffer clobbered the same register the
close branch tested. Because emphasis bodies are requeued through the
ordinary dispatch (technique 2) rather than drained and encoded in place,
there is no separate content-buffer register to clobber in this redesign,
but implementers must still keep the opener/closer run-length register
(Macbeth) untouched by anything that walks body content.

### Register and stack map addition (binding for Task 4)

| Holder | Role during Task 4, in addition to Amendment A1's map |
|---|---|
| HECATE (value) | Field glyph register while draining Hecate's reverse stack, or active `RESUME_*` immediately before a private `TEXT_END`. Amendment A7 supersedes the former field-tag assignment. |
| PROSPERO (value) | Active `FIELD_*` call-site code from `LYRIC_FIELD_RETRY` through `LYRIC_FIELD_DRAIN_CLOSE`; later, after that tag is dead, frozen `RESUME_*` close choice in `LYRIC_RESUME_DISPATCH`. |
| MACBETH (value) | Local scratch per field: destination paren-balance counter, or emphasis opener/closer run length. Never shared concurrently between these uses. |
| ROMEO (stack) | Field capture buffer above a private `STREAM_END` sentinel (unchanged discipline from Amendment A1). |
| HORATIO (stack, newly on stage in Act III) | Hold buffer for captured, unprocessed label/alt glyphs and for emphasis body glyphs between capture and requeue. |
| LADY_MACBETH (stack) | Private continuation records and the duplicate autolink buffer; see Amendment A4. |
| A private `TEXT_END` on PUCK | Marks where requeued label/alt/emphasis-body content ends; Hecate's resume code directs it to `LYRIC_RESUME_DISPATCH`. |

### Amendment A2 literary reservations (ready to paste, supersedes the Task 4 pool above)

41 new working scene titles plus 10 spares for `src/30-act3-literary.toml`.
Add only labels the IR actually uses. If this spare pool is exhausted, stop
and request a further planning amendment instead of inventing prose.

```toml
# src/30-act3-literary.toml — Amendment A2 pool (replaces the retired Task 4 pool)
[scenes.LYRIC_FIELD_OPEN]
title = "Romeo opens the unnamed field's gate."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_SCAN]
title = "Romeo walks the unnamed field's edge."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_UNTERMINATED]
title = "The unnamed field ends without its gate."
pattern = "bare_statement"
[scenes.LYRIC_FIELD_REV_KEEP]
title = "Romeo gathers one field-worn mark."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_REV]
title = "Romeo turns the field's line about."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_CLOSE_DISPATCH]
title = "Romeo asks which road the field leads to."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_HEAD]
title = "Juliet lifts the field's first glyph."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_GLYPH]
title = "Juliet weighs the field's kept glyph."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_PLAIN]
title = "Juliet lays the field's glyph plain."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_AMP]
title = "Juliet names the field's small riverbend."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_LT]
title = "Juliet softens the field's bright corner."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_GT]
title = "Juliet softens the field's far corner."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_NEXT]
title = "Juliet tends the field's next glyph."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_DRAIN_CLOSE]
title = "The field's drained line reaches its gate."
pattern = "bare_statement"
[scenes.LYRIC_FIELD_HOLD]
title = "Horatio keeps the unspoken field whole."
pattern = "scene_of_character"
[scenes.LYRIC_ANGLE_TEST]
title = "Juliet asks what the bright angle names."
pattern = "scene_of_character"
[scenes.LYRIC_HTML_OPEN]
title = "Romeo keeps the moonlit tag whole."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_OPEN]
title = "Juliet opens the shining road."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_TEXT_OPEN]
title = "Romeo walks the shining road again."
pattern = "scene_of_character"
[scenes.LYRIC_AUTOLINK_CLOSE]
title = "The shining road meets its silver gate."
pattern = "bare_statement"
[scenes.LYRIC_LINK_REGION]
title = "Romeo binds the rose to its bright path."
pattern = "scene_of_character"
[scenes.LYRIC_IMAGE_TEST]
title = "Juliet sees the little garden portrait."
pattern = "scene_of_character"
[scenes.LYRIC_LABEL_OPEN]
title = "Horatio opens the rose's tender name."
pattern = "scene_of_character"
[scenes.LYRIC_ALT_OPEN]
title = "Horatio opens the portrait's quiet name."
pattern = "scene_of_character"
[scenes.LYRIC_DEST_OPEN]
title = "Romeo enters the winding garden road."
pattern = "scene_of_character"
[scenes.LYRIC_DEST_BALANCE]
title = "Macbeth balances each round garden turn."
pattern = "cross_character"
[scenes.LYRIC_TITLE_OPEN]
title = "Romeo opens the path's quiet name."
pattern = "scene_of_character"
[scenes.LYRIC_REGION_TAG_OPEN]
title = "Juliet seals the gate before the name."
pattern = "scene_of_character"
[scenes.LYRIC_REGION_RESUME]
title = "Horatio releases the tender name at last."
pattern = "scene_of_character"
[scenes.LYRIC_REGION_FALLBACK]
title = "The unbound rose returns to the field."
pattern = "bare_statement"
[scenes.LYRIC_RESUME_DISPATCH]
title = "Romeo asks which held name has returned."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_OPEN]
title = "Juliet lays the star within the sunlit seal."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_COUNT_MORE]
title = "Juliet lengthens the sunlit tally."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_SEEK]
title = "Romeo follows the star through the leaves."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_CAND_COUNT]
title = "Macbeth counts the answering starlight."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_CAND_MORE]
title = "Macbeth lengthens the answering starlight."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_COMPARE]
title = "The lovers weigh two sunlit measures."
pattern = "cross_character"
[scenes.LYRIC_EMPHASIS_MATCH]
title = "Romeo finds the star's faithful mate."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_RESUME]
title = "The sunlit seal closes around the star."
pattern = "bare_statement"
[scenes.LYRIC_EMPHASIS_FALLBACK]
title = "The unpaired star remains in the garden."
pattern = "bare_statement"
[scenes.LYRIC_EMPHASIS_REPLAY]
title = "Romeo restores the unpaired starlight."
pattern = "scene_of_character"

# Amendment A2 spare pool — do not use unless an extra generated scene is necessary.
[scenes.LYRIC_FIELD_RETRY]
title = "Romeo tries the unnamed field once more."
pattern = "scene_of_character"
[scenes.LYRIC_FIELD_HOLD_REPLAY]
title = "Horatio restores the unspoken field."
pattern = "scene_of_character"
[scenes.LYRIC_HTML_FALLBACK]
title = "The loose moonlit gate remains a gate."
pattern = "bare_statement"
[scenes.LYRIC_AUTOLINK_FALLBACK]
title = "The unmarked road returns to the field."
pattern = "bare_statement"
[scenes.LYRIC_LABEL_FALLBACK]
title = "The unnamed rose remains among the leaves."
pattern = "bare_statement"
[scenes.LYRIC_DEST_FALLBACK]
title = "The unclosed road rests beside the rose."
pattern = "bare_statement"
[scenes.LYRIC_TITLE_FALLBACK]
title = "The unclosed name rests beside the path."
pattern = "bare_statement"
[scenes.LYRIC_REGION_SPARE]
title = "The lovers leave the finished garden whole."
pattern = "cross_character"
[scenes.LYRIC_EMPHASIS_SPARE]
title = "The lonely star rests beneath the hedge."
pattern = "bare_statement"
[scenes.LYRIC_RESUME_SPARE]
title = "Romeo wakes the waiting held name."
pattern = "scene_of_character"
```

New recall keys for `src/literary.toml` (recall keys live in the pool of the
**speaker** who says the Recall line, per `lower.py::_roles`, matching
Amendment A1's convention). Add only the ones the IR actually needs, drawing
from this reserved list; do not invent others.

```toml
# src/literary.toml additions — Amendment A2
[characters.romeo.recall]  # merge into the existing table
field_first_glyph = "Recall the field's first glyph."
field_kept_mark = "Recall the field's kept mark."
held_name_returned = "Recall the held name's return."

[characters.juliet.recall]  # merge into the existing table
fields_first_glyph = "Recall the field's opening glyph."
fields_next_glyph = "Recall the field's next glyph."

[characters.hecate.recall]  # merge into the existing table
field_call_site = "Recall the field's chosen road."

[characters.macbeth.recall]  # merge into the existing table
answering_starlight = "Recall the answering starlight."

[characters.horatio.recall]  # merge into the existing table
held_label_glyph = "Recall the held label's glyph."
held_alt_glyph = "Recall the held portrait's glyph."
```

The same reuse rule as Amendment A1 applies: these registers and stacks are
freely clobbered once their phase is over, and every branch arrival into a
shared scene must leave the same stage pair. Task 4 prose must come only
from this pool (superseding the retired Task 4 pool above) plus Amendment
A1's Step 5 pool where genuinely shared (e.g. Task 4 must not redefine
`LYRIC_CODE_*`).

## Amendment A3 (2026-07-13): source-buffer assertion boundary and legal handoff

This amendment clears the Task 4 Step 1 assertion-boundary blocker. The Task 4 Step 1 negative
assertion incorrectly calls all values above the borrowed Puck prefix a
"source buffer" after Act III has halted. That is false by the existing
Act-III/Act-IV contract: `LYRIC_OPEN_REVERSE` deliberately seeds a fresh
`STREAM_END` on Puck, and `LYRIC_REVERSE_POP` deliberately transfers the
completed Juliet stream onto it. The non-empty region observed at exit is
therefore the required Act IV carrier, not requeued input. This also explains
why the assertion fails for the already-landed code-span fixtures at HEAD.

The accepted design is amended in
`docs/superpowers/specs/2026-07-12-span-architecture-spike-design.md` under
"Boundaries and invariants". That wording is binding for Task 4 and
supersedes Step 1's phrase "the source-buffer stack" and every assertion in
`test_act3_source_buffer_never_receives_generated_output*` that requires
Puck to be empty after `ACT3` returns.

### Binding replacement contract

The invariant has two separately observable parts:

1. **Pre-handoff emptiness.** At interpreter entry to
   `LYRIC_OPEN_REVERSE` — before that scene pushes the new output-carrier
   `STREAM_END` — Puck must equal the injected borrowed prefix exactly. Its
   original Act-II stream, every temporary source value, and every allowed
   raw-glyph requeue have been consumed. Juliet must hold the completed
   forward stream. This is the only valid point at which to assert that Puck
   is empty above the borrowed prefix.
2. **One-way provenance.** Inspect `src_ir.act3.ACT` as IR, not generated
   SPL. Before the reverse handoff, any `Push(PUCK, ...)` is limited to an
   original raw glyph held in Puck/Romeo/Horatio, `TEXT_END`, or a raw
   emphasis control delimiter. `Push(PUCK, val(JULIET))` is permitted exactly once as a
   scene shape, in `LYRIC_REVERSE_POP`; no other scene may transfer Juliet to
   Puck. This permits raw label/alt/emphasis requeue while forbidding
   generated HTML from becoming scan input. After the handoff, assert a
   structurally valid `PARA ... TEXT_END, STREAM_END` carrier rather than
   emptiness.

### Task 4 Step 2 required test-infrastructure change

Before adding a protected scanner scene, amend only verification code as part
of this unchecked step:

- In `scripts/splc/interpret.py`, extend the existing verification-only
  `InterpreterObserver` with `on_scene(label: str, state: InterpreterState)`
  and invoke it immediately after `sc = by_label[label]`, before that scene's
  first operation. Existing observers receive a no-op `on_scene` method.
  This changes neither the IR nor generated SPL.
- In `tests/test_act3_contracts.py`, replace both exit-state
  `source_buffer_never_receives_generated_output` assertions with one
  parameterized observer-based test over all five span stems. Give the
  observer the injected `_CarrierBoundary`; when `label ==
  "LYRIC_OPEN_REVERSE"`, snapshot `tuple(state.stacks[Char.PUCK])` and
  `tuple(state.stacks[Char.JULIET])`. Assert exactly one snapshot, assert its
  Puck stack equals `_BORROWED_PREFIX`, and assert the Juliet snapshot is
  non-empty and begins with the forward stream's `STREAM_END` floor. Continue
  the act, then retain the existing borrowed-prefix and decoded-carrier
  structural assertions at exit.
- Add a focused IR-shape test in that same file. Iterate `ACT3.scenes`, find
  `Push` operations targeting `PUCK`, and assert every occurrence with
  `expr == val(JULIET)` belongs to the singleton set
  `{("LYRIC_REVERSE_POP", <the output-carrier push>)}`. In the two handoff
  scenes, allow exactly `push(PUCK, const(tokens.STREAM_END))` in
  `LYRIC_OPEN_REVERSE` and `push(PUCK, val(JULIET))` in
  `LYRIC_REVERSE_POP`. Before that boundary, allow only `val(PUCK)`,
  `val(ROMEO)`, `val(HORATIO)`, `const(tokens.TEXT_END)`, and the
  raw emphasis delimiter constants. Assert no literal `<`, `>`, `&`, or
  any `val(JULIET)` transfer appears in a pre-handoff source scene. Use the
  IR node types (`Push`, `Val`, `Const`) rather than rendered prose.

Task 4's file list is correspondingly extended with
`scripts/splc/interpret.py` and `tests/test_act2_frame_floors.py`: the latter
is the existing observer implementation that must gain the no-op
`on_scene` method so the verification-only protocol remains type-complete.

No controlled title, Recall line, or production scene is introduced by this
amendment. Task 4 continues to use only Amendment A2's 41+10 literary pool;
the exact literary gate already named in Global Constraints remains required
after the subsequent Act III/TOML change.

### Revised Task 4 evidence expectation

Task 4 Step 3's first pytest command must include
`tests/test_splc_interpret.py`, because the observer hook is
verification-only interpreter behavior. Its expected result is PASS for the
new pre-handoff/provenance assertions, the protected-mode contracts, every
reviewed dump, and all existing spike structure tests. A failure showing
Puck non-empty only after `ACT3` returns is not evidence against this design;
the failure must instead be evaluated against the pre-handoff snapshot and
the explicit transfer allowlist above.

## Amendment A4 (2026-07-13): carrier-safe field/requeue choreography

The A2 shared idiom is retained, but its former "private resume sentinel"
description was not sufficient to implement safely: it left unclear how a
requeued label/alt/emphasis region differs from the paragraph's `TEXT_END`,
and it allowed the field duplicate/continuation state to collide with Romeo,
Hecate, or Puck. The validated replacement is now part of the accepted design
under [Carrier-safe protected-region amendment](../specs/2026-07-12-span-architecture-spike-design.md#carrier-safe-protected-region-amendment-2026-07-13).
It is binding for Step 2 and supersedes only A2's resume-sentinel/register
wording; A2's 41+10 controlled literary pool remains the sole title source.

### Task 4 Step 2 additional required tests (before production IR changes)

Extend the A3 observer work before adding a protected scene:

- Add `on_scene` to `InterpreterObserver` as A3 specifies, then create a
  recording observer in `tests/test_act3_contracts.py` that records
  `(label, tuple(PUCK), tuple(JULIET), HECATE, MACBETH)` on entry.
- Add parameterized tests for `inline_html_and_autolink`,
  `links_images_protected`, and `overlapping_emphasis` that, once the scanner
  exists, require every Puck-private `TEXT_END` to enter
  `LYRIC_RESUME_DISPATCH`, require the unique real `TEXT_END` to enter
  `TRAVERSE_COPY_TERMINATOR`, and require no observed Puck stack above the
  borrowed prefix at `LYRIC_OPEN_REVERSE`.
- Add an IR-shape test which permits pre-handoff Puck pushes only from the
  A4 allowlist, asserts one `Push(PUCK, val(JULIET))` in
  `LYRIC_REVERSE_POP`, and asserts every `LYRIC_FIELD_OPEN` has a matching
  Romeo `STREAM_END` floor plus a `LYRIC_FIELD_DRAIN_CLOSE` path.
- Add a focused no-underflow regression covering each of the three protected
  stems with `STEP_LIMIT = 200_000`; it must fail on the old WIP shape with
  `StackUnderflow`/unexpected text-end routing and pass only after the A4
  scene choreography is present.

Run the red gate before production edits:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q
```

Expected before Step 2 production scenes: the newly added carrier tests fail
only because the named A4 scenes do not exist; existing Task 1–3 green tests
remain green. After implementation, the same command passes, followed by the
full Task 4 evidence commands already named in Steps 3–5.

## Amendment A5 (2026-07-13): quarantine the retired WIP and reconstruct through the carrier gate

The active blocker is resolved by a sequencing correction, not another scene
pool. The uncommitted Task 4 attempt adds the retired per-feature families
(`LYRIC_HTML_TAG`/`LYRIC_LABEL_SCAN`/`LYRIC_DESTINATION_*`/
`LYRIC_EMPHASIS_EMIT_*`) and therefore cannot become carrier-safe through
ad-hoc additions. Its observed failures are diagnostic: `TEXT_END` escapes
the paragraph carrier, the binding shared A4 labels are absent, and
`LYRIC_EMPHASIS_EMIT_CLOSE` falls off after Hecate was reused as a body-glyph
register. Preserve the WIP unchanged as handoff evidence, but do not extend
or commit any production portion of it.

The accepted design gains the binding
[A4 reconstruction sequence](../specs/2026-07-12-span-architecture-spike-design.md#a4-reconstruction-sequence-2026-07-13).
It supersedes Task 4 Step 2's former implication that the old scene families
could be incrementally refactored. Amendment A2 remains the sole controlled
surface reservation; A5 allocates no titles, Recall lines, token codes, or
new registers.

### Step 2 mandatory execution order

Before production IR is edited, retain the current worktree WIP without
mutation (for example, use an isolated worktree at the committed Task 3
baseline for the replacement). Do not use `git restore`, `reset`, or a
destructive cleanup against the handoff worktree. In that isolated replacement
worktree:

1. Commit the A3/A4 verification-only observer protocol first:
   `InterpreterObserver.on_scene`, the compatible no-op observer method, and
   the observer/IR-shape/no-underflow tests. The red result at this point may
   be the absent A4 labels and absent resume traversal only; it must not show
   a structural-carrier decode error, `StackUnderflow`, or scene fall-through
   in any Task 1–3 probe.
2. Reconstruct from the committed Task 3 `src_ir/act3.py`, not from the WIP.
   Add the shared field scenes as one coherent pipeline before connecting
   `<`, `[`, `![`, `*`, or `_` dispatch. Every `LYRIC_FIELD_OPEN` creates a
   Romeo `STREAM_END` floor, every success reaches
   `LYRIC_FIELD_DRAIN_CLOSE`, and every fallback drains that same floor. Add
   only the matching A2 TOML entries and recall keys actually used.
3. Route protected modes in dependency order: opaque tag and autolink;
   link/image destination plus label/alt requeue; then emphasis/strong/triple
   emphasis requeue. A nested raw region always pushes its Lady-Macbeth
   `[STREAM_END, saved Hecate code, saved Macbeth value]` record before its
   private Puck `TEXT_END`. `LYRIC_RESUME_DISPATCH` alone restores that record
   and emits the caller's close. `MACBETH` never becomes a field-glyph value.
4. Stop immediately if the focused gate exposes a second real paragraph
   terminator, a leaked `TEXT_END`, a pop below a private floor, or a missing
   A2 working label. Record a new `BLOCK[plan]` with the exact first failed
   invariant; do not consume a spare title to mask the failure.

### Replacement focused evidence gate

At the first production checkpoint, run exactly:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q
```

Expected: all tests pass, including structural decoding for every span probe;
the three protected stems observe one `TRAVERSE_COPY_TERMINATOR`, each private
Puck `TEXT_END` reaches `LYRIC_RESUME_DISPATCH`, every `LYRIC_FIELD_OPEN` has
a Romeo floor and drain-close path, and no protected stem underflows or falls
off a scene. A rendered-output mismatch after those facts hold is a normal
Task 4 follow-up; any carrier failure is a plan blocker, not permission for
ad-hoc scene additions.

## Amendment A6 (2026-07-13): reset continuation construction and make A4 event-exact

The second Step 2 attempt fails the mandatory observer gate: Lady Macbeth
underflows in `LYRIC_RESUME_RESTORE_MACBETH` for link/image and emphasis, and
the broad pre-handoff observer newly underflows Puck on the already-shipped
`escapes_and_overlap` probe. The accepted design's [A6 continuation-record
reset and event-order gate](../specs/2026-07-12-span-architecture-spike-design.md#a6-continuation-record-reset-and-event-order-gate-2026-07-13)
is binding. It supersedes any Step 2 wording that permits incremental repair
of the current worktree graph.

1. Preserve the handoff worktree unchanged. In an isolated worktree begin
   from committed Task 3 `src_ir/act3.py`; copy no uncommitted production
   `LYRIC_*` scene or flow from this failed attempt.
2. Recreate the A3/A4 observer against that baseline and extend it to record
   Puck-pop event order. The ordinary terminator must remain
   `LYRIC_POP_GLYPH -> TRAVERSE_COPY_TERMINATOR`, and all Task 1--3 probes,
   especially `escapes_and_overlap`, must have no underflow before a protected
   opener is connected.
3. Add the A2 shared-field skeleton and A4 labels as a carrier-complete unit.
   Every requeue follows A6's exact Lady-Macbeth push/pop order, freezes the
   close code in Prospero, and no close scene pops Lady Macbeth. Prove the
   focused gate before connecting any protected opener.
4. Connect opaque tag/autolink, link/image requeue, then emphasis requeue.
   Re-run the focused gate after each family. Do not add a recovery scene,
   consume an A2 spare, or change real-terminator flow to mask a carrier
   failure.

A6 allocates no controlled prose, Recall key, token code, holder, or sentinel:
only Amendment A2's 41 working plus 10 spare labels, and genuinely shared A1
labels, remain available.

Run exactly:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q
```

Expected: PASS. Event order proves every private terminator enters
`LYRIC_RESUME_DISPATCH`, exactly one real terminator enters
`TRAVERSE_COPY_TERMINATOR`, every resume consumes one record, and Task 1--3
paths stay no-underflow. Any other result is `BLOCK[plan]`.

## Amendment A7 (2026-07-13): move field tags to Prospero and legalize A6 restores

The accepted design's [A7 holder and adapter amendment](../specs/2026-07-12-span-architecture-spike-design.md#a7-field-tag-holder-and-two-character-restore-adapters-2026-07-13)
supersedes A2/A4's claim that Hecate retains a field tag and A6's no-spare
rule. It is binding for Task 4 Step 2.

1. A caller sets Hecate to its `FIELD_*` code and enters the already-reserved
   `(HECATE, PROSPERO)` `LYRIC_FIELD_RETRY` adapter. It copies the tag to
   Prospero before `LYRIC_FIELD_OPEN`; all field scan/output/close branches
   inspect off-stage Prospero. Hecate may then be popped as the field glyph
   register. Once `LYRIC_FIELD_DRAIN_CLOSE` selects its continuation, the
   field tag is dead, so the existing resume dispatcher may overwrite
   Prospero with `RESUME_*` to freeze the close choice.
2. Add only the six exact A7 adapters:
   `LYRIC_RESUME_POP_MACBETH`, `LYRIC_RESUME_RESTORE_MACBETH`,
   `LYRIC_RESUME_POP_HECATE`, `LYRIC_RESUME_RESTORE_HECATE`,
   `LYRIC_RESUME_VERIFY_FLOOR`, and `LYRIC_RESUME_FLOOR_FAIL`. Use their
   exact pair/operation graph from A7. They consume six A2 spare-capacity
   entries; with `LYRIC_FIELD_RETRY`, seven of ten A2 spares are allocated.
   Add the ready-to-paste A7 TOML entries only with their corresponding IR
   scenes; the remaining three spares are not permission to repair a carrier
   fault.
3. Extend the A6 observer to require the A7 label order after every private
   terminator, exactly three Lady-Macbeth pops, no floor-failure scene, and a
   close selected from frozen Prospero. The real terminator bypasses this
   graph and no close scene pops Lady Macbeth.

Before connecting a protected opener, run exactly:

```bash
uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q
```

Expected: PASS for Task 1--3 paths and the A7 graph gate, with no underflow,
fall-through, leaked `TEXT_END`, or malformed record. After any Act III/TOML
change, run the exact Global Constraints literary command too.

## Amendment A8 (2026-07-13): source-end restore and ordered raw requeue

The A7 reconstruction diagnostic (preserved unchanged in stash
`Task 4 Step 2 A7 reconstruction blocked by private Puck floor underflow`)
underflows Puck in `LYRIC_FIELD_SCAN` for `links_images_protected` and in
`LYRIC_EMPHASIS_SEEK` for `overlapping_emphasis`.  The accepted design's
[A8 correction](../specs/2026-07-12-span-architecture-spike-design.md#a8-source-end-and-requeue-drainer-correction-2026-07-13)
is now binding for Task 4 Step 2 and supersedes A2/A4's ambiguous
unterminated/requeue routes.

1. Reconstruct from committed Task 3; do not repair or copy the diagnostic
   WIP.  A direct Puck pop in a scanner branches on real `TEXT_END` before
   any other action.  Its source-end route restores that same terminator,
   drains only its own private capture literally in source order, and returns
   to `LYRIC_POP_GLYPH` without another Puck pop.  It never targets
   `LYRIC_RESUME_FLOOR_FAIL`.
2. Implement the exact A8 field/title protocol: destination owns its closing
   `)`, title owns its matching quote and verifies one following `)`, and
   malformed/missing close routes use the A8 literal unwind.  Do not capture
   the final `)` or treat it as a field glyph.
3. Replace all label/alt/emphasis requeue loops with A8's one
   `LYRIC_REQUEUE_OPEN`/`LYRIC_REQUEUE_DRAIN` family.  The order is binding:
   Lady-Macbeth record; Hecate `RESUME_*`; Puck private `TEXT_END`; then
   pop Horatio and push each non-floor raw glyph to Puck.  The Horatio floor
   is consumed, not transferred.  Triple emphasis pushes synthetic close,
   drains the body, then pushes synthetic open, giving raw source order
   `* body * TEXT_END`.
4. Reserve only A8's 10 working and four spare titles from the accepted
   design.  The A2 spare labels consumed in the failed diagnostic attempt are
   retired; no implementation agent may reuse them.  Add the exact A8 TOML
   entries with their IR scenes and run the plan's Global Constraints literary
   gate after each Act III/TOML edit.
5. Before connecting rendering refinements, extend the observer so it proves
   a scanner-owned real terminator is restored and next reaches
   `TRAVERSE_COPY_TERMINATOR`, every private terminator enters the A7
   restore sequence, and both A8 source-end scenes make no further Puck pop.
   Run exactly:

   ```bash
   uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q
   ```

   Expected: PASS with no Puck/Lady-Macbeth underflow, no scene fall-through,
   exactly one real terminator per protected probe, and no
   `LYRIC_RESUME_FLOOR_FAIL`.  Any failure is `BLOCK[plan]`; it does not
   authorize another recovery scene or title.

---

## Amendment A10 (2026-07-14): image-title ordering and nested-floor correction

The A2 shared field pipeline must not emit an image title when it captures it:
doing so produces `src, title, alt`, while Markdown.pl requires `src, alt,
title`.  The accepted design's [A10 correction](../specs/2026-07-12-span-architecture-spike-design.md#a10-image-title-ordering-and-nested-floor-correction-2026-07-14)
is binding for Task 4 Step 2.

- `FIELD_IMAGE_TITLE` captures raw bytes onto Romeo above its own private
  `STREAM_END`, consumes the source closing syntax, and skips the normal
  `LYRIC_FIELD_RETRY` drain until the alt has been requeued and scanned.
- Use `RESUME_IMAGE_TITLE=12` for that alt requeue.  The complete A9 adapter
  freezes it in Prospero, then dispatches to the sole new working scene
  `LYRIC_IMAGE_TITLE_CLOSE`.  That scene alone is authorized to set Hecate
  back to `FIELD_IMAGE_TITLE` and enter the existing shared field reverse /
  entity / drain family; its field-close branch emits `" />`.
- The title Romeo floor must remain untouched while the Horatio/Puck alt
  requeue runs.  This is legal and was confirmed by the focused IR interpreter
  probe recorded in the accepted design.  Add the specified
  `test_image_title_floor_survives_alt_requeue` regression before production
  IR changes and extend the existing image observer assertions to witness
  selector `12`, `LYRIC_IMAGE_TITLE_CLOSE`, no early Romeo pop, and one final
  image-title drain.
- Reserve only the one A10 working label and four A10 spares quoted in the
  accepted design.  The spares are not implementation authority.  Run the
  exact Global Constraints literary gate after each Act III/TOML change.

This amendment leaves the original A2 emphasis family unchanged.  Implement
that self-contained family first: `PROSPERO` holds opener code `42`/`95`,
`HECATE` the opener run length, `MACBETH` the candidate/matched run length,
and `HORATIO` raw body bytes requeued only via A8's shared requeue family.
The reserved ten-label emphasis family must fold seek initialization and the
count loop into `LYRIC_EMPHASIS_OPEN` / `LYRIC_EMPHASIS_COUNT_MORE` rather
than inventing a label; if that cannot be expressed, stop with `BLOCK[plan]`.
This emphasis-first checkpoint must make `escapes_and_overlap` and
`overlapping_emphasis` green before HTML/link/image work is connected.

## Amendment A11 (2026-07-14): emphasis candidate lookahead ownership

The first A9/A10 focused-gate failure is an emphasis comparator ownership
bug, specified in the accepted design's [A11 amendment](../specs/2026-07-12-span-architecture-spike-design.md#a11-emphasis-candidate-lookahead-ownership-2026-07-14).
The preserved diagnostic consumes the lookahead after an unmatched candidate
run. At the real terminator it routes that `TEXT_END` through fallback, then
`LYRIC_EMPHASIS_SEEK` pops an empty Puck stack. Before any HTML/link/image
work, add A11's two observer tests and make the emphasis-first checkpoint
green.

In `LYRIC_EMPHASIS_COMPARE`, distinguish `TEXT_END` from a non-star
lookahead before fallback: the former restores exactly one real terminator and
enters the shared literal unwind without another source pop; the latter is
held on Horatio before candidate-star replay. Add only
`LYRIC_EMPHASIS_CAND_KEEP_LOOKAHEAD` and
`LYRIC_EMPHASIS_CAND_SOURCE_END`, with exactly the A11 TOML entries. Refactor
the existing source-end entry so it owns literal-unwind setup but does not
duplicate a caller-restored terminator. This correction must not alter A8's
raw requeue drain, A9's Lady-Macbeth record, A10's image-title flow, or use
Juliet/Romeo as a fallback carrier. The four A11 spares are not implementation
authority.

Run this exact gate before expanding protected modes:

```bash
uv run pytest tests/test_act3_contracts.py -q -k \
  "emphasis_candidate_keeps_nonmatching_lookahead or emphasis_candidate_restores_real_text_end_once or protected_modes_do_not_underflow or text_end_event_order_is_carrier_safe"
```

Expected: all selected cases pass, especially `escapes_and_overlap`, with no
`StackUnderflow`, no duplicate `TEXT_END`, and exactly one real terminator
route. Then run the Global Constraints exact literary gate. A failure remains
a `BLOCK[plan]`; it does not authorize a recovery pop or any other new scene.

### Task 1: Commit the span-spike corpus and reviewed expected output

**Files:**
- Create: `tests/fixtures/architecture_spikes/spans/variable_code_spans.text`
- Create: `tests/fixtures/architecture_spikes/spans/escapes_and_overlap.text`
- Create: `tests/fixtures/architecture_spikes/spans/inline_html_and_autolink.text`
- Create: `tests/fixtures/architecture_spikes/spans/links_images_protected.text`
- Create: `tests/fixtures/architecture_spikes/spans/overlapping_emphasis.text`
- Create: `tests/fixtures/architecture_spikes/spans/*.expected`
- Modify: `tests/test_architecture_spikes.py`

**Consumes:** The accepted design's probe table and local `~/markdown/Markdown.pl`.

**Produces:** Five permanent, byte-exact source/output contracts that fail against the pre-spike production runtime without changing it.

- [x] **Step 1: Add the exact source fixtures.**

  Create the five `.text` files with precisely these bytes (each final newline is significant):

  ```text
  variable_code_spans: `` a ` b `` and `x & <y>`\n
  escapes_and_overlap: \*literal* and \[bracket\] \`tick\` and ***both***\n
  inline_html_and_autolink: <span>*raw*</span> and <http://example.com/a?x=1&y=2>\n
  links_images_protected: [a *b*](http://e/x_(y) "t") and ![c *d*](img.png "i")\n
  overlapping_emphasis: ***both*** and **outer *inner* outer**\n
  ```

- [x] **Step 2: Generate and review oracle expectations.**

  For every `.text`, run `perl ~/markdown/Markdown.pl < <fixture> > <fixture>.expected`; inspect the resulting bytes. In particular, assert the expected output contains `<code>a \` b</code>`, `<code>x &amp; &lt;y&gt;</code>`, literal `*literal*`, `<span><em>raw</em></span>`, a once-encoded autolink query ampersand, `<img src="img.png" alt="c <em>d</em>" title="i" />`, and `<strong><em>both</em></strong>`.

- [x] **Step 3: Add direct probe tests.**

  In `tests/test_architecture_spikes.py`, add `SPAN_FIXTURES`, `_span_cases()`, and a parametrized test that loads each `.text` and `.expected`, runs both `./shakedown` and `perl ~/markdown/Markdown.pl`, and requires both outputs equal the checked-in expected bytes. Reuse `_first_diff()` so a mismatch reports its byte index. Do not route this assertion through mdtest normalization.

- [x] **Step 4: Run the red gate.**

  Run: `uv run pytest tests/test_architecture_spikes.py -k span -q`  
  Expected: FAIL for all new span cases on the current Act III behavior; existing list and nested-block spike cases remain PASS.

- [x] **Step 5: Commit and push the corpus.**

  Run: `git add tests/fixtures/architecture_spikes/spans tests/test_architecture_spikes.py && git commit -m "test: add span architecture spike corpus"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding.

### Task 2: Scaffold the buffered carrier contract before production scanning

**Files:**
- Create: `tests/test_act3_contracts.py`

**Consumes:** Task 1 fixture names; `ACT1`, `ACT2`, `ACT3`, `run_act`, `decode_stream`, and `validate_stream`.

**Produces:** Executable proof scaffolding that Act III retains exactly one `STREAM_END`, exposes a valid block stream, and provides a stable comparison point for the private scan floor. Task 4 adds reviewed final dumps only after the implementation exists.

- [x] **Step 1: Write interpreter helpers and failing contracts.**

  Add `_run_to_act3(stem: str) -> InterpreterState` that feeds the fixture text through `ACT1`, `ACT2`, and `ACT3` with `STEP_LIMIT = 200_000`; add `_carrier_stream(state) -> list[int]` that pops Puck through the sole terminal `STREAM_END`. Assert `stream.count(tokens.STREAM_END) == 1`, `decode_stream(stream[:-1])` succeeds, and `validate_stream(...)` accepts it. Add a parameterized test that records the pre-scan paragraph stream and proves non-text structural tokens/payloads remain unchanged across Act III; keep the expected rendered text deliberately failing until Task 3.

- [x] **Step 2: Run the contract tests to verify failure.**

  Run: `uv run pytest tests/test_act3_contracts.py -q`  
  Expected: structural-prefix assertions PASS, while expected rendered-region assertions FAIL because current Act III cannot produce the protected-region contracts.

- [x] **Step 3: Assert the floor/prefix boundary.**

  Instrument only the IR-interpreter-facing test helper (not production SPL) to retain the carrier prefix before calling `ACT3`; assert that the prefix beneath the planned private floor is byte-for-byte equal after the act exits. Assert the final stream carries no leaked `ITEM_START` marker and no extra `STREAM_END`.

- [x] **Step 4: Run the structural evidence.**

  Run: `uv run pytest tests/test_act3_contracts.py tests/test_token_decode.py tests/test_token_structure.py -q`  
  Expected: prefix/stream-shape assertions PASS; intentionally expected span-output assertions remain red until Task 3.

  Evidence (2026-07-12): `53 passed, 5 failed`. The five failures are exactly the intentionally-red `test_act3_does_not_yet_render_expected_span_html` cases (one per span probe); all prefix, stream-shape, floor-boundary, and decode/structure assertions pass.

- [x] **Step 5: Commit and push the carrier contract.**

  Run: `git add tests/test_act3_contracts.py && git commit -m "test: scaffold span carrier contracts"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding.

  Evidence (2026-07-12): the carrier contract (`tests/test_act3_contracts.py`) is committed and pushed to `origin/main` across commits `d47ed74`→`6e5c1a5`. Re-run confirms the recorded Task 2 state: `10 passed, 5 failed`, where the five failures are exactly the intentionally-red `test_act3_does_not_yet_render_expected_span_html` cases (one per span probe) held red until Task 3.

### Task 3: Implement the one-way buffered scan for code spans and escapes

**Files:**
- Modify: `src_ir/act3.py`
- Modify: `src/30-act3-literary.toml`
- Regenerate: `src/30-act3-span.spl`
- Regenerate: `shakedown.spl`

**Consumes:** Task 1's red corpus, Task 2's contracts, and only the active/spare Act III prose above.

**Produces:** A floor-bounded source buffer that supports variable-length code spans and escaped punctuation without feeding generated output back into the scan; Amps remains byte-identical.

- [x] **Step 1: Add the minimum IR tests before changing the scanner.**

  In `tests/test_act3_contracts.py`, assert `variable_code_spans` has exactly two `<code>` regions with `<code>a \` b</code>` and `<code>x &amp; &lt;y&gt;</code>` in its decoded paragraph text; assert `escapes_and_overlap` retains literal `*literal*`, `[bracket]`, and `` `tick` ``. Assert that the carrier below the temporary scan-floor sentinel matches the pre-scan prefix exactly.

  Evidence (2026-07-12): added `test_act3_renders_variable_length_code_spans`, `test_act3_preserves_escaped_and_literal_span_punctuation`, and the parameterized `test_act3_scan_floor_matches_pre_scan_prefix` over `variable_code_spans`/`escapes_and_overlap`.

- [x] **Step 2: Run the focused red gate.**

  Run: `uv run pytest tests/test_act3_contracts.py tests/test_architecture_spikes.py -k 'span or act3' -q`  
  Expected: FAIL because the existing `LYRIC_POP_GLYPH` path has no variable-run or escape buffering.

  Evidence (2026-07-12): `12 failed, 12 passed, 14 deselected`. The two new rendering assertions fail red as intended (alongside the pre-existing span-probe reds); the two new scan-floor invariant cases pass, keeping the borrowed-prefix contract green before the scanner lands.

- [x] **Step 3: Add the floor-bounded paragraph drain and ordinary-glyph loop.**

  In `src_ir/act3.py`, preserve `_traverse_dispatch()` and route
  `TRAVERSE_OPEN_TEXT` through `LYRIC_BUFFER_OPEN`, `LYRIC_BUFFER_DRAIN`,
  `LYRIC_BUFFER_KEEP`, `LYRIC_BUFFER_DRAIN_CLOSE`, `LYRIC_SCAN_NEXT`,
  `LYRIC_ORDINARY_GLYPH`, `LYRIC_BUFFER_ENTITY_AMP`,
  `LYRIC_BUFFER_ENTITY_ANGLE`, `LYRIC_BUFFER_UNWIND`,
  `LYRIC_BUFFER_CLOSE`, and `LYRIC_BUFFER_RETURN` as needed. Push exactly one
  private floor above the borrowed carrier prefix, drain exactly one paragraph
  through `TEXT_END` into a source buffer, and emit ordinary glyphs directly
  to Juliet with amp/angle encoding. Consume the private floor exactly once,
  then write one `TEXT_END` and resume the existing structural-copy path. Do
  not consume structural codes or payloads in this loop, and do not return
  emitted output to the source buffer.

  Evidence (2026-07-13): routed `TRAVERSE_OPEN_TEXT` through the buffered
  drain/unwind/scan loop, using a temporary `STREAM_END` floor on Puck and a
  private Romeo source buffer. Regeneration plus the Step 3 boundary gate
  passed: `uv run pytest tests/test_splc_generated_fragments.py
  tests/test_act3_contracts.py::test_act3_preserves_span_fixture_structural_stream
  tests/test_act3_contracts.py::test_act3_preserves_borrowed_carrier_prefix_and_cleans_sentinels
  tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix
  -q` => `14 passed`; `uv run pytest tests/test_literary_compliance.py
  tests/test_literary_toml_schema.py tests/test_assemble.py
  tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q` =>
  `1 passed, 208 deselected`.

- [x] **Step 4: Regenerate and prove the buffer boundary before delimiter work.**

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  uv run pytest \
    tests/test_splc_generated_fragments.py \
    tests/test_act3_contracts.py::test_act3_preserves_span_fixture_structural_stream \
    tests/test_act3_contracts.py::test_act3_preserves_borrowed_carrier_prefix_and_cleans_sentinels \
    tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix \
    -q
  uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
  ```

  Expected: generated artifacts are fresh; borrowed-prefix, stream-shape, and
  scan-floor assertions pass; the code-span and escape rendering tests can
  remain red; Amps remains byte-identical.

  Evidence (2026-07-13): regenerated the generated fragments with `uv run
  python -m scripts.splc` and rebuilt `shakedown.spl` with `uv run python
  scripts/assemble.py`. The structural proof gate passed unchanged:
  `uv run pytest tests/test_splc_generated_fragments.py
  tests/test_act3_contracts.py::test_act3_preserves_span_fixture_structural_stream
  tests/test_act3_contracts.py::test_act3_preserves_borrowed_carrier_prefix_and_cleans_sentinels
  tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix
  -q` => `14 passed`; the literary/parity gate also remained green:
  `uv run pytest tests/test_literary_compliance.py
  tests/test_literary_toml_schema.py tests/test_assemble.py
  tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q`
  => `1 passed, 208 deselected`.

- [x] **Step 5: Add maximal backtick-run matching and byte-exact replay (per Amendment A1).**

  Implement the Amendment A1 scene table exactly: add the
  `branch(eq(val(PUCK), _k(96)), then="LYRIC_CODE_RUN")` entry hook to
  `LYRIC_POP_GLYPH` and the thirty `LYRIC_CODE_*` scenes with the listed ops,
  pairs, anchors, and companions. Use HECATE's value for the opener run
  length, MACBETH's value for the candidate run length, ROMEO's stack (above
  a private `STREAM_END` sentinel) for speculative source, and HECATE's stack
  (above a private `STREAM_END` sentinel) for the reversed content buffer —
  no scene stages more than two characters, and run-length tests use
  off-stage value references. Treat an opener as a maximal run, accept only
  the first later maximal run of the same length, keep runs of other lengths
  as code content, strip all leading and trailing spaces/tabs from content
  (Amendment A1 oracle correction), encode `&`, `<`, and `>` only in code
  content, and write literal `<code>` boundaries directly to Juliet. An
  unmatched opener and every speculative source glyph must replay
  byte-for-byte in source order. Keep all output out of the source buffer.
  Add the Amendment A1 scene titles (only those actually used) to
  `src/30-act3-literary.toml` and the Amendment A1 recall keys to
  `src/literary.toml`, both verbatim from the reserved pools.

  Evidence (2026-07-13): implemented the entry hook and the thirty
  `LYRIC_CODE_*` scenes in `src_ir/act3.py` exactly per the Amendment A1
  table (opener/candidate counting into HECATE/MACBETH, off-stage
  `eq(val(MACBETH), val(HECATE))` compare, ROMEO/HECATE sentinel-bounded
  buffers, tail-trim before reverse, head-trim plus amp/angle encoding on
  emit, byte-exact fallback replay). Added the reserved scene titles to
  `src/30-act3-literary.toml` and the reserved recall keys to
  `src/literary.toml`, both used verbatim. Regenerated fragments with
  `uv run python -m scripts.splc` and `uv run python scripts/assemble.py`:
  no drift beyond the intended scanner change. Gate:
  `uv run pytest tests/test_splc_generated_fragments.py -q` => `2 passed`;
  `uv run pytest tests/test_act3_contracts.py::test_act3_renders_variable_length_code_spans tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix 'tests/test_architecture_spikes.py::test_span_architecture_spike_matches_checked_in_oracle_bytes[variable_code_spans]' -q`
  => `4 passed`; `uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q`
  => `1 passed, 208 deselected`. Full `tests/test_act3_contracts.py
  tests/test_architecture_spikes.py -q` run: `9 failed, 29 passed` — the
  nine failures are exactly the still-red escape/HTML/autolink/link/image/
  overlapping-emphasis probes reserved for Steps 7 and Task 4; no
  regression on the code-span or structural/floor assertions.

- [x] **Step 6: Regenerate and prove variable code spans.**

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  uv run pytest \
    tests/test_splc_generated_fragments.py \
    tests/test_act3_contracts.py::test_act3_renders_variable_length_code_spans \
    tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix \
    'tests/test_architecture_spikes.py::test_span_architecture_spike_matches_checked_in_oracle_bytes[variable_code_spans]' \
    -q
  uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
  ```

  Expected: both code regions and the byte-exact `variable_code_spans` probe
  pass; the scan-floor invariant and Amps remain green; escape rendering may
  remain red until Step 7.

  Evidence (2026-07-13): regenerated fragments with `uv run python -m
  scripts.splc` and rebuilt `shakedown.spl` with `uv run python
  scripts/assemble.py`; `git status --short` showed no drift after
  regeneration (Step 5's committed generated fragments were already fresh).
  Gate: `uv run pytest tests/test_splc_generated_fragments.py
  tests/test_act3_contracts.py::test_act3_renders_variable_length_code_spans
  tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix
  'tests/test_architecture_spikes.py::test_span_architecture_spike_matches_checked_in_oracle_bytes[variable_code_spans]'
  -q` => `6 passed`; `uv run pytest tests/test_literary_compliance.py
  tests/test_literary_toml_schema.py tests/test_assemble.py
  tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q` =>
  `1 passed, 208 deselected`.

- [x] **Step 7: Add escaped-glyph consumption and the unmatched-opener edge cases.**

  Added `LYRIC_ESCAPE_TEST`, `LYRIC_ESCAPE_GLYPH`, `LYRIC_ESCAPE_LITERAL`, and
  `LYRIC_ESCAPE_FALLBACK` to consume a backslash plus one Markdown-escapable
  punctuation glyph as one literal output glyph. For a non-escapable next
  glyph, `LYRIC_ESCAPE_LITERAL` preserves the backslash literally then emits
  the glyph as-is; for a trailing backslash at `TEXT_END`, `LYRIC_ESCAPE_FALLBACK`
  emits the backslash literally and goes straight to `TRAVERSE_COPY_TERMINATOR`
  (the terminator constant is pushed fresh there, never the already-consumed
  popped value). The escapable set matches Markdown.pl's `_EscapeSpecialChars`
  table exactly: `\ \` * _ { } [ ] ( ) > # + - . !` (16 glyphs). The backslash
  branch in `LYRIC_POP_GLYPH` runs before the backtick branch so an escaped
  backtick never opens a code span. The unmatched-backtick fallback (Step 5)
  is untouched — no new floor/sentinel was added, and it still replays through
  the same source-replay path.

  Evidence (2026-07-13): added the entry-hook branch and four `LYRIC_ESCAPE_*`
  scenes to `src_ir/act3.py`, added their titles to `src/30-act3-literary.toml`
  (all four taken verbatim from the Task 3 reserved/spare pool — no new prose
  invented) and the `hedges_kept_glyph` recall key (Task 3 romeo spare) to
  `src/literary.toml`. Regenerated with `uv run python -m scripts.splc` and
  `uv run python scripts/assemble.py`; no unexpected drift. Gate:
  `uv run pytest tests/test_splc_generated_fragments.py
  tests/test_act3_contracts.py::test_act3_preserves_escaped_and_literal_span_punctuation
  tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix
  tests/test_act3_contracts.py::test_act3_preserves_borrowed_carrier_prefix_and_cleans_sentinels
  'tests/test_architecture_spikes.py::test_span_architecture_spike_matches_checked_in_oracle_bytes[variable_code_spans]'
  -q` => `11 passed`; `uv run pytest tests/test_literary_compliance.py
  tests/test_literary_toml_schema.py tests/test_assemble.py
  tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q` =>
  `1 passed, 208 deselected`. Full `tests/test_act3_contracts.py
  tests/test_architecture_spikes.py -q` run: `8 failed, 30 passed` — the eight
  failures are exactly the still-red HTML/autolink/link/image/overlapping-
  emphasis probes reserved for Task 4; no regression on code-span, escape, or
  structural/floor assertions.

- [x] **Step 8: Regenerate and prove code, escapes, and fallback safety.**

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  uv run pytest \
    tests/test_splc_generated_fragments.py \
    tests/test_act3_contracts.py::test_act3_preserves_escaped_and_literal_span_punctuation \
    tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix \
    tests/test_act3_contracts.py::test_act3_preserves_borrowed_carrier_prefix_and_cleans_sentinels \
    'tests/test_architecture_spikes.py::test_span_architecture_spike_matches_checked_in_oracle_bytes[variable_code_spans]' \
    -q
  uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
  ```

  Expected: code-span and escape-specific contracts pass; all floor/prefix
  assertions and Amps remain green. Whole-fixture parity for
  `escapes_and_overlap`, HTML/link/image, and overlapping emphasis remains
  Task 4 work.

- [x] **Step 9: Commit and push the scanner foundation.**

  Evidence (2026-07-13): `uv run pytest tests/test_splc_generated_fragments.py tests/test_act3_contracts.py::test_act3_preserves_escaped_and_literal_span_punctuation tests/test_act3_contracts.py::test_act3_scan_floor_matches_pre_scan_prefix tests/test_act3_contracts.py::test_act3_preserves_borrowed_carrier_prefix_and_cleans_sentinels 'tests/test_architecture_spikes.py::test_span_architecture_spike_matches_checked_in_oracle_bytes[variable_code_spans]' -q` => `11 passed`; `uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q` => `1 passed, 208 deselected`. Files committed in `2695819` (`feat: add maximal backtick-run code-span scanner`) and `de32b28` (`feat: add backslash-escape consumption to span scanner`). `git push` succeeded.

### Task 4: Add protected HTML/link/image regions and strong-then-emphasis output

**Files:**
- Modify: `src_ir/act3.py`
- Modify: `src/30-act3-literary.toml`
- Modify: `tests/test_act3_contracts.py`
- Create: `tests/fixtures/token_stream/spans/*.dump`
- Modify: `tests/test_token_dump.py`
- Regenerate: `src/30-act3-span.spl`
- Regenerate: `shakedown.spl`

**Consumes:** Task 3 scanner and Task 1's remaining probe contracts.

**Produces:** Protected tags/destinations/titles, child label/alt scans, and representative nested strong/emphasis output under the one-way scan invariant.

- [x] **Step 1: Extend failing contracts for every protected mode.**

  Add assertions that the decoded output for `inline_html_and_autolink` contains literal `<span><em>raw</em></span>` and exactly one `&amp;` in the autolink query; `links_images_protected` contains `<a href="http://e/x_(y)" title="t">a <em>b</em></a>` and `<img src="img.png" alt="c <em>d</em>" title="i" />`; and `overlapping_emphasis` contains both exact expected strong/em nesting sequences. Add a negative assertion that no generated output is placed back on the source-buffer stack.

  Evidence (2026-07-13): the four Task 4 contract tests (`test_act3_renders_inline_html_and_autolink`, `test_act3_renders_links_images_protected`, `test_act3_renders_overlapping_emphasis`, and the parameterized `test_act3_source_buffer_never_receives_generated_output`/`_code_spans` negative assertion) were already committed in `8c69d89`/`6709f1f`/`510fda4` ("test: extend failing contracts for protected span modes") but the checkbox was never flipped. Re-ran `uv run pytest tests/test_act3_contracts.py -q` against committed `HEAD` (stashing an unrelated, unfinished Task 4 Step 2 WIP diff in `src_ir/act3.py` first): `11 failed, 15 passed` — the 11 failures are exactly the new Task 4 protected-mode assertions (`_does_not_yet_render_expected_span_html` for all five span fixtures, the three `_renders_*` contracts, and the four `_source_buffer_never_receives_generated_output*` cases); all Task 1-3 contracts, including code-span/escape rendering, remain green. This is the expected red gate before Task 4 Step 2 implementation.

- [ ] **Step 2: Implement the remaining scanner modes using the Amendment A2 shared design.**

  **A9 resumption constraint (2026-07-13; binding before any production edit):**
  Amendments A2/A7/A8 remain the shared-field and source-end basis, but A9
  supersedes their live-continuation rule. Reconstruct from committed Task 3;
  do not repair the current `src_ir/act3.py` WIP. Store the live `RESUME_*`
  selector in Lady Macbeth's value, preserve the parent selector in each
  four-cell continuation record, route every top-level `TEXT_END` through
  `LYRIC_TEXT_END_DISPATCH`, and freeze the child selector in Prospero only
  inside the A9 resume family. Romeo is field capture only: no deferred close
  HTML may be stacked there, and resume closes emit directly to Juliet. Drain
  every Horatio glyph to Puck once; triple emphasis adds only its synthetic
  delimiter pair. Use exclusively the five A9 working scene labels and the
  ready-to-paste TOML entries in the accepted design; its three spares are not
  implementation authority. The exact first checkpoint is:

  ```bash
  uv run pytest tests/test_splc_interpret.py tests/test_act3_contracts.py -q -k \
    "protected_modes_do_not_underflow or pre_handoff_source_is_empty_and_output_is_forward or text_end_event_order_is_carrier_safe"
  ```

  Expected: `11 passed`. The observer must show a `LYRIC_TEXT_END_DISPATCH`
  after each top-level terminator pop, private ends reaching the complete A9
  resume adapter with an unchanged frozen `RESUME_*`, and exactly one real end
  reaching `TRAVERSE_COPY_TERMINATOR` with `CONT_NONE`. Run the plan's exact
  literary compliance gate after every Act III/TOML change. Any miss is a new
  `BLOCK[plan]`, not permission to patch the WIP, add a recovery pop, or use a
  spare title.

  **A10 image-title constraint (2026-07-14; binding before image production
  edit):** Add and pass
  `tests/test_splc_interpret.py::test_image_title_floor_survives_alt_requeue`
  before editing `src_ir/act3.py`.  For `FIELD_IMAGE_TITLE`, retain Romeo's
  raw title floor across the independent alt requeue; set
  `RESUME_IMAGE_TITLE=12`, and have only `LYRIC_IMAGE_TITLE_CLOSE` re-enter
  `LYRIC_FIELD_RETRY` after alt scanning, so its existing field drain emits
  the title followed by `" />`.  Do not use an A2/A8/A9 spare.  Extend the
  image observer contract to prove selector 12, the new close scene, no
  Romeo pop during alt drain, and exactly one delayed title drain.  The exact
  pre-production gate is:

  ```bash
  uv run pytest tests/test_splc_interpret.py::test_image_title_floor_survives_alt_requeue tests/test_act3_contracts.py -q
  ```

  Expected before protected production scenes: the new focused floor test
  passes; existing named Task 4 rendering contracts remain red only because
  their implementation is absent.  Any floor or ordering failure is a fresh
  `BLOCK[plan]`.

  The original per-feature Task 4 pool (`LYRIC_HTML_TAG` through
  `LYRIC_AUTOLINK_CLOSE`, `LYRIC_LINK_REGION` through `LYRIC_REGION_EMIT`,
  `LYRIC_EMPHASIS_STRONG` through `LYRIC_EMPHASIS_CLOSE`) is retired — a
  2026-07-13 attempt following that shape needed 91 scenes against a
  29-title budget (stashed at `git stash list` entry "Task 4 Step 2 WIP:
  HTML/autolink/link/image/emphasis scanner, 91 scenes vs 29 reserved
  budget"; recorded in `.agent/blockers.md` history). Implement instead
  against **Amendments A2, A7, and A8** above: one shared `LYRIC_FIELD_*` pipeline
  (anchored on Juliet, with field tags retained by off-stage Prospero after
  `LYRIC_FIELD_RETRY`) for HTML
  tag copy, autolink href/text, link/image destination, and title; the
  capture-hold-then-requeue technique (Horatio holds raw label/alt glyphs,
  which are pushed back onto Puck above a private `TEXT_END` boundary and
  processed by the ordinary top-level scan dispatch, giving nested
  entity/emphasis handling for free) for link/image label and image alt;
  duplicate-on-reverse for autolink's two encoded emits (href, then text)
  from one capture; and the Amendment A1 code-span run-length technique for
  strong-then-emphasis, with emit-open/emit-close branching on the
  opener/closer run-length register (Macbeth) rather than whatever register
  drains body content — the stashed WIP's actual bug was branching on the
  content-draining register instead. `<...>` distinguishes a literal inline
  HTML tag from an HTTP/HTTPS/FTP autolink; tags copy as opaque source
  bytes via the shared pipeline's opaque mode. Parse the exact balanced
  probe link/image forms: `http://e/x_(y)` is retained verbatim as an
  opaque destination and quoted titles remain opaque (both through the
  shared field pipeline), while bracketed label/alt text is requeued rather
  than recursively re-implemented. The ten Amendment A2 spares and the
  separately reserved A10 image-title working/spare pool are the only
  permitted additional states; exhaustion of either pool is a
  planning-amendment stop. Do not add general reference resolution or
  unsupported delimiter grammar.

  Before writing `src_ir/act3.py`, implement the A4 verification-only
  observer and carrier tests above. Then implement the exact scene families
  and holder/floor rules in the accepted design's A4 table. In particular,
  use A8's source-end restore and ordered raw requeue: a private `TEXT_END`
  plus a Lady-Macbeth continuation record for every successful requeue, with
  the record written before the boundary and Horatio's floor consumed rather
  than transferred.  A real `TEXT_END` popped by field or emphasis scanning
  is restored and literal-unwound, never followed by another source pop. Do not
  use a numeric sentinel, reuse Puck as a field-output
  carrier, or use Juliet output as source. Implement A7's exact six-scene
  two-character restore graph. A Step 2 attempt that does not
  make the A4 focused no-underflow and scene-observer tests pass is a
  `BLOCK[plan]` condition, not a reason to add ad-hoc recovery scenes.

- [ ] **Step 3: Regenerate and run all spike evidence.**

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  uv run pytest tests/test_architecture_spikes.py tests/test_act3_contracts.py tests/test_token_dump.py tests/test_token_decode.py tests/test_token_structure.py -q
  uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
  ```

  Expected: all five span probes, every reviewed span dump, existing list/nested-block spikes, and Amps pass.

- [ ] **Step 4: Record and enforce reviewed final dumps.**

  Capture the exact `shakedown-debug` output for every probe, append `-1` as the carrier sentinel in `tests/fixtures/token_stream/spans/<stem>.dump`, and hand-check that every dump ends `PARA ... TEXT_END, STREAM_END` with final HTML glyphs and no persistent positive inline token code. Add the matching parameterized `tests/test_token_dump.py` comparison, omitting only terminal `-1` because the debug target does not print it. Run `uv run pytest tests/test_act3_contracts.py tests/test_token_dump.py tests/test_token_decode.py tests/test_token_structure.py -q`; expected PASS.

- [ ] **Step 5: Re-run interpreter/generated-SPL parity if the new scenes introduce a new IR control-flow shape.**

  Run: `uv run pytest tests/test_splc_interpret.py tests/test_splc_interpret_parity.py tests/test_splc_validate.py -q`  
  Expected: PASS; no lowered branch/goto or stack-floor behavior differs from the IR interpreter.

- [ ] **Step 6: Commit and push protected regions.**

  Run: `git add src_ir/act3.py src/30-act3-literary.toml src/30-act3-span.spl shakedown.spl tests/test_act3_contracts.py tests/fixtures/token_stream/spans && git commit -m "feat: protect buffered span regions"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding.

### Task 5: Close the spike with regression, performance, and halt evidence

**Files:**
- Modify: `docs/superpowers/plans/2026-07-12-span-architecture-spike.md`
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: `docs/verification-plan.md` only if a measured claim changes

**Consumes:** All preceding gates and the accepted design's halt rule.

**Produces:** A recorded confirmed-or-halted Act III model and exactly one updated roadmap state.

- [ ] **Step 1: Record measured program and feedback-loop evidence.**

  Record generated line/scene counts for `src/30-act3-span.spl`, one cold run and three representative runs of `variable_code_spans`, and the wall time of the shipped-fixture/spike regression command. Compare the measurements against `docs/performance/budget.md` yellow/red thresholds; do not infer performance from line count alone.

- [ ] **Step 2: Run the completion gate.**

  Run:

  ```bash
  uv run pytest -q
  uv run pytest tests/test_architecture_spikes.py -q
  uv run pytest tests/test_splc_generated_fragments.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'
  ```

  Expected: all default tests pass; all list, nested-block, and span spikes are byte-identical; generated/literary gates pass; the one shipped deterministic mdtest fixture is strict-oracle byte-identical. Do not claim unshipped fixtures are parity gates.

- [ ] **Step 3: Apply the halt rule from the accepted design.**

  If a protected region required output rescanning, could not preserve bytes, left a floor/prefix corrupted, or produced an invalid reviewed stream, append `- BLOCK:` to `.agent/blockers.md`, leave this plan in flight, and stop. Otherwise add concise measured evidence and checked boxes to this plan, mark 4S `shipped: <date> at commit <sha>` in the roadmap, and leave row 5 pending.

- [ ] **Step 4: Commit and push the outcome.**

  Run: `git add docs/superpowers/plans/2026-07-12-span-architecture-spike.md docs/superpowers/plans/plan-roadmap.md docs/verification-plan.md && git commit -m "docs: record span spike outcome"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding. Omit `docs/verification-plan.md` from the command if no measured claim changed; never create an empty commit.
