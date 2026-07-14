# MCO Loop Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile outstanding work and prevent the MCO loop from resuming ordinary roadmap execution when planner routing, unmerged branch work, blockers, or active planning artifacts are ambiguous.

**Architecture:** Perform the one-time repository reconciliation before adding enforcement.  Then keep all decision logic in `scripts/mco_loop.py`: pure helpers discover candidate branches, parse the tracked disposition ledger, validate structured blockers, and detect untracked active planning artifacts; `main()` converts their diagnostics into planner-only actions.  A failed planning action remains a planning action, while failed implementation work retains the current bounded-fix recovery behavior.

**Tech Stack:** Python 3.13, `tomllib`, Git CLI (read-only), pytest, Ruff, pyright, MCO configuration and roadmap Markdown.

## Global Constraints

- Authority is the accepted [MCO reconciliation design](../specs/2026-07-14-mco-loop-reconciliation-design.md).  This is loop infrastructure only: do not modify SPL, generated fragments, `shakedown.spl`, or Markdown rendering behavior.
- The stopped Slice-2 plan remains preserved as halted; this plan is the only in-flight row.  Do not create a second in-flight row.
- Never merge, rebase, delete, force-push, or mutate a branch/worktree automatically.  Candidate code enters `main` only as a fresh, tested, non-conflicting commit after the required review evidence.
- `.agent/branch-dispositions.toml` is intentionally tracked by adding a narrow `.gitignore` exception; other `.agent/` runtime state remains ignored.
- A disposition head mismatch is a fresh review requirement, not an error that may be silently accepted.
- Preserve compatibility with existing free-text `- BLOCK:` and `- BLOCK[plan]:` lines.
- Every implementation checkpoint runs `uv run pytest tests/test_mco_loop.py -q`, `uv run ruff check .`, and `uv run pyright`; the final gate also runs `uv run pytest -q`.
- Each autonomous commit must use the repository’s required `Agent:`, `Model:`, `Harness: MCO 0.10.8`, and executor-specific `Co-authored-by:` trailers, followed by a non-force push.  A push failure records one blocker and stops.

---

## File map

| File | Responsibility |
|---|---|
| `.gitignore` | Permit only the tracked branch-disposition ledger inside `.agent/`. |
| `.agent/branch-dispositions.toml` | Durable disposition, head, and reason for every unmerged local branch. |
| `.agent/blockers.md` | Replace the opaque merge-conflict line with a structured branch-reconciliation blocker, then remove it only after a terminal disposition. |
| `scripts/mco_loop.py` | Branch inventory, ledger parsing, structured-blocker validation, untracked-artifact detection, canonical action recovery, and `main()` integration. |
| `tests/test_mco_loop.py` | Unit tests for every pure helper and action-routing boundary. |
| `docs/superpowers/plans/2026-07-14-development-efficiency.md` | Reconcile previously landed cache/cooldown commits with the plan’s checkbox/evidence state. |
| `docs/superpowers/specs/2026-07-14-development-efficiency-design.md` | Commit the previously untracked accepted design as historical infrastructure context. |
| `docs/superpowers/plans/plan-roadmap.md` | Record recovery completion and leave Slice 2 halted pending a fresh explicit resume decision. |

### Task 1: Reconcile the outstanding branches and active planning artifacts

**Files:**
- Create: `.agent/branch-dispositions.toml`
- Modify: `.gitignore`, `.agent/blockers.md`
- Modify: `docs/superpowers/plans/2026-07-14-development-efficiency.md`
- Add: `docs/superpowers/specs/2026-07-14-development-efficiency-design.md`

**Interfaces:**
- Produces a ledger whose entries have `head: str`, `disposition: Literal["preserve", "superseded", "integrated"]`, and nonempty `reason: str`.
- Removes the active blocker only after `fix-665750fcbb154a4dadcddbfc55ab3326-codex-implement` has a terminal, evidence-backed disposition.

- [x] **Step 1: Capture immutable review evidence for both candidate branches.**

Run the following read-only comparison and add its command, merge base, changed-file list, and conclusion to the relevant `reason` fields; do not edit code during this step.

```bash
git log --oneline main..fix-665750fcbb154a4dadcddbfc55ab3326-codex-implement
git diff --stat main...fix-665750fcbb154a4dadcddbfc55ab3326-codex-implement
git log --oneline main..codex/implement-a9e381f6
git diff --stat main...codex/implement-a9e381f6
uv run pytest tests/test_act3_contracts.py tests/test_act2_frame_floors.py -q
```

Expected: the Slice-2 repair is assessed against current main rather than merged by assumption; the carrier-observer branch is assessed against shipped 4S contract coverage.

- [x] **Step 2: Write terminal branch dispositions and replace the opaque blocker.**

Use the recorded current 40-character heads below.  Preserve the historical WIP exactly as shown.  If the Step-1 comparison finds behavior absent from main, reproduce it with a new focused test and a fresh mainline implementation commit before recording `integrated`; otherwise record `superseded` and cite the current-main test evidence.  Never merge either original branch.

```toml
[branches."spike-a-lists-wip"]
head = "a31e61cfa18f462ab2028b9428b23ff7eaf640fb"
disposition = "preserve"
reason = "Documented non-parsing pre-splc Spike-A redesign reference; never a merge candidate."

[branches."fix-665750fcbb154a4dadcddbfc55ab3326-codex-implement"]
head = "cd89aa80d8da93793fe9c749754702e3cd10f1c7"
disposition = "review"
reason = "Task 1 Step 1 compares this stale Slice-2 repair against current main before a terminal disposition is recorded."

[branches."codex/implement-a9e381f6"]
head = "888b200675edec0148a592b9cfe9110755da59fb"
disposition = "review"
reason = "Task 1 Step 1 compares carrier-observer coverage with shipped 4S contracts before a terminal disposition is recorded."
```

Replace the free-text merge-conflict blocker, while review is active, with this exact grammar; remove it after both candidate entries become terminal:

```text
- BLOCK[plan]: branch=fix-665750fcbb154a4dadcddbfc55ab3326-codex-implement; head=cd89aa80d8da93793fe9c749754702e3cd10f1c7; base=17f7f306adac7071368668c1475b12cfeb841b19; request=supersede; detail=Review stale Slice-2 repair against current main before resuming roadmap work.
```

- [x] **Step 3: Register the development-efficiency work without pretending it was loop progress.**

Commit both currently untracked documents.  In the plan, check only steps whose named commits and stated evidence are present on `main` (`8f2aab8`, `ef53139`, `6cd7fe5`, `f0dd88e`, `48f7fc8`, `55b6a5b`, `8a4fa1a`, `74704ad`, and `a1891ce`); annotate each checked step with its exact commit and test evidence.  If a proposed step lacks evidence, replace it with a completed historical limitation rather than claiming it shipped.  Add a concise design status note that this is operator-directed infrastructure history, not a second roadmap plan.

Run: `git diff --check && uv run pytest tests/test_inprocess_interceptor.py tests/test_mco_loop.py -q`

Expected: the artifacts are tracked, their historical scope is auditable, and no untracked planning document remains.

- [x] **Step 4: Commit the reconciliation record.**

```bash
git add .gitignore .agent/branch-dispositions.toml .agent/blockers.md \
  docs/superpowers/plans/2026-07-14-development-efficiency.md \
  docs/superpowers/specs/2026-07-14-development-efficiency-design.md
git commit -m "docs: reconcile mco loop work inventory"
git push origin HEAD
```

Expected: the commit contains documentation/ledger state only; neither candidate branch is mutated.

### Task 2: Preserve planner routing during failed-action recovery

**Files:**
- Modify: `scripts/mco_loop.py`
- Modify: `tests/test_mco_loop.py`

**Interfaces:**
- Consumes: `apply_failure_action(action: NextAction, state: Mapping[str, object]) -> NextAction`.
- Produces: unchanged `PLAN` actions on `backend_failure`/`no_progress`, and `FIX` actions only for non-planning canonical actions.

- [x] **Step 1: Add focused failing recovery tests.**

Add these assertions beside the existing action-routing tests:

```python
def test_failed_planner_action_remains_planner_action() -> None:
    action = NextAction(ActionKind.PLAN, "amend blocker", None, None, ())
    recovered = mco_loop.apply_failure_action(
        action, {"last_failure": {"kind": "backend_failure"}}
    )
    assert recovered == action


def test_failed_implementation_action_becomes_fix_action() -> None:
    action = NextAction(ActionKind.IMPLEMENT, "execute step", None, "step", ())
    recovered = mco_loop.apply_failure_action(
        action, {"last_failure": {"kind": "no_progress"}}
    )
    assert recovered.kind is ActionKind.FIX
    assert recovered.step == "step"
```

Run: `uv run pytest tests/test_mco_loop.py -k 'failed_planner or failed_implementation' -q`

Expected: the planner test fails because the current implementation returns `FIX`.

- [x] **Step 2: Make recovery conditional on the canonical action kind.**

At the start of `apply_failure_action`, preserve planner actions:

```python
if action.kind is ActionKind.PLAN:
    return action
```

Leave the existing failure-kind filter and `NextAction(ActionKind.FIX, ...)` construction unchanged for `IMPLEMENT` and `FIX` inputs.

Run: `uv run pytest tests/test_mco_loop.py -k 'failed_planner or failed_implementation or planner_only' -q`

Expected: planner-only blockers continue to select the planning pool after an availability-independent failure.

- [x] **Step 3: Commit the routing repair.**

```bash
git add scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "fix: preserve mco planner recovery routing"
git push origin HEAD
```

### Task 3: Add tracked branch inventory and disposition validation

**Files:**
- Modify: `scripts/mco_loop.py`
- Modify: `tests/test_mco_loop.py`
- Modify: `.agent/branch-dispositions.toml`

**Interfaces:**
- Add `BranchDisposition(name: str, head: str, disposition: str, reason: str)` and `BranchIssue(name: str, head: str, base: str | None, detail: str)` frozen dataclasses.
- Add `load_branch_dispositions(path: Path) -> dict[str, BranchDisposition]` and `branch_inventory_issues(repo: Path, ledger: Mapping[str, BranchDisposition]) -> tuple[BranchIssue, ...]`.
- `branch_inventory_issues` uses only `git for-each-ref`, `git rev-parse`, and `git merge-base`; it returns issues and never calls a mutating Git command.

- [x] **Step 1: Add pure-helper tests using a mocked Git output seam.**

Refactor `_git_output` to accept `repo: Path = REPO`, then monkeypatch it in tests.  Cover: no candidates; a merged branch; an unledgered unmerged branch; a `review` disposition; a stale ledger head; an invalid TOML disposition; and a `preserve` entry whose head matches.

```python
def test_branch_inventory_reports_unledgered_unmerged_branch(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mco_loop, "_git_output", lambda args, repo=tmp_path: {
        ("for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads"): "topic abc\n",
        ("merge-base", "--is-ancestor", "topic", "main"): "",
        ("merge-base", "topic", "main"): "base\n",
    }.get(tuple(args), ""))
    assert mco_loop.branch_inventory_issues(tmp_path, {}) == (
        mco_loop.BranchIssue("topic", "abc", "base", "missing disposition"),
    )
```

Run: `uv run pytest tests/test_mco_loop.py -k 'branch_inventory or branch_disposition' -q`

Expected: FAIL until the dataclasses and helpers exist.

- [x] **Step 2: Implement fail-closed ledger parsing and inventory.**

Load TOML with `tomllib`; reject unknown keys, non-40-hex heads, empty reasons, and dispositions outside `{"review", "preserve", "superseded", "integrated"}` using `ValueError`.  For each local branch except `main`, use `git merge-base --is-ancestor <branch> main`; skip only branches already merged.  Emit issues for missing entries, `review`, head drift, and remote-only unmerged refs.  Sort results by branch name for stable prompts and tests.

Run: `uv run pytest tests/test_mco_loop.py -k 'branch_inventory or branch_disposition' -q`

Expected: all inventory cases pass without changing any branch.

- [ ] **Step 3: Convert branch issues to a planner-only action before normal step selection.**

Add `reconciliation_action(rows, repo=REPO) -> NextAction | None`.  It returns `ActionKind.PLAN`, the active plan path, and a summary containing every `BranchIssue` when inventory is nonempty; otherwise it returns `None`.  In `main()`, call it after `determine_next_action()` and before `apply_failure_action()`, replacing the canonical action only when non-`None`.

Add an integration-style main test that a ledger entry with `disposition = "review"` selects the planning pool, and one terminal ledger test that reaches the ordinary active-plan action.

Run: `uv run pytest tests/test_mco_loop.py -k 'reconciliation_action or branch_inventory' -q`

Expected: review work cannot be dispatched to an implementation provider.

- [ ] **Step 4: Commit the branch fence.**

```bash
git add scripts/mco_loop.py tests/test_mco_loop.py .agent/branch-dispositions.toml
git commit -m "feat: reconcile unmerged mco branch work"
git push origin HEAD
```

### Task 4: Validate structured blockers and fence unregistered active plans

**Files:**
- Modify: `scripts/mco_loop.py`
- Modify: `tests/test_mco_loop.py`

**Interfaces:**
- Add `BranchBlocker(branch: str, head: str, base: str, request: str, detail: str)` and `parse_branch_blocker(line: str) -> BranchBlocker | None`.
- Add `invalid_branch_blockers(blockers: Sequence[str], repo: Path = REPO) -> tuple[str, ...]` and `unregistered_planning_artifacts(repo: Path = REPO) -> tuple[Path, ...]`.

- [ ] **Step 1: Add failing validation and artifact-detection tests.**

Cover a valid structured line; missing field; invalid request; branch/head/base mismatch; legacy free-text planning blocker; no artifacts; an untracked `docs/superpowers/plans/example.md`; an untracked `docs/superpowers/specs/example.md`; and ignored `.agent/mco-loop-state.json`.

```python
def test_unregistered_planning_artifacts_excludes_ignored_agent_state(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        mco_loop, "_git_output",
        lambda args, repo=tmp_path: "docs/superpowers/plans/example.md\n.agent/mco-loop-state.json\n",
    )
    assert mco_loop.unregistered_planning_artifacts(tmp_path) == (
        tmp_path / "docs/superpowers/plans/example.md",
    )
```

Run: `uv run pytest tests/test_mco_loop.py -k 'branch_blocker or unregistered_planning' -q`

Expected: FAIL until the validators and artifact fence exist.

- [ ] **Step 2: Implement validation without breaking legacy blockers.**

Parse only lines beginning `- BLOCK[plan]: branch=` with `; `-separated `key=value` fields.  Require exactly `branch`, `head`, `base`, `request`, and `detail`; permit only `review`, `integrate`, and `supersede` requests.  Validate the branch head and merge base via read-only Git calls.  An invalid structured blocker produces a `FIX` action whose summary contains the validation failure; a valid one continues through existing planner routing.  `unregistered_planning_artifacts` filters `git ls-files --others --exclude-standard` to the two documentation directories and returns sorted paths.

Run: `uv run pytest tests/test_mco_loop.py -k 'branch_blocker or unregistered_planning or legacy_blocker' -q`

Expected: legacy lines retain their present behavior, while malformed branch context cannot send an agent on an ambiguous repair.

- [ ] **Step 3: Integrate both fences into canonical action selection.**

In `main()`, before applying failed-action recovery, give precedence to invalid structured-blocker diagnostics (`FIX`), then unregistered active-plan/spec artifacts (`PLAN`), then branch reconciliation (`PLAN`), then the normal roadmap/blocker action.  Use the current active plan path in every generated action and include all affected paths/branches in the summary.

Add tests proving precedence and proving a prior planner backend failure cannot downgrade either fence from `PLAN` to `FIX`.

Run: `uv run pytest tests/test_mco_loop.py -k 'fence_precedence or unregistered_planning or failed_planner' -q`

Expected: every ambiguity has a deterministic, safe action kind.

- [ ] **Step 4: Commit the actionable-blocker and artifact fences.**

```bash
git add scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "feat: fence ambiguous mco reconciliation state"
git push origin HEAD
```

### Task 5: Verify recovery controls and close the governance plan

**Files:**
- Modify: `docs/2026-07-12-mco-loop-details.md`
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: this plan

**Interfaces:**
- The ordinary loop dry run reports a planner action for an unresolved review and normal active-plan action only with terminal ledger entries and no unregistered planning artifacts.
- After this plan ships, Slice 2 remains halted until an operator-approved fresh plan marks it in flight.

- [ ] **Step 1: Add the operational documentation.**

Document the ledger location, allowed dispositions, structured blocker grammar, unregistered-artifact fence, and the rule that a failed planning action remains planning work.  Include the safe operator workflow: inspect → record disposition → commit → `./agent-loop --dry-run`; never delete a branch merely to satisfy the inventory.

- [ ] **Step 2: Run the complete evidence gate.**

```bash
uv run pytest tests/test_mco_loop.py -q
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q
./agent-loop --dry-run
git status --short
```

Expected: every Python gate exits zero.  The dry run contains no unresolved inventory/artifact diagnostic after Task 1 and reports a normal non-running next action; the final status contains only files intentionally staged for the checkpoint.

- [ ] **Step 3: Mark the recovery shipped without resuming Slice 2.**

After the closure commit in Step 4 is pushed, make one follow-up documentation commit that changes this row to shipped and records that already-created closure commit hash.  Keep Slice 2’s halted status and add a current-reconciliation paragraph stating that a new interactive planning decision is required before it can resume.  Clear the blocker only if its branch entry is terminal and all final gates passed.

- [ ] **Step 4: Commit and push the closure.**

```bash
git add docs/2026-07-12-mco-loop-details.md \
  docs/superpowers/plans/plan-roadmap.md \
  docs/superpowers/plans/2026-07-14-mco-loop-reconciliation.md \
  .agent/blockers.md
git commit -m "docs: complete mco loop reconciliation"
git push origin HEAD
```

## Plan self-review

- Coverage: Task 1 resolves the actual branch/artifact debt; Task 2 fixes the observed planner-routing failure; Task 3 adds durable branch state; Task 4 validates structured blockers and planning artifacts; Task 5 verifies and documents the resulting operating model.
- Safety: all Git inspection is read-only and all branch outcomes require a documented human/evidence-backed decision.  No task performs a destructive branch operation.
- Scope: the plan deliberately halts rather than resumes Slice 2, so its Markdown implementation can only continue through a later explicit planning decision.
