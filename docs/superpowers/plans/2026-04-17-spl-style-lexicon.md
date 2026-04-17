# SPL Style Lexicon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the canonical SPL reference with missing lexicon legality facts and add a separate style companion that helps agents generate vivid but grammar-valid SPL phrases.

**Architecture:** Keep `docs/research/shakedown-spl-reference.md` as the single legality source for hard lexicon constraints, and add `docs/research/shakedown-spl-style-lexicon.md` as a generation-oriented companion. Mine all vocabulary from the installed grammar and all phrase examples from bundled example plays or sample plays so the style layer never outruns parser truth.

**Tech Stack:** Markdown docs, local `shakespeare.ebnf`, bundled SPL example corpus, git

---

### Task 1: Inventory Missing Hard Lexicon Facts

**Files:**
- Modify: `docs/research/shakedown-spl-reference.md`
- Reference: `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf`
- Reference: `/home/ec2-user/spl-1.2.1/examples/`
- Reference: `/home/ec2-user/shakespearelang/shakespearelang/tests/sample_plays/`

- [ ] **Step 1: Read the current lexicon portions of the canonical reference**

Run: `nl -ba docs/research/shakedown-spl-reference.md | sed -n '90,260p'`
Expected: the current adjective, noun, arithmetic, I/O, grammar-gotchas, and related lexicon sections with line numbers.

- [ ] **Step 2: Read the grammar sections that define adjective, noun, and comparative inventories**

Run: `nl -ba /home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf | sed -n '20,220p'`
Expected: the positive/negative/neutral comparative definitions plus adjective and noun inventories with exact grammar text.

Run: `nl -ba /home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf | sed -n '366,380p'`
Expected: the noun-phrase composition rules showing which adjective classes may combine with which noun classes.

- [ ] **Step 3: Inventory the currently missing hard facts**

Use this working checklist:

```text
missing-hard-facts:
- comparative-only words not yet surfaced clearly in the reference:
  fresher, friendlier, nicer, jollier, punier
- exact noun-phrase composition rules:
  positive_or_neutral adjectives + positive_or_neutral nouns
  negative_or_neutral adjectives + negative nouns
- multi-word noun reminder:
  summer's day, stone wall
- noun-phrase starters:
  article or possessive
```

- [ ] **Step 4: Confirm those facts are grammar-backed before doc changes**

Run: `rg -n "fresher|friendlier|nicer|jollier|punier|positive_noun_phrase|negative_noun_phrase|summer's|stone" /home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf`
Expected: direct grammar hits for every missing fact.

- [ ] **Step 5: Commit the implementation plan checkpoint**

```bash
git status --short
git add docs/superpowers/plans/2026-04-17-spl-style-lexicon.md
git commit -m "docs: add SPL style lexicon plan"
```

Expected: a clean commit containing the implementation plan only.

### Task 2: Mine Technically Valid Phrase Material

**Files:**
- Create: `docs/research/2026-04-17-spl-style-lexicon-sources.md`
- Reference: `/home/ec2-user/spl-1.2.1/examples/`
- Reference: `/home/ec2-user/shakespearelang/shakespearelang/tests/sample_plays/`

- [ ] **Step 1: Search the bundled examples for vivid attested phrases**

Run: `rg -n "summer's day|stone wall|flirt-gill|trustworthy|fat-kidneyed|golden|lovely|proud rich|foul smelly|horrid|sunny" /home/ec2-user/spl-1.2.1/examples /home/ec2-user/shakespearelang/shakespearelang/tests/sample_plays -g '*.spl'`
Expected: a compact set of example lines containing reusable attested phrase patterns.

- [ ] **Step 2: Create a source note capturing candidate phrases and provenance**

Create `docs/research/2026-04-17-spl-style-lexicon-sources.md` with this structure:

```md
# SPL Style Lexicon Sources

## Grammar-backed inventories
- source paths:

## Example-attested phrases
| Phrase | Source file | Why it is useful |

## Candidate palettes
- noble / radiant:
- pastoral / natural:
- domestic / familial:
- grotesque / abusive:
- martial / catastrophic:
```

- [ ] **Step 3: Separate attested phrases from newly composed but grammar-valid patterns**

Use this rule in the source note:

```text
- "example-attested" means the wording appears in an example or sample play
- "grammar-valid composition" means the wording is newly assembled only from grammar-backed tokens and allowed composition rules
```

- [ ] **Step 4: Keep the source note small and selective**

Run: `sed -n '1,220p' docs/research/2026-04-17-spl-style-lexicon-sources.md`
Expected: a compact source note with a manageable number of high-signal phrases, not a raw dump of the corpus.

- [ ] **Step 5: Commit the source note**

```bash
git status --short
git add docs/research/2026-04-17-spl-style-lexicon-sources.md
git commit -m "docs: collect SPL style lexicon sources"
```

Expected: the source note is committed on its own.

### Task 3: Update The Canonical Reference

**Files:**
- Modify: `docs/research/shakedown-spl-reference.md`
- Reference: `/home/ec2-user/shakespearelang/shakespearelang/shakespeare.ebnf`
- Reference: `docs/research/2026-04-17-spl-style-lexicon-sources.md`

- [ ] **Step 1: Add missing comparative vocabulary to the reference**

Update `docs/research/shakedown-spl-reference.md` so the comparison guidance explicitly includes:

```md
Positive comparisons:
- better
- bigger
- fresher
- friendlier
- nicer
- jollier
- more <positive adjective>

Negative comparisons:
- worse
- smaller
- punier
- more <negative adjective>
```

- [ ] **Step 2: Add exact noun-phrase composition rules**

Insert concise grammar-backed guidance equivalent to:

```md
- positive noun phrases use positive or neutral adjectives with positive or neutral nouns
- negative noun phrases use negative or neutral adjectives with negative nouns
- noun phrases may start with an article or a possessive
- `summer's day` and `stone wall` are multi-word nouns in the grammar
```

- [ ] **Step 3: Add a pointer to the style companion**

Add a short note such as:

```md
For generation-oriented palettes and phrase suggestions built from this legal vocabulary, see
`docs/research/shakedown-spl-style-lexicon.md`.
```

- [ ] **Step 4: Review the reference for correctness and readability**

Run: `sed -n '90,260p' docs/research/shakedown-spl-reference.md`
Expected: the added lexicon material reads like canonical constraint documentation, not creative-writing advice.

- [ ] **Step 5: Commit the canonical-reference update**

```bash
git status --short
git add docs/research/shakedown-spl-reference.md
git commit -m "docs: expand SPL lexicon reference"
```

Expected: the commit contains only the legality-oriented reference updates.

### Task 4: Write The Style Companion

**Files:**
- Create: `docs/research/shakedown-spl-style-lexicon.md`
- Reference: `docs/research/2026-04-17-spl-style-lexicon-sources.md`
- Reference: `docs/research/shakedown-spl-reference.md`

- [ ] **Step 1: Create the style companion with a clear safety boundary**

Start `docs/research/shakedown-spl-style-lexicon.md` with:

```md
# SPL Style Lexicon

This companion doc is for expressive generation, not parser truth.
For legality and hard grammar constraints, use `docs/research/shakedown-spl-reference.md`.

Every token listed here is accepted by the installed interpreter grammar.
Phrases are labeled as either example-attested or grammar-valid composition.
```

- [ ] **Step 2: Add a writer-facing comparative palette**

Include a compact table or grouped lists for:

```md
- upbeat comparisons
- hostile comparisons
- equality forms
```

using only grammar-backed comparative vocabulary.

- [ ] **Step 3: Add semantic palettes built from valid vocabulary**

Include sections such as:

```md
## Noble / Radiant
## Pastoral / Natural
## Domestic / Familial
## Grotesque / Abusive
## Martial / Catastrophic
```

Each section should:
- list valid adjectives and nouns
- note whether they are positive, negative, or neutral contributors
- avoid implying semantic rules the parser does not enforce

- [ ] **Step 4: Add attested phrases and grammar-valid patterns**

Use both categories explicitly:

```md
### Example-attested phrases
- ...

### Grammar-valid composition patterns
- ...
```

Patterns should demonstrate how to build variety without leaving the grammar:
- preserve adjective count to preserve magnitude
- preserve noun sign to preserve sign
- vary within the allowed adjective/noun class

- [ ] **Step 5: Add anti-pattern guidance for agents**

Include warnings such as:

```md
- do not mix positive adjectives into negative noun phrases
- do not mix negative adjectives into positive noun phrases
- do not invent Shakespeare-sounding words
- do not treat style palettes as parser-enforced semantic categories
```

- [ ] **Step 6: Review the companion for technical correctness**

Run: `sed -n '1,320p' docs/research/shakedown-spl-style-lexicon.md`
Expected: every token is grammar-backed, and every phrase is clearly labeled as attested or newly composed but grammar-valid.

- [ ] **Step 7: Commit the style companion**

```bash
git status --short
git add docs/research/shakedown-spl-style-lexicon.md
git commit -m "docs: add SPL style lexicon companion"
```

Expected: the style companion is committed separately from the source note and canonical reference update.

### Task 5: Final Verification And Cleanup

**Files:**
- Reference: `docs/research/shakedown-spl-reference.md`
- Reference: `docs/research/shakedown-spl-style-lexicon.md`
- Reference: `docs/research/2026-04-17-spl-style-lexicon-sources.md`

- [ ] **Step 1: Check for unsupported vocabulary or unlabeled phrases**

Run: `rg -n "TODO|TBD|placeholder|invented|uncited" docs/research/shakedown-spl-reference.md docs/research/shakedown-spl-style-lexicon.md docs/research/2026-04-17-spl-style-lexicon-sources.md`
Expected: no placeholders or loose wording remain.

- [ ] **Step 2: Review the final diff**

Run: `git diff -- docs/research/shakedown-spl-reference.md docs/research/shakedown-spl-style-lexicon.md docs/research/2026-04-17-spl-style-lexicon-sources.md`
Expected: the diff clearly separates legality facts, style guidance, and source provenance.

- [ ] **Step 3: Produce the final status summary**

The closeout should state:

```text
- what hard lexicon facts were added to the canonical reference
- what the new style companion contains
- how phrases are labeled for technical safety
- whether any lexicon gap still remains
```

- [ ] **Step 4: Commit cleanup if needed**

```bash
git status --short
git commit -m "docs: clean up SPL style lexicon docs"
```

Expected: only needed if final review caused additional tracked-file edits after the prior commits.
