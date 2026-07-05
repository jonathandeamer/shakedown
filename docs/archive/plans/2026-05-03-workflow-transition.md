# Workflow Transition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace forward-facing references to `run-loop` autonomous execution in `CLAUDE.md`, `docs/README.md`, and `docs/superpowers/plans/plan-roadmap.md` with the new supervised superpowers-session workflow, leaving `run-loop` code, prompt, and history intact as legacy artifacts.

**Architecture:** Documentation-only edits. Three files change. No SPL source, no tests, no code logic. Each edit is a string replacement with exact before/after content from the spec. Verification is by `grep` for residual forward-facing run-loop references and visual inspection of the new sections.

**Tech Stack:** Markdown only. Edits via the `Edit` tool. Verification via `grep`.

---

## Required Reading

Read before editing:

- `docs/superpowers/specs/2026-05-03-workflow-transition-design.md` — the approved spec this plan implements
- `CLAUDE.md` — the file most heavily edited; understand the section structure before editing
- `docs/README.md` — secondary edit target
- `docs/superpowers/plans/plan-roadmap.md` — small edit target

## File Structure

- Modify: `CLAUDE.md` (five distinct edits, single commit)
- Modify: `docs/README.md` (two distinct edits, single commit)
- Modify: `docs/superpowers/plans/plan-roadmap.md` (one edit, single commit)
- Do **not** touch: `docs/prompt-shakedown.md`, `run-loop`, `.agent/blockers.md`, `.agent/run-loop-state.json`, `.agent/run-loop.log`, `tests/test_run_loop.py`, any plan file, any SPL source.

---

## Task 1: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the "Intended workflow" paragraph**

In `CLAUDE.md`, replace this exact line:

```
**Intended workflow:** Interactive Claude sessions (with superpowers) are used for bootstrapping, design, and planning. Huntley/run-loop autonomous loops are used for the actual implementation of `shakedown.spl` once a concrete plan is marked in flight in `docs/superpowers/plans/plan-roadmap.md`.
```

with:

```
**Intended workflow:** Interactive Claude sessions (with superpowers) are used for bootstrapping, design, and planning. Implementation sessions are operator-triggered and supervised: start a new session, invoke `superpowers:executing-plans` (or `superpowers:subagent-driven-development`), and work through the active plan task by task with the operator present.
```

- [ ] **Step 2: Rewrite the "Roadmap first" section**

In `CLAUDE.md`, replace this exact block:

```
## Roadmap first

Before starting SPL, prompt, plan, or run-loop work, read:

- `docs/README.md`
- `docs/superpowers/plans/plan-roadmap.md`

The roadmap is the source of truth for what plan is in flight. Do not advance
implementation unless the roadmap has at most one in-flight plan and the active
prompt references that exact plan. If no plan is marked `in flight`, do not
invent implementation work; follow the active prompt's completion behavior or
return to interactive planning from `docs/README.md`.
```

with:

```
## Roadmap first

Before starting SPL, plan, or implementation work, read:

- `docs/README.md`
- `docs/superpowers/plans/plan-roadmap.md`

The roadmap is the source of truth for what plan is in flight. Do not advance
implementation unless the roadmap has at most one in-flight plan. If no plan
is marked `in flight`, do not invent implementation work; return to
interactive planning from `docs/README.md`.
```

- [ ] **Step 3: Replace the `## run-loop` section with `## Implementation workflow`**

In `CLAUDE.md`, replace this exact block (lines 42–65 in the current file):

```
## run-loop

`run-loop` is a Python executable that drives autonomous agent sessions.
It switches automatically between codex and claude when one hits a usage limit.

```bash
./run-loop                            # use the active default prompt
./run-loop docs/some-other-prompt.md  # alternate prompt
./run-loop docs/archive/prompt-shakedown.md  # legacy archived prompt, if you explicitly want it
```

- Current code default: `docs/prompt-shakedown.md`
- Current docs reality: `docs/prompt-shakedown.md` is plan-driven and should point at the current in-flight plan
- Practical guidance: use `./run-loop` only when the roadmap has an in-flight implementation plan and the prompt references that exact plan; otherwise start fresh interactive sessions from `docs/README.md`
- State: `.agent/run-loop-state.json` (tracks which backend was last used)
- Completion marker: derived from prompt filename — `docs/prompt-<name>.md` → `.agent/complete-<name>.md`

To signal completion, write the marker file:
```bash
mkdir -p .agent && touch .agent/complete-shakedown.md
```
The run-loop checks for this file at the top of every iteration and exits when it exists.

`AGENTS.md` is a symlink to `CLAUDE.md` — same instructions served to Codex.
```

with:

````
## Implementation workflow

When a plan is marked `in flight` in `docs/superpowers/plans/plan-roadmap.md`,
start a supervised implementation session:

1. Read the roadmap and identify the active plan.
2. Invoke `superpowers:executing-plans` or `superpowers:subagent-driven-development`
   to work through the plan task by task.
3. The operator triggers each session manually and is present throughout.

`AGENTS.md` is a symlink to `CLAUDE.md` — same instructions served to Codex.

### Legacy: run-loop

The earlier approach used `run-loop`, a Python executor that drove autonomous
agent sessions via `docs/prompt-shakedown.md`. The code and prompt are
preserved for history but are no longer the active workflow.

```bash
./run-loop                            # legacy: use the active default prompt
./run-loop docs/some-other-prompt.md  # legacy: alternate prompt
```

State: `.agent/run-loop-state.json`. Completion marker: `.agent/complete-<name>.md`.
````

Note: the four-backtick fences shown in this step are presentation only — they exist so the inner triple-backtick `bash` block renders inside this plan. When passing the replacement to the `Edit` tool's `new_string` parameter, **do not include the outer four-backtick fence**. The actual section content written into `CLAUDE.md` runs from the line `## Implementation workflow` through the line ending `Completion marker: \`.agent/complete-<name>.md\`.` and contains exactly one triple-backtick code block (the `bash` example).

- [ ] **Step 4: Remove the `## Operator halt switch` section**

In `CLAUDE.md`, delete this exact block (lines 84–91 in the current file):

```
## Operator halt switch (`.agent/blockers.md`)

The autonomous agent reads `.agent/blockers.md` on every iteration via the
`@.agent/blockers.md` university reference in `docs/prompt-shakedown.md`. Any
line starting with `- BLOCK:` halts plan advancement until the operator
removes it. Non-blocking notes use `- NOTE:`. See
`docs/superpowers/specs/2026-04-27-loop-prompt-design.md` §5 for the full
convention.
```

Including the trailing blank line (so two consecutive `##` sections do not collide). The replacement is the empty string.

- [ ] **Step 5: Update the version-cut operator-only note**

In `CLAUDE.md`, replace this exact line:

```
**Operator-only.** Autonomous run-loop agents must NOT run `cz bump`,
```

with:

```
**Operator-only.** Implementation agents must NOT run `cz bump`,
```

(Single-line replacement; the `git tag`, `git push --tags` continuation lines below it are unchanged.)

- [ ] **Step 6: Verify CLAUDE.md changes**

Run:

```bash
grep -n "run-loop\|Huntley" CLAUDE.md
```

Expected: only these residual matches survive, and they are intentional:

- Line in `## What is shakedown?`: `Huntley-loop methodology. See \`docs/lineage.md\` for the full story.` — historical lineage reference, intentional.
- The new `### Legacy: run-loop` subsection content, including `./run-loop` shell snippets and `.agent/run-loop-state.json`.
- `tests/test_run_loop.py # run-loop infrastructure tests` in the test-runner snippet — factually correct (the test file still exists).
- `CLI operator scripts (\`run-loop\`) may use \`print()\` for status output.` in the Python conventions section — factually correct.
- `docs/ralph-loop.md — Huntley/Ralph loop methodology reference and how it applies here` in the Reference materials list — historical reference doc, intentional.

There must be **no** match in the `## Roadmap first` section, no match in the `**Intended workflow:**` paragraph, no `## Operator halt switch` heading, no `Autonomous run-loop agents` phrase.

Also run:

```bash
grep -c "^## Operator halt switch" CLAUDE.md
```

Expected output: `0`.

```bash
grep -c "^## run-loop$" CLAUDE.md
```

Expected output: `0`.

```bash
grep -c "^## Implementation workflow" CLAUDE.md
```

Expected output: `1`.

- [ ] **Step 7: Commit CLAUDE.md changes**

Run:

```bash
git add CLAUDE.md
git commit -m "docs: switch CLAUDE.md to supervised superpowers workflow"
```

---

## Task 2: Update docs/README.md

**Files:**
- Modify: `docs/README.md`

- [ ] **Step 1: Update the optional-context bullet**

In `docs/README.md`, replace this exact line:

```
- [`prompt-shakedown.md`](prompt-shakedown.md) — active `run-loop` prompt; currently exits when the roadmap has no plan marked `in flight`.
```

with:

```
- [`prompt-shakedown.md`](prompt-shakedown.md) — legacy `run-loop` prompt (archived); no longer the active implementation workflow.
```

- [ ] **Step 2: Update the Canonical Flow of Truth entry**

In `docs/README.md`, replace this exact line:

```
- **Operational process artifacts:** `docs/superpowers/plans/plan-roadmap.md` tracks live plan status, and `docs/prompt-shakedown.md` is the active run-loop prompt. Other `docs/superpowers/` content is supporting context only, except for the selected architecture spec linked from `architecture/selected-architecture.md`.
```

with:

```
- **Operational process artifacts:** `docs/superpowers/plans/plan-roadmap.md` tracks live plan status. `docs/prompt-shakedown.md` is the legacy run-loop prompt (archived). Other `docs/superpowers/` content is supporting context only, except for the selected architecture spec linked from `architecture/selected-architecture.md`.
```

- [ ] **Step 3: Verify docs/README.md changes**

Run:

```bash
grep -n "active.*run-loop\|active run-loop" docs/README.md
```

Expected output: empty (no matches). The phrase "active run-loop" or "active `run-loop`" must not appear anywhere in `docs/README.md`.

Run:

```bash
grep -n "legacy.*run-loop" docs/README.md
```

Expected output: two matches — the optional-context bullet and the Canonical Flow of Truth entry.

- [ ] **Step 4: Commit docs/README.md changes**

Run:

```bash
git add docs/README.md
git commit -m "docs: mark prompt-shakedown.md as legacy run-loop artifact in README"
```

---

## Task 3: Update plan-roadmap.md

**Files:**
- Modify: `docs/superpowers/plans/plan-roadmap.md`

- [ ] **Step 1: Update the References entry**

In `docs/superpowers/plans/plan-roadmap.md`, replace this exact line:

```
- `CLAUDE.md` — commit conventions, version cadence, target interface, `run-loop` contract.
```

with:

```
- `CLAUDE.md` — commit conventions, version cadence, target interface, implementation workflow.
```

- [ ] **Step 2: Verify plan-roadmap.md change**

Run:

```bash
grep -n "run-loop contract\|\`run-loop\` contract" docs/superpowers/plans/plan-roadmap.md
```

Expected output: empty (no matches).

Run:

```bash
grep -n "implementation workflow" docs/superpowers/plans/plan-roadmap.md
```

Expected output: one match — the References entry.

- [ ] **Step 3: Commit plan-roadmap.md change**

Run:

```bash
git add docs/superpowers/plans/plan-roadmap.md
git commit -m "docs: drop run-loop contract reference from plan roadmap"
```

---

## Task 4: Final Verification

**Files:**
- No modifications. Read-only verification across the repo.

- [ ] **Step 1: Confirm preserved files are unchanged**

Run:

```bash
git status
git diff --stat HEAD~3..HEAD
```

Expected: working tree clean. The diff between three commits ago and HEAD must show changes **only** in:

- `CLAUDE.md`
- `docs/README.md`
- `docs/superpowers/plans/plan-roadmap.md`

There must be **no** changes to:

- `docs/prompt-shakedown.md`
- `run-loop`
- `.agent/blockers.md`, `.agent/run-loop-state.json`, `.agent/run-loop.log`
- Any file under `src/`, `tests/`, `scripts/`
- Any other plan file under `docs/superpowers/plans/`

- [ ] **Step 2: Confirm legacy artifacts are still readable**

Run:

```bash
test -f docs/prompt-shakedown.md && test -x run-loop && test -f .agent/blockers.md && echo OK
```

Expected output: `OK`.

- [ ] **Step 3: Confirm no forward-facing run-loop instructions remain in the three edited files**

Run:

```bash
grep -n "Autonomous run-loop\|run-loop work\|active prompt\|active run-loop\|Operator halt switch" CLAUDE.md docs/README.md docs/superpowers/plans/plan-roadmap.md
```

Expected output: empty (no matches).

- [ ] **Step 4: Read the rendered Implementation workflow section**

Run:

```bash
sed -n '/^## Implementation workflow/,/^## /p' CLAUDE.md
```

Expected: section displays cleanly, contains the three numbered steps, the `AGENTS.md` symlink line, and the `### Legacy: run-loop` subsection with its `bash` code block. No stray backticks, no broken fences, no truncation mid-section.

- [ ] **Step 5: Read the rendered Roadmap first section**

Run:

```bash
sed -n '/^## Roadmap first/,/^## /p' CLAUDE.md
```

Expected: section reads as a self-consistent instruction. No mention of "run-loop work" or "active prompt".

- [ ] **Step 6: Confirm tests still pass**

Run:

```bash
uv run pytest -q
```

Expected: existing default test suite passes. (No tests should be affected by docs-only changes; this is a regression sanity check.)

- [ ] **Step 7: No commit needed**

Task 4 is verification only. The three task commits already constitute the full change.

---

## Completion criteria

All four tasks above have every checkbox checked. The repository contains three new commits on `main`, in this order:

1. `docs: switch CLAUDE.md to supervised superpowers workflow`
2. `docs: mark prompt-shakedown.md as legacy run-loop artifact in README`
3. `docs: drop run-loop contract reference from plan roadmap`

After this plan ships, future agents reading `CLAUDE.md` and `docs/README.md` will be directed to the supervised superpowers-session model. The `run-loop` executable, prompt, `.agent/` state, and `tests/test_run_loop.py` remain in place as legacy artifacts, available for future removal.
