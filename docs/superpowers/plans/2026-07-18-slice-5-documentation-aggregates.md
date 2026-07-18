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
- New Act-II labels are limited to the design's eight working Setext labels, including Amendment A2's `PASS_SETEXT_BRIDGE`. The four named spares may be used only by a design amendment; another surface, token, role, participant, or Act-III/IV capability is `- BLOCK[plan]:` with the minimal witness.
- Every SPL change runs: `uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q`.

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

**Files:** Modify `src_ir/act2.py`, `src/20-act2-literary.toml`, `tests/test_act2_slice4.py`, `tests/test_slice5_documentation_aggregates.py`, `tests/test_mdtest.py`; regenerate `src/20-act2-block.spl` and `shakedown.spl`.

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

- [ ] **Step 3: Implement the general block paths.** Add the design's eight Setext TOML entries before matching Act-II labels and implement only Amendment A2's candidate/underline/replay state table. Its only legal carrier chain is `Hecate/Lady Macbeth -> Hecate/Puck -> Puck/Horatio -> Lady Macbeth/Horatio`; `PASS_SETEXT_REPLAY` is the Hecate-to-Puck transfer, the newly reserved `PASS_SETEXT_BRIDGE` is the Puck-to-Horatio transfer, and `PASS_SETEXT_CLOSE` returns Horatio's glyphs to Lady Macbeth. No scene may touch Hecate, Puck, and Horatio together. Extend the existing generic raw-HTML admission to accept the aggregate's top-level `ul` block without altering span HTML. Strip only whitespace-separated ATX closing hashes in the existing header close path. Regenerate and assemble.

- [ ] **Step 4: Run the Basics four-gate checkpoint.** Run:

  ```bash
  uv run pytest tests/test_act2_slice4.py tests/test_slice5_documentation_aggregates.py tests/test_architecture_spikes.py tests/test_token_dump.py -q
  uv run pytest tests/test_mdtest.py -k 'Markdown Documentation - Basics' -q
  uv run python scripts/strict_parity_harness.py 'Markdown Documentation - Basics'
  uv run python scripts/differential_smoke.py --require 'Markdown Documentation - Basics'
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  ```

  Expected: all pass and the strict harness reports `summary: 1/1 byte-identical`.

- [ ] **Step 5: Enable and checkpoint.** Add Basics to `_IMPLEMENTED_FIXTURES`; commit Task-3 files as `feat: complete documentation basics aggregate`; push with the required trailers.

### Task 4: Make Markdown Documentation — Syntax a strict aggregate gate

**Files:** Modify only files implicated by a red minimal Syntax witness among `src_ir/act1.py`, `src_ir/act2.py`, `src_ir/act3.py`, `src_ir/act4.py`, their matching literary TOML file, and `tests/test_slice5_documentation_aggregates.py`; modify `tests/test_mdtest.py`; regenerate affected fragments and `shakedown.spl`.

**Interfaces:** Every repair consumes/emits the existing stream grammar. The test inventory records `(category, source witness, first differing byte, owning act)` so a later failure cannot silently become a fixture-specific patch.

- [ ] **Step 1: Turn the Syntax diff into a finite category inventory.** Add a helper test that compares real release bytes with the local oracle and records the first difference plus the minimal contiguous source witness. Seed it with the observed categories: raw top-level HTML (`h2`/`h3` with attributes), nested list close ordering, multi-definition reference resolution, and paragraph/block separators. Require each category to have a fast-IR, release, and strict oracle assertion before changing production behavior.

- [ ] **Step 2: Repair one evidenced category at a time.** For each red category, write its minimal test, prove it red, modify the owning existing IR route, regenerate, and run the Task-4 gate below before beginning another category. Do not add a label beyond Task 3's eight working labels or change token grammar. If one category needs either, record `- BLOCK[plan]:` with the witness and stop.

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

Tasks 1–2 close every skipped predecessor fixture with strict evidence; Tasks 3–4 separately gate the two §7.8 aggregates; Task 5 supplies all-fixture, raw-parity, smoke, quality, and release-performance evidence. The plan preserves the accepted architecture and only reserves Amendment A2's derived eight-scene Act-II Setext pool plus four spares; each aggregate defect begins as a minimal general-path test and cannot expand token or literary scope silently.

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
