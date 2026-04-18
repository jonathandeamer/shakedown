> Archived 2026-04-17. Mid-session brainstorming snapshot from 2026-04-14; its purpose (resuming a specific feasibility-study session on another machine) was consumed. Consolidated feasibility findings now live in `docs/prior-attempt/feasibility-lessons.md`. Lineage narrative lives in `docs/lineage.md` and `docs/archive/project-history.md`.

---

# Shakedown SPL Feasibility Study — Session Context for Resumption

**Date:** 2026-04-14
**Purpose:** Allow this brainstorming session to be resumed on a different machine. Captures everything learned so far, the user's ask, the state of thinking, and the next step.

---

## The user's ask

> "look back through the git history and read the shakespeare/shakedown/spl files we removed a few days ago. then read all the related files in /docs/. i want us to carry out a feasability study for the shakedown spl project as if we were starting from scratch (markdown.pl only, not common mark). read the docs, then let's use superpowers to brainstorm"

Intent: produce a fresh feasibility study for a Shakespeare Programming Language (SPL) implementation of Markdown.pl v1.0.1 — **not** CommonMark — treating it as a greenfield decision rather than continuing the stalled `shakedown.spl` work. The study should mirror the rigour of the recent `quackdown-cm` CommonMark feasibility study (four pre-flight SQL experiments with PASS/PARTIAL/BLOCKED verdicts) but targeted at SPL and the Markdown.pl feature set.

Methodology: the superpowers `brainstorming` skill (activated this session). Flow is:
1. Explore context ✓
2. Ask clarifying questions (in progress — one question asked, awaiting answer)
3. Propose 2–3 approaches
4. Present design sections, get approval
5. Write design doc to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
6. Self-review + user review of spec
7. Invoke `writing-plans` skill

Hard gate: no implementation, no code, no scaffolding until user approves a presented design.

---

## Project lineage (as of 2026-04-14)

The current repo is `quackdown` (DuckDB SQL port of Markdown.pl). It has two predecessors whose artifacts were deleted but live in git history:

1. **Shakedown (SPL)** — lived in `~/shakedown/`, 2026-04-03 to 2026-04-11. Stalled.
2. **Snarkdown (CURSED)** — lived briefly in `~/snarkdown/`, 2026-04-11. Blocked by a pre-alpha CURSED compiler that had no stdin, no file I/O, no conditionals, no loops.
3. **Quackdown (DuckDB SQL)** — current. Phase 2 complete (23/23 Markdown.mdtest cases). Phase 3 (`quackdown-cm.sql`, CommonMark) in progress at 328/655.

The unifying substrate across all three: Huntley-loop methodology (automated agent iterating against a citation spec + test harness), same 23 `Markdown.mdtest` fixtures, same `Markdown.pl` oracle.

Full narrative: `docs/project-history.md`.

---

## Where the SPL files live now

Deleted in commit `9e6c04f` ("chore!: remove Shakespeare Programming Language artifacts now that history is merged", 2026-04-12). Recover with `git show 9e6c04f^:<path>`.

Deleted paths of interest:
- `shakedown.spl` — **4311 lines**, the SPL implementation
- `shakedown` — shell wrapper delegating to `shakespeare run shakedown.spl`
- `scripts/spl-smoke` — smoke-test helper for slow-machine workflow (supports `slice1` and `blockquote` cases, `--oracle` flag for comparison)
- `pytest.ini`, `tests/conftest.py`, `tests/harness.py`, `tests/test_*.py`, `tests/fixtures/**` — full Python test suite replaced during the quackdown pivot

Reference docs that **still exist** in `docs/`:
- `project-history.md` — three-chapter narrative
- `shakedown-spl-reference.md` — SPL language reference (characters, encoding, operations, control flow, constraints)
- `shakedown-divergences.md` — two documented divergences from Markdown.pl
- `shakedown-2026-04-03-tests-prompt-for-superpowers.md`
- `shakedown-2026-04-06-blockquote-investigation.md`
- `shakedown-2026-04-09-blockquote-follow-up.md` — status at end of Slice 1
- `shakedown-2026-04-09-slow-machine-spl-workflow.md` — slow-machine workflow + `scripts/spl-smoke` usage
- `shakedown-2026-04-10-spl-act-architecture.md` — the architecture decision doc; project stalled here
- `docs/superpowers/specs/2026-04-05-shakedown-spl-design.md` — original approved design
- `docs/superpowers/plans/2026-04-05-shakedown-spl-slice-1.md` — Slice 1 plan
- `docs/superpowers/plans/2026-04-03-shakedown-test-harness.md`, `2026-04-04-coverage-gaps-round-2.md`, `2026-04-03-test-coverage-gaps.md`, `2026-04-04-missing-test-coverage.md` — harness/coverage plans
- `docs/superpowers/specs/2026-04-03-shakedown-test-harness-design.md`, `2026-04-03-test-coverage-design.md`, `2026-04-04-missing-test-coverage-design.md`

The analogous precedent we're trying to mirror:
- `docs/superpowers/specs/2026-04-12-commonmark-feasibility-design.md` — four-experiment structure with PASS/PARTIAL/BLOCKED verdicts
- `docs/prompt-feasibility.md` — the loop prompt that drove that study
- `experiments/` directory — previous feasibility outputs (exp-N-*.sql, exp-N-*-verdict.md, feasibility-summary.md)

---

## What the prior SPL attempt proved and where it stalled

**Completed (Slice 1 — block structure):**
- Character-by-character stdin ingest with CRLF normalisation
- Line buffering on Hamlet's stack
- Tab expansion
- Paragraph emission
- ATX headings (`#`..`######`)
- Setext headings (`=` and `-` underlines)
- Horizontal rules (`***`, `---`, `___` variants)
- Indented code blocks with HTML-encoded `<` and `&`
- Blockquotes: simple, multiline, lazy continuation, nested (structurally correct; not byte-identical to oracle quirk), containing headings, containing code blocks

**Not started:** inline (emphasis, code spans, links, images, autolinks, escapes, entity encoding), lists, HTML blocks. Slice 2 and Slice 3 never began.

**Documented divergences from Markdown.pl:**
1. Email autolinks — Markdown.pl randomly entity-encodes each character; SPL has no randomness primitive, so output is plain `<a href="mailto:...">...</a>`.
2. Nested blockquote closer — Markdown.pl emits `<p></blockquote></p>` (a malformed quirk); Shakedown emits a bare closing tag at the correct nesting level.

**Two blockers that stalled the project:**

### Blocker 1 — Act-boundary goto constraint

SPL gotos (`let us return/proceed to scene N`) cannot cross act boundaries. The design spec envisioned Acts I–IV as phases (read, block scan, inline, emit), but the streaming `read → classify → handle → read` loop requires a backwards jump after each block handler — which forces the entire pipeline into one Act. Act I grew to ~130 scenes and ~4300 lines.

Three options were laid out in `shakedown-2026-04-10-spl-act-architecture.md`:
- **A.** Keep single act, sub-dispatch inline per block handler (more duplication, no rewrite)
- **B.** Multi-pass rewrite with Act I emitting a token stream, Act II processing it (correct SPL structure but effectively a rewrite of Slice 1, slower on the machine)
- **C.** Consolidate duplicated patterns first, then Option A (pragmatic path, recommended but never executed)

The last commit on the SPL branch was this decision doc. No decision was made.

### Blocker 2 — Interpreter performance

The `shakespearelang` interpreter on the Lightsail instance:
- Empty-input run: 17–26 seconds (the startup cost alone)
- Blockquote sample runs: ~1 minute each
- Full `pytest tests/test_blockquotes.py`: 324 seconds for 17 tests

This defeated the Huntley tight-loop methodology. Mitigations tried (documented in `shakedown-2026-04-09-slow-machine-spl-workflow.md`):
- `scripts/spl-smoke` wrapper for single-shot smoke tests without pytest overhead
- Two-machine workflow: slow machine for editing, fast machine for milestone verification, sync via pushed branches
- Worktree layout at `.worktrees/spl-slice-1`
- Single-test pytest invocations instead of broad runs

None of these removed the interpreter startup cost. The feedback loop for an automated agent was too slow to be practical.

---

## Key SPL language facts (condensed from `shakedown-spl-reference.md`)

- Single `.spl` file; no imports
- Dramatis personae with integer values and per-character stacks (`Remember`, `Recall`)
- Exactly 2 characters on stage for second-person pronoun arithmetic
- Numbers encoded as noun phrases: positive noun + N adjectives = +2^N; negative noun = −2^N; `nothing`/`zero` = 0
- Stdin: `Open your mind!` reads one byte (-1 on EOF, via `a pig`)
- Stdout: `Speak your mind!` prints `chr(listener_value)`; `Open your heart!` prints as integer
- Control flow: one global boolean updated by every question; `If so,` / `If not,` uses it; gotos restricted to current act
- Integer only; no floats
- No randomness primitive (blocks Markdown.pl's email autolink obfuscation)
- Interpreter: `shakespearelang` via `shakespeare run play.spl`

---

## What a Markdown.pl-only target needs (per original design)

From `docs/superpowers/specs/2026-04-05-shakedown-spl-design.md`:

**Slice 1 (block structure) — DONE in prior attempt:**
Paragraphs, ATX headings, setext headings, horizontal rules, indented code blocks, blockquotes.

**Slice 2 (inline spans) — NOT ATTEMPTED:**
`&`/`<` encoding, backslash escapes, code spans, emphasis/strong, autolinks, inline links, reference links, inline images, reference images.

**Slice 3 (lists and HTML blocks) — NOT ATTEMPTED:**
Unordered and ordered lists (tight/loose, nested); raw HTML block pass-through.

Test surface: 23 `Markdown.mdtest` fixtures + ~200 pytest cases across 14 modules in the deleted `tests/`. Two divergences documented above reduce achievable pass rate.

---

## What this feasibility study should look like (proposed by analogy with quackdown-cm)

The CommonMark feasibility study ran four experiments — each one a self-contained SQL file stress-testing a known technical unknown — and produced a written verdict per experiment plus a summary with an estimated pass-rate ceiling. The four unknowns were:
1. RE2 without lookaround for flanking rules
2. Recursive CTE as emphasis delimiter stack
3. (further experiments — see the design spec)
4. (ditto)

The SPL equivalent would target **SPL-specific** unknowns, with the Markdown.pl feature set (not CommonMark) as the target behavioural surface. Candidate experiments to scope during brainstorming:

1. **Interpreter startup cost baseline** — is there any combination of interpreter flag, language choice (alternate SPL implementations?), or machine that brings empty-input runtime under, say, 2s? If no, the Huntley loop is simply not viable for SPL on available hardware.
2. **Inline pass architecture** — can a single-act Slice 1 design be extended with inline scans that don't duplicate scene logic per block handler? I.e., test Option C from the April 10 decision doc as a small prototype before committing.
3. **List parsing feasibility** — lists are the most structurally complex Markdown.pl feature (tight/loose detection, nesting, interaction with other blocks). Does SPL's stack model support the lookahead needed?
4. **Divergence catalogue** — enumerate every Markdown.pl behaviour that depends on a primitive SPL lacks (randomness for email autolinks; possibly regex; string manipulation). Decide up-front which divergences are acceptable.

These are suggestions — actual experiment scope is what brainstorming should produce.

---

## Session state at time of snapshot

### Task list (superpowers TaskCreate)

1. **Explore project context** — completed
2. **Ask clarifying questions** — in progress
3. **Propose 2-3 approaches** — pending
4. **Present design sections** — pending
5. **Write design doc and user review** — pending

### Open clarifying question (just asked the user)

> What outcome are you after?
>
> - **A.** Rigorous, decision-grade feasibility study — real SPL experiments, verdicts, evidence-based answer.
> - **B.** Retrospective feasibility study — written from current knowledge and git history, no new SPL code.
> - **C.** Narrow feasibility targeting only the two known blockers (act-boundary goto, interpreter speed) — design and run the pre-flight checks that would have caught them before 4300 lines.

Awaiting user answer. After the answer, propose 2–3 approaches and iterate.

### Assumptions already baked in

- Target is Markdown.pl v1.0.1, not CommonMark.
- Same 23 `Markdown.mdtest` fixtures as the oracle surface.
- Previous divergences (email autolink, nested blockquote quirk) are acceptable starting points.
- The final deliverable of the feasibility study itself is a design doc in `docs/superpowers/specs/` plus experiment artifacts in a new directory (probably `experiments-spl/`), ending in a summary with PASS/PARTIAL/BLOCKED verdicts and a go/no-go recommendation. This is NOT yet a commitment to actually implement shakedown-from-scratch; it's a study of whether doing so would be viable.

### Important procedural rules for the resuming session

- The `brainstorming` skill forbids writing code or scaffolding until a design has been presented and approved.
- Commits in this repo follow conventional commits (`.githooks/commit-msg`). `docs:` for this context file.
- The design doc, when written, should go to `docs/superpowers/specs/YYYY-MM-DD-shakedown-spl-feasibility-design.md` and be committed before moving to plans.
- Terminal next skill after brainstorming is `writing-plans` — no other implementation skills.

---

## Files to re-read on resumption (in priority order)

1. This file.
2. `docs/project-history.md` — narrative context.
3. `docs/shakedown-2026-04-10-spl-act-architecture.md` — the unresolved decision.
4. `docs/shakedown-spl-reference.md` — language reference for scoping experiments.
5. `docs/superpowers/specs/2026-04-12-commonmark-feasibility-design.md` — the structural template this study should mirror.
6. `docs/superpowers/specs/2026-04-05-shakedown-spl-design.md` — prior approved SPL design.
7. `git show 9e6c04f^:shakedown.spl | head -400` — taste of the prior implementation shape.

---

## Entry point to resume

After re-reading this file and at least items 2–5 above, respond to the user's answer to the three-option question. Then continue the brainstorming flow from step 3 (propose approaches).
