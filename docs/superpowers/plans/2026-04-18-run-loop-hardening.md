# Run-Loop Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden `run-loop` so backend failures, no-progress iterations, and Claude memory pressure are handled by a graceful switch-or-sleep state machine instead of tight retry loops or permanent exits.

**Architecture:** Keep `run-loop` as a single script, but add small helper functions for repo snapshotting, output fingerprinting, iteration classification, cooldown handling, and Claude temp cleanup. Drive the change with tests first in `tests/test_run_loop.py`, then implement the minimal script changes needed to make each batch pass.

**Tech Stack:** Python script, pytest, monkeypatch-based unit tests, local filesystem and `/tmp` probes

---

## File Structure

- Modify: `run-loop`
  - Add repo snapshot helpers, output fingerprinting, iteration classification, cooldown handling, and Claude temp cleanup.
- Modify: `tests/test_run_loop.py`
  - Add deterministic tests for repo progress detection, no-progress classification, switch/sleep policy, and Claude temp cleanup.

## Task 1: Add Repo Progress Snapshot Helpers

**Files:**
- Modify: `tests/test_run_loop.py`
- Modify: `run-loop`

- [ ] **Step 1: Write the failing tests for repo snapshot normalization and ignored paths**

Add these tests to `tests/test_run_loop.py` near the other helper-level tests:

```python
class TestRepoProgress:
    def test_snapshot_counts_tracked_and_untracked_files(self, tmp_path):
        tracked = tmp_path / "tracked.txt"
        tracked.write_text("v1")
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_path, check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)

        tracked.write_text("v2")
        (tmp_path / "new.txt").write_text("new")

        snapshot = _mod.collect_repo_snapshot(tmp_path)

        assert "tracked.txt" in snapshot["tracked_paths"]
        assert "new.txt" in snapshot["untracked_paths"]

    def test_has_useful_repo_progress_ignores_run_loop_state_file(self):
        before = {
            "tracked_paths": (),
            "untracked_paths": (),
        }
        after = {
            "tracked_paths": (".agent/run-loop-state.json",),
            "untracked_paths": (),
        }

        assert _mod.has_useful_repo_progress(before, after) is False

    def test_has_useful_repo_progress_counts_untracked_repo_file(self):
        before = {
            "tracked_paths": (),
            "untracked_paths": (),
        }
        after = {
            "tracked_paths": (),
            "untracked_paths": ("notes.txt",),
        }

        assert _mod.has_useful_repo_progress(before, after) is True
```

- [ ] **Step 2: Run the new snapshot tests to verify RED**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRepoProgress -q
```

Expected:
- FAIL with `AttributeError` for missing `collect_repo_snapshot` / `has_useful_repo_progress`

- [ ] **Step 3: Implement minimal repo snapshot and progress helpers in `run-loop`**

Add imports and helpers in `run-loop`:

```python
import hashlib
```

```python
RUN_LOOP_IGNORED_PROGRESS_PREFIXES = (".agent/complete-",)
RUN_LOOP_IGNORED_PROGRESS_PATHS = {".agent/run-loop-state.json"}


def _filter_progress_paths(paths: tuple[str, ...]) -> tuple[str, ...]:
    filtered = []
    for path in paths:
        if path in RUN_LOOP_IGNORED_PROGRESS_PATHS:
            continue
        if any(path.startswith(prefix) for prefix in RUN_LOOP_IGNORED_PROGRESS_PREFIXES):
            continue
        filtered.append(path)
    return tuple(sorted(filtered))


def collect_repo_snapshot(repo_root: Path) -> dict[str, tuple[str, ...]]:
    tracked = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked_paths: list[str] = []
    untracked_paths: list[str] = []
    for line in tracked.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:]
        if status == "??":
            untracked_paths.append(path)
        else:
            tracked_paths.append(path)
    return {
        "tracked_paths": tuple(sorted(tracked_paths)),
        "untracked_paths": tuple(sorted(untracked_paths)),
    }


def has_useful_repo_progress(
    before: dict[str, tuple[str, ...]], after: dict[str, tuple[str, ...]]
) -> bool:
    before_tracked = _filter_progress_paths(before["tracked_paths"])
    after_tracked = _filter_progress_paths(after["tracked_paths"])
    before_untracked = _filter_progress_paths(before["untracked_paths"])
    after_untracked = _filter_progress_paths(after["untracked_paths"])
    return (before_tracked, before_untracked) != (after_tracked, after_untracked)
```

- [ ] **Step 4: Run the snapshot tests to verify GREEN**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRepoProgress -q
```

Expected:
- PASS

- [ ] **Step 5: Commit the repo snapshot helpers**

Run:

```bash
git add run-loop tests/test_run_loop.py
git commit -m "test: add run-loop repo progress detection"
```

Expected:
- one commit containing the snapshot/progress helper tests and implementation

## Task 2: Add Iteration Classification And Cooldown State

**Files:**
- Modify: `tests/test_run_loop.py`
- Modify: `run-loop`

- [ ] **Step 1: Write the failing classification and cooldown tests**

Add these tests to `tests/test_run_loop.py`:

```python
class TestRunLoopRecovery:
    def test_no_progress_on_first_failure_switches_backend(self, monkeypatch, capsys):
        saved_states = []
        complete_checks = iter([False, True])

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
                "consecutive_recoverable_failures": 0,
                "consecutive_claude_resource_failures": 0,
                "last_failure_kind": None,
                "last_output_fingerprint": None,
            },
        )
        monkeypatch.setattr(_mod, "collect_repo_snapshot", lambda repo: {"tracked_paths": (), "untracked_paths": ()})
        monkeypatch.setattr(_mod, "run_backend", lambda backend, prompt: (0, "read-only analysis"))
        monkeypatch.setattr(_mod, "expand_refs", lambda text, repo: text)
        monkeypatch.setattr(_mod, "save_state", lambda path, state: saved_states.append(state.copy()))

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=[])

        assert excinfo.value.code == 0
        assert saved_states[-1]["last_used"] == "claude"
        assert saved_states[-1]["consecutive_recoverable_failures"] == 1

    def test_second_consecutive_recoverable_failure_sleeps_for_one_hour(self, monkeypatch):
        sleeps = []
        saved_states = []
        complete_checks = iter([False, True])

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
                "last_used": "claude",
                "cooldown_until": 0,
                "consecutive_recoverable_failures": 1,
                "consecutive_claude_resource_failures": 0,
                "last_failure_kind": "no_progress",
                "last_output_fingerprint": "same",
            },
        )
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
        monkeypatch.setattr(_mod, "collect_repo_snapshot", lambda repo: {"tracked_paths": (), "untracked_paths": ()})
        monkeypatch.setattr(_mod, "run_backend", lambda backend, prompt: (0, "same"))
        monkeypatch.setattr(_mod, "expand_refs", lambda text, repo: text)
        monkeypatch.setattr(_mod.time, "sleep", lambda seconds: sleeps.append(seconds))
        monkeypatch.setattr(_mod, "save_state", lambda path, state: saved_states.append(state.copy()))

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=[])

        assert excinfo.value.code == 0
        assert sleeps == [3600]
        assert saved_states[-1]["consecutive_recoverable_failures"] == 2
```

- [ ] **Step 2: Run the recovery tests to verify RED**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRunLoopRecovery -q
```

Expected:
- FAIL because `main()` currently treats zero-exit/no-diff runs as success and never sleeps on the second no-progress failure

- [ ] **Step 3: Implement output fingerprinting, classification, and cooldown helpers in `run-loop`**

Add helpers like:

```python
def fingerprint_output(output: str) -> str:
    return hashlib.sha256(output.strip().encode("utf-8")).hexdigest()


def default_state() -> dict[str, object]:
    return {
        "last_used": "codex",
        "both_limited": False,
        "cooldown_until": 0,
        "consecutive_recoverable_failures": 0,
        "consecutive_claude_resource_failures": 0,
        "last_failure_kind": None,
        "last_output_fingerprint": None,
    }


def normalize_state(state: dict[str, object]) -> dict[str, object]:
    normalized = default_state()
    normalized.update(state)
    return normalized


def classify_iteration(
    *,
    backend: str,
    exit_code: int,
    output: str,
    before_snapshot: dict[str, tuple[str, ...]],
    after_snapshot: dict[str, tuple[str, ...]],
    limit_hit: bool,
    claude_resource_failure: bool,
    prompt_failure: bool = False,
) -> str:
    if has_useful_repo_progress(before_snapshot, after_snapshot):
        return "useful_progress"
    if limit_hit:
        return "recoverable_failure"
    if claude_resource_failure:
        return "recoverable_failure"
    if prompt_failure:
        return "recoverable_failure"
    if exit_code != 0:
        return "recoverable_failure"
    return "recoverable_failure"
```

Update `load_state()` to return `default_state()` on failure, and normalize loaded state.

Update `main()` so it:

```python
state = normalize_state(load_state(STATE_FILE))
if state["cooldown_until"] and time.time() < state["cooldown_until"]:
    time.sleep(int(state["cooldown_until"] - time.time()))

before_snapshot = collect_repo_snapshot(REPO)
...
after_snapshot = collect_repo_snapshot(REPO)
classification = classify_iteration(...)
fingerprint = fingerprint_output(output)
```

Then apply the switch/sleep logic:

```python
if classification == "useful_progress":
    state["last_used"] = backend
    state["consecutive_recoverable_failures"] = 0
    state["last_failure_kind"] = None
else:
    state["consecutive_recoverable_failures"] += 1
    state["last_failure_kind"] = "no_progress" if exit_code == 0 else "backend_failure"
    other = "claude" if backend == "codex" else "codex"
    if state["consecutive_recoverable_failures"] == 1:
        state["last_used"] = other
    else:
        state["last_used"] = other
        state["cooldown_until"] = int(time.time()) + 3600
        save_state(STATE_FILE, state)
        time.sleep(3600)
        sys.exit(0)
state["last_output_fingerprint"] = fingerprint
save_state(STATE_FILE, state)
```

- [ ] **Step 4: Run the recovery tests to verify GREEN**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRunLoopRecovery -q
```

Expected:
- PASS

- [ ] **Step 5: Commit the recovery state machine**

Run:

```bash
git add run-loop tests/test_run_loop.py
git commit -m "fix: harden run-loop recovery state"
```

Expected:
- one commit containing the classification and cooldown behavior

## Task 3: Add Claude Temp Cleanup On Third Consecutive Resource Failure

**Files:**
- Modify: `tests/test_run_loop.py`
- Modify: `run-loop`

- [ ] **Step 1: Write the failing tests for Claude cleanup behavior**

Add these tests to `tests/test_run_loop.py`:

```python
class TestClaudeCleanup:
    def test_cleanup_trigger_deletes_all_claude_tmp_paths_when_threshold_is_crossed(
        self, monkeypatch
    ):
        removed = []

        monkeypatch.setattr(
            _mod,
            "find_claude_tmp_paths_for_cleanup",
            lambda tmp_path, threshold_bytes: ([Path("/tmp/claude-a"), Path("/tmp/claude-b")], True),
        )
        monkeypatch.setattr(_mod.shutil, "rmtree", lambda path, ignore_errors=False: removed.append(path))

        cleaned = _mod.cleanup_claude_tmp_if_needed(
            consecutive_claude_resource_failures=3,
            tmp_path=Path("/tmp"),
        )

        assert cleaned is True
        assert removed == [Path("/tmp/claude-a"), Path("/tmp/claude-b")]

    def test_cleanup_does_not_run_before_third_consecutive_resource_failure(self, monkeypatch):
        monkeypatch.setattr(
            _mod,
            "find_claude_tmp_paths_for_cleanup",
            lambda tmp_path, threshold_bytes: pytest.fail("should not inspect tmp before threshold"),
        )

        cleaned = _mod.cleanup_claude_tmp_if_needed(
            consecutive_claude_resource_failures=2,
            tmp_path=Path("/tmp"),
        )

        assert cleaned is False
```

- [ ] **Step 2: Run the Claude cleanup tests to verify RED**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestClaudeCleanup -q
```

Expected:
- FAIL with missing helper functions

- [ ] **Step 3: Implement Claude cleanup helpers in `run-loop`**

Add:

```python
import shutil
```

```python
CLAUDE_TMP_CLEANUP_THRESHOLD_BYTES = 700 * 1024 * 1024


def find_claude_tmp_paths_for_cleanup(
    tmp_path: Path, threshold_bytes: int
) -> tuple[list[Path], bool]:
    paths = []
    threshold_crossed = False
    for path in sorted(tmp_path.iterdir()):
        if path.name.startswith("claude-") and not path.is_symlink():
            paths.append(path)
            if _sum_file_bytes(path) > threshold_bytes:
                threshold_crossed = True
    return paths, threshold_crossed


def cleanup_claude_tmp_if_needed(
    *, consecutive_claude_resource_failures: int, tmp_path: Path
) -> bool:
    if consecutive_claude_resource_failures < 3:
        return False
    paths, threshold_crossed = find_claude_tmp_paths_for_cleanup(
        tmp_path, CLAUDE_TMP_CLEANUP_THRESHOLD_BYTES
    )
    if not threshold_crossed:
        return False
    for path in paths:
        shutil.rmtree(path, ignore_errors=False)
    return True
```

When Claude preflight or resource failure occurs in `main()`, increment
`consecutive_claude_resource_failures`; on non-resource iterations reset it to `0`.

On the third consecutive resource failure, call:

```python
cleanup_claude_tmp_if_needed(
    consecutive_claude_resource_failures=state["consecutive_claude_resource_failures"],
    tmp_path=Path("/tmp"),
)
```

If cleanup happens, print:

```python
print("run-loop: deleted all /tmp/claude-* after repeated Claude resource failures.", file=sys.stderr)
```

- [ ] **Step 4: Run the Claude cleanup tests to verify GREEN**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestClaudeCleanup -q
```

Expected:
- PASS

- [ ] **Step 5: Commit the Claude cleanup logic**

Run:

```bash
git add run-loop tests/test_run_loop.py
git commit -m "fix: self-heal repeated claude temp pressure"
```

Expected:
- one commit containing the third-failure cleanup behavior

## Task 4: Wire Prompt Errors, Repeated Output, And Full Verification

**Files:**
- Modify: `tests/test_run_loop.py`
- Modify: `run-loop`

- [ ] **Step 1: Write the failing end-to-end tests for prompt failures and repeated identical no-progress output**

Add these tests to `tests/test_run_loop.py`:

```python
class TestRunLoopEdgeHandling:
    def test_missing_prompt_file_becomes_recoverable_failure(self, monkeypatch):
        saved_states = []

        class _Marker:
            def exists(self) -> bool:
                return False

        class _PromptFile:
            def read_text(self) -> str:
                raise FileNotFoundError("missing prompt")

        monkeypatch.setattr(_mod, "COMPLETE_MARKER", _Marker())
        monkeypatch.setattr(_mod, "PROMPT_FILE", _PromptFile())
        monkeypatch.setattr(_mod, "load_state", lambda path: _mod.default_state())
        monkeypatch.setattr(_mod, "save_state", lambda path, state: saved_states.append(state.copy()))

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=[])

        assert excinfo.value.code == 0
        assert saved_states[-1]["consecutive_recoverable_failures"] == 1

    def test_identical_output_and_no_progress_still_count_as_recoverable_failure(
        self, monkeypatch
    ):
        saved_states = []
        complete_checks = iter([False, True])

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
                **_mod.default_state(),
                "last_output_fingerprint": _mod.fingerprint_output("same output"),
            },
        )
        monkeypatch.setattr(_mod, "collect_repo_snapshot", lambda repo: {"tracked_paths": (), "untracked_paths": ()})
        monkeypatch.setattr(_mod, "run_backend", lambda backend, prompt: (0, "same output"))
        monkeypatch.setattr(_mod, "expand_refs", lambda text, repo: text)
        monkeypatch.setattr(_mod, "save_state", lambda path, state: saved_states.append(state.copy()))

        with pytest.raises(SystemExit):
            _mod.main(argv=[])

        assert saved_states[-1]["consecutive_recoverable_failures"] == 1
```

- [ ] **Step 2: Run the edge-handling tests to verify RED**

Run:

```bash
uv run pytest tests/test_run_loop.py::TestRunLoopEdgeHandling -q
```

Expected:
- FAIL because prompt read errors and identical-output/no-progress behavior are not yet handled

- [ ] **Step 3: Implement minimal prompt-failure and repeated-output handling**

In `run-loop`, wrap prompt expansion:

```python
try:
    expanded = expand_refs(prompt_file.read_text(), REPO)
    prompt_failure = False
except OSError as exc:
    print(f"run-loop: prompt read failed: {exc}", file=sys.stderr)
    expanded = ""
    prompt_failure = True
```

Then treat prompt failures as recoverable in `classify_iteration(...)`.

Also add repeated identical-output detection:

```python
fingerprint = fingerprint_output(output)
same_output = fingerprint == state.get("last_output_fingerprint")
if same_output and not has_useful_repo_progress(before_snapshot, after_snapshot):
    classification = "recoverable_failure"
```

- [ ] **Step 4: Run the targeted run-loop test module**

Run:

```bash
uv run pytest tests/test_run_loop.py -q
```

Expected:
- PASS

- [ ] **Step 5: Run the full test suite**

Run:

```bash
uv run pytest -q
```

Expected:
- PASS

- [ ] **Step 6: Commit the final run-loop hardening batch**

Run:

```bash
git add run-loop tests/test_run_loop.py
git commit -m "fix: harden run-loop failure recovery"
```

Expected:
- one commit containing the final prompt/error/output hardening behavior

## Task 5: Final Review And Handoff

**Files:**
- Verify: `run-loop`
- Verify: `tests/test_run_loop.py`

- [ ] **Step 1: Review the final diff**

Run:

```bash
git diff -- run-loop tests/test_run_loop.py
```

Expected:
- changes limited to the run-loop script and its tests

- [ ] **Step 2: Check final repo status**

Run:

```bash
git status --short
```

Expected:
- no unexpected files from `/tmp` cleanup tests or local harness artifacts

- [ ] **Step 3: Prepare the user-facing summary**

Summarize:

- how no-progress detection now works
- how switch-once-then-sleep works
- how Claude resource failures now self-heal
- which paths are ignored for progress detection
- verification evidence from `tests/test_run_loop.py` and the full suite

## Self-Review

Spec coverage:
- repo progress detection is covered in Task 1
- classification and cooldown state are covered in Task 2
- Claude temp cleanup is covered in Task 3
- prompt/read failures and repeated identical output are covered in Task 4
- final verification and handoff are covered in Task 5

Placeholder scan:
- no `TBD`, `TODO`, or deferred implementation placeholders remain

Type and naming consistency:
- helper names are consistent across tasks: `collect_repo_snapshot`, `has_useful_repo_progress`,
  `fingerprint_output`, `classify_iteration`, `find_claude_tmp_paths_for_cleanup`, and
  `cleanup_claude_tmp_if_needed`
