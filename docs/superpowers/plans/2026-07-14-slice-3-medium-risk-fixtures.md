# Slice 3 Medium-Risk Fixtures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the ten roadmap-row-6 fixtures with Markdown.pl-compatible bytes while preserving shipped fixtures and spike contracts.

**Architecture:** Follow [the accepted design](../specs/2026-07-14-slice-3-medium-risk-design.md), architecture §7.6/§7.8a/§8.1, and the existing four-act IR pipeline. Act I owns the reference table; Act II block shape; Act III protected spans and lookup; Act IV byte emission. Reuse `RAW_HTML_HASH = 10` for raw simple-HTML leaves.

**Tech Stack:** Python 3.13, typed splc IR, generated Shakespeare SPL, TOML-controlled literary surfaces, pytest, local Markdown.pl v1.0.1.

## Global Constraints

- This is the sole in-flight plan. Slice 2 is halted: Task 1 proves only the declared shipped baseline and must not mark Slice 2 shipped.
- Before SPL edits read `docs/superpowers/notes/spl-literary-protocol.md`,
  `docs/superpowers/notes/correctness-first-spl-workflow.md`,
  `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`,
  `docs/spl/codegen-style-guide.md`, `src/literary.toml`,
  `docs/markdown/reference-mechanics.md`,
  `docs/markdown/html-block-boundaries.md`, and
  `docs/markdown/list-mechanics.md`.
- Edit generated acts only via `src_ir/*.py`; run `uv run python -m scripts.splc` and `uv run python scripts/assemble.py`. Never hand-edit generated SPL or `shakedown.spl`.
- Enable a fixture in `tests/test_mdtest.py` only in its green task; never change fixture expected files or invoke Markdown.pl at runtime.
- After each SPL/TOML checkpoint run: `uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q`.
- The same checkpoint must include `uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q` before broader fixture regression, preserving the first full-pipeline proof.
- Every checkpoint commits only its task files with the required provenance trailers and pushes. Failed push or exhausted reserve: append one `- BLOCK:` / `- BLOCK[plan]:` line and stop.

## File map

| Path | Responsibility |
|---|---|
| `src_ir/act1.py`, `src/10-act1-literary.toml` | Reference-definition collection and document table. |
| `src_ir/act2.py`, `src/20-act2-literary.toml` | Hard-wrap ambiguity and quote/code stream formation. |
| `src_ir/act3.py`, `src/30-act3-literary.toml` | Reference/image lookup, protected HTML, title quoting, strong/em. |
| `src_ir/act4.py`, `src/40-act4-literary.toml` | Raw HTML and quote-code leaf emission. |
| `tests/test_act{1,2,3,4}_slice3.py`, `tests/test_slice3_medium_risk.py` | Fast-IR, scene/pair, stack, and fixture contracts. |
| `tests/test_mdtest.py` | Per-fixture enablement only after strict parity. |

## Literary reservation

Reuse existing `LYRIC_HTML_*`, `LYRIC_LINK_*`, `LYRIC_IMAGE_*`,
`LYRIC_EMPHASIS_*`, and `LYRIC_DEFINITION_*` only in their existing
scanner roles. New Incidental TOML-owned surfaces are:

| Act | Working labels | Spare labels |
|---|---|---|
| I | `PREP_REF_OPEN`, `PREP_REF_LABEL`, `PREP_REF_PATH`, `PREP_REF_TITLE`, `PREP_REF_STORE`, `PREP_REF_REPLAY` | `PREP_REF_BLANK`, `PREP_REF_ANGLE`, `PREP_REF_FALLBACK`, `PREP_REF_FINISH` |
| II | `PASS_WRAP_DOT`, `PASS_WRAP_REPLAY`, `PASS_QUOTE_CODE`, `PASS_QUOTE_CLOSE` | `PASS_WRAP_GUARD`, `PASS_QUOTE_REPLAY`, `PASS_QUOTE_GUARD`, `PASS_QUOTE_FINISH` |
| IV | `SCRIBE_RAW_HTML`, `SCRIBE_RAW_HTML_CLOSE`, `SCRIBE_QUOTE_CODE`, `SCRIBE_QUOTE_CODE_CLOSE` | `SCRIBE_RAW_HTML_GUARD`, `SCRIBE_QUOTE_CODE_GUARD`, `SCRIBE_RAW_HTML_FINISH`, `SCRIBE_QUOTE_CODE_FINISH` |

Append these ready-to-paste entries before using labels:

```toml
[scenes.PREP_REF_OPEN]
title = "Horatio opens the kingdom's quiet ledger."
pattern = "scene_of_character"
[scenes.PREP_REF_LABEL]
title = "Hecate gathers the ledger's folded name."
pattern = "scene_of_character"
[scenes.PREP_REF_PATH]
title = "Horatio keeps the ledger's river road."
pattern = "scene_of_character"
[scenes.PREP_REF_TITLE]
title = "Hecate seals the ledger's whispered title."
pattern = "scene_of_character"
[scenes.PREP_REF_STORE]
title = "The kingdom stores the settled road."
pattern = "bare_statement"
[scenes.PREP_REF_REPLAY]
title = "Horatio restores the unproved ledger line."
pattern = "scene_of_character"
[scenes.PREP_REF_BLANK]
title = "The ledger keeps one silent interval."
pattern = "bare_statement"
[scenes.PREP_REF_ANGLE]
title = "Hecate uncovers the ledger's bright road."
pattern = "scene_of_character"
[scenes.PREP_REF_FALLBACK]
title = "The loose ledger leaf returns unchanged."
pattern = "bare_statement"
[scenes.PREP_REF_FINISH]
title = "Horatio closes the kingdom's ledger."
pattern = "scene_of_character"
[scenes.PASS_WRAP_DOT]
title = "Macbeth weighs the wandering numbered stroke."
pattern = "scene_of_character"
[scenes.PASS_WRAP_REPLAY]
title = "Lady Macbeth returns the unclaimed number."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_CODE]
title = "Macbeth bears the indented echo within the hall."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_CLOSE]
title = "The echoing hall releases its chamber line."
pattern = "bare_statement"
[scenes.PASS_WRAP_GUARD]
title = "The numbered stroke keeps its plain path."
pattern = "bare_statement"
[scenes.PASS_QUOTE_REPLAY]
title = "Lady Macbeth restores the echoing mark."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_GUARD]
title = "The hall keeps one measured threshold."
pattern = "bare_statement"
[scenes.PASS_QUOTE_FINISH]
title = "Macbeth frees the finished echo."
pattern = "scene_of_character"
[scenes.SCRIBE_RAW_HTML]
title = "Prospero releases the unbroken courtly mark."
pattern = "scene_of_character"
[scenes.SCRIBE_RAW_HTML_CLOSE]
title = "The courtly mark returns without a veil."
pattern = "bare_statement"
[scenes.SCRIBE_QUOTE_CODE]
title = "Prospero opens the echoing chamber."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_CODE_CLOSE]
title = "The echoing chamber closes in peace."
pattern = "bare_statement"
[scenes.SCRIBE_RAW_HTML_GUARD]
title = "The courtly mark keeps its clear edge."
pattern = "bare_statement"
[scenes.SCRIBE_QUOTE_CODE_GUARD]
title = "The chamber keeps its echoing measure."
pattern = "bare_statement"
[scenes.SCRIBE_RAW_HTML_FINISH]
title = "Prospero frees the finished courtly line."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_CODE_FINISH]
title = "The echo returns to the outer hall."
pattern = "bare_statement"
```

---

### Task 1: Establish Slice-3 seams and the predecessor baseline

**Files:** Create `tests/test_slice3_medium_risk.py`, `tests/test_act1_slice3.py`, `tests/test_act2_slice3.py`, `tests/test_act3_slice3.py`, `tests/test_act4_slice3.py`; modify `tests/test_mdtest.py`.

**Interfaces:** Add `_run_acts(input_text: str, through_act: int) -> str | list[int]` helpers around the fast interpreter. `_IMPLEMENTED_FIXTURES` remains the sole enablement set.

- [ ] **Step 1: Add disabled capability contracts.** Parametrize the ten row-6 fixture files; assert they are not enabled. Add strict-xfail contracts for hard-wrap ambiguity; inline/reference/collapsed/missing links; inline/reference images and title quotes; strong/em; inline tag/comment; raw block HTML; and quote code.

  Run: `uv run pytest tests/test_slice3_medium_risk.py -q`

  Expected: XFAIL only.

- [ ] **Step 2: Prove the existing baseline.**

  ```bash
  uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Horizontal rules' 'Code Blocks' Tabs
  ```

  Expected: four byte-identical strict cases. On failure, record it and stop; do not change Markdown behavior.

### Task 2: Preserve hard-wrapped list-like paragraph lines

**Files:** Modify `src_ir/act2.py`, `src/20-act2-literary.toml`, `tests/test_act2_slice3.py`, `tests/test_mdtest.py`, `tests/test_slice3_medium_risk.py`; regenerate Act II and release SPL.

**Interfaces:** A top-level digit-dot candidate without the required blank boundary replays exactly into one `PARA`; a true list keeps the existing stream.

- [ ] **Step 1: Write red tests** for `Paragraph\n8. Oops\n` (one paragraph) and `\n\n8. List\n` (list), then exact IR/binary fixture bytes.

  Run: `uv run pytest tests/test_act2_slice3.py tests/test_mdtest.py -k 'Hard-wrapped paragraphs' -q`

  Expected: FAIL.

- [ ] **Step 2: Implement bounded replay** using `PASS_WRAP_DOT` to retain digit/dot/lookahead until the physical-line boundary is known and `PASS_WRAP_REPLAY` only for a lowering adapter. Preserve all bytes and leave four spares unreachable.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act2_slice3.py tests/test_mdtest.py -k 'Hard-wrapped paragraphs' -q && uv run python scripts/strict_parity_harness.py 'Hard-wrapped paragraphs with list-like lines'`

  Expected: PASS and `summary: 1/1 byte-identical`.

- [ ] **Step 3: Checkpoint** with the global SPL gate, all enabled mdtest/spikes, enable only this fixture, commit `feat: preserve hard-wrapped paragraphs`, and push.

### Task 3: Collect references and resolve links/images

**Files:** Modify Act I/III/IV IR and their TOML, `tests/test_act1_slice3.py`, `tests/test_act3_slice3.py`, `tests/test_act4_slice3.py`, `tests/test_mdtest.py`, and `tests/test_slice3_medium_risk.py`; regenerate all affected fragments.

**Interfaces:** Act I stores lower-case `(label, destination, title-present, title)` records and strips only valid definitions. Act III copies/restores records during lookup, resolves images before anchors, and replays unresolved source. Act IV receives final emitted bytes only.

- [ ] **Step 1: Write red tests** for 3-space/case-folded/angle-wrapped definitions, optional wrapped title, full/collapsed/spaced/missing refs, inline and reference images, two uses of one record, and `&quot;` title escaping.

  Run: `uv run pytest tests/test_act1_slice3.py tests/test_act3_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Links or Images or Literal quotes' -q`

  Expected: FAIL; temporary definition discard cannot pass positive lookup.

- [ ] **Step 2: Implement table collection and lookup.** Replace temporary discard with `PREP_REF_*`; malformed candidates use `PREP_REF_REPLAY`. In Act III copy each record to scratch and restore it before continuing; emit image before anchor and replay a miss. Use reserved labels only.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act1_slice3.py tests/test_act3_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Links or Images or Literal quotes' -q && uv run python scripts/strict_parity_harness.py 'Links, inline style' 'Links, reference style' 'Links, shortcut references' Images 'Literal quotes in titles'`

  Expected: five strict byte-identical cases.

- [ ] **Step 3: Checkpoint** with global SPL gate and enabled mdtest/spikes; enable these five fixtures; commit `feat: resolve reference links and images`; push.

### Task 4: Complete strong/em nesting

**Files:** Modify `src_ir/act3.py`, `tests/test_act3_slice3.py`, `tests/test_mdtest.py`, `tests/test_slice3_medium_risk.py`; regenerate Act III/release SPL.

- [ ] **Step 1: Write red tests** for `***both***`, `**outer *inner* outer**`, escaped/unmatched delimiters, and delimiters inside code/link fields.

  Run: `uv run pytest tests/test_act3_slice3.py tests/test_mdtest.py -k 'Strong and em' -q`

  Expected: FAIL.

- [ ] **Step 2: Correct only existing `RESUME_EMPH`, `RESUME_STRONG`, and `RESUME_TRIPLE_EMPH` requeue order.** Protected field contents remain opaque and every held glyph is restored before `LYRIC_POP_GLYPH`; an unrepresentable transition is `BLOCK[plan]`.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act3_slice3.py tests/test_mdtest.py -k 'Strong and em' -q && uv run python scripts/strict_parity_harness.py 'Strong and em together'`

  Expected: PASS and strict byte identity.

- [ ] **Step 3: Checkpoint** with global gate plus enabled mdtest/spikes; enable fixture; commit `feat: render nested strong emphasis`; push.

### Task 5: Protect Simple HTML/comments and emit raw leaves

**Files:** Modify Act II/III/IV IR and TOML, Act-II/III/IV Slice-3 tests, `tests/test_mdtest.py`, and `tests/test_slice3_medium_risk.py`; regenerate affected fragments. Change `src_ir/tokens.py`, token docs/tests only if existing code-10 text-leaf arity proves inadequate.

**Interfaces:** Inline tags/comments are protected paragraph glyphs; left-margin simple blocks and standalone comments are `RAW_HTML_HASH` text leaves, emitted unwrapped.

- [ ] **Step 1: Write red tests** for `<span>`, `<br />`, inline and standalone comments, and fixture simple `div`/raw-`hr` cases; assert Advanced stays skipped.

  Run: `uv run pytest tests/test_act2_slice3.py tests/test_act3_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Inline HTML' -q`

  Expected: Simple/comment failures; Advanced skip.

- [ ] **Step 2: Implement bounded matching.** Respect documented left-margin/blank-line boundaries; protect inline regions to `>` or `-->`; emit code-10 leaves for raw blocks; Act IV writes their bytes with block separators. Do not match nested or attributed blocks.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act2_slice3.py tests/test_act3_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Inline HTML (Simple) or Inline HTML comments' -q && uv run python scripts/strict_parity_harness.py 'Inline HTML (Simple)' 'Inline HTML comments'`

  Expected: two strict byte-identical cases.

- [ ] **Step 3: Checkpoint** with global gate, token-code test if changed, enabled mdtest/spikes; enable two fixtures; commit `feat: preserve simple html regions`; push.

### Task 6: Compose blockquotes with code leaves and close Slice 3

**Files:** Modify Act II/IV IR and TOML, Act-II/IV Slice-3 tests, `tests/test_mdtest.py`, `tests/test_slice3_medium_risk.py`, and roadmap at final closure; regenerate affected fragments.

**Interfaces:** Stream exactly `BLOCKQUOTE_OPEN, CODE_BLOCK(text), BLOCKQUOTE_CLOSE`; Act IV emits quote/code separators matching the oracle.

- [ ] **Step 1: Write red stream/bytes tests** for the fixture, final code newline and indentation repair, plus unchanged standalone code behavior.

  Run: `uv run pytest tests/test_act2_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Blockquotes with code blocks' -q`

  Expected: FAIL.

- [ ] **Step 2: Implement only quote-code handoff/frame return** using `PASS_QUOTE_CODE`, `PASS_QUOTE_CLOSE`, `SCRIBE_QUOTE_CODE`, and `SCRIBE_QUOTE_CODE_CLOSE`; do not expand nested blockquotes or full lists.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act2_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Blockquotes with code blocks' -q && uv run python scripts/strict_parity_harness.py 'Blockquotes with code blocks'`

  Expected: documented normalized fixture test and fresh-oracle strict parity pass.

- [ ] **Step 3: Run final gate and close.**

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  uv run python scripts/strict_parity_harness.py 'Hard-wrapped paragraphs with list-like lines' 'Links, inline style' 'Links, reference style' 'Links, shortcut references' Images 'Literal quotes in titles' 'Strong and em together' 'Inline HTML (Simple)' 'Inline HTML comments' 'Blockquotes with code blocks'
  uv run pytest -q
  uv run ruff check .
  uv run ruff format --check .
  uv run pyright
  ```

  Expected: green and `summary: 10/10 byte-identical`. Enable final fixture, mark row 6 shipped, commit `feat: complete slice three fixtures`, and push.

## Plan self-review

All ten row-6 fixtures map to Tasks 2–6. Each task supplies red tests, implementation boundary, exact commands, strict oracle proof, generated/literary gate, regression, fixture enablement, and checkpoint. The plan neither declares Slice 2 shipped nor authorizes Slice-4 behavior.
