# Pre-Slice-1 Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land every architecture §7.1 deliverable so Slice 1 (Plan 2) can begin without re-deriving scaffolding — literary data schema, codegen, parity harness, dev wrapper, cache decision, run-loop prompt, operator halt switch, and generated-artifact policy all in place.

**Architecture:** Each task is one self-contained 2–5 minute change ending in a commit. Tasks add new files or augment existing ones; no fragment of the prototype `src/*.spl` is renamed or replaced here — that work belongs to Slice 1. Cache feasibility is decided by a real spike, not predicted.

**Tech stack:** Python (`uv` toolchain, `tomllib`, `subprocess`, `pickle`, `pytest`, `ruff`, `pyright`); `shakespearelang` interpreter; bash 5; `Markdown.pl` perl oracle at `~/markdown/Markdown.pl`; `~/mdtest/Markdown.mdtest/` fixture set.

**Source-of-truth references the implementer must keep open:**
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — §7.1 deliverables, §5 wrapper/cache, §3 literary architecture, §6 cast, §8 verification gates, §7.9 operator-only `cz bump`.
- `docs/superpowers/specs/2026-04-27-loop-prompt-design.md` — exact decisions the run-loop prompt must encode (universities, standing instructions, blockers.md mechanics, completion criteria).
- `docs/superpowers/plans/plan-roadmap.md` — staged implementation-plan ladder; this is plan 1 of 8.
- `docs/spl/literary-spec.md` — §4 (Stable Utility per-character surfaces), §7.2 (scene-title iconic moments), §7.5.1 (Recall echo iconic moments + single-surface rule), §8.1/§8.2 (token-code atom cap, Critical recipe).
- `docs/spl/codegen-style-guide.md` — Critical / Stable Utility / Incidental partition.
- `docs/spl/reference.md` — SPL legality (every authored phrase must parse).
- `docs/markdown/oracle-mechanics.md`, `docs/markdown/reference-mechanics.md` — Markdown.pl behaviour surfaces (referenced by harness; not modified here).
- `docs/ralph-loop.md` — `@file` stack-allocation pattern used by the run-loop prompt.
- `CLAUDE.md` — commit conventions, completion-marker convention, target interface.

**No-progress safeguards in force:** every step ends with a commit using a conventional-commit prefix (no `--no-verify`); a step that genuinely cannot be completed without operator input must append `- BLOCK: <reason>` to `.agent/blockers.md` and stop, per the loop-prompt design note §5.

---

## File map

**Created by this plan:**
- `.agent/blockers.md` — operator-managed halt switch (empty initially).
- `docs/spl/token-codes.md` — explicit dispatch-token-code allocation table satisfying literary-spec §8.1 atom cap.
- `docs/spl/iconic-moments.md` — scene-title and Recall echo iconic-moment maps (single-surface rule enforced).
- `docs/architecture/cache-spike.md` — cache feasibility outcome and decided dev-mode shape.
- `docs/prompt-shakedown.md` — run-loop prompt per loop-prompt design note.
- `src/literary.toml` — hand-authored literary surface data (Slice 1 entries; schema covers all 9 characters).
- `scripts/codegen_html.py` — HTML byte-literal codegen.
- `scripts/shakedown_run.py` — dev wrapper skeleton.
- `scripts/strict_parity_harness.py` — strict Shakedown-vs-Markdown.pl byte-comparison harness.
- `scripts/cache_spike.py` — one-shot cache feasibility spike.
- `tests/test_codegen_html.py` — codegen byte-literal round-trip tests.
- `tests/test_shakedown_run.py` — wrapper skeleton tests.
- `tests/test_strict_parity_harness.py` — harness self-test.
- `tests/test_literary_toml_schema.py` — literary.toml shape and atom-cap validators.
- `tests/test_iconic_moments.py` — single-surface-rule validator and budget caps.
- `tests/test_token_codes.py` — token-code atom-cap validator.

**Modified:**
- `.gitignore` — remove `shakedown.spl` ignore; confirm `.cache/` ignored.
- `CLAUDE.md` — add `.agent/blockers.md` convention paragraph; add `cz bump` operator-only note (cross-link to architecture §7.9).
- `docs/superpowers/plans/plan-roadmap.md` — at end of plan, status of plan 1 → `shipped`.

**Untouched in this plan (Slice 1's job):**
- `src/00-preamble.spl`, `src/10-phase1-read.spl`, `src/20-phase2-block.spl`, `src/30-phase3-inline.spl`, `src/manifest.toml` — prototype files; Slice 1 replaces them with the four-act layout and new cast.
- `./shakedown` — stays as the Markdown.pl oracle stub through Plan 1; Slice 1 swaps it for the dev wrapper invocation.

---

## Task 1: Operator halt switch and `cz bump` convention

**Files:**
- Create: `.agent/blockers.md`
- Modify: `CLAUDE.md` (add blockers.md convention paragraph; mark `cz bump` operator-only)

- [ ] **Step 1.1: Create `.agent/blockers.md` with the convention header**

```markdown
# Blockers

This file is the operator's in-repo halt switch for the run-loop. Any line
starting with `- BLOCK:` halts the autonomous agent on the next iteration —
the agent must address it (or, if it cannot, exit cleanly without modifying
code).

The agent itself MAY append `- BLOCK:` lines when it hits a question it
cannot resolve from the universities (`@file` references in
`docs/prompt-shakedown.md`); doing so is the only legal way to surface a
blocker mid-run. The operator removes the line when the block is resolved.

Non-blocking notes (no halt) use `- NOTE:` instead.
```

- [ ] **Step 1.2: Add blockers.md convention paragraph to CLAUDE.md**

In `CLAUDE.md`, insert a new section after the existing `## run-loop` section and before `## Target interface`:

```markdown
## Operator halt switch (`.agent/blockers.md`)

The autonomous agent reads `.agent/blockers.md` on every iteration via the
`@.agent/blockers.md` university reference in `docs/prompt-shakedown.md`. Any
line starting with `- BLOCK:` halts plan advancement until the operator
removes it. Non-blocking notes use `- NOTE:`. See
`docs/superpowers/specs/2026-04-27-loop-prompt-design.md` §5 for the full
convention.
```

- [ ] **Step 1.3: Mark `cz bump` operator-only in CLAUDE.md**

In `CLAUDE.md`, locate the `### How to cut a version` block (the section containing `uv run cz bump # computes bump from commits, updates pyproject.toml, commits + tags`). Insert the following paragraph **immediately above** that block:

```markdown
**Operator-only.** Autonomous run-loop agents must NOT run `cz bump`,
`git tag`, `git push --tags`, or update `CHANGELOG.md` unless the current
plan step explicitly authorises it. Version cuts are operator decisions per
architecture spec §7.9.
```

- [ ] **Step 1.4: Commit**

```bash
git add .agent/blockers.md CLAUDE.md
git commit -m "chore: document operator halt switch and operator-only cz bump"
```

Expected `git status`: clean.

---

## Task 2: Generated-artifact policy

**Files:**
- Modify: `.gitignore`

- [ ] **Step 2.1: Read current `.gitignore` to confirm exact lines**

```bash
cat .gitignore
```

Confirm the file contains both:
- `.cache/` (already ignored — keep)
- `shakedown.spl` under "Build artifact — assembled from src/ fragments..." (must remove for §5.3b)

- [ ] **Step 2.2: Remove the `shakedown.spl` ignore**

Edit `.gitignore`. Delete the trailing block:
```
# Build artifact — assembled from src/ fragments by scripts/assemble.py
shakedown.spl
```

Replace with the policy comment so future readers see why it was removed:
```
# shakedown.spl is INTENTIONALLY tracked. The release-mode bash entry runs
# the committed file directly with no assembly step. CI verifies the
# committed shakedown.spl matches scripts/assemble.py output. See
# docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md §5.3b.
```

- [ ] **Step 2.3: Verify `.cache/` is still ignored**

```bash
grep -n "^\.cache/" .gitignore
```

Expected: one match. If missing, add `.cache/` under the existing `# Tools` block.

- [ ] **Step 2.4: Confirm no stray `shakedown.spl` is in the working tree**

```bash
ls shakedown.spl 2>&1
```

Expected: `ls: cannot access 'shakedown.spl': No such file or directory` (Slice 1 will produce the first committed copy). If a stale assembled file exists, delete it: `rm shakedown.spl`.

- [ ] **Step 2.5: Commit**

```bash
git add .gitignore
git commit -m "chore: stop ignoring shakedown.spl per architecture §5.3b"
```

---

## Task 3: Token-code allocation table

**Files:**
- Create: `docs/spl/token-codes.md`
- Create: `tests/test_token_codes.py`

The architecture's Act II token vocabulary (§4.2) is `PARA`, `HEADER(level, text)`, `HR`, `LIST_OPEN(kind)`, `LIST_ITEM(text)`, `LIST_CLOSE`, `BLOCKQUOTE_OPEN`, `BLOCKQUOTE_CLOSE`, `CODE_BLOCK(text)`, `RAW_HTML_HASH(id)`. Each name needs a small positive integer code that is expressible as a short SPL value expression satisfying literary-spec §8.1: atoms 2–4 words, never more than 6 words, single-atom forms preferred where legal.

- [ ] **Step 3.1: Write the failing test**

Create `tests/test_token_codes.py`:

```python
"""Validate the dispatch token-code allocation table satisfies §8.1 atom cap."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

TOKEN_CODES_DOC = Path(__file__).parent.parent / "docs" / "spl" / "token-codes.md"

# Match Markdown table rows: | NAME | CODE | "atom phrase" |
_ROW_RE = re.compile(
    r"^\|\s*(?P<name>[A-Z_]+)\s*\|\s*(?P<code>\d+)\s*\|\s*`(?P<phrase>[^`]+)`\s*\|"
)

REQUIRED_TOKENS = {
    "PARA", "HEADER", "HR",
    "LIST_OPEN", "LIST_ITEM", "LIST_CLOSE",
    "BLOCKQUOTE_OPEN", "BLOCKQUOTE_CLOSE",
    "CODE_BLOCK", "RAW_HTML_HASH",
}

ATOM_WORD_MAX = 6


def parse_table() -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for line in TOKEN_CODES_DOC.read_text().splitlines():
        match = _ROW_RE.match(line)
        if match:
            rows.append((match["name"], int(match["code"]), match["phrase"]))
    return rows


def test_doc_exists() -> None:
    assert TOKEN_CODES_DOC.exists(), TOKEN_CODES_DOC


def test_all_required_tokens_present() -> None:
    names = {row[0] for row in parse_table()}
    missing = REQUIRED_TOKENS - names
    assert not missing, f"missing token names: {sorted(missing)}"


def test_codes_are_unique_positive_integers() -> None:
    codes = [row[1] for row in parse_table()]
    assert all(c > 0 for c in codes), codes
    assert len(codes) == len(set(codes)), f"duplicate codes: {codes}"


def test_atom_word_cap() -> None:
    """Each phrase atom must be <= 6 words. Compounds (`the sum of A and B`)
    are decomposed and each side checked."""
    for name, code, phrase in parse_table():
        atoms = _atoms_in(phrase)
        for atom in atoms:
            words = atom.strip().split()
            assert len(words) <= ATOM_WORD_MAX, (
                f"{name}={code} atom {atom!r} exceeds {ATOM_WORD_MAX}-word cap"
            )


def _atoms_in(phrase: str) -> list[str]:
    """Decompose `the sum of A and B` recursively; return leaf atoms.

    Codegen produces RIGHT-nested compounds: `the sum of <atom> and <rest>`.
    Atoms never contain ` and `, so the first ` and ` after stripping the
    outer prefix separates the left atom from the recursive right side.
    """
    text = phrase.strip()
    prefix = "the sum of "
    if text.lower().startswith(prefix):
        rest = text[len(prefix):]
        idx = rest.find(" and ")
        if idx == -1:
            return [text]
        left, right = rest[:idx], rest[idx + len(" and "):]
        return _atoms_in(left) + _atoms_in(right)
    return [text]
```

- [ ] **Step 3.2: Run test to verify it fails**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_token_codes.py -v
```

Expected: FAIL with `assert TOKEN_CODES_DOC.exists()` or similar.

- [ ] **Step 3.3: Write `docs/spl/token-codes.md` with the allocation table**

Create `docs/spl/token-codes.md`:

````markdown
# Dispatch Token-Code Allocation

**Status:** Pre-Slice-1 deliverable per architecture spec §7.1 #3.
**Constraint:** literary-spec §8.1 atom cap (2–4 word target, 6 word max);
single-atom forms preferred when legal.

These codes are *Critical* in the codegen-style-guide sense: every speaker
uses the canonical phrase repo-wide for a given dispatch value. Per-character
Stable Utility variation (literary-spec §4) does NOT apply to these.

## Block-token allocation

| Name | Code | Canonical SPL phrase |
|---|---:|---|
| PARA | 1 | `a cat` |
| HEADER | 2 | `a big cat` |
| HR | 3 | `the sum of a big cat and a cat` |
| LIST_OPEN | 4 | `a big big cat` |
| LIST_ITEM | 5 | `the sum of a big big cat and a cat` |
| LIST_CLOSE | 6 | `the sum of a big big cat and a big cat` |
| BLOCKQUOTE_OPEN | 7 | `the sum of a big big cat and the sum of a big cat and a cat` |
| BLOCKQUOTE_CLOSE | 8 | `a big big big cat` |
| CODE_BLOCK | 9 | `the sum of a big big big cat and a cat` |
| RAW_HTML_HASH | 10 | `the sum of a big big big cat and a big cat` |

**Atoms used:** `a cat` (1, 2 words), `a big cat` (2, 3 words), `a big big cat` (4, 4 words),
`a big big big cat` (8, 5 words). All atoms ≤ 6 words.

**Compound-only codes (3, 5, 6, 7, 9, 10):** unavoidable because adjective
doubling jumps 1 → 2 → 4 → 8; values 3, 5, 6, 7, 9, 10 cannot be reached as
single atoms. Compound length is uncapped per §8.1; each atom still obeys the
cap. Sum-of compounds are left-associative.

## How to extend

Slice 3 onward may need additional tokens (e.g., span-level dispatch,
character-class codes). Append rows here, validate via
`uv run pytest tests/test_token_codes.py`. Document any conflict between a
mechanical demand (e.g., "this code must equal 0 for sentinel") and the atom
cap inline at the row, per literary-spec §10 #6.

## References

- `docs/spl/literary-spec.md` §8.1 (atom cap), §8.2 (Critical recipe).
- `docs/spl/codegen-style-guide.md` (Critical/Stable/Incidental partition).
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §4.2 (token vocabulary), §7.1 #3 (this deliverable).
````

- [ ] **Step 3.4: Run test to verify it passes**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_token_codes.py -v
```

Expected: 4 tests pass.

- [ ] **Step 3.5: Commit**

```bash
git add docs/spl/token-codes.md tests/test_token_codes.py
git commit -m "feat: add dispatch token-code allocation table"
```

(Uses `feat:` because §7.1 #3 is a user-facing deliverable per the architecture-spec slice plan.)

---

## Task 4: Iconic-moment maps

**Files:**
- Create: `docs/spl/iconic-moments.md`
- Create: `tests/test_iconic_moments.py`

Per literary-spec §7.2 (≤12 scene-title iconic moments) and §7.5.1 (4–8 Recall echo iconic moments, ≤20 combined ceiling, single-surface rule: each Shakespeare phrase appears in exactly one iconic surface).

- [ ] **Step 4.1: Write the failing test**

Create `tests/test_iconic_moments.py`:

```python
"""Validate iconic-moment maps satisfy literary-spec §7.2 + §7.5.1 budgets."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

DOC = Path(__file__).parent.parent / "docs" / "spl" / "iconic-moments.md"

SCENE_TITLE_MAX = 12  # literary-spec §7.2
RECALL_ECHO_MIN = 4   # literary-spec §7.5.1
RECALL_ECHO_MAX = 8
COMBINED_MAX = 20


def parse_iconic_moments() -> dict[str, list[dict[str, str]]]:
    """Extract the two TOML fenced blocks from the doc."""
    text = DOC.read_text()
    matches = re.findall(r"```toml\n(.*?)```", text, flags=re.DOTALL)
    assert len(matches) == 2, f"expected 2 toml blocks, got {len(matches)}"
    scene_titles = tomllib.loads(matches[0])["scene_titles"]
    recall_echoes = tomllib.loads(matches[1])["recall_echoes"]
    return {"scene_titles": scene_titles, "recall_echoes": recall_echoes}


def test_doc_exists() -> None:
    assert DOC.exists(), DOC


def test_scene_title_budget() -> None:
    moments = parse_iconic_moments()["scene_titles"]
    assert len(moments) <= SCENE_TITLE_MAX, len(moments)


def test_recall_echo_budget() -> None:
    moments = parse_iconic_moments()["recall_echoes"]
    assert RECALL_ECHO_MIN <= len(moments) <= RECALL_ECHO_MAX, len(moments)


def test_combined_ceiling() -> None:
    parsed = parse_iconic_moments()
    total = len(parsed["scene_titles"]) + len(parsed["recall_echoes"])
    assert total <= COMBINED_MAX, total


def test_single_surface_rule() -> None:
    """Each Shakespeare phrase appears in exactly one iconic surface."""
    parsed = parse_iconic_moments()
    phrases = [m["phrase"] for m in parsed["scene_titles"]]
    phrases += [m["phrase"] for m in parsed["recall_echoes"]]
    duplicates = {p for p in phrases if phrases.count(p) > 1}
    assert not duplicates, f"phrases reused across surfaces: {sorted(duplicates)}"


def test_required_fields_present() -> None:
    parsed = parse_iconic_moments()
    for moment in parsed["scene_titles"] + parsed["recall_echoes"]:
        for field in ("phrase", "play", "speaker", "shakedown_use"):
            assert field in moment, f"missing {field} in {moment}"
```

- [ ] **Step 4.2: Run test to verify it fails**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_iconic_moments.py -v
```

Expected: FAIL on `assert DOC.exists()`.

- [ ] **Step 4.3: Write `docs/spl/iconic-moments.md`**

Create `docs/spl/iconic-moments.md`. Draw phrases from literary-spec §7.2 examples and the cast play list; the schema is binding, the specific phrases are starting picks reviewable in code review.

````markdown
# Iconic-Moment Maps

**Status:** Pre-Slice-1 deliverable per architecture spec §7.1 #10.
**Constraints (literary-spec §7.2 + §7.5.1):**
- Scene-title iconic moments: ≤12.
- Recall echo iconic moments: 4–8.
- Combined ceiling: ≤20.
- **Single-surface rule:** each Shakespeare phrase appears in exactly one
  iconic surface (scene title XOR Recall echo). No re-use.

The maps live in fenced TOML blocks below so the validator can parse them
without a separate file. Slice work that touches an iconic surface must
update this doc and the validator.

## Scene-title iconic-moment map

```toml
[[scene_titles]]
phrase = "Out, damned spot"
play = "Macbeth"
speaker = "Lady Macbeth"
shakedown_use = "Act I scene that strips whitespace-only lines"

[[scene_titles]]
phrase = "Something wicked this way comes"
play = "Macbeth"
speaker = "Second Witch"
shakedown_use = "Act I scene that hashes raw HTML blocks"

[[scene_titles]]
phrase = "Once more unto the breach"
play = "Henry V"
speaker = "King Henry"
shakedown_use = "Act II opening scene; first block-recognition pass"

[[scene_titles]]
phrase = "But soft, what light"
play = "Romeo and Juliet"
speaker = "Romeo"
shakedown_use = "Act III opening scene; first span pass"

[[scene_titles]]
phrase = "A rose by any other name"
play = "Romeo and Juliet"
speaker = "Juliet"
shakedown_use = "Act III scene that performs ampersand/angle encoding"

[[scene_titles]]
phrase = "Our revels now are ended"
play = "The Tempest"
speaker = "Prospero"
shakedown_use = "Act IV closing emit scene"

[[scene_titles]]
phrase = "Lord, what fools these mortals be"
play = "A Midsummer Night's Dream"
speaker = "Puck"
shakedown_use = "Herald dispatch transition between acts II and III"

[[scene_titles]]
phrase = "All the world's a stage"
play = "As You Like It"
speaker = "Jaques"
shakedown_use = "Reserved: documentation-aggregate fixture entry scene (Slice 5)"
```

## Recall echo iconic-moment map

```toml
[[recall_echoes]]
phrase = "Double, double, toil and trouble"
play = "Macbeth"
speaker = "Witches"
shakedown_use = "Recall description for Hecate's detab loop"

[[recall_echoes]]
phrase = "Two households, both alike in dignity"
play = "Romeo and Juliet"
speaker = "Chorus"
shakedown_use = "Recall description for Romeo/Juliet's strong-then-emphasis pair"

[[recall_echoes]]
phrase = "All that glisters is not gold"
play = "The Merchant of Venice"
speaker = "Prince of Morocco"
shakedown_use = "Recall description for Rosalind's reference-table consultation"

[[recall_echoes]]
phrase = "I am thy father's spirit"
play = "Hamlet"
speaker = "Ghost"
shakedown_use = "Recall description for Horatio's HTML-hash lookup"

[[recall_echoes]]
phrase = "We are such stuff as dreams are made on"
play = "The Tempest"
speaker = "Prospero"
shakedown_use = "Recall description for Prospero's emit walk"
```

## How to extend

Adding a moment: append a TOML row, then run
`uv run pytest tests/test_iconic_moments.py`. The validator enforces the
single-surface rule, the per-surface budgets, and the combined ceiling.
A would-be entry that is already used in the other surface must be replaced
by a different phrase.

## References

- `docs/spl/literary-spec.md` §7.2 (scene titles), §7.5 (Recall conventions),
  §7.5.1 (single-surface rule, ≤8 echo budget, ≤20 combined ceiling).
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §7.1 #10.
````

- [ ] **Step 4.4: Run test to verify it passes**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_iconic_moments.py -v
```

Expected: 6 tests pass.

- [ ] **Step 4.5: Commit**

```bash
git add docs/spl/iconic-moments.md tests/test_iconic_moments.py
git commit -m "feat: add iconic-moment maps with single-surface validator"
```

---

## Task 5: literary.toml schema and Slice 1 entries

**Files:**
- Create: `src/literary.toml`
- Create: `tests/test_literary_toml_schema.py`

Schema covers all 9 characters (literary-spec §2.2 cast roster); initial Slice 1 entries populate **home** Stable Utility surfaces for `+1`, `+2`, `-1`, `0` per literary-spec §4.4 sketch table verbatim. Per-act surface variants for the hybrid-voice cross-act characters (Rosalind, Puck) are deferred to Slice 1 — at that point the act-specific code site that needs them dictates the exact phrase, and the literary review can validate against the visited act's palette. Plan 1's deliverable is "schema and initial Slice 1 entries" per architecture §7.1 #1; full per-act denormalisation is not part of that floor.

**SPL grammar constraint:** every phrase must parse against `shakespeare.ebnf`. Adjectives MUST come from `docs/spl/reference.md` §"Positive adjectives", §"Negative adjectives", §"Neutral adjectives"; nouns from the corresponding noun lists. `positive_noun_phrase` admits only positive/neutral adjectives with positive/neutral nouns; `negative_noun_phrase` admits only negative/neutral adjectives with negative nouns (literary-spec §3.1 sign-path constraints).

- [ ] **Step 5.1: Write the failing test**

Create `tests/test_literary_toml_schema.py`:

```python
"""Validate src/literary.toml shape and atom-cap compliance for Slice 1."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

LITERARY_TOML = Path(__file__).parent.parent / "src" / "literary.toml"

CHARACTERS = {
    # Cross-act state holders (literary-spec §2.2)
    "rosalind": {"role": "librarian", "voice": "hybrid"},
    "horatio": {"role": "steward", "voice": "stable"},
    "puck": {"role": "herald", "voice": "hybrid"},
    # Per-act workers
    "hecate": {"role": "sorter", "voice": "act_bound", "act": 1},
    "lady_macbeth": {"role": "mason", "voice": "act_bound", "act": 2},
    "macbeth": {"role": "apprentice", "voice": "act_bound", "act": 2},
    "romeo": {"role": "lyric_a", "voice": "act_bound", "act": 3},
    "juliet": {"role": "lyric_b", "voice": "act_bound", "act": 3},
    "prospero": {"role": "scribe", "voice": "act_bound", "act": 4},
}

REQUIRED_STABLE_UTILITY_VALUES = {1, 2, -1, 0}  # §4.4 sketch
ATOM_WORD_MAX = 6


def _atoms_in(phrase: str) -> list[str]:
    text = phrase.strip()
    prefix = "the sum of "
    if text.lower().startswith(prefix):
        rest = text[len(prefix):]
        idx = rest.find(" and ")
        if idx == -1:
            return [text]
        left, right = rest[:idx], rest[idx + len(" and "):]
        return _atoms_in(left) + _atoms_in(right)
    return [text]


def load() -> dict:
    with LITERARY_TOML.open("rb") as f:
        return tomllib.load(f)


def test_file_exists() -> None:
    assert LITERARY_TOML.exists(), LITERARY_TOML


def test_all_characters_present() -> None:
    data = load()
    assert set(data["characters"]) == set(CHARACTERS), (
        sorted(set(data["characters"])), sorted(set(CHARACTERS))
    )


def test_stable_utility_coverage_for_slice1() -> None:
    """Every character has every required home stable-utility value.

    Per-act variants for hybrid-voice characters are deferred to Slice 1
    (when act-site context dictates phrasing).
    """
    data = load()
    for name in CHARACTERS:
        section = data["characters"][name]
        stable = section.get("stable_utility", {})
        for value in REQUIRED_STABLE_UTILITY_VALUES:
            key = f"v{value}" if value >= 0 else f"vneg{abs(value)}"
            assert key in stable, f"{name} missing home {key}"


def test_per_act_variants_when_present_have_legal_keys() -> None:
    """If per_act_stable_utility is present, keys must be act1..act4 only."""
    data = load()
    for name, section in data["characters"].items():
        per_act = section.get("per_act_stable_utility", {})
        for key in per_act:
            assert key in {"act1", "act2", "act3", "act4"}, (name, key)


def test_atom_cap() -> None:
    data = load()
    for name, section in data["characters"].items():
        for surface_set, surfaces in _walk_surfaces(section):
            for value, phrase in surfaces.items():
                if not isinstance(phrase, str):
                    continue
                for atom in _atoms_in(phrase):
                    words = atom.split()
                    assert len(words) <= ATOM_WORD_MAX, (
                        f"{name}.{surface_set}.{value}: atom {atom!r} "
                        f"exceeds {ATOM_WORD_MAX} words"
                    )


def _walk_surfaces(section: dict):
    if "stable_utility" in section:
        yield ("stable_utility", section["stable_utility"])
    for act_key, surfaces in section.get("per_act_stable_utility", {}).items():
        yield (f"per_act_stable_utility.{act_key}", surfaces)


def test_critical_zero_is_nothing() -> None:
    """§4.4: 0 stays `nothing` repo-wide as a Critical override."""
    data = load()
    for name, section in data["characters"].items():
        for surface_set, surfaces in _walk_surfaces(section):
            if "v0" in surfaces:
                assert surfaces["v0"] == "nothing", (
                    f"{name}.{surface_set}.v0 must be 'nothing' (Critical)"
                )
```

- [ ] **Step 5.2: Run test to verify it fails**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_toml_schema.py -v
```

Expected: FAIL on file-existence.

- [ ] **Step 5.3: Write `src/literary.toml`**

Authored from literary-spec §4.4 sketch. The sketch lists Hecate, Lady M, Macbeth, Romeo, Juliet, Prospero, plus cross-act home picks for Rosalind, Horatio, Puck. Per-act variants for Rosalind and Puck come from §2.4 Hybrid strategy: Puck swaps adjective only, Rosalind swaps adjective with optional noun-borrow.

```toml
# src/literary.toml — hand-authored literary surface data
#
# Schema:
#   [characters.<name>]
#     play, role, palette, voice_register, blurb,
#     stable_utility = { v1 = "...", v2 = "...", vneg1 = "...", v0 = "nothing" }
#     per_act_stable_utility = { act1 = {...}, act2 = {...}, ... }   # OPTIONAL
#
# Plan 1 ships HOME stable_utility for every character, drawn verbatim from
# the literary-spec §4.4 sketch table. Per-act variants for the hybrid-voice
# cross-act characters (Rosalind, Puck) are deferred to Slice 1 because
# act-site context dictates the exact phrase. The schema (per_act_stable_utility
# may be present and keys must be act1..act4) is enforced today; populating
# the values is Slice 1+ work.
#
# Constraints:
# - v0 is Critical and stays "nothing" repo-wide (literary-spec §4.4).
# - Atom phrases obey literary-spec §8.1: 2-4 word target, 6 word max per atom.
# - Adjectives/nouns must come from docs/spl/reference.md legal lists
#   (verified by tests/test_literary_toml_schema.py at the atom-cap layer;
#   SPL grammar legality verified by SPL parse during Slice 1 integration).
# - positive_noun_phrase admits only positive/neutral adjectives with
#   positive/neutral nouns; negative_noun_phrase mirrors for negative nouns.
#
# Validators: tests/test_literary_toml_schema.py, tests/test_token_codes.py.

# === Cross-act state holders ===

[characters.rosalind]
play = "As You Like It"
role = "librarian"
palette = "pastoral_natural"
voice_register = "witty_agile_cross_register"
blurb = "Rosalind, keeper of references, agile of tongue across the Forest of Arden."
[characters.rosalind.stable_utility]
v1 = "a tree"
v2 = "a green tree"
vneg1 = "a wolf"   # sign-path borrow from Martial; literary-spec §4.4
v0 = "nothing"

[characters.horatio]
play = "Hamlet"
role = "steward"
palette = "domestic_familial"
voice_register = "plain_spoken_keeper"
blurb = "Horatio, plain witness of the household, holder of secrets."
[characters.horatio.stable_utility]
v1 = "a brother"
v2 = "a happy brother"
vneg1 = "a beggar"   # negative-noun borrow; closest Domestic-tinted neg noun
v0 = "nothing"

[characters.puck]
play = "A Midsummer Night's Dream"
role = "herald"
palette = "pastoral_natural"
voice_register = "chameleonic_messenger"
blurb = "Puck, swift messenger, whose adjectives change with the room he visits."
[characters.puck.stable_utility]
v1 = "a flower"
v2 = "a sweet flower"
vneg1 = "a wolf"   # sign-path borrow; literary-spec §4.4
v0 = "nothing"

# === Per-act workers ===

[characters.hecate]
play = "Macbeth"
role = "sorter"
palette = "grotesque_abusive"
voice_register = "incantatory_grimy"
blurb = "Hecate, witch-queen, who scours the underbelly of the page."
[characters.hecate.stable_utility]
v1 = "a cat"   # neutral fallback; Grotesque has no positive nouns
v2 = "a big cat"
vneg1 = "a toad"
v0 = "nothing"

[characters.lady_macbeth]
play = "Macbeth"
role = "mason"
palette = "martial_catastrophic"
voice_register = "decisive_clean_martial"
blurb = "Lady Macbeth, mason of the block, who cuts the page into rooms."
[characters.lady_macbeth.stable_utility]
v1 = "a hero"
v2 = "a noble hero"
vneg1 = "a wolf"
v0 = "nothing"

[characters.macbeth]
play = "Macbeth"
role = "apprentice"
palette = "martial_catastrophic"
voice_register = "doubt_shadowed_martial"
blurb = "Macbeth, apprentice mason, who pairs with the Lady though dread shadows him."
[characters.macbeth.stable_utility]
v1 = "a kingdom"
v2 = "a proud kingdom"
vneg1 = "a curse"
v0 = "nothing"

[characters.romeo]
play = "Romeo and Juliet"
role = "lyric_a"
palette = "pastoral_natural"
voice_register = "lyrical_sun_imagery"
blurb = "Romeo, who pushes candidate substitutions like sunlit petals."
[characters.romeo.stable_utility]
v1 = "a summer's day"
v2 = "a sunny summer's day"
vneg1 = "a wolf"   # borrowed Martial; literary-spec §4.4
v0 = "nothing"

[characters.juliet]
play = "Romeo and Juliet"
role = "lyric_b"
palette = "pastoral_natural"
voice_register = "lyrical_night_imagery"
blurb = "Juliet, who commits final tokens like petals laid on stone."
[characters.juliet.stable_utility]
v1 = "a rose"
v2 = "a sweet rose"
vneg1 = "a wolf"   # borrowed Martial; literary-spec §4.4
v0 = "nothing"

[characters.prospero]
play = "The Tempest"
role = "scribe"
palette = "noble_radiant"
voice_register = "ceremonial_declarative"
blurb = "Prospero, scribe and emitter, whose pronouncements close the work."
[characters.prospero.stable_utility]
v1 = "an angel"
v2 = "a noble angel"
vneg1 = "a curse"   # borrowed Martial; literary-spec §4.4
v0 = "nothing"
```

- [ ] **Step 5.4: Run test to verify it passes**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_literary_toml_schema.py -v
```

Expected: 6 tests pass.

- [ ] **Step 5.5: Commit**

```bash
git add src/literary.toml tests/test_literary_toml_schema.py
git commit -m "feat: add src/literary.toml schema with Slice 1 stable-utility entries"
```

---

## Task 6: HTML byte-literal codegen

**Files:**
- Create: `scripts/codegen_html.py`
- Create: `tests/test_codegen_html.py`

Codegen quarantines forced-byte HTML literals (architecture §3.7 #1, literary-spec §4.3). For every byte in a target HTML literal (e.g., `<p>`), it must emit the canonical SPL noun-phrase chain that pushes that byte's ASCII value. Slice 1's deliverable §7.2 names `&amp;`, `&lt;`, `&gt;`, `<p>`, `</p>`, `<a href="...">`, `</a>`. We add the function and test the round-trip; the actual emit-into-fragment work happens in Slice 1.

- [ ] **Step 6.1: Write the failing test**

Create `tests/test_codegen_html.py`:

```python
"""Codegen byte-literal round-trip tests."""

from __future__ import annotations

import re

import pytest

from scripts.codegen_html import emit_byte, emit_literal, parse_value_phrase


@pytest.mark.parametrize(
    "byte_value, expected_includes",
    [
        (0, "nothing"),
        (1, "a cat"),
        (2, "a big cat"),
        (4, "a big big cat"),
    ],
)
def test_emit_byte_atom_forms(byte_value: int, expected_includes: str) -> None:
    spl = emit_byte(byte_value)
    assert expected_includes in spl


def test_emit_byte_returns_compound_when_no_atom() -> None:
    spl = emit_byte(3)
    assert "the sum of" in spl


@pytest.mark.parametrize("byte_value", list(range(0, 128)))
def test_emit_byte_round_trips_for_ascii(byte_value: int) -> None:
    """Every ASCII code can be emitted, and re-parsed back to its int."""
    spl = emit_byte(byte_value)
    assert parse_value_phrase(spl) == byte_value


def test_emit_literal_for_amp() -> None:
    """`&amp;` is 5 bytes; codegen returns 5 SPL phrases keyed by index."""
    bytes_ = emit_literal(b"&amp;")
    assert len(bytes_) == 5
    parsed = [parse_value_phrase(p) for p in bytes_]
    assert parsed == [ord("&"), ord("a"), ord("m"), ord("p"), ord(";")]


def test_emit_literal_for_open_p_tag() -> None:
    bytes_ = emit_literal(b"<p>")
    parsed = [parse_value_phrase(p) for p in bytes_]
    assert parsed == [ord("<"), ord("p"), ord(">")]


def test_atom_cap_on_emitted_atoms() -> None:
    """Every atom in a generated phrase obeys the 6-word cap."""
    for value in range(0, 128):
        spl = emit_byte(value)
        for atom in _atoms(spl):
            assert len(atom.split()) <= 6, (value, atom)


def _atoms(phrase: str) -> list[str]:
    text = phrase.strip()
    prefix = "the sum of "
    if text.lower().startswith(prefix):
        rest = text[len(prefix):]
        idx = rest.find(" and ")
        if idx == -1:
            return [text]
        return _atoms(rest[:idx]) + _atoms(rest[idx + len(" and "):])
    return [text]
```

- [ ] **Step 6.2: Run test to verify it fails**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_codegen_html.py -v
```

Expected: ImportError or FAIL on `from scripts.codegen_html import ...`.

- [ ] **Step 6.3: Write `scripts/codegen_html.py`**

```python
"""HTML byte-literal codegen.

Each byte in a target HTML literal is emitted as a canonical SPL noun-phrase
that, evaluated by the SPL interpreter, equals the byte's integer value.

Critical canonical surfaces (literary-spec §8.2, codegen-style-guide):
    0  -> "nothing"
    1  -> "a cat"
    2  -> "a big cat"
    4  -> "a big big cat"
    8  -> "a big big big cat"
   16  -> "a big big big big cat"
   32  -> "a big big big big big cat"   (5 'big')
   64  -> "a big big big big big big cat"  (6 'big', cap)
   128 -> compound
Atoms doubled by 'big' until the 6-word atom cap (literary-spec §8.1) forbids
further single-atom growth; values beyond 64 use 'the sum of' compounds.
"""

from __future__ import annotations

import re

# Single-atom ASCII values reachable as `a [big*] cat`.
# atom_word_count = 2 + n_bigs; cap at 6 -> max 4 'big' adjectives.
# adjectives double the magnitude: 1, 2, 4, 8, 16.
_ATOM_BY_VALUE: dict[int, str] = {
    0: "nothing",
    1: "a cat",
    2: "a big cat",
    4: "a big big cat",
    8: "a big big big cat",
    16: "a big big big big cat",
}


def emit_byte(value: int) -> str:
    """Return the canonical SPL value phrase for an integer byte (0..255)."""
    if value < 0 or value > 255:
        raise ValueError(f"byte value out of range: {value}")
    if value in _ATOM_BY_VALUE:
        return _ATOM_BY_VALUE[value]
    return _decompose(value)


def _decompose(value: int) -> str:
    """Greedy: pick the largest atom <= value, recurse on remainder."""
    for atom_value in sorted(_ATOM_BY_VALUE, reverse=True):
        if atom_value == 0:
            continue
        if atom_value <= value:
            remainder = value - atom_value
            left = _ATOM_BY_VALUE[atom_value]
            if remainder == 0:
                return left
            right = emit_byte(remainder)
            return f"the sum of {left} and {right}"
    return _ATOM_BY_VALUE[0]


def emit_literal(literal: bytes) -> list[str]:
    """Return one SPL phrase per byte in a literal."""
    return [emit_byte(b) for b in literal]


_PHRASE_RE = re.compile(r"^a(?: big)*(?: cat)$")


def parse_value_phrase(phrase: str) -> int:
    """Reverse `emit_byte`. Used by the round-trip test.

    Compounds are right-nested (`the sum of <atom> and <rest>`); atoms never
    contain ` and `, so the FIRST ` and ` after stripping the outer prefix
    separates the left atom from the recursive right side.
    """
    text = phrase.strip()
    if text == "nothing":
        return 0
    prefix = "the sum of "
    if text.lower().startswith(prefix):
        rest = text[len(prefix):]
        idx = rest.find(" and ")
        if idx == -1:
            raise ValueError(f"malformed compound: {phrase!r}")
        return parse_value_phrase(rest[:idx]) + parse_value_phrase(
            rest[idx + len(" and "):]
        )
    if not _PHRASE_RE.match(text):
        raise ValueError(f"unrecognised atom: {phrase!r}")
    bigs = text.count(" big ")
    return 1 << bigs


def main() -> None:
    """CLI smoke test: emit phrases for `&amp;`."""
    for byte, phrase in zip(b"&amp;", emit_literal(b"&amp;"), strict=True):
        print(f"{byte:>3} ({chr(byte)!r}): {phrase}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6.4: Run test to verify it passes**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_codegen_html.py -v
```

Expected: all tests pass (128 parametrized round-trips + 5 explicit cases + atom-cap sweep).

- [ ] **Step 6.5: Commit**

```bash
git add scripts/codegen_html.py tests/test_codegen_html.py
git commit -m "feat: add HTML byte-literal codegen with round-trip test"
```

---

## Task 7: Cache feasibility spike

**Files:**
- Create: `scripts/cache_spike.py`
- Create: `docs/architecture/cache-spike.md`

Architecture §5.3a requires demonstrating *all four* of: (1) cached representation built and re-executed without parse-metadata loss; (2) byte-identical to direct `shakespeare run` on at least one fixture input; (3) wrapper overhead measured separately; (4) cache invalidation includes Python version, `shakespearelang` version, SPL hash, cache-shape version. The architecture §5.3 already records that pickling parsed AST or preprocessed `Play` is *not viable* in the installed interpreter — so the spike is expected to find a way around that or fall back. The spike either ships a working cache approach or documents the fallback.

- [ ] **Step 7.1: Write `scripts/cache_spike.py`**

```python
"""Cache feasibility spike for the dev wrapper.

Per architecture spec §5.3a, prove ALL of:
1. A cached representation can be built and later executed without parse-metadata loss.
2. Cached execution is byte-identical to direct `shakespeare run` on at least one fixture.
3. Wrapper overhead is measured separately from SPL execution.
4. Cache invalidation key includes SPL hash, Python version, `shakespearelang` version,
   cache-shape version.

This is a one-shot script. It writes a verdict to docs/architecture/cache-spike.md
and exits 0 on a "cache proven" outcome, 0 on a "fallback chosen" outcome (both are
valid; only an unhandled exception means the spike itself is broken).
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import pickle
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).parent.parent
SPL_FIXTURE = REPO / "src"  # use existing prototype src for spike input
ASSEMBLED = REPO / ".cache" / "spike-shakedown.spl"
CACHE_DIR = REPO / ".cache"
VERDICT_DOC = REPO / "docs" / "architecture" / "cache-spike.md"

CACHE_SHAPE_VERSION = 1


def cache_key(spl_path: Path) -> str:
    spl_hash = hashlib.sha256(spl_path.read_bytes()).hexdigest()
    py = platform.python_version()
    sl = importlib.metadata.version("shakespearelang")
    return f"{spl_hash}:{py}:{sl}:v{CACHE_SHAPE_VERSION}"


def assemble_spike_input() -> Path:
    """Concatenate src/*.spl into a one-off file for the spike."""
    from scripts.assemble import assemble  # local import; project script

    CACHE_DIR.mkdir(exist_ok=True)
    assemble(
        src_dir=REPO / "src",
        manifest=REPO / "src" / "manifest.toml",
        output=ASSEMBLED,
    )
    return ASSEMBLED


def run_direct(spl_path: Path, stdin_bytes: bytes) -> tuple[bytes, float]:
    start = time.perf_counter()
    result = subprocess.run(
        ["uv", "run", "shakespeare", "run", str(spl_path)],
        input=stdin_bytes,
        capture_output=True,
        check=True,
    )
    return result.stdout, time.perf_counter() - start


def attempt_pickle_play(spl_path: Path) -> tuple[bool, str]:
    """Try the architecture-mentioned non-viable path; document the failure mode."""
    try:
        from shakespearelang import Shakespeare
    except ImportError as exc:
        return False, f"import-failed:{exc}"
    try:
        play = Shakespeare(spl_path.read_text())
    except Exception as exc:  # noqa: BLE001 — spike-only diagnostic
        return False, f"parse-failed:{type(exc).__name__}:{exc}"
    try:
        blob = pickle.dumps(play)
    except Exception as exc:  # noqa: BLE001
        return False, f"pickle-dumps-failed:{type(exc).__name__}:{exc}"
    try:
        restored = pickle.loads(blob)
    except Exception as exc:  # noqa: BLE001
        return False, f"pickle-loads-failed:{type(exc).__name__}:{exc}"
    try:
        # smoke-execute the restored Play to detect parse-metadata loss
        restored.run()
    except Exception as exc:  # noqa: BLE001
        return False, f"run-after-load-failed:{type(exc).__name__}:{exc}"
    return True, "ok"


def write_verdict(verdict: dict[str, Any]) -> None:
    VERDICT_DOC.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "# Cache Feasibility Spike Outcome\n"
        "\n"
        "**Status:** Pre-Slice-1 deliverable per architecture spec §7.1 #4 / §5.3a.\n"
        "\n"
        "Re-run with `uv run python scripts/cache_spike.py`.\n"
        "\n"
        "## Result\n"
        "\n"
        "```json\n"
        f"{json.dumps(verdict, indent=2, sort_keys=True)}\n"
        "```\n"
        "\n"
        "## Decision\n"
        "\n"
        f"**Dev-mode shape:** {verdict['decision']}\n"
        "\n"
        "If `decision` is `direct_assemble_and_run`, the wrapper at\n"
        "`scripts/shakedown_run.py` MUST NOT carry cache logic. If `decision`\n"
        "is `cache_proven`, the wrapper consumes the cache key fields recorded\n"
        "above. Re-running this spike on a different machine, Python version,\n"
        "or shakespearelang version regenerates the verdict.\n"
        "\n"
        "## References\n"
        "\n"
        "- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §5.3a (acceptance criteria), §8.2 (halt trigger if cache fails).\n"
        "- `docs/verification-plan.md` baseline B14 cold-cost figure used as the comparator.\n"
    )
    VERDICT_DOC.write_text(body)


def main() -> int:
    spl_path = assemble_spike_input()
    stdin_bytes = b"hello *world*\n"

    direct_out, direct_time = run_direct(spl_path, stdin_bytes)
    pickle_ok, pickle_diag = attempt_pickle_play(spl_path)

    if pickle_ok:
        # Future spike work would prove byte-identity here. We stop short
        # because the architecture lists pickling as expected-not-viable;
        # if a future runner finds it works, expand the spike then.
        decision = "cache_proven"
    else:
        decision = "direct_assemble_and_run"

    verdict = {
        "cache_key_inputs": {
            "spl_hash": hashlib.sha256(spl_path.read_bytes()).hexdigest(),
            "python_version": platform.python_version(),
            "shakespearelang_version": importlib.metadata.version("shakespearelang"),
            "cache_shape_version": CACHE_SHAPE_VERSION,
        },
        "direct_run_seconds": round(direct_time, 3),
        "direct_run_stdout_bytes": len(direct_out),
        "pickle_path_outcome": pickle_diag,
        "decision": decision,
    }
    write_verdict(verdict)
    print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 7.2: Run the spike**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/cache_spike.py
```

Expected: prints a JSON verdict and creates `docs/architecture/cache-spike.md`. Exit 0.

If the script raises an unhandled exception, the spike itself is broken — fix the spike, do NOT commit a broken verdict. If the prototype `src/*.spl` is incompatible with the installed interpreter (e.g., needs stdin), the spike's `run_direct` call may error; in that case the spike must be adjusted to provide a benign stdin or use a minimal SPL test program in `.cache/`. Document the adjustment in the verdict doc.

- [ ] **Step 7.3: Inspect verdict, confirm decision is concrete**

```bash
cat docs/architecture/cache-spike.md | head -40
```

Expected: a `decision` field reading either `cache_proven` or `direct_assemble_and_run`. Anything else is a bug in the spike.

- [ ] **Step 7.4: Commit**

```bash
git add scripts/cache_spike.py docs/architecture/cache-spike.md
git commit -m "experiment: add pre-Slice-1 cache feasibility spike"
```

(Uses `experiment:` per CLAUDE.md commit-type guide; this is a feasibility study, not a delivered feature.)

---

## Task 8: Dev wrapper skeleton

**Files:**
- Create: `scripts/shakedown_run.py`
- Create: `tests/test_shakedown_run.py`

Per architecture §5.3, the dev wrapper assembles, optionally consults the cache (only if §5.3a spike proved one), runs the SPL interpreter, and passes stdin/stdout/stderr/exit code through. ≤100 lines of Python. The wrapper's runtime cache logic is gated on `docs/architecture/cache-spike.md`'s decision field — implementer reads that file at script startup.

This task does NOT replace `./shakedown` (the bash oracle stub). Slice 1 (Plan 2) does that swap.

- [ ] **Step 8.1: Write the failing test**

Create `tests/test_shakedown_run.py`:

```python
"""Dev wrapper skeleton tests (no cache logic in skeleton)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
WRAPPER = REPO / "scripts" / "shakedown_run.py"


def test_wrapper_exists() -> None:
    assert WRAPPER.exists()


def test_wrapper_passes_through_empty_stdin() -> None:
    """Skeleton: assemble → invoke shakespeare run → echo back. Empty stdin
    yields whatever the prototype src produces; the wrapper must not crash and
    must propagate the interpreter's exit code."""
    result = subprocess.run(
        [sys.executable, str(WRAPPER)],
        input=b"",
        capture_output=True,
        check=False,
    )
    # Skeleton returns whatever shakespeare run returns; non-zero is acceptable
    # if the prototype SPL needs input. The contract is that the wrapper itself
    # does not raise an unhandled Python exception.
    assert b"Traceback" not in result.stderr, result.stderr.decode()


def test_wrapper_assembles_before_running(tmp_path: Path) -> None:
    """Run with --print-assembled-path to confirm assembly happened."""
    result = subprocess.run(
        [sys.executable, str(WRAPPER), "--print-assembled-path"],
        capture_output=True,
        check=True,
    )
    out = result.stdout.decode().strip()
    assert out.endswith("shakedown.spl"), out
    assert Path(out).exists(), out


def test_wrapper_honours_cache_decision() -> None:
    """The wrapper reads docs/architecture/cache-spike.md and refuses to use
    cache logic when the decision is `direct_assemble_and_run`."""
    result = subprocess.run(
        [sys.executable, str(WRAPPER), "--print-mode"],
        capture_output=True,
        check=True,
    )
    mode = result.stdout.decode().strip()
    assert mode in {"direct", "cached"}, mode


def test_wrapper_line_budget() -> None:
    """Architecture §5.3: wrapper ≤100 lines of Python during dev."""
    lines = WRAPPER.read_text().splitlines()
    assert len(lines) <= 100, len(lines)
```

- [ ] **Step 8.2: Run test to verify it fails**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_shakedown_run.py -v
```

Expected: FAIL on `assert WRAPPER.exists()`.

- [ ] **Step 8.3: Write `scripts/shakedown_run.py`**

```python
"""Dev wrapper for the SPL Markdown port.

Flow per architecture §5.3:
  1. Assemble src/*.spl -> shakedown.spl via scripts/assemble.py.
  2. Read cache-spike verdict (`docs/architecture/cache-spike.md`); if
     decision == "direct_assemble_and_run", skip cache logic entirely.
  3. Invoke `uv run shakespeare run shakedown.spl`, passing stdin/stdout/
     stderr/exit code through.

Slice 1 may extend this; Slice 1 also swaps `./shakedown` to invoke this file.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
ASSEMBLED = REPO / "shakedown.spl"
SPIKE_DOC = REPO / "docs" / "architecture" / "cache-spike.md"


def _assemble() -> Path:
    from scripts.assemble import assemble

    assemble(
        src_dir=REPO / "src",
        manifest=REPO / "src" / "manifest.toml",
        output=ASSEMBLED,
    )
    return ASSEMBLED


def _read_mode() -> str:
    if not SPIKE_DOC.exists():
        return "direct"
    text = SPIKE_DOC.read_text()
    match = re.search(r'"decision":\s*"([^"]+)"', text)
    if not match:
        return "direct"
    return "cached" if match.group(1) == "cache_proven" else "direct"


def _run(spl_path: Path) -> int:
    proc = subprocess.run(
        ["uv", "run", "shakespeare", "run", str(spl_path)],
        stdin=sys.stdin.buffer,
        stdout=sys.stdout.buffer,
        stderr=sys.stderr.buffer,
        check=False,
    )
    return proc.returncode


def main(argv: list[str]) -> int:
    if "--print-assembled-path" in argv:
        print(_assemble())
        return 0
    if "--print-mode" in argv:
        print(_read_mode())
        return 0
    spl_path = _assemble()
    if _read_mode() == "cached":
        # Cache path is implementation-deferred to whichever later plan
        # extends this wrapper after a follow-up cache spike validates a
        # concrete cache target. Today's spike outcome (direct) keeps this
        # branch dead.
        return _run(spl_path)
    return _run(spl_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 8.4: Run test to verify it passes**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_shakedown_run.py -v
```

Expected: 5 tests pass. The first test that runs the wrapper with empty stdin may produce a non-zero exit from the prototype SPL — the assertion only forbids Python tracebacks.

- [ ] **Step 8.5: Type-check**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright scripts/shakedown_run.py
```

Expected: zero errors.

- [ ] **Step 8.6: Commit**

```bash
git add scripts/shakedown_run.py tests/test_shakedown_run.py
git commit -m "feat: add dev-mode wrapper skeleton for shakedown"
```

---

## Task 9: Strict Shakedown-vs-Markdown.pl parity harness

**Files:**
- Create: `scripts/strict_parity_harness.py`
- Create: `tests/test_strict_parity_harness.py`

Architecture §7.1 #6 calls for a script/test path that runs `./shakedown` on claimed fixture inputs and compares **byte-for-byte** to fresh `perl ~/markdown/Markdown.pl`. This is the canonical comparison tool for implementation claims (architecture §8.1 gate 2). It is distinct from `scripts/markdown_pl_parity_audit.py` which compares checked-in expected files against the local oracle; the new harness compares `./shakedown` output against the local oracle.

The harness must:
- Take a list of fixture names (defaults to all `*.text` files in `~/mdtest/Markdown.mdtest/`).
- Run `./shakedown < fixture.text` and capture bytes.
- Run `perl ~/markdown/Markdown.pl < fixture.text` and capture bytes.
- Produce a byte-identical/not table; exit non-zero on any mismatch.

In Plan 1, `./shakedown` is the oracle stub — so the harness will trivially report 100% byte-identical on every fixture. That's fine; the harness exists to be reused by Plan 2+ once `./shakedown` becomes the real wrapper.

- [ ] **Step 9.1: Write the failing test**

Create `tests/test_strict_parity_harness.py`:

```python
"""Strict parity harness self-test.

These tests verify the harness *itself* — they do not certify that shakedown
matches the oracle on real fixtures. That certification only becomes
meaningful once `./shakedown` stops being the oracle stub (Slice 1).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
HARNESS = REPO / "scripts" / "strict_parity_harness.py"
SHAKEDOWN = REPO / "shakedown"
ORACLE = Path.home() / "markdown" / "Markdown.pl"


def test_harness_exists() -> None:
    assert HARNESS.exists()


def test_harness_runs_on_synthetic_input(tmp_path: Path) -> None:
    """Pass a tiny fixture dir; expect the harness to byte-compare cleanly
    while ./shakedown is still the oracle stub."""
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "trivial.text").write_text("hello\n")
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--shakedown",
            str(SHAKEDOWN),
            "--markdown-pl",
            str(ORACLE),
            "--fixtures-dir",
            str(fixtures),
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    assert b"trivial" in result.stdout
    assert b"byte-identical: yes" in result.stdout


def test_harness_reports_mismatch(tmp_path: Path) -> None:
    """Force a mismatch by pointing --shakedown at /bin/cat."""
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "trivial.text").write_text("hello\n")
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--shakedown",
            "/bin/cat",
            "--markdown-pl",
            str(ORACLE),
            "--fixtures-dir",
            str(fixtures),
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert b"byte-identical: no" in result.stdout
```

- [ ] **Step 9.2: Run test to verify it fails**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_strict_parity_harness.py -v
```

Expected: FAIL on `assert HARNESS.exists()`.

- [ ] **Step 9.3: Write `scripts/strict_parity_harness.py`**

```python
"""Run ./shakedown vs. local Markdown.pl on each fixture. Byte-compare.

Distinct from scripts/markdown_pl_parity_audit.py: that script audits
checked-in expected files against the oracle. This script audits
./shakedown's *runtime output* against the oracle.

Architecture spec §7.1 #6 / §8.1 gate 2.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_FIXTURES = Path.home() / "mdtest" / "Markdown.mdtest"
DEFAULT_ORACLE = Path.home() / "markdown" / "Markdown.pl"
DEFAULT_SHAKEDOWN = Path(__file__).parent.parent / "shakedown"


@dataclass(frozen=True)
class FixtureResult:
    name: str
    shakedown_bytes: int
    oracle_bytes: int
    byte_identical: bool
    first_diff_index: int | None


def run_one(executable: Path, input_bytes: bytes) -> bytes:
    if executable.suffix == ".pl" or executable.name.endswith("Markdown.pl"):
        argv = ["perl", str(executable)]
    else:
        argv = [str(executable)]
    result = subprocess.run(
        argv,
        input=input_bytes,
        capture_output=True,
        check=True,
    )
    return result.stdout


def first_diff(a: bytes, b: bytes) -> int | None:
    for i, (x, y) in enumerate(zip(a, b, strict=False)):
        if x != y:
            return i
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def compare(fixture: Path, shakedown: Path, oracle: Path) -> FixtureResult:
    input_bytes = fixture.read_bytes()
    sd = run_one(shakedown, input_bytes)
    or_ = run_one(oracle, input_bytes)
    return FixtureResult(
        name=fixture.stem,
        shakedown_bytes=len(sd),
        oracle_bytes=len(or_),
        byte_identical=(sd == or_),
        first_diff_index=first_diff(sd, or_),
    )


def render(results: list[FixtureResult]) -> str:
    lines = ["# Strict Shakedown-vs-Markdown.pl Parity"]
    lines.append("")
    for r in results:
        verdict = "yes" if r.byte_identical else "no"
        diff = "-" if r.first_diff_index is None else str(r.first_diff_index)
        lines.append(
            f"- {r.name}: byte-identical: {verdict} "
            f"(shakedown={r.shakedown_bytes}, oracle={r.oracle_bytes}, "
            f"first diff: {diff})"
        )
    mismatches = [r for r in results if not r.byte_identical]
    lines.append("")
    lines.append(f"summary: {len(results) - len(mismatches)}/{len(results)} byte-identical")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shakedown", type=Path, default=DEFAULT_SHAKEDOWN)
    p.add_argument("--markdown-pl", type=Path, default=DEFAULT_ORACLE)
    p.add_argument("--fixtures-dir", type=Path, default=DEFAULT_FIXTURES)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    fixtures = sorted(args.fixtures_dir.glob("*.text"))
    if not fixtures:
        print(f"no fixtures in {args.fixtures_dir}", file=sys.stderr)
        return 2
    results = [compare(f, args.shakedown, args.markdown_pl) for f in fixtures]
    print(render(results))
    return 0 if all(r.byte_identical for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 9.4: Run test to verify it passes**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_strict_parity_harness.py -v
```

Expected: 3 tests pass. `test_harness_runs_on_synthetic_input` requires `~/markdown/Markdown.pl` to exist; if it doesn't, the test should be skipped via `pytest.skip`. Add a guard:

```python
if not ORACLE.exists():
    pytest.skip(f"oracle not present at {ORACLE}")
```

at the top of the two tests that need it.

- [ ] **Step 9.5: Smoke-run the harness against the full fixture set**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py | tail -3
```

Expected: every line says `byte-identical: yes` (because `./shakedown` is the oracle stub = `perl Markdown.pl`); summary line reads `23/23 byte-identical`. Exit 0.

- [ ] **Step 9.6: Commit**

```bash
git add scripts/strict_parity_harness.py tests/test_strict_parity_harness.py
git commit -m "feat: add strict shakedown-vs-Markdown.pl parity harness"
```

---

## Task 10: Run-loop prompt

**Files:**
- Create: `docs/prompt-shakedown.md`

Authored against `docs/superpowers/specs/2026-04-27-loop-prompt-design.md` decisions: plan-driven shape (Ralph #2), one step per iteration, eight `@file` university references, ~200-word standing-instructions body, blockers.md cooperation, no autonomous `cz bump`.

The completion-marker convention (`docs/prompt-<name>.md` → `.agent/complete-<name>.md`) is already encoded in `run-loop`. Confirm by reading the relevant code in `run-loop` once before authoring.

- [ ] **Step 10.1: Confirm `run-loop`'s prompt-path expectation**

```bash
grep -n "prompt-shakedown\|complete-" run-loop | head -10
```

Expected: at least one match showing the default prompt path is `docs/prompt-shakedown.md` and the marker path is derived as `.agent/complete-<name>.md`. If the default in code differs from the design note, update `docs/superpowers/specs/2026-04-27-loop-prompt-design.md` to match — the code is ground truth.

- [ ] **Step 10.2: Write `docs/prompt-shakedown.md`**

```markdown
@docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md
@docs/superpowers/plans/plan-roadmap.md
@docs/spl/literary-spec.md
@docs/spl/reference.md
@docs/markdown/target.md
@docs/markdown/divergences.md
@CLAUDE.md
@.agent/blockers.md

You are implementing the Shakedown Markdown-to-HTML port in SPL. This is one
iteration of a continuous run-loop driven by `run-loop` at the repo root.

Your job, this iteration:

1. Read the current implementation plan (the plan file referenced from the
   `plan-roadmap.md` whose status is *in flight*; if multiple are in flight,
   the lowest-numbered one).
2. Find the **first unchecked step** in the **first task** with any unchecked
   step. Complete that step as written. One step. No batching.
3. If the step changes code or data, run the tests the step specifies and
   confirm they pass before proceeding.
4. Check the step's checkbox in the plan file.
5. Commit using a conventional-commit prefix matching the change type
   (`.githooks/commit-msg` enforces this; do not bypass with `--no-verify`).

Standing rules:

- **No placeholders.** Real implementations only. If a step says "write code
  X", write code X — don't write a stub that says "TODO".
- **Aesthetic policy lives in `@docs/spl/literary-spec.md`.** Reach for it
  *before* writing any decorative surface (scene title, character speech,
  Recall description, dramatis personae blurb), not after.
- **No autonomous version bumps.** Do not run `cz bump`, create tags, push
  tags, or update `CHANGELOG.md` unless the current plan step explicitly
  authorises it (architecture spec §7.9). Version cuts are operator
  decisions.
- **Respect `.agent/blockers.md`.** If any line begins with `- BLOCK:`,
  address it first; if you cannot, exit cleanly without modifying code.
- **Stuck? Append `- BLOCK: <one-line reason>` to `.agent/blockers.md` and
  exit.** Do not modify anything else. The operator will see it on the next
  iteration. This is the only sanctioned way to surface a blocker.

Completion: when every step in the active plan is checked and the slice's
verification gate passes (architecture spec §8.1: fixture/snippet pass,
byte-identical to oracle, no regression, no oracle stub), write
`.agent/complete-shakedown.md` (touch is fine). The `run-loop` driver exits
on that marker.
```

- [ ] **Step 10.3: Verify `run-loop` resolves the prompt**

```bash
./run-loop --help 2>&1 | head -5 || true
ls docs/prompt-shakedown.md
test -e docs/prompt-shakedown.md && echo "prompt found"
```

Expected: the prompt file exists and `./run-loop` either accepts it (if the driver supports `--help`) or at least the existence check confirms it. The marker path `.agent/complete-shakedown.md` is derived in code, not authored.

- [ ] **Step 10.4: Commit**

```bash
git add docs/prompt-shakedown.md
git commit -m "feat: add run-loop prompt for autonomous implementation"
```

---

## Task 11: Verification gate for Plan 1

This is the §8.1-style gate for the plan itself: every §7.1 deliverable must exist, all setup tests pass, the cache spike has a decided outcome, and the run-loop driver finds the prompt.

- [ ] **Step 11.1: Run the full setup test suite**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_token_codes.py tests/test_iconic_moments.py tests/test_literary_toml_schema.py tests/test_codegen_html.py tests/test_shakedown_run.py tests/test_strict_parity_harness.py -v
```

Expected: every test passes. If any fails, fix in-place (re-open the relevant task) and re-run before proceeding.

- [ ] **Step 11.2: Confirm every §7.1 deliverable is committed**

```bash
for path in \
  src/literary.toml \
  docs/spl/token-codes.md \
  docs/spl/iconic-moments.md \
  docs/architecture/cache-spike.md \
  scripts/codegen_html.py \
  scripts/shakedown_run.py \
  scripts/strict_parity_harness.py \
  scripts/cache_spike.py \
  docs/prompt-shakedown.md \
  .agent/blockers.md; do
  git ls-files --error-unmatch "$path" >/dev/null 2>&1 && echo "tracked: $path" \
    || echo "MISSING: $path"
done
```

Expected: every line says `tracked:`. Any `MISSING:` halts the gate.

- [ ] **Step 11.3: Confirm `shakedown.spl` ignore is removed**

```bash
grep -E "^shakedown\.spl$" .gitignore && echo "STILL IGNORED" || echo "ok"
```

Expected: `ok`.

- [ ] **Step 11.4: Confirm cache spike has a decided outcome**

```bash
grep -E '^"decision"|"decision":' docs/architecture/cache-spike.md
```

Expected: a line containing either `"cache_proven"` or `"direct_assemble_and_run"`. Anything else is a bug; re-run the spike.

- [ ] **Step 11.5: Confirm run-loop prompt resolves and references its universities**

```bash
head -10 docs/prompt-shakedown.md
```

Expected: eight `@`-prefixed lines listing the universities, in the order from the design note.

- [ ] **Step 11.6: Lint and type-check the new Python**

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run ruff check scripts/ tests/
env UV_CACHE_DIR=/tmp/uv-cache uv run pyright scripts/codegen_html.py scripts/shakedown_run.py scripts/strict_parity_harness.py scripts/cache_spike.py
```

Expected: zero ruff diagnostics, zero pyright errors. Fix in-place if any.

- [ ] **Step 11.7: Update plan roadmap status**

Edit `docs/superpowers/plans/plan-roadmap.md`. In the plan ladder table, change the Plan 1 row's `Status` cell from `pending` to `shipped: 2026-04-28 at commit <SHA>` (use the SHA you get from `git rev-parse --short HEAD` after committing the gate).

- [ ] **Step 11.8: Commit the gate result**

```bash
git add docs/superpowers/plans/plan-roadmap.md
git commit -m "docs: mark plan 1 (pre-Slice-1 setup) shipped"
```

The next plan (Slice 1 — Amps and angle encoding) is now ready to be written per the roadmap's "How to write the next plan" workflow.

---

## Self-review checklist (run before handoff)

1. **Spec coverage:** every architecture §7.1 deliverable maps to a task —
   §7.1 #1 (literary.toml) → Task 5; #2 (Stable Utility) → Task 5; #3
   (token codes) → Task 3; #4 (cache spike) → Task 7; #5 (gitignore policy)
   → Task 2; #6 (parity harness) → Task 9; #7 (wrapper + assembler) →
   Task 8 + (assembler already shipped); #8 (codegen) → Task 6;
   #9 (run-loop prompt) → Task 10; #10 (iconic moments) → Task 4. Plus
   `.agent/blockers.md` (Task 1) and verification gate (Task 11).
2. **Placeholders:** no "TBD"/"TODO"/"add validation"/"similar to N" patterns
   in any task body.
3. **Type/identifier consistency:** `emit_byte`, `emit_literal`,
   `parse_value_phrase` used consistently in Task 6; `cache_proven` /
   `direct_assemble_and_run` used consistently in Tasks 7, 8, 11; token
   names match between Task 3 (allocation), Task 5 (literary.toml uses
   `v1`/`v2`/etc. for Stable Utility, not the dispatch codes), and the
   architecture §4.2 token list.
4. **Test discipline:** every code task has a failing test written first,
   verified to fail, then code to make it pass, then verified to pass.
5. **Commit discipline:** every task ends in a commit; no task batches
   multiple commits except where a single conceptual unit needs them
   (none here).

## References

- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — §7.1 deliverables.
- `docs/superpowers/specs/2026-04-27-loop-prompt-design.md` — run-loop prompt decisions.
- `docs/superpowers/plans/plan-roadmap.md` — staged ladder; this is plan 1 of 8.
- `docs/spl/literary-spec.md` — voice, palette, atom cap, single-surface rule.
- `docs/spl/codegen-style-guide.md` — Critical / Stable / Incidental partition.
- `docs/spl/reference.md` — SPL legality.
- `docs/markdown/target.md`, `docs/markdown/divergences.md` — oracle surface and exceptions.
- `docs/ralph-loop.md` — methodology and `@file` pattern.
- `CLAUDE.md` — commit conventions, `cz bump` operator-only rule.
