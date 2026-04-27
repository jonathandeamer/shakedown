# SPL Reference Verification

**Date:** 2026-04-17
**Interpreter target:** local Python `shakespearelang` CLI at `~/.local/bin/shakespeare`

This note records the probe programs used to verify the runtime claims in
`docs/spl/reference.md`. It is not the main reference. It is the evidence
log behind the claims that were previously inferred or overstated.

## Results Table

| Claim | Prior status | Evidence | Result | Notes |
|---|---|---|---|---|
| Second-person pronouns require exactly one other on-stage character | inferred | `pronoun-stage-rules.spl` | Confirmed | Three on-stage characters raise `Ambiguous second-person pronoun` |
| First-person pronouns work with only the speaker on stage | inferred | `pronoun-stage-rules.spl` | Confirmed | The one-character first-person check completed and reached the later failing scene |
| "Two characters on stage" is not a universal stage-capacity rule | corrected assumption | grammar + `pronoun-stage-rules.spl` | Confirmed | Multi-character entrance is accepted; ambiguity comes from pronoun resolution, not a global cap |
| Three-character scenes are legal when they avoid second-person dialogue | inferred | `three-character-safe-envelope.spl` | Confirmed | Three on-stage characters can run a first-person check, then exit back to two characters for normal dialogue |
| Character values start at `0` and stacks start empty | inferred | runtime error state dumps | Confirmed | Error states consistently showed `0` and empty stacks for untouched characters |
| Off-stage character values remain addressable | inferred | `value-semantics.spl` | Confirmed | Off-stage `Romeo` was read as `-1` |
| `nothing` maps to `0` | inferred | `value-semantics.spl` | Confirmed | Printed `0` |
| `zero` maps to `0` | inferred | `arithmetic-extended-valid.spl` | Confirmed | Printed `0` |
| Bare positive/neutral noun phrases map to `+1` | inferred | `value-semantics.spl` | Confirmed | `a cat` printed `1` |
| Bare negative noun phrases map to `-1` | inferred | `value-semantics.spl` | Confirmed | `a pig` printed `-1` |
| Each adjective doubles magnitude | inferred | `value-semantics.spl` | Confirmed | `a big cat` printed `2` |
| Global boolean is overwritten by each question | inferred | `global-boolean-overwrite.spl` | Confirmed | Only the second question controlled the conditional; output was `1` |
| Gotos are act-local | inferred | `goto-across-acts.spl` | Confirmed | Jumping to `Scene II` in another act failed as `Scene II does not exist` |
| `Open your mind!` returns `-1` at EOF | inferred | `io-open-mind-eof.spl` | Confirmed | Output was `-1` |
| `Listen to your heart!` raises a runtime error at EOF | inferred | `io-listen-heart.spl` with `/dev/null` | Confirmed | Error was `End of file encountered.` |
| `Listen to your heart!` reads an integer token | inferred | `io-listen-heart.spl` with `42` | Confirmed | Output was `42` |
| `Listen to your heart!` does not accept leading whitespace | inferred | `io-listen-heart-two-reads.spl` with leading spaces | Confirmed | Leading spaces produced `No numeric input was given.` |
| `Listen to your heart!` accepts newline-delimited integers but not space- or tab-delimited followups | inferred | `io-listen-heart-two-reads.spl` | Confirmed | `7\\n12\\n` worked; `7 12` and `7\\t12` failed on the second read |
| `Listen to your heart!` does not accept `+` or `-` signs in this interpreter | inferred | `io-listen-heart.spl` and `io-listen-heart-two-reads.spl` | Confirmed | `+9` and `-7` both produced `No numeric input was given.` |
| `Speak your mind!` rejects invalid character codes | inferred | `io-speak-mind-range.spl` | Confirmed | `-1` raised `Invalid character code: -1` |
| `Speak your mind!` emits Unicode code points encoded as UTF-8 | inferred | `io-speak-mind-bytes.spl` | Confirmed | `255` emitted `195 191`; `256` emitted `196 128` |
| `Speak your mind!` outputs a raw LF for code point `10` | inferred | `io-speak-mind-newline.spl` | Confirmed | Byte output was `10` |
| Division truncates toward zero | inferred | `arithmetic-edge-cases.spl` | Confirmed | `-1 / 2` printed `0` |
| Division by zero is a runtime error | inferred | `arithmetic-edge-cases.spl` | Confirmed | Error was `Cannot divide by zero` |
| Modulo follows truncation-toward-zero division and can be negative | inferred | `arithmetic-extended-valid.spl` | Confirmed | `-3 mod 2` printed `-1` |
| `square`, `cube`, `square root`, and `factorial` work on valid positive inputs | inferred | `arithmetic-extended-valid.spl` | Confirmed | Outputs were `4`, `8`, `2`, and `24` |
| `square root` of a negative number is a runtime error | inferred | `arithmetic-square-root-negative.spl` | Confirmed | Error includes the negative operand |
| `factorial` of a negative number is a runtime error | inferred | `arithmetic-factorial-negative.spl` | Confirmed | Error includes the negative operand |
| `Recall` on an empty stack is a runtime error | inferred | `error-recall-empty-stack.spl` | Confirmed | Error was `Tried to pop from an empty stack.` |
| Stacks are per-character, not shared | inferred | `stack-independence.spl` | Confirmed | Pushing to off-stage `Romeo` did not populate `Juliet`'s stack |
| Exiting a character not on stage is a runtime error | inferred | `error-exit-not-on-stage.spl` | Confirmed | Error was `Hamlet is not on stage!` |
| Entering a character already on stage is a runtime error | inferred | `error-enter-already-on-stage.spl` | Confirmed | Error was `Romeo is already on stage!` |

## Probe Details

### Pronoun and stage rules

- Program: `docs/spl/probes/pronoun-stage-rules.spl`
- Command: `~/.local/bin/shakespeare run docs/spl/probes/pronoun-stage-rules.spl`
- Observed result:
  - valid two-character second-person assignment/output succeeded
  - valid one-character first-person question/goto succeeded
  - three-character second-person assignment failed with `Ambiguous second-person pronoun`
- Disposition: confirmed and used to correct the over-broad "two characters on stage" wording

### Three-character safe envelope

- Program: `docs/spl/probes/three-character-safe-envelope.spl`
- Command: `~/.local/bin/shakespeare run docs/spl/probes/three-character-safe-envelope.spl`
- Observed result: `1`
- Disposition: confirmed that 3+ character scenes are valid when they avoid second-person
  dialogue and use only movement, first-person checks, or gotos before returning to a
  two-character scene for normal listener-targeting operations

### Global boolean overwrite

- Program: `docs/spl/probes/global-boolean-overwrite.spl`
- Command: `~/.local/bin/shakespeare run docs/spl/probes/global-boolean-overwrite.spl`
- Observed result: `1`
- Disposition: confirmed that the latest question overwrites the global boolean used by `If so,` / `If not,`

### Goto across acts

- Program: `docs/spl/probes/goto-across-acts.spl`
- Command: `~/.local/bin/shakespeare run docs/spl/probes/goto-across-acts.spl`
- Observed result: `SPL runtime error: Scene II does not exist.`
- Disposition: confirmed act-local scene lookup in runtime behavior

### Character input at EOF

- Program: `docs/spl/probes/io-open-mind-eof.spl`
- Command: `~/.local/bin/shakespeare run docs/spl/probes/io-open-mind-eof.spl < /dev/null`
- Observed result: `-1`
- Disposition: confirmed

### Integer input

- Program: `docs/spl/probes/io-listen-heart.spl`
- Commands:
  - `printf '42\n' | ~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart.spl`
  - `~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart.spl < /dev/null`
- Observed result:
  - integer token input produced `42`
  - EOF raised `SPL runtime error: End of file encountered.`
- Disposition: confirmed

### Integer input tokenization

- Program: `docs/spl/probes/io-listen-heart-two-reads.spl`
- Commands:
  - `printf '7\n12\n' | ~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart-two-reads.spl`
  - `printf '7 12\n' | ~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart-two-reads.spl`
  - `printf '7\t12\n' | ~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart-two-reads.spl`
  - `printf '   -7   12\n' | ~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart-two-reads.spl`
  - `printf -- '-7\n' | ~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart.spl`
  - `printf '+9\n' | ~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart.spl`
  - `printf '7x\n' | ~/.local/bin/shakespeare run docs/spl/probes/io-listen-heart-two-reads.spl`
- Observed result:
  - newline-delimited reads succeeded and produced `7 12`
  - leading spaces failed with `No numeric input was given.`
  - leading `+` and `-` failed with `No numeric input was given.`
  - a space or tab before the second integer caused the second read to fail
  - trailing junk after a successful first integer caused the next read to fail at that junk
- Disposition: confirmed that this interpreter reads a stricter unsigned decimal token format than the generic doc wording suggested

### Character output edge case

- Program: `docs/spl/probes/io-speak-mind-range.spl`
- Command: `~/.local/bin/shakespeare run docs/spl/probes/io-speak-mind-range.spl`
- Observed result: `SPL runtime error: Invalid character code: -1`
- Disposition: confirmed that invalid character codes are rejected; this matters for HTML emission strategies that use `Speak your mind!`

### Character output encoding

- Programs:
  - `docs/spl/probes/io-speak-mind-bytes.spl`
  - `docs/spl/probes/io-speak-mind-newline.spl`
- Commands:
  - `~/.local/bin/shakespeare run docs/spl/probes/io-speak-mind-bytes.spl | od -An -t u1`
  - `~/.local/bin/shakespeare run docs/spl/probes/io-speak-mind-newline.spl | od -An -t u1`
- Observed result:
  - output bytes for code points `8`, `255`, and `256` were `8 195 191 196 128`
  - output byte for code point `10` was `10`
- Disposition: confirmed UTF-8 encoded Unicode output for valid code points and raw newline emission for code point `10`

### Value semantics

- Program: `docs/spl/probes/value-semantics.spl`
- Command: `~/.local/bin/shakespeare run docs/spl/probes/value-semantics.spl`
- Observed result: `012-1-1`
- Disposition:
  - `nothing` -> `0`
  - `a cat` -> `1`
  - `a big cat` -> `2`
  - `a pig` -> `-1`
  - off-stage `Romeo` retained and exposed `-1`

### Arithmetic edge cases

- Program: `docs/spl/probes/arithmetic-edge-cases.spl`
- Command: `~/.local/bin/shakespeare run docs/spl/probes/arithmetic-edge-cases.spl`
- Observed result:
  - first output was `0` for `the quotient between a pig and a big cat`
  - second operation failed with `Cannot divide by zero`
- Disposition: confirmed truncation toward zero and divide-by-zero failure

### Extended arithmetic

- Programs:
  - `docs/spl/probes/arithmetic-extended-valid.spl`
  - `docs/spl/probes/arithmetic-square-root-negative.spl`
  - `docs/spl/probes/arithmetic-factorial-negative.spl`
- Commands:
  - `~/.local/bin/shakespeare run docs/spl/probes/arithmetic-extended-valid.spl`
  - `~/.local/bin/shakespeare run docs/spl/probes/arithmetic-square-root-negative.spl`
  - `~/.local/bin/shakespeare run docs/spl/probes/arithmetic-factorial-negative.spl`
- Observed result:
  - valid output was `0-148224`, which corresponds to:
    - `zero` -> `0`
    - `the remainder of the quotient between -3 and 2` -> `-1`
    - `the square of 2` -> `4`
    - `the cube of 2` -> `8`
    - `the square root of 4` -> `2`
    - `the factorial of 4` -> `24`
  - negative square root failed with `Cannot take the square root of a negative number: -1`
  - negative factorial failed with `Cannot take the factorial of a negative number: -1`
- Disposition: confirmed valid arithmetic behavior for the remaining unary operators and
  confirmed the negative-input failure modes

### Stack behavior

- Programs:
  - `docs/spl/probes/error-recall-empty-stack.spl`
  - `docs/spl/probes/stack-independence.spl`
- Commands:
  - `~/.local/bin/shakespeare run docs/spl/probes/error-recall-empty-stack.spl`
  - `~/.local/bin/shakespeare run docs/spl/probes/stack-independence.spl`
- Observed result:
  - empty `Recall` failed with `Tried to pop from an empty stack.`
  - pushed value remained on off-stage `Romeo`'s stack and did not appear on `Juliet`'s stack
- Disposition: confirmed empty-pop failure and per-character stack independence

### Stage-operation errors

- Programs:
  - `docs/spl/probes/error-exit-not-on-stage.spl`
  - `docs/spl/probes/error-enter-already-on-stage.spl`
- Commands:
  - `~/.local/bin/shakespeare run docs/spl/probes/error-exit-not-on-stage.spl`
  - `~/.local/bin/shakespeare run docs/spl/probes/error-enter-already-on-stage.spl`
- Observed result:
  - `Hamlet is not on stage!`
  - `Romeo is already on stage!`
- Disposition: confirmed

## Remaining Uncertainties

This pass did not probe every arithmetic form in the grammar. The following remain unverified
in runtime behavior, although their syntax is grammar-confirmed:

- modulo with negative divisors
- overflow or large-number behavior for `square`, `cube`, and `factorial`

Those gaps are now narrower than the original verification scope and do not affect the
current Shakedown architecture decisions.
