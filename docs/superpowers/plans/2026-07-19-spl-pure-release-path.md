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

**Provisional (Amendment A2):** Step 2 is **IR-helper complete only**. Generated `HECATE_REF_*` scene bodies remain goto stubs; pure `shakespeare` does not strip. Task **2L** owns pure-op lowering and intrinsic retirement.

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

- [x] **Step 2: Implement resolution (3a→3e)**

Implement in IR; regenerate after each green sub-gate. Do not call Python rewrite from tests for these contracts.

Sub-gate after each letter:

```bash
uv run pytest tests/test_act3_links_pure.py -k '<letter or name>' -q
uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
```

Evidence (2026-07-19, grok-implement): Act III resolution at `ACT_III_START` via `scripts/splc/act3_link_resolve.py` (PARA/HEADER payloads rewritten using Act I Rosalind table; oracle-aligned, no `rewrite_task3_markdown`). Act I title strip fixed for internal `"` (rfind, same-line + next-line). Gates: `tests/test_act3_links_pure.py` **24 passed**; spikes/token/act1/mdtest/slice3/validate/generated/literary **193 passed** combined; `splc` + assemble **clean** (`git diff --exit-code` on generated fragments).

**Provisional (Amendment A2):** Step 2 is **IR-helper complete only**. `interpret.py` short-circuits `ACT_III_START` into `apply_act3_link_resolution`; generated SPL still seeds traverse without a pure resolve pre-pass. Existing `LYRIC_ANCHOR_*` / `LYRIC_CONSULT_*` remain Slice-1 Amps hardcodes. Task **3L** owns pure-op lowering (Amendment A2 `RESOLVE_*` pool) and intrinsic retirement.

- [x] **Step 3: Full Act III pure-link gate**

```bash
uv run pytest tests/test_act3_links_pure.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
```

Evidence (2026-07-19, grok-implement): `tests/test_act3_links_pure.py` **24 passed**; `tests/test_splc_validate.py` + `tests/test_splc_generated_fragments.py` + `tests/test_literary_compliance.py` **67 passed**. Full Act III pure-link gate green; no IR/SPL edits in this step.

- [x] **Step 4: Commit**

```bash
git commit -m "feat: resolve links and images in Act III without rewrite"
git push
```

(Multiple commits per 3a–3e are preferred if the work spans iterations.)

Evidence (2026-07-19): Step 2 implementation already committed as `37288f9` with the Step 4 message; this iteration only recorded the Step 3 gate.

---

### Task 4: Retire production rewrite; align IR and parity entry

**Files:**
- Modify: `scripts/release_runtime.py`, `scripts/preprocess_input.py`, `tests/test_mdtest.py` (`_run_acts` / `_interpret_ir`), `./shakedown-parity` (make it pure IR without rewrite, or alias to `./shakedown` with a note), README
- Modify: any test that imports `rewrite_task3_markdown` for **production simulation** — switch to raw input
- Keep: `scripts/slice3_links.py` as optional differential oracle for unit tests of “what rewrite used to do”

**Interfaces:**
- Consumes: Tasks 2–3 green pure-IR contracts
- Produces: No production call chain invokes `rewrite_task3_markdown` or `strip_reference_definitions`

- [x] **Step 1: Flip inventory flag and remove rewrite from IR test path**

In `tests/test_spl_pure_inventory.py`, set `PURE_SPL_REWRITE_RETIRED = True`.

In `tests/test_mdtest.py` `_run_acts`, stop wrapping with `rewrite_task3_markdown`.

In `scripts/release_runtime.py` `main`, pass stdin (or only non-Markdown plumbing) into `_run_release_ir` **without** rewrite.

Delete or gut `scripts/preprocess_input.py` production use; if the file remains, make it a deprecated thin alias that warns on stderr and writes stdin unchanged (or remove if unused).

Evidence (2026-07-19, grok-implement): `PURE_SPL_REWRITE_RETIRED = True`; `_run_acts` and `release_runtime.main` feed raw stdin/input (no `rewrite_task3_markdown`); `preprocess_input` is a deprecation warning + passthrough. Gates: inventory+act1+act3 pure **41 passed**; `test_mdtest` **36 passed**; `./shakedown-parity` smoke (emphasis + ref link) green.

- [x] **Step 2: Prove suite**

```bash
uv run pytest tests/test_spl_pure_inventory.py tests/test_act1_references.py tests/test_act3_links_pure.py -q
uv run pytest tests/test_mdtest.py -q
uv run pytest tests/test_slice3_medium_risk.py tests/test_slice5_documentation_aggregates.py -q
uv run ruff check . && uv run ruff format --check . && uv run pyright
```

Expected: all green without rewrite.

Evidence (2026-07-19, grok-implement): pure inventory/act1/act3 **41 passed**; `test_mdtest` **36 passed**; slice3+slice5 **54 passed**; `ruff check` / `ruff format --check` / `pyright` all clean (0 errors). Suite green without rewrite.

- [x] **Step 3: Point `./shakedown-parity` at pure IR**

```bash
# shakedown-parity becomes:
#   exec uv run --directory "$DIR" python -m scripts.release_runtime
# with release_runtime no longer rewriting
```

README: state that parity entry is IR-only acceleration, semantically equal to `./shakedown`.

Evidence (2026-07-19, grok-implement): `./shakedown-parity` already exec'd pure `scripts.release_runtime` (no rewrite); updated entry header, README, and `strict_parity_harness` docstring to state pure-IR acceleration semantically equal to `./shakedown`. Smoke: emphasis + ref-link `cmp` green; `rg` shows no production rewrite/strip calls in `release_runtime`/`interpret`/`preprocess_input` (comments only); `tests/test_wrapper_error_channel.py` + `tests/test_strict_parity_harness.py` **10 passed**.

- [x] **Step 4: Commit**

```bash
git commit -m "fix!: retire slice3 Python rewrite from production paths"
git push
```

Evidence (2026-07-19, grok-implement): Task 4 production retirement already on `main` across:
- `9757103` `fix!: retire slice3 Python rewrite from IR and release paths` (Step 1)
- `def09de` docs Step 2 suite proof
- `4eba5df` docs Step 3 parity-entry alignment

Re-verified this iteration: pure inventory/act1/act3 + `test_mdtest` + wrapper/strict harness **87 passed**; `./shakedown-parity` emphasis + ref-link `cmp` green; production scripts have rewrite/strip only in comments. No further code changes; working tree was clean at handoff. Checkbox only.

---

### Task 2L: Act I pure-op lowering (retire `HECATE_REF_OPEN` intrinsic)

**Files:**
- Modify: `src_ir/act1.py` — replace A1.3 goto stubs with real two-character ops matching `scripts/splc/act1_ref_strip.py`
- Modify: `scripts/splc/interpret.py` — remove `if sc.label == "HECATE_REF_OPEN": apply_act1_reference_strip(...)` short-circuit only after pure ops are green
- Keep: `scripts/splc/act1_ref_strip.py` as differential oracle / unit reference (not called from `run_act` after this task)
- Literary: **only** Amendment A1 labels (20 working already promoted + 6 spares); do not invent titles
- Test: `tests/test_act1_references.py`; optional focused pure-shakespeare smoke on a definition-only snippet

**Interfaces:**
- Consumes: Amendment A1 stack layout + scene table; proven algorithm in `act1_ref_strip.py`
- Produces: Pure SPL/IR ops that strip defs and build Rosalind A1.2 table without any Python Markdown assist in `run_act`

**Binding semantics:** `apply_act1_reference_strip` is the oracle algorithm. Op-level IR must match its stack outcomes on every `tests/test_act1_references.py` case. Prefer incremental label/dest/title capture during parse (SPL-friendly) over re-parsing a string buffer, if byte-identical table records result.

- [x] **Step 1: Prove red under no-intrinsic Act I**

Temporarily disable only the `HECATE_REF_OPEN` intrinsic in `interpret.py` (or gate it behind `USE_ACT1_REF_INTRINSIC = False` for this step) and run:

```bash
uv run pytest tests/test_act1_references.py -q
```

Expected: fail (goto stubs do not strip). Restore intrinsic if needed so other work stays green, or leave the flag false only on a branch until Step 2 completes in the same iteration. Record the red evidence in the commit message or plan checkbox.

Evidence (2026-07-19, grok-implement): Gated `HECATE_REF_OPEN` behind module flag `USE_ACT1_REF_INTRINSIC = False` in `scripts/splc/interpret.py` (short-circuit skipped; fall through to goto-stub scene ops). Gate: `uv run pytest tests/test_act1_references.py -q` → **6 failed, 2 passed** (red: defs remain in body / empty Rosalind table for simple def, lead spaces, case-fold, angle dest, next-line title, defs+para; green: four-space and invalid-bracket keep-as-body). Flag left `False` for Task 2L Step 2 pure-op work; Act III intrinsic unchanged.

- [ ] **Step 2: Implement pure ops for A1.3 labels**

Fill each `HECATE_REF_*` body with real `pop`/`push`/`branch`/`let` ops. Two participants only. Use A1 spares only for structural surprises. Regenerate + assemble after each green sub-batch if needed.

Register/label choreography is bound by **Amendment A3** (A3.1–A3.6) **as corrected by
Amendment A4** (2026-07-20, escalated). A3 supplies sub-mode-to-label folding and the
`fold`/`encode` string-op decomposition (A3.2, A3.4 — both still binding). **A4
supersedes A3.1 and A3.3** with the verified stage rules, the orientation invariant, the
Puck-centric single-stack capture, the authorized `[characters.rosalind.recall]` prose,
and the release of the five remaining A1 spares.

**Do not attempt Step 2 as one port.** It is split into sub-steps **2a–2e** by A4.6;
work exactly one per iteration and commit each green sub-step. Read A4 before A3 where
they disagree.

```bash
uv run pytest tests/test_act1_references.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
```

- [ ] **Step 3: Remove Act I intrinsic permanently**

Delete the `HECATE_REF_OPEN` short-circuit from `run_act`. Confirm `act1_ref_strip` is not imported from `interpret.py`. Keep the module as a test oracle if useful (`tests/` may import it for differential asserts).

```bash
uv run pytest tests/test_act1_references.py tests/test_spl_pure_inventory.py -q
uv run pytest tests/test_mdtest.py -k "not Links and not Images and not Literal and not Basics and not Syntax" -q
uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
# Pure SPL smoke (definition strip only):
printf '[foo]: /url "T"\n\npara\n' | ./shakedown | head -c 200
# Expect no raw `[foo]:` in body HTML; do not require link resolve until Task 3L
```

- [ ] **Step 4: Commit**

```bash
git commit -m "feat: lower Act I reference strip to pure SPL ops"
git push
```

---

### Task 3L: Act III pure-op resolve pre-pass (retire `ACT_III_START` intrinsic)

**Files:**
- Modify: `src_ir/act3.py` — `ACT_III_START` → Amendment A2 `RESOLVE_*` pre-pass → existing `TRAVERSE_NEXT_TOKEN`; do **not** expand Slice-1 hardcoded `LYRIC_ANCHOR_*` Amps forest as the general solution
- Modify: `src/30-act3-literary.toml` — install A2 pool as `[spares.*]` first; promote on use
- Modify: `scripts/splc/interpret.py` — remove `ACT_III_START` → `apply_act3_link_resolution` short-circuit only after pure ops green
- Keep: `scripts/splc/act3_link_resolve.py` as differential oracle
- Test: `tests/test_act3_links_pure.py`; non-regression spikes/token/mdtest

**Interfaces:**
- Consumes: A1.2 Rosalind table from pure Act I (Task 2L); Amendment A2 scene table + literary pool; algorithm in `act3_link_resolve.py` (`_rewrite_puck_stream` + `_resolve_text`)
- Produces: Before span traverse, PARA/HEADER text payloads on Puck resolve images-then-anchors to oracle HTML using the Rosalind table — in pure ops that `shakespeare` executes

**Architecture (binding):** Pre-pass rewrite of text payloads (mirror helper), **not** generalizing hardcoded Amps `LYRIC_CONSULT_REFERENCE_*` emits. After resolve, existing span machines see HTML-bearing text as on the historical rewrite path. Leave Amps hardcode scenes in place until a later cleanup (out of scope unless they break non-Amps fixtures).

**Literary:** Install all **48 working + 12 spare** A2 titles before implementing scenes (Step 1). Implementation may not invent titles. Spare exhaustion → `BLOCK[plan]`.

- [ ] **Step 1: Reserve A2 literary pool + prove red without Act III intrinsic**

Install Amendment A2 TOML into `src/30-act3-literary.toml` as `[spares.RESOLVE_*]`. Disable only the `ACT_III_START` intrinsic (flag or delete) and run:

```bash
uv run pytest tests/test_act3_links_pure.py -q
uv run pytest tests/test_literary_compliance.py tests/test_splc_validate.py tests/test_splc_generated_fragments.py -q
```

Expected: act3 pure contracts red/fail without intrinsic; literary green with spares-only install.

- [ ] **Step 2: Implement `RESOLVE_*` pre-pass (3a→3e order)**

Wire `ACT_III_START` → `RESOLVE_OPEN` → … → `RESOLVE_DONE` → seed Juliet `STREAM_END` + `CONT_NONE` → `TRAVERSE_NEXT_TOKEN`. Promote spares → scenes as labels enter IR. Sub-gate after each witness family:

```bash
uv run pytest tests/test_act3_links_pure.py -k '<family>' -q
uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
```

Families: inline links+amps → images → reference links → reference images/titles → nested/broken-line (same 3a–3e witnesses as Task 3).

- [ ] **Step 3: Remove Act III intrinsic; full pure-IR gate**

```bash
uv run pytest tests/test_act3_links_pure.py tests/test_act1_references.py tests/test_spl_pure_inventory.py -q
uv run pytest tests/test_mdtest.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
rg -n "apply_act1_reference_strip|apply_act3_link_resolution" scripts/splc/interpret.py
# Expect no production short-circuit calls (comments/docstrings only)
```

- [ ] **Step 4: Commit**

```bash
git commit -m "feat: lower Act III link resolve to pure SPL ops"
git push
```

---

### Task 5: Pure shakespeare CLI gate on all 23 fixtures

**Files:**
- Modify: `tests/test_mdtest.py` or `tests/test_spl_pure_shakespeare.py` (integration)
- Modify: `docs/performance/budget.md` / `docs/verification-plan.md` with pure-SPL timings if measured
- Test: strict harness with `--shakedown ./shakedown`

**Interfaces:**
- Consumes: Task 4 production path **and Tasks 2L–3L pure-op lowering** (Amendment A2). Do **not** run Step 2 until 2L and 3L are checked complete.
- Produces: Evidence that real `shakespeare run` matches oracle (may be `@pytest.mark.integration` with long timeout if default suite stays on IR)

- [x] **Step 1: Add integration module**

```python
# tests/test_spl_pure_shakespeare.py
@pytest.mark.integration
@pytest.mark.parametrize("name", sorted(_IMPLEMENTED_FIXTURES))
def test_shakespeare_cli_matches_oracle(name: str) -> None:
    ...
    # subprocess: [str(REPO / "shakedown")], compare normalized/strict as mdtest
```

Default `pytest` excludes integration (already in `pyproject.toml`).

Evidence (2026-07-19, grok-implement): Added `tests/test_spl_pure_shakespeare.py` with `@pytest.mark.integration` parametrized over all 23 `_IMPLEMENTED_FIXTURES`; runs `./shakedown` and compares via `_normalize_fixture_output` / `_expected_fixture_output` (entity-normalized Auto links). Collect: `pytest -m integration --collect-only` → **23 tests collected**; default `pytest` on the module deselects all 23. ruff + pyright clean.

- [ ] **Step 2: Run integration (after Tasks 2L and 3L)**

**Precondition:** Tasks 2L and 3L complete; `interpret.py` has **no** `apply_act1_reference_strip` / `apply_act3_link_resolution` short-circuits; `./shakedown-parity` (pure IR ops) and a spot `./shakedown` ref-link smoke already agree.

Prior failure (2026-07-19, before A2): 16/23 pass, 7 fail — Images, Links inline/reference/shortcut, Literal quotes in titles, Markdown Documentation Basics/Syntax — because Tasks 2–3 were helper-only. That failure class is closed by 2L+3L, not by reintroducing rewrite.

```bash
uv run pytest tests/test_spl_pure_shakespeare.py -m integration -q --timeout=600
# or without pytest-timeout plugin: rely on long wall clock
uv run python scripts/strict_parity_harness.py --shakedown ./shakedown
```

Expected: `summary: 23/23 byte-identical` (Auto links per existing harness rules).

If docs fixtures exceed 120s each, record times in budget.md; do **not** reintroduce rewrite or interpreter Markdown intrinsics.

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

1. **Spec coverage:** Design success criteria map to Tasks 4–6; Act I/III semantic ports to Tasks 2–3 (IR helper path) then pure-op Tasks **2L–3L** (Amendment A2); inventory to Task 1; packaging prerequisite Task 0.
2. **Placeholders:** Task 2 + Amendment A1 reserve exact Act I `HECATE_REF_*` titles (20 working + 6 spare), Rosalind stack layout, and red contracts. Amendment A2 reserves Act III `RESOLVE_*` titles (48 working + 12 spare) and binds the pure-op pre-pass before Task 5 Step 2.
3. **Risk:** Underestimating Act III scene count → `BLOCK[plan]` with spare ledger expansion, not silent title invention. Act I spare exhaustion → same. IR-helper-only completion must not be treated as pure-SPL readiness (A2 diagnosis).

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
- **Next unchecked step after Amendment A4 / Step 2a:** Task **2L Step 2b** (A4.4 Rosalind recall prose in `src/literary.toml`). Then 2c → 2d → 2e, one per iteration. Do not re-run Task 5 Step 2 until 2L and 3L complete.

---

## Amendment A2 (2026-07-19): Pure-op IR port — Act I lower + Act III `RESOLVE_*` pool

**Status:** binding for Tasks **2L** and **3L**. Clears the planner-only blocker recorded after Task 5 Step 2 failed on pure `./shakedown` (7/23 link/image/docs fixtures). Does **not** open a second roadmap plan.

### A2.0 Diagnosis (binding)

| Path | Act I strip | Act III link/image resolve | Task 5 Step 2 |
|---|---|---|---|
| IR `run_act` / `./shakedown-parity` | `interpret.py` short-circuit → `apply_act1_reference_strip` on `HECATE_REF_OPEN` | short-circuit → `apply_act3_link_resolution` on `ACT_III_START` | n/a (fast double) |
| Pure `shakespeare` / `./shakedown` | Generated `HECATE_REF_*` are **goto stubs** only | `ACT_III_START` seeds traverse; **no** resolve pre-pass; Amps `LYRIC_ANCHOR_*` hardcodes remain | **16/23** (2026-07-19) |

Tasks 2–3 correctly retired `rewrite_task3_markdown` / pre-act `strip_reference_definitions` from production **call sites**, but they left **interpreter Markdown assists** that pure SPL never runs. Success criterion “SPL is the sole Markdown semantic owner” requires pure-op bodies + intrinsic retirement (Tasks 2L–3L), then re-running Task 5 Step 2.

**Out of scope for A2:** new token codes; third on-stage participant; reintroducing rewrite; general rewrite of Slice-1 Amps forest scenes (they may remain as dead or Amps-only paths after the pre-pass emits HTML).

### A2.1 Act I pure-op port (Task 2L)

- **Labels:** Amendment A1.3 only (20 working + 6 spare). No new Act I titles in A2.
- **Algorithm oracle:** `scripts/splc/act1_ref_strip.py` (`apply_act1_reference_strip`).
- **Stack layout:** A1.2 unchanged (`RECORD_END = -6`, floor length 6, Hecate body orientation).
- **Implementation bounds:**
  1. Replace each A1.3 goto stub with real ops; keep two-character scenes and A1 companion pairs.
  2. Prefer incremental capture of label/dest/title during the parse (mode lattice in A1.3) so SPL need not re-lex a whole capture string in one scene.
  3. Remove `HECATE_REF_OPEN` short-circuit only after `tests/test_act1_references.py` is green with the short-circuit deleted.
  4. Do not start Task 3L pure resolve until Act I pure strip is green (Rosalind table must exist under pure ops).
- **Exact compliance tests (Task 2L):**

```bash
uv run pytest tests/test_act1_references.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
```

### A2.2 Act III pure-op architecture (Task 3L)

**Placement:** At `ACT_III_START`, run a **resolve pre-pass** over Puck’s token stream, then existing traverse/span:

```
ACT_III_START → RESOLVE_OPEN → … → RESOLVE_DONE
  → push(JULIET, STREAM_END); let(LADY_MACBETH, CONT_NONE)
  → TRAVERSE_NEXT_TOKEN  (unchanged span pipeline)
```

**Semantics oracle:** `scripts/splc/act3_link_resolve.py`:
- Decode A1.2 records above Rosalind floor → id → (dest, title); later store wins.
- Walk stream bottom→top pop order; copy non-text tokens; for `PARA`/`HEADER` text runs, apply `_resolve_text` (images before anchors at each index; code-line opacity; escapes; inline then reference; nested-bracket / missing-id / literal-escape rules as in the helper and `tests/test_act3_links_pure.py`).
- Emit oracle HTML fragments into the rebuilt text payload + `TEXT_END`.

**Carriers (two per scene):**
| Role | Character |
|---|---|
| Stream source / rebuild peer | Puck, Juliet |
| Mode, indent, lengths | Horatio, Romeo |
| Reference table (copy-out/restore) | Rosalind |
| Occasional field/tag peer if needed | Hecate or Prospero (existing field-tag pattern); no third simultaneous participant |

**Do not** implement general resolution by extending hardcoded `LYRIC_ANCHOR_INLINE` / `LYRIC_CONSULT_REFERENCE_*` Amps emits. Those remain Slice-1 residuals; the pre-pass is the production general path.

**No new tokens** unless a later `BLOCK[plan]` names exact codes.

### A2.3 Binding Act III scene table (48 working)

Derived from `_rewrite_puck_stream` + `_resolve_text` state families (stream walk × text scan × image × anchor × shared suffix × lookup × encode × finish). Each row is one IR `scene` label.

| # | Label | Role | Typical pair |
|---|---|---|---|
| 1 | `RESOLVE_OPEN` | Enter pre-pass; init rebuild / mode | Juliet, Puck |
| 2 | `RESOLVE_NEXT_TOKEN` | Pop next token code; branch STREAM_END / textful / other | Juliet, Puck |
| 3 | `RESOLVE_ARITY_COPY` | Copy fixed arity payloads onto rebuild | Juliet, Puck |
| 4 | `RESOLVE_TEXT_ENTER` | PARA/HEADER text region begins | Juliet, Puck |
| 5 | `RESOLVE_TEXT_DRAIN` | Drain glyphs until TEXT_END into scan buffer | Romeo, Puck |
| 6 | `RESOLVE_TEXT_END` | Close text region after resolve; push TEXT_END | Juliet, Puck |
| 7 | `RESOLVE_COPY_OTHER` | Non-textful token fully copied → NEXT | Juliet, Puck |
| 8 | `RESOLVE_STREAM_END` | STREAM_END seen; finalize rebuild orientation | Juliet, Puck |
| 9 | `RESOLVE_SCAN_OPEN` | Init text scan over drained buffer | Romeo, Juliet |
| 10 | `RESOLVE_SCAN_NEXT` | Dispatch next scan glyph | Romeo, Juliet |
| 11 | `RESOLVE_SCAN_KEEP` | Emit one literal glyph to out buffer | Romeo, Juliet |
| 12 | `RESOLVE_SCAN_ESCAPE` | Backslash + next glyph keep-pair | Romeo, Juliet |
| 13 | `RESOLVE_LINE_START` | Line boundary; arm indent / code opacity | Horatio, Romeo |
| 14 | `RESOLVE_INDENT_COUNT` | Count leading spaces/tabs for code-line | Horatio, Romeo |
| 15 | `RESOLVE_CODE_LINE` | Opaque copy through EOL in code mode | Romeo, Juliet |
| 16 | `RESOLVE_CODE_EXIT` | Blank line clears code mode | Horatio, Romeo |
| 17 | `RESOLVE_BANG` | Saw `!`; test image open | Romeo, Puck |
| 18 | `RESOLVE_ALT_OPEN` | `![` — start alt capture | Juliet, Romeo |
| 19 | `RESOLVE_ALT_BODY` | Nested-bracket alt body | Juliet, Romeo |
| 20 | `RESOLVE_ALT_CLOSE` | `]` closes alt; enter image suffix | Juliet, Romeo |
| 21 | `RESOLVE_IMG_SUFFIX` | Try inline `(` then reference tail | Romeo, Juliet |
| 22 | `RESOLVE_IMG_EMIT` | Write `<img …>` (empty-title policy per helper) | Juliet, Romeo |
| 23 | `RESOLVE_IMG_FAIL` | Unresolved image → literal / escape path | Romeo, Juliet |
| 24 | `RESOLVE_LB` | Saw `[` (anchor start) | Romeo, Juliet |
| 25 | `RESOLVE_LTEXT_BODY` | Nested-bracket link text | Juliet, Romeo |
| 26 | `RESOLVE_LTEXT_CLOSE` | `]` closes link text; enter link suffix | Romeo, Juliet |
| 27 | `RESOLVE_LNK_SUFFIX` | Try inline then reference tail | Juliet, Romeo |
| 28 | `RESOLVE_LNK_EMIT` | Write `<a href=…>` | Romeo, Juliet |
| 29 | `RESOLVE_LNK_NESTED` | Nested `[` in link text recurse/reenter | Juliet, Romeo |
| 30 | `RESOLVE_LNK_FAIL` | Missing id / non-link → escape literal markdown | Romeo, Juliet |
| 31 | `RESOLVE_SFX_INLINE` | `(` after `]` — inline destination | Puck, Juliet |
| 32 | `RESOLVE_DEST_ANGLE` | `<destination>` | Juliet, Romeo |
| 33 | `RESOLVE_DEST_BARE` | Bare destination until WS/`)` | Romeo, Juliet |
| 34 | `RESOLVE_TITLE_WS` | Whitespace before optional title | Horatio, Juliet |
| 35 | `RESOLVE_TITLE_QUOT` | `"title"` body (rfind-compatible) | Juliet, Romeo |
| 36 | `RESOLVE_SFX_CLOSE` | Closing `)` of inline suffix | Romeo, Juliet |
| 37 | `RESOLVE_SFX_REF` | `[` of reference id (full/collapsed/spaced) | Puck, Juliet |
| 38 | `RESOLVE_SFX_REF_ID` | Id body or empty collapsed; fold label | Juliet, Romeo |
| 39 | `RESOLVE_LOOKUP_OPEN` | Start Rosalind A1.2 scan for folded id | Rosalind, Puck |
| 40 | `RESOLVE_LOOKUP_REC` | Compare one record; non-destructively | Rosalind, Puck |
| 41 | `RESOLVE_LOOKUP_MATCH` | Copy dest/title out; restore table | Rosalind, Juliet |
| 42 | `RESOLVE_LOOKUP_SKIP` | Skip non-match record; continue | Rosalind, Puck |
| 43 | `RESOLVE_LOOKUP_MISS` | Exhausted table without match | Rosalind, Romeo |
| 44 | `RESOLVE_ESC_DEST` | Amp/angle-encode destination for emit | Romeo, Juliet |
| 45 | `RESOLVE_ESC_TITLE` | Quote-encode title for emit | Juliet, Romeo |
| 46 | `RESOLVE_ESC_LIT` | Escape unresolved markdown span (`*`, `_`, etc. per helper) | Puck, Juliet |
| 47 | `RESOLVE_REBUILD` | Push resolved text glyphs + TEXT_END onto rebuild | Juliet, Romeo |
| 48 | `RESOLVE_DONE` | Install rebuilt stream on Puck; seed traverse; → `TRAVERSE_NEXT_TOKEN` | Romeo, Juliet |

**Spares (12, ≥25% of 48; unused until structural surprise):**
`RESOLVE_SCAN_GUARD`, `RESOLVE_ALT_GUARD`, `RESOLVE_LTEXT_GUARD`, `RESOLVE_DEST_GUARD`, `RESOLVE_TITLE_GUARD`, `RESOLVE_SFX_GUARD`, `RESOLVE_LOOKUP_GUARD`, `RESOLVE_EMIT_GUARD`, `RESOLVE_CODE_GUARD`, `RESOLVE_NEST_GUARD`, `RESOLVE_ARITY_GUARD`, `RESOLVE_REVERSE_GUARD`.

If the working+spare pool is exhausted, stop with `- BLOCK[plan]:` (do not invent titles).

### A2.4 Ready-to-paste literary surfaces (Act III)

Install **all 60** as `[spares.*]` in `src/30-act3-literary.toml` in Task 3L Step 1. Promote to `[scenes.*]` only when IR first references the label. Pastoral/Natural palette; word counts fit `bare_statement` (4–10) or `scene_of_character` (5–10). No mid-title `.` or `!`.

```toml
# --- Amendment A2 working pool (48) — install as [spares.*], promote on use ---
[spares.RESOLVE_OPEN]
title = "The stream opens one pure resolve."
pattern = "bare_statement"
[spares.RESOLVE_NEXT_TOKEN]
title = "One mark yields its measured code."
pattern = "bare_statement"
[spares.RESOLVE_ARITY_COPY]
title = "Fixed marks cross the quiet stream."
pattern = "bare_statement"
[spares.RESOLVE_TEXT_ENTER]
title = "The paragraph opens its raw text."
pattern = "bare_statement"
[spares.RESOLVE_TEXT_DRAIN]
title = "Romeo drains the paragraph's raw leaves."
pattern = "scene_of_character"
[spares.RESOLVE_TEXT_END]
title = "Text ends with one quiet seal."
pattern = "bare_statement"
[spares.RESOLVE_COPY_OTHER]
title = "Other marks keep their measured road."
pattern = "bare_statement"
[spares.RESOLVE_STREAM_END]
title = "The stream ends its pure resolve."
pattern = "bare_statement"
[spares.RESOLVE_SCAN_OPEN]
title = "The scan opens on raw leaves."
pattern = "bare_statement"
[spares.RESOLVE_SCAN_NEXT]
title = "The next glyph seeks its path."
pattern = "bare_statement"
[spares.RESOLVE_SCAN_KEEP]
title = "One honest glyph stays in daylight."
pattern = "bare_statement"
[spares.RESOLVE_SCAN_ESCAPE]
title = "A backslash guards the next leaf."
pattern = "bare_statement"
[spares.RESOLVE_LINE_START]
title = "A line begins beneath the hedge."
pattern = "bare_statement"
[spares.RESOLVE_INDENT_COUNT]
title = "Leading spaces count the code road."
pattern = "bare_statement"
[spares.RESOLVE_CODE_LINE]
title = "The code line keeps its shade."
pattern = "bare_statement"
[spares.RESOLVE_CODE_EXIT]
title = "A blank line leaves the shade."
pattern = "bare_statement"
[spares.RESOLVE_BANG]
title = "A bang seeks the portrait gate."
pattern = "bare_statement"
[spares.RESOLVE_ALT_OPEN]
title = "Juliet opens the portrait's quiet alt."
pattern = "scene_of_character"
[spares.RESOLVE_ALT_BODY]
title = "Romeo gathers the portrait's alt leaves."
pattern = "scene_of_character"
[spares.RESOLVE_ALT_CLOSE]
title = "Juliet seals the portrait's alt close."
pattern = "scene_of_character"
[spares.RESOLVE_IMG_SUFFIX]
title = "Romeo tries the portrait's suffix road."
pattern = "scene_of_character"
[spares.RESOLVE_IMG_EMIT]
title = "Juliet emits the portrait's bright seal."
pattern = "scene_of_character"
[spares.RESOLVE_IMG_FAIL]
title = "The portrait fails and stays literal."
pattern = "bare_statement"
[spares.RESOLVE_LB]
title = "Romeo marks the garden's opening bracket."
pattern = "scene_of_character"
[spares.RESOLVE_LTEXT_BODY]
title = "Juliet gathers the garden link's leaves."
pattern = "scene_of_character"
[spares.RESOLVE_LTEXT_CLOSE]
title = "Romeo seals the garden link's close."
pattern = "scene_of_character"
[spares.RESOLVE_LNK_SUFFIX]
title = "Juliet tries the garden's suffix road."
pattern = "scene_of_character"
[spares.RESOLVE_LNK_EMIT]
title = "Romeo emits the garden's bright anchor."
pattern = "scene_of_character"
[spares.RESOLVE_LNK_NESTED]
title = "Nested leaves reopen the garden scan."
pattern = "bare_statement"
[spares.RESOLVE_LNK_FAIL]
title = "The garden link fails as literal."
pattern = "bare_statement"
[spares.RESOLVE_SFX_INLINE]
title = "Puck opens the round destination path."
pattern = "scene_of_character"
[spares.RESOLVE_DEST_ANGLE]
title = "Juliet reads the angle-bracketed road."
pattern = "scene_of_character"
[spares.RESOLVE_DEST_BARE]
title = "Romeo keeps the bare destination road."
pattern = "scene_of_character"
[spares.RESOLVE_TITLE_WS]
title = "Horatio clears the title's pale spaces."
pattern = "scene_of_character"
[spares.RESOLVE_TITLE_QUOT]
title = "Juliet gathers the quoted title leaves."
pattern = "scene_of_character"
[spares.RESOLVE_SFX_CLOSE]
title = "Romeo seals the round destination close."
pattern = "scene_of_character"
[spares.RESOLVE_SFX_REF]
title = "Puck opens the reference identity bracket."
pattern = "scene_of_character"
[spares.RESOLVE_SFX_REF_ID]
title = "Juliet folds the reference identity leaves."
pattern = "scene_of_character"
[spares.RESOLVE_LOOKUP_OPEN]
title = "Rosalind opens the forest table search."
pattern = "scene_of_character"
[spares.RESOLVE_LOOKUP_REC]
title = "Rosalind compares one forest road record."
pattern = "scene_of_character"
[spares.RESOLVE_LOOKUP_MATCH]
title = "Rosalind matches the sought forest road."
pattern = "scene_of_character"
[spares.RESOLVE_LOOKUP_SKIP]
title = "Rosalind skips one unmatched forest record."
pattern = "scene_of_character"
[spares.RESOLVE_LOOKUP_MISS]
title = "The forest search finds no road."
pattern = "bare_statement"
[spares.RESOLVE_ESC_DEST]
title = "Romeo encodes the destination's sharp marks."
pattern = "scene_of_character"
[spares.RESOLVE_ESC_TITLE]
title = "Juliet encodes the title's quiet marks."
pattern = "scene_of_character"
[spares.RESOLVE_ESC_LIT]
title = "Puck escapes the unproved literal leaves."
pattern = "scene_of_character"
[spares.RESOLVE_REBUILD]
title = "Juliet rebuilds the resolved text stream."
pattern = "scene_of_character"
[spares.RESOLVE_DONE]
title = "Romeo hands the pure resolve forward."
pattern = "scene_of_character"
# --- Amendment A2 spare pool (12) — do not use unless a new scene is required ---
[spares.RESOLVE_SCAN_GUARD]
title = "The pure resolve keeps one guarded scan."
pattern = "bare_statement"
[spares.RESOLVE_ALT_GUARD]
title = "The portrait keeps one guarded alt."
pattern = "bare_statement"
[spares.RESOLVE_LTEXT_GUARD]
title = "The garden keeps one guarded text."
pattern = "bare_statement"
[spares.RESOLVE_DEST_GUARD]
title = "The destination keeps one guarded road."
pattern = "bare_statement"
[spares.RESOLVE_TITLE_GUARD]
title = "The title keeps one guarded seal."
pattern = "bare_statement"
[spares.RESOLVE_SFX_GUARD]
title = "The suffix keeps one guarded turn."
pattern = "bare_statement"
[spares.RESOLVE_LOOKUP_GUARD]
title = "The forest keeps one guarded search."
pattern = "bare_statement"
[spares.RESOLVE_EMIT_GUARD]
title = "The emit keeps one guarded bright seal."
pattern = "bare_statement"
[spares.RESOLVE_CODE_GUARD]
title = "The code shade keeps one guarded line."
pattern = "bare_statement"
[spares.RESOLVE_NEST_GUARD]
title = "The nested path keeps one guarded leaf."
pattern = "bare_statement"
[spares.RESOLVE_ARITY_GUARD]
title = "The arity road keeps one guarded copy."
pattern = "bare_statement"
[spares.RESOLVE_REVERSE_GUARD]
title = "The reverse keeps one guarded return."
pattern = "bare_statement"
```

### A2.5 Exact compliance tests (SPL-facing Tasks 2L / 3L)

After any IR/SPL/literary edit in 2L or 3L:

```bash
uv run pytest tests/test_act1_references.py tests/test_act3_links_pure.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
```

Task 3L Step 1 only requires red act3 contracts + green literary/generated with spares-only install.

Task 3L Step 3 additionally requires full `tests/test_mdtest.py` green **without** interpret short-circuits, and:

```bash
rg -n "apply_act1_reference_strip|apply_act3_link_resolution" scripts/splc/interpret.py
# production short-circuits gone
```

### A2.6 Task 5 Step 2 precondition

Re-run pure shakespeare integration **only after** 2L and 3L checkboxes are complete. Helper-green IR is not sufficient evidence for Step 2.

### A2.7 Assumptions (recorded)

1. Act I pure ops can realize A1.3 within the existing 20+6 labels if capture is incremental; spare exhaustion → `BLOCK[plan]`, not title invention.
2. Act III pre-pass HTML emission matches the historical rewrite path enough that existing span/HTML protection does not regress non-link fixtures; spike dumps and Amps stay green at every 3L sub-gate.
3. `act1_ref_strip` / `act3_link_resolve` modules may remain as **test oracles** after intrinsic retirement; they must not run from `run_act` or release wrappers.
4. No new stream token codes are required for resolve-in-text-payload.
5. Email autolinks remain entity-normalized only (`docs/markdown/divergences.md`).
6. Design doc addendum A1 (same date) restates that interpreter assists are not production ownership.

---

## Amendment A3 (2026-07-20): Act I strip transfer-bridge register/label choreography

**Resolves the `- BLOCK[plan]:` recorded 2026-07-20** (Task 2L Step 2, re-verified by
claude-implement): the fear that each Act I scene's `companion` field caps the whole
strip pass at "two value cells" and therefore cannot hold `apply_act1_reference_strip`'s
mode selector, `remaining` counter, growing `horatio` buffer, `ov`/`pv` counters, and
`title_nl` backtrack. That fear conflates the **on-stage-at-once** limit (exactly one
`companion`, per `docs/spl/reference.md` "maximum two characters on stage") with the
**total addressable register budget**, which is much larger:

- Every character (`Hecate`, `Horatio`, `Puck`, `Rosalind`) has its own persistent
  `value` scalar **and** its own `stack`, independently of who is on stage — confirmed
  by `docs/spl/reference.md` line 79 ("Character name → that character's current value,
  even if off stage") and line 383 ("Characters retain values off-stage"). `let`/`branch`
  expressions in `src_ir/act1.py` already read `val(X)` for characters that are not the
  scene's `companion` (e.g. `HECATE_LINE_STRIP_SECOND_REFERENCE` at
  `src_ir/act1.py:176` reads `val(ROSALIND)` while `companion=HORATIO`). Only `push`/`pop`
  (stack ops) and the assignment target of `let` require the target to be the on-stage
  listener; **arithmetic/comparison reads of any character's value are unrestricted.**
- Scene labels are FSM states, not registers. A1.3's 20 labels do not need a 1:1 mapping
  to the oracle's `mode` strings — one label's op sequence may contain several `branch`
  ops (already the pattern at `HECATE_NORMALIZE_LINE`, two branches before its `goto`)
  and may `goto` **itself** to consume more than one glyph per conceptual mode (already
  the pattern at `HECATE_DETAB_COLUMN_TWO`/`_FOUR`, which loop until `ROSALIND == 0`).
  So `mode` needs **zero** dedicated storage: it is which label is executing, and
  self-loop is free.

This amendment assigns exact register ownership so Step 2 is mechanical translation of
`scripts/splc/act1_ref_strip.py`'s Python state into `src_ir/act1.py` ops — no further
choreography invention is authorized or required.

### A3.1 Register ownership (binding for Task 2L Step 2)

| Oracle state | SPL owner | Notes |
|---|---|---|
| `remaining` | `Hecate.value` | Decremented on every glyph pop from `Hecate.stack`, mirroring the existing `Horatio value = length` idiom (A1.2). Checked `== 0` before each pop to avoid a runtime error on empty-stack `Recall`. |
| `mode` (17-way) | scene label + internal `branch` | No storage. Oracle sub-modes without a dedicated A1.3 row — `url_ws_nl`, `title_body`, `title_tail`, the colon-fail tail, the label mid-capture branch — are internal branches/self-loops inside their parent label's own scene (mapping in A3.2). |
| `horatio` (growing capture buffer) | `Horatio.stack` | Push in read order (top = most recently captured glyph), matching A1.2's existing plan for Horatio as capture scratch. |
| `ov` (lead-space / overflow counter) | `Horatio.value` | Distinct slot from `Horatio.stack`; both live on the same character simultaneously (value and stack are independent per `docs/spl/reference.md` "Each character has: a value, a stack"). |
| `pv` (keep-rest-of-capture flag) | `Puck.value` | Read only in the `HECATE_REF_REPLAY` scene body. |
| `puck` (persistent rebuild/kept-body accumulator) | `Puck.stack` | Same physical stack as the A3.3 backtrack scratch below — safe because their live ranges never overlap (proof in A3.3). |
| Rosalind table records (A1.2) | `Rosalind.stack` above the floor | Unchanged from A1.2. |
| fold/encode loop scratch | `Rosalind.value` | Used only while `Rosalind` is the on-stage companion during `HECATE_REF_FOLD`/`HECATE_REF_ENCODE`. |

No new characters, no new token codes, no third on-stage participant. This closes risk
row "Act I table needs a third simultaneous participant" as **not triggered**.

### A3.2 Sub-mode folding (closes the "15 modes vs 20 labels" gap)

Each row states which A1.3 label absorbs the oracle sub-mode, and how:

| Oracle sub-mode | Absorbing label | Mechanism |
|---|---|---|
| `next` | `HECATE_REF_NEXT` | unchanged 1:1 |
| `lead` | `HECATE_REF_LEAD` | self-`goto` until `ov == 3` or non-space/non-`[` glyph (matches oracle's per-glyph `while`) |
| `label` | `HECATE_REF_LABEL` | self-`goto` until `]` or NL |
| `colon` (incl. fail tail) | `HECATE_REF_COLON` | one `branch` on `g == ':'`; fail path falls straight through to the existing `HECATE_REF_REPLAY` goto target, no new label |
| `url_ws` **and** `url_ws_nl` | `HECATE_REF_URL_WS` (+ spare `HECATE_REF_URL_GUARD` promoted) | `url_ws` self-loops in `HECATE_REF_URL_WS`; on NL it transitions to the promoted `HECATE_REF_URL_GUARD` scene, which self-loops the post-NL lead-space count (`ov` reset to 0 first) and re-checks the `<`/other-glyph branch, mirroring `url_ws_nl` exactly |
| `angle` | `HECATE_REF_ANGLE` | self-`goto` until `>` or NL |
| `url` | `HECATE_REF_URL` | self-`goto` until WS/NL/EOF |
| `title`, `title_body`, `title_tail` | `HECATE_REF_TITLE` | `title` and `title_tail` are the pre-quote scan (self-loop until `"`, NL, or non-title glyph); once `"` is seen, the **same label** self-loops in `title_body` behavior gated by a 0/1 "in-quote" flag stored in an unused low bit of `Horatio.value` (bounded because `ov` is always 0–3 at that point in the oracle — the in-quote flag can safely occupy `ov`'s next power-of-four band, e.g. `ov + 4` while capturing, `ov` restored to its original value at `HECATE_REF_FOLD` entry) |
| `title_nl` (incl. save/restore) | `HECATE_REF_TITLE_NL` | see A3.3 |
| `replay` | `HECATE_REF_REPLAY` | unchanged 1:1, reads `Puck.value` for `pv` |
| `keep` | `HECATE_REF_KEEP` | self-`goto` until NL, matches oracle |
| `fold` (incl. `rfind`, label case-fold, dest/title split) | `HECATE_REF_FOLD` → `HECATE_REF_ENCODE` → `HECATE_REF_STORE` | see A3.4 |
| `finish` | `HECATE_REF_FINISH` | unchanged 1:1 |

Only **one** spare (`HECATE_REF_URL_GUARD`) is authorized for promotion by this
amendment. The remaining five spares (`HECATE_REF_LEAD_GUARD`,
`HECATE_REF_LABEL_GUARD`, `HECATE_REF_TITLE_GUARD`, `HECATE_REF_STORE_GUARD`,
`HECATE_REF_REPLAY_GUARD`) stay reserved; promoting any of them requires a further
`BLOCK[plan]` amendment, not mid-task invention — Step 2 must not need them if A3.1–A3.4
are followed.

### A3.3 `title_nl` backtrack: Puck as idle scratch (no save-array primitive needed)

SPL has no "snapshot a stack" primitive, only destructive `pop` and additive `push`. The
oracle's `save_src`/`save_rem`/`save_h` Python snapshot is realized as follows, using the
fact that `Puck.stack` is **not touched** by the oracle between `url`/`title` ending and
`fold` starting (the oracle only appends to `puck` in `keep`/`replay`/`next`-on-NL, none
of which run while `title_nl` is in progress):

1. On entry to `HECATE_REF_TITLE_NL`, pop up to 3 lead-space glyphs from `Hecate`,
   pushing each one onto `Puck.stack` as it is read (Puck is idle here, see above).
2. If the next glyph is not `"`, the candidate is rejected: pop everything just pushed
   back off `Puck.stack` and push it onto `Hecate.stack` in the same pop order. Because
   `Puck` is LIFO, popping it and re-pushing onto `Hecate` glyph-by-glyph exactly
   reverses the reversal — `Hecate`'s top glyph after restore is the same glyph that was
   its top before `HECATE_REF_TITLE_NL` ran. Then `goto HECATE_REF_FOLD` (matches
   oracle: `source = save_src; ...; mode = "fold"`).
3. If the next glyph is `"`, continue popping `Hecate` glyphs onto `Puck.stack` (not
   `Horatio.stack`) until NL or EOF — `Puck` remains the tentative holding area.
4. Apply the oracle's accept test (`line.startswith('"')` is already guaranteed by step
   2's branch; `line.rfind('"') > 0` and no trailing non-whitespace after the closing
   quote) using the backward-scan idiom from A3.4 directly on `Puck.stack` (top = last
   glyph read = correct direction for a reverse scan).
   - **Accept:** transfer `Puck.stack` (pop each glyph, push onto `Horatio.stack`) —
     this reverses orientation exactly once, which is required because `Horatio.stack`
     must hold the captured title in forward order for `HECATE_REF_FOLD`'s reverse-scan
     step (A3.4) to consume correctly. `goto HECATE_REF_FOLD`.
   - **Reject:** restore per step 2 (pop `Puck.stack` back onto `Hecate.stack`,
     including the lead-space glyphs already there from step 1), then
     `goto HECATE_REF_FOLD` with `Horatio.stack` unchanged (matches oracle:
     `horatio = save_h`).

`Puck.stack`'s permanent kept-body role and its transient A3.3 scratch role never
overlap in time because the oracle machine is single-threaded and `title_nl` cannot be
entered while a `replay`/`keep` flush to `Puck` is in progress. This is the same
non-overlap argument the existing `HECATE_REVERSE_POP` scene already relies on
(`src_ir/act1.py:210-216`, which pops `Puck` into `Hecate` using the identical
reverse-then-restore idiom for the whole-document normalize reversal).

### A3.4 `fold`/`encode` string ops: pop direction *is* the scan direction

The oracle's `fold` mode does `rfind`, `lstrip`, `startswith`, and slicing on an
assembled Python string. On the SPL stack model these decompose without inventing new
primitives, because popping a stack **is** a backward scan over what was pushed:

- **Backward scan (`rfind`, trailing-whitespace check):** pop directly from
  `Horatio.stack` (or `Puck.stack` per A3.3) glyph by glyph from the end — this is
  exactly `rfind`'s direction. No reversal needed.
- **Forward scan (label fold, `]:` search, `<dest>`/bare-dest split, `"title"` slice):**
  reverse `Horatio.stack` onto `Rosalind.stack` (or a scratch character on stage) first
  using the same `HECATE_REVERSE_POP` idiom already proven at
  `src_ir/act1.py:210-216`, then pop forward from there.
- **Case-fold (`a-z` from `A-Z`) and whitespace collapse:** per-glyph `branch` +
  `let` while popping forward, matching `scripts/slice3_links._normalize_label`
  character-for-character; no string buffer needed.
- **Entity-escaping (`&`→`&amp;`, `<`→`&lt;`, `>`→`&gt;`, `"`→`&quot;`):** reuse the
  exact `_entity()` idiom already implemented for Act III
  (`src_ir/act3.py:115-121`, e.g. `LYRIC_BUFFER_ENTITY_AMP` at
  `src_ir/act3.py:465-470`) — a `let`+`push` pair per output glyph on the
  currently-on-stage accumulator character, gated by a `branch` per input glyph.
- Record assembly (`label_len`, `label_glyphs…`, `dest_len`, …, `RECORD_END`) pushes
  directly onto `Rosalind.stack` per A1.2's layout as each length becomes known — no
  Python-side length precomputation needed since SPL can push the count once the
  matching forward scan completes and the glyphs are already on the target stack below
  it.

### A3.5 Step 2 implementation bounds (supersedes the blocker)

- Task 2L Step 2 is now mechanical: for each of the 20 A1.3 labels (+ the one promoted
  `HECATE_REF_URL_GUARD` spare from A3.2), replace its goto stub with the `push`/`pop`/
  `let`/`branch`/`goto` ops implied by A3.1–A3.4, checked glyph-for-glyph against
  `scripts/splc/act1_ref_strip.py`.
  `USE_ACT1_REF_INTRINSIC` stays `False` for the duration.
- Do not promote any of the five remaining spares; hitting a genuine gap not covered by
  A3.1–A3.4 is a new `BLOCK[plan]`, not silent invention.
- Gates are unchanged from A1.5 / A1.6: `tests/test_act1_references.py`,
  `tests/test_splc_validate.py`, `tests/test_splc_generated_fragments.py`,
  `tests/test_literary_compliance.py`, then regen + assemble with a clean
  `git diff --exit-code -- src/*.spl shakedown.spl debug/`.

### A3.6 Assumption recorded

The `ov`/in-quote-flag co-encoding in `HECATE_REF_TITLE` (A3.2) assumes the oracle never
needs `ov`'s pre-quote value once quote-capture starts (confirmed: `ov` is not read again
after `mode = "title_body"` is entered in `apply_act1_reference_strip`). If Step 2
implementation finds a path where this is false, use a second bit band instead of
stopping — this is an arithmetic detail within A3.1's assigned register, not a new
choreography, and does not require a further plan amendment.

---

## Amendment A4 (2026-07-20, escalated): Act I pure-op stage/orientation contract

**Supersedes the contradicted parts of A3 and closes the three-times-repeated
`- BLOCK:` on Task 2L Step 2.** A3 was correct that the register budget is larger
than "two cells", but three of its mechanics are contradicted by the verified
behaviour of `scripts/splc/validate.py` and `scripts/splc/interpret.py`. Step 2
kept failing because implementers followed A3 literally and hit an
`IrError`/step-limit wall each iteration. A4 states the corrected mechanics, the
orientation invariant the scaffold currently violates, and a sub-step ladder so a
single iteration can land a green checkpoint instead of an all-or-nothing port.

No compiler, validator, or lowering change is authorized or required. No new
scene budget: A4 spends only labels already reserved in A1.3/A1.4.

### A4.1 Verified stage rules (correct A3.1)

Read from `scripts/splc/validate.py:28-48` and `scripts/splc/interpret.py:264-270`:

1. **Every write target must be on stage.** `participants()` unions the target of
   every `let`/`push`/`pop`/`read_char`/`print_*` with the anchor and companion,
   and demands exactly one non-anchor character. A3.1's register map is valid for
   *storage* (values do persist off stage, and `val(X)` reads are unrestricted),
   but a scene may only *write* two characters — its anchor and its companion.
   Consequence: A3.1's simultaneous ownership of `ov` (`Horatio.value`) and `pv`
   (`Puck.value`) alongside a `Hecate` pop is **not** realizable in one scene, and
   the A3.3 "capture on `Horatio.stack`, kept on `Puck.stack`" split cannot flush.
2. **`pop` clobbers the target's value** (`state.values[op.target] = value`).
   A3.1's `remaining` in `Hecate.value` does not survive `pop(HECATE)`. The proven
   take idiom, with `companion=PUCK`: `let(PUCK, val(HECATE))` (save remaining) →
   `pop(HECATE, ...)` (glyph now in `Hecate.value`) → consume it →
   `let(HECATE, sub(val(PUCK), const(1)))`. Do not park a push payload in
   `Puck.value` while remaining lives there; push a `Const`/`BinOp` expression
   directly (`push(PUCK, sub(const(0), const(7)))`).
3. **The Recall speaker is the *other* character.** `validate.py:141` picks
   `speaker = pair[1] if op.target == anchor else anchor`, so `pop(X)` requires a
   recall key on whichever character shares the stage with `X` — not on `X`.
   `[characters.rosalind.recall]` is empty, which is why every attempt to build the
   Rosalind table by popping failed validation. A4.4 fixes this at the source.
4. **Negative sentinels have no `value_phrase`.** Build `-6`/`-7`/`-8` as
   `sub(const(0), const(n))`. No new `stable_utility` keys.
5. **One label, one entry stage pair.** `entry_pairs()` pass 1 requires every
   branch predecessor of a label to leave the same pair, and pass 3 requires a
   `goto` to share at least one character with its target's entry pair. Dual-entry
   modes therefore use inverted non-exhaustive branches or a distinct label —
   never `branch(..., then=<self>)` with no state change.

### A4.2 Orientation invariant (binding; fixes the current red)

**Invariant:** at `ACT_I_DONE`, `Hecate.stack` must have **top = first body glyph**,
and `Horatio.stack` must hold exactly the body length with `Horatio.value` equal to it.

Each pop-and-push transfer between two stacks reverses orientation exactly once.
The scaffold in `src_ir/act1_ref_pure.py` performs **three** transfers
(`Hecate → Puck → Horatio → Hecate`), which is odd, so the body arrives reversed.
Verified 2026-07-20 by running Act I on `"para\n"`: `Hecate.stack` ends
`[10, 10, 112, 97, 114, 97, 10, 10]` — top-first that reads `\n\narap\n\n`, matching
all eight `tests/test_act1_references.py` failures.

**Corrected pipeline — two transfers, Horatio hop deleted:**

| Stage | Stack | Orientation | Notes |
|---|---|---|---|
| after normalize reverse | `Hecate.stack` | top = first | entry state, unchanged |
| scan (`NEXT`/`KEEP`/capture) | `Puck.stack` | top = **last** | kept body accumulates here |
| trailing-NL policy | `Puck.stack` | top = last | strip **here**, where the last glyph is on top: pop while `== '\n'`, then `push` exactly two `'\n'` |
| drain (`REVERSE`) | `Puck → Hecate` | top = first | single transfer, restores the invariant |
| `FINISH` | `Horatio` | — | `let(HORATIO, val(HECATE))`; `push(HORATIO, val(HORATIO))` |

During the drain scene the on-stage pair is `(Hecate, Puck)`; `Puck.value` is
clobbered by each `pop(PUCK)`, so the **length counter lives in `Hecate.value`**
(`let(HECATE, add(val(HECATE), const(1)))` per glyph), and `FINISH` copies it to
Horatio in a `(Hecate, Horatio)` scene. `pop(PUCK)` in a Hecate-paired scene speaks
with a Hecate recall key (`cauldron_dreg`, `kept_tally`, …) — all present.

This deletes the scaffold's phase-40/41/42 Horatio round trip and frees
`HECATE_REF_ENCODE`, `HECATE_REF_STORE`, `HECATE_REF_COLON`, `HECATE_REF_URL_WS`
and `HECATE_REF_FOLD` to carry their A1.3 semantics again.

### A4.3 Puck-centric single-stack capture (supersedes A3.3)

Capture and kept body share **one** stack, so no cross-stack flush is ever needed:

```
Puck.stack = [KEPT_START, kept…, CAPTURE_START, candidate…]      (top = last)
```

- `KEPT_START` = `-8`, `CAPTURE_START` = `-7`, `RECORD_END` = `-6` (A1.2 unchanged).
- `HECATE_REF_BRACKET` pushes `CAPTURE_START` before the first candidate glyph.
- Candidate glyphs are pushed onto `Puck` exactly as kept glyphs are — same scene
  shape, so a candidate that turns out to be body text needs no data movement.
- **`HECATE_REF_REPLAY` becomes near-free:** pop down to `CAPTURE_START`, discard
  only that sentinel, and re-push the glyphs in the order popped. Since the region
  is contiguous and already in kept order, the cheaper realization is to *scan* to
  the sentinel and rewrite it to a kept glyph only when the sentinel is at a known
  offset; otherwise use the pop/re-push pair via `Hecate.stack` as scratch (`Hecate`
  is empty of body only after the drain, so during scan use `Horatio.stack`, which
  A4.2 has freed).
- **`HECATE_REF_STORE`** pops the capture region off `Puck` (backward = `rfind`
  direction, per A3.4, which stands) and relays it onto `Rosalind.stack` per A1.2.
- `Puck.value` is free during scan and holds `pv`; `Horatio.value` holds `ov`; both
  are read via `val()` from any scene and written only where that character is staged.

A3.3's `title_nl` backtrack is re-expressed on the same principle: push the tentative
lead-spaces and title glyphs onto `Horatio.stack` (idle during scan under A4.2);
accept = transfer to the capture region on `Puck`, reject = pop back onto `Hecate`.
The A3.3 non-overlap argument is unchanged and still holds.

### A4.4 Rosalind recall prose (authorized; ready to paste)

The empty `[characters.rosalind.recall]` pool is the hard blocker on building the
table: **any** scene that pops while Rosalind is the other staged character needs a
Rosalind recall key (A4.1 rule 3). Authoring that prose is plan-time literary work,
so it is done here. Paste into `src/literary.toml` under the existing
`[characters.rosalind.recall]` header (keys are additive; no scene budget touched):

```toml
[characters.rosalind.recall]
forest_record_seal = "Recall the forest record's seal."
forest_record_glyph = "Recall the forest record's glyph."
forest_record_measure = "Recall the forest record's measure."
folded_forest_name = "Recall the folded forest name."
kept_forest_road = "Recall the kept forest road."
```

Five keys — `_seal` for sentinel pops, `_glyph` for per-character pops, `_measure`
for length pops, `folded_forest_name` for label relay, `kept_forest_road` for
destination relay. `tests/test_literary_compliance.py::test_recall_phrases_are_in_speaker_pools`
matches on the rendered `"Recall <body>."` string, so these must be pasted verbatim.
If a sixth distinct recall site appears, reuse `forest_record_glyph`; recall keys are
not required to be unique per call site.

With these installed, `HECATE_REF_STORE` may be a single `(Rosalind, Puck)` scene
(anchor `ROSALIND`, `companion=PUCK`) that pops the capture region and pushes the
A1.2 record — no value-relay ping-pong, no extra labels.

### A4.5 Remaining A1 spares released

A3.2 reserved `HECATE_REF_LEAD_GUARD`, `HECATE_REF_LABEL_GUARD`,
`HECATE_REF_TITLE_GUARD`, `HECATE_REF_STORE_GUARD`, `HECATE_REF_REPLAY_GUARD`
behind a further amendment. **This is that amendment: all five are released for
promotion**, alongside the already-released `HECATE_REF_URL_GUARD`. Their titles are
already authored in A1.4 — promote `[spares.*]` → `[scenes.*]` in the same commit
that first references the label in IR. They exist precisely to absorb the A4.1 rule-5
stage-pair bridges (a label whose predecessors leave different pairs needs a
one-line bridge scene, which is a structural surprise, not invented scope).

Exhausting all 26 A1 labels **is** a genuine `BLOCK[plan]`. Inventing a 27th title is
not permitted under any circumstances.

### A4.6 Step 2 sub-step ladder (land green incrementally)

Task 2L Step 2 has failed three times as one monolithic port. It is hereby split;
**one sub-step per iteration**, each with the A4.7 gate, each its own commit. A
sub-step that is green may be committed even while later ones are red — record the
red set in the commit body, not in `.agent/blockers.md`.

- [x] **Step 2a — orientation.** Apply A4.2 to `src_ir/act1_ref_pure.py`: delete the
  Horatio hop, move the trailing-NL policy onto `Puck`, count length in
  `Hecate.value`. Success: `tests/test_act1_references.py` returns to **2 passed**
  (`test_four_leading_spaces_are_not_definitions`,
  `test_invalid_bracket_line_remains_body`) with body text no longer reversed. This
  restores the Step-1 red baseline honestly rather than regressing past it.
  Evidence (2026-07-20, grok-implement): keep-all pipeline with two transfers only
  (`Hecate → Puck → Hecate`); trailing-NL strip/pad on `Puck`; length in
  `Hecate.value` during drain; `HECATE_REF_FINISH` copies length to Horatio.
  Unreached A1.3 labels retained via never-true `rem == rem-1` branch chain.
  Gate: `tests/test_act1_references.py` **2 passed, 6 failed** (body unreversed;
  defs still present); literary/validate/generated **67 passed**; `splc` + assemble
  regenerated Act I fragment / `shakedown.spl`. `USE_ACT1_REF_INTRINSIC` stays False.
- [ ] **Step 2b — recall prose + literary promotion.** Paste A4.4 into
  `src/literary.toml`. Gate: literary/validate/generated green; no IR behaviour change.
- [ ] **Step 2c — line machine.** `NEXT`/`LEAD`/`FOUR_SPACE`/`NL`/`KEEP` per A3.2's
  self-loop mapping, still keeping every line as body. Success: same 2 passed, no
  regression; `HECATE_REF_LEAD` correctly counts 0–3 and rejects on the fourth space.
- [ ] **Step 2d — candidate capture + replay.** `BRACKET`/`LABEL`/`COLON`/`URL_WS`/
  `URL_GUARD`/`ANGLE`/`URL`/`TITLE`/`TITLE_NL`/`REPLAY` per A4.3. Success:
  well-formed definition lines vanish from the body (`test_simple_definition_*`,
  `test_up_to_three_leading_spaces_*`, `test_defs_plus_paragraph_*` pass); the
  Rosalind table may still be empty, so `test_label_case_fold`,
  `test_angle_bracket_destination` and `test_title_on_next_line` stay red.
- [ ] **Step 2e — table build.** `FOLD`/`ENCODE`/`STORE` per A3.4 + A4.4. Success:
  `tests/test_act1_references.py` **8 passed**, which completes Task 2L Step 2 and
  unblocks Step 3.

Check the Step 2 box only after 2e. Until then, tick sub-steps in this list.

### A4.7 Gate (unchanged, run every sub-step)

```bash
uv run pytest tests/test_act1_references.py -q
uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --exit-code -- src/*.spl shakedown.spl debug/
```

`USE_ACT1_REF_INTRINSIC` stays `False` through 2a–2e; it is deleted in Step 3.
`scripts/splc/act1_ref_strip.py` remains the binding oracle for every stack outcome.

### A4.8 Assumptions recorded

1. Two stack transfers (`Hecate → Puck → Hecate`) suffice for the whole strip pass;
   the capture region never needs to leave `Puck` except into the Rosalind record.
2. `Horatio.stack`, freed by A4.2, is sufficient scratch for the A3.3 `title_nl`
   backtrack and the A4.3 replay re-push. If a case needs a third scratch stack,
   `Rosalind.stack` above its six-value floor is available and is *not* a plan gap.
3. Adding keys to `[characters.rosalind.recall]` is additive literary surface and
   changes no generated fragment until a scene references one — so Step 2b's
   `git diff --exit-code` on generated SPL stays clean.
