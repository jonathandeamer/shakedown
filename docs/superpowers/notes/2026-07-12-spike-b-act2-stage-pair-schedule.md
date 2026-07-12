# Spike B Act II Stage-Pair Schedule

**Date:** 2026-07-12  
**Plan:** `docs/superpowers/plans/2026-07-12-spike-b-nested-blocks.md`  
**Scope:** Task 3 Step 3 blocker resolution for `src_ir/act2.py`

## Problem

Spike B Task 3 needs Act II to do two incompatible kinds of work:

- glyph scanning and newline classification, which must stay on the existing
  `(Lady Macbeth, Hecate)` pair because `_read()` pops Hecate and decrements
  Lady Macbeth's countdown; and
- container-state mutation, which must touch Macbeth's borrowed frame stack for
  explicit `LIST_OPEN` / `LIST_ITEM` / `ITEM_CLOSE` / `LIST_CLOSE` scheduling,
  while quote open/close state must avoid Hecate entirely to preserve entry-pair
  validation.

IR validation allows branch conditions to inspect off-stage characters, but it
does **not** allow an op sequence to target three characters in one scene.
That means the Task 3 rewrite cannot directly "read a glyph and push a
Macbeth-frame" in the same scene. It needs adapter scenes whose only job is to
switch legal pairs before the next mutation.

## Required pair split

Task 3 should keep these three pair families:

| Pair | Responsibility | Notes |
|---|---|---|
| `(Lady Macbeth, Hecate)` | `_read()`, line-head tests, optional-space stripping after `>` | Never mutates Macbeth's or Horatio's borrowed stacks. |
| `(Lady Macbeth, Macbeth)` | Open/close explicit list and item frames on the mixed stream; mutate Macbeth's frame stack | May branch on Hecate's current glyph, but may not pop Hecate. |
| `(Lady Macbeth, Horatio)` | Open/close blockquote state and replay the current glyph after a quote-boundary decision | Horatio should carry only quote state/value bookkeeping for Spike B. |

No other pair is needed for the blocker. `FRAME_STAGE_*`, `PASS_PARA_*`, and
`FRAME_REVERSE_*` can then be rewritten against a stable container stream
without fighting entry-pair validation.

## Reserved-scene assignment

The nine Step 3 reservations are sufficient if used this way:

| Label | Pair | Role |
|---|---|---|
| `PASS_CONTAINERS_OPEN` | `(Lady Macbeth, Macbeth)` | Goto-only adapter from a scan scene into list/item open work. Emits `LIST_OPEN` / `ITEM_START(payload)` or `ITEM_CLOSE` + nested `LIST_OPEN` as required by the already-classified boundary. |
| `PASS_CONTAINERS_QUOTE` | `(Lady Macbeth, Horatio)` | Goto-only adapter that toggles quote-open state and emits `BLOCKQUOTE_OPEN` / `BLOCKQUOTE_CLOSE` before control returns to a scan scene. |
| `PASS_CONTAINERS_CLOSE` | `(Lady Macbeth, Macbeth)` | Goto-only adapter for list/item close cascades (`ITEM_CLOSE`, `LIST_CLOSE`, end-of-input close-all). |
| `PASS_PARA_ITEM_OPEN` | `(Lady Macbeth, Macbeth)` | Paragraph-pass copy scene: consume internal `ITEM_START(payload)` and emit final `LIST_ITEM(payload)`. |
| `PASS_PARA_ITEM_CLOSE` | `(Lady Macbeth, Macbeth)` | Paragraph-pass copy scene: pass through final `ITEM_CLOSE`. |
| `PASS_CONTAINERS_BOUNDARY` | `(Lady Macbeth, Hecate)` | Spare adapter for "reprocess current glyph after a close" boundaries. |
| `PASS_CONTAINERS_REPLAY` | `(Lady Macbeth, Horatio)` | Spare adapter when quote close must preserve the current glyph for the next non-quote classifier. |
| `PASS_CONTAINERS_DEPTH` | `(Lady Macbeth, Macbeth)` | Spare adapter if Step 3 keeps Macbeth's scalar depth register in sync with the frame stack in a separate scene. |
| `PASS_CONTAINERS_EOF` | `(Lady Macbeth, Macbeth)` | Spare adapter for end-of-input close cascades if `PASS_CONTAINERS_CLOSE` would otherwise need two incompatible entry pairs. |

## Safe control-flow shape

The blocked rewrite should follow this pattern whenever one physical-line
boundary needs both glyph inspection and container mutation:

1. A `(Lady Macbeth, Hecate)` scan scene reads or classifies the current glyph.
2. That scan scene branches to one of the `PASS_CONTAINERS_*` adapters without
   touching Macbeth or Horatio.
3. The adapter scene emits or mutates only on its legal pair.
4. The adapter jumps back to a scan or replay scene that resumes using the
   already-read glyph, rather than popping Hecate again.

This keeps both borrowed-stack floors intact:

- Macbeth's stack is only pushed/popped in `(Lady Macbeth, Macbeth)` scenes.
- Horatio's stack remains a borrowed floor only; quote state should live in
  Horatio's current value, not on Horatio's stack.

## Consequences for Task 3

- The old looseness side channel on Horatio's stack should be retired in Task 3.
  Internal item-open state can instead be represented as `ITEM_START` followed
  by one looseness payload on the mixed stream, then converted in
  `PASS_PARA_ITEM_OPEN`.
- Quote-boundary decisions must never be embedded directly into `_read()` scenes.
  They need the adapter hop above.
- The blocker is resolved only when `src_ir/act2.py` adopts this pair schedule,
  regenerates cleanly, and passes the Task 3 gate in the plan.
