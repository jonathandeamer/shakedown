# Shakedown Docs

Starting point for new agents. These docs support architecture planning and implementation for a Shakespeare Programming Language port of `Markdown.pl` v1.0.1 against the 23 `Markdown.mdtest` fixtures.

The repo root `CLAUDE.md` covers working conventions, tooling, and commit policy. This README maps the docs themselves.

## Reading Order for a New Agent

For an agent about to plan the Shakedown architecture:

1. [`lineage.md`](lineage.md) — one-minute lineage and why this repo exists.
2. [`markdown/target.md`](markdown/target.md) — the Markdown.pl surface Shakedown targets.
3. [`markdown/divergences.md`](markdown/divergences.md) — intentional differences from the oracle.
4. [`spl/reference.md`](spl/reference.md) — the SPL language reference (verified).
5. [`prior-attempt/architecture-lessons.md`](prior-attempt/architecture-lessons.md) — why the prior attempt stalled and which trade-offs surfaced.
6. [`prior-attempt/feasibility-lessons.md`](prior-attempt/feasibility-lessons.md) — what the prior experiments showed and which claims transfer to this repo.
7. [`markdown/fixture-outlook.md`](markdown/fixture-outlook.md) — risk tiers for a fresh build.
8. [`verification-plan.md`](verification-plan.md) — what is verified, what is retrospective, what is predicted, what is open.

## Directory Map

| Path | Purpose |
|---|---|
| `lineage.md` | Short lineage of the Shakedown / Snarkdown / Quackdown triad. |
| `verification-plan.md` | Claim inventory by bucket (A–E). |
| `spl/` | SPL language reference, style, codegen policy, and verification evidence. |
| `spl/reference.md` | Verified SPL semantics. |
| `spl/style-lexicon.md` | Legal expressive vocabulary and phrase patterns. |
| `spl/codegen-style-guide.md` | Implementation policy for recurring value phrases. |
| `spl/verification-evidence.md` | Probe programs and observed interpreter behaviour. |
| `spl/lexicon-sources.md` | Grammar and example-attested sources for lexicon entries. |
| `spl/probes/` | Runnable SPL probe programs cited by `verification-evidence.md`. |
| `markdown/` | The target behaviour. |
| `markdown/target.md` | Markdown.pl v1.0.1 surface and test fixtures. |
| `markdown/divergences.md` | Intentional divergences from the oracle. |
| `markdown/fixture-outlook.md` | Predictive risk tiers for each of the 23 fixtures. |
| `prior-attempt/` | Retrospective evidence from the earlier SPL attempt. |
| `prior-attempt/feasibility-lessons.md` | Consolidated feasibility findings from round 1 and round 2. |
| `prior-attempt/architecture-lessons.md` | Consolidated architecture memo and the A/B/C options. |
| `archive/` | Historical artifacts preserved for context, not current guidance. |
| `superpowers/specs/` | Design specs for sub-projects within Shakedown. |
| `superpowers/plans/` | Implementation plans for sub-projects. |

## Canonical Flow of Truth

- **Legality and verified semantics:** `spl/reference.md` (evidence: `spl/verification-evidence.md`).
- **Expressive vocabulary:** `spl/style-lexicon.md` (sources: `spl/lexicon-sources.md`).
- **Implementation policy for constants:** `spl/codegen-style-guide.md`.
- **Oracle behaviour:** `markdown/target.md` + `Markdown.pl` itself.
- **What is proven vs retrospective vs open:** `verification-plan.md`.

## What This Docs Set Does Not Do

- It does not commit to a Shakedown architecture. Architecture planning is the next step after reading these docs.
- It does not treat the prior attempt's feasibility verdicts as facts about this repository. They are retrospective evidence from a prior checkout; see `prior-attempt/feasibility-lessons.md` and `verification-plan.md` bucket C.
- It does not include a loop prompt. The replacement for the archived `docs/prompt-shakedown.md` will be written once architecture planning decides what a new agent should load.
