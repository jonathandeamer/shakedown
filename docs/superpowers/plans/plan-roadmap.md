# Implementation Plan Roadmap

**Last updated:** 2026-05-01
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
| 2P | Literary Prevention Rails (`docs/superpowers/plans/2026-04-30-literary-prevention-rails.md`) | §7.1 support / literary prevention design | Teach assembler/codegen and future prompt authors to consume `src/literary.toml` for controlled SPL literary surfaces; add `@LIT.` placeholder resolution, TOML-backed value atoms, prompt gates, and production literary compliance rails | Exact plan path is present in this row; active prompt can discover it; final literary surface audit passes; implemented mdtest fixtures remain byte-identical | shipped: 2026-05-01 at commit 78e0c53 |
| 3 | Spike A — Lists at minimum viable scope (`docs/superpowers/plans/2026-05-01-spike-a-lists.md`) | §7.3 | Multi-pass dispatcher + frame-sentinel pattern validated on flat tight/loose lists, one nesting level, one indented continuation. Snippet fixtures committed under `tests/fixtures/architecture_spikes/lists/` | Spike snippets pass byte-identical to oracle through `tests/test_architecture_spikes.py`; dispatcher shape confirmed or halt-and-redesign triggered | in flight |
| 4 | Spike B — Nested blockquote-in-list | §7.4 | Two-structure composition (blockquote-in-list, list-in-blockquote at minimum scope). Snippet fixtures under `tests/fixtures/architecture_spikes/nested_blocks/` | Spike snippets pass byte-identical to oracle; composition confirmed or halt-and-redesign triggered | pending |
| 5 | Slice 2 — Low-risk fixtures | §7.5 | Seven fixtures pass: Auto links (URL only), Backslash escapes, Code Spans, Tidyness, Tabs, Horizontal rules, Code Blocks | §8.1 four-gate per fixture; spike snippets still pass | pending |
| 6 | Slice 3 — Medium-risk fixtures | §7.6 | ~10 fixtures pass: Hard-wrapped paragraphs with list-like lines; Links (inline, reference, shortcut); Images; Literal quotes in titles; Strong and em together; Inline HTML (Simple); Inline HTML comments; Blockquotes with code blocks | §8.1 four-gate per fixture; spike snippets still pass | pending |
| 7 | Slice 4 — High-risk fixtures | §7.7 | Three fixtures pass: Inline HTML (Advanced); Nested blockquotes (full); Ordered and unordered lists (full) | §8.1 four-gate per fixture; spike snippets still pass | pending |
| 8 | Slice 5 — Documentation aggregates | §7.8 | Two aggregate fixtures pass: Markdown Documentation — Basics; Markdown Documentation — Syntax. If all 23 fixtures pass or are documented divergences, cuts `1.0.0` per CLAUDE.md milestone policy | §8.1 four-gate per fixture; full 23-fixture suite green | pending |

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

## Source notes

- Literary prevention is already designed and planned. After this cleanup is
  reviewed and integrated, use
  `docs/superpowers/specs/2026-04-30-literary-prevention-design.md` and
  `docs/superpowers/plans/2026-04-30-literary-prevention-rails.md` to teach the
  assembler/codegen path to consume `src/literary.toml` and to enforce the SPL
  literary protocol in future run-loop prompts. Do not start a new design phase
  for that same scope unless the approved prevention plan is superseded.
- SPL-changing plans must use `docs/superpowers/notes/spl-literary-protocol.md`
  or explicitly reference its required docs and literary compliance tests.

## References

- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — the durable plan that this roadmap stages execution against.
- `docs/superpowers/specs/2026-04-27-loop-prompt-design.md` — design for `docs/prompt-shakedown.md`, produced by plan 1.
- `docs/superpowers/specs/2026-04-29-slice-1-halt-resolution-design.md` — accepted design for resolving the Slice 1 line-budget halt.
- `docs/superpowers/specs/2026-04-30-literary-prevention-design.md` — approved design for TOML-backed assembler/codegen and prompt-author prevention rails.
- `docs/superpowers/plans/2026-04-30-literary-prevention-rails.md` — implementation plan for the approved literary prevention rails.
- `docs/spl/literary-spec.md` — voice, palette, decorative-surface policy.
- `docs/ralph-loop.md` — Huntley/Ralph loop methodology and `@file` university pattern.
- `CLAUDE.md` — commit conventions, version cadence, target interface, implementation workflow.
