# Active blockers

- BLOCK[plan]: Task 4 Step 2c (`whitespace_only_blank_boundary`) cannot meet its evidence gate under design Amendment A16 alone. A16's authorized `PASS_PARA_WS_*` machine is confined to the second-pass paragraph scanner (`pop(MACBETH)` on the already-staged stream, no `_read()`/Hecate). That machine correctly closes a paragraph on a spaces-only line (witness `Para:\n    \n` → single `PARA` matching the oracle), but it cannot emit `CODE_BLOCK`.

  Minimal failing witness (also the plan's contract): `Para:\n    \n    code line\n`.

  Observed with A16 PARA-only WIP:
  - decoded stream: `[PARA("Para:"), PARA("    code line")]`
  - fast/release HTML: `<p>Para:</p>\n\n<p>    code line</p>\n`
  - oracle: `<p>Para:</p>\n\n<pre><code>code line\n</code></pre>\n`

  Control that already works (bare blank, no spaces on the blank line): `Para:\n\n    code line\n` → `[PARA, CODE_BLOCK]` and byte-identical HTML. Bare blank is handled in the first-pass raw path: `PASS_LISTS_RAW_AFTER_NEWLINE` sees a second `NEWLINE`, goes to `PASS_LISTS_RAW_BLANK`, then `PASS_LISTS_BLOCK_START` → `PASS_CODE_GATE` emits `CODE_BLOCK`. A spaces-only blank never takes that path because `PASS_LISTS_RAW_AFTER_NEWLINE` treats a leading space as raw continuation (`goto PASS_LISTS_RAW_GLYPH`), so the following indented line is still character data inside one raw region. The PARA pass can only wrap that residual region as another `PARA`; it has no authorized way to mint a `CODE_BLOCK` token.

  Same root cause as Syntax offset 22422 (`And then define the link:\n\t\n\t[Daring Fireball]: …` after Act I detab).

  What A16/A18 already authorize is insufficient for the gate: eight `PASS_PARA_WS_*` labels on Macbeth's PARA stack. What is needed is a first-pass whitespace-only blank at `PASS_LISTS_RAW_AFTER_NEWLINE` (buffer/classify spaces; on terminator discard spaces and `PASS_LISTS_RAW_BLANK` so `BLOCK_START` can open `CODE_BLOCK`; on trailing content reverse-replay spaces and continue raw). That is the same algorithm as A16 but on Hecate/`_read()`, and it needs either (a) authorization to implement that algorithm with the existing A16 eight labels under first-pass pairs (Hecate+Puck etc.), (b) a new first-pass label pool, or (c) explicit authorization to overload the existing `PASS_LISTS_RAW_*` scenes with Horatio mode flags and no new labels. Soft-break control `Para:\n    still para\n` must stay one paragraph.

  Working tree retains the prior rate-limited A16 PARA WIP (tests, literary TOML, `PASS_PARA_WS_*` IR, generated SPL) uncommitted; do not discard. Step 2c stays unchecked until a planning amendment authorizes the first-pass half.
