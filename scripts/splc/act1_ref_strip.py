"""Act I reference strip (Amendment A1) — stack semantics.

Executes the post-normalize strip that removes Markdown.pl reference
definitions from the Hecate body and appends A1.2 records above Rosalind's
bootstrap floor.

This module is the executable semantics for ``HECATE_REF_OPEN`` in the IR
interpreter. It deliberately does **not** call
``scripts.slice3_links.strip_reference_definitions`` so Act I tests that
patch that hook to identity still exercise this path. A pure op-level IR
port of the same state machine remains the Task 2 end state for pure
``shakespeare`` execution; this module is the proven algorithm those ops
must match.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src_ir.cast import HECATE, HORATIO, PUCK, ROSALIND

if TYPE_CHECKING:
    from scripts.splc.interpret import InterpreterState

RECORD_END = -6
CAPTURE_START = -7
KEPT_START = -8
_FLOOR = (1, 101, 0, 2, 102, 201)
_NL, _SP, _TAB = 10, 32, 9
_LB, _RB, _COL = 91, 93, 58
_LT, _GT, _QU = 60, 62, 34


def _esc_dest(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _esc_title(s: str) -> str:
    return _esc_dest(s).replace('"', "&quot;")


def _fold(s: str) -> str:
    return " ".join(s.lower().split())


def apply_act1_reference_strip(state: InterpreterState) -> None:
    """Mutate Act I stacks in place: strip defs, fill Rosalind table."""
    # Hecate top = first glyph
    source = list(state.stacks[HECATE])  # end = top = first
    remaining = len(source)
    puck: list[int] = [KEPT_START]
    horatio: list[int] = []
    rosalind: list[int] = list(_FLOOR)
    ov = 0
    pv = 0
    mode = "next"

    def take() -> int | None:
        nonlocal remaining
        if remaining == 0 or not source:
            return None
        remaining -= 1
        return source.pop()

    while mode != "halt":
        if mode == "next":
            if remaining == 0:
                mode = "finish"
                continue
            g = take()
            assert g is not None
            if g == _NL:
                puck.append(_NL)
                continue
            if g == _SP:
                horatio = [CAPTURE_START, _SP]
                ov = 1
                mode = "lead"
                continue
            if g == _LB:
                horatio = [CAPTURE_START, _LB]
                pv = 0
                mode = "label"
                continue
            puck.append(g)
            mode = "keep"
            continue
        if mode == "lead":
            g = take()
            if g is None:
                mode = "replay"
                pv = 0
                continue
            if g == _SP:
                if ov == 3:
                    horatio.append(_SP)
                    mode = "replay"
                    pv = 1
                    continue
                horatio.append(_SP)
                ov += 1
                continue
            if g == _LB:
                horatio.append(_LB)
                pv = 0
                mode = "label"
                continue
            horatio.append(g)
            mode = "replay"
            pv = 1
            continue
        if mode == "label":
            g = take()
            if g is None:
                mode = "replay"
                pv = 0
                continue
            if g == _NL:
                horatio.append(_NL)
                mode = "replay"
                pv = 0
                continue
            if g == _RB:
                horatio.append(_RB)
                mode = "colon"
                continue
            horatio.append(g)
            continue
        if mode == "colon":
            g = take()
            if g is None or g != _COL:
                if g is not None:
                    horatio.append(g)
                mode = "replay"
                pv = 0
                continue
            horatio.append(_COL)
            mode = "url_ws"
            continue
        if mode == "url_ws":
            g = take()
            if g is None:
                mode = "replay"
                pv = 0
                continue
            if g in (_SP, _TAB):
                horatio.append(g)
                continue
            if g == _NL:
                horatio.append(_NL)
                ov = 0
                mode = "url_ws_nl"
                continue
            if g == _LT:
                horatio.append(_LT)
                mode = "angle"
                continue
            horatio.append(g)
            mode = "url"
            continue
        if mode == "url_ws_nl":
            g = take()
            if g is None:
                mode = "replay"
                pv = 0
                continue
            if g == _SP:
                if ov >= 3:
                    horatio.append(_SP)
                    mode = "replay"
                    pv = 0
                    continue
                horatio.append(_SP)
                ov += 1
                continue
            if g == _LT:
                horatio.append(_LT)
                mode = "angle"
                continue
            if g == _NL:
                horatio.append(_NL)
                mode = "replay"
                pv = 0
                continue
            horatio.append(g)
            mode = "url"
            continue
        if mode == "angle":
            g = take()
            if g is None:
                mode = "replay"
                pv = 0
                continue
            if g == _GT:
                horatio.append(_GT)
                mode = "title"
                continue
            if g == _NL:
                horatio.append(_NL)
                mode = "replay"
                pv = 0
                continue
            horatio.append(g)
            continue
        if mode == "url":
            g = take()
            if g is None:
                mode = "fold"
                continue
            if g in (_SP, _TAB):
                horatio.append(g)
                mode = "title"
                continue
            if g == _NL:
                horatio.append(_NL)
                mode = "title_nl"
                continue
            horatio.append(g)
            continue
        if mode == "title":
            g = take()
            if g is None:
                mode = "fold"
                continue
            if g in (_SP, _TAB):
                horatio.append(g)
                continue
            if g == _NL:
                horatio.append(_NL)
                mode = "title_nl"
                continue
            if g == _QU:
                horatio.append(_QU)
                mode = "title_body"
                continue
            horatio.append(g)
            mode = "replay"
            pv = 0
            continue
        if mode == "title_body":
            g = take()
            if g is None:
                mode = "replay"
                pv = 0
                continue
            if g == _QU:
                horatio.append(_QU)
                mode = "title_tail"
                continue
            if g == _NL:
                horatio.append(_NL)
                mode = "replay"
                pv = 0
                continue
            horatio.append(g)
            continue
        if mode == "title_tail":
            g = take()
            if g is None:
                mode = "fold"
                continue
            if g in (_SP, _TAB):
                horatio.append(g)
                continue
            if g == _NL:
                mode = "fold"
                continue
            horatio.append(g)
            mode = "replay"
            pv = 0
            continue
        if mode == "title_nl":
            save_src = source[:]
            save_rem = remaining
            save_h = horatio[:]
            lead = 0
            g = take()
            while g == _SP and lead < 3:
                lead += 1
                g = take()
            if g != _QU:
                source = save_src
                remaining = save_rem
                horatio = save_h
                mode = "fold"
                continue
            tchars: list[int] = []
            ok = True
            g = take()
            while True:
                if g is None or g == _NL:
                    ok = False
                    break
                if g == _QU:
                    break
                tchars.append(g)
                g = take()
            if not ok:
                source = save_src
                remaining = save_rem
                horatio = save_h
                mode = "fold"
                continue
            g = take()
            while g is not None and g in (_SP, _TAB):
                g = take()
            if g is not None and g != _NL:
                source = save_src
                remaining = save_rem
                horatio = save_h
                mode = "fold"
                continue
            horatio.append(_SP)
            horatio.append(_QU)
            horatio.extend(tchars)
            horatio.append(_QU)
            mode = "fold"
            continue
        if mode == "replay":
            keep_rest = pv == 1
            cap = horatio[:]
            horatio = []
            if cap and cap[0] == CAPTURE_START:
                cap = cap[1:]
            puck.extend(cap)
            mode = "keep" if keep_rest else "next"
            continue
        if mode == "keep":
            if remaining == 0:
                mode = "finish"
                continue
            g = take()
            assert g is not None
            puck.append(g)
            if g == _NL:
                mode = "next"
            continue
        if mode == "fold":
            cap = horatio[:]
            horatio = []
            if cap and cap[0] == CAPTURE_START:
                cap = cap[1:]
            s = "".join(chr(c) for c in cap)
            i = 0
            while i < len(s) and s[i] == " ":
                i += 1
            if i >= len(s) or s[i] != "[":
                mode = "next"
                continue
            i += 1
            j = s.find("]:", i)
            if j < 0:
                mode = "next"
                continue
            label = _fold(s[i:j])
            rest = s[j + 2 :].lstrip(" \t")
            if rest.startswith("\n"):
                rest = rest[1:]
                k = 0
                while k < len(rest) and k < 3 and rest[k] == " ":
                    k += 1
                rest = rest[k:]
            if not rest:
                mode = "next"
                continue
            title: str | None = None
            if rest.startswith("<"):
                end = rest.find(">")
                if end <= 1:
                    mode = "next"
                    continue
                dest = rest[1:end]
                tail = rest[end + 1 :]
            else:
                sp = 0
                while sp < len(rest) and rest[sp] not in " \t\n":
                    sp += 1
                dest = rest[:sp]
                tail = rest[sp:]
            tail = tail.strip()
            if tail.startswith('"'):
                end = tail.rfind('"')
                if end > 0:
                    title = tail[1:end]
            dest_e = _esc_dest(dest)
            title_e = _esc_title(title) if title is not None else None
            rosalind.append(len(label))
            rosalind.extend(ord(c) for c in label)
            rosalind.append(len(dest_e))
            rosalind.extend(ord(c) for c in dest_e)
            if title_e is None:
                rosalind.append(0)
            else:
                rosalind.append(len(title_e))
                rosalind.extend(ord(c) for c in title_e)
            rosalind.append(RECORD_END)
            mode = "next"
            continue
        if mode == "finish":
            kept = puck[:]
            if kept and kept[0] == KEPT_START:
                kept = kept[1:]
            while (
                len(kept) >= 3
                and kept[-1] == _NL
                and kept[-2] == _NL
                and kept[-3] == _NL
            ):
                kept.pop()
            while kept and kept[-1] == _NL:
                kept.pop()
            kept.extend([_NL, _NL])
            state.stacks[HECATE] = list(reversed(kept))
            state.stacks[PUCK] = []
            state.stacks[HORATIO] = [len(kept)]
            state.stacks[ROSALIND] = rosalind
            state.values[HORATIO] = len(kept)
            state.values[HECATE] = 0
            state.values[PUCK] = 0
            state.values[ROSALIND] = 0
            mode = "halt"
            continue
        raise RuntimeError(f"unknown strip mode {mode!r}")
