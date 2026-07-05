# Literary Final Compliance Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the remaining literary review gaps in the current SPL without regressing any currently green Markdown fixtures.

**Architecture:** This is a controlled, source-first SPL pass. Add objective literary compliance tests first, then make small hand edits to `src/*.spl` and `src/literary.toml`, regenerate `shakedown.spl`, and verify both structural tests and Markdown fixture parity. Do not redesign assembler/codegen here; the future-facing prevention rails plan owns that work.

**Tech Stack:** SPL source fragments, TOML via Python `tomllib`, pytest, existing `scripts/assemble.py`, existing subprocess fixture suite.

---

## Scope

Fix only the current review gaps:

- Macbeth speaks or is removed from the live cast.
- Rosalind is more present in reference-link scenes.
- Juliet visibly carries night/star imagery.
- Puck does less plain control-flow labor where a safe stage handoff is available.
- Act IV scene titles use more ceremonial verb variety.
- Technical nouns in titles are softened only where clarity survives.
- Existing numeric phrase limits remain intact; no generator redesign in this pass.
- Puck's blurb and other blurbs avoid implementation-meta language.
- Existing dramatic moment ledger entries become visible in production surfaces.

The acceptance bar is stricter than "tests pass": all tests that are green before this plan must still be green afterward.

## File Structure

- Modify `tests/test_literary_compliance.py`: add objective tests for speaking presence, reference-scene presence, Juliet motif coverage, Act IV verb variety, blurb meta-language, and visible dramatic moments.
- Modify `src/literary.toml`: update blurbs, scene titles, and scene metadata to match source edits.
- Modify `src/00-preamble.spl`: remove Macbeth from the assembled cast if a safe
  executable line cannot be added without changing fixture behavior.
- Modify `src/30-act3-span.spl`: shift safe no-effect reference handoffs to Rosalind and strengthen Juliet night/star scene surfaces.
- Modify `src/40-act4-emit.spl`: vary Prospero's Act IV scene titles.
- Modify `shakedown.spl`: regenerate only with `scripts/assemble.py`.

## Guardrails

- Do not hand-edit `shakedown.spl`.
- Do not move `Recall`, `Remember`, assignment, comparison, input, or output statements between speakers unless a local SPL trace proves the same target character and stack are used.
- Safe speaker reassignments in this plan are limited to unconditional `Let us proceed to scene @...` lines and scene-title prose.
- Keep every `Scene @LABEL: title` source title byte-identical to `src/literary.toml` for the same label.
- After each SPL edit group, run at least the targeted literary tests and one affected Markdown fixture.

## Task 1: Add Objective Literary Gap Tests

**Files:**
- Modify: `tests/test_literary_compliance.py`

- [ ] **Step 1: Add helper functions and constants**

In `tests/test_literary_compliance.py`, add this import near the existing imports:

```python
from collections import Counter
```

```python
Add these constants immediately after the existing `CHARACTER_KEY` mapping, so
`CHARACTER_KEY` is already defined:

```python
PRODUCTION_CHARACTER_NAMES = tuple(CHARACTER_KEY)
REFERENCE_SCENES = {
    "LYRIC_OPEN_CONSULT_REFERENCE_ONE",
    "LYRIC_CONSULT_REFERENCE_ONE",
    "LYRIC_OPEN_OUTPUT_REFERENCE_ONE",
    "LYRIC_OPEN_CONSULT_REFERENCE_TWO",
    "LYRIC_CONSULT_REFERENCE_TWO",
    "LYRIC_OPEN_OUTPUT_REFERENCE_TWO",
}
JULIET_NIGHT_WORDS = {"night", "star", "stars", "starlit", "silver"}
IMPLEMENTATION_META_WORDS = {
    "adjective",
    "adjectives",
    "codegen",
    "implementation",
    "mechanism",
    "token",
    "tokens",
}
ACT_IV_DULL_VERBS = {"tests", "opens", "closes"}
MAX_ACT_IV_DULL_VERB_USES = 2
```

Add these helpers after `_word_count`:

```python
def _speaker_counts(source: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in source.splitlines():
        match = SPEAKER_ONLY_RE.match(line.strip())
        if match and match["speaker"] in CHARACTER_KEY:
            counts[match["speaker"]] += 1
    return counts


def _scene_blocks(source: str) -> dict[str, str]:
    matches = list(SCENE_RE.finditer(source))
    blocks: dict[str, str] = {}
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(source)
        blocks[match["label"]] = source[start:end]
    return blocks


def _scene_titles() -> dict[str, str]:
    return {
        match["label"]: match["title"].strip()
        for match in SCENE_RE.finditer(_production_source())
    }


def _words(text: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[A-Za-z']+", text)}
```

- [ ] **Step 2: Add the failing tests**

Append these tests to `tests/test_literary_compliance.py`:

```python
def test_named_production_characters_have_speaking_lines() -> None:
    counts = _speaker_counts(_production_source())
    silent = [
        character
        for character in PRODUCTION_CHARACTER_NAMES
        if counts[character] == 0
    ]
    assert not silent


def test_reference_librarian_is_visible_in_reference_scenes() -> None:
    blocks = _scene_blocks(_production_source())
    reference_text = "\n".join(blocks[label] for label in sorted(REFERENCE_SCENES))
    assert reference_text.count("Rosalind:") >= 4


def test_juliet_surfaces_include_night_or_star_imagery() -> None:
    data = _literary()
    characters = data["characters"]
    assert isinstance(characters, dict)
    juliet = characters["juliet"]
    assert isinstance(juliet, dict)

    titles = _scene_titles()
    juliet_titles = " ".join(
        title
        for title in titles.values()
        if "Juliet" in title or _words(title) & {"rose", "evening"}
    )
    surfaces = f"{juliet['blurb']} {juliet_titles}"
    assert _words(surfaces) & JULIET_NIGHT_WORDS


def test_act_iv_scene_titles_use_ceremonial_verb_variety() -> None:
    titles = _scene_titles()
    act_iv_titles = [
        title
        for label, title in titles.items()
        if label.startswith("SCRIBE_") or label == "ACT_IV_DONE"
    ]
    words = Counter(
        word
        for title in act_iv_titles
        for word in re.findall(r"[A-Za-z']+", title.lower())
    )
    overused = {
        verb: words[verb]
        for verb in ACT_IV_DULL_VERBS
        if words[verb] > MAX_ACT_IV_DULL_VERB_USES
    }
    assert not overused


def test_character_blurbs_avoid_implementation_meta_language() -> None:
    data = _literary()
    characters = data["characters"]
    assert isinstance(characters, dict)
    offenders: dict[str, set[str]] = {}
    for key, character in characters.items():
        assert isinstance(character, dict)
        blurb = character["blurb"]
        assert isinstance(blurb, str)
        meta_words = _words(blurb) & IMPLEMENTATION_META_WORDS
        if meta_words:
            offenders[key] = meta_words
    assert not offenders


def test_dramatic_moments_are_visible_in_scene_surfaces() -> None:
    data = _literary()
    moments = data["dramatic_moments"]
    assert isinstance(moments, dict)
    titles = _scene_titles()
    blocks = _scene_blocks(_production_source())

    missing: list[str] = []
    for name, moment in moments.items():
        assert isinstance(moment, dict)
        scene = moment["scene"]
        character = moment["character"]
        assert isinstance(scene, str)
        assert isinstance(character, str)
        title_words = _words(titles[scene])
        block_words = _words(blocks[scene])
        character_words = _words(character)
        if not (title_words & character_words or block_words & character_words):
            missing.append(name)
    assert not missing
```

- [ ] **Step 3: Run the new tests and confirm they fail**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py -q
```

Expected: existing tests pass, and at least the new Macbeth, Rosalind, Juliet, Act IV verb, Puck blurb, and dramatic-moment tests fail.

Do not weaken the tests to make the current source pass.

## Task 2: Capture A No-Regression Baseline

**Files:**
- No source changes.

- [ ] **Step 1: Run the current full test suite before SPL edits**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
```

Expected: only the new literary tests from Task 1 fail. If any pre-existing test fails, stop and investigate before editing SPL.

- [ ] **Step 2: Capture current passing Markdown fixture output**

Run:

```bash
mkdir -p /tmp/shakedown-literary-baseline
fixture="$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text"
./shakedown < "$fixture" > "/tmp/shakedown-literary-baseline/Amps and angle encoding.xhtml"
```

Expected: command exits 0 for the currently implemented fixture. These files
are a temporary local baseline only; do not commit them.

## Task 3: Remove Macbeth From The Assembled Cast

**Files:**
- Modify: `src/00-preamble.spl`
- Modify: `src/literary.toml`
- Modify: `shakedown.spl`

- [ ] **Step 1: Remove Macbeth from the production preamble**

The interpreter cannot safely execute a distinct Macbeth line in the current
Act II structure without disturbing the shipped fixture. Use the review-allowed
alternative and remove Macbeth from the assembled cast. In `src/00-preamble.spl`,
delete this paragraph:

```spl
Macbeth, apprentice mason, who pairs with the Lady though dread shadows him.
```

- [ ] **Step 2: Update Macbeth's blurb if needed**

In `src/literary.toml`, keep Macbeth as apprentice for future block-phase work,
but use a non-meta blurb:

```toml
blurb = "Macbeth, apprentice mason, who steps through the shadowed threshold."
```

- [ ] **Step 3: Regenerate the assembled SPL**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
```

Expected: `shakedown.spl` is updated and no longer introduces Macbeth in the
assembled preamble.

- [ ] **Step 4: Verify the production-cast test and one shipped fixture**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_named_production_characters_have_speaking_lines -q
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k "Amps and angle" -q
```

Expected: production-cast speaking test passes. The selected Markdown fixture
remains green.

## Task 4: Make Rosalind Visible In Reference Scenes

**Files:**
- Modify: `src/30-act3-span.spl`
- Modify: `src/literary.toml`
- Modify: `shakedown.spl`

- [ ] **Step 1: Reassign only safe reference-scene gotos to Rosalind**

In `src/30-act3-span.spl`, change the unconditional goto after `[Enter Rosalind]` in `Scene @LYRIC_OPEN_CONSULT_REFERENCE_ONE` from:

```spl
Puck:
 Let us proceed to scene @LYRIC_CONSULT_REFERENCE_ONE.
```

to:

```spl
Rosalind:
 Let us proceed to scene @LYRIC_CONSULT_REFERENCE_ONE.
```

In `Scene @LYRIC_OPEN_CONSULT_REFERENCE_TWO`, make the same change for the goto to `@LYRIC_CONSULT_REFERENCE_TWO`.

Do not move the three `Puck: Recall ...` lines in either consult scene. Those affect the other on-stage character's stack and must stay with Puck in this pass.

- [ ] **Step 2: Soften reference titles without hiding the mechanic**

In both `src/30-act3-span.spl` and `src/literary.toml`, use these exact title replacements:

```text
LYRIC_OPEN_CONSULT_REFERENCE_ONE = "Rosalind opens the first forest shelf."
LYRIC_CONSULT_REFERENCE_ONE = "The forest yields Rosalind's first bargain."
LYRIC_OPEN_OUTPUT_REFERENCE_ONE = "Juliet receives the first starlit path."
LYRIC_OPEN_CONSULT_REFERENCE_TWO = "Rosalind opens the second forest shelf."
LYRIC_CONSULT_REFERENCE_TWO = "The forest yields Rosalind's second bargain."
LYRIC_OPEN_OUTPUT_REFERENCE_TWO = "Juliet receives the titled star path."
```

Keep the existing `pattern` values for these scenes; the replacement titles fit
their current pattern word-count bounds.

- [ ] **Step 3: Regenerate and verify**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_reference_librarian_is_visible_in_reference_scenes tests/test_literary_compliance.py::test_scene_titles_have_toml_entries_and_match_source -q
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k "Links" -q
```

Expected: Rosalind visibility and scene-title sync tests pass. The selected Markdown fixture remains green if it was green before Task 1.

## Task 5: Strengthen Juliet Night/Star Surfaces

**Files:**
- Modify: `src/30-act3-span.spl`
- Modify: `src/literary.toml`
- Modify: `shakedown.spl`

- [ ] **Step 1: Update Juliet's blurb**

In `src/literary.toml`, replace Juliet's blurb with:

```toml
blurb = "Juliet, night-star lyric, who lays final roses on the silver path."
```

- [ ] **Step 2: Update Juliet-associated scene titles**

In both `src/30-act3-span.spl` and `src/literary.toml`, use these title replacements:

```text
LYRIC_OPEN_OUTPUT_INLINE_LINK = "Juliet receives the first silver path."
LYRIC_OPEN_OUTPUT_LINK_FALLBACK = "Juliet keeps the moonlit loose rose."
LYRIC_OPEN_REFERENCE_FALLBACK = "Juliet keeps the starlit reference rose."
LYRIC_OPEN_OUTPUT_LT_ENTITY_CURRENT = "Juliet receives the softened silver angle."
LYRIC_REVERSE_POP = "Juliet lifts one starlit glyph."
LYRIC_OPEN_PUSH_BACK = "Puck takes the starlit word."
```

Do not change any `Let us proceed` lines in this task. This task is title/blurb surface only, so it should be mechanically inert.

- [ ] **Step 3: Regenerate and verify**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_juliet_surfaces_include_night_or_star_imagery tests/test_literary_compliance.py::test_scene_titles_have_toml_entries_and_match_source -q
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k "Amps and angle" -q
```

Expected: Juliet motif test and title sync pass. The selected Markdown fixture remains green if it was green before Task 1.

## Task 6: Vary Prospero's Act IV Ceremony

**Files:**
- Modify: `src/40-act4-emit.spl`
- Modify: `src/literary.toml`
- Modify: `shakedown.spl`

- [ ] **Step 1: Replace repetitive Act IV titles**

In both `src/40-act4-emit.spl` and `src/literary.toml`, use these exact title replacements:

```text
SCRIBE_TEST_ANCHOR_OPEN = "Prospero weighs the anchor gate."
SCRIBE_TEST_ANCHOR_TITLE = "Prospero proves the title gate."
SCRIBE_TEST_ANCHOR_TEXT = "Prospero summons the text gate."
SCRIBE_TEST_ANCHOR_CLOSE = "Prospero seals the anchor close."
SCRIBE_EMIT_ANCHOR_OPEN = "Prospero inscribes the anchor gate."
SCRIBE_EMIT_ANCHOR_TITLE = "Prospero releases the anchor title."
SCRIBE_EMIT_ANCHOR_TEXT = "Prospero sets free the anchor text."
SCRIBE_EMIT_ANCHOR_CLOSE = "Prospero binds the anchor seal."
SCRIBE_EMIT_PARAGRAPH_OPEN = "Prospero opens one chamber."
SCRIBE_TEST_FINAL_CLOSE = "Prospero weighs the last seal."
SCRIBE_EMIT_PARAGRAPH_CLOSE = "Prospero closes one chamber."
SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE = "Prospero seals the final chamber."
```

These retain useful domain nouns while reducing the `tests/opens/closes` rhythm.

- [ ] **Step 2: Regenerate and verify**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_act_iv_scene_titles_use_ceremonial_verb_variety tests/test_literary_compliance.py::test_scene_titles_have_toml_entries_and_match_source -q
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k "Amps and angle" -q
```

Expected: Act IV title variety and title sync pass. The selected Markdown fixture remains green if it was green before Task 1.

## Task 7: Remove Meta Blurbs And Surface Dramatic Moments

**Files:**
- Modify: `src/10-act1-preprocess.spl`
- Modify: `src/20-act2-block.spl`
- Modify: `src/30-act3-span.spl`
- Modify: `src/literary.toml`
- Modify: `shakedown.spl`

- [ ] **Step 1: Replace Puck's meta blurb**

In `src/literary.toml`, replace Puck's blurb with:

```toml
blurb = "Puck, swift messenger, who wears each room's colour and flies between them."
```

- [ ] **Step 2: Make dramatic moments visible in scene titles**

In both the source `.spl` files and `src/literary.toml`, use these title replacements:

```text
ACT_I_DONE = "Hecate seals the cauldron and vanishes."
MASON_OPEN_REVERSE_STREAM = "Lady Macbeth gives Puck the mason's order."
ACT_III_DONE = "Romeo and Juliet part as one bright rose."
```

Do not change `ACT_IV_DONE`; it already carries the `Our revels now are ended` iconic moment.

- [ ] **Step 3: Regenerate and verify**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_character_blurbs_avoid_implementation_meta_language tests/test_literary_compliance.py::test_dramatic_moments_are_visible_in_scene_surfaces tests/test_literary_compliance.py::test_scene_titles_have_toml_entries_and_match_source -q
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k "Amps and angle" -q
```

Expected: blurb, dramatic moment, and title sync tests pass. The selected Markdown fixture remains green if it was green before Task 1.

## Task 8: Full Regression Verification

**Files:**
- No source changes unless verification finds a defect.

- [ ] **Step 1: Run the full test suite**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
```

Expected: every test that was green before this plan is still green, and the new literary tests are green.

- [ ] **Step 2: Compare current fixture outputs to the temporary baseline**

Run:

```bash
mkdir -p /tmp/shakedown-literary-after
fixture="$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text"
./shakedown < "$fixture" > "/tmp/shakedown-literary-after/Amps and angle encoding.xhtml"
diff -u \
  "/tmp/shakedown-literary-baseline/Amps and angle encoding.xhtml" \
  "/tmp/shakedown-literary-after/Amps and angle encoding.xhtml"
```

Expected: no output and exit 0. If this fails, inspect the diff and revert or
repair the most recent SPL edit group before continuing.

- [ ] **Step 3: Re-run repeated-pattern scans**

Run:

```bash
rg -n '\b(big big|fine fine|noble noble|small fine small|big black big|black big|big black|as good as)\b' src/*.spl shakedown.spl
```

Expected: no matches. If matches appear, fix the source phrase and regenerate.

- [ ] **Step 4: Run Python quality gates for touched tests**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check tests/test_literary_compliance.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright tests/test_literary_compliance.py
```

Expected: both commands pass.

- [ ] **Step 5: Inspect the final diff**

Run:

```bash
git diff -- src/*.spl src/literary.toml shakedown.spl tests/test_literary_compliance.py
```

Expected: diff contains only the planned literary/test changes. `shakedown.spl` changes should correspond to assembled output from `src/*.spl`.

- [ ] **Step 6: Commit**

Run:

```bash
git add docs/superpowers/plans/2026-05-01-literary-final-compliance-pass.md tests/test_literary_compliance.py src/*.spl src/literary.toml shakedown.spl
git commit -m "style: finish literary compliance pass"
```

Expected: commit succeeds.

## Self-Review Checklist

- The plan covers every review item listed in scope.
- The plan adds objective tests before implementation.
- The plan avoids broad assembler/codegen redesign.
- The plan uses the review-allowed Macbeth removal because a distinct Macbeth
  line would regress the shipped fixture.
- The plan explicitly preserves currently green fixture output with a before/after diff gate.
- The plan includes exact commands and expected outcomes for every verification step.
