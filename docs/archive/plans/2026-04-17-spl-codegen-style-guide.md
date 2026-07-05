# SPL Codegen Style Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new implementation-facing SPL codegen style guide that defines how Shakedown should choose, reuse, and vary value expressions without making architecture-dependent commitments.

**Architecture:** This is a docs-only change. The implementation adds a new research document positioned between the verified SPL reference and the expressive style lexicon, then cross-links it from the existing docs so future agents can use the three layers correctly.

**Tech Stack:** Markdown documentation, git, existing SPL research docs in `docs/research/`

---

## File Structure

- Create: `docs/research/shakedown-spl-codegen-style-guide.md`
  - New implementation-facing guide for value-expression code generation policy.
- Modify: `docs/research/shakedown-spl-reference.md`
  - Add a short pointer to the codegen guide from the constant-encoding / generation-oriented guidance area.
- Modify: `docs/research/shakedown-spl-style-lexicon.md`
  - Add a short pointer clarifying that the style lexicon supplies legal expressive vocabulary, while the codegen guide defines implementation policy.

## Task 1: Draft The New Codegen Guide

**Files:**
- Create: `docs/research/shakedown-spl-codegen-style-guide.md`

- [ ] **Step 1: Re-read the source docs that this guide must bridge**

Run:

```bash
sed -n '1,260p' docs/research/shakedown-spl-reference.md
sed -n '1,260p' docs/research/shakedown-spl-style-lexicon.md
sed -n '1,260p' docs/superpowers/specs/2026-04-17-spl-codegen-style-guide-design.md
```

Expected:
- the reference remains the legality source
- the style lexicon remains the expressive-vocabulary source
- the approved spec limits this guide to value-expression policy

- [ ] **Step 2: Write the new guide with the approved section structure**

Create `docs/research/shakedown-spl-codegen-style-guide.md` with content shaped like:

```md
# SPL Codegen Style Guide

This guide defines how Shakedown should express recurring numeric values in SPL.
It is implementation policy, not parser truth.

Use the docs in this order:

1. `docs/research/shakedown-spl-reference.md` for legality and verified semantics
2. `docs/research/shakedown-spl-style-lexicon.md` for legal expressive vocabulary
3. `docs/research/shakedown-spl-codegen-style-guide.md` for implementation policy

## Purpose And Scope

- in scope: constants, computed value expressions, phrase reuse, palette-by-purpose
- out of scope: character naming, act/scene rhetoric, architecture-specific role naming

## Constant Strategy

### Critical Constants

- keep one canonical surface for values that act as sentinels or repeated control markers
- examples: EOF-adjacent markers, booleans reused in control flow, newline if heavily reused

### Stable Utility Constants

- allow a small approved family for frequently used but non-sentinel values such as `1`, `2`, and small counters

### Incidental Literals

- allow broader variation when the literal is local, one-off, and not recognition-critical

## Value-Preserving Variation Rules

- preserve sign by staying on the same noun-sign path
- preserve magnitude by preserving adjective count
- prefer neutral adjectives for low-risk stylistic variation
- keep multi-word nouns intact

## Palette By Purpose

- benign state: noble, domestic, pastoral
- error or poison state: grotesque, catastrophic
- parsing utility: plainer phrases, less ornament

## Reuse And Consistency Rules

- do not vary critical sentinels casually
- keep repeated nearby infrastructure values recognizable
- permit variation only where it does not reduce debugging clarity

## Expression Templates

- canonical constant assignment example
- same-value controlled alternate-surface example
- comparison example with recognizable constants
- arithmetic example where clarity outranks flourish

## Anti-Patterns

- sign-confusing swaps
- adjective-count drift
- random phrase churn for the same sentinel
- decorative overgrowth in utility code

## Deferred Guidance

Character naming and dramatic voice are intentionally deferred until the SPL architecture is chosen.
```

Expected:
- the guide stays implementation-facing
- the guide contains concrete policy, not broad literary advice
- the guide does not invent grammar or architecture commitments

- [ ] **Step 3: Add short, technically correct examples**

Ensure the guide includes examples such as:

```md
- Canonical repeated sentinel:
  keep one phrase, such as `nothing`, everywhere the sentinel is compared or assigned nearby.

- Controlled same-value variation:
  `a cat` and `a fellow` both encode `+1`, but only use both if the value is noncritical and the variation will not impair scanning.

- Unsafe variation:
  `a cat` to `a big cat` is not a style change; it changes `+1` to `+2`.
```

Expected:
- examples are grammar-valid
- examples teach policy by contrast
- examples do not require an assumed final program architecture

- [ ] **Step 4: Review the new file for scope drift and ambiguity**

Run:

```bash
sed -n '1,260p' docs/research/shakedown-spl-codegen-style-guide.md
rg -n "TBD|TODO|FIXME|character naming|scene voice|act voice|role assignment" docs/research/shakedown-spl-codegen-style-guide.md
```

Expected:
- no placeholders
- no architecture-dependent guidance except the explicit deferred-guidance note
- no contradiction with the approved design spec

- [ ] **Step 5: Commit the new guide**

Run:

```bash
git add docs/research/shakedown-spl-codegen-style-guide.md
git commit -m "docs: add SPL codegen style guide"
```

Expected:
- one docs-only commit containing the new guide

## Task 2: Cross-Link The Existing Docs

**Files:**
- Modify: `docs/research/shakedown-spl-reference.md`
- Modify: `docs/research/shakedown-spl-style-lexicon.md`

- [ ] **Step 1: Add a reference-doc pointer to the new codegen guide**

Update the generation-oriented note in `docs/research/shakedown-spl-reference.md` so it reads like:

```md
Lexicon legality note:

- For generation-oriented palettes and phrase suggestions built from this legal vocabulary, see
  `docs/research/shakedown-spl-style-lexicon.md`.
- For implementation policy on when Shakedown should preserve or vary recurring value phrases,
  see `docs/research/shakedown-spl-codegen-style-guide.md`.
```

Expected:
- the reference remains the legality source
- the new pointer is short and operational

- [ ] **Step 2: Add a style-lexicon pointer to the new codegen guide**

Add a short note near the top of `docs/research/shakedown-spl-style-lexicon.md` like:

```md
This companion doc is for expressive generation, not parser truth and not codegen policy.
For legality and hard grammar constraints, use `docs/research/shakedown-spl-reference.md`.
For implementation policy on choosing and reusing value phrases, use
`docs/research/shakedown-spl-codegen-style-guide.md`.
```

Expected:
- the style lexicon remains the vocabulary source
- the codegen guide is clearly distinguished from it

- [ ] **Step 3: Re-read the touched docs together**

Run:

```bash
sed -n '1,120p' docs/research/shakedown-spl-reference.md
sed -n '1,120p' docs/research/shakedown-spl-style-lexicon.md
sed -n '1,260p' docs/research/shakedown-spl-codegen-style-guide.md
```

Expected:
- the three-doc layering is explicit and non-overlapping
- no duplicated long-form policy text was added to the reference or style lexicon

- [ ] **Step 4: Commit the cross-linking edits**

Run:

```bash
git add docs/research/shakedown-spl-reference.md docs/research/shakedown-spl-style-lexicon.md
git commit -m "docs: link SPL codegen guide"
```

Expected:
- a docs-only commit with the cross-link updates

## Task 3: Final Verification And Handoff

**Files:**
- Verify: `docs/research/shakedown-spl-reference.md`
- Verify: `docs/research/shakedown-spl-style-lexicon.md`
- Verify: `docs/research/shakedown-spl-codegen-style-guide.md`

- [ ] **Step 1: Check working tree state and final diff**

Run:

```bash
git status --short
git diff -- docs/research/shakedown-spl-reference.md docs/research/shakedown-spl-style-lexicon.md docs/research/shakedown-spl-codegen-style-guide.md
```

Expected:
- no unexpected files
- diff limited to the intended doc set

- [ ] **Step 2: Run doc-level placeholder and contradiction scans**

Run:

```bash
rg -n "TBD|TODO|FIXME|placeholder" docs/research/shakedown-spl-reference.md docs/research/shakedown-spl-style-lexicon.md docs/research/shakedown-spl-codegen-style-guide.md
rg -n "character naming|scene voice|act voice|role assignment" docs/research/shakedown-spl-codegen-style-guide.md
```

Expected:
- no placeholders
- only the deferred-guidance section mentions architecture-dependent topics

- [ ] **Step 3: Summarize outcomes for the user**

Prepare a handoff summary that states:

```md
- new file added: `docs/research/shakedown-spl-codegen-style-guide.md`
- existing docs now point to it
- the guide covers value-expression policy only
- character naming and dramatic voice remain intentionally deferred
```

Expected:
- the final report makes the layering and scope clear

- [ ] **Step 4: Leave the branch in a clean state**

Run:

```bash
git status --short
```

Expected:
- no uncommitted changes remain

## Self-Review

Spec coverage:
- purpose and narrow scope are covered in Task 1 Step 2
- constant strategy, variation rules, palette-by-purpose, reuse rules, templates, anti-patterns, and deferred guidance are all required in Task 1 Step 2 and Step 3
- positioning between reference and style lexicon is implemented in Task 2

Placeholder scan:
- no `TBD`, `TODO`, or deferred implementation placeholders appear in the plan steps

Type and naming consistency:
- the new file path is consistently `docs/research/shakedown-spl-codegen-style-guide.md`
- the approved design spec path is consistently `docs/superpowers/specs/2026-04-17-spl-codegen-style-guide-design.md`
