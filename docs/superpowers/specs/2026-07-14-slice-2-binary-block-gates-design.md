# Slice 2 Act II Binary Block-Gates — Design

**Date:** 2026-07-14
**Status:** accepted for Slice 2 Task 2 Step 2 (Amendment B, 2026-07-14)
**Amends:** `docs/superpowers/plans/2026-07-14-slice-2-low-risk-fixtures.md`

## Decision

The horizontal-rule and indented-code gate keeps its existing Markdown
decision order and token shapes.  It is reconstructed only at the IR-scene
boundary so every scene has Act II's anchor, Lady Macbeth, and exactly one
assignment target.  Branch tests and right-hand-side reads may continue to
name off-stage registers, as permitted by `docs/spl/reference.md`; this
amendment does not change `scripts/splc/validate.py`, lowering, carrier
ownership, token allocation, replay order, or Act IV rendering.

Each split is a terminal `goto` handoff. It separates already-planned writes
without adding a Pop, Recall key, sentinel, token, Markdown branch, or byte.
The existing `PASS_CODE_BLANK` spare becomes the sixth working split label;
five new working titles and five new spares restore the required 20% reserve.

### Amendment B — whitespace-only blank lines and the Puck-to-Hecate replay bridge

Fresh local `Markdown.pl` establishes two binding corrections to the original
Task-2 seam: an HR candidate may have three leading spaces, and a line
containing spaces only is a blank separator before that candidate. The latter
path enters `PASS_HR_SAVE` with Puck on stage. Its newline and rejected-input
branches must not arrive directly at `PASS_HR_REPLAY`, because that scene also
has Hecate-stage branch predecessors. The compiler correctly rejects those
inconsistent branch-entry pairs.

Promote the pre-reserved `PASS_HR_PAIR_RETURN` title to one working adapter.
`PASS_HR_SAVE` sends its newline and final rejected-input branches to it.
The adapter has no state operation, declares `companion=HECATE`, and terminally
goes to `PASS_HR_REPLAY`. Thus its branch entry is `(LADY_MACBETH, PUCK)`, its
operating pair is `(LADY_MACBETH, HECATE)`, and its goto shares Lady Macbeth
with `PASS_HR_REPLAY`. It changes only SPL staging, not carrier bytes or
Markdown control flow. All other Hecate-stage replay branches continue to
target `PASS_HR_REPLAY`; the `PASS_HR_EMIT` Macbeth-stage fallback remains a
goto and is legal through the shared anchor.

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
| `PASS_HR_SAVE` (Amendment B) | redirect its newline and final rejected-input branches to `PASS_HR_PAIR_RETURN`; the adapter makes no write and terminally goes to `PASS_HR_REPLAY` | entry `(LADY_MACBETH, PUCK)`; operating pair `(LADY_MACBETH, HECATE)` |

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

# `PASS_HR_PAIR_RETURN` is promoted to a working pair adapter by Amendment B.
# It keeps its already-reserved title; do not create a duplicate.

# Slice 2 binary-gate spare pool — unavailable without another plan amendment.
[scenes.PASS_HR_PAIR_GUARD]
title = "The level iron keeps its faithful pair."
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
[scenes.PASS_HR_PAIR_WATCH]
title = "The level iron watches its faithful pair."
pattern = "bare_statement"
[scenes.PASS_BLOCK_PAIR_WATCH]
title = "The shaped block watches its faithful pair."
pattern = "bare_statement"
```

The pre-amendment pool had 19 active working labels and one remaining spare:
three original spares were already consumed by the in-progress block pass.
This reconstruction consumes that final spare and adds five working labels,
for 25 working labels. Amendment B promotes one of those five spares to the
26th working label and adds two new spares. The remaining six spares exceed
20% of the 26-working-label pool; none is implementation authority.

## Required proof and stop condition

Before regeneration, extend `tests/test_act2_slice2.py` with a focused
`participants(scene, ACT.anchor)` assertion over every Act II scene. It must
assert the ledger's exact pairs for the twelve split/retained labels above,
including `PASS_HR_PAIR_RETURN=HECATE`; assert
`entry_pairs(ACT2)["PASS_HR_PAIR_RETURN"] == (LADY_MACBETH, PUCK)`; and assert
none of the six remaining spare labels is reachable from `ACT.scenes`. The HR
contract must assert that `   ---` emits `tokens.HR` and that whitespace-only
separator lines before both compact and space-separated HR candidates emit no
paragraph token. Then run:

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

## Amendment C (2026-07-14): lossless rejected-HR replay

**Status:** accepted for the unchecked Slice-2 Task-2 checkpoint. The HR
accept path is correct, but rejection retains only indentation and a marker;
it loses consumed markers from ordinary prose. The concrete regression is
`***both*** and **outer *inner* outer**`, which Act II currently passes to Act
III as `*both*** ...`.

Once the gate sees a leading space or HR marker, save every consumed byte on a
Romeo stack above one `STREAM_END` floor: indentation, markers, inter-marker
spaces, newline, and the first rejecting byte. A confirmed HR drains that
floor and emits only `tokens.HR`. A rejected candidate pops Romeo and pushes
the saved bytes onto Lady Macbeth in the same carrier orientation as
`PASS_LISTS_RAW_GLYPH`, then resumes that raw path without another read. The
disproving byte is replayed once; the replay does not synthesize `TEXT_END`,
enter the code gate, or discard a four-space code candidate.

Keep the current accepted Amendment-B labels and entry-pair contract. Add only
these working `(LADY_MACBETH, ROMEO)` labels:
`PASS_HR_BUFFER_OPEN`, `PASS_HR_BUFFER_KEEP`, `PASS_HR_REPLAY_OPEN`,
`PASS_HR_REPLAY_POP`, `PASS_HR_REPLAY_KEEP`, and `PASS_HR_REPLAY_CLOSE`.
Append these exact Incidental surfaces plus four unavailable spares:

```toml
[scenes.PASS_HR_BUFFER_OPEN]
title = "Romeo opens the level iron's private casket."
pattern = "scene_of_character"
[scenes.PASS_HR_BUFFER_KEEP]
title = "Romeo keeps one doubtful iron stroke."
pattern = "scene_of_character"
[scenes.PASS_HR_REPLAY_OPEN]
title = "Romeo unlocks the doubtful iron casket."
pattern = "scene_of_character"
[scenes.PASS_HR_REPLAY_POP]
title = "Romeo recalls one doubtful iron stroke."
pattern = "scene_of_character"
[scenes.PASS_HR_REPLAY_KEEP]
title = "Romeo restores one iron stroke to the field."
pattern = "scene_of_character"
[scenes.PASS_HR_REPLAY_CLOSE]
title = "The doubtful iron line returns unbroken."
pattern = "bare_statement"
[scenes.PASS_HR_BUFFER_GUARD]
title = "The iron casket waits beneath a quiet cloud."
pattern = "bare_statement"
[scenes.PASS_HR_REPLAY_GUARD]
title = "The iron field keeps one patient boundary."
pattern = "bare_statement"
[scenes.PASS_HR_CASKET_GUARD]
title = "A sealed iron casket rests beside the road."
pattern = "bare_statement"
[scenes.PASS_HR_RETURN_GUARD]
title = "The iron path returns beneath clear morning."
pattern = "bare_statement"
```

Add pair/unreachable assertions and decoded-`PARA` contracts for
`***both***`, `**not an hr**`, `---x`, and `- - x`. Then run:

```bash
uv run pytest tests/test_act2_slice2.py tests/test_act3_contracts.py tests/test_splc_validate.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
uv run pytest tests/test_splc_generated_fragments.py tests/test_spl_parse_smoke.py tests/test_splc_validate.py tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py -k "(Amps and angle and encoding) or (Horizontal and rules)" -q
uv run python scripts/strict_parity_harness.py 'Amps and angle encoding' 'Horizontal rules'
```

Require `summary: 2/2 byte-identical`. A changed accepted HR, rejected byte,
entry-pair, title outside this six-plus-four pool, or an Act-III underflow
after the exact `***both***` carrier contract is `BLOCK[plan]`.
