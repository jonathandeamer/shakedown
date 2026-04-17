# SPL Language Reference

Quick reference for writing Shakespeare Programming Language programs in Shakedown.
Interpreter: `shakespearelang` (`shakespeare run play.spl`).
Full grammar: `~/shakespearelang/shakespearelang/shakespeare.ebnf`.
Worked examples: `~/spl-1.2.1/examples/`.

---

## Program Structure

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

Valid names are exactly the `character` alternatives in the installed grammar. This interpreter accepts:

`Achilles`, `Adonis`, `Adriana`, `Aegeon`, `Aemilia`, `Agamemnon`, `Agrippa`, `Ajax`, `Alonso`, `Andromache`, `Angelo`, `Antiochus`, `Antonio`, `Arthur`, `Autolycus`, `Balthazar`, `Banquo`, `Beatrice`, `Benedick`, `Benvolio`, `Bianca`, `Brabantio`, `Brutus`, `Capulet`, `Cassandra`, `Cassius`, `Christopher Sly`, `Cicero`, `Claudio`, `Claudius`, `Cleopatra`, `Cordelia`, `Cornelius`, `Cressida`, `Cymberline`, `Demetrius`, `Desdemona`, `Dionyza`, `Doctor Caius`, `Dogberry`, `Don John`, `Don Pedro`, `Donalbain`, `Dorcas`, `Duncan`, `Egeus`, `Emilia`, `Escalus`, `Falstaff`, `Fenton`, `Ferdinand`, `Ford`, `Fortinbras`, `Francisca`, `Friar John`, `Friar Laurence`, `Gertrude`, `Goneril`, `Hamlet`, `Hecate`, `Hector`, `Helen`, `Helena`, `Hermia`, `Hermonie`, `Hippolyta`, `Horatio`, `Imogen`, `Isabella`, `John of Gaunt`, `John of Lancaster`, `Julia`, `Juliet`, `Julius Caesar`, `King Henry`, `King John`, `King Lear`, `King Richard`, `Lady Capulet`, `Lady Macbeth`, `Lady Macduff`, `Lady Montague`, `Lennox`, `Leonato`, `Luciana`, `Lucio`, `Lychorida`, `Lysander`, `Macbeth`, `Macduff`, `Malcolm`, `Mariana`, `Mark Antony`, `Mercutio`, `Miranda`, `Mistress Ford`, `Mistress Overdone`, `Mistress Page`, `Montague`, `Mopsa`, `Oberon`, `Octavia`, `Octavius Caesar`, `Olivia`, `Ophelia`, `Orlando`, `Orsino`, `Othello`, `Page`, `Pantino`, `Paris`, `Pericles`, `Pinch`, `Polonius`, `Pompeius`, `Portia`, `Priam`, `Prince Henry`, `Prospero`, `Proteus`, `Publius`, `Puck`, `Queen Elinor`, `Regan`, `Robin`, `Romeo`, `Rosalind`, `Sebastian`, `Shallow`, `Shylock`, `Slender`, `Solinus`, `Stephano`, `Thaisa`, `The Abbot of Westminster`, `The Apothecary`, `The Archbishop of Canterbury`, `The Duke of Milan`, `The Duke of Venice`, `The Ghost`, `Theseus`, `Thurio`, `Timon`, `Titania`, `Titus`, `Troilus`, `Tybalt`, `Ulysses`, `Valentine`, `Venus`, `Vincentio`, `Viola`

Each character has:
- A **value** (integer, initialised to 0)
- A **stack** (list of integers, initially empty)

---

## Pronouns

`I`, `me`, and `myself` refer to the speaker and work when only the speaker is on stage. `you`, `thou`, `thee`, `yourself`, and `thyself` require exactly one other on-stage character; otherwise evaluation is ambiguous or targets nobody and raises a runtime error.

| Pronoun | Refers to |
|---------|-----------|
| `I`, `me`, `myself` | the speaker |
| `you`, `thou`, `thee`, `yourself`, `thyself` | the other character |
| Character name | that character's current value (even if off stage) |

---

## Encoding Constants

Numbers are encoded as noun phrases. The value is:
- **Positive noun**: `2^(number of adjectives)` — minimum 2 with one adjective
- **Negative noun**: `-(2^(number of adjectives))`
- `nothing` or `zero` → 0

Adjective count is the total number of adjectives (including neutral ones) before the noun.

**Rule: value = sign × 2^(adjective_count)**
Bare noun (no adjectives) = ±1. Each adjective doubles.

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

---

## Operations

### Assignment

```
Juliet: You are as good as nothing.          → Romeo = 0
Juliet: Thou art as lovely as a cat!         → Romeo = 1
Juliet: You are the sum of a cat and a cat.  → Romeo = 1 + 1 = 2
```

The speaker assigns to the listener. `as ADJECTIVE as` before the value is cosmetic.

### Arithmetic

| Operation | Syntax |
|-----------|--------|
| Addition | `the sum of A and B` |
| Subtraction | `the difference between A and B` |
| Multiplication | `the product of A and B` |
| Integer division | `the quotient between A and B` |
| Modulo | `the remainder of the quotient between A and B` |
| Square | `the square of A` |
| Cube | `the cube of A` |
| Square root | `the square root of A` (truncated; errors on negative) |
| Factorial | `the factorial of A` (errors on negative) |
| Double | `twice A` |

Division truncates toward zero (not floor division). Division by zero is a runtime error.

### I/O

```
Juliet: Speak your mind!           → print chr(Romeo's value)
Juliet: Open your heart!           → print Romeo's value as integer
Juliet: Open your mind!            → Romeo = ord(next char from stdin); -1 at EOF
Juliet: Listen to your heart!      → Romeo = next integer from stdin
```

Always operates on the **listener** (the other character on stage).

### Stack

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

```
[Enter Romeo and Juliet]           → bring characters on stage
[Exit Romeo]                       → remove one character
[Exeunt Romeo and Juliet]          → remove multiple characters
[Exeunt]                           → remove all characters
[A pause]                          → debugger breakpoint
```

Cannot `[Enter]` a character already on stage — runtime error.
Cannot remove a character not on stage — runtime error.

---

## Control Flow

### Conditional (global boolean)

Questions set the global boolean:
```
Juliet: Are you better than nothing?       → global_boolean = (Romeo > 0)
Juliet: Am I as good as nothing?           → global_boolean = (Juliet == 0)
```

Comparatives: `better`/`bigger`/`more [positive adj]` → `>`; `worse`/`smaller`/`more [negative adj]` → `<`; `as [adj] as` → `==`.

Conditionals use the global boolean:
```
Juliet: If so, speak your mind!            → only if global_boolean is True
Juliet: If not, let us return to scene I.  → only if global_boolean is False
```

### Goto

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

1. **Exactly 2 characters on stage** when using second-person pronouns (`you`, `thou`, etc.) — otherwise runtime error.
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
