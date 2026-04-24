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

**Intended workflow:** Interactive Claude sessions (with superpowers) are used for bootstrapping, design, and planning. Huntley/run-loop autonomous loops are used for the actual implementation of `shakedown.spl`. The run-loop prompt is an output of implementation planning — it does not exist yet and should not be created until that planning is done.

## Setup

```bash
git config core.hooksPath .githooks  # activate conventional commit enforcement
uv sync                               # install dev dependencies
```

## run-loop

`run-loop` is a Python executable that drives autonomous agent sessions.
It switches automatically between codex and claude when one hits a usage limit.

```bash
./run-loop                            # currently broken: hard-coded default prompt was archived
./run-loop docs/some-other-prompt.md  # alternate prompt
./run-loop docs/archive/prompt-shakedown.md  # legacy archived prompt, if you explicitly want it
```

- Current code default: `docs/prompt-shakedown.md`
- Current docs reality: `docs/prompt-shakedown.md` was archived to `docs/archive/prompt-shakedown.md` and no replacement prompt exists yet
- **The missing prompt is intentional, not a gap to fill.** It is a planned output of implementation planning — do not create it during design or planning sessions.
- Practical guidance: start fresh sessions from `docs/README.md`; only use `run-loop` with an explicit prompt path until a new default prompt is written
- State: `.agent/run-loop-state.json` (tracks which backend was last used)
- Completion marker: derived from prompt filename — `docs/prompt-<name>.md` → `.agent/complete-<name>.md`

To signal completion, write the marker file:
```bash
mkdir -p .agent && touch .agent/complete-shakedown.md
```
The run-loop checks for this file at the top of every iteration and exits when it exists.

`AGENTS.md` is a symlink to `CLAUDE.md` — same instructions served to Codex.

## Target interface

`tests/test_mdtest.py` invokes `./shakedown` as a subprocess — stdin Markdown, stdout HTML. Everything else about the shape (single `.spl` file, shell wrapper, Python orchestrator, something else) is a design decision. The retrospective research (`docs/prior-attempt/`) is evidence from the prior attempt, not a prescription — the design should justify its choice against the current state of the interpreter and machine.

`shakespeare` is the CLI provided by the `shakespearelang` Python package (the SPL interpreter). Currently at `~/.local/bin/shakespeare` — may not be on PATH in a fresh shell.

## Interpreter cost (measured)

Retrospective measurements from the prior SPL attempt on this machine put `shakespeare run` on a
~4k-line `.spl` at 17–26s cold and 2–3s per input thereafter. Treat those numbers as prior-attempt
context, not as the current repo baseline.

Current repo-scale measurements are recorded in `docs/verification-plan.md`. On 2026-04-24, the
current `./shakedown-dev` prototype measured about 5.0s on empty input and 4.8s on
`tests/prototype/fixtures/p2_blockquote_input.md`. This is still load-bearing context for tooling
decisions (inner-loop test command, CI shape, whether to pre-parse), but the design chooses how to
live with it. See `docs/verification-plan.md`, `docs/archive/slow-machine-spl-workflow.md`, and
`docs/prior-attempt/feasibility-lessons.md`.

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
- `docs/spl/codegen-style-guide.md` — implementation policy for recurring value phrases
- `docs/spl/style-guide-validation.md` — validation status for the style lexicon and codegen guide
- `docs/markdown/target.md` — Markdown.pl v1.0.1 target surface
- `docs/markdown/divergences.md` — intentional divergences from the oracle
- `docs/markdown/oracle-mechanics.md` — Markdown.pl transform order and parity-critical mechanics
- `docs/markdown/oracle-fixture-audit.md` — strict local-oracle audit of the 23 fixtures
- `docs/markdown/fixture-outlook.md` — predictive risk tiers for each of the 23 fixtures
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
- Use `docs/verification-plan.md` to distinguish what is verified in this repo from retrospective evidence, predictions, and still-open questions.
- Treat `docs/spl/style-lexicon.md` and `docs/spl/codegen-style-guide.md` as generation/policy docs, not parser truth. `docs/spl/style-guide-validation.md` records which representative claims are mechanically enforceable, which are demonstrable only, and which remain advisory policy.

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
