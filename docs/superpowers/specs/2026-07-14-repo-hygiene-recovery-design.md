# Repo Hygiene Recovery Design

**Date:** 2026-07-14  
**Status:** Accepted for autonomous execution  
**Scope:** Reconcile the stale Task 5 Step 2 hygiene blocker without changing
Markdown behavior or the SPL architecture.

## Decision

The reported `scripts/codegen_html.py` Ruff debt is not present in the handed-off
worktree: `uv run ruff check .`, `uv run ruff format --check .`, and
`uv run pytest tests/test_repo_hygiene.py -q` all pass on 2026-07-14. Treat the
blocker as stale rather than reformatting or changing code unnecessarily.

The recovery execution must first repeat those three commands. If any one fails
because `scripts/codegen_html.py` has again acquired the reported debt, the only
authorized source repair is to remove the unused `re` import if it exists and run
Ruff's formatter on that file. It must not change `emit_value`, literal emission,
or any generated phrase. The normal codegen and literary compliance tests then
prove that this mechanical repair did not alter SPL output.

## Boundaries

- No compiler, validator, IR, generated SPL, fixture, token-code, or scene-title
  change is authorized.
- No controlled literary surface is added or changed. The already-reserved
  `src/literary.toml` atom vocabulary remains the only prose source for
  `scripts/codegen_html.py`.
- The authoritative closure evidence is the original Task 5 Step 2 completion
  gate plus the full default suite. Only after it passes may the stale blocker be
  removed and the reconciliation roadmap row be marked shipped.

## Failure handling

If the bounded repair cannot restore the named Ruff and codegen/literary gates,
append exactly one `- BLOCK[plan]:` line describing the diagnostic and stop. Do
not widen scope to production behavior, new literary reservations, or compiler
changes.
