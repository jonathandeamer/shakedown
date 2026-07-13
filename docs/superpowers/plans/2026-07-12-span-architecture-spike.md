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

---

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

- [ ] **Step 1: Extend failing contracts for every protected mode.**

  Add assertions that the decoded output for `inline_html_and_autolink` contains literal `<span><em>raw</em></span>` and exactly one `&amp;` in the autolink query; `links_images_protected` contains `<a href="http://e/x_(y)" title="t">a <em>b</em></a>` and `<img src="img.png" alt="c <em>d</em>" title="i" />`; and `overlapping_emphasis` contains both exact expected strong/em nesting sequences. Add a negative assertion that no generated output is placed back on the source-buffer stack.

- [ ] **Step 2: Implement the remaining scanner modes in oracle order.**

  Extend the Task 3 buffer using the pre-reserved Task 4 protected-region
  pool: `LYRIC_HTML_TAG` through `LYRIC_AUTOLINK_CLOSE` for opaque tags and
  active autolinks; `LYRIC_LINK_REGION` through `LYRIC_REGION_EMIT` for the
  balanced link/image label, destination, and title states; and
  `LYRIC_EMPHASIS_STRONG` through `LYRIC_EMPHASIS_CLOSE` for strong-before-em
  output. `<...>` distinguishes a literal inline HTML tag from an
  HTTP/HTTPS/FTP autolink; tags copy as opaque source bytes, while autolink
  URLs receive amp/angle encoding once. Parse the exact balanced probe
  link/image forms: bracketed label/alt text is recursively scanned as source
  text, `http://e/x_(y)` is retained verbatim as an opaque destination, and
  quoted titles remain opaque. Apply amp/angle encoding, strong substitution,
  and emphasis substitution only to ordinary/child-label source regions, with
  strong before emphasis. The six Task 4 spares are the only permitted
  additional states; exhaustion is a planning-amendment stop. Do not add
  general reference resolution or unsupported delimiter grammar.

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
