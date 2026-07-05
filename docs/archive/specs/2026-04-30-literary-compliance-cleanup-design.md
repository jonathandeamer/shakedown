# Literary Compliance Cleanup Design

## Goal

Bring the current production SPL surface into conformance with the live
literary, lexicon, and codegen-style guidance without redesigning future
generation yet.

This pass fixes the material that already exists. It does not rewrite historical
probe programs, and it does not teach the assembler or byte-literal generator a
new literary data model. Future prevention is a separate follow-up design after
the current production text is clean.

## Scope

Production files in scope:

- `src/00-preamble.spl`
- `src/10-act1-preprocess.spl`
- `src/20-act2-block.spl`
- `src/30-act3-span.spl`
- `src/40-act4-emit.spl`
- `src/literary.toml`
- generated `shakedown.spl`
- tests that validate the production files above

Out of scope:

- `docs/spl/probes/**`
- older prototype fixtures and retired experiment programs
- broad generator or assembler redesign
- changing Markdown behavior or expanding fixture support

The implementation edits source fragments first, then runs
`scripts/assemble.py` so `shakedown.spl` remains assembled output.

## Source Of Truth

For this cleanup, `src/*.spl` remains the hand-edited production source. The
assembled `shakedown.spl` is regenerated from those fragments and should not be
edited as the only copy of a change.

`src/literary.toml` becomes the audit ledger for current literary surfaces. It
must contain the production literary data that already exists after cleanup:

- the locked play title
- the four locked act titles
- current scene titles keyed by symbolic scene label
- per-character soft-variation pools
- per-character Recall pools
- stable utility surfaces already present
- tags for each currently used iconic or dramatic moment; if the current
  production source keeps none, the TOML records empty `iconic_moments` and
  `dramatic_moments` tables

The TOML does not need to pre-author future slices. It only needs complete
coverage for current production surfaces.

## Numeric Prose Policy

The cleanup preserves exact SPL values while improving phrase surfaces.

Rules:

- `nothing` remains canonical where zero is Critical.
- Critical dispatch values stay consistent across speakers.
- Non-Critical utility values use the current speaker's palette unless the
  phrase participates in a comparison or arithmetic form where substitution
  would change sign, magnitude, or parser acceptance.
- No production noun-phrase atom may exceed the literary spec's atom cap.
- Production source must not contain `a big big big big cat` or worse.
- Compound expressions may remain long when needed, but their component atoms
  should stay short and should avoid monotonous high-count `big ... cat`
  phrasing.

If replacing a phrase risks changing semantics, behavior wins. The phrase stays
mechanically plain, and the exception is documented in the implementation notes
or test name.

## Literary Surface Policy

Current titles, Recall text, and soft-variation choices follow
`docs/spl/literary-spec.md`.

Required corrections:

- play title is exactly `Shakedown: A Most Excellent Tragicomedy of Glyph and Line.`
- the four act titles are exactly the locked `Wherein ...` titles from
  `docs/spl/literary-spec.md` section 7.1
- every production scene title is represented in `src/literary.toml`
- scene titles remain accurate to the scene's mechanical work
- every production Recall phrase is represented in the speaker's Recall pool
- soft comparatives stay inside the speaker's pool where grammar permits
- Prospero uses his `We shall ...` goto voice where grammar permits
- Hecate's backward motion uses her stronger return voice where grammar permits
- pronoun choices follow character policy where doing so is behavior-neutral

The cleanup should prefer precise, legal, characterful prose over iambic flavor.
The drop-first rule applies whenever style conflicts with grammar legality,
semantic correctness, or technical clarity.

## Layout Policy

Production SPL moves toward the Folio-style source layout in
`docs/spl/literary-spec.md` section 7.7:

- speaker names on their own line after a parser smoke test proves the layout
  is accepted by `shakespeare`
- one blank line between events
- two blank lines between scenes
- three blank lines between acts
- long value expressions split at `the sum of ... and ...` boundaries after a
  parser smoke test proves the layout is accepted by `shakespeare`

Layout must not change runtime behavior. The implementation first verifies the
candidate layout with a minimal SPL smoke program before applying it to
production fragments. If a layout form fails that smoke test, production keeps
the existing parser-safe form and the test suite records the unsupported layout
as an explicit exception.

## Validation Strategy

Tests should lock objective rules, not subjective taste.

Add or update tests that verify:

- locked play title and act titles appear in `shakedown.spl`
- production scene titles have matching entries in `src/literary.toml`
- production Recall phrases are present in the relevant character Recall pool
- production source has no noun-phrase atom over the atom cap
- production source has no `a big big big big cat` or worse
- `src/literary.toml` includes the new current-surface sections
- Folio layout invariants hold for every layout form validated by the smoke
  program; unsupported forms are named in one explicit exception test

Behavioral gates remain required:

- `env UV_CACHE_DIR=/tmp/uv-cache uv run pytest`
- `env UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/strict_parity_harness.py 'Amps and angle encoding'`
- `env UV_CACHE_DIR=/tmp/uv-cache uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q`
- `bash -n shakedown`
- `env UV_CACHE_DIR=/tmp/uv-cache uv run pyright`
- relevant `ruff` checks for touched Python tests

## Follow-Up

After this cleanup lands, write a separate prevention design. That design should
decide how the assembler and codegen consume `src/literary.toml`, so future
generated production SPL cannot reintroduce inline invented prose or monotonous
numeric phrases.
