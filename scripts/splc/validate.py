"""Build-time IR validation. Every violation names the offending scene,
so authors never debug a downstream SPL parse error."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    BinOp,
    Branch,
    Char,
    Cond,
    Const,
    Expr,
    Goto,
    HaltAct,
    Let,
    Op,
    Pop,
    PrintChar,
    PrintInt,
    Push,
    ReadChar,
    Scene,
    Val,
)
from scripts.splc.prose import ProseEngine


class IrError(ValueError):
    pass


def _expr_chars(expr: Expr) -> set[Char]:
    if isinstance(expr, Const):
        return set()
    if isinstance(expr, Val):
        return {expr.char}
    if isinstance(expr, BinOp):
        return _expr_chars(expr.left) | _expr_chars(expr.right)
    raise IrError(f"unknown expression node {expr!r}")


def _cond_chars(cond: Cond) -> set[Char]:
    return _expr_chars(cond.left) | _expr_chars(cond.right)


def _op_chars(op: Op) -> set[Char]:
    if isinstance(op, (Let, Push)):
        return {op.target} | _expr_chars(op.expr)
    if isinstance(op, (Pop, ReadChar, PrintChar, PrintInt)):
        return {op.target}
    if isinstance(op, Branch):
        return _cond_chars(op.cond)
    return set()


def participants(sc: Scene, anchor: Char) -> tuple[Char, Char]:
    chars: set[Char] = {anchor}
    for op in sc.ops:
        chars |= _op_chars(op)
    if sc.companion is not None:
        chars.add(sc.companion)
    others = sorted(chars - {anchor}, key=lambda c: c.value)
    if len(others) != 1:
        raise IrError(
            f"scene {sc.label}: needs exactly one character besides the "
            f"anchor {anchor.value}, found {[c.value for c in others]} "
            "(declare companion=... if no op references a second character)"
        )
    return (anchor, others[0])


def _jump_targets(op: Op) -> list[str]:
    if isinstance(op, Goto):
        return [op.target]
    if isinstance(op, Branch):
        return [op.then] + ([op.else_] if op.else_ is not None else [])
    return []


def _check_terminal(sc: Scene) -> None:
    if not sc.ops:
        raise IrError(f"scene {sc.label}: empty scene is not terminal")
    for op in sc.ops[:-1]:
        if isinstance(op, (Goto, HaltAct)):
            raise IrError(f"scene {sc.label}: unreachable ops after {op!r}")
        if isinstance(op, Branch) and op.else_ is not None:
            raise IrError(f"scene {sc.label}: exhaustive branch must be the last op")
    last = sc.ops[-1]
    terminal = isinstance(last, (Goto, HaltAct)) or (
        isinstance(last, Branch) and last.else_ is not None
    )
    if not terminal:
        raise IrError(
            f"scene {sc.label}: not terminal — fallthrough between scenes "
            "is forbidden; end with goto, halt_act, or an exhaustive branch"
        )


def entry_pairs(a: Act) -> dict[str, tuple[Char, Char] | None]:
    by_label = {sc.label: sc for sc in a.scenes}
    entry: dict[str, tuple[Char, Char] | None] = {a.scenes[0].label: None}
    for sc in a.scenes:
        leaving = participants(sc, a.anchor)
        for op in sc.ops:
            for target in _jump_targets(op):
                if target not in by_label:
                    continue  # undefined targets reported by validate()
                if target in entry and entry[target] != leaving:
                    raise IrError(
                        f"scene {target}: predecessors leave inconsistent "
                        f"stage pairs ({entry[target]} vs {leaving} from "
                        f"{sc.label})"
                    )
                entry[target] = leaving
    return entry


def validate(a: Act, prose: ProseEngine) -> dict[str, tuple[Char, Char] | None]:
    labels = [sc.label for sc in a.scenes]
    if len(labels) != len(set(labels)):
        raise IrError(f"act {a.number}: duplicate scene labels")
    defined = set(labels)
    for sc in a.scenes:
        try:
            prose.scene_heading(sc.label)
        except KeyError as exc:
            raise IrError(f"scene {sc.label}: {exc}") from exc
        _check_terminal(sc)
        pair = participants(sc, a.anchor)
        for op in sc.ops:
            for target in _jump_targets(op):
                if target not in defined:
                    raise IrError(f"scene {sc.label}: jump to undefined scene {target}")
            for c in _op_chars(op):
                if c not in pair:
                    raise IrError(
                        f"scene {sc.label}: {c.value} referenced but not in "
                        f"stage pair {tuple(p.value for p in pair)}"
                    )
            if isinstance(op, Pop):
                speaker = pair[1] if op.target == a.anchor else a.anchor
                try:
                    prose.recall_placeholder(speaker, op.recall)
                except KeyError as exc:
                    raise IrError(f"scene {sc.label}: {exc}") from exc
    return entry_pairs(a)
