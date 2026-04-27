# Shakedown Architecture — Design

**Date:** 2026-04-26
**Status:** Draft for review
**Author pairing:** interactive Claude session (superpowers:brainstorming workflow)

## Context

The pre-architecture hardening pass (`docs/superpowers/specs/2026-04-24-pre-architecture-hardening-design.md`) closed roughly 14 gaps in the docs set so that an architecture-planning session could reason from measurement rather than inference. This spec is the architecture itself: the load-bearing decisions about how `shakedown.spl` is structured, how the Markdown pipeline maps onto SPL, how state is partitioned across characters, and how the literary work and the computational work reinforce each other rather than fighting.

The architecture is the consolidated output of a brainstorming dialogue that ran across two sessions. It locks in eight major decisions, four pieces of literary architecture, a verification strategy, and an implementation order with two architecture-validation spikes. Reasoning is recorded section-by-section so future contributors (and future Claude sessions) can see *why* each decision was made, not just what was chosen.

## Goals

1. **Pass the 23-fixture mdtest suite** by-fixture against the Markdown.pl oracle, with intentional divergences explicitly documented in `docs/markdown/divergences.md`.
2. **`shakedown.spl` is the art object.** SPL owns Markdown semantics. Anything outside the SPL is plumbing.
3. **Make `shakedown.spl` a fun art artefact** — literary richness is a primary project goal alongside correctness, not garnish. Tradeoffs that pull between utility and aesthetic richness should surface aesthetic considerations explicitly.
4. **Avoid the prior attempt's stall.** The prior 4,300-line single-act dispatcher hit duplicated-pattern pressure (5×-copied dispatch prefixes, 44%-of-file blockquote machinery) and stalled on block-only. The architecture must give each piece of work a clear home so duplication doesn't compound.
5. **Keep the Huntley/Ralph loop snappy.** Fixture-by-fixture verification is the rubric's primary correctness gate; if a contract run takes minutes, the loop loses its character.

## Non-goals

- This spec does not require a separate cast-bible document. Specific Shakespeare-character picks and voice policy are now captured in `docs/spl/literary-spec.md`; concrete surface tables belong in the future `src/literary.toml`, written before Slice 1 begins.
- This spec does not produce the implementation plan. That is the next skill's output (`superpowers:writing-plans`).
- This spec does not produce the run-loop prompt. That is an output of the writing-plans phase, not architecture.
- This spec does not modify `shakedown.spl`, `src/*.spl`, or any production code path. Those are implementation work.
- This spec does not re-open the Markdown.pl parity target or the divergence list.

## Decision Summary

| # | Decision | Locked |
|---|---|---|
| D1 | Runtime: dev-time Python wrapper with AST cache; release-time bash-only entry | yes |
| D2 | Source: hand-written SPL fragments + assembler + scoped codegen for forced-byte HTML literals only | yes |
| D3 | Internal pipeline: four acts (Pre-process / Block / Span / Emit) | yes |
| D4 | Dispatcher shape: multi-pass token-stream | yes |
| D5 | AST cache: dev-mode only, removed at release | yes |
| D6 | Cast: ~9 themed Shakespeare characters across the canon, single-responsibility per character | yes |
| D7 | Per-act aesthetic palette + literary surface tables written before Slice 1 | yes |
| D8 | Implementation order: Slice 1 (Amps) → Spike A (lists) → Spike B (nested blockquote-in-list) → Slices 2-5 risk-ascending | yes |

Each decision is detailed in its own section below, with reasoning preserved.

---

## Section 1 — Runtime Boundary and Art Object

### Decision

**`shakedown.spl` is a single, hand-curated SPL file** — the art object. **`./shakedown` is a thin wrapper** that does only plumbing.

**During development:** `./shakedown` is a Python wrapper (`scripts/shakedown_run.py`) that reads stdin, hashes `shakedown.spl`, loads or builds an AST cache (Section 5), invokes `shakespearelang`'s runtime, passes stdout/stderr/exit through.

**At release (pre-`1.0.0`):** `./shakedown` is a bash entry that resolves the SPL interpreter through the project's `uv`-managed environment and invokes it on the committed `shakedown.spl`. No wrapper-side Python *logic*. (Full wrapper shown in §5.1.)

### Plumbing-only constraint (binding)

The wrapper performs **no Markdown work**. No tokenizing, no normalization beyond what stdin transport requires, no HTML emission, no fixture-specific branches. If a feature requires logic, that logic lives in SPL. Wrapper line budget during development: ≤100 lines of Python total.

### Reasoning

- **Direct SPL** pays cold-start cost on every run with no cache opportunity (B14 measured ~13.3s for a 4k-line SPL file).
- **Generated SPL** puts the art object behind a code generator and weakens the "SPL owns Markdown" claim from the rubric.
- **Wrapper-assisted SPL** lets the SPL stay hand-curated and readable, lets us cache the parse, and keeps the rubric's SPL-ownership axis clean.
- A single `shakedown.spl` over runtime-loaded fragments: SPL has no import mechanism, the rubric values the art object, and assembly happens at build time anyway.

---

## Section 2 — Source Layout and Assembly

### Decision

Hand-written SPL fragments are the source of truth. They live under `src/`, are committed, and are what humans read and edit. The assembled `shakedown.spl` is generated output — checked in for inspection and CI, but never hand-edited.

```
src/
  00-preamble.spl         # dramatis personae + Act I header
  10-act1-preprocess.spl  # normalize, append \n\n, detab, strip whitespace-only lines, hash HTML blocks, strip link defs
  20-act2-block.spl       # block parse → token stream
  30-act3-span.spl        # span substitution over tokens
  40-act4-emit.spl        # emit HTML
  manifest.toml           # ordered fragment list

scripts/
  assemble.py             # concat + resolve symbolic scene labels → Roman numerals
  codegen_html.py         # narrow codegen for forced-byte HTML literals only
  shakedown_run.py        # dev wrapper (until release transition)
```

### Assembly does two things

1. Concatenate fragments in manifest order.
2. Resolve symbolic scene labels (e.g. `@scene:dispatch_block`) to act-local Roman numerals so cross-scene gotos within an act stay readable in source.

### Codegen is scoped, not pervasive

`scripts/codegen_html.py` produces only the **forced-byte HTML literals** required for HTML output (the exact ASCII codes for `<p>`, `</p>`, `<em>`, `&amp;`, etc.) following `docs/spl/codegen-style-guide.md`. Everything else — control flow, state machines, dispatch, character roles — is hand-written. Codegen output is plain by policy because it's parsing utility, not literary register.

### Reasoning

- **Fragments over a single hand-edited file:** the prior attempt's single-file approach hit ~4,300 lines on block-only and stalled under duplicated-pattern pressure. Fragments let each act stay in working memory.
- **Build-time assembler over runtime composition:** SPL has no import mechanism, and the art object must be a single legal SPL program.
- **Scoped codegen over full codegen:** full codegen makes the SPL a build artifact rather than a hand-curated work. Forced-byte literals are the one place where humans don't add expressive value, so we delegate them.

---

## Section 3 — Literary Architecture

This section codifies how we make `shakedown.spl` read as a coherent work of literature, not as code that happens to compile under SPL. Without these commitments, the literary quality won't happen by accident.

### 3.1 Literary Spec And Surfaces (committed policy, data written before production SPL)

`docs/spl/literary-spec.md` specifies for each named character:

- The Shakespeare play they are drawn from.
- Their canonical dramatic register (e.g. courtly, grotesque, pastoral, mercantile).
- Their role in `shakedown` (which act, what computational responsibility).
- Why that play-character pairing makes sense for that responsibility.
- The lexicon palette they typically draw from.

The future `src/literary.toml` file supplies the hand-authored surfaces that codegen may select:
per-character Stable Utility phrases, soft-variation pools, Recall pools, scene titles, iconic
moments, and short character blurbs.

**Reasoning:** A character's voice has to be predictable for the work to feel coherent. Without a fixed reference, by the time we're writing Act III we will have forgotten the register we used for the same character in Act II, and lines will drift toward generic-Shakespearean-sounding-text. The literary spec is the reviewable policy; `src/literary.toml` is the operational handle. If a generated speech feels off, the question is "does this match the spec and the curated surface table for this character," not "does this sound vaguely Shakespearean."

### 3.2 Cross-Canon, Not Single-Play

Characters are drawn from across the Shakespeare canon, not from a single play.

**Reasoning:** A single-play cast (e.g., everyone from *Hamlet*) would force assignments that violate canonical voice — *Hamlet* has no character whose canonical register is "delicate ornament," and forcing Polonius or Horatio into that role would defeat the purpose of using named Shakespeare characters at all. Cross-canon casting lets us select voices on register fit:

- **Witches from *Macbeth*** for the grimy parsing/normalization work — incantatory, grotesque, mechanical.
- **Prospero from *The Tempest*** for the emitter — formal, declarative, ceremonial.
- **Beatrice and Benedick from *Much Ado About Nothing*** for span substitution — wit and wordplay are their canonical mode.
- **A herald or messenger figure** for dispatch — announce-and-route.

These are illustrative; specific final picks are governed by `docs/spl/literary-spec.md`. The architectural commitment is the principle: voice fit > play-of-origin tidiness.

**Trade-off accepted:** the work won't read as a coherent retelling of any one play. It reads as a Shakespeare-canon ensemble cast, not as one play.

### 3.3 Per-Act Aesthetic Palette

Each of the four acts has a designated literary palette governed by `docs/spl/literary-spec.md`
and selected from the legal vocabulary inventory in `docs/spl/style-lexicon.md`.

| Act | Purpose | Palette | Register |
|---|---|---|---|
| I — Pre-process | Normalize, detab, hash HTML blocks, strip link defs (Markdown.pl setup order — see §4.1) | Grotesque/Abusive | Grimy mechanical work; the underworld of the pipeline |
| II — Block | Block parse → token stream | Martial/Catastrophic | Structural recognition; decisive cuts |
| III — Span | Span substitution over tokens | Pastoral/Natural | Fine ornament; delicate substitution |
| IV — Emit | Emit HTML | Noble/Radiant | Ceremonial completion; pronouncements |

**Reasoning:** Without per-act palettes, lexicon choice becomes decorative — applied unevenly, with no logic the reader can follow. Per-act palettes let the reader (and any future contributor) predict the register of any new line: *"this is Act II, so this should sound noble/martial; if it sounds pastoral, something's off."* This pairs naturally with the literary spec and the curated `src/literary.toml` tables.

**Trade-off accepted:** characters whose canonical register doesn't match their act's palette can't appear in that act.

### 3.4 What Still Waits for Implementation

- Concrete `src/literary.toml` surfaces for each implementation slice.
- Scene-by-scene aesthetic choices (which adjectives, which similes).
- Monologue-level language.
- Cross-act thematic resonances or callbacks (if any).

### 3.5 What We Are Explicitly *Not* Committing To

- A unifying narrative arc across the four acts. The technical structure is load-bearing and the literary structure must accommodate it, not the reverse.
- A consistent meter across the work. SPL doesn't enforce meter; pursuing iambic pentameter would impose costs the rubric's runtime-cost axis can't justify.
- A scene-as-dramatic-unit-with-arc requirement. Some scenes are computationally trivial; demanding rising-action structure would distort their shape.

### 3.6 Where This Lives in the Repo

- `docs/spl/literary-spec.md` — adopted literary policy.
- `src/literary.toml` — future hand-authored surface data, created before Slice 1.
- This architecture spec records why those commitments are load-bearing.

### 3.7 How We Avoid Mechanical Monotony ("big big cat")

SPL expresses integers as a noun (sign) modified by adjectives (each adjective doubles magnitude). Values like 60 (`<`'s ASCII code) need long doubling chains plus arithmetic. That's mechanical and unavoidable for the value itself. Variation is bought everywhere *around* the chain.

**Five tactics, taken together:**

1. **Mechanical chaining is confined to forced-byte HTML literals — codegen only.** Quarantined to Act IV's emit scenes, governed by codegen-style-guide's *Critical* rule (one canonical phrase per byte). They look uniform on purpose — searchable, diffable, auditable. The rest of the SPL never produces them by hand.
2. **Stable Utility families for common test values.** Values that recur constantly (1, 0, −1, small token codes) each get a small approved family of surface forms, per act and per character. Value 1 in Act I (witches, grotesque palette): `a wretched toad`, `a meager scrap`, `a mangled hare`. Value 1 in Act III (wit pair, pastoral palette): `a tender kiss`, `a fair flower`, `a quiet sigh`.
3. **Per-act palette × character voice double up.** Per-act palette and per-character voice register stack on each other. The same operation has different vocabulary depending on which character speaks it in which act.
4. **Most of the SPL is not numeric expressions.** Scene titles, enter/exit/exeunt, gotos, question/branch flow, stack operations, comments — all non-numeric. The full lexicon lives here.
5. **We design the token codes, not inherit them.** Token vocabulary (`PARA`, `HEADER`, `HR`, `LIST_OPEN`, etc.) is *our* numeric design. We choose values 1, 2, 3, 4, 5 — short, single-noun-or-one-adjective-and-noun expressions in Stable Utility territory.

**What we accept:** Act IV's emit scenes will look mechanical because forced-byte literals look mechanical. We treat them as the "underclothing" of the work — structurally necessary, visually uniform, deliberately drab.

---

## Section 4 — Internal Pipeline: Four-Act Dispatcher

`shakedown.spl` is structured as four acts. Each act runs to completion before the next begins. State crosses act boundaries via per-character stacks (SPL retains values when characters are off-stage).

### 4.1 Act I — Pre-process

**Input:** raw Markdown source.
**Output:** normalized text + reference-definition table on the Librarian's stack + raw HTML hash table on the Custodian's stack.

**Responsibilities (in Markdown.pl order — see `docs/markdown/oracle-mechanics.md` row 1):**

1. Normalize line endings (`\r\n` and `\r` → `\n`).
2. Append `\n\n` to the end of input. (Oracle setup; affects EOF-sensitive boundary fixtures.)
3. Detab (tabs → 4 spaces, column-aware).
4. Strip whitespace-only lines (replace runs of whitespace-only lines with bare `\n`s; oracle setup).
5. Hash raw HTML blocks (replace with sentinel tokens, store originals on the Custodian's stack). **This precedes link-def stripping** because HTML blocks may contain reference-definition-shaped text that must not be rewritten.
6. Strip link reference definitions (`[id]: url "title"`) and capture them as `(id, url, title)` triples on the Librarian's stack.

**Mechanic:** linear scan, line-at-a-time state machine. No nested-structure recognition yet.

**Why pre-process is its own act:** Markdown.pl's transform order is non-negotiable here — HTML block hashing must precede link-def stripping, both must precede the block gamut, and the oracle's setup steps (append, strip-whitespace-only-lines) affect blank-line-sensitive fixtures. Putting these as Act I scenes makes that ordering structural rather than convention.

### 4.2 Act II — Block Parse

**Input:** normalized text.
**Output:** ordered token stream representing block structure.

**Token vocabulary (initial; grows with fixtures):**
- `PARA(text)`, `HEADER(level, text)`, `HR`
- `LIST_OPEN(kind)`, `LIST_ITEM(text)`, `LIST_CLOSE`
- `BLOCKQUOTE_OPEN`, `BLOCKQUOTE_CLOSE`
- `CODE_BLOCK(text)`
- `RAW_HTML_HASH(id)` (resolved in Act IV)

**Mechanic:** **multi-pass token-stream dispatcher.** Each pass recognizes one block class. Pass order matches Markdown.pl's `_RunBlockGamut` (see `docs/markdown/oracle-mechanics.md` Block Pipeline):

1. Pass A: Headers — Setext (`===` / `---` underlines) before ATX (`#` prefixes). **Headers run first** so setext underlines are recognized as headers before any other pass can consume them.
2. Pass B: Horizontal rules — `***`, `---`, `___` (with optional spaces, up to two leading spaces). Runs *after* headers so setext `---` underlines are not misread as rules.
3. Pass C: Lists — ordered + unordered, with nesting; tight/loose handled per `_ProcessListItems` mechanics (loose items recurse through the block gamut, tight items run only the span gamut). **Lists run before code blocks** so indented content inside list items isn't pulled out as a code block.
4. Pass D: Code blocks — 4-space indent (Markdown.pl is indent-only).
5. Pass E: Blockquotes — strip one `>` level, recurse through the block gamut on the unquoted body, then prefix two spaces and strip those from embedded `<pre>` (the indent fix is parity-critical per oracle-mechanics.md row 6).
6. Pass F: Second `_HashHTMLBlocks` pass — Markdown.pl re-hashes any block-level HTML produced by recursion before paragraph formation (see `docs/markdown/html-block-boundaries.md:8-10`). The Custodian's stack receives any new entries.
7. Pass G: Paragraph formation — unhashed chunks become `PARA` tokens; previously hashed HTML blocks are restored without paragraph wrapping in Act IV.

**Why multi-pass:** the prior attempt's single-pass dispatcher hit ~4,300 lines on block-only and stalled because every dispatch site duplicated the same recognition prefix. Multi-pass narrows each scene's recognition responsibility and lets the inter-pass token stream act as a contract.

**Frame-sentinel nesting** (B16) handles nested lists and blockquotes: each open emits a frame sentinel onto the structural-helper character's stack; close pops back to the matching sentinel.

### 4.3 Act III — Span Substitution

**Input:** Act II's token stream.
**Output:** transformed token stream with span structure resolved.

**Responsibilities (in Markdown.pl order — see `docs/markdown/oracle-mechanics.md`):**

1. Code spans (greedy backtick matching).
2. Backslash escapes.
3. Images (`![alt](url)` and reference form).
4. Anchors (`[text](url)` and reference form, using Act I's ref table).
5. Autolinks (`<http://...>` and `<email>`).
6. Ampersand and angle-bracket encoding.
7. Italics and bold (strong-then-emphasis substitution order — B15).
8. Hard line breaks (two-space-end-of-line → `<br />`).

**Mechanic:** for each token in the stream, if it carries text content, apply the span gamut. Code blocks and raw HTML hashes are left alone.

**Why span is its own act:** span work runs uniformly over block tokens; separating it from Act II eliminates the per-block-type span-code duplication that hurt the prior attempt.

### 4.4 Act IV — Emit

**Input:** Act III's transformed token stream + Act I's HTML-block hash table.
**Output:** HTML to stdout.

**Responsibilities:**
- For each token, emit the corresponding HTML.
- Resolve `RAW_HTML_HASH(id)` tokens by looking up the original HTML and emitting it verbatim.
- Apply Markdown.pl's final unescape pass.

**Mechanic:** linear walk over the token stream. The only act that calls SPL's character-output verbs in production work.

**Forced-byte HTML literals are codegen output** (Section 2). Every `<p>`, `</p>`, `<em>`, `&amp;` is emitted by codegen-named scenes; the surrounding control flow is hand-written in the Act IV palette.

### 4.5 Why Four Acts

- **Three acts** (read-block-inline, the prior attempt's shape) collapses pre-processing into block parse and span substitution into emission — recreating the cross-cutting tangle that stalled the prior attempt.
- **Five+ acts** pays act-boundary plumbing costs (state must transit per-character stacks at every boundary) for marginal clarity gains.
- **Four acts** is the smallest split that gives each major Markdown.pl phase its own home and each act a defensible aesthetic register.

### 4.6 What Crosses Act Boundaries

- **Reference table** (Act I → Act III): Librarian's stack.
- **HTML hash table** (Act I → Act IV): Custodian's stack.
- **Token stream** (Act II → Act III → Act IV): Dispatcher's stack. Two-stack reverse pattern (B-confirmed) at each handover restores stream order.

---

## Section 5 — Dev-Time AST Cache, Removed at Release

### 5.1 Two Modes, One Art Object

`shakedown.spl` is the same file in both modes; the interface is the same; only the wrapper changes.

**Dev mode:** Python wrapper → SHA-256 the SPL → look up `.cache/shakedown-<hash>.pickle` → on hit unpickle the AST and run; on miss parse via `shakespearelang`, pickle the AST, run.

**Release mode (pre-`1.0.0`):** bash entry that resolves the SPL interpreter via the project's declared tooling (`uv`) and invokes it on the committed `shakedown.spl`:

```bash
#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
exec uv run --directory "$DIR" shakespeare run "$DIR/shakedown.spl"
```

This resolves `shakespeare` through the project's `uv`-managed environment rather than ambient `PATH`, because CLAUDE.md explicitly notes `~/.local/bin/shakespeare` may not be on PATH in a fresh shell. The prototype's `./shakedown-dev` already uses this approach for the same reason. No wrapper-side Python *logic*, no cache, ~10 lines.

### 5.2 Why Both

- **Dev needs fast feedback.** Pre-cache cold cost (B14): ~13s for a 4k-line SPL file. 23 fixtures × 13s ≈ 5 minutes per contract run. The Huntley/Ralph loop loses its character at that pace. The cache reduces this to ~ms per run.
- **Release wants a clean story.** When the work is presented as a finished SPL Markdown port, the entry point should hand control directly to the SPL interpreter without wrapper-side Markdown or parse-acceleration logic. (Python is still the runtime substrate of `shakespearelang` itself; we accept that, because we don't *write* Python at release.)
- **Compatible because the cache is Markdown-blind.** The wrapper hashes the SPL, caches the parse, and hands the AST to `shakespearelang`. It never inspects stdin or stdout. Cache and bash entry produce byte-identical HTML for any input.

### 5.3 Mechanics (Dev Wrapper)

The dev wrapper's per-invocation flow:

1. **Assemble.** Run `scripts/assemble.py` to refresh `shakedown.spl` from `src/*.spl`. Assembly is fast (concat + label resolution); doing it on every invocation guarantees the cache key reflects current fragment state without developers remembering to assemble.
2. **Hash.** SHA-256 the resulting `shakedown.spl`.
3. **Cache lookup.** Read `.cache/shakedown-<hash>.pickle` if present.
4. **Hit:** unpickle the AST and execute. **Miss:** parse `shakedown.spl` via `shakespearelang`, pickle the AST, then execute.
5. **Pass through** stdout, stderr, and exit code.

Other mechanics:

- **Cache shape:** `pickle.dumps()` of the `shakespearelang`-produced AST.
- **Cache location:** `.cache/shakedown-<hash>.pickle`, gitignored.
- **Cache safety:** local-only. Pickle's untrusted-input fragility doesn't apply.
- **Pinning:** `shakespearelang` is pinned in `pyproject.toml`; AST shape changes only on intentional version bumps.
- **Wrapper line budget:** ≤100 lines of Python during development.

### 5.3a `shakedown.spl` Is Committed

`shakedown.spl` is tracked in git (not gitignored), because the release-mode bash entry runs it directly with no assembly step. CI runs `assemble.py` and verifies the committed `shakedown.spl` matches the assembled output; a mismatch fails the build. A pre-commit hook may enforce the same locally. This keeps the art object always in a publishable state without requiring Python at release.

### 5.4 Release Transition (pre-`1.0.0`)

1. Run the full 23-fixture contract under the bash-only wrapper at least once. Confirm output is byte-identical to dev-mode output.
2. Replace `./shakedown` with the bash entry.
3. Move the dev wrapper (the Python `shakedown_run.py`) to `scripts/dev/shakedown-dev`. This **replaces** the inherited prototype's `./shakedown-dev` bash wrapper, which is obsolete by then — the new dev wrapper subsumes its responsibilities.
4. Cut `1.0.0` with the bash-only entry as the published interface.

The transition must happen *before* `1.0.0`, not after.

### 5.5 Performance Expectation

- **Dev mode, post-warm:** Python startup + unpickle + execute. Predicted single-digit ms unpickle on our AST size; few hundred ms total per fixture.
- **Dev mode, cold (cache miss):** ~13s per representative SPL. One-time per SPL edit.
- **Release mode:** ~13s per fixture. Acceptable because release-mode runs are ceremonial.

**B19 (new):** measure dev-mode unpickle + execute time on a representative `shakedown.spl` ≥ 2k lines once the wrapper exists. Threshold: ≤100ms wrapper overhead.

---

## Section 6 — State Carrier Model

SPL has no variables: each character has one integer "value" and one stack of integers, plus one global boolean (most-recent question result). Every piece of program state is partitioned across characters. **Cast design is data-structure design.**

### 6.1 Cross-Act State Holders (3 characters)

**The Librarian — reference table.**
- Built up in Act I; consulted in Act III.
- Stack: serialized `(id, url, title)` triples with sentinel separators.
- Voice: archival, scholarly. Neutral palette in Act I; pastoral in Act III when paired with the wit pair.

**The Custodian — raw HTML block hash table.**
- Built up in Act I; consulted in Act IV.
- Stack: serialized `(id, html_bytes)` pairs.
- Voice: caretaker, formal. Aligns with Act IV's formal/declarative palette.

**The Dispatcher — token stream.**
- Built in Act II; transformed in Act III; consumed in Act IV.
- The "spine" character of the work.
- Stack: tokens as integer codes with optional payloads.
- Voice: martial in Act II; measured in Act III; ceremonial in Act IV.

### 6.2 Per-Act Workers (5 characters)

- **The Pre-processor (Act I).** Line-end normalize, append `\n\n`, detab, strip whitespace-only lines, HTML-block hashing, link-def detection — in Markdown.pl order (see §4.1). Stack as line buffer. Grotesque/catastrophic palette. Witches-from-*Macbeth* territory.
- **The Block-shaper (Act II).** Runs the block-recognition passes. Stack as region buffer. Noble/martial palette.
- **The Wit Pair (Act III, two characters).** Span substitution. One pushes candidate substitutions; the other commits final tokens. The two-character pairing enables the strong-then-emphasis mechanic (B15) cleanly. Pastoral/celestial palette. Beatrice-and-Benedick canonical model.
- **The Emitter (Act IV).** Walks the Dispatcher's token stream, speaks HTML to stdout. The only character who calls SPL's output verbs in production work. Formal/declarative palette. Prospero-from-*Tempest* territory.

### 6.3 Helper: Structural Helper (1 character)

Holds the open-block sentinel stack in Act II for frame-sentinel nesting (B16). Serves as reverse-stack partner during act handovers.

**Recommendation:** dedicated character, not folded into a worker. Single responsibility is clear; folding risks state collisions.

### 6.4 Cast Total

**9 characters:** 3 cross-act state holders + 5 per-act workers + 1 structural helper. Slightly over the original ~6-8 estimate but is what the partitioning naturally produces. Folding the Structural Helper into the Pre-processor would compress to 8 at the cost of single-responsibility clarity; we lean toward the cleaner 9.

### 6.5 The One-Global-Boolean Implication

SPL has a single global boolean: most-recent question result. Every scene that asks a question must consume the result before another question is asked. **Discipline:** scenes ask one question, branch immediately, complete the consequence before any further question. Block-recognition passes in Act II are the most question-dense; their scene structure is constrained by this rule.

### 6.6 What This Section Does *Not* Decide

- Concrete `src/literary.toml` surface assignments for each role.
- Exact encoding details for ref table, hash table, token stream stacks (implementation choices made when each act is written; the design commits to *which character holds the stack*, not exactly how triples are interleaved).
- Whether the Lyrical Pair need additional implementation-time surface overrides beyond `docs/spl/literary-spec.md`.

---

## Section 7 — Implementation Order

### 7.1 Pre-Implementation Deliverables (before Slice 1)

1. `src/literary.toml` schema and initial Slice 1 entries, following `docs/spl/literary-spec.md`.
2. Stable Utility families for 1, 0, −1, and small token codes selected from verified legal vocabulary.
3. **Token-code allocation table** — explicit assignments (e.g., `PARA = 1`, `HEADER = 2`, `LIST_OPEN = 3`, …) committed before any SPL references them.
4. Wrapper skeleton (`scripts/shakedown_run.py`) and assembler (`scripts/assemble.py`) usable but empty of content.
5. Codegen (`scripts/codegen_html.py`) with a unit test that verifies one byte literal round-trips.

### 7.2 Slice 1 — Amps and Angle Encoding

The first fixture. Narrow but walks all four acts.

**Delivers:**
- Wrapper (dev mode, with AST cache).
- Assembly tooling.
- HTML-byte codegen for `&amp;`, `&lt;`, `&gt;`, `<p>`, `</p>`.
- `src/00-preamble.spl` — dramatis personae and Act I header.
- `src/10-act1-preprocess.spl` — line-end normalize, append `\n\n`, detab, strip whitespace-only lines. *No link-def stripping yet, no HTML hashing yet — the Amps fixture has neither, and the order constraint between them only matters when both are present.*
- `src/20-act2-block.spl` — paragraph recognition only. *No headers, no lists, no blockquotes, no code blocks, no HR.*
- `src/30-act3-span.spl` — `&` / `<` / `>` encoding only. *No code spans, no escapes, no anchors, no images, no autolinks, no italics/bold.*
- `src/40-act4-emit.spl` — emit `<p>...</p>` with encoded text.

**Why this fixture first:** lowest-risk fixture in the suite that still requires the full four-act pipeline. Establishes architecture, build flow, the first `src/literary.toml` surfaces, and the dev wrapper, all on a fixture where Markdown.pl's behavior is straightforwardly machine-checkable.

**Definition of done:** `uv run pytest tests/test_mdtest.py -k "Amps and angle"` passes; output byte-identical to Markdown.pl; first ~6 characters have spoken lines that follow `docs/spl/literary-spec.md` and draw from checked-in `src/literary.toml` surfaces.

### 7.3 Spike A — Lists at Minimum Viable Scope

Immediately after Slice 1.

**Goal:** validate the multi-pass dispatcher and frame-sentinel nesting.

**Scope:** flat unordered list (3 items, bare paragraphs); flat ordered list (3 items); one nesting level (one ordered inside one unordered, or vice versa).

**Not in spike:** tight vs loose lists, list-with-paragraphs, list-with-blockquotes, list-with-code-blocks. Those wait for Slice 4.

**Outcomes:**
- ✅ Spike passes — frame-sentinel pattern confirmed at fixture-relevant scope.
- ❌ Spike struggles — revisit dispatcher shape *now*. Cost of pivot is bounded.

### 7.4 Spike B — Nested Blockquote-Inside-List at Minimum Viable Scope

Immediately after Spike A.

**Goal:** validate that two nesting structures compose.

**Scope:** a two-item list where one item contains a single-line blockquote; a two-line blockquote that contains one bullet item.

**Outcomes:** same shape as Spike A.

### 7.5 Slice 2 — Remaining Low-Risk Fixtures

After both spikes succeed.

**Fixtures:** Auto links (URL only), Backslash escapes, Code Spans, Tidyness, Tabs, Horizontal rules, Code Blocks. Order within slice: cheapest first.

**Done:** all 7 pass; no regression; spike fixtures still pass at spike scope.

### 7.6 Slice 3 — Medium-Risk Fixtures

Inline HTML (simpler variants); Links (inline then reference); Images (inline then reference); Strong and em together (uses B15); Blockquotes with code blocks. Features that share machinery cluster together.

### 7.7 Slice 4 — High-Risk Fixtures

Nested blockquotes (full fixture); Ordered and unordered lists (full fixture); any inline-HTML-ish that didn't make Slice 3. Spikes give a floor; this slice expands to full fixture scope.

### 7.8 Slice 5 — Documentation Aggregates

The three `Markdown Documentation - X` fixtures. Pull every feature together at scale. Run last because they reveal interactions, not capabilities.

### 7.9 Per-Slice Discipline

Every slice ends with: target fixture(s) passing; all prior fixtures still passing; commit per slice (or sub-fixture) following conventional-commits; version bump per CLAUDE.md (first fixture → 0.1.0; coherent group → minor; bug fix → patch).

---

## Section 8 — Verification Strategy

### 8.1 Per-Slice Verification Gates

Every slice and spike must clear all four:

1. **Fixture pass** — `uv run pytest tests/test_mdtest.py -k "<name>"` passes.
2. **Byte-identical to oracle** — output matches `perl ~/markdown/Markdown.pl < fixture.text` byte-for-byte. Any divergence is documented in `docs/markdown/divergences.md` *before* merge.
3. **No regression** — all prior slices' fixtures still pass.
4. **No oracle stub** — the SPL owns the work for that fixture. Bash-fallback-to-`Markdown.pl` is removed before Slice 1 cuts `0.1.0`.

The strict-oracle audit (`scripts/markdown_pl_parity_audit.py`) is the canonical comparison tool. Slice merges are blocked on a clean audit for claimed fixtures.

### 8.2 Architecture Validation Gates

Conditions under which we **halt and redesign:**

| Trigger | What it indicates | Action |
|---|---|---|
| Spike A fails | Multi-pass dispatcher needs revision | Revisit Section 4's pass decomposition |
| Spike B fails | Frame-sentinel composition needs revision | Revisit per-character stack partitioning |
| Slice 1 assembled `shakedown.spl` exceeds ~600 lines | Act granularity wrong; duplication pressure showing | Revisit four-act split |
| Dev-mode unpickle exceeds 100ms (B19) | Serialization choice needs revision | Investigate alternatives |
| Aesthetic drift detected in review | Lexicon use degrading toward "big big cat" | Re-anchor on `docs/spl/literary-spec.md` and `src/literary.toml`; merge blocker |

Halting is cheaper than continuing on a wrong floor. Spikes exist *because* halt-now-and-redesign is the right answer to architectural surprise.

### 8.3 Performance Verification

- **B19 (new):** dev-mode unpickle + execute on representative `shakedown.spl` ≥ 2k lines. Threshold: ≤100ms wrapper overhead.
- **B14 re-measurement:** before `1.0.0`, re-measure cold release-mode runtime on the final `shakedown.spl` against representative fixtures. Compare to `docs/performance/budget.md`.
- **Slice 5 budget check:** Documentation aggregates is the worst case; release-mode runtime there is the headline number for `1.0.0`.

### 8.4 Open Questions (deferred)

| Question | Where resolved |
|---|---|
| Concrete Slice 1 literary surfaces | `src/literary.toml` before Slice 1 |
| Stdin transport: temp file vs pipe | Slice 1 implementation step |
| Token encoding details | Slice 1 implementation; Spike A may force revision |
| Whether structural helper folds into another character | After Spike A — actual stack pressure known by then |
| Run-loop prompt content | Output of writing-plans, not architecture |
| Exact line-budgets per slice | Set during writing-plans |

### 8.5 Risks and Mitigations

- **Markdown.pl divergences accumulate silently.** *Mitigation:* every byte-divergence documented in `divergences.md` before merge; audit is a merge gate.
- **Aesthetic discipline drifts as implementation pressure mounts.** *Mitigation:* `docs/spl/literary-spec.md` is the reference policy, `src/literary.toml` is checked-in authored data, and lexicon use is a review axis.
- **A fixture requires Markdown.pl behavior we haven't seen.** *Mitigation:* `~/markdown/Markdown.pl` is ground truth; unexpected behavior is investigated against the binary, not against documentation.
- **A spike succeeds at minimum scope but fails at full fixture scope in Slice 4.** *Mitigation:* spikes establish a floor, not a ceiling; Slice 4 has its own design step.

### 8.6 What "Done" Looks Like for `1.0.0`

- All 23 mdtest fixtures either pass or are documented divergences.
- Strict-oracle audit clean for every claimed fixture.
- Release-mode wrapper in place; dev wrapper moved to `scripts/dev/`.
- `docs/spl/literary-spec.md` and `src/literary.toml` match the shipped SPL.
- Performance budget met for representative fixtures.
- `1.0.0` tag cut per CLAUDE.md's version policy.

---

## References

- `docs/architecture/decision-rubric.md` — optimization target and scoring questions.
- `docs/architecture/runtime-boundary.md` — runtime-boundary options canvassed.
- `docs/architecture/encoding-and-scope.md` — encoding and target-scope assumptions.
- `docs/architecture/inherited-scaffold.md` — prototype scaffold (kept where it serves; replaced where it doesn't).
- `docs/spl/reference.md` — SPL language reference.
- `docs/spl/codegen-style-guide.md` — Critical / Stable Utility / Incidental partition.
- `docs/spl/style-lexicon.md` — palette source.
- `docs/spl/literary-spec.md` — character voice, per-act palettes, decorative surfaces, and future `src/literary.toml` policy.
- `docs/markdown/oracle-mechanics.md` — Markdown.pl pipeline order.
- `docs/markdown/fixtures.md` — fixture risk matrix.
- `docs/performance/budget.md` — benchmark protocol and thresholds.
- `docs/verification-plan.md` — claim inventory (B-numbered probes).
- `docs/prior-attempt/architecture-lessons.md` — why the prior attempt stalled.
