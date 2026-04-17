# SPL Act Architecture — Design Decision for Slice 2

**Date:** 2026-04-10  
**Status:** Decision pending (revisit when Slice 1 is complete)

## Current state

`shakedown.spl` is one `Act I` with ~130 scenes and ~4300 lines. No Act II/III/IV exist.
The original design spec envisioned Acts I–IV as phases (read, block scan, inline, emit), but
Slice 1 collapsed that. This doc records whether that collapse was correct and what it means for Slice 2.

---

## Why the single act is forced — given the current architecture

The control flow is a streaming dispatch loop:

```
Scene II (read) → Scene VII (newline) → Scene XXVII (dispatch)
   ↑                                        ↓
   ←————————————— each block handler jumps back ←—
```

Every block handler eventually jumps *backwards* to Scene II to read more input. Backwards
jumps across act boundaries are illegal in SPL — acts only fall through sequentially, once,
and never return. So as long as "read → classify → handle → read again" is the loop shape,
it must live in one act. This is correct, not a mistake.

You cannot put block handlers in Act II and have them "return to" Act I's read loop. Act
transitions are sequential fall-through, not calls.

---

## The only way multi-act works: a multi-pass rewrite

To genuinely use multiple acts, the architecture must change to batch passes:

- **Act I** — Read all stdin into a buffer. Fall through.
- **Act II** — Walk the buffer, classify blocks, emit tagged tokens onto another stack. Fall through.
- **Act III** — Walk tokens, run inline processing, emit HTML. Fall through.

Each act has its own self-contained loop with backwards gotos *inside* it. No act jumps back to
a previous act. This is legal SPL and properly exploits the act structure.

This is what the design spec was gesturing at with "Act I passes line content to Act II via
stage directions" — but that phrasing is misleading. Act II cannot be *called* per-line from
Act I; it can only run *once* after Act I falls through. So any real use of Act II for inline
processing requires Act I to emit a token stream rather than HTML directly.

---

## The real problem: duplicated patterns, not act count

What actually makes Act I unwieldy is repeated re-implementation of the same logic:

**Before-block dispatch** appears ~5 times (ATX, setext, HR, code block, blockquote). They
all do: "if Juliet==1 emit `</p>\n`; if Juliet==2 emit `\n`; else nothing."

Scenes involved:
- XXXVII/XXXVIII/XXXIX (ATX headings)
- LVII/LVIII/LIX (setext headings)
- LXX/LXXI/LXXII (horizontal rules)
- LXXVII/LXXVIII/LXXIX (code blocks)
- LXXXVII/LXXXVIII/LXXXIX (blockquotes)

**Content emission loops** (pop from Prospero, emit until sentinel) are reimplemented per block type.

**Blockquote sub-machinery** (Scenes LXXXVII–CXXXIII, ~2000 lines / ~half the file) largely
reimplements paragraph/heading/code-block logic inside the blockquote context instead of
reusing the outer machinery.

Consolidating shared patterns would shrink the file more than splitting acts, and is a
safer change.

---

## Options for Slice 2

### Option A: Keep single act, add inline as sub-dispatch

Inline processing becomes a per-content-loop sub-dispatch inside Act I. Each block handler's
content-emission loop calls into inline scenes before emitting each character run. More
duplication, no rewrite of existing code.

| Pros | Cons |
|------|------|
| No rewrite of Slice 1 | Inline logic scattered across every block handler |
| Simpler transition | Act I grows even larger |
| Lower risk | Blockquote inline processing gets its own copy again |

### Option B: Multi-pass rewrite (token stream)

Act I stops emitting HTML directly. Instead it emits a typed token stream onto a stack:
`(BLOCK_TYPE, content...)`. Act II processes that stream, runs inline substitutions on
content tokens, emits HTML. This is effectively "Slice 1.5: rewrite the emitter."

| Pros | Cons |
|------|------|
| Inline logic is isolated and non-duplicated | Requires rewriting most of Slice 1 |
| Correct SPL act structure | Likely slower (more passes on slow machine) |
| Each act is a small, debuggable state machine | Significant scope before Slice 2 starts |
| Blockquote nesting handled naturally | Intermediate token representation needs design |

### Option C: Hybrid — consolidate first, then Option A

Before Slice 2 starts: extract shared before-block dispatch and content emission into
reusable scenes (called via Ophelia as a "return address" register). Then add inline
processing to the consolidated content path. No multi-pass, but far less duplication.

Probably the right pragmatic path.

---

## Recommendation

1. **Slice 1 is architecturally correct as-is.** Single act forced by streaming dispatch. No fix needed.

2. **Before Slice 2, consolidate duplicate patterns** (Option C setup):
   - Extract before-block dispatch into one shared scene
   - Extract content emission loop into one shared scene
   - This alone will significantly reduce file size and make inline additions safer

3. **For Slice 2 itself, decide between A and B.** Option B is the "right" architecture
   but is effectively a Slice 1.5 rewrite. Option A is faster to execute but produces
   a harder-to-maintain file. This decision should be made with fresh eyes once Slice 1 is committed.

4. **Performance on this machine is already a constraint.** Option B adds another full pass
   over the data. If `shakespeare run` on empty input already takes 26s, that matters.

---

## Decision needed after Slice 1 lands

- [ ] Option A, B, or C for Slice 2?
- [ ] If B: scope the token representation before writing any Slice 2 code
- [ ] If A or C: extract shared before-block dispatch and content loop first
