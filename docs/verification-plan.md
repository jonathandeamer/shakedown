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
- **Observed:**
  ```
  # first run
  real	0m0.105s
  user	0m0.089s
  sys	0m0.010s

  # second run
  real	0m0.100s
  user	0m0.079s
  sys	0m0.020s
  ```
- **Disposition:** Not a drift — the probe used a minimal `[Exeunt]`-only play, which measures interpreter *startup*, not the per-run execution cost of a ~4k-line program. The documented 17–26s figure was measured against a real-sized SPL file. Architecture planning should re-measure against a realistically sized SPL program before leaning on a specific per-run figure.

### B2 — Interpreter identity

- **Expected install path:** `~/.local/bin/shakespeare`.
- **Observed:**
  ```
  $ which shakespeare
  /home/ec2-user/.local/bin/shakespeare

  $ shakespeare --version
  Error: no such option: --version
  ```
  Identity confirmed via `which` and the first lines of `--help` (subcommands: `console`, `debug`, `run`).
- **Disposition:** Matches — `~/.local/bin/shakespeare` is the path documented in `docs/spl/reference.md`. The CLI has no `--version` flag; not a drift, the docs never claimed one.

### B3 — Oracle present and version

- **Expected:** `~/markdown/Markdown.pl` exists and identifies as v1.0.1.
- **Observed:**
  ```
  $VERSION = '1.0.1';
  # Tue 14 Dec 2004
  ```
- **Disposition:** Confirmed.

### B4 — Fixture count

- **Expected:** 23 `*.text` fixtures under `~/mdtest/Markdown.mdtest/`.
- **Observed:** `ls ~/mdtest/Markdown.mdtest/*.text | wc -l` → `23`.
- **Disposition:** 23 confirmed. Full list in `docs/markdown/target.md`.

### B5 — No randomness primitive in SPL grammar

- **Command:** `grep -iE 'random|rand|chance' ~/shakespearelang/shakespearelang/shakespeare.ebnf`
- **Expected:** no matches.
- **Observed:**
  ```
  "granddaughter" |
  "grandfather" |
  "grandmother" |
  "grandson" |
  "Miranda" |
  ```
  Hits are substring false-positives in character names (`rand` inside `granddaughter`, `grandfather`, `grandmother`, `grandson`, `Miranda`). None are randomness tokens.
- **Disposition:** Confirms the email-autolink divergence in `docs/markdown/divergences.md`. Future re-runs should use word-boundary matching (`-w`) to avoid the false positives.

### B6 — Integer-only numeric grammar

- **Command:** `grep -iE 'float|double|decimal' ~/shakespearelang/shakespearelang/shakespeare.ebnf`
- **Expected:** no numeric-type matches.
- **Observed:** no matches.
- **Disposition:** Confirms the "integer only, no floats" claim in `docs/spl/reference.md`.

### B7 — AST-cache feasibility smoke

- **Purpose:** sanity-check the round-2 Exp-6 "cached-AST" claim has a plausible CLI surface in this interpreter.
- **Observed:** `shakespeare --help` lists only three commands: `console`, `debug`, `run`. There is no parse-only subcommand. `shakespeare run` accepts `--input-style` and `--output-style` but no separate parse step.
- **Disposition:** Any AST-caching strategy would live in a Python wrapper, not the CLI. This is a useful input for architecture planning.

### B8 — Reference claim coverage sweep

- **Purpose:** every claim in `docs/spl/reference.md` should be either backed by a probe row, grammar-confirmed with an ebnf line, or explicitly labelled as a corrected project assumption.
- **Tally observed:**

  | Category | Count |
  |---|---|
  | P (probed) | ~32 |
  | G (grammar) | ~17 |
  | C (corrected assumption) | 1 |
  | ? (unbacked) | 0 |

- **Unbacked (`?`) claims:** none. Every labelled claim in the reference is covered by either a probe row in `docs/spl/verification-evidence.md`, a rule in `~/shakespearelang/shakespearelang/shakespeare.ebnf`, or an explicit `Corrected project assumption` label.
- **Disposition:** Clean. No items need to be promoted to bucket D on this pass.

### B9 — Current oracle-stub mdtest contract pass

- **Command:** `uv run pytest tests/test_mdtest.py -q`
- **Observed:**
  ```
  23 passed in 1.44s
```
- **Disposition:** Confirmed only for the current `./shakedown` oracle stub. This proves the repo contract and fixture wiring, not SPL implementation coverage. Do not cite this as evidence that `./shakedown-dev` or `shakedown.spl` handles the full mdtest corpus.

### B10 — Pre-design SPL mechanics probes

- **Command:** `uv run pytest tests/test_pre_design_probes.py -q`
- **Observed:**
  ```
  3 passed in 2.93s
  ```
- **Disposition:** Confirms the SPL mechanics for stack-backed reference lookup, delayed setext line commitment, and nested list-state push/pop. These probes do not implement full Markdown features; they are architecture evidence for the detailed spec.

### B11 — Emphasis backtracking review

- **Commands:**
  - `sed -n '1030,1048p' ~/markdown/Markdown.pl`
  - `printf 'One *foo **bar* baz** here.\n' | perl ~/markdown/Markdown.pl`
  - `printf 'One *foo **bar* baz** here.\n' | ./shakedown-dev`
- **Observed:** Markdown.pl performs `_DoItalicsAndBold` as two substitutions: strong delimiters first, then emphasis delimiters over the modified buffer. The oracle emits `<p>One <em>foo <strong>bar</em> baz</strong> here.</p>`. The P2 prototype emits `<p>One <em>foo </em><em>bar</em> baz<em></em> here.</p>`.
- **Disposition:** The XFAIL is a limitation of the P2 single-toggle prototype, not a forced divergence. A parity implementation should model Markdown.pl's strong-before-emphasis order.

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

- Build order across risky fixture groups.
- Integration boundary between block and inline phases.
- Milestone sequence for chasing the `Markdown.mdtest` ceiling.
- Decision among prior Options A / B / C (or a fourth shape) for dispatcher architecture.
- Whether the AST-cache mechanism lives in the SPL file, a Python wrapper, or is not used at all.
- Production implementation of reference lookup, setext line buffering, and list looseness/nesting state. The mechanics are covered by B10, but feature-level Markdown coverage still belongs to implementation.
- Any remaining policy questions around list exactness. Emphasis backtracking is now classified as a two-pass implementation requirement unless deliberately scoped out.

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
