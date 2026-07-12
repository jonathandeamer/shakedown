# Completability Hardening — Design

**Date:** 2026-07-11
**Status:** approved for staged implementation
**Origin:** interactive architecture review after Spike A P2
**Amends:** `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`

## Problem

Spike A established that the SPL-from-IR workflow and the multi-pass block
dispatcher can ship real Markdown behavior. It also exposed the next class of
completability risks:

1. the token table defines lexical arity but not a grammar for nested block
   ownership;
2. splc validates SPL choreography but not runtime stack/sentinel behavior;
3. the span pipeline has no early architecture gate for protected regions and
   backtracking;
4. fixed parse cost grows with generated program size; and
5. skipped future fixtures provide no early structural signal.

None of these findings invalidates the four-act split, the IR compiler, or the
one-plan-at-a-time roadmap. They require stronger contracts at those
boundaries before the remaining feature slices make them expensive to change.

## Decision summary

1. **Add completion-safety rails before Spike B.** Commit the
   instruction-level IR interpreter previously used only during Spike A plan
   validation, executable stack-preservation assertions, a structural token
   validator, an all-fixture differential smoke report, and measured feedback-
   loop experiments.
2. **Spike B validates a recursive container grammar, not merely two output
   examples.** Its design step must choose and document explicit list-item
   ownership before implementation. The preferred shape is container-normal
   tokens with explicit item boundaries; retaining implicit closure requires
   equally strong grammar and return-boundary evidence.
3. **A span architecture spike precedes broad Act III growth.** It is the first
   stage of Slice 2 and has its own halt-and-redesign outcome.
4. **Performance is measured at every shipped plan.** Program size, scene
   count, representative single-run time, and regression wall time replace the
   obsolete 600-line halt trigger.
5. **All 23 fixtures become non-gating canaries immediately.** Shipped
   fixtures remain the only parity gate; future fixtures produce a report of
   match, mismatch, crash, first difference, and runtime.
6. **The autonomous executor is MCO-only.** A project-local supervisor chooses
   the next roadmap action and dispatches exactly one MCO provider at a time.
   Durable repository state, never a provider's private conversation, is the
   cross-provider handoff contract.

## 1. Structural token contract

`src_ir/tokens.py::ARITY` remains the single lexical definition of token code,
fixed payload count, and text-bearing status. A new structural layer validates
legal token sequences after lexical decoding.

The target recursive grammar is:

```text
document   := block*
block      := paragraph | header | horizontal_rule | code_block | raw_html
            | list | blockquote
list       := LIST_OPEN item+ LIST_CLOSE
item       := ITEM_OPEN block* ITEM_CLOSE
blockquote := BLOCKQUOTE_OPEN block* BLOCKQUOTE_CLOSE
```

This is the semantic grammar, not yet a commitment to final numeric token
codes. Spike B chooses the concrete representation. In particular, it decides
whether the existing text-bearing `LIST_ITEM` can safely encode `ITEM_OPEN`
with implicit closure, or whether the stream migrates to explicit
`LIST_ITEM_OPEN`/`LIST_ITEM_CLOSE` tokens. The decision must account for:

- a nested block followed by a sibling item;
- loose items containing multiple paragraphs or other block types;
- list-in-blockquote and blockquote-in-list return boundaries;
- later passes descending into already-tokenized containers; and
- Act III applying spans only to eligible leaf text.

The structural validator is verification infrastructure. It may decode and
inspect token dumps in Python, but it performs no production Markdown work and
does not alter the SPL-ownership boundary.

## 2. Executable IR and stack ownership

The instruction-level interpreter described in the Spike A P2 plan-validation
provenance becomes committed test infrastructure. It implements the closed IR
instruction set, character values/stacks, global question result, scene jumps,
input, output, and a configurable step limit. It does not interpret generated
SPL prose and is never used by `./shakedown`.

The interpreter supports executable invariants at act and pass boundaries:

- no pop below a declared stack floor;
- every temporary sentinel frame is consumed exactly once;
- a borrowed stack preserves the prefix beneath its floor sentinel;
- Act II preserves Horatio's pre-existing cross-act payload while borrowing
  the stack for list looseness;
- carrier streams end with exactly one `STREAM_END`; and
- the emitted stream passes lexical and structural validation.

This design deliberately starts with executable contracts rather than a
general static stack-height theorem. Data-dependent loops make a sound static
height analysis substantially more complex. If an invariant can only be
proved statically, splc validation may grow a conservative analysis later;
the committed interpreter and contracts are the immediate, testable floor.

Empty stdin becomes a mandatory interpreter and real-wrapper case. The
currently recorded Act I underflow is fixed by the first feature plan that is
allowed to change behavior; the safety-rails plan first makes it a visible,
non-silent failure and establishes the expected empty-document contract.

## 3. Spike B acceptance contract

Spike B keeps the existing two oracle cases and adds at least:

1. a list item containing a blockquote followed by a sibling list item;
2. a blockquote containing a list followed by quoted paragraph text;
3. a loose list item containing a blockquote or second paragraph; and
4. a nested container that closes two levels before ordinary following text.

Before SPL-changing tasks begin, the Spike B plan must include reviewed token
streams for every case and ready-to-paste literary reservations per
`docs/superpowers/notes/spl-literary-protocol.md`. Passing rendered HTML while
emitting a structurally invalid stream is a gate failure.

If Spike B fails, the first revision target is the container grammar and
recursive pass scheduling. Character-stack partitioning is reconsidered only
when evidence shows that a valid grammar cannot be realized with the current
stack ownership.

## 4. Span architecture spike

The former Slice 2 becomes two stages:

- **Span Spike:** code-span protection, escapes, and representative interaction
  probes establish the protected-region representation and buffered scanning
  shape.
- **Slice 2 fixtures:** the remaining low-risk fixtures land against the
  accepted span design.

The spike includes multiple/variable-length code spans, escapes inside and
outside protected spans, punctuation-rich link/image destinations, emphasis
inside link text, HTML-tag protection, and representative overlapping
strong/emphasis cases. It may conclude that protected tokens, hashes, or
buffered substreams are required. A failure reopens Act III's transformation
model before additional span scenes are committed.

## 5. Feedback-loop performance

The completion-safety plan measures, rather than assumes, two acceleration
paths:

1. `pytest-xdist` over independent subprocess fixtures; and
2. a session-scoped in-process parsed-play runner with explicit state reset or
   reconstruction between inputs.

The in-process runner is test-only. The real `./shakedown` subprocess remains
the binary-contract and release-performance authority. A cache path is adopted
only if repeated-input output, stderr, and failure behavior match fresh
subprocess execution and mutable interpreter state cannot leak between cases.

Every shipped plan records:

- generated SPL lines and scenes per act;
- first-run and median representative fixture time;
- shipped-fixture regression wall time; and
- a projection against the performance-budget yellow/red thresholds.

The architecture conversation trigger is now either a measured red threshold
or two consecutive plans whose observed growth projects the full contract
beyond red. Raw line count alone is diagnostic, not a halt condition.

## 6. Differential smoke reporting

A new CLI runs all 23 local mdtest inputs through `./shakedown` and Markdown.pl
with per-case timeouts. It writes a stable machine-readable result and a human
Markdown summary containing:

- byte-identical / mismatch / shakedown crash / oracle crash / timeout;
- first differing byte;
- return code and bounded stderr excerpt; and
- shakedown and oracle elapsed time.

The command returns nonzero only for harness/configuration failure by default;
future unimplemented fixture mismatches are observations. A `--require`
option makes named shipped fixtures gating. CI and plans keep the existing
strict parity harness as the canonical shipped-fixture gate.

The two documentation aggregates run from the first safety-rails plan onward,
not after Slice 2. Their results are canaries, never an excuse to widen a
feature plan opportunistically.

## Staging

1. **Plan 3M — Completion Safety Rails.** Verification-only IR interpreter,
   executable stack contracts, structural token validator, differential smoke
   CLI, and measured parallel/cache experiments. No generated SPL or literary
   surface changes.
2. **Plan 4 — Spike B.** Concrete container representation plus nested
   blockquote/list implementation against the strengthened acceptance contract.
3. **Plan 4S — Span Architecture Spike.** Protected-region and buffered-scan
   decision before the remaining low-risk fixtures.
4. **Plan 5 onward.** Existing risk-ascending fixture slices without changing
   their feature scope.

One plan remains in flight at a time. Later plans are written only after their
predecessor's evidence is incorporated into the canonical architecture.

## 7. MCO autonomous execution

The active autonomous entry point is `./agent-loop`. The historical
`./run-loop` remains preserved but is not used by the new workflow. MCO is the
only provider orchestration layer; the supervisor does not invoke Claude,
Codex, agy, Pi, xAI, or OpenRouter directly.

### Action classification

Each iteration reads the live roadmap, active plan, blocker file, and prior
loop state:

1. Any `- BLOCK:` line makes the action `fix`.
2. More than one in-flight roadmap row is a hard configuration error.
3. No in-flight row plus at least one pending row makes the action `plan`.
4. One in-flight row with an unchecked step makes the action `implement`,
   except an explicitly plan-authoring/design/literary-reservation step is
   `plan`.
5. An in-flight plan with no unchecked steps is `fix` until its final gate is
   proven and the roadmap status is updated.
6. With no pending or in-flight rows, the action is `fix` until the full pytest
   suite passes, all 23 mdtest fixtures pass with no skips, and the 22
   deterministic fixtures pass the strict oracle harness; only then is the
   project complete. `Auto links` is proven by the documented entity-normalized
   mdtest comparison because Markdown.pl randomizes email entity choices.

### Model policy

Ordinary planning dispatch begins with balanced models and escalates only after
substantive failures. Its order is:

1. Codex `gpt-5.6-terra`;
2. Claude `sonnet` as the cross-provider routine fallback;
3. Claude `opus` as a quality escalation;
4. Codex `gpt-5.6-sol` as the final planning escalation.

A planning executor is non-interactive. It writes a complete Superpowers-style
plan at `docs/superpowers/plans/YYYY-MM-DD-<slug>.md`, using the established
checkbox/evidence-gate conventions, and updates the roadmap with that exact
path as the sole in-flight plan. SPL-facing plans include the literary
protocol, exact compliance commands, ready-to-paste controlled surfaces, and
spares. If an architecture decision must be made first, the executor writes an
accepted design under `docs/superpowers/specs/YYYY-MM-DD-<slug>.md` and cites
it from the plan. It makes and records reasonable assumptions instead of
waiting for human input; only a genuine safety/authority blocker may stop it.

Implementation and fixing dispatch use, in order:

1. Claude `sonnet`;
2. Codex `gpt-5.4`;
3. Agy with Gemini 3.5 Flash High;
4. Claude `opus` as a quality escalation;
5. Codex `gpt-5.6-sol` as a quality escalation;
6. Agy with Gemini 3.1 Pro High as the last quality escalation;
7. Pi through xAI with `grok-build-0.1`;
8. Pi through OpenRouter with `tencent/hy3:free`.

Hy3 free is the only permitted OpenRouter model. Agy is implementation/fix
only. This ladder favors sensible routine models and diversity before premium
reasoning, rather than paying for the strongest model on every iteration.

Provider/model identifiers are configuration, not control-flow constants, so
retired aliases can be replaced without changing the loop. The OpenRouter
policy is nevertheless an explicit allowlist of `tencent/hy3:free`, not a
general free-model router.

Claude Fable 5 is deliberately absent from both automatic pools. The loop may
recommend `./agent-loop --govern` only after the complete eligible fallback
chain is unavailable or a formal architecture halt is recorded. That command
runs one read-only review and persists a `CONTINUE`, `FIX`, `REDIRECT`, or
`STOP` directive under ignored `.agent/` state. Ordinary Opus/`gpt-5.6-sol`
planning agents or implementation agents execute the directive; Fable never
writes the repository. This is a manual cost gate, not an automatic retry.

### Rate limits and handoff

MCO performs its own retry/backoff within one invocation. The supervisor then
classifies the normalized MCO result. Rate limits and transient failures cool
the whole provider quota group; backend and zero-progress failures cool only
that executor so a stronger model from the same provider remains eligible.
Either case advances to the next eligible executor for the same action.
Planning executors never fall through to implementation-only models.

Only one writing invocation may run at once. Before every handoff the next
prompt includes the action, exact active plan/step, blocker state, working-tree
status, prior failure summary, and required verification gate. Secrets are
loaded only from named environment variables and never written into prompts,
state, artifacts, or logs.

Each successful iteration runs its scoped evidence gate, makes a small
conventional commit at a logical checkpoint, and pushes the current branch so
GitHub is a live progress surface. Empty commits, force-pushes, tags, and
version churn are forbidden. A required push failure becomes a durable blocker
instead of being silently deferred.

Every autonomous commit includes `Agent:`, `Model:`, and `Harness:` Git
trailers plus the configured `Co-authored-by:` model/provider identity. This
explicit provenance overrides generic agent defaults that suppress AI credit;
the operator's configured Git identity remains the primary commit author.

### Completion

Agent self-reports and marker files are advisory. The supervisor owns
termination. Completion requires all roadmap work shipped, `uv run pytest -q`
green, `tests/test_mdtest.py` reporting 23 passed with no skips, and
`scripts/strict_parity_harness.py` reporting 22/22 byte-identical deterministic
fixtures. The excluded `Auto links` raw comparison is covered by the accepted
entity-normalized divergence in `tests/test_mdtest.py`.

## What does not change

- SPL owns all production Markdown behavior.
- `src_ir/` plus `src/literary.toml` are authored sources; generated SPL is
  never hand-edited.
- The four-act Pre-process / Block / Span / Emit split remains.
- Byte-identical local-oracle comparison remains the shipped-fixture gate.
- Literary authorship remains planning-time work.
- The one-plan-at-a-time roadmap and halt discipline remain binding.
