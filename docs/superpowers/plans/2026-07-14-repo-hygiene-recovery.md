# Repo Hygiene Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile the stale Task 5 Step 2 hygiene blocker, preserving the
already-shipped span result and allowing the roadmap to proceed only after fresh
completion evidence.

**Architecture:** This is a verification-first recovery. The current worktree
is already clean, so the normal path changes only operational records. A
strictly bounded fallback repairs the reported `scripts/codegen_html.py` import
and formatting debt if it reappears, then proves code-generation and literary
output remain unchanged.

**Tech Stack:** Python 3.12, Ruff, pytest, splc/codegen compliance tests, and
the committed Shakedown release artifact.

## Global Constraints

- Read `docs/superpowers/plans/plan-roadmap.md`,
  `docs/superpowers/specs/2026-07-14-repo-hygiene-recovery-design.md`, and
  `docs/superpowers/notes/spl-literary-protocol.md` before editing.
- Because the bounded fallback can touch `scripts/codegen_html.py`, also read
  `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`,
  `docs/spl/codegen-style-guide.md`, and `src/literary.toml`. No new literary
  prose is authorized; classify the change as a non-prose mechanical repair.
- Do not hand-edit generated SPL, modify `src_ir/`, change the compiler or
  validator, reserve scenes, or change Markdown behavior.
- The exact literary/codegen compliance command is:
  `uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q`.
- Preserve unrelated worktree changes. At the logical checkpoint, make one
  conventional commit with the required MCO provenance trailers and push the
  current branch. Never force-push.

---

### Task 1: Reconcile and close the stale hygiene gate

**Files:**

- Modify: `.agent/blockers.md`
- Modify: `docs/superpowers/plans/2026-07-12-span-architecture-spike.md`
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Conditional modify only if the first gate fails: `scripts/codegen_html.py`

**Consumes:** The original Task 5 Step 2 completion-gate commands and the
accepted recovery design.

**Produces:** A fresh hygiene/completion record, no active hygiene blocker, and
a shipped reconciliation row. If the gate cannot be restored under the bounded
repair, one planner-only blocker instead.

- [x] **Step 1: Re-run the exact hygiene diagnostics before editing source.**

  Run:

  ```bash
  uv run ruff check .
  uv run ruff format --check .
  uv run pytest tests/test_repo_hygiene.py -q
  ```

  Expected: `All checks passed!`, all files already formatted, and `2 passed`.
  Record the command outputs and date in the recovery evidence below. If all
  three pass, do not edit `scripts/codegen_html.py`; continue directly to Step
  3.

  **Evidence (2026-07-14):**
  - `uv run ruff check .` → `All checks passed!` (exit 0)
  - `uv run ruff format --check .` → `85 files already formatted` (exit 0)
  - `uv run pytest tests/test_repo_hygiene.py -q` → `2 passed` (exit 0)

  All three passed as expected. `scripts/codegen_html.py` was not touched.
  Step 2's fallback is not applicable; continuing to Step 3 in the next
  iteration.

- [x] **Step 2: Apply only the pre-authorized mechanical fallback if Step 1 fails.** *(not applicable — Step 1 passed all three diagnostics, so this conditional fallback was not triggered.)*

  In `scripts/codegen_html.py`, delete this line only when it is present and
  unused:

  ```python
  import re
  ```

  Then run:

  ```bash
  uv run ruff format scripts/codegen_html.py
  uv run ruff check scripts/codegen_html.py
  uv run ruff format --check scripts/codegen_html.py
  uv run pytest tests/test_codegen_html.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py -q
  ```

  Expected: Ruff succeeds and the codegen/literary command passes. Do not alter
  any string literal, `_ATOM_BY_VALUE` lookup, emitted value phrase, or function
  behavior. If this exact repair does not restore the gates, append one
  `- BLOCK[plan]:` line to `.agent/blockers.md` with the failing command and
  diagnostic, then stop without proceeding.

- [x] **Step 3: Run the original completion gate and full default suite.**

  Run:

  ```bash
  uv run pytest -q
  uv run pytest tests/test_architecture_spikes.py -q
  uv run pytest tests/test_splc_generated_fragments.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'
  ```

  Expected: every command exits zero; generated/literary checks pass; all
  architecture spikes remain byte-identical; and strict parity reports the
`Amps and angle encoding` fixture byte-identical. Treat any failure as a
  blocker with its exact command and output, not permission to broaden this
  plan.

  **Evidence (2026-07-14):**
  - `uv run pytest -q` → `660 passed, 26 skipped, 2 deselected` (exit 0)
  - `uv run pytest tests/test_architecture_spikes.py -q` → `19 passed` (exit 0)
  - `uv run pytest tests/test_splc_generated_fragments.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q` → `1 passed, 210 deselected` (exit 0)
  - `uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'` → `summary: 1/1 byte-identical` (exit 0)

  All four completion-gate commands passed with fresh 2026-07-14 evidence.
  Step 4 remains for closure records, commit, and push in the next iteration.

- [x] **Step 4: Record closure, commit, and push.**

  **Evidence (2026-07-14):** Step 2 was skipped — Step 1's three diagnostics
  (`uv run ruff check .`, `uv run ruff format --check .`,
  `uv run pytest tests/test_repo_hygiene.py -q`) all passed on the first run,
  so the pre-authorized `scripts/codegen_html.py` fallback was never
  triggered and that file is not part of this closure commit. Step 3's four
  completion-gate commands all exited zero: `uv run pytest -q` (660 passed,
  26 skipped, 2 deselected), `uv run pytest tests/test_architecture_spikes.py -q`
  (19 passed), the generated/literary/Amps command (1 passed, 210 deselected),
  and `uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'`
  (1/1 byte-identical). `.agent/blockers.md` already had no hygiene line to
  remove — the log's only content is its header. See
  `2026-07-12-span-architecture-spike.md` Task 5 for the linked amendment.

  Add dated evidence to this plan stating whether Step 2 was skipped or used
  and listing the Step 1 and Step 3 exit results. Remove the resolved hygiene
  line from `.agent/blockers.md`. Add a concise Task 5 amendment to
  `2026-07-12-span-architecture-spike.md` linking this recovery plan and its
  fresh successful completion evidence. In the roadmap, mark row 4R shipped
  with the resulting commit SHA and leave row 5 pending.

  Run:

  ```bash
  git add .agent/blockers.md docs/superpowers/plans/2026-07-12-span-architecture-spike.md docs/superpowers/plans/2026-07-14-repo-hygiene-recovery.md docs/superpowers/plans/plan-roadmap.md scripts/codegen_html.py
  git commit -m "chore: reconcile stale repo hygiene gate" \
    -m "Agent: codex-terra-escalate
  Model: gpt-5.6-terra
  Harness: MCO 0.10.8
  Co-authored-by: OpenAI Codex <noreply@openai.com>"
  git push origin main
  ```

  Expected: commit and non-force push succeed. Omit `scripts/codegen_html.py`
  from `git add` when Step 2 was skipped. If the push fails, append one
  `- BLOCK:` line to `.agent/blockers.md` naming the push failure and stop.
