# Span Architecture Spike Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish and prove Act III's protected-region, buffered-scan shape for code spans, escapes, HTML, links/images, and representative strong/emphasis before Slice 2 expands span behavior.

**Architecture:** Follow [the accepted span design](../specs/2026-07-12-span-architecture-spike-design.md): Act III copies the structural stream but reads each eligible paragraph into a private, floor-bounded source buffer and writes final glyphs once to Juliet. Protected regions are scanner modes rather than persistent inline tokens; output HTML is never treated as later Markdown input. Oracle-backed probe fixtures and reviewed debug dumps are both gates.

**Tech Stack:** Python 3.12 typed splc IR, generated SPL fragments, TOML-controlled literary surfaces, pytest, local Markdown.pl v1.0.1 oracle, shakespearelang.

## Global Constraints

- First read `docs/superpowers/plans/plan-roadmap.md`, architecture §4.3/§7.5/§8.2, the accepted design above, `docs/markdown/oracle-mechanics.md`, and `docs/superpowers/notes/spl-literary-protocol.md`; this is the sole in-flight plan.
- Before SPL-facing edits read `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`, `docs/spl/codegen-style-guide.md`, and `src/literary.toml`. New Act III prose is controlled TOML-owned prose; use only the reservations below.
- Do not hand-edit `src/30-act3-span.spl`, `debug/40-act4-token-dump.spl`, or `shakedown.spl`. Edit `src_ir/*.py` and `src/30-act3-literary.toml`, then run `uv run python -m scripts.splc` and `uv run python scripts/assemble.py`.
- Do not add final inline token codes, change the accepted list/blockquote grammar, widen mdtest's shipped-fixture set, implement reference links, or broaden the scope to general HTML-block, hard-break, or full image/title syntax beyond the named probes.
- The exact literary compliance gate after every Act III/TOML change is: `uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q`.
- At each task boundary run its evidence gate; make a small conventional commit with the required MCO provenance trailers, then `git push`. If pushing fails, append one `- BLOCK:` line to `.agent/blockers.md` and exit without force-pushing.

## File map

| Path | Responsibility |
|---|---|
| `src_ir/act3.py` | Buffered source-region scan, protected-region dispatch, and Act III carrier-floor choreography. |
| `src/30-act3-literary.toml` | Every newly generated Act III scene title and Recall phrase. |
| `tests/fixtures/architecture_spikes/spans/*.text` | Five narrowly scoped Markdown inputs. |
| `tests/fixtures/architecture_spikes/spans/*.expected` | Fresh Markdown.pl byte contracts. |
| `tests/fixtures/token_stream/spans/*.dump` | Reviewed final Act-III streams, one integer per line including terminal `STREAM_END`. |
| `tests/test_architecture_spikes.py` | Oracle and literal-byte probe parity. |
| `tests/test_token_dump.py` | Debug-target baselines and interpreter carrier/sentinel checks. |
| `tests/test_act3_contracts.py` | Act-III interpreter-level protected-region and borrowed-stack contracts. |
| `tests/test_splc_interpret_parity.py` | Generated-SPL/interpreter parity coverage when new control-flow shapes require it. |

## Literary reservations (ready to paste)

These are Act III pastoral/natural controlled titles and Recall surfaces. Add
only the labels and keys actually used in the IR. The four marked spares are
pre-approved for a necessary additional scene; if they are exhausted, stop
instead of inventing prose. No new Critical or Stable Utility phrase is
needed.

```toml
# src/30-act3-literary.toml
[scenes.LYRIC_BUFFER_OPEN]
title = "Romeo gathers the unspent morning line."
pattern = "scene_of_character"
[scenes.LYRIC_CODE_RUN]
title = "Juliet shelters the silver backtick measure."
pattern = "scene_of_character"
[scenes.LYRIC_ESCAPE_GLYPH]
title = "Romeo frees one guarded garden mark."
pattern = "scene_of_character"
[scenes.LYRIC_HTML_TAG]
title = "Juliet keeps the moonlit tag whole."
pattern = "scene_of_character"
[scenes.LYRIC_LINK_REGION]
title = "Romeo binds the rose to its bright path."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_STRONG]
title = "Juliet lays the star within the sunlit seal."
pattern = "scene_of_character"
[scenes.LYRIC_BUFFER_CLOSE]
title = "The lovers return the finished line."
pattern = "cross_character"

[characters.romeo.recall]
buffered_first_glyph = "Recall the morning buffer's first glyph."
protected_run_measure = "Recall the guarded measure."
link_label_mark = "Recall the bound rose's mark."
[characters.juliet.recall]
buffered_last_glyph = "Recall the night's final glyph."
protected_tag_mark = "Recall the silver tag's mark."

# Spare pool — do not use unless an extra generated scene is necessary.
[scenes.LYRIC_BUFFER_FALLBACK]
title = "The loose rose returns to daylight."
pattern = "bare_statement"
[scenes.LYRIC_PROTECTED_CLOSE]
title = "Juliet closes the guarded silver path."
pattern = "scene_of_character"
[scenes.LYRIC_LABEL_REPLAY]
title = "Romeo sends the bound petals onward."
pattern = "scene_of_character"
[scenes.LYRIC_EMPHASIS_FALLBACK]
title = "The unpaired star remains in the garden."
pattern = "bare_statement"
```

---

### Task 1: Commit the span-spike corpus and reviewed expected output

**Files:**
- Create: `tests/fixtures/architecture_spikes/spans/variable_code_spans.text`
- Create: `tests/fixtures/architecture_spikes/spans/escapes_and_overlap.text`
- Create: `tests/fixtures/architecture_spikes/spans/inline_html_and_autolink.text`
- Create: `tests/fixtures/architecture_spikes/spans/links_images_protected.text`
- Create: `tests/fixtures/architecture_spikes/spans/overlapping_emphasis.text`
- Create: `tests/fixtures/architecture_spikes/spans/*.expected`
- Modify: `tests/test_architecture_spikes.py`

**Consumes:** The accepted design's probe table and local `~/markdown/Markdown.pl`.

**Produces:** Five permanent, byte-exact source/output contracts that fail against the pre-spike production runtime without changing it.

- [x] **Step 1: Add the exact source fixtures.**

  Create the five `.text` files with precisely these bytes (each final newline is significant):

  ```text
  variable_code_spans: `` a ` b `` and `x & <y>`\n
  escapes_and_overlap: \*literal* and \[bracket\] \`tick\` and ***both***\n
  inline_html_and_autolink: <span>*raw*</span> and <http://example.com/a?x=1&y=2>\n
  links_images_protected: [a *b*](http://e/x_(y) "t") and ![c *d*](img.png "i")\n
  overlapping_emphasis: ***both*** and **outer *inner* outer**\n
  ```

- [x] **Step 2: Generate and review oracle expectations.**

  For every `.text`, run `perl ~/markdown/Markdown.pl < <fixture> > <fixture>.expected`; inspect the resulting bytes. In particular, assert the expected output contains `<code>a \` b</code>`, `<code>x &amp; &lt;y&gt;</code>`, literal `*literal*`, `<span><em>raw</em></span>`, a once-encoded autolink query ampersand, `<img src="img.png" alt="c <em>d</em>" title="i" />`, and `<strong><em>both</em></strong>`.

- [x] **Step 3: Add direct probe tests.**

  In `tests/test_architecture_spikes.py`, add `SPAN_FIXTURES`, `_span_cases()`, and a parametrized test that loads each `.text` and `.expected`, runs both `./shakedown` and `perl ~/markdown/Markdown.pl`, and requires both outputs equal the checked-in expected bytes. Reuse `_first_diff()` so a mismatch reports its byte index. Do not route this assertion through mdtest normalization.

- [x] **Step 4: Run the red gate.**

  Run: `uv run pytest tests/test_architecture_spikes.py -k span -q`  
  Expected: FAIL for all new span cases on the current Act III behavior; existing list and nested-block spike cases remain PASS.

- [ ] **Step 5: Commit and push the corpus.**

  Run: `git add tests/fixtures/architecture_spikes/spans tests/test_architecture_spikes.py && git commit -m "test: add span architecture spike corpus"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding.

### Task 2: Scaffold the buffered carrier contract before production scanning

**Files:**
- Create: `tests/test_act3_contracts.py`

**Consumes:** Task 1 fixture names; `ACT1`, `ACT2`, `ACT3`, `run_act`, `decode_stream`, and `validate_stream`.

**Produces:** Executable proof scaffolding that Act III retains exactly one `STREAM_END`, exposes a valid block stream, and provides a stable comparison point for the private scan floor. Task 4 adds reviewed final dumps only after the implementation exists.

- [ ] **Step 1: Write interpreter helpers and failing contracts.**

  Add `_run_to_act3(stem: str) -> InterpreterState` that feeds the fixture text through `ACT1`, `ACT2`, and `ACT3` with `STEP_LIMIT = 200_000`; add `_carrier_stream(state) -> list[int]` that pops Puck through the sole terminal `STREAM_END`. Assert `stream.count(tokens.STREAM_END) == 1`, `decode_stream(stream[:-1])` succeeds, and `validate_stream(...)` accepts it. Add a parameterized test that records the pre-scan paragraph stream and proves non-text structural tokens/payloads remain unchanged across Act III; keep the expected rendered text deliberately failing until Task 3.

- [ ] **Step 2: Run the contract tests to verify failure.**

  Run: `uv run pytest tests/test_act3_contracts.py -q`  
  Expected: structural-prefix assertions PASS, while expected rendered-region assertions FAIL because current Act III cannot produce the protected-region contracts.

- [ ] **Step 3: Assert the floor/prefix boundary.**

  Instrument only the IR-interpreter-facing test helper (not production SPL) to retain the carrier prefix before calling `ACT3`; assert that the prefix beneath the planned private floor is byte-for-byte equal after the act exits. Assert the final stream carries no leaked `ITEM_START` marker and no extra `STREAM_END`.

- [ ] **Step 4: Run the structural evidence.**

  Run: `uv run pytest tests/test_act3_contracts.py tests/test_token_decode.py tests/test_token_structure.py -q`  
  Expected: prefix/stream-shape assertions PASS; intentionally expected span-output assertions remain red until Task 3.

- [ ] **Step 5: Commit and push the carrier contract.**

  Run: `git add tests/test_act3_contracts.py && git commit -m "test: scaffold span carrier contracts"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding.

### Task 3: Implement the one-way buffered scan for code spans and escapes

**Files:**
- Modify: `src_ir/act3.py`
- Modify: `src/30-act3-literary.toml`
- Regenerate: `src/30-act3-span.spl`
- Regenerate: `shakedown.spl`

**Consumes:** Task 1's red corpus, Task 2's contracts, and only the active/spare Act III prose above.

**Produces:** A floor-bounded source buffer that supports variable-length code spans and escaped punctuation without feeding generated output back into the scan; Amps remains byte-identical.

- [ ] **Step 1: Add the minimum IR tests before changing the scanner.**

  In `tests/test_act3_contracts.py`, assert `variable_code_spans` has exactly two `<code>` regions with `<code>a \` b</code>` and `<code>x &amp; &lt;y&gt;</code>` in its decoded paragraph text; assert `escapes_and_overlap` retains literal `*literal*`, `[bracket]`, and `` `tick` ``. Assert that the carrier below the temporary scan-floor sentinel matches the pre-scan prefix exactly.

- [ ] **Step 2: Run the focused red gate.**

  Run: `uv run pytest tests/test_act3_contracts.py tests/test_architecture_spikes.py -k 'span or act3' -q`  
  Expected: FAIL because the existing `LYRIC_POP_GLYPH` path has no variable-run or escape buffering.

- [ ] **Step 3: Replace direct glyph dispatch with the bounded scanner.**

  In `src_ir/act3.py`, preserve `_traverse_dispatch()` and route `TRAVERSE_OPEN_TEXT` to scenes that: (1) push one private floor sentinel above the borrowed carrier prefix; (2) drain the entire paragraph until `TEXT_END` into the source buffer; (3) consume a maximal backtick run and seek only a same-length closing run; (4) emit `<code>`/`</code>` and encoded code content directly to Juliet; (5) consume `\\` plus an escapable punctuation glyph as one literal output glyph; and (6) drain the source floor exactly once before writing `TEXT_END` and returning to traversal. Any unmatched opener falls back byte-for-byte to literal source output. Keep structural codes/payloads on the existing copy path. Use only `LYRIC_BUFFER_OPEN`, `LYRIC_CODE_RUN`, `LYRIC_ESCAPE_GLYPH`, and `LYRIC_BUFFER_CLOSE` plus the reserved Recall keys actually referenced.

- [ ] **Step 4: Regenerate, assemble, and run focused evidence.**

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  uv run pytest tests/test_splc_generated_fragments.py tests/test_act3_contracts.py tests/test_architecture_spikes.py -k 'variable_code_spans or escapes_and_overlap or Amps or act3' -q
  uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
  ```

  Expected: generated artifacts are fresh; code-span and escape assertions pass; Amps remains byte-identical; HTML/link/image/overlap probe cases may still fail.

- [ ] **Step 5: Commit and push the scanner foundation.**

  Run: `git add src_ir/act3.py src/30-act3-literary.toml src/30-act3-span.spl shakedown.spl tests/test_act3_contracts.py && git commit -m "feat: add buffered code-span scanner"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding.

### Task 4: Add protected HTML/link/image regions and strong-then-emphasis output

**Files:**
- Modify: `src_ir/act3.py`
- Modify: `src/30-act3-literary.toml`
- Modify: `tests/test_act3_contracts.py`
- Create: `tests/fixtures/token_stream/spans/*.dump`
- Modify: `tests/test_token_dump.py`
- Regenerate: `src/30-act3-span.spl`
- Regenerate: `shakedown.spl`

**Consumes:** Task 3 scanner and Task 1's remaining probe contracts.

**Produces:** Protected tags/destinations/titles, child label/alt scans, and representative nested strong/emphasis output under the one-way scan invariant.

- [ ] **Step 1: Extend failing contracts for every protected mode.**

  Add assertions that the decoded output for `inline_html_and_autolink` contains literal `<span><em>raw</em></span>` and exactly one `&amp;` in the autolink query; `links_images_protected` contains `<a href="http://e/x_(y)" title="t">a <em>b</em></a>` and `<img src="img.png" alt="c <em>d</em>" title="i" />`; and `overlapping_emphasis` contains both exact expected strong/em nesting sequences. Add a negative assertion that no generated output is placed back on the source-buffer stack.

- [ ] **Step 2: Implement the remaining scanner modes in oracle order.**

  Extend the Task 3 scenes so `<...>` distinguishes a literal inline HTML tag from an HTTP/HTTPS/FTP autolink; tags copy as opaque source bytes, while autolink URLs receive amp/angle encoding once. Parse the exact balanced probe link/image forms: bracketed label/alt text is recursively scanned as source text, `http://e/x_(y)` is retained verbatim as an opaque destination, and quoted titles remain opaque. Then apply amp/angle encoding, strong substitution, and emphasis substitution only to ordinary/child-label source regions, with strong before emphasis. Use only `LYRIC_HTML_TAG`, `LYRIC_LINK_REGION`, `LYRIC_EMPHASIS_STRONG`, and already reserved spare labels/Recall keys actually needed. Do not add general reference resolution or unsupported delimiter grammar.

- [ ] **Step 3: Regenerate and run all spike evidence.**

  Run:

  ```bash
  uv run python -m scripts.splc
  uv run python scripts/assemble.py
  uv run pytest tests/test_architecture_spikes.py tests/test_act3_contracts.py tests/test_token_dump.py tests/test_token_decode.py tests/test_token_structure.py -q
  uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py tests/test_mdtest.py -k 'Amps and angle' -q
  ```

  Expected: all five span probes, every reviewed span dump, existing list/nested-block spikes, and Amps pass.

- [ ] **Step 4: Record and enforce reviewed final dumps.**

  Capture the exact `shakedown-debug` output for every probe, append `-1` as the carrier sentinel in `tests/fixtures/token_stream/spans/<stem>.dump`, and hand-check that every dump ends `PARA ... TEXT_END, STREAM_END` with final HTML glyphs and no persistent positive inline token code. Add the matching parameterized `tests/test_token_dump.py` comparison, omitting only terminal `-1` because the debug target does not print it. Run `uv run pytest tests/test_act3_contracts.py tests/test_token_dump.py tests/test_token_decode.py tests/test_token_structure.py -q`; expected PASS.

- [ ] **Step 5: Re-run interpreter/generated-SPL parity if the new scenes introduce a new IR control-flow shape.**

  Run: `uv run pytest tests/test_splc_interpret.py tests/test_splc_interpret_parity.py tests/test_splc_validate.py -q`  
  Expected: PASS; no lowered branch/goto or stack-floor behavior differs from the IR interpreter.

- [ ] **Step 6: Commit and push protected regions.**

  Run: `git add src_ir/act3.py src/30-act3-literary.toml src/30-act3-span.spl shakedown.spl tests/test_act3_contracts.py tests/fixtures/token_stream/spans && git commit -m "feat: protect buffered span regions"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding.

### Task 5: Close the spike with regression, performance, and halt evidence

**Files:**
- Modify: `docs/superpowers/plans/2026-07-12-span-architecture-spike.md`
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: `docs/verification-plan.md` only if a measured claim changes

**Consumes:** All preceding gates and the accepted design's halt rule.

**Produces:** A recorded confirmed-or-halted Act III model and exactly one updated roadmap state.

- [ ] **Step 1: Record measured program and feedback-loop evidence.**

  Record generated line/scene counts for `src/30-act3-span.spl`, one cold run and three representative runs of `variable_code_spans`, and the wall time of the shipped-fixture/spike regression command. Compare the measurements against `docs/performance/budget.md` yellow/red thresholds; do not infer performance from line count alone.

- [ ] **Step 2: Run the completion gate.**

  Run:

  ```bash
  uv run pytest -q
  uv run pytest tests/test_architecture_spikes.py -q
  uv run pytest tests/test_splc_generated_fragments.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
  uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'
  ```

  Expected: all default tests pass; all list, nested-block, and span spikes are byte-identical; generated/literary gates pass; the one shipped deterministic mdtest fixture is strict-oracle byte-identical. Do not claim unshipped fixtures are parity gates.

- [ ] **Step 3: Apply the halt rule from the accepted design.**

  If a protected region required output rescanning, could not preserve bytes, left a floor/prefix corrupted, or produced an invalid reviewed stream, append `- BLOCK:` to `.agent/blockers.md`, leave this plan in flight, and stop. Otherwise add concise measured evidence and checked boxes to this plan, mark 4S `shipped: <date> at commit <sha>` in the roadmap, and leave row 5 pending.

- [ ] **Step 4: Commit and push the outcome.**

  Run: `git add docs/superpowers/plans/2026-07-12-span-architecture-spike.md docs/superpowers/plans/plan-roadmap.md docs/verification-plan.md && git commit -m "docs: record span spike outcome"`  
  Expected: conventional commit with required provenance trailers succeeds, followed by `git push` succeeding. Omit `docs/verification-plan.md` from the command if no measured claim changed; never create an empty commit.
