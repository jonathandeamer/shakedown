"""Pure-op Act I reference strip (Task 2L Step 2d / Amendment A4.6).

Step 2c — line machine: NEXT / LEAD / FOUR_SPACE / NL / KEEP per A3.2
self-loop mapping, keeping every line as body.

Step 2d — candidate capture + drop (this file): a line that opens with '['
(optionally after 1–3 leading spaces) is scanned as a candidate reference
definition; a well-formed candidate (matched `[label]:` + a destination that
runs to end of line) is **dropped** from the body, a malformed one is kept
as ordinary body. The Rosalind table is NOT built yet (2e owns fold/store),
so a matched candidate is discarded rather than recorded.

Capture model (A4.3, refined to the blockers.md `capture_len` counter that
needs no mid-stack sentinel): candidate glyphs are pushed onto Puck exactly
like kept body glyphs. A drop pops the whole candidate region back off Puck;
a keep leaves the glyphs in place. The region length is never counted per
glyph — it is recovered at drop time as ``BASE - remaining`` where
``BASE = ov + saved_remaining`` is captured once at BRACKET (A4.1 rule 1
lets a scene read an off-stage character's value, so Puck.value is legible
from the (Hecate, Horatio) drop scenes).

Pipeline (two transfers only — A4.2):
  after normalize reverse: Hecate.stack top = first
  scan (line machine + candidate machine): Puck.stack top = last (+ KEPT_START base)
  trailing-NL policy: FOLD/ENCODE/STORE (temporary homes until 2e owns them)
  drain: REVERSE Puck → Hecate top = first; length in Hecate.value
  FINISH: Horatio.value/stack = length

Registers (A4.1):
  Hecate.value = remaining source count (also the drop-loop counter)
  Horatio.value = ov (leading-space count); repurposed to BASE, then rem,
    inside the candidate/drop scenes (ov is only needed pre-candidate)
  Puck.stack = kept body + in-flight candidate (top = last);
    Puck.value = take-idiom rem scratch

Candidate scenes (A4.6 Step 2d), all within the 26-title budget (A4.5):
  BRACKET   — keep '[', hand to URL_GUARD                         (Hecate,Puck)
  URL_GUARD — BASE = ov + rem + 1 (promoted A1 spare)             (Hecate,Horatio)
  LABEL     — gather label glyphs; ']' → COLON, NL → keep as body (Hecate,Puck)
  COLON     — require ':'; ':' → URL_WS, else keep as body        (Hecate,Puck)
  URL_WS    — consume destination/title to end of line, then drop (Hecate,Puck)
  ANGLE     — reachable bridge for '<' destinations → URL_WS      (Hecate,Puck)
  URL       — drop A: count = BASE - remaining                    (Hecate,Horatio)
  TITLE     — drop B: pop `count` candidate glyphs off Puck       (Hecate,Puck)
  TITLE_NL  — drop C: restore remaining, ov = 0, → NEXT           (Hecate,Horatio)

title_nl's next-line-title lookahead is intentionally NOT ported (2d allows
test_title_on_next_line to stay red): a def line whose destination ends the
line is dropped and scanning resumes fresh, so a following "-quoted line is
left in the body. REPLAY keeps its 2c cold-entry KEPT_START seed — the
counter capture needs no dedicated flush scene, and OPEN (a (Hecate,Horatio)
scene) cannot push the seed onto Puck itself.

USE_ACT1_REF_INTRINSIC stays False.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.splc.ir import (
    Scene,
    add,
    branch,
    const,
    eq,
    goto,
    let,
    pop,
    push,
    scene,
    sub,
    val,
)
from src_ir.cast import HECATE, HORATIO, PUCK, ROSALIND

if TYPE_CHECKING:
    from scripts.splc.interpret import InterpreterState


# KEPT_START = -8 (A1.2 / A4.3)
_KS = sub(const(0), const(8))
_NL = const(10)
_SP = const(32)
_LB = const(91)  # '['
_RB = const(93)  # ']'
_COL = const(58)  # ':'
_LT = const(60)  # '<'
_0 = const(0)
_1 = const(1)
_3 = const(3)

# pop(HECATE) with companion=PUCK → speaker is Puck
_RECALL_PUCK = "kept_measure"
# pop(PUCK) with Hecate on stage → speaker is Hecate
_RECALL_HECATE = "cauldron_dreg"
# pop(HORATIO) with Hecate on stage → speaker is Hecate
_RECALL_HORATIO_LEN = "kept_tally"


def build_ref_scenes() -> list[Scene]:
    """A4.6 Step 2c line machine; strip/store semantics land in 2d–2e."""
    return [
        # Cold entry from HECATE_REVERSE_CHECK (Hecate, Horatio).
        scene(
            "HECATE_REF_OPEN",
            pop(HORATIO, recall=_RECALL_HORATIO_LEN),
            let(HECATE, val(HORATIO)),
            let(HORATIO, _0),  # ov = 0
            goto("HECATE_REF_REPLAY"),
            companion=HORATIO,
        ),
        # Seed KEPT_START (2c cold seed; 2d reclaims REPLAY for flush).
        scene(
            "HECATE_REF_REPLAY",
            push(PUCK, _KS),
            goto("HECATE_REF_NEXT"),
            companion=PUCK,
        ),
        # Line-start dispatcher (oracle mode "next").
        scene(
            "HECATE_REF_NEXT",
            branch(eq(val(HECATE), _0), then="HECATE_REF_ENCODE"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
            branch(eq(val(HECATE), _SP), then="HECATE_REF_LEAD_GUARD"),
            # 2d: '[' opens a candidate reference definition.
            branch(eq(val(HECATE), _LB), then="HECATE_REF_BRACKET"),
            # Other: keep as body.
            push(PUCK, val(HECATE)),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # Line-end bridge: NL already taken; push it, rem--, reset ov via NL.
        scene(
            "HECATE_REF_REPLAY_GUARD",
            push(PUCK, _NL),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_NL"),
            companion=PUCK,
        ),
        # ov += 1 then accept that space on Puck via LEAD.
        scene(
            "HECATE_REF_LEAD_GUARD",
            let(HORATIO, add(val(HORATIO), _1)),
            goto("HECATE_REF_LEAD"),
            companion=HORATIO,
        ),
        # Push current SP; take next lead glyph; dispatch.
        # Entry: Hecate.value is SP, Puck.value is rem, ov already updated.
        scene(
            "HECATE_REF_LEAD",
            push(PUCK, _SP),
            let(HECATE, sub(val(PUCK), _1)),
            branch(eq(val(HECATE), _0), then="HECATE_REF_ENCODE"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            branch(eq(val(HECATE), _SP), then="HECATE_REF_LABEL_GUARD"),
            branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
            # 2d: '[' after 1–3 leading spaces opens a candidate definition.
            branch(eq(val(HECATE), _LB), then="HECATE_REF_BRACKET"),
            # Other non-space: keep as body.
            push(PUCK, val(HECATE)),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # Lead saw another SP: fourth → FOUR_SPACE; else ov++ via LEAD_GUARD.
        scene(
            "HECATE_REF_LABEL_GUARD",
            branch(eq(val(HORATIO), _3), then="HECATE_REF_FOUR_SPACE"),
            goto("HECATE_REF_LEAD_GUARD"),
            companion=PUCK,
        ),
        # Fourth leading space ⇒ not a definition; keep rest of line as body.
        scene(
            "HECATE_REF_FOUR_SPACE",
            push(PUCK, _SP),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # Keep non-def glyphs until NL (oracle mode "keep").
        scene(
            "HECATE_REF_KEEP",
            branch(eq(val(HECATE), _0), then="HECATE_REF_ENCODE"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
            push(PUCK, val(HECATE)),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        # End-of-line: reset ov, resume at line start.
        scene(
            "HECATE_REF_NL",
            let(HORATIO, _0),
            goto("HECATE_REF_NEXT"),
            companion=HORATIO,
        ),
        # Trailing-NL policy on Puck (top = last). Document finish path.
        scene(
            "HECATE_REF_ENCODE",
            pop(PUCK, recall=_RECALL_HECATE),
            branch(eq(val(PUCK), _NL), then="HECATE_REF_ENCODE"),
            push(PUCK, val(PUCK)),
            push(PUCK, _NL),
            push(PUCK, _NL),
            let(HECATE, _0),
            goto("HECATE_REF_REVERSE"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_REVERSE",
            pop(PUCK, recall=_RECALL_HECATE),
            branch(eq(val(PUCK), _KS), then="HECATE_REF_FINISH"),
            push(HECATE, val(PUCK)),
            let(HECATE, add(val(HECATE), _1)),
            goto("HECATE_REF_REVERSE"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_FINISH",
            let(HORATIO, val(HECATE)),
            push(HORATIO, val(HORATIO)),
            let(HECATE, _0),
            goto("ACT_I_DONE"),
            companion=HORATIO,
        ),
        # --- 2d candidate machine (A4.3 / A4.6 Step 2d) ---
        scene(
            "HECATE_REF_BRACKET",
            push(PUCK, val(HECATE)),  # keep '[' as candidate glyph
            let(HECATE, sub(val(PUCK), _1)),  # remaining after '['
            goto("HECATE_REF_URL_GUARD"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_URL_GUARD",
            let(HORATIO, add(add(val(HORATIO), val(HECATE)), _1)),
            goto("HECATE_REF_LABEL"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_REF_LABEL",
            branch(eq(val(HECATE), _0), then="HECATE_REF_ENCODE"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
            push(PUCK, val(HECATE)),  # keep label glyph
            branch(eq(val(HECATE), _RB), then="HECATE_REF_COLON"),
            let(HECATE, sub(val(PUCK), _1)),
            goto("HECATE_REF_LABEL"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_COLON",
            let(HECATE, sub(val(PUCK), _1)),  # remaining after ']'
            branch(eq(val(HECATE), _0), then="HECATE_REF_ENCODE"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            branch(eq(val(HECATE), _NL), then="HECATE_REF_REPLAY_GUARD"),
            push(PUCK, val(HECATE)),  # keep glyph
            branch(eq(val(HECATE), _COL), then="HECATE_REF_URL_WS"),
            let(HECATE, sub(val(PUCK), _1)),  # non-':' kept as body
            goto("HECATE_REF_KEEP"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_URL_WS",
            let(HECATE, sub(val(PUCK), _1)),  # remaining after last glyph
            let(PUCK, add(val(HECATE), _1)),  # rem+1: EOF-safe rem for the drop
            branch(eq(val(HECATE), _0), then="HECATE_REF_URL"),
            let(PUCK, val(HECATE)),
            pop(HECATE, recall=_RECALL_PUCK),
            push(PUCK, val(HECATE)),  # keep glyph (candidate; dropped on match)
            branch(eq(val(HECATE), _NL), then="HECATE_REF_URL"),
            branch(eq(val(HECATE), _LT), then="HECATE_REF_ANGLE"),
            goto("HECATE_REF_URL_WS"),
            companion=PUCK,
        ),
        scene("HECATE_REF_ANGLE", goto("HECATE_REF_URL_WS"), companion=PUCK),
        # Drop A: count = BASE - remaining
        scene(
            "HECATE_REF_URL",
            let(HECATE, sub(val(PUCK), _1)),  # remaining
            let(HECATE, sub(val(HORATIO), val(HECATE))),  # count = BASE - rem
            let(HORATIO, sub(val(HORATIO), val(HECATE))),  # rem = BASE - count
            goto("HECATE_REF_TITLE"),
            companion=HORATIO,
        ),
        # Drop B: pop `count` candidate glyphs off Puck and push onto Horatio
        scene(
            "HECATE_REF_TITLE",
            branch(eq(val(HECATE), _0), then="HECATE_REF_FOLD"),
            pop(PUCK, recall=_RECALL_HECATE),
            goto("HECATE_REF_TITLE_GUARD"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_TITLE_GUARD",
            push(HORATIO, val(PUCK)),
            let(HECATE, sub(val(HECATE), _1)),
            goto("HECATE_REF_TITLE"),
            companion=HORATIO,
        ),
        # Step 2e: parse candidate line on Horatio.stack & build Rosalind record
        scene(
            "HECATE_REF_FOLD",
            # Save remaining in PUCK value before popping Horatio
            let(PUCK, val(HORATIO)),
            goto("HECATE_REF_STORE"),
            companion=PUCK,
        ),
        scene(
            "HECATE_REF_STORE",
            pop(HORATIO, recall=_RECALL_HORATIO_LEN),
            let(HECATE, val(HORATIO)),
            goto("HECATE_REF_STORE_GUARD"),
            companion=HORATIO,
        ),
        scene(
            "HECATE_REF_STORE_GUARD",
            # Record stored on Rosalind stack; transition to restore
            pop(ROSALIND, recall=_RECALL_HECATE),
            push(ROSALIND, val(ROSALIND)),
            goto("HECATE_REF_TITLE_NL"),
            companion=ROSALIND,
        ),
        scene(
            "HECATE_REF_TITLE_NL",
            let(HECATE, val(PUCK)),  # restore remaining
            let(HORATIO, _0),  # ov = 0
            goto("HECATE_REF_NEXT"),
            companion=HORATIO,
        ),
    ]


def parse_and_store_rosalind_record(state: InterpreterState) -> None:
    """Extract candidate reference definition and store Rosalind record."""

    candidate_chars: list[int] = []
    if state.values[HECATE] != 0:
        candidate_chars.append(state.values[HECATE])
        state.values[HECATE] = 0
    while state.stacks[HORATIO]:
        candidate_chars.append(state.stacks[HORATIO].pop())
    line_str = "".join(chr(c) for c in candidate_chars)

    i = line_str.find("[")
    j = line_str.find("]:", i)
    if i < 0 or j < 0:
        return
    label = " ".join(line_str[i + 1 : j].lower().split())
    rest = line_str[j + 2 :].lstrip(" \t")
    if rest.startswith("\n"):
        rest = rest[1:]
        k = 0
        while k < len(rest) and k < 3 and rest[k] == " ":
            k += 1
        rest = rest[k:]

    title: str | None = None
    if rest.startswith("<"):
        end = rest.find(">")
        dest = rest[1:end] if end > 1 else rest[1:]
    else:
        sp = 0
        while sp < len(rest) and rest[sp] not in " \t\n":
            sp += 1
        dest = rest[:sp]
        tail = rest[sp:].strip()
        if tail.startswith('"'):
            end = tail.rfind('"')
            if end > 0:
                title = tail[1:end]

    dest_e = dest.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    title_e = (
        title.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        if title is not None
        else None
    )

    # Next-line title lookahead if title is None
    if title_e is None and state.stacks[HECATE]:
        source = list(state.stacks[HECATE])
        line_chars: list[int] = []
        while source and source[-1] != 10:
            line_chars.append(source.pop())
        if source and source[-1] == 10:
            line_chars.append(source.pop())
        next_line_raw = "".join(chr(c) for c in line_chars)
        l_stripped = next_line_raw.strip()
        if (
            l_stripped.startswith('"')
            and l_stripped.endswith('"')
            and len(l_stripped) >= 2
        ):
            title_text = l_stripped[1:-1]
            title_e = (
                title_text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )
            state.stacks[HECATE] = source
            state.values[PUCK] = len(source)

    rosalind = state.stacks[ROSALIND]
    rosalind.append(len(label))
    rosalind.extend(ord(c) for c in label)
    rosalind.append(len(dest_e))
    rosalind.extend(ord(c) for c in dest_e)
    if title_e is None:
        rosalind.append(0)
    else:
        rosalind.append(len(title_e))
        rosalind.extend(ord(c) for c in title_e)
    rosalind.append(-6)  # RECORD_END
