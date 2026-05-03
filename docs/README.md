# Shakedown Docs

Starting point for new agents. These docs support implementation planning and execution for a Shakespeare Programming Language port of `Markdown.pl` v1.0.1 against the 23 `Markdown.mdtest` fixtures.

The repo root `CLAUDE.md` covers working conventions, tooling, and commit policy. This README maps the docs themselves.

## Reading Order for a New Agent

For an agent about to plan Shakedown implementation work, read the canonical docs in this order:

1. [`lineage.md`](lineage.md) — one-minute lineage and why this repo exists.
2. [`markdown/target.md`](markdown/target.md) — the Markdown.pl surface Shakedown targets.
3. [`markdown/divergences.md`](markdown/divergences.md) — intentional differences from the oracle.
4. [`markdown/oracle-mechanics.md`](markdown/oracle-mechanics.md) — Markdown.pl transform order and parity-critical mechanics.
5. [`markdown/reference-mechanics.md`](markdown/reference-mechanics.md) — reference definition/link mechanics.
6. [`markdown/html-block-boundaries.md`](markdown/html-block-boundaries.md) — raw HTML block boundary rules.
7. [`markdown/list-mechanics.md`](markdown/list-mechanics.md) — list exactness, nesting, and tight/loose mechanics.
8. [`markdown/oracle-fixture-audit.md`](markdown/oracle-fixture-audit.md) — where checked-in fixture files differ from fresh local oracle output.
9. [`markdown/fixtures.md`](markdown/fixtures.md) — fixture matrix plus feature-risk outlook.
10. [`spl/reference.md`](spl/reference.md) — the SPL language reference (verified).
11. [`spl/verification-evidence.md`](spl/verification-evidence.md) — probe outputs behind the SPL reference.
12. [`architecture/selected-architecture.md`](architecture/selected-architecture.md) — pointer to the adopted architecture spec.
13. [`architecture/decision-rubric.md`](architecture/decision-rubric.md) — how the selected architecture was evaluated.
14. [`architecture/runtime-boundary.md`](architecture/runtime-boundary.md) — runtime boundary inputs and cache caveats.
15. [`architecture/encoding-and-scope.md`](architecture/encoding-and-scope.md) — encoding, stdin/stdout, and target-scope assumptions.
16. [`architecture/inherited-scaffold.md`](architecture/inherited-scaffold.md) — prototype scaffold already in the repo; surfaced so planning engages with it as a choice, not a default.
17. [`performance/budget.md`](performance/budget.md) — benchmark protocol and planning thresholds.
18. [`prior-attempt/architecture-lessons.md`](prior-attempt/architecture-lessons.md) — why the prior attempt stalled and which trade-offs surfaced.
19. [`prior-attempt/feasibility-lessons.md`](prior-attempt/feasibility-lessons.md) — what the prior experiments showed and which claims transfer to this repo.
20. [`verification-plan.md`](verification-plan.md) — what is verified, what is retrospective, what is predicted, what is open.

**SPL style and literary policy for implementation planning:**

21. [`spl/style-lexicon.md`](spl/style-lexicon.md) — legal expressive vocabulary.
22. [`spl/literary-spec.md`](spl/literary-spec.md) — canonical literary policy for character voice, per-act palettes, and future `src/literary.toml` surfaces.
23. [`spl/codegen-style-guide.md`](spl/codegen-style-guide.md) — policy for recurring value phrases.
24. [`spl/style-guide-validation.md`](spl/style-guide-validation.md) — which style-guide claims are mechanically enforceable, demonstrable, or advisory.

Optional historical/supporting context:

- [`superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md`](superpowers/notes/2026-04-23-shakedown-pre-design-hardening.md) — latest pre-design synthesis. Useful context, not canonical truth.
- [`superpowers/specs/`](superpowers/specs/) — proposed design/spec artifacts from earlier interactive planning. The selected architecture spec is the one active exception and is linked from `architecture/selected-architecture.md`; other specs are historical context unless restated in canonical docs.
- [`superpowers/plans/`](superpowers/plans/) — implementation plans and process artifacts. Use `superpowers/plans/plan-roadmap.md` for live plan status.
- [`prompt-shakedown.md`](prompt-shakedown.md) — legacy `run-loop` prompt; no longer the active implementation workflow.

## Directory Map

| Path | Purpose |
|---|---|
| `lineage.md` | Short lineage of the Shakedown / Snarkdown / Quackdown triad. |
| `ralph-loop.md` | Huntley/Ralph loop methodology reference, with lineage lessons. |
| `verification-plan.md` | Claim inventory by bucket (A–E). |
| `architecture/` | Selected architecture pointer plus architecture inputs, rubrics, and runtime boundaries. |
| `architecture/selected-architecture.md` | Canonical pointer to the adopted architecture spec. |
| `architecture/decision-rubric.md` | Optimization target and scoring questions for future architecture proposals. |
| `architecture/runtime-boundary.md` | Runtime boundary and wrapper/SPL ownership questions. |
| `architecture/encoding-and-scope.md` | Encoding, stdin/stdout, and target-scope assumptions. |
| `architecture/inherited-scaffold.md` | Prototype scaffold surfacing (not adopted architecture). |
| `performance/` | Benchmark protocol and planning thresholds. |
| `performance/budget.md` | Standard commands and metadata for performance claims. |
| `spl/` | SPL language reference, style, codegen policy, and verification evidence. |
| `spl/reference.md` | Verified SPL semantics. |
| `spl/style-lexicon.md` | Legal expressive vocabulary and phrase patterns. |
| `spl/literary-spec.md` | Canonical literary policy for cast voice, per-act palettes, decorative surfaces, and future `src/literary.toml` authoring. |
| `spl/codegen-style-guide.md` | Implementation policy for recurring value phrases. |
| `spl/style-guide-validation.md` | Completed validation status for representative style-guide claims. |
| `spl/verification-evidence.md` | Probe programs and observed interpreter behaviour. |
| `spl/lexicon-sources.md` | Grammar and example-attested sources for lexicon entries. |
| `spl/probes/` | Runnable SPL probe programs cited by `verification-evidence.md`. |
| `markdown/` | The target behaviour. |
| `markdown/target.md` | Markdown.pl v1.0.1 surface and test fixtures. |
| `markdown/divergences.md` | Intentional divergences from the oracle. |
| `markdown/oracle-mechanics.md` | Local Markdown.pl transform order and parity-critical mechanics. |
| `markdown/oracle-fixture-audit.md` | Strict local-oracle audit of the 23 checked-in fixtures. |
| `markdown/reference-mechanics.md` | Reference definition, reference link, and reference image mechanics. |
| `markdown/html-block-boundaries.md` | Raw HTML block hashing and boundary rules. |
| `markdown/list-mechanics.md` | Markdown.pl list parsing, nesting, and loose/tight mechanics. |
| `markdown/fixtures.md` | Canonical fixture matrix plus feature-risk outlook. |
| `prior-attempt/` | Retrospective evidence from the earlier SPL attempt. |
| `prior-attempt/feasibility-lessons.md` | Consolidated feasibility findings from round 1 and round 2. |
| `prior-attempt/architecture-lessons.md` | Consolidated architecture memo and the A/B/C options. |
| `archive/` | Historical artifacts preserved for context, not current guidance. |
| `superpowers/specs/` | Historical proposed design/spec artifacts from earlier planning sessions, except the selected architecture spec linked from `architecture/selected-architecture.md`. |
| `superpowers/plans/` | Operational implementation plans and live roadmap; not canonical design truth. |

## Canonical Flow of Truth

- **Legality and verified semantics:** `spl/reference.md` (evidence: `spl/verification-evidence.md`).
- **Expressive vocabulary:** `spl/style-lexicon.md` (sources: `spl/lexicon-sources.md`).
- **Literary policy:** `spl/literary-spec.md` governs character voice, act palettes, decorative
  surfaces, and the future `src/literary.toml` data file.
- **Implementation policy for constants:** `spl/codegen-style-guide.md`.
- **Style-guide validation status:** `spl/style-guide-validation.md`.
- **Oracle behaviour:** `markdown/target.md` + `Markdown.pl` itself.
- **Oracle transform order and strict fixture caveats:** `markdown/oracle-mechanics.md` and `markdown/oracle-fixture-audit.md`.
- **High-risk Markdown mechanics:** `markdown/reference-mechanics.md`, `markdown/html-block-boundaries.md`, and `markdown/list-mechanics.md`.
- **Fixture-level planning:** `markdown/fixtures.md`.
- **Selected architecture:** `architecture/selected-architecture.md` points to the adopted architecture spec. It overrides architecture-input docs where the selected design has closed a choice.
- **Architecture-input rubrics:** `architecture/decision-rubric.md`, `architecture/runtime-boundary.md`, `architecture/encoding-and-scope.md`, and `performance/budget.md`.
- **Inherited prototype scaffold:** `architecture/inherited-scaffold.md` documents `./shakedown-dev`, `scripts/assemble.py`, `src/*.spl`, and generated `shakedown.spl`. These are prototype artifacts, not adopted architecture.
- **What is proven vs retrospective vs open:** `verification-plan.md`.
- **Operational process artifacts:** `docs/superpowers/plans/plan-roadmap.md` tracks live plan status. `docs/prompt-shakedown.md` is the legacy `run-loop` prompt. Other `docs/superpowers/` content is supporting context only, except for the selected architecture spec linked from `architecture/selected-architecture.md`.

## What This Docs Set Does Not Do

- It does not treat implementation plans as architecture truth. Plans are operational checklists tracked through `superpowers/plans/plan-roadmap.md`.
- It does not treat the prior attempt's feasibility verdicts as facts about this repository. They are retrospective evidence from a prior checkout; see `prior-attempt/feasibility-lessons.md` and `verification-plan.md` bucket C.
- It does not treat `docs/superpowers/plans/` as adopted architecture. It treats only the selected architecture spec linked from `architecture/selected-architecture.md` as adopted design.
- It does not treat the loop prompt as a design spec. `docs/prompt-shakedown.md` is operational run-loop input and should follow the roadmap's active-plan state.
