@docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md
@docs/superpowers/plans/plan-roadmap.md
@docs/spl/literary-spec.md
@docs/superpowers/notes/spl-literary-protocol.md
@docs/spl/reference.md
@docs/markdown/target.md
@docs/markdown/divergences.md
@CLAUDE.md
@.agent/blockers.md

You are implementing the Shakedown Markdown-to-HTML port in SPL. This is one
iteration of a continuous run-loop driven by `run-loop` at the repo root.

Your job, this iteration:

1. Read `@docs/superpowers/plans/plan-roadmap.md`.
2. If no plan is marked `in flight`, write `.agent/complete-shakedown.md`
   and exit cleanly without modifying anything else.
3. If a plan is marked `in flight`, use the plan file named by the roadmap
   and find the first unchecked step in the first task with any unchecked
   step. Complete that step as written. One step. No batching.
4. If the step changes code or data, run the tests the step specifies and
   confirm they pass before proceeding.
5. Check the step's checkbox in the plan file.
6. Commit using a conventional-commit prefix matching the change type
   (`.githooks/commit-msg` enforces this; do not bypass with `--no-verify`).

Standing rules:

- No placeholders. Real implementations only. If a step says "write code X",
  write code X; do not write a stub that says "TODO".
- SPL literary, aesthetic, and stylistic policy is mandatory for any SPL-facing
  change. Before editing `src/*.spl`, `scripts/assemble.py`,
  `scripts/codegen_html.py`, `src/literary.toml`, or future SPL generators,
  read and follow `@docs/superpowers/notes/spl-literary-protocol.md`.
  Controlled prose must remain TOML-owned and referenced by `@LIT.`
  placeholders where the protocol requires it. Do not treat literary compliance
  as optional cleanup; run the literary compliance tests named by the active
  plan before committing.
- No autonomous version bumps. Do not run `cz bump`, create tags, push tags, or
  update `CHANGELOG.md` unless the current plan step explicitly authorises it.
- Respect `.agent/blockers.md`. If any line begins with `- BLOCK:`, address it
  first. If you cannot address an open block, exit cleanly without modifying
  code.
- Stuck? Append `- BLOCK: <one-line reason>` to `.agent/blockers.md` and exit.

Completion: when every step in the active plan is checked and the slice's
verification gate passes, write `.agent/complete-shakedown.md`. The `run-loop`
driver exits on that marker.
