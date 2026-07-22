# shakedown.spl as a literary/art artefact — improvement backlog

Captured 2026-07-22 during the `experiment/stage-lyrical-pair-exit` spike. These
are *artefact-quality* ideas (how it reads as a Shakespeare play), not
correctness work. None of them may change HTML output — the play must remain a
faithful Markdown.pl port. Ordered by rough impact.

## What already works (don't regress it)

- **Cross-play casting** with per-character `palette` / `voice_register`
  (`src/literary.toml`): witches preprocess, masons block, lovers gild spans,
  Prospero emits. Coherent controlling metaphor.
- **Per-character `value_atoms`**: each character counts in their own imagery
  (Hecate/cats, Juliet/roses, Macbeth/kingdoms, Lady Macbeth/cursed wolves).
  The arithmetic substrate speaks character. Best mechanical-literary fusion here.
- **`iconic_moments`** anchored to semantically apt scenes ("Out, damned spot"
  on boundary-restore, "A rose by any other name" on the ampersand lyric test).

## Backlog

### 1. Stage the emotional beats the titles already promise  → IN PROGRESS (this spike)
`dramatic_moments` (`lyrical_pair_as_one`, `lady_macbeth_death_exit`,
`hecate_final_exit`) name real dramatic beats, but the staging is bare
`[Exit]/[Enter]/[Exeunt]`. Scene CCLXXXII "Romeo and Juliet part as one bright
rose" resolves to three stage directions and no dialogue. The title writes a
check the stage doesn't cash.
- **Seam:** dead-after-Act variables + `let(...)` render as equality lines built
  from the speaker's own atoms, addressed to the companion. Inert, value-safe.
- This spike prototypes the R&J "as one" exit; if it lands, extend to Lady
  Macbeth's death handoff (`FRAME_REVERSE_OPEN`) and Hecate's final exit
  (`ACT_I_DONE`).

### 2. Even out the scene-title voice
The `SCRIBE_QUOTE_CODE_*` chamber titles are atmospheric ("Prospero enters the
echoing chamber", "The echoing chamber settles into peace"), but the mechanical
ones read like loop counters in a ruff ("The second chamber line counts another
faded step"). Pass to make image-driven titles the norm. Cheapest polish;
touches only `title =` strings in the per-act `*-literary.toml`, zero code risk.

### 3. Commit one surface to actual verse *form*
There is no meter or rhyme anywhere — the "verse-ness" is naming, not form.
Pick one load-bearing surface and make it scan: e.g. every **scene title** in
iambic pentameter, or each **act** closing on a rhymed couplet. Signals that the
poetry is intentional and load-bearing. Larger effort; needs a literary-protocol
plan and a compliance test guarding the meter.

### 4. Vary the fixed stack/IO barks
`Remember yourself.` / `Open your mind!` / `Speak your mind!` are the
most-repeated and least-characterful lines. SPL allows some latitude in phrasing
I/O and stack ops. Per-character variants would cut the "print statement" feel.
Check `shakespearelang` grammar for which synonyms the interpreter accepts before
committing (`docs/spl/reference.md`).

## Hard constraint for all of the above
Nothing here may alter emitted HTML. Any dialogue added to a terminal/handoff
scene must operate only on variables that are dead in every later act, and must
not push/pop shared stacks that a later act reads. Verify with the full
`tests/test_mdtest.py` suite (23 fixtures) plus the literary-compliance tests
named in whatever plan ships the change.
