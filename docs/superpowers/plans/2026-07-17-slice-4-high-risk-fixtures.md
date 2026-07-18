# Slice 4 High-Risk Fixtures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `Inline HTML (Advanced)`, `Nested blockquotes`, and `Ordered and unordered lists` with strict Markdown.pl bytes while preserving all shipped fixtures and Spike A/B contracts.

**Architecture:** Follow the [accepted Slice-4 design](../specs/2026-07-17-slice-4-high-risk-design.md), including Amendments A2–A15, architecture §7.7/§7.8a/§8.1, and the four-act IR pipeline. Act II produces the balanced container grammar plus A2's existing allocated `HEADER(level, text)` leaf, A4's final-blank transaction with its separate accepted nested-after-blank selector, and A5's tally/read split for tab-depth classification; A15 directs the accepted loose-nested return around A14's ordinary parent close while retaining the immutable tight-nesting stream. Act III preserves structural/raw leaves, and Act IV renders those frames and headers; no parser, token number, structural role, or participant is added.

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
- For `Ordered and unordered lists`, the strict-byte authority is likewise
  the installed `~/markdown/Markdown.pl` 1.0.2b8 executable, per design
  Amendment A13.  Its checked-in corpus has only a nested-tight-list
  line-placement drift; Task 4 Step 3 alone may add A13's two replacement
  rules to the fixture-scoped mdtest comparator.  This does not weaken the
  raw strict-parity harness and does not authorize changing expected files.
- Amendment A2 authorizes only `HEADER = 2`'s new `TokenArity(1, True)` row and bounded top-level ATX path as a prerequisite of Task 4 Step 2. A needed token, third participant, structural-role change, broader header syntax/container handling, unreserved surface, or any other fixture requirement outside the accepted design is `- BLOCK[plan]: ...` in `.agent/blockers.md` followed by a clean stop.
- Amendment A4 supersedes A3's five-label limit with exactly six Act-II provisional-looseness labels.  It preserves the existing list token grammar and Act-IV renderer: stage a final blank provisionally; commit an ordinary continuation/sibling through `PASS_LISTS_LOOSE_COMMIT`; route an accepted nested marker through `PASS_LISTS_LOOSE_NESTED`; and restore tightness plus staged glyph order at EOF/list termination.
- Amendment A5 consumes A4's four guards and authorizes exactly `PASS_LISTS_INDENT_TAB_READ` plus five unused Act-II `PASS_LISTS_INDENT_*_GUARD` spares.  The existing tab entry updates the indentation tally, the read helper owns `_read()`, and the first non-tab glyph is classified before marker staging can overwrite `PUCK`; equal indentation is a sibling route and deeper indentation is a nested-open route.  A need for another helper, a sixth spare, a different register ownership, or any Act-III/IV/token/grammar change is `- BLOCK[plan]: ...` followed by a clean stop.
- Amendment A6 authorizes exactly one new Act-II working scene, `PASS_LISTS_LOOSE_OUTDENT`, plus a `PUCK`-versus-`MACBETH` depth comparison added to `PASS_LISTS_CONTINUE_GUARD` and `PASS_LISTS_INDENT_FOUR_GUARD`, so a blank-then-indented plain-text continuation that lands on an open ancestor's depth closes exactly the exceeded nested frame(s) via the existing `PASS_LISTS_SIB_OUTDENT`/`PASS_LISTS_BSIB_OUTDENT` close idiom, looping until `PUCK == MACBETH`, before falling through to the existing `PASS_LISTS_BLANK_JOIN` route. It consumes no A5 spare and touches no token, participant, Act-III/IV surface, or `PASS_LISTS_FULL_GUARD`'s HR-collapse path. A need for a second new scene, a change to that HR path, or any Act-III/IV/token/grammar change is `- BLOCK[plan]: ...` followed by a clean stop.
- Amendment A7 clears the Task-4-Step-2 `PASS_LISTS_CLOSE_ALL` underflow that appears when the ordered-list `Multiple paragraphs` subsection precedes the fixture-tail witness. It authorizes only a control-flow and guard correction of the **existing** loose-outdent cluster (`PASS_LISTS_LOOSE_OUTDENT`, `PASS_LISTS_LOOSE_OUTDENT_CLOSE`, `PASS_LISTS_LOOSE_OUTDENT_JOIN`): make `_CLOSE` loop back to `PASS_LISTS_LOOSE_OUTDENT` (per A6's authorized "loop while `PUCK < MACBETH`") instead of jumping to the join, and give `PASS_LISTS_LOOSE_OUTDENT` the same `MACBETH > 1` frame-floor discipline already guarding `PASS_LISTS_SIB_OUTDENT`/`PASS_LISTS_BSIB_OUTDENT` so the loop never pops or overwrites Macbeth's `_END` sentinel. It adds no working scene, token, participant, structural role, Act-III/IV surface, `PASS_LISTS_FULL_GUARD` HR-path change, or `src/literary.toml` entry, and consumes none of A5's five reserved spares; the A6 22-working/5-spare ledger is unchanged. A need for a second new scene, a token/grammar change, an Act-III/IV change, or any budget beyond this correction is `- BLOCK[plan]: ...` followed by a clean stop with the exact operator decision required.
- Amendment A8 authorizes exactly one existing-scene handoff for blank-line indentation after Act I detabs a source tab to four spaces: `PASS_LISTS_BLANK_INDENT_4`, after its existing `_read()`, enters the existing `PASS_LISTS_INDENT_DEPTH_GUARD` rather than directly entering `PASS_LISTS_INDENT_CLASSIFY_FOUR`. The guard increments `PUCK` once per completed four-space group while preserving Hecate's glyph and routes to the unchanged classifier, so A6's `PUCK < MACBETH` test distinguishes same-depth continuation from true outdent. Literal-tab counting, current marker depth routing, the 22-working/5-spare ledger, tokens, participants, grammar, Acts III/IV, compiler/validator behavior, and controlled prose remain frozen. Any need beyond this handoff is `- BLOCK[plan]: ...` followed by a clean stop.
- Amendment A9 authorizes one Act-II-only Hecate-stage adapter, `PASS_LISTS_LOOSE_COMMIT_HECATE`, for a blank-separated outer sibling after a nested list.  It first closes only the completed nested tail (`TEXT_END`, `ITEM_CLOSE`, `LIST_CLOSE`) and decrements the nested frame depth; it then transfers `_LOOSE_COMMIT_SIB` through the existing `PASS_CONTAINERS_OPEN` transaction so that transaction rewrites the exposed outer item, never the nested tail.  The existing Horatio-stage `PASS_LISTS_LOOSE_JOIN` / `PASS_LISTS_LOOSE_COMMIT` route remains the sole route for a blank-then-indented continuation.  A9 adds its ready-to-paste working title while retaining A5's five unused `PASS_LISTS_INDENT_*_GUARD` spares, preserving the 23-working/5-spare ledger.  It changes no token, participant, structural role, grammar, Act-III/IV surface, validator, or existing close order.  Any need to rewrite more than the exposed outer item, close more than one nested frame, add another scene, consume a spare, or change Acts III/IV is `- BLOCK[plan]: ...` followed by a clean stop.
- Amendment A11 supersedes A10's false one-sentinel premise with a structural immediate-nested-list segment scan. A10's `PASS_CONTAINERS_DEPTH_SKIP_TAIL` preserves the first direct nested `ITEM_START`; the A11-only `_LOOSE_COMMIT_SIB_HECATE_TAIL` selector then directs `PASS_CONTAINERS_DEPTH_SKIP_SUBTREE` to preserve every remaining direct nested item sentinel and payload until its immediate `LIST_OPEN` boundary, where `PASS_CONTAINERS_DEPTH_SKIP_SUBTREE_CLOSE` alone restores existing `_LOOSE_COMMIT_SIB`. The unchanged transaction then rewrites only the outer item. A11 reserves both new working titles and `PASS_LISTS_INDENT_TAIL_GUARD` as a sixth unused spare: the derived ledger is 26 working labels and six unused spares. It authorizes no recursive boundary walk, token/grammar/participant/Act-III/IV/compiler/validator change, or spare use; any such need is `- BLOCK[plan]: ...` followed by a clean stop.
- Amendment A14 authorizes only the full-suite regression repair in the accepted design: restore `ITEM_CLOSE` before the ordinary nested-list `LIST_OPEN`, and split the existing A10 tail-selector helper into the Lady-Macbeth/Horatio selector half plus one reserved Lady-Macbeth/Macbeth save half. The repaired `nested_one_level` dump remains the existing P2 blessed baseline; all tokens, Acts III/IV, fixture corpus files, and six current spares remain frozen. Add the A14 TOML surface before its one new IR scene, run the exact generated/literary gate below, and stop with `- BLOCK[plan]:` on any need beyond that bounded repair.
- Amendment A15 limits A14's restored `ITEM_CLOSE` to ordinary tight nesting. Reuse `_LOOSE_NEST_UL`/`_LOOSE_NEST_OL` as the two loose-nested return selectors: preserve the selector in `PASS_LISTS_LOOSE_NESTED[_UL]`, test it before the existing generic negative-Horatio branch in the matching `PASS_LISTS_NEST_EMIT_*`, and enter existing `PASS_LISTS_NEST_OPEN_*` directly. The ordinary `MACBETH == 1` entry still uses `PASS_LISTS_NEST_EMIT_*_OPEN` with A14's `TEXT_END`, `ITEM_CLOSE`, and existing target. No new selector, scene, literary surface, spare draw, token/grammar/participant, Act-III/IV, compiler/validator, or baseline change is authorized; route traces must prove the loose path bypasses `*_OPEN` and the tight P2 path still enters it.
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

**A11 amendment:** Amendment A10's one-sentinel instruction is superseded. After A9's one-level close/decrement, `_LOOSE_COMMIT_SIB_HECATE` preserves the first direct nested `ITEM_START` through `PASS_CONTAINERS_DEPTH_SKIP_TAIL` and changes to private `_LOOSE_COMMIT_SIB_HECATE_TAIL`. Under that selector, `PASS_CONTAINERS_DEPTH_SKIP_SUBTREE` copies every direct nested item sentinel and payload through the immediate closed list's `LIST_OPEN`; `PASS_CONTAINERS_DEPTH_SKIP_SUBTREE_CLOSE` alone restores existing `_LOOSE_COMMIT_SIB`, so the unchanged transaction rewrites the next, outer `ITEM_START`. Do not count sentinels, cross another `LIST_OPEN`, emit a token, close a frame, alter a non-A9 route, or use the reserved `PASS_LISTS_INDENT_TAIL_GUARD`. Add the two A11 working TOML entries before their labels, retain the three-item witness, and add a fast-IR/release/strict-local-oracle four-item witness `2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\t* Fum\n\n3. Third\n` whose exact output is `<ol>\n<li><p>Second:</p>\n\n<ul><li>Fee</li>\n<li>Fie</li>\n<li>Foe</li>\n<li>Fum</li></ul></li>\n<li><p>Third</p></li>\n</ol>\n`. Add a narrow source/route assertion that only `_LOOSE_COMMIT_SIB_HECATE` reaches the A10/A11 helpers, only the A11 close scene clears `_LOOSE_COMMIT_SIB_HECATE_TAIL`, and ordinary `1.\tItem 1\n\n\tItem 2\n` reaches none. The A11 ledger is 26 working / 6 unused spares; any need for another working scene, spare draw, recursive boundary counter, token/grammar/participant/Act-III/IV work is `- BLOCK[plan]:` followed by a clean stop.

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

- [x] **Step 2: Implement the A2 header prerequisite and full fixture scope through the accepted grammar.** First make the header contract red: in `tests/test_token_codes.py`, assert the documented `HEADER` row has one payload and text; in `tests/test_token_decode.py`, decode `[HEADER, 2, ord("U"), TEXT_END]` as level-2 text; in `tests/test_token_structure.py`, accept a decoded header leaf but reject levels `0` and `7`; and in the Slice-4 Act-II/Act-IV/binary tests assert `## Unordered\n` produces exactly `HEADER(2, "Unordered")` and `<h2>Unordered</h2>\n`.  Include a negative probe proving an indented or `##Unordered` candidate remains a paragraph.

  Add the Amendment-A2-reserved `PASS_HEADER_*` and `SCRIBE_HEADER_*` TOML entries before labels are used.  Add only `HEADER: TokenArity(1, True)` to `src_ir/tokens.py` and the matching documentation row; do not renumber a code or change a structural role.  In Act II, run the bounded top-level ATX candidate before the existing HR/list routes: count one through six leading hashes, require a following space/tab, stage non-empty line text, trim only a whitespace-preceded closing hash run, emit `HEADER`, its level, and text, or reverse-replay every rejected glyph to the paragraph route.  In Act III, add only the generic arity traversal required by that row.  In Act IV, validate level 1–6 and render `<h{level}>` plus the existing span-processed text and matching close with the normal separator.  Then add the reserved `PASS_LISTS_*` and `SCRIBE_LIST_*` entries.  Extend marker scanning to multi-digit ordered labels and up-to-three-space top-level indentation; classify tight/loose by blank lines; retain multiple paragraph leaves; recursively open/close nested list frames; and replay failed candidates byte-for-byte.  In Act IV, use only explicit frames and `ITEM_CLOSE` to render loose paragraphs, nested kind transitions, and list/item closings.  Do not add a token, alter a token number or structural role, broaden headers beyond A2, or replace the parser with a fixture-specific output path.

  For the remaining blank-sensitive cases, use only Amendment A4's ready-to-paste Act-II labels. `PASS_LISTS_LOOSE_PROVISION` stages the current tight item payload and frame state when a blank is seen. `PASS_LISTS_LOOSE_COMMIT` commits only a validated ordinary indented continuation or sibling to the existing `PASS_LISTS_BLANK_JOIN` or `PASS_LISTS_BSIB_EMIT` route. `PASS_LISTS_LOOSE_NESTED` commits a validated indented unordered/ordered marker while preserving it in `PUCK`, then re-enters `PASS_LISTS_NEST_EMIT_UL` or `PASS_LISTS_NEST_EMIT_OL`; it must never use `PASS_LISTS_BLANK_JOIN`, which would turn `*   sub` into paragraph text. `PASS_LISTS_LOOSE_EOF` recognizes EOF/list termination before either accepted path; `PASS_LISTS_LOOSE_ROLLBACK` restores the tight payload; and `PASS_LISTS_LOOSE_REPLAY` requeues saved boundary glyphs, in source order, into `PASS_LISTS_LIST_END_REPLAY`.

  Add red-then-green focused contracts for `* parent\n\n\t* sub\n` (outer loose item + nested tight list, no paragraph text `*   sub`), `* parent\n\n* sibling\n` (two loose siblings; no nested selector), and `* parent\n\n` (one tight item with no `<p>` wrapper; rollback before existing `ITEM_CLOSE`/`LIST_CLOSE`). Preserve the complete fixture's final nested tab item followed by a list-ending blank as tight. A real blank-separated continuation remains loose.  Per Amendment A5, split tab counting from `_read()`: the existing tab entry updates the count, `PASS_LISTS_INDENT_TAB_READ` only reads and loops for a further tab, and the first non-tab glyph reaches the existing four-unit classifier with the tally intact.  Add fast-IR and release probes for `1. a\n\t* b\n\t* c\n` (one nested unordered list, two sibling items) and `* a\n\t* b\n\t\t* c\n` (a second nested open for `c`); both must be strict-oracle byte-identical.  The five A5 `PASS_LISTS_INDENT_*_GUARD` labels are the only unused Act-II list spares.

  Per Amendment A6, handle the blank-then-ancestor-indent case `*\tthis\n\n\t*\tsub\n\n\tthat\n`: add `PASS_LISTS_LOOSE_OUTDENT` and route `PASS_LISTS_CONTINUE_GUARD`/`PASS_LISTS_INDENT_FOUR_GUARD` through it (via a `PUCK`-versus-`MACBETH` comparison) whenever the scanned indentation lands shallower than the currently open frame depth, closing exactly the exceeded nested frame(s) with the existing single-level outdent idiom before falling through to the existing `PASS_LISTS_BLANK_JOIN` route. Add red-then-green focused fast-IR and release contracts for the fixture-tail witness above and for a two-level blank-then-return variant; both must be strict-oracle byte-identical, and the existing A4/A5 focused contracts must stay green unchanged. Do not emit `HR`, synthesize a paragraph, change an `ITEM_CLOSE`/`LIST_CLOSE` order, add a second new scene, touch `PASS_LISTS_FULL_GUARD`'s HR-collapse path, or add any Act-IV branch.

  Per Amendment A7, clear the `PASS_LISTS_CLOSE_ALL` underflow that surfaces only when the ordered-list `Multiple paragraphs` subsection precedes the fixture-tail witness, using a control-flow and guard correction of the **existing** loose-outdent cluster and no new budget.  Make `PASS_LISTS_LOOSE_OUTDENT_CLOSE` re-enter `PASS_LISTS_LOOSE_OUTDENT` after closing one frame (A6's authorized loop while `PUCK < MACBETH`) instead of jumping to `PASS_LISTS_LOOSE_OUTDENT_JOIN`, and give `PASS_LISTS_LOOSE_OUTDENT` the same `MACBETH > 1` frame-floor guard that already protects `PASS_LISTS_SIB_OUTDENT`/`PASS_LISTS_BSIB_OUTDENT`, so the loop stops at the ancestor depth and never pops or overwrites Macbeth's `_END` sentinel.  Add a red-then-green fast-IR and release contract for the combined repro (the ordered `Multiple paragraphs` subsection immediately followed by the tail witness) and a `tests/test_act2_frame_floors.py` assertion that the sentinel survives a loose outdent unwinding to the floor; the three A4, two A5, and two A6 focused contracts must stay green unchanged.  Add no working scene, token, participant, structural role, Act-III/IV surface, `PASS_LISTS_FULL_GUARD` HR-path change, or `src/literary.toml` entry, and consume no A5 spare.  If the full fixture still cannot validate under the frozen grammar after this correction, record the architecture-halt `- BLOCK[plan]:` with the exact operator decision required and stop.

  Per Amendment A8, make the blank-line four-space scanner represent the same detabbed indentation unit as the existing ordinary-line scanner: after `PASS_LISTS_BLANK_INDENT_4` performs its existing `_read()`, route it to the existing `PASS_LISTS_INDENT_DEPTH_GUARD`, which increments `PUCK` exactly once and then enters the unchanged `PASS_LISTS_INDENT_CLASSIFY_FOUR`.  Do not duplicate the increment, add a helper, alter literal-tab handling, or modify the marker classifier.  First add red, then green, fast-IR and release contracts for `1.\tx\n\n\ty\n` → `<ol>\n<li><p>x</p>\n\n<p>y</p></li>\n</ol>\n`, `*\ta\n\n\tb\n` → `<ul>\n<li><p>a</p>\n\n<p>b</p></li>\n</ul>\n`, and `1.\ta\n\n\t* b\n` → `<ol>\n<li><p>a</p>\n\n<ul><li>b</li></ul></li>\n</ol>\n`, each with strict local Markdown.pl bytes.  Keep the A4–A7 focused contracts, all six List Spike-A and four nested-block Spike-B fixtures, and the `loose_second_paragraph`/`nested_one_level` interpreter and token-dump baselines unchanged.  Add no working scene, token, participant, structural role, Act-III/IV surface, compiler/validator change, TOML entry, or A5-spare use.  Any need beyond that one handoff is `- BLOCK[plan]: ...` followed by a clean stop.

  Per Amendment A9, add red-then-green fast-IR, release, and strict-local-oracle contracts for both stage-pair disjoint paths: `1.\tItem 1\n\n\tItem 2\n` must retain one ordered loose item with two paragraph leaves, and `2. Second:\n\t* Fee\n\t* Fie\n\t* Foe\n\n3. Third\n` must decode as a loose outer `Second:` item containing a tight nested list whose `Fee`/`Fie`/`Foe` items each remain tight, followed by a loose outer `Third` sibling.  Its release bytes are exactly `<ol>\n<li><p>Second:</p>\n\n<ul><li>Fee</li>\n<li>Fie</li>\n<li>Foe</li></ul></li>\n<li><p>Third</p></li>\n</ol>\n`.  Route only the nested-to-outer-sibling branch, while Hecate is live, to `PASS_LISTS_LOOSE_COMMIT_HECATE`; it must emit the inner tail close sequence once, decrement the frame once, set `HORATIO` to `_LOOSE_COMMIT_SIB`, and enter `PASS_CONTAINERS_OPEN`.  The existing container transaction then reaches the existing Horatio-stage `PASS_LISTS_LOOSE_COMMIT` and `PASS_LISTS_BSIB_EMIT` route, which closes the now-exposed loose outer item and opens `Third`.  Do not branch the Hecate-stage predecessor directly to `PASS_LISTS_LOOSE_COMMIT`, do not use `PASS_LISTS_LOOSE_OUTDENT`, and do not route the ordinary continuation through the new adapter: those choices respectively violate splc's stage-pair validation, rewrite `Foe`, or change explicit close order.  Add the A9 ready-to-paste TOML entry before use and retain all five A5 spares unused.  Keep every A4–A8 witness, all Spike-A/B fixtures, token-dump baselines, generated/literary gate, and Amps proof unchanged.

  Per Amendment A10, preserve A9's one-level tail close and decrement but set the private `_LOOSE_COMMIT_SIB_HECATE` selector before entering `PASS_CONTAINERS_OPEN`.  In the existing `PASS_CONTAINERS_DEPTH` scan, branch only that selector's first encountered `ITEM_START` to the new `PASS_CONTAINERS_DEPTH_SKIP_TAIL`; it copies that sentinel into the saved suffix, changes `HORATIO` to the existing `_LOOSE_COMMIT_SIB`, and resumes the same scan.  The next `ITEM_START` is the outer item and therefore reaches the unchanged rewrite/close transaction; the existing `PASS_LISTS_LOOSE_COMMIT` and `PASS_LISTS_BSIB_EMIT` paths own its close and `Third` opening.  The skip scene may skip exactly one sentinel, emit no token, close no frame, and must be unreachable from the ordinary Horatio-stage continuation, loose nested-marker paths, quote paths, and all other container rewrites.  Add the A10 ready-to-paste TOML entry before its IR label.  Extend the A9 decoded-stream test to assert the unchanged nested `Fee`/`Fie`/`Foe` item sequence before the outer close, and add a focused negative route assertion (scene label or narrow IR trace, matching existing test style) that `1.\tItem 1\n\n\tItem 2\n` never enters `PASS_CONTAINERS_DEPTH_SKIP_TAIL`.  Retain all five A5 spares unused.  Any need for a second skip, another scene, a spare draw, a token/grammar change, or Act-III/IV work is `- BLOCK[plan]:` followed by a clean stop.

  Per Amendment A12, complete A11's immediate nested-list preservation without allowing the existing close transaction to mistake a preserved nested `ITEM_START` for the outer stop marker. Keep `_LOOSE_COMMIT_SIB_HECATE_TAIL` while `PASS_CONTAINERS_DEPTH_SKIP_SUBTREE` copies the direct nested segment. After its immediate `LIST_OPEN`, `PASS_CONTAINERS_DEPTH_SKIP_SUBTREE_CLOSE` must set the new private `_LOOSE_COMMIT_SIB_HECATE_CLOSE_TAIL` selector—not `_LOOSE_COMMIT_SIB`—so the generic depth scan reaches the outer `ITEM_START` and existing EOF path. In `PASS_CONTAINERS_CLOSE`, test this selector before the generic `ITEM_START` stop and enter `PASS_CONTAINERS_CLOSE_SKIP_SUBTREE`. That scene copies each popped value unchanged to Lady Macbeth; direct nested `ITEM_START` values remain data until the one immediate `LIST_OPEN`, where `PASS_CONTAINERS_CLOSE_SKIP_SUBTREE_CLOSE` alone restores existing `_LOOSE_COMMIT_SIB` and returns to `PASS_CONTAINERS_CLOSE`. The next `ITEM_START` is then the outer boundary and follows the unchanged `PASS_CONTAINERS_CLOSE_ROUTE`/restore/`PASS_LISTS_LOOSE_COMMIT`/`PASS_LISTS_BSIB_EMIT` ownership path. Add both A12 ready-to-paste TOML entries before their IR labels. First make the A11 three-item and four-item witness contracts red, then make them green in fast IR, release binary, and strict local Markdown.pl output; assert all direct nested items stay tight and source ordered, `Second:` closes once, and loose `Third` opens once. Add narrow source/route assertions that only the depth-side close helper writes `_LOOSE_COMMIT_SIB_HECATE_CLOSE_TAIL`, only the close-side helper restores `_LOOSE_COMMIT_SIB`, and ordinary `1.\tItem 1\n\n\tItem 2\n` enters none of A10/A11/A12 helpers. Retain all A4–A11 witnesses, immutable Spike-A/B streams, generated/literary gates, Amps proof, and strict full-list gate unchanged. This is exactly two working scenes and one private selector: no spare draw (28 working / 6 unused spares), token/grammar/participant/Act-III/IV/compiler/validator change, recursive boundary counter, or second nested `LIST_OPEN` is authorized. Any need beyond that is `- BLOCK[plan]:` with the exact witness followed by a clean stop.

  Run:

  ```bash
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  uv run pytest tests/test_act2_slice4.py tests/test_act4_slice4.py tests/test_slice4_high_risk.py -k full_list -q
  uv run pytest tests/test_act2_frame_floors.py -q
  uv run pytest tests/test_token_codes.py tests/test_token_decode.py tests/test_token_structure.py -q
  uv run pytest tests/test_act2_contracts.py tests/test_act2_frame_floors.py tests/test_architecture_spikes.py -q
  uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
  uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
  uv run python scripts/strict_parity_harness.py 'Ordered and unordered lists'
  ```

  Expected: all pass, strict harness reports `summary: 1/1 byte-identical`, and every existing list/nested spike stream and byte test remains unchanged.  The complete fixture's three leading sections begin with `<h2>Unordered</h2>`, `<h2>Ordered</h2>`, and `<h2>Nested</h2>`; no header syntax beyond Amendment A2 is accepted. If a required stream cannot validate under the existing grammar, or a header requirement exceeds A2's bounded path, record the architecture halt blocker rather than changing the grammar locally.

- [x] **Step 3: Enable and checkpoint full lists.** In `tests/test_mdtest.py`, add
  `_normalize_ordered_unordered_list_layout(text: str) -> str` with a docstring
  naming the checked-in Markdown-1.0.1 nested-tight-list layout drift.  After
  `_normalize(text)`, call it only for `name == "Ordered and unordered lists"`:

  ```python
  def _normalize_ordered_unordered_list_layout(text: str) -> str:
      """Normalize the static corpus's nested tight-list line placement."""
      text = text.replace("<ul>\n<li>", "<ul><li>")
      return text.replace("</li>\n</ul></li>", "</li></ul></li>")
  ```

  Apply the same function to expected, fast-IR, and release output through
  `_normalize_fixture_output`; do not use it for any other fixture and do not
  alter expected files.  Then add `Ordered and unordered lists` to
  `_IMPLEMENTED_FIXTURES`; run the global SPL/literary gate plus:

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  uv run python scripts/strict_parity_harness.py 'Hard-wrapped paragraphs with list-like lines' 'Ordered and unordered lists' 'Nested blockquotes'
  ```

  Expected: pass and `summary: 3/3 byte-identical`; the enabled mdtest
  parametrization runs the full list fixture under the A13 corpus-layout
  comparator, while the strict harness proves raw installed-oracle bytes.
  Commit Task-4 files as `feat: complete markdown list fixture`; push.

### Task 5: Run the Slice-4 completion gate and register shipment

**Files:** Modify `src_ir/act2.py`, `src/20-act2-literary.toml`, `tests/test_act2_slice2.py`, `tests/test_act2_slice4.py`, `tests/test_splc_interpret_parity.py`, `tests/test_token_dump.py`, `docs/superpowers/plans/plan-roadmap.md`, `tests/test_slice4_high_risk.py`, and only evidence/measurement files required by the established performance procedure; regenerate `src/20-act2-block.spl` and reassemble `shakedown.spl`.

**Interfaces:** All three fixture names are enabled in `_IMPLEMENTED_FIXTURES`; roadmap row 7 becomes shipped only after every command below passes.

- [x] **Step 1: Replace capability xfails with green scope assertions.** Assert that exactly `Inline HTML (Advanced)`, `Nested blockquotes`, and `Ordered and unordered lists` are Slice-4 enabled and their fast-IR contracts match their fixture expected output. Remove no regression test and do not modify production code.

  Run: `uv run pytest tests/test_slice4_high_risk.py tests/test_mdtest.py -q`

  Expected: PASS, no XFAIL/XPASS.

- [x] **Step 2: Repair the pre-existing full-suite regressions under Amendments A14–A15.** First add focused red contracts: assert every `ACT2` scene has Lady Macbeth as anchor and exactly one companion; assert both ordinary nested-open scenes emit `TEXT_END`, `ITEM_CLOSE`, then their existing `PASS_LISTS_NEST_OPEN_*` target; and assert the fast and release debug streams for `nested_one_level` equal the committed P2 baseline, including the parent `ITEM_CLOSE` immediately before the child ordered `LIST_OPEN`. Confirm those contracts fail against the pre-A14 tree. Then, against the A14 WIP, confirm the three existing loose-nesting/full-fixture stream contracts fail because the shared opener has acquired the extra close.

  Add the A14 `PASS_CONTAINERS_DEPTH_SKIP_TAIL_SAVE` TOML entry before its IR label. Change only `src_ir/act2.py`: restore `push(LADY_MACBETH, const(tokens.ITEM_CLOSE))` in each `PASS_LISTS_NEST_EMIT_*_OPEN`; make `PASS_CONTAINERS_DEPTH_SKIP_TAIL` set `_LOOSE_COMMIT_SIB_HECATE_TAIL` and jump to the new save scene; and make that scene push the current Lady-Macbeth glyph to Macbeth before re-entering `PASS_CONTAINERS_DEPTH`. Per A15, do not reset `HORATIO` in `PASS_LISTS_LOOSE_NESTED[_UL]`; instead, add the matching equality branch before the existing negative-Horatio branch in each `PASS_LISTS_NEST_EMIT_*`, entering the existing `PASS_LISTS_NEST_OPEN_*` directly. Add source/IR branch-order assertions and scene-trace assertions for `* parent\n\n\t* sub\n` and `1. parent\n\n\t1. sub\n`: each loose route enters its existing `PASS_LISTS_NEST_OPEN_*` and never enters `PASS_LISTS_NEST_EMIT_*_OPEN`. Assert ordinary `nested_one_level` still enters `PASS_LISTS_NEST_EMIT_OL_OPEN`. Do not alter a baseline file, selector value other than retaining the existing loose-nest selector through its specified return, or any other route.

  Run:

  ```bash
  uv run python -m scripts.splc && uv run python scripts/assemble.py
  uv run pytest tests/test_act2_slice2.py::test_act2_scenes_have_exactly_one_companion tests/test_act2_slice4.py -q
  uv run pytest tests/test_splc_interpret_parity.py tests/test_token_dump.py -q
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -q
  uv run python scripts/strict_parity_harness.py 'Ordered and unordered lists' 'Nested blockquotes' 'Inline HTML (Advanced)'
  uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
  uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
  ```

  Expected: all commands pass; the immutable `nested_one_level` baseline passes in both interpreter paths, strict parity reports `summary: 3/3 byte-identical`, and no generated or literary contract drifts. Commit the repair files as `fix: restore nested list stream`; push.

- [x] **Step 3: Execute final evidence and performance gates.**

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

- [ ] **Step 4: Mark shipped and checkpoint.** Update roadmap row 7 to `shipped: 2026-07-17 at commit <final-sha>` only after Step 3 is green. Commit the Task-5 files as `feat: complete slice four fixtures`; push. Do not begin Slice 5 in this plan.

## Plan self-review

The three §7.7 fixtures map one-to-one to Tasks 2–4; Task 1 proves the shipped floor and Task 5 supplies the full four-gate close. The accepted design supplies the bounded HTML surface, balanced quote/list grammar, A2 header prerequisite, A4's final-blank transaction and nested-after-blank selector, A5/A8's shared detabbed-depth accounting, and A9–A15's stage-pair-safe nested-to-outer sibling adapter, A14 restoration of the immutable P2 nested-list stream, and A15's bounded loose-return bypass, with explicit no-new-token authority and a ready-to-paste literary pool whose 29-working/6-spare ledger is derived. A13 makes the installed oracle authoritative over only the static list corpus's nested-tight layout drift, while retaining raw strict parity. Every SPL-facing task names generated-fragment, parse, validation, literary, Amps, fixture, strict-oracle, and spike gates; all fixture claims remain strict-byte claims.
