# SPL Style Lexicon

This companion doc is for expressive generation, not parser truth and not codegen policy.
For legality and hard grammar constraints, use `docs/spl/reference.md`.
For implementation policy on choosing and reusing value phrases, use
`docs/spl/codegen-style-guide.md`.

Every token listed here is accepted by the installed interpreter grammar.
Phrases are labeled as either `example-attested` or `grammar-valid composition`.

## How To Use This Doc

Use the sections in this order:

1. **Inventories**: find the complete set of legal comparatives, adjectives, and nouns.
2. **Construction Rules**: verify which classes can be combined legally.
3. **Phrasebook**: choose an attested phrase or a grammar-valid pattern.
4. **Palettes**: pick a surface texture if you want a particular tone.
5. **Agent Patterns**: vary expression while preserving sign and magnitude.

To keep this document closer to MECE:

- inventories are exhaustive
- construction rules are separate from inventories
- attested phrases are separate from newly composed patterns
- semantic palettes are illustrative subsets, not another exhaustive inventory

## Comparative Inventory

### Positive Comparatives

These all map to the grammar's positive-comparative path.

- `better than`
- `bigger than`
- `fresher than`
- `friendlier than`
- `nicer than`
- `jollier than`
- `more <positive adjective> than`

### Negative Comparatives

These all map to the grammar's negative-comparative path.

- `worse than`
- `smaller than`
- `punier than`
- `more <negative adjective> than`

### Equality Comparatives

These all map to the grammar's neutral/equality-comparative path.

- `as <positive adjective> as`
- `as <neutral adjective> as`
- `as <negative adjective> as`

## Adjective Inventory

These inventories are exhaustive for the installed grammar.

### Positive Adjectives

`amazing`, `beautiful`, `blossoming`, `bold`, `brave`, `charming`, `clearest`, `cunning`, `cute`, `delicious`, `embroidered`, `fair`, `fine`, `gentle`, `golden`, `good`, `handsome`, `happy`, `healthy`, `honest`, `lovely`, `loving`, `mighty`, `noble`, `peaceful`, `pretty`, `prompt`, `proud`, `reddest`, `rich`, `smooth`, `sunny`, `sweet`, `sweetest`, `trustworthy`, `warm`

### Neutral Adjectives

`big`, `black`, `blue`, `bluest`, `bottomless`, `furry`, `green`, `hard`, `huge`, `large`, `little`, `normal`, `old`, `purple`, `red`, `rural`, `small`, `tiny`, `white`, `yellow`

### Negative Adjectives

`bad`, `cowardly`, `cursed`, `damned`, `dirty`, `disgusting`, `distasteful`, `dusty`, `evil`, `fat-kidneyed`, `fatherless`, `fat`, `foul`, `hairy`, `half-witted`, `horrible`, `horrid`, `infected`, `lying`, `miserable`, `misused`, `oozing`, `rotten`, `smelly`, `snotty`, `sorry`, `stinking`, `stuffed`, `stupid`, `vile`, `villainous`, `worried`

## Noun Inventory

These inventories are exhaustive for the installed grammar.

### Positive Nouns

`Heaven`, `King`, `Lord`, `angel`, `flower`, `happiness`, `joy`, `plum`, `hero`, `rose`, `kingdom`, `pony`, `summer's day`

### Neutral Nouns

`animal`, `aunt`, `brother`, `cat`, `chihuahua`, `cousin`, `cow`, `daughter`, `door`, `face`, `father`, `fellow`, `granddaughter`, `grandfather`, `grandmother`, `grandson`, `hair`, `hamster`, `horse`, `lamp`, `lantern`, `mistletoe`, `moon`, `morning`, `mother`, `nephew`, `niece`, `nose`, `purse`, `road`, `roman`, `sister`, `sky`, `son`, `squirrel`, `stone wall`, `thing`, `town`, `tree`, `uncle`, `wind`

### Negative Nouns

`Hell`, `Microsoft`, `bastard`, `beggar`, `blister`, `codpiece`, `coward`, `curse`, `death`, `devil`, `draught`, `famine`, `flirt-gill`, `goat`, `hate`, `hog`, `hound`, `leech`, `lie`, `pig`, `plague`, `starvation`, `toad`, `war`, `wolf`

## Phrase Construction Rules

These rules are the bridge between the exhaustive inventories and the expressive phrasebook.

### Sign Path Rules

- Positive noun phrases use positive or neutral adjectives with positive or neutral nouns.
- Negative noun phrases use negative or neutral adjectives with negative nouns.
- Neutral nouns still travel through the positive noun-phrase path.
- Multi-word nouns such as `summer's day` and `stone wall` must stay intact.

### Surface Form Rules

- A noun phrase may start with an article: `a`, `an`, or `the`.
- A noun phrase may also start with a possessive such as `my`, `thy`, `your`, `his`, `her`, `its`, or `their`.
- Adjective order is stylistic, not parser-significant.
- Adjective count controls magnitude. Changing count changes the numeric value.

### Safe Variation Rules

- To preserve sign, keep the noun on the same sign path.
- To preserve magnitude, keep the adjective count unchanged.
- Neutral adjectives are usually the lowest-risk stylistic swap when you want to change texture
  without changing sign.
- Swapping a positive noun for a neutral noun preserves positive sign but changes imagery.

## Semantic Palettes

These palettes are representative subsets, not exhaustive lists.

### Noble / Radiant

Representative adjectives:
`amazing`, `healthy`, `honest`, `noble`, `peaceful`, `fine`, `golden`, `warm`, `mighty`, `proud`, `rich`, `trustworthy`

Representative nouns:
`hero`, `angel`, `Lord`, `King`, `rose`, `flower`, `joy`, `happiness`, `summer's day`, `kingdom`

Typical use:
- grandeur
- virtue
- ceremony
- stately praise

### Pastoral / Natural

Representative adjectives:
`sunny`, `sweet`, `gentle`, `beautiful`, `fair`, `smooth`, `green`, `rural`, `little`, `yellow`

Representative nouns:
`summer's day`, `flower`, `rose`, `tree`, `wind`, `moon`, `morning`, `pony`, `sky`, `stone wall`

Typical use:
- seasonal imagery
- open-air calm
- fields, gardens, weather, and landscape

### Domestic / Familial

Representative adjectives:
`lovely`, `pretty`, `gentle`, `fair`, `warm`, `healthy`, `happy`

Representative nouns:
`mother`, `father`, `brother`, `sister`, `son`, `daughter`, `aunt`, `uncle`, `nephew`, `niece`, `cousin`, `grandmother`, `grandfather`

Typical use:
- intimacy
- household imagery
- kinship language

### Grotesque / Abusive

Representative adjectives:
`fat-kidneyed`, `fatherless`, `oozing`, `rotten`, `smelly`, `vile`, `horrid`, `disgusting`, `dirty`, `hairy`, `half-witted`, `stinking`, `cursed`, `miserable`

Representative nouns:
`flirt-gill`, `codpiece`, `toad`, `blister`, `coward`, `pig`, `plague`, `devil`, `curse`, `goat`, `wolf`, `hate`

Typical use:
- direct insult
- decay
- filth
- plague and corruption

### Martial / Catastrophic

Representative adjectives:
`mighty`, `bold`, `brave`, `cunning`, `foul`, `evil`, `villainous`

Representative nouns:
`war`, `death`, `devil`, `wolf`, `curse`, `famine`, `starvation`, `hero`, `kingdom`

Typical use:
- danger
- command
- threat
- ruin

## Attested Phrasebook

These phrases appear directly in bundled examples or sample plays.

### Short Attested Phrases

- `example-attested`: `a sunny summer's day`
- `example-attested`: `a red rose`
- `example-attested`: `a stone wall`
- `example-attested`: `a flirt-gill`
- `example-attested`: `a dirty smelly toad`

### Dense Positive Attested Phrases

- `example-attested`: `a proud rich trustworthy hero`
- `example-attested`: `a lovely fine sunny summer's day`
- `example-attested`: `a charming handsome healthy lovely pretty noble angel`
- `example-attested`: `a big lovely sweet delicious rich plum`
- `example-attested`: `a rich proud noble roman`

### Dense Negative Attested Phrases

- `example-attested`: `a horrible disgusting rotten oozing blister`
- `example-attested`: `a cursed miserable dirty disgusting hairy half-witted lying coward`

### Compound Attested Patterns

- `example-attested`: `the sum of an amazing healthy honest noble peaceful fine Lord and a lovely sweet golden summer's day`
- `example-attested`: `the sum of a rich proud noble roman and a huge stone wall`

## Grammar-Valid Composition Patterns

These phrases are newly composed from grammar-backed tokens and construction rules.

### Positive / Neutral Patterns

- `grammar-valid composition`: `a noble peaceful golden hero`
- `grammar-valid composition`: `a lovely gentle summer's day`
- `grammar-valid composition`: `a fair warm golden rose`
- `grammar-valid composition`: `a rich proud noble kingdom`
- `grammar-valid composition`: `a beautiful rural morning`
- `grammar-valid composition`: `a healthy honest Lord`

### Negative Patterns

- `grammar-valid composition`: `a vile smelly plague`
- `grammar-valid composition`: `a cursed rotten devil`
- `grammar-valid composition`: `a dirty hairy wolf`
- `grammar-valid composition`: `a miserable stinking pig`
- `grammar-valid composition`: `a horrid oozing blister`
- `grammar-valid composition`: `a fatherless half-witted coward`

### Neutral-Heavy Utility Patterns

- `grammar-valid composition`: `a huge stone wall`
- `grammar-valid composition`: `a little yellow flower`
- `grammar-valid composition`: `a large rural town`
- `grammar-valid composition`: `a green tree`
- `grammar-valid composition`: `a black wind`
- `grammar-valid composition`: `a furry hamster`

### Comparison Patterns

- `grammar-valid composition`: `as noble as a golden hero`
- `grammar-valid composition`: `as sweet as a sunny summer's day`
- `grammar-valid composition`: `more villainous than a rotten wolf`
- `grammar-valid composition`: `friendlier than a gentle pony`
- `grammar-valid composition`: `punier than a dirty pig`

## Agent Patterns

### Preserve Sign

- Positive sign:
  choose a positive or neutral noun and only positive or neutral adjectives
- Negative sign:
  choose a negative noun and only negative or neutral adjectives

### Preserve Magnitude

- Keep adjective count unchanged.
- Swap adjective texture, not adjective count.
- Swap nouns only within the same sign path.

### Avoid Repetition

- Rotate between positive nouns:
  `hero`, `angel`, `Lord`, `rose`, `summer's day`, `kingdom`
- Rotate between neutral textures:
  `stone wall`, `town`, `wind`, `morning`, `tree`, `hair`
- Rotate between hostile nouns:
  `blister`, `toad`, `coward`, `pig`, `plague`, `devil`
- Rotate adjective clusters:
  - bright: `golden warm peaceful`
  - soft: `lovely sweet sunny`
  - stately: `proud rich noble`
  - filthy: `dirty smelly`
  - ruined: `horrid rotten oozing`

### Good Default Templates

- praise:
  `a <positive cluster> <positive noun>`
- insult:
  `a <negative cluster> <negative noun>`
- scenic / pastoral:
  `a <positive-or-neutral cluster> <summer's day | rose | flower | morning | wind>`
- utility / arithmetic:
  `a <neutral cluster> <stone wall | town | tree | wind | moon>`

## Anti-Patterns

- Do not mix positive adjectives into negative noun phrases.
- Do not mix negative adjectives into positive noun phrases.
- Do not invent Shakespeare-sounding words that are not in the grammar.
- Do not break multi-word nouns into free substitutions.
- Do not treat these palettes as parser-enforced semantic categories.
- Do not change adjective count casually when numeric magnitude matters.
- Do not assume a vivid phrase is safe if you have not checked its sign path.

## Source And Label Policy

- `example-attested` means the phrase appears in a bundled example or sample play.
- `grammar-valid composition` means the phrase is newly assembled only from grammar-backed tokens.
- When legality and style guidance conflict, the canonical reference wins.
