"""Structural validator for the shipped block grammar: malformed-stream
cases per rejection class, expected-future cases from the target recursive
container grammar, and validation of every committed dump fixture, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §1."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.splc.token_decode import DecodedToken, decode_stream
from scripts.splc.token_structure import StructuralError, validate_stream
from src_ir import tokens

REPO = Path(__file__).parent.parent
BASELINES = REPO / "tests" / "fixtures" / "token_stream"


def _dump_values(path: Path) -> list[int]:
    return [int(line) for line in path.read_text().splitlines()]


def _all_dump_fixtures() -> list[Path]:
    return sorted(BASELINES.rglob("*.dump"))


@pytest.mark.parametrize(
    "path", _all_dump_fixtures(), ids=lambda p: str(p.relative_to(BASELINES))
)
def test_every_committed_dump_decodes_and_validates(path: Path) -> None:
    validate_stream(decode_stream(_dump_values(path)))


def test_flat_list_validates() -> None:
    values = [
        tokens.LIST_OPEN,
        1,
        tokens.LIST_ITEM,
        1,
        ord("a"),
        tokens.TEXT_END,
        tokens.LIST_CLOSE,
    ]
    validate_stream(decode_stream(values))


def test_top_level_paragraph_then_list_validates() -> None:
    values = [
        tokens.PARA,
        ord("h"),
        tokens.TEXT_END,
        tokens.LIST_OPEN,
        1,
        tokens.LIST_ITEM,
        1,
        ord("a"),
        tokens.TEXT_END,
        tokens.LIST_CLOSE,
    ]
    validate_stream(decode_stream(values))


def test_rejects_list_close_without_matching_open() -> None:
    with pytest.raises(StructuralError, match="no matching open list"):
        validate_stream(decode_stream([tokens.LIST_CLOSE]))


def test_rejects_stream_ending_with_list_still_open() -> None:
    with pytest.raises(StructuralError, match="still open"):
        validate_stream(
            decode_stream(
                [tokens.LIST_OPEN, 1, tokens.LIST_ITEM, 1, ord("a"), tokens.TEXT_END]
            )
        )


def test_rejects_empty_list_with_no_item() -> None:
    with pytest.raises(StructuralError, match="without any item"):
        validate_stream(decode_stream([tokens.LIST_OPEN, 1, tokens.LIST_CLOSE]))


def test_rejects_item_outside_any_list() -> None:
    with pytest.raises(StructuralError, match="outside any open list"):
        validate_stream(decode_stream([tokens.LIST_ITEM, 1, ord("a"), tokens.TEXT_END]))


def test_rejects_paragraph_nested_inside_an_open_list() -> None:
    """Expected future case: the target grammar's `item := ITEM_OPEN block*
    ITEM_CLOSE` would let a PARA sit inside an item's block* content, but
    that representation is undecided until Spike B. Today a standalone PARA
    while a list is open must be rejected, not silently accepted."""
    values = [
        tokens.LIST_OPEN,
        1,
        tokens.LIST_ITEM,
        1,
        ord("a"),
        tokens.TEXT_END,
        tokens.PARA,
        ord("b"),
        tokens.TEXT_END,
        tokens.LIST_CLOSE,
    ]
    with pytest.raises(StructuralError, match="not yet legal inside an open list"):
        validate_stream(decode_stream(values))


def test_rejects_nested_list_opened_before_parent_has_an_item() -> None:
    values = [
        tokens.LIST_OPEN,
        1,
        tokens.LIST_OPEN,
        1,
        tokens.LIST_ITEM,
        1,
        ord("a"),
        tokens.TEXT_END,
        tokens.LIST_CLOSE,
        tokens.LIST_CLOSE,
    ]
    with pytest.raises(StructuralError, match="before its parent list had any item"):
        validate_stream(decode_stream(values))


def test_rejects_inline_marker_at_block_level() -> None:
    """Expected future case: ANCHOR_* markers are allocated (docs/spl/token-
    codes.md) for Act III inline spans, but have no ARITY row yet, so they
    cannot even be lexically decoded today. The structural role table
    already classifies them INLINE_MARKER for when Spike B's span work adds
    their arity; feed a hand-built DecodedToken directly to prove the
    validator rejects a bare inline marker at block level rather than
    silently accepting an undecided representation."""
    with pytest.raises(StructuralError, match="not yet legal in the block-level"):
        validate_stream([DecodedToken(code=tokens.ANCHOR_OPEN, payloads=(), text=None)])
