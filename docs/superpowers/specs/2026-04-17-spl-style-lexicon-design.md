# SPL Style Lexicon Design

**Date:** 2026-04-17
**Status:** Proposed

## Goal

Add a technically correct, agent-friendly SPL lexicon layer that improves the expressive
quality of future `shakedown.spl` code without weakening the canonical language reference.

The design should let an agent answer two different questions cleanly:

- "Is this token or phrase legal in the installed interpreter?"
- "What vivid but valid phrase should I use here instead of repeating `big big big cat`?"

## Scope

In scope:

- expanding `docs/research/shakedown-spl-reference.md` with missing lexicon facts that belong
  in the canonical reference
- creating a new companion document for style guidance and phrase patterns
- mining valid vocabulary and phrase examples from the installed grammar and bundled example
  plays
- documenting safe composition and substitution rules for agents

Out of scope:

- changing the SPL interpreter grammar
- adding invented vocabulary not accepted by the installed interpreter
- changing `shakedown.spl`
- writing a general essay on literary style outside the constraints of valid SPL

## Problem

The current reference is technically useful but not agent-optimal for expressive generation.
It has three gaps:

1. It does not surface all parser-valid comparative vocabulary in one place.
2. It lists the adjective and noun inventories, but it does not reorganize them as a
   generation aid.
3. It does not separate "legal vocabulary" from "good stylistic choices," which makes it too
   easy for an agent to improvise invalid wording.

## Recommendation

Use a two-layer structure.

### Layer 1: Canonical reference

Keep `docs/research/shakedown-spl-reference.md` as the authoritative legality source.

This layer should contain:

- complete grammar-backed adjective, noun, and comparative inventories
- exact composition rules for noun phrases and comparisons
- parser-facing constraints on what can be combined legally
- a short pointer to the style companion

This document remains the place an agent should trust for hard constraints.

### Layer 2: Style companion

Add a new companion doc at:

`docs/research/shakedown-spl-style-lexicon.md`

This layer should contain:

- curated semantic palettes built only from grammar-valid vocabulary
- example-derived phrase patterns from the bundled SPL example corpus
- safe substitution guidance for generating more varied but still valid numeric phrases
- warnings about where style freedom stops and grammar constraints begin

This document is for generation quality, not parser truth.

## Why This Split Is Better

### Option A: Put everything in the main reference

Pros:
- one file

Cons:
- mixes legality and taste
- makes the canonical reference harder to scan
- increases the chance an agent treats stylistic suggestions as grammar facts

### Option B: Add only a style doc

Pros:
- better generation guidance

Cons:
- leaves the canonical reference incomplete on lexicon details
- forces agents to infer legality from a non-canonical file

### Option C: Canonical reference plus style companion

Pros:
- legality remains centralized
- style guidance can be richer without contaminating the reference
- agents can use the two docs differently and safely

Cons:
- two docs to maintain

Recommended: Option C.

## Canonical Reference Changes

Update `docs/research/shakedown-spl-reference.md` to add:

### 1. Missing comparative vocabulary

The current reference should explicitly include all grammar-backed comparative forms:

- positive: `better`, `bigger`, `fresher`, `friendlier`, `nicer`, `jollier`, `more <positive adjective>`
- negative: `worse`, `smaller`, `punier`, `more <negative adjective>`
- equality: `as <negative adjective or positive/neutral adjective> as`

### 2. Lexicon composition rules

The reference should state clearly:

- positive and neutral nouns are parsed through the positive noun-phrase path
- negative nouns are parsed through the negative noun-phrase path
- positive noun phrases allow positive and neutral adjectives
- negative noun phrases allow negative and neutral adjectives
- articles and possessives are both legal noun-phrase starters
- multi-word nouns such as `summer's day` and `stone wall` are single grammar-backed nouns

### 3. Pointer to style guidance

Add a short note that the main reference is the legality source and the companion style doc is
the generation aid.

## Style Companion Design

Create `docs/research/shakedown-spl-style-lexicon.md` with these sections:

### 1. Purpose and safety boundary

State explicitly:

- every token listed is accepted by the installed interpreter grammar
- phrases are either example-attested or newly composed but grammar-valid
- when legality and style conflict, the main reference wins

### 2. Comparative palette

Collect comparison words in a writer-facing table:

- upbeat comparisons
- hostile comparisons
- equality forms

### 3. Semantic palettes

Group valid vocabulary into generation-friendly palettes such as:

- noble / radiant
- pastoral / natural
- domestic / familial
- grotesque / abusive
- martial / catastrophic

These are style groupings only. They do not change semantics.

### 4. Phrase patterns

Include technically valid patterns such as:

- `<positive adjectives> <positive/neutral noun>`
- `<negative adjectives> <negative noun>`
- paired sums like `the sum of a proud rich trustworthy hero and a lovely sweet golden summer's day`

### 5. Attested examples

Mine a small set of vivid phrases from:

- `~/spl-1.2.1/examples/`
- `/home/ec2-user/shakespearelang/shakespearelang/tests/sample_plays/`

Each example should be labeled as example-attested.

### 6. Safe substitutions for agents

Explain how to vary expressions while preserving validity:

- rotate adjectives within the same allowed sign path
- swap nouns within the same allowed sign path
- preserve adjective count when the numeric magnitude must stay the same
- preserve noun sign when the numeric sign must stay the same

### 7. Anti-patterns

Warn against:

- mixing positive adjectives into negative noun phrases
- mixing negative adjectives into positive noun phrases
- inventing Shakespeare-sounding but invalid words
- treating the style categories as semantic types enforced by the parser

## Source Policy

Every vocabulary item in the new or updated docs must come from one of:

1. `shakespeare.ebnf`
2. the installed interpreter test/sample plays
3. the bundled SPL examples

No uncited invented words should appear as recommended lexicon.

## Success Criteria

This work succeeds if:

- the main reference becomes a more complete legality source for lexicon
- the style companion gives agents a richer pool of valid phrase choices
- the new material is technically correct against the installed interpreter grammar
- the docs make it harder, not easier, for an agent to generate invalid SPL wording

## Implementation Approach

1. Extract the complete grammar-backed comparative and noun/adjective composition rules.
2. Audit the current reference for missing lexicon details.
3. Mine vivid but valid phrases from bundled examples and sample plays.
4. Write the companion style lexicon with clear provenance labels.
5. Update the main reference with missing hard facts and a pointer to the companion doc.
