# Architecture Decision Rubric

This rubric defines how to compare future Shakedown architecture proposals. It is an
input to architecture planning, not an architecture choice.

## Non-Negotiable Gates

Any candidate architecture must satisfy these before trade-offs are scored:

1. Preserve the target interface: `./shakedown` reads Markdown from stdin and writes HTML to stdout.
2. Keep `~/markdown/Markdown.pl` as an oracle and test tool only. The final Shakedown
   implementation must not use Markdown.pl as its production Markdown transformer.
3. Treat `docs/markdown/divergences.md` as the only accepted divergence list.
4. Explain which Markdown behaviour is implemented in SPL and which, if any, is handled by
   wrapper/tooling code.
5. Provide a fixture-by-fixture verification path for all 23 `Markdown.mdtest` fixtures.

## Priority Order

Use this order when two goals conflict:

1. **Observable correctness.** The normalized `tests/test_mdtest.py` contract is the first
   regression gate. Deterministic Markdown.pl behaviour should then move toward strict
   local-oracle parity.
2. **Documented parity exceptions.** Email auto-link byte identity is unavailable in a pure
   SPL implementation unless runtime help is added. Entity-normalized equivalence is the
   documented target for that case.
3. **Fixture-level verification.** A design that makes each fixture's status explainable is
   preferred over one that only reports aggregate pass counts.
4. **SPL ownership of Markdown semantics.** Markdown parsing and rendering logic should live
   in SPL when feasible. Helper code may be proposed for orchestration, generation, caching,
   or benchmarking, but it must not obscure where Markdown semantics are implemented.
5. **Maintainability and debuggability.** Prefer designs with clear state carriers, repeatable
   probes, and local reasoning over designs that save lines but make failures opaque.
6. **Runtime cost.** Runtime matters for the Huntley/run-loop workflow and CI shape, but it
   should not justify accepting incorrect output. Use `docs/performance/budget.md` when
   comparing performance claims.

## Scoring Questions

For each candidate architecture, answer these questions explicitly:

| Criterion | Strong answer | Weak answer |
|---|---|---|
| Normalized mdtest parity | Names the route to all 23 fixtures and the first fixture milestone | Only says "run mdtest" |
| Strict oracle parity | Identifies deterministic byte-parity gaps and how they are tested | Ignores raw oracle output |
| SPL/helper boundary | States exactly what is SPL, generated, cached, or wrapper-owned | Treats the wrapper as an implementation detail |
| State model | Names state carriers for references, lists, block recursion, and inline scanning | Relies on unspecified global state |
| Verification | Provides fixture-level and feature-level checks | Provides only aggregate test counts |
| Performance | Uses the benchmark protocol and records environment details | Uses one-off timing anecdotes |
| Debuggability | Describes how to isolate a failing fixture or transform phase | Requires reading a monolithic trace |

## What This Rubric Does Not Decide

- Whether Shakedown is single-pass, multi-pass, generated SPL, wrapper-assisted, or another shape.
- Whether AST/cache help is used.
- Fixture implementation order.
- Whether any future non-SPL helper is acceptable for a specific purpose.

Those remain architecture decisions.
