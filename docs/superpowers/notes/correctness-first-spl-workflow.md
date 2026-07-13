# Correctness-First SPL Workflow

Literary authorship happens at planning time, not implementation time.
Implementation agents solve byte parity; they never invent controlled
prose mid-task. This note is normative for every SPL-changing plan,
alongside `docs/superpowers/notes/spl-literary-protocol.md`.

## Rules for plan authors

1. **Reserve all controlled surfaces in the plan.** Every scene title,
   Recall line, and recurring value phrase the implementation will need
   is written into the plan as ready-to-paste `src/literary.toml`
   blocks, validated against `docs/spl/literary-spec.md` and
   `docs/spl/style-lexicon.md` during planning (Spike A Task 2 is the
   model — that part of Spike A worked).
2. **Derive the working-pool size, never estimate it.** For any
   scanner-, dispatcher-, or state-machine-shaped task, the plan must
   contain a binding scene table (states × transitions, or an
   equivalent explicit enumeration) and size the working pool from it.
   Plan 4S proved that guessed pools fail: Task 4 reserved 29 titles
   against a design that needed 91 scenes until Amendment A2 redesigned
   it around shared idioms with a derived 41-title pool. Both 4S
   amendments (A1's register/stack map and scene table, A2's shared
   scan pipeline and pool) are the model.
3. **Reserve proportional spares.** Include a spare pool of
   pre-approved scene titles of at least 20% of the working pool per
   act touched, and never fewer than four, clearly marked as the spare
   pool, so a mid-task structural surprise does not force an agent to
   author prose. (Amendment A2's 41 working + 10 spare is the model.)
3. **Sequence polish after parity.** Voice, motif, and palette
   improvements beyond the reserved surfaces land as separate commits
   after the plan's parity gates pass — never in the same commit as a
   correctness change.

## Rules for implementation agents

1. Take scene titles only from the plan's reserved blocks or spare pool.
2. If the spare pool runs out, that is a plan defect: stop the task and
   record it as a `- BLOCK[plan]:` line in `.agent/blockers.md` so it
   routes to the planning pool. Do not improvise literary prose.
3. Keep the scene ledger in sync per commit: a new `Scene @LABEL:` in
   `src/*.spl` and its `[scenes.LABEL]` entry (from the reserved blocks)
   land in the same commit.
4. Debug artifacts (`debug/*.spl`, anything under `.cache/`) are outside
   literary scope: no `@LIT.` placeholders, no `src/literary.toml`
   entries, plain literal titles.
