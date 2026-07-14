# Development Efficiency Implementation Plan

> **Historical reconciliation (2026-07-14):** This operator-directed
> infrastructure work landed on `main` outside the roadmap executor.  Its
> cache/interceptor commits are `8f2aab8`, `ef53139`, `6cd7fe5`, `f0dd88e`,
> `48f7fc8`, `55b6a5b`, and `8a4fa1a`; its MCO quota/cooldown commits are
> `74704ad` and `a1891ce`.  The committed focused regression suite is the
> evidence record.  This document is retained as historical implementation
> context and does not create an additional roadmap plan.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement in-process AST caching for `shakespearelang` execution in pytest to achieve a 600x test suite speedup, and optimize the MCO loop configuration to resolve fallback timeouts and cooldown blockages.

**Architecture:** 
1. Create a global [tests/conftest.py](file:///Users/jonathan/shakedown/tests/conftest.py) file that monkeypatches `subprocess.run` during test runs, executing the target play in-process via `shakespearelang.Shakespeare(play_ast)` utilizing a session-cached AST dictionary.
2. If `shakedown-dev` or `shakedown-debug` is invoked, call `assemble(..., parse_check=False)` dynamically in-process before executing the play to prevent stale runs. The cached-AST lookup immediately afterward is the parse gate: a cache miss parses the newly assembled source once, while repeated debug invocations reuse that AST instead of paying the TatSu parse cost during every assembly.
3. Filter the monkeypatch based on caller test file stack (blacklisting `test_wrapper_error_channel.py`, `test_shakedown_run.py`, and `test_empty_input_contract.py`) and customize input/output types (bytes vs text) to preserve full correctness.
4. Add a `--real-wrapper` pytest CLI option to fully disable interception when desired.
5. Split the OpenRouter quota groups in `agent-loop.toml` into unique per-model groups.
6. Modify `agent-loop.toml` and `mco_loop.py` to support shorter, configurable cooldowns for transient errors and rate limits.

**Tech Stack:** Python, pytest, TatSu, shakespearelang, MCO.

---

### Task 1: Add pytest CLI option and conftest skeleton

**Files:**
- Create: [tests/conftest.py](file:///Users/jonathan/shakedown/tests/conftest.py)

- [ ] **Step 1: Write conftest.py with pytest option and dummy interceptor**
  Write the initial conftest structure that defines `--real-wrapper`.
  ```python
  import pytest
  import subprocess
  
  def pytest_addoption(parser):
      parser.addoption(
          "--real-wrapper",
          action="store_true",
          default=False,
          help="Disable in-process AST caching and run real subprocess shakedown wrapper",
      )
  
  @pytest.fixture(autouse=True, scope="session")
  def intercept_subprocess(pytestconfig):
      if pytestconfig.getoption("--real-wrapper"):
          return
          
      original_run = subprocess.run
      
      def mocked_run(args, *p_args, **kwargs):
          # Skeleton check
          return original_run(args, *p_args, **kwargs)
          
      subprocess.run = mocked_run
  ```

- [ ] **Step 2: Run pytest to make sure option works**
  Run: `uv run pytest --real-wrapper -k "test_binary_contract"`
  Expected: PASS

- [ ] **Step 3: Commit**
  ```bash
  git add tests/conftest.py
  git commit -m "test: initialize conftest with real-wrapper option"
  ```

---

### Task 2: Implement AST Caching & In-Process Execution in Interceptor

**Files:**
- Modify: [tests/conftest.py](file:///Users/jonathan/shakedown/tests/conftest.py)
- Create: [tests/test_inprocess_interceptor.py](file:///Users/jonathan/shakedown/tests/test_inprocess_interceptor.py)

- [ ] **Step 1: Write the full monkeypatch interceptor**
  Add the path check, stack blacklist, assembly execution for dev/debug wrappers, AST caching, StringIO/BytesIO redirectors, and exit code emulation:
  ```python
  import pytest
  import subprocess
  import io
  import contextlib
  import sys
  import os
  import hashlib
  from pathlib import Path
  from shakespearelang import Shakespeare
  
  _AST_CACHE = {}
  _WRAPPER_NAMES = {"shakedown", "shakedown-dev", "shakedown-debug"}
  
  def pytest_addoption(parser):
      parser.addoption(
          "--real-wrapper",
          action="store_true",
          default=False,
          help="Disable in-process AST caching and run real subprocess shakedown wrapper",
      )
  
  @pytest.fixture(autouse=True, scope="session")
  def intercept_subprocess(pytestconfig):
      if pytestconfig.getoption("--real-wrapper"):
          return
          
      original_run = subprocess.run
      
      def mocked_run(args, *p_args, **kwargs):
          # Determine command name
          cmd = args[0] if isinstance(args, list | tuple) else args
          if isinstance(cmd, Path):
              cmd = str(cmd)
              
          # Match only the three supported wrapper basenames. Repository paths
          # containing "shakedown" (for example sys.executable in this checkout)
          # must continue through the real subprocess implementation.
          wrapper_name = Path(cmd).name if isinstance(cmd, str) else None
          is_shakedown = wrapper_name in _WRAPPER_NAMES
          
          # Check if caller stack contains blacklisted test files
          import inspect
          stack = inspect.stack()
          blacklist = {
              "test_wrapper_error_channel.py",
              "test_shakedown_run.py",
              "test_empty_input_contract.py",
          }
          is_blacklisted = any(
              any(name in frame.filename for name in blacklist)
              for frame in stack
          )
          
          if is_shakedown and not is_blacklisted:
              # Rebuild dev/debug plays without the assembler's standalone
              # parse check. The hash-keyed cache below parses a changed play
              # once and reuses its AST on subsequent wrapper calls.
              if wrapper_name in {"shakedown-dev", "shakedown-debug"}:
                  from scripts.assemble import assemble

                  root = Path(cmd).resolve().parent
                  debug = wrapper_name == "shakedown-debug"
                  assembled_path = (
                      root / ".cache" / "shakedown-debug.spl"
                      if debug
                      else root / "shakedown.spl"
                  )
                  assembled_path.parent.mkdir(exist_ok=True)
                  assemble(
                      src_dir=root / "src",
                      manifest=root / "src" / "manifest.toml",
                      output=assembled_path,
                      parse_check=False,
                      replace=(
                          {
                              "40-act4-emit.spl": (
                                  root / "debug" / "40-act4-token-dump.spl"
                              )
                          }
                          if debug
                          else None
                      ),
                  )
                      
              # Determine path of the target play file
              env_spl = kwargs.get("env", {}).get("SHAKEDOWN_SPL") or os.environ.get("SHAKEDOWN_SPL")
              if env_spl:
                  spl_path = Path(env_spl)
              elif wrapper_name == "shakedown-debug":
                  spl_path = Path(cmd).parent / ".cache" / "shakedown-debug.spl"
              else:
                  spl_path = Path(cmd).parent / "shakedown.spl"
                  
              if not spl_path.exists():
                  return original_run(args, *p_args, **kwargs)
                  
              # Read and get cached AST
              play_text = spl_path.read_text()
              h = hashlib.sha256(play_text.encode()).hexdigest()
              cache_key = (spl_path, h)
              if cache_key not in _AST_CACHE:
                  temp_interpreter = Shakespeare(play_text)
                  _AST_CACHE[cache_key] = temp_interpreter.parser.parse(play_text, "play")
              play_ast = _AST_CACHE[cache_key]
              
              # Setup input based on types (text vs bytes)
              input_data = kwargs.get("input", "")
              is_bytes = isinstance(input_data, bytes)
              if is_bytes:
                  input_str = input_data.decode("utf-8", errors="replace")
              else:
                  input_str = input_data or ""
                  
              # Redirect I/O
              stdin_buf = io.StringIO(input_str)
              stdout_buf = io.StringIO()
              stderr_buf = io.StringIO()
              
              exit_code = 0
              try:
                  with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                      old_stdin = sys.stdin
                      sys.stdin = stdin_buf
                      try:
                          interpreter = Shakespeare(play_ast)
                          interpreter.run()
                      finally:
                          sys.stdin = old_stdin
              except Exception as e:
                  stderr_buf.write(f"SPL runtime error: {str(e)}\n")
                  exit_code = 1
                  
              stdout_val = stdout_buf.getvalue()
              stderr_val = stderr_buf.getvalue()
              
              # Return correct type (bytes or str) matching caller expectation
              if is_bytes:
                  stdout_res = stdout_val.encode("utf-8")
                  stderr_res = stderr_val.encode("utf-8")
              else:
                  stdout_res = stdout_val
                  stderr_res = stderr_val
                  
              return subprocess.CompletedProcess(
                  args=args,
                  returncode=exit_code,
                  stdout=stdout_res,
                  stderr=stderr_res,
              )
              
          return original_run(args, *p_args, **kwargs)
          
      subprocess.run = mocked_run
  ```

- [ ] **Step 2: Add a regression test for exact wrapper-basename matching**
  Create `tests/test_inprocess_interceptor.py`. Supplying `SHAKEDOWN_SPL` must not turn an unrelated executable whose parent path contains `shakedown` into an intercepted SPL wrapper:
  ```python
  from __future__ import annotations

  import os
  import subprocess
  import sys
  from pathlib import Path


  def test_repository_path_substring_does_not_trigger_interception(
      tmp_path: Path,
  ) -> None:
      fake_play = tmp_path / "override.spl"
      fake_play.write_text("this is not a valid play")
      misleading_dir = tmp_path / "contains-shakedown"
      misleading_dir.mkdir()
      python_link = misleading_dir / "python"
      python_link.symlink_to(sys.executable)

      result = subprocess.run(
          [str(python_link), "-c", "print('python subprocess')"],
          capture_output=True,
          text=True,
          check=False,
          env={**os.environ, "SHAKEDOWN_SPL": str(fake_play)},
      )

      assert result.returncode == 0
      assert result.stdout == "python subprocess\n"
      assert result.stderr == ""
  ```

- [ ] **Step 3: Run test suite to verify fast execution and correctness**
  Run: `uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py`
  Expected: PASS (and run in < 5 seconds instead of 3+ minutes)

- [ ] **Step 4: Run the debug dump suite to verify repeated wrapper calls reuse the cached AST**
  Run: `uv run pytest tests/test_token_dump.py`
  Expected: PASS without performing a TatSu parse during every debug assembly; only the first distinct debug-play content hash is parsed.

- [ ] **Step 5: Run the test suite with `--real-wrapper` option to verify original behavior remains functional**
  Run: `uv run pytest tests/test_architecture_spikes.py tests/test_mdtest.py --real-wrapper`
  Expected: PASS (takes longer, but passes completely)

- [ ] **Step 6: Run the blacklisted empty-input contract and basename regression test**
  Run: `uv run pytest tests/test_empty_input_contract.py tests/test_inprocess_interceptor.py`
  Expected: PASS

- [ ] **Step 7: Commit**
  ```bash
  git add tests/conftest.py tests/test_inprocess_interceptor.py
  git commit -m "test: implement in-process AST caching and subprocess monkeypatching"
  ```

---

### Task 3: Split Quota Groups in agent-loop.toml

**Files:**
- Modify: [agent-loop.toml](file:///Users/jonathan/shakedown/agent-loop.toml)

- [ ] **Step 1: Edit agent-loop.toml to split free-tier models**
  Modify each implementation executor under OpenRouter to have a unique `quota_group` name, and add `rate_limit_cooldown_seconds`:
  ```toml
  # agent-loop.toml
  [loop]
  env_file = ".env"
  state_file = ".agent/mco-loop-state.json"
  artifact_dir = ".agent/mco-artifacts"
  cooldown_seconds = 3600
  rate_limit_cooldown_seconds = 300
  iteration_pause_seconds = 5
  
  [[implementation]]
  name = "nemotron-ultra-implement"
  provider = "pi-nemotron-ultra-stateless"
  display_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
  quota_group = "openrouter-nemotron-ultra"
  coauthor_name = "NVIDIA Nemotron"
  coauthor_email = "noreply@nvidia.com"
  
  [[implementation]]
  name = "gpt-oss-implement"
  provider = "pi-gpt-oss-stateless"
  display_model = "openai/gpt-oss-120b:free"
  quota_group = "openrouter-gpt-oss"
  coauthor_name = "OpenAI gpt-oss"
  coauthor_email = "noreply@openai.com"
  
  [[implementation]]
  name = "nemotron-super-implement"
  provider = "pi-nemotron-super-stateless"
  display_model = "nvidia/nemotron-3-super-120b-a12b:free"
  quota_group = "openrouter-nemotron-super"
  coauthor_name = "NVIDIA Nemotron"
  coauthor_email = "noreply@nvidia.com"
  
  [[implementation]]
  name = "hy3-implement"
  provider = "pi-hy3-stateless"
  display_model = "tencent/hy3:free"
  quota_group = "openrouter-hy3"
  coauthor_name = "Tencent Hy3"
  coauthor_email = "noreply@tencent.com"
  
  [[implementation]]
  name = "laguna-implement"
  provider = "pi-laguna-stateless"
  display_model = "poolside/laguna-m.1:free"
  quota_group = "openrouter-laguna"
  coauthor_name = "Poolside Laguna"
  coauthor_email = "noreply@poolside.ai"
  
  [[implementation]]
  name = "qwen-coder-implement"
  provider = "pi-qwen-coder-stateless"
  display_model = "qwen/qwen3-coder:free"
  quota_group = "openrouter-qwen-coder"
  coauthor_name = "Alibaba Qwen"
  coauthor_email = "noreply@alibabacloud.com"
  ```

- [ ] **Step 2: Commit quota split changes**
  ```bash
  git add agent-loop.toml
  git commit -m "chore: split OpenRouter fallback quota groups"
  ```

---

### Task 4: Implement MCO Loop Cooldown and Timeout logic

**Files:**
- Modify: [scripts/mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py)
- Modify: [tests/test_mco_loop.py](file:///Users/jonathan/shakedown/tests/test_mco_loop.py)

- [ ] **Step 1: Write failing coverage for both availability cooldowns and CLI override preservation**
  Replace `test_rate_limit_cools_quota_group_and_selects_next_executor` with this parametrized test so both classified availability failures assert the new 300-second duration rather than inheriting `cooldown_seconds=600`:
  ```python
  @pytest.mark.parametrize(
      ("result", "expected_outcome"),
      (
          (
              InvocationResult(
                  2, '{"error_kind":"retryable_rate_limit"}', "", False
              ),
              "rate_limit",
          ),
          (
              InvocationResult(
                  2, '{"error_kind":"retryable_transient_network"}', "", False
              ),
              "transient",
          ),
      ),
  )
  def test_availability_failure_uses_short_quota_group_cooldown_and_selects_next(
      tmp_path: Path,
      result: InvocationResult,
      expected_outcome: str,
  ) -> None:
      config = mco_loop.load_config()
      config = mco_loop.LoopConfig(
          env_file=config.env_file,
          state_file=tmp_path / "state.json",
          artifact_dir=tmp_path / "artifacts",
          cooldown_seconds=600,
          iteration_pause_seconds=0,
          planning=config.planning,
          implementation=config.implementation,
          rate_limit_cooldown_seconds=300,
      )
      state: dict[str, object] = {
          "cooldowns": {},
          "failures": {},
          "last_failure": None,
      }
      first = config.implementation[0]
      action = NextAction(ActionKind.IMPLEMENT, "test", None, "step", ())

      failure = mco_loop.apply_result(
          config, state, first, action, result, now=1000
      )
      selected, _ = mco_loop.available_executor(
          config.implementation, state, now=1001
      )

      assert failure == expected_outcome
      assert selected == config.implementation[1]
      saved = json.loads(config.state_file.read_text())
      assert saved["cooldowns"][first.quota_group] == 1300
  ```

  Add a CLI-path regression test proving that the existing `--cooldown-seconds` reconstruction changes only the long cooldown and carries the configured short cooldown through:
  ```python
  def test_cooldown_cli_override_preserves_rate_limit_cooldown(
      tmp_path: Path,
      monkeypatch: pytest.MonkeyPatch,
  ) -> None:
      config = mco_loop.LoopConfig(
          env_file=tmp_path / ".env",
          state_file=tmp_path / "state.json",
          artifact_dir=tmp_path / "artifacts",
          cooldown_seconds=600,
          iteration_pause_seconds=0,
          planning=(),
          implementation=(),
          rate_limit_cooldown_seconds=123,
      )
      roadmap = tmp_path / "roadmap.md"
      roadmap.write_text("ignored")
      captured: dict[str, mco_loop.LoopConfig] = {}

      monkeypatch.setattr(mco_loop, "ROADMAP", roadmap)
      monkeypatch.setattr(mco_loop, "load_config", lambda path: config)
      monkeypatch.setattr(mco_loop.shutil, "which", lambda name: "/bin/mco")
      monkeypatch.setattr(mco_loop, "load_named_secrets", lambda path: {})
      monkeypatch.setattr(mco_loop, "ensure_git_hooks", lambda: None)
      monkeypatch.setattr(mco_loop, "pi_auth_shadow_warning", lambda: None)
      monkeypatch.setattr(mco_loop, "pi_models_config_warning", lambda: None)
      monkeypatch.setattr(
          mco_loop,
          "parse_roadmap",
          lambda text: (_row("4S", "in flight"),),
      )
      monkeypatch.setattr(
          mco_loop,
          "determine_next_action",
          lambda rows, blockers: NextAction(
              ActionKind.IMPLEMENT, "test", None, "step", ()
          ),
      )

      def fake_run_governor(
          actual: mco_loop.LoopConfig,
          action: NextAction,
          environment: dict[str, str],
      ) -> int:
          captured["config"] = actual
          return 0

      monkeypatch.setattr(mco_loop, "run_governor", fake_run_governor)

      assert mco_loop.main(
          ["--govern", "--cooldown-seconds", "10"]
      ) == 0
      assert captured["config"].cooldown_seconds == 10
      assert captured["config"].rate_limit_cooldown_seconds == 123
  ```

- [ ] **Step 2: Run the focused tests to verify the new behavior is absent**
  Run: `uv run pytest tests/test_mco_loop.py -k "availability_failure_uses_short or cooldown_cli_override_preserves"`
  Expected: FAIL because `LoopConfig` does not yet accept `rate_limit_cooldown_seconds`.

- [ ] **Step 3: Update LoopConfig definition with validated default**
  Modify [scripts/mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py#L176-L185) to add `rate_limit_cooldown_seconds` with default value `300`:
  ```python
  # scripts/mco_loop.py
  @dataclass(frozen=True)
  class LoopConfig:
      env_file: Path
      state_file: Path
      artifact_dir: Path
      cooldown_seconds: int
      iteration_pause_seconds: int
      planning: tuple[Executor, ...]
      implementation: tuple[Executor, ...]
      rate_limit_cooldown_seconds: int = 300
      escalation: tuple[Executor, ...] = ()
  ```

- [ ] **Step 4: Update load_config validation**
  Immediately after `load_config` obtains the `loop` mapping, read the optional setting through the existing non-negative-integer validator:
  ```python
  loop = _mapping(table.get("loop"), "loop")
  rate_limit_cooldown_seconds = 300
  if "rate_limit_cooldown_seconds" in loop:
      rate_limit_cooldown_seconds = _integer(loop, "rate_limit_cooldown_seconds")
  ```

  Pass that local into the existing `LoopConfig` constructor between `implementation` and `escalation`:
  ```python
  rate_limit_cooldown_seconds=rate_limit_cooldown_seconds,
  ```

- [ ] **Step 5: Preserve the short cooldown in the CLI reconstruction path**
  Add the new field when `main()` rebuilds `LoopConfig` for `--cooldown-seconds`:
  ```python
  if args.cooldown_seconds is not None:
      config = LoopConfig(
          env_file=config.env_file,
          state_file=config.state_file,
          artifact_dir=config.artifact_dir,
          cooldown_seconds=max(0, args.cooldown_seconds),
          iteration_pause_seconds=config.iteration_pause_seconds,
          planning=config.planning,
          implementation=config.implementation,
          rate_limit_cooldown_seconds=config.rate_limit_cooldown_seconds,
          escalation=config.escalation,
      )
  ```

- [ ] **Step 6: Apply the short cooldown to all availability failures**
  In the failure branch of `apply_result`, replace the existing `cooldowns[cooldown_key] = now + config.cooldown_seconds` assignment with this duration selection, keeping the existing failure-count and state-recording code around it unchanged:
  ```python
  availability_failure = outcome in {"rate_limit", "transient"}
  cooldown_key = (
      executor.quota_group
      if availability_failure
      else f"executor:{executor.name}"
  )
  duration = (
      config.rate_limit_cooldown_seconds
      if availability_failure
      else config.cooldown_seconds
  )
  cooldowns[cooldown_key] = now + duration
  ```

- [ ] **Step 7: Reduce MCO --stall-timeout in mco_loop.py**
  In the `mco_command` command list, replace the current timeout pair with:
  ```python
  "--stall-timeout",
  "300",
  ```

- [ ] **Step 8: Run the focused cooldown tests**
  Run: `uv run pytest tests/test_mco_loop.py -k "availability_failure_uses_short or cooldown_cli_override_preserves"`
  Expected: PASS; both rate-limit and transient outcomes record `1300`, and the CLI override preserves the configured value `123`.

- [ ] **Step 9: Run pytest on all loop infrastructure tests to ensure safety**
  Run: `uv run pytest tests/test_mco_loop.py`
  Expected: PASS

- [ ] **Step 10: Commit**
  ```bash
  git add scripts/mco_loop.py tests/test_mco_loop.py
  git commit -m "chore: implement transient and rate-limit short cooldown and reduce stall timeout"
  ```
