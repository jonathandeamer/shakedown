"""IR for the splc compiler: scenes as states, a closed instruction set.

There is deliberately no escape hatch to raw SPL. If the instruction set
cannot express something, extend the instruction set (a compiler change
with tests) — never bypass it. See
docs/superpowers/specs/2026-07-05-spl-ir-compiler-design.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class Char(Enum):
    """The fixed dramatis personae. The cast is closed; adding a character
    is an architecture change, not an IR edit."""

    ROSALIND = "Rosalind"
    HORATIO = "Horatio"
    PUCK = "Puck"
    HECATE = "Hecate"
    LADY_MACBETH = "Lady Macbeth"
    MACBETH = "Macbeth"
    ROMEO = "Romeo"
    JULIET = "Juliet"
    PROSPERO = "Prospero"

    @property
    def toml_key(self) -> str:
        return self.value.lower().replace(" ", "_")


@dataclass(frozen=True)
class Const:
    value: int


@dataclass(frozen=True)
class Val:
    char: Char


@dataclass(frozen=True)
class BinOp:
    op: Literal["add", "sub", "mul", "div", "mod"]
    left: Expr
    right: Expr


Expr = Const | Val | BinOp


@dataclass(frozen=True)
class Cond:
    op: Literal["eq", "gt", "lt"]
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Let:
    target: Char
    expr: Expr


@dataclass(frozen=True)
class Push:
    target: Char
    expr: Expr


@dataclass(frozen=True)
class Pop:
    target: Char
    recall: str


@dataclass(frozen=True)
class ReadChar:
    target: Char


@dataclass(frozen=True)
class PrintChar:
    target: Char


@dataclass(frozen=True)
class PrintInt:
    target: Char


@dataclass(frozen=True)
class Branch:
    cond: Cond
    then: str
    else_: str | None


@dataclass(frozen=True)
class Goto:
    target: str


@dataclass(frozen=True)
class HaltAct:
    pass


Op = Let | Push | Pop | ReadChar | PrintChar | PrintInt | Branch | Goto | HaltAct


@dataclass(frozen=True)
class Scene:
    label: str
    ops: tuple[Op, ...]
    companion: Char | None


@dataclass(frozen=True)
class Act:
    number: int
    anchor: Char
    scenes: tuple[Scene, ...]


def const(n: int) -> Const:
    return Const(n)


def ch(c: str) -> Const:
    if len(c) != 1:
        raise ValueError(f"ch() takes a single character, got {c!r}")
    return Const(ord(c))


def val(c: Char) -> Val:
    return Val(c)


def add(left: Expr, right: Expr) -> BinOp:
    return BinOp("add", left, right)


def sub(left: Expr, right: Expr) -> BinOp:
    return BinOp("sub", left, right)


def mul(left: Expr, right: Expr) -> BinOp:
    return BinOp("mul", left, right)


def div(left: Expr, right: Expr) -> BinOp:
    return BinOp("div", left, right)


def mod(left: Expr, right: Expr) -> BinOp:
    return BinOp("mod", left, right)


def eq(left: Expr, right: Expr) -> Cond:
    return Cond("eq", left, right)


def gt(left: Expr, right: Expr) -> Cond:
    return Cond("gt", left, right)


def lt(left: Expr, right: Expr) -> Cond:
    return Cond("lt", left, right)


def let(target: Char, expr: Expr) -> Let:
    return Let(target, expr)


def push(target: Char, expr: Expr) -> Push:
    return Push(target, expr)


def pop(target: Char, recall: str) -> Pop:
    return Pop(target, recall)


def read_char(target: Char) -> ReadChar:
    return ReadChar(target)


def print_char(target: Char) -> PrintChar:
    return PrintChar(target)


def print_int(target: Char) -> PrintInt:
    return PrintInt(target)


def branch(cond: Cond, then: str, else_: str | None = None) -> Branch:
    return Branch(cond, then, else_)


def goto(target: str) -> Goto:
    return Goto(target)


def halt_act() -> HaltAct:
    return HaltAct()


def scene(label: str, *ops: Op, companion: Char | None = None) -> Scene:
    return Scene(label, tuple(ops), companion)


def act(number: int, anchor: Char, scenes: list[Scene]) -> Act:
    return Act(number, anchor, tuple(scenes))
