# Malformed Reference Definitions Match the Oracle — Design

**Date:** 2026-07-22
**Status:** approved design (operator-reviewed in interactive session)
**Scope:** three SPL/IR bugs in reference-definition handling; one plan, one
branch, one PR. Separate from the in-flight `fix/ampersand-and-romeo-parity`
PR, which stays as-is.

## Problem

Three malformed reference-definition forms render incorrectly from the shipped
`./shakedown` binary. All three should render as literal paragraphs per the
Markdown.pl oracle; instead they are swallowed or corrupted. The bugs are
**pre-existing** (they also fail on `main`) and were surfaced — not caused — by
un-skipping three `test_act3_contracts.py` tests during the ampersand/Romeo PR
review. Those three tests are currently marked `xfail(strict=True)` pointing at
exactly this work.

Confirmed on the real binary:

| Input | Oracle | `./shakedown` (current) |
|---|---|---|
| `[not]:` | `<p>[not]:</p>` | *(empty)* |
| `[not]:   ` | `<p>[not]:   </p>` | *(empty)* |
| `[]: destination` | `<p>[]: destination</p>` | *(empty)* |
| `[x] : destination` | `<p>[x] : destination</p>` | `<p>x: destination</p>` |

The deliverable is the **SPL** (`shakedown.spl`, generated from the `src_ir/`
IR scenes). The Python interpreter (`scripts/splc/interpret.py`) is the fast
verification harness only; correctness is judged on `./shakedown` output and
the 23-fixture oracle parity suite.

## The oracle contract

`Markdown.pl`'s `_StripLinkDefinitions` strips a line as a definition **only**
when it matches, in order:

- `^[ ]{0,3}\[(.+)\]:` — 0–3 leading spaces, a **non-empty** label (`.+`),
  and a colon **immediately** after `]`; then
- optional `[ \t]*`, one optional newline, `[ \t]*`; then
- `<?(\S+?)>?` — a **non-empty** URL (at least one non-whitespace char).

Any line failing this stays in the body and renders as an ordinary paragraph.
All three failing inputs above violate one of these clauses, so all three must
render literally.

## Root cause — three distinct scene-level defects

### Bug 1 — empty label `[]:` accepted (Act I)
`src_ir/act1_ref_pure.py` `HECATE_REF_LABEL` enters its label-gathering loop
immediately after `HECATE_REF_BRACKET` keeps `[`. On the first iteration a `]`
glyph branches straight to `HECATE_REF_COLON` with **zero** label glyphs seen,
so `[]:` is treated as a valid label. The oracle's `\[(.+)\]` requires ≥1
label character.

**Fix direction:** require at least one label glyph before `]`→colon is
honored. An immediate `]` (or `NL`) after `[` falls through to "keep as body"
(`HECATE_REF_KEEP`).

### Bug 2 — empty URL `[not]:` accepted (Act I)
`HECATE_REF_URL_WS` allows the candidate to drop when it reaches `NL`/EOF even
though no non-whitespace URL glyph has been consumed. `[not]:` (nothing after
the colon) and `[not]:   ` (only spaces) both drop. The oracle requires
`\S+?` — at least one non-whitespace URL character.

**Fix direction:** the candidate becomes drop-eligible only after ≥1
non-whitespace (`\S`) URL glyph is seen; reaching `NL`/EOF beforehand keeps the
line as body.

### Bug 3 — lossy Act III replay `[x] :` (Act III)
Act I correctly **keeps** `[x] : destination` as body (verified: Act II output
is `\x01[x] : destination\x00`). Act III then runs a **second, redundant**
definition-detector (`LYRIC_DEFINITION_*`) over paragraph-leading `[…]:` text.
It correctly *rejects* the space-before-colon form (`HECATE`/`LYRIC` colon
check fails on the space) and routes to `LYRIC_DEFINITION_REPLAY_*` — but the
replay restoration is **lossy**: it drops `[`/`]` and collapses ` :`→`:`,
yielding `x: destination`.

**Fix direction (plan decides with evidence):** Act III's detector is
redundant with a correct Act I. The plan first proves whether Act III's
detector ever strips anything Act I (post-fix) misses, across all 23 fixtures
and the four regression inputs:

- **If provably redundant:** bypass/remove the Act III definition-detector so
  paragraph text goes straight to span traversal. This deletes a subsystem and
  frees Act III title budget. Preferred if the evidence supports it.
- **If it catches real cases:** keep the detector and fix
  `LYRIC_DEFINITION_REPLAY_*` to restore the rejected candidate byte-for-byte.

The decision is made from fixture evidence during implementation, not assumed
up front.

## Constraints the plan must honor

- **SPL literary protocol.** Any new guard scenes (bugs 1–2 likely need 1–2
  new Act I scenes) require scene-titles authored as controlled prose in
  `src/literary.toml`, reserved **up front in this plan**, never invented
  mid-task.
- **The 26-title budget (A4.5) is a process gate, not a technical ceiling.**
  It is the reserved pool of hand-authored Act I ref-machine titles; it exists
  to enforce "literary authorship at planning time." The IR automates scene
  *numbering* and goto wiring (mechanical); the budget governs title *prose*
  (artistic) — the two are complementary, not redundant. Because this is a
  planning session, reserving the additional guard-scene titles is the
  sanctioned path. If the existing A1 spare pool has capacity, promote spares;
  otherwise the plan authors the new titles as an explicit up-front reservation
  step. Codegen selects reserved prose and never synthesizes titles.
- **SPL structural rules:** two-person-per-scene rule; arithmetic-operator
  limits per statement.
- **Python/SPL consistency:** the Act I intrinsic (`act1_ref_pure.py`) and the
  2e ref-table build must stay consistent with the SPL scenes, but the SPL is
  the deliverable and the oracle is the judge.

## Verification gates (named for the plan)

- **New oracle-parity regression tests** for all four inputs (`[not]:`,
  `[not]:   `, `[]: destination`, `[x] : destination`) run through Act IV,
  asserting the exact oracle output. Author these as failing tests first (TDD).
- **The three `xfail(strict=True)` markers** in
  `tests/test_act3_contracts.py::test_act3_replays_rejected_definition_candidates_byte_for_byte`
  flip to passing. `strict=True` means they fail loudly the moment the bug is
  fixed — a built-in tripwire; the plan removes the `xfail` marks in the same
  change that fixes the behavior.
- **`tests/test_mdtest.py`** — all 23 oracle fixtures unchanged (no
  regression).
- **`tests/test_literary_compliance.py`** and
  **`tests/test_splc_generated_fragments.py`** green after regen.
- **Regenerate** `shakedown.spl` (`uv run python -m scripts.splc` +
  `scripts/assemble.py`) and re-verify the four inputs on the real `./shakedown`
  binary.

## Out of scope

- The ampersand/Romeo/literary PR (`fix/ampersand-and-romeo-parity`) — stays a
  separate, complete unit.
- Any reference-**link** resolution behavior (`[text][id]`) beyond these four
  definition forms.
- The Python intrinsics as an end in themselves — they are kept consistent, but
  no Python-only "fix" counts as resolving these bugs.

## Roadmap

New plan, added to `docs/superpowers/plans/plan-roadmap.md` and marked
in flight (no plan currently in flight). One plan → one branch → one PR.
