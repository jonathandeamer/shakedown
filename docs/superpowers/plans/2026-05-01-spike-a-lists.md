# Spike A Lists Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate production-shaped list parsing at minimum viable scope.

**Architecture:** Add a real list pass to Act II before paragraph formation, emit durable `LIST_OPEN`, `LIST_ITEM`, and `LIST_CLOSE` token flow with list-kind and item-looseness payloads, and teach Act IV to render those tokens. The spike proves the multi-pass dispatcher and frame-sentinel nesting shape through small oracle-backed snippets, while leaving full mdtest list coverage for Slice 4.

**Tech Stack:** SPL fragments in `src/*.spl`, Python 3.12, pytest, local `~/markdown/Markdown.pl`, existing assembler/codegen/literary-surface tooling.

---

## Required Reading

Read these before editing:

- `docs/superpowers/plans/plan-roadmap.md`
- `docs/superpowers/specs/2026-05-01-spike-a-lists-design.md`
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §4.2 and §7.3
- `docs/markdown/list-mechanics.md`
- `docs/markdown/oracle-mechanics.md`
- `docs/spl/reference.md`
- `docs/superpowers/notes/spl-literary-protocol.md`
- `docs/spl/literary-spec.md`
- `docs/spl/style-lexicon.md`
- `docs/spl/codegen-style-guide.md`
- `src/literary.toml`

Follow `docs/superpowers/notes/spl-literary-protocol.md` before changing
`src/*.spl`, `scripts/assemble.py`, `scripts/codegen_html.py`, or any SPL code
generator.

## File Structure

- Create: `tests/fixtures/architecture_spikes/lists/flat_unordered_tight.text`
- Create: `tests/fixtures/architecture_spikes/lists/flat_ordered_tight.text`
- Create: `tests/fixtures/architecture_spikes/lists/nested_one_level.text`
- Create: `tests/fixtures/architecture_spikes/lists/loose_second_paragraph.text`
- Create: `tests/fixtures/architecture_spikes/lists/indented_continuation.text`
- Create: `tests/fixtures/architecture_spikes/lists/hard_wrapped_boundary.text`
- Create: `tests/test_architecture_spikes.py`
- Modify: `src/literary.toml`
- Modify: `src/20-act2-block.spl`
- Modify: `src/40-act4-emit.spl`
- Modify: `shakedown.spl`
- Modify only if implementation proves it necessary: `docs/spl/token-codes.md`, `scripts/codegen_html.py`, `tests/test_codegen_html.py`

## Token Contract

Reuse the existing token codes from `docs/spl/token-codes.md`:

- `LIST_OPEN = 4`
- `LIST_ITEM = 5`
- `LIST_CLOSE = 6`

Emit payloads next to those token codes:

- list kind `1` means unordered list;
- list kind `2` means ordered list;
- item looseness `1` means tight item;
- item looseness `2` means loose item.

Act II owns list recognition, item buffering, nesting state, and tight/loose
classification. Act IV may maintain a small list-kind stack so it can choose
`</ul>` or `</ol>`, but it must not inspect raw Markdown source to recover list
structure.

## Task 1: Add Oracle-Backed Spike Harness

**Files:**
- Create: `tests/fixtures/architecture_spikes/lists/flat_unordered_tight.text`
- Create: `tests/fixtures/architecture_spikes/lists/flat_ordered_tight.text`
- Create: `tests/fixtures/architecture_spikes/lists/nested_one_level.text`
- Create: `tests/fixtures/architecture_spikes/lists/loose_second_paragraph.text`
- Create: `tests/fixtures/architecture_spikes/lists/indented_continuation.text`
- Create: `tests/fixtures/architecture_spikes/lists/hard_wrapped_boundary.text`
- Create: `tests/test_architecture_spikes.py`

- [x] **Step 1: Create list spike snippets**

Create `tests/fixtures/architecture_spikes/lists/flat_unordered_tight.text`:

```text
* alpha
* beta
* gamma
```

Create `tests/fixtures/architecture_spikes/lists/flat_ordered_tight.text`:

```text
1. alpha
2. beta
3. gamma
```

Create `tests/fixtures/architecture_spikes/lists/nested_one_level.text`:

```text
* alpha
  1. beta
  2. gamma
* delta
```

Create `tests/fixtures/architecture_spikes/lists/loose_second_paragraph.text`:

```text
* alpha

  second paragraph
* beta
```

Create `tests/fixtures/architecture_spikes/lists/indented_continuation.text`:

```text
* alpha
    continuation
* beta
```

Create `tests/fixtures/architecture_spikes/lists/hard_wrapped_boundary.text`:

```text
Here is a wrapped paragraph
8. Oops this stays paragraph text.
```

- [x] **Step 2: Add the failing architecture spike harness**

Create `tests/test_architecture_spikes.py`:

```python
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
SHAKEDOWN = REPO / "shakedown"
MARKDOWN_PL = Path.home() / "markdown" / "Markdown.pl"
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"


def _first_diff(a: bytes, b: bytes) -> int | None:
    for idx, (left, right) in enumerate(zip(a, b, strict=False)):
        if left != right:
            return idx
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def _run(argv: list[str], input_bytes: bytes) -> bytes:
    result = subprocess.run(
        argv,
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=True,
    )
    return result.stdout


def _list_cases() -> list[Path]:
    return sorted(LIST_FIXTURES.glob("*.text"))


@pytest.mark.parametrize("fixture", _list_cases(), ids=lambda path: path.stem)
def test_list_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
    input_bytes = fixture.read_bytes()
    actual = _run([str(SHAKEDOWN)], input_bytes)
    expected = _run(["perl", str(MARKDOWN_PL)], input_bytes)

    assert actual == expected, (
        f"Output mismatch for {fixture.name}; first diff: "
        f"{_first_diff(actual, expected)}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual\n{actual.decode(errors='replace')}"
    )
```

- [x] **Step 3: Verify the harness fails for unimplemented list snippets**

Run:

```bash
uv run pytest tests/test_architecture_spikes.py -q
```

Expected: the list snippets fail because `./shakedown` still treats list-shaped
input as paragraph text.

- [x] **Step 4: Commit the failing spike harness**

Run:

```bash
git add tests/fixtures/architecture_spikes/lists tests/test_architecture_spikes.py
git commit -m "test: add list architecture spike harness"
```

## Task 2: Confirm Literary Surface Rules For List Scenes

**Files:**
- Read: `docs/superpowers/notes/spl-literary-protocol.md`
- Read: `src/literary.toml`
- Read: `tests/test_literary_compliance.py`

- [ ] **Step 1: Confirm scene ledger and source labels must change together**

Read `tests/test_literary_compliance.py::test_scene_ledger_matches_source_scene_labels`.
The rule is strict: every `Scene @LABEL:` in production source must have a
matching `[scenes.LABEL]` entry in `src/literary.toml`, and every TOML scene
entry must be used by production source.

Do not commit ledger-only scene entries. Add each `[scenes.LABEL]` entry in the
same commit as the corresponding `Scene @LABEL:` source change.

- [ ] **Step 2: Reserve Act II and Act IV scene labels for this spike**

Use these Act II labels unless implementation proves one is unnecessary:

```toml
[scenes.MASON_TEST_LIST_START]
title = "Where the captain spies ordered ranks."

[scenes.MASON_OPEN_LIST]
title = "The gate of ranks is opened."

[scenes.MASON_OPEN_LIST_ITEM]
title = "Each soldier receives his place."

[scenes.MASON_CLOSE_LIST_ITEM]
title = "The place is sealed."

[scenes.MASON_CLOSE_LIST]
title = "The ranks are dismissed."

[scenes.MASON_RETURN_NESTED_LIST]
title = "The inner troop returns to command."
```

Use these Act IV labels unless implementation proves one is unnecessary:

```toml

[scenes.SCRIBE_TEST_LIST_OPEN]
title = "Prospero tests the ordered gate."

[scenes.SCRIBE_EMIT_UNORDERED_LIST_OPEN]
title = "Prospero releases the rough ranks."

[scenes.SCRIBE_EMIT_ORDERED_LIST_OPEN]
title = "Prospero releases the numbered ranks."

[scenes.SCRIBE_EMIT_LIST_ITEM]
title = "Prospero grants each place."

[scenes.SCRIBE_EMIT_LIST_CLOSE]
title = "Prospero closes the ranks."
```

If the implementation adds another `Scene @LABEL:`, add a matching
`[scenes.LABEL]` table with a concrete `title` in the same task.

- [ ] **Step 3: Run the protocol enforcement tests**

```bash
uv run pytest tests/test_prompt_literary_protocol.py -q
```

Expected: pass. This confirms the active in-flight plan includes the required
SPL literary protocol and exact compliance-test references.

- [ ] **Step 4: Commit the literary-surface planning checkpoint**

Run:

```bash
git add docs/superpowers/plans/2026-05-01-spike-a-lists.md
git commit -m "docs: record list spike literary surface rules"
```

## Task 3: Implement Minimum Act II List Tokens

**Files:**
- Modify: `src/20-act2-block.spl`
- Modify: `shakedown.spl`
- Test: `tests/test_architecture_spikes.py`
- Test: `tests/test_mdtest.py`
- Test: `tests/test_literary_compliance.py`

- [ ] **Step 1: Add the Act II list pass before paragraph formation**

In `src/literary.toml`, add the Act II scene entries from Task 2 that are
actually used by the new Act II scenes.

In `src/20-act2-block.spl`, add a list recognition path that runs before the
existing paragraph close path. Use the existing Act II character ownership:

- Lady Macbeth remains the block mason and speaks the main Act II list scenes.
- Puck remains the Herald stream carrier at the Act II handoff.
- Use `@LIT.scenes.MASON_TEST_LIST_START.title`,
  `@LIT.scenes.MASON_OPEN_LIST.title`,
  `@LIT.scenes.MASON_OPEN_LIST_ITEM.title`,
  `@LIT.scenes.MASON_CLOSE_LIST_ITEM.title`,
  `@LIT.scenes.MASON_CLOSE_LIST.title`, and
  `@LIT.scenes.MASON_RETURN_NESTED_LIST.title` for controlled scene titles.

Implement the token contract from this plan:

- emit `LIST_OPEN`, then payload `1` for `*` lists or payload `2` for digit-dot
  lists;
- emit `LIST_ITEM`, then payload `1` for tight items or payload `2` for loose
  items;
- emit item body text through the existing text/payload stream pattern used by
  paragraphs;
- emit `LIST_CLOSE` when the current list frame ends;
- preserve the top-level rule that a list starts at document start or after a
  blank line;
- allow one nested list level when the nested marker is indented two spaces
  under the parent item;
- treat a four-space indented continuation inside a tight list item as item
  text for the Spike A `indented_continuation.text` snippet.

Do not add support for `+` or `-` unordered markers in this task. Do not unskip
the full `Ordered and unordered lists` mdtest fixture.

- [ ] **Step 2: Regenerate assembled SPL**

Run:

```bash
uv run python scripts/assemble.py
```

Expected: `shakedown.spl` is regenerated with no unresolved `@LIT.` placeholders.

- [ ] **Step 3: Run the list spike harness**

Run:

```bash
uv run pytest tests/test_architecture_spikes.py -q
```

Expected: failures may remain in Act IV list emission, but failures should show
list token progress rather than unchanged paragraph-only output.

- [ ] **Step 4: Run literary/source consistency for Act II changes**

Run:

```bash
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py -q
```

Expected: pass. If this fails with a scene-ledger mismatch, add or remove
`[scenes.*]` entries so `src/literary.toml` and production scene labels match
exactly.

- [ ] **Step 5: Commit Act II list token work**

Run:

```bash
git add src/literary.toml src/20-act2-block.spl shakedown.spl
git commit -m "feat: emit minimum list block tokens"
```

## Task 4: Implement Act IV List HTML Emission

**Files:**
- Modify: `src/40-act4-emit.spl`
- Modify: `shakedown.spl`
- Modify only if needed: `scripts/codegen_html.py`
- Modify only if needed: `tests/test_codegen_html.py`
- Test: `tests/test_architecture_spikes.py`
- Test: `tests/test_codegen_html.py`

- [ ] **Step 1: Confirm list tag byte phrases through codegen**

Run:

```bash
uv run python - <<'PY'
from scripts.codegen_html import emit_literal
for literal in (b"<ul>", b"</ul>", b"<ol>", b"</ol>", b"<li>", b"</li>"):
    print(literal.decode(), "=>", emit_literal(literal))
PY
```

Expected: every literal prints a list of byte phrases and the command exits
zero. If it does not, update `scripts/codegen_html.py` and
`tests/test_codegen_html.py` before hand-editing SPL emission scenes.

- [ ] **Step 2: Add list token dispatch to Act IV**

In `src/literary.toml`, add the Act IV scene entries from Task 2 that are
actually used by the new Act IV scenes.

In `src/40-act4-emit.spl`, extend the token dispatch after paragraph and anchor
checks:

- `LIST_OPEN` with payload `1` emits `<ul>` and pushes unordered kind onto the
  emission-side list-kind stack;
- `LIST_OPEN` with payload `2` emits `<ol>` and pushes ordered kind onto the
  emission-side list-kind stack;
- `LIST_ITEM` with payload `1` emits tight item HTML as `<li>text</li>`;
- `LIST_ITEM` with payload `2` emits loose item HTML with paragraph structure
  inside `<li>`;
- `LIST_CLOSE` pops the current list kind and emits `</ul>` or `</ol>`.

Use these controlled scene-title placeholders for new scenes:

- `@LIT.scenes.SCRIBE_TEST_LIST_OPEN.title`
- `@LIT.scenes.SCRIBE_EMIT_UNORDERED_LIST_OPEN.title`
- `@LIT.scenes.SCRIBE_EMIT_ORDERED_LIST_OPEN.title`
- `@LIT.scenes.SCRIBE_EMIT_LIST_ITEM.title`
- `@LIT.scenes.SCRIBE_EMIT_LIST_CLOSE.title`

Use `scripts/codegen_html.py` output for forced-byte literals. Keep any
hand-authored dialogue incidental and aligned with `docs/spl/style-lexicon.md`.

- [ ] **Step 3: Regenerate assembled SPL**

Run:

```bash
uv run python scripts/assemble.py
```

Expected: `shakedown.spl` is regenerated with no unresolved `@LIT.` placeholders.

- [ ] **Step 4: Verify list snippets are byte-identical to Markdown.pl**

Run:

```bash
uv run pytest tests/test_architecture_spikes.py -q
```

Expected: all list architecture spike snippets pass.

- [ ] **Step 5: Run literary/source consistency for Act IV changes**

Run:

```bash
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
```

Expected: pass. If this fails with a scene-ledger mismatch, add or remove
`[scenes.*]` entries so `src/literary.toml` and production scene labels match
exactly.

- [ ] **Step 6: Commit Act IV list emission**

Run:

```bash
git add src/literary.toml src/40-act4-emit.spl shakedown.spl scripts/codegen_html.py tests/test_codegen_html.py
git commit -m "feat: emit minimum list html"
```

If `scripts/codegen_html.py` and `tests/test_codegen_html.py` were not changed,
omit them from `git add`.

## Task 5: Run Spike A Regression Gate

**Files:**
- Modify: `docs/superpowers/plans/2026-05-01-spike-a-lists.md`
- Test: full Spike A gate

- [ ] **Step 1: Run architecture spike snippets**

Run:

```bash
uv run pytest tests/test_architecture_spikes.py -q
```

Expected: all list architecture spike snippets pass.

- [ ] **Step 2: Run implemented mdtest fixture**

Run:

```bash
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: `1 passed, 22 deselected`.

- [ ] **Step 3: Run strict Slice 1 parity**

Run:

```bash
uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'
```

Expected output includes:

```text
- Amps and angle encoding: byte-identical: yes
summary: 1/1 byte-identical
```

- [ ] **Step 4: Run token and literary compliance gates**

Run:

```bash
uv run pytest tests/test_token_codes.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
```

Expected: all selected tests pass.

- [ ] **Step 5: Run the full default suite**

Run:

```bash
uv run pytest
```

Expected: default test suite passes.

- [ ] **Step 6: Commit the completed Spike A plan checkboxes**

After all previous steps pass and this plan's checkboxes are up to date, run:

```bash
git add docs/superpowers/plans/2026-05-01-spike-a-lists.md
git commit -m "chore: complete spike a list plan"
```

Do not update `docs/superpowers/plans/plan-roadmap.md` to mark Spike A shipped
until the final verification evidence is available in the repository history.
