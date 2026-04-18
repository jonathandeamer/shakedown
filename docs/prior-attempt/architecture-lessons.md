# Architecture Lessons from the Prior Attempt

> This file consolidates three earlier sources: `shakedown-mdtest-architecture-memo.md` (recommended build shape), `shakedown-before-design.md` (pre-design reminder), and `spl-act-architecture.md` (the 2026-04-10 options memo). The originals are removed by the restructure; their content is preserved and integrated below.

## What the Prior Attempt Tried

The prior Shakedown SPL implementation was a single-act streaming dispatcher. It read stdin character-by-character, classified blocks, and dispatched to handlers that emitted HTML and jumped backwards to re-read input. The implementation reached roughly 4,300 lines across ~130 scenes. Slice 1 completed block-level features (paragraphs, ATX and setext headings, horizontal rules, indented code blocks, blockquotes including nested/lazy forms). Slice 2 (inline) and Slice 3 (lists, HTML blocks) were never begun.

## Act-Boundary Constraint

The core runtime property that shaped the architecture: **gotos cannot cross act boundaries**. Scene lookup in the installed interpreter is act-local. This is confirmed in `docs/spl/verification-evidence.md` and documented in `docs/spl/reference.md`.

Because the main processing loop is `read → classify → handle → read again`, every block handler needs a backwards jump to the read scene. That backwards jump cannot cross act boundaries, so the entire streaming dispatcher must live in one act. The original design envisioned Acts I–IV as pipeline phases (read / block scan / inline / emit); that shape is only legal if each act is itself a self-contained loop with its own internal backwards gotos, and the pipeline runs as multiple passes over buffered state rather than streaming per-line.

## Duplicated-Pattern Pressure

What made the single-act file unwieldy was not act count but repeated re-implementation of the same logic:

- **Before-block dispatch** appeared about five times (ATX, setext, HR, code block, blockquote): each block type re-implemented "emit `</p>` if we were in a paragraph; emit `\n` if the prior was a blockquote; else emit nothing."
- **Content emission loops** (pop from the line stack, emit until sentinel) were re-implemented per block type.
- **Blockquote sub-machinery** (scenes LXXXVII–CXXXIII, roughly half of the file) largely reimplemented paragraph/heading/code-block logic inside the blockquote context instead of reusing outer machinery.

The round-2 feasibility work validated that a shared-scene return-address pattern (treat Ophelia's value as a return address) and a buffer-fed recursive dispatcher can coexist inside a single act and together materially reduce duplication.

## The Three April-2026-04-10 Options (A/B/C) — Preserved as Historical Decision Surface

Options A, B, C were laid out near the end of the prior attempt. No decision was made; the project stalled at that decision memo.

**Option A — Keep single act, add inline as sub-dispatch.** Inline processing becomes a per-content-loop sub-dispatch. Each block handler's content emission loop calls into inline scenes before emitting each character run. No rewrite of Slice 1, but inline logic scatters across every block handler.

**Option B — Multi-pass rewrite (token stream).** Act I stops emitting HTML and instead emits a typed token stream. Act II processes the stream, runs inline substitutions, emits HTML. Correct use of SPL act structure. Requires rewriting most of Slice 1 and adds another full pass over data on a slow machine.

**Option C — Hybrid (consolidate duplicates first, then Option A).** Before any Slice 2 work, extract shared before-block dispatch and content emission into reusable scenes. Then add inline processing to the consolidated content path. Pragmatic; recommended by the memo but never executed.

For architecture planning in this repo, these three options are input, not a pending decision. A fresh design may select one, combine parts, or propose a fourth shape. What transfers is the framing of the trade-off (streaming vs multi-pass, duplication vs rewrite) and the identification of the duplication pressure as the real cost driver.

## Pre-Design Reminders That Still Apply

From the prior "before-design" note:

- The prior attempt proved that the target is not blocked by Markdown.pl itself; the earlier difficulty was the fit between SPL's shape and the workload.
- Start from the validated block-level baseline rather than from the original multi-act wish list.
- Treat recursive dispatch, cached execution (where available), and buffered inline handling as candidate starting shapes.
- Keep the design mdtest-focused and fixture-driven. The 23 `Markdown.mdtest` fixtures are the success surface.
- The main ceiling risks are email autolink encoding (permanent divergence), emphasis backtracking edge cases, loose-list exactness, and exact nested-block compositions.

One line from the earlier note is intentionally dropped: the earlier note said "do not re-open the question of whether SPL can be made to work at all for Markdown.pl." Architecture planning in this repo is, by design, re-opening exactly that question — for a fresh build with no inherited implementation.

## Items the Prior Memo Left Open

These are the open items architecture planning in this repo must close:

- The concrete build order across risky fixture groups.
- The exact integration boundary between block and inline phases.
- The milestone sequence for chasing the `Markdown.mdtest` ceiling.
- A decision among options A/B/C (or a fourth shape).
