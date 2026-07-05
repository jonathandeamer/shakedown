# Act IV Port-Readiness Audit (input to plan 3I)

**Date:** 2026-07-05
**Scope:** `src/40-act4-emit.spl` (20 scenes, 461 lines) and
`debug/40-act4-token-dump.spl` (6 scenes), decoded against the splc IR as it
stands after plan 3G plus the compiler changes specified in plan 3H
(`docs/superpowers/plans/2026-07-05-splc-act2.md`).
**Purpose:** durable ground truth for writing plan 3I once 3H ships. This is
an audit note, not a plan; per the roadmap's staging philosophy, plan 3I is
written only after 3H's gate is green.

## Verdict

Act IV needs **zero new IR operations and zero new prose pools**. Every scene
lowers to existing ops (`let`, `pop`, `print_char`, `print_int`, `branch`,
`goto`, `halt_act`). The only compiler features it depends on are the three
already being built in 3H (targets-only participants, third-person questions,
goto entry adaptation — and of those, only the first two are actually
exercised; see "3H couplings"). The debug play port needs six `[scenes.DBG_*]`
ledger entries (titles already authored in the hand fragment — copy them
verbatim) and a decision about where the generated debug fragment lives.

## Choreography

- **Anchor: `PROSPERO`.** Verified against every op: `let`/`pop`/`print` ops
  targeting Puck are spoken by Prospero exactly as the hand fragment has them
  (e.g. every "Speak your mind!" is Prospero's line), and ops targeting
  Prospero are spoken by Puck ("You are as noble as Horatio").
- **Single pair throughout.** All 20 scenes stage (Prospero, Puck). No
  mid-act pair change, so Act IV does not even stress 3H's entry-pair
  refinement: `[Enter Puck and Prospero]` once at `ACT_IV_START`, `[Exeunt]`
  at `ACT_IV_DONE`, nothing in between.
- **Companions needed** (targets-only rule leaves these scenes with no
  non-anchor target): `ACT_IV_START`, `SCRIBE_SET_SLICE_ONE_STREAM_COUNT`,
  `SCRIBE_SET_SHORT_STREAM_COUNT`, `SCRIBE_STREAM_CHECK`,
  `SCRIBE_TEST_FINAL_CLOSE`, `ACT_IV_DONE` — all `companion=PUCK`.

## Registers

- **Prospero = remaining stream count.** Set once at act start, decremented
  per token, tested against 0 for loop exit and for final-vs-interior
  paragraph close.
- **Puck = current token / scratch.** `Recall` pops the next token into Puck;
  the emit scenes then overwrite Puck with output character codes (safe: the
  token has already been dispatched).
- **Horatio (off-stage) = carried from earlier acts**; read twice without
  entering (branch test at `ACT_IV_START`, value copy at
  `SCRIBE_SET_SHORT_STREAM_COUNT`).

## Decoded ground truth (scene by scene)

Constants verified by evaluating the adjective chains (flower base 1, each
adjective doubles: `little green sweet flower`=8, `rural …`=16; angel base 1:
`warm fine golden noble angel`=16, `fine golden noble angel`=8; cat base 1:
`little furry black cat`=8).

| Scene | Ops |
|---|---|
| `ACT_IV_START` | `branch(gt(val(HORATIO), const(128)), then=SCRIBE_SET_SLICE_ONE_STREAM_COUNT, else_=SCRIBE_SET_SHORT_STREAM_COUNT)` — 128 = 8×16 |
| `SCRIBE_SET_SLICE_ONE_STREAM_COUNT` | `let(PROSPERO, const(387))` — (1+2)×(1+8×16); `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_SET_SHORT_STREAM_COUNT` | `let(PROSPERO, val(HORATIO))`; `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_STREAM_CHECK` | `branch(eq(val(PROSPERO), const(0)), then=ACT_IV_DONE, else_=SCRIBE_POP_TOKEN)` |
| `SCRIBE_POP_TOKEN` | `pop(PUCK, recall="heralds_present_word")`; `let(PROSPERO, sub(val(PROSPERO), const(1)))`; `branch(eq(val(PUCK), const(1)), then=SCRIBE_EMIT_PARAGRAPH_OPEN, else_=SCRIBE_TEST_PARAGRAPH_CLOSE)` — 1 = `tokens.PARA` |
| `SCRIBE_TEST_PARAGRAPH_CLOSE` | `branch(eq(val(PUCK), const(0)), then=SCRIBE_TEST_FINAL_CLOSE, else_=SCRIBE_TEST_ANCHOR_OPEN)` — 0 = paragraph-close stream marker |
| `SCRIBE_TEST_ANCHOR_OPEN` | `branch(eq(val(PUCK), const(11)), then=SCRIBE_EMIT_ANCHOR_OPEN, else_=SCRIBE_TEST_ANCHOR_TITLE)` — 11 = `tokens.ANCHOR_OPEN` |
| `SCRIBE_TEST_ANCHOR_TITLE` | `branch(eq(val(PUCK), const(12)), then=SCRIBE_EMIT_ANCHOR_TITLE, else_=SCRIBE_TEST_ANCHOR_TEXT)` — 12 = `tokens.ANCHOR_TITLE` |
| `SCRIBE_TEST_ANCHOR_TEXT` | `branch(eq(val(PUCK), const(13)), then=SCRIBE_EMIT_ANCHOR_TEXT, else_=SCRIBE_TEST_ANCHOR_CLOSE)` — 13 = `tokens.ANCHOR_TEXT` |
| `SCRIBE_TEST_ANCHOR_CLOSE` | `branch(eq(val(PUCK), const(14)), then=SCRIBE_EMIT_ANCHOR_CLOSE, else_=SCRIBE_EMIT_PAYLOAD)` — 14 = `tokens.ANCHOR_CLOSE` |
| `SCRIBE_EMIT_PAYLOAD` | `print_char(PUCK)`; `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_EMIT_ANCHOR_OPEN` | emit `<a href="` — let/print pairs for 60, 97, 32, 104, 114, 101, 102, 61, 34; `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_EMIT_ANCHOR_TITLE` | emit `" title="` — 34, 32, 116, 105, 116, 108, 101, 61, 34; `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_EMIT_ANCHOR_TEXT` | emit `">` — 34, 62; `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_EMIT_ANCHOR_CLOSE` | emit `</a>` — 60, 47, 97, 62; `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_EMIT_PARAGRAPH_OPEN` | emit `<p>` — 60, 112, 62; `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_TEST_FINAL_CLOSE` | `branch(eq(val(PROSPERO), const(0)), then=SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE, else_=SCRIBE_EMIT_PARAGRAPH_CLOSE)` |
| `SCRIBE_EMIT_PARAGRAPH_CLOSE` | emit `</p>\n\n` — 60, 47, 112, 62, 10, 10; `goto(SCRIBE_STREAM_CHECK)` |
| `SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE` | emit `</p>\n` — 60, 47, 112, 62, 10; `goto(SCRIBE_STREAM_CHECK)` |
| `ACT_IV_DONE` | `halt_act()` (`companion=PUCK`) |

Each "emit" row is a chain of `let(PUCK, const(code))` + `print_char(PUCK)`
pairs (39 `Speak your mind!` sites total, all Prospero's line, all matching
`_roles` with anchor Prospero). The anchor dispatch codes 11–14 must be
written as `src_ir.tokens` references in `act4.py`, not literals — that
module is the single definition shared with the future Act III port.

## `square(e)` stays out (addendum §A2 confirmed)

Every "the square of" in the Act IV fragment (10 occurrences) sits inside a
pure-constant phrase — e.g. `'='` = 61 as "square of 8 minus (1+2)", `'/'` =
47 as "square of (8−1) minus 2". The compiler decomposes constants through
`prose.value_phrase`, which may pick a different (behaviorally identical)
decomposition. No dynamic square exists in Act IV. The §A2 escape clause
remains reserved for Act III if a dynamic use appears there.

## 3H couplings (confirm after 3H ships, before writing 3I)

1. **Targets-only participants** — Act IV reads off-stage Horatio in two
   scenes. Also confirm 3H's rule for the *tested* character of a branch: at
   `ACT_IV_START` the tested char (Horatio) is off-stage, so the tested char
   must not count as a participant (this is the same shape as Act II's
   Horatio tests, so 3H already covers it — just verify the shipped code).
2. **Third-person questions** — "Is Horatio jollier than …?" at
   `ACT_IV_START`. Puck's `greater_than` pool already contains "jollier
   than".
3. **Goto entry adaptation is NOT exercised** (single pair act) — no risk.

## Accepted surface changes (behavioral parity only; G1/G2 unaffected)

- The hand fragment's two **first-person self-questions** ("Am I as noble as
  nothing?", Prospero testing his own count at `SCRIBE_STREAM_CHECK` and
  `SCRIBE_TEST_FINAL_CLOSE`) lower to second-person form: Puck asks "Are you
  as noble as nothing?" and Prospero speaks the If-arms. Same condition, same
  jump targets; matches addendum §A2's ruling that self-questions are a prose
  surface, not an IR op. No compiler change needed.
- Plain gotos are spoken by the anchor (Prospero, "We shall proceed/return
  to") where the hand fragment sometimes gives them to Puck ("Let us return
  to"). Same control flow.
- Constant phrases are re-decomposed by the prose engine; identical values.

## Debug play (`./shakedown-debug`)

Mechanism today: `scripts/assemble.py --debug` swaps
`40-act4-emit.spl` → `debug/40-act4-token-dump.spl` in the manifest and
writes `.cache/shakedown-debug.spl`; the `shakedown-debug` wrapper execs
`shakedown` against it. The debug fragment currently contains **no `@LIT.`
placeholders** — titles and the Recall line are literal text.

Decoded debug scenes (same anchor Prospero, same pair, same registers):

| Scene | Ops |
|---|---|
| `DBG_START` | `branch(gt(val(HORATIO), const(128)), then=DBG_OLD_MEASURE, else_=DBG_SHORT_MEASURE)` |
| `DBG_OLD_MEASURE` | `let(PROSPERO, const(387))`; `goto(DBG_LOOP)` |
| `DBG_SHORT_MEASURE` | `let(PROSPERO, val(HORATIO))`; `goto(DBG_LOOP)` |
| `DBG_LOOP` | `branch(eq(val(PROSPERO), const(0)), then=DBG_DONE, else_=DBG_POP)` |
| `DBG_POP` | `pop(PUCK, "heralds_present_word")`; `let(PROSPERO, sub(val(PROSPERO), const(1)))`; `print_int(PUCK)`; `let(PUCK, const(10))`; `print_char(PUCK)`; `goto(DBG_LOOP)` |
| `DBG_DONE` | `halt_act()` (`companion=PUCK`) |

Findings for the 3I plan:

1. **Sharing correction to addendum §A3.** "debug_act4.py imports scenes
   from act4.py" cannot be literal Scene reuse: labels, titles, and jump
   targets all differ, and `DBG_POP` has a different body by design. The real
   drift risk is the two magic numbers that must match the shipped act:
   the **128** threshold and the **387** Slice-1 stream count. Recommendation:
   `src_ir/act4.py` exports `STREAM_THRESHOLD = 128` and
   `SLICE_ONE_STREAM_COUNT = 387` (with the 387 ideally derived from the Act
   II push count at the source of truth); `src_ir/debug_act4.py` imports
   them and otherwise duplicates its four tiny setup scenes. A parameterized
   scene factory is YAGNI at this size.
2. **Ledger entries needed.** `validate()` requires every scene label in the
   merged literary ledger. The six `DBG_*` labels are in no TOML. Reserve
   them at 3I planning time by copying the already-authored hand titles
   verbatim (e.g. `DBG_LOOP` → "The scribe asks if words remain.") into
   `src/40-act4-literary.toml` (the loader globs `src/*-literary.toml`, so no
   loader change; the debug play is Act IV's shadow, so co-locating is
   cleaner than a new file).
3. **Generated-artifact placement.** `rendered_fragments()` in
   `scripts/splc/__main__.py` currently writes only into `src/`. The debug
   fragment lives at `debug/40-act4-token-dump.spl` (path hardcoded in
   `assemble.py --debug`). Simplest: keep that path and teach `main()` to
   render it there; extend the generated-fragment contract test to cover it.
   `@LIT.` resolution already works in debug mode because the swapped
   fragment goes through the same assemble pipeline.
4. **G2 ordering simplifies for 3I.** The token stream measured by
   `./shakedown-debug` is produced by acts 1–3 plus the debug dump — the real
   Act IV emit play never runs in debug mode. So the two ports are validated
   by *independent* instruments: (a) snapshot token streams with the current
   hand-authored debug play, port `debug_act4`, regenerate, compare — equal
   streams validate the debug port; (b) the `act4.py` port is validated
   directly by G1 fixture bytes (plus G3). §A3's "snapshot with the OLD debug
   play first" ordering still holds, but there is no circular dependency.

## Gate checklist for plan 3I (carry into the plan)

- G1: Amps fixture byte-identical (strict parity harness).
- G2: token-stream equality, snapshot taken with the hand-authored debug play
  before either port lands.
- G3: full default pytest suite green.
- Regen byte-identity for **both Act I and Act II** fragments after every
  compiler change (Act II joins the invariant set once 3H ships; 3I itself
  should need no lowering changes at all — flag any as scope creep).
- Literary compliance: no new prose pools; six `DBG_*` scene-title ledger
  entries reserved in the plan itself per
  `docs/superpowers/notes/correctness-first-spl-workflow.md`.
