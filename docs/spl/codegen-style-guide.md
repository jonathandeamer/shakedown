# SPL Codegen Style Guide

This guide defines how Shakedown should express recurring numeric values in SPL.
It is implementation policy, not parser truth.

Use the docs in this order:

1. `docs/spl/reference.md` for legality and verified semantics
2. `docs/spl/style-lexicon.md` for legal expressive vocabulary
3. `docs/spl/literary-spec.md` for character voice, per-act palettes, and decorative surfaces
4. `docs/spl/codegen-style-guide.md` for implementation policy on recurring value phrases

## Purpose And Scope

This guide exists to keep generated SPL both colorful and operationally legible.
It is concerned with how Shakedown should phrase values that recur in real code, not with
describing the whole language and not with choosing a full dramatic voice for the final play.
Full-program voice policy lives in `docs/spl/literary-spec.md`.

In scope:

- recurring constants such as `0`, `1`, `-1`, `2`, and other small infrastructure values
- computed value expressions that appear repeatedly in assignments, arithmetic, and comparisons
- when to preserve a phrase exactly versus when to vary it safely
- palette-by-purpose guidance for different implementation roles

Out of scope:

- naming conventions for dramatis personae
- act and scene diction
- architecture-specific naming of implementation roles
- full-program dramatic voice

Those are governed by `docs/spl/literary-spec.md` and the future hand-authored
`src/literary.toml` data file. This guide remains the lower-level numeric policy.

## Constant Strategy

Not every value needs the same amount of stylistic stability. The implementation should treat
constants in three categories.
These categories are codegen policy labels, not interpreter-detectable properties.

### Critical Constants

Critical constants are values whose recognizability matters more than local variety.
These should keep one canonical surface within a local subsystem, and often globally.

Typical candidates:

- EOF-adjacent values such as `-1` when modeling input exhaustion
- booleans that recur in control flow
- newline and other I/O markers when they are compared or emitted repeatedly
- sentinel values that distinguish normal from exceptional paths

Policy:

- prefer one canonical phrase for each critical constant
- do not rotate among multiple surfaces in nearby code
- only change the canonical surface deliberately and repo-wide for that subsystem

Examples:

- canonical repeated sentinel: keep `nothing` for `0` if that value acts as a nearby control
  marker rather than a decorative literal
- canonical negative sentinel: if `-1` is used as EOF state, keep one recognizable negative
  phrase rather than alternating among insults

### Stable Utility Constants

Stable utility constants recur often, but they are not usually semantic sentinels.
These may use a small approved family of interchangeable surfaces if readability remains high.

Typical candidates:

- `1`, `2`, and other small counters
- common arithmetic operands used in loops or local transforms
- punctuation code points used repeatedly but not as branching sentinels

Policy:

- prefer one default phrase
- allow a small approved family when variation improves texture without hurting scanning
- avoid excessive local churn even for noncritical constants

Examples:

- `a cat` and `a fellow` both encode `+1`
- `a big cat` and `a big fellow` both encode `+2`

Use both only when the value is noncritical and the variation does not make the code harder to
scan.

### Incidental Literals

Incidental literals are local one-off values whose exact surface is not load-bearing for
debugging or control flow.

Policy:

- broader variation is acceptable
- choose phrases that fit the local tone or clarify the nearby expression
- still obey sign and magnitude rules exactly

Examples:

- a one-off `+1` in a decorative comparison can vary more freely than a repeated loop step
- a local arithmetic phrase can be more colorful if it is not reused as a recognizable marker

## Value-Preserving Variation Rules

Variation is only valid when it preserves behavior.

### Preserve Sign

- preserve positive sign by staying with positive or neutral nouns and positive or neutral
  adjectives
- preserve negative sign by staying with negative nouns and negative or neutral adjectives
- do not switch noun-sign paths casually just to get different imagery

Examples:

- safe positive variation: `a cat` to `a fellow`
- safe negative variation: `a pig` to `a wolf`
- unsafe sign change: `a cat` to `a pig`

### Preserve Magnitude

- preserve magnitude by preserving adjective count
- treat adjective count as semantic, not decorative
- remember that neutral adjectives still double magnitude

Examples:

- safe same-value variation: `a big cat` to `a red fellow`
- unsafe magnitude drift: `a cat` to `a big cat`
- unsafe magnitude drift: `a horrible wolf` to `a horrible dirty wolf`

`a cat` to `a big cat` is not a style change; it changes `+1` to `+2`.

### Prefer Low-Risk Texture Changes

Neutral adjectives are usually the lowest-risk way to add or swap texture within a sign path
because they do not alter sign. They still alter magnitude, so they stay low-risk only when
adjective count stays fixed.

Examples:

- safe texture shift at `+2`: `a big cat` to `a red cat`
- safe texture shift at `-2`: `an old pig` to `a big pig`

### Keep Grammar Atoms Intact

Some legal nouns are multi-word grammar tokens and should be treated as indivisible.

Examples:

- keep `summer's day` intact
- keep `stone wall` intact
- do not split or partially substitute words inside those nouns

## Palette By Purpose

Palette guidance is advisory. It should support readability and tone, not override constant
discipline. For production Shakedown SPL, `docs/spl/literary-spec.md` supplies the act palette,
character voice, and precedence cascade. This section remains lower-level fallback guidance for
choosing safe value phrases inside that literary policy.

### Stable Or Benign State

Prefer noble, domestic, or pastoral wording when the value represents:

- normal control state
- benign flags
- ordinary counters or local bookkeeping
- values whose tone should feel steady rather than alarming

Examples:

- `a gentle pony`
- `a fair warm rose`
- `a healthy honest Lord`

### Error, Poison, Or Sentinel-Adjacent State

Prefer grotesque or catastrophic wording when the value represents:

- failure-adjacent state
- poison or invalid markers
- EOF-style exhaustion state
- values that conceptually signal danger or corruption

Examples:

- `a cursed rotten devil`
- `a vile smelly plague`
- `a fatherless half-witted coward`

Keep these stable when they function as true sentinels.

### Parsing Utility And Dense Mechanics

Prefer plainer, easier-to-scan wording when the code is doing dense utility work.

Typical cases:

- punctuation-related literals
- arithmetic-heavy local machinery
- stack traffic
- repeated comparisons in parsing logic

Examples:

- `a cat`
- `a big cat`
- `nothing`

In dense utility code, clarity outranks flourish.

## Literary Precedence

When this guide and the literary spec both apply, use the precedence cascade in
`docs/spl/literary-spec.md`:

- SPL grammar legality comes first.
- Sign and magnitude preservation come next.
- Critical canonical surfaces override decorative variety.
- Per-act palette and per-character voice inflect only the surfaces that remain safe to vary.

In practice, this means codegen may add variety only by selecting a pre-authored legal surface
that preserves the intended value and matches the current character/use-site policy.

## Reuse And Consistency Rules

This is the operational core of the guide.

### Keep The Same Surface When Recognition Matters

Keep one surface form when a value is:

- a sentinel
- a repeated boolean in nearby control flow
- a well-known I/O marker
- a frequently repeated infrastructure constant within a dense region

Examples:

- if `nothing` is the nearby false-like or empty marker, keep using `nothing`
- if one negative phrase marks EOF state, do not alternate among multiple negative phrases in
  the same control cluster

### Allow Controlled Variation When Recognition Does Not Matter

Controlled variation is acceptable when a value is:

- incidental and one-off
- reused only at wide distance
- not functioning as a branch discriminator
- not part of a dense local arithmetic pattern

Examples:

- one isolated `+1` assignment may use `a cat`
- a distant unrelated `+1` literal may use `a fellow`

### Prefer Local Consistency Over Global Ornament

If a section of code is visually dense, keep nearby repeated values uniform even if the wider
file permits more variation. Local recognizability matters more than global novelty.

## Expression Templates

These are policy examples, not mandated exact phrases.

### Canonical Constant Assignment

Use a stable phrase for a critical constant:

```text
Juliet: You are as good as nothing.
```

If `0` is acting as a nearby sentinel or empty marker, repeating `nothing` is preferable to
cycling through alternatives.

### Same Numeric Value, Controlled Alternate Surface

Use alternate surfaces only for noncritical values:

```text
Juliet: You are as lovely as a cat.
Juliet: You are as lovely as a fellow.
```

Both are `+1`. Use both only if the distinction is not load-bearing for debugging.

### Keep Comparisons Recognizable

In comparisons, repeated control values should remain easy to spot:

```text
Juliet: Am I as good as nothing?
Juliet: Are you worse than a pig?
```

If the same comparison constant recurs nearby, keep its surface stable.

### Keep Arithmetic Readable

Arithmetic-heavy code should prefer clarity over decorative churn:

```text
Juliet: You are the sum of a cat and a cat.
Juliet: You are the difference between yourself and nothing.
```

When the arithmetic is already carrying cognitive load, keep the constants simple.

### Stack-Adjacent Phrasing Should Stay Plain

Stack operations are easier to follow when the pushed values are recognizable:

```text
Juliet: Remember a cat.
Juliet: Remember nothing.
```

Avoid ornate one-off phrases if they make stack contents harder to inspect mentally.

## Anti-Patterns

Avoid these failure modes.

### Random Phrase Churn For The Same Sentinel

Bad:

- use `nothing`, then `a pig`, then `a wolf` for the same repeated control marker

Why it is bad:

- scanning becomes harder
- debugging intent becomes less obvious

### Sign-Confusing Swaps

Bad:

- replacing a positive noun phrase with a negative one just for variety

Why it is bad:

- the code changes meaning

### Magnitude Drift From Decorative Edits

Bad:

- adding an adjective because a phrase feels too plain

Why it is bad:

- adjective count changes the value

### Decorative Overgrowth In Utility Code

Bad:

- using long florid phrases in dense arithmetic or stack-manipulation regions

Why it is bad:

- the code becomes harder to scan than the underlying logic justifies

## Deferred Guidance

The concrete `src/literary.toml` tables remain deferred until implementation planning, before
Slice 1. They should be selected from verified legal vocabulary and should follow
`docs/spl/literary-spec.md`; this guide should not be used to invent character voice policy.
