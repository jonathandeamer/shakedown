# Findings for the Detailed Implementation Spec

**Date:** 2026-04-19
**Builds on:** `2026-04-18-p1-evidence.md`, `2026-04-18-p2-evidence.md`
**Purpose:** Post-prototype synthesis for the detailed implementation spec. Records what the prototype evidence docs don't: refinements to caveat handling, architectural patterns that generalise, tooling gaps, spec artifacts the detailed design must produce, and risks the prototypes did not cover.

## 1. Divergence Audit — Empirical

Verified against the mdtest corpus on 2026-04-19.

### Email autolink entity randomisation is moot for mdtest

`docs/markdown/divergences.md` documents that Markdown.pl randomly entity-encodes email autolink characters and Shakedown will not. **No mdtest fixture exercises this behaviour.**

- `~/mdtest/Markdown.mdtest/Auto links.text` contains zero email autolinks — only HTTP URLs, which Markdown.pl emits with plain literal characters (verified with `perl ~/markdown/Markdown.pl < "…/Auto links.text"`).
- Only two email-like strings appear in any `.text` fixture, both in `Markdown Documentation - Syntax.text`: one is inside a 4-space indented code block (rendered as `<pre><code>&lt;address@example.com&gt;</code></pre>`), the other is plain prose text. Neither triggers the autolink code path.
- `grep -P '^\S.*<[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+>'` across every `.text` returns zero matches.
- `mailto:` appears in zero expected outputs (`.xhtml`/`.html`).
- `tests/test_mdtest.py::_decode_entities` (applied only to the "Auto links" test) never fires on real content — the oracle produces no entity-encoded output for this fixture.

**Decision:** Keep the divergence entry as-is. It still accurately describes Markdown.pl behaviour, and preserving it is robust against future fixture additions. But the detailed spec should not spend effort implementing or designing around email autolink encoding — the passrate does not depend on it.

### Nested blockquote closer quirk

The second documented divergence (`<p></blockquote></p>` from Markdown.pl, bare `</blockquote>` from Shakedown). This is a *chosen* divergence for HTML validity, not a forced one. SPL can emit any byte sequence; matching the oracle's quirk would be simple state-tracking. If the detailed spec prefers byte-exact over valid, this is reversible.

## 2. Caveat Re-analysis — SPL-Only Workarounds

For each prototype caveat, an in-SPL path to match the oracle:

### Emphasis backtracking (currently P2 XFAIL)

Markdown.pl's behaviour comes from **two sequential regex passes**: strong `(\*\*|__)…\1` first, then emphasis `(\*|_)…\1` over the strong-substituted buffer. The overlapping `<em>foo <strong>bar</em> baz</strong>` output falls out naturally.

P2's single-flag toggle (Mercutio = open/closed) can't reproduce overlap. But a **two-pass inline emitter** can: one pass produces a buffer with `<strong>`/`</strong>` tags inserted; a second pass over that buffer inserts `<em>`/`</em>`. Cost: one additional reversal, roughly 40 scene lines. Converts the XFAIL to PASS.

The early P2 framing treated backtracking as a candidate divergence. This review supersedes that framing: the two-pass approach is well within the architecture's reach.

### Loose-list exactness (prior PARTIAL)

Original framing (from P2 architectural outlook): "track loose flag per nesting level" — handwaved the hard part. With nested lists, per-depth scalar state in SPL means N cast members or encoding depth+flag into a single integer. Both ugly.

**Better approach:** a dedicated cast member (suggested: `Cordelia, a registrar of list looseness`) as a stack. Push 0/1 on every `<ul>`/`<ol>` entry, pop on exit, stage-swap read at each `<li>` emit. Nesting handled natively; same idiom as Ophelia/Mercutio, but with push/pop rather than fixed-value read. Cost: one cast member, ~3 scenes.

### Nested block compositions (prior PARTIAL)

Prior attempt's fragility came from entangling *parse state* and *emit state* — Phase 2 and Phase 3 both carrying block context, so changes in one cascaded to the other.

**Better approach:** lift Phase 2 to emit a **balanced OPEN_X/CLOSE_X marker IR** — context-dependent decisions (tight vs loose `<li>`) resolved at parse time into distinct markers. Phase 3 becomes a pure tree-walker: one job, marker → HTML tag. No block state in Phase 3.

Benefits: nested compositions compose trivially (any balanced OPEN/CLOSE sequence is legal IR); Phase 3 stays linear regardless of nesting depth; Phase 2 and Phase 3 become independently testable.

Cost: ~15–20 new IR marker values (sub-printable range has ~22 positive values available, negatives unbounded). Phase 2 grows; Phase 3 shrinks.

### The unifying pattern

Both refinements use the same architectural move: **push decision-state onto a dedicated cast-member stack at parse time; consume it at emit time.** For loose-list the stack holds one bit per list frame; for nested blocks the stack holds the current-block-type. Same move, different state.

This is a strong pattern. Name it, codify it in the spec, apply it wherever state has hierarchy.

## 3. Architectural Refinements

### IR unification

P2 established "raw chars when wrapper is context-free, markers when state-dependent." At P2 scale (blockquote is context-free), raw-char push is fine. At full scale, more wrappers become state-dependent (`<li>` depends on looseness; paragraph nesting inside blockquote inside list requires coordinated close order). The raw-char-vs-marker split will become confusing.

**Recommendation:** migrate toward uniform balanced-tag marker IR at detailed-spec time. Markers for every block open/close; Phase 3 dispatches them into HTML tag chars. Keep raw-char push only for genuinely context-free cases (or retire it entirely for consistency).

### Phase 2 peek-at-line-start is a reusable pattern

P2 uses it for `>` (blockquote). The same pattern applies to:
- `*`, `-`, `+` followed by space → unordered list item
- `1.`, `2.` etc. followed by space → ordered list item
- `#`, `##`, `###` etc. → ATX heading
- `    ` (four spaces) → indented code block
- `---`, `***`, `___` → horizontal rule
- `> ` → blockquote

Canonical pattern: Recall-and-restore on the first character of each line. Generalise into a named idiom in the spec so every contributor applies it identically.

### Scene fall-through is load-bearing

Both P1 and P2 hit bugs from implicit fall-through between scenes with state mismatches. The P2 doc notes it; it should be elevated to a **style rule**: every scene tail must have an explicit `[Exeunt]`, `Let us return to scene @X`, or `Let us proceed to scene @Y`. No implicit fall-through. Enforceable via lint (see §4).

## 4. Tooling Gaps for Detailed Spec

Items that were fine at prototype scale but will not scale to full implementation.

### Codegen helper for raw-char push sequences

P2 hand-encoded 107 lines of `You are as good as <value>! / Remember yourself!` pairs just for blockquote open/close bytes. Full implementation will push `<ul>`, `<ol>`, `<li>`, `</li>`, `<h1>`–`<h6>`, `<pre>`, `</pre>`, `<strong>`, `</strong>`, `<em>`, `</em>`, `<a href="`, `">`, `</a>`, `<img src="`, `" alt="`, `/>`, `<hr />`, etc. — roughly 1000+ lines of value-phrase pairs if hand-encoded.

P1's surprise ("value-phrase arithmetic for 3-byte chars" → produced `ceee` instead of `code`) belongs to the same bug class: copy-pasting "nearby" value phrases without re-computing the arithmetic.

**Recommendation:** a Python helper — `push_chars(speaker: str, listener: str, text: str) -> str` — that emits the SPL lines for pushing each byte of `text` onto `listener`'s stack. ~80 lines. Eliminates the bug class entirely. Should land before the detailed spec's first fragment.

### Assembler → mini-linter

The assembler currently concatenates + resolves scene labels. Extensions:

- **Fall-through check.** Every scene body must end with `[Exeunt]`, `Let us return to scene …`, or `Let us proceed to scene …`. Regex-detect scene boundaries and verify tail. ~30 lines.
- **Label-collision check.** Already present (tested in `test_assemble.py`).
- **Dangling-reference check.** Already effectively present (unresolved `@LABEL` raises). Tighten.
- **Cast-member consistency.** Extract dramatis personae from preamble; fail if any speaker/listener elsewhere is not declared.

These are all cheap regex-based checks. Catches whole classes of runtime bugs at build time. The P2 `Mercutio is not on stage` bug would have been a fall-through-lint warning.

### Fragment-level test harness

Currently we test only end-to-end. Debugging a Phase 2 change means re-running Phase 1 and Phase 3 every iteration. At full implementation scale this becomes prohibitive.

**Proposal:** generated `test-phase2.spl` that has (Act I = synthesise Romeo's stack from a fixture's bytes, Act II = real Phase 2 under test, Act III = dump Hamlet's contents to stdout for verification). Same for Phase 3 in isolation. Let us TDD each fragment without the full pipeline.

Big inner-loop win as fragments grow. Worth investing in before the detailed spec locks in more fragment structure.

### Parser-warm test-suite orchestration

`CLAUDE.md` records 17–26 s cold and 2–3 s warm per input on this machine. Running 23 fixtures cold-per-run = 6–10 minutes. Running them against one warm parser = ~1 minute dominated by warm per-input cost.

`shakespeare run` reads stdin per invocation. Can one process serve many inputs? Needs investigation — if yes, the test harness should spawn one subprocess and feed all fixtures to it. If no, we accept the cold cost for CI but find ways to amortise in local dev (e.g., run only the fixture under test during the inner loop).

## 5. Spec Artifacts Required

Small documents the detailed spec must include, not as engineering but as bookkeeping. Each prevents a recurring bug class.

### IR marker budget table

Pre-allocate every marker value before implementation starts. Format:

| Value | Meaning | Introduced in |
|---|---|---|
| -1 | bottom sentinel / EOF | P1 |
| 1 | paragraph-open | P1 |
| 2 | paragraph-close | P1 |
| 3–22 | reserved for balanced-tag IR | detailed spec |
| 96 | literal backtick + code toggle | P1 |

Negative values (`-2, -3, …`) are unreserved and can carry additional markers if positive sub-printable space (values 3–31) runs out. Document the choice at allocation time.

### State-lifetime table

Track every stage-swap state character's phase-level lifecycle:

| Character | Role | Set in | Consumed in | Reset in |
|---|---|---|---|---|
| Ophelia | code-span state | Phase 3 @TOGGLE_CODE | Phase 3 @EMIT_LOOP | Phase 3 @FLIP3 prelude |
| Mercutio | emphasis state (P3) + BQ flag (P2) | Phase 2 @SEED_BQ_EMIT / Phase 3 @TOGGLE_EM | Phase 2 @FINISH / Phase 3 @EMIT_LOOP | Phase 2 @FINISH_END |

Without this table, the "Mercutio still carries 1 from Phase 2 into Phase 3" bug recurs every time a new state character is added. At 5–10 state characters this is no longer hand-trackable.

### Emit idiom

From P1 evidence doc: "Juliet speaks, sets Oberon's value, then tells Oberon to speak mind." Not obvious; bit us twice in P1. The detailed spec must codify this as the canonical emit idiom so no contributor reinvents it.

### Line-start peek pattern catalog

Document the Recall-and-restore pattern once, with a cast-agnostic template. Every block-start detector (blockquote, list items, headings, HR, code blocks) is a specialisation of this template. Writing it once saves N re-derivations.

## 6. Risks Not Yet Prototyped

Three features the prototypes did not cover that will need their own design attention.

### Setext headings need two-line lookahead

`Title\n===\n` is a heading; `Title\nSomething else\n` is a paragraph. You cannot decide which until you see the line *after* `Title`. Phase 2's current pattern is single-char lookahead (via Puck peek). Setext requires at least line-level lookahead — accumulate a whole line before committing to its block type.

Not a wall, but a different Phase 2 pattern than blockquote's single-char peek. Worth a P3-style prototype or a heavy spec section.

### Reference links are the real hard case

`[text][label]` + `[label]: http://example.com` interact across the whole document. Markdown.pl does a pre-pass collecting definitions into a Perl hash keyed by label. SPL has no keyed lookup.

Options:
- **Linear scan.** On each use, pop through a "references" stack, compare labels, push back. O(n²) but acceptable for mdtest-sized documents unless implementation timing evidence says otherwise.
- **Two-pass with inline substitution.** Pass 0 scans the input and emits a buffer with reference uses already substituted (if the definition appeared earlier or can be found by scanning forward). Pass 1 is the main block parse.
- **Defer to emit time.** Phase 2 emits a `REF_LOOKUP(label)` marker; Phase 3 (or a new Phase 4) resolves at emit time by scanning a refs-stack.

All three are plausible; at the time of this note, none had been prototyped. This was the largest remaining architectural risk before the 2026-04-23 pre-design hardening probes.

### IR inconsistency resolution

Already flagged in §3 under "IR unification." Listed here as well because the decision — raw-char push vs balanced-tag markers — is itself an architectural choice the detailed spec must make explicitly before implementation begins. Don't let it evolve ad-hoc.

## 7. Summary

Prototype results are stronger than the initial framing suggested:

- **Two of the three documented caveats have in-SPL workarounds** (emphasis backtracking → two-pass emitter; nested blockquote quirk → reversible choice). Only the email autolink divergence is genuinely accepted, and it doesn't affect the passrate.
- **The two prior PARTIALs are execution difficulty, not architectural walls**, and both fit the same "dedicated cast-member stack for decision-state" pattern.
- **Realistic passrate ceiling: ≥21/23 byte-exact, potentially 23/23** with the workarounds applied.

Items that should land before or during the detailed spec:

| Item | Category | Priority |
|---|---|---|
| Codegen helper for raw-char push | tooling | do first |
| Assembler fall-through lint | tooling | early |
| IR marker budget table | spec artifact | before implementation |
| State-lifetime table | spec artifact | before implementation |
| Emit idiom + line-start-peek patterns codified | spec artifact | before implementation |
| Fragment-level test harness | tooling | before mid-implementation |
| Parser-warm test orchestration | tooling | before mid-implementation |
| Reference-link prototype or heavy spec section | design | before reference-link implementation |
| Setext heading design | design | before heading implementation |
| IR unification decision | design | at spec time |
| Two-pass emphasis emitter design | design | at spec time |
| Loose-list `Cordelia` stack design | design | at spec time |
| Balanced-tag IR design | design | at spec time |

Feed these into the detailed implementation spec.
