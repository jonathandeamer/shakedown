> Archived 2026-04-17. Historical artifact — references `scripts/spl-smoke`, `.worktrees/spl-slice-1`, and a `feature/spl-slice-1` branch that no longer exist in this repository. Interpreter timing numbers are preserved in `docs/prior-attempt/feasibility-lessons.md`. Inner-loop workflow for the new effort is an open architecture-planning question.

---

# Slow-Machine SPL Workflow — 2026-04-09

This workflow assumes the current repository layout:

- repo root checkout on `main`
- SPL implementation work on branch `feature/spl-slice-1`
- SPL branch checked out in `.worktrees/spl-slice-1`

The goal is to keep the slow machine for editing and light smoke checks, and use
a faster machine for milestone verification.

## Key rule

Treat `shakespeare run` as an expensive integration test.

Do not use `pytest` as the inner loop while editing `shakedown.spl` on the slow
machine. Each `render()` call starts a fresh subprocess, which is too expensive
here.

## Local inner loop on the slow machine

From the repo root:

```bash
scripts/spl-smoke --oracle blockquote
scripts/spl-smoke blockquote
```

Notes:

- `scripts/spl-smoke` defaults to `.worktrees/spl-slice-1` when that worktree
  exists
- use `blockquote` while working on quote logic
- use `slice1` for a broader one-run smoke check across major Slice 1 features
- compare against the oracle first so the expected output is clear before paying
  for a slow SPL run

Recommended loop:

1. Read and trace the relevant scenes locally.
2. Check expected output with `scripts/spl-smoke --oracle ...`.
3. Make a batch of SPL edits.
4. Run one smoke invocation with `scripts/spl-smoke ...`.
5. Repeat.

## Milestone verification on the faster machine

Milestone verification only works cleanly from committed states. If you want the
other machine to verify a checkpoint, commit it first, then push the branch.

On the slow machine:

```bash
git -C .worktrees/spl-slice-1 status --short
git -C .worktrees/spl-slice-1 add shakedown.spl
git -C .worktrees/spl-slice-1 commit -m "wip: checkpoint blockquote nesting"
git -C .worktrees/spl-slice-1 push -u origin feature/spl-slice-1
```

The `wip:` prefix is acceptable for temporary checkpoint commits as long as the
message still follows the repo's conventional-commit format.

## Set up the faster machine

Clone the repo normally, keep `main` at the root, and recreate the same SPL
worktree layout:

```bash
git clone <repo-url> shakedown
cd shakedown
git fetch origin
git fetch origin feature/spl-slice-1:feature/spl-slice-1
git worktree add .worktrees/spl-slice-1 feature/spl-slice-1
```

After that, the same commands work on both machines:

```bash
scripts/spl-smoke blockquote
scripts/spl-smoke slice1
```

## Refresh the faster machine for a new checkpoint

If the worktree already exists on the faster machine:

```bash
git fetch origin
git -C .worktrees/spl-slice-1 pull --ff-only
```

This keeps the verification machine aligned with the latest pushed checkpoint on
`feature/spl-slice-1`.

## What to run on the faster machine

Use the fast machine for the expensive steps:

```bash
scripts/spl-smoke blockquote
pytest tests/test_blockquotes.py -q
pytest tests/test_paragraphs.py tests/test_headings.py tests/test_blockquotes.py -q
pytest -m "not oracle" -q
```

Run the narrowest useful command first. Only pay for broader pytest runs when the
smoke output looks plausible.

## If the faster machine needs to make a fix

Make the fix in `.worktrees/spl-slice-1`, commit it on `feature/spl-slice-1`,
and push it back:

```bash
git -C .worktrees/spl-slice-1 add shakedown.spl
git -C .worktrees/spl-slice-1 commit -m "fix: correct nested blockquote open path"
git -C .worktrees/spl-slice-1 push
```

Then on the slow machine:

```bash
git fetch origin
git -C .worktrees/spl-slice-1 pull --ff-only
```

## Optional: milestone tags

If you want immutable verification points, tag them after pushing the branch:

```bash
git -C .worktrees/spl-slice-1 tag -a milestone/2026-04-09-blockquotes -m "blockquote checkpoint"
git -C .worktrees/spl-slice-1 push origin milestone/2026-04-09-blockquotes
```

That makes it easy to answer "which exact checkpoint passed on the fast machine?"
