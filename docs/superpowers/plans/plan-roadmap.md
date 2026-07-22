# Implementation Plan Roadmap

**Last updated:** 2026-07-19
**Purpose:** live index of the staged implementation plans for Shakedown,
so any session — interactive or autonomous — can see what has shipped,
what is in flight, and what is still pending.

This is the entry point for "what plans exist and in what order?". The
plans themselves live alongside this file under
`docs/superpowers/plans/YYYY-MM-DD-<name>.md`.

## Staging philosophy

Shakedown's implementation work decomposes naturally into eight
shipping units (architecture spec §7). We write **one plan at a time**,
not all eight up front. Reasoning:

- **Halt-and-redesign is cheap by design.** Architecture spec §8.2
  explicitly flags Spike A and Spike B as halt triggers. Plans for
  Slice 3 onwards may need to change shape after Spike A teaches us
  how the dispatcher actually behaves under list pressure. Writing
  those plans today wastes work if a redesign invalidates them.
- **Plans decay.** Bite-sized step-by-step plans are accurate when
  written against current reality. Speculative plans for slices that
  haven't started yet age fast — file paths drift, function signatures
  change, learnings invalidate assumptions.
- **The architecture spec is the durable plan.** Slice ordering, the
  fixture-to-slice inventory (§7.8a), per-slice verification gates
  (§8.1), and halt-and-redesign triggers (§8.2) are already locked.
  Each implementation plan is the bite-sized expansion of one slice
  against an unchanged backdrop.
- **Token economics.** Eight detailed plans is ~250+ tasks. Writing
  them all up front is cheap once but expensive to rewrite. Writing
  one at a time keeps each plan tight and current.

The trade-off accepted: more planning sessions, more operator review
gates. The win: every plan is written against ground truth.

## Plan ladder

| # | Plan | Architecture §  | Ships | Verification gate | Status |
|---|---|---|---|---|---|
| 1 | Pre-Slice-1 Setup | §7.1 | All 10 §7.1 deliverables (parity harness, wrapper, assembler, codegen, `src/literary.toml` schema + Slice 1 entries, Stable Utility families, token-code allocation, cache spike outcome, generated-artifact policy, run-loop prompt, iconic-moment maps) plus `.agent/blockers.md` and the `cz bump` operator-only convention documented | All setup unit tests pass; every §7.1 deliverable exists and is committed; cache spike has a decided outcome (proven or fallen back); `run-loop` finds `docs/prompt-shakedown.md` and reads its university references | shipped: 2026-04-28 at commit e9fe5d0 |
| 2 | Slice 1 — Amps and angle encoding | §7.2 | First fixture passing byte-identical via SPL through all four acts; minimal anchor machinery (inline + full reference links with optional titles) | §8.1 four-gate: fixture pass, byte-identical to oracle (strict parity harness §7.1 #6), no regression, no oracle stub. Cuts `0.1.0` per CLAUDE.md milestone policy | superseded: 2026-04-29 by Slice 1 Halt Resolution after §8.2 line-budget halt |
| 2R | Slice 1 Halt Resolution | §8.2 halt resolution for §7.2 | Replace fixture-specific unrolling and full hardcoded anchor output scenes while preserving byte-identical Slice 1 behavior | Structural regression gate passes; Slice 1 strict parity remains byte-identical; runtime is re-recorded; `.agent/blockers.md` line is removed only after proof | shipped: 2026-04-30 at commit 58f80661a04d5da8ca1b8733c2dfe39f04195c94 |
| 2P | Literary Prevention Rails (`docs/archive/plans/2026-04-30-literary-prevention-rails.md`) | §7.1 support / literary prevention design | Teach assembler/codegen and future prompt authors to consume `src/literary.toml` for controlled SPL literary surfaces; add `@LIT.` placeholder resolution, TOML-backed value atoms, prompt gates, and production literary compliance rails | Exact plan path is present in this row; active prompt can discover it; final literary surface audit passes; implemented mdtest fixtures remain byte-identical | shipped: 2026-05-01 at commit 78e0c53 |
| 3 | Spike A — Lists at minimum viable scope (`docs/archive/plans/2026-05-01-spike-a-lists.md`) | §7.3 | Multi-pass dispatcher + frame-sentinel pattern validated on flat tight/loose lists, one nesting level, one indented continuation. Snippet fixtures committed under `tests/fixtures/architecture_spikes/lists/` | Spike snippets pass byte-identical to oracle through `tests/test_architecture_spikes.py`; dispatcher shape confirmed or halt-and-redesign triggered | halted: 2026-07-05 per §8.2 — hand-authored Act II list SPL never reached a parseable state; WIP preserved on branch spike-a-lists-wip; resume after the SPL-from-IR architecture revision |
| 3F | Agent Feedback Rails (`docs/archive/plans/2026-07-05-agent-feedback-rails.md`) | §8.2 halt support / tooling | Wrapper parse-error guard, assemble-time parse gate, parse smoke test, token-stream debug target (`./shakedown-debug`), correctness-first literary workflow note, Spike A halt recorded | Default pytest suite green (spike list cases xfail with halt reason); wrapper exits nonzero on parse errors; debug target dumps an integer token stream for the Amps fixture | shipped: 2026-07-05 at commit c58f993 |
| 3G | splc Compiler + Act I Port (`docs/archive/plans/2026-07-05-splc-act1.md`) | §8.2 halt resolution stage 1 (`docs/superpowers/specs/2026-07-05-spl-ir-compiler-design.md`) | splc compiler package (IR, validation, prose engine, lowering), `src_ir/act1.py`, `src/10-act1-preprocess.spl` as generated artifact, generated-fragment contract test | G1 Amps fixture byte-identical; G2 token-stream equality; G3 full default suite green | shipped: 2026-07-05 at commit 3c5b521 |
| 3H | splc Act II Port (`docs/archive/plans/2026-07-05-splc-act2.md`) | §8.2 halt resolution stage 2 (design Addendum §A1–A4) | Targets-only stage pairs, third-person questions, and goto entry adaptation in splc; `src_ir/act2.py`; `src/20-act2-block.spl` as generated artifact; wrapper runtime-error contract restored (minimal erroring play test replaces the accidental xfailed binary-contract test) | G1 Amps fixture byte-identical; G2 token-stream equality against pre-port snapshot; G3 full default suite green; Act I regen byte-identical after every compiler change | shipped: 2026-07-05 at commit 7f43f69 |
| 3I | splc Act IV Port (`docs/archive/plans/2026-07-05-splc-act4.md`) | §8.2 halt resolution stage 3 (design Addendum §A3) | `src_ir/act4.py` (20 scenes, anchor Prospero), `src_ir/debug_act4.py` (6 DBG_* scenes), `src/40-act4-emit.spl` and `debug/40-act4-token-dump.spl` as generated artifacts; inlined DBG_* debug titles; shared threshold/count constants | G1 Amps fixture byte-identical; G2 token-stream equality (debug snapshot before port); G3 full default suite green; Act I and Act II regen byte-identical | shipped: 2026-07-05 at commit 67d12a7 |
| 3J | splc Act III Port (`docs/archive/plans/2026-07-05-splc-act3.md`) | §8.2 halt resolution stage 4 (design Addendum §A1; audit: `docs/superpowers/notes/act3-port-audit.md`) | Per-scene anchor override in splc; `src_ir/act3.py` (56 scenes, four stage pairs); `src/30-act3-span.spl` as generated artifact; shared 128/315/387 constant homes; spike xfails re-examined | G2 token-stream equality (primary semantic gate — the debug dump measures acts 1–3); G1 Amps fixture byte-identical; G3 full default suite green; Acts I/II/IV + debug regen byte-identical after every compiler change | shipped: 2026-07-06 at commit a2f47c5 |
| 3K | Spike A P1 — Tokenized stream + dispatcher skeleton (`docs/archive/plans/2026-07-06-spike-a-p1-stream-skeleton.md`) | §4.2/§7.3 as revised 2026-07-06 (`docs/superpowers/specs/2026-07-06-spike-a-ir-lists-design.md`, stage P1) | Arity table + framing markers (`src_ir/tokens.py`, `docs/spl/token-codes.md`); Act II rebuilt as dispatcher skeleton (`PASS_PARA_*` pass + `FRAME_REVERSE_*` final reverse); sentinel-terminated stream traversal in Acts III/IV/debug; Slice-1 fixed counts (128/315/387) retired; blessed G2 dump baselines committed under `tests/fixtures/token_stream/` | G1 Amps byte-identical; G2 pre-migration dumps recorded, Amps dump byte-equal, short dump hand-reviewed against the contract and blessed as committed baseline; G3 full default suite green (list spikes stay xfailed until P2); regen byte-identical for untouched fragments after every task | shipped: 2026-07-06 at commit 269f770 |
| 3L | Spike A P2 — List pass at spike scope (`docs/archive/plans/2026-07-07-spike-a-p2-list-pass.md`) | §7.3 as revised 2026-07-06 (`docs/superpowers/specs/2026-07-06-spike-a-ir-lists-design.md`, stage P2) | `LIST_OPEN`/`LIST_ITEM`/`LIST_CLOSE` at spike scope; frame sentinels on Macbeth; looseness side channel + `ITEM_START` intra-act marker; Act III arity dispatch; Act IV list emission; Macbeth's first production scenes | G2: amps/short dumps byte-equal to 3K's blessed baselines at every task boundary, six new list dumps hand-reviewed against the plan's expected streams and blessed; six list spike fixtures un-xfailed and byte-identical to the oracle; full default suite green | shipped: 2026-07-07 at commit 19b64fe |
| 3M | Completion Safety Rails (`docs/superpowers/plans/2026-07-11-completion-safety-rails.md`) | Completability hardening (`docs/superpowers/specs/2026-07-11-completability-hardening-design.md`, stage 1) | Verification-only IR interpreter; executable stack/sentinel contracts; structural token validation; all-fixture differential smoke report; measured feedback acceleration; MCO-only roadmap executor with role-scoped model failover | Fast interpreter equals committed token dumps; borrowed-stack prefixes and sentinels validated; malformed streams rejected; all 23 fixtures reported non-gating; MCO action/model/failover tests pass without secret leakage; generated SPL byte-identical; full default suite green | shipped: 2026-07-12 |
| 3N | Agent Loop Provider Pool Refresh (`docs/superpowers/plans/2026-07-12-agent-loop-provider-pool-refresh.md`) | Loop infrastructure follow-up (`docs/superpowers/specs/2026-07-12-agent-loop-provider-pool-refresh-design.md`); requires the landed result-hardening plan | OpenRouter throttle markers; Pi credential-shadowing startup warning; verified free-model fallback pool (Nemotron 3 Ultra, gpt-oss-120b, Hy3, Laguna M.1) with explicit stateless write-capable shims; Grok/xAI removed everywhere; stale loop state reset | MCO loop tests green including throttle, preflight, and config assertions; ruff/pyright clean; full default suite green; `./agent-loop --dry-run` selects a real executor with no grok/agy/xai remnants | shipped: 2026-07-12 at commit 7c0d5c3 |
| 4 | Spike B — Nested blockquote-in-list (`docs/superpowers/plans/2026-07-12-spike-b-nested-blocks.md`) | §7.4 | Two-structure composition (blockquote-in-list, list-in-blockquote at minimum scope). Snippet fixtures under `tests/fixtures/architecture_spikes/nested_blocks/` | Spike snippets pass byte-identical to oracle; composition confirmed or halt-and-redesign triggered | shipped: 2026-07-12 at commit cd838116feee4e552dea032652648e3c88a6b61f |
| 4S | Span Architecture Spike (`docs/superpowers/plans/2026-07-12-span-architecture-spike.md`) | Completability hardening §4 | Establish protected-region and buffered-scan shape before broad Act III growth: variable code spans, escapes, protected HTML/link/image regions, representative overlapping strong/emphasis | Reviewed span streams and oracle-backed probes pass; Act III model confirmed or halt-and-redesign triggered; Spike A/B snippets remain green. Amended 2026-07-13: A1 authorizes the two-character code-span machine; A2 replaces the retired Task 4 pool with the 41+10 shared-idiom pool; A3 corrects the pre-handoff assertion boundary; A4 supplies carrier-safe scene-family choreography; A5 quarantines the retired WIP; A6 requires reconstruction from committed Task 3 with an event-order terminator observer; A7 moves field tags to Prospero and authorizes the exact two-character restore adapters; A8 requires real-terminator restoration plus ordered raw requeue draining; and A9 separates the live continuation selector from field registers and Romeo field capture. A17 supplies the binary-scene ledger and 17+5 controlled adapter pool; A18 supplies the exhaustive ten no-op branch-entry adapters and 10+4 controlled pool required for lowering after A17; A19 makes goto staging source-aware and reserves seven disconnected-entry bridge chains (14+5 controlled pool). | shipped: 2026-07-14 at commit aab20ed |
| 4R | Repo Hygiene Recovery (`docs/superpowers/plans/2026-07-14-repo-hygiene-recovery.md`) | Task 5 Step 2 evidence reconciliation (`docs/superpowers/specs/2026-07-14-repo-hygiene-recovery-design.md`) | Re-run and record the stale codegen Ruff/completion gate; make only the pre-authorized import/format repair if it reproduces | Repo-wide Ruff, hygiene tests, original 4S completion gate, full default suite, and Amps strict parity all pass; no active blocker remains | shipped: 2026-07-14 at commit ef82d6e |
| 5 | Slice 2 — Low-risk fixtures (`docs/superpowers/plans/2026-07-14-slice-2-low-risk-fixtures.md`) | §7.5 | Seven fixtures pass: Auto links (URL only), Backslash escapes, Code Spans, Tidyness, Tabs, Horizontal rules, Code Blocks | §8.1 four-gate per fixture; spike snippets still pass | halted: 2026-07-14 for MCO governance recovery; completed checkpoints are preserved |
| 5R | MCO Loop Reconciliation (`docs/superpowers/plans/2026-07-14-mco-loop-reconciliation.md`) | Loop-governance recovery (`docs/superpowers/specs/2026-07-14-mco-loop-reconciliation-design.md`) | Reconcile outstanding branch/artifact debt; preserve planner routing; durable branch dispositions; actionable blockers; and planning-artifact fencing | Focused MCO-loop controls pass; full default suite, Ruff, pyright, and dry-run evidence pass; Slice 2 remains halted pending an explicit resume plan | shipped: 2026-07-14 at commit 48ef7df |
| 5C | Slice 2 List-Regression Continuation (`docs/superpowers/plans/2026-07-14-slice-2-list-regression-continuation.md`) | Isolated prerequisite from reconciliation design Amendment A3 | Restore the pre-existing `*`/`-` rejected-HR list handoff and its shipped Spike-A token/HTML contract; no broader Slice-2 fixture work | Focused Act-II handoff, real and fast list dumps, list/nested spikes, generated-artifact and literary gates, full default suite, and dry run pass | shipped: 2026-07-14 at commit bd22ab3 |
| 6 | Slice 3 — Medium-risk fixtures (`docs/superpowers/plans/2026-07-14-slice-3-medium-risk-fixtures.md`) | §7.6 | ~10 fixtures pass: Hard-wrapped paragraphs with list-like lines; Links (inline, reference, shortcut); Images; Literal quotes in titles; Strong and em together; Inline HTML (Simple); Inline HTML comments; Blockquotes with code blocks | §8.1 four-gate per fixture; spike snippets still pass | shipped: 2026-07-17 at commit e3d40cb |
| 7 | Slice 4 — High-risk fixtures (`docs/superpowers/plans/2026-07-17-slice-4-high-risk-fixtures.md`) | §7.7 | Three fixtures pass: Inline HTML (Advanced); Nested blockquotes (full); Ordered and unordered lists (full) | §8.1 four-gate per fixture; spike snippets still pass | shipped: 2026-07-17 at commit 2ebb55f |
| 8 | Slice 5 — Documentation aggregates (`docs/superpowers/plans/2026-07-18-slice-5-documentation-aggregates.md`) | §7.8 | Two aggregate fixtures pass: Markdown Documentation — Basics; Markdown Documentation — Syntax. All 23 fixtures pass or are documented divergences | §8.1 four-gate per fixture; full 23-fixture suite green | shipped: 2026-07-18 at commit 7958f66 |
| 9 | SPL-Pure Release Path (`docs/superpowers/plans/2026-07-19-spl-pure-release-path.md`) | Architecture §D1/§5.1; design `docs/superpowers/specs/2026-07-19-spl-pure-release-path-design.md` (Addendum A1); plan Amendments A0–A2 | Production path is `shakespeare run shakedown.spl` / `./shakedown` with no Python Markdown rewrite, strip, or interpret-label assists; Act I pure ops own reference definitions; Act III pure `RESOLVE_*` pre-pass owns link/image resolution; 23/23 deterministic parity | Pure CLI strict harness (or integration gate) green; `release_runtime` / IR without `rewrite_task3_markdown`, `strip_reference_definitions`, or `apply_act1_reference_strip` / `apply_act3_link_resolution` short-circuits; literary + regen gates | shipped: 2026-07-21 at commit b286976 |
| 10 | Malformed Reference Definitions (`docs/superpowers/plans/2026-07-22-malformed-reference-definitions.md`) | Correctness follow-up; design `docs/superpowers/specs/2026-07-22-malformed-reference-definitions-design.md` | Three malformed reference-definition forms render as literal paragraphs matching the oracle: empty-label `[]:` and empty-URL `[not]:` over-strips in Act I; lossy Act III definition-replay for `[x] : destination`. Stacked on the ampersand PR branch | Four-input oracle parity on the real `./shakedown` binary; the three `test_act3_contracts` xfail(strict=True) cases pass without xfail; 23-fixture `test_mdtest` unchanged; literary + regen gates; full suite green | in flight |

## How to write the next plan

When the predecessor's verification gate passes:

1. Confirm the verification gate is genuinely green (not just "tests pass" — for fixture work, the strict parity harness from architecture §7.1 #6 must report zero byte-level mismatches).
2. Update this file: bump the predecessor's status to `shipped` and add a "shipped: <date> at commit <sha>" trailer.
3. Invoke `superpowers:writing-plans` with the next plan as scope.
4. The new plan's first reference should be back here, plus the architecture-spec section that defines its scope.
5. Carry forward any learnings — especially anything that revises an architecture decision — into the architecture spec itself before writing the next plan. The architecture spec is the durable input; this roadmap and the per-plan files track execution against it.

## Halt-and-redesign

If a spike or slice triggers a halt (architecture §8.2):

1. Stop the loop. Write to `.agent/blockers.md`.
2. Re-open the architecture spec, not just the plan. Spikes exist to
   force architecture changes when reality contradicts the design.
3. After the architecture is updated, mark the affected plans
   `superseded` here and write replacement plans against the revised
   architecture.

Halting is cheap. Continuing on a wrong floor is expensive.

Spike A is mechanically resolved and its outcome is now recorded in the
architecture spec. The 2026-07-05 halt on hand-authored SPL was resolved by
the splc compiler (plans 3G-3J), and the resumed Spike A chain is complete in
code and tests: P1 (row 3K, tokenized stream + dispatcher skeleton) shipped
2026-07-06 and P2 (row 3L, list pass) shipped 2026-07-07. Spike B (row 4)
shipped 2026-07-12 and confirmed that explicit item/container streams compose
cleanly across Act II and Act IV.

## Current reconciliation before Slice 2

`docs/superpowers/notes/2026-07-07-completability-review.md` records a
2026-07-07 review of roadmap completability. Its input-size scaling action is
resolved by B20. The broader 2026-07-11 audit adds structural token, executable
stack-contract, early span-risk, and all-fixture smoke findings; plan 3M
shipped all of it (2026-07-12). The container representation work in Spike B
is now shipped; row 4S, the span architecture spike, shipped on 2026-07-14.
Row 4R, the repo-hygiene reconciliation, shipped before Slice 2 began. Slice
2 is halted on 2026-07-14. Rows 5R and 5C shipped on 2026-07-14, preserving
the isolated list-regression repair and loop-governance closure. Row 6 is the
explicitly registered successor plan: it does not relabel Slice 2 as shipped,
and its first task proves the declared shipped baseline before it enables any
new fixture.
On 2026-07-13 an interactive planning session added Amendment A1 to the
4S plan document, resolving the repeated Task 3 Step 5 halts: it authorizes a
two-character code-span scanner (idle-character registers plus off-stage
value references — no `validate.py`/`lower.py` changes) and reserves the
expanded scene-title and recall-key pools Step 5 needs. A second
interactive planning session the same day added Amendment A2, retiring the
original Task 4 protected-region pool (which a stashed WIP overran 91
scenes to 29 reserved) in favor of a shared-idiom design — one generic
field-scan pipeline, a capture-hold-then-requeue trick for recursively
scanned link/image label and alt text, and duplicate-on-reverse for
autolink's two encoded emits — with its own 41-working/10-spare pool.

## Source notes

- Literary prevention is already designed and planned. After this cleanup is
  reviewed and integrated, use
  `docs/archive/specs/2026-04-30-literary-prevention-design.md` and
  `docs/archive/plans/2026-04-30-literary-prevention-rails.md` to teach the
  assembler/codegen path to consume `src/literary.toml` and to enforce the SPL
  literary protocol in future run-loop prompts. Do not start a new design phase
  for that same scope unless the approved prevention plan is superseded.
- SPL-changing plans must use `docs/superpowers/notes/spl-literary-protocol.md`
  or explicitly reference its required docs and literary compliance tests.

## References

- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — the durable plan that this roadmap stages execution against.
- `docs/archive/specs/2026-04-27-loop-prompt-design.md` — design for `docs/prompt-shakedown.md`, produced by plan 1.
- `docs/archive/specs/2026-04-29-slice-1-halt-resolution-design.md` — accepted design for resolving the Slice 1 line-budget halt.
- `docs/archive/specs/2026-04-30-literary-prevention-design.md` — approved design for TOML-backed assembler/codegen and prompt-author prevention rails.
- `docs/archive/plans/2026-04-30-literary-prevention-rails.md` — implementation plan for the approved literary prevention rails.
- `docs/superpowers/specs/2026-07-05-spl-ir-compiler-design.md` — approved design for the SPL-from-IR compiler (splc), resolving the Spike A halt.
- `docs/superpowers/specs/2026-07-11-completability-hardening-design.md` — approved staging for structural stream contracts, executable stack safety, the span spike, performance gates, and all-fixture smoke reporting.
- `docs/spl/literary-spec.md` — voice, palette, decorative-surface policy.
- `docs/ralph-loop.md` — Huntley/Ralph loop methodology and `@file` university pattern.
- `CLAUDE.md` — commit conventions, target interface, implementation workflow.
