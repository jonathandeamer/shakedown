# Run-Loop Review Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the review-identified `run-loop` contract regressions so default invocation fails clearly, cooldown retries instead of terminating, Claude resource-failure streaks reset correctly, and on-disk state remains authoritative across iteration boundaries.

**Architecture:** Keep the existing hardening state machine and patch only the contract gaps. Drive the fix with targeted tests in `tests/test_run_loop.py`, then add small helper functions in `run-loop` for default-prompt validation, cooldown entry, success-path counter reset, and strict state normalization.

**Tech Stack:** Python script, pytest, monkeypatch-based loop tests, local JSON state handling

---

## File Structure

- Modify: `run-loop`
  - Add a fail-fast default prompt check, cooldown helper behavior that re-enters the loop, strict state normalization on read/write, and success-path reset of Claude resource-failure streaks.
- Modify: `tests/test_run_loop.py`
  - Add regression tests for default prompt validation, cooldown retry semantics, state normalization, and Claude streak reset after useful progress.

## Task 1: Restore The Default Prompt Contract

**Files:**
- Modify: `tests/test_run_loop.py`
- Modify: `run-loop`

- [ ] **Step 1: Write the failing test for missing default prompt behavior**

Add this test to `tests/test_run_loop.py` near the main-loop tests:

```python
    def test_missing_default_prompt_exits_with_operator_error(
        self, monkeypatch, capsys
    ):
        class _MissingPrompt:
            def exists(self) -> bool:
                return False

        monkeypatch.setattr(_mod, "PROMPT_FILE", _MissingPrompt())

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=[])

        captured = capsys.readouterr()
        assert excinfo.value.code == 1
        assert "default prompt path is unavailable" in captured.err
        assert "pass an explicit prompt path" in captured.err
```

- [ ] **Step 2: Run the new default-prompt test to verify RED**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestMainLoop::test_missing_default_prompt_exits_with_operator_error -q
```

Expected:
- FAIL because `main()` currently treats the missing default prompt as a recoverable iteration failure instead of a startup contract error

- [ ] **Step 3: Implement minimal default-prompt validation in `run-loop`**

Add a helper near the prompt/marker setup code:

```python
def validate_default_prompt_path(prompt_file: Path) -> None:
    """Fail fast when the repo default prompt is intentionally unavailable."""
    if prompt_file.exists():
        return
    print(
        "run-loop: default prompt path is unavailable. Pass an explicit prompt path.",
        file=sys.stderr,
    )
    sys.exit(1)
```

Then in `main()`:

```python
    else:
        prompt_file = PROMPT_FILE
        complete_marker = COMPLETE_MARKER
        validate_default_prompt_path(prompt_file)
```

- [ ] **Step 4: Run the default-prompt test to verify GREEN**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestMainLoop::test_missing_default_prompt_exits_with_operator_error -q
```

Expected:
- PASS

- [ ] **Step 5: Commit the default-prompt contract fix**

Run:

```bash
git add run-loop tests/test_run_loop.py
git commit -m "fix: fail fast on missing default run-loop prompt"
```

Expected:
- one commit containing the startup contract fix and its regression test

## Task 2: Make Cooldown Retry And Keep State Fresh

**Files:**
- Modify: `tests/test_run_loop.py`
- Modify: `run-loop`

- [ ] **Step 1: Write the failing tests for cooldown retry and strict state normalization**

Add these tests to `tests/test_run_loop.py`:

```python
class TestRunLoopCooldown:
    def test_second_recoverable_failure_sleeps_and_reloads_state_before_retry(
        self, monkeypatch
    ):
        saved_states = []
        sleeps = []
        complete_checks = iter([False, False, True])
        loaded_states = iter(
            [
                {
                    "last_used": "claude",
                    "cooldown_until": 0,
                    "consecutive_recoverable_failures": 1,
                    "consecutive_claude_resource_failures": 0,
                    "last_failure_kind": "no_progress",
                    "last_output_fingerprint": "same",
                    "unexpected_key": "drop-me",
                },
                {
                    "last_used": "codex",
                    "cooldown_until": 0,
                    "consecutive_recoverable_failures": 0,
                    "consecutive_claude_resource_failures": 0,
                    "last_failure_kind": None,
                    "last_output_fingerprint": None,
                },
            ]
        )

        class _Marker:
            def exists(self) -> bool:
                return next(complete_checks)

        class _PromptFile:
            def read_text(self) -> str:
                return "prompt"

        monkeypatch.setattr(_mod, "COMPLETE_MARKER", _Marker())
        monkeypatch.setattr(_mod, "PROMPT_FILE", _PromptFile())
        monkeypatch.setattr(_mod, "load_state", lambda path: next(loaded_states))
        monkeypatch.setattr(
            _mod,
            "gather_claude_host_facts",
            lambda: {
                "mem_available_kib": 1_500 * 1024,
                "swap_enabled": True,
                "tmp_total_bytes": 1_000_000_000,
                "tmp_used_bytes": 100_000_000,
                "claude_tmp_bytes": 0,
            },
        )
        monkeypatch.setattr(
            _mod,
            "collect_repo_snapshot",
            lambda repo: {"tracked_paths": (), "untracked_paths": ()},
        )
        monkeypatch.setattr(_mod, "run_backend", lambda backend, prompt: (0, "same"))
        monkeypatch.setattr(_mod, "expand_refs", lambda text, repo: text)
        monkeypatch.setattr(_mod.time, "sleep", lambda seconds: sleeps.append(seconds))
        monkeypatch.setattr(
            _mod, "save_state", lambda path, state: saved_states.append(state.copy())
        )

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=["docs/archive/prompt-shakedown.md"])

        assert excinfo.value.code == 0
        assert sleeps == [3600]
        assert saved_states[0]["cooldown_until"] > 0
        assert "unexpected_key" not in saved_states[0]

    def test_load_state_silently_drops_unknown_keys(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text(
            json.dumps(
                {
                    "last_used": "codex",
                    "both_limited": False,
                    "unexpected_key": "drop-me",
                }
            )
        )

        loaded = load_state(p)

        assert loaded["last_used"] == "codex"
        assert "unexpected_key" not in loaded
```

- [ ] **Step 2: Run the cooldown tests to verify RED**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRunLoopCooldown -q
```

Expected:
- FAIL because cooldown still exits after sleep instead of retrying through the top-of-loop reload path
- FAIL because state normalization currently happens on load but not necessarily on every save path

- [ ] **Step 3: Implement minimal cooldown helper and strict save normalization in `run-loop`**

Add a helper:

```python
def enter_cooldown(state: dict[str, object]) -> None:
    """Persist cooldown state and back off before retrying."""
    state["cooldown_until"] = int(time.time()) + 3600
    save_state(STATE_FILE, state)
    time.sleep(3600)
```

Update `save_state()`:

```python
def save_state(path: Path, state: dict) -> None:
    """Write normalized state JSON, creating parent directories as needed."""
    normalized = normalize_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalized, indent=2))
```

Then replace both cooldown branches in `main()`:

```python
                enter_cooldown(state)
                continue
```

and

```python
                enter_cooldown(state)
                continue
```

Do not call `sys.exit(0)` in cooldown branches anymore.

- [ ] **Step 4: Run the cooldown tests to verify GREEN**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRunLoopCooldown -q
```

Expected:
- PASS

- [ ] **Step 5: Commit the cooldown/state-freshness fix**

Run:

```bash
git add run-loop tests/test_run_loop.py
git commit -m "fix: retry run-loop after cooldown"
```

Expected:
- one commit containing the cooldown contract repair and state normalization coverage

## Task 3: Reset Claude Resource Streaks On Useful Progress

**Files:**
- Modify: `tests/test_run_loop.py`
- Modify: `run-loop`

- [ ] **Step 1: Write the failing test for resetting Claude resource-failure streaks**

Add this test to `tests/test_run_loop.py`:

```python
class TestRunLoopSuccessResets:
    def test_useful_progress_resets_claude_resource_failure_streak(
        self, monkeypatch
    ):
        saved_states = []
        complete_checks = iter([False, True])
        snapshots = iter(
            [
                {"tracked_paths": (), "untracked_paths": ()},
                {"tracked_paths": ("run-loop",), "untracked_paths": ()},
            ]
        )

        class _Marker:
            def exists(self) -> bool:
                return next(complete_checks)

        class _PromptFile:
            def read_text(self) -> str:
                return "prompt"

        monkeypatch.setattr(_mod, "COMPLETE_MARKER", _Marker())
        monkeypatch.setattr(_mod, "PROMPT_FILE", _PromptFile())
        monkeypatch.setattr(
            _mod,
            "load_state",
            lambda path: {
                "last_used": "codex",
                "cooldown_until": 0,
                "consecutive_recoverable_failures": 1,
                "consecutive_claude_resource_failures": 2,
                "last_failure_kind": "backend_failure",
                "last_output_fingerprint": None,
            },
        )
        monkeypatch.setattr(_mod, "collect_repo_snapshot", lambda repo: next(snapshots))
        monkeypatch.setattr(_mod, "run_backend", lambda backend, prompt: (0, "made progress"))
        monkeypatch.setattr(_mod, "expand_refs", lambda text, repo: text)
        monkeypatch.setattr(
            _mod, "save_state", lambda path, state: saved_states.append(state.copy())
        )

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=["docs/archive/prompt-shakedown.md"])

        assert excinfo.value.code == 0
        assert saved_states[-1]["consecutive_recoverable_failures"] == 0
        assert saved_states[-1]["consecutive_claude_resource_failures"] == 0
```

- [ ] **Step 2: Run the streak-reset test to verify RED**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRunLoopSuccessResets -q
```

Expected:
- FAIL because the useful-progress path does not currently clear `consecutive_claude_resource_failures`

- [ ] **Step 3: Implement minimal success-path reset logic**

In `run-loop`, add:

```python
def reset_success_counters(state: dict[str, object]) -> None:
    """Clear failure streaks after useful progress."""
    state["both_limited"] = False
    state["consecutive_recoverable_failures"] = 0
    state["consecutive_claude_resource_failures"] = 0
    state["last_failure_kind"] = None
```

Then in the `classification == "useful_progress"` branch:

```python
            state["last_used"] = backend
            reset_success_counters(state)
```

- [ ] **Step 4: Run the streak-reset test to verify GREEN**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRunLoopSuccessResets -q
```

Expected:
- PASS

- [ ] **Step 5: Run the full run-loop test module**

Run:

```bash
uv run pytest tests/test_run_loop.py -q
```

Expected:
- PASS

- [ ] **Step 6: Run the full test suite**

Run:

```bash
uv run pytest -q
```

Expected:
- PASS

- [ ] **Step 7: Commit the streak-reset and final verification batch**

Run:

```bash
git add run-loop tests/test_run_loop.py
git commit -m "fix: reset run-loop claude failure streaks on progress"
```

Expected:
- one commit containing the success-path reset and final green verification

## Task 4: Final Review And Handoff

**Files:**
- Verify: `run-loop`
- Verify: `tests/test_run_loop.py`

- [ ] **Step 1: Review the final diff**

Run:

```bash
git diff -- run-loop tests/test_run_loop.py
```

Expected:
- changes limited to the loop script and its tests

- [ ] **Step 2: Check final repo status**

Run:

```bash
git status --short
```

Expected:
- no unexpected files from test scaffolding or local state churn

- [ ] **Step 3: Prepare the user-facing summary**

Summarize:

- how default invocation now fails fast
- how cooldown now sleeps and retries instead of terminating
- how state normalization silently drops unknown keys
- how useful progress resets Claude resource-failure streaks
- verification evidence from `tests/test_run_loop.py` and the full suite

## Self-Review

Spec coverage:
- default prompt contract is covered in Task 1
- cooldown retry and state authority are covered in Task 2
- Claude streak reset is covered in Task 3
- final review and handoff are covered in Task 4

Placeholder scan:
- no `TBD`, `TODO`, or deferred implementation placeholders remain

Type and naming consistency:
- helper names are consistent across tasks: `validate_default_prompt_path`,
  `enter_cooldown`, and `reset_success_counters`
