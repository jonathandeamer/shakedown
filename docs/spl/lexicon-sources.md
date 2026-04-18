# SPL Style Lexicon Sources

## Grammar-backed inventories

- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:33`
  Positive comparatives: `better`, `bigger`, `fresher`, `friendlier`, `nicer`,
  `jollier`, `more <positive adjective>`
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:35`
  Negative comparatives: `punier`, `smaller`, `worse`, `more <negative adjective>`
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:39`
  Negative adjectives
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:73`
  Neutral adjectives
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:94`
  Positive adjectives
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:131`
  Negative nouns
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:157`
  Neutral nouns
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:199`
  Positive nouns
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:374`
  Negative noun phrases = article/possessive + negative/neutral adjectives + negative noun
- `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf:376`
  Positive noun phrases = article/possessive + positive/neutral adjectives + positive/neutral noun

## Example-attested phrases

| Phrase | Source file | Why it is useful |
|---|---|---|
| `a proud rich trustworthy hero` | `/home/ec2-user/spl-1.2.1/examples/shakesbeer.spl:26` | Strong positive/martial cluster |
| `a lovely fine sunny summer's day` | `/home/ec2-user/spl-1.2.1/examples/shakesbeer.spl:51` | Compact positive pastoral phrase |
| `a charming handsome healthy lovely pretty noble angel` | `/home/ec2-user/spl-1.2.1/examples/shakesbeer.spl:49` | Dense positive phrase using only valid positive adjectives |
| `a horrible disgusting rotten oozing blister` | `/home/ec2-user/spl-1.2.1/examples/shakesbeer.spl:55` | Dense negative phrase with clear sign path |
| `a dirty smelly toad` | `/home/ec2-user/spl-1.2.1/examples/shakesbeer.spl:63` | Short hostile phrase |
| `a cursed miserable dirty disgusting hairy half-witted lying coward` | `/home/ec2-user/spl-1.2.1/examples/shakesbeer.spl:56` | Long negative phrase that stays grammar-valid |
| `a sunny summer's day` | `/home/ec2-user/spl-1.2.1/examples/primes.spl:28` | Minimal positive pastoral phrase |
| `a red rose` | `/home/ec2-user/spl-1.2.1/examples/primes.spl:49` | Minimal positive symbolic phrase |
| `a stone wall` | `/home/ec2-user/spl-1.2.1/examples/reverse.spl:22` | Multi-word neutral noun used in arithmetic |
| `a flirt-gill` | `/home/ec2-user/spl-1.2.1/examples/reverse.spl:23` | Distinctive negative noun |
| `the sum of an amazing healthy honest noble peaceful fine Lord and a lovely sweet golden summer's day` | `/home/ec2-user/shakespearelang/shakespearelang/tests/sample_plays/parse_everything.spl:921` | High-signal attested phrase pattern combining two positive phrases |
| `a rich proud noble roman` | `/home/ec2-user/shakespearelang/shakespearelang/tests/sample_plays/sierpinski.spl:429` | Positive phrase using a neutral noun |
| `a huge stone wall` | `/home/ec2-user/shakespearelang/shakespearelang/tests/sample_plays/sierpinski.spl:429` | Neutral-heavy phrase with strong texture |
| `a big lovely sweet delicious rich plum` | `/home/ec2-user/shakespearelang/shakespearelang/tests/sample_plays/sierpinski.spl:60` | Mixed positive/neutral phrase around a positive noun |

## Candidate palettes

- noble / radiant:
  `amazing`, `healthy`, `honest`, `noble`, `peaceful`, `fine`, `golden`, `warm`,
  `hero`, `angel`, `Lord`, `King`, `rose`, `summer's day`
- pastoral / natural:
  `sunny`, `sweet`, `gentle`, `beautiful`, `fair`, `green`, `rural`, `flower`,
  `rose`, `tree`, `wind`, `moon`, `morning`, `summer's day`
- domestic / familial:
  `mother`, `father`, `brother`, `sister`, `son`, `daughter`, `aunt`, `uncle`,
  `nephew`, `niece`, `cousin`, `grandmother`, `grandfather`
- grotesque / abusive:
  `fat-kidneyed`, `fatherless`, `oozing`, `rotten`, `smelly`, `vile`, `flirt-gill`,
  `codpiece`, `toad`, `blister`, `coward`, `pig`, `plague`
- martial / catastrophic:
  `mighty`, `bold`, `brave`, `war`, `death`, `devil`, `wolf`, `curse`, `famine`,
  `starvation`, `hero`, `kingdom`

## Provenance labels

- `example-attested`: the wording appears in an example or sample play
- `grammar-valid composition`: newly assembled wording built only from grammar-backed tokens
  and composition rules
