# Quota-Preservation Priority (Smart Routing) Design Spec

**Date:** 2026-07-12  
**Topic:** Quota Preservation  
**Reference:** [CLAUDE.md](file:///Users/jonathan/shakedown/CLAUDE.md), [mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py)

---

## 1. Context and Problem

Currently, the autonomous MCO loop runs in priority-queue order based on the config file [agent-loop.toml](file:///Users/jonathan/shakedown/agent-loop.toml). The implementation pool lists `claude-implement` (quota group: `claude`) as the first executor. 

This leads to the `claude` quota group being quickly exhausted by implementation and fix tasks. Once rate-limited or timed out, the entire `claude` group is placed on cooldown in [.agent/mco-loop-state.json](file:///Users/jonathan/shakedown/.agent/mco-loop-state.json). When a subsequent planning task arrives, the loop cannot use Claude models for planning (even though planning is less frequent and requires Claude's advanced capabilities).

---

## 2. Selected Design (Two-Pass Selection)

We will introduce a two-pass selection algorithm in [available_executor](file:///Users/jonathan/shakedown/scripts/mco_loop.py#L352) to deprioritize planning quota groups (`claude` and `codex`) for implementation tasks.

### 2.1 Preserved Groups Constant
We define the set of quota groups that should be preserved for planning at the top of [mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py):
```python
PRESERVED_PLANNING_GROUPS = {"claude", "codex"}
```

### 2.2 available_executor Modification
We add a `preserve_planning: bool = False` parameter to [available_executor](file:///Users/jonathan/shakedown/scripts/mco_loop.py#L352) (defaulting to `False` to preserve compatibility with existing invocations). When `preserve_planning=True`:
1. **Pass 1**: The function searches only for executors whose `quota_group` is **not** in `PRESERVED_PLANNING_GROUPS`. If a ready executor is found, it is returned immediately.
2. **Pass 2**: If no ready executor is found in Pass 1, the function scans the entire pool (including those in `PRESERVED_PLANNING_GROUPS`) and selects the first ready executor.
3. If no executor is ready, it calculates the minimum wait time across the entire pool.

### 2.3 Main Loop Updates
We update the invocation of `available_executor` in the `main` loop of [mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py#L933) to set `preserve_planning` dynamically:
```python
            executor, next_ready = available_executor(
                pool,
                state,
                now,
                preserve_planning=(action.kind is not ActionKind.PLAN),
            )
```

This guarantees that:
* Planning tasks directly access `claude`/`codex` in priority order.
* Implementation tasks try non-planning providers (`agy`, `xai`, `openrouter`) first, falling back to `claude`/`codex` only if all others are cooling down.

---

## 3. Verification Plan

### 3.1 Unit Testing
We will add new unit tests in [tests/test_mco_loop.py](file:///Users/jonathan/shakedown/tests/test_mco_loop.py) covering:
1. **No Preservation**: When `preserve_planning=False`, the selector uses standard priority order.
2. **Implementation Routing with Ready Non-Preserved**: When `preserve_planning=True` and a non-preserved model (e.g. `agy`) is ready, it bypasses ready preserved models (e.g. `claude`).
3. **Implementation Routing with No Ready Non-Preserved**: When `preserve_planning=True` but all non-preserved models are in cooldown, it falls back to a ready preserved model (e.g. `claude`).
4. **All Cooled Down**: When all models are cooling down, it correctly calculates the earliest wake-up time.
