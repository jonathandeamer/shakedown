# Spike A P2 — List Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the list pass at spike scope — `LIST_OPEN`/`LIST_ITEM`/`LIST_CLOSE`
tokens, frame sentinels on Macbeth, Act IV list emission — so the six list spike
fixtures pass byte-identical to Markdown.pl and Spike A completes.

**Architecture:** Stage P2 of the Spike A resumption
(`docs/superpowers/specs/2026-07-06-spike-a-ir-lists-design.md`; architecture
spec §4.2/§6.3/§7.3 as revised 2026-07-06). Act II becomes a genuine two-pass
dispatcher: `PASS_LISTS_*` (marker recognition, item framing, nesting frames on
Macbeth's stack) runs before `PASS_PARA_*` (paragraph formation from the mixed
stream), with the stack ping-pong the design prescribes (Lady Macbeth ↔ Macbeth
carriers, explicit final reverse onto Puck). Act III's traversal becomes a
dispatch generated over `tokens.ARITY`; Act IV gains route-driven list emission
scenes. **No splc compiler changes are expected** — every construct this plan
uses (mid-scene non-exhaustive branches, third-person off-stage questions,
scene-level anchor overrides, self-referential pushes) is already supported and
already used by the ported acts. If a genuine IR gap surfaces, extend the
instruction set with tests per the splc design's no-escape-hatch rule — never
bypass it — and report the plan defect.

**Tech Stack:** Python 3.12 (frozen dataclasses), existing `scripts/splc/`
package, `shakespearelang` interpreter via `./shakedown` / `./shakedown-debug`,
pytest, local `~/markdown/Markdown.pl` oracle.

## Plan validation provenance

Every IR code block in this plan was validated before the plan was written:

- `scripts/splc/validate.py` (the real validator) passes on all three acts —
  stage pairs, terminal rules, jump targets, recall keys.
- `scripts/splc/lower.py` (the real lowerer) renders all three acts with this
  plan's TOML reservations merged into the live pools (this is what surfaced
  the `vneg2` requirement in Task 4).
- An instruction-level IR interpreter executed the full four-act play (real
  Act I and the untouched Act III span scenes included) against all six spike
  fixtures plus twelve composition probes; output was byte-identical to
  `Markdown.pl` in every in-scope case, and the Amps/short debug dumps were
  byte-equal to the blessed 3K baselines.

So a gate failure during implementation means either transcription drift from
this plan (diff your file against the plan's block) or a real-interpreter
behavior difference the simulation could not see (report it; do not patch
generated SPL).

## Global Constraints

- **Literary protocol is binding:** `docs/superpowers/notes/spl-literary-protocol.md`. All controlled prose an implementer needs is reserved in this plan's ready-to-paste TOML blocks plus the spare pool (§Reserved literary surfaces). **Implementation agents must not author controlled prose.** If the spare pool runs out, stop and report a plan defect.
- **Scene ledger sync per commit:** a scene label appearing in a generated fragment and its `[scenes.LABEL]` TOML entry land in the same commit; retired labels lose their TOML entries in the same commit (orphans fail `test_scene_titles_have_toml_entries_and_match_source`).
- **Literary compliance regression gates** (run in every task's final verify): `uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q` plus `uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q`.
- **Never hand-edit** `shakedown.spl` or any generated fragment. Regenerate: `uv run python -m scripts.splc && uv run python scripts/assemble.py`.
- **Regen identity for untouched fragments after every change:** `uv run python -m scripts.splc && git diff --exit-code` on the generated fragments *not* owned by the current task must show no diff. `debug/40-act4-token-dump.spl` is untouched by every task in this plan.
- **G2 discipline (design spec):** `tests/fixtures/token_stream/amps.dump` and `short.dump` are the blessed 3K baselines and must be **byte-equal at every task boundary** (`uv run pytest tests/test_token_dump.py -q`). The six new list dumps are recorded and blessed only in Task 5, after hand-review against this plan's expected streams. Do not re-bless amps/short — if they drift, the task has a bug.
- **Act I is unchanged.** The Slice-1 quirks outside Act II's paragraph pass (Romeo's dead scan decrement and discard pile, Rosalind's consult pops, hardcoded anchor payloads, empty-input crash shape — the crash is in Act I) stay byte-for-byte. Act III's 56 span scenes are untouched; only the traversal header changes.
- **Operator-only:** no version bumps, tags, or pushes.
- Python conventions per `CLAUDE.md`: type hints everywhere, no bare `Any`, no `print()` outside CLI scripts; `uv run ruff check . && uv run ruff format . && uv run pyright` clean before each commit.
- Conventional commits (hook-enforced); types used here: `chore:` (contract), `refactor:` (Act III traversal), `feat:` (Act IV emission, Act II list pass), `test:` (baselines/un-xfail), `docs:`.

## Contract and choreography ground truth

**Token vocabulary** (unchanged from `docs/spl/token-codes.md`): `PARA(1)` text;
`LIST_OPEN(4)` payload kind 1=unordered/2=ordered; `LIST_ITEM(5)` payload
looseness 1=tight/2=loose, then text; `LIST_CLOSE(6)` bare. Text runs end with
`TEXT_END(0)`; streams bottom out at `STREAM_END(-1)`.

**New framing marker (Task 1):** `ITEM_START = -2`. On the *intra-Act-II* mixed
stream (list-pass output) an item is `[ITEM_START, glyphs…, TEXT_END]`. The
paragraph pass replaces `ITEM_START` with `LIST_ITEM` plus the looseness value
pulled from the side channel. `ITEM_START` never crosses an act boundary — the
G2 dumps must never contain a `-2`.

**The looseness side channel** (how a stack machine emits a payload that is
only known after the text): an item's looseness (blank line before or inside
the item ⇒ loose) is decided while its text is already flowing onto the
carrier. Instead of buffering every item, the list pass pushes the finished
item's looseness onto **Horatio's stack** (completion order) and brackets the
text with `ITEM_START`. The staging reverse flips the side stack onto **Puck**,
so the paragraph pass — walking the staged stream in document order — pops one
looseness value per `ITEM_START` it meets, first item first. Items complete
strictly sequentially (a nested open closes the enclosing item's text first),
so the pairing is exact.

**Carrier choreography (Act II):**

| Step | Reads | Writes | Order restored by |
|---|---|---|---|
| `PASS_LISTS_*` | Hecate (glyphs; countdown on Lady Macbeth's value) | Lady Macbeth's stack (mixed stream); Horatio's stack (side channel) | — |
| `FRAME_STAGE_*` | Lady Macbeth; Horatio | Macbeth (main); Puck (side) | this reverse |
| `PASS_PARA_*` | Macbeth (+ Puck side pops) | Lady Macbeth (token stream) | — |
| `FRAME_REVERSE_*` (P1 scenes, unchanged) | Lady Macbeth | Puck (forward stream for Act III) | this reverse |

One deliberate refinement of the design text: §6.3's illustration has the
list pass "reading from Lady Macbeth and writing to Puck's staging". The
validated choreography instead has the list pass read Hecate directly (as the
paragraph pass did in P1 — "Hecate delivers Act I's normalized text, as
today") and uses Macbeth, then Puck, as the staging carriers. The binding
§6.3 constraint — a pass holding nesting frames must not simultaneously use
Macbeth as its ping-pong destination — holds: frames live on Macbeth only
during `PASS_LISTS_*`, which writes to Lady Macbeth. Task 6 does not need to
amend §6.3 (its constraint is stated generally); this note is the record of
the refinement.

Macbeth's stack does double duty **sequentially, never concurrently** (§6.3):
during `PASS_LISTS_*` it holds the open-list frame sentinels (the kind value
per level, above a `STREAM_END` floor); after every list closes it is empty of
frames, and the staging step reuses it as the main carrier.

**Register map during `PASS_LISTS_*`:** Lady Macbeth = input countdown (the
only end-of-input signal; Hecate's stack has no sentinel — Act I is
unchanged); Hecate = current glyph; Macbeth = open-list depth (0/1/2 —
statically restored after every frame pop, because popping overwrites his
value); Horatio = current item's looseness (1/2); Puck = saved marker
character. During `PASS_PARA_*`: Macbeth = current staged item; the rest are
scratch.

**Countdown invariant:** Act I guarantees the normalized text ends with two
newlines (the final-newline restore path — every spike fixture ends with a
newline, so the reference-strip quirk is not in play). Therefore the countdown
can only reach zero immediately after consuming a newline, and only the
newline-consuming scenes guard `Lady Macbeth == 0`. Marker scans mid-line never
run out of input.

**Act IV list invariants** (from Act II construction; the G2 dumps enforce
them): `LIST_ITEM`/`LIST_CLOSE` never reach `SCRIBE_DISPATCH_TOKEN` — they are
consumed by lookahead inside the list flow, so only `LIST_OPEN` gets a dispatch
arm; a `LIST_OPEN` is always followed by a `LIST_ITEM`; a nested `LIST_CLOSE`
is always followed by `LIST_ITEM` or `LIST_CLOSE` while a top-level one never
is — so nested-vs-top close is decided by lookahead and Act IV needs **no depth
register** (Prospero's value is scratch: popped kind, then stashed lookahead;
his stack holds the open kinds).

**Act IV byte rules** (derived from the oracle, verified byte-identical):

| Event | Bytes |
|---|---|
| top-level `LIST_OPEN` | `<ul>\n` / `<ol>\n` |
| nested `LIST_OPEN` (from item text end; `</li>` suppressed) | `\n<ul>` / `\n<ol>` |
| first item in a list | `<li>` (loose: `<li><p>`) |
| subsequent item | `\n<li>` (loose: `\n<li><p>`) |
| loose text interior `\n\n` | `</p>\n\n<p>` |
| item text end | loose: `</p>`; then `</li>` unless a nested `LIST_OPEN` follows |
| nested `LIST_CLOSE` | `</ul></li>` / `</ol></li>` |
| top-level `LIST_CLOSE` | `\n</ul>` / `\n</ol>`, then `\n` at stream end or `\n\n` + dispatch |

**Paragraph pass change:** Slice 1 closed a `PARA` at every newline; P2 closes
only at blank lines (one-glyph lookahead), keeping interior newlines as text —
the `hard_wrapped_boundary` fixture is the oracle case. For Amps and the short
probe every paragraph is single-line, so the emitted streams are unchanged and
the blessed dumps hold. The Slice-1 unconditional leading `PARA` push is
retired (a leading `LIST_OPEN` would corrupt it); paragraphs now open lazily on
the first raw glyph. Empty-input behavior is untouched (the crash is in Act I).

**Expected token streams** (computed by the validated simulation; these are the
Task 5 hand-review contract for the new dumps — one integer per dump line):

```
flat_unordered_tight: 4 1 5 1 97 108 112 104 97 0 5 1 98 101 116 97 0
                      5 1 103 97 109 109 97 0 6
flat_ordered_tight:   4 2 5 1 97 108 112 104 97 0 5 1 98 101 116 97 0
                      5 1 103 97 109 109 97 0 6
indented_continuation: 4 1 5 1 97 108 112 104 97 10 99 111 110 116 105 110
                       117 97 116 105 111 110 0 5 1 98 101 116 97 0 6
loose_second_paragraph: 4 1 5 2 97 108 112 104 97 10 10 115 101 99 111 110
                        100 32 112 97 114 97 103 114 97 112 104 0
                        5 1 98 101 116 97 0 6
nested_one_level:     4 1 5 1 97 108 112 104 97 0 4 2 5 1 98 101 116 97 0
                      5 1 103 97 109 109 97 0 6 5 1 100 101 108 116 97 0 6
hard_wrapped_boundary: 1 72 101 114 101 32 105 115 32 97 32 119 114 97 112
                       112 101 100 32 112 97 114 97 103 114 97 112 104 10
                       56 46 32 79 111 112 115 32 116 104 105 115 32 115
                       116 97 121 115 32 112 97 114 97 103 114 97 112 104
                       32 116 101 120 116 46 0
```

Reading `loose_second_paragraph` as a worked example: `4 1` opens an unordered
list; `5 2` is a loose item whose text is `alpha\n\nsecond paragraph`
(`97 108 112 104 97`, the interior blank `10 10`, then the outdented
continuation) closed by `0`; `5 1` is the tight item `beta`; `6` closes the
list. In `nested_one_level`, note gamma's `0` is followed directly by `6`
(nested close) and then `5 1` for `delta` — the token order Act IV's lookahead
rules depend on.

## Scope narrowings vs the design spec (operator visibility)

The following narrow the design's marker-recognition bullet to what the six
fixtures exercise. Each degrades gracefully to paragraph/continuation text,
none affects a gate fixture, and Slice 4 (full list fixture) is the scheduled
home for lifting them. Task 6 records them in the architecture spec §7.3.

1. **Ordered markers are single-digit** (`0.`–`9.` + whitespace). `10. x`
   becomes paragraph or continuation text. Multi-digit markers would need a
   digit-count register and replay loop this spike does not justify.
2. **Top-level markers take no leading indent** (design said up to 3 spaces).
   An indented top-level marker line becomes paragraph text. Nested markers
   (indent 1–3 inside a list) are fully supported — that is the spike's
   nesting case.
3. **After a blank line inside a list, an indented marker-shaped line is
   loose continuation text, not a nested list.** Probe
   `* a\n  * b\n\n  cont\n* c\n` diverges from the oracle here — it is
   exactly the "nested loose-list combinations" the design excludes.
4. **Whitespace-only lines inside list items are unsupported** (Act I does not
   strip them at Slice-1 scope; no fixture contains one).

Also for the operator: the design's rough budget said ~15–20 new Act II
scenes. The validated machine needs **93** (plus 2 in Act III and 31 in Act
IV): SPL's two-characters-per-scene and one-question-per-branch rules multiply
every state of the line-classification automaton into 1–3 scenes, and each
marker context (block start, in-list line head, indented, post-blank) needs
its own confirm chain because scenes cannot share a return address. The
assembled play grows from 1,911 to ≈4,540 lines (measured through the real
lowerer), which projects to ≈13s cold per run at the measured B14 curve.
Task 5 measures actuals; Task 6 records them. This is a spike finding about
SPL's cost surface, not a dispatcher-shape failure — the pass decomposition
itself validated cleanly.

## Reserved literary surfaces

Reserved at planning time per
`docs/superpowers/notes/correctness-first-spl-workflow.md`. Exact TOML appears
inline in each task. Summary:

- **Scene titles:** Act II — full ledger replacement (97 entries: 4 kept from
  P1, 93 new; retired P1 `PASS_PARA_*` titles are reused verbatim where
  semantics match). Act III — 2 new entries. Act IV — 31 new entries (existing
  entries unchanged; new titles use zero instances of the dull verbs
  tests/opens/closes).
- **Recall lines** (`src/literary.toml`): `lady_macbeth.recall.fallen_rampart
  = "Recall the fallen rampart."`, `lady_macbeth.recall.kept_measure = "Recall
  the kept measure."`, `lady_macbeth.recall.staged_stone = "Recall the staged
  stone."`, `macbeth.recall.masons_stone = "Recall the mason's stone."`,
  `puck.recall.kept_measure = "Recall the kept measure."`,
  `puck.recall.sealed_gates_colour = "Recall the sealed gate's colour."`,
  `juliet.recall.kept_charge = "Recall the kept charge."`
- **Stable-utility `vneg2` phrases** (the `ITEM_START` marker is −2; the
  lowerer requires a phrase for every speaker of a negative constant):
  `hecate = "a rotten toad"`, `horatio = "a miserable beggar"`,
  `lady_macbeth = "a cursed wolf"`, `macbeth = "a foul curse"`,
  `puck = "a vile wolf"` (negative noun + one negative adjective = −2 per
  `docs/spl/reference.md`).
- **Dramatis personae:** Macbeth's preamble line (Task 4):
  `Macbeth, apprentice mason, who steps through the shadowed threshold.`
- **Pointer move:** `iconic_moments.once_more_breach.scene` →
  `PASS_LISTS_BLOCK_START` (its P1 home `PASS_PARA_READ_GLYPH` is retired; the
  title text moves with it).

**Spare scene-title pool** (pre-approved; use only if a structural surprise
forces an extra scene, `pattern = "bare_statement"` unless noted; report use
to the operator):

- Act II (Martial/Catastrophic): `"The wall answers the mason's doubt."`,
  `"A cold stone waits at the threshold."`, `"The keep holds one more
  measure."`, `"The breach is walled anew."`, `"A scout returns with a torn
  banner."`, `"The rampart takes an uncounted stone."`
- Act III (pastoral, lovers): `"The starlit path takes one more word."`,
  `"Morning light falls on the next petal."`, `"The night keeps a silver
  tally."`, `"The garden yields its last rose."`
- Act IV (noble/ceremonial, `scene_of_character`): `"The scribe proves the
  herald's word."`, `"Prospero attends the quiet gate."`, `"The scribe
  bestows one more measure."`, `"Prospero salutes the standing ranks."`

**Spare recall lines** (add under the named speaker only if needed):
`lady_macbeth: watched_gate = "Recall the watched gate."`;
`puck: carried_colour = "Recall the carried colour."`

---
### Task 1: `ITEM_START` framing marker

**Files:**
- Modify: `src_ir/tokens.py`
- Modify: `docs/spl/token-codes.md`
- Test: `tests/test_token_codes.py`

**Interfaces:**
- Consumes: existing `tokens` module.
- Produces: `tokens.ITEM_START = -2`. Task 4's Act II relies on this exact name.

- [ ] **Step 1: Extend the failing test**

In `tests/test_token_codes.py`, replace
`test_framing_markers_are_disjoint_from_token_codes` with:

```python
def test_framing_markers_are_disjoint_from_token_codes() -> None:
    from src_ir import tokens

    assert tokens.TEXT_END == 0
    assert tokens.STREAM_END == -1
    assert tokens.ITEM_START == -2
    codes = {row[1] for row in parse_table()}
    assert tokens.TEXT_END not in codes
    assert tokens.STREAM_END not in codes
    assert tokens.ITEM_START not in codes
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_token_codes.py -q`
Expected: the extended test FAILS with `AttributeError: ... ITEM_START`; the rest PASS.

- [ ] **Step 3: Add the marker**

In `src_ir/tokens.py`, directly below `STREAM_END = -1`, add:

```python
# ITEM_START brackets a list item's text on the intra-Act-II mixed stream
# (list-pass output): [ITEM_START, glyphs..., TEXT_END]. The paragraph pass
# replaces it with the LIST_ITEM code plus the looseness payload from the
# side channel; it never crosses an act boundary, so it never appears in a
# G2 dump. Spoken via stable_utility vneg2 per speaker.
ITEM_START = -2
```

- [ ] **Step 4: Extend `docs/spl/token-codes.md`**

Append to the Framing markers table:

```markdown
| ITEM_START | −2 | brackets a list item's text on Act II's intra-act mixed stream (pass-internal; never crosses an act boundary) |
```

and change the sentence above the table from "Spoken through each speaker's
`stable_utility` `v0`/`vneg1` pools" to "Spoken through each speaker's
`stable_utility` `v0`/`vneg1`/`vneg2` pools".

- [ ] **Step 5: Verify, regen identity, lint, commit**

```bash
uv run pytest tests/test_token_codes.py tests/test_stream_recipes.py -q
uv run python -m scripts.splc && git diff --exit-code src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl src/40-act4-emit.spl debug/40-act4-token-dump.spl
uv run ruff check . && uv run ruff format . && uv run pyright
git add src_ir/tokens.py docs/spl/token-codes.md tests/test_token_codes.py
git commit -m "chore: add item-start framing marker to the stream contract"
```

Expected: tests pass; no fragment diff (nothing consumes the marker yet).

---
### Task 2: Act III traversal dispatch over the arity table

Replaces the P1 PARA-only copy in `TRAVERSE_NEXT_TOKEN` with a dispatch
generated over `tokens.ARITY`, plus two payload-copy scenes. Fixture-visible
behavior is unchanged (list codes do not exist on the stream until Task 4);
the Amps/short dumps must stay byte-equal.

**Files:**
- Modify: `src_ir/act3.py`
- Modify: `src/30-act3-literary.toml` (2 additions)
- Modify: `src/literary.toml` (1 recall key)
- Modify (generated): `src/30-act3-span.spl`, `shakedown.spl`

**Interfaces:**
- Consumes: `tokens.ARITY`, `tokens.STREAM_END`; Act II's sentinel-seeded Puck stack.
- Produces: labels `TRAVERSE_COPY_PAYLOAD_NEXT` / `TRAVERSE_COPY_PAYLOAD_TEXT`; the dispatch that Task 4's list tokens flow through. Later slices extend the vocabulary by adding `ARITY` rows — the dispatch regenerates.

- [ ] **Step 1: Edit `src_ir/act3.py`**

**(a)** Update the module docstring's first line from
`"""Act III — span pass over the tokenized stream (Spike A P1). Traversal`
to
`"""Act III — span pass over the tokenized stream (Spike A P2). Traversal`.

**(b)** Delete the P1 module-level guard (the comment starting
`# P1 traverses PARA-only streams` and the
`assert tokens.ARITY[tokens.PARA] == tokens.TokenArity(0, True)` line) and put
this in its place:

```python
# Traversal routes per arity shape: (payloads, has_text). Codes with neither
# payloads nor text copy through and loop; unknown shapes fail the build.
_ARITY_ROUTE = {
    (0, True): "TRAVERSE_OPEN_TEXT",
    (1, False): "TRAVERSE_COPY_PAYLOAD_NEXT",
    (1, True): "TRAVERSE_COPY_PAYLOAD_TEXT",
}


def _traverse_dispatch() -> list[Op]:
    """The token-code dispatch, generated over the arity table. Codes with
    neither payloads nor text ((0, False)) copy through and take the final
    goto back to the token loop."""
    ops: list[Op] = [
        pop(PUCK, recall="nights_next_word"),
        branch(
            eq(val(PUCK), const(tokens.STREAM_END)), then="LYRIC_OPEN_REVERSE"
        ),
        push(JULIET, val(PUCK)),
    ]
    for code, arity in sorted(tokens.ARITY.items()):
        shape = (arity.payloads, arity.has_text)
        if shape == (0, False):
            continue
        if shape not in _ARITY_ROUTE:
            raise ValueError(f"token {code}: unsupported arity {shape}")
        ops.append(branch(eq(val(PUCK), const(code)), then=_ARITY_ROUTE[shape]))
    ops.append(goto("TRAVERSE_NEXT_TOKEN"))
    return ops
```

**(c)** Replace the `TRAVERSE_NEXT_TOKEN` scene (the whole
`scene("TRAVERSE_NEXT_TOKEN", ...)` entry including its `# PARA (build-time
assert above)` comment) with these three scenes:

```python
        scene(
            "TRAVERSE_NEXT_TOKEN",
            *_traverse_dispatch(),
            anchor=JULIET,
        ),
        scene(
            "TRAVERSE_COPY_PAYLOAD_NEXT",
            pop(PUCK, recall="kept_charge"),
            push(JULIET, val(PUCK)),
            goto("TRAVERSE_NEXT_TOKEN"),
            anchor=JULIET,
        ),
        scene(
            "TRAVERSE_COPY_PAYLOAD_TEXT",
            pop(PUCK, recall="kept_charge"),
            push(JULIET, val(PUCK)),
            goto("TRAVERSE_OPEN_TEXT"),
            anchor=JULIET,
        ),
```

Every other scene in the module is byte-unchanged.

- [ ] **Step 2: Reserve the controlled surfaces**

Add to `src/30-act3-literary.toml` (alphabetical position):

```toml
[scenes.TRAVERSE_COPY_PAYLOAD_NEXT]
title = "The night carries the word's charge onward."
pattern = "bare_statement"

[scenes.TRAVERSE_COPY_PAYLOAD_TEXT]
title = "The night carries the charge to the garden."
pattern = "bare_statement"
```

In `src/literary.toml`, add to `[characters.juliet.recall]`:

```toml
kept_charge = "Recall the kept charge."
```

- [ ] **Step 3: Regenerate and gate**

```bash
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --stat src/10-act1-preprocess.spl src/20-act2-block.spl src/40-act4-emit.spl debug/40-act4-token-dump.spl
uv run pytest tests/test_token_dump.py -q
uv run pytest -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q
```

Expected: only `src/30-act3-span.spl` and `shakedown.spl` change; the blessed
amps/short dump tests pass unchanged; full suite green, same pass/xfail shape.

- [ ] **Step 4: Lint, type-check, commit**

```bash
uv run ruff check . && uv run ruff format . && uv run pyright
git add src_ir/act3.py src/30-act3-literary.toml src/literary.toml src/30-act3-span.spl shakedown.spl
git commit -m "refactor: dispatch act three traversal over the arity table"
```

---
### Task 3: Act IV list emission

Full-module rewrite: the paragraph/anchor scenes are byte-identical to P1;
the dispatch chain gains one `LIST_OPEN` arm; 31 list-emission scenes land
(unreachable until Task 4 emits list tokens, so every existing fixture stays
green). The byte rules and invariants are in §Contract and choreography.

**Files:**
- Modify: `src_ir/act4.py` (full replacement below)
- Modify: `src/40-act4-literary.toml` (31 additions)
- Modify: `src/literary.toml` (1 recall key)
- Modify (generated): `src/40-act4-emit.spl`, `shakedown.spl`

**Interfaces:**
- Consumes: `tokens.LIST_OPEN`/`LIST_ITEM`/`LIST_CLOSE`/`TEXT_END`/`STREAM_END`; Act III's sentinel-seeded Puck stack.
- Produces: the list-flow scene group `SCRIBE_LIST_OPEN` … `SCRIBE_EMIT_LIST_BLOCK_SEP` that Task 4's token streams drive; Prospero's stack as the list-kind stack.

- [ ] **Step 1: Replace `src_ir/act4.py` with:**

```python
"""Act IV — emit pass over the tokenized stream (Spike A P2). Prospero
anchors and speaks; Puck carries the current token / scratch. Dispatch pops
until the STREAM_END sentinel; paragraph emission is the Slice-1 port
unchanged (docs/superpowers/notes/act4-port-audit.md); list emission follows
the P2 plan's oracle-derived byte rules.

List-flow invariants (from Act II construction, enforced by the G2 dumps):
- LIST_ITEM (5) and LIST_CLOSE (6) never reach SCRIBE_DISPATCH_TOKEN; they
  are consumed by lookahead inside the list flow. Only LIST_OPEN needs a
  dispatch arm.
- A LIST_OPEN is always followed by a LIST_ITEM.
- A nested LIST_CLOSE is always followed by LIST_ITEM or LIST_CLOSE; a
  top-level LIST_CLOSE never is — so close depth is decided by lookahead
  and no depth register is needed.
- Prospero's value is scratch (popped kind, then stashed lookahead);
  Prospero's stack holds the open list kinds."""

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
    push,
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


def _bytes(text: str) -> list[int]:
    return list(text.encode())


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
                else_="SCRIBE_TEST_LIST_OPEN",
            ),
            companion=PUCK,
        ),
        # Dispatch arm (only LIST_OPEN reaches the top-level chain).
        scene(
            "SCRIBE_TEST_LIST_OPEN",
            branch(
                eq(val(PUCK), const(tokens.LIST_OPEN)),
                then="SCRIBE_LIST_OPEN",
                else_="SCRIBE_TEST_ANCHOR_OPEN",
            ),
            companion=PUCK,
        ),
        # List open: kind onto Prospero's stack. Top-level opens arrive from the
        # dispatch chain; nested opens arrive from SCRIBE_ITEM_END.
        scene(
            "SCRIBE_LIST_OPEN",
            pop(PUCK, recall="heralds_present_word"),
            push(PROSPERO, val(PUCK)),
            branch(
                eq(val(PUCK), const(1)),
                then="SCRIBE_EMIT_UL_OPEN_TOP",
                else_="SCRIBE_EMIT_OL_OPEN_TOP",
            ),
        ),
        scene(
            "SCRIBE_EMIT_UL_OPEN_TOP",
            # <ul>\n
            *_emit(*_bytes("<ul>"), 10),
            goto("SCRIBE_ITEM_FIRST"),
        ),
        scene(
            "SCRIBE_EMIT_OL_OPEN_TOP",
            # <ol>\n
            *_emit(*_bytes("<ol>"), 10),
            goto("SCRIBE_ITEM_FIRST"),
        ),
        scene(
            "SCRIBE_NESTED_OPEN",
            # Reached from an item's text end: the enclosing <li> stays open.
            pop(PUCK, recall="heralds_present_word"),
            push(PROSPERO, val(PUCK)),
            branch(
                eq(val(PUCK), const(1)),
                then="SCRIBE_EMIT_UL_OPEN_NESTED",
                else_="SCRIBE_EMIT_OL_OPEN_NESTED",
            ),
        ),
        scene(
            "SCRIBE_EMIT_UL_OPEN_NESTED",
            # \n<ul>
            *_emit(10, *_bytes("<ul>")),
            goto("SCRIBE_ITEM_FIRST"),
        ),
        scene(
            "SCRIBE_EMIT_OL_OPEN_NESTED",
            # \n<ol>
            *_emit(10, *_bytes("<ol>")),
            goto("SCRIBE_ITEM_FIRST"),
        ),
        # Items. A LIST_OPEN is always followed by a LIST_ITEM, so the first-item
        # entry consumes the item code directly; subsequent items arrive with
        # their code already consumed by the </li> lookahead.
        scene(
            "SCRIBE_ITEM_FIRST",
            pop(PUCK, recall="heralds_present_word"),
            goto("SCRIBE_ITEM_LOOSENESS"),
        ),
        scene(
            "SCRIBE_ITEM_SUBSEQUENT",
            # \n between </li> and the next <li>
            *_emit(10),
            goto("SCRIBE_ITEM_LOOSENESS"),
        ),
        scene(
            "SCRIBE_ITEM_LOOSENESS",
            pop(PUCK, recall="heralds_present_word"),
            branch(
                eq(val(PUCK), const(2)),
                then="SCRIBE_EMIT_ITEM_OPEN_LOOSE",
                else_="SCRIBE_EMIT_ITEM_OPEN_TIGHT",
            ),
        ),
        scene(
            "SCRIBE_EMIT_ITEM_OPEN_TIGHT",
            *_emit(*_bytes("<li>")),
            goto("SCRIBE_ITEM_TEXT_TIGHT"),
        ),
        scene(
            "SCRIBE_ITEM_TEXT_TIGHT",
            pop(PUCK, recall="heralds_present_word"),
            branch(eq(val(PUCK), const(tokens.TEXT_END)), then="SCRIBE_ITEM_END"),
            print_char(PUCK),
            goto("SCRIBE_ITEM_TEXT_TIGHT"),
        ),
        scene(
            "SCRIBE_EMIT_ITEM_OPEN_LOOSE",
            *_emit(*_bytes("<li><p>")),
            goto("SCRIBE_ITEM_TEXT_LOOSE"),
        ),
        scene(
            "SCRIBE_ITEM_TEXT_LOOSE",
            pop(PUCK, recall="heralds_present_word"),
            branch(
                eq(val(PUCK), const(tokens.TEXT_END)),
                then="SCRIBE_EMIT_LOOSE_END",
            ),
            branch(eq(val(PUCK), const(10)), then="SCRIBE_LOOSE_NEWLINE"),
            print_char(PUCK),
            goto("SCRIBE_ITEM_TEXT_LOOSE"),
        ),
        scene(
            "SCRIBE_LOOSE_NEWLINE",
            # Two newlines mark a paragraph break inside the loose item; one is
            # literal text. Stash the lookahead glyph before _emit reuses Puck.
            pop(PUCK, recall="heralds_parting_word"),
            branch(eq(val(PUCK), const(10)), then="SCRIBE_EMIT_PARAGRAPH_BREAK"),
            let(PROSPERO, val(PUCK)),
            goto("SCRIBE_LOOSE_NEWLINE_GLYPH"),
        ),
        scene(
            "SCRIBE_LOOSE_NEWLINE_GLYPH",
            *_emit(10),
            let(PUCK, val(PROSPERO)),
            print_char(PUCK),
            goto("SCRIBE_ITEM_TEXT_LOOSE"),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_BREAK",
            # </p>\n\n<p>
            *_emit(*_bytes("</p>"), 10, 10, *_bytes("<p>")),
            goto("SCRIBE_ITEM_TEXT_LOOSE"),
        ),
        scene(
            "SCRIBE_EMIT_LOOSE_END",
            *_emit(*_bytes("</p>")),
            goto("SCRIBE_ITEM_END"),
            companion=PROSPERO,
        ),
        scene(
            "SCRIBE_ITEM_END",
            # Lookahead: a nested LIST_OPEN keeps this <li> open.
            pop(PUCK, recall="heralds_parting_word"),
            branch(
                eq(val(PUCK), const(tokens.LIST_OPEN)), then="SCRIBE_NESTED_OPEN"
            ),
            let(PROSPERO, val(PUCK)),
            goto("SCRIBE_EMIT_LI_CLOSE"),
        ),
        scene(
            "SCRIBE_EMIT_LI_CLOSE",
            # The lookahead (LIST_ITEM or LIST_CLOSE) is stashed in Prospero.
            *_emit(*_bytes("</li>")),
            branch(
                eq(val(PROSPERO), const(tokens.LIST_ITEM)),
                then="SCRIBE_ITEM_SUBSEQUENT",
            ),
            goto("SCRIBE_LIST_CLOSE"),
        ),
        # List close. Entered with the LIST_CLOSE code already consumed. Pops
        # the kind, then one lookahead token; the lookahead picks nested vs top.
        scene(
            "SCRIBE_LIST_CLOSE",
            pop(PROSPERO, recall="sealed_gates_colour"),
            pop(PUCK, recall="heralds_parting_word"),
            branch(
                eq(val(PUCK), const(tokens.LIST_ITEM)), then="SCRIBE_NESTED_CLOSE"
            ),
            branch(
                eq(val(PUCK), const(tokens.LIST_CLOSE)),
                then="SCRIBE_NESTED_CLOSE",
            ),
            goto("SCRIBE_TOP_CLOSE"),
        ),
        scene(
            "SCRIBE_NESTED_CLOSE",
            branch(
                eq(val(PROSPERO), const(1)),
                then="SCRIBE_STASH_UL_CLOSE_NESTED",
                else_="SCRIBE_STASH_OL_CLOSE_NESTED",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_STASH_UL_CLOSE_NESTED",
            # Kind is consumed by the branch above; stash the lookahead before
            # emission reuses Puck.
            let(PROSPERO, val(PUCK)),
            # </ul></li> — the parent item closes with the nested list.
            *_emit(*_bytes("</ul></li>")),
            goto("SCRIBE_AFTER_NESTED_CLOSE"),
        ),
        scene(
            "SCRIBE_STASH_OL_CLOSE_NESTED",
            let(PROSPERO, val(PUCK)),
            *_emit(*_bytes("</ol></li>")),
            goto("SCRIBE_AFTER_NESTED_CLOSE"),
        ),
        scene(
            "SCRIBE_AFTER_NESTED_CLOSE",
            branch(
                eq(val(PROSPERO), const(tokens.LIST_ITEM)),
                then="SCRIBE_ITEM_SUBSEQUENT",
            ),
            # Otherwise the stashed lookahead is another LIST_CLOSE, already
            # consumed — exactly SCRIBE_LIST_CLOSE's entry state.
            goto("SCRIBE_LIST_CLOSE"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_TOP_CLOSE",
            branch(
                eq(val(PROSPERO), const(1)),
                then="SCRIBE_STASH_UL_CLOSE_TOP",
                else_="SCRIBE_STASH_OL_CLOSE_TOP",
            ),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_STASH_UL_CLOSE_TOP",
            let(PROSPERO, val(PUCK)),
            # \n</ul>
            *_emit(10, *_bytes("</ul>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_STASH_OL_CLOSE_TOP",
            let(PROSPERO, val(PUCK)),
            *_emit(10, *_bytes("</ol>")),
            goto("SCRIBE_LIST_BLOCK_SEP"),
        ),
        scene(
            "SCRIBE_LIST_BLOCK_SEP",
            branch(
                eq(val(PROSPERO), const(tokens.STREAM_END)),
                then="SCRIBE_EMIT_FINAL_LIST_NEWLINE",
            ),
            goto("SCRIBE_EMIT_LIST_BLOCK_SEP"),
            companion=PUCK,
        ),
        scene(
            "SCRIBE_EMIT_FINAL_LIST_NEWLINE",
            *_emit(10),
            goto("ACT_IV_DONE"),
        ),
        scene(
            "SCRIBE_EMIT_LIST_BLOCK_SEP",
            *_emit(10, 10),
            let(PUCK, val(PROSPERO)),
            goto("SCRIBE_DISPATCH_TOKEN"),
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
            # item to choose the final (single-newline) close. Stashed in
            # Prospero (his count register is retired) because _emit's
            # per-byte loop below overwrites Puck's value.
            pop(PUCK, recall="heralds_parting_word"),
            let(PROSPERO, val(PUCK)),
            branch(
                eq(val(PUCK), const(tokens.STREAM_END)),
                then="SCRIBE_EMIT_FINAL_PARAGRAPH_CLOSE",
                else_="SCRIBE_EMIT_PARAGRAPH_CLOSE",
            ),
        ),
        scene(
            "SCRIBE_EMIT_PARAGRAPH_CLOSE",
            # </p>\n\n — then recall the stashed lookahead and dispatch it.
            *_emit(60, 47, 112, 62, 10, 10),
            let(PUCK, val(PROSPERO)),
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

- [ ] **Step 2: Reserve the controlled surfaces**

Add to `src/40-act4-literary.toml` (alphabetical position with the existing
entries):

```toml
[scenes.SCRIBE_TEST_LIST_OPEN]
title = "Prospero weighs the gate of ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_LIST_OPEN]
title = "Prospero admits the gathered ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_UL_OPEN_TOP]
title = "Prospero unfurls the rough ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_OL_OPEN_TOP]
title = "Prospero unfurls the numbered ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_NESTED_OPEN]
title = "Prospero admits an inner troop."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_UL_OPEN_NESTED]
title = "Prospero unfurls the inner rough ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_OL_OPEN_NESTED]
title = "Prospero unfurls the inner numbered ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_ITEM_FIRST]
title = "The first soldier steps forward."
pattern = "bare_statement"

[scenes.SCRIBE_ITEM_SUBSEQUENT]
title = "Another soldier steps forward."
pattern = "bare_statement"

[scenes.SCRIBE_ITEM_LOOSENESS]
title = "Prospero weighs each soldier's bearing."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_ITEM_OPEN_TIGHT]
title = "Prospero grants the soldier his place."
pattern = "scene_of_character"

[scenes.SCRIBE_ITEM_TEXT_TIGHT]
title = "The soldier speaks his plain words."
pattern = "bare_statement"

[scenes.SCRIBE_EMIT_ITEM_OPEN_LOOSE]
title = "Prospero grants the soldier a wide chamber."
pattern = "scene_of_character"

[scenes.SCRIBE_ITEM_TEXT_LOOSE]
title = "The soldier speaks at his ease."
pattern = "bare_statement"

[scenes.SCRIBE_LOOSE_NEWLINE]
title = "Prospero weighs the pause within."
pattern = "scene_of_character"

[scenes.SCRIBE_LOOSE_NEWLINE_GLYPH]
title = "The pause passes and speech resumes."
pattern = "bare_statement"

[scenes.SCRIBE_EMIT_PARAGRAPH_BREAK]
title = "Prospero parts the chamber in two."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_LOOSE_END]
title = "Prospero seals the wide chamber."
pattern = "scene_of_character"

[scenes.SCRIBE_ITEM_END]
title = "Prospero hears the soldier's last word."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_LI_CLOSE]
title = "Prospero seals the soldier's place."
pattern = "scene_of_character"

[scenes.SCRIBE_LIST_CLOSE]
title = "Prospero receives the barred gate."
pattern = "scene_of_character"

[scenes.SCRIBE_NESTED_CLOSE]
title = "Prospero pronounces on the inner gate."
pattern = "scene_of_character"

[scenes.SCRIBE_STASH_UL_CLOSE_NESTED]
title = "Prospero bars the inner rough ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_STASH_OL_CLOSE_NESTED]
title = "Prospero bars the inner numbered ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_AFTER_NESTED_CLOSE]
title = "The inner gate yields to the outer march."
pattern = "bare_statement"

[scenes.SCRIBE_TOP_CLOSE]
title = "Prospero pronounces on the outer gate."
pattern = "scene_of_character"

[scenes.SCRIBE_STASH_UL_CLOSE_TOP]
title = "Prospero bars the rough ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_STASH_OL_CLOSE_TOP]
title = "Prospero bars the numbered ranks."
pattern = "scene_of_character"

[scenes.SCRIBE_LIST_BLOCK_SEP]
title = "Prospero weighs the parting word."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_FINAL_LIST_NEWLINE]
title = "Prospero releases the final measure."
pattern = "scene_of_character"

[scenes.SCRIBE_EMIT_LIST_BLOCK_SEP]
title = "The scribe inscribes a waiting seal."
pattern = "scene_of_character"
```

In `src/literary.toml`, add to `[characters.puck.recall]`:

```toml
sealed_gates_colour = "Recall the sealed gate's colour."
```

- [ ] **Step 3: Regenerate and gate**

```bash
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --stat src/10-act1-preprocess.spl src/20-act2-block.spl src/30-act3-span.spl debug/40-act4-token-dump.spl
uv run pytest tests/test_token_dump.py -q
uv run pytest -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q
```

Expected: only `src/40-act4-emit.spl` and `shakedown.spl` change; amps/short
dumps byte-equal; full suite green, same shape. Watch
`test_act_iv_scene_titles_use_ceremonial_verb_variety` (the 31 new titles add
zero uses of tests/opens/closes — the budget stays 0/1/1).

- [ ] **Step 4: Lint, type-check, commit**

```bash
uv run ruff check . && uv run ruff format . && uv run pyright
git add src_ir/act4.py src/40-act4-literary.toml src/literary.toml src/40-act4-emit.spl shakedown.spl
git commit -m "feat: emit list html from act four"
```

---
### Task 4: Act II list pass + paragraph pass

The activation task: Act II becomes the two-pass dispatcher and list tokens
flow end-to-end. After this task the six list spike tests flip from `xfail`
to `XPASS` (their marks use `strict=False`; Task 5 removes them). Macbeth
enters production for the first time — his dramatis personae line is part of
this task.

**Files:**
- Modify: `src_ir/act2.py` (full replacement below)
- Modify: `src/20-act2-literary.toml` (full replacement below)
- Modify: `src/literary.toml` (recall keys, `vneg2` phrases, one pointer move)
- Modify: `src/00-preamble.spl` (Macbeth's line — hand-authored fragment)
- Modify (generated): `src/20-act2-block.spl`, `shakedown.spl`

**Interfaces:**
- Consumes: Task 1's `tokens.ITEM_START`; Tasks 2–3's traversal and emission; `emit_token`; the full cast.
- Produces: the tokenized stream on Puck exactly as §Contract specifies; scene-group prefixes `PASS_LISTS_*` / `PASS_PARA_*` that future passes (headers, HR, code, blockquotes — later slices) slot between.

- [ ] **Step 1: Replace `src_ir/act2.py` with:**

```python
"""Act II — block dispatcher (Spike A P2): list pass + paragraph pass.

Carrier choreography (design spec ping-pong, §6.3):
  PASS_LISTS:   Hecate (glyphs, countdown on Lady Macbeth) -> Lady Macbeth
  STAGE:        Lady Macbeth -> Macbeth (main); Horatio -> Puck (side)
  PASS_PARA:    Macbeth (+ Puck side) -> Lady Macbeth
  FRAME_REVERSE: Lady Macbeth -> Puck (unchanged from P1)

Registers during PASS_LISTS: Lady Macbeth = input countdown; Hecate = current
glyph; Macbeth = open-list depth (statically restored after frame pops);
Horatio = current item looseness (1 tight / 2 loose); Puck = saved marker
char. Macbeth's stack holds the open-list frame sentinels (kind per level)
above a -1 floor; Horatio's stack is the per-item looseness side channel
above a -1 floor.

The list pass emits item text directly onto the carrier bracketed as
[ITEM_START(-2), glyphs..., 0]; the item's looseness is pushed onto the side
channel at item end (completion order). PASS_PARA replaces each ITEM_START
with the LIST_ITEM code and the next side-channel value (the STAGE reverse
flips the side stack so first-completed pops first).
"""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    act,
    add,
    branch,
    const,
    eq,
    goto,
    gt,
    halt_act,
    let,
    lt,
    pop,
    push,
    scene,
    sub,
    val,
)
from src_ir import tokens
from src_ir.cast import (
    HECATE,
    HORATIO,
    LADY_MACBETH,
    MACBETH,
    PUCK,
)
from src_ir.stream import emit_token

_NEWLINE = const(10)
_SPACE = const(32)
_TAB = const(9)
_END = const(tokens.STREAM_END)


def _read(recall: str = "hewn_glyph"):
    """Pop the next input glyph into Hecate and decrement the countdown."""
    return [
        pop(HECATE, recall=recall),
        let(LADY_MACBETH, sub(val(LADY_MACBETH), const(1))),
    ]


ACT: Act = act(
    2,
    LADY_MACBETH,
    [
        # --- Frame entry: seed the carrier, side-channel, and frame floors.
        scene(
            "ACT_II_START",
            let(LADY_MACBETH, val(HORATIO)),
            push(LADY_MACBETH, _END),
            push(HORATIO, _END),
            goto("PASS_LISTS_SEED_FRAMES"),
        ),
        scene(
            "PASS_LISTS_SEED_FRAMES",
            push(MACBETH, _END),
            let(MACBETH, const(0)),
            goto("PASS_LISTS_BLOCK_START"),
        ),
        # --- Block-start gate: list markers only at doc start / after blank.
        scene(
            "PASS_LISTS_BLOCK_START",
            *_read(),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_LISTS_BLOCK_BLANK",
                else_="PASS_LISTS_GATE_UNORDERED",
            ),
        ),
        scene(
            "PASS_LISTS_BLOCK_BLANK",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_LISTS_DONE",
                else_="PASS_LISTS_BLOCK_START",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_GATE_UNORDERED",
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_MARK_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_MARK_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_MARK_SAVE_UL"),
            goto("PASS_LISTS_GATE_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_GATE_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_RAW_GLYPH"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_RAW_GLYPH"),
            goto("PASS_LISTS_MARK_SAVE_OL"),
            companion=HECATE,
        ),
        # --- Marker confirmation at block start.
        scene(
            "PASS_LISTS_MARK_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_MARK_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_MARK_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_OPEN_UL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_OPEN_UL"),
            goto("PASS_LISTS_RAW_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_MARK_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_MARK_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_MARK_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_MARK_TEST_OL"),
            goto("PASS_LISTS_RAW_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_MARK_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_OPEN_OL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_OPEN_OL"),
            goto("PASS_LISTS_RAW_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_RAW_REPLAY_SAVED",
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_RAW_REPLAY_SAVED_DOT",
            push(LADY_MACBETH, val(PUCK)),
            push(LADY_MACBETH, const(46)),
            goto("PASS_LISTS_RAW_GLYPH"),
            companion=PUCK,
        ),
        # --- Raw copy mode: non-list text flows through untouched.
        scene(
            "PASS_LISTS_RAW_GLYPH",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_LISTS_RAW_AFTER_NEWLINE",
                else_="PASS_LISTS_RAW_NEXT",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_RAW_NEXT",
            *_read(),
            goto("PASS_LISTS_RAW_GLYPH"),
        ),
        scene(
            "PASS_LISTS_RAW_AFTER_NEWLINE",
            branch(eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_DONE"),
            *_read("blank_glyph"),
            branch(
                eq(val(HECATE), _NEWLINE),
                then="PASS_LISTS_RAW_BLANK",
                else_="PASS_LISTS_RAW_GLYPH",
            ),
        ),
        scene(
            "PASS_LISTS_RAW_BLANK",
            push(LADY_MACBETH, val(HECATE)),
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_LISTS_DONE",
                else_="PASS_LISTS_BLOCK_START",
            ),
            companion=HECATE,
        ),
        # --- List open: token, frame sentinel, first item.
        scene(
            "PASS_LISTS_OPEN_UL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 1),
            push(MACBETH, const(1)),
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        scene(
            "PASS_LISTS_OPEN_OL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 2),
            push(MACBETH, const(2)),
            let(MACBETH, add(val(MACBETH), const(1))),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        scene(
            "PASS_LISTS_ITEM_BEGIN_TIGHT",
            let(HORATIO, const(1)),
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            goto("PASS_LISTS_ITEM_SKIP_SPACES"),
        ),
        scene(
            "PASS_LISTS_ITEM_BEGIN_LOOSE",
            let(HORATIO, const(2)),
            push(LADY_MACBETH, const(tokens.ITEM_START)),
            goto("PASS_LISTS_ITEM_SKIP_SPACES"),
        ),
        scene(
            "PASS_LISTS_ITEM_SKIP_SPACES",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_ITEM_SKIP_SPACES"),
            goto("PASS_LISTS_ITEM_GLYPH"),
        ),
        # --- Item text: glyphs flow directly onto the carrier.
        scene(
            "PASS_LISTS_ITEM_GLYPH",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_ITEM_LINE_END"),
            push(LADY_MACBETH, val(HECATE)),
            goto("PASS_LISTS_ITEM_NEXT"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_ITEM_NEXT",
            *_read(),
            goto("PASS_LISTS_ITEM_GLYPH"),
        ),
        scene(
            "PASS_LISTS_ITEM_LINE_END",
            branch(
                eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_END_OF_INPUT"
            ),
            *_read(),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_1"),
            goto("PASS_LISTS_LINE_HEAD"),
        ),
        # --- Line head at indent 0 inside a list: sibling marker or lazy text.
        scene(
            "PASS_LISTS_LINE_HEAD",
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_SIB_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_SIB_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_SIB_SAVE_UL"),
            goto("PASS_LISTS_LINE_HEAD_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_LINE_HEAD_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_JOIN_LINE"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_JOIN_LINE"),
            goto("PASS_LISTS_SIB_SAVE_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_JOIN_LINE",
            push(LADY_MACBETH, _NEWLINE),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_SIB_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_SIB_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_SIB_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_SIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_SIB_EMIT"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_SIB_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_SIB_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_SIB_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_SIB_TEST_OL"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_SIB_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_SIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_SIB_EMIT"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_LAZY_REPLAY_SAVED",
            push(LADY_MACBETH, _NEWLINE),
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_LAZY_REPLAY_SAVED_DOT",
            push(LADY_MACBETH, _NEWLINE),
            push(LADY_MACBETH, val(PUCK)),
            push(LADY_MACBETH, const(46)),
            goto("PASS_LISTS_ITEM_GLYPH"),
            companion=PUCK,
        ),
        scene(
            "PASS_LISTS_SIB_EMIT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            branch(
                eq(val(MACBETH), const(2)),
                then="PASS_LISTS_SIB_OUTDENT",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
        ),
        scene(
            "PASS_LISTS_SIB_OUTDENT",
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            let(MACBETH, const(1)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        # --- Indented line inside a list (no blank): nested marker or
        # --- outdented continuation (up to four spaces stripped).
        scene(
            "PASS_LISTS_INDENT_1",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_2"),
            goto("PASS_LISTS_INDENT_CLASSIFY"),
        ),
        scene(
            "PASS_LISTS_INDENT_2",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_3"),
            goto("PASS_LISTS_INDENT_CLASSIFY"),
        ),
        scene(
            "PASS_LISTS_INDENT_3",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_INDENT_4"),
            goto("PASS_LISTS_INDENT_CLASSIFY"),
        ),
        scene(
            "PASS_LISTS_INDENT_4",
            push(LADY_MACBETH, _NEWLINE),
            *_read(),
            goto("PASS_LISTS_ITEM_GLYPH"),
        ),
        scene(
            "PASS_LISTS_INDENT_CLASSIFY",
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_NEST_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_NEST_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_NEST_SAVE_UL"),
            goto("PASS_LISTS_INDENT_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_INDENT_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_JOIN_LINE"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_JOIN_LINE"),
            goto("PASS_LISTS_NEST_SAVE_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_NEST_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_NEST_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_NEST_EMIT_UL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_NEST_EMIT_UL"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_NEST_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_NEST_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_NEST_TEST_OL"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_NEST_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_NEST_EMIT_OL"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_NEST_EMIT_OL"),
            goto("PASS_LISTS_LAZY_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_NEST_EMIT_UL",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            branch(
                eq(val(MACBETH), const(1)),
                then="PASS_LISTS_NEST_OPEN_UL",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
        ),
        scene(
            "PASS_LISTS_NEST_EMIT_OL",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            branch(
                eq(val(MACBETH), const(1)),
                then="PASS_LISTS_NEST_OPEN_OL",
                else_="PASS_LISTS_ITEM_BEGIN_TIGHT",
            ),
        ),
        scene(
            "PASS_LISTS_NEST_OPEN_UL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 1),
            push(MACBETH, const(1)),
            let(MACBETH, const(2)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        scene(
            "PASS_LISTS_NEST_OPEN_OL",
            *emit_token(LADY_MACBETH, tokens.LIST_OPEN, 2),
            push(MACBETH, const(2)),
            let(MACBETH, const(2)),
            goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
        ),
        # --- Blank line inside a list: continuation, sibling, or list end.
        scene(
            "PASS_LISTS_BLANK",
            branch(
                eq(val(LADY_MACBETH), const(0)), then="PASS_LISTS_END_OF_INPUT"
            ),
            *_read("blank_glyph"),
            branch(eq(val(HECATE), _NEWLINE), then="PASS_LISTS_BLANK"),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_1"),
            goto("PASS_LISTS_BLANK_HEAD"),
        ),
        scene(
            "PASS_LISTS_BLANK_HEAD",
            branch(eq(val(HECATE), const(42)), then="PASS_LISTS_BSIB_SAVE_UL"),
            branch(eq(val(HECATE), const(43)), then="PASS_LISTS_BSIB_SAVE_UL"),
            branch(eq(val(HECATE), const(45)), then="PASS_LISTS_BSIB_SAVE_UL"),
            goto("PASS_LISTS_BLANK_HEAD_ORDERED"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_BLANK_HEAD_ORDERED",
            branch(lt(val(HECATE), const(48)), then="PASS_LISTS_LIST_END"),
            branch(gt(val(HECATE), const(57)), then="PASS_LISTS_LIST_END"),
            goto("PASS_LISTS_BSIB_SAVE_OL"),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_BSIB_SAVE_UL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_BSIB_TEST_UL"),
        ),
        scene(
            "PASS_LISTS_BSIB_TEST_UL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BSIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_BSIB_EMIT"),
            goto("PASS_LISTS_LIST_END_REPLAY"),
        ),
        scene(
            "PASS_LISTS_BSIB_SAVE_OL",
            let(PUCK, val(HECATE)),
            goto("PASS_LISTS_BSIB_TEST_DOT"),
        ),
        scene(
            "PASS_LISTS_BSIB_TEST_DOT",
            *_read(),
            branch(eq(val(HECATE), const(46)), then="PASS_LISTS_BSIB_TEST_OL"),
            goto("PASS_LISTS_LIST_END_REPLAY"),
        ),
        scene(
            "PASS_LISTS_BSIB_TEST_OL",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BSIB_EMIT"),
            branch(eq(val(HECATE), _TAB), then="PASS_LISTS_BSIB_EMIT"),
            goto("PASS_LISTS_LIST_END_REPLAY_DOT"),
        ),
        scene(
            "PASS_LISTS_BSIB_EMIT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            let(HORATIO, const(2)),
            push(HORATIO, val(HORATIO)),
            branch(
                eq(val(MACBETH), const(2)),
                then="PASS_LISTS_BSIB_OUTDENT",
                else_="PASS_LISTS_ITEM_BEGIN_LOOSE",
            ),
        ),
        scene(
            "PASS_LISTS_BSIB_OUTDENT",
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            pop(MACBETH, recall="fallen_rampart"),
            let(MACBETH, const(1)),
            goto("PASS_LISTS_ITEM_BEGIN_LOOSE"),
        ),
        # Blank + indented continuation: the item is loose; the blank and the
        # outdented line join its text.
        scene(
            "PASS_LISTS_BLANK_INDENT_1",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_2"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_2",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_3"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_3",
            *_read(),
            branch(eq(val(HECATE), _SPACE), then="PASS_LISTS_BLANK_INDENT_4"),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_INDENT_4",
            *_read(),
            goto("PASS_LISTS_BLANK_JOIN"),
        ),
        scene(
            "PASS_LISTS_BLANK_JOIN",
            let(HORATIO, const(2)),
            push(LADY_MACBETH, _NEWLINE),
            push(LADY_MACBETH, _NEWLINE),
            goto("PASS_LISTS_ITEM_GLYPH"),
        ),
        # --- List end and input end.
        scene(
            "PASS_LISTS_LIST_END",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            goto("PASS_LISTS_CLOSE_ALL"),
        ),
        scene(
            "PASS_LISTS_LIST_END_REPLAY",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY"),
        ),
        scene(
            "PASS_LISTS_LIST_END_REPLAY_DOT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY_DOT"),
        ),
        scene(
            "PASS_LISTS_END_OF_INPUT",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            push(HORATIO, val(HORATIO)),
            goto("PASS_LISTS_CLOSE_ALL"),
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL",
            pop(MACBETH, recall="fallen_rampart"),
            branch(eq(val(MACBETH), _END), then="PASS_LISTS_CLOSE_ALL_DONE"),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL"),
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL_DONE",
            push(MACBETH, _END),
            let(MACBETH, const(0)),
            goto("PASS_LISTS_AFTER_LIST"),
        ),
        scene(
            "PASS_LISTS_AFTER_LIST",
            branch(
                eq(val(LADY_MACBETH), const(0)),
                then="PASS_LISTS_DONE",
                else_="PASS_LISTS_RAW_GLYPH",
            ),
            companion=HECATE,
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL_REPLAY",
            pop(MACBETH, recall="fallen_rampart"),
            branch(
                eq(val(MACBETH), _END), then="PASS_LISTS_CLOSE_REPLAY_DONE"
            ),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY"),
        ),
        scene(
            "PASS_LISTS_CLOSE_REPLAY_DONE",
            push(MACBETH, _END),
            let(MACBETH, const(0)),
            goto("PASS_LISTS_RAW_REPLAY_SAVED"),
        ),
        scene(
            "PASS_LISTS_CLOSE_ALL_REPLAY_DOT",
            pop(MACBETH, recall="fallen_rampart"),
            branch(
                eq(val(MACBETH), _END),
                then="PASS_LISTS_CLOSE_REPLAY_DOT_DONE",
            ),
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            goto("PASS_LISTS_CLOSE_ALL_REPLAY_DOT"),
        ),
        scene(
            "PASS_LISTS_CLOSE_REPLAY_DOT_DONE",
            push(MACBETH, _END),
            let(MACBETH, const(0)),
            goto("PASS_LISTS_RAW_REPLAY_SAVED_DOT"),
        ),
        scene(
            "PASS_LISTS_DONE",
            goto("FRAME_STAGE_MAIN_OPEN"),
            companion=HECATE,
        ),
        # --- Staging: reverse the mixed stream onto Macbeth and the
        # --- looseness side channel onto Puck.
        scene(
            "FRAME_STAGE_MAIN_OPEN",
            push(MACBETH, _END),
            goto("FRAME_STAGE_MAIN_POP"),
        ),
        scene(
            "FRAME_STAGE_MAIN_POP",
            pop(LADY_MACBETH, recall="masons_stone"),
            branch(
                eq(val(LADY_MACBETH), _END), then="FRAME_STAGE_SIDE_OPEN"
            ),
            push(MACBETH, val(LADY_MACBETH)),
            goto("FRAME_STAGE_MAIN_POP"),
        ),
        scene(
            "FRAME_STAGE_SIDE_OPEN",
            goto("FRAME_STAGE_SIDE_POP"),
            companion=MACBETH,
        ),
        scene(
            "FRAME_STAGE_SIDE_POP",
            pop(HORATIO, recall="kept_measure"),
            branch(eq(val(HORATIO), _END), then="PASS_PARA_OPEN"),
            push(PUCK, val(HORATIO)),
            goto("FRAME_STAGE_SIDE_POP"),
            anchor=HORATIO,
        ),
        # --- Paragraph pass: walk the staged stream, form PARA tokens from
        # --- raw regions, finalize item frames from the side channel.
        scene(
            "PASS_PARA_OPEN",
            push(LADY_MACBETH, _END),
            goto("PASS_PARA_NEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_NEXT",
            pop(MACBETH, recall="staged_stone"),
            branch(eq(val(MACBETH), _END), then="FRAME_REVERSE_OPEN"),
            branch(eq(val(MACBETH), _NEWLINE), then="PASS_PARA_NEXT"),
            branch(
                eq(val(MACBETH), const(tokens.LIST_OPEN)),
                then="PASS_PARA_COPY_OPEN",
            ),
            branch(
                eq(val(MACBETH), const(tokens.LIST_CLOSE)),
                then="PASS_PARA_COPY_CLOSE",
            ),
            branch(
                eq(val(MACBETH), const(tokens.ITEM_START)), then="PASS_PARA_ITEM"
            ),
            goto("PASS_PARA_OPEN_PARA"),
        ),
        scene(
            "PASS_PARA_COPY_OPEN",
            push(LADY_MACBETH, const(tokens.LIST_OPEN)),
            pop(MACBETH, recall="staged_stone"),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_NEXT"),
        ),
        scene(
            "PASS_PARA_COPY_CLOSE",
            push(LADY_MACBETH, const(tokens.LIST_CLOSE)),
            goto("PASS_PARA_NEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_ITEM",
            push(LADY_MACBETH, const(tokens.LIST_ITEM)),
            pop(PUCK, recall="kept_measure"),
            push(LADY_MACBETH, val(PUCK)),
            goto("PASS_PARA_ITEM_TEXT"),
        ),
        scene(
            "PASS_PARA_ITEM_TEXT",
            pop(MACBETH, recall="staged_stone"),
            push(LADY_MACBETH, val(MACBETH)),
            branch(
                eq(val(MACBETH), const(tokens.TEXT_END)),
                then="PASS_PARA_NEXT",
                else_="PASS_PARA_ITEM_TEXT",
            ),
        ),
        scene(
            "PASS_PARA_OPEN_PARA",
            *emit_token(LADY_MACBETH, tokens.PARA),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_TEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_TEXT",
            pop(MACBETH, recall="staged_stone"),
            branch(eq(val(MACBETH), _NEWLINE), then="PASS_PARA_NEWLINE"),
            branch(eq(val(MACBETH), _END), then="PASS_PARA_FINAL_CLOSE"),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_TEXT"),
        ),
        scene(
            "PASS_PARA_NEWLINE",
            pop(MACBETH, recall="staged_stone"),
            branch(eq(val(MACBETH), _NEWLINE), then="PASS_PARA_CLOSE_BLANK"),
            branch(eq(val(MACBETH), _END), then="PASS_PARA_FINAL_CLOSE"),
            push(LADY_MACBETH, _NEWLINE),
            push(LADY_MACBETH, val(MACBETH)),
            goto("PASS_PARA_TEXT"),
        ),
        scene(
            "PASS_PARA_CLOSE_BLANK",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("PASS_PARA_NEXT"),
            companion=MACBETH,
        ),
        scene(
            "PASS_PARA_FINAL_CLOSE",
            push(LADY_MACBETH, const(tokens.TEXT_END)),
            goto("FRAME_REVERSE_OPEN"),
            companion=MACBETH,
        ),
        # --- Final reverse onto Puck (P1 scenes, unchanged labels/titles).
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

- [ ] **Step 2: Replace `src/20-act2-literary.toml` with:**

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

[scenes.FRAME_STAGE_MAIN_OPEN]
title = "Macbeth shoulders the finished wall."
pattern = "scene_of_character"

[scenes.FRAME_STAGE_MAIN_POP]
title = "Lady Macbeth hands each stone to Macbeth."
pattern = "cross_character"

[scenes.FRAME_STAGE_SIDE_OPEN]
title = "The tally passes to the herald."
pattern = "scene_of_character"

[scenes.FRAME_STAGE_SIDE_POP]
title = "Horatio hands the kept measures to Puck."
pattern = "cross_character"

[scenes.PASS_LISTS_AFTER_LIST]
title = "The field lies open beyond the gates."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLANK]
title = "A silence falls across the ranks."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLANK_HEAD]
title = "The captain reads past the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLANK_HEAD_ORDERED]
title = "The captain counts past the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLANK_INDENT_1]
title = "One step inward past the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLANK_INDENT_2]
title = "Two steps inward past the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLANK_INDENT_3]
title = "Three steps inward past the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLANK_INDENT_4]
title = "Four steps inward past the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLANK_JOIN]
title = "The far line rejoins its wide soldier."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLOCK_BLANK]
title = "Quiet lines pass before the gate."
pattern = "bare_statement"

[scenes.PASS_LISTS_BLOCK_START]
title = "Once more unto the breach."
pattern = "iconic_echo"

[scenes.PASS_LISTS_BSIB_SAVE_OL]
title = "A number rises after the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BSIB_SAVE_UL]
title = "A banner rises after the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BSIB_EMIT]
title = "The soldier is sealed loose upon the field."
pattern = "bare_statement"

[scenes.PASS_LISTS_BSIB_OUTDENT]
title = "The inner troop yields after the silence."
pattern = "bare_statement"

[scenes.PASS_LISTS_BSIB_TEST_DOT]
title = "The risen number awaits its seal."
pattern = "bare_statement"

[scenes.PASS_LISTS_BSIB_TEST_OL]
title = "A space must follow the risen number."
pattern = "bare_statement"

[scenes.PASS_LISTS_BSIB_TEST_UL]
title = "A space must follow the risen banner."
pattern = "bare_statement"

[scenes.PASS_LISTS_CLOSE_ALL]
title = "Every open gate is barred."
pattern = "bare_statement"

[scenes.PASS_LISTS_CLOSE_ALL_DONE]
title = "Macbeth lays a new floor for the rampart."
pattern = "scene_of_character"

[scenes.PASS_LISTS_CLOSE_ALL_REPLAY]
title = "The gates are barred behind a false banner."
pattern = "bare_statement"

[scenes.PASS_LISTS_CLOSE_ALL_REPLAY_DOT]
title = "The gates are barred behind a false number."
pattern = "bare_statement"

[scenes.PASS_LISTS_CLOSE_REPLAY_DONE]
title = "Macbeth restores the rampart's floor."
pattern = "scene_of_character"

[scenes.PASS_LISTS_CLOSE_REPLAY_DOT_DONE]
title = "Macbeth steadies the rampart's floor."
pattern = "scene_of_character"

[scenes.PASS_LISTS_DONE]
title = "The first pass lays down its arms."
pattern = "bare_statement"

[scenes.PASS_LISTS_END_OF_INPUT]
title = "The last soldier stands at the page's end."
pattern = "bare_statement"

[scenes.PASS_LISTS_GATE_ORDERED]
title = "The captain counts a numbered banner."
pattern = "bare_statement"

[scenes.PASS_LISTS_GATE_UNORDERED]
title = "The captain eyes a rough banner."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_1]
title = "One step inward from the wall."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_2]
title = "Two steps inward from the wall."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_3]
title = "Three steps inward from the wall."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_4]
title = "Four steps mark a carried line."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_CLASSIFY]
title = "The captain weighs the indented head."
pattern = "bare_statement"

[scenes.PASS_LISTS_INDENT_ORDERED]
title = "The captain counts the indented head."
pattern = "bare_statement"

[scenes.PASS_LISTS_ITEM_BEGIN_LOOSE]
title = "A wide-marching soldier takes his place."
pattern = "bare_statement"

[scenes.PASS_LISTS_ITEM_BEGIN_TIGHT]
title = "A close-drawn soldier takes his place."
pattern = "bare_statement"

[scenes.PASS_LISTS_ITEM_GLYPH]
title = "One glyph is laid within the rank."
pattern = "bare_statement"

[scenes.PASS_LISTS_ITEM_LINE_END]
title = "The rank's line reaches its end."
pattern = "bare_statement"

[scenes.PASS_LISTS_ITEM_NEXT]
title = "The rank takes one more glyph."
pattern = "bare_statement"

[scenes.PASS_LISTS_ITEM_SKIP_SPACES]
title = "Idle spaces fall before the soldier."
pattern = "bare_statement"

[scenes.PASS_LISTS_JOIN_LINE]
title = "The wrapped line joins the standing rank."
pattern = "bare_statement"

[scenes.PASS_LISTS_LAZY_REPLAY_SAVED]
title = "The false banner joins the rank."
pattern = "bare_statement"

[scenes.PASS_LISTS_LAZY_REPLAY_SAVED_DOT]
title = "The false number joins the rank."
pattern = "bare_statement"

[scenes.PASS_LISTS_LINE_HEAD]
title = "The captain reads the new line's head."
pattern = "bare_statement"

[scenes.PASS_LISTS_LINE_HEAD_ORDERED]
title = "The captain counts the new line's head."
pattern = "bare_statement"

[scenes.PASS_LISTS_LIST_END]
title = "The ranks are dismissed."
pattern = "bare_statement"

[scenes.PASS_LISTS_LIST_END_REPLAY]
title = "The ranks are dismissed by a false banner."
pattern = "bare_statement"

[scenes.PASS_LISTS_LIST_END_REPLAY_DOT]
title = "The ranks are dismissed by a false number."
pattern = "bare_statement"

[scenes.PASS_LISTS_MARK_SAVE_OL]
title = "The numbered banner is held aloft."
pattern = "bare_statement"

[scenes.PASS_LISTS_MARK_SAVE_UL]
title = "The rough banner is held aloft."
pattern = "bare_statement"

[scenes.PASS_LISTS_MARK_TEST_DOT]
title = "The number awaits its seal."
pattern = "bare_statement"

[scenes.PASS_LISTS_MARK_TEST_OL]
title = "A space must follow the number."
pattern = "bare_statement"

[scenes.PASS_LISTS_MARK_TEST_UL]
title = "A space must follow the banner."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_EMIT_OL]
title = "The soldier yields to an inner column."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_EMIT_UL]
title = "The soldier yields to an inner troop."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_OPEN_OL]
title = "An inner gate of numbered ranks."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_OPEN_UL]
title = "An inner gate of rough ranks."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_SAVE_OL]
title = "An inner number is held aloft."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_SAVE_UL]
title = "An inner banner is held aloft."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_TEST_DOT]
title = "The inner number awaits its seal."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_TEST_OL]
title = "A space must follow the inner number."
pattern = "bare_statement"

[scenes.PASS_LISTS_NEST_TEST_UL]
title = "A space must follow the inner banner."
pattern = "bare_statement"

[scenes.PASS_LISTS_OPEN_OL]
title = "The gate of numbered ranks is opened."
pattern = "bare_statement"

[scenes.PASS_LISTS_OPEN_UL]
title = "The gate of rough ranks is opened."
pattern = "bare_statement"

[scenes.PASS_LISTS_RAW_AFTER_NEWLINE]
title = "The watch turns at the line's end."
pattern = "bare_statement"

[scenes.PASS_LISTS_RAW_BLANK]
title = "A blank rank crosses the field."
pattern = "bare_statement"

[scenes.PASS_LISTS_RAW_GLYPH]
title = "One plain glyph joins the wall."
pattern = "bare_statement"

[scenes.PASS_LISTS_RAW_NEXT]
title = "The line marches on."
pattern = "bare_statement"

[scenes.PASS_LISTS_RAW_REPLAY_SAVED]
title = "The held banner returns to the wall."
pattern = "bare_statement"

[scenes.PASS_LISTS_RAW_REPLAY_SAVED_DOT]
title = "The banner and seal return to the wall."
pattern = "bare_statement"

[scenes.PASS_LISTS_SEED_FRAMES]
title = "Macbeth lays the first stone of the rampart."
pattern = "scene_of_character"

[scenes.PASS_LISTS_SIB_EMIT]
title = "The soldier is sealed into the ranks."
pattern = "bare_statement"

[scenes.PASS_LISTS_SIB_OUTDENT]
title = "The inner troop returns to command."
pattern = "bare_statement"

[scenes.PASS_LISTS_SIB_SAVE_OL]
title = "A brother number is held aloft."
pattern = "bare_statement"

[scenes.PASS_LISTS_SIB_SAVE_UL]
title = "A brother banner is held aloft."
pattern = "bare_statement"

[scenes.PASS_LISTS_SIB_TEST_DOT]
title = "The brother number awaits its seal."
pattern = "bare_statement"

[scenes.PASS_LISTS_SIB_TEST_OL]
title = "A space must follow the brother number."
pattern = "bare_statement"

[scenes.PASS_LISTS_SIB_TEST_UL]
title = "A space must follow the brother banner."
pattern = "bare_statement"

[scenes.PASS_PARA_CLOSE_BLANK]
title = "The wall is sealed against the blank."
pattern = "bare_statement"

[scenes.PASS_PARA_COPY_CLOSE]
title = "A barred stone passes through unchanged."
pattern = "bare_statement"

[scenes.PASS_PARA_COPY_OPEN]
title = "A gate stone passes through unchanged."
pattern = "bare_statement"

[scenes.PASS_PARA_FINAL_CLOSE]
title = "The last chamber is sealed."
pattern = "bare_statement"

[scenes.PASS_PARA_ITEM]
title = "The soldier receives his kept measure."
pattern = "bare_statement"

[scenes.PASS_PARA_ITEM_TEXT]
title = "The soldier's words pass through unchanged."
pattern = "bare_statement"

[scenes.PASS_PARA_NEWLINE]
title = "The wall pauses at the line's end."
pattern = "bare_statement"

[scenes.PASS_PARA_NEXT]
title = "The mason takes the next staged stone."
pattern = "bare_statement"

[scenes.PASS_PARA_OPEN]
title = "The mason opens the second pass."
pattern = "bare_statement"

[scenes.PASS_PARA_OPEN_PARA]
title = "A new chamber takes its mark."
pattern = "bare_statement"

[scenes.PASS_PARA_TEXT]
title = "One glyph is laid within the wall."
pattern = "bare_statement"
```

- [ ] **Step 3: Edit `src/literary.toml`**

**(a)** In `[iconic_moments.once_more_breach]`, change
`scene = "PASS_PARA_READ_GLYPH"` to `scene = "PASS_LISTS_BLOCK_START"`.

**(b)** Replace the empty `[characters.macbeth.recall]` table with:

```toml
[characters.macbeth.recall]
masons_stone = "Recall the mason's stone."
```

**(c)** Add to `[characters.lady_macbeth.recall]`:

```toml
fallen_rampart = "Recall the fallen rampart."
kept_measure = "Recall the kept measure."
staged_stone = "Recall the staged stone."
```

**(d)** Add to `[characters.puck.recall]`:

```toml
kept_measure = "Recall the kept measure."
```

**(e)** Add one `vneg2` line to each of these `stable_utility` tables:

```toml
[characters.hecate.stable_utility]      # add: vneg2 = "a rotten toad"
[characters.horatio.stable_utility]     # add: vneg2 = "a miserable beggar"
[characters.lady_macbeth.stable_utility] # add: vneg2 = "a cursed wolf"
[characters.macbeth.stable_utility]     # add: vneg2 = "a foul curse"
[characters.puck.stable_utility]        # add: vneg2 = "a vile wolf"
```

(One line each inside the existing tables — do not duplicate the table
headers. Negative noun + one negative adjective = −2 per
`docs/spl/reference.md`.)

- [ ] **Step 4: Add Macbeth to the dramatis personae**

In `src/00-preamble.spl`, insert directly after the Lady Macbeth line:

```text
Macbeth, apprentice mason, who steps through the shadowed threshold.
```

(A blank line above and below, matching the other declarations. This is
load-bearing SPL — Act II now puts Macbeth on stage — and it satisfies
`test_named_production_characters_have_speaking_lines` because he speaks in
the staging scenes of this same commit.)

- [ ] **Step 5: Regenerate and gate**

```bash
uv run python -m scripts.splc && uv run python scripts/assemble.py
git diff --stat src/10-act1-preprocess.spl src/30-act3-span.spl src/40-act4-emit.spl debug/40-act4-token-dump.spl
uv run pytest tests/test_token_dump.py -q
uv run pytest tests/test_architecture_spikes.py -q
uv run pytest -q
uv run pytest tests/test_literary_compliance.py tests/test_literary_toml_schema.py tests/test_literary_surfaces.py tests/test_iconic_moments.py tests/test_assemble.py tests/test_codegen_html.py -q
uv run pytest tests/test_slice1_amps_angle.py tests/test_strict_parity_harness.py -q
uv run pytest tests/test_mdtest.py -k 'Amps and angle' -q
```

Expected: only `src/20-act2-block.spl` and `shakedown.spl` change among the
generated files; **amps and short dumps byte-equal** (the paragraph-pass
rewrite is stream-invisible for single-line paragraphs — any drift is a bug);
the six spike tests report **XPASS**; the full default suite is green; G1
strict parity holds. If a spike fixture mismatches, diff `./shakedown-debug`
output for that fixture against §Contract's expected stream to localize the
act at fault before touching anything.

- [ ] **Step 6: Lint, type-check, commit**

```bash
uv run ruff check . && uv run ruff format . && uv run pyright
git add src_ir/act2.py src/20-act2-literary.toml src/literary.toml src/00-preamble.spl src/20-act2-block.spl shakedown.spl
git commit -m "feat: recognize lists in act two at spike scope"
```

---
### Task 5: Bless the list dumps, un-xfail the spikes

**Files:**
- Create: `tests/fixtures/token_stream/lists/<fixture>.dump` (six files)
- Modify: `tests/test_token_dump.py`
- Modify: `tests/test_architecture_spikes.py`

**Interfaces:**
- Consumes: the completed play from Tasks 1–4.
- Produces: the extended G2 baseline set that gates Spike B and Slices 2+; the spike tests as hard gates.

- [ ] **Step 1: Record and machine-check the six dumps**

```bash
mkdir -p tests/fixtures/token_stream/lists
for f in tests/fixtures/architecture_spikes/lists/*.text; do
  ./shakedown-debug < "$f" > "tests/fixtures/token_stream/lists/$(basename "${f%.text}").dump"
done
```

Then compare every dump against this plan's expected streams:

```bash
uv run python - <<'EOF'
from pathlib import Path

expected = {
    "flat_unordered_tight": [4, 1, 5, 1, 97, 108, 112, 104, 97, 0, 5, 1, 98,
                             101, 116, 97, 0, 5, 1, 103, 97, 109, 109, 97, 0, 6],
    "flat_ordered_tight": [4, 2, 5, 1, 97, 108, 112, 104, 97, 0, 5, 1, 98,
                           101, 116, 97, 0, 5, 1, 103, 97, 109, 109, 97, 0, 6],
    "indented_continuation": [4, 1, 5, 1, 97, 108, 112, 104, 97, 10, 99, 111,
                              110, 116, 105, 110, 117, 97, 116, 105, 111, 110,
                              0, 5, 1, 98, 101, 116, 97, 0, 6],
    "loose_second_paragraph": [4, 1, 5, 2, 97, 108, 112, 104, 97, 10, 10, 115,
                               101, 99, 111, 110, 100, 32, 112, 97, 114, 97,
                               103, 114, 97, 112, 104, 0, 5, 1, 98, 101, 116,
                               97, 0, 6],
    "nested_one_level": [4, 1, 5, 1, 97, 108, 112, 104, 97, 0, 4, 2, 5, 1, 98,
                         101, 116, 97, 0, 5, 1, 103, 97, 109, 109, 97, 0, 6, 5,
                         1, 100, 101, 108, 116, 97, 0, 6],
    "hard_wrapped_boundary": [1, *b"Here is a wrapped paragraph", 10,
                              *b"8. Oops this stays paragraph text.", 0],
}
base = Path("tests/fixtures/token_stream/lists")
for name, want in expected.items():
    got = [int(line) for line in (base / f"{name}.dump").read_text().split()]
    assert got == want, f"{name}: {got} != {want}"
print("all six dumps match the plan's expected streams")
EOF
```

Expected: `all six dumps match the plan's expected streams`. Any mismatch is
an implementation bug — stop and fix the offending act task; do not bless.

- [ ] **Step 2: Hand-review two dumps against the contract**

Read `loose_second_paragraph.dump` and `nested_one_level.dump` top to bottom
against the worked decodings in §Contract and choreography (loose payload `2`
with the interior `10 10`; gamma's `0` followed by `6` then delta's `5 1`).
Confirm no `-2` and no `-1` appears in any dump (framing markers never cross
the act boundary). This is the design spec's deliberate-extension review; the
committed files below are the durable record of it.

- [ ] **Step 3: Add the baseline regression tests**

Append to `tests/test_token_dump.py`:

```python
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"
LIST_BASELINES = BASELINES / "lists"


@pytest.mark.parametrize(
    "stem",
    sorted(path.stem for path in LIST_FIXTURES.glob("*.text")),
)
def test_dump_matches_blessed_list_baseline(stem: str) -> None:
    """G2 gate over the P2 list vocabulary: blessed by the P2 plan after
    hand-review; later slices re-bless deliberately, never casually."""
    fixture = LIST_FIXTURES / f"{stem}.text"
    assert _dump(fixture.read_bytes()) == (
        LIST_BASELINES / f"{stem}.dump"
    ).read_bytes()
```

and add `import pytest` below the existing imports.

Run: `uv run pytest tests/test_token_dump.py -q`
Expected: PASS (nine tests).

- [ ] **Step 4: Un-xfail the spike tests**

In `tests/test_architecture_spikes.py`, delete the `_SPIKE_A_HALT_REASON`
assignment and replace the whole `@pytest.mark.parametrize(...)` decorator
with:

```python
@pytest.mark.parametrize("fixture", _list_cases(), ids=lambda path: path.stem)
```

Run: `uv run pytest tests/test_architecture_spikes.py -q`
Expected: `6 passed` (hard passes, no xfail/xpass).

- [ ] **Step 5: Measure the grown play (for Task 6's record)**

```bash
wc -l shakedown.spl
time ./shakedown < tests/fixtures/architecture_spikes/lists/flat_unordered_tight.text > /dev/null
time ./shakedown < ~/mdtest/Markdown.mdtest/"Amps and angle encoding.text" > /dev/null
```

Note the line count and the two wall times for Task 6.

- [ ] **Step 6: Full verify, commit**

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format . && uv run pyright
git add tests/fixtures/token_stream/lists tests/test_token_dump.py tests/test_architecture_spikes.py
git commit -m "test: bless list token-stream baselines and un-xfail list spikes"
```

Expected: default suite fully green with **zero xfails remaining for lists**.

---
### Task 6: Record the spike outcome

**Files:**
- Modify: `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` (§4.2, §7.3)
- Modify: `.agent/blockers.md`
- Modify: `docs/superpowers/plans/plan-roadmap.md`, this plan file

**Interfaces:**
- Consumes: Task 5's measurements and the green gates.
- Produces: Spike A closed in the durable design record; the roadmap pointing at Spike B.

- [ ] **Step 1: Architecture spec §4.2 — record the intra-act marker**

In the `**Stream contract (2026-07-06):**` paragraph's termination note,
append:

```markdown
P2 (2026-07-07) adds one pass-internal framing marker: `ITEM_START` (−2)
brackets a list item's text on Act II's mixed stream and is consumed by the
paragraph pass; it never crosses an act boundary. Item looseness travels on a
side channel (Horatio's stack, staged onto Puck) rather than by buffering
item text.
```

- [ ] **Step 2: Architecture spec §7.3 — record the outcome**

Append to §7.3 (after the **Outcomes** bullets), filling in Task 5's measured
numbers:

```markdown
**Outcome (P2, 2026-07-07): ✅ spike passed.** All six snippet fixtures are
byte-identical to the oracle through the four-act play
(`tests/test_architecture_spikes.py`, hard-gated); the dispatcher shape and
frame-sentinel pattern are confirmed in IR. Findings: (1) SPL's
two-characters-per-scene and one-question rules inflate the pass automaton to
93 Act II scenes against the design's ~15–20 estimate — a cost-surface
finding, not a decomposition failure; (2) the assembled play grew from 1,911
to <measured> lines with cold runtime ≈<measured>s per invocation (B14
curve); (3) spike-scope narrowings, lifted in Slice 4: single-digit ordered
markers; no top-level marker indent; post-blank indented markers read as
loose continuation text (nested loose sublists diverge from the oracle —
probe `* a\n  * b\n\n  cont\n* c\n`); whitespace-only lines inside items
unsupported. Item looseness uses the §4.2 side channel.
```

- [ ] **Step 3: Clear the blocker**

In `.agent/blockers.md`, delete the Spike A `- BLOCK:` entry entirely (the
resolution chain 3F–3L is complete; gates are green as of Task 5's commit).

- [ ] **Step 4: Roadmap and plan bookkeeping**

In `docs/superpowers/plans/plan-roadmap.md`: set row 3L's status to
`shipped: <date> at commit <sha of Task 5's commit or later>`; update the
"Active halt" paragraph under Halt-and-redesign to state that Spike A is
resolved and closed (P1+P2 shipped; outcome recorded in architecture spec
§7.3); leave row 4 (Spike B) as the next pending row. Tick every checkbox in
this plan file.

- [ ] **Step 5: Verify and commit**

```bash
uv run pytest tests/test_roadmap_contract.py tests/test_iconic_moments.py -q
uv run pytest -q
git add docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md .agent/blockers.md docs/superpowers/plans/plan-roadmap.md docs/superpowers/plans/2026-07-07-spike-a-p2-list-pass.md
git commit -m "docs: record spike a completion and list-pass narrowings"
```

Flag to the operator: Spike A is complete; the next planning session writes
Spike B (roadmap row 4) against the extended G2 baseline set.

---

## Self-review notes (plan author)

- **Spec coverage:** stream-contract extension (`ITEM_START`, Task 1), arity
  dispatch in Act III (Task 2), Act IV list emission per oracle byte rules
  (Task 3), list pass + paragraph pass + frame sentinels on Macbeth + carrier
  ping-pong + final reverse (Task 4), G2 record/review/bless of the six list
  dumps with amps/short held byte-equal throughout (Tasks 2–5), six spikes
  un-xfailed (Task 5), outcome + narrowings recorded (Task 6). Design-spec
  deviations are consolidated in §Scope narrowings and re-recorded in the
  architecture spec by Task 6.
- **Validation:** all IR validated with the repo validator, rendered by the
  repo lowerer against this plan's TOML, and simulated end-to-end against the
  oracle (six fixtures byte-identical; twelve probes; amps/short dumps
  byte-equal). The uncovered risk is real-interpreter divergence from the
  simulation semantics; the per-task G1/G2/G3 gates bound it to one act.
- **Type consistency:** `tokens.ITEM_START`, `emit_token`, recall keys
  (`fallen_rampart`, `kept_measure`, `staged_stone`, `masons_stone`,
  `kept_charge`, `sealed_gates_colour`), and every scene label referenced
  across tasks were cross-checked mechanically (ledger coverage: no missing,
  no orphan entries; title word counts within pattern limits; Act IV dull-verb
  budget 0/1/1).
- **Known accepted behavior:** the `nested_then_loose` probe diverges from the
  oracle (documented narrowing #3); doc-start blank lines are copied through
  the mixed stream and skipped by the paragraph pass (stream-invisible);
  Prospero's value becomes scratch in the list flow; Macbeth's stack keeps a
  spent `STREAM_END` floor per closed list group (inert below the staging
  sentinel).

## References

- `docs/superpowers/specs/2026-07-06-spike-a-ir-lists-design.md` — governing design (stream contract, list-pass scope, P2 gates)
- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` — §4.2 stream contract, §6.3 sentinel ownership, §7.3 spike scope (all as revised 2026-07-06)
- `docs/superpowers/plans/plan-roadmap.md` — plan ladder; 3L row
- `docs/superpowers/plans/2026-07-06-spike-a-p1-stream-skeleton.md` — P1 (shipped); blessed baselines this plan extends
- `docs/markdown/list-mechanics.md` — Markdown.pl list behavior
- `docs/spl/token-codes.md` — canonical token codes; gains the ITEM_START row in Task 1
- `docs/spl/reference.md` — SPL legality (negative noun phrases; adjective doubling)
- `docs/superpowers/notes/spl-literary-protocol.md` — binding literary protocol
- `docs/superpowers/notes/correctness-first-spl-workflow.md` — prose reserved at planning time; spare-pool rules
