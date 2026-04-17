# Shakedown SPL Feasibility Assumption Corrections

This note is the canonical correction note for the Shakedown SPL feasibility-study assumptions.

The core stage-capacity and character-budget corrections are now also folded into
`docs/research/shakedown-spl-reference.md`, which should be the first stop for current SPL
semantics in this repo.

Use it when relying on SPL semantics for implementation planning, architectural decisions,
or pass-rate estimates. Several statements about SPL constraints are outdated or too broad
as written.

## Corrected Assumptions

### 1. The local SPL reference does not support a language-level “6-character budget” claim

Some round-1 feasibility material treats Shakedown as if SPL imposes a six-character
architectural ceiling. The local SPL reference does not support that claim.

What the reference does support:
- each character has one value and one stack
- legal character names come from the interpreter grammar

Correct reading:
- the cited local reference does not support the claimed six-character SPL limit

Sources:
- docs/research/shakedown-spl-reference.md lines 37-45

### 2. “Two characters on stage” is a pronoun rule, not a universal stage-capacity rule

Some phase-2 material states that SPL only permits two characters on stage at a time.
That is too strong.

What the reference does support:
- second-person pronouns such as `you`, `thou`, `thee`, `yourself`, and `thyself`
  require exactly one other on-stage character
- otherwise evaluation is ambiguous or invalid

The grammar and stage-direction forms also include multi-character entrances and exits.

Correct reading:
- SPL strongly favors two-character interaction when code relies on second-person pronouns
- it is not the same as a global “maximum two characters on stage” rule

Sources:
- docs/research/shakedown-spl-reference.md lines 49-57
- docs/research/shakedown-spl-reference.md lines 159-170
- /home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf lines 442-450

### 3. “No limit on characters” is also too broad

Phase 2 correctly rejects the false six-character budget, but one statement overcorrects by
saying SPL imposes no limit on the number of characters in the dramatis personae.

The local reference says valid character names are exactly the grammar alternatives accepted
by the installed interpreter, so the set of distinct valid names is finite.

Correct reading:
- SPL does not impose the claimed six-character semantic budget
- SPL still operates within a finite grammar-defined vocabulary of legal character names

Sources:
- docs/research/shakedown-spl-reference.md lines 37-45

## Affected Documents

These documents should be read together with this correction note:
- experiments-spl/feasibility-summary.md
- experiments-spl/feasibility-summary-2.md
- docs/superpowers/specs/2026-04-16-shakedown-spl-validation-2-design.md

## Planning Guidance

For future implementation planning, use these corrected assumptions:
- the local SPL reference does not support a language-level six-character budget claim
- the important two-character rule is about second-person pronoun addressing
- the available cast is finite because legal names come from the interpreter grammar

Do not treat the old “6-character budget” or “two characters on stage at a time” wording as
authoritative SPL semantics without this correction layer.
