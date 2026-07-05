"""IR dataclasses and builders for the splc compiler."""

from __future__ import annotations

import pytest


def test_expression_builders_produce_frozen_nodes() -> None:
    from scripts.splc.ir import BinOp, Char, Const, Val, add, ch, const, val

    expr = add(val(Char.HECATE), const(1))
    assert isinstance(expr, BinOp)
    assert expr.op == "add"
    assert expr.left == Val(Char.HECATE)
    assert expr.right == Const(1)
    assert ch("*") == Const(42)
    with pytest.raises(AttributeError):
        expr.op = "sub"  # type: ignore[misc]  # frozen dataclass raises


def test_scene_builder_collects_ops_and_companion() -> None:
    from scripts.splc.ir import Char, Goto, Scene, goto, scene

    s = scene("A_LABEL", goto("B_LABEL"), companion=Char.PUCK)
    assert isinstance(s, Scene)
    assert s.label == "A_LABEL"
    assert s.ops == (Goto("B_LABEL"),)
    assert s.companion == Char.PUCK


def test_act_builder_freezes_scene_order() -> None:
    from scripts.splc.ir import Char, act, goto, halt_act, scene

    a = act(
        1,
        Char.HECATE,
        [scene("FIRST", goto("LAST")), scene("LAST", halt_act())],
    )
    assert a.number == 1
    assert a.anchor == Char.HECATE
    assert [s.label for s in a.scenes] == ["FIRST", "LAST"]


def test_branch_defaults_else_to_none() -> None:
    from scripts.splc.ir import Char, branch, const, eq, val

    b = branch(eq(val(Char.PUCK), const(-1)), then="EOF_SCENE")
    assert b.then == "EOF_SCENE"
    assert b.else_ is None


def test_cast_module_reexports_characters() -> None:
    from scripts.splc.ir import Char
    from src_ir.cast import HECATE, PUCK

    assert HECATE is Char.HECATE
    assert PUCK is Char.PUCK


def test_tokens_match_canonical_table() -> None:
    from src_ir import tokens

    assert tokens.PARA == 1
    assert tokens.HEADER == 2
    assert tokens.LIST_OPEN == 4
    assert tokens.LIST_ITEM == 5
    assert tokens.LIST_CLOSE == 6
    assert tokens.ANCHOR_OPEN == 11
    assert tokens.ANCHOR_CLOSE == 14
