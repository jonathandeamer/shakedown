@docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md
@docs/superpowers/plans/plan-roadmap.md
@docs/superpowers/plans/2026-04-28-pre-slice-1-setup.md
@docs/spl/literary-spec.md
@docs/spl/reference.md
@docs/markdown/target.md
@docs/markdown/divergences.md
@CLAUDE.md
@.agent/blockers.md

You are implementing the Shakedown Markdown-to-HTML port in SPL. This is one
iteration of a continuous run-loop driven by `run-loop` at the repo root.

Your job, this iteration:

1. Read the current implementation plan. For this prompt revision, the active
   plan is `@docs/superpowers/plans/2026-04-28-pre-slice-1-setup.md`. A later
   operator-authored prompt revision may replace this `@` reference with the
   next concrete plan file after the roadmap marks that plan `in flight`.
2. Find the first unchecked step in the first task with any unchecked step.
   Complete that step as written. One step. No batching.
3. If the step changes code or data, run the tests the step specifies and
   confirm they pass before proceeding.
4. Check the step's checkbox in the plan file.
5. Commit using a conventional-commit prefix matching the change type
   (`.githooks/commit-msg` enforces this; do not bypass with `--no-verify`).

Standing rules:

- No placeholders. Real implementations only. If a step says "write code X",
  write code X; do not write a stub that says "TODO".
- Aesthetic policy lives in `@docs/spl/literary-spec.md`. Reach for it before
  writing any decorative surface.
- No autonomous version bumps. Do not run `cz bump`, create tags, push tags, or
  update `CHANGELOG.md` unless the current plan step explicitly authorises it.
- Respect `.agent/blockers.md`. If any line begins with `- BLOCK:`, address it
  first; if you cannot, exit cleanly without modifying code.
- Stuck? Append `- BLOCK: <one-line reason>` to `.agent/blockers.md` and exit.

Completion: when every step in the active plan is checked and the slice's
verification gate passes, write `.agent/complete-shakedown.md`. The `run-loop`
driver exits on that marker.
