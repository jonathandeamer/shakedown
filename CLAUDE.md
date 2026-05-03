# CLAUDE.md

This file provides context for Claude Code sessions working in this repository.

## What is shakedown?

A port of John Gruber's `Markdown.pl` (v1.0.1) to SPL (Shakespeare Programming Language).
Reads Markdown from stdin, writes HTML to stdout. See **Target interface** below.

**Origin:** This project is part of a three-step Markdown.pl porting lineage:
- `shakedown` — the SPL attempt (this repo)
- `snarkdown` — the CURSED attempt (abandoned)
- `quackdown` — the DuckDB SQL implementation (complete)

All three share the same goal, the same 23 `Markdown.mdtest` test fixtures, and the same
Huntley-loop methodology. See `docs/lineage.md` for the full story.

Start a new session with `docs/README.md` as the entry point for the docs set.

**Intended workflow:** Interactive Claude sessions (with superpowers) are used for bootstrapping, design, and planning. Implementation sessions are operator-triggered and supervised: start a new session, invoke `superpowers:executing-plans` (or `superpowers:subagent-driven-development`), and work through the active plan task by task with the operator present.

## Roadmap first

Before starting SPL, plan, or implementation work, read:

- `docs/README.md`
- `docs/superpowers/plans/plan-roadmap.md`

The roadmap is the source of truth for what plan is in flight. Do not advance
implementation unless the roadmap has at most one in-flight plan. If no plan
is marked `in flight`, do not invent implementation work; return to
interactive planning from `docs/README.md`.

## Setup

```bash
git config core.hooksPath .githooks  # activate conventional commit enforcement
uv sync                               # install dev dependencies
```

## Implementation workflow

When a plan is marked `in flight` in `docs/superpowers/plans/plan-roadmap.md`,
start a supervised implementation session:

1. Read the roadmap and identify the active plan.
2. Invoke `superpowers:executing-plans` or `superpowers:subagent-driven-development`
   to work through the plan task by task.
3. The operator triggers each session manually and is present throughout.

`AGENTS.md` is a symlink to `CLAUDE.md` — same instructions served to Codex.

### Legacy: run-loop

The earlier approach used `run-loop`, a Python executor that drove autonomous
agent sessions via `docs/prompt-shakedown.md`. The code and prompt are
preserved for history but are no longer the active workflow.

```bash
./run-loop                            # legacy: use the active default prompt
./run-loop docs/some-other-prompt.md  # legacy: alternate prompt
```

State: `.agent/run-loop-state.json`. Completion marker: `.agent/complete-<name>.md`.

## SPL literary protocol for prompts and plans

SPL-changing prompts and implementation plans must use
`docs/superpowers/notes/spl-literary-protocol.md`. This includes work that edits
`src/*.spl`, `scripts/assemble.py`, `scripts/codegen_html.py`, or future SPL
generators. Prompt authors must include the protocol block or load it by
university reference, and SPL-changing plans must name the exact literary
compliance tests they expect the implementation agent to run.

Controlled SPL prose belongs in `src/literary.toml`. Source fragments should
refer to controlled titles, scene surfaces, Recall lines, and recurring
literary values with `@LIT.` placeholders that `scripts/assemble.py` resolves
when rebuilding `shakedown.spl`. Codegen should load configured value atoms
from the same TOML instead of hardcoding adjective chains. Do not hand-edit
`shakedown.spl` for literary surface changes; edit `src/*.spl` and
`src/literary.toml`, then rebuild with `uv run python scripts/assemble.py`.

## Target interface

`tests/test_mdtest.py` invokes `./shakedown` as a subprocess — stdin Markdown, stdout HTML. Everything else about the shape (single `.spl` file, shell wrapper, Python orchestrator, something else) is a design decision. The retrospective research (`docs/prior-attempt/`) is evidence from the prior attempt, not a prescription — the design should justify its choice against the current state of the interpreter and machine.

`shakespeare` is the CLI provided by the `shakespearelang` Python package (the SPL interpreter). Currently at `~/.local/bin/shakespeare` — may not be on PATH in a fresh shell.

## Interpreter cost (measured)

Current-repo baselines (B14, measured 2026-04-25, fresh subprocess each run):

| Fixture | Lines | First run | Median |
|---|---|---|---|
| `spl-cost-1k.spl` | ~1255 | 3.67s | 3.30s |
| `spl-cost-4k.spl` | ~5005 | 13.29s | 13.29s |
| `scene-count.spl` (200 scenes) | ~2005 | 5.44s | 5.25s |
| `reference-lookup-scale.spl` (N=20) | — | 1.68s | 1.56s |

Every run pays cold startup — no warm reuse (the interpreter has no persistent-process mode).
Scene count is not the dominant cost driver at ~200 scenes. See `docs/verification-plan.md` B14,
B17, B18 for full details and dispositions.

Historical context (prior codebase, does not transfer):
- Prior attempt's ~4k-line `.spl`: 17–26s cold and 2–3s per input thereafter.
- `./shakedown-dev` prototype (~372 lines): ~5.0s on empty input, ~4.8s on a small fixture.

See `docs/performance/budget.md`, `docs/verification-plan.md`, and
`docs/prior-attempt/feasibility-lessons.md` for full context.

## Run tests

```bash
uv run pytest                        # all tests
uv run pytest tests/test_mdtest.py   # Markdown.mdtest suite (23 fixtures)
uv run pytest -k "Auto links"        # single test by name
uv run pytest tests/test_run_loop.py # run-loop infrastructure tests
```

To validate a fixture against the Markdown.pl oracle directly:
```bash
perl ~/markdown/Markdown.pl < ~/mdtest/Markdown.mdtest/"Test Name.text"
```

## Tooling

```bash
uv run ruff check .  # lint Python
uv run ruff format . # format Python
uv run pyright       # type-check Python
uv run cz bump                              # bump version based on conventional commits since last tag
uv run git-cliff -o CHANGELOG.md           # regenerate full changelog
uv run git-cliff --unreleased --prepend CHANGELOG.md  # prepend unreleased commits only
```

## Python conventions

- **Type hints required** on all function signatures (parameters and return types).
- **No bare `Any`** without an inline comment explaining why it can't be avoided.
- **No `print()`** in library or application code. CLI operator scripts (`run-loop`) may use `print()` for status output.
- **Mock external calls** in unit tests (subprocesses, file I/O). Integration tests that invoke real backends must be marked `@pytest.mark.integration` and are excluded from the default `uv run pytest` run.

## Reference materials

- `~/markdown/Markdown.pl` — oracle; the thing being ported
- `~/mdtest/Markdown.mdtest/` — 23 test fixtures (.text input, .xhtml/.html expected)
- `docs/README.md` — entry point for the docs set
- `docs/spl/reference.md` — SPL language reference (verified)
- `docs/spl/verification-evidence.md` — probe programs and observed interpreter behaviour
- `docs/spl/style-lexicon.md` — legal expressive vocabulary
- `docs/spl/literary-spec.md` — canonical literary policy for character voice, act palettes, decorative surfaces, and future `src/literary.toml`
- `docs/spl/codegen-style-guide.md` — implementation policy for recurring value phrases
- `docs/spl/style-guide-validation.md` — validation status for the style lexicon and codegen guide
- `docs/architecture/selected-architecture.md` — pointer to the adopted architecture spec
- `docs/superpowers/plans/plan-roadmap.md` — staged implementation-plan ladder; live status of each plan
- `docs/markdown/target.md` — Markdown.pl v1.0.1 target surface
- `docs/markdown/divergences.md` — intentional divergences from the oracle
- `docs/markdown/oracle-mechanics.md` — Markdown.pl transform order and parity-critical mechanics
- `docs/markdown/oracle-fixture-audit.md` — strict local-oracle audit of the 23 fixtures
- `docs/markdown/reference-mechanics.md` — reference definition/link mechanics
- `docs/markdown/html-block-boundaries.md` — raw HTML block boundary rules
- `docs/markdown/list-mechanics.md` — list exactness, nesting, and tight/loose mechanics
- `docs/markdown/fixtures.md` — canonical fixture matrix plus feature-risk outlook
- `docs/architecture/decision-rubric.md` — optimization target and scoring questions for architecture proposals
- `docs/architecture/runtime-boundary.md` — runtime boundary and wrapper/SPL ownership questions
- `docs/architecture/encoding-and-scope.md` — encoding, stdin/stdout, and target-scope assumptions
- `docs/architecture/inherited-scaffold.md` — prototype scaffold surfacing
- `docs/performance/budget.md` — benchmark protocol and planning thresholds
- `docs/prior-attempt/architecture-lessons.md` — why the prior attempt stalled and which trade-offs surfaced
- `docs/prior-attempt/feasibility-lessons.md` — consolidated feasibility findings; which claims transfer
- `docs/verification-plan.md` — claim inventory (verified / retrospective / predicted / open)
- `docs/ralph-loop.md` — Huntley/Ralph loop methodology reference and how it applies here
- `docs/lineage.md` — short lineage context
- `docs/archive/` — historical artifacts; prefer live docs unless specifically checking history

## Docs Truth Hierarchy

- Treat `docs/spl/reference.md` as the canonical statement of SPL legality and verified interpreter semantics.
- Use `docs/spl/verification-evidence.md` for the probe programs and observed outputs behind those claims.
- Treat `docs/markdown/target.md` plus `~/markdown/Markdown.pl` as the oracle behaviour surface, with intentional exceptions only from `docs/markdown/divergences.md`.
- Use `docs/markdown/reference-mechanics.md`, `docs/markdown/html-block-boundaries.md`, `docs/markdown/list-mechanics.md`, and `docs/markdown/fixtures.md` as canonical Markdown planning inputs.
- Use `docs/architecture/selected-architecture.md` as the canonical pointer to the adopted architecture spec.
- Use `docs/architecture/decision-rubric.md`, `docs/architecture/runtime-boundary.md`, `docs/architecture/encoding-and-scope.md`, and `docs/performance/budget.md` as architecture-input rubrics and supporting rationale.
- Treat `docs/architecture/inherited-scaffold.md` as inherited prototype state, not as adopted architecture.
- Use `docs/verification-plan.md` to distinguish what is verified in this repo from retrospective evidence, predictions, and still-open questions.
- Treat `docs/spl/style-lexicon.md`, `docs/spl/literary-spec.md`, and `docs/spl/codegen-style-guide.md` as generation/policy docs, not parser truth. `docs/spl/literary-spec.md` is the canonical source for voice and palette policy; `docs/spl/style-guide-validation.md` records which representative claims are mechanically enforceable, which are demonstrable only, and which remain advisory policy.

## Git

Conventional commits enforced by `.githooks/commit-msg` (activated in Setup above).

### Commit types

| Type | Use for | Bumps version? |
|---|---|---|
| `feat` | User-facing functionality added to `shakedown.spl` | minor |
| `fix` | Bug fix in a deliverable or infrastructure — **not** for test-only changes | patch |
| `test` | Adding or fixing tests; use this instead of `fix:` when only test files change | no |
| `docs` | Documentation, specs, plans, design docs, READMEs | no |
| `experiment` | Feasibility study, experiment sketch, or research finding | no |
| `chore` | Tooling, infrastructure, config, build, cleanup, renaming | no |
| `refactor` | Code restructure with no behaviour change | no |
| `perf` | Performance improvement | patch |
| `ci` | CI/CD pipeline changes | no |
| `build` | Build system changes | no |
| `style` | Formatting only | no |
| `revert` | Revert a prior commit | depends |

### Breaking changes

Append `!` before the colon for breaking changes:

```
chore!: rename shakedown → something-else
```

### When to cut a version

Version = progress signal. Cut one when something is demonstrably working, not after every commit.

| Milestone | Version |
|---|---|
| First fixture passing end-to-end | `0.1.0` |
| Each additional fixture, or a coherent group (e.g. all inline elements) | minor bump |
| Bug fix in a passing fixture, no new capability | patch bump |
| Every fixture either passes or is documented as an accepted divergence in `docs/markdown/divergences.md` | `1.0.0` |

**Operator-only.** Implementation agents must NOT run `cz bump`,
`git tag`, `git push --tags`, or update `CHANGELOG.md` unless the current
plan step explicitly authorises it. Version cuts are operator decisions per
architecture spec §7.9.

### How to cut a version

```bash
uv run cz bump                              # computes bump from commits, updates pyproject.toml, commits + tags
uv run git-cliff -o CHANGELOG.md           # regenerate changelog up to the new tag
git add CHANGELOG.md
git commit -m "docs: update changelog for $(uv run cz version --project)"
```

`cz bump` reads conventional commits since the last tag to determine the bump type:
`feat` → minor, `fix`/`perf` → patch, any `!` breaking change → major.

### Common mistakes to avoid

- Don't use `feat:` for infrastructure or tooling — use `chore:`
- Don't use `feat:` for research or experiments — use `experiment:`
- Don't use `fix:` when only test files change — use `test:`
- Don't use scopes unless consistently used across the repo — omit them
- Don't use `feat:` for milestone markers or phase completions — use `chore:` or `docs:`
