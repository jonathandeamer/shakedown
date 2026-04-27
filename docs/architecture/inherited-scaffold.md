# Inherited Scaffold

This document describes the prototype scaffold that was present in the repository before the selected architecture. Its purpose is to surface the inherited state so implementation planning engages with it as a deliberate input, not as an invisible default.

**Important:** this is prototype shape, not adopted architecture. The selected architecture may keep, revise, or replace any element of the scaffold without constraint.

## The Scaffold

The prototype scaffold consists of:

- **`./shakedown`** - the production entry-point. Currently a bash stub that delegates to `~/markdown/Markdown.pl` via `perl`. This is the oracle stub; all 23 mdtest fixtures pass because Markdown.pl is the oracle. This is deliberate: the stub keeps the contract green while the SPL implementation is built up.

- **`./shakedown-dev`** - the prototype entry-point. A bash wrapper that runs `uv run python scripts/assemble.py` (to rebuild `shakedown.spl` from `src/*.spl`) then `uv run shakespeare run shakedown.spl`. Its own comment states "This is the shape the final ./shakedown will take." Treat that comment as aspirational, not decided: follow the selected architecture rather than the prototype comment where they differ.

- **`scripts/assemble.py`** - a Python script that concatenates `src/*.spl` into the single `shakedown.spl` file and resolves symbolic scene labels to act-local Roman numerals. SPL has no import mechanism, so assembly is one way to keep source readable while complying with the single-file constraint.

- **`src/*.spl`** - source fragments, currently split as:
  - `00-preamble.spl` - dramatis personae and act header
  - `10-phase1-read.spl` - phase 1 (read) scenes
  - `20-phase2-block.spl` - phase 2 (block) scenes
  - `30-phase3-inline.spl` - phase 3 (inline) scenes

  The three-phase split (read / block / inline) is a prototype design choice, not a verified requirement. Follow the selected architecture for the implementation source layout.

- **`src/manifest.toml`** - the ordered fragment list consumed by `scripts/assemble.py`.

- **`shakedown.spl`** - the assembled output when `./shakedown-dev` or `scripts/assemble.py` has been run. It may be absent in a clean checkout. It is generated output, not hand-edited source.

## What the Scaffold Does Not Decide

- Whether the final `./shakedown` is bash, Python, or something else.
- Whether SPL source is assembled from fragments or maintained as a single hand-edited file.
- Whether the internal phase split is read/block/inline, pre-scan/dispatch/render, one-pass-streaming, or another shape.
- Whether an AST cache exists between assembly and interpreter run.
- Whether SPL execution happens every invocation or once per cached parse.

These were architecture decisions. This document exists so implementation planning does not inherit prototype details tacitly.

## Relationship to the Architecture Rubric

`docs/architecture/decision-rubric.md` lists observable correctness, documented parity exceptions, fixture-level verification, SPL ownership of Markdown semantics, maintainability, and runtime cost as the scoring axes. The scaffold does not preempt any of those: any candidate architecture must justify its choices on the rubric, even if it adopts the scaffold as-is.
