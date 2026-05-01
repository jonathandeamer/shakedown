# Literary Prevention Rails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Teach assembler/codegen and future prompt authors to route controlled SPL literary surfaces through `src/literary.toml`.

**Architecture:** Keep production SPL fragments readable, but allow explicit `@LIT.<section>.<key>[.<field>]` placeholders for controlled prose. Add a shared `scripts/literary_surfaces.py` loader, have `assemble.py` resolve placeholders, have `codegen_html.py` load numeric atom families from TOML, and add prompt compliance tests that force future run-loop prompts and plans to include the SPL literary protocol.

The literary ledger may contain deferred characters and motifs that are not yet
active in assembled production SPL. Prevention gates must therefore distinguish
TOML ledger coverage from production-surface obligations: active cast members
are the characters introduced in `src/00-preamble.spl`, and every active cast
member must have visible production speech and voice/motif coverage.

**Tech Stack:** Python 3.12, `tomllib`, pytest, pyright, ruff, existing SPL assembler/codegen scripts.

---

## Prerequisite

Run this plan only after the literary compliance cleanup branch has landed and
`src/literary.toml` contains the cleaned play, act, scene, Recall, and
soft-variation ledger. Starting from the cleaned source matters because this
plan makes that ledger operational.

## File Structure

- `docs/superpowers/notes/spl-literary-protocol.md`: reusable prompt block for SPL-changing prompts and plans.
- `CLAUDE.md`: repo-level rule telling prompt authors to use the protocol block.
- `docs/prompt-shakedown.md`: active run-loop prompt loads the protocol block.
- `tests/test_prompt_literary_protocol.py`: structural prompt/plan enforcement.
- `scripts/literary_surfaces.py`: TOML loader and typed access helpers.
- `tests/test_literary_surfaces.py`: loader validation and failure tests.
- `scripts/assemble.py`: placeholder resolution before scene-label resolution.
- `tests/test_assemble.py`: placeholder success/failure tests.
- `src/literary.toml`: add `value_atoms.default`, production-facing motif
  metadata, and any missing key structure needed by the loader.
- `scripts/codegen_html.py`: load value atoms from TOML instead of hardcoded Python constants.
- `tests/test_codegen_html.py`: TOML-backed atom and round-trip tests.
- `tests/test_literary_compliance.py`: production-cast, motif, scene-title
  monotony, blurb, dramatic-moment, and placeholder compliance tests.
- `src/*.spl`: replace controlled title, scene-title, Recall, and recurring value surfaces with `@LIT.` placeholders where readability remains good.
- `shakedown.spl`: regenerated assembled output.

---

## Task 1: Add Prompt Literary Protocol

**Files:**
- Create: `docs/superpowers/notes/spl-literary-protocol.md`
- Create: `tests/test_prompt_literary_protocol.py`
- Modify: `CLAUDE.md`
- Modify: `docs/prompt-shakedown.md`

- [x] **Step 1: Write failing prompt protocol tests**

Create `tests/test_prompt_literary_protocol.py`:

```python
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).parent.parent
PROTOCOL = REPO / "docs" / "superpowers" / "notes" / "spl-literary-protocol.md"
ACTIVE_PROMPT = REPO / "docs" / "prompt-shakedown.md"
CLAUDE = REPO / "CLAUDE.md"
ROADMAP = REPO / "docs" / "superpowers" / "plans" / "plan-roadmap.md"

REQUIRED_DOCS = {
    "docs/spl/literary-spec.md",
    "docs/spl/style-lexicon.md",
    "docs/spl/codegen-style-guide.md",
    "src/literary.toml",
}

SPL_TOUCH_RE = re.compile(
    r"(src/\*\.spl|src/[^`\s]+\.spl|scripts/assemble\.py|codegen)",
    re.IGNORECASE,
)


def _read(path: Path) -> str:
    return path.read_text()


def _active_plan_paths() -> list[Path]:
    paths: list[Path] = []
    for line in _read(ROADMAP).splitlines():
        if not re.search(r"\|\s*in flight\s*(?:\||$)", line):
            continue
        path_matches = re.findall(r"`(docs/superpowers/plans/[^`]+\.md)`", line)
        assert path_matches, f"in-flight roadmap row lacks exact plan path: {line}"
        paths.extend(REPO / path for path in path_matches)
    return paths


def test_protocol_note_exists_and_names_required_inputs() -> None:
    text = _read(PROTOCOL)
    for required in REQUIRED_DOCS:
        assert required in text
    assert "Classify new prose" in text
    assert "Critical" in text
    assert "Stable Utility" in text
    assert "Recall" in text


def test_active_prompt_loads_protocol_note() -> None:
    text = _read(ACTIVE_PROMPT)
    assert "@docs/superpowers/notes/spl-literary-protocol.md" in text


def test_claude_tells_prompt_authors_to_use_protocol() -> None:
    text = _read(CLAUDE)
    assert "docs/superpowers/notes/spl-literary-protocol.md" in text
    assert "SPL-changing prompts" in text


def test_in_flight_roadmap_row_names_exact_plan_path() -> None:
    paths = _active_plan_paths()
    assert len(paths) == 1
    assert paths[0].exists()


def test_in_flight_spl_plans_reference_protocol_or_required_docs() -> None:
    for path in _active_plan_paths():
        text = _read(path)
        if not SPL_TOUCH_RE.search(text):
            continue
        has_protocol = "docs/superpowers/notes/spl-literary-protocol.md" in text
        has_docs = all(required in text for required in REQUIRED_DOCS)
        assert has_protocol or has_docs, path
        required_tests = {
            "tests/test_literary_compliance.py",
            "tests/test_literary_toml_schema.py",
            "tests/test_assemble.py",
            "tests/test_codegen_html.py",
            "tests/test_mdtest.py -k 'Amps and angle'",
        }
        missing_tests = {
            required for required in required_tests if required not in text
        }
        assert not missing_tests, (path, missing_tests)
```

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_prompt_literary_protocol.py -q
```

Expected: failures because the protocol note does not exist and the active
prompt does not load it.

- [x] **Step 3: Create the reusable protocol note**

Create `docs/superpowers/notes/spl-literary-protocol.md`:

```markdown
# SPL Literary Protocol

Use this block in any run-loop prompt or implementation plan that asks an agent
to edit `src/*.spl`, `scripts/assemble.py`, `scripts/codegen_html.py`, or any
future SPL code generator.

Before editing, read:

- `docs/spl/literary-spec.md`
- `docs/spl/style-lexicon.md`
- `docs/spl/codegen-style-guide.md`
- `src/literary.toml`

Rules:

- Classify new prose before writing it: Critical, Stable Utility, Incidental,
  Recall, title, scene title, or dramatic tag.
- Controlled surfaces belong in `src/literary.toml` and are referenced from SPL
  or codegen by key.
- Do not invent recurring literary surfaces inline when TOML already owns the
  category.
- Use `docs/spl/style-lexicon.md` and `docs/spl/codegen-style-guide.md` for
  Incidental prose that remains hand-authored.
- Run the exact compliance tests named by the active plan after changing SPL,
  assembler, or codegen behavior. Do not write "literary compliance" as a
  generic placeholder for test commands.
```

- [x] **Step 4: Update active prompt to load the protocol**

In `docs/prompt-shakedown.md`, add this university reference after
`@docs/spl/literary-spec.md`:

```markdown
@docs/superpowers/notes/spl-literary-protocol.md
```

Then replace the existing standing rule:

```markdown
- Aesthetic policy lives in `@docs/spl/literary-spec.md`. Reach for it before
  writing any decorative surface.
```

with:

```markdown
- SPL literary policy lives in `@docs/superpowers/notes/spl-literary-protocol.md`.
  Follow it before editing SPL, assembler, codegen, or literary surface data.
```

- [x] **Step 5: Update CLAUDE.md for prompt authors**

In `CLAUDE.md`, add this section after "run-loop" and before "Operator halt
switch":

```markdown
## SPL literary protocol for prompts and plans

Any SPL-changing prompt or implementation plan must use
`docs/superpowers/notes/spl-literary-protocol.md`. This includes work that edits
`src/*.spl`, `scripts/assemble.py`, `scripts/codegen_html.py`, or future SPL
generators. Prompt authors must include the protocol block or load it by
university reference, and SPL-changing plans must name the literary compliance
tests they expect the implementation agent to run.
```

- [x] **Step 6: Run tests**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_prompt_literary_protocol.py -q
```

Expected: all tests pass.

- [x] **Step 7: Commit**

```bash
git add docs/superpowers/notes/spl-literary-protocol.md tests/test_prompt_literary_protocol.py CLAUDE.md docs/prompt-shakedown.md
git commit -m "docs: add SPL literary prompt protocol"
```

---

## Task 2: Add Literary Surface Loader

**Files:**
- Create: `scripts/literary_surfaces.py`
- Create: `tests/test_literary_surfaces.py`

- [x] **Step 1: Write failing loader tests**

Create `tests/test_literary_surfaces.py`:

```python
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.literary_surfaces import (
    LiterarySurfaces,
    load_literary_surfaces,
)


def _write_literary(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "literary.toml"
    path.write_text(text)
    return path


def test_resolve_known_literary_keys(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[play]
title = "Shakedown."

[acts.act1]
title = "Wherein the first act begins."

[scenes.DETAB_RAW]
title = "The cauldron is stirred."

[characters.hecate.recall]
detab_cauldron = "Recall the cauldron dreg."

[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
v2 = "a black cat"
v4 = "a furry black cat"
v8 = "a little furry black cat"
v16 = "a normal little furry black cat"
""",
    )

    surfaces = load_literary_surfaces(path)

    assert surfaces.resolve("play.title") == "Shakedown."
    assert surfaces.resolve("acts.act1.title") == "Wherein the first act begins."
    assert surfaces.resolve("scenes.DETAB_RAW.title") == "The cauldron is stirred."
    assert (
        surfaces.resolve("characters.hecate.recall.detab_cauldron")
        == "Recall the cauldron dreg."
    )
    assert surfaces.value_atoms("default")[16] == "a normal little furry black cat"


def test_unknown_key_raises_clear_error(tmp_path: Path) -> None:
    path = _write_literary(tmp_path, "[play]\ntitle = \"Shakedown.\"\n")
    surfaces = load_literary_surfaces(path)

    with pytest.raises(KeyError, match="play.subtitle"):
        surfaces.resolve("play.subtitle")


def test_value_atoms_require_integer_keys(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
bad = "a cat"
""",
    )

    with pytest.raises(ValueError, match="value_atoms.default.bad"):
        load_literary_surfaces(path)


def test_value_atoms_reject_overlong_atoms(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[value_atoms.default]
v0 = "nothing"
v1 = "a big big big big big big cat"
""",
    )

    with pytest.raises(ValueError, match="exceeds 6 words"):
        load_literary_surfaces(path)


def test_value_atoms_reject_repeated_adjectives(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
v2 = "a big big cat"
""",
    )

    with pytest.raises(ValueError, match="repeats adjective"):
        load_literary_surfaces(path)


def test_literary_surfaces_type_is_constructible() -> None:
    surfaces = LiterarySurfaces(data={"play": {"title": "Shakedown."}})
    assert surfaces.resolve("play.title") == "Shakedown."
```

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_surfaces.py -q
```

Expected: import failure because `scripts/literary_surfaces.py` does not exist.

- [x] **Step 3: Implement the loader**

Create `scripts/literary_surfaces.py`:

```python
"""Load and resolve TOML-backed SPL literary surfaces."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

ATOM_WORD_MAX = 6
_VALUE_KEY_RE = re.compile(r"^v(?P<value>0|[1-9][0-9]*)$")


@dataclass(frozen=True)
class LiterarySurfaces:
    """Resolved access to `src/literary.toml`."""

    data: dict[str, object]

    def resolve(self, key: str) -> str:
        current: object = self.data
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                raise KeyError(key)
            current = current[part]
        if not isinstance(current, str):
            raise KeyError(key)
        return current

    def value_atoms(self, family: str = "default") -> dict[int, str]:
        value_atoms = self.data.get("value_atoms")
        if not isinstance(value_atoms, dict):
            raise KeyError("value_atoms")
        raw_family = value_atoms.get(family)
        if not isinstance(raw_family, dict):
            raise KeyError(f"value_atoms.{family}")
        atoms: dict[int, str] = {}
        for key, phrase in raw_family.items():
            if not isinstance(key, str) or not isinstance(phrase, str):
                raise ValueError(f"value_atoms.{family}.{key}")
            match = _VALUE_KEY_RE.match(key)
            if match is None:
                raise ValueError(f"value_atoms.{family}.{key}")
            _validate_atom_phrase(f"value_atoms.{family}.{key}", phrase)
            atoms[int(match["value"])] = phrase
        return atoms


def load_literary_surfaces(path: Path) -> LiterarySurfaces:
    with path.open("rb") as f:
        data = tomllib.load(f)
    surfaces = LiterarySurfaces(data=cast(dict[str, object], data))
    if "value_atoms" in data:
        value_atoms = data["value_atoms"]
        if isinstance(value_atoms, dict):
            for family in value_atoms:
                if isinstance(family, str):
                    surfaces.value_atoms(family)
    return surfaces


def _validate_atom_phrase(key: str, phrase: str) -> None:
    for atom in _atoms_in(phrase):
        words = atom.split()
        if len(words) > ATOM_WORD_MAX:
            raise ValueError(
                f"{key}: atom {atom!r} exceeds {ATOM_WORD_MAX} words"
            )
        _reject_repeated_adjectives(key, atom)


def _reject_repeated_adjectives(key: str, atom: str) -> None:
    words = atom.split()
    if len(words) < 3 or words[0] not in {"a", "an"}:
        return
    adjectives = words[1:-1]
    if len(adjectives) != len(set(adjectives)):
        raise ValueError(f"{key}: atom {atom!r} repeats adjective")


def _atoms_in(phrase: str) -> list[str]:
    text = phrase.strip()
    for prefix in ("the sum of ", "the product of "):
        if not text.lower().startswith(prefix):
            continue
        rest = text[len(prefix) :]
        for match in reversed(list(re.finditer(r" and ", rest))):
            left = rest[: match.start()]
            right = rest[match.end() :]
            return _atoms_in(left) + _atoms_in(right)
        return [text]
    square_prefix = "the square of "
    if text.lower().startswith(square_prefix):
        return _atoms_in(text[len(square_prefix) :])
    return [text]
```

- [x] **Step 4: Run tests and type checks**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_surfaces.py -q
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check scripts/literary_surfaces.py tests/test_literary_surfaces.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright scripts/literary_surfaces.py tests/test_literary_surfaces.py
```

Expected: all pass.

- [x] **Step 5: Commit**

```bash
git add scripts/literary_surfaces.py tests/test_literary_surfaces.py
git commit -m "feat: load literary surface data"
```

---

## Task 3: Resolve Literary Placeholders In Assembler

**Files:**
- Modify: `scripts/assemble.py`
- Modify: `tests/test_assemble.py`

- [x] **Step 1: Add failing assembler placeholder tests**

Append to `tests/test_assemble.py`:

```python
def test_assemble_resolves_literary_placeholders(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "fragment.spl").write_text(
        "@LIT.play.title\n"
        "Act I: @LIT.acts.act1.title\n"
        "Scene @START: @LIT.scenes.START.title\n"
    )
    (src / "manifest.toml").write_text('fragments = ["fragment.spl"]\n')
    (src / "literary.toml").write_text(
        """
[play]
title = "Shakedown."

[acts.act1]
title = "Wherein the first act begins."

[scenes.START]
title = "The page awakens."
"""
    )

    output = tmp_path / "out.spl"
    assemble(src_dir=src, manifest=src / "manifest.toml", output=output)

    assert output.read_text() == (
        "Shakedown.\n"
        "Act I: Wherein the first act begins.\n"
        "Scene I: The page awakens.\n"
    )


def test_assemble_unknown_literary_placeholder_raises(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "fragment.spl").write_text("@LIT.play.subtitle\n")
    (src / "manifest.toml").write_text('fragments = ["fragment.spl"]\n')
    (src / "literary.toml").write_text("[play]\ntitle = \"Shakedown.\"\n")

    output = tmp_path / "out.spl"
    with pytest.raises(KeyError, match="play.subtitle"):
        assemble(src_dir=src, manifest=src / "manifest.toml", output=output)
```

- [x] **Step 2: Run tests to verify they fail**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_assemble.py -q
```

Expected: the new placeholder test fails because placeholders are not resolved.

- [x] **Step 3: Implement placeholder resolution**

Modify `scripts/assemble.py`:

```python
import re
import tomllib
from pathlib import Path

from scripts.literary_surfaces import load_literary_surfaces
```

Add:

```python
_LIT_RE = re.compile(r"@LIT\.([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*)")


def _resolve_literary_placeholders(source: str, literary_path: Path) -> str:
    if "@LIT." not in source:
        return source
    surfaces = load_literary_surfaces(literary_path)

    def replace(match: re.Match[str]) -> str:
        return surfaces.resolve(match.group(1))

    resolved = _LIT_RE.sub(replace, source)
    if "@LIT." in resolved:
        raise ValueError("unresolved @LIT placeholder")
    return resolved
```

In `assemble`, replace:

```python
combined = "".join((src_dir / name).read_text() for name in fragments)
resolved = _resolve_scene_labels(combined)
```

with:

```python
combined = "".join((src_dir / name).read_text() for name in fragments)
with_literary = _resolve_literary_placeholders(
    combined,
    src_dir / "literary.toml",
)
resolved = _resolve_scene_labels(with_literary)
```

- [x] **Step 4: Run assembler checks**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_assemble.py tests/test_literary_surfaces.py -q
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check scripts/assemble.py scripts/literary_surfaces.py tests/test_assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright scripts/assemble.py scripts/literary_surfaces.py tests/test_assemble.py
```

Expected: all pass.

- [x] **Step 5: Commit**

```bash
git add scripts/assemble.py tests/test_assemble.py
git commit -m "feat: resolve literary placeholders in assembler"
```

---

## Task 4: Move Codegen Value Atoms Into TOML And Compact Recipes

**Files:**
- Modify: `src/literary.toml`
- Modify: `scripts/codegen_html.py`
- Modify: `tests/test_codegen_html.py`

- [x] **Step 1: Add default value atom family to TOML**

Add this section to `src/literary.toml`:

```toml
[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
v2 = "a black cat"
v4 = "a furry black cat"
v8 = "a little furry black cat"
v16 = "a normal little furry black cat"
```

- [x] **Step 2: Update codegen tests for TOML-loaded atoms and compact recipes**

In `tests/test_codegen_html.py`, add `import re`, then change the atom
expectation for `16` by adding this case to `test_emit_byte_atom_forms`:

```python
(16, "a normal little furry black cat"),
```

Add `emit_value` to the import from `scripts.codegen_html`.

Add these tests:

```python
def test_emit_byte_uses_toml_value_atoms() -> None:
    assert emit_byte(16) == "a normal little furry black cat"
    assert "big big big big cat" not in emit_byte(16)


@pytest.mark.parametrize("value", [38, 65, 97, 256, 505])
def test_emit_value_uses_compact_large_value_recipes(value: int) -> None:
    phrase = emit_value(value)

    assert parse_value_phrase(phrase) == value
    assert "the product of" in phrase or "the square of" in phrase
    assert _max_atom_repetition(phrase) <= 3


def test_parse_value_phrase_understands_compact_arithmetic() -> None:
    assert parse_value_phrase("the square of a normal little furry black cat") == 256
    assert (
        parse_value_phrase(
            "the product of a normal little furry black cat and a furry black cat"
        )
        == 64
    )


def _max_atom_repetition(phrase: str) -> int:
    atoms = _atoms(phrase)
    return max((atoms.count(atom) for atom in set(atoms)), default=0)


def _atoms(phrase: str) -> list[str]:
    text = phrase.strip()
    for prefix in ("the sum of ", "the product of "):
        if not text.lower().startswith(prefix):
            continue
        rest = text[len(prefix) :]
        left, right = _split_binary_for_test(rest, phrase)
        return _atoms(left) + _atoms(right)
    square_prefix = "the square of "
    if text.lower().startswith(square_prefix):
        return _atoms(text[len(square_prefix) :])
    return [text]


def _split_binary_for_test(rest: str, phrase: str) -> tuple[str, str]:
    for match in reversed(list(re.finditer(r" and ", rest))):
        left = rest[: match.start()]
        right = rest[match.end() :]
        try:
            parse_value_phrase(left)
            parse_value_phrase(right)
        except ValueError:
            continue
        return left, right
    raise ValueError(f"malformed binary expression: {phrase!r}")
```

Also add a failing test that rejects repeated adjectives inside one generated
atom:

```python
def test_emit_byte_atoms_do_not_repeat_adjectives() -> None:
    for value in [1, 2, 4, 8, 16]:
        phrase = emit_byte(value)
        adjectives = _atom_adjectives(phrase)
        assert len(adjectives) == len(set(adjectives)), phrase


def _atom_adjectives(phrase: str) -> list[str]:
    words = phrase.split()
    return words[1:-1]
```

Extend `tests/test_literary_surfaces.py` so TOML atom families are held to the
same rule before codegen consumes them:

```python
def test_value_atoms_reject_repeated_adjectives(tmp_path: Path) -> None:
    path = _write_literary(
        tmp_path,
        """
[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
v2 = "a big big cat"
""",
    )

    with pytest.raises(ValueError, match="repeats adjective"):
        load_literary_surfaces(path)
```

- [x] **Step 3: Run tests to verify they fail before implementation**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_codegen_html.py -q
```

Expected: the new TOML and compact-recipe tests fail because codegen still uses
hardcoded atoms and repeated largest-atom subtraction.

- [x] **Step 4: Implement TOML-backed atoms**

Modify `scripts/codegen_html.py`:

```python
"""HTML byte-literal codegen."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.literary_surfaces import load_literary_surfaces

_ROOT = Path(__file__).parent.parent
_LITERARY_TOML = _ROOT / "src" / "literary.toml"
_ATOM_BY_VALUE = load_literary_surfaces(_LITERARY_TOML).value_atoms("default")
```

Add `emit_value`, then replace `emit_byte`, `_decompose`, and
`parse_value_phrase` with compact recipe-aware versions. Keep `emit_literal` and
`emit_speak_lines` as callers of `emit_byte`:

```python
_ATOM_TO_VALUE = {phrase: value for value, phrase in _ATOM_BY_VALUE.items()}


def emit_value(value: int) -> str:
    """Return the canonical SPL value phrase for a non-negative integer."""
    if value < 0 or value > 1024:
        raise ValueError(f"value out of supported range: {value}")
    if value in _ATOM_BY_VALUE:
        return _ATOM_BY_VALUE[value]
    return _decompose(value)


def emit_byte(value: int) -> str:
    """Return the canonical SPL value phrase for an integer byte."""
    if value < 0 or value > 255:
        raise ValueError(f"byte value out of range: {value}")
    return emit_value(value)


def _decompose(value: int) -> str:
    terms: list[str] = []
    if value >= 256:
        count = value // 256
        terms.extend([f"the square of {_ATOM_BY_VALUE[16]}"] * count)
        value %= 256

    sixteens = value // 16
    if sixteens == 1:
        terms.append(_ATOM_BY_VALUE[16])
    elif sixteens > 1:
        terms.append(
            f"the product of {_ATOM_BY_VALUE[16]} and {emit_value(sixteens)}"
        )
    value %= 16

    for atom_value in sorted(_ATOM_BY_VALUE, reverse=True):
        if atom_value == 0:
            continue
        if atom_value <= value:
            terms.append(_ATOM_BY_VALUE[atom_value])
            value -= atom_value

    return _sum_terms(terms)


def _sum_terms(terms: list[str]) -> str:
    if not terms:
        return _ATOM_BY_VALUE[0]
    phrase = terms[-1]
    for term in reversed(terms[:-1]):
        phrase = f"the sum of {term} and {phrase}"
    return phrase


def parse_value_phrase(phrase: str) -> int:
    """Reverse `emit_byte`; used by round-trip tests."""
    text = phrase.strip()
    if text in _ATOM_TO_VALUE:
        return _ATOM_TO_VALUE[text]
    if text.lower().startswith("the square of "):
        inner = text[len("the square of ") :]
        value = parse_value_phrase(inner)
        return value * value
    if text.lower().startswith("the product of "):
        rest = text[len("the product of ") :]
        left, right = _split_binary(rest, phrase)
        return parse_value_phrase(left) * parse_value_phrase(right)
    if text.lower().startswith("the sum of "):
        rest = text[len("the sum of ") :]
        left, right = _split_binary(rest, phrase)
        return parse_value_phrase(left) + parse_value_phrase(right)
    raise ValueError(f"unrecognised atom: {phrase!r}")


def _split_binary(rest: str, phrase: str) -> tuple[str, str]:
    for match in reversed(list(re.finditer(r" and ", rest))):
        left = rest[: match.start()]
        right = rest[match.end() :]
        try:
            parse_value_phrase(left)
            parse_value_phrase(right)
        except ValueError:
            continue
        return left, right
    raise ValueError(f"malformed binary expression: {phrase!r}")
```

The exact implementation may factor helpers differently, but it must preserve
these properties:

- no generated phrase for representative large values repeats the same atom more
  than three times
- no generated atom repeats an adjective inside one noun phrase, such as
  `big big`, `fine fine`, or `noble noble`
- no configured TOML atom family repeats an adjective inside one noun phrase
- 256 is expressed with `the square of ...`, not sixteen repeated 16-value atoms
- values with several 16-value chunks use `the product of ... and ...`
- every generated phrase round-trips through `parse_value_phrase`

- [x] **Step 5: Run codegen checks**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_codegen_html.py tests/test_literary_surfaces.py -q
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check scripts/codegen_html.py scripts/literary_surfaces.py tests/test_codegen_html.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright scripts/codegen_html.py scripts/literary_surfaces.py tests/test_codegen_html.py
```

Expected: all pass.

- [x] **Step 6: Commit**

```bash
git add src/literary.toml scripts/codegen_html.py tests/test_codegen_html.py
git commit -m "feat: drive byte value atoms from literary data"
```

---

## Task 5: Convert Production Controlled Surfaces To Placeholders

**Files:**
- Modify: `src/00-preamble.spl`
- Modify: `src/10-act1-preprocess.spl`
- Modify: `src/20-act2-block.spl`
- Modify: `src/30-act3-span.spl`
- Modify: `src/40-act4-emit.spl`
- Modify: `shakedown.spl`
- Modify: `tests/test_literary_compliance.py`
- Modify: `src/literary.toml`

- [x] **Step 1: Add or update source-placeholder and production-literary tests**

Add this import near the top of `tests/test_literary_compliance.py` if it is
not already present:

```python
from collections import Counter
```

Add the following helpers/tests to `tests/test_literary_compliance.py`. If a
helper or test with the same purpose already exists, update the existing
definition instead of appending a duplicate:

```python
SCENE_TITLE_WORD_LIMITS = {
    "wherein": (6, 12),
    "bare_statement": (4, 10),
    "scene_of_character": (5, 10),
    "iconic_echo": (3, 8),
    "cross_character": (6, 14),
    "locale": (3, 7),
}

VALUE_ATOM_RE = re.compile(
    r"\b(?:a|an)\s+(?P<adjectives>[a-z][a-z' -]*?)\s+"
    r"(?P<noun>cat|flower|day|rose|hero|angel|tree|brother)\b",
    re.IGNORECASE,
)
REFERENCE_SCENES = {
    "LYRIC_OPEN_CONSULT_REFERENCE_ONE",
    "LYRIC_CONSULT_REFERENCE_ONE",
    "LYRIC_OPEN_OUTPUT_REFERENCE_ONE",
    "LYRIC_OPEN_CONSULT_REFERENCE_TWO",
    "LYRIC_CONSULT_REFERENCE_TWO",
    "LYRIC_OPEN_OUTPUT_REFERENCE_TWO",
}
IMPLEMENTATION_META_WORDS = {
    "adjective",
    "adjectives",
    "codegen",
    "implementation",
    "mechanism",
    "token",
    "tokens",
}
ACT_TITLE_DULL_VERBS = {
    "act4": {"tests", "opens", "closes"},
}
MAX_DULL_VERB_USES = 2


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
        for match in SCENE_RE.finditer(_resolved_production_source())
    }


def _words(text: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[A-Za-z']+", text)}


def _preamble_character_lines(source: str) -> set[str]:
    preamble = source.split("Act I:", maxsplit=1)[0]
    return {
        character
        for character in CHARACTER_KEY
        if re.search(rf"^{re.escape(character)},", preamble, re.MULTILINE)
    }


def _resolved_production_source() -> str:
    data = _literary()
    source = _production_source()

    def replace(match: re.Match[str]) -> str:
        current: object = data
        key = match.group(1)
        for part in key.split("."):
            assert isinstance(current, dict), key
            current = current[part]
        assert isinstance(current, str), key
        return current

    return re.sub(r"@LIT\.([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*)", replace, source)


def test_value_atoms_do_not_repeat_adjectives() -> None:
    for match in VALUE_ATOM_RE.finditer(_production_source()):
        adjectives = match["adjectives"].lower().split()
        assert len(adjectives) == len(set(adjectives)), match.group(0)


def test_scene_titles_fit_declared_pattern_lengths() -> None:
    scenes = _literary()["scenes"]
    assert isinstance(scenes, dict)
    for label, scene in scenes.items():
        pattern = scene["pattern"]
        title = scene["title"]
        low, high = SCENE_TITLE_WORD_LIMITS[pattern]
        word_count = len(re.findall(r"[A-Za-z0-9']+", title))
        assert low <= word_count <= high, (label, pattern, title)


def test_prospero_assignment_equalities_use_his_pool() -> None:
    data = _literary()
    equality_pool = data["characters"]["prospero"]["soft_variation"]["equality"]
    current_speaker: str | None = None
    for line in _production_source().splitlines():
        stripped = line.strip()
        speaker_only = SPEAKER_ONLY_RE.match(stripped)
        if speaker_only:
            current_speaker = speaker_only["speaker"]
            continue
        if current_speaker != "Prospero":
            continue
        match = re.search(r"\bYou are (as [a-z-]+ as)\b", stripped)
        if match:
            assert match.group(1) in equality_pool, stripped


def test_named_production_characters_have_speaking_lines() -> None:
    source = _production_source()
    introduced = _preamble_character_lines(source)
    counts = {
        character: source.count(f"\n{character}:\n")
        for character in introduced
    }
    assert all(counts[character] > 0 for character in introduced), counts


def test_reference_librarian_is_visible_in_reference_scenes() -> None:
    blocks = _scene_blocks(_production_source())
    reference_text = "\n".join(blocks[label] for label in sorted(REFERENCE_SCENES))
    assert reference_text.count("Rosalind:") >= 4


def test_active_character_motifs_are_visible() -> None:
    data = _literary()
    characters = data["characters"]
    production_motifs = data["production_motifs"]
    assert isinstance(characters, dict)
    assert isinstance(production_motifs, dict)
    titles = " ".join(_scene_titles().values())
    source = _production_source()
    active_keys = {
        CHARACTER_KEY[character]
        for character in _preamble_character_lines(source)
    }

    missing: dict[str, set[str]] = {}
    for key in active_keys & set(production_motifs):
        character = characters[key]
        motifs = production_motifs[key]
        assert isinstance(character, dict)
        assert isinstance(motifs, list)
        assert all(isinstance(motif, str) for motif in motifs)
        blurb = character["blurb"]
        assert isinstance(blurb, str)
        surfaces = f"{blurb} {titles}"
        motif_set = set(motifs)
        motif_hits = _words(surfaces) & motif_set
        if not motif_hits:
            missing[key] = motif_set
    assert not missing


def test_act_scene_titles_avoid_overused_utility_verbs() -> None:
    titles = _scene_titles()
    by_act: dict[str, list[str]] = {"act1": [], "act2": [], "act3": [], "act4": []}
    for label, title in titles.items():
        if label.startswith("SCRIBE_") or label == "ACT_IV_DONE":
            by_act["act4"].append(title)

    overused: dict[str, dict[str, int]] = {}
    for act, dull_verbs in ACT_TITLE_DULL_VERBS.items():
        words = Counter(
            word
            for title in by_act[act]
            for word in re.findall(r"[A-Za-z']+", title.lower())
        )
        act_overused = {
            verb: words[verb]
            for verb in dull_verbs
            if words[verb] > MAX_DULL_VERB_USES
        }
        if act_overused:
            overused[act] = act_overused
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
        character_words = _words(character)
        visible_words = _words(titles[scene]) | _words(blocks[scene])
        if not visible_words & character_words:
            missing.append(name)
    assert not missing


def test_controlled_surfaces_use_literary_placeholders_in_source() -> None:
    source = _production_source()
    assert "@LIT.play.title" in source
    for act in ACT_TITLES:
        assert f"@LIT.acts.{act}.title" in source
    assert "@LIT.scenes." in source
    assert "@LIT.characters." in source


def test_all_literary_placeholders_in_source_resolve() -> None:
    source = _production_source()
    resolved = _resolved_production_source()
    assert "@LIT." in source
    assert "@LIT." not in resolved
    assert "@LIT." not in ASSEMBLED.read_text()


def test_scene_ledger_matches_source_scene_labels() -> None:
    data = _literary()
    scenes = data["scenes"]
    assert isinstance(scenes, dict)
    source_labels = {
        match["label"] for match in SCENE_RE.finditer(_production_source())
    }
    assert set(scenes) == source_labels


def test_controlled_literals_are_not_duplicated_inline() -> None:
    data = _literary()
    source = _production_source()
    assembled = ASSEMBLED.read_text()

    play = data["play"]
    assert isinstance(play, dict)
    assert play["title"] in assembled
    assert play["title"] not in source

    acts = data["acts"]
    assert isinstance(acts, dict)
    for act in acts.values():
        assert isinstance(act, dict)
        title = act["title"]
        assert isinstance(title, str)
        assert title in assembled
        assert title not in source
```

Add the following schema checks to `tests/test_literary_toml_schema.py`. If a
check with the same purpose already exists, update the existing definition
instead of appending a duplicate:

```python
REQUIRED_HECATE_VALUE_ATOMS = {
    "v1": "a cat",
    "v2": "a black cat",
    "v4": "a furry black cat",
    "v8": "a little furry black cat",
    "v16": "a normal little furry black cat",
}


def test_hecate_value_atoms_match_cleaned_cat_family() -> None:
    data = load()
    stable = data["characters"]["hecate"]["stable_utility"]
    for key, phrase in REQUIRED_HECATE_VALUE_ATOMS.items():
        assert stable[key] == phrase


def test_iconic_and_dramatic_moment_ledgers_are_populated() -> None:
    data = load()
    iconic = data["iconic_moments"]
    dramatic = data["dramatic_moments"]
    assert len(iconic) >= 4
    assert len(dramatic) >= 3


def test_production_motifs_shape() -> None:
    data = load()
    motifs = data["production_motifs"]
    characters = data["characters"]
    assert isinstance(motifs, dict)
    assert isinstance(characters, dict)
    assert set(motifs) <= set(characters)
    for key, values in motifs.items():
        assert isinstance(key, str)
        assert isinstance(values, list)
        assert values
        assert all(isinstance(value, str) for value in values)
```

The active-character motif test is intentionally production-facing. It does not
require deferred TOML characters such as a future Macbeth role to appear in the
assembled preamble or to speak before the implementation actually uses them.

- [x] **Step 1a: Add production motif metadata**

Add this section to `src/literary.toml`:

```toml
[production_motifs]
juliet = ["night", "star", "stars", "starlit", "silver"]
prospero = ["revels", "inscribes", "releases", "seals"]
puck = ["messenger", "room", "colour", "flies"]
romeo = ["sun", "sunlit", "morning", "summer", "golden"]
rosalind = ["forest", "shelf", "references", "bargain"]
```

Only list characters whose motifs are active production obligations. Deferred
ledger characters may remain under `[characters]` without appearing in
`[production_motifs]` until they enter the assembled preamble.

- [x] **Step 1b: Update existing compliance tests for placeholders and keyed Recall**

Existing tests that compare raw `src/*.spl` titles against TOML must resolve
`@LIT.` placeholders before comparing. Update them to use
`_resolved_production_source()` for title, motif, and dramatic-surface checks.

For Recall, convert `recall_pool` arrays to keyed tables before replacing
source Recall strings, and update helper code so tests read the keyed table:

```python
def _recall_values(character: dict[str, object]) -> set[str]:
    recall = character.get("recall")
    if isinstance(recall, dict):
        return {value for value in recall.values() if isinstance(value, str)}
    recall_pool = character.get("recall_pool")
    if isinstance(recall_pool, list):
        return {value for value in recall_pool if isinstance(value, str)}
    return set()
```

Then change the Recall compliance test to assert each resolved production
Recall is present in `_recall_values(characters[key])`. Keep `recall_pool`
compatibility only until the keyed table conversion lands in the same task;
after conversion, schema tests should require keyed `recall` tables and may
allow `recall_pool` only as a temporary compatibility mirror if the plan chooses
to keep both.

- [x] **Step 2: Capture pre-conversion implemented fixture baseline**

Capture the implemented fixture output before replacing any source text with
placeholders:

```bash
mkdir -p /tmp/shakedown-literary-prevention-baseline
fixture="$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text"
./shakedown < "$fixture" > "/tmp/shakedown-literary-prevention-baseline/Amps and angle encoding.xhtml"
```

Expected: command exits 0. If `_IMPLEMENTED_FIXTURES` in
`tests/test_mdtest.py` has grown by the time this plan runs, capture every
fixture named there.

- [x] **Step 3: Run test to verify it fails**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_compliance.py::test_controlled_surfaces_use_literary_placeholders_in_source -q
```

Expected: fails because production source still contains direct prose.
The scene-title length, Prospero equality, Hecate atom family, and
iconic/dramatic ledger tests should already pass before placeholder conversion;
if any fail, stop and restore the cleaned source before proceeding.

- [x] **Step 4: Replace play and act titles**

In `src/00-preamble.spl`, replace the literal play title line with:

```spl
@LIT.play.title
```

In each act fragment, replace locked act title text with:

```spl
Act I: @LIT.acts.act1.title
Act II: @LIT.acts.act2.title
Act III: @LIT.acts.act3.title
Act IV: @LIT.acts.act4.title
```

- [x] **Step 5: Replace scene titles**

For each scene declaration of the form:

```spl
Scene @LABEL: Existing title.
```

replace only the title text:

```spl
Scene @LABEL: @LIT.scenes.LABEL.title
```

Use the exact symbolic label already present in the scene declaration.

- [x] **Step 6: Replace Recall phrases with character keys**

For each production Recall phrase that exists in
`src/literary.toml` under `[characters.<character>.recall]`, replace:

```spl
Speaker:
 Recall existing phrase.
```

with:

```spl
Speaker:
 @LIT.characters.<character>.recall.<key>
```

For inline Recall forms, replace:

```spl
Speaker: Recall existing phrase.
```

with:

```spl
Speaker: @LIT.characters.<character>.recall.<key>
```

Use the existing TOML key for the exact phrase. If the cleanup ledger currently
stores Recall pools as arrays, first convert those pools to keyed tables while
preserving the same phrase strings.

- [x] **Step 7: Assemble and run focused checks**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/assemble.py
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_assemble.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: assembler tests pass, the Slice 1 fixture still passes, and any
remaining literary compliance failure names a prevention-specific gate introduced
by this task rather than a pre-existing cleanup issue.
The placeholder conversion must preserve the scene-title pattern-length gate,
Prospero equality-pool gate, Hecate value-atom family gate, and populated
iconic/dramatic moment ledger gate. It must also preserve the production-cast,
active-motif, scene-title monotony, blurb meta-language, and dramatic-moment
visibility gates.

- [x] **Step 8: Compare implemented fixture output to the pre-conversion baseline**

Only compare fixtures currently marked implemented in `tests/test_mdtest.py`.
Do not use all 23 mdtest fixtures here; non-shipped fixtures may correctly exit
nonzero.

Run:

```bash
mkdir -p /tmp/shakedown-literary-prevention-after
fixture="$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text"
./shakedown < "$fixture" > "/tmp/shakedown-literary-prevention-after/Amps and angle encoding.xhtml"
diff -u \
  "/tmp/shakedown-literary-prevention-baseline/Amps and angle encoding.xhtml" \
  "/tmp/shakedown-literary-prevention-after/Amps and angle encoding.xhtml"
```

Expected: no diff. If `_IMPLEMENTED_FIXTURES` in `tests/test_mdtest.py` has grown
by the time this plan runs, compare every fixture named there.

- [x] **Step 9: Commit**

```bash
git add src/*.spl shakedown.spl tests/test_literary_compliance.py src/literary.toml
git commit -m "refactor: reference literary surfaces by key"
```

---

## Task 6: Add Prompt/Plan Gate To Roadmap Workflow

**Files:**
- Modify: `docs/superpowers/plans/plan-roadmap.md`
- Modify: `tests/test_prompt_literary_protocol.py`

- [x] **Step 1: Add roadmap source note**

In `docs/superpowers/plans/plan-roadmap.md`, add this source note:

```markdown
- SPL-changing plans must use `docs/superpowers/notes/spl-literary-protocol.md`
  or explicitly reference its required docs and literary compliance tests.
```

- [x] **Step 2: Add test that roadmap names the protocol**

Append to `tests/test_prompt_literary_protocol.py`:

```python
def test_roadmap_names_spl_literary_protocol() -> None:
    assert "docs/superpowers/notes/spl-literary-protocol.md" in _read(ROADMAP)
```

- [x] **Step 3: Run prompt protocol tests**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_prompt_literary_protocol.py -q
```

Expected: all pass.

- [x] **Step 4: Commit**

```bash
git add docs/superpowers/plans/plan-roadmap.md tests/test_prompt_literary_protocol.py
git commit -m "docs: require literary protocol in SPL plans"
```

---

## Task 7: Final Verification

**Files:**
- No new files

- [ ] **Step 1: Run full verification**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
bash -n shakedown
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .
```

Expected: all pass, except any existing repository-wide skips already present in
the baseline.

- [ ] **Step 1a: Run the literary surface audit subset**

Run this audit whenever assembler, codegen, TOML surface data, SPL fragments, or
prompt protocol files changed:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest \
  tests/test_prompt_literary_protocol.py \
  tests/test_literary_toml_schema.py \
  tests/test_literary_compliance.py \
  tests/test_assemble.py \
  tests/test_codegen_html.py \
  tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: all selected tests pass. If `_IMPLEMENTED_FIXTURES` in
`tests/test_mdtest.py` has grown, replace the `-k 'Amps and angle'` filter with
the full implemented-fixture subset.

- [ ] **Step 2: Confirm generated output has no unresolved placeholders**

Run:

```bash
rg -n '@LIT\\.' shakedown.spl && exit 1 || true
```

Expected: no output and exit status 0.

- [ ] **Step 3: Confirm source still uses placeholders**

Run:

```bash
rg -n '@LIT\\.' src/*.spl
```

Expected: matches for title, scene-title, Recall, or recurring value surfaces.

- [ ] **Step 4: Commit any verification-only plan checkbox changes**

If executing through the run-loop and this plan file is being checked off, commit
the checked boxes:

```bash
git add docs/superpowers/plans/2026-04-30-literary-prevention-rails.md
git commit -m "chore: complete literary prevention rails plan"
```
