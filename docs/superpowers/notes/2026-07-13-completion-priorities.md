# Completion Priorities (2026-07-13)

Point-in-time prioritization of the highest effort-to-value work for
finishing Shakedown, written while plan 4S (span architecture spike) is
the sole in-flight plan and Task 4 Step 2 has just been unblocked by
Amendment A2. This is a supporting note, not architecture truth; the
roadmap (`docs/superpowers/plans/plan-roadmap.md`) remains the source of
truth for what is actually in flight.

**Headline:** the architecture risk is nearly retired. The remaining
cost of the project is dominated by (a) per-fixture iteration speed
across Slices 2–5 (~22 fixtures) and (b) the plan-amendment bottleneck
that consumed ~20 loop iterations on 4S Task 3 Step 5 before Amendment
A1 landed.

## Ranked by effort-to-value

1. **Finish 4S Tasks 4–5.** Amendment A2 resolved the Task 4 scene
   budget; the step is executable now. Until 4S ships, the roadmap
   forbids other implementation work, so this is pure critical path.
   After 4S, all remaining work is fixture grinding against a confirmed
   architecture.
2. **Kill the plan-amendment waste mode.** Both A1 and A2 halts shared
   a root cause: plans reserved literary pools that implementation
   overran (Task 4: 91 scenes needed vs 29 reserved), and the loop
   cannot amend plans. Actions: (a) codify a pool-sizing policy in
   `correctness-first-spl-workflow.md` — derive scene counts from a
   binding scene table and reserve proportional spares; (b) prove the
   3-strike `BLOCK[plan]` escalation fires end-to-end with a test that
   accumulates the counter through real loop iterations rather than
   pre-seeding it. **Done 2026-07-13** (this session): policy added to
   the workflow note; accumulation test added to
   `tests/test_mco_loop.py`.
3. **Probe the Slice-5 aggregates early.** Gap 3 of the 2026-07-07
   completability review is still live: the two Markdown Documentation
   fixtures are the largest inputs and land last. Record wall-time and
   failure shape for them from the all-fixture differential smoke
   report each slice, and treat runtime blow-up as an early halt
   trigger instead of a Slice-5 surprise.
4. **Make the fast IR interpreter the default inner loop.** Every real
   SPL run pays multi-second cold interpreter startup, and Slices 2–5
   are ~22 fixtures of red-green iteration. Run 3M's verification-only
   IR interpreter first for step-level evidence; reserve `./shakedown`
   runs for byte-parity gates.
5. **Generalize Amendment A2's shared idioms into reusable splc IR
   building blocks.** The `LYRIC_FIELD_*` scan pipeline,
   capture-hold-then-requeue, and duplicate-on-reverse idioms are what
   keep Act III inside scene budgets for Slices 3–4 (~10 remaining
   fixtures are span-heavy). After 4S ships, extract and document them
   so future plans compose rather than re-derive them.
6. **Keep the plan pipeline warm.** The moment 4S's completion gate
   passes, mark the roadmap row shipped promptly so the planning pool
   drafts the Slice 2 plan without an operator round-trip. Slice 2
   (7 low-risk fixtures) is also the best test of unattended fixture
   grinding.

## Explicit non-priorities

- More loop/provider infrastructure — plan 3N just refreshed it and it
  is not the constraint.
- Further interpreter caching/performance work — B21's parallel pytest
  already took the available 3.5–4x win; revisit only if item 3's
  probes show scaling trouble.
- Speculative plans for Slices 3–4 — the roadmap's one-plan-at-a-time
  reasoning holds; 4S learnings should feed those plans.
