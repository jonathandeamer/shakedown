# Shakedown Literary Spec

> **Status:** spec, dated 2026-04-27. Project-canonical literary policy for `shakedown.spl`.
> Deliverable of the literary sub-brainstorm that followed the architecture spec
> (`docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`).

## 1. Goal and Framing

Shakedown is explicitly intended to be a *fun art artefact* — that is a stated
primary project goal alongside correctness, not decoration. This spec exists so
the assembled `shakedown.spl` reads as a literary work with character voices,
dramatic structure, and aesthetic coherence, while remaining a faithful port of
Markdown.pl v1.0.1.

Two umbrella principles govern everything below:

**Literary surfaces are data. Mechanical surfaces are codegen output.**
Decorative text (play title, act titles, scene titles, dramatis personae blurbs,
Recall strings, per-character soft-variation pools, per-character Stable Utility
surfaces) lives in a hand-authored sidecar (`src/literary.toml`) keyed by stable
symbolic names. The codegen tool reads it and emits SPL; it never invents prose.
This preserves the "codegen quarantine" tactic from the architecture spec
(§3.7 mechanical-monotony policy) and makes literary content auditable in one
place.

**Drop-first rule.** Wherever iambic flavour, ornament, or aesthetic ambition
collides with grammar legality, semantic correctness, character voice fidelity,
or technical accuracy, *iambic flavour is dropped first*. Aesthetic richness is a
goal, not a license. The rule applies at every level — line, title, narrator
description, structural choice — and the literary review checklist (§9) treats
"defensible drop" as a satisfied condition, not a failure.

## 2. Cast

### 2.1 Play title

Locked:

> *Shakedown: A Most Excellent Tragicomedy of Glyph and Line.*

The form mirrors how modern editions of Shakespeare's plays are titled — pithy
modern lead, fuller period subtitle (e.g., *"Hamlet: The Tragical Historie of
Hamlet, Prince of Denmark"*). "A Most Excellent" is a real Elizabethan title
formula (the 1597 quarto of *Romeo and Juliet* opens *"An Excellent conceited
Tragedie of Romeo and Iuliet"*). "Glyph and Line" is paired in the Elizabethan
mode (cf. *"Lord and Father"*, *"Sun and Stars"*) and is semantically precise:
the play's substance is the transformation of glyphs (the characters of
Markdown) and lines (the units of structure). "Tragicomedy" is a real
Shakespearean genre (*Cymbeline*, *The Winter's Tale*, *The Tempest*) — it
honestly names what shakedown is: structure cuts through chaos and emerges
ordered, neither pure tragedy nor pure comedy.

The colon is grammar-legal (`text_before_punctuation` regex `[^!\.]*` permits
`:`, `,`, `—`, `;` mid-string; only `.` and `!` are forbidden mid-title).

### 2.2 Cast roster

Nine named characters, drawn cross-canon from six well-known Shakespeare plays.
Includes four women across the cast.

| # | Role | Character | Play | Acts | Home palette |
|---|---|---|---|---|---|
| 1 | Sorter | Hecate | Macbeth | I | Grotesque/Abusive |
| 2 | Mason | Lady Macbeth | Macbeth | II | Martial/Catastrophic |
| 3 | Apprentice | Macbeth | Macbeth | II | Martial/Catastrophic |
| 4 | Lyrical Pair (A) | Romeo | Romeo & Juliet | III | Pastoral/Natural |
| 5 | Lyrical Pair (B) | Juliet | Romeo & Juliet | III | Pastoral/Natural |
| 6 | Scribe | Prospero | The Tempest | IV | Noble/Radiant |
| 7 | Librarian | Rosalind | As You Like It | I→III | Pastoral/Natural (range) |
| 8 | Steward | Horatio | Hamlet | I→IV | Domestic/Familial |
| 9 | Herald | Puck | Midsummer | II→IV | Pastoral/Natural (chameleon) |

**Plays:** Macbeth (3), Romeo & Juliet (2), Tempest, As You Like It, Hamlet,
Midsummer (1 each) — six plays, all top-tier well-known.

**Women:** Hecate, Lady Macbeth, Juliet, Rosalind.

**On Hecate vs. the Three Witches.** SPL grammar's character-name list
(`shakespeare.ebnf`) admits `Hecate` but not `Witch` / `First Witch` /
`Three Witches`. We cast Hecate as the Sorter — she is the goddess-queen
of the witches in Macbeth (Act III Scene 5, Act IV Scene 1) and presides
over their cauldron — and reserve "the witches" as a *narrator-voice
plural* in act and scene titles (parallel to "the lovers" naming Romeo
and Juliet as a unit). Hecate is the on-stage character; "the witches"
is the cauldron tradition the narrator may invoke. Trade-off accepted:
we lose the literal Three Witches plural-chant device, but grammar
legality is non-negotiable per the drop-first rule (§1).

**Role-to-architecture mapping** (architecture spec §3 / inherited-scaffold):

- **Sorter** — Pre-process / Read phase. Sorts raw input into hash buckets
  (HTML), reference definitions, and remaining text. Hecate's cauldron
  presidency — riddles, diseased nouns, magisterial witch register — is the
  right voice for the sift.
- **Mason** — Block phase. Shapes blocks: headers, HR, lists, code,
  blockquotes. Lady Macbeth's "unsex me here" decisiveness fits the cuts.
- **Apprentice** — Block phase support. Macbeth as junior to Lady Macbeth;
  natural craft pairing.
- **Lyrical Pair** — Span / Inline phase. Romeo and Juliet adorn the line with
  emphasis, links, code-spans, autolinks. Romeo carries sun-and-day lyric;
  Juliet carries night-and-star lyric.
- **Scribe** — Emit phase. Prospero inscribes the final HTML. "Our revels now
  are ended" is the Act IV signature.
- **Librarian** — Reference shelf keeper across Acts I–III. Rosalind's range
  across registers (court ↔ forest ↔ male disguise) makes her the right voice
  for cross-phase reference lookups.
- **Steward** — HTML hash and other cross-act state. Horatio is steady witness
  across all four acts; the only character with full-span Acts I–IV presence.
- **Herald** — Dispatcher across Acts II–IV. Puck's "girdle round the earth"
  makes him the literal messenger; his trickster nature lets him modulate per
  act without losing himself.

The cast leans Macbeth-heavy in Acts I–II (Hecate + Lady M + Macbeth), but
they don't share scenes awkwardly — Hecate finishes Act I before Lady M and
Macbeth take over Act II — and concentrating the dark plays early frees Acts
III–IV for the lyrical and noble registers without tonal whiplash.

### 2.3 Voice signatures

Each character carries a distinct vocal signature drawn from their Shakespeare
canon. These are the per-line touches that make speech read as the character
even when the line is mechanical.

| Character | Voice signature |
|---|---|
| Hecate | Riddles, diseased nouns, magisterial witch register, cauldron-tradition allusions |
| Lady Macbeth | Cold imperatives, hard decisions, royal/martial nouns |
| Macbeth | Dread-tinged martial — doubt-shaded version of Lady M |
| Romeo | Sun-and-day lyric — "light through yonder window" |
| Juliet | Night-and-star lyric — wonder-leaning counterpart to Romeo |
| Prospero | Ceremonial, magisterial — "our revels now are ended" |
| Rosalind | Witty, agile across registers; flexes Domestic in Act I |
| Horatio | Plain-spoken keeper, kin/house/friend lexicon; the steady ledger |
| Puck | Trickster — most chameleonic; borrows palette of whichever act he visits |

### 2.4 Cross-act voice strategy

Three of the nine characters appear in multiple acts: Rosalind (I→III),
Horatio (I→IV), Puck (II→IV). The remaining six are act-bound. Cross-act
characters use a **Hybrid voice strategy** — home palette plus neighbouring
palette colours when visiting other acts. This keeps each character recognisable
across acts without clashing against the visited act's ambient texture.

The three hybrid styles, per character:

- **Puck (chameleonic).** Noun stays from home (Pastoral) palette; adjective
  tilts toward visited palette. Recognisably Puck (flower, wind, light); wears
  the act's costume (martial adjective in Act II, noble adjective in Act IV).
- **Horatio (steady, refuses to modulate).** Full home (Domestic/Familial)
  surface in every act. The cross-palette contrast IS his texture — he is the
  calm voice in every room.
- **Rosalind (broadest range).** Noun usually home (Pastoral) with visited-act
  adjectives; full noun-borrow allowed for in-character moments where she
  steps fully into a Martial or Noble register. Range across registers IS
  canonically Rosalind.

These three rules compose with the per-act palette and per-character Stable
Utility surfaces below — they aren't separate machinery, they're how cross-act
characters resolve the precedence cascade in §6.

## 3. Per-Act Palettes

Drawn from `docs/spl/style-lexicon.md`, which names five canonical palettes:
Grotesque/Abusive, Martial/Catastrophic, Pastoral/Natural, Noble/Radiant,
Domestic/Familial. Four palettes map to the four acts; the fifth is reserved
for Horatio's per-character cross-act voice.

| Act | Phase | Palette | Mood |
|---|---|---|---|
| I | Pre-process / Read | **Grotesque/Abusive** | Grimy mechanical sorting; cauldron register |
| II | Block | **Martial/Catastrophic** | Decisive structural cuts; royal/martial decision |
| III | Span / Inline | **Pastoral/Natural** | Fine ornament; lyric substitution |
| IV | Emit | **Noble/Radiant** | Ceremonial completion; magisterial benediction |

**Domestic/Familial** is not act-bound. It is Horatio's home palette across all
four acts.

### 3.1 Sign-path constraints

The lexicon's sign-path rules (positive nouns require positive or neutral
adjectives; negative nouns require negative or neutral adjectives) interact with
the palettes' actual word inventories. Some palettes lack one sign:

| Palette | Positive nouns | Negative nouns |
|---|---|---|
| Grotesque/Abusive | none — neutral fallback only | many (`toad`, `wolf`, `plague`, `blister`, `devil`, `curse`) |
| Martial/Catastrophic | `hero`, `kingdom` | many (`war`, `death`, `wolf`, `curse`, `famine`) |
| Pastoral/Natural | many (`rose`, `flower`, `summer's day`, `morning`, `tree`, `wind`) | none — must borrow |
| Noble/Radiant | many (`hero`, `Lord`, `King`, `angel`, `kingdom`, `Heaven`) | none — must borrow |
| Domestic/Familial | none directly — kin nouns (`brother`, `mother`, `son`) classified neutral | none |

When an act needs a value of opposite-sign-from-its-palette, it borrows from a
neighbouring palette. Concrete fallbacks:

- **Act III (Pastoral) needs negative:** borrow from Martial → `a wolf`. Reads
  as natural-world peril; fits pastoral setting.
- **Act IV (Noble) needs negative:** borrow from Martial → `a curse` or
  `a wolf`. Reads as noble-world threat; fits noble register.
- **Act I (Grotesque) needs positive:** use neutral → `a cat`. Cats are
  witch-familiars; reads natural even in grotesque setting.

These borrows are bounded: opposite-sign values are *rare* in any given act
because each act's work tends toward its native polarity (Hecate does mostly
negative-sign sorting; Prospero does mostly positive-sign noble emission). The
borrow is visible *and that's fine* — an opposite-sign value IS notable, so its
surface looking foreign is a feature, not a bug.

### 3.2 Palette inflects voice; voice never abandons character

The palette colours the act's ambient texture; it does not replace any
character's voice. When palette and voice would conflict, voice wins. Concretely:

- A Hecate line in Act I is grotesque-coloured because both her voice and
  the act palette pull that way — no conflict.
- A Horatio line in Act I is Domestic/Familial — Horatio does not become
  grotesque because the act is. The cross-palette contrast IS his texture.
- A Puck line in Act II uses Pastoral noun + Martial adjective — palette
  inflects, voice persists.

This is the same rule that drives the §2.4 cross-act voice strategy.

## 4. Stable Utility — Per-Character Surfaces

Stable Utility values are the recurring infrastructure constants that appear
hundreds of times: small positive integers (`+1`, `+2`, `+3`), zero, small
negatives (`-1`, `-2`), and small token codes used in dispatch. The
codegen-style-guide (`docs/spl/codegen-style-guide.md`) classifies these as
"Stable Utility" — distinguishable from Critical sentinels (which require one
canonical phrase repo-wide) and Incidental values (free per-line).

This spec adopts **per-character Stable Utility surfaces** (Option C in the
brainstorm). Each of the nine characters has their own preferred surface phrase
for each Stable Utility value they actively use.

### 4.1 Why per-character

The alternative (per-act palette-tilted Stable Utility, stable within each act)
would have been simpler — fewer surfaces to track. We chose per-character
deliberately. Reasoning:

- **Character-as-color-code is a literary feature, not just a cost.** When Lady
  Macbeth pushes `+1` as `a hero` and Macbeth pushes `+1` as `a kingdom` in
  the same scene, a reader sees two surfaces for one value, but the divergence
  *is* drama. Same beat, different mouth, different word — which is exactly
  what Shakespeare does. Per-act uniformity would erase that.
- **The cost is bounded by codegen quarantine.** This is a static lookup table
  `(character, value) → surface`, consulted by the codegen tool at generation
  time. Humans don't memorise 30–45 entries; the tool does.
- **Sign-path proximity within shared palettes keeps paired characters'
  surfaces close.** Lady M (`a hero`) and Macbeth (`a kingdom`) for `+1`
  diverge but stay in the same Martial neighbourhood. Romeo (`a summer's
  day`) and Juliet (`a rose`) for `+1` diverge but stay Pastoral. Readers see
  *recognisably-related* surfaces, not foreign ones.
- **Critical sentinels override per-character.** `0` stays `nothing` repo-wide
  (the codegen-style-guide canonical surface). Any other Critical-classified
  value also stays canonical. Per-character variation applies only to
  non-Critical Stable Utility — so the values most prone to causing scanning
  confusion (the sentinels) keep their cross-character uniformity.

### 4.2 Mitigations for the three known costs

**Many surfaces (9 × N values).** Bounded. N is small (~6–10 Stable Utility
values total: `+1`, `+2`, `+3`, `-1`, `-2`, `0`, plus a handful of small
counters). Each character actively uses only a 3–5 value subset. Total
surface count: ~30–45 entries in `src/literary.toml`. Codegen handles the
lookup; humans review the table once.

**Same value differs between speakers in the same scene.** Mitigated by
documented legend in this spec (§4.4 sketch table), sign-path proximity
within shared palettes, and Critical override for the values most prone to
confusion.

**Cross-act characters need a precedence rule.** Resolved by the §2.4
Hybrid voice strategy: Puck swaps adjectives but keeps home noun; Horatio
keeps full home; Rosalind swaps adjectives with optional noun-borrow for
in-character moments.

### 4.3 Codegen quarantine

The Stable Utility surface table is *data*, not code. It lives in
`src/literary.toml` keyed by `(character_name, value)`. Codegen reads the
table when emitting any expression that needs a Stable Utility value. The
table has no presence in the assembled `shakedown.spl`; it is an input to
the assembly process.

This means: a literary-spec edit (e.g., changing Romeo's `+1` from `a
summer's day` to `a rosy morning`) is a one-line data change followed by
re-assembly. No SPL hand-editing.

### 4.4 Sketch surface table (illustrative — Wave 4 mechanical finalises)

| Character | `+1` | `+2` | `-1` | `0` |
|---|---|---|---|---|
| Hecate | `a cat` (neutral fallback) | `a big cat` | `a toad` | `nothing` (Critical) |
| Lady Macbeth | `a hero` | `a noble hero` | `a wolf` | `nothing` |
| Macbeth | `a kingdom` | `a foul kingdom` | `a curse` | `nothing` |
| Romeo | `a summer's day` | `a sunny summer's day` | `a wolf` (borrowed Martial) | `nothing` |
| Juliet | `a rose` | `a sweet rose` | `a wolf` (borrowed Martial) | `nothing` |
| Prospero | `an angel` | `a noble angel` | `a curse` (borrowed Martial) | `nothing` |
| Rosalind home | `a tree` | `a green tree` | (rare, borrow) | `nothing` |
| Horatio | `a brother` | `a happy brother` | (rare, borrow) | `nothing` |
| Puck home | `a flower` | `a sweet flower` | (rare, borrow) | `nothing` |

This is illustrative. The final surface table is produced by the
implementation phase as the architecture spec's `+1`, `+2`, etc. dispatch
codes are pinned. Sketch is here so reviewers can see the policy applied
concretely.

Notes on the sketch:

- Hecate's `+1` is `a cat` because Grotesque has no positive nouns. Cats
  are witch-familiars, so the neutral fallback reads natural in setting.
- Lady M and Macbeth share Martial sign path but diverge: Lady M is the
  `hero` voice (clean martial); Macbeth is the `kingdom`/`curse` voice
  (martial-with-dread). Both lawful in lexicon.
- Romeo and Juliet share Pastoral sign path but diverge along the
  sun/night axis: Romeo's `summer's day`, Juliet's `rose`.
- Sign-path borrows are explicit annotations (`borrowed Martial`) so the
  codegen tool can record provenance and reviewers can verify intent.

## 5. Soft-Variation Pools

SPL grammar locks the load-bearing verbs (Remember, Recall, Enter, Exit,
Exeunt, Speak your mind, Open your heart, Listen to your heart, Open your
mind). Our policy is moot for these — the parser already decided. But SPL
grammar permits soft variation at four points where it makes a real
expressive difference, and per-character pools turn those points into
character-voice signal.

### 5.1 Soft variation points

| Variation point | Legal options | Effect |
|---|---|---|
| Positive comparatives | `better`, `bigger`, `fresher`, `friendlier`, `nicer`, `jollier`, `more <adj>` | Same boolean test; different speech |
| Negative comparatives | `worse`, `smaller`, `punier`, `more <adj>` | Same test; different character voice |
| Equality form | `as <any adjective> as` (full lexicon) | Massive expressive room |
| Possessive / pronoun | `your`/`thy`, `you`/`thou`, `myself`/`thyself` | Period flavour dial |
| Goto verb | `Let us proceed to` / `Let us return to` / `We shall proceed to` / `We must return to` | Free synonyms; can mark forward/back jumps |

Conditional joiners (`If so` / `If not`) are already varied by branch
polarity, so policy is moot.

### 5.2 Per-character soft-variation pools

Each character draws from a small consistent pool. The pool is small enough
to feel like that character; large enough to avoid mechanical repetition.

| Character | Comparative pool (positive / negative) | Pronoun tilt | Goto verb tilt |
|---|---|---|---|
| Hecate | `as cursed as`, `as rotten as`, `as horrid as` / `worse than`, `more cursed than`, `more foul than` | `thy`/`thou` (most archaic) | `We must return to` |
| Lady Macbeth | `bolder than`, `bigger than`, `as mighty as`, `as bold as` / `worse than`, `as villainous as` | `you`/`your` | `Let us proceed to` |
| Macbeth | same pool as Lady M, biased to negative variants (`worse than`, `more foul than`, `as villainous as`) | `you`/`your` | `Let us proceed to` |
| Romeo | `sweeter than`, `as sunny as`, `as golden as`, `as fair as` | `you`/`your` (tilts `thy`/`thou` for love-spoken lines) | `Let us proceed to` |
| Juliet | `gentler than`, `as fair as`, `as gentle as`, `as sweet as` | `thy`/`thou` (more period than Romeo) | `Let us proceed to` |
| Prospero | `nobler than`, `more peaceful than`, `as honest as`, `as noble as` | `thy`/`thou` globally | `We shall proceed to` |
| Rosalind | broadest range — `friendlier`, `jollier`, `nicer`, plus palette-borrowed variants when on tour | mixed; flexes per scene | `Let us proceed to` |
| Horatio | `friendlier than`, `as warm as`, `as healthy as`, `as happy as` | `you`/`your` (plain-spoken) | `Let us proceed to` |
| Puck | `jollier than`, `nicer than`, `friendlier than` at home; borrows visiting acts' pools when on tour | mixed; tilts archaic | `Let us proceed to` |

The pools are small. Variety within a single character's lines is achieved
by the codegen tool rotating through the pool, not by hand-authored
selection.

## 6. Precedence Rule

When grammar legality, sign correctness, Critical canonical surface, per-act
palette ambiance, per-character voice, and free decorative slots could all
apply to the same line, this is the order of precedence. Each lower rule
operates only in space the higher rule leaves open.

1. **Grammar legality** — parser-enforced. SPL EBNF accepts or rejects.
2. **Sign + magnitude correctness** — the value the operation must produce.
   Sign and magnitude are not negotiable.
3. **Critical canonical surface** — for any value classified Critical (e.g.,
   `0` is `nothing`; sentinels stay sentinel-shaped). One phrase repo-wide.
4. **Per-act palette ambiance** — the act's home palette colours the ambient
   texture, especially for narrator-voiced surfaces (titles, scene actions)
   and for act-bound characters' own lines.
5. **Per-character voice tilt** — pulls Stable Utility surfaces, soft-variation
   pools, and Recall pools from the character's own lookup table. For
   cross-act characters, applies the Hybrid strategy from §2.4.
6. **Decorative slots** — free per literary commitment. Scene title patterns
   (six admitted), Recall description pools, dramatis personae blurbs,
   stage-direction pairings.

This formalises the codegen quarantine tactic from the architecture spec.
Each rule operates in a strictly subordinate scope — palette never overrides
Critical; voice never overrides palette ambiance for narrator surfaces;
decoration never overrides voice. The cascade is deterministic and the
codegen tool implements it directly.

## 7. Conventions

### 7.1 Act titles

**Format:** `Wherein <subject> <action>.`

The "Wherein" clause is a real 17th-century narrative-summary device used in
chapter headings of Cervantes, Defoe, Fielding (and adjacent to the period
register Shakespeare himself worked in, even if not strictly Shakespearean).
It announces what the act *does*, in voice that sits between play-text and
chapter-heading.

**Conventions:**

1. Each act title takes the form `Wherein <subject> <action>.`
2. Subject names the act-bound character(s) by role or name — *the witches*,
   *Lady Macbeth*, *the lovers*, *Prospero*. The character signals the act's
   voice before any line is read.
3. Action describes the act's structural work — *sort raw matter*, *shape the
   kingdom of blocks*, *gild the line*, *inscribe and release*. Each act's
   mechanical work mapped onto a poetic verb-phrase.
4. Length: one line, ~10–14 words.
5. Loose iambic feel preferred but not enforced (drop-first rule applies).

**The four locked act titles:**

- Act I: *Wherein the witches sort raw matter into shelves and seals.*
- Act II: *Wherein the kingdom of blocks is shaped, and each form named.*
- Act III: *Wherein the lovers gild the line with light and rose.*
- Act IV: *Wherein Prospero, his work done, inscribes and releases all.*

### 7.2 Scene titles

For ~50–200 scene titles, six admitted patterns. Authors pick per scene;
patterns can blend.

1. **Wherein-clause** (matches act titles) — *"Wherein a header is hewn from
   the line."*
2. **Bare poetic statement** — *"A horizontal rule is laid."*
3. **Scene-of-character** — *"The witches consult their list."*
4. **Iconic-moment echo** (sparingly) — *"Double, double — the witches at
   their first sorting."* / *"Out, damned token."* / *"What light through
   yonder line breaks."* / *"Our revels now are ended."*
5. **Cross-character narration** (marks state handovers) — *"Wherein Lady
   Macbeth receives what the witches sorted."* / *"Wherein Puck takes word
   from the mason to the lovers."*
6. **Locale-evocation** (short, atmospheric) — *"At the cauldron's edge."* /
   *"Within the keep, the kingdom is shaped."*

**Length:** 6–12 words. Drop-first rule applies for iambic.

**Voice:** narrator's voice (the play's), inflected by the act's palette —
not any single character's voice.

**Density-tilted length:**

- Dense mechanical scenes (long sequences of similar token-handling steps):
  briefer titles, often pattern 6.
- Dramatic peak scenes (act openings, transitions, final emit): richer
  titles, often patterns 1, 4, or 5.

**Iconic-moment budget (pattern 4):** 1–3 per act, 4–12 across the work.
Reserved for scenes whose mechanical work *coincides* with a canonical
Shakespeare image. Overusing them erases the special-ness; under-using
forfeits the strongest art moments. The explicit map of (symbolic-scene
name → iconic-moment phrase) is produced as part of the implementation
plan deliverables; the *budget* lives here.

**Word choice:**

- **Recurring motif words** preferred: `form`, `shape`, `line`, `glyph`,
  `hewn`, `laid`, `gild`, `inscribe`, `seal`, `release`, `light`. These
  accumulate as the work's thematic signature.
- **Per-act motif tilts:**
  - Act I: `cauldron`, `sort`, `sift`, `seal`
  - Act II: `keep`, `shape`, `hew`, `kingdom`
  - Act III: `garden`, `gild`, `light`, `rose`, `line`
  - Act IV: `cell`, `inscribe`, `release`, `world`

**Avoid:**

- CS jargon (`parse`, `dispatch`, `token`, `pre-process`, `block-shape`).
  These belong in code comments, which we don't have. In titles, render
  them in the play's vocabulary.
- Repeated identical titles. Even when scenes do mechanically similar work,
  the locale or motif word should vary.

**Hand-authoring:** Scene titles are hand-authored data, not generated.
They live in `src/literary.toml` keyed by symbolic scene name; codegen
reads them during assembly. This is the load-bearing application of
"literary surfaces are data."

### 7.3 Dramatis personae descriptions

Each character's one-line description in the personae block.

- **Length:** medium — one full sentence; flexible enough to seat the
  character without becoming a paragraph.
- **Voice:** narrator-neutral. In-character self-introduction breaks the
  fourth wall awkwardly in SPL; narrator voice is steadier.
- **Content:** hybrid — function named, palette flavours the words. A
  casual reader gets both *what does this character do* and *what does
  this character feel like*.

Example: `Romeo, a worker of the inline garden who hews each line into
ordered ornament.`

### 7.4 Stage directions

SPL stage directions are grammar-locked: `[Enter X]`, `[Enter X and Y]`,
`[Exit X]`, `[Exeunt]`, `[Exeunt X and Y]`. No decorative slots inside the
brackets. The literary choice is *which characters are on stage when, and
how scene transitions look.*

**Cast size per scene.** Default 2 (one speaker + one addressee — the SPL
idiom, since Speak/Listen need an addressee). Occasional 3+ for
council/transition moments. Single-character scenes are not viable.

**Named pairings.** Some cast units enter together when both are needed:

- The Lyrical Pair (Romeo + Juliet) — entering together carries weight.
- The Mason + Apprentice (Lady Macbeth + Macbeth) — natural craft pairing.

**Scene rhythm.** **Monolithic scenes** by default — every scene = one
`[Enter ...]` at top, one `[Exeunt]` at bottom. Simple, regular cadence;
easier to author and reason about. **Theatrical mid-scene movement**
(`[Exit X]` / `[Enter Y]` mid-scene) is permitted as an explicit opt-in
literary device for high-drama beats — act boundaries, character
introductions, phase handoffs. Budget: ≤6 mid-scene movements across the
whole work.

### 7.5 Recall description convention

Recall is `Recall recall_string ("!" | ".")` where `recall_string` is
free-form `[^!\.]*`. The text doesn't affect execution; it's pure
literary surface, spoken by the recalling character. It is the closest
thing SPL has to in-line decorative text.

- **Length:** tight (3–8 words). Keeps line count manageable; matches
  SPL's clipped dialogue rhythm. Longer descriptions feel narrator-y when
  the speaker is a character.
- **Voice:** character-spoken — palette- and character-flavoured. A Lady
  Macbeth Recall reads differently from a Rosalind Recall, even when the
  popped value plays the same mechanical role.
- **Content style:** atmospheric / character-voiced, not
  mechanical-descriptive. *"Recall the morning's first cut!"* (Macbeth)
  beats *"Recall the prior count!"* (which makes the literary slot do the
  work the variable name should do). Occasional narrative-leaning
  descriptions (*"Recall thy oath to thy love!"*) are permitted for
  high-drama moments where the narrative gloss earns its keep, but the
  default is atmospheric.
- **Frequency / reuse:** per-character pool of 5–8 phrases in
  `src/literary.toml`, codegen rotates cyclically (or random with fixed
  seed for reproducibility). Avoids both per-Recall identical (dull) and
  every-Recall unique (hundreds of authored lines for a possibly-large
  pop count). Cross-act characters (Puck/Horatio/Rosalind) get one flat
  pool each — their hybrid voice already handles act-by-act flex.

Per the data principle, pools are hand-authored data; codegen selects
but never invents.

### 7.6 Branch / scene naming

Symbolic scene names live in source files only —
`scripts/assemble.py` resolves them to act-local Roman numerals in the
assembled `shakedown.spl`. They appear in goto targets (`Let us proceed
to mason_block_quote_open.`) and as keys in `src/literary.toml`. So this
is internal-facing literary surface: source files themselves read like a
play even before assembly.

**Convention: hybrid `<role>_<mechanical>` format.**

Examples: `mason_block_quote_open`, `apprentice_pre_scan_setup`,
`hecate_sort_hash_blocks`, `prospero_emit_paragraph_close`. The prefix
may be either the *role* (`mason`, `apprentice`) or the *character name*
(`hecate`, `prospero`); pick whichever reads more recognisable for the
scene.

Reasoning:

- Role prefix gives literary flavour and confirms cast assignment at a
  glance.
- Mechanical suffix stays greppable and survives refactors. If a scene's
  purpose changes, only the suffix needs update; the role stays stable.
- Cheaper than fully-literary names, which risk lying when scene
  mechanics evolve.

The literary dimension comes from titles, descriptions, and Recall pools
— naming doesn't need to carry the full load.

**File naming.** The inherited scaffold splits source as
`00-preamble.spl` / `10-phase1-read.spl` / `20-phase2-block.spl` /
`30-phase3-inline.spl`. That's a phase-split scheme tied to one
architecture choice. File-naming convention is **deferred to architecture
spec finalisation**: if the file split is per-act, names take a literary
tilt (`01-cauldron.spl`, `02-keeping.spl`, …); if it stays phase-split,
mechanical names are appropriate. This spec records "file naming follows
the file split decided by architecture spec" as an open hand-off.

## 8. Mechanical Decisions

### 8.1 Token code constraint

The architecture spec produces a list of dispatch token codes (block-token,
inline-token, character-class). The literary spec asserts a constraint on
what those codes shall be:

**Dispatch token codes shall be small positive integers expressible in 2–4
word Stable Utility noun phrases**, so dispatch lines read as character
speech, not as machine codes.

- No floats, no negatives (signed only when sign is meaningful), no large
  primes.
- Range 1–~32 covers all plausible dispatch tables.
- 2–4 words per phrase target; never exceed 6.

Example mappings (illustrative — actual codes pinned by architecture
spec):

- `1` → `a cat`
- `2` → `the sum of a cat and a cat`
- `3` → `the sum of a big cat and a cat`
- `8` → `the sum of a big big cat and a big big cat`

Architecture spec picks the actual codes; the *constraint* lives here.

### 8.2 Critical phrase recipe

Architecture spec produces a list of N Critical dispatch values. Literary
spec asserts the recipe for their canonical phrases.

**Scope.** This recipe covers Critical *dispatch* values — positive
non-zero integers used as block-token, inline-token, or character-class
codes. Pre-existing Critical canonicals from the codegen-style-guide
(notably `0` → `nothing`, plus any other repo-wide sentinel surfaces
already established there) take precedence and are not re-derived from
this recipe.

**Recipe (for in-scope dispatch values):**

- Sign: positive non-zero (dispatch codes are 1, 2, 3, … per §8.1).
- Build from `cat` (Stable Utility neutral noun) using `sum of` and
  `big`/`big big` doublings as needed — multi-tactic to avoid mechanical
  monotony.
- Same canonical phrase used by every speaker for that value (this is
  what makes it Critical).
- 2–4 words per phrase target; never exceed 6.

Final phrase list is produced as a deliverable of the architecture spec /
implementation plan, validated against this recipe and against the
codegen-style-guide for pre-existing canonicals.

### 8.3 Mechanical-monotony tactics (recap)

The architecture spec §3.7 commits to five tactics for avoiding mechanical
monotony in `shakedown.spl`. The literary spec inherits them; this
recap is here so the connection is visible.

1. **Codegen-only mechanical chaining.** No hand-authored value chains
   like `the sum of a big big cat and a big big cat`; codegen emits these.
2. **Stable Utility families.** Recurring values use the per-character
   Stable Utility surface table (§4).
3. **Palette × voice doubling.** Per-act palette inflects ambient texture;
   per-character voice signature pulls from soft-variation pools (§5)
   and Stable Utility surfaces (§4).
4. **Non-numeric surface area.** Decorative slots (titles, Recall
   descriptions, dramatis personae blurbs) carry character/narrator voice
   so the SPL isn't just chains of numeric phrases.
5. **Designed token codes.** This spec's §8.1 — token codes are chosen
   for short Stable Utility expressibility, not allocated by some
   ASCII/numeric mapping.

## 9. Literary Review Checklist

A reviewer (human, or codegen self-check) runs this against the assembled
`shakedown.spl` and `src/literary.toml`. Each item maps to a specific
section above.

1. **Critical compliance.** Every Critical value uses the canonical phrase
   regardless of speaker. No drift. (§4, §6)
2. **Stable Utility per-speaker.** Each speaker uses their own surface for
   non-Critical Stable Utility values, drawn from `src/literary.toml`. No
   cross-character borrowing unintentionally. (§4)
3. **Soft-variation pools.** Per-character comparatives, possessives, and
   goto verb stay within the character's pool. (§5)
4. **Scene title coverage.** Every symbolic scene name has a title key in
   `literary.toml`. No missing keys, no orphan titles. (§7.2, §7.6)
5. **Title rules.** Each scene title 6–12 words; legal punctuation only
   (no mid-title `.` or `!`); voice inflected by act palette. (§7.2)
6. **Iconic-moment alignment.** 4–12 iconic-moment echoes used; each
   lands on a scene whose mechanical work earns the echo. (§7.2)
7. **Act titles.** Wherein-clause format; the four locked titles; palette
   alignment. (§7.1)
8. **Stage directions.** Default cast size 2; named pairings (Lyrical
   Pair, Mason+Apprentice) enter together when both present; monolithic
   scenes unless explicitly opted in (≤6 theatrical mid-scene movements
   across the work). (§7.4)
9. **Recall descriptions.** Drawn from per-character pool; no inline
   invention; tight (3–8 words); atmospheric voice. (§7.5)
10. **Title-vs-work coupling.** Every Wherein-clause / scene-of-character
    title accurately describes the mechanical work the scene performs;
    titles that have drifted from the scene's actual work get updated.
    (§7.2)
11. **Drop-first rule.** Wherever iambic flavour conflicts with
    legality/clarity/voice/technical accuracy, iambic was dropped — and
    the choice is defensible if questioned. (§1)
12. **Codegen quarantine.** No literary prose in codegen output that
    wasn't read from `literary.toml`. (§1, §4.3)

## 10. Open Hand-offs

These are deliverables of later phases (architecture-spec finalisation or
implementation planning) that consume the policies in this spec. They are
*not* gaps in this spec; they are downstream products that depend on
upstream decisions still in progress.

1. **Final Critical token list.** Architecture spec produces the
   enumerated Critical values; literary review validates against §4 and
   §8.2.
2. **Final per-character Stable Utility surface table.** Once Critical
   values are pinned, the §4.4 sketch table becomes a concrete table in
   `src/literary.toml`, written before Slice 1 of implementation begins.
3. **Iconic-moment scene assignments.** Map of symbolic scene name →
   iconic-moment phrase, ≤12 entries, written during implementation
   planning. (§7.2)
4. **Source file-naming convention.** Decided when architecture spec
   finalises the source file split. (§7.6)
5. **`src/literary.toml` schema.** Concrete TOML keys, types, and example
   entries. Deliverable of the implementation plan's pre-Slice-1 task
   list.

## 11. Doc-update Follow-ups

Adopting this spec implies edits to other docs. These are deliverables
of a single follow-up PR after this spec lands; not prerequisites.

1. **`codegen-style-guide.md` — "Palette By Purpose" section.** Currently
   advises noble/domestic/pastoral for stable state, grotesque/catastrophic
   for error/poison-adjacent (a value-purpose-driven rule from before
   architecture was chosen). Update to: act palette inflects ambient
   texture; Critical override at value level; palette-by-purpose advisory
   now lives at the *value* level via the per-character Stable Utility
   surfaces, not at the *line* level.
2. **`codegen-style-guide.md` — "Deferred Guidance" section.** Currently
   defers character/role/voice until architecture chosen. Architecture is
   chosen and this spec resolves the deferral. Replace with forward
   pointer to this document.
3. **`codegen-style-guide.md` — Precedence stub.** Add a short section
   pointing to §6 of this spec for the full precedence cascade.
4. **`style-lexicon.md`** — Top-of-file pointer: "For per-character voice
   and per-act palette assignment, see `literary-spec.md`." The lexicon
   itself stays as-is (it remains the inventory).
5. **`style-guide-validation.md`** — Add a row noting literary-spec
   policies are advisory authoring policy enforced by review checklist
   (this doc §9), not mechanically by parser.
6. **`CLAUDE.md`**:
    - Reference materials list: add `docs/spl/literary-spec.md`.
    - Docs Truth Hierarchy section: literary spec joins
      codegen-style-guide as a generation/policy doc.
7. **Architecture spec
   (`docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`)** —
   Replace pre-lexicon palette names ("celestial", "formal/declarative")
   with lexicon-canonical names (Grotesque/Abusive, Martial/Catastrophic,
   Pastoral/Natural, Noble/Radiant, Domestic/Familial). Reference this
   spec by path where the architecture spec mentions `docs/literary/`.

## 12. References

- `docs/spl/style-lexicon.md` — five named palettes, exhaustive lexicon,
  sign-path rules.
- `docs/spl/codegen-style-guide.md` — Critical/Stable Utility/Incidental
  partition; codegen quarantine policy.
- `docs/spl/style-guide-validation.md` — what's mechanically enforceable
  vs advisory.
- `docs/spl/reference.md` — SPL grammar surface (program structure, soft
  variation points, Recall as decorative slot).
- `docs/spl/verification-evidence.md` — probe programs supporting the
  reference.
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` —
  architecture spec; per-act palette assignments at §3.3;
  mechanical-monotony tactics at §3.7.
- `docs/architecture/decision-rubric.md` — architecture-input rubric.
- `~/markdown/Markdown.pl` — oracle.
