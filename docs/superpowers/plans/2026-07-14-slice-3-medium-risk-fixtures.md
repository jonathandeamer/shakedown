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
| II | `PASS_WRAP_DOT`, `PASS_WRAP_REPLAY`, `PASS_QUOTE_CODE`, `PASS_QUOTE_CLOSE`, `PASS_QUOTE_PREFIX`, `PASS_QUOTE_CONTINUE_PREFIX` | `PASS_WRAP_GUARD`, `PASS_QUOTE_REPLAY`, `PASS_QUOTE_GUARD`, `PASS_QUOTE_FINISH`, `PASS_QUOTE_PREFIX_REPLAY`, `PASS_QUOTE_PREFIX_FINISH` |
| IV | `SCRIBE_RAW_HTML`, `SCRIBE_RAW_HTML_CLOSE`, `SCRIBE_QUOTE_CODE`, `SCRIBE_QUOTE_CODE_CLOSE`, `SCRIBE_QUOTE_CODE_PROBE`, `SCRIBE_QUOTE_CODE_REPLAY` | `SCRIBE_RAW_HTML_GUARD`, `SCRIBE_QUOTE_CODE_GUARD`, `SCRIBE_RAW_HTML_FINISH`, `SCRIBE_QUOTE_CODE_FINISH`, `SCRIBE_QUOTE_CODE_PROBE_GUARD`, `SCRIBE_QUOTE_CODE_REPLAY_FINISH` |

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
[scenes.PASS_QUOTE_PREFIX]
title = "Lady Macbeth keeps the echo's first small space."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_CONTINUE_PREFIX]
title = "Lady Macbeth measures the echo's returning threshold."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_PREFIX_REPLAY]
title = "The echo restores each unspent pale step."
pattern = "bare_statement"
[scenes.PASS_QUOTE_PREFIX_FINISH]
title = "Macbeth releases the echo's guarded margin."
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
[scenes.SCRIBE_QUOTE_CODE_PROBE]
title = "Puck counts the chamber's pale threshold."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_CODE_REPLAY]
title = "Puck returns the threshold in faithful order."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTE_CODE_PROBE_GUARD]
title = "The pale threshold keeps one certain count."
pattern = "bare_statement"
[scenes.SCRIBE_QUOTE_CODE_REPLAY_FINISH]
title = "Prospero closes the restored threshold."
pattern = "scene_of_character"
```

---

### Task 1: Establish Slice-3 seams and the predecessor baseline

**Files:** Create `tests/test_slice3_medium_risk.py`, `tests/test_act1_slice3.py`, `tests/test_act2_slice3.py`, `tests/test_act3_slice3.py`, `tests/test_act4_slice3.py`; modify `tests/test_mdtest.py`.

**Interfaces:** Add `_run_acts(input_text: str, through_act: int) -> str | list[int]` helpers around the fast interpreter. `_IMPLEMENTED_FIXTURES` remains the sole enablement set.

- [x] **Step 1: Add disabled capability contracts.** Parametrize the ten row-6 fixture files; assert they are not enabled. Add strict-xfail contracts for hard-wrap ambiguity; inline/reference/collapsed/missing links; inline/reference images and title quotes; strong/em; inline tag/comment; raw block HTML; and quote code.

  Run: `uv run pytest tests/test_slice3_medium_risk.py -q`

  Expected: XFAIL only.

- [x] **Step 2: Prove the existing baseline.**

  ```bash
  uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Horizontal rules' 'Code Blocks' Tabs
  ```

  Expected: four byte-identical strict cases. On failure, record it and stop; do not change Markdown behavior.

### Task 2: Promote the proved hard-wrapped list-like paragraph baseline

**Files:** Modify `tests/test_act2_slice3.py`, `tests/test_mdtest.py`, and `tests/test_slice3_medium_risk.py`. No production, TOML, generated-fragment, or release-SPL file changes are authorized for this proved-baseline task.

**Interfaces:** A top-level digit-dot candidate without the required blank boundary already replays exactly into one `PARA`; a true list already keeps the existing stream. This task records and enables that behavior without a production parser change.

- [x] **Step 1: Promote the existing exact behavior to green contracts.** In `tests/test_act2_slice3.py`, add fast-Act-IV assertions for `Paragraph\n8. Oops\n` producing `<p>Paragraph\n8. Oops</p>\n` and `\n\n8. List\n` producing `<ol>\n<li>List</li>\n</ol>\n`. In `tests/test_slice3_medium_risk.py`, remove only the strict-xfail marker from `test_hard_wrap_ambiguity_contract`; retain its full-fixture byte comparison. Add `Hard-wrapped paragraphs with list-like lines` to `_IMPLEMENTED_FIXTURES` in `tests/test_mdtest.py`. Do not edit `src_ir/act2.py`, TOML, generated fragments, or `shakedown.spl`: the evidence already proves their behavior.

  Run:

  ```bash
  uv run pytest tests/test_act2_slice3.py tests/test_slice3_medium_risk.py -k hard_wrap -q
  uv run pytest 'tests/test_mdtest.py::test_mdtest[Hard-wrapped paragraphs with list-like lines]' -q
  uv run python scripts/strict_parity_harness.py 'Hard-wrapped paragraphs with list-like lines'
  ```

  Expected: all selected tests PASS and `summary: 1/1 byte-identical`. The direct mdtest node is deliberately quoted; do not use `-k 'Hard-wrapped paragraphs'`, which pytest cannot parse.

- [x] **Step 2: Checkpoint the promotion without a production regeneration.** Run the global SPL gate and the enabled-fixture/spike regression; the green contract from Step 1 is the focused proof. Commit only `tests/test_act2_slice3.py`, `tests/test_slice3_medium_risk.py`, and `tests/test_mdtest.py` with `test: enable hard-wrapped paragraph fixture`, then push. If any command exposes a real Act-II divergence, append `- BLOCK[plan]:` and stop rather than applying the retired bounded-replay design.

  Run:

  ```bash
  uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
  uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  ```

  Expected: PASS. No generated artifact changes are expected or staged.

### Task 3: Collect references and resolve links/images

**Files:** Modify Act I/III/IV IR and their TOML, `tests/test_act1_slice3.py`, `tests/test_act3_slice3.py`, `tests/test_act4_slice3.py`, `tests/test_mdtest.py`, and `tests/test_slice3_medium_risk.py`; regenerate all affected fragments.

**Interfaces:** Act I stores lower-case `(label, destination, title-present, title)` records and strips only valid definitions. Act III copies/restores records during lookup, resolves images before anchors, and replays unresolved source. Act IV receives final emitted bytes only.

- [x] **Step 1: Write red tests** for 3-space/case-folded/angle-wrapped definitions, optional wrapped title, full/collapsed/spaced/missing refs, inline and reference images, two uses of one record, and `&quot;` title escaping.

  Run: `uv run pytest tests/test_act1_slice3.py tests/test_act3_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Links or Images or Literal quotes' -q`

  Expected: FAIL; temporary definition discard cannot pass positive lookup.

- [x] **Step 2: Implement table collection and lookup.** Replace temporary discard with `PREP_REF_*`; malformed candidates use `PREP_REF_REPLAY`. In Act III copy each record to scratch and restore it before continuing; emit image before anchor and replay a miss. Use reserved labels only.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act1_slice3.py tests/test_act3_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Links or Images or Literal quotes' -q && uv run python scripts/strict_parity_harness.py 'Links, inline style' 'Links, reference style' 'Links, shortcut references' Images 'Literal quotes in titles'`

  Expected: five strict byte-identical cases.

- [x] **Step 3: Checkpoint** with global SPL gate and enabled mdtest/spikes; enable these five fixtures; commit `feat: resolve reference links and images`; push.

### Task 4: Complete strong/em nesting

**Files:** Modify `src_ir/act2.py`, `src_ir/act3.py`, `tests/test_act2_slice3.py`, `tests/test_act3_slice3.py`, `tests/test_mdtest.py`, `tests/test_slice3_medium_risk.py`; regenerate Acts II/III and release SPL.

- [x] **Step 1: Write red tests** for `***both***`, `**outer *inner* outer**`, escaped/unmatched delimiters, and delimiters inside code/link fields.

  Run: `uv run pytest tests/test_act3_slice3.py tests/test_mdtest.py -k 'Strong and em' -q`

  Expected: FAIL.

- [x] **Step 2: Repair the bounded Act-II HR-replay prerequisite, then correct the existing Act-III emphasis requeue order.** Before touching `RESUME_*`, add fast-Act-II stream/state contracts proving that failed `***` and `___` HR candidates restore Macbeth to no-open-list state, preserve the following plain paragraph as a `PARA`, and do not consume an `ITEM_START`; retain the shipped `* item` and `- item` rejected-HR list-handoff contracts. In `PASS_HR_FALLBACK`, only `PASS_HR_SPACE`'s single-marker plus space/tab route may enter `PASS_HR_FALLBACK_LIST_HANDOFF`; every failed no-space marker run replays raw glyphs after Macbeth's scratch count is reset. Do not add a token, scene, TOML surface, or parser. Then correct only existing `RESUME_EMPH`, `RESUME_STRONG`, and `RESUME_TRIPLE_EMPH` requeue order. Protected field contents remain opaque and every held glyph is restored before `LYRIC_POP_GLYPH`; an unrepresentable transition is `BLOCK[plan]`.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act2_slice3.py tests/test_act3_slice3.py tests/test_mdtest.py -k 'Strong and em' -q && uv run python scripts/strict_parity_harness.py 'Strong and em together' && uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py -q`

  Expected: PASS and strict byte identity.

- [x] **Step 3: Checkpoint** with global gate plus enabled mdtest/spikes; enable fixture; commit `feat: render nested strong emphasis`; push.

### Task 5: Protect Simple HTML/comments and emit raw leaves

**Files:** Modify Act II/III/IV IR and TOML, Act-II/III/IV Slice-3 tests, `tests/test_mdtest.py`, and `tests/test_slice3_medium_risk.py`; regenerate affected fragments. Change `src_ir/tokens.py`, token docs/tests only if existing code-10 text-leaf arity proves inadequate.

**Interfaces:** Inline tags/comments are protected paragraph glyphs; left-margin simple blocks and standalone comments are `RAW_HTML_HASH` text leaves, emitted unwrapped.

- [x] **Step 1: Write red tests** for `<span>`, `<br />`, inline and standalone comments, and fixture simple `div`/raw-`hr` cases; assert Advanced stays skipped.

  Run: `uv run pytest tests/test_act2_slice3.py tests/test_act3_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Inline HTML' -q`

  Expected: Simple/comment failures; Advanced skip.

- [x] **Step 2: Implement bounded matching.** Respect documented left-margin/blank-line boundaries; protect inline regions to `>` or `-->`; emit code-10 leaves for raw blocks; Act IV writes their bytes with block separators. Do not match nested or attributed blocks.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act2_slice3.py tests/test_act3_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Inline HTML (Simple) or Inline HTML comments' -q && uv run python scripts/strict_parity_harness.py 'Inline HTML (Simple)' 'Inline HTML comments'`

  Expected: two strict byte-identical cases.

- [x] **Step 3: Checkpoint** with global gate, token-code test if changed, enabled mdtest/spikes; enable two fixtures; commit `feat: preserve simple html regions`; push.

### Task 6: Compose blockquotes with code leaves and close Slice 3

**Files:** Modify Act II/IV IR and TOML, Act-II/IV Slice-3 tests, `tests/test_mdtest.py`, `tests/test_slice3_medium_risk.py`, and roadmap at final closure; regenerate affected fragments.

**Interfaces:** Per accepted-design Amendment A5, Act II preserves the raw post-marker quote payload in a `PARA`: the fixture's code leaves therefore carry `4/8/4` leading ASCII spaces on their three physical lines. Act IV alone recognizes the initial four-space candidate while a blockquote frame is live, removes one four-space code indent from every physical code line, and emits the resulting `0/4/0` payload. Act II never needs a simultaneous source glyph, output carrier, and quote-mode register.

- [x] **Step 1: Write red stream/bytes tests** for the fixture, final code newline and indentation repair, plus unchanged standalone code behavior.

  Run: `uv run pytest tests/test_act2_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Blockquotes with code blocks' -q`

  Expected: FAIL.

- [x] **Step 2: Replace the obsolete red Act-II `CODE_BLOCK` assertion, then implement the representable late quote-code normalization.** First change `tests/test_act2_slice3.py` so the fixture asserts `BLOCKQUOTE_OPEN`, `PARA("Example:")`, a `PARA` whose payload is exactly `    sub status {\n        print "working";\n    }\n`, `PARA("Or:")`, a `PARA` whose payload is exactly `    sub status {\n        return "working";\n    }\n`, and `BLOCKQUOTE_CLOSE`. These are raw post-marker source payloads (`4/8/4`), not the normalized code-emitter payload. Add focused contracts that the entry and continuation quote prefixes consume one optional marker space or tab only, preserve every following source space, and leave ordinary quote text unchanged. In `tests/test_act4_slice3.py`, retain the standalone `CODE_BLOCK` test; replace its synthetic quote-code-token input with the five `PARA` leaves above and assert the fixture's emitted code is `sub status {\n    print "working";\n}\n` / `sub status {\n    return "working";\n}\n`. Add probe-replay cases for one, two, three, and four-then-EOF leading spaces, each rendered as an ordinary quoted paragraph in source order. In `src_ir/act2.py`, route quote entry and quote continuation through `PASS_QUOTE_PREFIX` / `PASS_QUOTE_CONTINUE_PREFIX`: consume at most one marker space or tab, then copy every remaining glyph unchanged to Lady Macbeth's mixed carrier; do not use Horatio as a mutable indentation counter. In `src_ir/act4.py`, before normal paragraph opening only when Prospero's top frame is `QUOTE_EMPTY` or `QUOTE_USED`, use `SCRIBE_QUOTE_CODE`, `SCRIBE_QUOTE_CODE_CLOSE`, `SCRIBE_QUOTE_CODE_PROBE`, and `SCRIBE_QUOTE_CODE_REPLAY` to pop/restore that frame, probe the first four Puck glyphs, and either (a) for four ASCII spaces followed by a non-terminator fifth glyph, enter the existing code emitter through a bounded line-prefix adapter that discards exactly four ASCII spaces at the start of every physical code line while preserving all later spaces and the terminal code newline, or (b) reverse-push every probe glyph onto Puck and resume the existing paragraph emitter. Pop the temporary count before code/paragraph frame handling, and use the existing code-leaf return route to set `QUOTE_USED`. Add the ready-to-paste reserved TOML entries above before using their labels; regenerate only through splc and assemble. Do not add a token, third on-stage character, nested-blockquote behavior, tab expansion, or general code-block parser.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act2_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Blockquotes with code blocks' -q && uv run python scripts/strict_parity_harness.py 'Blockquotes with code blocks'`

  Expected: focused contracts pass, the documented mdtest comparison and fresh-oracle strict parity pass, and the generated/literary gate below reports no IR, parse, or controlled-surface error.

  Then run the required SPL/literary checkpoint:

  `uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q && uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q`

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

All ten row-6 fixtures map to Tasks 2–6. Task 2 supplies green characterization because its behavior is already proved; later tasks supply red tests before their implementation boundary. Every task has exact commands, strict oracle proof, generated/literary gate where applicable, regression, fixture enablement, and checkpoint. The plan neither declares Slice 2 shipped nor authorizes Slice-4 behavior.

## Amendment A1 (2026-07-14): Task 2 proved-baseline promotion

The cited accepted design's Amendment A1 is binding for Task 2. The former
Step 1 contradicted the current repository: its two proposed red cases and
the complete fixture already pass through both execution paths, so its
strict-xfail fixture contract XPASSes. This amendment replaces that impossible
red phase with green characterization and controlled fixture enablement. It
also replaces the invalid `-k 'Hard-wrapped paragraphs'` expression with a
valid identifier selector and a fully quoted mdtest node id. Task 2 makes no
SPL-facing change, consumes none of its reserved literary labels, and leaves
all later tasks unchanged.

## Amendment A2 (2026-07-14): Task 2 Step 2 checkpoint reconciliation

Task 2 Step 2's file delta landed on `main` as commit `1b1bdfb`
(`test: promote hard-wrap baseline contracts`) before a later loop iteration
attempted to mint the plan's narrower checkpoint message
`test: enable hard-wrapped paragraph fixture`. By that point `HEAD` already
matched `origin/main` for `tests/test_act2_slice3.py`,
`tests/test_slice3_medium_risk.py`, and `tests/test_mdtest.py`, so a second
checkpoint commit would have been empty. Rerun the Step 2 evidence gate, then
treat the task as complete without fabricating a redundant commit and advance
the loop to Task 3 Step 1.

## Amendment A3 (2026-07-15): Task 4 Act-II HR-replay prerequisite

The accepted design's Amendment A2 is binding. The former Task-4 Step 2 was
unrepresentable on current main because the mixed `Strong and em together`
input fails in Act II at `PASS_CONTAINERS_DEPTH` before Act III begins. The
failure is not an emphasis requeue-order observation: a failed `***` or `___`
HR candidate replays its glyphs while retaining Macbeth's temporary positive
marker count. The next ordinary line is classified as list-item content, and
its following blank line has no `ITEM_START` frame to close.

This amendment expands Task 4's existing implementation boundary to include
only the design-authorized Act-II scratch-register reset and list-handoff
guard described in Step 2. It adds `tests/test_act2_slice3.py` and Act II's
generated fragment to the task's explicit surface. No new scene label or TOML
entry is needed: the repair uses the existing `PASS_HR_*` scenes and their
reserved labels. The exact required literary compliance commands are
`uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py -q`
within the Step-2 gate, alongside generated-fragment, parse-smoke, and splc
validation checks. The former planner-only blocker is cleared by this
amendment; any need for a new token, scene/title, or broader list/HR grammar
remains `BLOCK[plan]`.

## Amendment A4 (2026-07-15): Task-5 Step-1 branch disposition

The MCO reconciliation action naming
`implement-1fc3c17d5ed7433dbbae26ed447a8bb0-codex-implement` is stale at
this checkout. Its head `e60e0fe7676f7e5e1e1f89e36c9a84c953f96dfd` equals
both `main` and `origin/main`; it contains only the Task-5 Step-1 checkbox
update already present in this plan. The branch is therefore recorded as
`integrated` in `.agent/branch-dispositions.toml`, with successful
merge-base ancestry and empty `main..branch` log/three-dot diff as evidence.

No implementation step is checked or advanced by this amendment. Task 5
remains at Step 2, and its existing SPL literary protocol, ready-to-paste
reservation, generated-artifact prohibition, and exact compliance commands
remain binding. The untracked `scripts/release_entry.py` is user work outside
this plan and is deliberately unstaged.

## Amendment A5 (2026-07-15): Task-6 quote payload and per-line deindentation

The raw-quote implementation correctly established the five-leaf stream, but
exposed an ambiguity in Amendment A4's abbreviated payload example. Markdown
blockquote stripping removes the `>` and at most its immediately following
space or tab; it does **not** remove a code indent. For the fixture, Act II
must therefore preserve the two code leaves as `4/8/4` source indentation:
`    sub status {\\n        print "working";\\n    }\\n` and
`    sub status {\\n        return "working";\\n    }\\n`. The former
`4/4/0` Act-II contract is withdrawn; it accidentally described Act IV's
normalized code payload rather than the inter-act stream.

Act IV owns the second, independent normalization: after its existing
four-space initial probe qualifies a quoted `PARA` leaf, its bounded
quote-code adapter removes exactly four ASCII spaces at the beginning of
**each physical code line** before the existing code emitter writes it. It
must preserve the remaining four spaces on the fixture's inner `print`/
`return` lines, remove the closing line's four spaces, preserve the final
newline, and replay every non-qualifying probe unchanged. This is not a
general indented-code parser: it applies only to a qualifying `PARA` inside
the existing top-level blockquote frames, uses the already reserved
`SCRIBE_QUOTE_CODE*` surfaces, and authorizes no new token, participant,
tab expansion, or nested-blockquote behavior.

The implementation tests must distinguish the two boundaries explicitly:
Act-II fast-stream assertions require `4/8/4`; Act-IV synthetic-stream and
fresh-oracle assertions require `0/4/0` inside `<pre><code>`. The existing
exact Task-6 generated-fragment, parse-smoke, splc-validation,
literary-compliance, TOML-schema, Amps, focused mdtest, strict-parity, spike,
and final-suite commands remain the mandatory evidence gates. This amendment
supersedes the conflicting Task-6 Step-2 wording and clears the planner-only
blocker.

## Amendment A6 (2026-07-15): Task-6 detab boundary and oracle-exact code contract

The local `Markdown.pl` v1.0.1 oracle disproves two clauses in the former
Task-6 Step-2 contract. First, Act I detabs before Act II: source
`>\t    code line\n` reaches Act II as `>       code line\n`, so the existing
two-scene Act-II prefix route cannot and must not consume an optional tab.
Replace the former tab assertions with source-through-Act-I assertions: after
the existing one ASCII marker-space consumption, `>     code line\n` yields
`PARA("    code line")`, while `>\t    code line\n` (both entry and
continuation) yields `PARA("      code line")`. Keep the ordinary-text
contract. The real fixture's two code leaves are `4/8/4` but have **no**
terminal newline in the decoded Act-II stream.

Second, fresh oracle output for `Blockquotes with code blocks` is `0/2/0`,
not the former synthetic `0/4/0`: its inner `print` and `return` lines begin
with exactly two ASCII spaces. Replace the Act-IV synthetic stream with the
five `PARA` leaves from the Act-II contract, with no terminal newline on the
two code leaves, and assert the oracle-exact HTML. The bounded adapter is
authorized only for those three-line `4/8/4` leaves under `QUOTE_EMPTY` or
`QUOTE_USED`: it supplies the emitter's final newline and removes `4/6/4`
spaces to produce `0/2/0`. Any other physical-line shape, a terminal newline
in the carrier, or a nonqualifying first-four-space probe reverse-replays to
the ordinary quoted paragraph path; it must not become a general indented-code
parser.

This amendment supersedes Task-6 Step-2's claims that Act II consumes a tab
or that Act IV emits `0/4/0`. It clears the planner-only blocker without
adding a token, title, scene, character, tab expansion, nested-blockquote
case, or Slice-4 behavior. The exact compliance commands already written in
Task 6 remain mandatory, including `tests/test_splc_generated_fragments.py`,
`tests/test_spl_parse_smoke.py`, `tests/test_splc_validate.py`,
`tests/test_literary_compliance.py`, `tests/test_literary_toml_schema.py`,
`tests/test_assemble.py`, and `tests/test_codegen_html.py`.

## Amendment A7 (2026-07-17): Task-6 quote-prefix bridge and Spike-B gate

The accepted design's Amendment A7 is binding. The final gate's eight
nested-block spike failures exposed that the two quote-prefix scenes share
`PASS_LISTS_RAW_NEXT`, a list-pass reader whose continuation lifecycle is part
of shipped Spike-B composition. This amendment authorizes only a quote-owned
one-glyph bridge in `src_ir/act2.py`; it is a prerequisite inside the existing
unchecked Task-6 Step 3, not a new task, fixture, or plan.

Before the repair, append these ready-to-paste Incidental Act-II surfaces to
`src/literary.toml`; do not invent prose during implementation:

```toml
[scenes.PASS_QUOTE_PREFIX_AFTER_MARKER]
title = "Lady Macbeth takes the echo's single pale mark."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_PREFIX_COPY_GLYPH]
title = "Lady Macbeth returns the echo's unshorn sign."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_CONTINUE_AFTER_MARKER]
title = "Macbeth receives the echo's returning pale mark."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_CONTINUE_COPY_GLYPH]
title = "Macbeth restores the echo's returning sign."
pattern = "scene_of_character"
[scenes.PASS_QUOTE_PREFIX_AFTER_MARKER_GUARD]
title = "The echo keeps one measured pale threshold."
pattern = "bare_statement"
[scenes.PASS_QUOTE_PREFIX_COPY_GLYPH_GUARD]
title = "The echo preserves its unspent first sign."
pattern = "bare_statement"
[scenes.PASS_QUOTE_CONTINUE_AFTER_MARKER_GUARD]
title = "The echo keeps one returning pale threshold."
pattern = "bare_statement"
```

Use only the four working labels in the design-defined entry/continuation
bridge. The three `_GUARD` labels are the entire spare pool; exhausting it is
`BLOCK[plan]`. `PASS_QUOTE_PREFIX` and `PASS_QUOTE_PREFIX_FINISH` dispatch to
the bridges; `PASS_QUOTE_CONTINUE_PREFIX` alone decides whether a subsequent
line continues the quote. The bridge strips at most one post-`>` ASCII space,
copies every other already-detabbed glyph to Lady Macbeth in source order, and
does not assign Macbeth, Horatio, a frame sentinel, or a token. It must not
edit `PASS_LISTS_RAW_NEXT`, `PASS_LISTS_RAW_AFTER_NEWLINE`,
`PASS_CONTAINERS_REPLAY`, or any list/container scene.

First add red contracts in `tests/test_act2_slice3.py` for entry and
continuation marker stripping, retained four/six-space code candidates, and
ordinary quote text; extend `tests/test_act2_contracts.py` and
`tests/test_act2_frame_floors.py` with the four committed files in
`tests/fixtures/architecture_spikes/nested_blocks/` as exact fast-stream and
Act-IV/oracle composition regressions. Then make only the authorized IR/TOML
change, regenerate with `uv run python -m scripts.splc` and
`uv run python scripts/assemble.py`, and run:

```bash
uv run pytest tests/test_act2_slice3.py tests/test_act2_contracts.py tests/test_act2_frame_floors.py tests/test_architecture_spikes.py -q
uv run pytest tests/test_act2_slice3.py tests/test_act4_slice3.py tests/test_mdtest.py -k 'Blockquotes with code blocks' -q
uv run python scripts/strict_parity_harness.py 'Blockquotes with code blocks'
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: every command passes; the quote fixture remains strict
byte-identical; all Spike-B cases are byte-identical; and no generated or
literary check reports an error. Only then rerun the existing final Task-6
Step-3 gate unchanged. A need for any other scene, token, participant,
protected Spike-B route mutation, changed raw `4/8/4` carrier, or broader
quote/code grammar is `BLOCK[plan]`.
