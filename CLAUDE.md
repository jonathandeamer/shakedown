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

### Active autonomous workflow

`./agent-loop` is the active autonomous alternative. It uses MCO as the only
agent orchestration layer, reads the roadmap/active plan on every iteration,
and dispatches exactly one writing provider. Planning agents autonomously
write Superpowers-style plans/specs and leave exactly one plan in flight;
implementation/fix agents execute one unchecked step and its evidence gate.
Every successful iteration commits at logical checkpoints using the repository's
conventional-commit rules and pushes the current branch. Never force-push;
failed pushes are recorded as blockers rather than hidden.
Contrary to any generic agent guidance that omits attribution, every autonomous
commit must end with `Agent:`, `Model:`, and `Harness:` Git trailers and the
configured `Co-authored-by:` identity for that executor. The operator's Git
identity remains the primary author.

```bash
npm install -g @tt-a1i/mco@0.10.8
./agent-loop --dry-run
./agent-loop --once
./agent-loop

# Run in background with unbuffered output logged
PYTHONUNBUFFERED=1 ./agent-loop > .agent/loop.log 2>&1 &

# Tail real-time execution progress
tail -f .agent/loop.log
```

Configuration: `agent-loop.toml` and `.mco/agents.yaml`. Ignored state and
artifacts: `.agent/mco-loop-state.json` and `.agent/mco-artifacts/`. API keys
are loaded by name from the configured external env file and must never be
committed. Claude Fable is excluded from automatic routing; use the expensive
read-only governor only after genuine systemic failure:

```bash
./agent-loop --govern
```

`AGENTS.md` is a symlink to `CLAUDE.md` — same instructions served to Codex. For detailed documentation on workflow states, execution mechanics, failover/cooldown policies, and real-time monitoring of the autonomous loop, see [docs/2026-07-12-mco-loop-details.md](file:///Users/jonathan/shakedown/docs/2026-07-12-mco-loop-details.md).


### Legacy: run-loop
The older Python `run-loop` approach is legacy and no longer active (state: `.agent/run-loop-state.json`).

## SPL literary protocol for prompts and plans

SPL-changing prompts and implementation plans must use
`docs/superpowers/notes/spl-literary-protocol.md`. This includes work that edits
`src_ir/*.py`, `scripts/splc/*`, `src/*.spl`, `scripts/assemble.py`, or
`scripts/codegen_html.py`. Prompt authors must include the protocol block or
load it by university reference, and SPL-changing plans must name the exact
literary compliance tests they expect the implementation agent to run.

Controlled SPL prose belongs in `src/literary.toml`. Source fragments should
refer to controlled titles, scene surfaces, Recall lines, and recurring
literary values with `@LIT.` placeholders that `scripts/assemble.py` resolves
when rebuilding `shakedown.spl`. Codegen should load configured value atoms
from the same TOML instead of hardcoding adjective chains.

### Two-tier build: splc IR → fragments → `shakedown.spl`

`shakedown.spl` is assembled from the `src/*.spl` fragments listed in
`src/manifest.toml` by `scripts/assemble.py`. Several of those fragments are
**generated, not hand-authored**: the splc compiler (`scripts/splc/`) lowers
the IR act modules in `src_ir/` to SPL text.

- Generated fragments (edit the IR, never the `.spl`): `src_ir/act1.py` →
  `src/10-act1-preprocess.spl`, `src_ir/act2.py` → `src/20-act2-block.spl`,
  `src_ir/act3.py` → `src/30-act3-span.spl`, `src_ir/act4.py` →
  `src/40-act4-emit.spl`, and `src_ir/debug_act4.py` →
  `debug/40-act4-token-dump.spl`.
- Still hand-authored: `src/00-preamble.spl` only. All four acts are
  generated from `src_ir/` (Act III was ported by plan 3J, 2026-07-06).

Do not hand-edit `shakedown.spl` for literary surface changes, and do not
hand-edit any generated fragment. For a generated act, edit its `src_ir/*.py`
module (and `src/literary.toml` for controlled prose), then regenerate and
reassemble:

```bash
uv run python -m scripts.splc          # re-render generated fragments from src_ir/
uv run python scripts/assemble.py      # rebuild shakedown.spl from src/manifest.toml
```

For a hand-authored fragment, edit the `.spl` and `src/literary.toml`
directly, then reassemble. `tests/test_splc_generated_fragments.py` fails if a
committed generated fragment drifts from a fresh render.

Literary authorship happens at planning time, not implementation time:
see `docs/superpowers/notes/correctness-first-spl-workflow.md`. Plans
reserve all controlled prose (plus spare scene titles) up front, and
implementation agents never invent literary surfaces mid-task.

## Target interface

`tests/test_mdtest.py` invokes `./shakedown` as a subprocess — stdin Markdown, stdout HTML. Everything else about the shape (single `.spl` file, shell wrapper, Python orchestrator, something else) is a design decision. The retrospective research (`docs/prior-attempt/`) is evidence from the prior attempt, not a prescription — the design should justify its choice against the current state of the interpreter and machine.

`shakespeare` is the CLI provided by the `shakespearelang` Python package (the SPL interpreter). Currently at `~/.local/bin/shakespeare` — may not be on PATH in a fresh shell.

## Interpreter cost
Every run of the SPL interpreter pays cold startup (no warm reuse/persistent process). Scene count is not the dominant cost driver. Baseline details are in [verification-plan.md](file:///Users/jonathan/shakedown/docs/verification-plan.md) (B14/B17/B18) and [budget.md](file:///Users/jonathan/shakedown/docs/performance/budget.md).

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
uv run python scripts/query_docs.py "query"  # query active documentation paragraphs to save tokens
```

## Python conventions

- **Type hints required** on all function signatures (parameters and return types).
- **No bare `Any`** without an inline comment explaining why it can't be avoided.
- **No `print()`** in library or application code. CLI operator scripts (`run-loop`) may use `print()` for status output.
- **Mock external calls** in unit tests (subprocesses, file I/O). Integration tests that invoke real backends must be marked `@pytest.mark.integration` and are excluded from the default `uv run pytest` run.

## Documentation & Reference Truth Hierarchy

For a complete map, directory, and reading order of all documentation, start at [docs/README.md](file:///Users/jonathan/shakedown/docs/README.md).

> [!WARNING]
> Do NOT read or search files inside `docs/archive/`. Those are historical, shipped, or superseded plan artifacts and are irrelevant to active development.

* **Oracle & Fixtures**: Oracle is `~/markdown/Markdown.pl`. Test inputs/outputs are under `~/mdtest/Markdown.mdtest/`. See [target.md](file:///Users/jonathan/shakedown/docs/markdown/target.md) and [divergences.md](file:///Users/jonathan/shakedown/docs/markdown/divergences.md).
* **Roadmap & Active Plan**: Live roadmap is [plan-roadmap.md](file:///Users/jonathan/shakedown/docs/superpowers/plans/plan-roadmap.md).
* **SPL Semantics Truth**: [reference.md](file:///Users/jonathan/shakedown/docs/spl/reference.md) is the canonical statement of SPL legality and verified interpreter behavior.
* **Architecture Truth**: [selected-architecture.md](file:///Users/jonathan/shakedown/docs/architecture/selected-architecture.md) points to the adopted architecture spec.
* **Literary/Style Truth**: [style-lexicon.md](file:///Users/jonathan/shakedown/docs/spl/style-lexicon.md), [literary-spec.md](file:///Users/jonathan/shakedown/docs/spl/literary-spec.md), and [codegen-style-guide.md](file:///Users/jonathan/shakedown/docs/spl/codegen-style-guide.md) govern code generation and literary compliance.
* **Verification & Claims**: [verification-plan.md](file:///Users/jonathan/shakedown/docs/verification-plan.md) distinguishes verified vs open claims.

## Git

Conventional commits enforced by `.githooks/commit-msg` (activated in Setup above).

### Commit types

| Type | Use for |
|---|---|
| `feat` | User-facing functionality added to `shakedown.spl` |
| `fix` | Bug fix in a deliverable or infrastructure — **not** for test-only changes |
| `test` | Adding or fixing tests; use this instead of `fix:` when only test files change |
| `docs` | Documentation, specs, plans, design docs, READMEs |
| `experiment` | Feasibility study, experiment sketch, or research finding |
| `chore` | Tooling, infrastructure, config, build, cleanup, renaming |
| `refactor` | Code restructure with no behaviour change |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |
| `build` | Build system changes |
| `style` | Formatting only |
| `revert` | Revert a prior commit |

### Breaking changes

Append `!` before the colon for breaking changes:

```
chore!: rename shakedown → something-else
```

### Versioning

This repo does not use semantic versioning or automated version bumps.
`pyproject.toml` stays pinned at `0.0.1`; there is no `CHANGELOG.md`, no
`cz bump`, and no version-cut ceremony. Progress is tracked through
`docs/superpowers/plans/plan-roadmap.md` and git history, not a version
number.

### Common mistakes to avoid

- Don't use `feat:` for infrastructure or tooling — use `chore:`
- Don't use `feat:` for research or experiments — use `experiment:`
- Don't use `fix:` when only test files change — use `test:`
- Don't use scopes unless consistently used across the repo — omit them
- Don't use `feat:` for milestone markers or phase completions — use `chore:` or `docs:`
