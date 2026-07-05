# Act III Port-Readiness Audit (input to plan 3J)

**Date:** 2026-07-05
**Scope:** `src/30-act3-span.spl` (56 scenes, 1,285 lines), decoded against the
splc compiler as shipped through plan 3I on main (Act I, Act II, Act IV, and
the debug play all generated; regen byte-identity and the full default suite
verified green while writing this audit).
**Purpose:** durable ground truth for writing plan 3J once 3I is marked
shipped. This is an audit note, not a plan; per the roadmap's staging
philosophy, plan 3J is written only after 3I's roadmap row is closed out.

## Verdict

Act III needs **zero new IR ops and zero new expression kinds** — every
statement lowers to existing `let` / `push` / `pop` / `branch` / `goto` /
`halt_act` ops, and all 37 `the square of` sites sit inside pure-constant
phrases (see "`square(e)` stays out"). It needs **one compiler extension**:
a **per-scene anchor override**. The shipped stage model (`Act.anchor` +
`participants()` in `scripts/splc/validate.py`) requires the act anchor
on stage in every scene, but Act III cycles through four stage pairs —
(Puck, Romeo), (Puck, Juliet), (Puck, Rosalind), (Romeo, Juliet) — and **no
single character appears in all of them** (Puck is off stage for the entire
reverse phase). This is a choreography-model extension, not an escape hatch:
`Scene` gains an optional anchor field, and `participants`, `entry_pairs`,
and the goto/branch speaker assignment in `lower.py` use the scene-effective
anchor. Everything else (goto entry adaptation, off-stage third-person
questions, targets-only companions) is already shipped and is exercised
as-is.

No new prose pools are needed: all 56 scene titles already exist in
`src/30-act3-literary.toml` (label sets verified identical), and every
Recall key the act uses already exists under the correct speaker in
`src/literary.toml` (24 `romeo.recall` keys, 6 `puck.recall` forest keys).

## Choreography

### Stage pairs and the per-scene anchor extension

The act has four phases with hard pair boundaries (all mid-act swaps are
exit-one/enter-one, which `_stage_directions` already renders):

| Phase | Pair | Scenes |
|---|---|---|
| Scan | Puck + Romeo | `ACT_III_START` through the dispatch/pop scenes, `LYRIC_RETURN_TO_SCAN` |
| Output | Puck + Juliet | every `LYRIC_OPEN_OUTPUT_*` / `LYRIC_ANCHOR_*` / `LYRIC_OUTPUT_*` / fallback scene |
| Consult | Puck + Rosalind | `LYRIC_OPEN_CONSULT_REFERENCE_{ONE,TWO}`, `LYRIC_CONSULT_REFERENCE_{ONE,TWO}` |
| Reverse | Romeo + Juliet, alternating with Juliet + Puck | `LYRIC_OPEN_REVERSE` through `ACT_III_DONE` |

The reverse loop swaps the pair **twice per token** ((Romeo, Juliet) →
(Juliet, Puck) → (Romeo, Juliet)), so this act is also the first real
stress of goto entry adaptation — Act IV staged one pair for 20 scenes.

Suggested effective anchors (reproduces the hand fragment's speaker
assignments almost exactly; final choice is a plan 3J decision **except**
the consult scenes, see below):

- **Romeo** — all scan-phase scenes (pop-on-Puck spoken by Romeo, let-on-Romeo
  spoken by Puck, glyph questions asked by Romeo with Puck answering the Ifs:
  all match the hand fragment), plus `LYRIC_RETURN_TO_SCAN` and
  `LYRIC_RETURN_TO_REVERSE` (companion=JULIET).
- **Puck** — `ACT_III_START` only (companion=ROMEO; the off-stage Horatio
  question is asked by the anchor, matching the hand fragment's Puck line).
- **Juliet** — all output/anchor/fallback scenes (push-on-Juliet spoken by
  Puck, gotos spoken by Juliet: both match the hand fragment) and the whole
  reverse phase (`LYRIC_OPEN_REVERSE`, both reverse-count scenes,
  `LYRIC_REVERSE_CHECK`, `LYRIC_REVERSE_POP`, `LYRIC_OPEN_PUSH_BACK`,
  `LYRIC_PUSH_BACK`, `ACT_III_DONE`).
- **Rosalind** — the four consult scenes (pop-on-Rosalind spoken by Puck,
  gotos spoken by Rosalind: matches the hand fragment). **This one is
  compliance-constrained, not free:** all four `Rosalind:` speaker lines in
  the entire play come from these scenes, and
  `test_reference_librarian_is_visible_in_reference_scenes` requires ≥4
  `Rosalind:` lines across the `REFERENCE_SCENES` blocks while
  `test_named_production_characters_have_speaking_lines` forbids a silent
  introduced character. Anchor=Rosalind yields exactly 4 (the gotos).

Companions needed (branch ops contribute no participants, so scenes that
are a lone branch — or a lone goto — must declare one): `ACT_III_START`
(anchor PUCK, companion=ROMEO), the six glyph-test scenes that are a single
branch on `val(PUCK)` (`LYRIC_TEST_AMPERSAND`, `LYRIC_TEST_LEFT_ANGLE`,
`LYRIC_LINK_TEST_INLINE_OPEN`, `LYRIC_INLINE_TEST_BRACKETED_DESTINATION`,
`LYRIC_INLINE_DEST_DIRECT_CHECK`, `LYRIC_REFERENCE_TEST_ATT_TEXT` — anchor
ROMEO, companion=PUCK), `LYRIC_SCAN_CHECK` (companion=PUCK),
`LYRIC_OPEN_REVERSE` (anchor JULIET, companion=ROMEO),
`LYRIC_REVERSE_CHECK` (anchor JULIET, companion=ROMEO), every goto-only
`LYRIC_OPEN_*` scene (companion = the entering character), and
`ACT_III_DONE` (anchor JULIET, companion=ROMEO).

### Compiler-change details the extension must cover

1. `Scene` gains an optional per-scene anchor (act anchor as default);
   `participants`, `entry_pairs`, `validate`'s Pop speaker check, and every
   speaker decision in `lower.py` (including plain-goto speaker) switch to
   the scene-effective anchor.
2. `entry_pairs` compares pairs as **tuples** `(anchor, other)`; with mixed
   anchors the same on-stage *set* can appear in different orders (e.g.
   `ACT_III_START` leaves (Puck, Romeo), scan scenes are (Romeo, Puck)).
   Entry consistency and stage-direction diffing must normalize to sets.
   (`_stage_directions` already diffs sets; the pass-1 consistency check in
   `entry_pairs` does not.)
3. Branch-arrival consistency holds throughout Act III as decoded — every
   branch target's predecessors leave the same on-stage set — so no
   relaxation of the pass-1 rule is needed, only the set normalization.

## Registers

- **Puck = the glyph stream.** His stack carries Act II's reversed token
  stream in; his value is the current glyph during the scan. At the end of
  the act his stack carries Act III's reversed *output* stream out to
  Act IV (loaded by the reverse phase).
- **Romeo = scan countdown** (315 in Slice-1 mode, Horatio in short mode),
  decremented once per pop. His **stack is a discard pile**: the inline-link
  destination scenes push scanned destination glyphs onto it
  (`Remember me.`) and nothing ever pops it — Slice 1 emits hardcoded
  anchor payloads instead. Quirk, ported as-is.
- **Juliet = forward output accumulator.** Output scenes push token codes
  and payload bytes onto her stack in forward order; the reverse phase pops
  her stack (`roses_kept_word`) and re-pushes onto Puck, reversing it.
  Her value is scratch (`let` + `Remember yourself` pairs).
- **Rosalind = Act I's reference-definition stack.** Each consult scene pops
  three entries (seal, path, name) and discards the values — Slice 1
  consults are stack drainage only, alignment with Act I's pushes. Quirk,
  ported as-is.
- **Horatio (off-stage) = short-stream count** carried from earlier acts;
  read four times without entering (threshold branches at `ACT_III_START`
  and `LYRIC_OPEN_REVERSE`, value copies at `LYRIC_SET_SHORT_SCAN_COUNT`
  and `LYRIC_SET_SHORT_REVERSE_COUNT`).

Stream contract: Act II hands Act III 315 glyphs (Slice 1) or Horatio
glyphs (short) on Puck's stack; Act III hands Act IV 387 tokens (Slice 1)
or Horatio tokens (short) on the same stack. In short mode the counts
assume one output token per input glyph, which the entity paths (1 glyph →
6 tokens) would violate — an existing Slice-1 quirk shared with the
hand-authored play, pinned by G2, not the port's problem to fix.

## Decoded ground truth (scene by scene)

Constants verified mechanically: every value phrase in the fragment was
parsed and evaluated by script (adjective chains double from base 1;
`nothing` = 0), zero parse failures. Dispatch codes 11–14 must be written
as `src_ir.tokens` references, matching the Act IV convention.

Scan phase — pair (Puck, Romeo):

| Scene | Ops |
|---|---|
| `ACT_III_START` | `branch(gt(val(HORATIO), const(128)), then=LYRIC_SET_SLICE_ONE_SCAN_COUNT, else_=LYRIC_SET_SHORT_SCAN_COUNT)` |
| `LYRIC_SET_SLICE_ONE_SCAN_COUNT` | `let(ROMEO, const(315))` — hand phrase (1+4)×(8²−1); `goto(LYRIC_SCAN_CHECK)` |
| `LYRIC_SET_SHORT_SCAN_COUNT` | `let(ROMEO, val(HORATIO))`; `goto(LYRIC_SCAN_CHECK)` |
| `LYRIC_SCAN_CHECK` | `branch(eq(val(ROMEO), const(0)), then=LYRIC_OPEN_REVERSE, else_=LYRIC_POP_GLYPH)` |
| `LYRIC_POP_GLYPH` | `pop(PUCK, "mornings_first_cut")`; `let(ROMEO, sub(val(ROMEO), const(1)))`; `branch(eq(val(PUCK), const(91)), …)` — 91 `'['`, then=`LYRIC_REFERENCE_POP_AFTER_OPEN`, else=`LYRIC_TEST_AMPERSAND` |
| `LYRIC_TEST_AMPERSAND` | `branch(eq(val(PUCK), const(38)), …)` — `'&'`, then=`LYRIC_AMP_POP_NEXT`, else=`LYRIC_TEST_LEFT_ANGLE` |
| `LYRIC_REFERENCE_POP_AFTER_OPEN` | pop(`brackets_first_petal`) + decrement; `branch(eq(val(PUCK), const(108)), …)` — `'l'`, then=`LYRIC_REFERENCE_LINK_POP_BODY`, else=`LYRIC_REFERENCE_TEST_ATT_TEXT` |
| `LYRIC_REFERENCE_TEST_ATT_TEXT` | `branch(eq(val(PUCK), const(65)), …)` — `'A'`, then=`LYRIC_REFERENCE_ATT_POP_BODY`, else=`LYRIC_OPEN_REFERENCE_FALLBACK` |
| `LYRIC_REFERENCE_LINK_POP_BODY` | five pop+decrement pairs (`links_second_petal` … `links_following_air`); `branch(eq(val(PUCK), const(32)), …)` — `' '`, then=`LYRIC_REFERENCE_ONE_POP_LABEL`, else=`LYRIC_LINK_TEST_INLINE_OPEN` |
| `LYRIC_LINK_TEST_INLINE_OPEN` | `branch(eq(val(PUCK), const(40)), …)` — `'('`, then=`LYRIC_INLINE_POP_FIRST_DESTINATION`, else=`LYRIC_OPEN_OUTPUT_LINK_FALLBACK` |
| `LYRIC_INLINE_POP_FIRST_DESTINATION` | pop(`inline_paths_first_gate`) + decrement; `branch(eq(val(PUCK), const(47)), …)` — `'/'`, then=`LYRIC_INLINE_DEST_DIRECT_CHECK`, else=`LYRIC_INLINE_TEST_BRACKETED_DESTINATION` |
| `LYRIC_INLINE_TEST_BRACKETED_DESTINATION` | `branch(eq(val(PUCK), const(60)), …)` — `'<'`, then=`LYRIC_INLINE_DEST_BRACKETED_POP`, else=`LYRIC_OPEN_OUTPUT_LINK_FALLBACK` |
| `LYRIC_INLINE_DEST_DIRECT_CHECK` | `branch(eq(val(PUCK), const(41)), …)` — `')'`, then=`LYRIC_OPEN_OUTPUT_INLINE_LINK`, else=`LYRIC_INLINE_DEST_DIRECT_KEEP` |
| `LYRIC_INLINE_DEST_DIRECT_KEEP` | `push(ROMEO, val(PUCK))` (discard pile); pop(`inline_paths_next_gate`) + decrement; `goto(LYRIC_INLINE_DEST_DIRECT_CHECK)` |
| `LYRIC_INLINE_DEST_BRACKETED_POP` | pop(`bracketed_paths_next_gate`) + decrement; `branch(eq(val(PUCK), const(62)), …)` — `'>'`, then=`LYRIC_INLINE_DEST_BRACKETED_CLOSE`, else=`LYRIC_INLINE_DEST_BRACKETED_KEEP` |
| `LYRIC_INLINE_DEST_BRACKETED_KEEP` | `push(ROMEO, val(PUCK))`; `goto(LYRIC_INLINE_DEST_BRACKETED_POP)` |
| `LYRIC_INLINE_DEST_BRACKETED_CLOSE` | pop(`bracketed_paths_round_seal`) + decrement; `branch(eq(val(PUCK), const(41)), …)` — `')'`, then=`LYRIC_OPEN_OUTPUT_INLINE_LINK`, else=`LYRIC_OPEN_OUTPUT_LINK_FALLBACK` |
| `LYRIC_REFERENCE_ONE_POP_LABEL` | three pop+decrement pairs (`first_shelfs_open_mark`, `first_shelfs_number`, `first_shelfs_close_mark`); `goto(LYRIC_OPEN_CONSULT_REFERENCE_ONE)` |
| `LYRIC_REFERENCE_ATT_POP_BODY` | eight pop+decrement pairs (`houses_second_petal`, `houses_ampersand`, `houses_last_petal`, `houses_closing_petal`, `houses_following_air`, `second_shelfs_open_mark`, `second_shelfs_number`, `second_shelfs_close_mark`); `goto(LYRIC_OPEN_CONSULT_REFERENCE_TWO)` |
| `LYRIC_AMP_POP_NEXT` | pop(`mornings_next_cut`) + decrement; `branch(eq(val(PUCK), const(97)), …)` — `'a'`, then=`LYRIC_OPEN_OUTPUT_LITERAL_AMP_CURRENT`, else=`LYRIC_OPEN_OUTPUT_AMP_ENTITY_CURRENT` |
| `LYRIC_TEST_LEFT_ANGLE` | `branch(eq(val(PUCK), const(60)), …)` — `'<'`, then=`LYRIC_LEFT_ANGLE_POP_NEXT`, else=`LYRIC_OPEN_OUTPUT_CURRENT` |
| `LYRIC_LEFT_ANGLE_POP_NEXT` | pop(`mornings_next_cut`) + decrement; `branch(eq(val(PUCK), const(47)), …)` — `'/'`, then=`LYRIC_OPEN_OUTPUT_LITERAL_LEFT_CURRENT`, else=`LYRIC_OPEN_OUTPUT_LT_ENTITY_CURRENT` |
| `LYRIC_RETURN_TO_SCAN` | `goto(LYRIC_SCAN_CHECK)` — entry (Puck, Juliet), pair (Puck, Romeo) |

Output and consult scenes — every `LYRIC_OPEN_*` row is a goto-only
stage-change scene (entry pair differs from its own pair; the exit/enter
diff is exactly what the hand fragment stages):

| Scene | Ops |
|---|---|
| `LYRIC_OPEN_OUTPUT_INLINE_LINK` | `goto(LYRIC_ANCHOR_INLINE)` — swaps Romeo→Juliet |
| `LYRIC_ANCHOR_INLINE` | 30 `push(JULIET, const(…))`: token 11, bytes of `/script?foo=1&amp;bar=2`, token 13, bytes of `link`, token 14; `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_CONSULT_REFERENCE_ONE` | `goto(LYRIC_CONSULT_REFERENCE_ONE)` — swaps Romeo→Rosalind |
| `LYRIC_CONSULT_REFERENCE_ONE` | `pop(ROSALIND, "first_forest_seal")`, `pop(ROSALIND, "first_forest_path")`, `pop(ROSALIND, "first_forest_name")` — values discarded; `goto(LYRIC_OPEN_OUTPUT_REFERENCE_ONE)` |
| `LYRIC_OPEN_OUTPUT_REFERENCE_ONE` | `goto(LYRIC_ANCHOR_REFERENCE_ONE)` — swaps Rosalind→Juliet |
| `LYRIC_ANCHOR_REFERENCE_ONE` | 42 pushes: token 11, bytes of `http://example.com/?foo=1&amp;bar=2`, token 13, bytes of `link`, token 14; `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_CONSULT_REFERENCE_TWO` | `goto(LYRIC_CONSULT_REFERENCE_TWO)` — swaps Romeo→Rosalind |
| `LYRIC_CONSULT_REFERENCE_TWO` | `pop(ROSALIND, "second_forest_seal")`, `…path`, `…name` — discarded; `goto(LYRIC_OPEN_OUTPUT_REFERENCE_TWO)` |
| `LYRIC_OPEN_OUTPUT_REFERENCE_TWO` | `goto(LYRIC_ANCHOR_REFERENCE_TWO)` — swaps Rosalind→Juliet |
| `LYRIC_ANCHOR_REFERENCE_TWO` | 35 pushes: token 11, bytes of `http://att.com/`, **token 12** (the act's only `ANCHOR_TITLE`), bytes of `AT&amp;T`, token 13, bytes of `AT&amp;T`, token 14; `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_OUTPUT_LINK_FALLBACK` | `goto(LYRIC_OUTPUT_LINK_FALLBACK)` — swaps Romeo→Juliet |
| `LYRIC_OUTPUT_LINK_FALLBACK` | 6 pushes: bytes of `[link(` (the current glyph is *not* re-emitted — Slice-1 quirk, as-is); `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_REFERENCE_FALLBACK` | `goto(LYRIC_REFERENCE_FALLBACK)` — swaps Romeo→Juliet |
| `LYRIC_REFERENCE_FALLBACK` | `push(JULIET, const(91))` `'['`; `push(JULIET, val(PUCK))` (hand: "Remember myself.", Puck speaking); `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_OUTPUT_CURRENT` | `goto(LYRIC_OUTPUT_CURRENT)` — swaps Romeo→Juliet |
| `LYRIC_OUTPUT_CURRENT` | `let(JULIET, val(PUCK))`; `push(JULIET, val(JULIET))`; `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_OUTPUT_AMP_ENTITY_CURRENT` | `goto(LYRIC_OUTPUT_AMP_ENTITY_CURRENT)` |
| `LYRIC_OUTPUT_AMP_ENTITY_CURRENT` | let+push pairs on Juliet for 38, 97, 109, 112, 59 (`&amp;`), then `let(JULIET, val(PUCK))` + push (the lookahead glyph popped in `LYRIC_AMP_POP_NEXT`); `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_OUTPUT_LITERAL_AMP_CURRENT` | `goto(LYRIC_OUTPUT_LITERAL_AMP_CURRENT)` |
| `LYRIC_OUTPUT_LITERAL_AMP_CURRENT` | let+push 38 `'&'`, then let+push `val(PUCK)` (lookahead, which is `'a'`); `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_OUTPUT_LT_ENTITY_CURRENT` | `goto(LYRIC_OUTPUT_LT_ENTITY_CURRENT)` |
| `LYRIC_OUTPUT_LT_ENTITY_CURRENT` | let+push pairs for 38, 108, 116, 59 (`&lt;`), then let+push `val(PUCK)` (lookahead); `goto(LYRIC_RETURN_TO_SCAN)` |
| `LYRIC_OPEN_OUTPUT_LITERAL_LEFT_CURRENT` | `goto(LYRIC_OUTPUT_LITERAL_LEFT_CURRENT)` |
| `LYRIC_OUTPUT_LITERAL_LEFT_CURRENT` | let+push 60 `'<'`, then let+push `val(PUCK)` (lookahead, which is `'/'`); `goto(LYRIC_RETURN_TO_SCAN)` |

Reverse phase — pairs (Romeo, Juliet) and (Juliet, Puck):

| Scene | Ops |
|---|---|
| `LYRIC_OPEN_REVERSE` | `branch(gt(val(HORATIO), const(128)), then=LYRIC_SET_SLICE_ONE_REVERSE_COUNT, else_=LYRIC_SET_SHORT_REVERSE_COUNT)` — entry (Puck, Romeo), pair (Romeo, Juliet): Puck exits for the rest of the act |
| `LYRIC_SET_SLICE_ONE_REVERSE_COUNT` | `let(ROMEO, const(387))` — hand phrase (1+2)×(1+8×16), identical to Act IV's `SLICE_ONE_STREAM_COUNT`; `goto(LYRIC_REVERSE_CHECK)` |
| `LYRIC_SET_SHORT_REVERSE_COUNT` | `let(ROMEO, val(HORATIO))`; `goto(LYRIC_REVERSE_CHECK)` |
| `LYRIC_REVERSE_CHECK` | `branch(eq(val(ROMEO), const(0)), then=ACT_III_DONE, else_=LYRIC_REVERSE_POP)` |
| `LYRIC_REVERSE_POP` | `pop(JULIET, "roses_kept_word")`; `let(ROMEO, sub(val(ROMEO), const(1)))`; `goto(LYRIC_OPEN_PUSH_BACK)` |
| `LYRIC_OPEN_PUSH_BACK` | `goto(LYRIC_PUSH_BACK)` — swaps Romeo→Puck |
| `LYRIC_PUSH_BACK` | `let(PUCK, val(JULIET))`; `push(PUCK, val(PUCK))`; `goto(LYRIC_RETURN_TO_REVERSE)` |
| `LYRIC_RETURN_TO_REVERSE` | `goto(LYRIC_REVERSE_CHECK)` — swaps Puck→Romeo |
| `ACT_III_DONE` | `halt_act()` |

## Constants: shared magic numbers and over-bound recipes

Three cross-act constants appear in Act III; single-definition homes should
be settled in plan 3J (a pure constant-hoisting refactor keeps regen
byte-identical):

- **128** (stream threshold): `src_ir/act4.py` exports `STREAM_THRESHOLD`;
  `src_ir/act2.py` still uses a literal `const(128)`. Act III uses it twice.
- **315** (Slice-1 glyph count): Act II's push count — `act2.py` renders it
  as two `let`s (9, then ×35) to stay within the recipe bound. Act III can
  use a single 4-operator recipe instead: `mul(add(1, 4), sub(mul(8, 8), 1))`
  (the hand fragment's own phrase). The shared value belongs next to its
  producer.
- **387** (Slice-1 token count): identical to Act IV's
  `SLICE_ONE_STREAM_COUNT` / `slice_one_count_expr()`; import, don't
  restate.

`test_numeric_recipe_complexity_stays_bounded` caps value phrases at 4
operators. Measured against the shipped `emit_value` decompositions, **11
distinct Act III constants are over the bound** and need explicit
`_EMIT_RECIPE`-style entries (Act IV already has 47, 61, 62 — hoist or
extend): 47 `'/'`, 59 `';'`, 61 `'='`, 62 `'>'`, 63 `'?'`, 91 `'['`,
107 `'k'`, 109 `'m'`, 110 `'n'`, 111 `'o'`, 115 `'s'`. The hand fragment
already contains a ≤4-operator phrase for every one of them (it passes the
same test today), so the recipes are transcription, not invention.

## `square(e)` stays out (addendum §A2 closed for good)

Addendum §A2 promised `square(e)` for Act III's 48 `the square of` sites.
The current count is **37, all in Act III** (the other acts' occurrences
disappeared when their generated fragments re-decomposed constants), and the
mechanical decode confirms **every one sits inside a pure-constant phrase** —
there is no dynamic square anywhere in the play. `scripts/splc/ir.py` never
grew a `square` builder, and it doesn't need one: `prose.value_phrase` /
explicit recipes cover every use (e.g. 8² is `mul(const(8), const(8))`).
Plan 3J should record this as the final disposition and amend §A2's promise
rather than implement an unused expression kind.

## Prose pools: sufficiency verified, exhaustion warning moot

- All 56 `[scenes.*]` labels in `src/30-act3-literary.toml` match the
  fragment's labels exactly (verified by set comparison).
- Every Recall key resolves for its generated speaker: the 24
  `characters.romeo.recall` keys cover all scan/reverse pops (speaker Romeo),
  and the 6 `characters.puck.recall` forest keys cover the consult pops
  (speaker Puck). No new pool material is required.
- Addendum §A3 required a "pool-exhaustion build warning" by stage 4. The
  shipped `prose.py` selects with seeded `random.choice` — pools are sampled
  with replacement, so exhaustion is not a failure mode that can occur.
  Repetition across 56 scenes is an aesthetic-pool concern (Romeo/Juliet/Puck
  each have 3-entry equality pools), and the compliance suite already targets
  the pools, not rendered SPL. Plan 3J should record a disposition: either
  formally retire the promised warning with this rationale, or implement a
  variety report if the operator wants one. No blocker either way.

## Accepted surface changes (behavioral parity only; G1/G2 unaffected)

Same classes as the Act IV port:

- **Self-questions → second person**: `LYRIC_SCAN_CHECK` and
  `LYRIC_REVERSE_CHECK` ("Am I as fair as nothing?", Romeo) lower to the
  partner asking "Are you … as nothing?" with the If-arms moving to Romeo.
  Same condition, same targets.
- **Goto speaker normalization**: plain gotos are spoken by the
  scene-effective anchor; the hand fragment occasionally gives them to the
  other pair member (e.g. Puck's "Let us proceed" in scan scenes with
  suggested anchor Romeo).
- **Goto entry adaptation renders at the source**: the hand fragment stages
  exits/enters at the target scene's start; the compiler stages them before
  the goto line in the source scene (established Act I/II/IV convention).
  Same on-stage sets at every spoken line.
- **Constant re-decomposition**: identical values, possibly different
  phrases, except where explicit recipes pin them.

## Couplings to confirm during plan 3J

1. **Per-scene anchor override** — the one compiler change (see
   Choreography). Scope it with unit tests per validation class plus a
   lowering test for mixed-anchor entry normalization; all four generated
   fragments must regen byte-identical after the change (default anchor path
   untouched).
2. **Rosalind visibility** — consult scenes must keep ≥4 `Rosalind:` lines
   (`test_reference_librarian_is_visible_in_reference_scenes`,
   `test_named_production_characters_have_speaking_lines`); anchor=Rosalind
   in the four consult scenes satisfies both.
3. **Off-stage Horatio** — two third-person threshold questions and two
   value copies; both shapes already shipped (Act II/IV precedent), just
   verify against the extension.
4. **Roadmap housekeeping first** — the roadmap still marks 3I `in flight`
   although its deliverables are on main (regen byte-identity and the full
   default suite were re-verified green while writing this audit). Close out
   3I's row before writing plan 3J.

## Gate checklist for plan 3J (carry into the plan)

- **G2 is the primary semantic gate for this port**: `./shakedown-debug`
  dumps the stream acts 1–3 produce, so it measures Act III's output
  directly. Snapshot the dump on the fixed input set with the hand-authored
  Act III still in place, in the same task that swaps it; the generated act
  must reproduce identical dumps. (Simpler than 3I: the debug play is
  already generated and does not change.)
- G1: Amps fixture byte-identical (strict parity harness) — confirms the
  Act III → Act IV integration.
- G3: full default pytest suite green, parse gate on every build.
- Regen byte-identity for Acts I, II, IV and the debug fragment after every
  compiler change (the anchor-override work is a compiler change; expect to
  re-check repeatedly).
- Literary compliance: no new prose pools, no new scene titles (all 56
  already reserved in `src/30-act3-literary.toml`); the named tests to run:
  `test_scene_titles_have_toml_entries_and_match_source`,
  `test_scene_ledger_matches_source_scene_labels`,
  `test_recall_phrases_are_in_speaker_pools`,
  `test_numeric_recipe_complexity_stays_bounded`,
  `test_reference_librarian_is_visible_in_reference_scenes`,
  `test_named_production_characters_have_speaking_lines`,
  `test_juliet_surfaces_include_night_or_star_imagery`.
- Spike A xfails re-examined per the roadmap row (3J is the last port
  stage; the resumed list plan unblocks when it ships).
