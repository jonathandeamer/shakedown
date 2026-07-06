"""Lowering: IR acts -> fragment-shaped SPL text.

Stage choreography (Enter/Exit, speaker/addressee, question/If adjacency)
is computed here, never authored. Output keeps `Scene @LABEL:` and `@LIT.`
forms so scripts/assemble.py resolves numbering and prose exactly as it
does for hand-authored fragments."""

from __future__ import annotations

from scripts.splc.ir import (
    Act,
    BinOp,
    Branch,
    Char,
    Const,
    Expr,
    Goto,
    HaltAct,
    Let,
    Pop,
    PrintChar,
    PrintInt,
    Push,
    ReadChar,
    Scene,
    Val,
)
from scripts.splc.prose import ProseEngine
from scripts.splc.validate import participants, validate

_HEADING_INDENT = " " * 20

_BINOP_TEMPLATE = {
    "add": "the sum of {l} and {r}",
    "sub": "the difference between {l} and {r}",
    "mul": "the product of {l} and {r}",
    "div": "the quotient between {l} and {r}",
    "mod": "the remainder of the quotient between {l} and {r}",
}


def _render_expr(expr: Expr, speaker: Char, addressee: Char, prose: ProseEngine) -> str:
    if isinstance(expr, Const):
        return prose.value_phrase(speaker, expr.value)
    if isinstance(expr, Val):
        if expr.char == addressee:
            return "yourself"
        if expr.char == speaker:
            return "myself"
        return expr.char.value
    if isinstance(expr, BinOp):
        return _BINOP_TEMPLATE[expr.op].format(
            l=_render_expr(expr.left, speaker, addressee, prose),
            r=_render_expr(expr.right, speaker, addressee, prose),
        )
    raise TypeError(f"unknown expression node {expr!r}")


def _speech(speaker: Char, sentence: str) -> str:
    return f"{speaker.value}:\n {sentence}\n"


def _roles(target: Char, anchor: Char, pair: tuple[Char, Char]) -> tuple[Char, Char]:
    """Return (speaker, addressee) for an op on `target`."""
    if target == anchor:
        other = pair[1] if pair[0] == anchor else pair[0]
        return (other, anchor)
    return (anchor, target)


def _tested_char(branch_op: Branch, sc: Scene) -> Char:
    left = branch_op.cond.left
    if not isinstance(left, Val):
        raise TypeError(
            f"scene {sc.label}: branch condition left side must be val(CHAR)"
        )
    return left.char


def _jump_sentence(
    prose: ProseEngine,
    speaker: Char,
    current_index: int,
    target: str,
    order: dict[str, int],
    seed: str,
    prefix: str = "",
) -> str:
    backward = order[target] <= current_index
    phrase = prose.goto_phrase(speaker, backward=backward, seed=seed)
    if prefix:
        phrase = phrase[0].lower() + phrase[1:]
    return f"{prefix}{phrase} scene @{target}."


def _stage_directions(
    prev: tuple[Char, Char] | None, pair: tuple[Char, Char]
) -> list[str]:
    if prev is None:
        return [f"[Enter {pair[0].value} and {pair[1].value}]"]
    prev_set, pair_set = set(prev), set(pair)
    lines = [
        f"[Exit {c.value}]" for c in sorted(prev_set - pair_set, key=lambda c: c.value)
    ]
    entering = sorted(pair_set - prev_set, key=lambda c: c.value)
    if len(entering) == 2:
        lines.append(f"[Enter {entering[0].value} and {entering[1].value}]")
    elif len(entering) == 1:
        lines.append(f"[Enter {entering[0].value}]")
    return lines


def lower_act(a: Act, prose: ProseEngine, next_act_heading: str | None = None) -> str:
    entry = validate(a, prose)
    order = {sc.label: i for i, sc in enumerate(a.scenes)}
    blocks: list[str] = []
    for index, sc in enumerate(a.scenes):
        pair = participants(sc, a.anchor)
        anchor = sc.anchor or a.anchor
        lines: list[str] = [
            f"{_HEADING_INDENT}{prose.scene_heading(sc.label)}",
            "",
        ]
        for direction in _stage_directions(entry[sc.label], pair):
            lines.append(direction)
            lines.append("")
        for op_index, op in enumerate(sc.ops):
            seed = f"{sc.label}:{op_index}"
            if isinstance(op, Let):
                speaker, addressee = _roles(op.target, anchor, pair)
                cmp_phrase = prose.comparator(speaker, "eq", seed)
                sentence = (
                    f"You are {cmp_phrase} "
                    f"{_render_expr(op.expr, speaker, addressee, prose)}."
                )
                lines.append(_speech(speaker, sentence))
            elif isinstance(op, Push):
                speaker, addressee = _roles(op.target, anchor, pair)
                sentence = (
                    f"Remember {_render_expr(op.expr, speaker, addressee, prose)}."
                )
                lines.append(_speech(speaker, sentence))
            elif isinstance(op, Pop):
                speaker, _ = _roles(op.target, anchor, pair)
                lines.append(
                    _speech(speaker, prose.recall_placeholder(speaker, op.recall))
                )
            elif isinstance(op, ReadChar):
                speaker, _ = _roles(op.target, anchor, pair)
                lines.append(_speech(speaker, "Open your mind!"))
            elif isinstance(op, PrintChar):
                speaker, _ = _roles(op.target, anchor, pair)
                lines.append(_speech(speaker, "Speak your mind!"))
            elif isinstance(op, PrintInt):
                speaker, _ = _roles(op.target, anchor, pair)
                lines.append(_speech(speaker, "Open your heart!"))
            elif isinstance(op, Branch):
                tested = _tested_char(op, sc)
                if tested in pair:
                    speaker, addressee = _roles(tested, anchor, pair)
                    cmp_phrase = prose.comparator(speaker, op.cond.op, seed)
                    rhs = _render_expr(op.cond.right, speaker, addressee, prose)
                    question = f"Are you {cmp_phrase} {rhs}?"
                else:
                    # Off-stage tested character: third-person question by
                    # the anchor; the other pair member answers the Ifs.
                    speaker = anchor
                    addressee = pair[1] if pair[0] == anchor else pair[0]
                    cmp_phrase = prose.comparator(speaker, op.cond.op, seed)
                    rhs = _render_expr(op.cond.right, speaker, addressee, prose)
                    question = f"Is {tested.value} {cmp_phrase} {rhs}?"
                lines.append(_speech(speaker, question))
                lines.append(
                    _speech(
                        addressee,
                        _jump_sentence(
                            prose,
                            addressee,
                            index,
                            op.then,
                            order,
                            f"{seed}:then",
                            prefix="If so, ",
                        ),
                    )
                )
                if op.else_ is not None:
                    lines.append(
                        _speech(
                            addressee,
                            _jump_sentence(
                                prose,
                                addressee,
                                index,
                                op.else_,
                                order,
                                f"{seed}:else",
                                prefix="If not, ",
                            ),
                        )
                    )
            elif isinstance(op, Goto):
                target_entry = entry.get(op.target)
                if target_entry is not None and set(pair) != set(target_entry):
                    for direction in _stage_directions(pair, target_entry):
                        lines.append(direction)
                        lines.append("")
                lines.append(
                    _speech(
                        anchor,
                        _jump_sentence(prose, anchor, index, op.target, order, seed),
                    )
                )
            elif isinstance(op, HaltAct):
                lines.append("[Exeunt]")
                lines.append("")
            else:
                raise TypeError(f"unknown op {op!r}")
        blocks.append("\n".join(lines).rstrip() + "\n")
    text = "\n\n".join(blocks)
    if next_act_heading is not None:
        text = text.rstrip() + f"\n\n\n\n{_HEADING_INDENT}{next_act_heading}\n"
    return text
