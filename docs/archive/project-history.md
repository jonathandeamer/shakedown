> Archived 2026-04-17. Historical artifact from an earlier attempt. See `docs/lineage.md` for current guidance.

---

# Project History: From Shakedown to Quackdown

**Written:** 2026-04-11

This document traces the lineage of quackdown through two predecessor projects that each taught a hard lesson about language feasibility before the current approach was settled.

---

## The Goal

Port John Gruber's `Markdown.pl` (v1.0.1) to an esoteric or unusual programming language, using Geoffrey Huntley's AI-assisted porting methodology as the delivery mechanism:

- A **citation spec** maps all 23 `Markdown.mdtest` test cases to the relevant functions in `Markdown.pl`, so an agent always knows where to look
- A **test harness** validates output against the oracle and provides backpressure
- An **automated loop** (`while :; do cat docs/prompt.md | claude-code; done`) runs the agent one test at a time until all 23 pass
- A **short prompt** (under 200 words) drives each iteration; supporting detail lives in files loaded via `@` stack allocation

The methodology was chosen because Huntley demonstrated that this kind of disciplined, anchor-driven loop could reliably port non-trivial codebases between languages using AI agents. The esoteric language target was a deliberate constraint — part art project, part stress test of the approach.

---

## Chapter 1: Shakedown (Shakespeare Programming Language)

**Repository:** `~/shakedown/`  
**Dates:** 2026-04-03 to 2026-04-11  
**Language:** SPL — the Shakespeare Programming Language, where code is structured as a Shakespearean play (characters, acts, scenes, stage directions)

### What was built

Phase 1 was completed in full: a comprehensive pytest test harness (~200 tests across 14 modules), a citation spec, and a real implementation of `shakedown.spl` covering all block-level Markdown constructs:

- Paragraph emission
- ATX headings (`# Heading`)
- Setext headings (underlined with `=` or `-`)
- Horizontal rules
- Indented code blocks
- Blockquotes (simple, multiline, nested, lazy continuation, containing headings and code blocks)

This was roughly 50% of the total feature surface — everything block-level. The implementation reached 4,311 lines in a single SPL act.

### Why it stalled

SPL's control flow model has an immovable constraint: **backwards jumps across act boundaries are illegal.** The main processing loop (`read → classify → handle → loop back to read`) requires jumping backwards to the read scene after each block handler. This forces the entire pipeline into a single act.

The original design envisioned Acts I–IV as separate processing phases (read, block scan, inline processing, emit). That architecture is simply impossible in SPL — act transitions are one-way sequential fall-throughs, not calls. Any real multi-pass design would require Act I to consume all stdin into a buffer before falling through, which is a fundamental rewrite.

By the time blockquotes were complete, the single-act file had duplicated the same "before-block dispatch" and "content emission loop" patterns approximately five times each. Adding inline processing (Slice 2: emphasis, links, code spans, autolinks, images, escapes) would require scattering inline-scan sub-calls into every block handler's content loop — making the duplication worse.

A detailed architecture decision document was written (`docs/shakedown-2026-04-10-spl-act-architecture.md`) laying out three options. No decision was made. The last commit is that decision doc. The project stalled awaiting a direction.

### The performance problem

SPL's interpreter (`shakespearelang`) was slow on this machine (a Lightsail instance). Even an empty-input run took 17–26 seconds. Blockquote tests ran for minutes. A complete implementation would have made the full test suite prohibitively slow to iterate on — tight feedback loops are essential for the automated loop methodology to work.

### What was learned

SPL works — it is Turing-complete and does support stdin, loops, and conditionals. But its act-boundary rules make the intended architecture impossible without a full rewrite of the partially-complete implementation, and its performance on constrained hardware makes the feedback loop too slow for automated agent iteration. The project was not abandoned; it was set aside pending a decision that was never revisited.

---

## Chapter 2: Snarkdown (CURSED Programming Language)

**Repository:** `~/quackdown/` (originally `~/snarkdown/`)  
**Date:** 2026-04-11  
**Language:** CURSED — a Gen-Z-flavoured esoteric language where programs are `.💀` files using `vibez`, `spill`, and similar vocabulary

### The appeal

CURSED was chosen as a tonal contrast to SPL — chaotic and internet-native rather than theatrical and formal, but similarly weird. The Huntley methodology had already been adapted for shakedown; snarkdown would reuse the same test harness design and citation spec approach, just targeting a different runtime.

A full Phase 1 was scoped: CURSED test harness, citation spec, automated loop prompt, repo infrastructure. A design spec was written. Work began.

### The blocker

The CURSED compiler turned out to be an early-stage prototype. It supported exactly one stdlib module with one function: `vibez.spill("literal string")`. All other stdlib modules (`hash_drip`, `math_rand_tea`, `io_drip`, etc.) produced import warnings and were silently ignored.

More fundamentally: the compiler had **no stdin reading, no file I/O, no runtime conditionals, and no loops.** It was a constant-folding engine that could only emit strings decided entirely at compile time. A `test_harness.💀` was written to spec and compiled without errors — but when run, it produced no output. The compiled binary simply could not read anything.

The CURSED compiler is not a blocker in the sense of a missing feature that might be added. It is pre-alpha software that does not yet exist in the form required for any meaningful program. The entire CURSED ecosystem would need to be built before snarkdown could run.

### The pivot decision

Rather than wait for the CURSED compiler to mature (no timeline) or attempt to contribute to it (out of scope), the project pivoted. The test harness was rewritten in Perl — keeping the same interface, test discovery logic, normalisation, and diff format — and `test_harness.💀` was kept in the repository as a historical artifact and canonical CURSED source.

Then the question became: what language actually works?

---

## Chapter 3: Quackdown (DuckDB SQL)

**Repository:** `~/quackdown/` (renamed from `~/snarkdown/`)  
**Date:** 2026-04-11  
**Language:** DuckDB SQL — a single `.sql` file containing a chain of CTEs

### Why DuckDB

After CURSED and shakedown, the selection criterion shifted: **prove it works before committing.** A feasibility study was run against DuckDB v1.5.1 before any design work was done:

| Capability | Technique | Result |
|---|---|---|
| Regex with backreferences | `regexp_replace` with `\1` in replacement | ✅ |
| Chained inline markup | nested `regexp_replace` calls | ✅ |
| Paragraph grouping | islands-and-gaps window function | ✅ |
| Code block detection | classify + group by kind | ✅ |
| Two-line lookahead | `LEAD()` window function | ✅ |
| Reference link resolution | `WITH RECURSIVE` per-link substitution | ✅ |
| MD5 for HTML block stashing | `md5()` built-in | ✅ |
| Stdin reading | `read_text('/dev/stdin')` as table function | ✅ |

All seven capabilities confirmed. No fundamental blockers.

DuckDB SQL is also genuinely unusual as a target for a Markdown processor — an in-process analytical database doing string transformation work, structured as a single query — which preserves the art-project spirit of the original goal.

The remote GitHub repository was renamed from `snarkdown` to `quackdown`. The local directory was renamed to match. The CURSED artifacts (`test_harness.💀`, `docs/cursed-reference.md`) were removed in a commit, with their history preserved in git.

### Phase 1 completion

The Perl test harness was validated: **23 passed, 0 failed** against `Markdown.pl`. The shell wrapper (`quackdown`) was written:

```bash
#!/usr/bin/env bash
duckdb :memory: -noheader -list -f "$(dirname "$0")/quackdown.sql"
```

A minimal `quackdown.sql` stub was committed. The loop prompt (`docs/prompt.md`) was written at 197 words. All 18 commits were pushed to origin.

Phase 2 is ready to run.

---

## The Thread

All three projects share the same substrate: the Huntley-loop methodology, the same 23 `Markdown.mdtest` test cases, the same citation spec mapping tests to `Markdown.pl` functions, the same automated loop structure, the same test harness design. The methodology itself was never the problem.

Shakedown proved SPL's architecture is the wrong shape for a streaming processor. Snarkdown proved CURSED doesn't exist yet. Quackdown picked a runtime that was verified to work before the design was written.

The `docs/superpowers/` directory in this repository preserves the snarkdown design artifacts. The shakedown repository at `~/shakedown/` preserves that project's full history.
