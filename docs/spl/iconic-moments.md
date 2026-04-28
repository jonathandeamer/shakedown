# Iconic-Moment Maps

**Status:** Pre-Slice-1 deliverable per architecture spec §7.1 #10.
**Constraints:** literary-spec §7.2 and §7.5.1.

- Scene-title iconic moments: at most 12.
- Recall echo iconic moments: 4 to 8.
- Combined ceiling: at most 20.
- Single-surface rule: each Shakespeare phrase appears in exactly one iconic
  surface.

The maps live in fenced TOML blocks below so the validator can parse them
without a separate file. Slice work that touches an iconic surface must update
this doc and the validator.

## Scene-title Iconic-Moment Map

```toml
[[scene_titles]]
phrase = "Out, damned spot"
play = "Macbeth"
speaker = "Lady Macbeth"
shakedown_use = "Act I scene that strips whitespace-only lines"

[[scene_titles]]
phrase = "Something wicked this way comes"
play = "Macbeth"
speaker = "Second Witch"
shakedown_use = "Act I scene that hashes raw HTML blocks"

[[scene_titles]]
phrase = "Once more unto the breach"
play = "Henry V"
speaker = "King Henry"
shakedown_use = "Act II opening scene; first block-recognition pass"

[[scene_titles]]
phrase = "But soft, what light"
play = "Romeo and Juliet"
speaker = "Romeo"
shakedown_use = "Act III opening scene; first span pass"

[[scene_titles]]
phrase = "A rose by any other name"
play = "Romeo and Juliet"
speaker = "Juliet"
shakedown_use = "Act III scene that performs ampersand/angle encoding"

[[scene_titles]]
phrase = "Our revels now are ended"
play = "The Tempest"
speaker = "Prospero"
shakedown_use = "Act IV closing emit scene"

[[scene_titles]]
phrase = "Lord, what fools these mortals be"
play = "A Midsummer Night's Dream"
speaker = "Puck"
shakedown_use = "Herald dispatch transition between acts II and III"

[[scene_titles]]
phrase = "All the world's a stage"
play = "As You Like It"
speaker = "Jaques"
shakedown_use = "Reserved: documentation-aggregate fixture entry scene"
```

## Recall Echo Iconic-Moment Map

```toml
[[recall_echoes]]
phrase = "Double, double, toil and trouble"
play = "Macbeth"
speaker = "Witches"
shakedown_use = "Recall description for Hecate's detab loop"

[[recall_echoes]]
phrase = "Two households, both alike in dignity"
play = "Romeo and Juliet"
speaker = "Chorus"
shakedown_use = "Recall description for Romeo/Juliet's strong-then-emphasis pair"

[[recall_echoes]]
phrase = "All that glisters is not gold"
play = "The Merchant of Venice"
speaker = "Prince of Morocco"
shakedown_use = "Recall description for Rosalind's reference-table consultation"

[[recall_echoes]]
phrase = "I am thy father's spirit"
play = "Hamlet"
speaker = "Ghost"
shakedown_use = "Recall description for Horatio's HTML-hash lookup"

[[recall_echoes]]
phrase = "We are such stuff as dreams are made on"
play = "The Tempest"
speaker = "Prospero"
shakedown_use = "Recall description for Prospero's emit walk"
```

## How To Extend

Adding a moment: append a TOML row, then run
`uv run pytest tests/test_iconic_moments.py`. The validator enforces the
single-surface rule, the per-surface budgets, and the combined ceiling.

## References

- `docs/spl/literary-spec.md` §7.2, §7.5, and §7.5.1.
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §7.1 #10.
