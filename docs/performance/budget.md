# Performance Budget and Benchmark Protocol

This document defines how Shakedown performance claims should be measured. It is a planning
input, not an architecture decision.

## Why This Exists

Prior timing notes mix several different things: interpreter startup, a prior 4k-line SPL file,
the current `./shakedown-dev` prototype, and pytest contract timing through the oracle stub.
Those numbers are useful only when the measured command and environment are clear.

## Required Metadata

Every timing claim records this minimum core:

- date;
- command (exact);
- input fixture or input size;
- run count and whether the reported value is first run, median, min, or max.

Add the following only when they might have varied across the runs being
compared:

- git commit or `git status --short` state;
- which shakedown variant (`./shakedown`, `./shakedown-dev`, `shakespeare run`, or oracle) — required if more than one is in scope;
- `which shakespeare` output — required if interpreter version drift is plausible;
- `UV_CACHE_DIR` — required if a run deviates from the pinned `/tmp/uv-cache` in Standard Commands.

Do not compare timings that omit the command or measured target.

## Standard Commands

Use `UV_CACHE_DIR=/tmp/uv-cache` for `uv run` commands unless there is a reason to measure a
fresh dependency cache.

### Contract Test Runtime

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -q
```

This measures the current regression contract. Today it mostly measures the oracle-stub wiring,
not production SPL Markdown semantics.

### Strict Oracle Audit Runtime

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/markdown_pl_parity_audit.py --output /tmp/shakedown-oracle-audit.md
```

This measures the audit tool and local Markdown.pl oracle comparison.

### Prototype Single-Input Runtime

```bash
/usr/bin/time -p ./shakedown-dev < /dev/null
/usr/bin/time -p ./shakedown-dev < tests/prototype/fixtures/p2_blockquote_input.md
```

Run each command five times and report the median plus the first-run value.

### Future Production Single-Fixture Runtime

Once `./shakedown` stops being an oracle stub, measure representative fixtures directly:

```bash
/usr/bin/time -p ./shakedown < ~/mdtest/Markdown.mdtest/"Code Spans.text"
/usr/bin/time -p ./shakedown < ~/mdtest/Markdown.mdtest/"Ordered and unordered lists.text"
/usr/bin/time -p ./shakedown < ~/mdtest/Markdown.mdtest/"Markdown Documentation - Syntax.text"
```

Run each command five times and report the median plus the first-run value.

## Planning Thresholds

These thresholds are for architecture planning and run-loop ergonomics, not user-facing product
requirements:

| Class | Green | Yellow | Red |
|---|---:|---:|---:|
| Single small fixture | <= 10s | <= 30s | > 30s |
| Single large fixture | <= 30s | <= 120s | > 120s |
| Full 23-fixture contract | <= 5m | <= 15m | > 15m |

A red result does not automatically reject an architecture; it triggers a conversation about
whether the cost is debuggable in the run-loop.

## Current Recorded Baselines

`docs/verification-plan.md` records the current baselines:

- **Interpreter startup** (empty `.spl`): about 0.10s cold (B1).
- **Current-repo SPL cost at 1k lines:** first-run and median per B14.
- **Current-repo SPL cost at 4k lines:** first-run and median per B14.
- **Current-repo scene-count-per-act (200 scenes):** first-run and median per B18.
- **Current-repo reference-lookup at fixture scale:** first-run and median per B17.
- **Current oracle-stub mdtest contract:** 23 passing tests in about 1.44s (B9).

### Historical / retrospective context

- **Prior 4k-line SPL (retrospective):** 17-26s cold and 2-3s warm on a prior codebase not present in this repo. Use B14 for current-repo claims.
- **`./shakedown-dev` prototype (2026-04-24):** about 5.0s on empty input and 4.8s on `tests/prototype/fixtures/p2_blockquote_input.md`. Prototype-scale only; use B14 for realistic-size claims.

Re-measure before making a performance-sensitive architecture decision.
