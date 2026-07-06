# Spike A P1 — Tokenized Stream + Dispatcher Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the tokenized inter-act stream contract (arity table, framing
markers, sentinel-terminated traversal) and rebuild Act II as the dispatcher
skeleton — `PARA` traffic only, every existing fixture stays green.

**Architecture:** Stage P1 of the Spike A resumption
(`docs/superpowers/specs/2026-07-06-spike-a-ir-lists-design.md`; architecture
spec §4.2/§7.3 as revised 2026-07-06). The Slice-1 stream (`1, glyphs…, 0` per
paragraph) already *is* the `PARA` token encoding, so the stream **content** is
unchanged; what changes is how the acts know where the stream ends. The Slice-1
fixed counts (`STREAM_THRESHOLD` 128 / 315 / 387) cannot survive a
variable-length token stream — P2's list tokens change the count per input — so
P1 retires them for a bottom-of-stream sentinel (`STREAM_END = -1`) seeded
beneath every carrier stack. The design spec explicitly permits this
retirement ("preserved **unless** the tokenized stream makes one structurally
unnecessary… invisible to G1/G3"). Act II is rewritten as the pass frame
(`PASS_PARA_*` paragraph-formation pass + `FRAME_REVERSE_*` final reverse onto
Puck); Acts III/IV and the debug dump migrate to sentinel traversal one act per
task, each task independently green. **No splc compiler changes are expected**
(the mid-scene non-exhaustive branch this plan leans on is already supported
and already used by Act I's `HECATE_READ_INPUT`). If a genuine IR gap surfaces,
extend the instruction set with tests per the splc design's no-escape-hatch
rule — never bypass it — and report the plan defect.

**Tech Stack:** Python 3.12 (frozen dataclasses), existing `scripts/splc/`
package, `shakespearelang` interpreter via `./shakedown` / `./shakedown-debug`,
pytest.

## Global Constraints

- **Literary protocol is binding:** `docs/superpowers/notes/spl-literary-protocol.md`. All controlled prose an implementer needs is reserved in this plan's ready-to-paste TOML blocks (§Reserved literary surfaces) plus the spare pool. **Implementation agents must not author controlled prose.** If the spare pool runs out, stop and report a plan defect.
- **Scene ledger sync per commit:** a scene label appearing in a generated fragment and its `[scenes.LABEL]` TOML entry land in the same commit; retired labels lose their TOML entries in the same commit (orphans fail `test_scene_titles_have_toml_entries_and_match_source`).
- **Literary compliance regression gates** (protocol requirement — run in every task's final verify): `uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q` plus `uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q`.
- **Never hand-edit** `shakedown.spl` or any generated fragment. Regenerate: `uv run python -m scripts.splc && uv run python scripts/assemble.py`.
- **Regen identity for untouched fragments after every change:** `uv run python -m scripts.splc && git diff --exit-code` on the generated fragments *not* owned by the current task must show no diff.
- **G2 discipline (design spec):** the pre-migration debug dumps are recorded once (Task 2 Step 1) and kept in `.cache/` for the whole plan. The **Amps dump must be byte-equal at every task boundary** (315/387 are the true Amps counts, so sentinel traversal reproduces them exactly). The short-probe dump is *expected* to change (the fixed-count reverse silently truncated short streams); it is hand-reviewed against the contract and blessed as a committed baseline in Task 5. Do not bless anything before Task 5.
- **Quirks preserved except the counts:** the unconditional leading `PARA` push on empty input (and its crash shape on truly empty streams), Romeo's now-dead scan decrement, Romeo's destination discard pile, and every Act III span-scene behavior stay byte-for-byte. **Act III's 56 span scenes are untouched** — only traversal-boundary scenes change.
- **Act I is unchanged** (design spec). `HORATIO` (Act I's glyph count) remains the Act I→II contract; it is no longer read downstream of Act II after this plan.
- **Operator-only:** no version bumps, tags, or pushes.
- Python conventions per `CLAUDE.md`: type hints everywhere, no bare `Any`, no `print()` outside CLI scripts; `uv run ruff check . && uv run ruff format . && uv run pyright` clean before each commit.
- Conventional commits (hook-enforced); types used here: `chore:` (contract/infra), `refactor:` (act migrations, no gated-behavior change), `test:` (baselines), `docs:`.

## Contract and choreography ground truth

**Stream contract (architecture spec §4.2, revised 2026-07-06):** a token is an
integer code from `docs/spl/token-codes.md`, then a fixed number of integer
payloads determined by the code, then — for text-bearing tokens — a glyph run
terminated by `0` (glyphs are always ≥ 1). One definition in
`src_ir/tokens.py`; consumed by Act II emission, Act III traversal, Act IV
dispatch, and the debug dump.

**Framing markers added by this plan** (not tokens — never dispatched on):

| Marker | Value | Meaning | SPL surface |
|---|---:|---|---|
| `TEXT_END` | 0 | ends a text-bearing token's glyph run | speaker's `v0` (`nothing`) |
| `STREAM_END` | −1 | bottom-of-stream sentinel under every carrier stack | speaker's `vneg1` (`a wolf` / `a curse` / `a toad`) |

**Sentinel protocol:** every producer seeds its output stack with
`STREAM_END` before pushing stream items; every consumer pops until it sees
`STREAM_END`. Order restoration stays explicit: Act II's final reverse and Act
III's reverse each seed the destination (Puck) with `STREAM_END` first, then
pop-push until the source's sentinel surfaces. Negative pushes are verified
SPL (`docs/spl/reference.md`: bare negative noun → −1); every character
already has `vneg1` in `src/literary.toml`.

**Stack/register map after P1:**

| Character | Act II | Act III | Act IV / debug |
|---|---|---|---|
| Hecate | stack: Act I glyphs (drained) | — | — |
| Horatio | value: Act I glyph count (input countdown source; last read here) | — | — |
| Lady Macbeth | value: input countdown, then popped items; stack: carrier (sentinel-seeded) | — | — |
| Puck | stack: forward stream (sentinel-seeded by Act II reverse) | value: current glyph; stack: drained then re-seeded for Act IV | value: current token/scratch; stack: drained |
| Macbeth | reserved (frame sentinels, P2) — off stage in P1 | — | — |
| Romeo | — | value: dead scan decrement (quirk kept); stack: discard pile (quirk) | — |
| Juliet | — | stack: forward output (sentinel-seeded); value: scratch | — |
| Rosalind | — | stack: Act I references (drained, quirk) | — |
| Prospero | — | — | anchors; no ops (count register retired) |

**Why each act migration is independently green:** the sentinels sit *below*
the stream, and 315/387 are the true Amps counts. A count-based consumer pops
exactly the stream items and never reaches the sentinel beneath; a
sentinel-based consumer pops the same items and stops at the sentinel. So Act
II can migrate while III/IV still count, then III, then IV+debug — Amps
G1/G2/G3 hold at every boundary. Short inputs shift behavior mid-ladder
(they were silently mis-counted before — no test pins them); only the final
state is reviewed and blessed.

**Choreography notes for the implementer:** stage pairs are computed by
`scripts/splc/validate.py` — an `IrError` means the plan's wiring was
transcribed wrong (fix against this plan's code blocks), not a compiler gap.
The wiring below was checked against the entry-pair rules: per-glyph paths
(`LYRIC_RETURN_TO_SCAN → LYRIC_POP_GLYPH`) stay direction-free; per-token and
per-paragraph transitions (`TRAVERSE_OPEN_TEXT`, `TRAVERSE_COPY_TERMINATOR`,
`FRAME_REVERSE_OPEN`) absorb the stage swaps.

## Reserved literary surfaces

Reserved at planning time per
`docs/superpowers/notes/correctness-first-spl-workflow.md`. Titles reuse the
retired scenes' vetted text wherever semantics match. Exact TOML appears
inline in each task. New controlled surfaces summary:

- **Scene titles:** Act II — 9 relabeled entries (`PASS_PARA_*` ×7, `FRAME_REVERSE_*` ×2); Act III — `TRAVERSE_NEXT_TOKEN`, `TRAVERSE_OPEN_TEXT`, `TRAVERSE_COPY_TERMINATOR`; Act IV — `SCRIBE_DISPATCH_TOKEN`.
- **Recall lines:** `characters.juliet.recall.nights_next_word = "Recall the night's next word."`; `characters.puck.recall.roses_kept_word = "Recall the rose's kept word."`; `characters.prospero.recall.heralds_parting_word = "Recall the herald's parting word."`
- **Pointer moves in `src/literary.toml`:** `iconic_moments.once_more_breach.scene` → `PASS_PARA_READ_GLYPH`; `dramatic_moments.lady_macbeth_death_exit.scene` → `FRAME_REVERSE_OPEN`.
- **Debug titles are outside literary scope** (plain literals in `src_ir/debug_act4.py`, no TOML): keep `DBG_POP`/`DBG_DONE` titles; `DBG_START` becomes `"The scribe takes his station."`

**Spare scene-title pool** (pre-approved; use only if a structural surprise
forces an extra scene, with `pattern = "bare_statement"` unless noted; report
use to the operator):

- Act II (Martial/Catastrophic): `"The wall answers the mason's doubt."`, `"A cold stone waits at the threshold."`, `"The keep holds one more measure."`, `"The breach is walled anew."`
- Act III (pastoral, lovers): `"The starlit path takes one more word."`, `"Morning light falls on the next petal."`, `"The night keeps a silver tally."`, `"The garden yields its last rose."`
- Act IV (noble/ceremonial, `scene_of_character`): `"Prospero weighs the parting word."`, `"The scribe inscribes a waiting seal."`, `"Prospero releases the final measure."`, `"The scribe proves the herald's word."`

---

### Task 1: Stream-contract arity table and framing markers

**Files:**
- Modify: `src_ir/tokens.py`
- Modify: `src_ir/stream.py` (add `emit_token`)
- Modify: `docs/spl/token-codes.md`
- Test: `tests/test_token_codes.py`, `tests/test_stream_recipes.py`

**Interfaces:**
- Consumes: existing token constants; `scripts.splc.ir` `Push`/`push`/`const`; `Char`.
- Produces: `tokens.TokenArity(payloads: int, has_text: bool)` frozen dataclass; `tokens.ARITY: dict[int, TokenArity]`; `tokens.TEXT_END = 0`; `tokens.STREAM_END = -1`; `stream.emit_token(target: Char, code: int, *payloads: int) -> list[Push]`. Tasks 2–5 rely on all of these names exactly.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_token_codes.py`:

```python
def test_framing_markers_are_disjoint_from_token_codes() -> None:
    from src_ir import tokens

    assert tokens.TEXT_END == 0
    assert tokens.STREAM_END == -1
    codes = {row[1] for row in parse_table()}
    assert tokens.TEXT_END not in codes
    assert tokens.STREAM_END not in codes


def test_arity_table_matches_doc() -> None:
    """The doc's arity rows and src_ir.tokens.ARITY are the same table."""
    from src_ir import tokens

    doc_rows: dict[int, tuple[int, bool]] = {}
    row_re = re.compile(
        r"^\|\s*(?P<name>[A-Z_]+)\s*\|\s*(?P<code>-?\d+)\s*\|"
        r"\s*(?P<payloads>\d+)\s*\|\s*(?P<text>yes|no)\s*\|"
    )
    for line in TOKEN_CODES_DOC.read_text().splitlines():
        match = row_re.match(line)
        if match:
            doc_rows[int(match["code"])] = (
                int(match["payloads"]),
                match["text"] == "yes",
            )
    assert doc_rows, "no arity rows found in docs/spl/token-codes.md"
    assert doc_rows == {
        code: (arity.payloads, arity.has_text)
        for code, arity in tokens.ARITY.items()
    }
```

Append to `tests/test_stream_recipes.py`:

```python
def test_emit_token_validates_arity() -> None:
    import pytest

    from scripts.splc.ir import Const, Push
    from src_ir import tokens
    from src_ir.stream import emit_token

    para = emit_token(Char.LADY_MACBETH, tokens.PARA)
    assert [type(op) for op in para] == [Push]
    assert para[0] == Push(Char.LADY_MACBETH, Const(tokens.PARA))

    list_open = emit_token(Char.LADY_MACBETH, tokens.LIST_OPEN, 1)
    assert [op.expr for op in list_open] == [
        Const(tokens.LIST_OPEN),
        Const(1),
    ]

    with pytest.raises(ValueError, match="payload"):
        emit_token(Char.LADY_MACBETH, tokens.LIST_OPEN)
    with pytest.raises(ValueError, match="payload"):
        emit_token(Char.LADY_MACBETH, tokens.PARA, 7)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_token_codes.py tests/test_stream_recipes.py -q`
Expected: the three new tests FAIL (`AttributeError`/`ImportError` for `TEXT_END`, `ARITY`, `emit_token`); all pre-existing tests PASS.

- [ ] **Step 3: Implement the contract constants**

Replace `src_ir/tokens.py` with:

```python
"""Dispatch token codes, framing markers, and the arity table — one
definition, matching docs/spl/token-codes.md. The arity table is the single
home of the stream contract (design spec 2026-07-06): contract drift is
structurally impossible because Act II emission, Act III traversal, Act IV
dispatch, and the debug dump all consume this module."""

from __future__ import annotations

from dataclasses import dataclass

PARA = 1
HEADER = 2
HR = 3
LIST_OPEN = 4
LIST_ITEM = 5
LIST_CLOSE = 6
BLOCKQUOTE_OPEN = 7
BLOCKQUOTE_CLOSE = 8
CODE_BLOCK = 9
RAW_HTML_HASH = 10
ANCHOR_OPEN = 11
ANCHOR_TITLE = 12
ANCHOR_TEXT = 13
ANCHOR_CLOSE = 14

# Framing markers — not tokens, never dispatched on by the arity table.
# TEXT_END closes a text-bearing token's glyph run (glyphs are always >= 1).
# STREAM_END is the bottom-of-stream sentinel seeded under every carrier
# stack; consumers pop until they see it. Spoken via stable_utility v0/vneg1
# per speaker, unlike Critical token-code phrases.
TEXT_END = 0
STREAM_END = -1


@dataclass(frozen=True)
class TokenArity:
    payloads: int  # fixed integer payloads following the code
    has_text: bool  # glyph run terminated by TEXT_END follows the payloads


# Spike-scope vocabulary (2026-07-06 design). Later slices append rows here
# and in docs/spl/token-codes.md together (test_arity_table_matches_doc).
ARITY: dict[int, TokenArity] = {
    PARA: TokenArity(0, True),
    LIST_OPEN: TokenArity(1, False),  # kind: 1 = unordered, 2 = ordered
    LIST_ITEM: TokenArity(1, True),  # looseness: 1 = tight, 2 = loose
    LIST_CLOSE: TokenArity(0, False),
}
```

Append to `src_ir/stream.py` (imports merge at the top: add
`Char`, `Push`, `push` to the existing `scripts.splc.ir` import and
`from src_ir import tokens`):

```python
def emit_token(target: Char, code: int, *payloads: int) -> list[Push]:
    """Push a token's code and fixed payloads per the arity table.

    Text-bearing tokens stream their glyph run afterwards; the caller closes
    it with push(target, const(tokens.TEXT_END))."""
    arity = tokens.ARITY[code]
    if len(payloads) != arity.payloads:
        raise ValueError(
            f"token {code} takes {arity.payloads} payload(s), got {len(payloads)}"
        )
    return [push(target, const(code)), *(push(target, const(p)) for p in payloads)]
```

- [ ] **Step 4: Extend `docs/spl/token-codes.md`**

Append before the "How To Extend" section:

```markdown
## Arity table (stream contract)

A token is its code, then a fixed number of integer payloads, then — for
text-bearing tokens — a glyph run terminated by `TEXT_END`. Mirrored in
`src_ir/tokens.py` (`ARITY`); `tests/test_token_codes.py` keeps the two in
step. Spike-scope vocabulary only; later slices append rows in both places.

| Token | Code | Fixed payloads | Text |
|---|---:|---:|---|
| PARA | 1 | 0 | yes |
| LIST_OPEN | 4 | 1 | no |
| LIST_ITEM | 5 | 1 | yes |
| LIST_CLOSE | 6 | 0 | no |

`LIST_OPEN` payload — kind: 1 = unordered, 2 = ordered. `LIST_ITEM` payload —
looseness: 1 = tight, 2 = loose.

## Framing markers

Not tokens: never dispatched on. Spoken through each speaker's
`stable_utility` `v0`/`vneg1` pools rather than a Critical canonical phrase.

| Marker | Value | Meaning |
|---|---:|---|
| TEXT_END | 0 | terminates a text-bearing token's glyph run (glyphs ≥ 1) |
| STREAM_END | −1 | bottom-of-stream sentinel seeded under every carrier stack |
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_token_codes.py tests/test_stream_recipes.py -q`
Expected: PASS (all, including pre-existing).

- [ ] **Step 6: Regen identity, lint, type-check, commit**

```bash
uv run python -m scripts.splc && git diff --exit-code src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl src/40-act4-emit.spl debug/40-act4-token-dump.spl
uv run ruff check . && uv run ruff format . && uv run pyright
git add src_ir/tokens.py src_ir/stream.py docs/spl/token-codes.md tests/test_token_codes.py tests/test_stream_recipes.py
git commit -m "chore: add stream-contract arity table and framing markers"
```

Expected: no fragment diff (nothing consumes the new names yet).

---

### Task 2: Act II dispatcher skeleton

Rewrite `src_ir/act2.py`: the paragraph-formation pass becomes `PASS_PARA_*`
(same algorithm, tokenized emission, sentinel-seeded carrier), the reverse
becomes the frame's `FRAME_REVERSE_*` scenes (sentinel-terminated, threshold
retired). Stream **content** is unchanged for Amps; short inputs now reverse
completely (previously truncated — untested surface).

**Files:**
- Modify: `src_ir/act2.py` (full rewrite below)
- Modify: `src/20-act2-literary.toml` (full replacement below)
- Modify: `src/literary.toml` (two pointer moves)
- Modify (generated): `src/20-act2-block.spl`, `shakedown.spl`

**Interfaces:**
- Consumes: Task 1's `tokens.STREAM_END`/`tokens.TEXT_END`/`emit_token`; existing cast and IR builders.
- Produces: Act II leaves Puck's stack as `STREAM_END` + forward token stream (Acts III/IV consume in Tasks 3–4); scene-label prefixes `PASS_PARA_*` / `FRAME_REVERSE_*` that P2's `PASS_LISTS_*` scenes will slot before.

- [ ] **Step 1: Record the G2 before-dumps (pre-migration play)**

```bash
mkdir -p .cache
./shakedown-debug < "$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text" > .cache/g2-p1-before-amps.txt
printf 'hello\n\nworld\n' | ./shakedown-debug > .cache/g2-p1-before-short.txt
wc -l .cache/g2-p1-before-amps.txt .cache/g2-p1-before-short.txt
```

Expected: 387 lines for Amps. Keep both files untouched for the whole plan.

- [ ] **Step 2: Rewrite `src_ir/act2.py`**

Replace the whole module with:

```python
"""Act II — block dispatcher skeleton (Spike A P1). One production pass
(paragraph formation) inside the frame: sentinel-seeded carrier stacks and an
explicit final reverse onto Puck, so order restoration is unconditional.

Pass ordering slots (architecture spec §4.2, matching _RunBlockGamut):
headers -> horizontal rules -> lists -> code blocks -> blockquotes ->
HTML re-hash -> paragraph formation. Only paragraph formation exists; each
future pass lands as a contiguous PASS_<NAME>_* scene group inserted before
the pass that follows it, reading one carrier stack and producing onto the
other (Lady Macbeth <-> Macbeth ping-pong; Macbeth's stack is reserved for
frame sentinels, so a pass needing frames must not write to him — design
spec §6.3). The FRAME_REVERSE_* scenes always drain the last carrier.

Slice-1 quirks preserved: the unconditional leading PARA push (empty input
keeps its crash shape) and the 1/0 paragraph framing, which is exactly the
PARA token encoding (code 1, glyph run, TEXT_END). The Slice-1 fixed reverse
count (315 above the 128 threshold) is retired: the tokenized stream is
bottom-terminated by STREAM_END, making counts structurally unnecessary
(design spec, cross-act impact)."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    act,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    push,
    scene,
    sub,
    val,
)
from src_ir import tokens
from src_ir.cast import HECATE, HORATIO, LADY_MACBETH, PUCK
from src_ir.stream import emit_token

_NEWLINE = const(10)

ACT: Act = act(
    2,
    LADY_MACBETH,
    [
        scene(
            "ACT_II_START",
            let(LADY_MACBETH, val(HORATIO)),
            push(LADY_MACBETH, const(tokens.STREAM_END)),
            *emit_token(LADY_MACBETH, tokens.PARA),
            goto("PASS_PARA_READ_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_READ_GLYPH",
            pop(HECATE, recall="hewn_glyph"),
            let(LADY_MACBETH, sub(val(LADY_MACBETH), const(1))),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_PARA_CLOSE_PARAGRAPH",
                else_="PASS_PARA_KEEP_GLYPH",
            ),
        ),
        scene(
            "PASS_PARA_KEEP_GLYPH",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_PARA_CLOSE_FINAL",
                else_="PASS_PARA_READ_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_CLOSE_PARAGRAPH",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="FRAME_REVERSE_OPEN",
                else_="PASS_PARA_SKIP_BLANK",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_SKIP_BLANK",
            pop(HECATE, recall="blank_glyph"),
            let(LADY_MACBETH, sub(val(LADY_MACBETH), const(1))),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_PARA_AFTER_BLANK",
                else_="PASS_PARA_OPEN_WITH_GLYPH",
            ),
        ),
        scene(
            "PASS_PARA_AFTER_BLANK",
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="FRAME_REVERSE_OPEN",
                else_="PASS_PARA_SKIP_BLANK",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_OPEN_WITH_GLYPH",
            *emit_token(LADY_MACBETH, tokens.PARA),
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_PARA_CLOSE_FINAL",
                else_="PASS_PARA_READ_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_PARA_CLOSE_FINAL",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("FRAME_REVERSE_OPEN"),
            companion=HECATE,
        ),
        scene(
            "FRAME_REVERSE_OPEN",
            push(PUCK, const(tokens.STREAM_END)),
            goto("FRAME_REVERSE_POP"),
        ),
        scene(
            "FRAME_REVERSE_POP",
            pop(LADY_MACBETH, recall="masons_stone"),
            branch(
                eq(val(LADY_MACBETH), const(tokens.STREAM_END)),
                then="ACT_II_DONE",
            ),
            push(PUCK, val(LADY_MACBETH)),
            goto("FRAME_REVERSE_POP"),
        ),
        scene("ACT_II_DONE", halt_act(), companion=PUCK),
    ],
)
```

- [ ] **Step 3: Replace `src/20-act2-literary.toml`**

Full new file content (titles reused verbatim from the retired labels):

```toml
[scenes.ACT_II_DONE]
title = "The second act yields."
pattern = "bare_statement"

[scenes.ACT_II_START]
title = "Wherein Lady Macbeth receives the cauldron's line."
pattern = "wherein"

[scenes.FRAME_REVERSE_OPEN]
title = "Lady Macbeth gives Puck the mason's order."
pattern = "cross_character"

[scenes.FRAME_REVERSE_POP]
title = "The herald turns the wall toward morning."
pattern = "scene_of_character"

[scenes.PASS_PARA_AFTER_BLANK]
title = "The mason counts the quiet."
pattern = "scene_of_character"

[scenes.PASS_PARA_CLOSE_FINAL]
title = "The last chamber is sealed."
pattern = "bare_statement"

[scenes.PASS_PARA_CLOSE_PARAGRAPH]
title = "The wall is sealed against the blank."
pattern = "bare_statement"

[scenes.PASS_PARA_KEEP_GLYPH]
title = "One glyph is laid within the wall."
pattern = "bare_statement"

[scenes.PASS_PARA_OPEN_WITH_GLYPH]
title = "A new chamber takes its mark."
pattern = "bare_statement"

[scenes.PASS_PARA_READ_GLYPH]
title = "Once more unto the breach."
pattern = "iconic_echo"

[scenes.PASS_PARA_SKIP_BLANK]
title = "Empty lines pass beneath the keep."
pattern = "bare_statement"
```

- [ ] **Step 4: Move the two pointers in `src/literary.toml`**

In `[iconic_moments.once_more_breach]`, change `scene = "MASON_READ_PARAGRAPH_GLYPH"` to `scene = "PASS_PARA_READ_GLYPH"`.
In `[dramatic_moments.lady_macbeth_death_exit]`, change `scene = "MASON_OPEN_REVERSE_STREAM"` to `scene = "FRAME_REVERSE_OPEN"`.

- [ ] **Step 5: Regenerate and gate**

```bash
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --stat src/10-act1-preprocess.spl src/30-act3-span.spl src/40-act4-emit.spl debug/40-act4-token-dump.spl
```

Expected: only `src/20-act2-block.spl` and `shakedown.spl` change; the other four fragments are byte-identical.

G2 (Amps must be byte-equal — sentinel and fixed-count traversal agree on the true 315/387 counts):

```bash
./shakedown-debug < "$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text" > .cache/g2-p1-task2-amps.txt
diff .cache/g2-p1-before-amps.txt .cache/g2-p1-task2-amps.txt
```

Expected: empty diff. Any difference is a transcription bug in Step 2 — the paragraph pass emits different bytes, or the reverse moved a different item set. Fix `src_ir/act2.py` against this plan; never patch generated SPL.

G1 + G3 + compliance:

```bash
uv run pytest tests/test_slice1_amps_angle.py tests/test_strict_parity_harness.py tests/test_mdtest.py -k "Amps" -q
uv run pytest -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q
```

Expected: all green, same pass/skip/xfail shape as before the task. Watch `test_scene_titles_have_toml_entries_and_match_source` (ledger sync), `test_iconic_moments`/`test_dramatic_moments_are_visible_in_scene_surfaces` (the two moved pointers), and `test_named_production_characters_have_speaking_lines` (Lady Macbeth still speaks throughout the pass).

- [ ] **Step 6: Lint, type-check, commit**

```bash
uv run ruff check . && uv run ruff format . && uv run pyright
git add src_ir/act2.py src/20-act2-literary.toml src/literary.toml src/20-act2-block.spl shakedown.spl
git commit -m "refactor: rebuild act two as dispatcher skeleton with sentinel-framed stream"
```

---

### Task 3: Act III token-aware traversal

Add the token-walking traversal header (per the arity table) and migrate the
reverse to sentinel termination. **The 56 span scenes are untouched** — the
scenes listed below are traversal-boundary scenes only.

**Files:**
- Modify: `src_ir/act3.py`
- Modify: `src/30-act3-literary.toml` (3 additions, 9 removals)
- Modify: `src/literary.toml` (2 new recall keys)
- Modify (generated): `src/30-act3-span.spl`, `shakedown.spl`

**Interfaces:**
- Consumes: `tokens.STREAM_END`/`tokens.TEXT_END`/`tokens.ARITY`/`tokens.TokenArity`; Act II's sentinel-seeded Puck stack (Task 2).
- Produces: Act III leaves Puck's stack as `STREAM_END` + forward gilded stream (Act IV consumes in Task 4); labels `TRAVERSE_*` that P2 extends with the `LIST_*` arms of the traversal dispatch.

- [ ] **Step 1: Edit `src_ir/act3.py`**

**(a) Imports and module guard.** Remove `gt` from the `scripts.splc.ir`
import (no longer used); remove `HORATIO` from the `src_ir.cast` import;
change the `src_ir.stream` import to `from src_ir.stream import RECIPES`.
Update the module docstring's first sentence to:

```python
"""Act III — span pass over the tokenized stream (Spike A P1). Traversal
copies token codes and fixed payloads through untouched and runs the span
gamut only on text-payload glyphs (arity table in src_ir/tokens.py); the 56
span scenes are the Slice-1 port, quirks included (Romeo's write-only
destination discard pile and dead scan decrement, Rosalind's
drained-and-discarded consult pops, the hardcoded Slice 1 anchor payloads,
the `[link(` fallback that drops the current glyph).
Decoded ground truth: docs/superpowers/notes/act3-port-audit.md."""
```

Add below the imports:

```python
# P1 traverses PARA-only streams: no fixed payloads, text follows. P2
# replaces the unconditional copy in TRAVERSE_NEXT_TOKEN with a dispatch
# generated over tokens.ARITY.
assert tokens.ARITY[tokens.PARA] == tokens.TokenArity(0, True)
```

**(b) Delete these nine scenes** (count machinery and the multi-scene
reverse loop): `LYRIC_SET_SLICE_ONE_SCAN_COUNT`, `LYRIC_SET_SHORT_SCAN_COUNT`,
`LYRIC_SCAN_CHECK`, `LYRIC_SET_SLICE_ONE_REVERSE_COUNT`,
`LYRIC_SET_SHORT_REVERSE_COUNT`, `LYRIC_REVERSE_CHECK`,
`LYRIC_OPEN_PUSH_BACK`, `LYRIC_PUSH_BACK`, `LYRIC_RETURN_TO_REVERSE`.

**(c) Replace `ACT_III_START`** (was the threshold branch; now seeds
Juliet's output stack) **and insert the traversal header directly after it:**

```python
        scene(
            "ACT_III_START",
            push(JULIET, const(tokens.STREAM_END)),
            goto("TRAVERSE_NEXT_TOKEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
        scene(
            "TRAVERSE_NEXT_TOKEN",
            pop(PUCK, recall="nights_next_word"),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="LYRIC_OPEN_REVERSE",
            ),
            # PARA (build-time assert above): copy the code through
            # untouched; no fixed payloads; a glyph run follows.
            push(JULIET, val(PUCK)),
            goto("TRAVERSE_OPEN_TEXT"),
            anchor=JULIET,
        ),
        scene(
            "TRAVERSE_OPEN_TEXT",
            goto("LYRIC_POP_GLYPH"),
            companion=PUCK,
        ),
```

**(d) Replace `LYRIC_POP_GLYPH`** (gains the TEXT_END test ahead of the
span dispatch; the dead Romeo decrement inside `_pop_glyph` is a preserved
quirk — Romeo starts the act at 0 and goes negative, never read):

```python
        scene(
            "LYRIC_POP_GLYPH",
            *_pop_glyph("mornings_first_cut"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="TRAVERSE_COPY_TERMINATOR",
            ),
            branch(
                eq(val(PUCK), _k(91)),  # '['
                then="LYRIC_REFERENCE_POP_AFTER_OPEN",
                else_="LYRIC_TEST_AMPERSAND",
            ),
        ),
```

**(e) Replace `LYRIC_RETURN_TO_SCAN`** (same label and title; the goto
target moves from the deleted `LYRIC_SCAN_CHECK` to the glyph pop —
per-glyph path stays direction-free):

```python
        scene(
            "LYRIC_RETURN_TO_SCAN",
            goto("LYRIC_POP_GLYPH"),
            companion=PUCK,
        ),
```

**(f) Insert `TRAVERSE_COPY_TERMINATOR`** directly after
`LYRIC_RETURN_TO_SCAN` (copies the glyph run's closing `TEXT_END` and
returns to the token loop):

```python
        scene(
            "TRAVERSE_COPY_TERMINATOR",
            push(JULIET, const(tokens.TEXT_END)),
            goto("TRAVERSE_NEXT_TOKEN"),
            anchor=JULIET,
            companion=PUCK,
        ),
```

**(g) Replace the reverse phase.** `LYRIC_OPEN_REVERSE` (same label/title)
now seeds Puck for Act IV; `LYRIC_REVERSE_POP` (same label/title) becomes the
whole single-scene reverse loop. `ACT_III_DONE` is untouched (the lovers'
united exit stands; entering it swaps Puck for Romeo once, which is fine):

```python
        scene(
            "LYRIC_OPEN_REVERSE",
            push(PUCK, const(tokens.STREAM_END)),
            goto("LYRIC_REVERSE_POP"),
            anchor=JULIET,
        ),
        scene(
            "LYRIC_REVERSE_POP",
            pop(JULIET, recall="roses_kept_word"),
            branch(
                eq(val(JULIET), const(tokens.STREAM_END)),
                then="ACT_III_DONE",
            ),
            push(PUCK, val(JULIET)),
            goto("LYRIC_REVERSE_POP"),
            anchor=JULIET,
        ),
```

Every other scene in the module is byte-unchanged.

- [ ] **Step 2: Reserve the new controlled surfaces**

Add to `src/30-act3-literary.toml` (alphabetical position with the other
entries):

```toml
[scenes.TRAVERSE_COPY_TERMINATOR]
title = "The night lays down the sealing stone."
pattern = "bare_statement"

[scenes.TRAVERSE_NEXT_TOKEN]
title = "Juliet takes the herald's next word."
pattern = "cross_character"

[scenes.TRAVERSE_OPEN_TEXT]
title = "The morning takes up the gilded scan."
pattern = "bare_statement"
```

Remove the nine entries for the deleted labels:
`LYRIC_SET_SLICE_ONE_SCAN_COUNT`, `LYRIC_SET_SHORT_SCAN_COUNT`,
`LYRIC_SCAN_CHECK`, `LYRIC_SET_SLICE_ONE_REVERSE_COUNT`,
`LYRIC_SET_SHORT_REVERSE_COUNT`, `LYRIC_REVERSE_CHECK`,
`LYRIC_OPEN_PUSH_BACK`, `LYRIC_PUSH_BACK`, `LYRIC_RETURN_TO_REVERSE`.

In `src/literary.toml`, add to `[characters.juliet.recall]` (currently
empty):

```toml
nights_next_word = "Recall the night's next word."
```

and to `[characters.puck.recall]`:

```toml
roses_kept_word = "Recall the rose's kept word."
```

(`characters.romeo.recall.roses_kept_word` stays — pools may hold unused
keys; do not remove entries this plan doesn't own.)

- [ ] **Step 3: Regenerate and gate**

```bash
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --stat src/10-act1-preprocess.spl src/20-act2-block.spl src/40-act4-emit.spl debug/40-act4-token-dump.spl
```

Expected: only `src/30-act3-span.spl` and `shakedown.spl` change.

```bash
./shakedown-debug < "$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text" > .cache/g2-p1-task3-amps.txt
diff .cache/g2-p1-before-amps.txt .cache/g2-p1-task3-amps.txt
uv run pytest tests/test_slice1_amps_angle.py tests/test_strict_parity_harness.py tests/test_mdtest.py -k "Amps" -q
uv run pytest -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q
```

Expected: empty Amps diff; all suites green, same shape. Watch
`test_reference_librarian_is_visible_in_reference_scenes` (the four
Rosalind consult scenes are untouched — it must still pass) and
`test_juliet_surfaces_include_night_or_star_imagery` (the new title and
recall line are night-imagery positive).

- [ ] **Step 4: Lint, type-check, commit**

```bash
uv run ruff check . && uv run ruff format . && uv run pyright
git add src_ir/act3.py src/30-act3-literary.toml src/literary.toml src/30-act3-span.spl shakedown.spl
git commit -m "refactor: walk act three over the tokenized stream by arity"
```

---

### Task 4: Act IV and debug-act sentinel dispatch

Act IV pops until `STREAM_END` and dispatches on the token code; the
final-close decision becomes a one-token lookahead (the old count-based
`PROSPERO == 0` test cannot exist without counts). The debug act dumps the
stream until `STREAM_END`. Prospero's count register is retired — he anchors
and speaks every line addressed to Puck, as before.

**Files:**
- Modify: `src_ir/act4.py` (full rewrite below)
- Modify: `src_ir/debug_act4.py` (full rewrite below)
- Modify: `src/40-act4-literary.toml` (1 addition, 3 removals)
- Modify: `src/literary.toml` (1 new recall key)
- Modify (generated): `src/40-act4-emit.spl`, `debug/40-act4-token-dump.spl`, `shakedown.spl`

**Interfaces:**
- Consumes: `tokens.STREAM_END`/`tokens.PARA`/anchor token constants; Act III's sentinel-seeded Puck stack (Task 3).
- Produces: `SCRIBE_DISPATCH_TOKEN` — the single dispatch-chain entry that P2's list-emission scenes extend; the debug dump that Task 5 blesses as the G2 baseline.

- [ ] **Step 1: Rewrite `src_ir/act4.py`**

```python
"""Act IV — emit pass over the tokenized stream (Spike A P1). Prospero
anchors and speaks; Puck carries the current token / scratch. Dispatch pops
until the STREAM_END sentinel (src_ir/tokens.py) — the Slice-1 fixed stream
count is retired. The final-paragraph close (single trailing newline) is
decided by a one-token lookahead at each TEXT_END. Emission ground truth is
unchanged from the Slice-1 port (docs/superpowers/notes/act4-port-audit.md)."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    Op,
    act,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    print_char,
    scene,
    val,
)
from src_ir import tokens
from src_ir.cast import PROSPERO, PUCK
from src_ir.stream import RECIPES


def _emit(*codes: int) -> list[Op]:
    """One `let`/`print_char` pair per output byte, on Puck."""
    ops: list[Op] = []
    for code in codes:
        ops.append(let(PUCK, RECIPES.get(code, const(code))))
        ops.append(print_char(PUCK))
    return ops


ACT: Act = act(
    4,
    PROSPERO,
    [
        scene(
            "ACT_IV_START",
            goto("SCRIBE_POP_TOKEN"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_POP_TOKEN",
            pop(PUCK, recall="heralds_present_word"),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="ACT_IV_DONE",
            ),
            goto("SCRIBE_DISPATCH_TOKEN"),
        ),
        scene(
            "SCRIBE_DISPATCH_TOKEN",
            branch(
                eq(val(PUCK), const(tokens.PARA)),
                then="SCRIBE_EMIT_PARAGRAPH_OPEN",
                else_="SCRIBE_TEST_PARAGRAPH_CLOSE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_PARAGRAPH_CLOSE",
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="SCRIBE_TEST_FINAL_CLOSE",
                else_="SCRIBE_TEST_ANCHOR_OPEN",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_ANCHOR_OPEN",
            branch(
                eq(val(PUCK), const(tokens.ANCHOR_OPEN)),
                then="SCRIBE_EMIT_ANCHOR_OPEN",
                else_="SCRIBE_TEST_ANCHOR_TITLE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_ANCHOR_TITLE",
            branch(
                eq(val(PUCK), const(tokens.ANCHOR_TITLE)),
                then="SCRIBE_EMIT_ANCHOR_TITLE",
                else_="SCRIBE_TEST_ANCHOR_TEXT",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_ANCHOR_TEXT",
            branch(
                eq(val(PUCK), const(tokens.ANCHOR_TEXT)),
                then="SCRIBE_EMIT_ANCHOR_TEXT",
                else_="SCRIBE_TEST_ANCHOR_CLOSE",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TEST_ANCHOR_CLOSE",
            branch(
                eq(val(PUCK), const(tokens.ANCHOR_CLOSE)),
                then="SCRIBE_EMIT_ANCHOR_CLOSE",
                else_="SCRIBE_EMIT_PAYLOAD",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_EMIT_PAYLOAD",
            print_char(PUCK),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_OPEN",
            # <a href="
            *_emit(60, 97, 32, 104, 114, 101, 102, 61, 34),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_TITLE",
            # " title="
            *_emit(34, 32, 116, 105, 116, 108, 101, 61, 34),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_TEXT",
            # ">
            *_emit(34, 62),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_ANCHOR_CLOSE",
            # </a>
            *_emit(60, 47, 97, 62),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_OPEN",
            # <p>
            *_emit(60, 112, 62),
            goto("SCRIBE_POP_TOKEN"),
        ),
        scene(
            "SCRIBE_TEST_FINAL_CLOSE",
            # Lookahead: the paragraph just closed; peek at the next stream
            # item to choose the final (single-newline) close.
            pop(PUCK, recall="heralds_parting_word"),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE",
                else_="SCRIBE_EMIT_PARAGRAPH_CLOSE",
            ),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_CLOSE",
            # </p>\n\n — the lookahead token is already in hand; dispatch it.
            *_emit(60, 47, 112, 62, 10, 10),
            goto("SCRIBE_DISPATCH_TOKEN"),
        ),
        scene(
            "SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE",
            # </p>\n — the lookahead consumed STREAM_END; the play is done.
            *_emit(60, 47, 112, 62, 10),
            goto("ACT_IV_DONE"),
        ),
        scene("ACT_IV_DONE", halt_act(), companion=PUCK),
    ],
)
```

- [ ] **Step 2: Rewrite `src_ir/debug_act4.py`**

```python
"""Debug Act IV — token-stream dump. Shadow of src_ir/act4.py used by
`./shakedown-debug`: acts I–III run unchanged, then this play pops each
inter-act stream item until the STREAM_END sentinel and prints it as an
integer (Open your heart!) followed by a newline, instead of emitting HTML.
The sentinel itself is not printed: the dump is exactly the stream, so it
serves as the G2 baseline artifact (tests/fixtures/token_stream/)."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    act,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    pop,
    print_char,
    print_int,
    scene,
    val,
)
from src_ir import tokens
from src_ir.cast import PROSPERO, PUCK

# The debug play lives outside the globbed production literary ledger (a
# src/*-literary.toml entry for these would orphan them against the
# production source and fail test_scene_titles_have_toml_entries_and_match_source).
# Titles are inlined at render time instead — plain literals, outside
# literary scope per docs/superpowers/notes/correctness-first-spl-workflow.md.
SCENE_TITLES: dict[str, str] = {
    "DBG_START": "The scribe takes his station.",
    "DBG_POP": "The herald yields one word and it is counted aloud.",
    "DBG_DONE": "The counting is done.",
}

ACT: Act = act(
    4,
    PROSPERO,
    [
        scene(
            "DBG_START",
            goto("DBG_POP"),
            companion=PUCK,
        ),
        scene(
            "DBG_POP",
            pop(PUCK, recall="heralds_present_word"),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="DBG_DONE",
            ),
            print_int(PUCK),
            let(PUCK, const(10)),
            print_char(PUCK),
            goto("DBG_POP"),
        ),
        scene("DBG_DONE", halt_act(), companion=PUCK),
    ],
)
```

- [ ] **Step 3: Reserve the new controlled surfaces**

Add to `src/40-act4-literary.toml`:

```toml
[scenes.SCRIBE_DISPATCH_TOKEN]
title = "The scribe reads the present word."
pattern = "scene_of_character"
```

Remove the three entries for the deleted labels:
`SCRIBE_SET_SLICE_ONE_STREAM_COUNT`, `SCRIBE_SET_SHORT_STREAM_COUNT`,
`SCRIBE_STREAM_CHECK`. (`SCRIBE_TEST_FINAL_CLOSE` keeps its label and title
`"Prospero weighs the last seal."` — he now weighs it by lookahead.)

In `src/literary.toml`, add to `[characters.prospero.recall]`:

```toml
heralds_parting_word = "Recall the herald's parting word."
```

- [ ] **Step 4: Regenerate and gate**

```bash
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --stat src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl
```

Expected: only `src/40-act4-emit.spl`, `debug/40-act4-token-dump.spl`, and `shakedown.spl` change.

```bash
./shakedown-debug < "$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text" > .cache/g2-p1-task4-amps.txt
diff .cache/g2-p1-before-amps.txt .cache/g2-p1-task4-amps.txt
uv run pytest tests/test_slice1_amps_angle.py tests/test_strict_parity_harness.py tests/test_mdtest.py -k "Amps" -q
uv run pytest -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q
```

Expected: empty Amps diff; all suites green, same shape. Watch
`test_prospero_assignment_equalities_use_his_pool` (Prospero no longer owns a
`let`; the test must pass vacuously or over `_emit`'s Puck assignments, which
he speaks) and `test_token_dump.py` (`values[0] == 1` still holds).

- [ ] **Step 5: Lint, type-check, commit**

```bash
uv run ruff check . && uv run ruff format . && uv run pyright
git add src_ir/act4.py src_ir/debug_act4.py src/40-act4-literary.toml src/literary.toml src/40-act4-emit.spl debug/40-act4-token-dump.spl shakedown.spl
git commit -m "refactor: dispatch act four and debug dump on sentinel-terminated stream"
```

---

### Task 5: Retire the count constants, bless the G2 baseline, close out

**Files:**
- Modify: `src_ir/stream.py` (remove dead constants)
- Modify: `tests/test_stream_recipes.py` (drop the count-expr test)
- Create: `tests/fixtures/token_stream/amps.dump`, `tests/fixtures/token_stream/short.dump`
- Modify: `tests/test_token_dump.py` (baseline tests)
- Modify: `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` (§4.2 stream-contract paragraph)
- Modify: `.agent/blockers.md`, `docs/superpowers/plans/plan-roadmap.md`, this plan file

**Interfaces:**
- Consumes: the migrated play from Tasks 2–4.
- Produces: committed G2 baselines that gate P2 and everything after; `src_ir/stream.py` reduced to `RECIPES` + `emit_token`.

- [ ] **Step 1: Remove the dead count machinery**

In `src_ir/stream.py`, delete `STREAM_THRESHOLD`, `SLICE_ONE_GLYPH_COUNT`,
`SLICE_ONE_STREAM_COUNT`, `slice_one_glyph_expr`, `slice_one_stream_expr`,
and the now-unused `add`/`mul` binop imports if nothing else uses them
(`RECIPES` still uses `add`, `mul`, `sub` — keep those). Update the module
docstring to:

```python
"""Shared <=4-operator value recipes and tokenized-stream emission helpers.

Single home for byte values whose default atom decomposition would exceed
the 4-operator compliance bound (test_numeric_recipe_complexity_stays_bounded)
and for arity-checked token emission (emit_token). The Slice-1 stream-count
constants (128/315/387) were retired by the P1 stream migration: the stream
is bottom-terminated by tokens.STREAM_END."""
```

In `tests/test_stream_recipes.py`, delete
`test_stream_constants_and_count_exprs` (keep
`test_recipes_evaluate_to_their_keys_within_bound` and
`test_emit_token_validates_arity`).

Run: `uv run grep -rn "STREAM_THRESHOLD\|SLICE_ONE" src_ir/ scripts/ tests/`
Expected: no hits.

Run: `uv run pytest -q && uv run ruff check . && uv run pyright`
Expected: green.

```bash
git add src_ir/stream.py tests/test_stream_recipes.py
git commit -m "chore: retire slice-one stream-count constants"
```

- [ ] **Step 2: Hand-review and bless the G2 baselines (design-spec procedure)**

```bash
./shakedown-debug < "$HOME/mdtest/Markdown.mdtest/Amps and angle encoding.text" > .cache/g2-p1-after-amps.txt
printf 'hello\n\nworld\n' | ./shakedown-debug > .cache/g2-p1-after-short.txt
diff .cache/g2-p1-before-amps.txt .cache/g2-p1-after-amps.txt
diff .cache/g2-p1-before-short.txt .cache/g2-p1-after-short.txt || true
```

Expected: the Amps diff is **empty** (315/387 were the true counts). The
short diff is **non-empty**: the fixed-count reverse used Horatio's glyph
count, which under-counted the marker-bearing stream and silently dropped
its deepest item; the sentinel reverse moves the whole stream.

**Hand-review the new short dump against the contract** (this is the
one-time re-bless the design spec mandates): read
`.cache/g2-p1-after-short.txt` top to bottom and check it parses as, exactly:
`1` (PARA), the byte values of `hello` (104 101 108 108 111), `0`
(TEXT_END), `1` (PARA), the byte values of `world` (119 111 114 108 100),
`0` (TEXT_END) — allowing for whatever Act I normalization does to the
probe's newlines (the dump must still parse as complete `PARA` token frames
under the arity table, nothing else). If any line cannot be assigned a place
in a token frame, that is a migration bug: stop and fix the offending act
task; do not bless.

Then commit the reviewed dumps as the durable G2 baselines:

```bash
mkdir -p tests/fixtures/token_stream
cp .cache/g2-p1-after-amps.txt tests/fixtures/token_stream/amps.dump
cp .cache/g2-p1-after-short.txt tests/fixtures/token_stream/short.dump
```

- [ ] **Step 3: Add the baseline regression tests**

Append to `tests/test_token_dump.py`:

```python
BASELINES = REPO / "tests" / "fixtures" / "token_stream"


def _dump(input_bytes: bytes) -> bytes:
    result = subprocess.run(
        [str(DEBUG_WRAPPER)],
        input=input_bytes,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    return result.stdout


def test_dump_matches_blessed_amps_baseline() -> None:
    """G2 gate: blessed by the P1 plan; P2 and later slices re-bless
    deliberately when the vocabulary grows, never casually."""
    assert _dump(AMPS_FIXTURE.read_bytes()) == (
        BASELINES / "amps.dump"
    ).read_bytes()


def test_dump_matches_blessed_short_baseline() -> None:
    assert _dump(b"hello\n\nworld\n") == (BASELINES / "short.dump").read_bytes()
```

Run: `uv run pytest tests/test_token_dump.py -q`
Expected: PASS (three tests).

```bash
git add tests/fixtures/token_stream tests/test_token_dump.py
git commit -m "test: bless tokenized-stream G2 dump baselines"
```

- [ ] **Step 4: Record the contract in the architecture spec**

In `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md`,
find the `**Stream contract (2026-07-06):**` paragraph in §4.2 and append to
it:

```markdown
Termination (P1, 2026-07-06): the stream is bottom-terminated by a
`STREAM_END` sentinel (−1) seeded beneath every carrier stack; traversal is
sentinel-based, retiring the Slice-1 fixed counts (128/315/387). `0` remains
reserved as the text-run terminator (`TEXT_END`); glyphs are always ≥ 1.
```

- [ ] **Step 5: Verify every gate one final time**

```bash
uv run pytest -q
uv run python -m scripts.splc && uv run python scripts/assemble.py && git diff --exit-code src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl src/40-act4-emit.spl debug/40-act4-token-dump.spl shakedown.spl
uv run ruff check . && uv run pyright
```

Expected: suite green (same xfail shape — the six list spike cases stay
xfailed until P2); no fragment diff; lint/types clean.

- [ ] **Step 6: Bookkeeping, tick, commit**

In `.agent/blockers.md`, update the Spike A `- BLOCK:` entry's last sentence
to reflect that the resumption is in flight: replace "Do not resume list
implementation until the replacement list plan is written in IR from an
interactive planning session" with "P1 (tokenized stream + dispatcher
skeleton) shipped; do not resume list implementation until the P2 list plan
is written in IR from an interactive planning session".

In `docs/superpowers/plans/plan-roadmap.md`, set the 3K row's status to
`shipped: <date> at commit <sha of the Task 5 baseline commit or later>`.
Tick every checkbox in this plan file.

```bash
git add .agent/blockers.md docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md
git commit -m "docs: record sentinel stream termination in architecture spec"
git add docs/superpowers/plans/plan-roadmap.md docs/superpowers/plans/2026-07-06-spike-a-p1-stream-skeleton.md
git commit -m "docs: mark spike-a p1 stream skeleton shipped"
```

Flag to the operator: P1 is the first half of the resumed Spike A; the next
planning session writes P2 (list pass at spike scope) against the blessed
baselines.

---

## Self-review notes (plan author)

- **Spec coverage:** arity table (Task 1), Act II skeleton + pass frame + final reverse (Task 2), Act III traversal per arity with span scenes untouched (Task 3), Act IV dispatch + debug dump (Task 4), G2 record/review/re-bless procedure and count-quirk retirement (Tasks 2–5), no new splc machinery (none needed — verified against `ir.py`/`validate.py`/`lower.py`), literary reservations + spares (§Reserved literary surfaces). Deferred to P2 by design: `LIST_*` emission, Macbeth's first speaking scenes and pool extension, frame sentinels, un-xfailing the spike fixtures.
- **Known accepted quirks:** Romeo's dead scan decrement stays (span scenes untouched); `romeo.recall.roses_kept_word` becomes an unused pool entry; empty-input crash shape unchanged; short-input HTML silently improves (no test pinned the broken behavior).
- **Type consistency:** `TokenArity(payloads, has_text)`, `emit_token(target, code, *payloads) -> list[Push]`, `TEXT_END`/`STREAM_END` names are used identically across Tasks 1–5.

## References

- `docs/superpowers/specs/2026-07-06-spike-a-ir-lists-design.md` — governing design (stream contract, dispatcher skeleton, G2 re-bless procedure, P1/P2 staging)
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — §4.2 stream contract and pass ordering, §6.3 sentinel ownership, §7.3 spike scope, §8.2 halt triggers (all as revised 2026-07-06)
- `docs/superpowers/plans/plan-roadmap.md` — plan ladder; 3K row
- `docs/superpowers/notes/spl-literary-protocol.md` — binding literary protocol
- `docs/superpowers/notes/correctness-first-spl-workflow.md` — prose reserved at planning time; spare-pool rules
- `docs/spl/token-codes.md` — canonical token codes; gains the arity/framing sections in Task 1
- `docs/spl/reference.md` — SPL legality (negative nouns → −1; mid-scene conditionals)
- `docs/superpowers/notes/act3-port-audit.md`, `docs/superpowers/notes/act4-port-audit.md` — Slice-1 decoded ground truth for the scenes this plan preserves
