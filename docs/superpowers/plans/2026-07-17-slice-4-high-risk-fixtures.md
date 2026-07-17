# Slice 4 High-Risk Fixtures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `Inline HTML (Advanced)`, `Nested blockquotes`, and `Ordered and unordered lists` with strict Markdown.pl bytes while preserving all shipped fixtures and Spike A/B contracts.

**Architecture:** Follow the [accepted Slice-4 design](../specs/2026-07-17-slice-4-high-risk-design.md), including Amendments A2–A5, architecture §7.7/§7.8a/§8.1, and the four-act IR pipeline. Act II produces the balanced container grammar plus A2's existing allocated `HEADER(level, text)` leaf, A4's final-blank transaction with its separate accepted nested-after-blank selector, and A5's tally/read split for tab-depth classification; Act III preserves structural/raw leaves, and Act IV renders those frames and headers; no parser, token number, structural role, or participant is added.

**Tech Stack:** Python 3.13, typed splc IR, generated Shakespeare SPL, TOML-controlled literary surfaces, pytest, local Markdown.pl 1.0.2b8 strict oracle.

## Global Constraints

- This is the sole in-flight plan.  Preserve the untracked `scripts/release_entry.py`; it is user work and must never be staged by this plan.
- Before any SPL-facing change read `docs/superpowers/notes/spl-literary-protocol.md`, `docs/superpowers/notes/correctness-first-spl-workflow.md`, `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`, `docs/spl/codegen-style-guide.md`, `src/literary.toml`, `docs/markdown/html-block-boundaries.md`, and `docs/markdown/list-mechanics.md`.
- Edit generated acts only through `src_ir/*.py`; run `uv run python -m scripts.splc` then `uv run python scripts/assemble.py`.  Never hand-edit `src/*.spl` generated fragments or `shakedown.spl`.
- Enable a fixture in `tests/test_mdtest.py` only in its green checkpoint.  Never change expected fixture files or invoke Markdown.pl at runtime.
- For `Nested blockquotes`, the strict-byte authority is the installed
  `~/markdown/Markdown.pl` 1.0.2b8 executable, as fixed by Slice-4 design
  Amendment A1.  The checked-in fixture remains the normalized-mdtest corpus;
  its Markdown-1.0.1 indentation is not a second raw-byte acceptance target.
- Amendment A2 authorizes only `HEADER = 2`'s new `TokenArity(1, True)` row and bounded top-level ATX path as a prerequisite of Task 4 Step 2. A needed token, third participant, structural-role change, broader header syntax/container handling, unreserved surface, or any other fixture requirement outside the accepted design is `- BLOCK[plan]: ...` in `.agent/blockers.md` followed by a clean stop.
- Amendment A4 supersedes A3's five-label limit with exactly six Act-II provisional-looseness labels.  It preserves the existing list token grammar and Act-IV renderer: stage a final blank provisionally; commit an ordinary continuation/sibling through `PASS_LISTS_LOOSE_COMMIT`; route an accepted nested marker through `PASS_LISTS_LOOSE_NESTED`; and restore tightness plus staged glyph order at EOF/list termination.
- Amendment A5 consumes A4's four guards and authorizes exactly `PASS_LISTS_INDENT_TAB_READ` plus five unused Act-II `PASS_LISTS_INDENT_*_GUARD` spares.  The existing tab entry updates the indentation tally, the read helper owns `_read()`, and the first non-tab glyph is classified before marker staging can overwrite `PUCK`; equal indentation is a sibling route and deeper indentation is a nested-open route.  A need for another helper, a sixth spare, a different register ownership, or any Act-III/IV/token/grammar change is `- BLOCK[plan]: ...` followed by a clean stop.
- Every SPL/TOML checkpoint runs the exact generated/literary gate and the Amps proof named in the design.  Every checkpoint commit contains the configured provenance trailers and is pushed; a failed push records one blocker and stops.

```bash
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

## File map

| Path | Responsibility |
|---|---|
| `src_ir/act2.py`, `src/20-act2-literary.toml` | HTML block recognition, quote-depth scheduling, full-list recognition, and A2's bounded top-level ATX-header emission; generated Act II only. |
| `src_ir/act3.py` | Preserve structural and raw HTML leaves; traverse A2's declared `HEADER(level, text)` arity without rewriting it. |
| `src_ir/act4.py`, `src/40-act4-literary.toml` | Raw-block separators, nested quote rendering, full-list frame rendering, and A2's header rendering; generated Act IV only. |
| `src_ir/tokens.py`, `docs/spl/token-codes.md` | A2's matching existing-code `HEADER = 2` arity declaration: one level payload plus text. |
| `src/20-act2-literary.toml`, `src/40-act4-literary.toml` | Ready-to-paste Slice-4 controlled-scene reservations, including A4's one Act-II selector. |
| `tests/test_act2_slice4.py`, `tests/test_act4_slice4.py`, `tests/test_slice4_high_risk.py`, `tests/test_token_codes.py`, `tests/test_token_decode.py`, `tests/test_token_structure.py` | Focused fast-IR stream, stack, HTML, binary, and A2 header-contract coverage. |
| `tests/test_mdtest.py` | Fixture enablement after strict proof only. |
| `tests/test_act2_contracts.py`, `tests/test_act2_frame_floors.py`, `tests/test_architecture_spikes.py` | Preserve prior list/nested-block stream and byte contracts. |

---

## Reconciliation record

`implement-add42130d5e6432cb459bcd08a95ce01-codex-implement@3d6fb4bb6fa24900da45b4351906b75ef0b55735` was a one-commit child of `main@91a26ce5f2ebd33fd4bf334352c9f08cce79af12` whose only content was to mark Task 1 Steps 1–2 complete.  It was not merged into `main`.  On 2026-07-17 this plan replayed that disposition after independently re-running Step 2's exact evidence gate on `main`: 43 passed / 9 skipped for mdtest plus architecture spikes, strict parity `5/5 byte-identical`, the two required smoke cases passed, and the Task-1 plan-policy gate passed 9 tests.  The terminal `superseded` ledger entry binds that exact branch head to the replayed `main` checkpoint `6508c33243025121ca0dd4c4d974fed8f7d99012`; it neither merges nor deletes the branch.  This reconciliation changes no production behavior and does not amend the accepted Slice-4 design.

---

### Task 1: Establish the Slice-4 contracts and prove the shipped baseline

**Files:** Create `tests/test_act2_slice4.py`, `tests/test_act4_slice4.py`, `tests/test_slice4_high_risk.py`; modify `tests/test_mdtest.py` only to add the Slice-4 enablement guard.

**Interfaces:** Reuse `tests.test_mdtest._run_acts(input_text: str, through_act: int) -> str | list[int]` and `_FIXTURES_BY_NAME`.  `_IMPLEMENTED_FIXTURES` remains the sole mdtest enablement authority.

- [x] **Step 1: Write disabled capability contracts.** Add one parametrized contract for each pending fixture that asserts it is absent from `_IMPLEMENTED_FIXTURES`. Add strict-xfail fast-IR contracts with these exact probes:

  ```python
  ADVANCED_HTML = '<div>\n<div style=">"/>\n</div>\n'
  NESTED_QUOTE = '> foo\n>\n> > bar\n>\n> foo\n'
  FULL_LIST = '1. First\n2. Second:\n\t* Fee\n\t* Fie\n3. Third\n'
  ```

  Assert the advanced case becomes one `RAW_HTML_HASH` leaf, the quote case has two matched open/close pairs, and the list case has nested `LIST_OPEN`/`ITEM_CLOSE`/`LIST_CLOSE` grammar. Keep the complete-fixture contracts xfailed; do not enable a fixture.

  Run: `uv run pytest tests/test_act2_slice4.py tests/test_act4_slice4.py tests/test_slice4_high_risk.py -q`

  Expected: XFAIL only, with no XPASS.

- [x] **Step 2: Prove the predecessor baseline before production work.** Run:

  ```bash
  uv run pytest tests/test_mdtest.py tests/test_architecture_spikes.py -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Blockquotes with code blocks' 'Inline HTML (Simple)' 'Inline HTML comments' 'Strong and em together'
  uv run python scripts/differential_smoke.py --require 'Amps and angle encoding' --require 'Blockquotes with code blocks'
  ```

  Expected: all tests pass, strict harness reports `summary: 5/5 byte-identical`, and the smoke command has no required-case failure. On failure, record the actual shipped regression and stop; do not repair Slice 4 behavior.

- [x] **Step 3: Checkpoint the characterization.** Run `uv run pytest tests/test_prompt_literary_protocol.py tests/test_roadmap_contract.py -q`; commit only the three new test files and `tests/test_mdtest.py` as `test: characterize slice four fixtures`; push.

### Task 2: Expand raw HTML blocks to the advanced fixture boundary

**Files:** Modify `src_ir/act2.py`, `src_ir/act4.py`, `src/literary.toml`, `tests/test_act2_slice4.py`, `tests/test_act4_slice4.py`, `tests/test_slice4_high_risk.py`, and `tests/test_mdtest.py`; regenerate Acts II/IV and release SPL.

**Interfaces:** Act II emits `RAW_HTML_HASH, <original glyphs>, TEXT_END` for one left-margin `div` block. Act III copies that token. Act IV emits precisely that payload unwrapped and separates it from adjacent block output exactly as Markdown.pl does.

- [x] **Step 1: Turn only the advanced-HTML contracts red.** Replace its xfail with stream assertions for (a) `<div>foo</div>`, (b) nested three-depth `div`, (c) `style=">"`, (d) indented `id="foo"`, and (e) the final `class="inlinepage"` block. Assert the token payload preserves source tabs only after Act I detab normalization and ends before the delimiting blank line. Add a binary contract for the complete fixture, still disabled in mdtest.

  Run: `uv run pytest tests/test_act2_slice4.py tests/test_act4_slice4.py tests/test_slice4_high_risk.py -k advanced -q`

  Expected: FAIL because current simple recognition does not balance attributed/nested blocks.

- [x] **Step 2: Implement only the accepted raw-block expansion.** Add the design-reserved `PASS_HTML_BLOCK_*` and `SCRIBE_RAW_HTML_ADVANCED*` TOML entries before their labels are used. In Act II, recognize a left-margin `div` opening with attributes, retain raw glyphs, and track only fixture-required nested matching `div` depth through a matching close followed by the Markdown.pl blank/EOF boundary. On a non-match, reverse-replay every staged glyph to the existing paragraph route. Act IV consumes the unchanged raw leaf and uses the reserved separator path; Act III and `src_ir/tokens.py` stay unchanged unless its focused contract proves otherwise.

  Run:

  ```bash
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  uv run pytest tests/test_act2_slice4.py tests/test_act4_slice4.py tests/test_slice4_high_risk.py -k advanced -q
  uv run python scripts/strict_parity_harness.py 'Inline HTML (Advanced)'
  ```

  Expected: all pass and strict harness reports `summary: 1/1 byte-identical`.

- [x] **Step 3: Enable and checkpoint advanced HTML.** Add `Inline HTML (Advanced)` to `_IMPLEMENTED_FIXTURES`; run the global SPL/literary gate, then:

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Inline HTML (Simple)' 'Inline HTML comments' 'Inline HTML (Advanced)'
  ```

  Expected: pass and `summary: 4/4 byte-identical`. The enabled mdtest parametrization now runs the advanced case. Commit the Task-2 files as `feat: support advanced inline html`; push.

### Task 3: Represent and render full nested blockquotes

**Files:** Modify `src_ir/act2.py`, `src_ir/act4.py`, `src/literary.toml`, `tests/test_act2_slice4.py`, `tests/test_act4_slice4.py`, `tests/test_slice4_high_risk.py`, `tests/test_act2_contracts.py`, `tests/test_act2_frame_floors.py`, and `tests/test_mdtest.py`; regenerate Acts II/IV and release SPL.

**Interfaces:** For every `>` depth, Act II emits a balanced `BLOCKQUOTE_OPEN`; blank quoted lines remain inside the current depth; an outdent emits the matching close(s) before replaying the next block. Act IV keeps one quote frame per token nesting and renders the installed-oracle indentation layout fixed by design Amendment A1.

- [x] **Step 1: Turn only nested-quote contracts red.** Replace its xfail with an exact decoded token-stream assertion for `Nested blockquotes`: `BLOCKQUOTE_OPEN; PARA(foo); BLOCKQUOTE_OPEN; PARA(bar); BLOCKQUOTE_CLOSE; PARA(foo); BLOCKQUOTE_CLOSE`. Add focused probes for quoted blank lines, a one-level return, and an unquoted final paragraph. Assert the full output in both fast IR and release binary against the installed-oracle literal below while mdtest remains disabled; do not use `_normalize_fixture_output` for this contract:

  ```python
  INSTALLED_ORACLE_NESTED_BLOCKQUOTES = (
      "<blockquote>\\n"
      "  <p>foo</p>\\n\\n"
      "<blockquote>\\n"
      "  <p>bar</p>\\n"
      "</blockquote>\\n\\n"
      "<p>foo</p>\\n"
      "</blockquote>\\n"
  )
  ```

  Run: `uv run pytest tests/test_act2_slice4.py tests/test_act4_slice4.py tests/test_slice4_high_risk.py -k nested_quote -q`

  Expected: FAIL on current one-depth scheduling or rendering.

- [x] **Step 2: Implement balanced quote depth without changing Spike-B grammar.** Add the reserved `PASS_QUOTE_NEST_*` and `SCRIBE_QUOTE_NEST_*` TOML entries. Extend only quote-owned Act-II routes so each new marker depth pushes a matched frame and each outdent/EOF closes in reverse order; do not route through or mutate `PASS_LISTS_RAW_NEXT`, list marker recognition, token codes, or the Spike-B explicit item grammar. Extend Act IV's quote frame dispatch so nested open/close output is byte-identical to `INSTALLED_ORACLE_NESTED_BLOCKQUOTES`: preserve the installed 1.0.2b8 oracle's two-space outer first line and nested opening, with no additional indent on the nested paragraph/close. Return to the correct parent frame; do not implement the checked fixture's four-space inner layout.

  Run:

  ```bash
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  uv run pytest tests/test_act2_slice4.py tests/test_act4_slice4.py tests/test_slice4_high_risk.py -k nested_quote -q
  uv run pytest tests/test_act2_contracts.py tests/test_act2_frame_floors.py tests/test_architecture_spikes.py -q
  uv run python scripts/strict_parity_harness.py 'Nested blockquotes'
  ```

  Expected: all pass and strict harness reports `summary: 1/1 byte-identical`.

- [x] **Step 3: Enable and checkpoint nested blockquotes.** Add `Nested blockquotes` to `_IMPLEMENTED_FIXTURES`; run the global SPL/literary gate plus:

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  uv run python scripts/strict_parity_harness.py 'Blockquotes with code blocks' 'Nested blockquotes'
  ```

  Expected: pass and `summary: 2/2 byte-identical`, with all ten spike cases still exact; the enabled mdtest parametrization runs the nested fixture. Commit Task-3 files as `feat: support nested blockquotes`; push.

### Task 4: Lift the list spike narrowings to the full fixture

**Files:** Modify `src_ir/act2.py`, `src_ir/act3.py`, `src_ir/act4.py`, `src_ir/tokens.py`, `docs/spl/token-codes.md`, `src/literary.toml`, `tests/test_act2_slice4.py`, `tests/test_act4_slice4.py`, `tests/test_slice4_high_risk.py`, `tests/test_token_codes.py`, `tests/test_token_decode.py`, `tests/test_token_structure.py`, `tests/test_act2_contracts.py`, `tests/test_act2_frame_floors.py`, `tests/test_architecture_spikes.py`, and `tests/test_mdtest.py`; regenerate Acts II–IV and release SPL.

**Interfaces:** Preserve `LIST_OPEN(kind)`, `LIST_ITEM(looseness)`, `ITEM_CLOSE`, and `LIST_CLOSE` exactly. The Act-II frame stack holds list depth/indent and outputs nested containers in source order; Act IV consumes explicit item closures and never infers a close from lookahead. Per design Amendment A2, the pre-allocated `HEADER = 2` gains exactly `HEADER(level, text)`: one level payload (1–6) and a `TEXT_END`-terminated text run, which Act III preserves and Act IV renders.

- [x] **Step 1: Turn only full-list contracts red.** Replace its xfail with parameterized fast-stream and HTML probes for each fixture family:

  ```python
  cases = {
      "markers": "*\tone\n+\ttwo\n-\tthree\n",
      "multi_digit": "10. Ten\n11. Eleven\n",
      "loose": "* one\n\n* two\n",
      "paragraphs": "1. one\n\n   two\n",
      "nested": "1. One\n2. Two:\n\t* Fee\n\t* Fie\n3. Three\n",
  }
  ```

  Assert `validate_stream` accepts every Act-II result, each `LIST_ITEM` is closed by `ITEM_CLOSE`, and the complete fixture has the Markdown-1.0.1 tail bytes. Retain all six list spike dumps as immutable expected streams.

  Run: `uv run pytest tests/test_act2_slice4.py tests/test_act4_slice4.py tests/test_slice4_high_risk.py -k full_list -q`

  Expected: FAIL on at least the declared spike narrowings; do not bless a changed dump.

- [ ] **Step 2: Implement the A2 header prerequisite and full fixture scope through the accepted grammar.** First make the header contract red: in `tests/test_token_codes.py`, assert the documented `HEADER` row has one payload and text; in `tests/test_token_decode.py`, decode `[HEADER, 2, ord("U"), TEXT_END]` as level-2 text; in `tests/test_token_structure.py`, accept a decoded header leaf but reject levels `0` and `7`; and in the Slice-4 Act-II/Act-IV/binary tests assert `## Unordered\n` produces exactly `HEADER(2, "Unordered")` and `<h2>Unordered</h2>\n`.  Include a negative probe proving an indented or `##Unordered` candidate remains a paragraph.

  Add the Amendment-A2-reserved `PASS_HEADER_*` and `SCRIBE_HEADER_*` TOML entries before labels are used.  Add only `HEADER: TokenArity(1, True)` to `src_ir/tokens.py` and the matching documentation row; do not renumber a code or change a structural role.  In Act II, run the bounded top-level ATX candidate before the existing HR/list routes: count one through six leading hashes, require a following space/tab, stage non-empty line text, trim only a whitespace-preceded closing hash run, emit `HEADER`, its level, and text, or reverse-replay every rejected glyph to the paragraph route.  In Act III, add only the generic arity traversal required by that row.  In Act IV, validate level 1–6 and render `<h{level}>` plus the existing span-processed text and matching close with the normal separator.  Then add the reserved `PASS_LISTS_*` and `SCRIBE_LIST_*` entries.  Extend marker scanning to multi-digit ordered labels and up-to-three-space top-level indentation; classify tight/loose by blank lines; retain multiple paragraph leaves; recursively open/close nested list frames; and replay failed candidates byte-for-byte.  In Act IV, use only explicit frames and `ITEM_CLOSE` to render loose paragraphs, nested kind transitions, and list/item closings.  Do not add a token, alter a token number or structural role, broaden headers beyond A2, or replace the parser with a fixture-specific output path.

  For the remaining blank-sensitive cases, use only Amendment A4's ready-to-paste Act-II labels. `PASS_LISTS_LOOSE_PROVISION` stages the current tight item payload and frame state when a blank is seen. `PASS_LISTS_LOOSE_COMMIT` commits only a validated ordinary indented continuation or sibling to the existing `PASS_LISTS_BLANK_JOIN` or `PASS_LISTS_BSIB_EMIT` route. `PASS_LISTS_LOOSE_NESTED` commits a validated indented unordered/ordered marker while preserving it in `PUCK`, then re-enters `PASS_LISTS_NEST_EMIT_UL` or `PASS_LISTS_NEST_EMIT_OL`; it must never use `PASS_LISTS_BLANK_JOIN`, which would turn `*   sub` into paragraph text. `PASS_LISTS_LOOSE_EOF` recognizes EOF/list termination before either accepted path; `PASS_LISTS_LOOSE_ROLLBACK` restores the tight payload; and `PASS_LISTS_LOOSE_REPLAY` requeues saved boundary glyphs, in source order, into `PASS_LISTS_LIST_END_REPLAY`.

  Add red-then-green focused contracts for `* parent\n\n\t* sub\n` (outer loose item + nested tight list, no paragraph text `*   sub`), `* parent\n\n* sibling\n` (two loose siblings; no nested selector), and `* parent\n\n` (one tight item with no `<p>` wrapper; rollback before existing `ITEM_CLOSE`/`LIST_CLOSE`). Preserve the complete fixture's final nested tab item followed by a list-ending blank as tight. A real blank-separated continuation remains loose.  Per Amendment A5, split tab counting from `_read()`: the existing tab entry updates the count, `PASS_LISTS_INDENT_TAB_READ` only reads and loops for a further tab, and the first non-tab glyph reaches the existing four-unit classifier with the tally intact.  Add fast-IR and release probes for `1. a\n\t* b\n\t* c\n` (one nested unordered list, two sibling items) and `* a\n\t* b\n\t\t* c\n` (a second nested open for `c`); both must be strict-oracle byte-identical.  The five A5 `PASS_LISTS_INDENT_*_GUARD` labels are the only unused Act-II list spares. Do not emit `HR`, synthesize a paragraph, change an `ITEM_CLOSE`/`LIST_CLOSE` order, or add any Act-IV branch.

  Run:

  ```bash
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  uv run pytest tests/test_act2_slice4.py tests/test_act4_slice4.py tests/test_slice4_high_risk.py -k full_list -q
  uv run pytest tests/test_token_codes.py tests/test_token_decode.py tests/test_token_structure.py -q
  uv run pytest tests/test_act2_contracts.py tests/test_act2_frame_floors.py tests/test_architecture_spikes.py -q
  uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
  uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
  uv run python scripts/strict_parity_harness.py 'Ordered and unordered lists'
  ```

  Expected: all pass, strict harness reports `summary: 1/1 byte-identical`, and every existing list/nested spike stream and byte test remains unchanged.  The complete fixture's three leading sections begin with `<h2>Unordered</h2>`, `<h2>Ordered</h2>`, and `<h2>Nested</h2>`; no header syntax beyond Amendment A2 is accepted. If a required stream cannot validate under the existing grammar, or a header requirement exceeds A2's bounded path, record the architecture halt blocker rather than changing the grammar locally.

- [ ] **Step 3: Enable and checkpoint full lists.** Add `Ordered and unordered lists` to `_IMPLEMENTED_FIXTURES`; run the global SPL/literary gate plus:

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  uv run python scripts/strict_parity_harness.py 'Hard-wrapped paragraphs with list-like lines' 'Ordered and unordered lists' 'Nested blockquotes'
  ```

  Expected: pass and `summary: 3/3 byte-identical`; the enabled mdtest parametrization runs the full list fixture. Commit Task-4 files as `feat: complete markdown list fixture`; push.

### Task 5: Run the Slice-4 completion gate and register shipment

**Files:** Modify `docs/superpowers/plans/plan-roadmap.md`, `tests/test_slice4_high_risk.py`, and only evidence/measurement files required by the established performance procedure.

**Interfaces:** All three fixture names are enabled in `_IMPLEMENTED_FIXTURES`; roadmap row 7 becomes shipped only after every command below passes.

- [ ] **Step 1: Replace capability xfails with green scope assertions.** Assert that exactly `Inline HTML (Advanced)`, `Nested blockquotes`, and `Ordered and unordered lists` are Slice-4 enabled and their fast-IR contracts match their fixture expected output. Remove no regression test and do not modify production code.

  Run: `uv run pytest tests/test_slice4_high_risk.py tests/test_mdtest.py -q`

  Expected: PASS, no XFAIL/XPASS.

- [ ] **Step 2: Execute final evidence and performance gates.**

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Blockquotes with code blocks' 'Inline HTML (Simple)' 'Inline HTML comments' 'Inline HTML (Advanced)' 'Nested blockquotes' 'Ordered and unordered lists'
  uv run python scripts/differential_smoke.py --require 'Inline HTML (Advanced)' --require 'Nested blockquotes' --require 'Ordered and unordered lists'
  uv run pytest -q
  uv run ruff check .
  uv run ruff format --check .
  uv run pyright
  ```

  Then run the representative-fixture measurement commands and recording procedure in `docs/performance/budget.md`; evaluate architecture §8.2's red threshold using the recorded result.

  Expected: all commands pass, strict harness reports `summary: 7/7 byte-identical`, smoke reports all three required cases byte-identical, and no performance halt trigger is met.

- [ ] **Step 3: Mark shipped and checkpoint.** Update roadmap row 7 to `shipped: 2026-07-17 at commit <final-sha>` only after Step 2 is green. Commit the Task-5 files as `feat: complete slice four fixtures`; push. Do not begin Slice 5 in this plan.

## Plan self-review

The three §7.7 fixtures map one-to-one to Tasks 2–4; Task 1 proves the shipped floor and Task 5 supplies the full four-gate close. The accepted design supplies the bounded HTML surface, balanced quote/list grammar, A2 header prerequisite, A4's final-blank transaction and nested-after-blank selector, explicit no-new-token authority, and ready-to-paste literary pool with derived working/spare counts. Every SPL-facing task names generated-fragment, parse, validation, literary, Amps, fixture, strict-oracle, and spike gates; all fixture claims remain strict-byte claims.
