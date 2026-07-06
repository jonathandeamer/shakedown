# Spike A Resumption — Dispatcher Skeleton + Lists, in IR — Design

**Date:** 2026-07-06
**Status:** approved design (operator-reviewed in interactive session)
**Resumes:** Spike A (architecture spec §7.3, as revised 2026-07-06), halted
2026-07-05 and mechanically resolved by the splc compiler
(`docs/superpowers/specs/2026-07-05-spl-ir-compiler-design.md`, plans 3G–3J)
**Companion revision:** the 2026-07-06 in-place revision of
`docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`
(§2, §4.2, §5.3, §6.3, §7.3, §8.2, §8.4)

## Problem

The original Spike A halted before it could answer its own question: it was
supposed to validate the multi-pass dispatcher and frame-sentinel nesting,
but hand-authored SPL never reached a parseable state. splc removed the
authoring confound. The dispatcher design is therefore **unvalidated, not
invalidated**, and the resumed spike is its first real test.

The spike cannot simply "add lists" to Act II. The Slice-1 Act II is a
pass-through that emits raw paragraph glyphs framed by `1`/`0` markers — not
the §4.2 token vocabulary. List tokens force the inter-act stream contract
into existence, and that contract touches Acts II, III, IV, and the debug
dump. This design covers the dispatcher skeleton, the stream contract, and
the list pass at the original spike's Markdown scope. It deliberately does
not design the header, HR, code-block, blockquote, or HTML-rehash passes;
they get named slots in the pass ordering and nothing more.

## Decision summary (operator-approved)

1. **Dispatcher skeleton + lists**, not a minimal list bolt-on and not the
   full §4.2 vocabulary. The spike validates the architecture it was created
   to validate; later slices land passes into a stable frame.
2. **Tokenized stream contract** with a single arity-table definition in
   `src_ir/tokens.py`. The G2 token-stream snapshot breaks **once,
   deliberately**, and is re-blessed.
3. **Two implementation plans**: (P1) stream migration + skeleton with
   `PARA` only, all fixtures stay green; (P2) the list pass proper.

## The stream contract

The Slice-1 stream is already almost a token stream: `1, <glyphs…>, 0` per
paragraph reads as `PARA` (code 1), text payload, terminator. The contract
generalizes this rather than replacing it.

**A token is:**

1. an integer **code** from the canonical table (`docs/spl/token-codes.md`,
   mirrored in `src_ir/tokens.py`);
2. a **fixed number of integer payloads** determined by the code;
3. for text-bearing tokens, a **glyph run terminated by `0`** (glyphs are
   always ≥ 1, so `0` is unambiguous).

**Spike-scope vocabulary** (payload contract carried over from the halted
spike plan, which still holds):

| Token | Code | Fixed payloads | Text |
|---|---|---|---|
| `PARA` | 1 | — | yes |
| `LIST_OPEN` | 4 | kind: 1 = unordered, 2 = ordered | no |
| `LIST_ITEM` | 5 | looseness: 1 = tight, 2 = loose | yes |
| `LIST_CLOSE` | 6 | — | no |

**The arity table** — `code → (payload count, has-text flag)` — is defined
once in `src_ir/tokens.py` and consumed by Act II emission, Act III
traversal, Act IV dispatch, and `debug_act4.py`. Contract drift becomes
structurally impossible: there is exactly one definition to change.

**Act III traversal rule:** copy token codes and fixed payloads through
untouched; run the span gamut only on text-payload glyphs. Act III's 56 span
scenes are unchanged; only the traversal entry becomes token-aware.

**G2 break (deliberate):** token-stream equality cannot hold across a stream
format change. Procedure: record the old debug dump on the fixed input set,
implement, review the new dump once against the contract by hand, bless it
as the new G2 baseline. All subsequent work (P2, Spike B, Slices 2+) is
gated against the new baseline.

## Dispatcher skeleton

The multi-pass shape from §4.2, realized as IR conventions — **no new splc
machinery is expected**. If list recognition surfaces a genuine expression
or op gap, the instruction set is extended with tests per the splc design's
no-escape-hatch rule; it is never bypassed.

- **A pass is a scene group, not an IR construct.** Each pass is a
  contiguous run of scenes in `src_ir/act2.py` sharing a label prefix
  (`PASS_LISTS_*`, `PASS_PARA_*`), consuming the stream from one character's
  stack and producing onto another.
- **Stack ping-pong.** Hecate delivers Act I's normalized text, as today.
  Passes alternate Lady Macbeth and Macbeth as stream carriers. Each
  pop/push pass reverses stream order; the design tracks pass parity, with
  an explicit final reverse onto Puck (as `HERALD_REVERSE_TOKEN_STREAM`
  does now) making order restoration unconditional.
- **Frame sentinels live on Macbeth's stack** (resolves the §6.3 deferred
  question). Constraint imposed on all future passes: a pass that needs
  nesting frames must not simultaneously use Macbeth as its ping-pong
  destination. The list pass obeys this by reading from Lady Macbeth and
  writing to Puck's staging. Spike B's blockquote composition reuses the
  same sentinel stack sequentially, not concurrently.
- **Pass ordering** (matching `_RunBlockGamut`): headers → horizontal rules
  → **lists** → code blocks → blockquotes → HTML re-hash → **paragraph
  formation**. The spike implements only the bolded passes plus the
  line-assembly evolution of the current Mason scenes and the final
  reverse. Unimplemented passes are named slots, each added by the slice
  whose fixtures force it.
- **One-boolean discipline** (§6.5) is already structural in the IR:
  `branch` renders question and consequence adjacently by construction.

## The list pass at spike scope

Mechanics from `docs/markdown/list-mechanics.md`, scoped to the six snippet
fixtures already committed under `tests/fixtures/architecture_spikes/lists/`
(currently xfailed with the halt reason):

- **Marker recognition:** `*`, `+`, `-` and `digits.`; up to 3 leading
  spaces; required whitespace after the marker. The first marker fixes the
  `LIST_OPEN` kind payload (`<ul>` vs `<ol>`).
- **Top-level gate:** a list opens only at document start or after a blank
  line — the `hard_wrapped_boundary` fixture (`8. Oops`) is the oracle case.
- **Tight/loose:** a blank line before or inside an item marks it loose
  (looseness payload 2). Loose item text is paragraph-wrapped by Act IV;
  tight items receive span-gamut-only treatment.
- **One nesting level:** a deeper-indented sublist marker pushes a frame on
  Macbeth and emits a nested `LIST_OPEN`; outdent pops the frame and emits
  `LIST_CLOSE`.
- **Indented continuation:** 4-space-indented lines inside an item join the
  item's text. There is no code-block pass yet, and Markdown.pl orders lists
  before code blocks precisely so this content stays in the item.

**Not in scope** (unchanged from the original spike): full
`Ordered and unordered lists` fixture, all marker-family variants,
list-with-blockquotes, nested loose-list combinations — Slice 4 territory.

## Cross-act impact

- **Act I:** unchanged.
- **Act II:** rewritten from pass-through to dispatcher skeleton. P1 may
  not change fixture-visible behavior: the Slice-1 quirks (fixed reverse
  count 315 above 128 glyphs) are preserved unless the tokenized stream
  makes one structurally unnecessary, and any such retirement must be
  invisible to G1/G3.
- **Act III:** gains the token-walking traversal header per the arity
  table; span scenes untouched.
- **Act IV:** dispatches on token code. A small list-kind stack (Prospero's
  own stack suffices at one nesting level) chooses `</ul>` vs `</ol>`;
  loose items get `<p>` wrapping. New emission scenes for the three list
  tags.
- **Debug act:** dumps the new stream format via the shared arity table.

## Verification gates

| Gate | P1 (stream migration) | P2 (list pass) |
|---|---|---|
| G1 | `Amps and angle encoding` byte-identical | same |
| G2 | old dump recorded, new dump hand-reviewed once, re-blessed as baseline | equality against P1's blessed baseline |
| G3 | full default suite green | same, plus the six list spike tests un-xfailed and byte-identical to the oracle |
| Regen | Acts I–IV + debug regen byte-identical after any compiler change | same |

Halt trigger (§8.2, revised): if the resumed spike struggles **in IR**, the
pass decomposition itself is implicated — halt and revisit architecture
spec §4.

## Plan staging

Two plans, written one at a time per roadmap policy, after 3J ships:

1. **P1 — Tokenized stream + dispatcher skeleton.** `PARA` tokens only;
   arity table in `src_ir/tokens.py`; Acts III/IV/debug migrate to the
   contract; pass frame and final reverse in place; every existing fixture
   stays green. A cheap failure here is the spike doing its job.
2. **P2 — List pass.** `LIST_OPEN`/`LIST_ITEM`/`LIST_CLOSE` at spike scope;
   frame sentinels on Macbeth; Act IV list emission; six spike fixtures
   pass.

Roadmap gets one row per plan when each is written. Spike B follows P2.

## Literary implications

All new scene titles and pool material are reserved in `src/literary.toml`
at planning time (correctness-first workflow; the compiler turns a missing
entry into a build error). Rough budgets, fixed exactly by each plan:

- **P1:** ~10–14 new Act II scenes (pass frame, paragraph pass, reverse),
  plus Act III traversal-entry scenes and Act IV dispatch scenes.
- **P2:** ~15–20 new Act II scenes (marker recognition, item buffering,
  tight/loose, nesting), plus Act IV list-emission scenes.
- Macbeth (the Apprentice) speaks in production scenes for the first time;
  his Martial/Catastrophic, doubt-shadowed pool material may need extending
  — a planning-time TOML task per the splc design's pool-sufficiency
  mitigation.

## Risks and mitigations

- **The G2 re-bless is a one-time loss of the strongest gate.** Mitigation:
  it happens in P1, where `PARA`-only traffic makes the new dump small and
  hand-reviewable; P2 and everything after re-gains full G2 protection.
- **Act III traversal change regresses the freshly ported act.** Mitigation:
  G1 plus the full suite catch behavioral drift; the traversal header is
  additive (span scenes untouched); regen gates keep the compiler honest.
- **Pass parity bookkeeping (stream reversal) is error-prone.** Mitigation:
  the explicit final reverse onto Puck makes order restoration
  unconditional rather than parity-dependent; the debug dump makes stream
  order directly observable.
- **Macbeth's dual role (carrier vs. frame holder) is a latent conflict.**
  Mitigation: the constraint is stated in §6.3 and this design; splc's
  stage-discipline validation catches co-presence violations at build time.

## References

- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` —
  §4.2 (dispatcher + stream contract), §6.3 (sentinel ownership), §7.3
  (spike scope), §8.2 (halt triggers), all as revised 2026-07-06
- `docs/superpowers/specs/2026-07-05-spl-ir-compiler-design.md` — splc
  design; no-escape-hatch rule; pool-sufficiency mitigation
- `docs/superpowers/plans/2026-05-01-spike-a-lists.md` — the halted plan;
  source of the token payload contract and snippet fixtures
- `docs/markdown/list-mechanics.md` — Markdown.pl list behavior
- `docs/spl/token-codes.md` — canonical token codes
- `docs/superpowers/notes/correctness-first-spl-workflow.md` — planning-time
  prose reservation
- branch `spike-a-lists-wip` — failure specimen from the original spike
