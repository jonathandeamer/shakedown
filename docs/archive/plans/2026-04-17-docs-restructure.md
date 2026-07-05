# Docs Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate, rename, and rewrite the Shakedown docs outside `docs/superpowers/` into a MECE subject-clustered set (`docs/spl/`, `docs/markdown/`, `docs/prior-attempt/`, `docs/archive/`, plus `docs/README.md`, `docs/lineage.md`, `docs/verification-plan.md`) so a new agent has a comprehensive, current, accurate starting point for architecture planning.

**Architecture:** Subject-clustered directory layout per `docs/superpowers/specs/2026-04-17-docs-restructure-design.md`. Three SPL style docs move with cross-reference path edits only. Feasibility and architecture evidence consolidates from 3-source chains into single retrospectives. Stale workflow and resumption docs archive with a one-line header. A new `verification-plan.md` inventories claims by bucket (already-verified, cheap-replayable, retrospective, prediction, new).

**Tech Stack:** Markdown; `git mv` for content-preserving moves; grep/ripgrep for link checking; `shakespeare` CLI and standard Unix tools for cheap verification replays.

**Source spec:** `docs/superpowers/specs/2026-04-17-docs-restructure-design.md`.

**Scratch file used during execution:** `.agent/restructure-verification-outputs.md` — captures raw output of bucket-B replays so Phase 10 can assemble `verification-plan.md` without re-running them. Cleaned up in the final task.

---

## Phase 1 — Cheap Verification Replays

These run before any file move. They produce capture data used in Phase 10. No commits in this phase; outputs accumulate in `.agent/restructure-verification-outputs.md`.

### Task 1: Initialise verification scratch file

**Files:**
- Create: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Create the `.agent/` directory if missing and initialise the scratch file**

```bash
mkdir -p .agent
cat > .agent/restructure-verification-outputs.md <<'EOF'
# Restructure Verification Outputs

Raw capture of bucket-B replays from the docs restructure.
Consumed by `docs/verification-plan.md`; delete after restructure completes.

EOF
```

- [ ] **Step 2: Confirm the file exists**

```bash
ls -la .agent/restructure-verification-outputs.md
```

Expected: file exists, non-empty.

No commit — this is a working file.

### Task 2: Replay 1 — interpreter cold start

**Files:**
- Append to: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Write a minimal valid SPL play**

```bash
cat > /tmp/empty-cold-start.spl <<'EOF'
Cold Start Probe.

Romeo, a reader.
Juliet, a writer.

                    Act I: Nothing to do.

                    Scene I: Exeunt immediately.

[Exeunt]
EOF
```

- [ ] **Step 2: Run cold-start timing twice (first is cold, second is warm)**

```bash
{ echo "### Replay 1 — interpreter cold start"
  echo ""
  echo "Command: \`time shakespeare run /tmp/empty-cold-start.spl\` (first run)"
  echo '```'
  { time shakespeare run /tmp/empty-cold-start.spl ; } 2>&1
  echo '```'
  echo ""
  echo "Command: \`time shakespeare run /tmp/empty-cold-start.spl\` (second run)"
  echo '```'
  { time shakespeare run /tmp/empty-cold-start.spl ; } 2>&1
  echo '```'
  echo ""
  echo "Expected range (per prior measurements on this machine): 17–26s cold, 2–3s warm."
  echo ""
} >> .agent/restructure-verification-outputs.md
```

- [ ] **Step 3: Eyeball the captured times**

If both runs are outside the documented range (e.g., cold start < 5s or > 40s), append a
note to the scratch file flagging the drift. Do not halt — Phase 10 records the finding
and architecture planning decides what to do about it.

### Task 3: Replay 2 — interpreter identity

**Files:**
- Append to: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Capture install path and version**

```bash
{ echo "### Replay 2 — interpreter identity"
  echo ""
  echo "Command: \`which shakespeare\`"
  echo '```'
  which shakespeare 2>&1
  echo '```'
  echo ""
  echo "Command: \`shakespeare --version\`"
  echo '```'
  shakespeare --version 2>&1 || echo "(no --version; fallback)"
  echo '```'
  echo ""
  echo "Command: \`shakespeare --help | head -20\`"
  echo '```'
  shakespeare --help 2>&1 | head -20
  echo '```'
  echo ""
  echo "Expected: install path under ~/.local/bin (matches spl/reference.md line 5)."
  echo ""
} >> .agent/restructure-verification-outputs.md
```

### Task 4: Replay 3 — oracle present and version

**Files:**
- Append to: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Capture Markdown.pl header and version string**

```bash
{ echo "### Replay 3 — oracle (Markdown.pl) present"
  echo ""
  echo "Command: \`head -30 ~/markdown/Markdown.pl\`"
  echo '```'
  head -30 ~/markdown/Markdown.pl 2>&1
  echo '```'
  echo ""
  echo "Command: \`grep -E 'VERSION|version' ~/markdown/Markdown.pl | head -5\`"
  echo '```'
  grep -E 'VERSION|version' ~/markdown/Markdown.pl 2>&1 | head -5
  echo '```'
  echo ""
  echo "Expected: Markdown.pl v1.0.1 header present."
  echo ""
} >> .agent/restructure-verification-outputs.md
```

### Task 5: Replay 4 — fixture count

**Files:**
- Append to: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Count fixtures and capture names**

```bash
{ echo "### Replay 4 — Markdown.mdtest fixture count"
  echo ""
  echo "Command: \`ls ~/mdtest/Markdown.mdtest/*.text | wc -l\`"
  echo '```'
  ls ~/mdtest/Markdown.mdtest/*.text 2>&1 | wc -l
  echo '```'
  echo ""
  echo "Command: fixture names"
  echo '```'
  ls ~/mdtest/Markdown.mdtest/*.text 2>&1 | xargs -n1 basename | sed 's/\.text$//'
  echo '```'
  echo ""
  echo "Expected: 23 fixtures."
  echo ""
} >> .agent/restructure-verification-outputs.md
```

### Task 6: Replay 5 — no randomness primitive in SPL grammar

**Files:**
- Append to: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Grep grammar for randomness tokens**

```bash
{ echo "### Replay 5 — SPL grammar has no randomness primitive"
  echo ""
  echo "Command: \`grep -iE 'random|rand|chance' ~/shakespearelang/shakespearelang/shakespeare.ebnf\`"
  echo '```'
  grep -iE 'random|rand|chance' ~/shakespearelang/shakespearelang/shakespeare.ebnf 2>&1 || echo "(no matches — expected)"
  echo '```'
  echo ""
  echo "Expected: no matches. Confirms the email-autolink divergence rationale."
  echo ""
} >> .agent/restructure-verification-outputs.md
```

### Task 7: Replay 6 — integer-only numeric grammar

**Files:**
- Append to: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Grep grammar for floating-point tokens**

```bash
{ echo "### Replay 6 — SPL grammar has no floating-point numeric type"
  echo ""
  echo "Command: \`grep -iE 'float|double|decimal' ~/shakespearelang/shakespearelang/shakespeare.ebnf\`"
  echo '```'
  grep -iE 'float|double|decimal' ~/shakespearelang/shakespearelang/shakespeare.ebnf 2>&1 || echo "(no matches — expected)"
  echo '```'
  echo ""
  echo "Expected: no matches, or any match is clearly not a numeric type."
  echo ""
} >> .agent/restructure-verification-outputs.md
```

### Task 8: Replay 7 — AST-cache feasibility smoke test

**Files:**
- Append to: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Probe for a separable parse step**

```bash
{ echo "### Replay 7 — AST-cache feasibility smoke"
  echo ""
  echo "Command: check CLI for a parse/compile subcommand separate from run"
  echo '```'
  shakespeare --help 2>&1
  echo '---'
  shakespeare run --help 2>&1 | head -40
  echo '```'
  echo ""
  echo "Purpose: sanity-check whether the round-2 Exp 6 \"cached-AST\" model has a CLI surface in the current interpreter. If no parse-only subcommand exists, the cache strategy would need to be inside a Python wrapper (as the prior attempt used); that's acceptable — record the finding."
  echo ""
} >> .agent/restructure-verification-outputs.md
```

- [ ] **Step 2: Record the shape of the finding**

Append a one-line disposition to the scratch file:

```bash
{ echo "Disposition: [fill in one of] (a) CLI has a parse-only subcommand; (b) CLI has only \`run\`, cache would live in a Python wrapper; (c) unexpected — see capture above."
  echo ""
} >> .agent/restructure-verification-outputs.md
```

### Task 9: Replay 8 — reference claim coverage sweep

**Files:**
- Read: `docs/research/shakedown-spl-reference.md`
- Read: `docs/research/2026-04-17-spl-reference-verification.md`
- Read: `~/shakespearelang/shakespearelang/shakespeare.ebnf`
- Append to: `.agent/restructure-verification-outputs.md`

- [ ] **Step 1: Walk each claim in `shakedown-spl-reference.md` and categorise its backing**

For every claim labelled `Grammar-confirmed`, `Empirically confirmed`, or
`Corrected project assumption` in `shakedown-spl-reference.md`, classify as:

- **P** — backed by a row in the probe table of
  `2026-04-17-spl-reference-verification.md`
- **G** — backed by an ebnf rule (cite line if you can find it quickly)
- **C** — corrected project assumption already framed as such
- **?** — no backing found in either source

Record the tally (count of P/G/C/? claims) and the full list of `?` claims in the
scratch file under a heading `### Replay 8 — reference claim coverage sweep`. The `?`
list feeds bucket D in `verification-plan.md`.

- [ ] **Step 2: Sanity-check the total**

Expected: near-zero `?` claims. If there are more than a handful, pause and raise it —
that would contradict the design's assumption that `spl/reference.md` needs no
substantive edits.

---

## Phase 2 — Directory Skeleton

### Task 10: Create the new directory skeleton

**Files:**
- Create: `docs/spl/` (empty for now)
- Create: `docs/markdown/` (empty for now)
- Create: `docs/prior-attempt/` (empty for now)
- Create: `docs/archive/` (empty for now)

- [ ] **Step 1: Create directories with placeholder `.gitkeep` so they are visible**

```bash
mkdir -p docs/spl/probes docs/markdown docs/prior-attempt docs/archive
touch docs/spl/.gitkeep docs/spl/probes/.gitkeep docs/markdown/.gitkeep docs/prior-attempt/.gitkeep docs/archive/.gitkeep
```

- [ ] **Step 2: Confirm structure**

```bash
find docs -maxdepth 2 -type d | sort
```

Expected output includes `docs/spl`, `docs/spl/probes`, `docs/markdown`,
`docs/prior-attempt`, `docs/archive`, plus existing `docs/superpowers/*` and
`docs/research`.

- [ ] **Step 3: Commit**

```bash
git add docs/spl/.gitkeep docs/spl/probes/.gitkeep docs/markdown/.gitkeep docs/prior-attempt/.gitkeep docs/archive/.gitkeep
git commit -m "chore: scaffold docs subject directories"
```

---

## Phase 3 — Frozen Files

The three style docs move with cross-reference path edits only. Content bodies are
unchanged.

### Task 11: Move `shakedown-spl-reference.md` and update cross-refs

**Files:**
- Move: `docs/research/shakedown-spl-reference.md` → `docs/spl/reference.md`
- Remove: `docs/spl/.gitkeep` (directory now has real content)

- [ ] **Step 1: Record the pre-move content hash**

```bash
shasum -a 256 docs/research/shakedown-spl-reference.md > /tmp/ref-hash-pre
```

- [ ] **Step 2: Move the file**

```bash
git mv docs/research/shakedown-spl-reference.md docs/spl/reference.md
git rm docs/spl/.gitkeep
```

- [ ] **Step 3: Apply exactly three cross-reference edits**

Use Edit tool. In `docs/spl/reference.md`:

Edit A — line 16 area:

- **old:** `\`docs/research/2026-04-17-spl-reference-verification.md\`.`
- **new:** `\`docs/spl/verification-evidence.md\`.`

Edit B — line 91 area (inside the Lexicon legality note):

- **old:** `\`docs/research/shakedown-spl-style-lexicon.md\`.`
- **new:** `\`docs/spl/style-lexicon.md\`.`

Edit C — line 93 area:

- **old:** `\`docs/research/shakedown-spl-codegen-style-guide.md\`.`
- **new:** `\`docs/spl/codegen-style-guide.md\`.`

- [ ] **Step 4: Confirm body is otherwise unchanged**

```bash
shasum -a 256 docs/spl/reference.md > /tmp/ref-hash-post
```

Then inspect the diff between the staged version and `HEAD:docs/research/shakedown-spl-reference.md`:

```bash
git diff --cached HEAD -- docs/spl/reference.md | grep -E '^[-+]' | grep -v '^[-+][-+][-+]'
```

Expected: exactly 3 pairs of `-`/`+` lines (the three edits above) and nothing else.

- [ ] **Step 5: Grep for any remaining `docs/research/` references in the file**

```bash
grep -n "docs/research" docs/spl/reference.md || echo "(no matches — expected)"
```

Expected: no matches.

- [ ] **Step 6: Commit**

```bash
git add docs/spl/reference.md docs/spl/.gitkeep
git commit -m "docs: move SPL reference to docs/spl/ and update cross-refs"
```

### Task 12: Move `shakedown-spl-style-lexicon.md` and update cross-refs

**Files:**
- Move: `docs/research/shakedown-spl-style-lexicon.md` → `docs/spl/style-lexicon.md`

- [ ] **Step 1: Move the file**

```bash
git mv docs/research/shakedown-spl-style-lexicon.md docs/spl/style-lexicon.md
```

- [ ] **Step 2: Apply cross-reference edits**

In `docs/spl/style-lexicon.md`:

Edit A — line 4 area:

- **old:** `\`docs/research/shakedown-spl-reference.md\`.`
- **new:** `\`docs/spl/reference.md\`.`

Edit B — line 5–6 area:

- **old:** `\`docs/research/shakedown-spl-codegen-style-guide.md\`.`
- **new:** `\`docs/spl/codegen-style-guide.md\`.`

- [ ] **Step 3: Confirm cleanliness of the diff and no remaining old paths**

```bash
git diff --cached HEAD -- docs/spl/style-lexicon.md | grep -E '^[-+]' | grep -v '^[-+][-+][-+]'
grep -n "docs/research" docs/spl/style-lexicon.md || echo "(no matches — expected)"
```

Expected: exactly 2 `-`/`+` pairs; no remaining `docs/research` paths.

- [ ] **Step 4: Commit**

```bash
git add docs/spl/style-lexicon.md
git commit -m "docs: move SPL style lexicon to docs/spl/ and update cross-refs"
```

### Task 13: Move `shakedown-spl-codegen-style-guide.md` and update cross-refs

**Files:**
- Move: `docs/research/shakedown-spl-codegen-style-guide.md` → `docs/spl/codegen-style-guide.md`

- [ ] **Step 1: Move the file**

```bash
git mv docs/research/shakedown-spl-codegen-style-guide.md docs/spl/codegen-style-guide.md
```

- [ ] **Step 2: Apply cross-reference edits**

In `docs/spl/codegen-style-guide.md`:

Edit A — line 8 area:

- **old:** `\`docs/research/shakedown-spl-reference.md\` for legality and verified semantics`
- **new:** `\`docs/spl/reference.md\` for legality and verified semantics`

Edit B — line 9 area:

- **old:** `\`docs/research/shakedown-spl-style-lexicon.md\` for legal expressive vocabulary`
- **new:** `\`docs/spl/style-lexicon.md\` for legal expressive vocabulary`

Edit C — line 10 area:

- **old:** `\`docs/research/shakedown-spl-codegen-style-guide.md\` for implementation policy`
- **new:** `\`docs/spl/codegen-style-guide.md\` for implementation policy`

- [ ] **Step 3: Confirm cleanliness of the diff and no remaining old paths**

```bash
git diff --cached HEAD -- docs/spl/codegen-style-guide.md | grep -E '^[-+]' | grep -v '^[-+][-+][-+]'
grep -n "docs/research" docs/spl/codegen-style-guide.md || echo "(no matches — expected)"
```

Expected: exactly 3 `-`/`+` pairs; no remaining `docs/research` paths.

- [ ] **Step 4: Commit**

```bash
git add docs/spl/codegen-style-guide.md
git commit -m "docs: move SPL codegen style guide to docs/spl/ and update cross-refs"
```

---

## Phase 4 — Support Files

### Task 14: Move verification-evidence and update cross-refs

**Files:**
- Move: `docs/research/2026-04-17-spl-reference-verification.md` → `docs/spl/verification-evidence.md`

- [ ] **Step 1: Move the file**

```bash
git mv docs/research/2026-04-17-spl-reference-verification.md docs/spl/verification-evidence.md
```

- [ ] **Step 2: Update any `docs/research/...` references inside it**

```bash
grep -n "docs/research" docs/spl/verification-evidence.md
```

For each hit, use Edit to replace `docs/research/tmp-spl-probes/` with
`docs/spl/probes/`. Other `docs/research/...` paths (if any) update to their new
locations per the disposition table in the spec.

- [ ] **Step 3: Confirm no stale references remain**

```bash
grep -n "docs/research" docs/spl/verification-evidence.md || echo "(no matches — expected)"
```

- [ ] **Step 4: Commit**

```bash
git add docs/spl/verification-evidence.md
git commit -m "docs: move SPL verification evidence to docs/spl/"
```

### Task 15: Move lexicon-sources and update cross-refs

**Files:**
- Move: `docs/research/2026-04-17-spl-style-lexicon-sources.md` → `docs/spl/lexicon-sources.md`

- [ ] **Step 1: Move the file**

```bash
git mv docs/research/2026-04-17-spl-style-lexicon-sources.md docs/spl/lexicon-sources.md
```

- [ ] **Step 2: Update any cross-refs**

```bash
grep -n "docs/research" docs/spl/lexicon-sources.md || echo "(no matches)"
```

If there are hits, edit them to new paths.

- [ ] **Step 3: Commit**

```bash
git add docs/spl/lexicon-sources.md
git commit -m "docs: move SPL lexicon sources to docs/spl/"
```

### Task 16: Move the SPL probes directory

**Files:**
- Move: `docs/research/tmp-spl-probes/` → `docs/spl/probes/`
- Remove: `docs/spl/probes/.gitkeep`

- [ ] **Step 1: Move the probe programs**

```bash
for f in docs/research/tmp-spl-probes/*.spl; do
  git mv "$f" "docs/spl/probes/$(basename "$f")"
done
git rm docs/spl/probes/.gitkeep
rmdir docs/research/tmp-spl-probes
```

- [ ] **Step 2: Confirm 18 probe files land in the new location**

```bash
ls docs/spl/probes/*.spl | wc -l
```

Expected: 18.

- [ ] **Step 3: Update probe-path references inside `docs/spl/verification-evidence.md`**

```bash
grep -n "tmp-spl-probes" docs/spl/verification-evidence.md
```

Edit each hit to replace `docs/research/tmp-spl-probes/` with `docs/spl/probes/`.

- [ ] **Step 4: Confirm no stale probe paths remain anywhere in the doc tree**

```bash
grep -rn "tmp-spl-probes" docs/ || echo "(no matches — expected)"
```

- [ ] **Step 5: Commit**

```bash
git add docs/spl/probes/ docs/spl/verification-evidence.md
git commit -m "docs: move SPL probes to docs/spl/probes/"
```

### Task 17: Move the divergences file

**Files:**
- Move: `docs/research/shakedown-divergences.md` → `docs/markdown/divergences.md`
- Remove: `docs/markdown/.gitkeep`

- [ ] **Step 1: Move the file**

```bash
git mv docs/research/shakedown-divergences.md docs/markdown/divergences.md
git rm docs/markdown/.gitkeep
```

- [ ] **Step 2: Commit**

```bash
git add docs/markdown/
git commit -m "docs: move Markdown.pl divergences to docs/markdown/"
```

---

## Phase 5 — Archive Historical Docs

Each archived file gets a one-line header stamp prepended to the existing content. Use
the exact template below, substituting the successor path.

**Header template:**

```
> Archived 2026-04-17. Historical artifact from an earlier attempt. See <SUCCESSOR> for current guidance.

---

```

### Task 18: Archive project-history.md

**Files:**
- Move: `docs/research/project-history.md` → `docs/archive/project-history.md`
- Remove: `docs/archive/.gitkeep`

- [ ] **Step 1: Move the file**

```bash
git mv docs/research/project-history.md docs/archive/project-history.md
git rm docs/archive/.gitkeep
```

- [ ] **Step 2: Prepend the header stamp**

Use Edit on `docs/archive/project-history.md`. Prepend to the top of the file:

```
> Archived 2026-04-17. Historical artifact from an earlier attempt. See `docs/lineage.md` for current guidance.

---

```

Then keep the existing `# Project History: From Shakedown to Quackdown` heading and
rest of the content intact.

- [ ] **Step 3: Commit**

```bash
git add docs/archive/project-history.md
git commit -m "docs: archive project-history narrative"
```

### Task 19: Archive slow-machine-spl-workflow.md

**Files:**
- Move: `docs/research/slow-machine-spl-workflow.md` → `docs/archive/slow-machine-spl-workflow.md`

- [ ] **Step 1: Move the file**

```bash
git mv docs/research/slow-machine-spl-workflow.md docs/archive/slow-machine-spl-workflow.md
```

- [ ] **Step 2: Prepend the header stamp**

At the top of `docs/archive/slow-machine-spl-workflow.md`:

```
> Archived 2026-04-17. Historical artifact — references `scripts/spl-smoke`, `.worktrees/spl-slice-1`, and a `feature/spl-slice-1` branch that no longer exist in this repository. Interpreter timing numbers are preserved in `docs/prior-attempt/feasibility-lessons.md`. Inner-loop workflow for the new effort is an open architecture-planning question.

---

```

- [ ] **Step 3: Commit**

```bash
git add docs/archive/slow-machine-spl-workflow.md
git commit -m "docs: archive slow-machine workflow note"
```

### Task 20: Archive spl-feasibility-resumption-context.md

**Files:**
- Move: `docs/research/spl-feasibility-resumption-context.md` → `docs/archive/spl-feasibility-resumption-context.md`

- [ ] **Step 1: Move the file**

```bash
git mv docs/research/spl-feasibility-resumption-context.md docs/archive/spl-feasibility-resumption-context.md
```

- [ ] **Step 2: Prepend the header stamp**

At the top of `docs/archive/spl-feasibility-resumption-context.md`:

```
> Archived 2026-04-17. Mid-session brainstorming snapshot from 2026-04-14; its purpose (resuming a specific feasibility-study session on another machine) was consumed. Consolidated feasibility findings now live in `docs/prior-attempt/feasibility-lessons.md`. Lineage narrative lives in `docs/lineage.md` and `docs/archive/project-history.md`.

---

```

- [ ] **Step 3: Commit**

```bash
git add docs/archive/spl-feasibility-resumption-context.md
git commit -m "docs: archive feasibility resumption snapshot"
```

### Task 21: Archive the current prompt-shakedown.md

**Files:**
- Move: `docs/prompt-shakedown.md` → `docs/archive/prompt-shakedown.md`

- [ ] **Step 1: Move the file**

```bash
git mv docs/prompt-shakedown.md docs/archive/prompt-shakedown.md
```

- [ ] **Step 2: Prepend the header stamp**

At the top of `docs/archive/prompt-shakedown.md`:

```
> Archived 2026-04-17. This prompt's `@`-stack referenced files now relocated by the docs restructure. A replacement prompt will be written once the architecture-planning phase decides what a new agent should load. Until then, `docs/README.md` is the entry point for a fresh session.

---

```

- [ ] **Step 3: Confirm run-loop behaviour is not broken**

The `run-loop` Python script defaults to `docs/prompt-shakedown.md`. Check whether the
move breaks it:

```bash
grep -n "prompt-shakedown" run-loop CLAUDE.md
```

If `run-loop` hard-codes the old path and will be invoked before the replacement prompt
exists, note this in a commit message footer so the restructure does not silently break
the loop. **Do not modify `run-loop` in this task** — that is a behaviour change outside
the restructure scope. If the grep shows a hard-coded dependency, raise it; otherwise
proceed.

- [ ] **Step 4: Commit**

```bash
git add docs/archive/prompt-shakedown.md
git commit -m "docs: archive legacy prompt-shakedown loop prompt"
```

---

## Phase 6 — Consolidations

### Task 22: Write `prior-attempt/feasibility-lessons.md`

**Files:**
- Create: `docs/prior-attempt/feasibility-lessons.md`
- Sources (read, do not modify): `docs/research/feasibility-summary.md`, `docs/research/feasibility-summary-2.md`, `docs/research/shakedown-spl-feasibility-assumption-corrections.md`
- Remove: `docs/prior-attempt/.gitkeep`

- [ ] **Step 1: Write the new consolidated file with this structure**

```markdown
# Feasibility Lessons from the Prior Attempt

> This file consolidates three earlier sources: `feasibility-summary.md` (round 1, five experiments), `feasibility-summary-2.md` (round 2, five experiments), and `shakedown-spl-feasibility-assumption-corrections.md`. The originals are removed by the restructure; their content is preserved and integrated below.

## Context

The ten experiments summarised here were run in a prior `~/shakedown/` checkout that is no longer present in this repository. Round 1 measured against a 4,311-line `shakedown.spl`. Round 2 measured against an 8,623-line projected full port built on top of that work. Neither artifact exists in this repo. Claims of the form "we measured X at Y lines" are evidence from a prior codebase, not facts about the current state.

The consolidated voice below integrates the round-1 assumption corrections inline. Read this file once rather than the three source documents in sequence.

## Experiment Table

| # | Round | Experiment | Verdict | Key finding | Status in this repo |
|---|---|---|---|---|---|
| 1 | 1 | Runtime | PARTIAL | AST cache achieves 1.09s/test at 4,311 lines; degrades past 2s at projected 8,600-line full port | Retrospective: depends on a 4,311-line SPL file not present here |
| 2 | 1 | Single-act consolidation | PARTIAL | Shared-scene return-address pattern works; ~8% reduction, not the 30% target; blockquote reimplementation was 44% of the file | Retrospective: prior-code measurement |
| 3 | 1 | Inline span architecture | PARTIAL | Simple spans (code, basic emphasis) stream cleanly; emphasis matching and reference links need buffered O(n²) processing | Transferable: shape of the inline-vs-buffered choice survives |
| 4 | 1 | List parsing | PARTIAL | Marker detection + one-byte lookahead work; tight/loose feasible but unprototyped; nesting bounded to 2–3 levels | Transferable: list-depth bound is architecture input |
| 5 | 1 | Recursive block reprocessing | PARTIAL | Buffer-fed dispatch proven; one-level nesting works cleanly; multi-level constrained by prior cast design | Transferable: nested-block framing pattern survives |
| 6 | 2 | Runtime: AST cache splitting | PASS | Pre-built AST cache reduces per-test cost to ~0.30s at 8,623 lines | Retrospective: needs a new cheap smoke test in this repo (see `docs/verification-plan.md` replay 7) |
| 7 | 2 | Consolidation: shared-scene + recursive dispatch | PASS | The two patterns coexist cleanly in one act and stay far below the line-count target | Retrospective: prior-code measurement |
| 8 | 2 | Inline spans: emphasis matching | PARTIAL | Simple emphasis works; Markdown.pl backtracking semantics still diverge on nested/contextual emphasis | Transferable: names an open risk |
| 9 | 2 | List parsing: tight/loose and 2-level nesting | PARTIAL | Tight and 2-level nested lists match exactly; loose-list buffering still fails | Transferable: names an open risk |
| 10 | 2 | Recursive dispatch: frame sentinel pattern | PARTIAL | Sentinel-delimited frames work mechanically; exact nested blockquote+list output remains fragile | Transferable: names an open risk |

No round-1 experiment returned BLOCKED. Round 2 returned two PASS verdicts (6, 7) and three PARTIAL (8, 9, 10). The round-2 recommendation was a guarded GO.

## Corrected Assumptions

Three round-1 framings are retracted:

1. **There is no language-level "6-character budget" in SPL.** The local reference does not support that claim. What the reference does support: each character has one value and one stack, and legal names come from the interpreter grammar.
2. **"Two characters on stage" is a pronoun rule, not a universal stage-capacity rule.** Second-person pronouns (`you`, `thou`, `thee`, `yourself`, `thyself`) require exactly one other on-stage character to be unambiguous. The grammar and stage directions accept multi-character entrances and exits.
3. **"No limit on characters" overcorrects.** SPL does not impose a six-character cap, but the set of legal character names is the finite alternatives in the installed grammar. The available cast is finite.

The two-character wording that appears in the round-1 and round-2 summaries should be read as shorthand for second-person-pronoun addressing pressure, not a universal stage cap. See `docs/spl/reference.md` for the verified pronoun rule.

## What Transfers to This Repo

- The shape of the architectural trade-off between streaming and buffered inline handling.
- The list-depth bound (2 levels is enough for `Markdown.mdtest` fixtures).
- The nested-block framing pattern (sentinel-delimited frames on stacks) as a candidate approach.
- The divergence catalogue: email autolink randomisation is permanently unavailable in SPL (no randomness primitive); nested blockquote closer quirk is acceptable to diverge from (see `docs/markdown/divergences.md`).
- The Go/No-Go framing: the architecture is viable if PARTIAL verdicts are accepted as real documented trade-offs.

## What Does Not Transfer

- Specific line counts (4,311 and ~8,623).
- Specific per-test timings (1.09s, 0.30s).
- The ~8% / ~47% consolidation reduction numbers.
- The "~91–96% pass ceiling" estimate — it was predicated on specific architectural choices in the prior build.
- Cast-pressure judgments tied to the prior implementation's specific character set.
- Any "already implemented in Slice 1" claim for specific fixtures (the implementation is not here).

These numbers can be re-derived during architecture planning or a new feasibility pass. Until then, they are not evidence about this repo.

## Bottom Line for Architecture Planning

The prior attempt's ten experiments establish that a Shakedown port is architecturally possible. It does not establish that the specific architecture chosen by the prior attempt (single-act dispatcher with particular cast, AST cache via Python wrapper, recursive dispatch with sentinel frames) is the right choice for a fresh build. Architecture planning in this repo may arrive at the same design by a different route, or at a different design entirely.
```

- [ ] **Step 2: Remove the directory placeholder and commit**

```bash
git rm docs/prior-attempt/.gitkeep
git add docs/prior-attempt/feasibility-lessons.md
git commit -m "docs: consolidate feasibility findings into prior-attempt/feasibility-lessons.md"
```

### Task 23: Write `prior-attempt/architecture-lessons.md`

**Files:**
- Create: `docs/prior-attempt/architecture-lessons.md`
- Sources (read, do not modify): `docs/research/shakedown-mdtest-architecture-memo.md`, `docs/research/shakedown-before-design.md`, `docs/research/spl-act-architecture.md`

- [ ] **Step 1: Write the new consolidated file with this structure**

```markdown
# Architecture Lessons from the Prior Attempt

> This file consolidates three earlier sources: `shakedown-mdtest-architecture-memo.md` (recommended build shape), `shakedown-before-design.md` (pre-design reminder), and `spl-act-architecture.md` (the 2026-04-10 options memo). The originals are removed by the restructure; their content is preserved and integrated below.

## What the Prior Attempt Tried

The prior Shakedown SPL implementation was a single-act streaming dispatcher. It read stdin character-by-character, classified blocks, and dispatched to handlers that emitted HTML and jumped backwards to re-read input. The implementation reached roughly 4,300 lines across ~130 scenes. Slice 1 completed block-level features (paragraphs, ATX and setext headings, horizontal rules, indented code blocks, blockquotes including nested/lazy forms). Slice 2 (inline) and Slice 3 (lists, HTML blocks) were never begun.

## Act-Boundary Constraint

The core runtime property that shaped the architecture: **gotos cannot cross act boundaries**. Scene lookup in the installed interpreter is act-local. This is confirmed in `docs/spl/verification-evidence.md` and documented in `docs/spl/reference.md`.

Because the main processing loop is `read → classify → handle → read again`, every block handler needs a backwards jump to the read scene. That backwards jump cannot cross act boundaries, so the entire streaming dispatcher must live in one act. The original design envisioned Acts I–IV as pipeline phases (read / block scan / inline / emit); that shape is only legal if each act is itself a self-contained loop with its own internal backwards gotos, and the pipeline runs as multiple passes over buffered state rather than streaming per-line.

## Duplicated-Pattern Pressure

What made the single-act file unwieldy was not act count but repeated re-implementation of the same logic:

- **Before-block dispatch** appeared about five times (ATX, setext, HR, code block, blockquote): each block type re-implemented "emit `</p>` if we were in a paragraph; emit `\n` if the prior was a blockquote; else emit nothing."
- **Content emission loops** (pop from the line stack, emit until sentinel) were re-implemented per block type.
- **Blockquote sub-machinery** (scenes LXXXVII–CXXXIII, roughly half of the file) largely reimplemented paragraph/heading/code-block logic inside the blockquote context instead of reusing outer machinery.

The round-2 feasibility work validated that a shared-scene return-address pattern (treat Ophelia's value as a return address) and a buffer-fed recursive dispatcher can coexist inside a single act and together materially reduce duplication.

## The Three April-2026-04-10 Options (A/B/C) — Preserved as Historical Decision Surface

Options A, B, C were laid out near the end of the prior attempt. No decision was made; the project stalled at that decision memo.

**Option A — Keep single act, add inline as sub-dispatch.** Inline processing becomes a per-content-loop sub-dispatch. Each block handler's content emission loop calls into inline scenes before emitting each character run. No rewrite of Slice 1, but inline logic scatters across every block handler.

**Option B — Multi-pass rewrite (token stream).** Act I stops emitting HTML and instead emits a typed token stream. Act II processes the stream, runs inline substitutions, emits HTML. Correct use of SPL act structure. Requires rewriting most of Slice 1 and adds another full pass over data on a slow machine.

**Option C — Hybrid (consolidate duplicates first, then Option A).** Before any Slice 2 work, extract shared before-block dispatch and content emission into reusable scenes. Then add inline processing to the consolidated content path. Pragmatic; recommended by the memo but never executed.

For architecture planning in this repo, these three options are input, not a pending decision. A fresh design may select one, combine parts, or propose a fourth shape. What transfers is the framing of the trade-off (streaming vs multi-pass, duplication vs rewrite) and the identification of the duplication pressure as the real cost driver.

## Pre-Design Reminders That Still Apply

From the prior "before-design" note:

- The prior attempt proved that the target is not blocked by Markdown.pl itself; the earlier difficulty was the fit between SPL's shape and the workload.
- Start from the validated block-level baseline rather than from the original multi-act wish list.
- Treat recursive dispatch, cached execution (where available), and buffered inline handling as candidate starting shapes.
- Keep the design mdtest-focused and fixture-driven. The 23 `Markdown.mdtest` fixtures are the success surface.
- The main ceiling risks are email autolink encoding (permanent divergence), emphasis backtracking edge cases, loose-list exactness, and exact nested-block compositions.

One line from the earlier note is intentionally dropped: the earlier note said "do not re-open the question of whether SPL can be made to work at all for Markdown.pl." Architecture planning in this repo is, by design, re-opening exactly that question — for a fresh build with no inherited implementation.

## Items the Prior Memo Left Open

These are the open items architecture planning in this repo must close:

- The concrete build order across risky fixture groups.
- The exact integration boundary between block and inline phases.
- The milestone sequence for chasing the `Markdown.mdtest` ceiling.
- A decision among options A/B/C (or a fourth shape).
```

- [ ] **Step 2: Commit**

```bash
git add docs/prior-attempt/architecture-lessons.md
git commit -m "docs: consolidate architecture findings into prior-attempt/architecture-lessons.md"
```

---

## Phase 7 — New Forward-Facing Docs

### Task 24: Write `markdown/target.md`

**Files:**
- Create: `docs/markdown/target.md`
- Sources (read, do not modify): `docs/archive/project-history.md`, `docs/prior-attempt/feasibility-lessons.md`, `docs/markdown/divergences.md`, `~/markdown/Markdown.pl`, `~/mdtest/Markdown.mdtest/`

- [ ] **Step 1: Gather the fixture names**

```bash
ls ~/mdtest/Markdown.mdtest/*.text | xargs -n1 basename | sed 's/\.text$//' | sort > /tmp/fixture-names.txt
cat /tmp/fixture-names.txt
```

- [ ] **Step 2: Write the target spec with this structure**

Use Write tool to create `docs/markdown/target.md`:

```markdown
# Markdown.pl Target Surface

Shakedown ports John Gruber's `Markdown.pl` v1.0.1 to SPL. This file describes the behavioural surface that port must cover.

## Oracle

- Location: `~/markdown/Markdown.pl` on this machine.
- Version: v1.0.1 (confirmed by the version header in that file).
- Invocation: `perl ~/markdown/Markdown.pl < input.md > output.html`.

`Markdown.pl` is the single source of truth for correct output. Where its behaviour surprises, the oracle is right and Shakedown must match it — except for the intentional divergences in `docs/markdown/divergences.md`.

## Test Surface: Markdown.mdtest

The 23 fixtures at `~/mdtest/Markdown.mdtest/` define "done" for Shakedown. Each fixture is a pair: `*.text` input and `*.xhtml` (or `*.html`) expected output generated against Markdown.pl.

Fixture names (alphabetical):

[Insert the list from /tmp/fixture-names.txt, one fixture name per bullet.]

A Shakedown run is considered correct when its output, normalised through the same whitespace and entity handling the harness uses, matches the oracle's output for each fixture — again with the exceptions in `docs/markdown/divergences.md`.

## Feature Surface

Markdown.pl v1.0.1 implements (at a high level):

### Block-level
- Paragraphs separated by blank lines.
- ATX headings (`#` through `######`).
- Setext headings (`=` and `-` underlines).
- Horizontal rules (`***`, `---`, `___` with optional spaces).
- Indented code blocks (4-space or tab indent).
- Blockquotes (`>` prefix, with lazy continuation and nested variants).
- Unordered lists (`*`, `+`, `-` markers).
- Ordered lists (digits followed by `.`).
- Loose vs tight list detection based on blank-line presence.
- Raw HTML blocks passed through without transformation.

### Inline
- Emphasis (`*text*`, `_text_`) and strong emphasis (`**text**`, `__text__`).
- Code spans (`` `text` `` including double-backtick form for literal backticks).
- Inline links (`[text](url "title")`).
- Reference links (`[text][id]` resolved to a named reference).
- Inline images (`![alt](url "title")`) and reference images.
- Auto-links (`<http://...>` and `<email@domain>`).
- Backslash escapes (`\*`, `\\`, `\[`, etc.).
- `&` and `<` entity escaping outside of code and HTML spans.
- Inline HTML tags passed through.

### Intentional divergences from oracle behaviour

See `docs/markdown/divergences.md`. Summary: email autolinks emit plain `mailto:` links (no per-character entity obfuscation; SPL has no randomness primitive); the outer close tag on nested blockquotes emits as a well-formed `</blockquote>` rather than Markdown.pl's `<p></blockquote></p>` quirk.

## Interface

`./shakedown` is invoked as a subprocess with Markdown on stdin and HTML on stdout. The test harness at `tests/test_mdtest.py` pipes each fixture through it and diffs against the oracle output.

## What This Document Does Not Decide

- How the SPL program is structured (acts, scenes, dispatch shape).
- Whether the implementation is a single `.spl` file, a shell wrapper, a Python harness, or a combination.
- Which fixtures to tackle in what order.
- Which Markdown.pl quirks beyond the two listed above (if any) to treat as acceptable divergences.

Those are architecture-planning questions. This file only defines the target.
```

Replace the `[Insert the list...]` placeholder with the actual fixture names from
`/tmp/fixture-names.txt`. One per line with bullet markers. No other placeholders.

- [ ] **Step 3: Verify no placeholders remain**

```bash
grep -n '\[Insert' docs/markdown/target.md || echo "(no placeholders — expected)"
```

- [ ] **Step 4: Commit**

```bash
git add docs/markdown/target.md
git commit -m "docs: add Markdown.pl target spec"
```

### Task 25: Rewrite the fixture matrix as a predictive outlook

**Files:**
- Create: `docs/markdown/fixture-outlook.md`
- Move: `docs/research/shakedown-mdtest-fixture-matrix.md` (delete it — its content is superseded)

- [ ] **Step 1: Write the new outlook with this structure**

Use Write tool to create `docs/markdown/fixture-outlook.md`:

```markdown
# Fixture Outlook for a Fresh Build

> This file replaces the prior `shakedown-mdtest-fixture-matrix.md`. The prior matrix assigned "likely pass / uncertain / likely fail" labels based on a 4,311-line block-level implementation that does not exist in this repository. This file reframes the outlook as *risk tiers for a fresh build*.

## How to Read This File

This is a planning input, not a scorecard. It ranks each of the 23 `Markdown.mdtest` fixtures by expected implementation risk given what is known today about SPL semantics (from `docs/spl/`), the prior attempt's lessons (from `docs/prior-attempt/`), and intentional divergences (from `docs/markdown/divergences.md`).

Risk tiers:
- **Low** — no known architectural obstacle; implementation is straightforward once the block/inline pipeline is in place.
- **Medium** — behaviour-level edge cases in Markdown.pl may be hard to reproduce exactly; core implementation is tractable.
- **High** — fundamental risk tied to SPL limits or to Markdown.pl quirks that resist reproduction.
- **Divergence** — will not match oracle; covered by `docs/markdown/divergences.md`.

## Fixture Outlook

| Fixture | Risk tier | Primary risk | Notes |
|---|---|---|---|
| ATX Headers | Low | — | Block-level structure is straightforward in a streaming dispatcher. |
| Setext Headers | Low | — | Two-line look-behind; manageable with line buffering. |
| Paragraphs and Simple Blocks | Low | — | The core flow of the block pipeline. |
| Horizontal Rules | Low | — | Single-line pattern. |
| Indented Code Blocks | Low | Interaction with nested blocks | HTML-encoding `<` and `&` inside the code block is routine. |
| Blockquotes | Low–Medium | Nested composition | Lazy continuation and heading/code-block-inside-blockquote were proven in the prior attempt. |
| Code Spans | Low | — | Streaming inline toggle. |
| Emphasis | Medium | Markdown.pl backtracking | Simple emphasis streams cleanly; exact backtracking semantics may diverge on nested/contextual cases. |
| Strong Emphasis | Medium | Same as Emphasis | `**x**` / `__x__` pairing inherits the same risk class. |
| Inline Links | Low–Medium | Inline complexity | Bracket/paren state machine plus optional title. |
| Reference Links | Medium | Two-pass lookup | Requires collecting definitions on a first pass; O(n×m) lookup acceptable at fixture sizes. |
| Inline Images | Low–Medium | Same as Inline Links | Structurally equivalent to inline links with a leading `!`. |
| Reference Images | Medium | Same as Reference Links | Inherits the reference-link risks. |
| Auto Links | Divergence | Email autolink encoding | Plain `<a href="mailto:...">` replaces Markdown.pl's randomised entity obfuscation. See `docs/markdown/divergences.md`. |
| Backslash Escapes | Low | — | One-byte lookahead. |
| Inline HTML | Low–Medium | Tag detection accuracy | Passes raw HTML through; boundary detection has edge cases. |
| Ordered Lists | Medium | Loose-list exactness | Tight lists are tractable; loose-list buffering was a PARTIAL in the prior attempt. |
| Unordered Lists | Medium | Loose-list exactness | Same risk class as Ordered Lists. |
| Nested Lists | Medium–High | Loose-list × nesting | Two-level nesting is tractable; interaction with loose-list semantics is the highest-risk inline area. |
| HTML Blocks | Low–Medium | Block boundary detection | Distinguishing raw HTML blocks from inline HTML requires careful lookahead. |
| Ampersands and Angle Brackets | Low | — | Entity encoding at the right points of the pipeline. |
| Nested Block Structures | High | Exact nested output | Sentinel-framed recursive dispatch works mechanically; exact composition output was fragile in the prior attempt. |
| Markdown Documentation - Syntax | High | Combined ceiling risks | The largest fixture; exercises every feature including emphasis edge cases and deeply nested structures. |

## What Would Lower These Risks

- **For Medium inline risks (Emphasis, Reference Links):** a prototype of the buffered-scan path that can be diff'd against Markdown.pl on representative snippets before committing to the wider implementation.
- **For List risks:** an explicit design decision on whether to aim for loose-list exactness or accept a documented divergence (list risks would drop a tier under divergence).
- **For Nested Block High risks:** a prototype of the recursive-dispatch framing pattern that exercises blockquote-containing-list and blockquote-containing-code, diffed against the oracle.

These are prototypes architecture planning may choose to run, not commitments made here.

## What This Outlook Does Not Claim

- It does not predict pass/fail counts. The prior attempt's "~91–96% ceiling" estimate was tied to a specific implementation and does not transfer to a fresh build.
- It does not assume any fixture is "already implemented" because the prior implementation is not present.
- It does not commit to a fixture order or slice structure.
```

- [ ] **Step 2: Remove the superseded original**

```bash
git rm docs/research/shakedown-mdtest-fixture-matrix.md
```

- [ ] **Step 3: Commit**

```bash
git add docs/markdown/fixture-outlook.md
git commit -m "docs: replace fixture matrix with predictive fixture outlook"
```

---

## Phase 8 — Verification Plan

### Task 26: Write `verification-plan.md`

**Files:**
- Create: `docs/verification-plan.md`
- Consume (read): `.agent/restructure-verification-outputs.md` (from Phase 1)

- [ ] **Step 1: Write the plan with this structure**

Use Write tool to create `docs/verification-plan.md`:

```markdown
# Verification Plan

A claim-by-claim inventory of what is verified in this repository, what is retrospective evidence from a prior codebase, what is a prediction, and what remains open. Buckets A–E below.

Architecture planning reads this file to know which claims it can lean on and which it must treat as open.

## Bucket A — Already Verified Against This Interpreter

Claims probed against the local `shakespearelang` CLI (~30 claims) with evidence in `docs/spl/verification-evidence.md`. No action required. Read `docs/spl/reference.md` as the canonical statement of each verified behaviour; read `docs/spl/verification-evidence.md` for the probe command and observed output.

Summary of what is covered: pronoun stage-resolution rules, character value and stack initial state, off-stage value addressability, noun-phrase value semantics, integer-only arithmetic with truncation-toward-zero division, modulo sign behaviour, extended arithmetic operators and their negative-input error modes, stack behaviour (empty-pop failure, per-character independence), stage-operation errors, global-boolean overwrite by questions, act-local goto, and I/O behaviours (EOF returns, UTF-8 encoded `Speak your mind!`, invalid-code-point rejection, `Listen to your heart!` tokenisation quirks).

## Bucket B — Cheap Replays Run During This Restructure

Each replay was run once as part of the docs restructure. Results below capture the observed state of the environment at restructure time. Re-run before any architecture decision that depends on the specific number.

### B1 — Interpreter cold-start timing

- **Command:** `time shakespeare run <empty.spl>`
- **Expected range:** 17–26s cold, 2–3s warm (per prior measurements on this machine).
- **Observed:** [Paste captured output from `.agent/restructure-verification-outputs.md` replay 1.]
- **Disposition:** [Within range / drift flagged]

### B2 — Interpreter identity

- **Expected install path:** `~/.local/bin/shakespeare`.
- **Observed:** [Paste from replay 2.]
- **Disposition:** [Matches / differs — noted]

### B3 — Oracle present and version

- **Expected:** `~/markdown/Markdown.pl` exists and identifies as v1.0.1.
- **Observed:** [Paste from replay 3.]
- **Disposition:** [Confirmed / deviation recorded]

### B4 — Fixture count

- **Expected:** 23 `*.text` fixtures under `~/mdtest/Markdown.mdtest/`.
- **Observed:** [Paste from replay 4.]
- **Disposition:** [23 confirmed / deviation recorded]

### B5 — No randomness primitive in SPL grammar

- **Command:** `grep -iE 'random|rand|chance' shakespeare.ebnf`
- **Expected:** no matches.
- **Observed:** [Paste from replay 5.]
- **Disposition:** Confirms the email-autolink divergence in `docs/markdown/divergences.md`.

### B6 — Integer-only numeric grammar

- **Command:** `grep -iE 'float|double|decimal' shakespeare.ebnf`
- **Expected:** no numeric-type matches.
- **Observed:** [Paste from replay 6.]
- **Disposition:** Confirms the "integer only, no floats" claim in `docs/spl/reference.md`.

### B7 — AST-cache feasibility smoke

- **Purpose:** sanity-check the round-2 Exp-6 "cached-AST" claim has a plausible CLI surface in this interpreter.
- **Observed:** [Paste from replay 7.]
- **Disposition:** [CLI has parse-only / cache would live in a Python wrapper / other — recorded]

### B8 — Reference claim coverage sweep

- **Purpose:** every claim in `docs/spl/reference.md` should be either backed by a probe row, grammar-confirmed with an ebnf line, or explicitly labelled as a corrected project assumption.
- **Tally observed:** [Paste the P/G/C/? tally from replay 8.]
- **Unbacked (`?`) claims:** [List from replay 8, or "none" if the tally was clean.]
- **Disposition:** [Clean / open items promoted to bucket D]

## Bucket C — Retrospective Evidence (From Prior Codebase, Not Proven Here)

These claims describe measurements and behaviours from artifacts that are not present in this repository. Architecture planning should read them as prior-attempt evidence, not as facts about the current state. Full retrospective in `docs/prior-attempt/feasibility-lessons.md`.

- The ten feasibility experiment verdicts (five per round) and their specific numeric findings.
- Line counts: 4,311 lines (prior Slice 1), ~8,623 lines (projected full port), ~2,300 lines (projected port size under the chosen consolidation pattern).
- Per-test timings: 1.09s/test at 4,311 lines (round 1), ~0.30s/test at 8,623 lines (round 2 Exp-6 cached AST).
- Code-size reduction ratios: ~8% (consolidation alone), ~47% (consolidation + recursive dispatch).
- "Cast pressure" judgments and the six-character framing (now corrected — see bucket A and `docs/prior-attempt/feasibility-lessons.md`).
- The "~91–96% pass ceiling" estimate.
- "Already implemented in Slice 1" claims for specific block-level fixtures.

## Bucket D — Predictions (Open Items for Architecture Planning)

These are not facts to verify; they are open questions architecture planning must close. Source: `docs/markdown/fixture-outlook.md` and the open-items section of `docs/prior-attempt/architecture-lessons.md`.

- Fixture-by-fixture pass outcome for a fresh build.
- Loose-list exactness risk — acceptable divergence or must match?
- Markdown.pl emphasis-backtracking semantics — reproducible in a buffered scan?
- Exact nested blockquote+list composition output.
- Build order across risky fixture groups.
- Integration boundary between block and inline phases.
- Milestone sequence for chasing the `Markdown.mdtest` ceiling.
- Decision among prior Options A / B / C (or a fourth shape) for dispatcher architecture.
- Whether the AST-cache mechanism lives in the SPL file, a Python wrapper, or is not used at all.
- Any open items flagged by the B8 reference-claim coverage sweep.

## Bucket E — New Claims Introduced During This Restructure

Verified while writing the new docs; results above.

- Markdown.pl v1.0.1 version header present (see B3).
- 23 fixtures in `Markdown.mdtest` (see B4 and the full list in `docs/markdown/target.md`).

## Pending Validations Held Elsewhere

The style lexicon and codegen style guide have an existing, un-executed validation plan at `docs/superpowers/plans/2026-04-17-spl-style-guide-validation.md`. That plan covers:

- Legality validation for representative lexicon phrases and palettes.
- Runtime validation for representative codegen examples.
- Classification of codegen-guide statements by testability.

Until that plan is executed, treat claims in `docs/spl/style-lexicon.md` and `docs/spl/codegen-style-guide.md` as bucket A for inventory-backed items (where `docs/spl/lexicon-sources.md` cites a source) and as bucket D for items awaiting empirical validation.

## How to Re-Verify

To re-run any bucket-B replay, the commands are in the per-replay subsections above. Update observed output and disposition inline when re-verifying. Keep a dated trailer below any section that gets re-run.
```

- [ ] **Step 2: Paste the actual replay outputs into the template**

Open `.agent/restructure-verification-outputs.md`. For each B1–B8 section of the new
`verification-plan.md`, replace the `[Paste ...]` placeholder with the captured output
from the scratch file, and the `[Disposition ...]` placeholder with a one-line
disposition based on whether the observation matched the expectation.

- [ ] **Step 3: Confirm no `[Paste ...]` or `[Disposition ...]` placeholders remain**

```bash
grep -n '\[Paste\|\[Disposition\|\[Within\|\[Matches\|\[Confirmed\|\[23 confirmed\|\[CLI has\|\[Clean' docs/verification-plan.md || echo "(no placeholders — expected)"
```

If matches remain, resolve them.

- [ ] **Step 4: Commit**

```bash
git add docs/verification-plan.md
git commit -m "docs: add claim-bucketed verification plan"
```

---

## Phase 9 — Index and CLAUDE.md

### Task 27: Write `docs/README.md`

**Files:**
- Create: `docs/README.md`

- [ ] **Step 1: Write the index**

Use Write tool to create `docs/README.md`:

```markdown
# Shakedown Docs

Starting point for new agents. These docs support architecture planning and implementation for a Shakespeare Programming Language port of `Markdown.pl` v1.0.1 against the 23 `Markdown.mdtest` fixtures.

The repo root `CLAUDE.md` covers working conventions, tooling, and commit policy. This README maps the docs themselves.

## Reading Order for a New Agent

For an agent about to plan the Shakedown architecture:

1. [`lineage.md`](lineage.md) — one-minute lineage and why this repo exists.
2. [`markdown/target.md`](markdown/target.md) — the Markdown.pl surface Shakedown targets.
3. [`markdown/divergences.md`](markdown/divergences.md) — intentional differences from the oracle.
4. [`spl/reference.md`](spl/reference.md) — the SPL language reference (verified).
5. [`prior-attempt/architecture-lessons.md`](prior-attempt/architecture-lessons.md) — why the prior attempt stalled and which trade-offs surfaced.
6. [`prior-attempt/feasibility-lessons.md`](prior-attempt/feasibility-lessons.md) — what the prior experiments showed and which claims transfer to this repo.
7. [`markdown/fixture-outlook.md`](markdown/fixture-outlook.md) — risk tiers for a fresh build.
8. [`verification-plan.md`](verification-plan.md) — what is verified, what is retrospective, what is predicted, what is open.

## Directory Map

| Path | Purpose |
|---|---|
| `lineage.md` | Short lineage of the Shakedown / Snarkdown / Quackdown triad. |
| `verification-plan.md` | Claim inventory by bucket (A–E). |
| `spl/` | SPL language reference, style, codegen policy, and verification evidence. |
| `spl/reference.md` | Verified SPL semantics. |
| `spl/style-lexicon.md` | Legal expressive vocabulary and phrase patterns. |
| `spl/codegen-style-guide.md` | Implementation policy for recurring value phrases. |
| `spl/verification-evidence.md` | Probe programs and observed interpreter behaviour. |
| `spl/lexicon-sources.md` | Grammar and example-attested sources for lexicon entries. |
| `spl/probes/` | Runnable SPL probe programs cited by `verification-evidence.md`. |
| `markdown/` | The target behaviour. |
| `markdown/target.md` | Markdown.pl v1.0.1 surface and test fixtures. |
| `markdown/divergences.md` | Intentional divergences from the oracle. |
| `markdown/fixture-outlook.md` | Predictive risk tiers for each of the 23 fixtures. |
| `prior-attempt/` | Retrospective evidence from the earlier SPL attempt. |
| `prior-attempt/feasibility-lessons.md` | Consolidated feasibility findings from round 1 and round 2. |
| `prior-attempt/architecture-lessons.md` | Consolidated architecture memo and the A/B/C options. |
| `archive/` | Historical artifacts preserved for context, not current guidance. |
| `superpowers/specs/` | Design specs for sub-projects within Shakedown. |
| `superpowers/plans/` | Implementation plans for sub-projects. |

## Canonical Flow of Truth

- **Legality and verified semantics:** `spl/reference.md` (evidence: `spl/verification-evidence.md`).
- **Expressive vocabulary:** `spl/style-lexicon.md` (sources: `spl/lexicon-sources.md`).
- **Implementation policy for constants:** `spl/codegen-style-guide.md`.
- **Oracle behaviour:** `markdown/target.md` + `Markdown.pl` itself.
- **What is proven vs retrospective vs open:** `verification-plan.md`.

## What This Docs Set Does Not Do

- It does not commit to a Shakedown architecture. Architecture planning is the next step after reading these docs.
- It does not treat the prior attempt's feasibility verdicts as facts about this repository. They are retrospective evidence from a prior checkout; see `prior-attempt/feasibility-lessons.md` and `verification-plan.md` bucket C.
- It does not include a loop prompt. The replacement for the archived `docs/prompt-shakedown.md` will be written once architecture planning decides what a new agent should load.
```

- [ ] **Step 2: Confirm every relative link resolves**

```bash
# Extract markdown links and check each target exists
grep -oE '\[[^]]+\]\(([^)]+)\)' docs/README.md | sed -E 's/.*\(([^)]+)\)/\1/' | while read link; do
  target="docs/$link"
  if [ -e "$target" ]; then
    echo "OK: $target"
  else
    echo "BROKEN: $target"
  fi
done
```

Expected: every line starts with `OK:`. If any `BROKEN:` line appears, the restructure missed a file; resolve before committing.

- [ ] **Step 3: Commit**

```bash
git add docs/README.md
git commit -m "docs: add docs/README.md index"
```

### Task 28: Update `CLAUDE.md` reference-materials section

**Files:**
- Modify: `CLAUDE.md` (lines 51, 57, 95–102, 144)

- [ ] **Step 1: Review the current references**

```bash
grep -n "docs/research\|docs/prompt-shakedown" CLAUDE.md
```

- [ ] **Step 2: Edit the Reference materials list (around line 95)**

Replace the current block:

```
- `~/markdown/Markdown.pl` — oracle; the thing being ported
- `~/mdtest/Markdown.mdtest/` — 23 test fixtures (.text input, .xhtml/.html expected)
- `docs/research/shakedown-spl-reference.md` — SPL language reference (critical for implementation)
- `docs/research/shakedown-mdtest-architecture-memo.md` — prior-attempt build shape (evidence, not prescription)
- `docs/research/shakedown-mdtest-fixture-matrix.md` — fixture-by-fixture pass/fail predictions
- `docs/research/shakedown-divergences.md` — intentional divergences from Markdown.pl
- `docs/research/feasibility-summary.md`, `feasibility-summary-2.md` — SPL feasibility experiments and verdicts
- `docs/research/spl-act-architecture.md` — options considered for SPL act/dispatch layout
- `docs/research/slow-machine-spl-workflow.md` — interpreter timing measurements and workflow implications
- `docs/research/` — full provenance docs from the earlier Shakedown and Quackdown work
- `docs/lineage.md` — project history and lineage context
- `docs/prompt-shakedown.md` — agent prompt used by `run-loop`
```

with:

```
- `~/markdown/Markdown.pl` — oracle; the thing being ported
- `~/mdtest/Markdown.mdtest/` — 23 test fixtures (.text input, .xhtml/.html expected)
- `docs/README.md` — entry point for the docs set
- `docs/spl/reference.md` — SPL language reference (verified)
- `docs/spl/verification-evidence.md` — probe programs and observed interpreter behaviour
- `docs/spl/style-lexicon.md` — legal expressive vocabulary
- `docs/spl/codegen-style-guide.md` — implementation policy for recurring value phrases
- `docs/markdown/target.md` — Markdown.pl v1.0.1 target surface
- `docs/markdown/divergences.md` — intentional divergences from the oracle
- `docs/markdown/fixture-outlook.md` — predictive risk tiers for each of the 23 fixtures
- `docs/prior-attempt/architecture-lessons.md` — why the prior attempt stalled and which trade-offs surfaced
- `docs/prior-attempt/feasibility-lessons.md` — consolidated feasibility findings; which claims transfer
- `docs/verification-plan.md` — claim inventory (verified / retrospective / predicted / open)
- `docs/lineage.md` — short lineage context
- `docs/archive/` — historical artifacts; prefer live docs unless specifically checking history
```

- [ ] **Step 3: Edit the inline reference on line 51**

Replace:

```
The feasibility research (`docs/research/`) is evidence from the prior attempt, not a prescription
```

with:

```
The retrospective research (`docs/prior-attempt/`) is evidence from the prior attempt, not a prescription
```

- [ ] **Step 4: Edit the inline reference on line 57**

Replace:

```
See `docs/research/slow-machine-spl-workflow.md` and `docs/research/feasibility-summary.md`.
```

with:

```
See `docs/archive/slow-machine-spl-workflow.md` and `docs/prior-attempt/feasibility-lessons.md`.
```

- [ ] **Step 5: Edit the inline reference on line 144**

Replace:

```
Every fixture either passes or is documented as an accepted divergence in `docs/research/shakedown-divergences.md` | `1.0.0` |
```

with:

```
Every fixture either passes or is documented as an accepted divergence in `docs/markdown/divergences.md` | `1.0.0` |
```

- [ ] **Step 6: Confirm no `docs/research` or legacy `docs/prompt-shakedown.md` references remain in `CLAUDE.md`**

```bash
grep -n "docs/research\|docs/prompt-shakedown" CLAUDE.md || echo "(no matches — expected)"
```

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md reference paths to new docs layout"
```

---

## Phase 10 — Cleanup and Final Verification

### Task 29: Remove the empty `docs/research/` directory

**Files:**
- Remove: `docs/research/` (should now be empty)

- [ ] **Step 1: Confirm it is empty**

```bash
ls -la docs/research/ 2>&1
```

Expected: directory is empty (only `.` and `..`), or does not exist.

- [ ] **Step 2: If the directory still exists, remove it**

```bash
rmdir docs/research/ 2>/dev/null || true
```

Git does not track empty directories, so no `git rm` is needed beyond the prior `git mv` operations already staged/committed.

- [ ] **Step 3: Confirm removal**

```bash
ls docs/research 2>&1 || echo "(does not exist — expected)"
```

### Task 30: Repo-wide stale-link sweep

**Files:**
- Touch: any doc file that still references `docs/research/`

- [ ] **Step 1: Grep the entire repo for `docs/research` references**

```bash
grep -rn "docs/research" docs/ CLAUDE.md AGENTS.md README.md pyproject.toml 2>/dev/null | grep -v '^docs/archive/' || echo "(no matches outside archive — expected)"
```

Expected: only `docs/archive/` entries (if any) retain `docs/research` strings in their
historical content — that is fine. Everywhere else should be clean.

- [ ] **Step 2: If matches exist outside `docs/archive/`, fix them**

For each hit, use Edit to replace with the new path per the disposition table in
`docs/superpowers/specs/2026-04-17-docs-restructure-design.md`. Commit with message
`docs: fix stale docs/research references`.

- [ ] **Step 3: Grep for `tmp-spl-probes` the same way**

```bash
grep -rn "tmp-spl-probes" docs/ CLAUDE.md AGENTS.md README.md 2>/dev/null | grep -v '^docs/archive/' || echo "(no matches — expected)"
```

- [ ] **Step 4: Grep for old frozen-file basenames outside archive**

```bash
grep -rn 'shakedown-spl-reference\.md\|shakedown-spl-style-lexicon\.md\|shakedown-spl-codegen-style-guide\.md\|shakedown-divergences\.md\|shakedown-mdtest-fixture-matrix\.md\|shakedown-mdtest-architecture-memo\.md\|shakedown-before-design\.md\|spl-act-architecture\.md\|feasibility-summary\.md\|feasibility-summary-2\.md\|shakedown-spl-feasibility-assumption-corrections\.md\|project-history\.md\|slow-machine-spl-workflow\.md\|spl-feasibility-resumption-context\.md' docs/ CLAUDE.md AGENTS.md 2>/dev/null | grep -v '^docs/archive/' || echo "(no matches — expected)"
```

- [ ] **Step 5: If any fixes were required, commit them**

```bash
git add -u
git commit -m "docs: fix stale filename references across the doc tree"
```

### Task 31: Final structure verification

**Files:** none

- [ ] **Step 1: Confirm the target structure exists**

```bash
find docs -maxdepth 3 -type f -name '*.md' | sort
find docs/spl/probes -name '*.spl' | wc -l
```

Expected `find ... *.md` output must include exactly these files (order may differ):

```
docs/README.md
docs/archive/project-history.md
docs/archive/prompt-shakedown.md
docs/archive/slow-machine-spl-workflow.md
docs/archive/spl-feasibility-resumption-context.md
docs/lineage.md
docs/markdown/divergences.md
docs/markdown/fixture-outlook.md
docs/markdown/target.md
docs/prior-attempt/architecture-lessons.md
docs/prior-attempt/feasibility-lessons.md
docs/spl/codegen-style-guide.md
docs/spl/lexicon-sources.md
docs/spl/reference.md
docs/spl/style-lexicon.md
docs/spl/verification-evidence.md
docs/superpowers/plans/2026-04-17-docs-restructure.md
docs/superpowers/plans/2026-04-17-spl-codegen-style-guide.md
docs/superpowers/plans/2026-04-17-spl-reference-verification.md
docs/superpowers/plans/2026-04-17-spl-style-guide-validation.md
docs/superpowers/plans/2026-04-17-spl-style-lexicon.md
docs/superpowers/specs/2026-04-17-docs-restructure-design.md
docs/superpowers/specs/2026-04-17-spl-codegen-style-guide-design.md
docs/superpowers/specs/2026-04-17-spl-reference-verification-design.md
docs/superpowers/specs/2026-04-17-spl-style-guide-validation-design.md
docs/superpowers/specs/2026-04-17-spl-style-lexicon-design.md
docs/verification-plan.md
```

Probes count must be 18.

- [ ] **Step 2: Confirm the three frozen-file bodies are unchanged except for cross-ref edits**

Diff each frozen file against its pre-move state using git:

```bash
git log --follow --oneline docs/spl/reference.md | head -5
git log --follow --oneline docs/spl/style-lexicon.md | head -5
git log --follow --oneline docs/spl/codegen-style-guide.md | head -5
```

Inspect each move-commit's diff and confirm only cross-reference path lines changed
(3 edits for `reference.md`, 2 for `style-lexicon.md`, 3 for `codegen-style-guide.md`).
If any commit shows extra body changes, that is a regression — fix before proceeding.

- [ ] **Step 3: Confirm the tests still pass**

```bash
uv run pytest
```

Expected: existing tests pass unchanged. The restructure touches docs only.

- [ ] **Step 4: Confirm `run-loop` is still self-consistent**

```bash
grep -n 'prompt-shakedown' run-loop
```

If the run-loop default prompt path is now broken (points at
`docs/prompt-shakedown.md` which is archived), this is expected — the replacement
prompt is explicitly out of scope for this restructure. Leave a note in the final
commit message body noting the known dangling default so the next work item picks it
up.

### Task 32: Clean up scratch files and commit the final state

**Files:**
- Remove: `.agent/restructure-verification-outputs.md`
- Remove: `/tmp/empty-cold-start.spl`, `/tmp/fixture-names.txt`, `/tmp/ref-hash-pre`, `/tmp/ref-hash-post` (best effort)

- [ ] **Step 1: Remove the scratch verification file**

```bash
rm -f .agent/restructure-verification-outputs.md /tmp/empty-cold-start.spl /tmp/fixture-names.txt /tmp/ref-hash-pre /tmp/ref-hash-post
```

- [ ] **Step 2: Confirm `.agent/` either is empty or holds only the run-loop state file**

```bash
ls -la .agent/ 2>&1
```

Expected: `.agent/run-loop-state.json` if run-loop has been used; otherwise empty.
Do not commit anything under `.agent/`; per repo convention it is local state.

- [ ] **Step 3: Final git status check**

```bash
git status --short
```

Expected: working tree is clean.

- [ ] **Step 4: Log the restructure as done**

No commit; the restructure is complete. Architecture planning can now start from
`docs/README.md`.

---

## Self-Review Checklist

Before handing off:

- [ ] Every file in the "Target Structure" of the spec is present under `docs/`.
- [ ] `docs/research/` does not exist.
- [ ] No `docs/research/` reference exists outside `docs/archive/`.
- [ ] The three frozen files have exactly the cross-reference edits called out and nothing else.
- [ ] `docs/verification-plan.md` has no `[Paste ...]` or `[Disposition ...]` placeholders.
- [ ] `docs/README.md` links all resolve to real files.
- [ ] `CLAUDE.md` reference list points at the new layout.
- [ ] `uv run pytest` passes.
- [ ] `.agent/restructure-verification-outputs.md` has been removed.
- [ ] A note has been left about the dangling `run-loop` default prompt path if applicable.
