# Design Spec: Development Efficiency Improvements

* **Date:** 2026-07-14
* **Status:** Historical operator-directed infrastructure context; changes landed on 2026-07-14 outside the roadmap executor.
* **Topic:** AST caching for test speedup & MCO loop fallback optimization

---

## 1. Testing Speedup: In-Process AST Caching & Subprocess Interception

### 1.1 Context & Problem
Running `./shakedown` or `shakedown-debug` as a subprocess inside `pytest` (e.g. in [test_architecture_spikes.py](file:///Users/jonathan/shakedown/tests/test_architecture_spikes.py) and [test_mdtest.py](file:///Users/jonathan/shakedown/tests/test_mdtest.py)) triggers a full parse of `shakedown.spl` using `tatsu` inside `shakespearelang`.
* Spawning a subprocess and parsing takes **~15 seconds** per test.
* Running in-process from a pre-parsed TatSu AST takes only **~26 milliseconds** (a **600x speedup**).

### 1.2 Proposed Design
We will implement transparent monkeypatching in a global [tests/conftest.py](file:///Users/jonathan/shakedown/tests/conftest.py) to intercept `subprocess.run` and `subprocess.Popen` calls:

1. **Monkeypatch Interceptor:**
   During pytest setup, we wrap `subprocess.run` and `subprocess.Popen`.
   ```python
   import subprocess
   
   original_run = subprocess.run
   
   def mocked_run(args, *p_args, **kwargs):
       if should_intercept(args, kwargs):
           return run_in_process(args, kwargs)
       return original_run(args, *p_args, **kwargs)
   
   subprocess.run = mocked_run
   ```

2. **Interception Conditions (`should_intercept`):**
   We intercept calls if:
   * The basename of the first argument of `args` exactly matches `"shakedown"`, `"shakedown-dev"`, or `"shakedown-debug"`. A repository path that merely contains the word `shakedown` is not a match.
   * The caller stack does *not* contain blacklisted test files: `test_wrapper_error_channel.py` and `test_shakedown_run.py`.
   * The binary path exists.

3. **AST Cache Map:**
   To handle multiple `.spl` targets (like `shakedown.spl` and `shakedown-debug.spl`) and update automatically if plays are recompiled mid-session, we cache ASTs by mapping `(play_file_path, sha256_content_hash) -> tatsu.ast.AST`.
   ```python
   _AST_CACHE = {}
   ```

4. **In-Process Run Simulation (`run_in_process`):**
   * For `shakedown-dev` and `shakedown-debug`, rebuild the target with `assemble(..., parse_check=False)`. The subsequent content-hash cache lookup is the parse gate: a changed play is parsed once on a cache miss, while repeated debug calls reuse the cached AST rather than reparsing during every assembly.
   * Feed inputs: Mock `sys.stdin` using `io.StringIO` to supply the test's `input` payload.
   * Capture outputs: Redirect `sys.stdout` and `sys.stderr` using `contextlib.redirect_stdout` and `contextlib.redirect_stderr`.
   * Run: Initialize `shakespearelang.Shakespeare(cached_ast)` and call `.run()`.
   * Error Handling: If execution raises a `ShakespeareRuntimeError` or other exception, capture it, write it to the mock stderr, and return `returncode=1`.
   * Result: Return a `subprocess.CompletedProcess` matching the signature of `original_run`.

---

## 2. MCO Loop & Quota Group Optimization

### 2.1 Quota Group Split
We split the generic `openrouter` quota group in [agent-loop.toml](file:///Users/jonathan/shakedown/agent-loop.toml) into per-model groups:
```toml
# agent-loop.toml
[[implementation]]
name = "nemotron-ultra-implement"
quota_group = "openrouter-nemotron-ultra"

[[implementation]]
name = "gpt-oss-implement"
quota_group = "openrouter-gpt-oss"

# ... and so on for all openrouter fallback models
```
This isolates failures: a cooldown on `nemotron-ultra` will only cool down its specific group, allowing the fallback chain to immediately try `gpt-oss-implement` at the next iteration.

### 2.2 Short Cooldown for Rate-Limits and Transients
We introduce `rate_limit_cooldown_seconds` under the `[loop]` section of `agent-loop.toml`:
```toml
[loop]
rate_limit_cooldown_seconds = 300  # 5 minutes
```
We update [mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py) to check for this key:
* If the classified outcome is `rate_limit` or `transient` (availability failure), we apply `rate_limit_cooldown_seconds` (defaulting to 300s) to the quota group.
* Other backend or implementation failures will continue to cool down the individual executor for the global `cooldown_seconds` (1 hour).
* When the existing `--cooldown-seconds` CLI option rebuilds `LoopConfig`, it preserves the independently configured `rate_limit_cooldown_seconds` value. Tests cover the exact durations for both `rate_limit` and `transient` outcomes and this CLI reconstruction path.

### 2.3 Shorter Stall Timeout
We update the `--stall-timeout` value passed to `mco` in [mco_loop.py](file:///Users/jonathan/shakedown/scripts/mco_loop.py#L886) from `900` to `300` seconds. If an executor stalls for 5 minutes without making progress, it fails fast.
