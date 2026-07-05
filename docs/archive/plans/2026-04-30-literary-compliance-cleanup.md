# Literary Compliance Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the current production SPL conform to the live literary, lexicon, and codegen-style guidance while preserving Slice 1 byte-identical behavior.

**Architecture:** This is a source-first manual cleanup. Edit `src/*.spl` and `src/literary.toml`, regenerate `shakedown.spl` with `scripts/assemble.py`, and add objective compliance tests so future edits cannot reintroduce the same current failures. Do not redesign `scripts/assemble.py` or `scripts/codegen_html.py` in this plan.

**Tech Stack:** SPL source fragments, TOML via Python `tomllib`, pytest, existing `scripts/assemble.py`, existing strict parity harness.

---

## File Map

- Modify `src/00-preamble.spl`: locked play title, existing dramatis personae text preserved unless a validation test fails, locked Act I title.
- Modify `src/10-act1-preprocess.spl`: Act I current scenes, Hecate/Horatio/Puck Recall/goto/comparison/value prose.
- Modify `src/20-act2-block.spl`: locked Act III handoff title currently embedded at the end, Act II current scenes, Lady Macbeth/Hecate/Puck Recall/goto/comparison/value prose.
- Modify `src/30-act3-span.spl`: locked Act IV handoff title currently embedded at the end, large current span surface, Romeo/Juliet/Puck/Rosalind Recall/goto/comparison/value prose.
- Modify `src/40-act4-emit.spl`: Act IV current scenes, Prospero/Puck Recall/goto/comparison/value prose.
- Modify `src/literary.toml`: add current-surface ledger sections for title, act titles, scene titles, Recall pools, soft-variation pools, and empty/current iconic/dramatic tags.
- Modify `shakedown.spl`: regenerated only by `scripts/assemble.py`.
- Modify `tests/test_literary_toml_schema.py`: schema coverage for new TOML sections.
- Create `tests/test_literary_compliance.py`: production-surface compliance checks.
- Create `tests/test_spl_layout_smoke.py`: parser smoke tests for Folio-style source forms.

## Shared Data Rules

Use these exact locked titles:

```python
PLAY_TITLE = "Shakedown: A Most Excellent Tragicomedy of Glyph and Line."
ACT_TITLES = {
    "act1": "Wherein the witches sort raw matter into shelves and seals.",
    "act2": "Wherein the kingdom of blocks is shaped, and each form named.",
    "act3": "Wherein the lovers gild the line with light and rose.",
    "act4": "Wherein Prospero, his work done, inscribes and releases all.",
}
```

Use these safe replacement atom families for large positive values. Each atom is legal, positive, and at most six words including article and noun:

```text
hecate: 1=a cat; 2=a black cat; 4=a furry black cat; 8=a little furry black cat; 16=a normal little furry black cat
puck: 1=a flower; 2=a sweet flower; 4=a green sweet flower; 8=a little green sweet flower; 16=a rural little green sweet flower
romeo: 1=a summer's day; 2=a sunny summer's day; 4=a golden sunny summer's day; 8=a fair golden sunny summer's day; 16=a warm fair golden sunny summer's day
juliet: 1=a rose; 2=a sweet rose; 4=a fair sweet rose; 8=a gentle fair sweet rose; 16=a beautiful gentle fair sweet rose
lady_macbeth: 1=a hero; 2=a noble hero; 4=a bold noble hero; 8=a mighty bold noble hero; 16=a proud mighty bold noble hero
prospero: 1=an angel; 2=a noble angel; 4=a golden noble angel; 8=a fine golden noble angel; 16=a warm fine golden noble angel
rosalind: 1=a tree; 2=a green tree; 4=a rural green tree; 8=a fair rural green tree; 16=a gentle fair rural green tree
horatio: 1=a brother; 2=a happy brother; 4=a warm happy brother; 8=a healthy warm happy brother; 16=a gentle healthy warm happy brother
```

For any positive value greater than 16, decompose it as a `the sum of ... and ...` expression whose component atoms come from the active speaker's family. For example, with Prospero:

```text
32 = the sum of a warm fine golden noble angel and a warm fine golden noble angel
65 = the sum of a warm fine golden noble angel and the sum of a warm fine golden noble angel and the sum of a warm fine golden noble angel and the sum of a warm fine golden noble angel and an angel
```

Keep `nothing` as `nothing`.

## Task 1: Add Layout Smoke Tests

**Files:**
- Create: `tests/test_spl_layout_smoke.py`

- [ ] **Step 1: Write the parser smoke tests**

Create `tests/test_spl_layout_smoke.py` with:

```python
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

SHAKESPEARE = shutil.which("shakespeare")
if SHAKESPEARE is None:
    fallback = Path.home() / ".local/bin/shakespeare"
    SHAKESPEARE = str(fallback) if fallback.is_file() else None


def _run_spl(tmp_path: Path, source: str) -> subprocess.CompletedProcess[str]:
    program = tmp_path / "layout.spl"
    program.write_text(source)
    assert SHAKESPEARE is not None
    return subprocess.run(
        [SHAKESPEARE, "run", str(program)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.skipif(SHAKESPEARE is None, reason="shakespeare executable not found")
def test_speaker_name_on_own_line_is_parser_accepted(tmp_path: Path) -> None:
    result = _run_spl(
        tmp_path,
        """The Layout Trial.

Romeo, a lad.
Juliet, a lass.

                    Act I: Wherein the test begins.

                    Scene I: The line is spoken.

[Enter Romeo and Juliet]

Romeo:
 You are as good as a cat.

Romeo:
 Speak your mind!

[Exeunt]
""",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "\x01"


@pytest.mark.skipif(SHAKESPEARE is None, reason="shakespeare executable not found")
def test_hanging_indent_inside_value_expression_is_parser_accepted(
    tmp_path: Path,
) -> None:
    result = _run_spl(
        tmp_path,
        """The Hanging Trial.

Romeo, a lad.
Juliet, a lass.

                    Act I: Wherein the test begins.

                    Scene I: The value is split.

[Enter Romeo and Juliet]

Romeo:
 You are as good as the sum of a big cat and
  a cat.

Romeo:
 Speak your mind!

[Exeunt]
""",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "\x03"
```

- [ ] **Step 2: Run smoke tests and record supported layout forms**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_spl_layout_smoke.py -q
```

Expected: both tests pass. If the hanging-indent test fails, mark it `xfail` with an explicit reason and do not apply hanging indentation to production fragments in later tasks.

- [ ] **Step 3: Commit**

```bash
git add tests/test_spl_layout_smoke.py
git commit -m "test: probe Folio SPL layout forms"
```

## Task 2: Add Production Literary Compliance Tests

**Files:**
- Create: `tests/test_literary_compliance.py`

- [ ] **Step 1: Write failing compliance tests**

Create `tests/test_literary_compliance.py` with:

```python
from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO = Path(__file__).parent.parent
SRC = REPO / "src"
ASSEMBLED = REPO / "shakedown.spl"
LITERARY_TOML = SRC / "literary.toml"

PLAY_TITLE = "Shakedown: A Most Excellent Tragicomedy of Glyph and Line."
ACT_TITLES = {
    "act1": "Wherein the witches sort raw matter into shelves and seals.",
    "act2": "Wherein the kingdom of blocks is shaped, and each form named.",
    "act3": "Wherein the lovers gild the line with light and rose.",
    "act4": "Wherein Prospero, his work done, inscribes and releases all.",
}

SCENE_RE = re.compile(r"Scene\s+@(?P<label>[A-Z_][A-Z0-9_]*)\s*:\s*(?P<title>.+)")
RECALL_RE = re.compile(r"^(?P<speaker>[A-Z][A-Za-z ]+):\s*Recall\s+(?P<body>.+)$")
SPEAKER_RE = re.compile(r"^[A-Z][A-Za-z ]+:")
SPEAKER_ONLY_RE = re.compile(r"^(?P<speaker>[A-Z][A-Za-z ]+):$")
BAD_BIG_CAT_RE = re.compile(r"\ba big(?: big){3,} cat\b")
ACT_ROMAN = {"act1": "I", "act2": "II", "act3": "III", "act4": "IV"}

CHARACTER_KEY = {
    "Hecate": "hecate",
    "Horatio": "horatio",
    "Juliet": "juliet",
    "Lady Macbeth": "lady_macbeth",
    "Macbeth": "macbeth",
    "Prospero": "prospero",
    "Puck": "puck",
    "Romeo": "romeo",
    "Rosalind": "rosalind",
}


def _production_source() -> str:
    return "\n".join(path.read_text() for path in sorted(SRC.glob("[0-9]*.spl")))


def _literary() -> dict[str, object]:
    with LITERARY_TOML.open("rb") as f:
        return tomllib.load(f)


def test_locked_play_title_and_act_titles() -> None:
    assembled = ASSEMBLED.read_text()
    data = _literary()

    assert assembled.splitlines()[0] == PLAY_TITLE
    assert data["play"]["title"] == PLAY_TITLE

    acts = data["acts"]
    assert isinstance(acts, dict)
    for key, title in ACT_TITLES.items():
        assert acts[key]["title"] == title
        assert f"Act {ACT_ROMAN[key]}: {title}" in assembled


def test_scene_titles_have_toml_entries_and_match_source() -> None:
    data = _literary()
    scenes = data["scenes"]
    assert isinstance(scenes, dict)

    source_titles = {
        match["label"]: match["title"].strip()
        for match in SCENE_RE.finditer(_production_source())
    }
    assert source_titles
    assert set(source_titles) == set(scenes)
    for label, title in source_titles.items():
        scene = scenes[label]
        assert isinstance(scene, dict)
        assert scene["title"] == title
        assert scene["pattern"] in {
            "wherein",
            "bare_statement",
            "scene_of_character",
            "iconic_echo",
            "cross_character",
            "locale",
        }


def test_recall_phrases_are_in_speaker_pools() -> None:
    data = _literary()
    characters = data["characters"]
    assert isinstance(characters, dict)

    current_speaker: str | None = None
    for line in _production_source().splitlines():
        stripped = line.strip()
        speaker_only = SPEAKER_ONLY_RE.match(stripped)
        if speaker_only:
            current_speaker = speaker_only["speaker"]
            continue

        inline_match = RECALL_RE.match(stripped)
        if inline_match:
            speaker = inline_match["speaker"]
            recall = f"Recall {inline_match['body'].strip()}"
        elif stripped.startswith("Recall ") and current_speaker is not None:
            speaker = current_speaker
            recall = stripped
        else:
            continue

        key = CHARACTER_KEY[speaker]
        pool = characters[key].get("recall_pool", [])
        assert isinstance(pool, list)
        assert recall in pool, f"{speaker} missing recall pool entry {recall!r}"


def test_no_production_big_big_big_big_cat_atoms() -> None:
    source = _production_source()
    assert not BAD_BIG_CAT_RE.search(source)


def test_speaker_colon_layout_is_removed_when_supported() -> None:
    source = _production_source()
    if "speaker_colon_inline" in _literary().get("layout_exceptions", {}):
        return
    offenders = [
        line for line in source.splitlines() if SPEAKER_RE.match(line.strip())
    ]
    assert not offenders[:10]
```

- [ ] **Step 2: Run tests to verify they fail for current source**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py -q
```

Expected: failures for title/act titles, missing TOML scene/Recall sections, `big big big big cat`, and possibly speaker-colon layout.

- [ ] **Step 3: Commit failing tests**

```bash
git add tests/test_literary_compliance.py
git commit -m "test: add production literary compliance gates"
```

## Task 3: Extend `src/literary.toml` Ledger

**Files:**
- Modify: `src/literary.toml`
- Modify: `tests/test_literary_toml_schema.py`

- [ ] **Step 1: Add schema tests for current-surface sections**

Append these tests to `tests/test_literary_toml_schema.py`:

```python
def test_current_surface_sections_exist() -> None:
    data = load()

    play = data.get("play")
    assert isinstance(play, dict)
    assert isinstance(play.get("title"), str)

    acts = data.get("acts")
    assert isinstance(acts, dict)
    assert set(acts) == {"act1", "act2", "act3", "act4"}
    for key, section in acts.items():
        assert isinstance(section, dict), key
        assert isinstance(section.get("title"), str), key

    scenes = data.get("scenes")
    assert isinstance(scenes, dict)
    assert scenes
    for label, scene in scenes.items():
        assert isinstance(scene, dict), label
        assert isinstance(scene.get("title"), str), label
        assert scene.get("pattern") in {
            "wherein",
            "bare_statement",
            "scene_of_character",
            "iconic_echo",
            "cross_character",
            "locale",
        }

    assert isinstance(data.get("iconic_moments"), dict)
    assert isinstance(data.get("dramatic_moments"), dict)


def test_character_soft_variation_and_recall_pools_exist() -> None:
    data = load()
    characters = data["characters"]
    assert isinstance(characters, dict)
    for name, section in characters.items():
        assert isinstance(section, dict), name
        soft = section.get("soft_variation")
        assert isinstance(soft, dict), name
        for key in ("greater_than", "less_than", "equality", "goto_forward", "goto_backward"):
            values = soft.get(key)
            assert isinstance(values, list), (name, key)
            assert values, (name, key)
            assert all(isinstance(value, str) for value in values), (name, key)
        recall_pool = section.get("recall_pool")
        assert isinstance(recall_pool, list), name
        assert all(isinstance(value, str) for value in recall_pool), name
```

- [ ] **Step 2: Run schema tests to verify they fail**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_toml_schema.py::test_current_surface_sections_exist tests/test_literary_toml_schema.py::test_character_soft_variation_and_recall_pools_exist -q
```

Expected: failures because `src/literary.toml` does not yet have the new sections.

- [ ] **Step 3: Add top-level TOML sections**

Add this structure near the top of `src/literary.toml`:

```toml
[play]
title = "Shakedown: A Most Excellent Tragicomedy of Glyph and Line."

[acts.act1]
title = "Wherein the witches sort raw matter into shelves and seals."

[acts.act2]
title = "Wherein the kingdom of blocks is shaped, and each form named."

[acts.act3]
title = "Wherein the lovers gild the line with light and rose."

[acts.act4]
title = "Wherein Prospero, his work done, inscribes and releases all."

[iconic_moments]

[dramatic_moments]
```

- [ ] **Step 4: Add per-character soft-variation pools**

For every `[characters.<name>]` section in `src/literary.toml`, add a nested `[characters.<name>.soft_variation]` table using the pools from `docs/spl/literary-spec.md` section 5.2. Use these exact current minimum values:

```toml
[characters.hecate.soft_variation]
greater_than = ["bigger than", "fresher than"]
less_than = ["worse than", "smaller than", "punier than", "more cursed than", "more foul than"]
equality = ["as cursed as", "as rotten as", "as horrid as"]
goto_forward = ["Let us proceed to"]
goto_backward = ["We must return to"]

[characters.lady_macbeth.soft_variation]
greater_than = ["more bold than", "bigger than"]
less_than = ["worse than", "more villainous than"]
equality = ["as mighty as", "as bold as", "as villainous as"]
goto_forward = ["Let us proceed to"]
goto_backward = ["Let us return to"]

[characters.macbeth.soft_variation]
greater_than = ["more bold than", "bigger than"]
less_than = ["worse than", "more foul than"]
equality = ["as mighty as", "as villainous as"]
goto_forward = ["Let us proceed to"]
goto_backward = ["Let us return to"]

[characters.romeo.soft_variation]
greater_than = ["more sweet than", "nicer than"]
less_than = ["smaller than", "punier than"]
equality = ["as sunny as", "as golden as", "as fair as"]
goto_forward = ["Let us proceed to"]
goto_backward = ["Let us return to"]

[characters.juliet.soft_variation]
greater_than = ["more gentle than", "friendlier than"]
less_than = ["smaller than", "punier than"]
equality = ["as fair as", "as gentle as", "as sweet as"]
goto_forward = ["Let us proceed to"]
goto_backward = ["Let us return to"]

[characters.prospero.soft_variation]
greater_than = ["more noble than", "more peaceful than"]
less_than = ["smaller than", "punier than"]
equality = ["as honest as", "as noble as"]
goto_forward = ["We shall proceed to"]
goto_backward = ["We shall return to"]

[characters.rosalind.soft_variation]
greater_than = ["friendlier than", "jollier than", "nicer than"]
less_than = ["smaller than", "punier than"]
equality = ["as fair as", "as warm as", "as happy as"]
goto_forward = ["Let us proceed to"]
goto_backward = ["Let us return to"]

[characters.horatio.soft_variation]
greater_than = ["friendlier than", "nicer than"]
less_than = ["smaller than", "punier than"]
equality = ["as warm as", "as healthy as", "as happy as"]
goto_forward = ["Let us proceed to"]
goto_backward = ["Let us return to"]

[characters.puck.soft_variation]
greater_than = ["jollier than", "nicer than", "friendlier than"]
less_than = ["smaller than", "punier than"]
equality = ["as fair as", "as noble as", "as rotten as"]
goto_forward = ["Let us proceed to"]
goto_backward = ["Let us return to"]
```

- [ ] **Step 5: Add current Recall pools**

Run this command to list current production Recall lines grouped by speaker:

```bash
rg -n "^[A-Z][A-Za-z ]+: Recall " src/*.spl
```

For each current `Speaker: Recall ...` line, add the exact phrase including `Recall` to that speaker's `recall_pool`, for example:

```toml
recall_pool = [
  "Recall the sealed second shelf.",
  "Recall the sealed first shelf.",
  "Recall the cauldron dreg.",
]
```

Keep punctuation exactly as production source uses it after cleanup.

- [ ] **Step 6: Add current scene-title entries**

Run this command to list current symbolic scene titles:

```bash
rg -n "Scene @[A-Z_][A-Z0-9_]*:" src/*.spl
```

For each `Scene @LABEL: Title.` line, add:

```toml
[scenes.LABEL]
title = "Title."
pattern = "bare_statement"
```

Use `pattern = "wherein"` for titles beginning with `Wherein `. Use `pattern = "scene_of_character"` for titles whose grammatical subject is a named character or role. Use `pattern = "cross_character"` for handoff titles naming both giver and receiver. Use `pattern = "locale"` for short place titles. Use `pattern = "iconic_echo"` only for explicit Shakespeare echoes.

- [ ] **Step 7: Run schema tests**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_toml_schema.py -q
```

Expected: all tests in that file pass.

- [ ] **Step 8: Commit TOML schema expansion**

```bash
git add src/literary.toml tests/test_literary_toml_schema.py
git commit -m "test: cover literary surface ledger"
```

## Task 4: Apply Locked Titles And Assemble

**Files:**
- Modify: `src/00-preamble.spl`
- Modify: `src/10-act1-preprocess.spl`
- Modify: `src/20-act2-block.spl`
- Modify: `src/30-act3-span.spl`
- Modify: `shakedown.spl`

- [ ] **Step 1: Update play and act titles in source fragments**

Make these exact replacements:

```text
src/00-preamble.spl:
The Shakedown.
=> Shakedown: A Most Excellent Tragicomedy of Glyph and Line.

src/00-preamble.spl:
Act I: The underworld of preparation.
=> Act I: Wherein the witches sort raw matter into shelves and seals.

src/10-act1-preprocess.spl:
Act II: The masonry of blocks.
=> Act II: Wherein the kingdom of blocks is shaped, and each form named.

src/20-act2-block.spl:
Act III: The ornament of spans.
=> Act III: Wherein the lovers gild the line with light and rose.

src/30-act3-span.spl:
Act IV: The ceremony of emission.
=> Act IV: Wherein Prospero, his work done, inscribes and releases all.
```

- [ ] **Step 2: Assemble**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
```

Expected: `shakedown.spl` is updated.

- [ ] **Step 3: Run locked-title test**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_locked_play_title_and_act_titles -q
```

Expected: pass.

- [ ] **Step 4: Run behavior smoke**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: `1 passed, 22 deselected`.

- [ ] **Step 5: Commit**

```bash
git add src/00-preamble.spl src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl shakedown.spl
git commit -m "style: lock production play and act titles"
```

## Task 5: Replace Monotonous Large Cat Atoms

**Files:**
- Modify: `src/10-act1-preprocess.spl`
- Modify: `src/20-act2-block.spl`
- Modify: `src/30-act3-span.spl`
- Modify: `src/40-act4-emit.spl`
- Modify: `shakedown.spl`

- [ ] **Step 1: Identify production violations**

Run:

```bash
rg -n "a big big big big cat|a big big big big big|a big big big big big big|a big big big big big big big|a big big big big big big big big" src/*.spl
```

Expected: current production violations are listed.

- [ ] **Step 2: Replace large positive atoms speaker-by-speaker**

For each line with `a big big big big cat` or worse, preserve value by replacing every high-count atom with the active speaker's atom family from "Shared Data Rules".

Examples:

```text
Puck old atom:
a big big big big cat
Puck new atom:
a rural little green sweet flower

Prospero old atom:
a big big big big cat
Prospero new atom:
a warm fine golden noble angel

Romeo old atom:
a big big big big cat
Romeo new atom:
a warm fair golden sunny summer's day

Lady Macbeth old atom:
a big big big big cat
Lady Macbeth new atom:
a proud mighty bold noble hero
```

For atoms larger than 16, decompose into sums of 16, 8, 4, 2, and 1 from that speaker family. Do not introduce negative nouns for positive values.

- [ ] **Step 3: Assemble**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
```

- [ ] **Step 4: Run no-large-cat compliance test**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_no_production_big_big_big_big_cat_atoms -q
```

Expected: pass.

- [ ] **Step 5: Run strict parity**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'
```

Expected: `summary: 1/1 byte-identical`.

- [ ] **Step 6: Commit**

```bash
git add src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl src/40-act4-emit.spl shakedown.spl
git commit -m "style: replace monotonous large value atoms"
```

## Task 6: Align Current Recall And Soft-Variation Surfaces

**Files:**
- Modify: `src/10-act1-preprocess.spl`
- Modify: `src/20-act2-block.spl`
- Modify: `src/30-act3-span.spl`
- Modify: `src/40-act4-emit.spl`
- Modify: `src/literary.toml`
- Modify: `shakedown.spl`

- [ ] **Step 1: Update Hecate backward gotos**

Where Hecate is the speaker and the destination is a previous scene in Act I, replace:

```text
Hecate: Let us return to scene @...
```

with:

```text
Hecate: We must return to scene @...
```

Only change Hecate's own lines. Do not change Puck/Horatio lines in this step.

- [ ] **Step 2: Update Prospero forward gotos**

Where Prospero is the speaker and the line is a forward unconditional goto, replace:

```text
Prospero: Let us proceed to scene @...
```

with:

```text
Prospero: We shall proceed to scene @...
```

Do not change conditional lines spoken by Puck.

- [ ] **Step 3: Ensure Recall pools match final source**

After any wording changes, run:

```bash
rg -n "^[A-Z][A-Za-z ]+: Recall " src/*.spl
```

For every production Recall line, confirm the exact phrase appears in the speaker's `recall_pool` in `src/literary.toml`.

- [ ] **Step 4: Assemble**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
```

- [ ] **Step 5: Run Recall compliance test**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_recall_phrases_are_in_speaker_pools -q
```

Expected: pass.

- [ ] **Step 6: Run focused parity**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'
```

Expected: focused mdtest passes and strict parity remains byte-identical.

- [ ] **Step 7: Commit**

```bash
git add src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl src/40-act4-emit.spl src/literary.toml shakedown.spl
git commit -m "style: align recall and soft-variation surfaces"
```

## Task 7: Apply Supported Folio Layout

**Files:**
- Modify: `src/00-preamble.spl`
- Modify: `src/10-act1-preprocess.spl`
- Modify: `src/20-act2-block.spl`
- Modify: `src/30-act3-span.spl`
- Modify: `src/40-act4-emit.spl`
- Modify: `src/literary.toml`
- Modify: `shakedown.spl`

- [ ] **Step 1: Check layout smoke results**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_spl_layout_smoke.py -q
```

If both smoke tests pass, apply speaker-on-own-line layout and hanging indentation for split value expressions. If the speaker-on-own-line smoke test fails, add this to `src/literary.toml`:

```toml
[layout_exceptions]
speaker_colon_inline = "shakespeare parser rejected speaker names on their own line in tests/test_spl_layout_smoke.py"
```

If the hanging-indent smoke test fails, add:

```toml
[layout_exceptions]
hanging_indent_value_expression = "shakespeare parser rejected split value expressions in tests/test_spl_layout_smoke.py"
```

- [ ] **Step 2: Apply blank-line layout**

Ensure production fragments use:

```text
one blank line between dialogue/stage events
two blank lines between scene declarations
three blank lines before each act declaration after Act I
```

Do not change scene label names or branch targets.

- [ ] **Step 3: Apply speaker layout if supported**

If `test_speaker_name_on_own_line_is_parser_accepted` passes, change dialogue from:

```text
Romeo: You are as fair as nothing.
```

to:

```text
Romeo:
 You are as fair as nothing.
```

Apply this consistently to production fragments.

- [ ] **Step 4: Apply hanging indentation if supported**

If `test_hanging_indent_inside_value_expression_is_parser_accepted` passes, split long value lines at ` and ` boundaries. Example:

```text
Prospero:
 You are as good as the sum of a warm fine golden noble angel and
  the sum of a warm fine golden noble angel and an angel.
```

If the smoke test failed, keep long value expressions on one line.

- [ ] **Step 5: Assemble and run parser smoke through real fixture**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: focused mdtest passes.

- [ ] **Step 6: Run layout compliance**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_speaker_colon_layout_is_removed_when_supported -q
```

Expected: pass.

- [ ] **Step 7: Commit**

```bash
git add src/00-preamble.spl src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl src/40-act4-emit.spl src/literary.toml shakedown.spl
git commit -m "style: apply supported Folio source layout"
```

## Task 8: Final Compliance Sweep And Verification

**Files:**
- Modify only files touched by Tasks 1-7 if a verification command below exposes a specific remaining defect.

- [ ] **Step 1: Run literary compliance tests**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_spl_layout_smoke.py -q
```

Expected: all tests pass, except explicitly documented `xfail` layout smoke tests if the parser rejected a Folio form.

- [ ] **Step 2: Run behavior gates**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_slice1_amps_angle.py -q
```

Expected:

```text
1 passed, 22 deselected
summary: 1/1 byte-identical
5 passed
```

- [ ] **Step 3: Run full project checks**

Run:

```bash
bash -n shakedown
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_spl_layout_smoke.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest
```

Expected:

```text
bash -n exits 0
ruff reports All checks passed
pyright reports 0 errors
pytest reports all non-skipped tests passing
```

- [ ] **Step 4: Confirm assembled output matches source**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
git diff --exit-code shakedown.spl
```

Expected: `git diff --exit-code shakedown.spl` exits 0.

- [ ] **Step 5: Commit final sweep only when Step 1-4 changed files**

If Step 1-4 required any fixes:

```bash
git add src shakedown.spl tests
git commit -m "style: complete literary compliance cleanup"
```

If no files changed, do not create an empty commit.

## Task 9: Record Follow-Up Prevention Work

**Files:**
- Modify: `docs/superpowers/plans/plan-roadmap.md`

- [ ] **Step 1: Add a pending prevention-plan note**

In `docs/superpowers/plans/plan-roadmap.md`, add a note under "Operating rules" or "Source notes" that the next interactive design after this cleanup should cover assembler/codegen prevention: `src/literary.toml` consumption, generated prose quarantine, and numeric phrase generation.

- [ ] **Step 2: Commit note**

```bash
git add docs/superpowers/plans/plan-roadmap.md
git commit -m "docs: note literary prevention follow-up"
```

- [ ] **Step 3: Stop before run-loop**

Do not mark a new roadmap item `in flight` and do not remove `.agent/complete-shakedown.md` in this plan. That is an operator decision after the cleanup is reviewed.
