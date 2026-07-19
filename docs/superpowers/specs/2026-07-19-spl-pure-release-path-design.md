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

---

## Addendum A1 (2026-07-19): Pure-op ownership vs interpreter assists

**Status:** accepted with plan Amendment A2 on
`docs/superpowers/plans/2026-07-19-spl-pure-release-path.md`.

### Problem observed

After Tasks 2–3 of the pure-release plan, the IR path achieved link/reference
parity by short-circuiting two scene labels inside
`scripts/splc/interpret.run_act`:

- `HECATE_REF_OPEN` → `apply_act1_reference_strip` (Python stack machine)
- `ACT_III_START` → `apply_act3_link_resolution` (Python stream rewrite)

Generated SPL for those labels remained non-semantic (goto lattices / ordinary
traverse entry). Pure `shakespeare run shakedown.spl` / `./shakedown` therefore
failed 7/23 mdtest fixtures (all link/image/docs aggregates that need strip +
resolve), while `./shakedown-parity` stayed green.

That state **does not** satisfy §D1 / §5.1 or this design’s success criteria.
Retiring `rewrite_task3_markdown` is necessary but not sufficient: **no Python
Markdown assist may run on the production or IR double path once pure ops
land.**

### Binding rule

1. **Semantic ownership** of strip and resolve is the **op-level IR** that
   lowers to SPL scenes, not a Python helper invoked by label name.
2. Helpers `act1_ref_strip.py` and `act3_link_resolve.py` are allowed only as
   **differential oracles** for tests after intrinsic retirement — never as
   `run_act` production behavior.
3. Act III general resolution is a **pre-pass** over PARA/HEADER text payloads
   (images then anchors) using the Act I Rosalind A1.2 table, then the existing
   span traverse. Slice-1 hardcoded Amps forest consult/emit scenes are not the
   general production mechanism.
4. Literary surfaces for the Act III pre-pass are reserved in plan Amendment A2
   (`RESOLVE_*`, 48 working + 12 spare). Act I pure lower reuses Amendment A1
   labels only.
5. Pure `shakespeare` integration (plan Task 5 Step 2) must not be declared
   green until plan Tasks **2L** and **3L** remove both interpret short-circuits
   and pass their gates.

### Non-changes

Architecture table (Act I strip, Act II blocks, Act III spans, Act IV emit),
forbidden third participant, forbidden silent token invention, and the email
autolink divergence are unchanged.
