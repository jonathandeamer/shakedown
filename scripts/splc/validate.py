"""Build-time IR validation. Every violation names the offending scene,
so authors never debug a downstream SPL parse error."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    Branch,
    Char,
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
)
from scripts.splc.prose import ProseEngine


class IrError(ValueError):
    pass


def _op_targets(op: Op) -> set[Char]:
    if isinstance(op, (Let, Push, Pop, ReadChar, PrintChar, PrintInt)):
        return {op.target}
    return set()


def participants(sc: Scene, act_anchor: Char) -> tuple[Char, Char]:
    anchor = sc.anchor or act_anchor
    chars: set[Char] = {anchor}
    for op in sc.ops:
        chars |= _op_targets(op)
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
    # Pass 1 — branch arrivals fix the entry stage: directions render at
    # the target's scene start, so branch predecessors must agree.
    for sc in a.scenes:
        leaving = participants(sc, a.anchor)
        for op in sc.ops:
            if not isinstance(op, Branch):
                continue
            for target in [op.then] + ([op.else_] if op.else_ is not None else []):
                if target not in by_label:
                    continue
                recorded = entry.get(target)
                if target in entry and (
                    recorded is None or set(recorded) != set(leaving)
                ):
                    raise IrError(
                        f"scene {target}: predecessors leave inconsistent "
                        f"stage pairs ({entry[target]} vs {leaving} from "
                        f"{sc.label})"
                    )
                entry[target] = leaving
    # Pass 2 — goto arrivals normally adapt at the source, so a goto-only
    # scene is entered with its own pair already staged. That only works
    # when the source's speaking anchor survives into the target's default
    # pair; if adaptation would exit the source's own anchor (only possible
    # with scene-level anchor overrides), defer instead to the target's own
    # scene-start direction by recording the source's leaving pair.
    for sc in a.scenes:
        source_anchor = sc.anchor or a.anchor
        for op in sc.ops:
            if isinstance(op, Goto) and op.target in by_label:
                target_pair = participants(by_label[op.target], a.anchor)
                candidate = (
                    target_pair
                    if source_anchor in target_pair
                    else participants(sc, a.anchor)
                )
                entry.setdefault(op.target, candidate)
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

            if isinstance(op, Pop):
                anchor = sc.anchor or a.anchor
                speaker = pair[1] if op.target == anchor else anchor
                try:
                    prose.recall_placeholder(speaker, op.recall)
                except KeyError as exc:
                    raise IrError(f"scene {sc.label}: {exc}") from exc
    return entry_pairs(a)
