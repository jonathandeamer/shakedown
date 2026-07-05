# SPL Style Guide Validation Design

Date: 2026-04-17
Status: proposed

## Purpose

Define how Shakedown should validate the technical claims made by:

- `docs/research/shakedown-spl-style-lexicon.md`
- `docs/research/shakedown-spl-codegen-style-guide.md`

The goal is not only to confirm that listed phrases are legal SPL, but also to test which
codegen-policy claims can be demonstrated concretely, which can be mechanically enforced, and
which should remain explicitly advisory.

## Problem

The repository now has:

- a verified SPL legality and semantics reference
- a writer-facing style lexicon
- an implementation-facing codegen style guide

What it does not yet have is a unified validation layer for those latter two guides. Without
that layer, several risks remain:

- a listed phrase or construction may be grammar-valid in principle but untested in practice
- a codegen guideline may read as stronger than the repo can actually enforce
- future edits may drift the guides away from the verified interpreter behavior without any
  regression signal

## Scope

This design covers validation of style- and codegen-guide claims.

In scope:

- legality validation for representative phrases and constructions
- runtime validation for representative examples drawn from both guides
- classification of guide statements by testability
- a focused runnable validation harness for mechanically testable claims
- an evidence note recording what was tested and what remains advisory

Out of scope:

- exhaustive enumeration of every legal adjective/noun combination
- exhaustive generation of every possible codegen phrase
- validating full-program dramatic tone
- validating architecture-dependent naming guidance that the repo has intentionally deferred

## Goals

- Distinguish hard technical claims from softer style guidance.
- Add regression protection for representative mechanically testable guide claims.
- Prove that the documented examples in the style and codegen guides are technically coherent.
- Tighten the docs where current language overstates what can actually be enforced.

## Non-Goals

- Proving every possible lexicon composition allowed by the grammar.
- Turning subjective style preferences into brittle pass/fail tests.
- Designing or approving the final SPL program architecture.

## Approaches Considered

### 1. Manual evidence note only

Pros:

- fast to produce
- low implementation cost

Cons:

- weak against future drift
- relies on humans remembering what to rerun
- gives no routine regression signal

### 2. Exhaustive generator-driven harness

Pros:

- maximal technical coverage
- attractive in theory for lexicon-heavy documentation

Cons:

- too much machinery for the current stage
- blurs the line between what must be enforced and what is only representative
- risks spending effort on combinations that do not materially improve guide trustworthiness

### 3. Categorized claim matrix plus focused runnable harness

Pros:

- clean separation between enforceable, demonstrable, and advisory claims
- good regression value at moderate cost
- easiest to keep aligned with the guides as they evolve

Cons:

- requires judgment about representative coverage
- will not mechanically settle every stylistic question

Recommendation: approach 3.

## Validation Model

The validation system should classify every relevant guide claim into one of three categories.

### 1. Mechanically Enforceable

These are claims the repo should be able to check automatically.

Expected examples:

- listed representative phrases parse and run
- sign-preserving substitutions preserve sign
- adjective-count-preserving substitutions preserve magnitude
- multi-word noun examples remain valid only when kept intact
- representative comparison forms parse and behave as documented
- representative codegen examples in the codegen guide produce the documented values or outputs

These claims belong in the runnable harness.

### 2. Demonstrable But Not Fully Enforceable

These are claims that can be illustrated with concrete examples but are not absolute invariants.

Expected examples:

- keeping a sentinel phrase stable improves recognizability in repeated local examples
- palette-by-purpose examples can be exercised without semantic contradiction
- utility-code examples can demonstrate “plain phrasing” without proving an objective global optimum

These claims belong in the evidence note as documented demonstrations, not hard regressions.

### 3. Advisory Only

These are claims that should remain guidance, not test requirements.

Expected examples:

- “clarity outranks flourish”
- broad style preferences about local ornament
- judgments about whether one valid phrase feels more legible than another in the abstract

These should be explicitly labeled as advisory in the docs if they currently read too strongly.

## Proposed Outputs

Create or update three layers:

### 1. Validation Evidence Note

Create:

- `docs/research/2026-04-17-spl-style-guide-validation.md`

Purpose:

- list the claims tested
- record which category each claim belongs to
- summarize probe/harness evidence
- identify any doc wording that should be softened or corrected

### 2. Runnable Validation Harness

Add a focused harness under `tests/` that:

- runs representative SPL programs through the local `shakespearelang` interpreter
- asserts parse success or failure where needed
- asserts numeric output via `Open your heart!`
- asserts character output where relevant
- checks representative examples taken directly from the two guides

This harness should remain intentionally small and representative.

### 3. Doc Corrections

Update the style and codegen guides only where validation reveals one of these:

- a listed example is invalid
- a policy claim is overstated as enforceable when it is only demonstrable
- a “safe” variation rule needs a tighter statement

## Harness Shape

The runnable harness should focus on representative rule families instead of exhaustive
combinatorics.

Suggested structure:

- one test module for style-lexicon legality and composition examples
- one test module for codegen-guide policy examples
- small probe files or inline-generated SPL programs for each rule family

Expected probe categories:

- representative positive, neutral, and negative noun-phrase examples
- representative same-sign substitutions
- representative same-magnitude substitutions
- representative comparison examples
- representative codegen assignment, arithmetic, comparison, and stack examples
- anti-pattern demonstrations that show semantic drift when a documented rule is violated

## Pass/Fail Criteria

### Mechanical Claims

Pass when:

- the probe parses
- the runtime result matches the documented claim
- any intentionally invalid case fails for the expected structural reason

Fail when:

- the example is illegal
- the example runs but yields a different semantic result than the guide claims
- the guide marks something as a safe variation when it changes sign or magnitude

### Demonstration Claims

Pass when:

- the evidence note contains at least one technically valid and semantically coherent example
  illustrating the guidance

Fail when:

- the guidance cannot be demonstrated without contradiction
- every candidate example undermines the rule it was meant to illustrate

### Advisory Claims

These do not produce harness failures.

Instead:

- they should be phrased as guidance
- the evidence note should explicitly mark them as advisory-only

## Testing Strategy

The validation work should proceed in this order:

1. map guide claims into the three testability categories
2. choose representative examples already present in the guides
3. add missing probe examples where a claim lacks a runnable representative
4. implement the runnable harness for mechanically enforceable claims
5. write the evidence note for demonstrable and advisory claims
6. tighten docs where validation changes confidence levels

## Risks

- The harness may drift toward exhaustive combinatorics instead of representative coverage.
- Some policy claims may look more objective than they really are.
- Example selection may accidentally privilege one aesthetic palette and under-test others.

## Mitigations

- explicitly reject exhaustive enumeration as a goal
- require every tested example to trace back to a documented rule family
- keep advisory claims out of pass/fail automation
- ensure representative coverage spans positive, neutral, and negative paths

## Success Criteria

This design is successful if the resulting implementation:

- gives the repo a repeatable way to verify representative style-guide claims
- distinguishes enforceable facts from softer guidance
- catches drift if examples in the guides become invalid or semantically misleading
- leaves the guides clearer about what is guaranteed versus what is merely recommended

## Implementation Note

After approval, the implementation plan should produce:

- one validation evidence note
- a focused runnable harness for mechanically testable claims
- only the minimum guide wording changes required by validation results
