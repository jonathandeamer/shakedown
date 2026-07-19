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

### Long Regression Suite (parallelized)

`pytest-xdist` is adopted (dev dependency) for the spikes + token-dump
regression only — see B21 in `docs/verification-plan.md` for the full
worker-count sweep and decision:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py -q -n auto
```

Do not apply `-n auto` to `tests/test_mdtest.py`; that suite is dominated by
worker-startup overhead relative to its ~11s sequential wall time and showed
no material win in the B21 sweep.

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
- **Input-size execution scaling (2026-07-07):** ~11s fixed program cost plus ~0.11s per KB of input; a Syntax-sized (27KB) synthetic input runs in ~14s median (B20).
- **Regression-loop acceleration (2026-07-12):** `pytest-xdist -n auto` cuts the
  spikes + token_dump regression from ~207s to ~53s-60s (~3.5x-4x); adopted for
  that suite only. An in-process parsed-play runner prototype was proven
  state-isolated but not adopted — its per-call construction cost (~11s-13s)
  matches a fresh `./shakedown` subprocess, so it buys no wall-time win (B21).
- **Slice 4 release-entry gate (2026-07-18):** `./shakedown` on shipped
  representative fixtures measured first/median 0.08s for `Code Spans` and
  0.11s for `Ordered and unordered lists`; the full `uv run pytest -q` suite
  completed in 228.75s (3:48), all green against the planning thresholds
  (B22).
- **Slice 5 documentation-aggregate gate (2026-07-19, commit `a6e3b97`,
  clean tree):** five cold `./shakedown` runs each of the two §7.8 aggregates
  plus five runs of the full mdtest contract (B23):
  - `Markdown Documentation - Basics`: first 0.53s, median 0.36s
  - `Markdown Documentation - Syntax`: first 1.17s, median 1.17s
  - `env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -q`:
    first 5.84s real, median 5.75s real (36 passed, 0 skipped each run)
  - All three series are green against the planning thresholds (large
    fixture `<= 30s` green / `> 120s` red; full contract `<= 5m` green /
    `> 15m` red). No performance halt before Slice-5 shipment.

### Historical / retrospective context

- **Prior 4k-line SPL (retrospective):** 17-26s cold and 2-3s warm on a prior codebase not present in this repo. Use B14 for current-repo claims.
- **`./shakedown-dev` prototype (2026-04-24):** about 5.0s on empty input and 4.8s on `tests/prototype/fixtures/p2_blockquote_input.md`. Prototype-scale only; use B14 for realistic-size claims.

Re-measure before making a performance-sensitive architecture decision.
