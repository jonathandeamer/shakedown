# Slice 2 Act II Binary Block-Gates — Design

**Date:** 2026-07-14
**Status:** accepted for Slice 2 Task 2 Step 2
**Amends:** `docs/superpowers/plans/2026-07-14-slice-2-low-risk-fixtures.md`

## Decision

The horizontal-rule and indented-code gate keeps its existing Markdown
decision order and token shapes.  It is reconstructed only at the IR-scene
boundary so every scene has Act II's anchor, Lady Macbeth, and exactly one
assignment target.  Branch tests and right-hand-side reads may continue to
name off-stage registers, as permitted by `docs/spl/reference.md`; this
amendment does not change `scripts/splc/validate.py`, lowering, carrier
ownership, token allocation, replay order, or Act IV rendering.

Each split is a terminal `goto` handoff.  It separates already-planned writes
without adding a Pop, Recall key, sentinel, token, Markdown branch, or byte.
The existing `PASS_CODE_BLANK` spare becomes the sixth working split label;
five new working titles and five new spares restore the required 20% reserve.

## Binding reconstruction ledger

The table is exhaustive for the five multi-target scenes reported by
`validate.participants`.  Retained labels keep their indicated first write;
the named new or repurposed label performs the next write(s) and retains the
original branch targets.  Every pair is `(LADY_MACBETH, companion)`.

| Current scene | Reconstruction, in order | Pair(s) |
|---|---|---|
| `PASS_HR_GATE` | retain `let(HORATIO, 0)`; goto `PASS_HR_GATE_MARKER`, which sets `PUCK` to zero and performs the existing marker branches | `(LADY_MACBETH, HORATIO)` → `(LADY_MACBETH, PUCK)` |
| `PASS_CODE_GATE` | retain the Horatio leading-space tally; goto `PASS_CODE_GATE_READ`, which performs the existing `_read()` and count branch | `(LADY_MACBETH, HORATIO)` → `(LADY_MACBETH, HECATE)` |
| `PASS_HR_SCAN` | redirect marker branches to `PASS_HR_MARKER_SAVE`, which saves the marker on Puck; retain `PASS_HR_SCAN` for Macbeth's count seed; goto `PASS_HR_SCAN_READ`, which performs `_read()` and the existing compare/space/replay branches | `(LADY_MACBETH, PUCK)` → `(LADY_MACBETH, MACBETH)` → `(LADY_MACBETH, HECATE)` |
| `PASS_HR_CONFIRM` | retain Macbeth's count increment; goto `PASS_HR_CONFIRM_READ`, which performs `_read()` and the existing compare/space/newline/replay branches | `(LADY_MACBETH, MACBETH)` → `(LADY_MACBETH, HECATE)` |
| `PASS_CODE_OPEN` | retain Horatio's four-space register setup and the `CODE_BLOCK` emit; goto the repurposed `PASS_CODE_BLANK`, which performs the existing first `_read()` before `PASS_CODE_GLYPH` | `(LADY_MACBETH, HORATIO)` → `(LADY_MACBETH, HECATE)` |

`PASS_HR_SAVE` must redirect marker branches to `PASS_HR_MARKER_SAVE` and use
Puck as its companion so both branch arrivals have the same entry pair.  The
following single-target scenes need only their existing intended companion:
`PASS_HR_SPACE=HECATE`, `PASS_HR_REPLAY=HECATE`,
`PASS_BLOCK_RETURN=HECATE`, `PASS_CODE_CLOSE=HECATE`, and
`PASS_BLOCK_FINISH=MACBETH`.  These choices preserve their destination entry
pairs; they introduce no operation or literary surface.

## Controlled-surface reservation

Append only labels used by the reconstruction to `src/20-act2-literary.toml`.
All are Incidental scene titles.  No Recall entry is needed: moved `_read()`
operations continue to use Hecate's already-reserved `hewn_glyph` line.

```toml
# src/20-act2-literary.toml — Slice 2 binary-gate working additions
[scenes.PASS_HR_GATE_MARKER]
title = "Puck takes the level iron's first mark."
pattern = "scene_of_character"
[scenes.PASS_CODE_GATE_READ]
title = "Hecate reads the fourfold threshold's next mark."
pattern = "scene_of_character"
[scenes.PASS_HR_MARKER_SAVE]
title = "Puck keeps the level iron's chosen mark."
pattern = "scene_of_character"
[scenes.PASS_HR_SCAN_READ]
title = "Hecate brings the next level iron stroke."
pattern = "scene_of_character"
[scenes.PASS_HR_CONFIRM_READ]
title = "Hecate brings the iron line's confirming stroke."
pattern = "scene_of_character"

# `PASS_CODE_BLANK` is the former Slice-2 spare and now the sixth working
# split state.  Keep its already-reserved title; do not create a duplicate.

# Slice 2 binary-gate spare pool — unavailable without another plan amendment.
[scenes.PASS_HR_PAIR_GUARD]
title = "The level iron keeps its faithful pair."
pattern = "bare_statement"
[scenes.PASS_HR_PAIR_RETURN]
title = "The iron measure returns by its faithful pair."
pattern = "bare_statement"
[scenes.PASS_CODE_PAIR_GUARD]
title = "The chamber keeps its faithful pair."
pattern = "bare_statement"
[scenes.PASS_CODE_PAIR_RETURN]
title = "The chamber measure returns by its faithful pair."
pattern = "bare_statement"
[scenes.PASS_BLOCK_PAIR_GUARD]
title = "The shaped block keeps its faithful pair."
pattern = "bare_statement"
```

The pre-amendment pool had 19 active working labels and one remaining spare:
three original spares were already consumed by the in-progress block pass.
This reconstruction consumes that final spare and adds five working labels,
for 25 working labels.  The five new spares yield exactly 20%; none is
implementation authority.

## Required proof and stop condition

Before regeneration, extend `tests/test_act2_slice2.py` with a focused
`participants(scene, ACT.anchor)` assertion over every Act II scene.  It must
assert the ledger's exact pairs for the eleven split/retained labels above,
assert none of the five new spare labels is reachable from `ACT.scenes`, and
then run:

```bash
uv run pytest tests/test_act2_slice2.py tests/test_splc_validate.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_act2_slice2.py tests/test_act4_slice2.py tests/test_mdtest.py -k 'Horizontal rules' -q
uv run python scripts/strict_parity_harness.py 'Horizontal rules'
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

A participant or branch-entry-pair failure, a missing TOML label, changed
token stream, lost replay byte, or parity regression is a new `BLOCK[plan]`.
It does not authorize consuming a spare, changing the compiler, or editing a
generated SPL fragment.
