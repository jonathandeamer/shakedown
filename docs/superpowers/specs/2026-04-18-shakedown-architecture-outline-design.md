# Shakedown Architecture Outline Design

**Date:** 2026-04-18
**Status:** Proposed

## Purpose

Commit to the architectural *shape* of Shakedown — the SPL port of Markdown.pl — without committing to the concrete mechanics that belong in a detailed spec. This outline spec exists specifically to break the "design while implementing" cycle that stalled the prior shakedown attempt and that quackdown evolved around rather than avoided.

The outline fixes the decisions that cannot be safely deferred. It leaves everything else to a two-phase prototype, whose evidence then feeds a detailed architecture spec, which in turn feeds the implementation plan that produces the run-loop prompt.

## Problem

Shakedown needs an architecture. The prior attempt built 4,311 lines of streaming single-act block-level SPL before discovering the streaming shape could not cleanly integrate inline processing. Quackdown grew its CTE structure organically fixture-by-fixture, which worked for Phase 2 but created a structure that resists extension. Both are instances of "design while implementing" — the architecture was discovered, not decided.

This repo's docs set (`docs/prior-attempt/`, `docs/spl/reference.md`, `docs/verification-plan.md`, `docs/markdown/target.md`, `docs/markdown/fixture-outlook.md`) provides the inputs an architecture spec needs. What has been missing is a written commitment to a specific shape, validated before being built on.

## Scope

In scope:

- Committing to the overall shape: SPL-pure, fragment-assembled, buffered multi-phase
- Committing to a Python build toolchain and its minimum responsibilities
- Specifying a two-phase throwaway prototype that validates the shape before any real implementation begins
- Specifying the workflow chain from this outline through to Huntley-loop execution
- Specifying decision gates between stages

Out of scope:

- Concrete intermediate representation between phases
- Character cast assignments
- Scene naming conventions, stack-reversal patterns, runtime deduplication via return-address-scenes
- Exact phase count (3 or 4)
- Fixture build order
- Any production SPL code
- The run-loop prompt itself

Those are outputs of the prototype + detailed spec stages, not this one.

## Committed Decisions

### Execution model

Shakedown is a **pure SPL program**. At runtime, one `.spl` file is executed by the `shakespearelang` interpreter. The shell wrapper `./shakedown` is a thin two-step script: (1) invoke the Python build assembler to produce a fresh `shakedown.spl` from the `src/` fragments, then (2) invoke `uv run shakespeare run shakedown.spl`. Both steps resolve their dependencies through the project's Python environment (`uv run`) rather than the ambient shell PATH. No Python wrapper does meaningful *markdown* work; no preprocessing, no reference-collection shim, no postprocessing. All markdown-processing logic lives inside SPL.

`shakedown.spl` is a **build artifact**, not a checked-in source file. It is listed in `.gitignore`. Only the `src/` fragments and the build script are committed. This eliminates the dual-source-of-truth risk where hand edits to `src/` could leave a stale `shakedown.spl` in place.

The per-invocation build is unconditional and idempotent. Its cost (ordered fragment concatenation plus scene-number substitution) is negligible relative to the `shakespearelang` interpreter cold-start on this machine, so always-rebuild is cheaper in design-time than any staleness-detection machinery.

`shakespearelang` must be declared as a project runtime dependency in `pyproject.toml` so that `uv sync` installs it into the project venv. This replaces the implicit reliance on `~/.local/bin/shakespeare` being on PATH, which `CLAUDE.md` explicitly flags as unreliable in a fresh shell and which would otherwise cause `tests/test_mdtest.py` to fail with exit 127 before any SPL runs.

Rationale: the SPL-pure constraint is the art-project spirit of the target and it removes a whole class of architectural ambiguity. It is also a stronger forcing function for the prototype work below — if SPL cannot do something, the prototype will surface that immediately rather than hiding it behind a Python helper. Resolving both assembler and interpreter through `uv run` is consistent with the rest of the repo's tooling (`uv sync`, `uv run pytest`, `uv run ruff`) and keeps the wrapper under a handful of lines with no conditional logic.

### Parse shape

Shakedown uses a **buffered, multi-phase architecture**. Stdin is fully consumed into a buffer before block processing begins. Block processing consumes the buffer and produces an intermediate representation. Inline processing consumes that representation and emits HTML.

Each major phase lives in **its own SPL act**, using act-local gotos the way the language affords. This is the structural opposite of the prior attempt, which crammed the entire read-classify-handle loop into a single act because its streaming shape forced backwards gotos across all of it.

This shape is closest to Option B in `docs/prior-attempt/architecture-lessons.md`, but deliberately does not inherit that memo's commitment to a typed token stream as the intermediate representation — the representation is deferred to the prototype.

Rationale: a buffered multi-phase shape fits SPL's act-local goto constraint naturally. It separates block and inline cleanly, which is the specific failure mode of the prior attempt. It makes reference-definition collection tractable without a wrapper. The per-run cost of multiple passes is dominated by interpreter startup, not pass count, so the cost of buffering is small on this machine.

The outline commits to **at least three phases**: read-to-buffer, block parse, inline process. Whether reference-definition collection is its own phase (for four total) is deferred to the prototype.

### Source layout

Shakedown source lives as **multiple `.spl` fragment files** under `src/`, assembled by a Python build script into a single runtime `shakedown.spl`. Ordering is explicit via a manifest (`src/manifest.toml` or equivalent), not filename-dependent. Scene numbers are assigned by the build, from logical labels declared in fragments (`Scene @READ_LOOP:` → `Scene I:`, etc.), so fragments remain independently readable and reorderable.

Rationale: SPL has no import mechanism, so the runtime artifact is always one file. Source-level fragmentation solves the prior attempt's duplication problem (before-block dispatch and content emission patterns were copy-pasted five-plus times) at the source layer, without requiring runtime macro machinery.

### Build toolchain

The build script is **Python** (stdlib sufficient; `uv run` invocation). Its minimum responsibilities are:

- Ordered fragment assembly per manifest
- Scene-number resolution from logical labels to Roman numerals
- Producing a deterministic single `shakedown.spl` build artifact

Everything else (templating, parameter substitution, incremental builds, dependency tracking) is deliberately out of scope for the initial build tool. If the prototype proves a need, the detailed spec adds it. The default is "minimal, Python, stdlib, one script."

`shakedown.spl` is gitignored; only the `src/` fragments, the manifest, and the build script are committed.

Two entry points use the build:

- `./shakedown` runs the build as its first step, then the interpreter (see "Execution model" above).
- `uv run python scripts/assemble.py` (or equivalent) runs the build alone, for cases where someone wants to inspect the assembled output without executing it.

Rationale: the repo already uses `uv` and `pyproject.toml`; adding a Python script costs nothing and introduces no foreign tooling. Keeping the build minimal until proven otherwise prevents the toolchain from becoming its own design problem. Always-rebuild-on-invocation is cheaper in design than staleness detection, given the interpreter's cold-start cost.

### Distribution

`shakedown.spl` is not committed to git, but it **is** intended to be distributed: for GitHub releases, the assembled `shakedown.spl` should be attached as a release asset so consumers can download and run the final Shakespearean artifact without installing `uv`, Python, and the build tooling. This fits the art-project spirit — the assembled play is itself the thing worth distributing.

Release mechanics integrate with the existing cadence documented in `CLAUDE.md`: `uv run cz bump` produces a tag based on conventional commits, `git push --tags` pushes it, and a CI workflow triggered on tag push builds `shakedown.spl` and attaches it to the release.

Creating that CI workflow is future **implementation** work, not in scope for this outline spec. It will be captured as a task in the implementation plan produced after the detailed architecture spec.

### Workflow model

Implementation of `shakedown.spl` itself happens in **Huntley-style run-loops**. All design, planning, and prototyping happens in **interactive Claude sessions with superpowers**. The run-loop prompt at `docs/prompt-shakedown.md` does not exist yet and will not be created until implementation planning produces it. The archived `docs/archive/prompt-shakedown.md` is not a starting point for the new prompt.

When the run-loop prompt is written, it must explicitly forbid version-cutting and release actions: **the loop must not run `uv run cz bump`, must not create version tags, and must not push tags to origin**. Version cadence is a deliberate human decision tied to milestones (per `CLAUDE.md`'s "When to cut a version" table). The loop's job is to produce conventional commits that accumulate toward a milestone; the human decides when to tag and release.

Rationale: the two-mode split keeps design sessions clean and ensures the run-loop prompt is designed deliberately as an output of implementation planning, not improvised to unblock a stalled loop. The release guardrail ensures CI-triggered artifact builds fire on intent, not on autonomous loop iteration.

### Policy docs (implementation guidance, not architecture)

`docs/spl/style-lexicon.md` and `docs/spl/codegen-style-guide.md` are implementation policy: legal SPL vocabulary and recommendations for encoding recurring value phrases. They are not architectural inputs. The prototype may incidentally exercise them but is not a validation of them (the pending `docs/superpowers/plans/2026-04-17-spl-style-guide-validation.md` does that separately).

The detailed architecture spec and the eventual run-loop prompt should both reference these docs as policy to follow during implementation.

## Deferred to the Prototype

The following decisions are **explicitly not made in this spec**. They are what the prototype discovers and the detailed spec then fixes:

- Exact phase count (3 vs 4 — whether reference-definition collection is its own phase)
- Intermediate representation between phases (raw chars plus boundary markers? typed numeric token codes? a stack convention?)
- Character cast: which characters play which roles, across which acts
- Stack-reversal patterns and cross-act buffer handoff mechanics
- Whether the runtime uses the return-address-scene deduplication pattern described in `docs/prior-attempt/architecture-lessons.md`
- Scene structure and naming conventions within each act
- Fixture build order

## Prototype 1 — Walking Skeleton

**Goal.** Prove the overall mechanics of Option B work end-to-end. The simplest possible build that exercises all three phases, the full fragment assembly flow, and the full stdin-to-stdout pipeline.

**Scope.**

- Phase 1 reads stdin to a buffer until EOF
- Phase 2 identifies paragraphs only (blank-line separation)
- Phase 3 processes one inline feature — code spans — within paragraph text
- Final act emits HTML to stdout
- At least three source fragments assembled by the build script

**Success criteria.**

- Handles a hand-crafted input: two paragraphs separated by a blank line, one containing a code span. Emits correct HTML.
- Fragment assembly produces a working `shakedown.spl`.
- Runs end-to-end without interpreter errors.

**Evidence produced (the real output).**

- What intermediate representation survived between phases
- What stack-reversal patterns were needed
- Which characters played which roles
- Cold-start and warm per-run timing on this machine
- Line counts per phase (rough sense of weight distribution)
- Anything surprisingly hard or surprisingly easy

**Gate.** If P1 reveals Option B is structurally wrong (e.g., buffer handoff between acts is intractable), stop and revisit this outline spec. If P1 works, proceed to P2.

**Throwaway discipline.** The code does not survive. Only the evidence document feeds the detailed spec.

## Prototype 2 — Inline Stressor

**Goal.** Catch the specific failure mode that killed the prior attempt: inline processing that works in isolation but can't handle block/inline interaction or Markdown.pl's backtracking semantics.

**Scope.**

- Extends P1 (or starts fresh if P1 reset the design)
- Adds one hard inline feature: emphasis (`*text*` and `_text_`), including at least one Markdown.pl backtracking case
- Adds one cross-cutting block/inline case: emphasis inside a blockquote

**Success criteria.**

- Simple emphasis matches the oracle.
- At least one Markdown.pl backtracking case matches the oracle, **or** is documented as a divergence candidate for the detailed spec to decide on.
- `> *foo*` inside a blockquote produces `<blockquote><p><em>foo</em></p></blockquote>` matching the oracle (modulo `docs/markdown/divergences.md`).
- Per-fixture runtime is re-measured on this first realistic-sized program.

**Evidence produced.**

- Whether P1's intermediate representation survived contact with inline complexity, or had to change
- What the block phase must encode for the inline phase to work inside nested structures
- Whether Markdown.pl emphasis backtracking is reproducible in this architecture — confirms or rules out a divergence
- Updated timing on a realistic-sized program
- A list of items the detailed spec now has to pin down

**Gate.** If P2 reveals emphasis backtracking is structurally impossible, either accept a documented divergence or revisit this outline spec. Either outcome is a valid result; neither is a failure of the architecture process.

**Throwaway discipline.** Same as P1. Only the evidence survives.

## Workflow Chain and Deliverables

1. **This outline spec** — commits to the shape. Committed now.
2. **Implementation plan for prototypes** — produced by the writing-plans skill immediately after this spec is approved. Breaks P1 and P2 into executable steps for an interactive Claude session.
3. **Prototype 1 execution** — interactive Claude session. Produces throwaway SPL and an evidence document.
4. **Prototype 2 execution** — interactive Claude session. Produces throwaway SPL and a second evidence document.
5. **Detailed architecture spec** — new brainstorm cycle informed by P1 + P2 evidence. Pins down every item in the "Deferred" section above.
6. **Implementation plan for `shakedown.spl`** — produced by writing-plans against the detailed spec. Establishes fixture-by-fixture build order with concrete iteration steps.
7. **Run-loop prompt** — final output of implementation planning. Lives at `docs/prompt-shakedown.md`. Replaces the archived prompt.
8. **Huntley-loop execution** — `./run-loop` executes the prompt fixture by fixture until the completion marker is written.

## Decision Gates

- **After P1.** Option B works mechanically? → P2. Doesn't work? → revise this outline spec.
- **After P2.** Inline integration works at the hard cases? → detailed spec. Doesn't work? → revise this outline spec or accept a documented divergence.
- **After detailed spec.** Any open questions block implementation? → the detailed spec isn't done. None? → implementation planning.
- **During Huntley loop.** Fixture-by-fixture pass rate improving? → continue. Stalling? → stop and revisit.

## What This Spec Prevents

- Writing SPL before the architecture is validated (the prior shakedown attempt's failure).
- Writing a detailed spec before the prototype has proven the shape (quackdown's "design while implementing" pattern).
- Starting a Huntley loop before there is a prompt targeting a validated architecture (the current broken state of `./run-loop`).

## What This Spec Does Not Do

- It does not commit to any SPL code.
- It does not decide fixture order.
- It does not resolve every sub-question raised by the A/B/C options in `docs/prior-attempt/architecture-lessons.md`. It commits to the buffered multi-phase shape those options collectively framed as "B-like," and leaves the specific mechanical choices (intermediate representation, runtime deduplication, sub-dispatch patterns) to the prototype and the detailed spec.
- It does not replace `docs/verification-plan.md` or any of the canonical truth docs.
