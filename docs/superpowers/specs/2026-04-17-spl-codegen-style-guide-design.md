# SPL Codegen Style Guide Design

Date: 2026-04-17
Status: proposed

## Purpose

Define a narrow, implementation-facing style guide for how Shakedown should express numeric
values in SPL. This guide is not a parser reference and not a full dramatic-style manifesto.
Its job is to keep generated SPL colorful, technically valid, and operationally readable when
the implementation starts emitting recurring constants and value expressions.

## Problem

The repo now has:

- `docs/research/shakedown-spl-reference.md` for legality and verified semantics
- `docs/research/shakedown-spl-style-lexicon.md` for expressive legal vocabulary

What is still missing is the policy layer between them: how the actual implementation should
choose, reuse, and vary value phrases. Without that layer, the eventual SPL can drift in two
bad directions:

- dull but mechanically safe output such as repeated `big big big cat`
- colorful but unstable output where the same critical value is phrased inconsistently and
  becomes harder to debug

## Scope

This design covers only value-expression code generation.

In scope:

- canonical handling of recurring constants
- value-preserving phrase variation rules
- palette-by-purpose guidance for categories of values
- reuse and consistency rules for infrastructure values
- examples of acceptable and unacceptable codegen choices

Out of scope:

- character naming conventions
- act and scene voice
- dramatic tone for the whole program
- architecture-specific role assignment

Those remain architecture-dependent and should be documented later, after the SPL program shape
is chosen.

## Goals

- Keep generated SPL technically correct against the verified grammar and interpreter behavior.
- Make recurring constants readable and recognizable during debugging.
- Permit controlled variety for noncritical literals so generated code does not sound
  mechanically repetitive.
- Give future codegen work a concrete policy for when to preserve a phrase exactly and when to
  vary it safely.

## Non-Goals

- Exhaustively enumerate every vivid phrase the implementation could use.
- Choose final character names, register roles, or scene-level rhetoric.
- Lock the project into one dramatic voice before the program architecture exists.

## Approaches Considered

### 1. Add a small codegen section to the main SPL reference

Pros:

- one fewer file
- constant policy would sit close to legality rules

Cons:

- mixes hard parser truth with project-specific generation policy
- makes the reference less clean as a canonical legality source

### 2. Fold codegen policy into the style lexicon companion

Pros:

- keeps all wording-related guidance together
- easy to discover alongside expressive vocab lists

Cons:

- mixes vocabulary inventory with implementation discipline
- weakens the distinction between "what is legal" and "how Shakedown should use it"

### 3. Create a separate codegen style guide

Pros:

- clean separation of concerns
- easiest for an agent to use operationally
- lets the guide stay narrow and architecture-aware without contaminating the reference docs

Cons:

- one more document to maintain

Recommendation: approach 3.

## Proposed Output

Create a new document:

- `docs/research/shakedown-spl-codegen-style-guide.md`

The guide should explicitly position itself between the legality reference and the style
lexicon:

- use the reference to check whether a form is legal
- use the style lexicon to find legal expressive vocabulary
- use the codegen guide to decide what Shakedown should actually emit

## Proposed Structure

### 1. Purpose And Scope

State that the guide is for implementation-facing value expression choices only. It should say
clearly that character naming and dramatic voice are deferred.

### 2. Constant Strategy

Define policy for recurring literals and values that are likely to appear throughout the
implementation.

Expected categories:

- neutral infrastructure constants such as `0`, `1`, `-1`, `2`, and small loop counters
- I/O-adjacent values such as newline and common punctuation code points when relevant
- sentinel and failure-adjacent values such as EOF markers

For each category, the guide should explain whether Shakedown should use:

- one canonical phrase everywhere
- a small approved family of interchangeable phrases
- free variation for incidental literals

### 3. Value-Preserving Variation Rules

Explain how codegen may vary wording without altering behavior:

- preserve sign by staying on the same noun-sign path
- preserve magnitude by keeping adjective count unchanged
- use neutral adjectives as the safest texture changes
- treat multi-word nouns as indivisible grammar tokens

This section should also call out that variation is not automatically good; it is only good
when it does not reduce recognizability of important values.

### 4. Palette By Purpose

Map semantic palettes to implementation roles rather than to general prose style.

Examples:

- noble, domestic, or pastoral wording for stable benign state
- grotesque or catastrophic wording for error, poison, or sentinel-adjacent values
- plainer utility wording for counters, punctuation literals, and parsing machinery

The guide should keep these as recommendations, not absolute mandates.

### 5. Reuse And Consistency Rules

This is the operational core of the guide.

It should define when a value should keep the same surface form:

- critical sentinels
- booleans used repeatedly in control flow
- well-known I/O markers
- frequently repeated infrastructure constants in dense local regions

It should also define when controlled variation is acceptable:

- incidental one-off literals
- wide-apart uses where variety improves readability without harming recognition
- noncritical phrases in explanatory or decorative code areas

### 6. Expression Templates

Provide short implementation-facing examples, not a full cookbook.

Expected template types:

- assigning a canonical constant
- assigning the same numeric value with controlled alternate surfaces
- comparisons that keep critical values recognizable
- arithmetic phrases where clarity matters more than flourish
- examples of safe stack-adjacent phrasing

### 7. Anti-Patterns

Document failure modes that would make generated SPL worse:

- random phrase churn for the same sentinel
- sign-confusing stylistic swaps
- magnitude drift from accidental adjective-count changes
- using vivid phrasing where a constant should stay recognizably canonical
- over-decorating utility code until the data flow is harder to inspect

### 8. Deferred Guidance

Close with an explicit note that character naming, role assignment, and dramatic voice are
intentionally deferred until the program architecture is chosen.

## Success Criteria

The design is successful if the resulting guide:

- can be followed by an agent generating SPL constants without re-deriving policy each time
- keeps critical values stable enough for debugging
- still leaves room for expressive variety in noncritical literals
- does not claim architecture-specific guidance that the repo has not yet earned

## Risks

- If the guide becomes too prescriptive, it may lock future implementation choices prematurely.
- If it stays too abstract, it will not improve actual generated code.
- If critical and incidental constants are not distinguished clearly, agents will still vary
  the wrong things.

## Mitigations

- keep the scope explicitly limited to value expressions
- define critical versus incidental constant categories directly
- use short concrete examples rather than long aesthetic advice
- defer architecture-dependent naming guidance on purpose

## Implementation Note

After this spec is approved, the implementation plan should produce the guide as a docs-only
change. No runtime code or architecture commitments are required for this pass.
