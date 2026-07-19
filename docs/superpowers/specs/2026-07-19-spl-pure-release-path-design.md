# SPL-Pure Release Path — Design

**Date:** 2026-07-19  
**Status:** accepted for roadmap planning (successor to shipped Slice 5)  
**Scope:** Retire production Markdown work from Python so the committed play is the full deterministic engine under `shakespeare run shakedown.spl`.

## Decision

Shakedown’s public product is the committed `shakedown.spl` play executed by the
`shakespearelang` CLI. After Slice 5, **full Markdown.pl parity for links and
reference definitions still depends on a Python preprocess**
(`scripts.slice3_links.rewrite_task3_markdown`) plus a fast IR runner
(`scripts.release_runtime` / `./shakedown-parity`). That violates architecture
§D1 / §5.1 (“wrapper performs no Markdown work”) and breaks the packaging
story for pure `shakespeare run shakedown.spl`.

This design makes **SPL the sole Markdown semantic owner** for all deterministic
fixtures (email autolinks remain entity-normalized only — `docs/markdown/divergences.md`).

## Current facts (binding baseline)

1. **Slice 5 shipped** at commit `7958f66` (roadmap row 8): 23/23 under the
   IR + rewrite pipeline; performance evidence recorded.
2. **`rewrite_task3_markdown`** changes at least eight fixtures’ source text
   before the engine runs (measured 2026-07-19), including converting Markdown
   links/images into HTML and stripping reference definition lines. Example:
   Amps’s reference and inline links become `<a href=…>` before Act I sees them.
3. **`scripts.splc.interpret.run_act`** also calls
   `strip_reference_definitions` at Act I entry — a second Python Markdown
   touch on the fast path only.
4. **Act I** scene labels named `HECATE_LINE_STRIP_*_REFERENCE` do **not**
   implement Markdown.pl `_StripLinkDefinitions`; they are normalize/detab
   control flow. No document-scoped reference table is built in SPL today.
5. **Act III** has substantial link/image/autolink machinery (field tags,
   resume selectors, `LYRIC_*` scenes) but the production path never feeds it
   raw Markdown links when rewrite has already emitted HTML.
6. **Public entry** (packaging WIP on main): `./shakedown` →
   `uv run shakespeare run shakedown.spl`. **Parity harness entry:**
   `./shakedown-parity` → rewrite + IR. Both must converge on pure SPL.

## Target interface

```bash
uv sync
echo '…markdown…' | uv run shakespeare run shakedown.spl
# equivalent:
echo '…markdown…' | ./shakedown
```

Strict local-oracle parity for every deterministic mdtest fixture; Auto links
entity-normalized as today. No Python rewrite on this path.

## Architecture shape

Keep the four-act IR pipeline. Move Markdown.pl’s early link pass into the play:

| Markdown.pl stage | Owner after this work |
|---|---|
| `_StripLinkDefinitions` | **Act I** — remove definition lines; store case-folded id → (url, title) on Rosalind (stack layout fixed in plan Amendment A1 of `docs/superpowers/plans/2026-07-19-spl-pure-release-path.md`) |
| Block gamut | Act II (unchanged ownership) |
| `_DoImages` then `_DoAnchors` (and related span work) | **Act III** — resolve from the Act I table; missing ids leave original Markdown bytes; images before anchors |
| Emit | Act IV (unchanged ownership) |

**Forbidden:** new wrapper Markdown transforms; new token grammar unless the
inventory proves a gap and a plan amendment authorizes exact codes; third
participant in any scene; inventing literary titles mid-task.

**Allowed:** IR/SPL scenes for Act I table build and Act III resolution;
retaining `scripts/slice3_links.py` as a **test oracle / differential
reference** after production retirement; fast IR interpreter that runs the
same IR as the play **without** Python strip/rewrite once SPL owns the work.

## Non-goals

- CommonMark / GFM divergence cleanup  
- Performance optimization of cold `shakespeare` startup (document only)  
- Removing the IR interpreter (it remains the fast test double **iff** it
  matches pure SPL output without Python Markdown assists)  
- Changing the email-autolink divergence  

## Success criteria

1. `rewrite_task3_markdown` is **not** called from `release_runtime`,
   `preprocess_input` (if kept), or `splc.interpret` on any production path.
2. `./shakedown` and `uv run shakespeare run shakedown.spl` produce
   byte-identical HTML to local Markdown.pl on all deterministic fixtures
   (strict harness with `--shakedown ./shakedown`).
3. Default `uv run pytest` stays usable: IR path without Python rewrite
   matches pure-SPL (or a documented slow integration gate covers pure SPL
   while IR remains bit-identical for the default suite).
4. README primary demo remains pure shakespeare; `./shakedown-parity` either
   becomes a pure-SPL alias or is removed after migration.
5. Roadmap row for this plan marked shipped with final SHA.

## Risks and halt triggers

| Risk | Halt |
|---|---|
| Act I table needs a third simultaneous participant | `BLOCK[plan]` — redesign carrier |
| Act III cannot resolve without new stream tokens | `BLOCK[plan]` — exact token amendment |
| Pure SPL runtime exceeds budget for docs fixtures | Record performance evidence; do not reintroduce Python Markdown; optional later cache work is separate |
| IR and real SPL diverge after rewrite retirement | Fix IR or mark pure-SPL as sole release truth; never re-add rewrite to “fix” IR |

## Relationship to packaging WIP

Uncommitted packaging work (env-based fixture paths, `./shakedown` as
shakespeare CLI, `./shakedown-parity` for harness) is **prerequisite hygiene**
for this plan’s gates. Land it (or equivalent) before pure-SPL enablement so
tests have a stable public vs harness entry story.

## References

- Architecture: `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` §D1, §5.1  
- Reference mechanics: `docs/markdown/reference-mechanics.md`  
- Slice 3 design (original intent): `docs/superpowers/specs/2026-07-14-slice-3-medium-risk-design.md`  
- Divergences: `docs/markdown/divergences.md`  
- Literary protocol: `docs/superpowers/notes/spl-literary-protocol.md`  
- Correctness-first literary workflow: `docs/superpowers/notes/correctness-first-spl-workflow.md`  
