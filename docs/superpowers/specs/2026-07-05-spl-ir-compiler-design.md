# SPL-from-IR Compiler (`splc`) — Design

**Date:** 2026-07-05
**Status:** approved design (operator-reviewed in interactive session)
**Resolves:** the Spike A §8.2 halt recorded in `docs/superpowers/plans/plan-roadmap.md` and `.agent/blockers.md`
**Supersedes:** the hand-authoring model of `src/*.spl` described in the architecture spec §5.3; all other architecture-spec decisions (four-act pipeline, token stream, character ownership, multi-pass dispatcher, frame-sentinel nesting) stand unchanged.

## Problem

Spike A halted because hand-authoring SPL at scale does not work: the Act II
list pass grew a ~1,300-line diff that never reached a parseable state
(preserved on branch `spike-a-lists-wip`). The failure class was long-range
bookkeeping — enter/exit choreography, question/conditional adjacency, scene
plumbing — not Markdown semantics. Agents are strong at Python and weak at
maintaining internal consistency across thousands of lines of adversarial
syntax. The repo is already half a compiler (assembler with label resolution,
`@LIT.` placeholder resolution, TOML-owned value atoms, `codegen_html.py`
byte-phrase emitters, an assemble-time parse gate, a token-stream debug
target). This design finishes the job.

## Decision Summary (operator-approved)

1. **Full port, staged.** The compiler becomes the sole producer of
   `shakedown.spl`. All four hand-authored acts are ported to IR, one act per
   plan task, gated by behavior parity. No permanent hybrid.
2. **Python eDSL IR.** Agents author typed Python modules under `src_ir/`
   using a small, closed builder API. No TOML macro layer, no custom parser.
3. **Literary compliance by construction.** All rendered prose comes from
   `src/literary.toml` pools, deterministically seeded. Source-scanning
   compliance tests that become tautological are retired or retargeted at the
   TOML and the compiler's own tests.

Parity is **behavioral, not textual**: generated SPL will not match the
hand-authored play byte-for-byte (prose differs), but fixture output bytes
and the inter-act token stream must be identical.

## Architecture

```
src_ir/act1.py … act4.py, cast.py, tokens.py     (authored IR)
        │  build (import, collect scenes)
        ▼
scripts/splc/  validation                        (labels, literary keys,
        │                                         stage discipline, atoms)
        ▼
scripts/splc/  lowering → SPL text               (prose from src/literary.toml,
        │                                         values via codegen atoms)
        ▼
parse gate (existing scripts/assemble.py _parse_check, reused)
        ▼
shakedown.spl                                    (still committed; CI verifies
                                                  it matches compiler output)
```

### Components

- **`src_ir/`** — the authored source of truth after the port.
  - `cast.py`: the fixed dramatis personae as an enum (Rosalind, Horatio,
    Puck, Hecate, Lady Macbeth, Macbeth, Romeo, Juliet, Prospero). The cast
    is closed; adding a character is an architecture change, not an IR edit.
  - `tokens.py`: token codes imported from the canonical table
    (`docs/spl/token-codes.md` values); one definition, used by both Act II
    emission and Act IV dispatch.
  - `act1.py` … `act4.py`: one module per act, exporting `ACT: Act`.
  - `debug_act4.py`: the token-dump act (replaces the hand-authored
    `debug/40-act4-token-dump.spl`); shares stream-count scenes with `act4.py`
    by importing them — drift between production and debug Act IV becomes
    impossible.
- **`scripts/splc/`** — the compiler package.
  - `ir.py`: frozen dataclasses for the instruction set (below) plus the
    builder functions. This is the entire authoring surface.
  - `validate.py`: build-time checks (see Validation).
  - `prose.py`: the literary engine (see Literary Engine).
  - `lower.py`: IR → SPL text, including computed stage choreography.
  - `__main__.py` / integration: `scripts/assemble.py` remains the CLI entry
    point (`--debug` included) so `./shakedown`, `./shakedown-debug`, CI, and
    tests do not change. During the port it composes generated acts with
    remaining hand-authored fragments via `src/manifest.toml`; after the port
    the manifest lists generated acts only.

## The IR — closed instruction set

Scenes are states in a state machine; ops are the only vocabulary. There is
deliberately **no escape hatch** to raw SPL — if the instruction set cannot
express something, the instruction set gets extended (a compiler change with
tests), not bypassed.

**Expressions** (evaluate to integers):
- `const(n)` — rendered via the canonical atom pool; Critical constants
  (token codes, sentinels) always use their canonical phrase
- `ch("*")` — character literal, sugar for `const(42)`
- `val(PUCK)` — a character's current value
- `add(e1, e2)`, `sub(e1, e2)`, `mul(e1, e2)`, `div(e1, e2)`, `mod(e1, e2)`
- `twice(e)`, `half(e)`, `square(e)`

**State ops:**
- `let(CHAR, expr)` — assignment ("You are as … as …")
- `push(CHAR, expr)` — Remember
- `pop(CHAR)` — Recall (noun phrase drawn from the character's Recall pool)
- `reset(CHAR)` — sugar for `let(CHAR, const(0))`

**I/O ops:**
- `read_char(CHAR)` — Open your mind
- `print_char(CHAR)` — Speak your mind
- `print_int(CHAR)` — Open your heart

**Control:**
- `branch(cond, then="LABEL", else_="LABEL" | None)` — question plus
  If so / If not; `cond` is `eq(e1, e2)`, `gt(e1, e2)`, or `lt(e1, e2)`
- `goto("LABEL")` — unconditional jump
- `halt()` — end of play ([Exeunt] at the final scene)
- Fallthrough between scenes is **forbidden**: validation rejects any scene
  that does not end in `goto`, an exhaustive `branch`, or `halt`. Implicit
  fallthrough was a hand-authoring bug source; making control flow total is
  cheap in the IR.

**Structure:**
- `scene("LABEL", *ops)` — label must be a key in `src/literary.toml`
  `[scenes.*]`
- `act(n, [scenes])` — act number fixes heading and (via prose pools) palette

Token emission is not a special op: it is `push(PUCK, tokens.LIST_OPEN)`
against the stream-carrier character, same as the current convention.

### Computed stage choreography

The single largest by-construction win. The lowering pass — not the author —
derives:

- **Enter/Exit/Exeunt directions** from which characters each scene's ops
  touch, inserting minimal stage movements between scenes
- **Speaker/addressee assignment** per SPL's second-person semantics (an op
  on CHAR is spoken *to* CHAR by a legal co-present speaker)
- **Question/conditional adjacency** — `branch` always renders the question
  and its `If so,`/`If not,` lines in the legal order and positions

This is exactly the bookkeeping class that produced the spike's fatal
`negative_if` parse error. Authors never see it.

### Validation (build-time, before any SPL is rendered)

Every violation is an error naming the IR file/scene, not a downstream SPL
parse error:

1. Every jump target is a defined scene label in the same act.
2. Every scene label has a `[scenes.LABEL]` TOML entry (replaces the
   ledger-sync scanning test).
3. Control flow is total (no fallthrough; `halt` reachable).
4. Stage discipline is satisfiable (every op has a legal speaker; scenes
   never require more simultaneous characters than SPL addressing allows).
5. Every `const` decomposes into legal atoms; Critical constants match their
   canonical phrases.
6. Duplicate scene labels rejected (per act, matching assembler semantics).

The existing parse gate remains as a belt-and-braces final check, but a
validated program failing it is a compiler bug, not an author error.

## Literary Engine (`prose.py`)

All rendered prose comes from `src/literary.toml`; the compiler never invents
prose, and authors never write prose in IR modules — consistent with
`docs/superpowers/notes/correctness-first-spl-workflow.md` (prose is authored
at planning time, in the TOML).

- **Scene titles:** by label key, as today.
- **Dialogue phrasing:** per-character pools — question forms, assignment
  forms, Recall noun phrases (e.g. Lady Macbeth's "Are you as mighty as …"
  vs Prospero's "Are you as noble as …"). Pool selection is seeded by a hash
  of the scene label plus op index: deterministic, stable across rebuilds
  (no spurious `shakedown.spl` diffs), varied within a character's voice.
- **Values:** rendered through the existing `codegen_html.py` atom machinery
  and the `[value_atoms]` pools; the canonical token-code phrases from
  `docs/spl/token-codes.md` are Critical and never vary.
- **Act headings, dramatis personae, iconic moments:** TOML-keyed, emitted
  once by the compiler.

New scenes therefore still require a planning-time TOML entry (title + any
new pool material), preserving the reserved-prose workflow; the compiler
turns a missing entry into an immediate build error.

## Compliance-test migration

| Current test class | Fate |
|---|---|
| Ledger sync, `@LIT.` resolution, placeholder discipline | Replaced by compiler validation + its unit tests |
| Atom canonicality, no-repeated-chains, numeric-recipe bounds | Compiler unit tests on `prose.py`/`lower.py` output |
| Aesthetic policy (motif visibility, verb variety, speaker pools, palettes) | Retargeted at the **TOML pools** (the authored artifact), not rendered SPL |
| Parse/behavior gates (parse smoke, mdtest, token dump, binary contract) | Unchanged |

Nothing scans generated SPL for style. Generated SPL is checked for exactly
two things: it parses, and it behaves.

## Staged port

> **Superseded for stages 2–4:** the line counts below were stale (Act II's
> figure came from the spike WIP branch). See Addendum §A1 for the corrected
> staging, approved after the stage-1 port shipped.

Order is smallest-first to shake out IR gaps at the lowest cost:

| Stage | Act | Hand-authored lines | Gate |
|---|---|---|---|
| 1 | Compiler core + Act I | 233 | G1–G3 |
| 2 | Act IV (+ `debug_act4` from shared scenes) | 461 | G1–G3 |
| 3 | Act III | 1,285 | G1–G3 |
| 4 | Act II | 1,467 | G1–G3, spike xfails re-examined |

**Gates, per stage:**
- **G1 — fixture parity:** `Amps and angle encoding` byte-identical via the
  strict parity harness.
- **G2 — token-stream equality:** `shakedown-debug` dump over a fixed input
  set is identical before and after the stage (pins the inter-act contract
  exactly for Acts I–III; for Act IV, G1 is the semantic gate and G2 confirms
  upstream acts undisturbed).
- **G3 — full default suite green** plus the parse gate on every build.

A hand-authored fragment is deleted only when its generated replacement
passes all gates in the same task. The `spike-a-lists-wip` branch stays
untouched as design reference for the eventual list pass.

**End state:** `src/*.spl` is gone; `src_ir/` + `src/literary.toml` are the
only authored sources; `shakedown.spl` remains committed and CI-verified
against compiler output. The Spike A halt resolves, and the replacement list
plan is written in IR.

## Testing strategy (compiler itself)

- Unit tests per module: expression rendering (value → phrase → parses back
  via `parse_value_phrase`), choreography lowering (op sequences → legal
  stage/speaker plans), validation rejections (one test per error class).
- Golden tests: small IR programs → full SPL text snapshots, parse-gated and
  executed against expected stdout (reusing the minimal-play pattern from
  `tests/test_wrapper_error_channel.py`).
- The behavior gates (G1–G3) are the integration tests; no new harness
  needed.

## Non-goals

- List semantics, Slice 2+ Markdown features (next plan, written in IR).
- Interpreter performance work (in-process AST reuse is a separate spike).
- IR support for SPL features the play does not use (no `Listen to your
  heart` integer input, no multi-play linking) — YAGNI until an act's port
  demands it.
- Prose authoring tools; the TOML remains hand-curated at planning time.

## Risks and mitigations

- **Choreography lowering is the hard part.** Mitigation: it is pure
  Python with property-style unit tests; Act I (smallest, simplest cast
  usage) is the first consumer.
- **Per-character pools may be too thin for full-act generation**, making
  output repetitive. Mitigation: pool sufficiency surfaces during the Act I
  port as a build warning ("pool X exhausted for scene run"); extending a
  pool is a planning-time TOML task, and aesthetic tests point at the pools.
- **Token-stream gate needs a before-snapshot.** Each port task records the
  dump outputs on the fixed input set *before* swapping the act, in the same
  task, so equality is checked against the actual predecessor, not an
  assumption.
- **Hidden semantics in hand-authored acts** (e.g. Act I's Slice 1
  reference-definition stripping quirk, see `.agent/blockers.md` history).
  Ports translate behavior as-is, quirks included; behavior changes are out
  of scope for the port and belong to later feature plans.

## Addendum — Acts II–IV Port (2026-07-05, operator-approved)

Written after the stage-1 (Act I) port shipped at commit 3c5b521. Corrects
stale inputs in the Staged port section and closes the gaps the Act I port
exposed. Everything else in this design stands unchanged.

### A1. Corrected staging

The original stage table counted Act II at 1,467 lines — that figure came
from the spike WIP branch, not main. On main, Act II is a 183-line
pass-through (the list logic was never merged). Smallest-first, applied to
the real numbers, gives the corrected order:

| Stage | Plan | Act | On main | Gate |
|---|---|---|---|---|
| 2 | 3H | Act II (pass-through) | 183 lines, 13 scenes | G1–G3 + error contract (A4) |
| 3 | 3I | Act IV + `debug_act4` shared scenes | 461 lines, 20 scenes | G1–G3 (order per A3) |
| 4 | 3J | Act III | 1,285 lines, 56 scenes | G1–G3, spike xfails re-examined |

One roadmap row per plan. List semantics never land in a port plan: they
arrive afterwards as the resumed Spike A plan, written directly in IR
against the fully ported play.

### A2. IR extensions (audit-backed, closed)

A construct audit of `src/20-act2-block.spl`, `src/30-act3-span.spl`,
`src/40-act4-emit.spl`, and `debug/40-act4-token-dump.spl` against the
implemented `scripts/splc/ir.py` found exactly one missing expression:

- **Add `square(e)`** — `the square of` appears 48 times, all in Act III.
- **Drop the promised `twice`/`half` builders** — zero uses in any act;
  YAGNI per this design's own non-goals. The instruction-set listing above
  is amended accordingly.
- **Self-questions are prose, not ops.** Acts III/IV use "Am I as …" when a
  speaker tests their own value. This is a question-form selection in
  `prose.py` (per-character self-question pool entries), not an IR change.

No other gaps: every statement in Acts II–IV maps to the existing op set.
Any further gap discovered mid-port is handled per the no-escape-hatch rule
(extend the instruction set with tests; never bypass).

### A3. Multi-act composition and the debug act

- `src/manifest.toml` continues to list fragments in order; each stage swaps
  one hand-authored fragment for a generated one, following the Act I
  pattern including the per-act literary TOML convention
  (`src/20-act2-literary.toml` etc. already exist).
- Stage 3 delivers `src_ir/debug_act4.py` importing the stream-count scenes
  from `act4.py`, replacing `debug/40-act4-token-dump.spl`. Because the
  debug play is itself the G2 instrument, stage 3's gate order is explicit:
  record the G2 snapshot with the **old** debug play before the swap; after
  the swap, G1 is the semantic gate and the new debug play must reproduce
  the identical dump on the fixed input set.
- Act III (56 scenes) is the prose-pool stress test. Its plan reserves all
  56 scene titles plus any new pool material in the TOML up front (existing
  correctness-first policy), and the pool-exhaustion build warning promised
  above must be implemented by stage 4 at the latest.

### A4. Deliberate runtime-error contract (lands in stage 2 / plan 3H)

The contract is wrapper-level: when the interpreter raises an SPL runtime
error, `./shakedown` exits nonzero and writes `SPL runtime error:` to
stderr. The xfailed
`tests/test_binary_contract.py::test_repo_shakedown_entrypoint_reports_spl_runtime_errors`
proved this only by accident — it relied on the pre-f45b626 play crashing
on `AT&T` input. Restore coverage by retargeting: a minimal deliberately
erroring play fixture driven through the wrapper (the
`tests/test_wrapper_error_channel.py` minimal-play pattern), replacing the
xfailed test. The production play is not required to error on any real
input. Plan 3H replaces the test and removes the corresponding half of the
`.agent/blockers.md` entry; the Spike A halt line itself clears when 3J
ships and the resumed list plan is written.

## References

- `docs/superpowers/plans/plan-roadmap.md` — halt record and staging ladder
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — the
  four-act architecture this compiler serves (§4, §5.3b, §8.2)
- `docs/spl/reference.md`, `docs/spl/verification-evidence.md` — SPL legality
- `docs/spl/token-codes.md` — canonical Critical constants
- `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`,
  `docs/spl/codegen-style-guide.md` — prose policy feeding the TOML pools
- `docs/superpowers/notes/correctness-first-spl-workflow.md` — planning-time
  prose authorship rule this design mechanizes
- `scripts/codegen_html.py` — atom machinery reused by `prose.py`
- branch `spike-a-lists-wip` — the failure specimen motivating this design
