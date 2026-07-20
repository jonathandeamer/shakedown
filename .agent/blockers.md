# Active blockers

- BLOCK: Task 2L Step 2 pure-op Act I strip unfinished under Amendment A3. `USE_ACT1_REF_INTRINSIC` remains False; `tests/test_act1_references.py` is red (6 failed, 2 passed — defs still in body / empty Rosalind table). Scaffold only: `src_ir/act1_ref_pure.py` holds the A1.3 goto lattice wired from `src_ir/act1.py` via `build_ref_scenes()`; literary/validate green. Full pure-op bodies did not reach the Step 2 evidence gate this iteration. Not a plan gap — continue Step 2 against A3.1–A3.6 and `scripts/splc/act1_ref_strip.py`. Do not re-enable the Act I intrinsic to “fix” green.

  Implementation findings (2026-07-20, grok-implement) for the next Step 2 agent:

  1. **Two-character write rule is absolute.** `participants()` counts every `let`/`push`/`pop`/`read_char` target. A scene with `companion=HORATIO` may not `let(PUCK, …)` even to clear `pv`. Off-stage `val(X)` reads are fine (third-person branch questions). Plan A3.1’s register map is correct for *storage*, but each *write* still requires that character on stage.

  2. **`pop` clobbers value.** `remaining` cannot stay in `Hecate.value` across `pop(HECATE)`. Proven take idiom with `companion=PUCK`: `let(PUCK, val(HECATE))` (save rem) → `pop(HECATE)` (glyph) → process → `let(HECATE, sub(val(PUCK), const(1)))`. Do not `let(PUCK, const)` for a push payload while rem lives in `Puck.value`; use `push(PUCK, expr)` with a `Const`/`BinOp` expr (e.g. `push(PUCK, sub(const(0), const(7)))` for `CAPTURE_START`) so rem survives.

  3. **Negative sentinels need no new literary keys.** `const(-7)` fails `value_phrase` (no `vneg7`). Build as `sub(const(0), const(7))` etc. for `RECORD_END`/`CAPTURE_START`/`KEPT_START` (`-6`/`-7`/`-8`).

  4. **REPLAY cross-stack is the hard part.** Capture on `Horatio.stack` + kept on `Puck.stack` cannot flush in one two-character scene. Prefer **Puck-centric capture**: `Puck.stack = [KEPT_START, kept…, CAPTURE_START, cap…]` so REPLAY is “drop `CAPTURE_START`” on one stack. `Horatio.value` keeps `ov` / phase only. Fold pops capture region onto Rosalind (above table) for A3.4 reverse-scan, then restores.

  5. **OPEN init bridge.** After normalize reverse, length sits on `Horatio.stack` and `Horatio.value==0`. `OPEN` (Horatio): `pop` length → `Hecate=rem`, `ov=0` → goto Puck scene to `push(KEPT_START)`. Scaffold’s `FOUR_SPACE` is the natural init bridge; fourth-leading-space reject can stay inlined in lead-SP handling (oracle-identical) so `FOUR_SPACE` need not carry that semantic.

  6. **One label = one companion.** Dual-entry modes (init vs continue) must use inverted non-exhaustive branches (`gt(ov,0) → other_label` + fallthrough init) or separate authorized labels — never `branch(…, then=self)` without state change (infinite loop / step limit). `URL_GUARD` is the only spare authorized for promotion (url_ws_nl per A3.2); promote in `src/10-act1-literary.toml` when first referenced.

  7. **Recall keys.** `pop(HECATE)` with companion C uses C’s recall keys. Rosalind has an empty `[characters.rosalind.recall]` — do not `pop(HECATE)` with `companion=ROSALIND` without a plan amendment for new recall prose. Reuse existing keys (`cauldron_dreg`, `kept_measure`, `held_label_glyph`, etc.).

  8. **FINISH / ACT_I_DONE.** `ACT_I_DONE` does `pop(HORATIO)`. Intrinsic leaves `Horatio.stack=[len]` and `values[HORATIO]=len`. Pure FINISH must push length and leave body on Hecate with top=first glyph (`list(reversed(kept))` semantics). Trailing-NL policy: strip all trailing NLs, append exactly two.

  9. **Evidence gate (unchanged):**
     ```bash
     uv run pytest tests/test_act1_references.py -q
     uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
     uv run python -m scripts.splc && uv run python scripts/assemble.py
     git diff --exit-code -- src/*.spl shakedown.spl debug/
     ```
     Keep `USE_ACT1_REF_INTRINSIC = False` until Step 3.
