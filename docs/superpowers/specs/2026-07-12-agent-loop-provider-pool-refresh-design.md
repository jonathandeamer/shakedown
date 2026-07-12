# Agent Loop Provider Pool Refresh Design

**Date:** 2026-07-12
**Status:** Accepted for implementation
**Scope:** Follow-up to `2026-07-12-agent-loop-result-hardening-design.md`; runs
only after that plan's five tasks have landed.

## Problem

Live diagnosis on 2026-07-12 (artifacts under `.agent/mco-artifacts/`, plus
direct `pi` invocations) established four facts the in-flight hardening plan
does not address:

1. **A stored Pi credential shadows the loop's key.** `~/.pi/agent/auth.json`
   held a revoked OpenRouter key that silently took precedence over the
   `OPENROUTER_API_KEY` environment variable the supervisor exports. Every
   OpenRouter run failed `401: User not found` even though the env-file key
   was valid the whole time. The stale entry has been removed manually, but
   nothing prevents recurrence: any interactive `pi` login rewrites that file.
2. **One configured model no longer exists.** `nvidia/nemotron-4-340b-instruct:free`
   is absent from OpenRouter's live model list. The hardening plan's Task 4
   carries the dead slug forward into the new Pi shim commands.
3. **The xAI account has no credits.** Grok returns
   `403 … used all available credits or reached its monthly spending limit`.
   The operator has confirmed no more credits will be purchased; the Grok
   executor is dead weight and its quota group can never recover.
4. **OpenRouter's free-tier 429 wording evades the rate-limit markers.**
   A live upstream throttle returned
   `429: {"message":"Provider returned error","code":429,…"temporarily
   rate-limited upstream"…}`. None of `RATE_LIMIT_MARKERS` matches
   (`rate limit` with a space, `too many requests`, `http 429`), so a
   throttled free-tier run classifies as a substantive failure instead of an
   availability failure, permanently burning the executor's attempt for the
   current action under the hardened exhaustion rules.

Separately, live capability testing through `pi` (a real tool-call task per
model) found five additional free OpenRouter models that work end-to-end and
are strong enough for fallback implementation work. Two of them
(`qwen/qwen3-coder:free`, `nvidia/nemotron-3-super-120b-a12b:free`) fail with
a `pi` output-budget bug when `pi` does not recognize the model ID (400:
requested 262 000 output tokens) and work only when the machine-local
`~/.pi/agent/models.json` defines them with an explicit `maxTokens` cap. That
file now exists on this machine and both models passed the tool-call test
through it (2026-07-12); `qwen/qwen3-coder:free` is chronically throttled
upstream (429 with `retry_after` longer than `pi`'s internal retry budget),
so it ranks last.

## Goals

- Warn loudly at supervisor startup when `~/.pi/agent/auth.json` contains an
  `openrouter` entry that would shadow the loop's environment key.
- Classify OpenRouter free-tier upstream throttles (`rate-limited`, `429:`)
  as `rate_limit` availability failures.
- Remove Grok and all xAI configuration (executor, shim, quota group,
  `XAI_API_KEY` allowlisting) from the loop.
- Replace the dead Nemotron slug with the verified
  `nvidia/nemotron-3-ultra-550b-a55b:free`.
- Add verified working fallbacks `openai/gpt-oss-120b:free`,
  `nvidia/nemotron-3-super-120b-a12b:free`, `poolside/laguna-m.1:free`, and
  `qwen/qwen3-coder:free`.
- Warn at startup when `~/.pi/agent/models.json` is missing the definitions
  the capped models depend on, so a fresh machine fails loudly instead of
  silently regressing to the 400 output-budget error.
- Give every Pi shim an explicit write-capable tool set
  (`--tools read,bash,edit,write`) so tool capability is deliberate, not an
  accident of `pi` defaults.

## Non-Goals

- Changing the hardening plan's classification order, action keys, exhaustion
  rules, or exit codes.
- Editing or refreshing `~/.pi/agent/auth.json` or `~/.pi/agent/models.json`
  automatically. The supervisor only observes and warns; both files remain
  operator-owned.
- Reordering the trusted Claude/Codex executors.

## Provider Policy

All six Pi fallbacks share the `openrouter` quota group because they share
one API key and one free-tier daily request cap; a group cooldown is the
correct blast radius for a throttle. Fallback priority is by observed
capability class and availability: Nemotron 3 Ultra (550B flagship),
gpt-oss-120b, Nemotron 3 Super (120B), Hy3, Laguna M.1, and Qwen3 Coder last
(strongest coder of the set, but chronically throttled upstream).

Two of the six (`nvidia/nemotron-3-super-120b-a12b:free`,
`qwen/qwen3-coder:free`) depend on machine-local definitions in
`~/.pi/agent/models.json` capping `maxTokens` at 32 768; without them, `pi`
requests a 262 000-token output budget and the endpoint rejects the call
with a 400. The supervisor warns at startup when either definition is
missing but does not edit the file.

Every Pi shim command must contain, verbatim: `--no-session` (stateless
boundary, per the hardening design), `--print` (non-interactive),
`--tools read,bash,edit,write` (explicit write capability), and a
`--provider openrouter --model <verified slug>` pair. Verified slugs
(checked against the live OpenRouter model list and exercised through `pi`
with a real tool call on 2026-07-12):

- `nvidia/nemotron-3-ultra-550b-a55b:free`
- `openai/gpt-oss-120b:free`
- `nvidia/nemotron-3-super-120b-a12b:free` (requires the `models.json` entry)
- `tencent/hy3:free`
- `poolside/laguna-m.1:free`
- `qwen/qwen3-coder:free` (requires the `models.json` entry)

Grok, the `xai` quota group, and `XAI_API_KEY` are removed everywhere:
`agent-loop.toml`, `.mco/agents.yaml`, `ALLOWED_SECRET_NAMES`, and tests.
Grok may return only with restored xAI credits and a fresh verification run.

## Startup Preflight

Two pure helpers inspect the machine-local Pi configuration:

```
pi_auth_shadow_warning(path: Path = PI_AUTH_FILE) -> str | None
pi_models_config_warning(path: Path = PI_MODELS_FILE) -> str | None
```

`pi_auth_shadow_warning` returns a warning string when the credential file
exists, parses as JSON, and contains an `openrouter` key; `None` for a
missing, malformed, or openrouter-free file. The warning names the file and
the shadowing risk but must never include key material.

`pi_models_config_warning` returns a warning when
`~/.pi/agent/models.json` is missing, malformed, or lacks either of the two
capped-model IDs (`nvidia/nemotron-3-super-120b-a12b:free`,
`qwen/qwen3-coder:free`); `None` when both are defined. The warning names
the missing IDs and the 400 consequence.

`main` prints each warning to stderr once at startup (all modes, including
`--dry-run` and `--status`); neither blocks execution, because the stored
key might be intentional and the capped models merely degrade to a
classified failure.

## Result Classification Delta

`RATE_LIMIT_MARKERS` gains two members: `"rate-limited"` (hyphenated form
used by OpenRouter's upstream-throttle message) and `"429:"` (the `pi`
error-line prefix observed live). Everything else about classification is
owned by the hardening plan and is unchanged. Because progress is checked
before markers, prose mentions of these strings in successful runs cannot
cause misclassification.

## State Hygiene

`.agent/mco-loop-state.json` accumulated cooldowns and failure counters for
executors that no longer exist (`grok-implement`, the Agy executors, the
pre-refresh Pi names). The state file is ignored, non-authoritative operator
state; the plan deletes it once at rollout so stale keys do not linger. No
code change is needed — the loader already tolerates a missing file.

## Verification

Unit tests with no live provider calls cover:

- hyphenated and `429:`-prefixed throttle text classifying as `rate_limit`;
- successful progress containing the same wording still classifying as
  progress;
- the auth-shadow warning for present, absent, malformed, and
  openrouter-free credential files, with no key material in the message;
- the models-config warning for missing, malformed, complete, and
  partially complete `models.json` files;
- the implementation pool naming exactly the six `openrouter`-group Pi
  shims after the trusted executors, with no `xai`/`grok`/`agy` remnants;
- every Pi shim command containing the required flags and a verified slug;
- `ALLOWED_SECRET_NAMES` containing only `OPENROUTER_API_KEY`.

The evidence gate is:

```bash
uv run pytest tests/test_mco_loop.py
uv run ruff check scripts/mco_loop.py tests/test_mco_loop.py
uv run pyright scripts/mco_loop.py
uv run pytest
./agent-loop --dry-run
```

No SPL source, generated fragment, or Markdown behavior changes as part of
this work.
