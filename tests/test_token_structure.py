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


TARGET_GRAMMAR = """\
document   := block*
block      := PARA | list | blockquote
list       := LIST_OPEN(kind) (LIST_ITEM(looseness) block* ITEM_CLOSE)+ LIST_CLOSE
blockquote := BLOCKQUOTE_OPEN block* BLOCKQUOTE_CLOSE
"""  # docs/superpowers/specs/2026-07-12-spike-b-nested-blocks-design.md


def test_target_grammar_transcription_matches_the_design_doc() -> None:
    design_doc = (
        REPO
        / "docs"
        / "superpowers"
        / "specs"
        / "2026-07-12-spike-b-nested-blocks-design.md"
    ).read_text()
    assert TARGET_GRAMMAR.strip() in design_doc


def test_list_item_with_nested_blockquote_validates() -> None:
    values = [
        tokens.LIST_OPEN,
        1,
        tokens.LIST_ITEM,
        1,
        tokens.PARA,
        ord("a"),
        tokens.TEXT_END,
        tokens.BLOCKQUOTE_OPEN,
        tokens.PARA,
        ord("b"),
        tokens.TEXT_END,
        tokens.BLOCKQUOTE_CLOSE,
        tokens.ITEM_CLOSE,
        tokens.LIST_CLOSE,
    ]
    validate_stream(decode_stream(values))


def test_rejects_item_close_without_matching_open_item() -> None:
    with pytest.raises(StructuralError, match="item close has no matching open item"):
        validate_stream(decode_stream([tokens.ITEM_CLOSE]))


def test_item_close_is_in_arity_table_with_zero_payloads_and_no_text() -> None:
    assert tokens.ARITY[tokens.ITEM_CLOSE] == tokens.TokenArity(0, False)


def test_blockquote_open_and_close_are_in_arity_table_with_zero_payloads_and_no_text() -> None:
    assert tokens.ARITY[tokens.BLOCKQUOTE_OPEN] == tokens.TokenArity(0, False)
    assert tokens.ARITY[tokens.BLOCKQUOTE_CLOSE] == tokens.TokenArity(0, False)


def test_item_close_has_container_close_role() -> None:
    assert tokens.ROLES[tokens.ITEM_CLOSE] == tokens.StructuralRole.CONTAINER_CLOSE


def test_blockquote_open_and_close_have_container_roles() -> None:
    assert tokens.ROLES[tokens.BLOCKQUOTE_OPEN] == tokens.StructuralRole.CONTAINER_OPEN
    assert tokens.ROLES[tokens.BLOCKQUOTE_CLOSE] == tokens.StructuralRole.CONTAINER_CLOSE


def test_rejects_blockquote_as_container_not_yet_shipped() -> None:
    """Expected future case: `blockquote := BLOCKQUOTE_OPEN block*
    BLOCKQUOTE_CLOSE` is in the target grammar and BLOCKQUOTE_OPEN/CLOSE
    already carry CONTAINER_OPEN/CONTAINER_CLOSE roles (src_ir/tokens.py),
    but they have no ARITY row yet, so decode_stream cannot lex them from an
    integer dump. Feed hand-built DecodedTokens directly to prove the
    validator still rejects the container as unshipped rather than silently
    accepting an undecided representation."""
    with pytest.raises(StructuralError, match="not yet shipped"):
        validate_stream(
            [DecodedToken(code=tokens.BLOCKQUOTE_OPEN, payloads=(), text=None)]
        )


def test_rejects_blockquote_close_not_yet_shipped() -> None:
    with pytest.raises(StructuralError, match="not yet shipped"):
        validate_stream(
            [DecodedToken(code=tokens.BLOCKQUOTE_CLOSE, payloads=(), text=None)]
        )


@pytest.mark.parametrize(
    "code", [tokens.HEADER, tokens.HR, tokens.CODE_BLOCK, tokens.RAW_HTML_HASH]
)
def test_rejects_other_target_grammar_leaf_blocks_not_yet_shipped(code: int) -> None:
    """Expected future case: the target grammar's `block` production admits
    header, horizontal_rule, code_block, and raw_html alongside paragraph.
    Each code already has a LEAF_BLOCK role, but only PARA is shipped
    today (`docs/superpowers/specs/2026-07-11-completability-hardening-
    design.md` §1 says this validator "must not accept them early")."""
    with pytest.raises(StructuralError, match="not yet shipped"):
        validate_stream([DecodedToken(code=code, payloads=(), text=None)])


def test_rejects_container_block_nested_inside_a_list_item() -> None:
    """Expected future case: the target grammar's `item := ITEM_OPEN block*
    ITEM_CLOSE` would let a blockquote sit inside an item's block* content.
    No ITEM_OPEN/ITEM_CLOSE token exists yet — Spike B decides whether
    LIST_ITEM's implicit closure is kept or replaced — so this feeds a
    BLOCKQUOTE_OPEN directly after a LIST_ITEM and confirms it is rejected
    for being an unshipped container, not accepted as nested item content."""
    with pytest.raises(StructuralError, match="not yet shipped"):
        validate_stream(
            decode_stream(
                [tokens.LIST_OPEN, 1, tokens.LIST_ITEM, 1, ord("a"), tokens.TEXT_END]
            )
            + [DecodedToken(code=tokens.BLOCKQUOTE_OPEN, payloads=(), text=None)]
        )


def test_rejects_token_with_no_structural_role() -> None:
    """Every allocated code has a role (test_token_structural_roles.py), so
    this can only be reached by a code that isn't allocated at all. The
    lexical decoder already rejects such codes from a real dump
    (test_rejects_unknown_code), so exercise this branch directly with a
    hand-built DecodedToken to prove the structural validator also refuses
    to guess a role for it rather than silently skipping the token."""
    with pytest.raises(StructuralError, match="has no structural role"):
        validate_stream([DecodedToken(code=999, payloads=(), text=None)])


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
