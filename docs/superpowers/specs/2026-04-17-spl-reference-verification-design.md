# SPL Reference Verification Design

**Date:** 2026-04-17
**Status:** Proposed

## Goal

Strengthen `docs/research/shakedown-spl-reference.md` so it clearly distinguishes:

- grammar-confirmed claims
- empirically confirmed behavior of the local Python `shakespearelang` interpreter
- claims that were previously inferred and now need verification or correction

The end state is a reference that can be used for Shakedown implementation planning without
guessing which semantics are hard facts, which are observed interpreter behavior, and which
remain assumptions.

## Scope

In scope:

- updating `docs/research/shakedown-spl-reference.md`
- verifying high-risk inferred claims against the installed Python `shakespearelang`
  interpreter
- folding important corrections from
  `docs/research/shakedown-spl-feasibility-assumption-corrections.md` into the main
  reference
- recording the probe methodology and results in a small supporting research note

Out of scope:

- changing `shakedown.spl`
- broad SPL language research beyond claims used by this project
- documenting every grammar production in `shakespeare.ebnf`
- proving behavior of the historical C interpreter

## Why This Matters

The current reference is useful but mixes several evidence levels:

- grammar facts derived from `shakespeare.ebnf`
- runtime behavior believed to hold for the local interpreter
- project-level corrections that live in separate docs

That is workable for discussion, but it is weak for implementation work. The most important
risk is not missing trivia. It is relying on an overstated or unverified constraint and
baking it into architecture.

## Proposed Changes

### 1. Keep one canonical reference

`docs/research/shakedown-spl-reference.md` remains the main document for SPL behavior in this
repo.

It should stay readable as a working reference, not become a raw experiment log.

### 2. Add explicit provenance markers where they carry planning value

The reference will use short provenance labels only on claims where the distinction matters:

- `Grammar-confirmed`
- `Empirically confirmed`
- `Corrected project assumption`
- `Unverified` only if a claim cannot be resolved during this pass

These markers should appear in section intros or short notes, not on every list item, so the
document remains scannable.

### 3. Verify high-risk runtime semantics with small probe programs

Probe coverage should focus on behavior that affects parser architecture, control flow, or
HTML emission:

- pronoun resolution and on-stage ambiguity rules
- multi-character stage capacity versus second-person pronoun constraints
- global-boolean overwrite behavior across consecutive questions
- goto limits within and across acts
- I/O edge cases:
  - `Open your mind!` EOF behavior
  - `Listen to your heart!` EOF and token parsing behavior
  - `Speak your mind!` behavior for negative and out-of-range values
- runtime errors for invalid stage directions and empty-stack recall

If a claim is already directly supported by grammar alone, no probe is required unless the
runtime could still materially differ.

### 4. Separate evidence log from user-facing reference

The raw verification results should go into a compact supporting note under `docs/research/`,
for example a file named with the same date and topic.

That note should contain:

- each verified claim
- the probe program or command used
- the observed interpreter result
- the resulting disposition: confirmed, corrected, or still unresolved

The main reference should then summarize the outcome and link to the note where useful.

## Evidence Sources

The verification pass should use this evidence order:

1. local Python interpreter grammar: `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf`
2. local Python interpreter runtime via `shakespeare run`
3. existing repo correction notes and feasibility docs

If the grammar and runtime disagree, runtime behavior of the installed interpreter wins for
this repo, and the discrepancy should be called out explicitly.

## Deliverables

1. Updated `docs/research/shakedown-spl-reference.md`
2. New supporting verification note in `docs/research/`
3. Any small corrections needed in
   `docs/research/shakedown-spl-feasibility-assumption-corrections.md` if that note points
   at wording that becomes obsolete after the reference update

## Testing And Validation

This is a documentation change, but it still needs verification discipline.

Validation for completion:

- every high-risk inferred claim identified in this design has a recorded disposition
- the updated reference no longer states the false universal "two characters on stage"
  constraint
- the reference clearly states it targets the local Python `shakespearelang` interpreter
- the supporting note includes enough detail for another agent to rerun probes
- all edited Markdown files read coherently after the provenance markers are added

## Risks And Tradeoffs

### Risk: overloading the reference with provenance noise

Mitigation:
- keep detailed probe transcripts in the supporting note
- use short labels only where they change planning decisions

### Risk: probe coverage grows into open-ended interpreter research

Mitigation:
- stop at project-relevant semantics
- do not expand into unused grammar features

### Risk: observed runtime behavior is awkward or surprising

Mitigation:
- document it exactly
- prefer precise local truth over cleaner but inaccurate generalization

## Implementation Approach

1. Inventory the claims in `shakedown-spl-reference.md` that are presently stated as facts.
2. Classify each as grammar-confirmed, already corrected elsewhere, or requiring runtime
   verification.
3. Write minimal SPL probe programs for the unresolved runtime claims.
4. Run probes against the installed Python interpreter and record outcomes.
5. Update the supporting verification note with results.
6. Rewrite the main reference to reflect verified behavior and fold in critical corrections.

## Success Criteria

This pass succeeds if a future implementation session can read the SPL reference and answer
these questions without consulting multiple side documents:

- Which constraints come from the grammar?
- Which behaviors were verified against the local Python interpreter?
- Which formerly inferred claims were corrected?
- Which semantics still remain uncertain, if any?
