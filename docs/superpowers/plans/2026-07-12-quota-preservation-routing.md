# Quota-Preservation Priority (Smart Routing) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement quota-preservation priority routing in the MCO loop to deprioritize `claude` and `codex` quota groups for implementation and fix tasks, preserving their limits for planning tasks.

**Architecture:** Add a `PRESERVED_PLANNING_GROUPS` constant to `scripts/mco_loop.py`, update `available_executor` to perform two-pass selection (preferring non-planning groups first), and pass the `preserve_planning` flag from the main execution loop.

**Tech Stack:** Python 3, pytest

---

### Task 1: Add Unit Tests in tests/test_mco_loop.py

**Files:**
- Modify: `tests/test_mco_loop.py`

- [ ] **Step 1: Write the failing tests**
  Add the following unit tests at the end of [tests/test_mco_loop.py](file:///Users/jonathan/shakedown/tests/test_mco_loop.py) to cover the new two-pass selection behavior:

  ```python
  def test_available_executor_preserves_planning_groups() -> None:
      from scripts.mco_loop import Executor, available_executor
      executors = [
          Executor("claude-impl", "claude-sonnet", "claude"),
          Executor("agy-impl", "agy-flash", "agy"),
      ]
      state = {"cooldowns": {}}
      # When preserve_planning=True, agy-impl (index 1) should be chosen over claude-impl (index 0)
      selected, _ = available_executor(executors, state, now=100, preserve_planning=True)
      assert selected is not None
      assert selected.name == "agy-impl"


  def test_available_executor_falls_back_to_preserved_groups() -> None:
      from scripts.mco_loop import Executor, available_executor
      executors = [
          Executor("claude-impl", "claude-sonnet", "claude"),
          Executor("agy-impl", "agy-flash", "agy"),
      ]
      # agy is cooling down, so only claude is available
      state = {"cooldowns": {"agy": 200}}
      selected, _ = available_executor(executors, state, now=100, preserve_planning=True)
      assert selected is not None
      assert selected.name == "claude-impl"
  ```

- [ ] **Step 2: Run tests to verify they fail**
  Run: `uv run pytest tests/test_mco_loop.py -k "available_executor_preserves" -v`
  Expected: FAIL (or Type/Signature error because `preserve_planning` is not accepted yet).

- [ ] **Step 3: Commit**
  ```bash
  git add tests/test_mco_loop.py
  git commit -m "test: add unit tests for available_executor quota preservation"
  ```

---

### Task 2: Implement available_executor Two-Pass Routing

**Files:**
- Modify: `scripts/mco_loop.py`

- [ ] **Step 1: Define PRESERVED_PLANNING_GROUPS and update available_executor**
  Define `PRESERVED_PLANNING_GROUPS = {"claude", "codex"}` in [scripts/mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py) (near `ALLOWED_SECRET_NAMES`), and update [available_executor](file:///Users/jonathan/shakedown/scripts/mco_loop.py#L352) to implement the two-pass logic:

  ```python
  PRESERVED_PLANNING_GROUPS = {"claude", "codex"}
  ```

  ```python
  def available_executor(
      executors: Sequence[Executor],
      state: Mapping[str, object],
      now: int,
      preserve_planning: bool = False,
  ) -> tuple[Executor | None, int | None]:
      """Return the first executor whose quota group is not cooling down."""
      raw_cooldowns = state.get("cooldowns", {})
      cooldowns = (
          cast(Mapping[str, object], raw_cooldowns)
          if isinstance(raw_cooldowns, dict)
          else {}
      )

      def get_cooldown_expiry(exec: Executor) -> int:
          group_value = cooldowns.get(exec.quota_group, 0)
          executor_value = cooldowns.get(f"executor:{exec.name}", 0)
          group_until = int(group_value) if isinstance(group_value, int | float) else 0
          executor_until = (
              int(executor_value) if isinstance(executor_value, int | float) else 0
          )
          return max(group_until, executor_until)

      # Pass 1: Prioritize executors whose quota groups are NOT in PRESERVED_PLANNING_GROUPS
      if preserve_planning:
          for executor in executors:
              if executor.quota_group in PRESERVED_PLANNING_GROUPS:
                  continue
              until = get_cooldown_expiry(executor)
              if until <= now:
                  return executor, None

      # Pass 2: Fall back to checking all executors (including preserved groups)
      waits: list[int] = []
      for executor in executors:
          until = get_cooldown_expiry(executor)
          if until <= now:
              return executor, None
          waits.append(until)

      return None, min(waits) if waits else None
  ```

- [ ] **Step 2: Run tests to verify they pass**
  Run: `uv run pytest tests/test_mco_loop.py -v`
  Expected: PASS (all tests, including the new ones and all existing `available_executor` tests, must pass successfully).

- [ ] **Step 3: Commit**
  ```bash
  git add scripts/mco_loop.py
  git commit -m "feat: implement two-pass available_executor with quota-preservation"
  ```

---

### Task 3: Wire available_executor in the Main Loop

**Files:**
- Modify: `scripts/mco_loop.py`

- [ ] **Step 1: Set preserve_planning flag in main**
  In the `main` loop of [scripts/mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py#L933), update the call to `available_executor` to pass `preserve_planning=(action.kind is not ActionKind.PLAN)`:

  ```python
              executor, next_ready = available_executor(
                  pool,
                  state,
                  now,
                  preserve_planning=(action.kind is not ActionKind.PLAN),
              )
  ```

- [ ] **Step 2: Run all tests to verify no regressions**
  Run: `uv run pytest`
  Expected: PASS

- [ ] **Step 3: Commit**
  ```bash
  git add scripts/mco_loop.py
  git commit -m "feat: enable preserve_planning for implementation/fix tasks in loop main"
  ```
