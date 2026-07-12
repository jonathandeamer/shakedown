# Completability Review — Next Steps After Spike A P2 (3L)

**Date:** 2026-07-07
**Status:** resolved 2026-07-12 — all three gaps and both hygiene items below
are closed (plan 3M Tasks 4, 5, and 7; see each section's "Resolved"/"Fixed"
note for the exact decision and evidence). The only carryover into future
work is Gap 3's cadence note: keep re-running the differential smoke report
as each slice ships, rather than only once.
**Origin:** interactive review of the roadmap and architecture spec asking
"what should change to ensure this project is completable?"

## Verdict

The roadmap's structure is sound. The halt discipline already caught and
fixed the one thing that genuinely threatened completability (hand-authoring
SPL, resolved by the splc compiler, plans 3G–3J). The remaining completability
risk is not the roadmap's shape — it is that **performance evidence is much
thinner than correctness evidence, and the expensive discovery is currently
scheduled last** (Slice 5 budget check, architecture spec §8.3).

## Gap 1 — Input-size execution scaling is unmeasured (highest priority)

All recorded baselines (B14, B17, B18 in `docs/verification-plan.md`) measure
**program-size** cost: interpreter time as a function of `.spl` line count.
Nothing measures how execution time grows with **input** size. The pipeline
processes input character by character through four acts, and Slice 5's
`Markdown Documentation - Syntax` is thousands of characters run through
multiple passes.

**Action:** add a B-numbered probe. Pipe a Syntax-sized input through the
current pipeline — the output will be wrong; only the execution time matters —
and record first-run + median per `docs/performance/budget.md` protocol.

**Decision rule:** if the result is red per the budget thresholds (>120s for a
single large fixture), the per-character pass structure needs a conversation
**before** Slices 3–4 lock it in, not after.

**Resolved 2026-07-07 — green.** Recorded as B20 in
`docs/verification-plan.md`: ~11s fixed program cost plus ~0.11s/KB of input;
a Syntax-sized (27KB) synthetic input runs in ~14s median. No pass-structure
conversation is forced. Fixed program cost (Gap 2) remains the term to watch.
The real Syntax fixture crashes at spike scope (Act III, expected); empty
stdin also crashes (Act I line 96) — hygiene item for a future plan.

## Gap 2 — Program-size growth will make the feedback loop painful around Slice 3

`shakedown.spl` was ~2,820 lines with essentially one fixture passing
(measured 2026-07-07, mid-3L). Full 23-fixture scope plausibly lands at 10k+
lines. B14 gives ~2.7s per 1k lines cold, with no warm reuse — ~30s+ per run,
×23 fixtures for the regression gate, which `docs/performance/budget.md`
already classes as red for the full contract (>15m).

**Actions (decide before writing the Slice 3 plan):**

1. **Parallelize the mdtest suite** with `pytest-xdist`. Fixtures are
   independent subprocesses; this is nearly free and cuts wall time ~8× on
   this machine.
2. **Re-open the cache spike.** The pre-Slice-1 spike fell back to direct
   assemble-and-run when the file was small. Caching the parsed AST becomes
   much more valuable at 10k lines, and architecture spec §8.2 already frames
   the cache decision as re-openable.

**Resolved 2026-07-12 — plan 3M Task 5, both actions decided.** Action 1:
`pytest-xdist` adopted, but scoped to the spikes + token-dump regression only
(`tests/test_architecture_spikes.py tests/test_token_dump.py -q -n auto`,
~3.5x-4x wall-time win, B21 in `docs/verification-plan.md`); `-n auto` was
**not** applied to `tests/test_mdtest.py`, which stays sequential per
`docs/performance/budget.md` (worker-startup overhead dominates its ~11s
wall time). Action 2: the cache spike was re-opened and re-decided, not
reversed — a session-scoped in-process `Shakespeare()` runner was prototyped,
proved state-isolated, but not adopted because per-call construction cost
(~11s-13s) matches a fresh `./shakedown` subprocess and buys no wall-time
win; `direct_assemble_and_run` remains the decision. Full writeup in
`docs/architecture/cache-spike.md` ("Follow-up: in-process interpreter
reuse") and `docs/performance/budget.md` ("Long Regression Suite
(parallelized)" and the B21 baseline entry).

## Gap 3 — Slice 4/5 risk is backloaded with no early smoke signal

Architecture spec §8.5 acknowledges "spike succeeds at minimum scope but
fails at full fixture scope" and answers it with Slice 4's own design step.
Fine for correctness — but there is no early *runtime* or *structural* signal
from the aggregates.

**Action:** once Slice 2 ships, start running the two
`Markdown Documentation - *` fixtures as **non-gating smoke checks** — not to
pass them, but to watch runtime growth and surface structural surprises (raw
HTML boundaries, deep nesting) while the pass decomposition is still cheap to
adjust.

**Resolved early 2026-07-12 — plan 3M Task 4.** The infrastructure for this
smoke signal was built ahead of Slice 2 rather than after it:
`scripts/differential_smoke.py` runs all 23 fixtures, including both
`Markdown Documentation - *` aggregates, in observational (non-gating) mode
by default, reporting status, elapsed time, and first-byte-difference or
crash information per case. The dated baseline is
`.agent/differential-smoke-2026-07-12.md`; as of that run, `Markdown
Documentation - Basics` mismatches and `Markdown Documentation - Syntax`
crashes in `./shakedown` (both expected at current implementation scope).
The remaining open item is *using* this signal on a cadence going forward
(e.g. re-running it as each slice ships), not building it.

## Hygiene items

1. ~~CLAUDE.md said Act III (`src/30-act3-span.spl`) was still hand-authored;
   plan 3J shipped the Act III IR port 2026-07-06 (`src_ir/act3.py`).~~
   **Fixed 2026-07-07** alongside this note.
2. ~~Architecture spec §8.2 still lists the "Slice 1 assembled `shakedown.spl`
   exceeds ~600 lines" halt trigger. It is long obsolete (~2,820 lines mid-3L)
   and should be retired or re-scoped so it doesn't read as an ignored
   tripwire. Do this the next time the architecture spec is opened for edits.~~
   **Fixed 2026-07-12** — plan 3M Task 7 replaced the obsolete ~600-line row
   in `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`
   §8.2 with the measured red-budget / two-consecutive-projection trigger
   already decided in §8.3, and updated the same table's "Spike B fails" row
   to match §7.4's container-grammar-first revision order.

## What NOT to change

One-plan-at-a-time staging, spike-before-slice ordering, and the
byte-identical verification gates are all pulling their weight — Spike A's
halt-and-redesign is the proof. Leave them alone.

## References

- `docs/superpowers/plans/plan-roadmap.md` — plan ladder; this note is queued after row 3L.
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — §8.2, §8.3, §8.5.
- `docs/performance/budget.md` — thresholds and benchmark protocol.
- `docs/verification-plan.md` — B-numbered claim inventory.
