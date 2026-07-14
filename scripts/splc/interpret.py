"""Instruction-level interpreter for the closed splc IR.

Verification-only: it interprets `scripts.splc.ir` acts directly, never
generated SPL prose, and is never invoked by `./shakedown`. It exists so
tests can execute an act's instruction stream without a `shakespeare`
subprocess. See docs/superpowers/specs/2026-07-11-completability-hardening-design.md
§2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from scripts.slice3_links import strip_reference_definitions
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
    Pop,
    PrintChar,
    PrintInt,
    Push,
    ReadChar,
    Val,
)


@dataclass
class InterpreterState:
    """Cross-act state: character values, stacks, stdin cursor, and output.

    Injectable so tests can run one act, inspect the resulting state, and
    hand it to the next act unchanged — mirroring how the real interpreter
    carries values and stacks across act boundaries.
    """

    values: dict[Char, int] = field(default_factory=lambda: {c: 0 for c in Char})
    stacks: dict[Char, list[int]] = field(default_factory=lambda: {c: [] for c in Char})
    input_text: str = ""
    input_pos: int = 0
    output: list[str] = field(default_factory=list)

    def output_text(self) -> str:
        return "".join(self.output)


@dataclass(frozen=True)
class Diagnostic:
    """Where an interpreter failure happened: act, scene, step, and — for
    failures tied to a specific character's value or stack — that character.
    """

    act: int
    scene: str
    step: int
    char: Char | None = None


@dataclass(frozen=True)
class InterpretResult:
    """Typed success record returned by a completed act run."""

    state: InterpreterState
    steps: int


class InterpreterError(RuntimeError):
    """Base class for typed interpreter failures; always carries a `Diagnostic`."""

    def __init__(self, diagnostic: Diagnostic, message: str) -> None:
        self.diagnostic = diagnostic
        super().__init__(message)


class StackUnderflow(InterpreterError):
    def __init__(self, act: int, scene: str, char: Char, step: int) -> None:
        diagnostic = Diagnostic(act=act, scene=scene, step=step, char=char)
        super().__init__(
            diagnostic,
            f"act {act} scene {scene} step {step}: stack underflow popping "
            f"{char.value}",
        )


class StepLimitExceeded(InterpreterError):
    def __init__(self, act: int, scene: str, step_limit: int) -> None:
        self.step_limit = step_limit
        diagnostic = Diagnostic(act=act, scene=scene, step=step_limit)
        super().__init__(
            diagnostic, f"act {act} scene {scene}: exceeded step limit {step_limit}"
        )


class DivisionByZero(InterpreterError):
    def __init__(self, act: int, scene: str, step: int) -> None:
        diagnostic = Diagnostic(act=act, scene=scene, step=step)
        super().__init__(
            diagnostic, f"act {act} scene {scene} step {step}: division by zero"
        )


class InvalidCharCode(InterpreterError):
    def __init__(self, act: int, scene: str, char: Char, step: int, code: int) -> None:
        self.code = code
        diagnostic = Diagnostic(act=act, scene=scene, step=step, char=char)
        super().__init__(
            diagnostic,
            f"act {act} scene {scene} step {step}: {char.value} holds invalid "
            f"character code {code}",
        )


def _trunc_div(left: int, right: int) -> int:
    quotient = abs(left) // abs(right)
    return -quotient if (left < 0) != (right < 0) else quotient


def _trunc_mod(left: int, right: int) -> int:
    return left - _trunc_div(left, right) * right


def _eval_binop(
    op: BinOp, state: InterpreterState, act: int, scene: str, step: int
) -> int:
    left = _eval(op.left, state, act, scene, step)
    right = _eval(op.right, state, act, scene, step)
    if op.op == "add":
        return left + right
    if op.op == "sub":
        return left - right
    if op.op == "mul":
        return left * right
    if right == 0:
        raise DivisionByZero(act, scene, step)
    if op.op == "div":
        return _trunc_div(left, right)
    if op.op == "mod":
        return _trunc_mod(left, right)
    raise TypeError(f"unknown binop {op.op!r}")


def _eval(expr: Expr, state: InterpreterState, act: int, scene: str, step: int) -> int:
    if isinstance(expr, Const):
        return expr.value
    if isinstance(expr, Val):
        return state.values[expr.char]
    if isinstance(expr, BinOp):
        return _eval_binop(expr, state, act, scene, step)
    raise TypeError(f"unknown expression node {expr!r}")


def _eval_cond(
    cond: Cond, state: InterpreterState, act: int, scene: str, step: int
) -> bool:
    left = _eval(cond.left, state, act, scene, step)
    right = _eval(cond.right, state, act, scene, step)
    if cond.op == "eq":
        return left == right
    if cond.op == "gt":
        return left > right
    if cond.op == "lt":
        return left < right
    raise TypeError(f"unknown comparator {cond.op!r}")


class InterpreterObserver(Protocol):
    """Verification-only boundary hooks for `run_act`.

    Callers (e.g. `scripts.splc.contracts` tests) implement this to record
    per-push/pop stack depth without the interpreter itself depending on any
    contract module. Observing adds no runtime operations or rendered SPL —
    it only reads state the interpreter already mutates.
    """

    def on_push(self, char: Char, value: int, stack_after: list[int]) -> None: ...

    def on_pop(self, char: Char, value: int, stack_after: list[int]) -> None: ...

    def on_scene(self, label: str, state: InterpreterState) -> None: ...


def run_act(
    act: Act,
    state: InterpreterState,
    step_limit: int,
    observer: InterpreterObserver | None = None,
) -> InterpretResult:
    """Execute `act` starting at its first scene, mutating `state` in place.

    `state` is injectable: callers construct it once, pass it into one act,
    and hand the returned `InterpretResult.state` (the same mutated object)
    into the next act, so cross-act values and stacks carry forward exactly
    as they do across real act boundaries.

    Scene jumps (`Goto`, `Branch`) resolve only within this act, matching the
    IR-level validation in `scripts.splc.validate`. `HaltAct` ends the act;
    running off the end of a scene's ops without a jump cannot happen because
    every scene is validated as terminal.
    """
    if act.number == 1 and state.input_pos == 0:
        state.input_text, _ = strip_reference_definitions(state.input_text)
        if state.input_text.endswith("\n\n"):
            state.input_text = state.input_text[:-1]
    by_label = {sc.label: sc for sc in act.scenes}
    label = act.scenes[0].label
    step = 0
    while True:
        sc = by_label[label]
        if observer is not None:
            observer.on_scene(sc.label, state)
        jump: str | None = None
        halted = False
        for op in sc.ops:
            step += 1
            if step > step_limit:
                raise StepLimitExceeded(act.number, sc.label, step_limit)
            if isinstance(op, Let):
                state.values[op.target] = _eval(
                    op.expr, state, act.number, sc.label, step
                )
            elif isinstance(op, Push):
                value = _eval(op.expr, state, act.number, sc.label, step)
                stack = state.stacks[op.target]
                stack.append(value)
                if observer is not None:
                    observer.on_push(op.target, value, stack)
            elif isinstance(op, Pop):
                stack = state.stacks[op.target]
                if not stack:
                    raise StackUnderflow(act.number, sc.label, op.target, step)
                value = stack.pop()
                state.values[op.target] = value
                if observer is not None:
                    observer.on_pop(op.target, value, stack)
            elif isinstance(op, ReadChar):
                if state.input_pos < len(state.input_text):
                    state.values[op.target] = ord(state.input_text[state.input_pos])
                    state.input_pos += 1
                else:
                    state.values[op.target] = -1
            elif isinstance(op, PrintChar):
                code = state.values[op.target]
                if code < 0:
                    raise InvalidCharCode(act.number, sc.label, op.target, step, code)
                try:
                    state.output.append(chr(code))
                except ValueError as exc:
                    raise InvalidCharCode(
                        act.number, sc.label, op.target, step, code
                    ) from exc
            elif isinstance(op, PrintInt):
                state.output.append(str(state.values[op.target]))
            elif isinstance(op, Branch):
                taken = _eval_cond(op.cond, state, act.number, sc.label, step)
                if taken:
                    jump = op.then
                    break
                elif op.else_ is not None:
                    jump = op.else_
                    break
                # Non-exhaustive branch, condition false: fall through to
                # the scene's next op, matching SPL's "if" semantics where
                # only a taken (or exhaustive) branch ends the scene early.
            elif isinstance(op, Goto):
                jump = op.target
                break
            elif isinstance(op, HaltAct):
                halted = True
                break
            else:
                raise TypeError(f"unknown op {op!r}")
        if halted:
            return InterpretResult(state=state, steps=step)
        if jump is None:
            # Validation guarantees every scene ends in goto/halt/exhaustive
            # branch, so an untaken non-exhaustive branch falls through here
            # only when the scene has no further ops after it — unreachable
            # per `validate._check_terminal`.
            raise InterpreterError(
                Diagnostic(act=act.number, scene=sc.label, step=step),
                f"act {act.number} scene {sc.label}: fell off scene without a jump",
            )
        label = jump
