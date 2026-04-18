# The Ralph Loop (Huntley Loop) — Reference

> Reference for the autonomous-agent loop methodology that drove Snarkdown and Quackdown, with notes on what transfers to Shakedown. Synthesised from Geoff Huntley's writing and the Shakedown → Snarkdown → Quackdown lineage.

## One-line definition

A *Ralph loop* is `while :; do cat PROMPT.md | agent-cli ; done` — a continuously executing LLM agent, invoked with a fixed short prompt, iterating against a test harness or task list until a completion marker is written.

Also called a *Huntley loop* after Geoff Huntley, who popularised the pattern in late 2025 / early 2026. The name *Ralph* comes from Ralph Wiggum: the loop is "deterministically bad in an undeterministic world" — each iteration is shallow, but the loop compounds.

## Why this pattern exists

From [ghuntley.com/ralph](https://ghuntley.com/ralph/) and [ghuntley.com/porting](https://ghuntley.com/porting/):

- **Context windows are the constraint, not model capability.** An agent given a 200k-token advertised window has ~170k usable before quality degrades. A single long-running session drifts; a fresh session with a focused prompt does not.
- **Correctness comes from the harness, not the agent.** The agent writes code; the test runner, type checker, linter, and citation spec provide backpressure. The agent is free to be wrong because the harness will reject wrong answers.
- **Speed × correctness, balanced.** The loop wins by iteration volume. Slowing the agent down with elaborate planning per iteration destroys the economics; letting it iterate with no backpressure destroys correctness.
- **Eventual consistency by faith.** Huntley: "faith and belief in eventual consistency". No single iteration is required to make progress; the *average* iteration must.
- **Scale is real.** The RepoMirror team at the YC Agents hackathon reported ~1,100 commits across 6 repositories in ~29 hours for ~$800 of inference. The loop is not a toy; it is a production porting mechanism when the work fits.

## Core axioms

Observed across Huntley's writing and the lineage:

1. **One thing per iteration.** The prompt says "pick the first failing test" or "find the first unchecked task". Not "do everything".
2. **Fresh context every iteration.** No session continuity. The agent re-reads the world from disk each time.
3. **No placeholders.** Huntley, all-caps: "DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS. WE WANT FULL IMPLEMENTATIONS. DO IT OR I WILL YELL AT YOU." Placeholders survive iterations; real implementations get exercised by the harness.
4. **Short prompts beat long prompts.** The RepoMirror team found a 103-word prompt outperformed a 1,500-word prompt written by Claude's own prompt-expansion. The long prompt degraded quality; reverting restored it. Prompt discipline is a first-class concern: aim for ~200 words of standing instructions plus `@file` references, not a treatise.
5. **Operator supervision is required.** Huntley is explicit: "There's no way in heck would I use Ralph in an existing code base" without a skilled operator reading diffs. The loop is not autonomous software; it is a human-supervised crank.
6. **Pattern-match problems to structure.** Porting a known spec (`Markdown.pl` → target language) is an excellent Ralph workload; greenfield design is not. The loop reduces implementation labour, not design labour.

## The mechanical shape

```bash
while :; do
  cat PROMPT.md | agent-cli --yolo
done
```

Minimum viable variant. Three pieces:

- **`PROMPT.md`** — a short (~200 word) fixed prompt. Reread every iteration. Contains the standing instruction, the stack-allocated references, and the exit condition.
- **`agent-cli`** — Claude Code, Codex, or equivalent, with permissions pre-approved (`--dangerously-skip-permissions` / `--dangerously-bypass-approvals-and-sandbox`).
- **The harness** — test runner, type checker, oracle diff. The agent's job each iteration is to make the harness happier.

Additions beyond the minimum (all observed in Quackdown's evolution, commit-by-commit):

- Completion-marker file that the *loop driver* (not the agent) checks, so a successful iteration can exit.
- Backend auto-switching on usage-limit messages (Claude ↔ Codex) to ride out rate limits without operator intervention.
- OOM / resource preflight guard to fail fast when the host cannot safely relaunch the agent.
- State file (`.agent/run-loop-state.json`) so backend choice persists across driver restarts.

`run-loop` at the root of this repo is one such driver. See `CLAUDE.md` "run-loop" section for the Shakedown-specific contract.

## Prompt patterns

Quackdown demonstrates three distinct Ralph-prompt shapes. All three are valid; pick the one that matches the work.

### 1. Test-driven iteration

```
Pick the first failing test alphabetically. Implement the minimal change to make it pass.
Commit. Do not work on any other test this iteration.
@docs/markdown-pl-spec.md
@.agent/blockers.md
```

**Use when:** there is a comprehensive test fixture set (e.g. `Markdown.mdtest`'s 23 fixtures) and the agent can execute the harness locally. The fixture set is the ordering; the agent picks one, fixes it, commits, exits. Next iteration picks the next.

**Shakedown applicability:** direct fit. 23 `*.text` / `*.xhtml` pairs are the natural work unit.

### 2. Task-plan-driven iteration

```
Find the first task in the plan that has any unchecked step (- [ ]).
Complete that step. Check it off. Commit.
@docs/superpowers/plans/<plan>.md
@<source-file-to-edit>
```

**Use when:** the work is sequenced (dependencies between steps, or a spec that must be built up in order). The plan document is the ordering; the agent advances the checkbox frontier one step per iteration.

**Shakedown applicability:** fits architecture-build phases where fixture order is constrained by shared machinery (e.g. inline must follow block-level).

### 3. Experiment-gated iteration

```
Run experiments in order. If current experiment is BLOCKED, exit.
Otherwise, execute the experiment and emit a PASS/PARTIAL/FAIL verdict.
@docs/experiments-spl/plan.md
```

**Use when:** the goal is feasibility evidence, not shipped code. Numbered experiments with a `BLOCKED` short-circuit let a single loop ride through many probes while preserving the option to stop the instant something fundamental breaks.

**Shakedown applicability:** used in the prior attempt (ten experiments across two rounds); not directly relevant to a fresh build, but the pattern is the right shape if Shakedown needs another feasibility sweep later.

## The `@file` stack-allocation pattern

Quackdown's `run-loop` expands `@path/to/file` references in the prompt *before* sending it to the agent. The expanded prompt looks like:

```
<original prompt lines>

=== Contents of docs/markdown-pl-spec.md ===
<entire file contents>

=== Contents of .agent/blockers.md ===
<entire file contents>
```

This matters because:

- The references are part of the prompt, so they do not cost the agent a `read_file` round-trip.
- They are always fresh — edits to the referenced file show up the next iteration automatically.
- They stack the agent's context without polluting the `PROMPT.md` file itself, which stays short and human-readable.

Huntley calls the per-agent reference file the agent's "university". `@file` stack-allocation is how you enrol the agent without lengthening the prompt.

**Implementation:** see `run-loop` in the root of this repo for the Python `expand_refs()` function. The mechanism is simple regex substitution; the discipline is in deciding what to include.

## The three-stage porting method

From [ghuntley.com/porting](https://ghuntley.com/porting/). Huntley's claim: "porting software has been trivial for a while now" — with this structure.

1. **Test-spec compression.** Dispatch subagents in parallel to compress each oracle test case into a one-paragraph spec. Output is a machine-checkable list of behaviours to preserve.
2. **Source-spec with citations.** Dispatch subagents to read the source and emit a spec that *cites specific functions and line numbers* in the oracle. Huntley: citations "tease the file_read tool to study the original implementation during stage 3". The citations are tripwires that pull the implementing agent back to the source when it drifts.
3. **TODO + iteration.** Write a TODO list. Run the Ralph loop against it. Strict compilation and strict tests provide the backpressure; citations provide the oracle anchor.

Quackdown's divergence (from its own snarkdown spec): collapsed stages 1–2 into a *single human-guided citation pass* because `Markdown.pl` is small (~1,500 lines) and one person can read it in an afternoon. See `docs/markdown-pl-spec.md` in the quackdown repo for the output format: one section per fixture, each citing the relevant `_DoHeaders` / `_DoCodeBlocks` / `_DoLists` function and a line range.

**Shakedown applicability:** a citation spec of this kind does not yet exist in this repo. Whether to build one is an architecture-planning question; if the answer is yes, the quackdown format is a working template.

## Operational infrastructure

The loop driver has to survive a multi-hour unattended run. Quackdown's `run-loop` grew four layers of operational plumbing, each in response to a concrete failure:

| Failure observed | Mitigation added | Quackdown commit |
|---|---|---|
| Backend hits usage limit, loop spins | Auto-switch to other backend on limit detection | `7c6f281` |
| Both backends limited simultaneously | Sleep 1 hour, then retry | `304c7f3` |
| Agent self-loops after completing work | Completion-marker file checked by driver, not agent | `9fa4667` |
| Claude OOM-killed on low-RAM host, loop relaunches | Preflight `/proc/meminfo` guard + post-exit OOM classifier | `43f1f60` |

The Shakedown `run-loop` inherits all four. The design lesson: **the driver should be the thing that knows when to stop.** Agents cannot reliably self-terminate; operators should not have to babysit; the driver must own termination, rate-limit handling, and resource failure.

Completion marker convention: `docs/prompt-<name>.md` → `.agent/complete-<name>.md`. The agent writes the marker; the driver checks it at the top of every iteration. The default marker for Shakedown is `.agent/complete-shakedown.md`.

## What transfers vs. what diverged in this lineage

Huntley's original playbook, adopted verbatim in parts and diverged from in others. This is the "what we learned" bit.

### Adopted across the lineage

- The while-true driver with a single fixed prompt.
- Fresh context every iteration; no session continuity.
- `@file` stack-allocation for standing references.
- One unit of work per iteration, selected by the agent from a deterministic ordering.
- Operator-in-the-loop reading diffs; Huntley's "skilled operator" requirement is load-bearing.

### Diverged in Snarkdown/Quackdown

- **Collapsed Huntley's three spec stages into one human-guided citation pass.** `Markdown.pl` is small enough that the subagent-parallel compression is overkill. One afternoon of reading produces a better spec than a fleet of subagents summarising in parallel.
- **Operator supervision rebalanced towards the driver.** Huntley's writing assumes a human watching the terminal. The quackdown driver absorbs rate-limiting, resource failure, and completion detection, so the human can leave the machine for hours.
- **Test harness is primary backpressure; type checker is secondary.** Huntley emphasises strict compilation. In Python and SQL, the type checker is helpful but not load-bearing; the fixture diff is.

### Open for Shakedown

- **Subagent parallelisation.** Huntley uses hundreds of subagents for search, single subagents for validation. Shakedown has not tried this. Whether it earns its keep against a small fixture set is unproven.
- **Prompt shape.** Test-driven, task-plan-driven, or experiment-gated — which fits a fresh Shakedown build is an architecture-planning question. The first fixture milestone is test-driven work; the full-port phase is likely task-plan-driven.
- **Citation spec against `Markdown.pl`.** Does not exist in this repo. Building one is optional; quackdown did, prior Shakedown did not.

## When the loop is the wrong tool

Huntley himself (from [ghuntley.com/ralph](https://ghuntley.com/ralph/)):

- **Greenfield design.** The loop implements; it does not decide what to build. Architecture planning is a human-led activity with agent assistance, not a Ralph workload.
- **Existing codebases without test coverage.** No backpressure, no correctness. The loop will happily "improve" the code into something broken.
- **Tasks without a clear ordering.** If the agent cannot pick the next unit deterministically, iterations collide.
- **Anything requiring cross-iteration memory.** The loop has no memory. If the task needs "remember this decision across hours", the decision belongs in a committed document the agent re-reads.
- **Scope-creep tolerance is low.** RepoMirror reported agents adding unrequested features (Flask/FastAPI integration, Pydantic validators) to a port. Sometimes useful, often noise. If the spec does not authorise it and the test harness does not require it, iterations should not produce it. A tight spec and a narrow test surface are the defences.
- **"Production quality" is rarely one-shot.** The RepoMirror runs that shipped overnight still needed interactive refinement before they were production-ready. Treat loop output as a completed draft, not finished software.

Shakedown's architecture-planning phase is an example of the wrong-tool case. The *implementation* phase that follows architecture is a canonical right-tool case.

## References

### Huntley's source material

- [ghuntley.com/ralph](https://ghuntley.com/ralph/) — The Ralph loop philosophy, backpressure-as-correctness, context-window constraints, the "deterministically bad" framing.
- [ghuntley.com/porting](https://ghuntley.com/porting/) — Three-stage porting method, subagent-driven test-spec compression, citations as tripwires.
- [ghuntley.com/cursed](https://ghuntley.com/cursed/) — The origin of the Ralph-Wiggum framing; a three-month while-true loop with a single prompt producing a Gen-Z compiler.
- [repomirrorhq/repomirror `repomirror.md`](https://github.com/repomirrorhq/repomirror/blob/main/repomirror.md) — YC Agents hackathon write-up: ~1,100 commits / 29h / $800 / 6 repos, and the empirical "short prompt beats long prompt" finding (103 words outperformed 1,500).

### Lineage source material

- `docs/lineage.md` — Shakedown → Snarkdown → Quackdown triad, one-minute summary.
- `~/quackdown/run-loop` — working Python implementation; reference for `@file` expansion, backend switching, OOM guard, completion marker.
- `~/quackdown/docs/prompt.md`, `prompt-cm.md`, `prompt-spl-feasibility.md` — the three prompt patterns, each in production use.
- `~/quackdown/docs/markdown-pl-spec.md` — the citation-spec format in working form.
- `~/quackdown/docs/superpowers/specs/2026-04-11-snarkdown-design.md` — the explicit "what we adopted / where we diverged" analysis.
- `~/quackdown/docs/superpowers/specs/2026-04-12-run-loop-python-design.md` — original design for the Python driver.
- `~/quackdown/docs/superpowers/specs/2026-04-16-run-loop-oom-guard-design.md` — OOM guard rationale and detection rules.

### In this repo

- `CLAUDE.md` "run-loop" section — Shakedown's driver contract.
- `run-loop` at repo root — the driver itself.
- `docs/prior-attempt/feasibility-lessons.md` — what the prior Shakedown Ralph run actually learned.
- `docs/prior-attempt/architecture-lessons.md` — where the prior Ralph run stalled (architecture, not the loop).
