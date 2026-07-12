# Completion Safety Rails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. If that
> skill is unavailable, follow the checkboxes sequentially and stop at every
> stated evidence gate.

**Goal:** Commit the verification and feedback infrastructure required before
Spike B: a fast IR interpreter, executable stack/stream contracts, structural
token validation, all-fixture differential smoke reporting, measured
feedback-loop acceleration decisions, and the MCO-only roadmap executor.

**Architecture:** Implements stage 1 of
`docs/superpowers/specs/2026-07-11-completability-hardening-design.md`.
Everything in this plan is verification or developer tooling. Production
Markdown behavior, token baselines, generated fragments, `shakedown.spl`, and
literary surfaces must remain byte-identical.

**Tech stack:** Python 3.12+, frozen IR dataclasses, pytest, subprocess,
`shakespearelang`, local `~/markdown/Markdown.pl`.

## Global constraints

- Read `docs/superpowers/notes/spl-literary-protocol.md`,
  `docs/spl/literary-spec.md`, `docs/spl/style-lexicon.md`,
  `docs/spl/codegen-style-guide.md`, and `src/literary.toml` before editing
  splc code.
- This plan changes compiler/test infrastructure but must not change rendered
  SPL. Therefore it requires **no new controlled prose, scene titles, Recall
  lines, value atoms, or spare title pool**. Any generated-fragment diff is a
  plan defect: stop rather than author a surface.
- Never hand-edit `shakedown.spl` or generated fragments.
- Preserve the real `./shakedown` subprocess as the binary-contract authority.
  The IR interpreter and any in-process runner are test-only.
- No future fixture becomes a parity gate in this plan. Differential smoke is
  observational unless `--require` names an already shipped fixture.
- Type hints on every function; no bare `Any`; no `print()` outside CLI code.
- Create small conventional commits after logical evidence gates and push the
  current branch so autonomous progress is visible on GitHub. Never force-push,
  tag, or change versions; record a failed required push as a blocker.
- Operator priority amendment (2026-07-12): implement and prove Task 6 before
  Task 1. Once Task 6's evidence gate passes, the executor resumes the first
  unchecked Task 1 item; this does not waive or reorder the completion gates.

## Required regression commands

Run after every task that changes Python behavior:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest tests/test_splc_ir.py tests/test_splc_validate.py -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
uv run pytest tests/test_architecture_spikes.py tests/test_token_dump.py -q
uv run python -m scripts.splc
uv run python scripts/assemble.py
git diff --exit-code -- src debug shakedown.spl
```

## Task 1 — Commit the instruction-level IR interpreter

- [x] Add `scripts/splc/interpret.py` implementing expressions, conditions,
      values, per-character stacks, input/output, branches/gotos, act halt,
      and a configurable step limit for the existing closed IR instruction
      set.
- [x] Define typed result and failure records; underflow errors must name the
      act, scene, character, and step.
- [x] Keep interpreter state injectable so tests can execute one act with
      preserved cross-act stacks and values.
- [x] Add `tests/test_splc_interpret.py` covering every op, both branch arms,
      EOF, underflow diagnostics, step-limit failure, and state handoff.
- [x] Port the six list spike inputs and the Amps/short token cases into fast
      interpreter parity tests without deleting the real-interpreter gates.
- [x] Run the required regression commands.

**Evidence gate:** interpreter token streams equal the committed dump baselines;
real generated SPL is byte-identical before and after the task.

## Task 2 — Add executable stack-borrow and stream contracts

- [x] Add a verification-only contract module under `scripts/splc/` with typed
      snapshots and assertions for stack prefix preservation, sentinel balance,
      expected carrier termination, and no pop below a declared floor.
- [x] Instrument the IR interpreter with optional boundary observers; do not
      add runtime operations or rendered SPL.
- [ ] Add Act II contract tests proving that arbitrary pre-existing payload on
      Horatio's stack survives the list-looseness side-channel borrow.
- [ ] Assert Macbeth's frame floor and all temporary carrier floors are restored
      across every existing list spike case.
- [ ] Add an explicit empty-input test that records the current real-runtime
      failure and a fast-interpreter diagnostic. Do not silently normalize or
      fix production behavior in this plan.
- [ ] Run the required regression commands.

**Evidence gate:** corrupting or omitting any floor/sentinel in a mutation-style
test causes a local, named contract failure rather than a downstream SPL pop.

## Task 3 — Add lexical decoding and structural token validation

- [ ] Extend token metadata with verification-only structural roles without
      changing numeric codes or `ARITY` behavior.
- [ ] Add a decoder that turns integer dumps into typed tokens and rejects
      unknown codes, truncated payloads, unterminated text, and framing markers
      that escape their permitted phase.
- [ ] Add a structural validator for the currently shipped grammar: top-level
      paragraphs and balanced lists with legal item placement/nesting.
- [ ] Represent the target recursive container grammar from the hardening
      design in tests marked as expected future cases; do not weaken current
      validation to accept an undecided representation.
- [ ] Validate every committed dump fixture in `tests/fixtures/token_stream/`.
- [ ] Add malformed-stream unit cases for each rejection class.
- [ ] Run the required regression commands.

**Evidence gate:** all committed dumps decode and validate; malformed nesting
fails before Act IV; no dump baseline changes.

## Task 4 — Add all-fixture differential smoke reporting

- [ ] Add `scripts/differential_smoke.py` with typed result records, per-case
      timeout, bounded stderr, first-byte-difference reporting, JSON output,
      and Markdown rendering.
- [ ] Default mode is observational: fixture mismatches/crashes/timeouts appear
      in the report but do not make the command fail. Harness/configuration
      failures do fail.
- [ ] Add repeatable `--require NAME` arguments that make named fixtures fail
      unless byte-identical; use the strict harness's selection conventions.
- [ ] Unit-test subprocesses via mocks and add one local integration test only
      if marked `@pytest.mark.integration`.
- [ ] Run the command over all 23 fixtures and write its dated baseline under
      `.agent/` (operator evidence, not a committed correctness oracle).
- [ ] Ensure both documentation aggregates appear with status, elapsed time,
      and crash/diff information.
- [ ] Run the required regression commands.

**Evidence gate:** observational mode completes all discoverable cases even
when `./shakedown` crashes; `--require 'Amps and angle encoding'` passes.

## Task 5 — Measure feedback-loop acceleration options

- [ ] Record the clean-tree baseline for sequential shipped-fixture plus spike
      regression wall time, current SPL line/scene counts, and representative
      single-fixture first/median runtime.
- [ ] Add `pytest-xdist` only in an isolated experiment and benchmark worker
      counts 2, 4, and logical-CPU count. Keep it only if the best repeatable
      result materially improves wall time without instability; otherwise
      record the negative decision and revert the dependency/config change.
- [ ] Inspect and prototype a session-scoped in-process parsed-play runner.
      Test repeated inputs in both orders, error cases, stdout/stderr parity,
      and state leakage against fresh subprocess execution.
- [ ] Adopt the runner only for regression acceleration if state isolation is
      proven. Keep at least one real subprocess binary-contract test and all
      release-performance measurements.
- [ ] Update `docs/architecture/cache-spike.md`,
      `docs/performance/budget.md`, and `docs/verification-plan.md` with exact
      commands, dates, run counts, and decisions.
- [ ] Run the required regression commands.

**Decision gate:** neither acceleration path is adopted on plausibility alone.
If both fail, direct subprocess mode remains and the recorded projection
determines whether Spike B needs a narrower execution cadence.

## Task 6 — Build the MCO-only autonomous roadmap executor

- [x] Add a project-local MCO custom-agent definition for `agy`; it is
      implementation/fix only and never eligible for planning.
- [x] Add the active `./agent-loop` entry point plus a typed Python module that
      parses roadmap rows, resolves the sole active plan and first unchecked
      step, classifies `plan`/`implement`/`fix`, and dispatches exactly one MCO
      invocation.
- [x] Encode a capability-escalating model policy as configuration: ordinary
      planning starts with Codex `gpt-5.6-terra` then Claude `sonnet`, escalating
      to Claude `opus` and Codex `gpt-5.6-sol`; implementation/fix starts with
      Claude `sonnet`, Codex `gpt-5.4`, and Agy Gemini 3.5 Flash High, escalating
      to Claude `opus`, Codex `gpt-5.6-sol`, and Agy Gemini 3.1 Pro High before
      the Pi+xAI Grok and Pi+OpenRouter `tencent/hy3:free` availability tail.
      Hy3 free is the only permitted OpenRouter model.
- [x] Load only `XAI_API_KEY` and `OPENROUTER_API_KEY` from the configurable
      external env file (default `~/hn-qotd/evals/.env`). Never print, persist,
      or pass secret values in argv.
- [x] Persist per-executor cooldown/failure state under ignored `.agent/`
      storage. Classify normalized MCO rate-limit/transient errors and
      zero-progress results; advance to the next eligible executor without
      crossing the planning/implementation role boundary.
- [x] Build prompts from durable repository state: roadmap action, exact plan
      and step, blockers, git status, prior failure summary, and verification
      commands. Never claim that one provider resumes another provider's
      private conversation.
- [x] Planning prompts are non-interactive and require a complete
      Superpowers-style `docs/superpowers/plans/YYYY-MM-DD-<slug>.md`, an exact
      sole-in-flight roadmap entry, and any prerequisite accepted design under
      the matching `docs/superpowers/specs/` convention. SPL-facing plans must
      reserve literary surfaces and name exact compliance tests. Planning
      agents record reasonable assumptions and do not wait for human input.
- [x] Add `--once`, dry-run/status output, configurable cooldown, and an
      operator-interrupt-safe continuous mode. One writing MCO invocation at a
      time; no parallel worktree mutation.
- [x] Require every successful agent iteration to make small conventional
      commits at logical verified checkpoints and push the current branch;
      never create empty commits or force-push, and surface push failures as
      blockers.
- [x] Require `Agent:`, `Model:`, and `Harness:` trailers plus the configured
      model/provider `Co-authored-by:` identity on every autonomous commit,
      while retaining the operator's Git identity as primary author.
- [x] Keep Claude Fable 5 outside automatic pools. Add only an explicit rare
      `--govern` read-only review that persists a directive under `.agent/`;
      recommend it after the complete fallback chain is unavailable or a
      formal architecture halt, and let ordinary agents execute its advice.
- [x] Make termination driver-owned: all roadmap rows shipped, full pytest
      green, all 23 mdtest fixtures passing with no skips, and strict parity
      22/22 for deterministic fixtures. `Auto links` uses the documented
      entity-normalized mdtest comparison because Markdown.pl randomizes its
      email encoding. Agent-created completion markers alone do not stop the
      loop.
- [x] Add unit tests with mocked MCO subprocesses for roadmap classification,
      model eligibility/order, env loading/redaction, rate-limit failover,
      zero-progress failover, dirty-worktree handoff context, and completion
      gates.
- [x] Update `CLAUDE.md`, `README.md`, and `docs/README.md` to make
      `./agent-loop` active and keep `./run-loop` explicitly historical.

**Evidence gate:** dry-run selects Plan 3M's first unchecked step and an
eligible implementation executor; forced failures walk the configured chain
in order; planning never selects `agy`, xAI, or OpenRouter; no secret appears
in captured argv, output, state, or artifacts.

**Evidence recorded 2026-07-12:** all nine MCO adapter/model dry-runs resolved
the reviewed command templates; `tests/test_mco_loop.py` passed 25 tests;
roadmap/protocol/legacy-loop contracts passed 68 tests; full lint, format, and
type checks passed; the full default suite passed 407 tests with the roadmap's
26 expected skips. Generated SPL was not touched.

## Task 7 — Integrate evidence into the roadmap and architecture

- [ ] Update the canonical architecture spec with the structural-contract,
      stack-contract, span-spike, differential-smoke, and performance-gate
      decisions from the approved hardening design.
- [ ] Replace the obsolete ~600-line halt trigger with the measured red-budget
      / two-consecutive-projection trigger.
- [ ] Revise Spike B's outcome language: failure reopens container grammar and
      recursive scheduling before character partitioning.
- [ ] Update `docs/superpowers/notes/2026-07-07-completability-review.md` so
      resolved, implemented, and still-open actions are unambiguous.
- [ ] Mark plan 3M shipped only after Tasks 1–5 pass; leave Spike B pending
      until its separate design and literary reservations are reviewed.
- [ ] Run:

```bash
uv run pytest tests/test_roadmap_contract.py tests/test_prompt_literary_protocol.py -q
uv run pytest -q
```

**Final gate:** default suite green; generated artifacts byte-identical; plan
3M evidence recorded; exactly zero plans are in flight after marking it
shipped; Spike B is the next pending implementation scope.
