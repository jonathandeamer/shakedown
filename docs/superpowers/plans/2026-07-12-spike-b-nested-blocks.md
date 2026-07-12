# Spike B — Nested Blockquote-In-List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that the four-act SPL pipeline can emit byte-identical Markdown.pl HTML for a blockquote inside a list and a list inside a blockquote, with valid explicit container streams.

**Architecture:** Implement the accepted explicit-item grammar in [the Spike B design](../specs/2026-07-12-spike-b-nested-blocks-design.md): `LIST_ITEM(looseness)` opens an item, `ITEM_CLOSE` closes it, and blockquotes are bracketed block containers. Act II owns recognition and bracketed stream construction; Acts III and IV preserve and consume that stream. The validation interpreter, committed dumps, and oracle-backed fixtures form independent structural and rendered-output gates.

**Tech Stack:** Python 3.12 typed splc IR, generated SPL fragments, TOML-controlled literary surfaces, pytest, Markdown.pl oracle, `shakespearelang`.

## Global Constraints

- First read `docs/superpowers/plans/plan-roadmap.md`, architecture §6.3/§7.4/§8.2, and the accepted design above; this is the sole in-flight plan.
- Do not hand-edit `src/20-act2-block.spl`, `src/30-act3-span.spl`, `src/40-act4-emit.spl`, `debug/40-act4-token-dump.spl`, or `shakedown.spl`; edit IR/TOML, then run `uv run python -m scripts.splc` and `uv run python scripts/assemble.py`.
- Follow `docs/superpowers/notes/spl-literary-protocol.md`: classify all new prose, take titles only from the reservations below, and run the exact literary gates listed in Task 2.
- Preserve all allocated token numbers. `LIST_ITEM` remains code 5 but changes to an item-open with one looseness payload and no text; `ITEM_CLOSE` is code 15 with no payload/text.
- Do not broaden scope to headers, code blocks, raw HTML, ordered markers, multiple quote depths, or full list semantics.
- At every task boundary run its evidence gate; commit only the task's files with a conventional subject and the required MCO provenance trailers, then push without force. On push failure append one `- BLOCK:` line to `.agent/blockers.md` and exit.

## File map

| Path | Responsibility |
|---|---|
| `src_ir/tokens.py` | Token constants, lexical arity, and structural roles. |
| `docs/spl/token-codes.md` | Human-readable canonical code and arity contract. |
| `scripts/splc/token_structure.py` | Verification-only recursive stream validator. |
| `src_ir/act2.py` | Container-aware list/blockquote recognition and paragraph tokenization. |
| `src_ir/act4.py` | Explicit item/container-stack HTML emitter. |
| `src/20-act2-literary.toml`, `src/40-act4-literary.toml` | Controlled titles for Act II/IV scenes. |
| `tests/fixtures/architecture_spikes/nested_blocks/*.text` | Four minimal Markdown inputs. |
| `tests/fixtures/token_stream/nested_blocks/*.dump` | Reviewed integer streams for those inputs. |
| `tests/test_architecture_spikes.py`, `tests/test_token_dump.py` | Oracle parity and dump-baseline parametrization. |
| `tests/test_token_structure.py`, `tests/test_token_codes.py` | Grammar and token-table coverage. |
| `tests/test_act2_contracts.py`, `tests/test_act2_frame_floors.py` | Borrowed-stack safety over the new corpus. |

## Literary reservations (ready to paste)

These are **controlled scene-title surfaces**. Add only labels actually used by the IR; retain the marked spare pool for structural surprises. They are Act II Martial/Catastrophic and Act IV Noble/Radiant, comply with the existing title patterns, and introduce no new Recall or Stable Utility prose.

```toml
# src/20-act2-literary.toml
[scenes.PASS_CONTAINERS_OPEN]
title = "Lady Macbeth opens the inner field."
pattern = "scene_of_character"
[scenes.PASS_CONTAINERS_QUOTE]
title = "Hecate bears the dark reply within."
pattern = "scene_of_character"
[scenes.PASS_CONTAINERS_CLOSE]
title = "Macbeth seals the folded rampart."
pattern = "scene_of_character"
[scenes.PASS_PARA_ITEM_OPEN]
title = "Lady Macbeth names the soldier's chamber."
pattern = "scene_of_character"
[scenes.PASS_PARA_ITEM_CLOSE]
title = "Macbeth lowers the inner standard."
pattern = "scene_of_character"

# Spare pool — do not use unless an extra generated scene is necessary.
[scenes.PASS_CONTAINERS_BOUNDARY]
title = "The outer field receives the broken line."
pattern = "bare_statement"
[scenes.PASS_CONTAINERS_REPLAY]
title = "The herald returns the guarded word."
pattern = "scene_of_character"
[scenes.PASS_CONTAINERS_DEPTH]
title = "Macbeth counts the inward marches."
pattern = "scene_of_character"
[scenes.PASS_CONTAINERS_EOF]
title = "The last rampart yields to silence."
pattern = "bare_statement"
```

```toml
# src/40-act4-literary.toml
[scenes.SCRIBE_ITEM_BLOCK_OPEN]
title = "Prospero grants the chamber its first seal."
pattern = "scene_of_character"
[scenes.SCRIBE_ITEM_BLOCK_CLOSE]
title = "Prospero releases the chamber's last seal."
pattern = "scene_of_character"
[scenes.SCRIBE_BLOCKQUOTE_OPEN]
title = "Prospero raises the inward pavilion."
pattern = "scene_of_character"
[scenes.SCRIBE_BLOCKQUOTE_CLOSE]
title = "Prospero lowers the inward pavilion."
pattern = "scene_of_character"
[scenes.SCRIBE_ITEM_CLOSE]
title = "Prospero seals the soldier's chamber."
pattern = "scene_of_character"

# Spare pool — do not use unless an extra generated scene is necessary.
[scenes.SCRIBE_CONTAINER_LOOKAHEAD]
title = "Prospero keeps the next bright measure."
pattern = "scene_of_character"
[scenes.SCRIBE_CONTAINER_RETURN]
title = "Prospero restores the waiting seal."
pattern = "scene_of_character"
[scenes.SCRIBE_QUOTED_PARAGRAPH]
title = "Prospero inscribes the inward chamber."
pattern = "scene_of_character"
[scenes.SCRIBE_OUTER_RELEASE]
title = "Prospero frees the outer procession."
pattern = "scene_of_character"
```

---

### Task 1: Lock the explicit container-stream contract

**Files:**
- Modify: `src_ir/tokens.py`
- Modify: `docs/spl/token-codes.md`
- Modify: `scripts/splc/token_structure.py`
- Modify: `tests/test_token_codes.py`
- Modify: `tests/test_token_structure.py`

**Consumes:** Existing codes 1–14 and `StructuralRole`.

**Produces:** `ITEM_CLOSE = 15`; a decoder/validator accepting the exact grammar in the design and rejecting crossed, unclosed, empty, or item-outside-list streams.

- [x] **Step 1: Write grammar and lexical failure tests.**

  Add a valid list-with-quote sequence and these rejection cases to `tests/test_token_structure.py`:

  ```python
  valid = [
      tokens.LIST_OPEN, 1, tokens.LIST_ITEM, 1,
      tokens.PARA, ord("a"), tokens.TEXT_END,
      tokens.BLOCKQUOTE_OPEN, tokens.PARA, ord("b"), tokens.TEXT_END,
      tokens.BLOCKQUOTE_CLOSE, tokens.ITEM_CLOSE, tokens.LIST_CLOSE,
  ]
  validate_stream(decode_stream(valid))

  with pytest.raises(StructuralError, match="item close has no matching open item"):
      validate_stream(decode_stream([tokens.ITEM_CLOSE]))
  ```

  Update the target-grammar transcription to `LIST_ITEM(looseness) block* ITEM_CLOSE`; assert BLOCKQUOTE_OPEN/CLOSE and ITEM_CLOSE are in `ARITY` and possess the correct roles.

- [ ] **Step 2: Run the new tests to verify they fail.**

  Run: `uv run pytest tests/test_token_structure.py tests/test_token_codes.py -q`  
  Expected: FAIL because `ITEM_CLOSE` and the shipped blockquote/item grammar do not exist.

- [ ] **Step 3: Implement the contract, without changing generated SPL.**

  In `src_ir/tokens.py`, make these rows exact:

  ```python
  ITEM_CLOSE = 15

  ARITY = {
      PARA: TokenArity(0, True),
      LIST_OPEN: TokenArity(1, False),
      LIST_ITEM: TokenArity(1, False),
      LIST_CLOSE: TokenArity(0, False),
      BLOCKQUOTE_OPEN: TokenArity(0, False),
      BLOCKQUOTE_CLOSE: TokenArity(0, False),
      ITEM_CLOSE: TokenArity(0, False),
  }
  ```

  Add `StructuralRole.ITEM_CLOSE`; rewrite `validate_stream()` around a stack of
  `("list", has_item)` and `("item", looseness)` frames. Permit `PARA`, list,
  and blockquote only where a block is legal; require the top frame to match
  every close; require an item before each list close. Update the code-allocation
  table and its arity table with code 15's canonical phrase
  ``the sum of a big big big cat and the sum of a big big cat and a cat``.

- [ ] **Step 4: Run contract evidence.**

  Run: `uv run pytest tests/test_token_codes.py tests/test_token_decode.py tests/test_token_structural_roles.py tests/test_token_structure.py -q`  
  Expected: PASS.

- [ ] **Step 5: Commit and push the token contract.**

  Run: `git add src_ir/tokens.py docs/spl/token-codes.md scripts/splc/token_structure.py tests/test_token_codes.py tests/test_token_structure.py tests/test_token_structural_roles.py && git commit -m "feat: define nested container stream contract"`  
  Expected: conventional commit succeeds; append the required provenance trailers, then `git push` succeeds.

### Task 2: Add the Spike B corpus, reservations, and structural baselines

**Files:**
- Create: `tests/fixtures/architecture_spikes/nested_blocks/list_quote_sibling.text`
- Create: `tests/fixtures/architecture_spikes/nested_blocks/quote_list_then_paragraph.text`
- Create: `tests/fixtures/architecture_spikes/nested_blocks/loose_list_quote.text`
- Create: `tests/fixtures/architecture_spikes/nested_blocks/closes_to_text.text`
- Create: `tests/fixtures/token_stream/nested_blocks/*.dump`
- Modify: `tests/test_architecture_spikes.py`
- Modify: `tests/test_token_dump.py`
- Modify: `tests/test_act2_contracts.py`
- Modify: `tests/test_act2_frame_floors.py`
- Modify: `src/20-act2-literary.toml`
- Modify: `src/40-act4-literary.toml`

**Consumes:** Task 1's parser and the reserved titles above.

**Produces:** Four permanent Spike B no-regression fixtures, mechanically validated reviewed streams, and all required prose before IR changes.

- [ ] **Step 1: Create the fixture files and parametrize all Spike B checks.**

  Write the exact Markdown from the design table. Add `NESTED_BLOCK_FIXTURES`, a
  `_nested_block_cases()` glob helper, and a second oracle-backed parametrized
  test in `tests/test_architecture_spikes.py`; do not weaken list-fixture tests.
  Include the same stems in token-dump and both Act II contract parametrizations.

- [ ] **Step 2: Add the reserved TOML titles exactly as supplied above.**

  Add the five active and four spare entries per touched act. Do not put scene
  prose in `src/literary.toml` or inline it in an IR module.

- [ ] **Step 3: Write literal reviewed dump fixtures before implementation.**

  Encode the four design-table streams one integer per line. For example
  `quote_list_then_paragraph.dump` begins:

  ```text
  7
  4
  1
  5
  1
  1
  97
  108
  112
  104
  97
  0
  15
  ```

  Finish each stream exactly as its design-table row specifies, ending in `-1`.

- [ ] **Step 4: Run pre-implementation evidence.**

  Run: `uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py tests/test_act2_contracts.py tests/test_act2_frame_floors.py -q`  
  Expected: structural baseline tests PASS; new real-runtime/oracle tests FAIL until Tasks 3–4 implement the behavior.

- [ ] **Step 5: Run required literary compliance evidence.**

  Run: `uv run pytest tests/test_literary_toml_schema.py tests/test_literary_compliance.py tests/test_spl_style_guide_validation.py tests/test_splc_prose.py -q`  
  Expected: PASS; this is the exact literary-protocol gate for the new TOML surfaces.

- [ ] **Step 6: Commit and push the corpus and reservations.**

  Run: `git add tests/fixtures tests/test_architecture_spikes.py tests/test_token_dump.py tests/test_act2_contracts.py tests/test_act2_frame_floors.py src/20-act2-literary.toml src/40-act4-literary.toml && git commit -m "test: add nested block spike corpus"`  
  Expected: conventional commit and provenance trailers succeed, followed by a successful `git push`.

### Task 3: Emit valid nested-container streams from Act II

**Files:**
- Modify: `src_ir/act2.py`
- Modify: `tests/test_act2_contracts.py`
- Modify: `tests/test_act2_frame_floors.py`
- Modify: `tests/test_token_dump.py`
- Regenerate: `src/20-act2-block.spl`
- Regenerate: `shakedown.spl`

**Consumes:** Task 1 grammar, Task 2 fixture/dump contract, and only the active/spare Act II titles reserved above.

**Produces:** Valid final streams for all old list and new nested-block fixtures; no borrowed-stack prefix is altered.

- [ ] **Step 1: Add Act-II interpreter tests that compare the final carrier stream with each reviewed dump.**

  Add a helper that runs Act I then Act II with `scripts.splc.interpret.run_act`,
  pops Puck's stream in document order through `STREAM_END`, and compares it to
  `tests/fixtures/token_stream/nested_blocks/<stem>.dump`. Include a test that
  passes the resulting integers through `decode_stream` and `validate_stream`.

- [ ] **Step 2: Run the focused interpreter tests to verify failure.**

  Run: `uv run pytest tests/test_token_dump.py tests/test_act2_contracts.py tests/test_act2_frame_floors.py -q`  
  Expected: FAIL because current Act II emits text-bearing implicit list items and no blockquote tokens.

- [ ] **Step 3: Replace implicit item text framing with recursive container frames.**

  In `src_ir/act2.py`:

  ```python
  # emitted ordering for every item
  emit_token(carrier, tokens.LIST_ITEM, looseness)
  # then zero or more PARA/list/blockquote child blocks
  emit_token(carrier, tokens.ITEM_CLOSE)

  # emitted ordering for a quote child
  emit_token(carrier, tokens.BLOCKQUOTE_OPEN)
  # recursively scheduled child blocks
  emit_token(carrier, tokens.BLOCKQUOTE_CLOSE)
  ```

  Preserve the `STREAM_END` floors and existing carrier partition. A quote line
  is recognized only at the current container line head (`>` followed by an
  optional space); strip exactly that prefix. An unquoted line closes quote
  frames; a sibling marker closes the current item before opening the next one.
  Paragraph formation must emit `PARA ... TEXT_END` inside items/quotes and
  must copy structural codes untouched. Use only the reserved scene labels.

- [ ] **Step 4: Regenerate and assemble.**

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  ```

  Expected: generated-fragment and assemble-time parser gates succeed; no generated file is manually edited.

- [ ] **Step 5: Run Act II and generated-artifact gates.**

  Run: `uv run pytest tests/test_act2_contracts.py tests/test_act2_frame_floors.py tests/test_token_structure.py tests/test_token_dump.py tests/test_splc_generated_fragments.py -q`  
  Expected: PASS. Replace all six existing list dump baselines in this task
  with the explicit-item representation, hand-review each against the same
  grammar, and record that deliberate G2 vocabulary migration in its commit.

- [ ] **Step 6: Commit and push the block-parser result.**

  Run: `git add src_ir/act2.py src/20-act2-block.spl shakedown.spl tests && git commit -m "feat: emit nested block container streams"`  
  Expected: conventional commit and provenance trailers succeed, followed by `git push`.

### Task 4: Render explicit items and blockquotes in Act IV

**Files:**
- Modify: `src_ir/act4.py`
- Modify: `tests/test_architecture_spikes.py`
- Modify: `tests/test_token_dump.py`
- Regenerate: `src/40-act4-emit.spl`
- Regenerate: `debug/40-act4-token-dump.spl`
- Regenerate: `shakedown.spl`

**Consumes:** Task 3's valid streams and the Act IV reservations.

**Produces:** Byte-identical Markdown.pl output for the four nested cases and no regression in six shipped list cases.

- [ ] **Step 1: Add emitter-facing byte assertions before implementation.**

  Keep oracle comparison as the authority and add direct expected-byte tests for
  the four snippets, including the necessary list/blockquote separators:

  ```python
  assert _run([str(SHAKEDOWN)], b"> * alpha\n> * bravo\n>\n> charlie\n") == (
      b"<blockquote>\n  <ul>\n<li>alpha</li>\n<li>bravo</li>\n</ul>\n\n"
      b"<p>charlie</p>\n</blockquote>\n"
  )
  ```

- [ ] **Step 2: Run renderer tests to verify they fail.**

  Run: `uv run pytest tests/test_architecture_spikes.py -q`  
  Expected: FAIL on all nested-block cases while the current emitter has no blockquote dispatch.

- [ ] **Step 3: Implement stack-driven container emission.**

  Replace the implicit-list-lookahead flow in `src_ir/act4.py` with dispatch for
  `LIST_OPEN`, `LIST_ITEM`, `ITEM_CLOSE`, `LIST_CLOSE`, `BLOCKQUOTE_OPEN`, and
  `BLOCKQUOTE_CLOSE`. Track container kind and item looseness on Prospero's
  stack above a sentinel; emit `\n`/`\n\n` based on sibling block boundaries,
  never on raw text. Preserve existing `PARA` and anchor paths. The four
  required byte layouts are the oracle outputs in Task 2's fixture tests.

- [ ] **Step 4: Regenerate and assemble.**

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  ```

  Expected: parser gate succeeds and generated fragments are fresh.

- [ ] **Step 5: Run spike and no-regression gates.**

  Run: `uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py tests/test_token_structure.py tests/test_splc_generated_fragments.py -q`  
  Expected: PASS; all ten architecture-spike fixtures are byte-identical and every dump validates.

- [ ] **Step 6: Commit and push renderer support.**

  Run: `git add src_ir/act4.py src/40-act4-emit.spl debug/40-act4-token-dump.spl shakedown.spl tests && git commit -m "feat: render nested block containers"`  
  Expected: conventional commit and provenance trailers succeed, followed by `git push`.

### Task 5: Finalize the spike evidence and roadmap state

**Files:**
- Modify: `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` when the measured outcome changes a durable decision
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: `docs/verification-plan.md` only for new measured evidence

**Consumes:** Passing Tasks 1–4.

**Produces:** A recorded pass or a documented halt-and-redesign result; no silent transition to the span spike.

- [ ] **Step 1: Run the complete required verification set.**

  Run:

  ```bash
  uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py \
    tests/test_token_structure.py tests/test_act2_contracts.py \
    tests/test_act2_frame_floors.py tests/test_splc_generated_fragments.py -q
  uv run pytest tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
  uv run pytest
  ```

  Expected: all commands PASS. The first command proves structural streams,
  borrowed-stack safety, generated artifacts, and oracle parity; the second
  proves assembly/codegen and the retained Slice-1 fixture; the third is the
  full default regression gate.

- [ ] **Step 2: Re-run exact literary compliance after regenerated SPL.**

  Run: `uv run pytest tests/test_literary_toml_schema.py tests/test_literary_compliance.py tests/test_spl_style_guide_validation.py tests/test_splc_prose.py -q`  
  Expected: PASS.

- [ ] **Step 3: Record the outcome.**

  If all gates pass, obtain the commit identifier with `git rev-parse HEAD`,
  mark row 4 `shipped: 2026-07-12 at commit` followed by that identifier, and
  clear the in-flight path. If any composition case fails, append one `- BLOCK:` line
  to `.agent/blockers.md`, preserve the failing dump/fixture evidence, and
  revise the architecture's container grammar and recursive scheduling before
  planning further work; do not advance to row 4S.

- [ ] **Step 4: Commit and push the verified outcome.**

  Run: `git add docs .agent/blockers.md && git commit -m "docs: record Spike B outcome"`  
  Expected: commit only when documentation/blocker content changed, with the required provenance trailers, then a successful `git push`.

## Plan self-review

- **Coverage:** Tasks 1–4 implement every §7.4 acceptance case, explicit streams,
  fixture parity, Act II/IV composition, and literary reservations; Task 5 owns
  the §8.2 halt path and full suite.
- **No placeholders:** every planned token number, fixture, stream, title,
  test path, command, and expected gate is named.
- **Consistency:** `LIST_ITEM` is the explicit item opening throughout; code 15
  is `ITEM_CLOSE`; blockquotes are codes 7/8 with zero payloads.
