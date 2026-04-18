# SPL Style Guide Validation

## Scope

This note validates claims from:

- `docs/spl/style-lexicon.md`
- `docs/spl/codegen-style-guide.md`

It separates three kinds of guidance:

- **Mechanically enforceable**: interpreter-backed examples or phrase properties that a focused
  pytest harness can check directly
- **Demonstrable**: supported by representative examples and interpreter behavior, but not
  suitable for strict mechanical enforcement across all future codegen contexts
- **Advisory**: policy or style guidance that remains intentionally non-binding

`docs/spl/reference.md` remains the canonical source for verified SPL legality and runtime
semantics.

## Claim Matrix

| Claim family | Source doc | Example claim | Category | Validation method |
| --- | --- | --- | --- | --- |
| Representative phrase legality | `style-lexicon.md` | `a noble peaceful golden hero` is valid | mechanically enforceable | pytest probe executed with `shakespeare run` |
| Same-sign variation | `style-lexicon.md`, `codegen-style-guide.md` | `a cat` to `a fellow` preserves positive sign | mechanically enforceable | numeric-output probe |
| Same-sign negative variation | `style-lexicon.md`, `codegen-style-guide.md` | `a pig` to `a wolf` preserves negative sign | mechanically enforceable | numeric-output probe |
| Same-magnitude variation | `style-lexicon.md`, `codegen-style-guide.md` | `a big cat` to `a red fellow` preserves `+2` | mechanically enforceable | numeric-output probe |
| Magnitude drift warning | `style-lexicon.md`, `codegen-style-guide.md` | `a cat` to `a big cat` changes value | mechanically enforceable | paired numeric-output probe |
| Representative comparisons | `style-lexicon.md` | `friendlier than a gentle pony` parses and runs in context | mechanically enforceable | conditional probe |
| Codegen assignment examples | `codegen-style-guide.md` | `You are as good as nothing.` yields `0` | mechanically enforceable | assignment probe |
| Stack-adjacent examples | `codegen-style-guide.md` | `Remember nothing.` remains semantically coherent | mechanically enforceable | stack probe |
| Sentinel consistency examples | `codegen-style-guide.md` | nearby repeated sentinel phrasing stays recognizable | demonstrable | evidence note example |
| Palette-by-purpose guidance | `style-lexicon.md`, `codegen-style-guide.md` | noble, pastoral, grotesque, and plain palettes support the intended tone | demonstrable | representative examples in note |
| Controlled variation when recognition does not matter | `codegen-style-guide.md` | distant one-off values may vary safely | advisory | documented as policy only |
| `clarity outranks flourish` | `codegen-style-guide.md` | dense mechanics should use plainer wording | advisory | documented as policy only |
| Local consistency over global ornament | `codegen-style-guide.md` | dense regions should keep repeated values uniform | advisory | documented as policy only |

## Representative Probe Targets

- Positive / neutral phrase legality
  - `a noble peaceful golden hero`
  - `a beautiful rural morning`
- Negative phrase legality
  - `a vile smelly plague`
  - `a fatherless half-witted coward`
- Same-sign substitutions
  - `a cat` vs `a fellow`
  - `a pig` vs `a wolf`
- Same-magnitude substitutions
  - `a big cat` vs `a red fellow`
  - `an old pig` vs `a big pig`
- Representative comparisons
  - `as noble as a golden hero`
  - `friendlier than a gentle pony`
  - `punier than a dirty pig`
- Codegen examples
  - `You are as good as nothing.`
  - `You are as lovely as a cat.`
  - `You are the sum of a cat and a cat.`
  - `Remember nothing.`

## Demonstrable Claims

- Sentinel consistency is demonstrable with repeated local examples, but it depends on codegen
  intent and cannot be enforced mechanically without extra metadata about which constants are
  sentinel-like.
- Palette-by-purpose guidance is demonstrable through representative valid phrases, but the choice
  of noble, domestic, grotesque, or plain wording remains a codegen preference rather than a
  parser invariant.

## Observed Representative Outcomes

- Positive / neutral legality examples produced the expected values:
  `a noble peaceful golden hero` -> `8`, `a beautiful rural morning` -> `4`
- Negative legality examples produced the expected values:
  `a vile smelly plague` -> `-4`, `a fatherless half-witted coward` -> `-4`
- Same-sign substitutions preserved sign:
  `a cat` and `a fellow` -> `1`; `a pig` and `a wolf` -> `-1`
- Same-magnitude substitutions preserved value:
  `a big cat` and `a red fellow` -> `2`; `an old pig` and `a big pig` -> `-2`
- Magnitude drift remained observable:
  `a cat` -> `1`, `a big cat` -> `2`
- Representative comparisons parsed and ran in conditional context:
  `as noble as a noble peaceful golden hero`, `friendlier than a gentle pony`, and
  `punier than a dirty pig`
- Codegen examples matched the documented values:
  `You are as good as nothing.` -> `0`,
  `You are as lovely as a cat.` -> `1`,
  `You are the sum of a cat and a cat.` -> `2`,
  `Remember nothing.` remained consistent in a stack-adjacent probe

## Advisory-Only Claims

- `clarity outranks flourish`
- broad ornament-versus-legibility preferences
- local consistency versus global novelty tradeoffs
- when variation is acceptable because recognition supposedly does not matter

## Scope Review

- The first harness pass stays representative and intentionally bounded.
- This note stays within lexicon legality, magnitude/sign preservation, comparisons, and codegen
  examples.
- It does not attempt full architecture validation or dramatic-voice policy.
