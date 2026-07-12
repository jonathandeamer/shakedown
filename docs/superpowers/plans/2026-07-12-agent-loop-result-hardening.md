# Agent Loop Result Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the MCO supervisor accept observable partial progress, retry trusted transient failures, and terminate with a durable diagnostic after substantive executor exhaustion.

**Architecture:** Keep MCO as the only orchestration layer. Separate the canonical roadmap action from its rewritten execution role, persist substantive attempts under a stable action key, and make selection return one of three explicit states: invoke, wait for a trusted cooldown, or exhaust. Provider shims supply stateless Claude/Pi sessions; repository fingerprint and blocker deltas remain the only task-outcome evidence.

**Tech Stack:** Python 3.12, pytest, TOML, MCO 0.10.8 shim agents, Claude Code CLI, Pi CLI.

## Global Constraints

- Preserve 3M as the sole in-flight roadmap plan.
- Do not edit SPL, `src_ir/`, generated fragments, or Markdown behavior.
- Preserve partial working-tree changes as progress; do not require a commit.
- Treat Python supervisor timeout exit `124` as substantive.
- Wait only for trusted Claude/Codex availability cooldowns, never Pi fallback cooldowns.
- Keep secrets and provider prose out of persisted diagnostics.
- Use test-first red/green cycles for every behavior change.

---

### Task 1: Evidence-First Result Classification

**Files:**
- Modify: `scripts/mco_loop.py`
- Test: `tests/test_mco_loop.py`

**Interfaces:**
- Consumes: `InvocationResult(exit_code, stdout, stderr, made_progress, recorded_blocker)`
- Produces: `classify_result(result: InvocationResult) -> str` with `progress`, `blocked`, `supervisor_timeout`, `rate_limit`, `transient`, `backend_failure`, and `no_progress` outcomes.

- [x] **Step 1: Write classification tests that expose marker precedence and timeout behavior**

Add focused tests equivalent to:

```python
def test_progress_outranks_rate_limit_wording() -> None:
    result = InvocationResult(0, "updated rate limit tests", "", True, False)
    assert mco_loop.classify_result(result) == "progress"


def test_supervisor_timeout_is_substantive_before_transient_markers() -> None:
    result = InvocationResult(124, "", "MCO execution timed out", False, False)
    assert mco_loop.classify_result(result) == "supervisor_timeout"


def test_new_blocker_is_not_no_progress() -> None:
    result = InvocationResult(0, "", "", False, True)
    assert mco_loop.classify_result(result) == "blocked"
```

Update existing `InvocationResult` constructions with `recorded_blocker=False`.

- [x] **Step 2: Run the tests and verify RED**

Run:

```bash
uv run pytest tests/test_mco_loop.py -k "progress_outranks or supervisor_timeout_is_substantive or new_blocker" -q
```

Expected: failures because `recorded_blocker` and `classify_result` do not exist.

- [x] **Step 3: Implement the minimal ordered classifier and blocker observation**

Extend the result record and replace `classify_failure` with this ordering:

```python
@dataclass(frozen=True)
class InvocationResult:
    exit_code: int
    stdout: str
    stderr: str
    made_progress: bool
    recorded_blocker: bool = False


def classify_result(result: InvocationResult) -> str:
    if result.made_progress:
        return "progress"
    if result.recorded_blocker:
        return "blocked"
    if result.exit_code == 124:
        return "supervisor_timeout"
    output = result.combined_output.lower()
    if any(marker in output for marker in RATE_LIMIT_MARKERS):
        return "rate_limit"
    if any(marker in output for marker in TRANSIENT_MARKERS):
        return "transient"
    if result.exit_code != 0:
        return "backend_failure"
    return "no_progress"
```

In `invoke_mco`, capture `read_blockers()` before spawning and after artifact redaction. Set `recorded_blocker` only when the post-run set contains a new blocker line. Apply the same comparison on timeout returns.

- [x] **Step 4: Run the focused and existing MCO tests GREEN**

```bash
uv run pytest tests/test_mco_loop.py -q
```

Expected: all tests pass.

- [x] **Step 5: Commit the classification checkpoint**

```bash
git add scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "fix: classify agent loop results from evidence"
```

---

### Task 2: Canonical Action Attempts and Exhaustion Selection

**Files:**
- Modify: `scripts/mco_loop.py`
- Test: `tests/test_mco_loop.py`

**Interfaces:**
- Consumes: the pre-rewrite `NextAction`, executor pool, persisted cooldowns, and current time.
- Produces: `action_key(action: NextAction) -> str`, persisted `action_attempt`, and `ExecutorSelection(executor, next_ready, exhausted)`.

- [x] **Step 1: Write failing tests for stable identity and compatible state loading**

Cover these exact properties:

```python
def test_recovery_rewrite_would_change_key_if_misused() -> None:
    canonical = NextAction(ActionKind.IMPLEMENT, "execute", Path("plan.md"), "step", ())
    rewritten = mco_loop.apply_failure_action(
        canonical, {"last_failure": {"kind": "no_progress", "executor": "claude"}}
    )
    assert rewritten != canonical
    assert mco_loop.action_key(rewritten) != mco_loop.action_key(canonical)


def test_load_state_preserves_optional_action_attempt(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text('{"action_attempt":{"key":"abc","attempts":{"claude":"no_progress"}}}')
    assert mco_loop.load_state(path)["action_attempt"] == {
        "key": "abc",
        "attempts": {"claude": "no_progress"},
    }
```

Also parameterize action-key tests so kind, summary, plan, step, and blockers each alter the key on the canonical action.

- [x] **Step 2: Run identity/state tests RED**

```bash
uv run pytest tests/test_mco_loop.py -k "action_key or action_attempt" -q
```

Expected: failures because the key and state field do not exist.

- [x] **Step 3: Add typed selection and canonical action helpers**

Implement deterministic JSON hashing and a selection record:

```python
@dataclass(frozen=True)
class ExecutorSelection:
    executor: Executor | None
    next_ready: int | None
    exhausted: bool


def action_key(action: NextAction) -> str:
    payload = {
        "kind": action.kind.value,
        "summary": action.summary,
        "active_plan": str(action.active_plan.relative_to(REPO))
        if action.active_plan and action.active_plan.is_relative_to(REPO)
        else str(action.active_plan) if action.active_plan else None,
        "step": action.step,
        "blockers": list(action.blockers),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()
```

Teach `load_state` to retain valid dictionary-shaped `action_attempt` and
`exhaustion` records, defaulting each to `None` otherwise. Retaining
`exhaustion` ensures the final diagnostic survives a later status read and
subsequent state save after the operator restarts the loop.

- [x] **Step 4: Write failing executor-selection tests**

Add tests proving:

- a substantive attempt skips that executor for the unchanged key;
- an unattempted available fallback is selected;
- a rate-limited trusted executor yields `exhausted=False` plus its expiry after other fallbacks are substantively attempted;
- a rate-limited untrusted Pi executor yields `exhausted=True` after trusted executors are substantively attempted;
- changing the canonical key ignores stale attempts;
- quota/transient failures never enter the substantive-attempt map.

- [x] **Step 5: Run selection tests RED**

```bash
uv run pytest tests/test_mco_loop.py -k "selection or substantive_attempt or trusted_retry" -q
```

Expected: failures because selection still considers cooldowns only.

- [x] **Step 6: Implement action-aware selection**

Replace the cooldown-only return tuple with `select_executor`. For the matching action key, skip names in `attempts`; select the first unattempted executor whose group and executor cooldowns have expired. If none is available, compute `next_ready` only from unattempted executors in `TRUSTED_RETRY_GROUPS = {"claude", "codex"}`. Return wait state when such an expiry exists; otherwise return exhaustion.

Preserve this invariant in a code comment: an unattempted executor can only be
cooling through an availability/quota-group cooldown, because every
substantive failure records the executor in `attempts` at the same time it adds
an executor-level cooldown. This is why trusted unattempted cooldowns are safe
to expose as retryable.

- [x] **Step 7: Update result application with attempt lifecycle**

Change `apply_result` to accept the canonical action and use `classify_result`:

- `progress` and `blocked`: clear `action_attempt`, clear `last_failure`, and add no cooldown;
- `rate_limit` and `transient`: retain the action record without adding an attempt, cool the quota group;
- `supervisor_timeout`, `backend_failure`, and `no_progress`: create/refresh the matching action record, add `executor.name: outcome`, and cool only that executor.

Keep historical failure counters for status visibility. Ensure a changed action key starts with an empty attempt map.

- [x] **Step 8: Run all MCO tests GREEN**

```bash
uv run pytest tests/test_mco_loop.py -q
```

Expected: all tests pass.

- [x] **Step 9: Commit attempt tracking and selection**

```bash
git add scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "fix: stop exhausted agent executor chains"
```

---

### Task 3: Main-Loop Exit Semantics and Diagnostics

**Files:**
- Modify: `scripts/mco_loop.py`
- Test: `tests/test_mco_loop.py`

**Interfaces:**
- Consumes: canonical action, rewritten execution action, and `ExecutorSelection`.
- Produces: secret-free `exhaustion_payload(...) -> dict[str, object]`, exit `3` for trusted wait in `--once`, and exit `5` for exhaustion.

- [x] **Step 1: Write failing main-loop tests**

Mock roadmap/config/time and assert:

- canonical action is captured before `apply_failure_action` and passed to selection/result handling;
- continuous mode sleeps only for `ExecutorSelection(None, expiry, False)`;
- `--once` returns `3` for that trusted wait state;
- both modes return `5` for `ExecutorSelection(None, None, True)`;
- exhaustion prints `agent-loop: exhausted` to stderr and persists a diagnostic without output/prompt/secrets;
- loading and re-saving state after exhaustion retains the diagnostic;
- `--status` and `--dry-run` expose action attempts and selection state without mutation.

- [x] **Step 2: Run main-loop tests RED**

```bash
uv run pytest tests/test_mco_loop.py -k "exhausted or exit_three or canonical_action" -q
```

Expected: failures because current no-executor handling always waits or returns `3`.

- [x] **Step 3: Implement the three-state main-loop branch**

In `main`, assign `canonical_action` immediately after roadmap/completion classification. Derive the execution action from it only afterward. Select and apply results using the canonical action. For selection:

```python
if selection.exhausted:
    payload = exhaustion_payload(canonical_action, pool, state, now)
    state["exhaustion"] = payload
    save_state(config.state_file, state)
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("agent-loop: exhausted", file=sys.stderr, flush=True)
    return 5
if selection.executor is None:
    if args.once:
        print(json.dumps(status_payload, indent=2, sort_keys=True))
        return 3
    time.sleep(max(1, cast(int, selection.next_ready) - now))
    continue
```

Print `agent-loop: supervisor outcome: <outcome>` after every invocation so MCO transport `PASS` is never presented as the task authority.

- [x] **Step 4: Run all MCO tests GREEN**

```bash
uv run pytest tests/test_mco_loop.py -q
```

Expected: all tests pass without real provider calls.

- [x] **Step 5: Commit supervisor diagnostics**

```bash
git add scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "fix: report terminal agent loop exhaustion"
```

---

### Task 4: Stateless Provider Configuration

**Files:**
- Modify: `.mco/agents.yaml`
- Modify: `agent-loop.toml`
- Test: `tests/test_mco_loop.py`

**Interfaces:**
- Consumes: MCO shim commands receiving the prompt from MCO.
- Produces: non-persistent Claude shims and `pi-grok-stateless`, `pi-hy3-stateless`, and `pi-nemotron-stateless` implementation executors.

- [x] **Step 1: Update configuration tests first**

Change the expected implementation order to:

```python
[
    "claude-sonnet",
    "codex",
    "claude-opus",
    "codex",
    "pi-grok-stateless",
    "pi-hy3-stateless",
    "pi-nemotron-stateless",
]
```

Add assertions that `.mco/agents.yaml` gives Claude `--no-session-persistence`, every Pi shim `--no-session`, and no implementation executor uses `agy-flash`, `agy-pro`, or built-in `pi`.

- [x] **Step 2: Run configuration tests RED**

```bash
uv run pytest tests/test_mco_loop.py -k "live_config or stateless" -q
```

Expected: failures against the current Agy/built-in-Pi configuration.

- [x] **Step 3: Update shim and executor configuration**

Add `--no-session-persistence` to all three Claude shim commands: Fable
governor, Opus, and Sonnet. Remove Agy executors from `agent-loop.toml`. Define
Pi shim commands using:

```yaml
- name: pi-grok-stateless
  transport: shim
  command: 'pi --no-session --print --provider xai --model grok-build-0.1'
- name: pi-hy3-stateless
  transport: shim
  command: 'pi --no-session --print --provider openrouter --model tencent/hy3:free'
- name: pi-nemotron-stateless
  transport: shim
  command: 'pi --no-session --print --provider openrouter --model nvidia/nemotron-4-340b-instruct:free'
```

Point the three configured fallback executors at those names and remove their
`model_provider`/`model` overrides because the shim command owns model
selection. Add explicit `display_model` values `grok-build-0.1`,
`tencent/hy3:free`, and `nvidia/nemotron-4-340b-instruct:free`; retain their
existing quota groups so operator logs remain readable and cooldown grouping
does not change.

- [x] **Step 4: Verify MCO resolves every configured command without invoking providers**

```bash
uv run pytest tests/test_mco_loop.py -k "live_config or stateless or mco_argv" -q
./agent-loop --dry-run
```

Expected: tests pass; dry run prints a valid selected executor and no secret values.

- [x] **Step 5: Commit provider isolation**

```bash
git add .mco/agents.yaml agent-loop.toml tests/test_mco_loop.py
git commit -m "fix: isolate automatic agent sessions"
```

---

### Task 5: Prompt Boundary and Operational Documentation

**Files:**
- Modify: `scripts/mco_loop.py`
- Modify: `tests/test_mco_loop.py`
- Modify: `docs/2026-07-12-mco-loop-details.md`
- Modify: `docs/superpowers/plans/2026-07-11-completion-safety-rails.md`

**Interfaces:**
- Consumes: per-invocation `task_id` and the completed behavior from Tasks 1-4.
- Produces: invocation-ID prompt boundary, documented exit table, and completed Task 6A evidence.

- [x] **Step 1: Write a failing prompt-boundary test**

Update `build_prompt` to accept `invocation_id: str` and assert the rendered prompt begins with the identifier plus an instruction to treat the file as a complete new-session task. Assert it contains no prior provider prose.

- [x] **Step 2: Run the prompt test RED**

```bash
uv run pytest tests/test_mco_loop.py -k "prompt_contains_invocation_boundary" -q
```

Expected: failure because `build_prompt` has no invocation identifier.

- [x] **Step 3: Move task-ID creation before prompt rendering and pass it through**

Create `task_id` before writing `.agent/mco-current-prompt.md`. Add this header before the existing objective:

```text
Invocation: <task_id>
Treat this file as the complete task for a fresh, isolated session. Do not
resume, answer, or rely on any earlier conversation.
```

- [x] **Step 4: Run the prompt test GREEN and commit the behavior change**

```bash
uv run pytest tests/test_mco_loop.py -k "prompt_contains_invocation_boundary" -q
git add scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "fix: add invocation boundary to agent prompts"
```

Expected: the focused test passes before the `fix:` commit is created.

- [x] **Step 5: Document cooldown, exhaustion, and exit behavior**

Update `docs/2026-07-12-mco-loop-details.md` with:

- progress-first result classification;
- canonical per-action substantive attempts;
- trusted-only cooldown waiting and intentional non-wait for Pi cooldowns;
- the `0/1/2/3/4/5/124/130` exit table from the design;
- the durable exhaustion diagnostic and final stderr line;
- stateless automatic provider policy.

- [x] **Step 6: Run the complete evidence gate**

```bash
uv run pytest tests/test_mco_loop.py
uv run ruff check scripts/mco_loop.py tests/test_mco_loop.py
uv run ruff format --check scripts/mco_loop.py tests/test_mco_loop.py
uv run pyright scripts/mco_loop.py
uv run pytest
git diff --check
```

Expected: every command exits `0`; the default suite retains only documented skips.

- [x] **Step 7: Record evidence and close Task 6A**

Add the exact test counts and command outcomes under Task 6A in the active 3M plan, then check its single checkbox. Do not advance Task 7.

- [x] **Step 8: Commit and push the completed hardening documentation**

```bash
git add docs/2026-07-12-mco-loop-details.md docs/superpowers/plans/2026-07-11-completion-safety-rails.md
git commit -m "docs: record agent loop hardening evidence"
git push origin main
```
