# SPL Style Lexicon

This companion doc is for expressive generation, not parser truth.
For legality and hard grammar constraints, use `docs/research/shakedown-spl-reference.md`.

Every token listed here is accepted by the installed interpreter grammar.
Phrases are labeled as either `example-attested` or `grammar-valid composition`.

## Purpose

Use this document when you want SPL code to sound varied, vivid, and deliberately chosen
instead of defaulting to repetitive fillers such as `big big big cat`.

Use the main reference for:

- exact legality
- composition constraints
- sign and magnitude rules

Use this companion for:

- palette selection
- phrase variety
- substitution ideas that preserve validity

## Comparative Palette

### Upbeat Comparisons

- `better than`
- `bigger than`
- `fresher than`
- `friendlier than`
- `nicer than`
- `jollier than`
- `more <positive adjective> than`

### Hostile Comparisons

- `worse than`
- `smaller than`
- `punier than`
- `more <negative adjective> than`

### Equality Forms

- `as <positive adjective> as`
- `as <neutral adjective> as`
- `as <negative adjective> as`

## Semantic Palettes

These are style groupings only. They are not parser-enforced semantic categories.

### Noble / Radiant

Adjectives:
`amazing`, `healthy`, `honest`, `noble`, `peaceful`, `fine`, `golden`, `warm`, `mighty`, `proud`, `rich`, `trustworthy`

Nouns:
`hero`, `angel`, `Lord`, `King`, `rose`, `flower`, `joy`, `happiness`, `summer's day`, `kingdom`

Use when:
- you want grandeur, virtue, warmth, or ceremonial language

### Pastoral / Natural

Adjectives:
`sunny`, `sweet`, `gentle`, `beautiful`, `fair`, `smooth`, `green`, `rural`, `little`, `yellow`

Nouns:
`summer's day`, `flower`, `rose`, `tree`, `wind`, `moon`, `morning`, `pony`, `sky`, `stone wall`

Use when:
- you want open-air, seasonal, or landscape imagery

### Domestic / Familial

Adjectives:
`lovely`, `pretty`, `gentle`, `fair`, `warm`, `healthy`, `happy`

Nouns:
`mother`, `father`, `brother`, `sister`, `son`, `daughter`, `aunt`, `uncle`, `nephew`, `niece`, `cousin`, `grandmother`, `grandfather`

Use when:
- you want intimate, household, or kinship-centered language

### Grotesque / Abusive

Adjectives:
`fat-kidneyed`, `fatherless`, `oozing`, `rotten`, `smelly`, `vile`, `horrid`, `disgusting`, `dirty`, `hairy`, `half-witted`, `stinking`, `cursed`, `miserable`

Nouns:
`flirt-gill`, `codpiece`, `toad`, `blister`, `coward`, `pig`, `plague`, `devil`, `curse`, `goat`, `wolf`, `hate`

Use when:
- you want open insult, decay, or plague-ridden imagery

### Martial / Catastrophic

Adjectives:
`mighty`, `bold`, `brave`, `cunning`, `foul`, `evil`, `villainous`

Nouns:
`war`, `death`, `devil`, `wolf`, `curse`, `famine`, `starvation`, `hero`, `kingdom`

Use when:
- you want conflict, danger, command, or ruin

## Example-Attested Phrases

These appear directly in the bundled examples or sample plays.

- `example-attested`: `a proud rich trustworthy hero`
- `example-attested`: `a lovely fine sunny summer's day`
- `example-attested`: `a charming handsome healthy lovely pretty noble angel`
- `example-attested`: `a horrible disgusting rotten oozing blister`
- `example-attested`: `a dirty smelly toad`
- `example-attested`: `a cursed miserable dirty disgusting hairy half-witted lying coward`
- `example-attested`: `a sunny summer's day`
- `example-attested`: `a red rose`
- `example-attested`: `a disgusting dusty evil fat-kidneyed fatherless foul ...`
- `example-attested`: `a stone wall`
- `example-attested`: `a flirt-gill`
- `example-attested`: `the sum of an amazing healthy honest noble peaceful fine Lord and a lovely sweet golden summer's day`
- `example-attested`: `a rich proud noble roman`
- `example-attested`: `a huge stone wall`
- `example-attested`: `a big lovely sweet delicious rich plum`

## Grammar-Valid Composition Patterns

These patterns are newly composed from grammar-backed tokens and composition rules.

### Positive / Neutral Phrase Patterns

- `grammar-valid composition`: `a noble peaceful golden hero`
- `grammar-valid composition`: `a lovely gentle summer's day`
- `grammar-valid composition`: `a fair warm golden rose`
- `grammar-valid composition`: `a rich proud noble kingdom`
- `grammar-valid composition`: `a beautiful rural morning`

### Negative Phrase Patterns

- `grammar-valid composition`: `a vile smelly plague`
- `grammar-valid composition`: `a cursed rotten devil`
- `grammar-valid composition`: `a dirty hairy wolf`
- `grammar-valid composition`: `a miserable stinking pig`
- `grammar-valid composition`: `a horrid oozing blister`

### Neutral-Heavy Utility Patterns

- `grammar-valid composition`: `a huge stone wall`
- `grammar-valid composition`: `a little yellow flower`
- `grammar-valid composition`: `a large rural town`
- `grammar-valid composition`: `a green tree`
- `grammar-valid composition`: `a black wind`

## Safe Substitutions For Agents

### Preserve Numeric Meaning

- Preserve adjective count when magnitude must remain the same.
- Preserve noun sign when positive vs negative value must remain the same.
- Neutral adjectives are useful style swaps because they preserve sign while still changing the surface text.

### Preserve Parser Validity

- Positive and neutral nouns only accept positive or neutral adjectives.
- Negative nouns only accept negative or neutral adjectives.
- Multi-word nouns such as `summer's day` and `stone wall` must stay intact.

### Vary Surface Texture

- Swap one bright adjective cluster for another:
  - `golden warm peaceful`
  - `lovely sweet sunny`
  - `proud rich noble`
- Swap one hostile cluster for another:
  - `dirty smelly`
  - `cursed miserable`
  - `horrid rotten oozing`
- Mix neutral structure words into value phrases for texture:
  - `huge stone wall`
  - `large rural town`
  - `little yellow flower`

## Anti-Patterns

- Do not mix positive adjectives into negative noun phrases.
- Do not mix negative adjectives into positive noun phrases.
- Do not invent Shakespeare-sounding words that are not in the grammar.
- Do not break multi-word nouns into free substitutions.
- Do not treat these palettes as semantic types enforced by the parser.
- Do not change adjective count casually when numeric magnitude matters.

## Source And Label Policy

- `example-attested` means the phrase appears in a bundled example or sample play.
- `grammar-valid composition` means the phrase is newly assembled only from grammar-backed tokens.
- When legality and style guidance conflict, the canonical reference wins.
