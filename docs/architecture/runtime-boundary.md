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

## Run-Loop Boundary

The replacement run-loop prompt is intentionally missing until architecture planning decides
what a new implementation agent should load. This document does not create that prompt and does
not choose the files it should reference.
