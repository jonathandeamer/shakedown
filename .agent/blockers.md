# Active blockers

- BLOCK: Task 2L Step 2d (candidate capture + replay) pure-op bodies unfinished.
  `USE_ACT1_REF_INTRINSIC` remains False; `tests/test_act1_references.py` stays at
  the Step 2c baseline (**2 passed, 6 failed** — defs still in body). Working tree
  `src_ir/act1_ref_pure.py` restored to the shipped 2c line machine (no partial 2d
  IR left in place). Literary/validate unchanged.

  Implementation findings (2026-07-20, grok-implement) for the next Step 2d agent:

  1. **Verified algorithm (Python sim, not IR):** Puck-centric capture with
     `capture_len` counter (no mid-stack `CAPTURE_START` removal) matches
     `strip_reference_definitions` **body** for simple / lead-spaces / defs+para /
     four-space / invalid / case / angle. Next-line titles intentionally left in
     body (2d allows title_nl / table tests to stay red). REPLAY is free
     (`capture_len = 0`; glyphs already on Puck). DROP pops exactly `capture_len`
     glyphs from Puck.

  2. **Discipline that fits 26 labels:** Mode take-loops only **take**. Transitions
     that already hold the glyph in `Hecate` push + `rem--` + set mode +
     `HECATE_REF_ENCODE` (`capture_len++` with `companion=HORATIO`) + dispatch.
     Point **all** dest modes (URL_WS / ANGLE / BARE / AFTER / TBODY) at **one**
     shared take-loop that branches on `Rosalind.value` — do not burn one label
     per dest mode. Colon-match must push `:` in a transition scene that is
     **never** the MWS dispatch target (or push `:` inline in COLON before INC).

  3. **Do not dual-purpose labels across scan vs trail vs DROP.** Trail reverse
     drain and DROP need dedicated end states (FINISH length handoff;
     REVERSE = Puck→Hecate only after trail pad). Fail paths share one
     `len++ → REPLAY` bridge (`TITLE_GUARD` pattern from 2c).

  4. **Stage rules still absolute (A4.1):** every `let`/`push`/`pop` target on
     stage; take-idiom parks rem in `Puck.value`; `pop` clobbers value; one entry
     stage pair per label.

  5. **Not a plan gap yet:** A1/A4 label pool and A4.3 capture model are sufficient
     if (2)–(3) are followed. Do not invent a 27th title; if a complete map truly
     needs more bridge labels after a counted ledger, escalate `- BLOCK[plan]:`.
     Do not re-enable `USE_ACT1_REF_INTRINSIC` to green the suite.

  6. **Evidence gate (unchanged, A4.7):**
     ```bash
     uv run pytest tests/test_act1_references.py -q
     uv run pytest tests/test_splc_validate.py tests/test_splc_generated_fragments.py tests/test_literary_compliance.py -q
     uv run python -m scripts.splc && uv run python scripts/assemble.py
     git diff --exit-code -- src/*.spl shakedown.spl debug/
     ```
     Step 2d success: `test_simple_definition_*`, `test_up_to_three_leading_spaces_*`,
     `test_defs_plus_paragraph_*` pass (body stripped); case/angle/title_nl may stay
     red on empty Rosalind table until 2e.

Next unchecked step: **Task 2L Step 2d** (A4.6).
`USE_ACT1_REF_INTRINSIC` remains False.
