# Docs Restructure Design

**Date:** 2026-04-17
**Status:** Proposed

## Purpose

Restructure the Shakedown documentation set so that a new agent starting architecture
planning has a comprehensive, current, accurate, and MECE reading list. The existing
`docs/research/` directory is a chronological pile of artifacts from an earlier attempt,
including stale workflow notes, a never-resolved decision memo, a mid-session resumption
snapshot, and a three-source chain of feasibility findings (summary-1 → corrections →
summary-2) that has to be reconciled by the reader.

The restructure is a prerequisite for the architecture planning work that follows. It is
not itself architecture work, and it does not commit to any implementation direction.

## Problem

Today the doc set has five concrete issues for an agent trying to plan architecture:

1. **Fragmented feasibility voice.** `feasibility-summary.md`, `feasibility-summary-2.md`,
   and `shakedown-spl-feasibility-assumption-corrections.md` together form one retrospective
   but must be read as three files with inline cross-refs and retractions. Round-1 claims
   are partly retracted; round-2 partly overcorrects; neither summary integrates the
   corrections.
2. **Evidence from a codebase that is not present.** The feasibility experiments describe
   runs on a 4,311-line `shakedown.spl` and a ~8,623-line projected port. This repository
   contains no `shakedown.spl`, no `scripts/spl-smoke`, and no `.worktrees/spl-slice-1`.
   Claims of the form "we measured X at Y lines" are evidence from a prior checkout, not
   facts about this repository.
3. **Stale workflow artifacts.** `slow-machine-spl-workflow.md` references deleted
   scripts and worktrees. `spl-act-architecture.md` is dated 2026-04-10 with status
   "decision pending" for a decision whose context no longer applies.
   `spl-feasibility-resumption-context.md` is a mid-brainstorming snapshot whose purpose
   was consumed.
4. **Predictions labeled as findings.** `shakedown-mdtest-fixture-matrix.md` assigns
   "likely pass" labels that assume the prior block-level implementation. With no
   implementation present, those labels are predictions for a fresh build, not assessments.
5. **No single verification inventory.** Individual claims have been probed
   (`2026-04-17-spl-reference-verification.md`), but the repo has no index that says, per
   claim, "this is verified against this repo / this is evidence from the prior attempt /
   this is a prediction / this is unchecked."

## Scope

In scope:

- consolidating, renaming, archiving, and rewriting files in `docs/` outside the
  `docs/superpowers/` tree
- writing a new `docs/README.md` index
- writing a new `docs/verification-plan.md` that inventories claims by status
- writing a new `docs/markdown/target.md` describing the Markdown.pl surface
- rewriting the fixture matrix as a predictive risk outlook for a fresh build
- consolidating the feasibility and architecture trails into single retrospectives
- updating `CLAUDE.md` paths to the new layout
- a small set of cheap verification replays (see `verification-plan.md` bucket B)

Out of scope:

- any change to `docs/superpowers/**` (specs and plans stay as-is)
- any substantive content change to `shakedown-spl-reference.md`,
  `shakedown-spl-style-lexicon.md`, or `shakedown-spl-codegen-style-guide.md` beyond
  cross-reference path updates and file renames
- executing the pending style-guide validation plan at
  `docs/superpowers/plans/2026-04-17-spl-style-guide-validation.md`
- writing the architecture design for Shakedown
- writing an implementation plan for Shakedown

## Goals

- Produce a MECE doc set organised by subject (SPL / Markdown.pl / prior-attempt /
  verification / history) so agents find material by what it is about.
- Separate living reference material from retrospective evidence from historical
  artifacts, so stale content cannot be mistaken for current guidance.
- Make every verification status explicit: what is probed in this repo, what was probed
  in a prior checkout, what is inferred from grammar, what is a prediction.
- Keep the three style docs content-stable; only rename files and fix broken
  cross-reference paths.
- Preserve all archived evidence in `docs/archive/` rather than deleting it.

## Non-Goals

- Making the docs shorter for brevity's sake.
- Deleting feasibility or architecture evidence.
- Re-running the full feasibility study.
- Modifying SPL reference / lexicon / codegen content.

## Target Structure

```
docs/
  README.md                         — index + how to use
  lineage.md                        — kept; edit only if drift found
  verification-plan.md              — new; claim inventory by bucket
  spl/
    reference.md                    — frozen content, renamed
    style-lexicon.md                — frozen content, renamed
    codegen-style-guide.md          — frozen content, renamed
    verification-evidence.md        — kept, renamed, cross-refs updated
    lexicon-sources.md              — kept, renamed, cross-refs updated
    probes/                         — moved from tmp-spl-probes/
  markdown/
    target.md                       — new; Markdown.pl surface in scope
    divergences.md                  — kept, renamed
    fixture-outlook.md              — rewritten from fixture-matrix.md
  prior-attempt/
    feasibility-lessons.md          — new; consolidates summary-1 + corrections + summary-2
    architecture-lessons.md         — new; consolidates memo + before-design + act-architecture
  archive/
    project-history.md              — moved
    slow-machine-spl-workflow.md    — moved
    spl-feasibility-resumption-context.md — moved
    prompt-shakedown.md             — moved; will be rewritten against new layout later
  superpowers/                      — untouched
    specs/
    plans/
```

## File-by-file Disposition

| Current path | Action | New path |
|---|---|---|
| `docs/lineage.md` | verify still accurate; edit only if drift found | `docs/lineage.md` |
| `docs/prompt-shakedown.md` | archive | `docs/archive/prompt-shakedown.md` |
| `docs/research/shakedown-spl-reference.md` | frozen content; rename; update its own cross-refs to `docs/spl/` paths | `docs/spl/reference.md` |
| `docs/research/shakedown-spl-style-lexicon.md` | frozen content; rename; update its own cross-refs | `docs/spl/style-lexicon.md` |
| `docs/research/shakedown-spl-codegen-style-guide.md` | frozen content; rename; update its own cross-refs | `docs/spl/codegen-style-guide.md` |
| `docs/research/2026-04-17-spl-reference-verification.md` | keep; rename | `docs/spl/verification-evidence.md` |
| `docs/research/2026-04-17-spl-style-lexicon-sources.md` | keep; rename | `docs/spl/lexicon-sources.md` |
| `docs/research/tmp-spl-probes/` | move; drop "tmp-" prefix | `docs/spl/probes/` |
| `docs/research/shakedown-divergences.md` | keep content; rename | `docs/markdown/divergences.md` |
| `docs/research/shakedown-mdtest-fixture-matrix.md` | rewrite as predictions | `docs/markdown/fixture-outlook.md` |
| — | new file | `docs/markdown/target.md` |
| `docs/research/feasibility-summary.md` + `feasibility-summary-2.md` + `shakedown-spl-feasibility-assumption-corrections.md` | consolidate | `docs/prior-attempt/feasibility-lessons.md` |
| `docs/research/shakedown-mdtest-architecture-memo.md` + `shakedown-before-design.md` + `spl-act-architecture.md` | consolidate | `docs/prior-attempt/architecture-lessons.md` |
| `docs/research/project-history.md` | archive | `docs/archive/project-history.md` |
| `docs/research/slow-machine-spl-workflow.md` | archive | `docs/archive/slow-machine-spl-workflow.md` |
| `docs/research/spl-feasibility-resumption-context.md` | archive | `docs/archive/spl-feasibility-resumption-context.md` |
| — | new file | `docs/verification-plan.md` |
| — | new file | `docs/README.md` |
| `docs/superpowers/**` | unchanged | unchanged |

After the moves, `docs/research/` should be empty and removed.

## Frozen-File Rule

The three style docs are "frozen" with one explicit exception:

- **Frozen:** body content, section structure, provenance labels, examples, tables, lists.
- **Not frozen:** inline cross-reference paths and filename-level identity, when the move
  breaks them. The replacement path has the same target; only the string changes.

No other edits. If during restructure a non-mechanical change looks warranted, raise it
as a question before making it.

## Consolidations

### `prior-attempt/feasibility-lessons.md`

Sources: `feasibility-summary.md`, `feasibility-summary-2.md`,
`shakedown-spl-feasibility-assumption-corrections.md`.

Shape:

1. **Context** — one paragraph: these experiments were run in a prior checkout against a
   4,311-line `shakedown.spl` (round 1) and an 8,623-line projected full port (round 2).
   Neither artifact is present in this repository.
2. **Experiment table** — all ten experiments (round 1: 1–5, round 2: 6–10) in one table
   with columns: number, name, verdict, key finding, **status in this repo**
   (e.g., "retrospective: depends on an artifact not present here", "replayable: cheap
   cold-start timing", "general SPL claim; covered by `spl/verification-evidence.md`").
3. **Corrected assumptions** — the three retractions from the corrections doc, integrated
   inline as the single voice (not as a separate retraction appendix).
4. **What transfers to this repo** — the shape of claims that remain useful for
   architecture planning (single-act dispatcher pressure, cached-AST feasibility idea,
   inline-vs-buffered pattern choices, list depth bounds, nested-block framing) without
   re-asserting specific numeric verdicts.
5. **What does not transfer** — line counts, specific timing verdicts, cast-pressure
   judgments, and anything that measured the now-absent implementation.

The "two characters on stage" wording in the sources is reconciled with the corrected
pronoun-rule framing from `spl/reference.md`.

### `prior-attempt/architecture-lessons.md`

Sources: `shakedown-mdtest-architecture-memo.md`, `shakedown-before-design.md`,
`spl-act-architecture.md`.

Shape:

1. **What the prior attempt tried** — single-act streaming dispatch; blockquote
   sub-machinery; ~4,300 lines across ~130 scenes.
2. **Act-boundary constraint** — why backwards gotos force one act; this is a real
   runtime property (confirmed in `spl/verification-evidence.md`).
3. **Duplicated pattern pressure** — before-block dispatch repeated ~5 times; content
   emission loops reimplemented per block type.
4. **The three April 2026-04-10 options (A/B/C)** — preserved verbatim as historical
   input, clearly marked as a decision surface the new architecture work can revisit,
   not a pending decision.
5. **The "before design" reminder** — carried forward, minus the "do not re-open SPL
   feasibility" line, which is stale because architecture planning in this repo is
   re-opening exactly that question.
6. **Items the prior memo left open** — build order across risky fixtures, block/inline
   integration boundaries, milestone sequencing.

## Verification Plan (what `docs/verification-plan.md` contains)

Five buckets, one table per bucket.

| Bucket | Source claims | Action |
|---|---|---|
| **A. Already verified against this interpreter** | ~30 SPL-semantics claims with probe evidence in `spl/verification-evidence.md` | Cite as-is; no action |
| **B. Cheap replays to run as part of this restructure** | Interpreter cold-start timing; `shakespeare` install path and version; `~/markdown/Markdown.pl` present and identifies as v1.0.1; 23 fixtures in `~/mdtest/Markdown.mdtest/`; ebnf contains no `random/rand/chance` token; ebnf has no `float` token; AST-cache smoke test; `spl/reference.md` claim-coverage sweep against probe log + ebnf | Run during restructure; record results and dates |
| **C. Retrospective — from prior codebase, not proven here** | All 10 feasibility experiment verdicts; line counts (4,311 and ~8,623); fixture-matrix "likely pass" labels tied to the prior implementation; projected ~2,300-line full-port size; cast-pressure commentary | Tag every such claim in `prior-attempt/feasibility-lessons.md` and `markdown/fixture-outlook.md`; do not replay |
| **D. Predictions, not facts — open items for architecture planning** | Fixture pass ceiling (~91–96%); loose-list risk; emphasis-backtracking risk; nested-block composition risk; build-order sequencing | Record as open questions; architecture planning closes them |
| **E. New claims this restructure introduces** | Exact Markdown.pl v1.0.1 version header; fixture list as 23 named fixtures | Verify while writing `markdown/target.md` |

### Cheap replays (bucket B) — specific procedures

1. **Interpreter cold start** — `time shakespeare run /tmp/empty.spl` with a minimal
   valid play; expect 17–26s (the documented range for this machine).
2. **Interpreter identity** — `which shakespeare; shakespeare --version`; confirm install
   path and interpreter identity match the assumptions in `spl/reference.md`.
3. **Oracle present** — `head -30 ~/markdown/Markdown.pl` confirms the v1.0.1 version
   string.
4. **Fixture count** — `ls ~/mdtest/Markdown.mdtest/*.text | wc -l` returns 23.
5. **No randomness primitive** — `grep -iE 'random|rand|chance' ~/shakespearelang/shakespearelang/shakespeare.ebnf` returns no matches.
6. **Integer-only** — `grep -iE 'float|double|decimal' ~/shakespearelang/shakespearelang/shakespeare.ebnf` returns no matches, or any matches are clearly not numeric-type tokens.
7. **AST cache smoke test** — confirm `shakespeare parse` (or equivalent) can produce a
   cached representation separable from `shakespeare run`, as a sanity check on the
   round-2 Exp 6 "PASS" for cached-AST execution. Light smoke only, not a full benchmark.
8. **Reference claim coverage** — for each claim in `spl/reference.md` labeled
   "Empirically confirmed" or "Corrected project assumption", locate the matching row in
   `spl/verification-evidence.md` or ebnf line. Record any unbacked claims as
   bucket D items.

Each replay records: command, observed output, date, and disposition ("claim confirmed",
"claim narrowed", "open").

## Sequencing

The implementation plan this design generates will have these phases:

1. **Verify** — run the bucket B cheap replays; capture output; note any claim that needs
   revising before it is moved.
2. **Create skeleton** — `mkdir -p docs/{spl/probes,markdown,prior-attempt,archive}`.
3. **Move frozen files** — `git mv` the three style docs and verify content-hash
   preservation. Apply cross-reference path edits only.
4. **Move supporting evidence** — `spl/verification-evidence.md`,
   `spl/lexicon-sources.md`, `spl/probes/`, `markdown/divergences.md`.
5. **Archive historical docs** — `project-history.md`, `slow-machine-spl-workflow.md`,
   `spl-feasibility-resumption-context.md`, and the current form of
   `prompt-shakedown.md`. Stamp each with a one-line header: `> Archived 2026-04-17.
   Historical artifact. See <live successor> for current guidance.`
6. **Write `prior-attempt/feasibility-lessons.md`** — consolidate the three feasibility
   sources using the shape above.
7. **Write `prior-attempt/architecture-lessons.md`** — consolidate the three architecture
   sources using the shape above.
8. **Write `markdown/target.md`** — describe the Markdown.pl v1.0.1 surface Shakedown
   targets, drawing from `project-history.md`, the feasibility sources, and the fixture
   names.
9. **Rewrite `markdown/fixture-outlook.md`** — the fixture matrix reframed as predictive
   risks for a fresh build; "likely pass" labels replaced with "low-risk / medium-risk /
   high-risk" commentary tied to what actually exists in this repo.
10. **Reference-claim coverage sweep** — diff `spl/reference.md` claims against
    `spl/verification-evidence.md` and ebnf line refs; capture findings for
    `verification-plan.md`.
11. **Write `verification-plan.md`** — the five-bucket tables with the replay outputs and
    any open items discovered in step 10.
12. **Write `docs/README.md`** — index with subject-by-subject navigation and a short
    "how to use these docs" section for a new agent.
13. **Update `CLAUDE.md`** — replace all `docs/research/...` paths in the reference list
    with new paths. Remove references to archived docs unless they belong in a "historical
    context" line.
14. **Remove `docs/research/`** — empty directory after steps 3–9 run.
15. **Verify internal links** — grep the new doc set for any remaining
    `docs/research/` reference and fix.

Each step is a single conventional commit (`docs:` or `chore:` depending on scope).

## Approaches Considered

### 1. Subject-clustered with archive (chosen)

- **Pros:** agents find material by what it is about (SPL / Markdown.pl / prior-attempt
  / verification / history); archive preserves evidence without polluting the live set;
  clean MECE axes.
- **Cons:** four subdirectories; a small amount of navigation overhead.

### 2. Flat directory with fewer bigger files

- **Pros:** less navigation; fewer file names to remember.
- **Cons:** file names carry all the structure; each file mixes more concerns, making
  MECE harder; future additions are less obvious about where they go.

### 3. Lifecycle-first layout (`frozen/`, `living/`, `archive/`)

- **Pros:** explicit stability contract per directory.
- **Cons:** does not match how agents search ("I need SPL semantics" is a subject query,
  not a stability query); cross-subject lookups become harder.

Approach 1 was chosen.

## Feasibility Treatment (of the prior attempt's results)

The two feasibility summaries describe experiments run in a checkout that is no longer
present in this repository. Three options were considered:

- **Replay them all** — highest evidence, out of scope for this restructure.
- **Cite and demote (chosen)** — preserve the learning, clearly label claims that rest on
  absent artifacts, and re-verify only the few cheap load-bearing ones (cold-start,
  AST-cache feasibility). This is what the verification plan encodes.
- **Drop them entirely** — throws away useful thinking about architectural trade-offs.

## Risks

- **Scope creep into the consolidations.** The two prior-attempt docs need to be
  retrospectives, not re-analyses. Mitigation: strict shape from the consolidation
  sections above; do not introduce new judgments while writing them.
- **Over-editing the frozen files.** The frozen-file rule is strict. Mitigation: cross-
  reference path edits only; any other edit triggers a question.
- **Cheap replays discover a drift from prior claims.** If cold-start timing, oracle
  version, or fixture count differs from what's documented, the restructure must surface
  the drift rather than paper over it. Mitigation: step 1 is a capture phase; any
  material drift pauses sequencing until raised.
- **`prompt-shakedown.md` becomes incoherent once its `@`-targets move.** Its rewrite is
  out of scope here, so it goes to archive and a replacement is written by the next piece
  of work.

## Commit Strategy

Each sequencing step is a `docs:` commit (or `chore:` for mechanical directory
operations). Consolidations use `docs:` with a body describing which sources were merged
into which target. The final commit removes `docs/research/` and updates `CLAUDE.md`.

## Success Criteria

- `docs/` contains exactly the files listed under "Target Structure".
- `docs/research/` no longer exists.
- No file under `docs/` outside `archive/` and `superpowers/` references a
  `docs/research/...` path.
- The three frozen files' bodies are unchanged except for cross-reference path edits (a
  content diff would show only those lines).
- `docs/verification-plan.md` contains a row per claim in buckets A–E.
- `CLAUDE.md` references resolve to real files.
- A new agent can read `docs/README.md` and reach every other doc with one click or
  `cat`.
