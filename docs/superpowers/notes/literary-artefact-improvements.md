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

### 1. Stage the emotional beats the titles already promise  → 2 of 3 done
`dramatic_moments` (`lyrical_pair_as_one`, `lady_macbeth_death_exit`,
`hecate_final_exit`) name real dramatic beats, but the staging was bare
`[Exit]/[Enter]/[Exeunt]`. The title wrote a check the stage didn't cash.
- **Seam:** a variable that is dead from the insertion point onward + `let(...)`
  render as equality lines built from the *speaker's* own atoms and comparator
  bank. Inert, value-safe. `let(target)` is spoken by the anchor when
  `target != anchor`, and by the companion when `target == anchor` — pick the
  target to pick the speaker.
- **DONE — R&J "as one" exit** (`ACT_III_DONE`, `src_ir/act3.py`): four-line
  duet on the two lovers' dead-in-Act-IV scalars. Terminal scene, trivially safe.
- **DONE — Lady Macbeth death exit** (`FRAME_REVERSE_OPEN`, `src_ir/act2.py`):
  three-line fall (noble hero → cursed wolf → nothing) via `let(PUCK, ...)`.
  This is a *mid-act handoff*, not terminal, so safety needed a real argument:
  the lines set Puck's SCALAR, not the stack that `FRAME_REVERSE_POP` drains,
  and Act III overwrites Puck's scalar with a `pop` before its first read, so
  the incoming scalar is dead. Lady Macbeth speaks (target PUCK != anchor).
- **TODO — Hecate's final exit** (`ACT_I_DONE`): same seam; verify which scalar
  is dead across the Act I→II boundary before choosing the speaker/target.
  The mid-act (non-terminal) safety argument from the Lady Macbeth beat is the
  template — do not assume terminal-scene triviality.

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
