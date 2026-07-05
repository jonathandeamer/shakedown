# Token Context Efficiency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve token efficiency and reduce active context window size by archiving shipped plans/specs, decomposing the monolithic `src/literary.toml` by Act, creating a target-querying utility for documentation, and updating `CLAUDE.md` to prevent agents from searching the archive folder.

**Architecture:** 
1. Move shipped files to `docs/archive/plans/` and `docs/archive/specs/` via `git mv`.
2. Split scene-specific sections from `src/literary.toml` into act-local `*-literary.toml` files, and update `load_literary_surfaces` in `scripts/literary_surfaces.py` to recursively load and merge them.
3. Update tests to use the merged loader instead of raw TOML loading.
4. Implement `scripts/query_docs.py` to filter documentation paragraphs by query terms.
5. Update `CLAUDE.md` and `docs/README.md` with explicit instructions to ignore `/archive` directories and utilize `query_docs.py`.

**Tech Stack:** Python 3.12/3.13, Git, TOML.

---

## File Structure

- **Archive Directories:**
  - Create: `docs/archive/plans/`
  - Create: `docs/archive/specs/`
- **TOML Source Files:**
  - Modify: `src/literary.toml` (slimming it down to global rules only)
  - Create: `src/10-act1-literary.toml` (Act I scenes)
  - Create: `src/20-act2-literary.toml` (Act II scenes)
  - Create: `src/30-act3-literary.toml` (Act III scenes)
  - Create: `src/40-act4-literary.toml` (Act IV scenes)
- **Utilities & Testing:**
  - Modify: `scripts/literary_surfaces.py` (merge support)
  - Create: `scripts/query_docs.py` (query CLI)
  - Modify: `tests/test_literary_toml_schema.py` (use merge-loader)
  - Modify: `tests/test_literary_compliance.py` (use merge-loader)
- **Configuration & Integration:**
  - Modify: `docs/superpowers/plans/plan-roadmap.md` (updated roadmap URLs)
  - Modify: `CLAUDE.md` (no-archive rules & query tool documentation)
  - Modify: `docs/README.md` (updated references)

---

## Task 1: Archive Shipped Plans and Specs

**Files:**
- Create: `docs/archive/plans/.gitkeep`
- Create: `docs/archive/specs/.gitkeep`
- Modify: `docs/superpowers/plans/plan-roadmap.md`

- [ ] **Step 1: Create the archive directory structure**

Run:
```bash
mkdir -p docs/archive/plans docs/archive/specs
touch docs/archive/plans/.gitkeep docs/archive/specs/.gitkeep
git add docs/archive/plans/.gitkeep docs/archive/specs/.gitkeep
```

- [ ] **Step 2: Move shipped plan files via git**

Run:
```bash
git mv docs/superpowers/plans/2026-04-17-docs-restructure.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-17-spl-codegen-style-guide.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-17-spl-reference-verification.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-17-spl-style-guide-validation.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-17-spl-style-lexicon.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-18-run-loop-hardening.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-18-run-loop-review-fixes.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-18-shakedown-architecture-prototypes.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-23-markdown-pl-parity-doc-audit.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-23-shakedown-pre-design-due-diligence.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-23-shakedown-pre-design-hardening.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-24-pre-architecture-hardening.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-28-pre-slice-1-setup.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-28-slice-1-amps-angle-encoding.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-29-slice-1-halt-resolution.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-30-literary-compliance-cleanup.md docs/archive/plans/
git mv docs/superpowers/plans/2026-04-30-literary-prevention-rails.md docs/archive/plans/
git mv docs/superpowers/plans/2026-05-01-literary-final-compliance-pass.md docs/archive/plans/
git mv docs/superpowers/plans/2026-05-03-workflow-transition.md docs/archive/plans/
```

- [ ] **Step 3: Move shipped spec files via git**

Run:
```bash
git mv docs/superpowers/specs/2026-04-17-docs-restructure-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-17-spl-codegen-style-guide-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-17-spl-reference-verification-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-17-spl-style-guide-validation-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-17-spl-style-lexicon-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-18-run-loop-hardening-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-18-run-loop-review-fixes-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-18-shakedown-architecture-outline-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-24-pre-architecture-hardening-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-27-loop-prompt-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-29-slice-1-halt-resolution-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-30-literary-compliance-cleanup-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-04-30-literary-prevention-design.md docs/archive/specs/
git mv docs/superpowers/specs/2026-05-03-workflow-transition-design.md docs/archive/specs/
```

- [ ] **Step 4: Update plan-roadmap.md links**

In `docs/superpowers/plans/plan-roadmap.md`, replace the following lines containing links to the specs and plans with their new locations under `docs/archive/`:

```markdown
- `docs/superpowers/plans/2026-04-30-literary-prevention-rails.md`
- `docs/superpowers/specs/2026-04-27-loop-prompt-design.md`
- `docs/superpowers/specs/2026-04-29-slice-1-halt-resolution-design.md`
- `docs/superpowers/specs/2026-04-30-literary-prevention-design.md`
- `docs/superpowers/plans/2026-04-30-literary-prevention-rails.md`
```

Replace them with:

```markdown
- `docs/archive/plans/2026-04-30-literary-prevention-rails.md`
- `docs/archive/specs/2026-04-27-loop-prompt-design.md`
- `docs/archive/specs/2026-04-29-slice-1-halt-resolution-design.md`
- `docs/archive/specs/2026-04-30-literary-prevention-design.md`
- `docs/archive/plans/2026-04-30-literary-prevention-rails.md`
```

- [ ] **Step 5: Verify tests still run**

Run:
```bash
uv run pytest tests/test_roadmap_contract.py
```
Expected: PASS.

- [ ] **Step 6: Commit the archiving stage**

Run:
```bash
git commit -m "chore: archive shipped plans and specs to docs/archive/"
```

---

## Task 2: Implement TOML Recursive Merging & Decompose literary.toml

**Files:**
- Modify: `scripts/literary_surfaces.py`
- Modify: `src/literary.toml`
- Create: `src/10-act1-literary.toml`
- Create: `src/20-act2-literary.toml`
- Create: `src/30-act3-literary.toml`
- Create: `src/40-act4-literary.toml`

- [ ] **Step 1: Write helper script to split literary.toml**

Write a temporary Python script `scripts/split_literary.py`:

```python
import tomllib
from pathlib import Path

SRC = Path("src")
LITERARY_TOML = SRC / "literary.toml"

def split_toml():
    with LITERARY_TOML.open("rb") as f:
        data = tomllib.load(f)

    scenes = data.pop("scenes", {})
    
    act1_scenes = {}
    act2_scenes = {}
    act3_scenes = {}
    act4_scenes = {}

    for label, scene in scenes.items():
        if label.startswith("HECATE_") or label.startswith("ACT_I_"):
            act1_scenes[label] = scene
        elif label.startswith("MASON_") or label.startswith("HERALD_") or label.startswith("ACT_II_"):
            act2_scenes[label] = scene
        elif label.startswith("LYRIC_") or label.startswith("ACT_III_"):
            act3_scenes[label] = scene
        elif label.startswith("SCRIBE_") or label.startswith("ACT_IV_"):
            act4_scenes[label] = scene
        else:
            # Fallback based on name or first letter
            if "HECATE" in label:
                act1_scenes[label] = scene
            elif "MASON" in label:
                act2_scenes[label] = scene
            elif "LYRIC" in label:
                act3_scenes[label] = scene
            elif "SCRIBE" in label:
                act4_scenes[label] = scene
            else:
                raise ValueError(f"Unknown scene ownership: {label}")

    # Helper to format single TOML block for scenes
    def format_scenes(scenes_dict):
        lines = []
        for label in sorted(scenes_dict):
            scene = scenes_dict[label]
            lines.append(f"[scenes.{label}]")
            lines.append(f'title = "{scene["title"]}"')
            if "pattern" in scene:
                lines.append(f'pattern = "{scene["pattern"]}"')
            lines.append("")
        return "\n".join(lines)

    (SRC / "10-act1-literary.toml").write_text(format_scenes(act1_scenes))
    (SRC / "20-act2-literary.toml").write_text(format_scenes(act2_scenes))
    (SRC / "30-act3-literary.toml").write_text(format_scenes(act3_scenes))
    (SRC / "40-act4-literary.toml").write_text(format_scenes(act4_scenes))

    # Re-write src/literary.toml without the [scenes] blocks
    # We will do this by truncating it right before the first [scenes.*] section
    content = LITERARY_TOML.read_text()
    idx = content.find("[scenes.")
    if idx != -1:
        slimmed_content = content[:idx].strip() + "\n"
        LITERARY_TOML.write_text(slimmed_content)

if __name__ == "__main__":
    split_toml()
```

Run the script to split the file, then remove it:
```bash
uv run python scripts/split_literary.py
rm scripts/split_literary.py
```

- [ ] **Step 2: Add TOML merging logic to load_literary_surfaces**

In `scripts/literary_surfaces.py`, modify `load_literary_surfaces` to load all `*-literary.toml` files in the directory and merge them recursively.

Replace lines 50-60 in `scripts/literary_surfaces.py`:

```python
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
```

With:

```python
def _merge_dicts(dest: dict, src: dict) -> None:
    for k, v in src.items():
        if k in dest and isinstance(dest[k], dict) and isinstance(v, dict):
            _merge_dicts(dest[k], v)
        else:
            dest[k] = v


def load_literary_surfaces(path: Path) -> LiterarySurfaces:
    with path.open("rb") as f:
        data = tomllib.load(f)
    
    # Recursively load and merge all other *-literary.toml files in the same directory
    for file_path in sorted(path.parent.glob("*-literary.toml")):
        if file_path == path:
            continue
        with file_path.open("rb") as f:
            sub_data = tomllib.load(f)
            _merge_dicts(data, sub_data)

    surfaces = LiterarySurfaces(data=cast(dict[str, object], data))
    if "value_atoms" in data:
        value_atoms = data["value_atoms"]
        if isinstance(value_atoms, dict):
            for family in value_atoms:
                if isinstance(family, str):
                    surfaces.value_atoms(family)
    return surfaces
```

- [ ] **Step 3: Verify the assembler runs on split TOMLs**

Run:
```bash
uv run python scripts/assemble.py
git diff shakedown.spl
```
Expected: `shakedown.spl` remains completely unchanged (zero diff), confirming the assembly pipeline outputs the exact same binary under split TOML files.

- [ ] **Step 4: Commit the split TOMLs and merge logic**

Run:
```bash
git add src/*-literary.toml src/literary.toml scripts/literary_surfaces.py
git commit -m "feat: decompose src/literary.toml by Act and load recursively"
```

---

## Task 3: Update Test Schema to Use Literary Surfaces Loader

**Files:**
- Modify: `tests/test_literary_toml_schema.py`
- Modify: `tests/test_literary_compliance.py`

- [ ] **Step 1: Update tests/test_literary_toml_schema.py**

In `tests/test_literary_toml_schema.py`, modify `load()` to read via `load_literary_surfaces` instead of reading the file raw.

Replace lines 47-49 in `tests/test_literary_toml_schema.py`:

```python
def load() -> dict[str, object]:
    with LITERARY_TOML.open("rb") as f:
        return tomllib.load(f)
```

With:

```python
from scripts.literary_surfaces import load_literary_surfaces

def load() -> dict[str, object]:
    return load_literary_surfaces(LITERARY_TOML).data
```

- [ ] **Step 2: Update tests/test_literary_compliance.py**

In `tests/test_literary_compliance.py`, modify `_literary()` to read via `load_literary_surfaces`.

Replace lines 94-96 in `tests/test_literary_compliance.py`:

```python
def _literary() -> dict[str, object]:
    with LITERARY_TOML.open("rb") as f:
        return tomllib.load(f)
```

With:

```python
from scripts.literary_surfaces import load_literary_surfaces

def _literary() -> dict[str, object]:
    return load_literary_surfaces(LITERARY_TOML).data
```

- [ ] **Step 3: Run the compliance tests**

Run:
```bash
uv run pytest tests/test_literary_toml_schema.py tests/test_literary_compliance.py
```
Expected: PASS.

- [ ] **Step 4: Commit the test fixes**

Run:
```bash
git add tests/test_literary_toml_schema.py tests/test_literary_compliance.py
git commit -m "test: update literary compliance and schema tests to load merged TOMLs"
```

---

## Task 4: Create scripts/query_docs.py

**Files:**
- Create: `scripts/query_docs.py`

- [ ] **Step 1: Write scripts/query_docs.py**

Write the query tool `scripts/query_docs.py` to index markdown paragraphs and filter by case-insensitive query terms.

```python
#!/usr/bin/env python3
"""Query tool to retrieve specific sections/paragraphs from docs/ to save tokens."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search documentation paragraphs for matches to reduce context size."
    )
    parser.add_argument("query", help="Term to search for (case-insensitive)")
    parser.add_argument(
        "--file-glob",
        default="*.md",
        help="Glob pattern for markdown files to search under docs/",
    )
    args = parser.parse_args()

    query_lower = args.query.lower()
    matches: list[tuple[Path, int, str]] = []

    # Walk docs directory, ignoring archive/
    for path in sorted(DOCS_DIR.rglob(args.file_glob)):
        if "archive" in path.parts:
            continue
        if not path.is_file():
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Split into paragraphs by double newline
        paragraphs = content.split("\n\n")
        for idx, para in enumerate(paragraphs, 1):
            if query_lower in para.lower():
                matches.append((path, idx, para.strip()))

    if not matches:
        print(f"No matches found for {args.query!r} under {args.file_glob} (excluding archive/).")
        return 1

    print(f"Found {len(matches)} matching paragraph(s):\n")
    for path, para_idx, para in matches:
        rel_path = path.relative_to(REPO_ROOT)
        print(f"--- File: {rel_path} (Paragraph {para_idx}) ---")
        print(para)
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Make scripts/query_docs.py executable**

Run:
```bash
chmod +x scripts/query_docs.py
```

- [ ] **Step 3: Verify the query tool works**

Run:
```bash
uv run scripts/query_docs.py pronoun
```
Expected: Prints the paragraph defining pronoun resolution from `docs/spl/reference.md` and/or `docs/spl/verification-evidence.md`.

- [ ] **Step 4: Commit the query tool**

Run:
```bash
git add scripts/query_docs.py
git commit -m "feat: add scripts/query_docs.py documentation query utility"
```

---

## Task 5: Update CLAUDE.md & docs/README.md

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/README.md`

- [ ] **Step 1: Add archive exclusion and query-tool guidelines to CLAUDE.md**

In `CLAUDE.md` (which is symlinked to `AGENTS.md`):
1. Under `## Reference materials`, add a warning about the `docs/archive/` folder.
2. Under `## Tooling`, document `uv run scripts/query_docs.py`.

Specifically, in `CLAUDE.md`, locate this block:
```markdown
## Reference materials

- `~/markdown/Markdown.pl` — oracle; the thing being ported
```

And insert the warning right before it:
```markdown
## Reference materials

> [!WARNING]
> Do NOT read or search files inside `docs/archive/`. Those are historical, shipped, or superseded plan artifacts and are irrelevant to active development.

- `~/markdown/Markdown.pl` — oracle; the thing being ported
```

Also, locate:
```markdown
## Tooling

```bash
uv run ruff check .  # lint Python
```

And insert the query tool:
```markdown
## Tooling

```bash
uv run python scripts/query_docs.py "query"  # query active documentation paragraphs to save tokens
uv run ruff check .  # lint Python
```

- [ ] **Step 2: Update docs/README.md optional-context section**

In `docs/README.md`, find the section:
```markdown
Optional historical/supporting context:

- [`superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`](superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md) — latest pre-design synthesis. Useful context, not canonical truth.
- [`superpowers/specs/`](superpowers/specs/) — proposed design/spec artifacts from earlier interactive planning. The selected architecture spec is the one active exception and is linked from `architecture/selected-architecture.md`; other specs are historical context unless restated in canonical docs.
- [`superpowers/plans/`](superpowers/plans/) — implementation plans and process artifacts. Use `superpowers/plans/plan-roadmap.md` for live plan status.
```

Replace it with:
```markdown
Optional historical/supporting context (Do not search or read inside `docs/archive/`):

- [`superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`](superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md) — latest pre-design synthesis. Useful context, not canonical truth.
- [`superpowers/specs/`](superpowers/specs/) — active design/spec artifacts. Historical design specs have been moved to `docs/archive/specs/` and do not need to be read.
- [`superpowers/plans/`](superpowers/plans/) — active plans. Shipped plans have been moved to `docs/archive/plans/` and do not need to be read.
```

- [ ] **Step 3: Run the full test suite regression check**

Run:
```bash
uv run pytest
```
Expected: The exact same 7 failures occur (6 in-flight list spikes + 1 binary contract exception), with no new failures.

- [ ] **Step 4: Commit the instructions updates**

Run:
```bash
git add CLAUDE.md docs/README.md
git commit -m "docs: update CLAUDE.md and README to document query utility and exclude archives"
```

---

## Completion criteria

All tasks have been implemented and checked.
The file `shakedown.spl` remains completely unchanged.
All active documentation tests pass.
A new commit log reflects:
1. `chore: archive shipped plans and specs to docs/archive/`
2. `feat: decompose src/literary.toml by Act and load recursively`
3. `test: update literary compliance and schema tests to load merged TOMLs`
4. `feat: add scripts/query_docs.py documentation query utility`
5. `docs: update CLAUDE.md and README to document query utility and exclude archives`
