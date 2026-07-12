"""splc IR interpreter: every op, both branch arms, EOF, underflow
diagnostics, step-limit failure, and cross-act state handoff."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from scripts.splc.interpret import (
    DivisionByZero,
    InterpreterState,
    InterpretResult,
    InvalidCharCode,
    StackUnderflow,
    StepLimitExceeded,
    run_act,
)
from scripts.splc.ir import (
    Act,
    BinOp,
    Char,
    Expr,
    Op,
    act,
    add,
    branch,
    const,
    div,
    eq,
    goto,
    gt,
    halt_act,
    let,
    lt,
    mod,
    mul,
    pop,
    print_char,
    print_int,
    push,
    read_char,
    scene,
    sub,
    val,
)

BinOpBuilder = Callable[[Expr, Expr], BinOp]

ROSALIND = Char.ROSALIND
HORATIO = Char.HORATIO


def _one_scene_act(number: int, *ops: Op) -> Act:
    return act(number, ROSALIND, [scene("S", *ops, companion=HORATIO)])


def test_let_evaluates_const_and_val() -> None:
    a = _one_scene_act(
        1, let(ROSALIND, const(7)), let(HORATIO, val(ROSALIND)), halt_act()
    )
    state = InterpreterState()
    result = run_act(a, state, step_limit=100)
    assert isinstance(result, InterpretResult)
    assert result.state.values[ROSALIND] == 7
    assert result.state.values[HORATIO] == 7


@pytest.mark.parametrize(
    ("op", "left", "right", "expected"),
    [
        (add, 3, 4, 7),
        (sub, 3, 4, -1),
        (mul, 3, 4, 12),
        (div, 7, 2, 3),
        (div, -7, 2, -3),
        (mod, 7, 2, 1),
        (mod, -7, 2, -1),
    ],
)
def test_binop_variants(op: BinOpBuilder, left: int, right: int, expected: int) -> None:
    a = _one_scene_act(1, let(ROSALIND, op(const(left), const(right))), halt_act())
    state = InterpreterState()
    result = run_act(a, state, step_limit=100)
    assert result.state.values[ROSALIND] == expected


def test_division_by_zero_raises_with_diagnostic() -> None:
    a = _one_scene_act(1, let(ROSALIND, div(const(1), const(0))), halt_act())
    with pytest.raises(DivisionByZero) as excinfo:
        run_act(a, InterpreterState(), step_limit=100)
    diagnostic = excinfo.value.diagnostic
    assert diagnostic.act == 1
    assert diagnostic.scene == "S"
    assert diagnostic.step == 1


def test_push_then_pop_round_trips_value() -> None:
    a = _one_scene_act(
        1,
        push(ROSALIND, const(42)),
        pop(ROSALIND, "the coin"),
        halt_act(),
    )
    state = InterpreterState()
    result = run_act(a, state, step_limit=100)
    assert result.state.values[ROSALIND] == 42
    assert result.state.stacks[ROSALIND] == []


def test_pop_underflow_names_act_scene_char_step() -> None:
    a = _one_scene_act(1, pop(ROSALIND, "nothing"), halt_act())
    with pytest.raises(StackUnderflow) as excinfo:
        run_act(a, InterpreterState(), step_limit=100)
    diagnostic = excinfo.value.diagnostic
    assert diagnostic.act == 1
    assert diagnostic.scene == "S"
    assert diagnostic.char == ROSALIND
    assert diagnostic.step == 1


def test_read_char_advances_cursor_then_reports_eof_as_negative_one() -> None:
    a = _one_scene_act(
        1,
        read_char(ROSALIND),
        read_char(HORATIO),
        halt_act(),
    )
    state = InterpreterState(input_text="a")
    result = run_act(a, state, step_limit=100)
    assert result.state.values[ROSALIND] == ord("a")
    assert result.state.values[HORATIO] == -1
    assert result.state.input_pos == 1


def test_print_char_appends_to_output() -> None:
    a = _one_scene_act(
        1, let(ROSALIND, const(ord("!"))), print_char(ROSALIND), halt_act()
    )
    state = InterpreterState()
    result = run_act(a, state, step_limit=100)
    assert result.state.output_text() == "!"


def test_print_char_negative_code_raises_invalid_char_code() -> None:
    a = _one_scene_act(1, read_char(ROSALIND), print_char(ROSALIND), halt_act())
    with pytest.raises(InvalidCharCode) as excinfo:
        run_act(a, InterpreterState(input_text=""), step_limit=100)
    assert excinfo.value.code == -1
    assert excinfo.value.diagnostic.char == ROSALIND


def test_print_char_out_of_range_code_raises_invalid_char_code() -> None:
    a = _one_scene_act(
        1, let(ROSALIND, const(0x110000)), print_char(ROSALIND), halt_act()
    )
    with pytest.raises(InvalidCharCode) as excinfo:
        run_act(a, InterpreterState(), step_limit=100)
    assert excinfo.value.code == 0x110000


def test_print_int_appends_decimal_representation() -> None:
    a = _one_scene_act(1, let(ROSALIND, const(-5)), print_int(ROSALIND), halt_act())
    state = InterpreterState()
    result = run_act(a, state, step_limit=100)
    assert result.state.output_text() == "-5"


def test_branch_then_arm_taken() -> None:
    a = act(
        1,
        ROSALIND,
        [
            scene("START", branch(eq(const(1), const(1)), "THEN", "ELSE")),
            scene("THEN", let(ROSALIND, const(1)), halt_act(), companion=HORATIO),
            scene("ELSE", let(ROSALIND, const(2)), halt_act(), companion=HORATIO),
        ],
    )
    result = run_act(a, InterpreterState(), step_limit=100)
    assert result.state.values[ROSALIND] == 1


def test_branch_else_arm_taken() -> None:
    a = act(
        1,
        ROSALIND,
        [
            scene("START", branch(gt(const(1), const(2)), "THEN", "ELSE")),
            scene("THEN", let(ROSALIND, const(1)), halt_act(), companion=HORATIO),
            scene("ELSE", let(ROSALIND, const(2)), halt_act(), companion=HORATIO),
        ],
    )
    result = run_act(a, InterpreterState(), step_limit=100)
    assert result.state.values[ROSALIND] == 2


def test_branch_lt_comparator() -> None:
    a = act(
        1,
        ROSALIND,
        [
            scene("START", branch(lt(const(1), const(2)), "THEN", "ELSE")),
            scene("THEN", let(ROSALIND, const(1)), halt_act(), companion=HORATIO),
            scene("ELSE", let(ROSALIND, const(2)), halt_act(), companion=HORATIO),
        ],
    )
    result = run_act(a, InterpreterState(), step_limit=100)
    assert result.state.values[ROSALIND] == 1


def test_non_exhaustive_branch_untaken_falls_off_scene() -> None:
    a = act(
        1,
        ROSALIND,
        [scene("START", branch(eq(const(1), const(2)), "THEN"), companion=HORATIO)],
    )
    with pytest.raises(Exception, match="fell off scene without a jump"):
        run_act(a, InterpreterState(), step_limit=100)


def test_goto_jumps_to_target_scene() -> None:
    a = act(
        1,
        ROSALIND,
        [
            scene("START", goto("END")),
            scene("END", let(ROSALIND, const(9)), halt_act(), companion=HORATIO),
        ],
    )
    result = run_act(a, InterpreterState(), step_limit=100)
    assert result.state.values[ROSALIND] == 9


def test_halt_act_stops_execution_and_reports_steps() -> None:
    a = _one_scene_act(1, let(ROSALIND, const(1)), halt_act())
    result = run_act(a, InterpreterState(), step_limit=100)
    assert result.state.values[ROSALIND] == 1
    assert result.steps == 2


def test_step_limit_exceeded_names_act_scene_and_limit() -> None:
    a = act(1, ROSALIND, [scene("LOOP", goto("LOOP"))])
    with pytest.raises(StepLimitExceeded) as excinfo:
        run_act(a, InterpreterState(), step_limit=5)
    assert excinfo.value.step_limit == 5
    assert excinfo.value.diagnostic.act == 1
    assert excinfo.value.diagnostic.scene == "LOOP"


def test_state_handoff_carries_values_and_stacks_across_acts() -> None:
    act_one = _one_scene_act(
        1, let(ROSALIND, const(3)), push(HORATIO, const(11)), halt_act()
    )
    act_two = _one_scene_act(2, pop(HORATIO, "the token"), halt_act())

    state = InterpreterState()
    first = run_act(act_one, state, step_limit=100)
    assert first.state is state

    second = run_act(act_two, first.state, step_limit=100)
    assert second.state.values[ROSALIND] == 3
    assert second.state.values[HORATIO] == 11
    assert second.state.stacks[HORATIO] == []
