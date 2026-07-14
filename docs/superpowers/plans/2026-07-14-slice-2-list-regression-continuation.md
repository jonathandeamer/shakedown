# Slice 2 List-Regression Continuation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the shipped unordered-list handoff after Act II rejects a horizontal-rule candidate, without resuming the broader Slice-2 fixture plan.

**Architecture:** The HR candidate gate has already consumed `*` or `-` and its separator while preserving the first item glyph in `HECATE`. Add one Act-II handoff scene which emits the existing list-open/frame/item-start prefix and goes directly to `PASS_LISTS_ITEM_GLYPH`; all other fallback routes stay unchanged. The source of truth is `src_ir/act2.py`, which renders `src/20-act2-block.spl` and then assembles `shakedown.spl`.

**Tech Stack:** Python 3.13, `scripts.splc` IR/lowering, Shakespeare Programming Language, pytest, local `~/markdown/Markdown.pl` oracle.

## Global Constraints

- Authority: Amendment A3 of `docs/superpowers/specs/2026-07-14-mco-loop-reconciliation-design.md`; the prior MCO reconciliation plan is halted and this is the sole in-flight roadmap plan.
- Scope is only the Act-II `*`/`-` rejected-HR handoff. Do not resume the wider `docs/superpowers/plans/2026-07-14-slice-2-low-risk-fixtures.md` work or change token numbers, fixture baselines, Act I, Act III, Act IV, or Markdown fixture expectations.
- Before editing, read `docs/superpowers/notes/spl-literary-protocol.md`, `docs/superpowers/notes/correctness-first-spl-workflow.md`, `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`, `docs/spl/codegen-style-guide.md`, and `src/literary.toml`.
- Generated artifacts are edited only through `src_ir/act2.py`: run `uv run python -m scripts.splc` and `uv run python scripts/assemble.py`; never hand-edit `src/20-act2-block.spl` or `shakedown.spl`.
- The sole new controlled surface is the ready-to-paste `PASS_HR_FALLBACK_LIST_HANDOFF` block below. It is Incidental, `bare_statement`, uses `(LADY_MACBETH, MACBETH)`, and leaves the six named Act-II spares unreachable. If another title, Recall, or value surface is needed, add exactly one `- BLOCK[plan]:` line to `.agent/blockers.md` and stop.
- Every autonomous commit must end after a blank line with `Agent: <executor>`, `Model: <model>`, `Harness: MCO 0.10.8`, and `Co-authored-by: OpenAI Codex <noreply@openai.com>`; non-force push after each logical checkpoint. A failed push records one `- BLOCK:` line and stops.

## Literary reservation

| Label | State / transition | Operating pair | Pattern |
|---|---|---|---|
| `PASS_HR_FALLBACK_LIST_HANDOFF` | Rejected `*` or `-` HR candidate after its separator is consumed; emit `LIST_OPEN(1)`, matching frame, and `ITEM_START(1)`, then enter `PASS_LISTS_ITEM_GLYPH` with `HECATE` unchanged | `(LADY_MACBETH, MACBETH)` | `bare_statement` |

```toml
# MCO reconciliation A2 working scene
[scenes.PASS_HR_FALLBACK_LIST_HANDOFF]
title = "The broken iron yields the list's first measure."
pattern = "bare_statement"
```

The six explicit spares remain `PASS_HR_PAIR_GUARD`, `PASS_CODE_PAIR_GUARD`, `PASS_CODE_PAIR_RETURN`, `PASS_BLOCK_PAIR_GUARD`, `PASS_HR_PAIR_WATCH`, and `PASS_BLOCK_PAIR_WATCH`; none is authority for new behavior.

---

### Task 1: Restore the consumed-marker list handoff

**Files:**
- Modify: `src_ir/act2.py`
- Modify: `src/20-act2-literary.toml`
- Modify: `tests/test_act2_slice2.py`
- Regenerate: `src/20-act2-block.spl`, `shakedown.spl`

**Interfaces:**
- Consumes: `PUCK` as saved marker and `HECATE` as the first non-HR glyph at `PASS_HR_FALLBACK`.
- Produces: `PASS_LISTS_ITEM_GLYPH` receives `HECATE == ord('a')` for `* alpha` without a second read; `tests/fixtures/token_stream/lists/flat_unordered_tight.dump` stays byte-identical.

- [ ] **Step 1: Confirm the focused contract fails against the unmodified source.**

Run:

```bash
uv run pytest tests/test_act2_slice2.py -k unordered_list_handoff -q
```

Expected: FAIL because the `*` and `-` entries in `PASS_HR_FALLBACK` target `PASS_CODE_REPLAY`, not `PASS_HR_FALLBACK_LIST_HANDOFF`.

- [ ] **Step 2: Implement the one-scene handoff and its source-level contract.**

In `tests/test_act2_slice2.py`, retain or add `test_hr_candidate_fallback_preserves_unordered_list_handoff`. It must assert that `*` and `-` target `PASS_HR_FALLBACK_LIST_HANDOFF`, `_` targets `PASS_CODE_REPLAY`, the new scene's companion is `Char.MACBETH`, it emits in order `LIST_OPEN`, kind `1`, `ITEM_START`, tightness `1`, then goes to `PASS_LISTS_ITEM_GLYPH`, has no `_read()`, and the six named spares remain unreachable. Extend the pair ledger with `PASS_HR_FALLBACK_LIST_HANDOFF: Char.MACBETH`.

Append only the reserved TOML block above. In `src_ir/act2.py`, change `PASS_HR_FALLBACK` so `PUCK == 42` and `PUCK == 45` target the handoff; leave `PUCK == 95` and the raw-glyph route unchanged. Add exactly:

```python
scene(
    "PASS_HR_FALLBACK_LIST_HANDOFF",
    *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 1),
    push(MACBETH, const(1)),
    let(MACBETH, add(val(MACBETH), const(1))),
    push(LADY_MACBETH, const(tokens.ITEM_START)),
    push(LADY_MACBETH, const(1)),
    goto("PASS_LISTS_ITEM_GLYPH"),
    companion=MACBETH,
),
```

Run:

```bash
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_act2_slice2.py -k unordered_list_handoff -q
uv run pytest tests/test_token_dump.py -k flat_unordered_tight -q
uv run pytest tests/test_splc_interpret_parity.py -k flat_unordered_tight -q
uv run pytest tests/test_architecture_spikes.py -k flat_unordered_tight -q
```

Expected: all pass; both dump paths equal the committed baseline and the architecture spike renders the Markdown.pl `<ul>` bytes.

- [ ] **Step 3: Run the complete regression, generated-artifact, and literary gates.**

Run:

```bash
uv run pytest tests/test_token_dump.py -k 'list or nested' -q
uv run pytest tests/test_splc_interpret_parity.py -k list -q
uv run pytest tests/test_architecture_spikes.py -k 'list or nested' -q
uv run pytest tests/test_splc_generated_fragments.py -q
uv run pytest tests/test_spl_parse_smoke.py tests/test_splc_validate.py -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py -q
uv run pytest tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: every command exits zero. If a dirty handoff file prevents safe attribution, stop and record `- BLOCK[plan]:` rather than staging unrelated changes.

- [ ] **Step 4: Commit and push the isolated repair.**

```bash
git add src_ir/act2.py src/20-act2-literary.toml tests/test_act2_slice2.py \
  src/20-act2-block.spl shakedown.spl
git commit -m "fix: restore unordered list fallback"
git push origin HEAD
```

Expected: the commit contains only the listed repair, test, TOML, and generated files, with required provenance trailers.

### Task 2: Close the continuation and return control to governance recovery

**Files:**
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: `docs/superpowers/plans/2026-07-14-mco-loop-reconciliation.md`
- Modify: `.agent/blockers.md`

- [ ] **Step 1: Run the recovery closure gate.**

```bash
uv run pytest tests/test_mco_loop.py -q
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -q
./agent-loop --dry-run
git status --short
```

Expected: all verification commands pass; the dry run reports no unresolved planning-artifact or inventory diagnostic.

- [ ] **Step 2: Mark the continuation shipped and resume only 5R's closure task.**

Change the continuation roadmap row to `shipped: <date> at commit <repair-sha>` and change row 5R from `halted` back to `in flight` after Step 1 passes. The scope-transfer blocker was cleared when this plan became the sole in-flight row; the broad Slice-2 plan remains halted.

- [ ] **Step 3: Commit and push closure state.**

```bash
git add docs/superpowers/plans/plan-roadmap.md \
  docs/superpowers/plans/2026-07-14-mco-loop-reconciliation.md \
  .agent/blockers.md
git commit -m "docs: close list regression continuation"
git push origin HEAD
```

## Plan self-review

- Coverage: Task 1 contains the entire scoped Act-II repair, ready-to-paste controlled prose, generated-artifact workflow, source test, real/fast interpreter list gates, and exact literary compliance commands. Task 2 runs the final recovery gate before returning governance control.
- Scope: no broad Slice-2 fixture work is authorized. The only controlled surface is the stated handoff title; six proportional Act-II spares remain reserved and unreachable.
- Safety: no generated SPL is hand-edited, no token or fixture baseline changes are permitted, and unrelated dirty changes stop the implementation rather than being staged.
