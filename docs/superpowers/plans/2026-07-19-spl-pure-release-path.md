# SPL-Pure Release Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make committed `shakedown.spl` under `shakespeare run` (and `./shakedown`) achieve full deterministic Markdown.pl parity with **no** Python Markdown rewrite or strip on the production path.

**Architecture:** Follow [2026-07-19-spl-pure-release-path-design.md](../specs/2026-07-19-spl-pure-release-path-design.md). Port Markdown.pl `_StripLinkDefinitions` into Act I and link/image resolution into Act III; retire `rewrite_task3_markdown` / `strip_reference_definitions` from release and IR production entrypoints; keep four-act IR → `splc` → assemble.

**Tech Stack:** Python 3.12+, typed splc IR (`src_ir/`), generated SPL, TOML literary surfaces, pytest, local Markdown.pl oracle, `shakespearelang` CLI.

## Global Constraints

- Sole in-flight plan until shipped. No second roadmap row in flight.
- **SPL literary protocol:** before any IR/SPL/literary edit, read `docs/superpowers/notes/spl-literary-protocol.md`, `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`, `src/literary.toml` (and act literary TOMLs). Reserve all new controlled surfaces + spare scene titles **in the plan or an amendment** before implementation. Implementation agents never invent titles mid-task.
- Exact literary compliance after every SPL-facing checkpoint:
  ```bash
  uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  git diff --exit-code -- src/*.spl shakedown.spl debug/
  ```
- Two-participant scenes only; no new tokens unless a `BLOCK[plan]` amendment names exact codes.
- Email autolinks stay entity-normalized only (`docs/markdown/divergences.md`).
- Do not reintroduce Python Markdown transforms to “fix” failures.
- Conventional commits + push at each logical checkpoint; no force-push.
- Preserve spike dumps and non-link fixture parity at every step.

**SPL-facing regression gate fragment** (run after each production IR/SPL change):

```bash
uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py tests/test_token_dump.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
```

**Pure-SPL probe** (slow; use on focused fixtures until Task 6):

```bash
# After rewrite is off the pure path:
uv run shakespeare run shakedown.spl < "$SHAKEDOWN_MDTEST/<Fixture>.text" > /tmp/out.html
# or: ./shakedown < ...
```

---

### Task 0: Land packaging entry baseline

**Files:**
- Modify (if still uncommitted): `README.md`, `./shakedown`, `./shakedown-dev`, `./shakedown-debug`, `./shakedown-parity`, `scripts/paths.py`, harness/tests using fixture env paths
- Test: `tests/test_wrapper_error_channel.py`

**Interfaces:**
- Consumes: none
- Produces: Public `./shakedown` = `uv run shakespeare run shakedown.spl` (+ stderr error detection). Harness `./shakedown-parity` = current rewrite+IR until later tasks retire rewrite. Env: `SHAKEDOWN_MDTEST`, `SHAKEDOWN_MARKDOWN_PL`, `SHAKEDOWN_SPL`.

- [x] **Step 1: Confirm or finish packaging WIP**

If `git status` still shows the dual-entry packaging diff, finish it to green:

```bash
uv run pytest tests/test_wrapper_error_channel.py tests/test_strict_parity_harness.py -q
echo 'Hello *world*' | ./shakedown | cmp - <(printf '<p>Hello <em>world</em></p>\n')
echo 'Hello *world*' | ./shakedown-parity | cmp - <(printf '<p>Hello <em>world</em></p>\n')
```

Expected: tests pass; both entries emit the emphasis line (parity entry is fast).

Evidence (2026-07-19, grok-implement): 9 passed (`test_wrapper_error_channel` + `test_strict_parity_harness`); `./shakedown` and `./shakedown-parity` both `cmp` equal to `<p>Hello <em>world</em></p>\n`.

- [x] **Step 2: Commit packaging baseline**

```bash
git add README.md shakedown shakedown-dev shakedown-debug shakedown-parity scripts/paths.py \
  scripts/strict_parity_harness.py scripts/differential_smoke.py scripts/markdown_pl_parity_audit.py \
  scripts/probe_documentation_aggregates.py scripts/count_reference_defs.py tests/
git commit -m "$(cat <<'EOF'
chore: dual entry paths for shakespeare release and parity harness

Public ./shakedown runs shakespeare on the committed play; ./shakedown-parity
keeps the fast IR+rewrite path for the suite until SPL owns links.
EOF
)"
git push
```

If already committed, check the step and skip.

---

### Task 1: Inventory pure-SPL red set and rewrite behavior matrix

**Files:**
- Create: `tests/test_spl_pure_inventory.py`
- Create: `docs/superpowers/notes/2026-07-19-spl-pure-rewrite-inventory.md` (evidence only; short)
- Modify: none of production yet

**Interfaces:**
- Consumes: `scripts.slice3_links.rewrite_task3_markdown`, `scripts.paths.mdtest_fixtures_dir`, IR `_interpret_ir` pattern from `tests/test_mdtest.py`
- Produces: Documented list of fixtures/behaviors that require rewrite today; pure-SPL red witnesses committed as failing tests (skipped or xfail with reason until enablement)

- [x] **Step 1: Write inventory helpers and pure-path red contracts**

Add `tests/test_spl_pure_inventory.py` that:

1. Lists every mdtest fixture where `rewrite_task3_markdown(text) != text`.
2. For each such fixture name in
   `{"Amps and angle encoding", "Images", "Links, inline style", "Links, reference style", "Links, shortcut references", "Literal quotes in titles", "Markdown Documentation - Basics", "Markdown Documentation - Syntax"}`,
   asserts a **pure** path is currently wrong:
   - Pure path definition for this task: IR interpreter **without** calling `rewrite_task3_markdown` (feed raw fixture text into `InterpreterState` / `_run_acts` equivalent with rewrite removed at the call site used by the test only).
3. Marks those asserts with `pytest.mark.xfail(strict=True, reason="SPL-pure: rewrite still required")` until Task 5 retires rewrite (or use a module-level flag `PURE_SPL_ENABLED = False` flipped in Task 5).

Minimal shape:

```python
from __future__ import annotations

import pytest

from scripts.paths import mdtest_fixtures_dir
from scripts.slice3_links import rewrite_task3_markdown
from scripts.runtime_constants import DOCUMENTATION_STEP_LIMIT
from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4
from tests.test_mdtest import _normalize_fixture_output, _expected_fixture_output, _FIXTURES_BY_NAME

PURE_SPL_REWRITE_RETIRED = False  # Task 5 flips to True

_REWRITE_TOUCHED = (
    "Amps and angle encoding",
    "Images",
    "Links, inline style",
    "Links, reference style",
    "Links, shortcut references",
    "Literal quotes in titles",
    "Markdown Documentation - Basics",
    "Markdown Documentation - Syntax",
)


def _interpret_ir_raw(input_text: str) -> str:
    """IR without Python rewrite (exposes SPL-pure gaps)."""
    state = InterpreterState(input_text=input_text)
    for act in (ACT1, ACT2, ACT3, ACT4):
        state = run_act(act, state, step_limit=DOCUMENTATION_STEP_LIMIT).state
    return state.output_text()


def test_rewrite_touches_expected_fixture_set() -> None:
    d = mdtest_fixtures_dir()
    touched = sorted(
        p.stem for p in d.glob("*.text") if rewrite_task3_markdown(p.read_text()) != p.read_text()
    )
    assert touched == sorted(_REWRITE_TOUCHED)


@pytest.mark.parametrize("name", _REWRITE_TOUCHED)
def test_raw_ir_matches_oracle_without_rewrite(name: str) -> None:
    if not PURE_SPL_REWRITE_RETIRED:
        pytest.xfail("SPL-pure: rewrite still required on production path")
    input_path, expected_path = _FIXTURES_BY_NAME[name]
    input_text = input_path.read_text()
    expected = _normalize_fixture_output(
        name, _expected_fixture_output(name, input_path, expected_path)
    )
    actual = _normalize_fixture_output(name, _interpret_ir_raw(input_text))
    assert actual == expected
```

Also record a short note file listing, for each touched fixture, the first semantic class of rewrite change (inline link → `<a>`, ref strip, image, title quotes, etc.) by sampling `difflib` of text vs rewrite — human-readable bullets, no novel design.

Evidence (2026-07-19, grok-implement): Added `tests/test_spl_pure_inventory.py` and `docs/superpowers/notes/2026-07-19-spl-pure-rewrite-inventory.md`.

- [x] **Step 2: Run inventory tests**

```bash
uv run pytest tests/test_spl_pure_inventory.py -q
```

Expected: `test_rewrite_touches_expected_fixture_set` passes; parametrized raw-IR tests xfail as intended.

Evidence (2026-07-19, grok-implement): `1 passed, 8 xfailed` — rewrite-touch set green; pure raw-IR witnesses xfail while `PURE_SPL_REWRITE_RETIRED` is false.

- [x] **Step 3: Commit inventory**

```bash
git add tests/test_spl_pure_inventory.py docs/superpowers/notes/2026-07-19-spl-pure-rewrite-inventory.md
git commit -m "test: inventory pure-SPL gaps vs slice3 rewrite"
git push
```

---

### Task 2: Act I — reference definition strip + table (design-bound)

**Files:**
- Modify: `src_ir/act1.py`, `src/10-act1-literary.toml` (or `src/literary.toml` per existing act1 home), generated `src/10-act1-preprocess.spl`, `shakedown.spl`
- Modify: `scripts/splc/interpret.py` — **stop** calling `strip_reference_definitions` once Act I owns strip (end of this task or Task 5; prefer end of this task with green gates)
- Test: `tests/test_act1_references.py` (create), extend `tests/test_spl_pure_inventory.py` witnesses

**Interfaces:**
- Consumes: Markdown.pl `_StripLinkDefinitions` rules in `docs/markdown/reference-mechanics.md`; inventory from Task 1
- Produces: After Act I, input stream has definition lines removed; Rosalind (or design-named carrier) holds a sentinel-terminated case-folded reference table readable by Act III. Exact stack layout must be written into this plan via **Amendment A1** in the same commit as the literary reservation if the first inventory pass requires more labels than estimated below.

**Literary reservation (install before scenes):**

Estimate (amend if short): **16 working + 6 spare** Act I scene titles under a single family prefix `HECATE_REF_*` (or rename to match voice — Hecate sorter / Rosalind librarian). Implementation may not invent titles. Install into the act1 literary TOML `[spares.*]` first, promote to `[scenes.*]` as built.

Minimal behavior contracts (red before implement):

1. Definition line `[foo]: /url "title"` alone → empty/no para content; table lookup foo → `/url` + title.
2. Up to three leading spaces before `[id]:`.
3. Case-fold: `[Foo]: /u` resolves as `foo`.
4. Angle-bracket URL `[id]: <http://x>`.
5. Optional title on next line per oracle.
6. Definition lines do not appear as paragraph text in Act IV for a doc that is only defs + a blank + a short paragraph.
7. Invalid/non-def lines starting with `[` remain body text.

- [ ] **Step 1: Reserve literary titles + write red Act I contracts**

Install spare titles; add `tests/test_act1_references.py` with the contracts above using fast IR **without** Python `strip_reference_definitions` (monkeypatch or temporary local interpret helper that skips the Act I hook). Prove red.

```bash
uv run pytest tests/test_act1_references.py -q
```

Expected: FAIL (defs still in body / empty table).

- [ ] **Step 2: Implement Act I strip + table**

Edit `src_ir/act1.py` only within reserved labels. Two-character scenes. Build table on Rosalind’s stack (or documented carrier). Do not implement Act III resolution yet.

Regenerate and assemble.

- [ ] **Step 3: Remove interpret.py Act I strip hook**

In `scripts/splc/interpret.py`, delete the `act.number == 1 and state.input_pos == 0: strip_reference_definitions(...)` block (and the trailing double-newline tweak **only if** Act I now owns equivalent boundary behavior; if removing the tweak regresses blanks, keep a one-line comment and a focused test proving Act I matches oracle blank handling).

- [ ] **Step 4: Gates**

```bash
uv run pytest tests/test_act1_references.py -q
# Shared fragment — expect link fixtures still red/xfail; non-link suite should stay green
uv run pytest tests/test_mdtest.py -k "not Links and not Images and not Literal and not Basics and not Syntax" -q
uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
```

Note: default `test_mdtest` still uses rewrite; raw inventory xfails remain. Act I tests must pass without Python strip.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat: strip reference definitions in Act I"
git push
```

---

### Task 3: Act III — resolve links and images without pre-emitted HTML

**Files:**
- Modify: `src_ir/act3.py`, Act III literary TOML, generated `src/30-act3-span.spl`, `shakedown.spl`
- Test: `tests/test_act3_links_pure.py` (create), fixture enablement stays via existing mdtest once rewrite retires

**Interfaces:**
- Consumes: Act I reference table layout from Task 2; existing Act III field tags / resume selectors where reusable
- Produces: Raw Markdown `[text](url)`, `[text][id]`, `![alt](url)`, `![alt][id]` (and oracle-required variants from `docs/markdown/reference-mechanics.md`) resolve inside Act III without Python rewrite

**Order of red→green witnesses (one commit family each is OK if gates stay green):**

| Step | Witness | Oracle fixture anchor |
|---|---|---|
| 3a | Inline link + angle-bracket dest + amp encoding | Amps / Links inline |
| 3b | Inline image | Images |
| 3c | Full/collapsed/spaced reference links | Links reference / shortcut |
| 3d | Reference images + title quotes | Images / Literal quotes in titles |
| 3e | Nested brackets / broken-line link text as in fixture | Links reference style |

**Literary:** Reserve Act III working+spare titles **before** 3a (Amendment A2 in plan file if counts exceed initial estimate). Prefer reusing existing `LYRIC_*` machines; only promote new labels when reuse is impossible.

- [ ] **Step 1: Write red pure-IR contracts for 3a–3e**

Each contract: raw Markdown in → Act IV HTML out via IR **without** `rewrite_task3_markdown`, compared to `perl $SHAKEDOWN_MARKDOWN_PL` or `_expected_fixture_output` for a minimal slice.

Run to confirm red:

```bash
uv run pytest tests/test_act3_links_pure.py -q
```

- [ ] **Step 2: Implement resolution (3a→3e)**

Implement in IR; regenerate after each green sub-gate. Do not call Python rewrite from tests for these contracts.

Sub-gate after each letter:

```bash
uv run pytest tests/test_act3_links_pure.py -k '<letter or name>' -q
uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
```

- [ ] **Step 3: Full Act III pure-link gate**

```bash
uv run pytest tests/test_act3_links_pure.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
```

- [ ] **Step 4: Commit**

```bash
git commit -m "feat: resolve links and images in Act III without rewrite"
git push
```

(Multiple commits per 3a–3e are preferred if the work spans iterations.)

---

### Task 4: Retire production rewrite; align IR and parity entry

**Files:**
- Modify: `scripts/release_runtime.py`, `scripts/preprocess_input.py`, `tests/test_mdtest.py` (`_run_acts` / `_interpret_ir`), `./shakedown-parity` (make it pure IR without rewrite, or alias to `./shakedown` with a note), README
- Modify: any test that imports `rewrite_task3_markdown` for **production simulation** — switch to raw input
- Keep: `scripts/slice3_links.py` as optional differential oracle for unit tests of “what rewrite used to do”

**Interfaces:**
- Consumes: Tasks 2–3 green pure-IR contracts
- Produces: No production call chain invokes `rewrite_task3_markdown` or `strip_reference_definitions`

- [ ] **Step 1: Flip inventory flag and remove rewrite from IR test path**

In `tests/test_spl_pure_inventory.py`, set `PURE_SPL_REWRITE_RETIRED = True`.

In `tests/test_mdtest.py` `_run_acts`, stop wrapping with `rewrite_task3_markdown`.

In `scripts/release_runtime.py` `main`, pass stdin (or only non-Markdown plumbing) into `_run_release_ir` **without** rewrite.

Delete or gut `scripts/preprocess_input.py` production use; if the file remains, make it a deprecated thin alias that warns on stderr and writes stdin unchanged (or remove if unused).

- [ ] **Step 2: Prove suite**

```bash
uv run pytest tests/test_spl_pure_inventory.py tests/test_act1_references.py tests/test_act3_links_pure.py -q
uv run pytest tests/test_mdtest.py -q
uv run pytest tests/test_slice3_medium_risk.py tests/test_slice5_documentation_aggregates.py -q
uv run ruff check . && uv run ruff format --check . && uv run pyright
```

Expected: all green without rewrite.

- [ ] **Step 3: Point `./shakedown-parity` at pure IR**

```bash
# shakedown-parity becomes:
#   exec uv run --directory "$DIR" python -m scripts.release_runtime
# with release_runtime no longer rewriting
```

README: state that parity entry is IR-only acceleration, semantically equal to `./shakedown`.

- [ ] **Step 4: Commit**

```bash
git commit -m "fix!: retire slice3 Python rewrite from production paths"
git push
```

---

### Task 5: Pure shakespeare CLI gate on all 23 fixtures

**Files:**
- Modify: `tests/test_mdtest.py` or `tests/test_spl_pure_shakespeare.py` (integration)
- Modify: `docs/performance/budget.md` / `docs/verification-plan.md` with pure-SPL timings if measured
- Test: strict harness with `--shakedown ./shakedown`

**Interfaces:**
- Consumes: Task 4 production path
- Produces: Evidence that real `shakespeare run` matches oracle (may be `@pytest.mark.integration` with long timeout if default suite stays on IR)

- [ ] **Step 1: Add integration module**

```python
# tests/test_spl_pure_shakespeare.py
@pytest.mark.integration
@pytest.mark.parametrize("name", sorted(_IMPLEMENTED_FIXTURES))
def test_shakespeare_cli_matches_oracle(name: str) -> None:
    ...
    # subprocess: [str(REPO / "shakedown")], compare normalized/strict as mdtest
```

Default `pytest` excludes integration (already in `pyproject.toml`).

- [ ] **Step 2: Run integration (operator or CI-with-flag)**

```bash
uv run pytest tests/test_spl_pure_shakespeare.py -m integration -q --timeout=600
# or without pytest-timeout plugin: rely on long wall clock
uv run python scripts/strict_parity_harness.py --shakedown ./shakedown
```

Expected: `summary: 23/23 byte-identical` (Auto links per existing harness rules).

If docs fixtures exceed 120s each, record times in budget.md; do **not** reintroduce rewrite.

- [ ] **Step 3: Commit evidence**

```bash
git commit -m "test: gate pure shakespeare CLI on mdtest fixtures"
git push
```

---

### Task 6: Ship roadmap row and cleanup

**Files:**
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: this plan’s checkboxes; optional archive note
- Modify: README if any “rewrite still required” language remains

- [ ] **Step 1: Final quality gate**

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format --check . && uv run pyright
uv run python scripts/strict_parity_harness.py --shakedown ./shakedown-parity
# Optional slow:
# uv run python scripts/strict_parity_harness.py --shakedown ./shakedown
rg -n "rewrite_task3_markdown|strip_reference_definitions" scripts/release_runtime.py scripts/splc/interpret.py scripts/preprocess_input.py
```

Expected: suite green; production scripts have **no** rewrite/strip calls.

- [ ] **Step 2: Mark roadmap shipped**

Set this plan’s roadmap row to `shipped: YYYY-MM-DD at commit <sha>`.

- [ ] **Step 3: Commit**

```bash
git commit -m "docs: ship SPL-pure release path"
git push
```

---

## Plan self-review

1. **Spec coverage:** Design success criteria map to Tasks 4–6; Act I/III port to Tasks 2–3; inventory to Task 1; packaging prerequisite Task 0.
2. **Placeholders:** Literary exact title strings are reserved at Task 2/3 start (not invented mid-implement). Stack layout for Rosalind table is fixed in Task 2 Step 1 before implementation; if uncertain, Amendment A1 in-repo before coding.
3. **Risk:** Underestimating Act III scene count → `BLOCK[plan]` with spare ledger expansion, not silent title invention.

## Amendment A0 (2026-07-19): Packaging dual-entry is in scope as Task 0

Landing the public shakespeare `./shakedown` and harness `./shakedown-parity` is required before pure-SPL enablement gates. No production rewrite retirement in Task 0.

---

## Execution notes

- Prefer **one unchecked step per MCO/agent iteration** with its evidence gate.
- SPL-changing steps must name and run the literary compliance commands in Global Constraints.
- If Act I table or Act III resolution needs tokens/participants beyond this plan, stop with `- BLOCK[plan]:` and amend; do not expand scope silently.
