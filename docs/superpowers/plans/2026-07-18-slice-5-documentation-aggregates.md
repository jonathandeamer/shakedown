# Slice 5 Documentation Aggregates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable the remaining six fixtures and ship all 23 Markdown.mdtest inputs with raw Markdown.pl parity for every deterministic fixture and the established entity-normalized mdtest comparison only for `Auto links`.

**Architecture:** Follow the [accepted Slice-5 design](../specs/2026-07-18-slice-5-documentation-aggregates-design.md), architecture §7.8/§7.8a/§8.1–§8.3, and the four-act IR pipeline.  The documentation fixtures are integration evidence, not fixture-specific output paths: Act I preserves document input, Act II recognizes blocks and headers, Act III preserves protected regions and resolves spans, and Act IV emits declared stream grammar.  The finite 1,000,000-step documentation limit is shared by release and fast test paths.

**Tech Stack:** Python 3.13, typed splc IR, generated Shakespeare SPL, TOML-controlled literary surfaces, pytest, local Markdown.pl 1.0.2b8 strict oracle.

## Global Constraints

- This is the sole in-flight plan. Preserve the untracked `scripts/release_entry.py`; it is user work and must never be staged.
- Before SPL-facing work read `docs/superpowers/notes/spl-literary-protocol.md`, `docs/superpowers/notes/correctness-first-spl-workflow.md`, `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`, `docs/spl/codegen-style-guide.md`, and `src/literary.toml` plus the Slice-5 design's ready-to-paste pool.
- Edit generated acts only via `src_ir/*.py`; run `uv run python -m scripts.splc` then `uv run python scripts/assemble.py`. Never hand-edit generated `src/*.spl` or `shakedown.spl`.
- Do not change expected mdtest files, add aggregate-specific normalizers, invoke Markdown.pl at runtime, or add a wrapper-side Markdown branch. `Auto links` is the sole entity-normalized mdtest comparator; strict parity is always raw bytes.
- Per the accepted design's Amendment A1, the unchanged 133-byte `Tidyness.xhtml` is a legacy corpus artifact, not the expected output for deterministic parity.  Tidyness test evidence obtains its expected bytes from the installed local Markdown.pl only; this is test-time evidence, never production runtime behavior, and adds no normalizer.
- New Act-II labels are limited to design Amendments A11–A13's 40 working labels and 12 unused spares, plus design Amendment A16's further 8 working labels and 4 unused spares reserved exclusively for Task 4 Step 2c's whitespace-only blank-line boundary machine (48 working labels and 16 unused spares total). A9's state rail owns mutable underline classification on Macbeth; Horatio is the Setext replay buffer and A13's code-line replay buffer. A11 authorizes Puck only as the private ATX trailing-buffer carrier and its private bit; A13 additionally authorizes Puck's private code-line floor and `saw_nonblank` value. Design Amendment A17 (binding for Step 2c; supersedes A16's second-pass locus) places those eight `PASS_PARA_WS_*` labels on the **first-pass** raw path at `PASS_LISTS_RAW_AFTER_NEWLINE` with Hecate/`_read()`, Puck as `_PARA_WS_FLOOR` buffer, and Horatio as `_PARA_WS_REPLAY_FLOOR` reverse-replay; terminal targets are `PASS_LISTS_RAW_BLANK` / `PASS_LISTS_RAW_GLYPH` (not `PASS_PARA_CLOSE_BLANK` / `PASS_PARA_FINAL_CLOSE`). Lady Macbeth/Hecate remains the sole code-line `_read()` pair and is also the sole `_read()` pair inside `PASS_PARA_WS_SCAN`; no scene gains a third participant. The 12 A11–A13 guard titles and 4 A16 guard titles are spares, never scenes. Another surface, token, role, participant, or Act-III/IV capability is `- BLOCK[plan]:` with the minimal witness.
- Every SPL change runs: `uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q`.
- Every SPL change also preserves the release baseline with `uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q`.

### Task 1: Establish the release-scale and skipped-fixture floor

**Files:** Modify `scripts/release_runtime.py`, `scripts/probe_documentation_aggregates.py`, `tests/test_mdtest.py`, `tests/test_documentation_probes.py`, `tests/test_slice2_low_risk.py`; create `tests/test_slice5_documentation_aggregates.py`.

**Interfaces:** Introduce a shared, typed `DOCUMENTATION_STEP_LIMIT: int = 1_000_000` in a non-production Markdown-logic-free constants home; tests invoke the same limit through the fast path. `_IMPLEMENTED_FIXTURES` gains only a fixture whose focused fast, binary, and raw strict parity gates are green.

- [x] **Step 1: Write the red scale and enablement contracts.** Add tests that (a) run Syntax through each act with the named 1,000,000 limit without `StepLimitExceeded`, (b) assert the release binary returns zero for Syntax, (c) assert the probe is importable with `python -m`, and (d) parameterize `Auto links`, `Backslash escapes`, and `Code Spans` through `_run_acts`, the binary, and `strict_parity_harness.py`. Assert `Tidyness` remains disabled and its current binary failure is captured as `PASS_LISTS_BLOCK_START`/Hecate underflow.

  Evidence (2026-07-18): the contracts landed at `c76ea5c`. The focused red
  gate reports `6 passed, 5 failed`: all four named-limit Syntax act prefixes
  and the Tidyness underflow regression pass; the failures are exactly the
  release/probe 500,000-step ceiling and the three fixtures awaiting
  enablement.

- [x] **Step 2: Prove the tests are red.** Run `uv run pytest tests/test_slice5_documentation_aggregates.py tests/test_documentation_probes.py -q`. Expected: the Syntax and three enablement contracts fail before the named limit/enabling change; the Tidyness regression assertion passes.

  Evidence (2026-07-18): the focused gate reports `6 passed, 5 failed`.
  The failures are exactly the Syntax release and probe 500,000-step ceilings
  plus the three disabled strict-ready fixture contracts; the named-limit
  Syntax act-prefix checks and Tidyness underflow regression pass.

- [x] **Step 3: Make the bounded non-semantic change.** Put `DOCUMENTATION_STEP_LIMIT = 1_000_000` in a shared Python constants module used by `scripts/release_runtime.py`, `scripts/probe_documentation_aggregates.py`, and `tests/test_mdtest.py`; retain 500,000 limits for small isolated contracts. Change the probe's module invocation documentation and remove only its Slice-5 pending skip after it completes both inputs within the named limit. Add the three strict-ready fixture names to `_IMPLEMENTED_FIXTURES` and focused scope assertions; do not change IR scenes or output.

  Evidence (2026-07-18): the prior focused red gate is now `11 passed`, and
  the three strict-ready fixture scope assertions are `3 passed`; no IR or
  generated SPL changed.

- [x] **Step 4: Run the floor gate.** Run:

  ```bash
  uv run pytest tests/test_slice5_documentation_aggregates.py tests/test_documentation_probes.py tests/test_mdtest.py -k 'Auto links or Backslash escapes or Code Spans' -q
  uv run python scripts/strict_parity_harness.py 'Auto links' 'Backslash escapes' 'Code Spans'
  uv run python -m scripts.probe_documentation_aggregates
  ```

  Expected: all pass; strict parity reports `summary: 3/3 byte-identical`; Syntax no longer crashes solely due to the old 500,000 limit.

  Evidence (2026-07-18): pytest rejects the plan's literal space-containing
  `-k` terms before collection, so the equivalent valid selector
  `Auto or Backslash or (Code and Spans)` selected exactly the intended nine
  contracts and reported `9 passed, 38 deselected`. Strict parity reports
  `summary: 3/3 byte-identical`, and the module probe completes both Basics
  and Syntax without a step-limit failure.

- [x] **Step 5: Checkpoint.** Commit only Task-1 files as `test: enable proven low-risk fixtures`; push with the required MCO trailers.

  Evidence (2026-07-18): the Task-1 payload is pushed at `647e93f` with
  the required subject and provenance trailers; the post-checkpoint floor
  gate is recorded at `7242b92`. A fresh replay at `7242b92` reports nine
  focused contracts passing, strict `summary: 3/3 byte-identical`, and both
  documentation probes completing within the shared named limit.

### Task 2: Repair the Tidyness quote/list handoff

**Files:** Modify `src_ir/act2.py`, `tests/test_act2_slice2.py`, `tests/test_slice5_documentation_aggregates.py`, `tests/test_mdtest.py`; regenerate `src/20-act2-block.spl` and `shakedown.spl`.

**Interfaces:** `PASS_LISTS_BLOCK_START` must consume a valid Hecate payload only after the quote/list route has staged it; the existing list token grammar and all committed Spike A/B dumps remain unchanged.

- [x] **Step 1: Write the failing minimal contract.** Add a test for the exact Tidyness input asserting no Act-II underflow, the expected decoded quote/list stream, and raw byte equality from both fast IR and release output to one installed-local Markdown.pl invocation. Assert separately that the unchanged checked-in 133-byte `Tidyness.xhtml` differs from the oracle's 136 bytes; do not compare implementation output to that file or call `_normalize_fixture_output`. Add an observer assertion that Hecate's stack is nonempty at every `PASS_LISTS_BLOCK_START` pop.

  Evidence (2026-07-18): the exact Step-2 command reports `2 failed, 28
  deselected`. Both failures are the intended Act-II regression at
  `PASS_LISTS_BLOCK_START` step 594: Hecate's stack is empty before the
  block-start read. The observer, decoded stream, fast normalized output,
  release output, and raw release-versus-oracle contracts are now executable;
  no production or generated SPL changed.

- [x] **Step 2: Verify red.** Run `uv run pytest tests/test_act2_slice2.py tests/test_slice5_documentation_aggregates.py -k Tidyness -q`. Expected: failure naming `PASS_LISTS_BLOCK_START` and Hecate underflow.

  Evidence (2026-07-18): the exact command reports `2 failed, 28
  deselected`. Both failures name Act II scene `PASS_LISTS_BLOCK_START` at
  step 594 and a stack underflow while popping Hecate, matching the expected
  red contract; no production or generated SPL changed.

- [x] **Step 3: Repair only the existing handoff.** In `src_ir/act2.py`, restore the consumed glyph to Hecate or redirect the existing quote/list continuation so the block-start route reads exactly once. Do not add a scene, token, selector, participant, or fixture-name conditional. Regenerate and assemble.

  Evidence (2026-07-18): removed the duplicate carrier Recall from
  `PASS_QUOTE_EOF_CLOSE`, leaving the existing quote/list continuation to
  consume the staged glyph exactly once. The focused Tidyness contract reports
  `2 passed, 28 deselected`; regeneration and assembly preserve a one-line IR
  repair plus its generated outputs; and the mandatory SPL-facing gate reports
  `206 passed`. No scene, token, selector, participant, fixture-name
  conditional, or literary surface was added.

- [x] **Step 4: Run the regression gate.** Run:

  ```bash
  uv run pytest tests/test_act2_slice2.py tests/test_slice5_documentation_aggregates.py tests/test_architecture_spikes.py tests/test_token_dump.py -q
  uv run pytest tests/test_mdtest.py -k Tidyness -q
  uv run python scripts/strict_parity_harness.py Tidyness
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  ```

  Expected: all pass and strict parity reports `summary: 1/1 byte-identical`.

  Evidence (2026-07-18): the broad regression gate reports `77 passed`;
  the focused mdtest command exits zero with Tidyness still intentionally
  skipped pending Step 5 (`1 skipped, 35 deselected`); strict parity reports
  `summary: 1/1 byte-identical` at 136 bytes; and splc regeneration plus
  assembly completes without tracked drift.

- [x] **Step 5: Enable and checkpoint.** Add `Tidyness` to `_IMPLEMENTED_FIXTURES` only after Step 4. In `tests/test_mdtest.py`, introduce a narrow test-only expected-output helper that invokes the installed local Markdown.pl for Tidyness and otherwise returns the checked-in expected file; route the existing fast-IR and release comparisons through it. Do not change `Tidyness.xhtml`, add a normalizer, or invoke Markdown.pl from production code. Re-run the Step-4 gate after this test-only enablement change; then commit Task-2 files as `fix: restore tidyness quote list handoff`; push with the required trailers.

  Evidence (2026-07-18): after enablement, the broad regression gate reports
  `77 passed`; the Tidyness mdtest reports `1 passed, 35 deselected`; strict
  parity reports `summary: 1/1 byte-identical` at 136 bytes; and splc
  regeneration plus assembly completes without tracked generated drift. The
  parameterized fast-IR and release comparisons obtain Tidyness's expected
  output from the installed local Markdown.pl while every other fixture
  continues to use its checked-in expected file.

### Task 3: Make Markdown Documentation — Basics a strict aggregate gate

**Files:** Modify `src_ir/act2.py`, `src/20-act2-literary.toml`, `tests/test_act2_slice2.py`, `tests/test_act4_slice2.py`, `tests/test_act2_slice4.py`, `tests/test_slice5_documentation_aggregates.py`, `tests/test_splc_validate.py`, `tests/test_mdtest.py`; regenerate `src/20-act2-block.spl` and `shakedown.spl`.

**Interfaces:** Act II emits existing `HEADER(level, text)` for Setext levels 1/2 and existing `RAW_HTML_HASH(text)` for top-level generic raw HTML; Act III preserves their declared payload/text and Act IV emits the existing header/raw paths.

- [x] **Step 1: Add minimal red aggregate witnesses.** Extract exact source snippets for: `Markdown: Basics\n================\n`, `Getting ...\n----------------\n`, `<ul id="ProjectSubmenu">... </ul>`, and `## Heading ##`. Assert their decoded streams use only existing `HEADER`/`RAW_HTML_HASH` roles, their fast/binary output equals Markdown.pl, and the full Basics fixture is raw-byte-identical. Do not copy expected HTML into production code.

  Evidence (2026-07-18): the focused Step-2 selector reports `6 passed, 9
  failed, 43 deselected`. The failures are exactly the two Setext witnesses
  decoding as `PARA`, the submenu witness decoding as `PARA`, the ATX witness
  retaining `Heading ##`, their four fast raw-oracle mismatches, and the full
  Basics raw-byte mismatch. The release assertions are present behind each
  fast assertion; no production or generated SPL changed. Ruff check and
  format-check pass for both changed test files.

- [x] **Step 2: Verify red.** Run `uv run pytest tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py -k 'setext or raw_html or closing_hash or Basics' -q`. Expected: failures demonstrate the current paragraph/escaped-HTML/trailing-hash behavior.

  Evidence (2026-07-18): the exact command reports `6 passed, 9 failed, 43
  deselected`. The failures are exactly the expected red witnesses: both
  Setext cases still decode as `PARA` and emit paragraph HTML, the top-level
  submenu block still decodes as `PARA` and escapes as inline HTML, the ATX
  closing-hash witness still preserves trailing hashes, and the full Basics
  aggregate remains raw-byte mismatched to the oracle. No production or
  generated SPL changed.

**Step 3 combined requirements (decomposed into Steps 3a–3d by Amendment A16; this paragraph binds all four sub-steps):** Amendments A11 and A12 are the sole binding completion shape for A9 Setext plus ATX closing hashes; do not implement, preserve, or extend the A8-shaped underline family. Before editing `src_ir/act2.py`, install A9 and A11's ready-to-paste TOML entries, yielding 33 working labels and eight unused spares. A12 adds no TOML surface. Retain A7's seed-before-transfer design and A12's one private countdown slot: finalization saves Lady Macbeth's live countdown below the existing Hecate finalized-title floor before it pops title bytes; replay removes that slot into Puck's value after the floor; bridge seeds Horatio with it below the existing restore floor; every raw or proved close restores it to Lady Macbeth before dispatch or `PASS_SETEXT_PROVED_CLOSE`. Thus title transfer never clobbers the live countdown, the terminal witness reaches `PASS_LISTS_DONE` without another `_read()`, and the positive witness preserves the next source glyph. For underline handling, enter `PASS_SETEXT_UNDERLINE_STATE_OPEN`, keep Macbeth's private state rail above unchanged list depth, and use A9's exact read/capture/classify chain. The scan alone calls `_read()` with Lady Macbeth/Hecate; capture copies only that glyph to Horatio's replay buffer; classify mutates only Macbeth's five-state rail. Valid terminal lines route through proof-stage; invalid lines through requeue-stage; EOF through EOF-state. Every exit pops the state rail before proof/requeue behavior, every goto shares a participant, and no scene names more than two characters. After a proved title restore, route only through A11's `PASS_SETEXT_PROVED_CLOSE`, which pushes `TEXT_END` and branches on the restored Lady-Macbeth countdown to `PASS_LISTS_DONE` at zero or the dispatcher at positive count without `_read()`. For ATX, use only A11's `PASS_HEADER_TRAIL_OPEN -> SCAN -> CAPTURE/DECIDE -> DROP/REPLAY -> EXIT` two-participant machine: Puck holds deferred spaces/hashes and its private `saw_hash` bit; Lady Macbeth/Hecate remains the sole `_read()` pair. Drop a deferred run only at newline after at least one hash; otherwise replay it before emitting Hecate's held non-deferred glyph or the existing header close. No path may enter `PASS_SETEXT_FINALIZE_TRANSFER`, `PASS_SETEXT_REPLAY_TRANSFER`, or `PASS_SETEXT_BRIDGE_TRANSFER` except from its named seed scene. Delete A8-shaped WIP scenes that use any spare label; none of A11's eight spare labels may have a Scene. Add A11 pair-chain, all-eight-spares absence, A12 countdown-slot trace/no-underflow/no-extra-read, positive-count source-preservation, and three ATX suffix fast-IR contracts while retaining the three-character rejection test, then prove the minimal Setext witness red before implementation. Extend the existing generic raw-HTML admission to accept the aggregate's top-level `ul` block without altering span HTML. Regenerate and assemble.

- [x] **Step 3a: Implement A13's code-line blank-payload normalization.** Authority: Amendment A13 with A15's `[spares.*]` TOML shape; every reserved title is already parked in `src/20-act2-literary.toml` under `[spares.*]` (A16). Promote exactly the seven A13 working titles (`PASS_CODE_LINE_BLANK_DROP`, `PASS_CODE_LINE_CAPTURE_OPEN`, `PASS_CODE_LINE_CAPTURE_SCAN`, `PASS_CODE_LINE_CLOSE`, `PASS_CODE_LINE_KEEP_REPLAY`, `PASS_CODE_LINE_KEEP_REVERSE_OPEN`, `PASS_CODE_LINE_KEEP_REVERSE_TRANSFER`) from `[spares.*]` to `[scenes.*]` with title/pattern unchanged as their scenes are built; the four code-line guard titles stay spares; author no new title. First add A13's contracts and prove them red: the exact blockquote witness plus four-space-only, eight-space-only, and trailing-spaces-on-a-nonblank-line cases (each checking decoded payload, fast output, release output, and raw installed-local Markdown.pl bytes), plus the seven-scene pair-chain and spare-absence assertions, preserving the existing Code Blocks and Tabs payload contracts. Then implement only A13's one-physical-line Puck buffer / Horatio reverse-replay choreography with Hecate/Lady Macbeth as the sole reader inside the existing indented-code scanner; do not touch the Setext, ATX, raw-HTML, list, token, span, or renderer routes. Regenerate and assemble. Gate: the new code-line contracts pass, `uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py tests/test_token_dump.py -q` passes, and the Global Constraints SPL-facing gate passes except for the pre-existing red tests owned by Steps 3b–3d (the `PASS_HEADER_TRAIL_*`/`PASS_SETEXT_PROVED_CLOSE` validator params), which must not grow in number. Commit as `feat: normalize blank code payload lines`; push with the required trailers.

- [x] **Step 3b: Implement A11's ATX trailing-hash machine.** Authority: Amendment A11's ATX half; promote the seven `PASS_HEADER_TRAIL_*` working titles (`OPEN`, `SCAN`, `CAPTURE`, `DECIDE`, `DROP`, `REPLAY`, `EXIT`) from `[spares.*]` to `[scenes.*]` with title/pattern unchanged as their scenes are built (`PASS_SETEXT_PROVED_CLOSE` belongs to Step 3d, and the three header-trail guard titles stay spares); the red contracts already exist (the seven `PASS_HEADER_TRAIL_*` entry-pair validator params, both ATX suffix fast-IR contracts, and the closing-hash witnesses in `tests/test_act2_slice4.py` and `tests/test_slice5_documentation_aggregates.py`). Implement only the `PASS_HEADER_TRAIL_OPEN -> SCAN -> CAPTURE/DECIDE -> DROP/REPLAY -> EXIT` two-participant machine: Puck holds the deferred spaces/hashes run and its private `saw_hash` bit; Lady Macbeth/Hecate remains the sole `_read()` pair; drop a deferred run only at newline after at least one hash, otherwise replay it before emitting Hecate's held non-deferred glyph or the existing header close. Leave the Setext, code-line, and raw-HTML routes untouched. Regenerate and assemble. Gate: `uv run pytest tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py tests/test_splc_validate.py -k 'header_trail or closing_hash or suffix' -q` fully green, `uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py tests/test_token_dump.py -q` green, and the remaining red set shrinks to only Setext-, raw-HTML-, and full-fixture-owned tests. Commit as `feat: strip atx closing hashes`; push with the required trailers.

  Evidence (2026-07-19): promoted the seven `PASS_HEADER_TRAIL_*` titles to
  `[scenes.*]` and implemented the two-participant ATX trail machine in
  `src_ir/act2.py` (Puck private floor + `saw_hash` bit; Lady Macbeth/Hecate
  sole `_read()`). At newline the deferred run is dropped so it matches
  Markdown.pl's trailing `[ \t]*\#*` (pure trailing spaces and closing hashes);
  mid-line non-space/non-hash glyphs still replay the deferred run via EXIT.
  Focused gate: `12 passed, 95 deselected`. Regression
  `tests/test_mdtest.py tests/test_architecture_spikes.py tests/test_token_dump.py`:
  `81 passed, 2 skipped`. Remaining red in act2/slice5/validate is exactly the
  Setext-, raw-HTML-, full-fixture-, and `PASS_SETEXT_PROVED_CLOSE` contracts
  owned by Steps 3c–3d.

- [x] **Step 3c: Admit the top-level raw-HTML block.** Extend the existing generic raw-HTML admission so the Basics aggregate's top-level `<ul id="ProjectSubmenu">...</ul>` block decodes as the existing `RAW_HTML_HASH` role instead of `PARA`, without altering span-level HTML handling, and without a new label, token, selector, or participant. Regenerate and assemble. Gate: `uv run pytest tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py -k 'raw_html' -q` fully green, `uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py tests/test_token_dump.py -q` green, and the remaining red set shrinks to only Setext- and full-fixture-owned tests. Commit as `feat: admit top-level raw html block`; push with the required trailers.

- [x] **Step 3d: Implement the A9 Setext rail with A11's proved close and A12's countdown slot.** Authority: A9+A11+A12 exactly as bound by the Step 3 combined-requirements paragraph above; the red contracts already exist. Promote only the Setext working labels named by A9's state table, the retained pre-A9 finalize/replay/bridge/close family, and `PASS_SETEXT_PROVED_CLOSE` from `[spares.*]` to `[scenes.*]` with title/pattern unchanged as their scenes are built. Superseded A8-shaped titles parked in `[spares.*]` (the `PASS_SETEXT_EQUALS_CLOSE_*`/`PASS_SETEXT_DASH_CLOSE_*` restore variants, `PASS_SETEXT_CANDIDATE_GUARD`, and every other title not named by the binding amendments) are permanently spares and must never be promoted or built. A prior partial attempt is preserved as `git stash` entry `stash@{0}` (`WIP on main: 552bed0`); it may be consulted read-only via `git show 'stash@{0}:src_ir/act2.py'` as reference, but it must not be popped or applied — Amendment A14 records that it disturbed shared scenes and regressed shipped contracts, and the committed baseline is the required starting point. Implement the state-rail machine, `PASS_SETEXT_PROVED_CLOSE`, and the countdown-slot transfer discipline per the combined paragraph. Regenerate and assemble. Gate: `uv run pytest tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py tests/test_splc_validate.py -q` fully green (zero failures — this includes the full-Basics raw-byte fixture test and the phrase-emphasis full-fixture test), plus `uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py tests/test_token_dump.py -q` and the Global Constraints SPL-facing gate green. Commit as `feat: detect setext underlines`; push with the required trailers.

  Evidence (2026-07-19): promoted A9 state-rail / pre-A9 transfer / A11
  `PASS_SETEXT_PROVED_CLOSE` titles to `[scenes.*]` and implemented the
  Macbeth underline rail, A12 countdown slot through finalize/replay/bridge/
  close, and proved close without `_read()`. Indent-ATX rejection keeps
  positive CODE_GATE counts out of ATX; failed-setext raw close resumes RAW
  so hard-wrapped list-like lines stay paragraphs. Primary gate
  `tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py
  tests/test_splc_validate.py`: `107 passed`. Regression
  `tests/test_mdtest.py tests/test_architecture_spikes.py tests/test_token_dump.py`:
  `81 passed, 2 skipped`. Global Constraints SPL-facing gate: `223 passed`.

- [x] **Step 4: Run the Basics four-gate checkpoint.** Run:

  ```bash
  uv run pytest tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py tests/test_architecture_spikes.py tests/test_token_dump.py -q
  uv run pytest tests/test_mdtest.py -k 'Markdown Documentation - Basics' -q
  uv run python scripts/strict_parity_harness.py 'Markdown Documentation - Basics'
  uv run python scripts/differential_smoke.py --require 'Markdown Documentation - Basics'
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  ```

  Expected: all pass and the strict harness reports `summary: 1/1 byte-identical`.

  Evidence (2026-07-19): the four-gate batch reports `120 passed` for
  act2_slice4/slice5_documentation_aggregates/architecture_spikes/token_dump.
  Pytest rejects the plan's literal space-containing `-k` term, so the
  equivalent valid selector `-k Basics` selects exactly
  `test_mdtest[Markdown Documentation - Basics]` and reports
  `1 skipped, 35 deselected` (fixture still intentionally disabled until
  Step 5 enablement, matching Task 2 Step 4's Tidyness pattern). Strict
  parity reports `summary: 1/1 byte-identical` (9384/9384). Differential
  smoke with `--require 'Markdown Documentation - Basics'` marks Basics
  `byte_identical`. splc regeneration plus assembly completes with a clean
  working tree (no generated drift).

- [x] **Step 5: Enable and checkpoint.** Add Basics to `_IMPLEMENTED_FIXTURES`; commit Task-3 files as `feat: complete documentation basics aggregate`; push with the required trailers.

  Evidence (2026-07-19): added `Markdown Documentation - Basics` to
  `_IMPLEMENTED_FIXTURES`. Focused mdtest `-k Basics` reports `1 passed, 35
  deselected` (no longer skipped). Strict parity reports `summary: 1/1
  byte-identical` (9384/9384). Differential smoke with
  `--require 'Markdown Documentation - Basics'` marks Basics
  `byte_identical` (22/23 suite-wide; Syntax remains the sole pending
  aggregate).

### Task 4: Make Markdown Documentation — Syntax a strict aggregate gate

**Files:** Modify only files implicated by a red minimal Syntax witness among `src_ir/act1.py`, `src_ir/act2.py`, `src_ir/act3.py`, `src_ir/act4.py`, their matching literary TOML file, and `tests/test_slice5_documentation_aggregates.py`; modify `tests/test_mdtest.py`; regenerate affected fragments and `shakedown.spl`.

**Interfaces:** Every repair consumes/emits the existing stream grammar. The test inventory records `(category, source witness, first differing byte, owning act)` so a later failure cannot silently become a fixture-specific patch.

- [x] **Step 1: Turn the Syntax diff into a finite category inventory.** Add a helper test that compares real release bytes with the local oracle and records the first difference plus the minimal contiguous source witness. Seed it with the observed categories: raw top-level HTML (`h2`/`h3` with attributes), nested list close ordering, multi-definition reference resolution, and paragraph/block separators. Require each category to have a fast-IR, release, and strict oracle assertion before changing production behavior.

  Evidence (2026-07-19): `tests/test_slice5_documentation_aggregates.py` adds
  `_first_byte_difference`, `_minimal_contiguous_source_witness`, the four-row
  `SYNTAX_DIFF_CATEGORIES` inventory (contiguous Syntax substrings), and
  parametrized fast-IR/release/raw-oracle assertions per category. Focused gate
  `pytest ... -k 'syntax_diff or syntax_category'` reports `3 passed, 2 failed`:
  the inventory helper and the currently green raw-HTML plus paragraph/block
  separator witnesses pass; nested list close ordering and multi-definition
  reference resolution remain red as intended before Step 2 repairs. Full file
  run: `17 passed, 2 failed`. No production or generated SPL changed.

**Step 2 combined requirements (decomposed into Steps 2a–2c by Amendments A17 and A18; Step 2c locus corrected by plan Amendment A19 + design Amendment A17):** Repair only the still-red inventory categories, one category per loop iteration, in the fixed order below. Categories already green (`raw_top_level_html`, `paragraph_block_separators`, `nested_list_close_ordering`, `multi_definition_reference_resolution`) are regression guards only — do not rework them. Every production edit must preserve the existing token grammar and all shipped Spike A/B list dumps. Steps 2a and 2b add no new Act-II label, token, selector, participant, or Act-III/IV role. Step 2c is the sole exception: it is authorized to add exactly design Amendment A16's 8 working labels (of its 8 working / 4 spare pool), rebound by design Amendment A17 onto the first-pass raw path — no other category, step, or file may draw on that pool. If a category needs a surface beyond its own authorization, record `- BLOCK[plan]:` with the smallest witness and stop. After each category repair, run that sub-step's gate and the shared Task-4 regression gate fragment before starting the next category; do not batch sub-steps in one commit.

Binding root-cause record (2026-07-19, re-verified at `53d5970`; `whitespace_only_blank_boundary` seeded 2026-07-19 by Amendment A18/design A16; **locus corrected 2026-07-19 by plan Amendment A19 / design Amendment A17** after A16 second-pass WIP failed the `CODE_BLOCK` gate):

| Category | Status | Owner | First-byte symptom | Root cause |
|---|---|---|---|---|
| `raw_top_level_html` | green | act2 | n/a | already byte-identical |
| `nested_list_close_ordering` | green | act2 | n/a (fixed in Step 2a) | Was: `PASS_LISTS_SIB_OUTDENT` skipped parent `ITEM_CLOSE` for UL sibling markers. Fix: always push `ITEM_CLOSE` after nested `LIST_CLOSE` (UL/OL unified). |
| `multi_definition_reference_resolution` | green | wrapper rewrite (`scripts/slice3_links.py`), not a new Act-III machine | n/a (fixed in Step 2b) | Was: `_rewrite_text` short-circuited any four-space line as opaque code, so lazy continuations kept raw brackets and Act III reversed label bodies. Fix: four-space opacity only for code-block context (start / after blank / consecutive code lines); lazy continuations use the existing unresolved-ref escape path. Inventory `owning_act` is `wrapper_rewrite`. |
| `paragraph_block_separators` | green | act2 | n/a | already byte-identical |
| `whitespace_only_blank_boundary` | red | act2 | offset 22422 | Act I detabs `\t\n` to four spaces, so Syntax source `And then define the link:\n\t\n\t[Daring Fireball]: http://daringfireball.net/\n` becomes a spaces-only blank line followed by four-space code. **First-pass** `PASS_LISTS_RAW_AFTER_NEWLINE` treats a leading space as raw continuation (`PASS_LISTS_RAW_GLYPH`), so the blank never becomes `PASS_LISTS_RAW_BLANK` and `PASS_CODE_GATE` never runs; the second-pass PARA scanner cannot mint `CODE_BLOCK`. Fix: design Amendment A17's first-pass `PASS_PARA_WS_*` machine (reuses A16 labels; Step 2c). Minimal witness: `Para:\n    \n    code line\n`. |

Authorized repairs only:

1. **2a nested list:** In `src_ir/act2.py` scene `PASS_LISTS_SIB_OUTDENT`, emit `ITEM_CLOSE` for UL sibling markers on the same path the OL marker path already uses (unify: after `LIST_CLOSE` + depth decrement, always `push(ITEM_CLOSE)` then `PASS_LISTS_ITEM_BEGIN_TIGHT`). Do not add a scene, token, depth register, or kind table. Do not change nest-open, blank-line list-end, or DEEP indent paths in this sub-step unless a focused regression proves they are the same missing-`ITEM_CLOSE` one-liner. Regenerate Act II and reassemble.
2. **2b multi-definition rewrite:** In `scripts/slice3_links.py` `_rewrite_text` only, stop treating every four-space line start as opaque code. Four-space opacity applies only when the line begins a code-block context (document start or immediately after a blank line). Lazy paragraph continuations that start with four spaces must still run the existing unresolved-reference literal escape / resolution logic on their content so `[Yahoo] [2]` becomes `\[Yahoo\] \[2\]` when no ref is registered, matching the first line's Google handling. Do not register six-space definition lines as refs; do not add Act-III scenes; do not change token grammar. Design Amendment A15 (below) records that repairing this already-shipped Slice-3 rewrite path is authorized and is not a new wrapper Markdown branch.
3. **2c whitespace-only blank-line boundary:** In `src_ir/act2.py`, implement design Amendment A17's first-pass `PASS_PARA_WS_*` machine exactly (labels and floors from A16; pairs and terminals from A17): `PASS_LISTS_RAW_AFTER_NEWLINE` gains one new branch on a leading space (after the existing quote-mode and bare-`NEWLINE` → `PASS_LISTS_RAW_BLANK` branches) to `PASS_PARA_WS_OPEN`, then the eight-scene Puck-buffer / Horatio-reverse-replay chain (`PASS_PARA_WS_OPEN` → `PASS_PARA_WS_SCAN` → `PASS_PARA_WS_CONTINUE` / `PASS_PARA_WS_BLANK_DROP` → `PASS_PARA_WS_REVERSE_OPEN` / `PASS_PARA_WS_TERMINATE` → `PASS_PARA_WS_REVERSE_TRANSFER` → `PASS_PARA_WS_REPLAY`) with terminals `PASS_LISTS_RAW_BLANK` (whitespace-only blank → `BLOCK_START` / `CODE_GATE`) and `PASS_LISTS_RAW_GLYPH` (soft-break reverse-replay). `PASS_PARA_WS_SCAN` is the sole further `_read()` owner (Lady Macbeth + Hecate); `PASS_PARA_WS_CONTINUE` is the Hecate + Puck capture half. **Do not** add a `PASS_PARA_NEWLINE` → `PASS_PARA_WS_OPEN` branch or any second-pass Macbeth/`pop` machine under these labels. Install exactly the eight A16 working titles from `[spares.*]` to `[scenes.*]`; the four A16 guard titles stay spares. Do not touch Setext, ATX, code-line, raw-HTML, list-token grammar, span, or renderer routes. Edit the prior A16 PARA-only WIP in place into this shape (preserve red contracts and literary TOML; rewrite IR and pair-chain validator params). Regenerate Act II and reassemble.

Shared Task-4 regression fragment (run after each of 2a, 2b, and 2c):

```bash
uv run pytest tests/test_slice5_documentation_aggregates.py tests/test_architecture_spikes.py tests/test_token_dump.py -q
uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py -q
```

Expected after 2a: nested-list category green; multi-definition and whitespace-boundary may still be red; list/nested spikes and blessed dumps green; no new SPL literary surface. Expected after 2b: nested-list and multi-definition categories green; whitespace-boundary may still be red; spikes and mdtest still green. Expected after 2c: all inventory categories green (focused `syntax_category` fully green), the eight-scene A17 first-pass pair-chain and all-16-spares-absence contracts pass, minimal witness decodes as `PARA`+`CODE_BLOCK` (not two `PARA`s), soft-break control stays one `PARA`, and the full-Basics/full-Syntax raw-byte fixture tests remain green; spikes and mdtest still green.

- [x] **Step 2a: Repair nested list close ordering (Act II).** Authority: Amendment A17. Files: `tests/test_slice5_documentation_aggregates.py` and/or `tests/test_act2_slice4.py` (minimal witnesses), `src_ir/act2.py`; regenerate `src/20-act2-block.spl` and `shakedown.spl`.

  1. Add (or keep) the minimal same-kind witness `* parent\n    * child\n* sibling\n` plus the inventory `SYNTAX_NESTED_LIST_CLOSE` witness with decoded-stream and fast/release/raw-oracle assertions. Optionally assert the positive control `1. parent\n    * child\n2. sibling\n` remains green. Prove red with `uv run pytest tests/test_slice5_documentation_aggregates.py -k 'nested_list' -q` (and any new minimal-witness test).
  2. Implement only the `PASS_LISTS_SIB_OUTDENT` UL/OL unification above. No new label. Regenerate and assemble.
  3. Gate: nested-list category and minimal witness green; `uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py -q` green; Global Constraints SPL-facing gate green; multi-definition may remain red. Commit as `fix: close parent item on list outdent`; push with the required trailers.

  Evidence (2026-07-19): `PASS_LISTS_SIB_OUTDENT` always pushes parent
  `ITEM_CLOSE` after nested `LIST_CLOSE` (UL/OL unified). Focused regression
  on soft-closed shallow nest (`nested_one_level`) required the authorized
  nest-open companion: `PASS_LISTS_NEST_EMIT_{UL,OL}_OPEN` keep the parent
  item open (`TEXT_END` only) so outdent is the sole parent close, matching
  the DEEP nest path. Minimal UL witness + OL control + inventory
  `nested_list_close_ordering` green; multi-definition remains red.
  Architecture spikes + token dumps: `47 passed` (re-blessed
  `nested_one_level.dump`). SPL-facing gate: `223 passed`. mdtest + spikes:
  `54 passed, 1 skipped`. Full `test_act2_slice4.py`: `61 passed`.

- [x] **Step 2b: Repair multi-definition / lazy-continuation reference rewrite.** Authority: Amendment A17 + design Amendment A15. Files: `tests/test_slice5_documentation_aggregates.py` and/or focused rewrite unit tests under `tests/`, `scripts/slice3_links.py`. No IR/SPL change unless a regression forces a one-line companion fix (then re-run the SPL-facing gate).

  1. Add minimal contracts for (a) the inventory multi-definition witness, (b) paragraph continuation `I get … [Google] [1] than from\n    [Yahoo] [2] or [MSN] [3].\n` with empty refs, asserting rewritten form escapes both lines' brackets, and (c) a true code-block control: blank line then four-space content must remain opaque (no false reference rewrite inside code). Prove the multi-definition category red before the rewrite change.
  2. Implement only the `_rewrite_text` four-space context fix above. Update the inventory row's `owning_act` to `wrapper_rewrite`.
  3. Gate: `uv run pytest tests/test_slice5_documentation_aggregates.py -k 'syntax_diff or syntax_category or multi_definition or nested_list' -q` fully green; shared Task-4 regression fragment green; no Act-II ledger growth. Commit as `fix: rewrite lazy continuation reference literals`; push with the required trailers.

  Evidence (2026-07-19): `_rewrite_text` treats four-space lines as opaque only in
  code-block context (document start / after blank / consecutive code lines);
  lazy paragraph continuations still run unresolved-reference escape. Inventory
  `owning_act` for multi-definition is `wrapper_rewrite`. Minimal contracts:
  inventory multi-definition witness, empty-ref lazy continuation escape on both
  lines, and blank-then-four-space code opacity. Focused gate
  `syntax_diff or syntax_category or multi_definition or nested_list` (plus lazy/
  code_block): `8 passed`. Shared Task-4 fragment: slice5+spikes+token dumps
  `69 passed`; mdtest+spikes `54 passed, 1 skipped`. No IR/SPL change.

- [x] **Step 2c: Implement the whitespace-only blank-line boundary (Act II).** Authority: plan Amendment A19 + design Amendment A17 (labels/floors/titles from design A16; first-pass locus and pair ledger from A17). Files: `tests/test_slice5_documentation_aggregates.py` and/or `tests/test_act2_slice4.py` (minimal witnesses), `src_ir/act2.py`, `src/20-act2-literary.toml`; regenerate `src/20-act2-block.spl` and `shakedown.spl`. Preserve existing uncommitted WIP for tests/TOML; rewrite second-pass PARA IR into the A17 first-pass shape rather than discarding contracts.

  1. Keep (or finish seeding) the Task-4 Step-1 inventory fifth `whitespace_only_blank_boundary` category row (owner `act2`). Keep focused contracts for: the exact Syntax witness, the minimal `Para:\n    \n    code line\n` witness (must be `PARA`+`CODE_BLOCK`, not two `PARA`s), the soft-break control `Para:\n    still para\n` (single `PARA`, leading spaces preserved), the ordinary continuation `Para:\nnext line\n`, and optionally the bare-blank control `Para:\n\n    code line\n`. Each contract checks decoded stream shape, fast Act-IV output, release output, and installed-local Markdown.pl bytes. Pair-chain assertions must match design A17's first-pass pairs (Hecate+Puck OPEN, Lady Macbeth+Hecate SCAN `_read`, Hecate+Puck CONTINUE capture, …, Horatio+Lady Macbeth REPLAY → `PASS_LISTS_RAW_GLYPH`); all four A16 guard titles remain absent from `data["scenes"]`. Prove red on the `CODE_BLOCK` witnesses before finishing the IR rewrite if they are not already red.
  2. Implement only design Amendment A17's first-pass `PASS_PARA_WS_*` machine as detailed in the 2c authorized-repair entry above. No second-pass `PASS_PARA_NEWLINE` branch; no token, selector, Act-III/IV role, or non-Act-II file change. Regenerate and assemble.
  3. Gate:

     ```bash
     uv run pytest tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py tests/test_splc_validate.py -k 'para_ws or whitespace_only or Basics or Syntax or validator' -q
     uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
     uv run pytest tests/test_slice5_documentation_aggregates.py tests/test_architecture_spikes.py tests/test_token_dump.py -q
     uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py -q
     ```

     All green; `syntax_category` fully green; no regression in any other category. Commit as `feat: split raw regions on whitespace-only blank lines`; push with the required trailers.

  Evidence (2026-07-19): A17 first-pass `PASS_PARA_WS_*` machine on
  `PASS_LISTS_RAW_AFTER_NEWLINE` (plus failed-setext look-ahead handoff and
  raw-HTML mode skip so Horatio's mode flag is not clobbered). Eight working
  titles promoted; four guards stay spares. Floors use recipe-simple -36/-46.
  Focused gate: `47 passed`. SPL-facing: `233 passed`. Task-4 fragment:
  `76 passed`. mdtest+spikes: `54 passed, 1 skipped`.

  After 2a, 2b, and 2c all land, Step 2 is complete. Do not enable the full Syntax fixture here — that remains Steps 3–4.

- [ ] **Step 3: Run the Syntax four-gate checkpoint.** Run:

  ```bash
  uv run pytest tests/test_slice5_documentation_aggregates.py tests/test_architecture_spikes.py tests/test_token_dump.py -q
  uv run pytest tests/test_mdtest.py -k 'Markdown Documentation - Syntax' -q
  uv run python scripts/strict_parity_harness.py 'Markdown Documentation - Syntax'
  uv run python scripts/differential_smoke.py --require 'Markdown Documentation - Syntax'
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  ```

  Expected: all pass and strict parity reports `summary: 1/1 byte-identical`.

- [ ] **Step 4: Enable and checkpoint.** Add Syntax to `_IMPLEMENTED_FIXTURES`; commit Task-4 files as `feat: complete documentation syntax aggregate`; push with the required trailers.

### Task 5: Prove release completion and register shipment

**Files:** Modify `docs/superpowers/plans/plan-roadmap.md`, `docs/performance/budget.md`, `docs/verification-plan.md`, and only evidence files created by the established measurement procedure.

**Interfaces:** All 23 fixture parameters are enabled. Roadmap row 8 becomes shipped only after the commands below are green and the final commit SHA is known.

- [ ] **Step 1: Run the full correctness and quality gate.**

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  uv run python scripts/strict_parity_harness.py
  uv run python scripts/differential_smoke.py --require 'Markdown Documentation - Basics' --require 'Markdown Documentation - Syntax'
  uv run pytest -q
  uv run ruff check .
  uv run ruff format --check .
  uv run pyright
  ```

  Expected: no skips in `tests/test_mdtest.py`, strict `summary: 23/23 byte-identical`, both required smoke cases byte-identical, and the full suite/tooling green.

- [ ] **Step 2: Record the Slice-5 performance evidence.** Run each command five times, recording first-run and median with date, exact command, fixture, and clean/dirty status in the established performance documents:

  ```bash
  /usr/bin/time -p ./shakedown < "$HOME/mdtest/Markdown.mdtest/Markdown Documentation - Basics.text"
  /usr/bin/time -p ./shakedown < "$HOME/mdtest/Markdown.mdtest/Markdown Documentation - Syntax.text"
  env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -q
  ```

  Expected: no single-large-fixture run exceeds 120 seconds and the full contract does not exceed 15 minutes; otherwise record the performance halt before shipment.

- [ ] **Step 3: Mark shipped and checkpoint.** Change roadmap row 8 to `shipped: 2026-07-18 at commit <final-sha>` only after Steps 1–2. Commit completion evidence and roadmap as `feat: complete documentation aggregates`; push with the exact provenance trailers. Do not stage `scripts/release_entry.py`.

## Plan self-review

Tasks 1–2 close every skipped predecessor fixture with strict evidence; Tasks 3–4 separately gate the two §7.8 aggregates; Task 5 supplies all-fixture, raw-parity, smoke, quality, and release-performance evidence. The plan preserves the accepted architecture and reserves Amendments A11–A13's 40-working/12-spare Act-II ledger; each aggregate defect begins as a minimal general-path test and cannot expand token or literary scope silently. Amendment A17 decomposes Task 4 Step 2 into 2a (Act-II `PASS_LISTS_SIB_OUTDENT` parent `ITEM_CLOSE`) and 2b (existing Slice-3 rewrite lazy-continuation escape), each with a red witness, focused gate, and commit, so one MCO iteration cannot batch both categories or invent Act-III reference machinery.

## Amendment A1 (2026-07-18): Tidyness raw-oracle evidence reconciliation

The accepted Slice-5 design's Amendment A1 is binding for Task 2.  The
focused Tidyness test now uses the installed deterministic oracle as the only
expected output and explicitly proves the checked-in fixture remains the
non-authoritative 133-byte legacy artifact.  Task 2 Step 5 must make the
parameterized mdtest path use the same test-time oracle expected output for
Tidyness before enabling it.  This resolves the former impossible requirement
that one release output equal both distinct byte streams; it does not
authorize a fixture edit, normalizer, production Markdown.pl call, SPL
surface, token, or grammar change.

## Amendment A2 (2026-07-18): Branch-reconciliation disposition

The MCO branch fence reported
`implement-eea93046e11d45dfa60ef5a09b76a921-codex-implement` at
`05ee8f318c6e5af2cd6ab5b8a894cc6e6a7becf2` solely because the terminal
ledger entry was absent.  The branch head is exactly `main` and `origin/main`;
`git merge-base --is-ancestor` succeeds, and both `git log main..branch` and
`git diff --stat main...branch` are empty.  Record it as `integrated` in
`.agent/branch-dispositions.toml`.  This administrative reconciliation does
not change the active Task-3 Step-3 implementation scope, fixture evidence,
SPL literary reservation, or any production behavior.

## Amendment A3 (2026-07-18): Setext carrier bridge

The accepted design's Amendment A2 is binding for Task 3 Step 3. The original
seven labels could not legally perform the required replay: a direct
Hecate-to-Puck-to-Horatio scene would include three participants and fail
`splc` validation. `PASS_SETEXT_REPLAY` is now exclusively the
Hecate/Puck transfer, new working label `PASS_SETEXT_BRIDGE` is exclusively
the Puck/Horatio transfer, and existing `PASS_SETEXT_CLOSE` is exclusively the
Lady Macbeth/Horatio restore. The implementation must use the design's
eight-row pair ledger, preserve all four named spares, and add the new
ready-to-paste TOML entry before its IR scene. The focused Basics four-gate
and the exact SPL-facing compliance command in Global Constraints remain
mandatory before enabling the fixture.

## Amendment A4 (2026-07-18): Source-safe Setext finalization

The A3 eight-label ledger is superseded by design Amendment A3. Hecate is Act
II's unread-source stack, so retaining candidate glyphs there makes `_read()`
consume the candidate again and prevents forward progress. Task 3 Step 3 is
therefore authorized to replace the unused `PASS_SETEXT_EOF` reservation with
`PASS_SETEXT_REQUEUE` and add `PASS_SETEXT_FINALIZE`, for nine working labels
and the unchanged four named spares.

Candidates are retained only on Lady Macbeth above a private candidate floor;
provisional underline bytes are retained only on Horatio above a private
underline floor. A failed underline is restored to Hecate by
`PASS_SETEXT_REQUEUE` without decrementing the source countdown, then the
candidate is sealed through `PASS_SETEXT_FINALIZE`. A proved underline is
discarded, `HEADER(level)` is pushed below the candidate, and it enters that
same finalization route. `PASS_SETEXT_REPLAY` must seed and discard Puck's
private floor, and `PASS_SETEXT_BRIDGE`/`PASS_SETEXT_CLOSE` must likewise seed
and discard Horatio's restore floor. No private floor may reach the emitted
stream. No token, selector, Act-III/IV role, compiler behavior, fixture
branch, raw-HTML scope, or additional literary spare is authorized. Any need
beyond this nine-label ledger remains `- BLOCK[plan]:` with the minimal
witness.

## Amendment A5 (2026-07-18): one-time Setext candidate floor

The accepted design's Amendment A4 is binding for Task 3 Step 3 and supersedes
the nine-label authorization above.  The minimal Setext witness
`Markdown: Basics\n================\n` exposed that `PASS_SETEXT_CANDIDATE`
cannot both seed Lady Macbeth's private floor once and scan an unbounded title
line: every IR self-loop re-enters the whole scene and would reseed the floor.

Task 3 Step 3 is therefore authorized to add the design-reserved
`PASS_SETEXT_CANDIDATE_SCAN` surface and IR scene, for ten working labels and
the unchanged four unused spares.  `PASS_SETEXT_CANDIDATE` owns only the
one-time floor seed and immediately enters the scan scene.  The scan scene is
the sole candidate self-loop and sole candidate `_read()` owner; it retains
title glyphs above the already-seeded floor, enters underline classification
only after the first newline, and enters raw finalization at EOF.  The rest of
the A3 floor/requeue/finalization/restore ledger is unchanged.  The precise
state table, ready-to-paste TOML entry, and the required SPL-facing compliance
command are in design Amendment A4.  No other label, spare draw, token,
selector, participant, Act-III/IV role, compiler behavior, fixture branch,
raw-HTML scope, or header behavior is authorized.

## Amendment A6 (2026-07-18): seeded Setext transfer-loop ledger

Design Amendment A5 supersedes the ten-label A4 ledger for Task 3 Step 3.
Its binding observation is that splc self-loops re-enter an entire scene, not
only a selected transfer statement. The candidate split therefore was
necessary but insufficient: `PASS_SETEXT_UNDERLINE`, `PASS_SETEXT_FINALIZE`,
`PASS_SETEXT_REPLAY`, and `PASS_SETEXT_BRIDGE` each also paired a one-time
floor seed with an unbounded scan or transfer.

Task 3 Step 3 must replace the prior reservation with Amendment A5's complete
fourteen-working/four-spare TOML block. The four former named spares become
`PASS_SETEXT_UNDERLINE_SCAN`, `PASS_SETEXT_FINALIZE_TRANSFER`,
`PASS_SETEXT_REPLAY_TRANSFER`, and `PASS_SETEXT_BRIDGE_TRANSFER`; the design
reserves four fresh named spares. Each seed scene immediately enters its loop
scene, and only that loop self-loops. `PASS_SETEXT_REQUEUE` and
`PASS_SETEXT_CLOSE` retain their existing floor-consuming loops and do not
seed a floor themselves. This is the complete derived ledger: 14 working
labels, 4 unused spares, satisfying `ceil(14 * 20%)` and the mandatory
four-spare floor.

No token, selector, participant pair, Act-III/IV role, compiler behavior,
fixture branch, raw-HTML scope, or header behavior is authorized. The exact
SPL-facing compliance command in Global Constraints remains mandatory before
the fixture can be enabled.

## Amendment A7 (2026-07-18): primed-glyph capture and proved close

Design Amendment A7 supersedes the fourteen-label A5 ledger for Task 3 Step
3.  It closes the planner-only Setext return blocker without implementing the
path: the Setext entry receives the first non-special glyph already held by
Hecate, so `PASS_SETEXT_CANDIDATE` must seed Lady Macbeth's candidate floor
and retain that primed glyph before the scan scene calls `_read()`.  The old
seed-only wording would lose the first `M` in `Markdown: Basics`. Candidate
EOF uses the expressly reserved Hecate/Horatio mode setter, rather than an
illegal third participant in the candidate scan.

The amendment also derives legal raw and proved closes.  Once its underline
floor has been discarded, Horatio carries private mode `0`, `1`, or `2` until
the existing replay pair reads it before Horatio is staged again.  It chooses
the corresponding Puck replay floor; the bridge observes that floor only
after title transfer. Raw text enters the existing `PASS_SETEXT_CLOSE`; the
two proved routes enter `PASS_SETEXT_EQUALS_CLOSE` or
`PASS_SETEXT_DASH_CLOSE`, push `HEADER(1)` or `HEADER(2)` below restored title
glyphs, and then make the explicitly authorized `goto("PASS_HEADER_CLOSE")`.
The existing header close appends `TEXT_END` and takes its existing countdown
branch to dispatch. Its Lady-Macbeth/Hecate stage pair is validator-compatible
with each proved close's Lady-Macbeth/Horatio pair because Lady Macbeth is
shared, and it does not consume Hecate.

Task 3 Step 3 must install design A7's ready-to-paste level-specific replay,
close, EOF-mode, and replacement-spare TOML entries with its nineteen
working/four-spare block.  This adds only one local close-mode register, three
private Puck floor values, and the five named working scenes; it does not
authorize a token, selector, other participant pair, compiler/validator
change, fixture branch, raw-HTML change, or Act-III/IV behavior.  The exact
Global Constraints SPL-facing gate and A7's focused Setext gate are mandatory
before the Basics four-gate checkpoint.

## Amendment A8 (2026-07-18): validator-safe underline read/capture split

Design Amendment A8 supersedes A7 only for the underline scanner.  The A7
wording assigned `_read()` and Horatio retention to
`PASS_SETEXT_UNDERLINE_SCAN`; because `_read()` targets Hecate and Lady
Macbeth, its glyph push to Horatio would be an illegal three-character scene.
Task 3 Step 3 instead adds the design-reserved
`PASS_SETEXT_UNDERLINE_CAPTURE` TOML/IR surface.  The unchanged scan is a
Lady-Macbeth/Hecate one-glyph read scene, and the new Hecate/Horatio capture
scene pushes and classifies that glyph above Horatio's existing underline
floor.  They alternate for each underline byte, with EOF handled by the read
scene and proof/requeue selected by the capture scene.

The pool is twenty working labels and four unused spares; no spare is drawn.
Before production code, the implementation adds a focused fast-IR contract
that accepts the exact two-scene pair and retains the existing validator
rejection of a three-target scene.  It then proves the minimal Setext witness
red, implements only this split, regenerates and assembles, and runs the
exact Global Constraints SPL-facing gate plus the focused A8 command in the
design before the existing Basics four-gate checkpoint.  No other scope is
authorized.

## Amendment A9 (2026-07-18): state rail, proof handoff, and restored spare pool

Design Amendment A9 supersedes A8 for Task 3 Step 3's complete Setext
underline family. Install A9's five working TOML entries and complete
five-title spare block before editing `src_ir/act2.py`. The binding pool is 25
working labels plus five unused spares; the former guard entries are spares
again, not implementation labels. Do not generate a Scene for
`PASS_SETEXT_RETURN_GUARD`, `PASS_SETEXT_LEVEL_GUARD`,
`PASS_SETEXT_REPLAY_GUARD`, `PASS_SETEXT_DISPATCH_GUARD`, or
`PASS_SETEXT_ATX_GUARD`.

Use A9's Macbeth rail only during underline classification, retain Horatio as
the byte replay buffer, and leave Puck untouched so the existing ATX route
remains intact. Follow its read/capture/classify choreography and proof/raw
handoffs. No path may enter a transfer loop before its named seed scene.

Before production code, add A9's pair-chain validation, spare-label absence,
and minimal-witness no-underflow fast-IR contracts. Then run its exact focused
command, regeneration/assembly, and the Global Constraints SPL-facing gate
before the existing Basics four-gate checkpoint. No behavior outside A9's
state table is authorized.

## Amendment A10 (2026-07-18): binding Setext ledger selection

This amendment clears the Task-3-Step-3 planner-only handoff contradiction.
Design Amendment A9, not Amendment A8, is the sole binding Setext ledger for
all remaining Task 3 work.  A8 is retained only as historical rationale for
the legal read/capture split; its twenty-working/four-spare pool, Horatio
state mutation, guard-label control flow, and any transfer-loop entry before
its named seed are expressly unauthorized.

The implementation must replace the current A8-shaped WIP with A9's
25-working/five-unused-spare ledger, reserve its ready-to-paste controlled
surfaces before IR edits, and satisfy A9's pair-chain, spare-absence, and
minimal-witness no-underflow contracts.  The exact pre-checkpoint command is:

```bash
uv run pytest tests/test_splc_validate.py tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py -k 'setext or underline or validator or Basics' -q
uv run python -m scripts.splc && uv run python scripts/assemble.py
```

No production behavior is changed by this planning amendment.  Any need to
depart from A9's state table or its reserved pool remains `- BLOCK[plan]:`
with the smallest witness.

## Amendment A11 (2026-07-18): validator-legal close and suffix choreography

Design Amendment A11 clears the Task-3-Step-3 planner-only blocker.  It
supersedes A10's 25-working/five-spare ceiling only by adding the exact eight
controlled scenes and three spare titles in the accepted design, for a
33-working/eight-unused-spare ledger.  The Setext proved route ends in the
new two-participant `PASS_SETEXT_PROVED_CLOSE`, which branches on the existing
input countdown before any dispatcher read.  The ATX route gets the exact
two-participant Puck trailing-buffer machine; its only reader remains Lady
Macbeth/Hecate.  This preserves A9's Macbeth state rail, Horatio replay-only
role, no-third-character validation rule, token grammar, and Act-III/IV
boundary.

Before changing production behavior, add the design's no-underflow/no-extra-
read, positive-count source-preservation, pair-chain, eight-spare-absence,
and three ATX suffix contracts, retaining the three-character rejection test.
Run both exact A11 commands in the design, then the Global Constraints SPL-
facing gate before the existing Basics four-gate checkpoint.  Any need beyond
the A11 table remains `- BLOCK[plan]:` with the smallest witness.

## Amendment A12 (2026-07-18): preserve the countdown through Setext transfer

Design Amendment A12 clears the remaining Task-3-Step-3 planner-only blocker
without expanding the A11 ledger. Its binding private-slot sequence saves Lady
Macbeth's live input countdown below the existing Hecate finalized-title floor
before finalization pops title bytes, moves that one slot into Puck's value
after replay reaches the floor, seeds it below Horatio's existing restore
floor before bridge transfer, and restores it to Lady Macbeth after title
restoration. This is not another mode or floor: it is one value slot carried
by existing two-participant scenes. The ledger remains 33 working labels and
eight unused spares; no TOML, scene, token, selector, participant,
compiler/validator, or Act-III/IV change is authorized.

Before behavior changes, add an observable A12 transfer contract for both the
terminal minimal witness and the same witness followed by `After.\n`: the
terminal path restores zero and reaches `PASS_LISTS_DONE` without a later
block-start read, while the positive path restores the remaining count and
consumes `A` once. Retain A11's exact pair-chain, spare-absence,
three-character rejection, and suffix contracts; run A11's two focused
commands and the Global Constraints SPL-facing gate before the existing Basics
checkpoint. Any need for a second slot, new mode, or new scene is
`- BLOCK[plan]:` with the smallest witness.

## Amendment A13 (2026-07-18): normalize blank indented-code payload lines

Design Amendment A13 clears the current Task-3-Step-3 planner-only blocker.
The remaining Basics witness is the general indented-code payload
`    <blockquote>\n        <p>One.</p>\n        \n        <p>Two.</p>\n    </blockquote>\n`:
after mandatory-indent removal, Markdown.pl emits its spaces-only physical
line as `"\n"`, while the current `CODE_BLOCK` leaf preserves `"    \n"`.
The amendment is Act-II-only and preserves the existing `CODE_BLOCK` token
grammar and Acts III/IV opaque-copy/render paths.

Before editing `src_ir/act2.py`, install A13's exact seven working and four
unused-spare TOML entries. Add the exact witness plus four-space-only,
eight-space-only, and trailing-spaces-on-a-nonblank-line contracts: each must
check decoded payload, fast output, release output, and raw installed-local
Markdown.pl bytes. Preserve the existing Code Blocks and Tabs fixture payload
contracts; add the A13 seven-scene pair-chain and all-12-spares absence
assertions. Implement only A13's one-line Puck buffer / Horatio
reverse-replay choreography, with Hecate/Lady Macbeth as the sole reader;
then regenerate and assemble. Do not modify the existing Setext, ATX,
raw-HTML, list, token, span, or renderer routes.

Run the two exact A13 commands in the design, then the Global Constraints
SPL-facing gate and the existing Basics four-gate checkpoint. The expected
strict result remains `summary: 1/1 byte-identical`. A need beyond A13's
seven scenes, one private `saw_nonblank` value, 40-working/12-spare ledger,
or Act-II-only scope is `- BLOCK[plan]:` with the smallest witness.

## Amendment A14 (2026-07-18): Step 3 is both Setext/ATX and code-line, and the WIP regression is a debugging substep

This amendment clears the generic Task-3-Step-3 planner-only blocker ("Need
to understand the active plan and roadmap before implementing Step 3"). That
blocker names no architecture question, so it is not a genuine halt: Step 3's
own checklist text only describes the A9/A11/A12 Setext-and-ATX machine and
never restates A13's separately-amended indented-code-payload requirement.
Both are binding for Step 3 completion; A13 does not replace or supersede the
Setext/ATX work, it is the checklist's missing second half. A future executor
must not re-derive this from the amendment stack alone: the checklist text
above is authoritative only together with A9, A11, A12, and A13 combined, and
no further consolidation amendment is needed to read it that way.

The working tree at this amendment's handoff already carries uncommitted
Task-3 Step-3 progress: `src_ir/act2.py`, `tests/test_act2_slice4.py`,
`tests/test_splc_validate.py`, `src/literary.toml`, and
`src/20-act2-literary.toml` implement and test the A9/A11/A12 Setext/ATX
machine (the `PASS_SETEXT_*`, `PASS_HEADER_TRAIL_*` pair-chain and spare-
absence tests pass), and separately declare A13's three private constants
(`_CODE_LINE_FLOOR`, `_CODE_LINE_REPLAY_FLOOR`, `_CODE_LINE_NONBLANK`) without
yet adding A13's seven working scenes or any code-line contract. This is
preserved, uncommitted, in-progress work, not a finished checkpoint: it must
not be discarded.

`uv run pytest tests/test_act2_slice4.py tests/test_splc_validate.py -q` at
this handoff reports `51 failed, 26 passed`, and the failures are not
confined to Setext/ATX/code-line — they include pre-existing full-list,
top-level ATX, and nested-quote contracts from earlier shipped slices. Before
any A13 scene is added, the next Step-3 session must treat driving this
count to zero as the first Step-3 substep, using `superpowers:systematic-
debugging` against the uncommitted `src_ir/act2.py` diff (`git diff
src_ir/act2.py`) to find what the A9/A11/A12 changes disturbed in shared
scenes or dispatch, rather than layering A13's scenes on top of a red
baseline. No new token, selector, participant, or scene beyond the already-
authorized A9/A11/A12/A13 ledgers is authorized to fix the regression; if the
regression's root cause requires one, record `- BLOCK[plan]:` with the
minimal failing witness and stop.

`.agent/blockers.md`'s generic entry is cleared by this amendment. It is not
a substitute for a real blocker: if the regression search in fact surfaces an
architecture question, record a fresh, specific `- BLOCK[plan]:` line rather
than reinstating the generic one.

## Amendment A15 (2026-07-19): spare TOML entries move to `[spares.*]`

This amendment clears the outstanding `- BLOCK[plan]:` recorded against Task
3 Step 3: the accepted design's ready-to-paste spare blocks for A9 (five
labels), A11 (eight labels), and A13 (four labels) each write
`[scenes.LABEL]`, but `scripts/literary_surfaces.load_literary_surfaces`
merges every such entry into one `data["scenes"]` table, and
`tests/test_literary_compliance.py`'s `test_scene_titles_have_toml_entries_and_match_source`
and `test_scene_ledger_matches_source_scene_labels` both require
`set(source_scene_labels) == set(data["scenes"])`. A spare label has no IR
`Scene`, so any `[scenes.LABEL]` spare entry fails both tests — verified
empirically by appending one such entry and observing both failures, then
reverting cleanly.

Design Amendment A14 is now binding for all of Task 3 Step 3: every spare
title in the accepted design (17 across A9/A11/A13, converging on the
40-working/12-spare ledger) is installed as `[spares.LABEL]`, not
`[scenes.LABEL]`, with the same `title`/`pattern` keys. This is a TOML-shape
correction only — it authorizes no new label, token, selector, participant,
compiler/validator change, or Act-III/IV behavior, and it does not change
which titles are spares versus working labels. Step 3 must install every
spare under `[spares.*]` from the start (not `[scenes.*]` followed by a
later move), run `uv run pytest tests/test_literary_compliance.py
tests/test_literary_toml_schema.py -q` after each amendment's spare block is
added, and keep the existing eight-/twelve-spare absence-from-`data["scenes"]`
IR contracts required by A9/A11/A13 — those contracts remain meaningful
because `[spares.*]` entries never appear in `data["scenes"]`.

Both `- BLOCK[plan]:` lines in `.agent/blockers.md` are cleared by this
amendment: the TOML-shape contradiction is resolved, and the separable
Setext/ATX/code-line IR reconstruction described by Amendment A14 (plan) may
now proceed using this corrected TOML shape from the start. Any need beyond
this shape correction remains `- BLOCK[plan]:` with the smallest witness.

## Amendment A16 (2026-07-19): loop-sized Step 3 decomposition and baseline record

This is an execution-granularity amendment only. It decomposes Task 3 Step 3
into Steps 3a–3d (code-line normalization, ATX trailing-hash machine,
raw-HTML admission, Setext rail + proved close + countdown slot), each a
single loop iteration with its own red set, focused gate, regression guard,
conventional commit, and push. The former Step 3 checkbox text is retained
verbatim as the "combined requirements" paragraph and remains binding for all
four sub-steps together with A9, A11, A12, A13, A14, and A15; this amendment
authorizes no new label, title, token, selector, participant,
compiler/validator change, or Act-III/IV behavior, and reserves no literary
surface. Sub-step order is binding: 3a and 3b and 3c isolate the independent
machines first so progress is banked before 3d's Setext core; the full-Basics
fixture test is expected to stay red until 3d completes.

Baseline record at commit f459965 (2026-07-19): despite that commit's
`feat: complete Slice-5 documentation aggregates and Act II lowering`
subject, it lowered no Act-II scene — it installed the literary TOML ledger,
prose phrases, and witness/validator tests only. Task 3 Step 3 remains
unimplemented; the plan checkboxes and the failing tests, not that commit
subject, are authoritative. The verified baseline is `uv run pytest
tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py
tests/test_splc_validate.py -q` reporting 23 failed / 68 passed, with every
failure owned by Steps 3b–3d.

Disposition of A14's preserved WIP: the uncommitted `src_ir/act2.py` work
A14 required preserving was stashed as `stash@{0}` (`WIP on main: 552bed0`,
2026-07-18) after its durable parts (tests, TOML, prose phrases) were
committed at e7b29bd/f459965. A14's drive-the-regression-to-zero substep is
resolved: the committed tree carries none of the disturbed scenes, and its
default suite is green apart from the Step-3 red witnesses recorded below. The stash is read-only
reference for Step 3d and must never be popped or applied.

`scripts/release_entry.py` no longer exists: the operator deliberately
deleted it as orphaned, superseding the Global Constraints line that asked to
preserve it. Do not recreate or stage it; Task 5 Step 3's warning against
staging it stands.

Reconciliation of f459965's two regressions (repaired 2026-07-19, this
amendment's commit lineage): (1) that commit removed `ProseEngine`'s
rejection of unpooled negative values and hardcoded a `_NEG_SPECIAL_PHRASES`
table in `scripts/splc/prose.py`, breaking
`test_value_phrase_rejects_unpooled_negative`; the guard is restored and the
table removed. Negative replay floors are IR-local constants, never prose
(design §A5 region); if an implementation genuinely needs a negative value
atom, it is a planning-time TOML `stable_utility` entry and a `- BLOCK[plan]:`
until one is authorized — never a Python literal. (2) That commit installed
58 unbuilt `PASS_SETEXT_*`/`PASS_HEADER_TRAIL_*` titles as `[scenes.*]`,
breaking both scene-ledger equality tests. All 58 are re-housed under
`[spares.*]` unchanged. The binding TOML discipline for Steps 3a–3d is
promote-on-implement: a title moves from `[spares.*]` to `[scenes.*]` only in
the sub-step that builds its Scene, so `set(data["scenes"])` equals the
generated source's scene labels at every commit boundary. The parked set
includes superseded A8-shaped titles; they are permanently spares, and
promoting or building any title not named by A9/A11/A13 (plus the retained
pre-A9 family) is `- BLOCK[plan]:` with the smallest witness.

Verified baseline after this reconciliation: the focused three-file command
reports 23 failed / 68 passed (unchanged red witnesses), and the Global
Constraints SPL-facing gate plus `tests/test_splc_prose.py` report only the
eight A11 entry-pair validator params red — every other default-suite test
passes.

## Amendment A17 (2026-07-19): Task 4 Step 2 category repairs

This amendment is the binding completion shape for Task 4 Step 2. It does not
authorize new Act-II labels, tokens, selectors, participants, or Act-III/IV
roles. It freezes the Step-1 inventory's two red categories into ordered
sub-steps 2a–2b with re-verified root causes at commit `53d5970`.

**2a — `nested_list_close_ordering` (Act II only).**
`PASS_LISTS_SIB_OUTDENT` already emits `ITEM_CLOSE` when the sibling marker is
ordered; when the marker is unordered (`*`, `+`, or `-`) it skips that push and
opens the next item immediately after nested `LIST_CLOSE`. Oracle HTML requires
`</ul></li>` (or `</ol></li>`) before the next sibling `<li>`. Unify the UL path
with the existing OL path: always push `ITEM_CLOSE` after closing the nested
list and decrementing depth, then enter `PASS_LISTS_ITEM_BEGIN_TIGHT`. The
minimal witness is `* parent\n    * child\n* sibling\n`. Retain Spike A
`nested_one_level` and all architecture-spike list dumps as regressions. No
TOML surface is reserved or promoted.

**2b — `multi_definition_reference_resolution` (existing Slice-3 rewrite only).**
Release and fast paths both run `rewrite_task3_markdown` before the IR. For the
Syntax multi-definition witness, reference definitions are six-space indented
code and correctly contribute zero refs. The rewrite escapes the first-line
unresolved form to `\[Google\] \[1\]` but `_rewrite_text`'s four-space line
short-circuit copies the lazy continuation line `    [Yahoo] [2] or [MSN] [3].`
verbatim. Act III then mangles the raw brackets into reversed label bodies.
Repair only the four-space short-circuit so it applies to true code-block
context (start of input or after a blank line), not to lazy paragraph
continuations. Lazy continuations must use the existing unresolved-reference
escape path. This is a bug fix to the already-shipped Slice-3 rewrite, not a
new wrapper Markdown branch; design Amendment A15 records that authorization.
Do not invent general multi-id Act-III reference machinery in this step.

Sub-step order is binding: bank the Act-II list fix in 2a before the rewrite
fix in 2b. After both sub-steps, all four `syntax_category` rows are green and
Step 2 may be checked off; full Syntax enablement remains Steps 3–4. Any need
for a new label, token, or Act-III scene remains `- BLOCK[plan]:` with the
smallest witness.

## Amendment A18 (2026-07-19): Task 4 Step 2c and the whitespace-boundary category

Amendment A17 closed Step 2 on the two categories the Step-1 inventory
originally seeded. After 2a and 2b landed (commits `933aa9e`, `8fecbce`), the
Task 4 Step 3 four-gate checkpoint recorded a new first-byte mismatch at
offset 22422, which `- BLOCK[plan]:` correctly flagged (commit `8a8bc2b`) as
outside A17's authorization: Act II treats a whitespace-only line as a
paragraph continuation instead of a blank-line boundary, so the oracle's
`PARA` + `CODE_BLOCK` split at a detabbed `\t\n` never happens. This is not a
regression in 2a or 2b's work — the Step-1 inventory simply never observed
this category because tab detabbing only exposes it inside the full Syntax
document, not in the four originally seeded witnesses.

Design Amendment A16 (`docs/superpowers/specs/2026-07-18-slice-5-documentation-aggregates-design.md`)
is the accepted design for this category: an 8-working/4-spare Act-II
`PASS_PARA_WS_*` extension, confined to Macbeth's own paragraph-scan stack
(no `_read()`/Hecate), reusing `PASS_PARA_CLOSE_BLANK`/`PASS_PARA_FINAL_CLOSE`
as terminal targets. This amendment:

1. Adds `whitespace_only_blank_boundary` as the fifth Task-4 Step-1 inventory
   category (owner `act2`), seeded directly in the root-cause table rather
   than requiring a separate Step-1 re-run, since the root cause and minimal
   witness are already fully characterized by the blocker record.
2. Authorizes Step 2c, ordered after 2a and 2b (both already shipped), as the
   binding completion shape for this category: install design A16's exact
   eight working titles and four spare titles, implement only the
   `PASS_PARA_WS_*` machine, and re-run the Task-4 regression fragment plus
   the Global Constraints SPL-facing gate before returning to Step 3.
3. Extends the Global Constraints Act-II ledger from A11–A13's 40
   working/12 spare to 48 working/16 spare, exclusively for Step 2c's draw
   from design A16's pool — no other step or category may use it.
4. Leaves Step 3 (the Syntax four-gate checkpoint) and Step 4 unchanged in
   shape; they simply now run after three sub-steps instead of two.

Any need for a ninth Act-II label beyond A16's eight, a second private floor
pair, a token/role change, tab-specific handling in Act II (Act I already
detabs before Act II ever sees this span), or Act III/IV behavior remains
`- BLOCK[plan]:` with the smallest witness.

## Amendment A19 (2026-07-19): first-pass locus for Step 2c (clears A16 PARA blocker)

Amendment A18 authorized Step 2c under design A16's second-pass paragraph
scanner. An implementation WIP that followed A16 exactly (Macbeth/`pop`,
terminals `PASS_PARA_CLOSE_BLANK` / `PASS_PARA_FINAL_CLOSE`) met the soft
"close paragraph on spaces-only line" behaviour for `Para:\n    \n` but
**failed the Step 2c evidence gate** on the binding witness
`Para:\n    \n    code line\n`: decoded stream stayed
`[PARA, PARA]` and HTML stayed two paragraphs; the oracle requires
`[PARA, CODE_BLOCK]` and `<pre><code>…`. That is not an incomplete
implementation of A16 — A16's locus cannot emit `CODE_BLOCK` by construction.

Design Amendment A17 is the accepted correction:

1. Root cause is first-pass `PASS_LISTS_RAW_AFTER_NEWLINE` treating leading
   space as raw continuation, so `PASS_LISTS_RAW_BLANK` → `BLOCK_START` →
   `CODE_GATE` never runs for spaces-only blanks.
2. Binding fix reuses A16's exact eight working labels and four spare titles
   (ledger stays 48 working / 16 spare) but rebinds every scene to the
   first-pass Hecate/`_read()` pair ledger in design A17; terminals are
   `PASS_LISTS_RAW_BLANK` and `PASS_LISTS_RAW_GLYPH`.
3. Second-pass `PASS_PARA_NEWLINE` → `PASS_PARA_WS_*` is not authorized.
4. Prior uncommitted A16 PARA WIP is preserved as starting material: keep
   tests and literary TOML, rewrite IR and validator pair-chain params in
   place to A17.

This amendment updates Global Constraints, the Step 2 combined-requirements
paragraph, the root-cause table row, authorized repair (3), Expected-after-2c,
and Step 2c itself. It does **not** create a second in-flight plan, change
roadmap row 8, authorize new labels beyond A16's pool, or enable the full
Syntax fixture (still Steps 3–4). The former `- BLOCK[plan]:` for Step 2c is
cleared by this amendment plus design A17.

Literary compliance for the Step 2c implementation remains the Global
Constraints SPL-facing gate:

```bash
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
```

Any need for a ninth working label, a second floor pair, a token/role change,
or Act III/IV behaviour remains `- BLOCK[plan]:` with the smallest witness.
