# SPL Reference Verification

**Date:** 2026-04-17
**Interpreter target:** local Python `shakespearelang` CLI at `~/.local/bin/shakespeare`

This note records the probe programs used to verify the runtime claims in
`docs/research/shakedown-spl-reference.md`. It is not the main reference. It is the evidence
log behind the claims that were previously inferred or overstated.

## Results Table

| Claim | Prior status | Evidence | Result | Notes |
|---|---|---|---|---|
| Second-person pronouns require exactly one other on-stage character | inferred | `pronoun-stage-rules.spl` | Confirmed | Three on-stage characters raise `Ambiguous second-person pronoun` |
| First-person pronouns work with only the speaker on stage | inferred | `pronoun-stage-rules.spl` | Confirmed | The one-character first-person check completed and reached the later failing scene |
| "Two characters on stage" is not a universal stage-capacity rule | corrected assumption | grammar + `pronoun-stage-rules.spl` | Confirmed | Multi-character entrance is accepted; ambiguity comes from pronoun resolution, not a global cap |
| Character values start at `0` and stacks start empty | inferred | runtime error state dumps | Confirmed | Error states consistently showed `0` and empty stacks for untouched characters |
| Off-stage character values remain addressable | inferred | `value-semantics.spl` | Confirmed | Off-stage `Romeo` was read as `-1` |
| `nothing` maps to `0` | inferred | `value-semantics.spl` | Confirmed | Printed `0` |
| Bare positive/neutral noun phrases map to `+1` | inferred | `value-semantics.spl` | Confirmed | `a cat` printed `1` |
| Bare negative noun phrases map to `-1` | inferred | `value-semantics.spl` | Confirmed | `a pig` printed `-1` |
| Each adjective doubles magnitude | inferred | `value-semantics.spl` | Confirmed | `a big cat` printed `2` |
| Global boolean is overwritten by each question | inferred | `global-boolean-overwrite.spl` | Confirmed | Only the second question controlled the conditional; output was `1` |
| Gotos are act-local | inferred | `goto-across-acts.spl` | Confirmed | Jumping to `Scene II` in another act failed as `Scene II does not exist` |
| `Open your mind!` returns `-1` at EOF | inferred | `io-open-mind-eof.spl` | Confirmed | Output was `-1` |
| `Listen to your heart!` raises a runtime error at EOF | inferred | `io-listen-heart.spl` with `/dev/null` | Confirmed | Error was `End of file encountered.` |
| `Listen to your heart!` reads an integer token | inferred | `io-listen-heart.spl` with `42` | Confirmed | Output was `42` |
| `Speak your mind!` rejects invalid character codes | inferred | `io-speak-mind-range.spl` | Confirmed | `-1` raised `Invalid character code: -1` |
| Division truncates toward zero | inferred | `arithmetic-edge-cases.spl` | Confirmed | `-1 / 2` printed `0` |
| Division by zero is a runtime error | inferred | `arithmetic-edge-cases.spl` | Confirmed | Error was `Cannot divide by zero` |
| `Recall` on an empty stack is a runtime error | inferred | `error-recall-empty-stack.spl` | Confirmed | Error was `Tried to pop from an empty stack.` |
| Stacks are per-character, not shared | inferred | `stack-independence.spl` | Confirmed | Pushing to off-stage `Romeo` did not populate `Juliet`'s stack |
| Exiting a character not on stage is a runtime error | inferred | `error-exit-not-on-stage.spl` | Confirmed | Error was `Hamlet is not on stage!` |
| Entering a character already on stage is a runtime error | inferred | `error-enter-already-on-stage.spl` | Confirmed | Error was `Romeo is already on stage!` |

## Probe Details

### Pronoun and stage rules

- Program: `docs/research/tmp-spl-probes/pronoun-stage-rules.spl`
- Command: `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/pronoun-stage-rules.spl`
- Observed result:
  - valid two-character second-person assignment/output succeeded
  - valid one-character first-person question/goto succeeded
  - three-character second-person assignment failed with `Ambiguous second-person pronoun`
- Disposition: confirmed and used to correct the over-broad "two characters on stage" wording

### Global boolean overwrite

- Program: `docs/research/tmp-spl-probes/global-boolean-overwrite.spl`
- Command: `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/global-boolean-overwrite.spl`
- Observed result: `1`
- Disposition: confirmed that the latest question overwrites the global boolean used by `If so,` / `If not,`

### Goto across acts

- Program: `docs/research/tmp-spl-probes/goto-across-acts.spl`
- Command: `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/goto-across-acts.spl`
- Observed result: `SPL runtime error: Scene II does not exist.`
- Disposition: confirmed act-local scene lookup in runtime behavior

### Character input at EOF

- Program: `docs/research/tmp-spl-probes/io-open-mind-eof.spl`
- Command: `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/io-open-mind-eof.spl < /dev/null`
- Observed result: `-1`
- Disposition: confirmed

### Integer input

- Program: `docs/research/tmp-spl-probes/io-listen-heart.spl`
- Commands:
  - `printf '42\n' | ~/.local/bin/shakespeare run docs/research/tmp-spl-probes/io-listen-heart.spl`
  - `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/io-listen-heart.spl < /dev/null`
- Observed result:
  - integer token input produced `42`
  - EOF raised `SPL runtime error: End of file encountered.`
- Disposition: confirmed

### Character output edge case

- Program: `docs/research/tmp-spl-probes/io-speak-mind-range.spl`
- Command: `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/io-speak-mind-range.spl`
- Observed result: `SPL runtime error: Invalid character code: -1`
- Disposition: confirmed that invalid character codes are rejected; this matters for HTML emission strategies that use `Speak your mind!`

### Value semantics

- Program: `docs/research/tmp-spl-probes/value-semantics.spl`
- Command: `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/value-semantics.spl`
- Observed result: `012-1-1`
- Disposition:
  - `nothing` -> `0`
  - `a cat` -> `1`
  - `a big cat` -> `2`
  - `a pig` -> `-1`
  - off-stage `Romeo` retained and exposed `-1`

### Arithmetic edge cases

- Program: `docs/research/tmp-spl-probes/arithmetic-edge-cases.spl`
- Command: `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/arithmetic-edge-cases.spl`
- Observed result:
  - first output was `0` for `the quotient between a pig and a big cat`
  - second operation failed with `Cannot divide by zero`
- Disposition: confirmed truncation toward zero and divide-by-zero failure

### Stack behavior

- Programs:
  - `docs/research/tmp-spl-probes/error-recall-empty-stack.spl`
  - `docs/research/tmp-spl-probes/stack-independence.spl`
- Commands:
  - `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/error-recall-empty-stack.spl`
  - `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/stack-independence.spl`
- Observed result:
  - empty `Recall` failed with `Tried to pop from an empty stack.`
  - pushed value remained on off-stage `Romeo`'s stack and did not appear on `Juliet`'s stack
- Disposition: confirmed empty-pop failure and per-character stack independence

### Stage-operation errors

- Programs:
  - `docs/research/tmp-spl-probes/error-exit-not-on-stage.spl`
  - `docs/research/tmp-spl-probes/error-enter-already-on-stage.spl`
- Commands:
  - `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/error-exit-not-on-stage.spl`
  - `~/.local/bin/shakespeare run docs/research/tmp-spl-probes/error-enter-already-on-stage.spl`
- Observed result:
  - `Hamlet is not on stage!`
  - `Romeo is already on stage!`
- Disposition: confirmed

## Remaining Uncertainties

This pass did not probe every arithmetic form in the grammar. The following remain unverified
in runtime behavior, although their syntax is grammar-confirmed:

- modulo exact semantics for negative operands
- `square`, `cube`, `square root`, and `factorial`
- whether `zero` has any runtime distinction from `nothing` beyond sharing the same grammar slot

Those gaps are small compared with the corrected stage, input, output, and state-model claims
that affect Shakedown architecture directly.
