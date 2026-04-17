# SPL Language Reference

Quick reference for writing Shakespeare Programming Language programs in Shakedown.
This reference targets the local Python `shakespearelang` interpreter used in this repo
(`~/.local/bin/shakespeare` / `shakespeare run play.spl`).
Full grammar: `~/shakespearelang/shakespearelang/shakespeare.ebnf`.
Worked examples: `~/spl-1.2.1/examples/`.

Provenance used in this document:

- **Grammar-confirmed**: directly supported by `shakespeare.ebnf`
- **Empirically confirmed**: verified against the local Python interpreter
- **Corrected project assumption**: prior project docs overstated or misread a real constraint

For probe programs and observed interpreter behavior, see
`docs/research/2026-04-17-spl-reference-verification.md`.

---

## Program Structure

Grammar-confirmed.

```
Title of the Play.

CharacterName, a description.
AnotherCharacter, another description.

                    Act I: Title of act.

                    Scene I: Title of scene.

[Enter CharacterName and AnotherCharacter]

CharacterName: You are as good as nothing!

[Exeunt]
```

- **Title**: any text ending with `.` or `!`
- **Dramatis personae**: one line per character — `Name, description.`
- **Acts**: `Act ROMAN: description.` — acts contain scenes
- **Scenes**: `Scene ROMAN: description.` — scenes contain events
- **Events**: dialogue lines, entrances/exits, breakpoints

---

## Characters

Grammar-confirmed for legal names. Empirically confirmed for initial state.

Valid names are exactly the `character` alternatives in the installed grammar. This interpreter accepts:

`Achilles`, `Adonis`, `Adriana`, `Aegeon`, `Aemilia`, `Agamemnon`, `Agrippa`, `Ajax`, `Alonso`, `Andromache`, `Angelo`, `Antiochus`, `Antonio`, `Arthur`, `Autolycus`, `Balthazar`, `Banquo`, `Beatrice`, `Benedick`, `Benvolio`, `Bianca`, `Brabantio`, `Brutus`, `Capulet`, `Cassandra`, `Cassius`, `Christopher Sly`, `Cicero`, `Claudio`, `Claudius`, `Cleopatra`, `Cordelia`, `Cornelius`, `Cressida`, `Cymberline`, `Demetrius`, `Desdemona`, `Dionyza`, `Doctor Caius`, `Dogberry`, `Don John`, `Don Pedro`, `Donalbain`, `Dorcas`, `Duncan`, `Egeus`, `Emilia`, `Escalus`, `Falstaff`, `Fenton`, `Ferdinand`, `Ford`, `Fortinbras`, `Francisca`, `Friar John`, `Friar Laurence`, `Gertrude`, `Goneril`, `Hamlet`, `Hecate`, `Hector`, `Helen`, `Helena`, `Hermia`, `Hermonie`, `Hippolyta`, `Horatio`, `Imogen`, `Isabella`, `John of Gaunt`, `John of Lancaster`, `Julia`, `Juliet`, `Julius Caesar`, `King Henry`, `King John`, `King Lear`, `King Richard`, `Lady Capulet`, `Lady Macbeth`, `Lady Macduff`, `Lady Montague`, `Lennox`, `Leonato`, `Luciana`, `Lucio`, `Lychorida`, `Lysander`, `Macbeth`, `Macduff`, `Malcolm`, `Mariana`, `Mark Antony`, `Mercutio`, `Miranda`, `Mistress Ford`, `Mistress Overdone`, `Mistress Page`, `Montague`, `Mopsa`, `Oberon`, `Octavia`, `Octavius Caesar`, `Olivia`, `Ophelia`, `Orlando`, `Orsino`, `Othello`, `Page`, `Pantino`, `Paris`, `Pericles`, `Pinch`, `Polonius`, `Pompeius`, `Portia`, `Priam`, `Prince Henry`, `Prospero`, `Proteus`, `Publius`, `Puck`, `Queen Elinor`, `Regan`, `Robin`, `Romeo`, `Rosalind`, `Sebastian`, `Shallow`, `Shylock`, `Slender`, `Solinus`, `Stephano`, `Thaisa`, `The Abbot of Westminster`, `The Apothecary`, `The Archbishop of Canterbury`, `The Duke of Milan`, `The Duke of Venice`, `The Ghost`, `Theseus`, `Thurio`, `Timon`, `Titania`, `Titus`, `Troilus`, `Tybalt`, `Ulysses`, `Valentine`, `Venus`, `Vincentio`, `Viola`

Each character has:
- A **value** (integer, initialised to 0)
- A **stack** (list of integers, initially empty)

---

## Pronouns

Grammar-confirmed for available pronoun forms. Empirically confirmed for resolution behavior.

`I`, `me`, and `myself` refer to the speaker. This was verified in a one-character scene.
`you`, `thou`, `thee`, `yourself`, and `thyself` require exactly one other on-stage
character; with three characters on stage, the interpreter raises `Ambiguous second-person
pronoun`.

Corrected project assumption: this is a pronoun-resolution rule, not a language-level
"maximum two characters on stage" rule. Multi-character stage directions are legal.

| Pronoun | Refers to |
|---------|-----------|
| `I`, `me`, `myself` | the speaker |
| `you`, `thou`, `thee`, `yourself`, `thyself` | the other character |
| Character name | that character's current value, even if off stage |

---

## Encoding Constants

Grammar-confirmed for the available adjective/noun vocabulary. Empirically confirmed for the
basic value rules below.

Lexicon legality note:

- For generation-oriented palettes and phrase suggestions built from this legal vocabulary, see
  `docs/research/shakedown-spl-style-lexicon.md`.
- For implementation policy on when Shakedown should preserve or vary recurring value phrases,
  see `docs/research/shakedown-spl-codegen-style-guide.md`.

Numbers are encoded as noun phrases. The value is:
- `nothing` or `zero` → 0
- bare positive or neutral noun phrase → `+1`
- bare negative noun phrase → `-1`
- each adjective doubles the magnitude

Adjective count is the total number of adjectives (including neutral ones) before the noun.

**Rule: value = sign × 2^(adjective_count)**
Bare noun (no adjectives) = `+1` or `-1`. Each adjective doubles the magnitude.

```
nothing             →  0
a cat               → +1   (positive noun, 0 adjectives)
a big cat           → +2   (1 adjective)
a big big cat       → +4   (2 adjectives)
a big big big cat   → +8   (3 adjectives)
a pig               → -1   (negative noun, 0 adjectives)
a big pig           → -2   (1 adjective)
a big big pig       → -4
twice VALUE         →  VALUE × 2
```

### Positive adjectives
`amazing`, `beautiful`, `blossoming`, `bold`, `brave`, `charming`, `clearest`, `cunning`, `cute`, `delicious`, `embroidered`, `fair`, `fine`, `gentle`, `golden`, `good`, `handsome`, `happy`, `healthy`, `honest`, `lovely`, `loving`, `mighty`, `noble`, `peaceful`, `pretty`, `prompt`, `proud`, `reddest`, `rich`, `smooth`, `sunny`, `sweet`, `sweetest`, `trustworthy`, `warm`

### Negative adjectives
`bad`, `cowardly`, `cursed`, `damned`, `dirty`, `disgusting`, `distasteful`, `dusty`, `evil`, `fat-kidneyed`, `fatherless`, `fat`, `foul`, `hairy`, `half-witted`, `horrible`, `horrid`, `infected`, `lying`, `miserable`, `misused`, `oozing`, `rotten`, `smelly`, `snotty`, `sorry`, `stinking`, `stuffed`, `stupid`, `vile`, `villainous`, `worried`

### Neutral adjectives (double the value, no sign change)
`big`, `black`, `blue`, `bluest`, `bottomless`, `furry`, `green`, `hard`, `huge`, `large`, `little`, `normal`, `old`, `purple`, `red`, `rural`, `small`, `tiny`, `white`, `yellow`

### Positive nouns (sign = +1)
`Heaven`, `King`, `Lord`, `angel`, `flower`, `happiness`, `joy`, `plum`, `hero`, `rose`, `kingdom`, `pony`, `summer's day`

### Negative nouns (sign = −1)
`Hell`, `Microsoft`, `bastard`, `beggar`, `blister`, `codpiece`, `coward`, `curse`, `death`, `devil`, `draught`, `famine`, `flirt-gill`, `goat`, `hate`, `hog`, `hound`, `leech`, `lie`, `pig`, `plague`, `starvation`, `toad`, `war`, `wolf`

### Neutral nouns (sign = +1, used for value-neutral phrasing)
`animal`, `aunt`, `brother`, `cat`, `chihuahua`, `cousin`, `cow`, `daughter`, `door`, `face`, `father`, `fellow`, `granddaughter`, `grandfather`, `grandmother`, `grandson`, `hair`, `hamster`, `horse`, `lamp`, `lantern`, `mistletoe`, `moon`, `morning`, `mother`, `nephew`, `niece`, `nose`, `purse`, `road`, `roman`, `sister`, `sky`, `son`, `squirrel`, `stone wall`, `thing`, `town`, `tree`, `uncle`, `wind`

### Noun-Phrase Composition Rules

Grammar-confirmed from `shakespeare.ebnf`.

- Positive noun phrases use positive or neutral adjectives with positive or neutral nouns.
- Negative noun phrases use negative or neutral adjectives with negative nouns.
- Noun phrases may start with an article or a possessive.
- `summer's day` and `stone wall` are multi-word nouns in the grammar, not free text.
- To preserve a numeric value while varying style, keep the noun-sign path and adjective count the same.

---

## Operations

### Assignment

Grammar-confirmed for syntax. Empirically confirmed that the speaker assigns to the listener.

```
Juliet: You are as good as nothing.          → Romeo = 0
Juliet: Thou art as lovely as a cat!         → Romeo = 1
Juliet: You are the sum of a cat and a cat.  → Romeo = 1 + 1 = 2
```

`as ADJECTIVE as` before the value is cosmetic.

### Arithmetic

Grammar-confirmed for the forms listed below. Empirically confirmed in this pass:

- integer division truncates toward zero
- division by zero is a runtime error
- modulo follows truncation-toward-zero division and can be negative
- `square`, `cube`, `square root`, and `factorial` work on valid positive inputs
- negative `square root` and negative `factorial` raise runtime errors

Large-number and overflow behavior were not re-probed in this pass.

| Operation | Syntax |
|-----------|--------|
| Addition | `the sum of A and B` |
| Subtraction | `the difference between A and B` |
| Multiplication | `the product of A and B` |
| Integer division | `the quotient between A and B` |
| Modulo | `the remainder of the quotient between A and B` |
| Square | `the square of A` |
| Cube | `the cube of A` |
| Square root | `the square root of A` (errors on negative input) |
| Factorial | `the factorial of A` (errors on negative input) |
| Double | `twice A` |

### I/O

Grammar-confirmed for syntax. Empirically confirmed for listener targeting and the edge cases
below.

```
Juliet: Speak your mind!           → print chr(Romeo's value)
Juliet: Open your heart!           → print Romeo's value as integer
Juliet: Open your mind!            → Romeo = ord(next char from stdin); -1 at EOF
Juliet: Listen to your heart!      → Romeo = next integer from stdin
```

Always operates on the **listener** (the other character on stage).

Empirically confirmed:

- `Open your mind!` stores `-1` at EOF
- `Listen to your heart!` raises a runtime error on EOF
- `Speak your mind!` raises a runtime error on invalid character codes such as `-1`

Interpreter quirks that matter for Shakedown:

- `Listen to your heart!` accepts a simple unsigned decimal token such as `42`
- leading whitespace is not skipped
- leading `+` and `-` signs were rejected in this interpreter
- newline-delimited repeated reads worked; space- and tab-delimited followup reads did not
- junk after a successful integer read remains in the stream and can break the next read
- `Speak your mind!` emits valid code points as Unicode text encoded through Python's UTF-8 stdout, not as raw single bytes
- code point `10` emits a raw line feed

### Stack

Grammar-confirmed for syntax. Empirically confirmed for listener targeting, empty-pop
failure, and per-character stack independence.

```
Juliet: Remember yourself!         → push Romeo's value onto Romeo's stack
Juliet: Remember me!               → push Juliet's value onto Romeo's stack
Juliet: Remember a cat!            → push 1 onto Romeo's stack
Juliet: Recall your past sins.     → pop from Romeo's stack into Romeo's value
```

`Remember` pushes any expression onto the listener's stack.
`Recall` pops from the listener's stack into their value. Popping empty stack = runtime error.

---

## Stage Directions

Grammar-confirmed for the forms below. Empirically confirmed for the runtime errors.

```
[Enter Romeo and Juliet]           → bring characters on stage
[Exit Romeo]                       → remove one character
[Exeunt Romeo and Juliet]          → remove multiple characters
[Exeunt]                           → remove all characters
[A pause]                          → debugger breakpoint
```

Multi-character `Enter` and `Exeunt` forms are legal grammar.

Cannot `[Enter]` a character already on stage — runtime error.
Cannot remove a character not on stage — runtime error.

---

## Grammar Gotchas

Grammar-confirmed from `shakespeare.ebnf`.

- Keywords are case-insensitive in this interpreter grammar.
- Questions must use the form `be value comparative value?`; the trailing `?` is part of the syntax.
- `If so,` and `If not,` are the conditional prefixes; the comma is part of the grammar.
- Assignments target second person only; the grammar does not permit assigning directly to a named character.
- Gotos target `scene` plus a Roman numeral, and the accepted lead-ins are `Let us`, `We shall`, or `We must` with `proceed to` or `return to`.
- `Speak your mind!`, `Open your heart!`, `Open your mind!`, and `Listen to your heart!` are possessive-second-person forms in the grammar, not free variations.
- `Recall ...` accepts essentially any text up to punctuation after `Recall`; the parser does not care about the wording of the memory phrase.
- Stage directions are exactly `[Enter ...]`, `[Exit ...]`, `[Exeunt ...]`, and `[A pause]`.
- Character lists in stage directions are either a single name or a comma-separated list ending in `and Name`.

---

## Interpreter Quirks

Empirically confirmed behavior of the local Python interpreter that is easy to miss if you
read only the grammar:

- `Listen to your heart!` is stricter than a generic "read integer" description suggests: no leading whitespace, no sign prefix, and repeated reads worked with newline-delimited input but not with space- or tab-delimited followups.
- `Speak your mind!` uses Python text output semantics for valid code points. For example, code point `255` emitted UTF-8 bytes `195 191`, and code point `256` emitted `196 128`.
- `Speak your mind!` emits a raw newline for code point `10`.
- Invalid character codes such as `-1` fail immediately instead of being wrapped or truncated.

---

## Control Flow

### Conditional (global boolean)

Grammar-confirmed for syntax. Empirically confirmed that every question overwrites one shared
global boolean used by later `If so,` / `If not,` sentences.

Questions set the global boolean:
```
Juliet: Are you better than nothing?       → global_boolean = (Romeo > 0)
Juliet: Am I as good as nothing?           → global_boolean = (Juliet == 0)
```

Comparatives: `better`/`bigger`/`more [positive adj]` → `>`; `worse`/`smaller`/`more [negative adj]` → `<`; `as [adj] as` → `==`.

Full comparative vocabulary in the grammar:

- Positive comparisons: `better`, `bigger`, `fresher`, `friendlier`, `nicer`, `jollier`, `more <positive adjective>`
- Negative comparisons: `worse`, `smaller`, `punier`, `more <negative adjective>`
- Equality comparisons: `as <negative adjective or positive/neutral adjective> as`

Conditionals use the global boolean:
```
Juliet: If so, speak your mind!            → only if global_boolean is True
Juliet: If not, let us return to scene I.  → only if global_boolean is False
```

### Goto

Grammar-confirmed for scene-target syntax. Empirically confirmed that scene lookup is act-local
at runtime: attempting to jump from one act to a scene number that exists only in another act
fails as "Scene ... does not exist."

```
Juliet: Let us proceed to scene III.
Juliet: Let us return to scene I.
Juliet: If so, let us proceed to scene II.
Juliet: If not, let us return to scene I.
```

**Gotos can only jump within the current act.** Cannot jump between acts.
Jumping to a non-existent scene = runtime error.

---

## Common Idioms

These are project-oriented idioms built on the verified semantics above, not additional grammar
rules.

### Loop (read input until EOF)
```
Scene I: The reading loop.

Juliet: Open your mind!
Juliet: Are you as good as a pig?       ← is Romeo == -1 (EOF)?
Romeo: If so, let us proceed to scene III.
... process Romeo's value ...
Romeo: Let us return to scene I.

Scene III: Done.
```
EOF returns -1. `a pig` = -1, so `Are you as good as a pig?` checks for EOF.

### Output a string character by character
Each character stores one ASCII value, computed once via adjective arithmetic, then output:
```
Juliet: You are as good as [value expression].
Romeo: Speak your mind!
```

### Reuse a value multiple times
```
Juliet: Remember yourself!         ← push Romeo's value
... change Romeo's value ...
Juliet: Recall your past glory.    ← restore Romeo's original value
Romeo: Speak your mind!
```

### Fibonacci / accumulator pattern
Two characters trade values:
```
Romeo: Thou art as noble as the sum of myself and thee.   ← Juliet = Romeo + Juliet
```

### Modulo (divisibility test)
```
Juliet: Is the remainder of the quotient between Romeo and me as good as nothing?
```
If true (remainder == 0), Romeo is divisible by Juliet.

---

## Critical Constraints

1. **Second-person pronouns need exactly one other on-stage character**. This is a pronoun-resolution rule, not a global two-character stage limit.
2. **Gotos cannot cross act boundaries** — can only jump to scenes within the current act.
3. **One global boolean** — every question overwrites it; conditionals always test the most recent question's result.
4. **Single file** — the entire SPL program is one `.spl` file; there is no import or include mechanism.
5. **Integer only** — all values are integers; no floats.
6. **EOF returns −1** for character input (`Open your mind!`). Numeric input on EOF = runtime error.
7. **Stack is per-character** — each character has their own independent stack.
8. **Characters retain values off-stage** — can reference their value in expressions even when not on stage.

---

## Running the Interpreter

```bash
shakespeare run shakedown.spl < input.md   # pipe markdown as stdin
shakespeare run shakedown.spl              # interactive stdin
shakespeare debug shakedown.spl            # step-through debugger
shakespeare console                        # REPL
```

### Interpreter CLI vs SPL Program Arguments

The `shakespeare` interpreter has its own CLI surface:

- `shakespeare [OPTIONS] COMMAND [ARGS]...`
- Commands include `run`, `debug`, and `console`
- Documented options include `--characters`, `--input-style`, and `--output-style`

For SPL code itself, this reference documents only standard input operations:

- `Open your mind!` for character input
- `Listen to your heart!` for integer input

There is no documented SPL-level `argv` or built-in CLI-flag mechanism in the official CLI/API docs. That means Shakedown should treat the SPL program as a stdin/stdout transformation engine and put user-facing flags in a wrapper command, not inside the SPL play.

Sources:

- <https://shakespearelang.com/1.0/CLI/>
- <https://shakespearelang.com/1.0/API/>
