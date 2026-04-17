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

Start a new session with `docs/prompt-shakedown.md`.

## Setup

```bash
git config core.hooksPath .githooks  # activate conventional commit enforcement
uv sync                               # install dev dependencies
```

## run-loop

`run-loop` is a Python executable that drives autonomous agent sessions.
It switches automatically between codex and claude when one hits a usage limit.

```bash
./run-loop                            # default: docs/prompt-shakedown.md
./run-loop docs/some-other-prompt.md  # alternate prompt
```

- Default prompt: `docs/prompt-shakedown.md`
- State: `.agent/run-loop-state.json` (tracks which backend was last used)
- Completion marker: derived from prompt filename — `docs/prompt-<name>.md` → `.agent/complete-<name>.md`

To signal completion, write the marker file:
```bash
mkdir -p .agent && touch .agent/complete-shakedown.md
```
The run-loop checks for this file at the top of every iteration and exits when it exists.

`AGENTS.md` is a symlink to `CLAUDE.md` — same instructions served to Codex.

## Target interface

`tests/test_mdtest.py` invokes `./shakedown` as a subprocess — stdin Markdown, stdout HTML. The implementation requires two files:

- `shakedown.spl` — the SPL implementation
- `shakedown` — an executable shell wrapper that calls `shakespeare run shakedown.spl`

```bash
#!/usr/bin/env bash
shakespeare run "$(dirname "$0")/shakedown.spl"
```

`shakespeare` is the CLI provided by the `shakespearelang` Python package (the SPL interpreter).

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
- `docs/research/shakedown-spl-reference.md` — SPL language reference (critical for implementation)
- `docs/research/shakedown-mdtest-architecture-memo.md` — prescribed build shape for this attempt
- `docs/research/shakedown-mdtest-fixture-matrix.md` — fixture-by-fixture pass/fail predictions
- `docs/research/shakedown-divergences.md` — intentional divergences from Markdown.pl
- `docs/research/` — full provenance docs from the earlier Shakedown and Quackdown work
- `docs/lineage.md` — project history and lineage context
- `docs/prompt-shakedown.md` — agent prompt used by `run-loop`

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
| All 23 fixtures green | `1.0.0` |

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
