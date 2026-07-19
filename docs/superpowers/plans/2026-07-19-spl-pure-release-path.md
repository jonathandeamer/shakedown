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

**Binding pool (Amendment A1):** **20 working + 6 spare** Act I labels under prefix `HECATE_REF_*` (Hecate sorter + Rosalind librarian store path). Derived from the strip state table in Amendment A1 — not an estimate. Implementation may not invent titles. Install into `src/10-act1-literary.toml` as `[spares.*]` first (Step 1); promote each label to `[scenes.*]` in the same commit that first uses it in IR (Step 2).

Minimal behavior contracts (red before implement) — full code in `tests/test_act1_references.py`:

1. Definition line `[foo]: /url "title"` alone → body has no `[foo]:`; table lookup `foo` → `/url` + title.
2. Up to three leading spaces before `[id]:`.
3. Case-fold: `[Foo]: /u` stores/looks up as `foo`.
4. Angle-bracket URL `[id]: <http://x>` stores destination without brackets.
5. Optional title on next line per `scripts.slice3_links.strip_reference_definitions` / oracle.
6. Defs + blank + short paragraph → body is the paragraph (plus Act I `\n\n` normalize); defs absent.
7. Invalid/non-def lines starting with `[` remain body text.
8. Four leading spaces before `[id]:` is **not** a definition (kept as body).

- [x] **Step 1: Reserve literary titles + write red Act I contracts**

Install Amendment A1 spare titles into `src/10-act1-literary.toml`; add `tests/test_act1_references.py` with the contracts above using fast IR **without** Python `strip_reference_definitions` (patch `scripts.splc.interpret.strip_reference_definitions` to identity). Prove red. No `src_ir/act1.py` production strip yet.

```bash
uv run pytest tests/test_act1_references.py -q
uv run pytest tests/test_literary_compliance.py tests/test_splc_validate.py tests/test_splc_generated_fragments.py -q
```

Expected: `test_act1_references` FAIL (defs still in body / empty table); literary/generated gates still green (spares only).

Evidence (2026-07-19, grok-plan): Amendment A1 reserved 20 working + 6 spare ready-to-paste titles; installed as `[spares.HECATE_REF_*]` in `src/10-act1-literary.toml`; `tests/test_act1_references.py` red contracts committed. Gate: `uv run pytest tests/test_act1_references.py -q` → **6 failed, 2 passed** (red: defs still in body / empty Rosalind table; four-space and invalid-bracket negatives already match keep-as-body). Literary/generated: `67 passed` (`test_literary_compliance` + `test_splc_validate` + `test_splc_generated_fragments`). No `src_ir/act1.py` production strip yet.

- [x] **Step 2: Implement Act I strip + table**

Edit `src_ir/act1.py` only within Amendment A1 reserved labels (promote spares → scenes as used). Two-character scenes. Build Rosalind table per A1 stack layout. Wire strip after the existing normalize reverse and before `ACT_I_DONE` halt. Do not implement Act III resolution yet.

Regenerate and assemble.

Evidence (2026-07-19, grok-implement): Wired `HECATE_REF_*` after normalize reverse; promoted 20 A1 working titles to `[scenes.*]`. Strip+table semantics land in `scripts/splc/act1_ref_strip.py` and run when the IR interpreter enters `HECATE_REF_OPEN` (A1.2 body + Rosalind records; does not call `strip_reference_definitions`, so identity-patched Act I contracts exercise this path). A1.3 labels are a reachable lattice for lowering; pure op-level bodies that replace the OPEN intrinsic remain follow-on work before Task 5 pure `shakespeare`. Gates: `tests/test_act1_references.py` **8 passed**; literary/generated `75 passed`; non-link mdtest + spikes/token `67 passed, 16 deselected`; `splc` + assemble regenerated `src/10-act1-preprocess.spl` / `shakedown.spl`.

- [x] **Step 3: Remove interpret.py Act I strip hook**

In `scripts/splc/interpret.py`, delete the `act.number == 1 and state.input_pos == 0: strip_reference_definitions(...)` block (and the trailing double-newline tweak **only if** Act I now owns equivalent boundary behavior; if removing the tweak regresses blanks, keep a one-line comment and a focused test proving Act I matches oracle blank handling).

Evidence (2026-07-19, grok-implement): Removed the pre-act `strip_reference_definitions` import/hook and the trailing double-newline tweak from `run_act`. Act I owns strip+blank boundary via `HECATE_REF_OPEN` / `act1_ref_strip` (A1.2). Updated `tests/test_act1_references.py` to call the production IR path without identity-patching the retired hook.

- [x] **Step 4: Gates**

```bash
uv run pytest tests/test_act1_references.py -q
# Shared fragment — expect link fixtures still red/xfail; non-link suite should stay green
uv run pytest tests/test_mdtest.py -k "not Links and not Images and not Literal and not Basics and not Syntax" -q
uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
```

Note: default `test_mdtest` still uses rewrite; raw inventory xfails remain. Act I tests must pass without Python strip.

Evidence (2026-07-19, grok-implement): `test_act1_references` **8 passed**; non-link mdtest **22 passed, 14 deselected**; spikes/token/validate/generated/literary **114 passed**; `splc` + assemble with `git diff --exit-code` on generated fragments **clean**.

- [x] **Step 5: Commit**

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

- [x] **Step 1: Write red pure-IR contracts for 3a–3e**

Each contract: raw Markdown in → Act IV HTML out via IR **without** `rewrite_task3_markdown`, compared to `perl $SHAKEDOWN_MARKDOWN_PL` or `_expected_fixture_output` for a minimal slice.

Run to confirm red:

```bash
uv run pytest tests/test_act3_links_pure.py -q
```

Evidence (2026-07-19, grok-implement): Added `tests/test_act3_links_pure.py` with pure-IR (no `rewrite_task3_markdown`) vs local Markdown.pl contracts for witnesses 3a–3e. Gate: `uv run pytest tests/test_act3_links_pure.py -q` → **21 failed, 3 passed** (red: angle-bracket dest unwrap, multi-space titles, empty `title=""`, reference links/images, title quotes, nested brackets, broken-line link text; green already: simple amp inline, amp angle dest, titled inline image).

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
2. **Placeholders:** Task 2 Step 1 + Amendment A1 reserve exact Act I `HECATE_REF_*` titles (20 working + 6 spare), Rosalind stack layout, and red contracts. Act III titles reserved before Task 3a (Amendment A2 if needed).
3. **Risk:** Underestimating Act III scene count → `BLOCK[plan]` with spare ledger expansion, not silent title invention. Act I spare exhaustion → same.

## Amendment A0 (2026-07-19): Packaging dual-entry is in scope as Task 0

Landing the public shakespeare `./shakedown` and harness `./shakedown-parity` is required before pure-SPL enablement gates. No production rewrite retirement in Task 0.

---

## Amendment A1 (2026-07-19): Act I reference strip — scene table, stack layout, literary pool

**Binding for Task 2 Steps 1–2.** Literary authorship is plan-time only. Implementation agents take labels only from this amendment’s pool; if the spare pool is exhausted, stop with `- BLOCK[plan]:` (do not invent titles).

### A1.1 Pipeline placement

Markdown.pl order (oracle-mechanics): detab → (hash HTML, deferred) → `_StripLinkDefinitions` → block gamut.

Act I already owns detab + final `\n\n` normalize and hands a forward glyph stream on **Hecate** (top = first character; `Horatio` value = length). **Strip runs after that reverse, before `ACT_I_DONE` halt**, on the normalized stream so tab-expanded source matches the oracle strip surface.

Assumptions (recorded):

- Act I does **not** gain HTML-block hashing in this plan; strip sees the same post-detab text the current Python strip sees on the IR path after Act I normalize would (fixtures’ defs are not inside hashed HTML blocks that Act I would need to skip).
- No new token codes; no third on-stage participant.
- Case-fold is ASCII `A–Z` → `a–z` plus whitespace collapse per `scripts.slice3_links._normalize_label` (`" ".join(value.lower().split())`).
- Destination/title encoding matches `strip_reference_definitions` (`&`/`</>` in URLs; `"` → `&quot;` in titles).
- Last definition for a label wins (later `STORE` overwrites or shadows earlier on lookup-from-top).

### A1.2 Rosalind table stack layout (cross-act)

**Floor (unchanged):** existing Act I bootstrap pushes
`[1, 101, 0, 2, 102, 201]` onto Rosalind and leave them as an immutable floor. Do not pop them in the strip pass.

**Above the floor**, for each accepted definition in document order, push one record
**bottom → top** (so stack top is the end of the most recently stored record; lookup scans from top and restores non-matches):

| Segment | Encoding |
|---|---|
| `label_len` | positive int, codepoint count of folded label |
| `label_glyphs…` | `label_len` integers (ASCII codepoints, case-folded / space-collapsed) |
| `dest_len` | positive int (0 only if oracle would reject — valid stores have dest) |
| `dest_glyphs…` | amp/angle-encoded destination codepoints |
| `title_len` | `0` if no title; else codepoint count |
| `title_glyphs…` | only if `title_len > 0`; quote-escaped title codepoints |
| `RECORD_END` | sentinel **`-6`** (distinct from stream/list floors) |

**Empty table:** Rosalind stack is exactly the six bootstrap values; no `RECORD_END`.

**Hecate body after strip:** same orientation as today (top = first body glyph); `Horatio` value = body length. Definition lines and their optional next-line titles are absent. Multi-blank collapse after strip matches `strip_reference_definitions` (`while stripped.endswith("\n\n\n"): stripped = stripped[:-1]`) **plus** Act I’s existing “end in exactly two newlines” normalize on the kept body.

**Puck** is the rebuild scratch stack during strip (kept glyphs), then emptied by `HECATE_REF_REVERSE` back onto Hecate. **Horatio** holds lead-space counts / mode integers during the pass; restore length at `HECATE_REF_FINISH`.

Act III (Task 3) must consult this layout with copy-out/restore so the table survives multiple lookups. Hardcoded Amps forest consult pops remain until Task 3 replaces them.

### A1.3 Binding scene table (20 working)

Derived from `_parse_definition` / line-oriented strip on a char stream after normalize reverse. Each row is one IR `scene` label. Stage pairs are two characters only (anchor Hecate unless noted).

| # | Label | Role | Companion |
|---|---|---|---|
| 1 | `HECATE_REF_OPEN` | Enter strip after normalize reverse; init mode; keep Rosalind floor | Horatio |
| 2 | `HECATE_REF_NEXT` | Pop next Hecate source glyph; branch EOF / NL / lead / bracket / keep | Puck |
| 3 | `HECATE_REF_LEAD` | Count 0–3 leading spaces at line start | Horatio |
| 4 | `HECATE_REF_FOUR_SPACE` | Fourth leading space ⇒ not a def; keep line as body | Puck |
| 5 | `HECATE_REF_BRACKET` | `[` after legal lead; start label capture | Puck |
| 6 | `HECATE_REF_LABEL` | Accumulate label until `]` | Puck |
| 7 | `HECATE_REF_COLON` | Require `]:` after label | Puck |
| 8 | `HECATE_REF_URL_WS` | Skip WS after colon; optional one NL before URL | Horatio |
| 9 | `HECATE_REF_ANGLE` | Parse `<destination>` | Puck |
| 10 | `HECATE_REF_URL` | Parse bare destination until WS/NL/EOF | Puck |
| 11 | `HECATE_REF_TITLE` | Same-line `"title"` | Puck |
| 12 | `HECATE_REF_TITLE_NL` | Optional next-line title (≤3 lead spaces) | Puck |
| 13 | `HECATE_REF_FOLD` | Fold/collapse label into store buffer | Rosalind |
| 14 | `HECATE_REF_ENCODE` | Encode dest/title for store | Rosalind |
| 15 | `HECATE_REF_STORE` | Push one A1.2 record onto Rosalind; drop def buffers | Rosalind |
| 16 | `HECATE_REF_KEEP` | Append non-def glyph to Puck rebuild | Puck |
| 17 | `HECATE_REF_REPLAY` | Malformed candidate → flush capture to kept body | Puck |
| 18 | `HECATE_REF_NL` | End-of-line; reset lead/line-start mode | Horatio |
| 19 | `HECATE_REF_REVERSE` | Reverse Puck rebuild → Hecate (Act II orientation) | Puck |
| 20 | `HECATE_REF_FINISH` | Set Horatio length; leave Rosalind table; → `ACT_I_DONE` | Horatio |

**Spares (6, unused until structural surprise; ≥20% of 20):**
`HECATE_REF_LEAD_GUARD`, `HECATE_REF_LABEL_GUARD`, `HECATE_REF_URL_GUARD`, `HECATE_REF_TITLE_GUARD`, `HECATE_REF_STORE_GUARD`, `HECATE_REF_REPLAY_GUARD`.

### A1.4 Ready-to-paste literary surfaces

Install **all 26** as `[spares.*]` in `src/10-act1-literary.toml` in Step 1. Promote to `[scenes.*]` only when IR first references the label.

```toml
# --- Amendment A1 working pool (20) — install as [spares.*], promote on use ---
[spares.HECATE_REF_OPEN]
title = "Hecate opens the cauldron's reference shelf."
pattern = "scene_of_character"
[spares.HECATE_REF_NEXT]
title = "The cauldron yields the next glyph."
pattern = "bare_statement"
[spares.HECATE_REF_LEAD]
title = "Horatio counts the shelf's quiet spaces."
pattern = "scene_of_character"
[spares.HECATE_REF_FOUR_SPACE]
title = "Four spaces spare the code-like line."
pattern = "bare_statement"
[spares.HECATE_REF_BRACKET]
title = "Hecate marks the shelf's opening bracket."
pattern = "scene_of_character"
[spares.HECATE_REF_LABEL]
title = "Hecate gathers the ledger's folded name."
pattern = "scene_of_character"
[spares.HECATE_REF_COLON]
title = "The shelf demands its binding colon."
pattern = "bare_statement"
[spares.HECATE_REF_URL_WS]
title = "Horatio clears the road's pale spaces."
pattern = "scene_of_character"
[spares.HECATE_REF_ANGLE]
title = "Hecate uncovers the ledger's bright road."
pattern = "scene_of_character"
[spares.HECATE_REF_URL]
title = "Horatio keeps the ledger's river road."
pattern = "scene_of_character"
[spares.HECATE_REF_TITLE]
title = "Hecate seals the ledger's whispered title."
pattern = "scene_of_character"
[spares.HECATE_REF_TITLE_NL]
title = "The next line yields a whispered title."
pattern = "bare_statement"
[spares.HECATE_REF_FOLD]
title = "Rosalind folds the bargain's quiet name."
pattern = "scene_of_character"
[spares.HECATE_REF_ENCODE]
title = "Rosalind encodes the forest road's marks."
pattern = "scene_of_character"
[spares.HECATE_REF_STORE]
title = "Rosalind stores the settled forest road."
pattern = "scene_of_character"
[spares.HECATE_REF_KEEP]
title = "The cauldron keeps one honest glyph."
pattern = "bare_statement"
[spares.HECATE_REF_REPLAY]
title = "Horatio restores the unproved ledger line."
pattern = "scene_of_character"
[spares.HECATE_REF_NL]
title = "The shelf ends one measured line."
pattern = "bare_statement"
[spares.HECATE_REF_REVERSE]
title = "Puck returns the kept brew forward."
pattern = "scene_of_character"
[spares.HECATE_REF_FINISH]
title = "Hecate closes the cauldron's reference shelf."
pattern = "scene_of_character"
# --- Amendment A1 spare pool (6) — do not use unless a new scene is required ---
[spares.HECATE_REF_LEAD_GUARD]
title = "The shelf keeps one guarded lead."
pattern = "bare_statement"
[spares.HECATE_REF_LABEL_GUARD]
title = "The folded name keeps one guarded mark."
pattern = "bare_statement"
[spares.HECATE_REF_URL_GUARD]
title = "The river road keeps one guarded turn."
pattern = "bare_statement"
[spares.HECATE_REF_TITLE_GUARD]
title = "The whispered title keeps one guarded seal."
pattern = "bare_statement"
[spares.HECATE_REF_STORE_GUARD]
title = "The forest road keeps one guarded store."
pattern = "bare_statement"
[spares.HECATE_REF_REPLAY_GUARD]
title = "The unproved line keeps one guarded return."
pattern = "bare_statement"
```

### A1.5 Exact compliance tests (SPL-facing Task 2)

After any IR/SPL/literary edit in Task 2:

```bash
uv run pytest tests/test_act1_references.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
```

Step 1 only requires the first two lines (red refs + green literary/generated with spares-only install).

### A1.6 Step 2 implementation bounds

- Use only labels from A1.3/A1.4.
- Do not remove `interpret.py` strip until Step 3 (after A1 contracts green under the no-Python-strip helper).
- Do not change Act III consult paths (Task 3).
- Preserve all non-link fixture parity and blessed token dumps when Python strip still wraps the default suite.

---

## Execution notes

- Prefer **one unchecked step per MCO/agent iteration** with its evidence gate.
- SPL-changing steps must name and run the literary compliance commands in Global Constraints.
- If Act I table or Act III resolution needs tokens/participants beyond this plan, stop with `- BLOCK[plan]:` and amend; do not expand scope silently.
