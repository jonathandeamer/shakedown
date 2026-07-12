# Agent Loop Provider Pool Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Pi/OpenRouter fallback executors actually usable: verified model slugs, explicit write-capable stateless shims, correct throttle classification, a credential-shadowing preflight warning, and no dead Grok/xAI configuration.

**Architecture:** All behavior changes live in `scripts/mco_loop.py` (two small, independent deltas: marker tuple, preflight helper) and configuration (`agent-loop.toml`, `.mco/agents.yaml`). This plan builds on the landed result-hardening plan (`2026-07-12-agent-loop-result-hardening.md`) and must not alter its classification order, action keys, or exit codes.

**Tech Stack:** Python 3.12, pytest, TOML, MCO 0.10.8 shim agents, Pi CLI.

## Global Constraints

- **Precondition:** the result-hardening plan is fully landed. Task 1 Step 1 verifies this and halts otherwise.
- Preserve 3M as the sole in-flight roadmap plan; this plan (3N) executes only after 3M ships or the operator triggers it explicitly.
- Do not edit SPL, `src_ir/`, generated fragments, or Markdown behavior.
- Verified OpenRouter slugs, copied verbatim from the spec, in fallback order: `nvidia/nemotron-3-ultra-550b-a55b:free`, `openai/gpt-oss-120b:free`, `nvidia/nemotron-3-super-120b-a12b:free`, `tencent/hy3:free`, `poolside/laguna-m.1:free`, `qwen/qwen3-coder:free`.
- Every Pi shim command contains `--no-session`, `--print`, and `--tools read,bash,edit,write`.
- `nvidia/nemotron-3-super-120b-a12b:free` and `qwen/qwen3-coder:free` require `maxTokens`-capped definitions in the machine-local `~/.pi/agent/models.json`; the supervisor warns when they are missing but never edits that file.
- The preflight warnings never contain key material and never block execution.
- Keep secrets out of tests, diagnostics, and commits.
- Use test-first red/green cycles for every behavior change.

---

### Task 1: OpenRouter Throttle Markers

**Files:**
- Modify: `scripts/mco_loop.py` (the `RATE_LIMIT_MARKERS` tuple near the top of the file)
- Test: `tests/test_mco_loop.py`

**Interfaces:**
- Consumes: `classify_result(result: InvocationResult) -> str` and `InvocationResult(exit_code, stdout, stderr, made_progress, recorded_blocker)` from the landed hardening plan.
- Produces: `RATE_LIMIT_MARKERS` additionally containing `"rate-limited"` and `"429:"`.

- [x] **Step 1: Verify the hardening precondition**

Run:

```bash
grep -q "pi-hy3-stateless" .mco/agents.yaml && grep -q "def classify_result" scripts/mco_loop.py && echo PRECONDITION-OK
```

Expected: `PRECONDITION-OK`. If either grep fails, the result-hardening plan
has not landed: record `- BLOCK: provider pool refresh requires the landed
agent-loop result hardening plan` in `.agent/blockers.md` and stop this plan.

- [x] **Step 2: Write failing marker tests**

Add to `tests/test_mco_loop.py` (match the file's existing import style):

```python
def test_openrouter_upstream_throttle_classifies_as_rate_limit() -> None:
    throttle = (
        '429: {"message":"Provider returned error","code":429,"metadata":'
        '{"raw":"openai/gpt-oss-120b:free is temporarily rate-limited '
        'upstream. Please retry shortly."}}'
    )
    result = mco_loop.InvocationResult(0, throttle, "", False, False)
    assert mco_loop.classify_result(result) == "rate_limit"


def test_progress_still_outranks_throttle_wording() -> None:
    result = mco_loop.InvocationResult(
        0, "documented how rate-limited 429: responses are handled", "", True, False
    )
    assert mco_loop.classify_result(result) == "progress"
```

- [x] **Step 3: Run the marker tests RED**

```bash
uv run pytest tests/test_mco_loop.py -k "throttle" -q
```

Expected: `test_openrouter_upstream_throttle_classifies_as_rate_limit` FAILS
(classified `no_progress`); the progress test may already pass.

- [x] **Step 4: Extend the marker tuple**

In `scripts/mco_loop.py`, extend `RATE_LIMIT_MARKERS` with exactly two new
entries:

```python
RATE_LIMIT_MARKERS = (
    "retryable_rate_limit",
    "rate_limit",
    "rate limit",
    "rate-limited",
    "usage limit",
    "too many requests",
    "http 429",
    "429:",
)
```

- [x] **Step 5: Run all MCO tests GREEN**

```bash
uv run pytest tests/test_mco_loop.py -q
```

Expected: all tests pass.

- [x] **Step 6: Commit**

```bash
git add scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "fix: classify openrouter upstream throttles as rate limits"
```

---

### Task 2: Pi Credential-Shadowing Preflight

**Files:**
- Modify: `scripts/mco_loop.py`
- Test: `tests/test_mco_loop.py`

**Interfaces:**
- Consumes: nothing new; standalone helpers plus calls in `main`.
- Produces: `PI_AUTH_FILE: Path` and `PI_MODELS_FILE: Path` module constants, `PI_MODELS_REQUIRED_IDS: tuple[str, ...]`, `pi_auth_shadow_warning(path: Path = PI_AUTH_FILE) -> str | None`, and `pi_models_config_warning(path: Path = PI_MODELS_FILE) -> str | None`.

- [x] **Step 1: Write failing preflight tests**

```python
def test_pi_auth_shadow_warning_detects_openrouter_entry(tmp_path: Path) -> None:
    auth = tmp_path / "auth.json"
    auth.write_text('{"openrouter": {"type": "api_key", "key": "sk-or-v1-stale"}}')
    warning = mco_loop.pi_auth_shadow_warning(auth)
    assert warning is not None
    assert "auth.json" in warning
    assert "openrouter" in warning.lower()
    assert "sk-or-v1-stale" not in warning


def test_pi_auth_shadow_warning_silent_when_clean(tmp_path: Path) -> None:
    clean = tmp_path / "auth.json"
    clean.write_text('{"anthropic": {"type": "api_key", "key": "sk-ant-x"}}')
    assert mco_loop.pi_auth_shadow_warning(clean) is None
    assert mco_loop.pi_auth_shadow_warning(tmp_path / "missing.json") is None
    malformed = tmp_path / "broken.json"
    malformed.write_text("{not json")
    assert mco_loop.pi_auth_shadow_warning(malformed) is None


def test_pi_models_config_warning_names_missing_capped_models(tmp_path: Path) -> None:
    missing = mco_loop.pi_models_config_warning(tmp_path / "models.json")
    assert missing is not None
    assert "models.json" in missing
    assert "qwen/qwen3-coder:free" in missing
    assert "nvidia/nemotron-3-super-120b-a12b:free" in missing
    partial = tmp_path / "partial.json"
    partial.write_text(
        '{"providers": {"openrouter": {"models": '
        '[{"id": "qwen/qwen3-coder:free", "maxTokens": 32768}]}}}'
    )
    warning = mco_loop.pi_models_config_warning(partial)
    assert warning is not None
    assert "nvidia/nemotron-3-super-120b-a12b:free" in warning
    assert "qwen/qwen3-coder:free" not in warning


def test_pi_models_config_warning_silent_when_complete(tmp_path: Path) -> None:
    complete = tmp_path / "models.json"
    complete.write_text(
        '{"providers": {"openrouter": {"models": ['
        '{"id": "qwen/qwen3-coder:free", "maxTokens": 32768},'
        '{"id": "nvidia/nemotron-3-super-120b-a12b:free", "maxTokens": 32768}'
        "]}}}"
    )
    assert mco_loop.pi_models_config_warning(complete) is None
```

- [x] **Step 2: Run the preflight tests RED**

```bash
uv run pytest tests/test_mco_loop.py -k "pi_auth_shadow or pi_models_config" -q
```

Expected: FAIL with `AttributeError: … has no attribute 'pi_auth_shadow_warning'`
(and the same for `pi_models_config_warning`).

- [x] **Step 3: Implement the helpers**

Add near the other module constants and helpers in `scripts/mco_loop.py`:

```python
PI_AUTH_FILE = Path.home() / ".pi" / "agent" / "auth.json"
PI_MODELS_FILE = Path.home() / ".pi" / "agent" / "models.json"
PI_MODELS_REQUIRED_IDS = (
    "nvidia/nemotron-3-super-120b-a12b:free",
    "qwen/qwen3-coder:free",
)


def pi_auth_shadow_warning(path: Path = PI_AUTH_FILE) -> str | None:
    """Warn when a stored Pi credential would shadow the loop's env key."""
    try:
        stored = json.loads(path.read_text())
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    if not isinstance(stored, dict) or "openrouter" not in stored:
        return None
    return (
        f"agent-loop: {path} contains a stored openrouter credential; "
        "pi prefers it over the loop's OPENROUTER_API_KEY. Remove the "
        "entry if the loop's key should win."
    )


def pi_models_config_warning(path: Path = PI_MODELS_FILE) -> str | None:
    """Warn when machine-local Pi model definitions for capped models are absent."""
    try:
        config_text = path.read_text()
    except (FileNotFoundError, OSError):
        config_text = ""
    try:
        parsed: object = json.loads(config_text) if config_text else {}
    except json.JSONDecodeError:
        parsed = {}
    defined: set[str] = set()
    if isinstance(parsed, dict):
        providers = parsed.get("providers")
        if isinstance(providers, dict):
            for provider in providers.values():
                if not isinstance(provider, dict):
                    continue
                models = provider.get("models")
                if not isinstance(models, list):
                    continue
                for model in models:
                    if isinstance(model, dict) and isinstance(model.get("id"), str):
                        defined.add(model["id"])
    missing = [name for name in PI_MODELS_REQUIRED_IDS if name not in defined]
    if not missing:
        return None
    return (
        f"agent-loop: {path} lacks maxTokens-capped definitions for "
        f"{', '.join(missing)}; those executors will fail with a 400 "
        "output-budget error until the entries are added."
    )
```

- [x] **Step 4: Print the warnings once at startup**

In `main`, immediately after `environment = load_named_secrets(config.env_file)`
(so they fire in every mode, including `--dry-run` and `--status`), add:

```python
    for preflight_warning in (pi_auth_shadow_warning(), pi_models_config_warning()):
        if preflight_warning:
            print(preflight_warning, file=sys.stderr)
```

- [x] **Step 5: Run all MCO tests GREEN**

```bash
uv run pytest tests/test_mco_loop.py -q
```

Expected: all tests pass.

- [x] **Step 6: Commit**

```bash
git add scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "chore: warn when stored pi credentials shadow the loop key"
```

---

### Task 3: Provider Pool Refresh and xAI Removal

**Files:**
- Modify: `agent-loop.toml`
- Modify: `.mco/agents.yaml`
- Modify: `scripts/mco_loop.py` (`ALLOWED_SECRET_NAMES` only)
- Test: `tests/test_mco_loop.py`

**Interfaces:**
- Consumes: the hardening plan's live-config and stateless-command tests (`test_live_config_has_role_scoped_model_order` and the stateless-shim assertions its Task 4 added).
- Produces: implementation providers, in order: `claude-sonnet`, `codex`, `claude-opus`, `codex`, `pi-nemotron-ultra-stateless`, `pi-gpt-oss-stateless`, `pi-nemotron-super-stateless`, `pi-hy3-stateless`, `pi-laguna-stateless`, `pi-qwen-coder-stateless`; `ALLOWED_SECRET_NAMES = ("OPENROUTER_API_KEY",)`.

- [x] **Step 1: Update configuration tests first**

In `test_live_config_has_role_scoped_model_order` (and any stateless-shim
test the hardening plan added), set the expected implementation provider
order to:

```python
[
    "claude-sonnet",
    "codex",
    "claude-opus",
    "codex",
    "pi-nemotron-ultra-stateless",
    "pi-gpt-oss-stateless",
    "pi-nemotron-super-stateless",
    "pi-hy3-stateless",
    "pi-laguna-stateless",
    "pi-qwen-coder-stateless",
]
```

Add a shim-content test:

```python
def test_pi_shims_are_stateless_and_write_capable() -> None:
    text = (REPO / ".mco" / "agents.yaml").read_text()
    for name, slug in (
        ("pi-nemotron-ultra-stateless", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        ("pi-gpt-oss-stateless", "openai/gpt-oss-120b:free"),
        ("pi-nemotron-super-stateless", "nvidia/nemotron-3-super-120b-a12b:free"),
        ("pi-hy3-stateless", "tencent/hy3:free"),
        ("pi-laguna-stateless", "poolside/laguna-m.1:free"),
        ("pi-qwen-coder-stateless", "qwen/qwen3-coder:free"),
    ):
        assert name in text
        assert slug in text
    for line in text.splitlines():
        if "command: 'pi " in line:
            assert "--no-session" in line
            assert "--print" in line
            assert "--tools read,bash,edit,write" in line
    for remnant in ("grok", "xai", "nemotron-4-340b", "agy-"):
        assert remnant not in text.lower()


def test_xai_key_is_no_longer_allowlisted() -> None:
    assert mco_loop.ALLOWED_SECRET_NAMES == ("OPENROUTER_API_KEY",)
```

Also update any existing secrets test that writes or expects `XAI_API_KEY`
(for example `test_load_named_secrets_loads_only_allowlisted_names`) to use
`OPENROUTER_API_KEY` as the allowlisted name and keep a non-allowlisted decoy.

- [x] **Step 2: Run configuration tests RED**

```bash
uv run pytest tests/test_mco_loop.py -k "live_config or stateless or allowlisted or write_capable" -q
```

Expected: failures against the current grok/nemotron-4 configuration.

- [x] **Step 3: Rewrite the Pi shim entries**

In `.mco/agents.yaml`, delete the Grok shim (and any remaining `agy-*`
entries) and define exactly these six Pi shims:

```yaml
  - name: pi-nemotron-ultra-stateless
    transport: shim
    command: 'pi --no-session --print --tools read,bash,edit,write --provider openrouter --model nvidia/nemotron-3-ultra-550b-a55b:free'
  - name: pi-gpt-oss-stateless
    transport: shim
    command: 'pi --no-session --print --tools read,bash,edit,write --provider openrouter --model openai/gpt-oss-120b:free'
  - name: pi-nemotron-super-stateless
    transport: shim
    command: 'pi --no-session --print --tools read,bash,edit,write --provider openrouter --model nvidia/nemotron-3-super-120b-a12b:free'
  - name: pi-hy3-stateless
    transport: shim
    command: 'pi --no-session --print --tools read,bash,edit,write --provider openrouter --model tencent/hy3:free'
  - name: pi-laguna-stateless
    transport: shim
    command: 'pi --no-session --print --tools read,bash,edit,write --provider openrouter --model poolside/laguna-m.1:free'
  - name: pi-qwen-coder-stateless
    transport: shim
    command: 'pi --no-session --print --tools read,bash,edit,write --provider openrouter --model qwen/qwen3-coder:free'
```

- [x] **Step 4: Rewrite the fallback executors**

In `agent-loop.toml`, delete the Grok executor and replace the Pi fallback
block so the implementation list ends with exactly:

```toml
[[implementation]]
name = "nemotron-ultra-implement"
provider = "pi-nemotron-ultra-stateless"
display_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
quota_group = "openrouter"
coauthor_name = "NVIDIA Nemotron"
coauthor_email = "noreply@nvidia.com"

[[implementation]]
name = "gpt-oss-implement"
provider = "pi-gpt-oss-stateless"
display_model = "openai/gpt-oss-120b:free"
quota_group = "openrouter"
coauthor_name = "OpenAI gpt-oss"
coauthor_email = "noreply@openai.com"

[[implementation]]
name = "nemotron-super-implement"
provider = "pi-nemotron-super-stateless"
display_model = "nvidia/nemotron-3-super-120b-a12b:free"
quota_group = "openrouter"
coauthor_name = "NVIDIA Nemotron"
coauthor_email = "noreply@nvidia.com"

[[implementation]]
name = "hy3-implement"
provider = "pi-hy3-stateless"
display_model = "tencent/hy3:free"
quota_group = "openrouter"
coauthor_name = "Tencent Hy3"
coauthor_email = "noreply@tencent.com"

[[implementation]]
name = "laguna-implement"
provider = "pi-laguna-stateless"
display_model = "poolside/laguna-m.1:free"
quota_group = "openrouter"
coauthor_name = "Poolside Laguna"
coauthor_email = "noreply@poolside.ai"

[[implementation]]
name = "qwen-coder-implement"
provider = "pi-qwen-coder-stateless"
display_model = "qwen/qwen3-coder:free"
quota_group = "openrouter"
coauthor_name = "Alibaba Qwen"
coauthor_email = "noreply@alibabacloud.com"
```

No `model` or `model_provider` keys: the shim command owns model selection,
and `--provider-models-json` must not be emitted for these executors.

- [x] **Step 5: Remove the xAI secret allowlisting**

In `scripts/mco_loop.py`:

```python
ALLOWED_SECRET_NAMES = ("OPENROUTER_API_KEY",)
```

- [x] **Step 6: Run all MCO tests GREEN, then dry-run**

```bash
uv run pytest tests/test_mco_loop.py -q
./agent-loop --dry-run
```

Expected: all tests pass; the dry run prints a valid selected executor and
JSON payload with no secret values and no `grok`/`agy` names.

- [x] **Step 7: Reset stale loop state**

```bash
rm -f .agent/mco-loop-state.json
```

The file is git-ignored operator state; it holds cooldowns and failure
counters for executors that no longer exist. `load_state` tolerates the
missing file. Nothing to commit for this step.

- [x] **Step 8: Commit**

```bash
git add agent-loop.toml .mco/agents.yaml scripts/mco_loop.py tests/test_mco_loop.py
git commit -m "chore: refresh agent loop fallback pool and drop xai"
```

---

### Task 4: Operational Documentation and Final Gate

**Files:**
- Modify: `docs/2026-07-12-mco-loop-details.md`
- Test: none (documentation task; final gate covers the repo)

**Interfaces:**
- Consumes: the completed behavior from Tasks 1–3.
- Produces: documented provider pool, credential-precedence gotcha, and free-tier expectations.

- [x] **Step 1: Document the refreshed provider policy**

Add or update sections in `docs/2026-07-12-mco-loop-details.md` covering:

- the six verified OpenRouter fallbacks, their shared `openrouter` quota
  group, and the priority rationale (Nemotron 3 Ultra 550B, gpt-oss-120b,
  Nemotron 3 Super 120B, Hy3, Laguna M.1, Qwen3 Coder last because it is
  chronically throttled upstream);
- the unresponsive-free-model guarantees: throttles are availability
  failures with a group cooldown the loop never waits on, silent empty
  completions are substantive `no_progress` attempts that skip the executor,
  and MCO's 900 s stall timeout bounds true hangs;
- the machine-local `~/.pi/agent/models.json` dependency for the two capped
  models (`nvidia/nemotron-3-super-120b-a12b:free`, `qwen/qwen3-coder:free`),
  the startup warning that guards it, and the exact JSON entries a fresh
  machine needs;
- Grok/xAI removal (no credits; may return only with restored credits plus a
  fresh verification run) and the removal of `XAI_API_KEY` from the secret
  allowlist, with a note that the operator may delete the stale key from the
  git-ignored repo-root `.env` file;
- the `~/.pi/agent/auth.json` precedence gotcha: stored Pi credentials
  silently outrank the loop's `OPENROUTER_API_KEY`, the supervisor now warns
  at startup, and any interactive `pi` login can reintroduce the entry;
- free-tier expectations: shared upstream capacity means intermittent
  `429`/`rate-limited` responses, which classify as availability failures
  (group cooldown, retryable), not substantive attempts;
- the `pi` output-budget bug (unknown model IDs request a 262 000-token
  completion) that the `models.json` entries work around, so a future
  session understands why the definitions exist.

- [x] **Step 2: Run the complete evidence gate**

```bash
uv run pytest tests/test_mco_loop.py
uv run ruff check scripts/mco_loop.py tests/test_mco_loop.py
uv run ruff format --check scripts/mco_loop.py tests/test_mco_loop.py
uv run pyright scripts/mco_loop.py
uv run pytest
./agent-loop --dry-run
git diff --check
```

Expected: every command exits `0`; the default suite retains only documented
skips; the dry run selects a real executor with no secret values in output.

- [x] **Step 3: Mark roadmap row 3N shipped and commit**

Update row 3N's status in `docs/superpowers/plans/plan-roadmap.md` to
`shipped: <date> at commit <short-sha of the Task 3 commit>`.

```bash
git add docs/2026-07-12-mco-loop-details.md docs/superpowers/plans/plan-roadmap.md
git commit -m "docs: document refreshed agent loop provider pool"
git push origin main
```
