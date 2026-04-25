# Runtime Boundary

This document defines the runtime questions every architecture must answer. It does
not choose an architecture.

## Current External Contract

`tests/test_mdtest.py` invokes `./shakedown` as a subprocess:

- stdin: Markdown fixture text
- stdout: rendered HTML
- expected output: checked-in `.xhtml` or `.html` fixture file, normalized by the test harness
- special comparison: the `Auto links` fixture decodes numeric entities before comparing

No command-line flags, input file paths, network access, or persistent service are part of
the current target interface.

## Boundary Shapes Still Open

Architecture planning may consider several runtime shapes:

| Shape | Boundary to document |
|---|---|
| Direct SPL | `./shakedown` invokes `shakespeare run shakedown.spl` and all Markdown semantics live in SPL. |
| Wrapper-assisted SPL | A wrapper manages interpreter invocation, environment, caching, or generated artifacts while Markdown semantics remain in SPL. |
| Generated SPL | A generator emits SPL source before execution; the architecture must state which source is authoritative. |
| Multi-stage runner | A wrapper coordinates several passes; each pass and data format must be documented. |

The current oracle-stub `./shakedown` is useful for contract wiring, but oracle delegation is
not a final Shakedown implementation.

## Required Runtime Claims

Any architecture proposal must state:

1. The executable path that users and tests call.
2. How stdin is read and how stdout is written.
3. Whether stderr is reserved for diagnostics.
4. Where Markdown semantics live.
5. Whether generated or cached files exist, where they are stored, and how they are invalidated.
6. How the design behaves when the SPL interpreter exits non-zero.
7. Which benchmark class from `docs/performance/budget.md` applies to inner-loop testing.

## Interpreter Constraints That Shape the Boundary

The installed `shakespearelang` CLI has `run`, `debug`, and `console` commands, but no
parse-only command. `docs/verification-plan.md` records this in B7. Any AST-cache strategy
therefore belongs in wrapper/tooling code unless future interpreter evidence changes that
claim.

SPL program code should be treated as a stdin/stdout transformation engine. `docs/spl/reference.md`
does not document SPL-level argv access, so user-facing flags belong in `./shakedown` or other
wrapper code, not inside the SPL play.

## Wrapper Toolchain

The project's existing scripts and test harness use Python 3 via `uv` (see `pyproject.toml` and `./run-loop`). The prototype entry-point `./shakedown-dev` is a bash shim that delegates to `uv run python scripts/assemble.py` and `uv run shakespeare run shakedown.spl`. Any wrapper-assisted architecture shape should use Python via `uv` as the wrapper toolchain unless it has a concrete reason to choose otherwise.

This is documentation of the toolchain already in use, not a new decision. Architecture planning may propose a different toolchain, but must justify the change given:

- existing Python scripts in `scripts/` (assembly, audit, measurement)
- existing pytest harness at `tests/test_pre_design_probes.py` and `tests/test_mdtest.py`
- existing `uv` dependency management via `pyproject.toml` and `uv.lock`
- existing `run-loop` Python entrypoint

## AST-Cache Feasibility

Prior-attempt round-2 experiment 6 (`docs/prior-attempt/feasibility-lessons.md`) reported that a pre-built AST cache reduced per-test cost from 1.09s to ~0.30s at 8,623 lines. That number is retrospective and does not transfer.

What does transfer:

- **The bottleneck the cache addressed.** B14 records cold `shakespeare run` cost at 1k and 4k lines in this repo. Compare B14's numbers to B1's 0.10s interpreter startup. The gap between startup and run cost is the parse-plus-execute window; caching can only shrink the parse portion.
- **The mechanism.** `shakespeare --help` lists no parse-only subcommand (B7). Any cache therefore lives in a Python wrapper. The canonical technique is to import `shakespeare.parser`, parse the `.spl` once, `pickle.dump` the AST to a side file, and on subsequent runs `pickle.load` and feed the AST to the interpreter. This is a Python-wrapper responsibility, not an SPL-level feature.
- **The decision shape.** Whether to build an AST cache depends on B14's cold-to-re-parse ratio. If cold runs are dominated by parse time (measurable by comparing `shakespeare run` cost to an AST-only parse timing), a cache likely helps. If they are dominated by execution time, a cache is wasted complexity.

Architecture planning should either demonstrate the cache is worth the wrapper complexity (with a current-repo measurement, not the retrospective 1.09 -> 0.30 number) or explicitly defer the cache until a bottleneck forces it.

## Run-Loop Boundary

The replacement run-loop prompt is intentionally missing until architecture planning decides
what a new implementation agent should load. This document does not create that prompt and does
not choose the files it should reference.
