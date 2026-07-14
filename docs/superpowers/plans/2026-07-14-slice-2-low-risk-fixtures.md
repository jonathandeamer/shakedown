# Slice 2 — Low-Risk Fixtures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Auto links, Backslash escapes, Code Spans, Tidyness, Tabs, Horizontal rules, and Code Blocks pass through the SPL pipeline, with strict fresh-Markdown.pl bytes for the six deterministic fixtures and the documented entity-normalized comparison for Auto links.

**Architecture:** Retain the accepted one-way buffered Act-III scan from the span spike; its code-span, escape, URL-autolink, and inline-tag machines are Slice 2's only span implementation model. Repair the prerequisite Act-I normalization/detab transport, extend Act II to emit the already-allocated `HR` and `CODE_BLOCK` leaf tokens before paragraph formation, and extend Act IV to render those leaf tokens without entering the container-frame grammar. The existing list/blockquote composition is not redesigned: Tidyness and the list portions of Auto links/Tabs are acceptance cases for Spike A/B.

**Tech Stack:** Python 3.13, `scripts.splc` IR/lowering, Shakespeare Programming Language, pytest, local `~/markdown/Markdown.pl` oracle.

## Global Constraints

- Authority and scope: roadmap row 5; architecture spec `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §§4.2, 4.3, 7.5, 7.8a, and 8.1; accepted span design `docs/superpowers/specs/2026-07-12-span-architecture-spike-design.md`.
- Production Markdown behavior remains SPL-owned. Do not add a Python/Perl fallback, fixture-name branch, canned output, or an oracle invocation to `./shakedown`.
- Generated acts are edited only in `src_ir/act1.py`, `src_ir/act2.py`, `src_ir/act3.py`, and `src_ir/act4.py`; regenerate with `uv run python -m scripts.splc` and assemble with `uv run python scripts/assemble.py`. Never hand-edit `src/10-act1-preprocess.spl`, `src/20-act2-block.spl`, `src/30-act3-span.spl`, `src/40-act4-emit.spl`, or `shakedown.spl`.
- Keep the Span Spike's one-way invariant: generated HTML never returns to the Act-III source buffer; code spans, escapes, URL autolinks, and inline tags remain protected regions in the existing scan order.
- `tokens.HR == 3` and `tokens.CODE_BLOCK == 9` are already allocated leaf blocks. Do not renumber tokens or change existing stream arities; update `docs/spl/token-codes.md` only if its descriptions need the newly emitted shapes.
- An HTML `<pre><code>` leaf is emitted only by Act IV. Act II sends code payload glyphs unescaped and terminated by `TEXT_END`; Act III copies `CODE_BLOCK` payload text without scanning it.
- Preserve literal trailing spaces inside code-block payloads. The Slice-2 strict gate compares `Code Blocks` to fresh local oracle output, not its known stale checked-in expected file.
- The `Auto links` fixture includes email nondeterminism only through the existing normalized mdtest contract. URL autolinks and all other Slice-2 fixtures must be fresh-oracle byte-identical.
- Every task that changes SPL IR or controlled prose runs these exact literary/build gates: `uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q`, followed by `uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q`.
- If an implementation needs a controlled surface outside the reservations below, stop, add exactly one `- BLOCK[plan]:` line to `.agent/blockers.md` identifying the depleted pool and required label, and do not invent prose.
- Each commit ends after a blank line with exactly: `Agent: <executor>`, `Model: <model>`, `Harness: MCO 0.10.8`, and `Co-authored-by: OpenAI Codex <noreply@openai.com>`. Push non-force to the current branch after each logical checkpoint; a failed push is a `- BLOCK:` and stops the iteration.

## File map

| File | Responsibility in this slice |
|---|---|
| `src_ir/act1.py` | Final-newline handling, whitespace-only-line normalization, four-column tab expansion, and input-count handoff without the Slice-1 hardcoded reference stripping. |
| `src_ir/act2.py` | Block-start dispatcher additions for horizontal-rule recognition and contiguous indented code leaves, before the existing list and paragraph passes. |
| `src_ir/act3.py` | Existing protected span machines are exercised; change only for an evidence-backed Slice-2 defect. |
| `src_ir/act4.py` | Direct leaf rendering for `HR` and `CODE_BLOCK`, preserving the existing paragraph/list/quote frame behavior. |
| `src/10-act1-literary.toml`, `src/20-act2-literary.toml`, `src/40-act4-literary.toml` | Controlled titles and Recall lines reserved below; add only labels used by the corresponding IR task. |
| `tests/test_mdtest.py` | Add a fixture to `_IMPLEMENTED_FIXTURES` only after that fixture's IR and real-wrapper acceptance gates pass. |
| `tests/test_act1_slice2.py`, `tests/test_act2_slice2.py`, `tests/test_act4_slice2.py` | Focused fast-interpreter contracts for preprocessing, leaf-token streams, and renderer bytes. |
| `tests/test_slice2_low_risk.py` | Fixture-specific strict-parity and no-oracle-stub regression tests, including the entity-normalized Auto-links assertion. |
| `docs/performance/budget.md`, `docs/verification-plan.md` | Record the Slice-2 measured line/scene/runtime/regression evidence required by architecture §8.3. |

## Literary protocol and reservations

Before editing any listed IR, implementation agents must read `docs/superpowers/notes/spl-literary-protocol.md`, `docs/superpowers/notes/correctness-first-spl-workflow.md`, `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`, `docs/spl/codegen-style-guide.md`, and `src/literary.toml`. These additions are Incidental controlled scene titles (and the two stated Recall lines), not new Critical or Stable Utility prose. The working pool is derived from the state table rather than guessed; each act's spare pool is at least 20% and never fewer than four.

| Act | State-family enumeration | Working | Spares |
|---|---|---:|---:|
| I | normalize final newline (2), expand tab column 0/1/2/3 (4), blank-line normalization (2), reverse/count handoff (2) | 10 | 4 |
| II | HR gate/save/scan/confirm/replay/emit (7), code-indent gate/open/copy/line-end/continue/close (6), paragraph boundary integration (3) | 16 | 4 |
| IV | HR dispatch/emit/separate (3), code dispatch/open/payload/close/separate (5), parent-frame return (2) | 10 | 4 |

Ready-to-paste controlled surfaces (append only the labels actually used):

```toml
# src/10-act1-literary.toml — Act I working pool
[scenes.HECATE_NORMALIZE_FINAL]
title = "Hecate settles the last cauldron ripple."
pattern = "scene_of_character"
[scenes.HECATE_NORMALIZE_BLANK]
title = "The cauldron keeps one quiet blank."
pattern = "bare_statement"
[scenes.HECATE_DETAB_OPEN]
title = "Hecate measures the tab's dark stride."
pattern = "scene_of_character"
[scenes.HECATE_DETAB_COLUMN_ONE]
title = "The first column yields its pale space."
pattern = "bare_statement"
[scenes.HECATE_DETAB_COLUMN_TWO]
title = "The second column yields its pale space."
pattern = "bare_statement"
[scenes.HECATE_DETAB_COLUMN_THREE]
title = "The third column yields its pale space."
pattern = "bare_statement"
[scenes.HECATE_DETAB_COLUMN_FOUR]
title = "The fourth column starts a fresh measure."
pattern = "bare_statement"
[scenes.HECATE_DETAB_GLYPH]
title = "Hecate carries one measured cauldron mark."
pattern = "scene_of_character"
[scenes.HECATE_NORMALIZE_LINE]
title = "The witch restores the measured line."
pattern = "scene_of_character"
[scenes.HECATE_HAND_NORMALIZED]
title = "Horatio receives the measured tally."
pattern = "scene_of_character"
# Act I spare pool
[scenes.HECATE_DETAB_FALLBACK]
title = "A loose tab returns to the cauldron."
pattern = "bare_statement"
[scenes.HECATE_NORMALIZE_CLOSE]
title = "The brew closes beneath one clear moon."
pattern = "bare_statement"
[scenes.HECATE_COLUMN_RECALL]
title = "Hecate recalls the measured cauldron edge."
pattern = "scene_of_character"
[scenes.HECATE_HANDOFF_FALLBACK]
title = "The witness keeps the final quiet tally."
pattern = "scene_of_character"
[characters.hecate.recall]
detab_column_mark = "Recall the measured cauldron column."
normalized_line_mark = "Recall the settled cauldron line."

# src/20-act2-literary.toml — Act II working pool
[scenes.PASS_HR_GATE]
title = "Macbeth tests the level iron stroke."
pattern = "scene_of_character"
[scenes.PASS_HR_SAVE]
title = "Lady Macbeth keeps the iron mark."
pattern = "scene_of_character"
[scenes.PASS_HR_SCAN]
title = "Macbeth counts the level iron strokes."
pattern = "scene_of_character"
[scenes.PASS_HR_SPACE]
title = "The iron strokes leave a narrow hush."
pattern = "bare_statement"
[scenes.PASS_HR_CONFIRM]
title = "The thane confirms the level iron line."
pattern = "scene_of_character"
[scenes.PASS_HR_REPLAY]
title = "Lady Macbeth restores the loose iron marks."
pattern = "scene_of_character"
[scenes.PASS_HR_EMIT]
title = "Macbeth raises the level iron bar."
pattern = "scene_of_character"
[scenes.PASS_CODE_GATE]
title = "Lady Macbeth tests the fourfold threshold."
pattern = "scene_of_character"
[scenes.PASS_CODE_OPEN]
title = "Macbeth opens the indented chamber."
pattern = "scene_of_character"
[scenes.PASS_CODE_GLYPH]
title = "Lady Macbeth keeps one chamber mark."
pattern = "scene_of_character"
[scenes.PASS_CODE_LINE_END]
title = "The chamber line reaches its stone edge."
pattern = "bare_statement"
[scenes.PASS_CODE_CONTINUE]
title = "Macbeth continues the indented chamber."
pattern = "scene_of_character"
[scenes.PASS_CODE_CLOSE]
title = "Lady Macbeth seals the indented chamber."
pattern = "scene_of_character"
[scenes.PASS_BLOCK_REPLAY]
title = "Macbeth restores the unclaimed block mark."
pattern = "scene_of_character"
[scenes.PASS_BLOCK_BOUNDARY]
title = "The kingdom keeps its measured boundary."
pattern = "bare_statement"
[scenes.PASS_BLOCK_RETURN]
title = "Lady Macbeth returns the shaped block stream."
pattern = "scene_of_character"
# Act II spare pool
[scenes.PASS_HR_FALLBACK]
title = "The broken iron line returns to earth."
pattern = "bare_statement"
[scenes.PASS_CODE_BLANK]
title = "The chamber holds one quiet interval."
pattern = "bare_statement"
[scenes.PASS_CODE_REPLAY]
title = "Macbeth restores the chamber's loose mark."
pattern = "scene_of_character"
[scenes.PASS_BLOCK_FINISH]
title = "The kingdom releases the finished measure."
pattern = "bare_statement"
[characters.lady_macbeth.recall]
code_chamber_mark = "Recall the indented chamber mark."

# src/40-act4-literary.toml — Act IV working pool
[scenes.SCRIBE_TEST_HR]
title = "Prospero weighs the level iron bar."
pattern = "scene_of_character"
[scenes.SCRIBE_EMIT_HR]
title = "Prospero inscribes the level iron bar."
pattern = "scene_of_character"
[scenes.SCRIBE_HR_RETURN]
title = "The scribe releases the iron measure."
pattern = "bare_statement"
[scenes.SCRIBE_TEST_CODE_BLOCK]
title = "Prospero tests the indented chamber seal."
pattern = "scene_of_character"
[scenes.SCRIBE_EMIT_CODE_OPEN]
title = "Prospero opens the indented chamber."
pattern = "scene_of_character"
[scenes.SCRIBE_EMIT_CODE_GLYPH]
title = "The scribe releases one chamber mark."
pattern = "bare_statement"
[scenes.SCRIBE_EMIT_CODE_AMP]
title = "Prospero gilds the chamber's broken river."
pattern = "scene_of_character"
[scenes.SCRIBE_EMIT_CODE_ANGLE]
title = "Prospero softens the chamber's bright corner."
pattern = "scene_of_character"
[scenes.SCRIBE_EMIT_CODE_CLOSE]
title = "Prospero seals the indented chamber."
pattern = "scene_of_character"
[scenes.SCRIBE_LEAF_RETURN]
title = "The scribe returns from the leaf's quiet chamber."
pattern = "scene_of_character"
# Act IV spare pool
[scenes.SCRIBE_HR_SEPARATOR]
title = "The iron bar leaves one clear pause."
pattern = "bare_statement"
[scenes.SCRIBE_CODE_BLANK]
title = "The chamber keeps one silent interval."
pattern = "bare_statement"
[scenes.SCRIBE_CODE_FALLBACK]
title = "The loose chamber mark returns unchanged."
pattern = "bare_statement"
[scenes.SCRIBE_LEAF_FINISH]
title = "Prospero frees the finished leaf measure."
pattern = "scene_of_character"
[characters.prospero.recall]
code_leaf_mark = "Recall the indented chamber mark."
```

---

### Task 1: Establish Slice-2 acceptance seams and remove the Slice-1-only preprocessing assumption

**Files:**
- Create: `tests/test_act1_slice2.py`
- Create: `tests/test_slice2_low_risk.py`
- Modify: `src_ir/act1.py`
- Modify: `src/10-act1-literary.toml`

**Interfaces:**
- Produces a normalized glyph carrier with a faithful final `\n\n`, tabs expanded to four-column stops, and no unconditional deletion of trailing lines.
- Preserves Act I's existing handoff: `HORATIO` holds the count and `PUCK` supplies the forward glyph stream to Act II.

- [x] **Step 1: Add the failing Act-I contracts.**

  Add interpreter-level tests that feed (a) `"one\n\ntwo\n"`, (b) `"\tX\n \tY\n  \tZ\n   \tQ\n"`, and (c) the ending of `Code Blocks.text` into Act I. Assert that the downstream glyph sequence retains every non-reference line, ends in exactly two newlines, and expands each tab to the next multiple of four columns. Assert that the literal trailing spaces in `"all contain trailing spaces  \n"` are retained.

  Run: `uv run pytest tests/test_act1_slice2.py -q`

  Expected: FAIL against the current hardcoded two-line stripping Act I.

- [x] **Step 2: Implement the bounded Act-I normalization state machine.**

  Replace the Slice-1 `HECATE_LINE_STRIP_*` behavior with a single pass that reads all stdin glyphs, normalizes the final newline, expands `\t` to `4 - (column % 4)` spaces, resets column on newline, preserves nonblank and trailing-space bytes, then appends the required second final newline. Do not attempt reference-definition parsing in this task: Slice 3 owns that table. Use only the Task-1 Act-I reserved labels and recalls above; add their TOML entries in the same change.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act1_slice2.py -q`

  Expected: PASS.

- [x] **Step 3: Run the literary/generated evidence gate and checkpoint.**

  Run:

  ```bash
  uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py -q
  git add src_ir/act1.py src/10-act1-literary.toml src/10-act1-preprocess.spl shakedown.spl tests/test_act1_slice2.py tests/test_slice2_low_risk.py
  git commit -m "feat: normalize slice two input"
  git push origin HEAD
  ```

  Expected: all tests pass; generated files are fresh; commit and non-force push succeed.

### Task 2: Emit and render horizontal-rule leaf blocks

**Files:**
- Create: `tests/test_act2_slice2.py`
- Create: `tests/test_act4_slice2.py`
- Modify: `src_ir/act2.py`
- Modify: `src_ir/act4.py`
- Modify: `src/20-act2-literary.toml`
- Modify: `src/40-act4-literary.toml`
- Modify: `tests/test_mdtest.py`
- Modify: `tests/test_slice2_low_risk.py`

**Interfaces:**
- Act II emits `[HR]` for a line of one repeated `-`, `*`, or `_` marker with optional spaces, at least three markers, and no more than two leading spaces; it replays every rejected candidate as normal paragraph text.
- Act IV renders an `HR` leaf exactly as `<hr />`, inserting the same block separator policy as sibling paragraphs and never pushing a container frame.

- [ ] **Step 1: Add failing HR stream and byte tests.**

  In `test_act2_slice2.py`, assert that `---\n\n`, `- - -\n\n`, `***\n\n`, and `_ _ _\n\n` emit `tokens.HR`, while `  ---\n\n` is accepted and `   ---\n\n` remains `PARA`; assert tab-expanded four-space candidates become `CODE_BLOCK`, not `HR`. In `test_act4_slice2.py`, feed `[STREAM_END, HR]` in Act-IV pop order and assert `<hr />\n`. Add `Horizontal rules` to the enabled set only after both interpreter and binary fixture tests are present.

  Run: `uv run pytest tests/test_act2_slice2.py tests/test_act4_slice2.py tests/test_mdtest.py -k 'Horizontal rules' -q`

  Expected: FAIL.

- [ ] **Step 2: Add the HR block pass and renderer dispatch.**

  At Act-II block boundaries, inspect up to two leading spaces then buffer one candidate marker/count; consume spaces only between identical markers; accept only a newline after count >= 3; otherwise replay the exact buffered bytes to the paragraph path. Run this pass after future-header entry but before list/code/paragraph processing. Emit only `tokens.HR`. In Act IV route `tokens.HR` before paragraph/list dispatch, output `<hr />`, and restore/update the parent frame exactly once. Use only the Task-2 Act-II/IV reserved labels.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_act2_slice2.py tests/test_act4_slice2.py tests/test_mdtest.py -k 'Horizontal rules' -q && uv run python scripts/strict_parity_harness.py 'Horizontal rules'`

  Expected: all commands pass and strict parity reports `summary: 1/1 byte-identical`.

- [ ] **Step 3: Run regression gates and checkpoint.**

  Run:

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -k 'Amps and angle or Horizontal rules' -q
  uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py -q
  git add src_ir/act2.py src_ir/act4.py src/20-act2-literary.toml src/40-act4-literary.toml src/20-act2-block.spl src/40-act4-emit.spl shakedown.spl tests/test_act2_slice2.py tests/test_act4_slice2.py tests/test_mdtest.py tests/test_slice2_low_risk.py
  git commit -m "feat: render horizontal rules"
  git push origin HEAD
  ```

  Expected: all gates pass.

### Task 3: Emit and render indented code blocks, including tab-sensitive payloads

**Files:**
- Modify: `src_ir/act2.py`
- Modify: `src_ir/act4.py`
- Modify: `tests/test_act2_slice2.py`
- Modify: `tests/test_act4_slice2.py`
- Modify: `tests/test_mdtest.py`
- Modify: `tests/test_slice2_low_risk.py`

**Interfaces:**
- Act II emits `[CODE_BLOCK, glyphs..., TEXT_END]` for each contiguous 4-column-indented block; remove exactly four leading spaces per nonblank line, retain blank lines and remaining indentation, and return the first non-code line to normal block processing.
- Act IV renders `CODE_BLOCK` as `<pre><code>` + payload with `&`, `<`, `>` HTML-escaped + `</code></pre>`; no Act-III span transform runs on its payload.

- [ ] **Step 1: Add failing code-block and tab contracts.**

  Add stream assertions for the `Code Blocks` fixture and the three code blocks in `Tabs.text`: one tab removes to column zero, two tabs leave four literal spaces, and tab-expanded example-list text is code rather than a list. Add renderer assertions for amp/angle escaping and preservation of two trailing spaces. Enable `Code Blocks` and `Tabs` only once their respective fixture assertions have been added.

  Run: `uv run pytest tests/test_act2_slice2.py tests/test_act4_slice2.py tests/test_mdtest.py -k 'Code Blocks or Tabs' -q`

  Expected: FAIL.

- [ ] **Step 2: Implement the code-block leaf path.**

  Add a block-start four-space gate after list recognition. On success emit `CODE_BLOCK`, copy each line after exactly four spaces, retain blank lines inside the block, and close with `TEXT_END` when the next nonblank line has fewer than four spaces; replay that line for the next block decision. In Act IV add a direct `CODE_BLOCK` branch before paragraph/list handling; emit literal `<pre><code>`, scan payload only for `&`, `<`, `>`, emit literal `</code></pre>`, then apply the ordinary sibling-block separator. Do not add a new token code or an inline token.

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  uv run pytest tests/test_act2_slice2.py tests/test_act4_slice2.py tests/test_mdtest.py -k 'Code Blocks or Tabs' -q
  uv run python scripts/strict_parity_harness.py 'Code Blocks' Tabs
  ```

  Expected: all tests pass; strict parity reports `2/2 byte-identical`.

- [ ] **Step 3: Prove the protected boundary and checkpoint.**

  Add a `test_slice2_low_risk.py` assertion that code-block payload bytes containing `\\*`, backticks, and `<http://example.com/>` do not create span HTML, while Act-IV code escaping still converts `<` to `&lt;`. Run the exact literary/generated gate, spike suite, `Amps and angle`/`Horizontal rules`/`Code Blocks`/`Tabs` mdtests, then commit `feat: render indented code blocks` and push.

  Expected: all selected mdtests and all 19 architecture spikes pass.

### Task 4: Promote the accepted code-span and escape machines to full fixtures

**Files:**
- Modify: `src_ir/act3.py` only if a failing full-fixture assertion identifies a state-machine defect
- Modify: `src/30-act3-literary.toml` only if an already-reserved unused Span-Spike label is used
- Modify: `tests/test_mdtest.py`
- Modify: `tests/test_slice2_low_risk.py`

**Interfaces:**
- Code spans use equal maximal backtick runs, trim one balanced outer space pair, and encode only `&`, `<`, `>` in their body.
- Backslash escapes consume exactly the documented punctuation set outside protected regions; protected code and raw inline HTML preserve the backslash semantics demonstrated by the fixture.

- [ ] **Step 1: Enable failing full-fixture coverage.**

  Add `Code Spans` and `Backslash escapes` to `_IMPLEMENTED_FIXTURES` in a local test change. Add focused assertions for the double-backtick literal-backtick case, malformed/unmatched backticks remaining literal, all escaped punctuation, code-span protection, and inline-tag protection. Run both selected mdtests and capture the first failing strict-oracle byte offset in the task evidence.

  Run: `uv run pytest tests/test_mdtest.py -k 'Code Spans or Backslash escapes' -q`

  Expected: FAIL until every fixture edge is covered.

- [ ] **Step 2: Apply only the evidenced Act-III repair.**

  Reproduce each asserted first-difference with an interpreter-level test before changing IR. Keep `LYRIC_CODE_*` and `LYRIC_ESCAPE_*` as protected-region states, preserve the existing `TEXT_END`/borrowed-prefix ownership contract, and use only an unused label from the already accepted Span-Spike literary pool. Do not create a second scanner, pass generated HTML back onto Puck, or broaden link/image behavior.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_mdtest.py -k 'Code Spans or Backslash escapes' -q && uv run python scripts/strict_parity_harness.py 'Code Spans' 'Backslash escapes'`

  Expected: both fixtures pass; strict parity reports `2/2 byte-identical`.

- [ ] **Step 3: Run span-regression gates and checkpoint.**

  Run `uv run pytest tests/test_architecture_spikes.py tests/test_act3_contracts.py tests/test_splc_interpret_parity.py -q`, the exact literary/generated gate, and strict parity for all deterministic fixtures shipped so far. Commit `feat: complete code spans and escapes` and push.

  Expected: all span probes, Act-III contracts, generated checks, and prior fixture gates pass.

### Task 5: Promote URL autolinks without changing email-normalized policy

**Files:**
- Modify: `src_ir/act3.py` only for a fixture-proven URL-autolink defect
- Modify: `src/30-act3-literary.toml` only under the accepted Span-Spike pool rule
- Modify: `tests/test_mdtest.py`
- Modify: `tests/test_slice2_low_risk.py`

**Interfaces:**
- `<http://...>` produces matching href/text values with `&` encoded exactly once; autolinks inside code spans/code blocks remain literal/encoded source, and URL autolinks continue to compose in list and blockquote text.
- Email autolink assertions decode decimal/hex entities through `tests.test_mdtest._decode_entities`; this task must not claim raw byte equality for email output.

- [ ] **Step 1: Add the failing Auto-links acceptance test.**

  Enable `Auto links`, assert the full fixture's URL-only bytes against fresh Markdown.pl after excluding the email-specific raw comparison, and assert `_decode_entities(actual) == _decode_entities(oracle)` for any email probe. Include the list, blockquote, code-span, and indented-code contexts from the fixture.

  Run: `uv run pytest tests/test_mdtest.py -k 'Auto links' -q`

  Expected: FAIL until its composed block contexts match.

- [ ] **Step 2: Repair only the evidenced existing autolink path.**

  Make any needed repair inside `LYRIC_AUTOLINK_*`/field-resume flow so the duplicated href/text field is emitted once per field and both URL ampersands encode once. Keep the `FIELD_AUTO_HREF`/`FIELD_AUTO_TEXT` continuation ownership and existing code/HTML protection; do not add email randomization or a fixture branch.

  Run: `uv run python -m scripts.splc && uv run python scripts/assemble.py && uv run pytest tests/test_mdtest.py -k 'Auto links' -q`

  Expected: PASS using the repository's documented entity-normalized fixture comparison.

- [ ] **Step 3: Verify URL strictness, composition, and checkpoint.**

  Run `uv run python scripts/strict_parity_harness.py 'Auto links'` only as a diagnostic (it may differ on email entity choices), then run a focused URL-only oracle probe plus `uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -k 'Amps and angle or Auto links or Code Spans or Backslash escapes' -q`. Record that Auto links is accepted by entity-normalized mdtest comparison, not raw harness success. Commit `feat: support url autolinks` and push.

  Expected: selected regression tests and spikes pass; no raw-email parity claim is made.

### Task 6: Accept the existing nested list/blockquote composition as Tidyness

**Files:**
- Modify: `src_ir/act2.py` and `src_ir/act4.py` only for a fixture-proven composition defect
- Modify: `src/20-act2-literary.toml` / `src/40-act4-literary.toml` only from their reserved pools
- Modify: `tests/test_mdtest.py`
- Modify: `tests/test_slice2_low_risk.py`

**Interfaces:**
- The established `BLOCKQUOTE_OPEN`, list, item, and close-token grammar emits the exact Tidyness nesting: a paragraph followed by a tight unordered list inside a blockquote, with no unwanted paragraph wrappers or indentation drift.

- [ ] **Step 1: Add the failing Tidyness fixture gate.**

  Enable `Tidyness`, add a decoded-stream assertion for `BLOCKQUOTE_OPEN, PARA, LIST_OPEN(kind=1), LIST_ITEM(looseness=1)×3, LIST_CLOSE, BLOCKQUOTE_CLOSE`, and assert exact Act-IV output bytes.

  Run: `uv run pytest tests/test_mdtest.py -k Tidyness -q`

  Expected: FAIL only if the full fixture exposes a real spike-scope composition gap.

- [ ] **Step 2: Fix the smallest proved stream/frame defect.**

  If the test fails, first add a regression assertion naming the missing/extra token or first output byte. Repair only the existing container pass/frame transition; retain the Spike B sentinel grammar and do not add a fixture-specific output scene. If it passes initially, record that no production IR change was required.

  Run: `uv run pytest tests/test_mdtest.py -k Tidyness -q && uv run python scripts/strict_parity_harness.py Tidyness && uv run pytest tests/test_architecture_spikes.py -q`

  Expected: fixture and spike suite pass; strict parity reports `1/1 byte-identical`.

- [ ] **Step 3: Run exact generated/literary gates when IR changed, then checkpoint.**

  If Step 2 changed IR/prose, run the Global Constraints literary/generated command; otherwise run `uv run pytest tests/test_token_structure.py tests/test_act2_contracts.py tests/test_act2_frame_floors.py -q`. Commit `feat: preserve tidy nested blocks` and push (or `test: enable tidyness fixture` if only tests changed).

### Task 7: Close Slice 2 with the seven-fixture gate, performance record, roadmap update, commit, and push

**Files:**
- Modify: `tests/test_mdtest.py`
- Modify: `tests/test_slice2_low_risk.py`
- Modify: `docs/performance/budget.md`
- Modify: `docs/verification-plan.md`
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: this plan (dated evidence only)

- [ ] **Step 1: Make the seven-fixture mdtest set authoritative.**

  Assert `_IMPLEMENTED_FIXTURES` contains exactly the original `Amps and angle encoding` plus the seven Slice-2 fixture names. Add a test that rejects a skip marker for any of those eight names.

  Run: `uv run pytest tests/test_mdtest.py -k 'Amps and angle or Auto links or Backslash escapes or Code Spans or Tidyness or Tabs or Horizontal rules or Code Blocks' -q`

  Expected: 8 passed, no skip.

- [ ] **Step 2: Run all four Slice-2 verification gates.**

  Run:

  ```bash
  uv run pytest tests/test_mdtest.py -k 'Amps and angle or Auto links or Backslash escapes or Code Spans or Tidyness or Tabs or Horizontal rules or Code Blocks' -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Backslash escapes' 'Code Spans' Tidyness Tabs 'Horizontal rules' 'Code Blocks'
  uv run pytest tests/test_architecture_spikes.py -q
  uv run pytest tests/test_slice2_low_risk.py -q
  ```

  Expected: 8 mdtests and all spikes pass; strict harness reports `7/7 byte-identical` (Amps plus six deterministic Slice-2 fixtures); `Auto links` is separately proven by the entity-normalized mdtest assertion; no test reveals an oracle stub.

- [ ] **Step 3: Run full verification and record measured evidence.**

  Run `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run pyright`. Record in `docs/performance/budget.md` and `docs/verification-plan.md`: generated line/scene counts per act, first-run and median time for `Tabs` and `Code Blocks`, xdist shipped-fixture regression wall time, and the yellow/red-threshold projection. Add the exact command results and date to this plan.

  Expected: all commands exit zero. A red threshold or two-plan projection triggers the architecture §8.2 halt rule rather than a performance workaround.

- [ ] **Step 4: Mark the slice shipped and checkpoint.**

  Mark roadmap row 5 `shipped: <date> at commit <sha>` only after Steps 1–3 are green; leave row 6 pending and leave no other in-flight row. Commit `feat: complete low risk markdown fixtures`, push, then amend the row with the actual resulting SHA in a follow-up `docs:` commit and push. If either push fails, append one `- BLOCK:` line and stop.

## Plan self-review

- Coverage: preprocessing/detab (Tasks 1 and 3), HR (Task 2), code leaves/Tabs (Task 3), accepted protected spans and escapes (Task 4), URL autolinks plus email comparison policy (Task 5), nested composition/Tidyness (Task 6), and all §8.1 gates/performance/roadmap closure (Task 7).
- No new architecture/spec is needed: the durable architecture and accepted span design are sufficient; this plan does not alter their ownership or scan model.
- No placeholders: every planned production file, interface, fixture, selection command, strict-parity exception, literary pool, and stop condition is explicit. The only conditional code changes are deliberately evidence-gated to avoid speculative repair of accepted Spike B/Span machinery.
