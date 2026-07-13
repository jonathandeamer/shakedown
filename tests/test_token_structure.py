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
    # Spike A list dumps retain the old text-bearing LIST_ITEM vocabulary until
    # Task 3 migrates Act II and its reviewed baselines atomically.
    return sorted(
        path for path in BASELINES.rglob("*.dump") if "lists" not in path.parts
    )


@pytest.mark.parametrize(
    "path", _all_dump_fixtures(), ids=lambda p: str(p.relative_to(BASELINES))
)
def test_every_committed_dump_decodes_and_validates(path: Path) -> None:
    values = _dump_values(path)
    if "nested_blocks" in path.parts:
        # Spike B's reviewed Act-II carrier fixtures include the runtime stack
        # floor.  The inter-act/debug stream contract begins above that floor.
        assert values[-1] == tokens.STREAM_END
        assert tokens.STREAM_END not in values[:-1]
        values = values[:-1]
    validate_stream(decode_stream(values))


def test_flat_list_validates() -> None:
    values = [
        tokens.LIST_OPEN,
        1,
        tokens.LIST_ITEM,
        1,
        tokens.PARA,
        ord("a"),
        tokens.TEXT_END,
        tokens.ITEM_CLOSE,
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
        tokens.PARA,
        ord("a"),
        tokens.TEXT_END,
        tokens.ITEM_CLOSE,
        tokens.LIST_CLOSE,
    ]
    validate_stream(decode_stream(values))


def test_rejects_list_close_without_matching_open() -> None:
    with pytest.raises(StructuralError, match="no matching open list"):
        validate_stream(decode_stream([tokens.LIST_CLOSE]))


def test_rejects_stream_ending_with_list_still_open() -> None:
    with pytest.raises(StructuralError, match="still open"):
        validate_stream(decode_stream([tokens.LIST_OPEN, 1, tokens.LIST_ITEM, 1]))


def test_rejects_empty_list_with_no_item() -> None:
    with pytest.raises(StructuralError, match="without any item"):
        validate_stream(decode_stream([tokens.LIST_OPEN, 1, tokens.LIST_CLOSE]))


def test_rejects_item_outside_any_list() -> None:
    with pytest.raises(StructuralError, match="outside any open list"):
        validate_stream(decode_stream([tokens.LIST_ITEM, 1]))


def test_rejects_paragraph_directly_inside_an_open_list() -> None:
    values = [
        tokens.LIST_OPEN,
        1,
        tokens.LIST_ITEM,
        1,
        tokens.ITEM_CLOSE,
        tokens.PARA,
        ord("b"),
        tokens.TEXT_END,
        tokens.LIST_CLOSE,
    ]
    with pytest.raises(StructuralError, match="where a block is not legal"):
        validate_stream(decode_stream(values))


def test_rejects_nested_list_opened_before_parent_has_an_item() -> None:
    values = [
        tokens.LIST_OPEN,
        1,
        tokens.LIST_OPEN,
        1,
        tokens.LIST_ITEM,
        1,
        tokens.ITEM_CLOSE,
        tokens.LIST_CLOSE,
        tokens.LIST_CLOSE,
    ]
    with pytest.raises(StructuralError, match="where a block is not legal"):
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


def test_blockquote_tokens_have_zero_payloads_and_no_text() -> None:
    assert tokens.ARITY[tokens.BLOCKQUOTE_OPEN] == tokens.TokenArity(0, False)
    assert tokens.ARITY[tokens.BLOCKQUOTE_CLOSE] == tokens.TokenArity(0, False)


def test_item_close_has_container_close_role() -> None:
    assert tokens.ROLES[tokens.ITEM_CLOSE] == tokens.StructuralRole.ITEM_CLOSE


def test_blockquote_open_and_close_have_container_roles() -> None:
    assert tokens.ROLES[tokens.BLOCKQUOTE_OPEN] == tokens.StructuralRole.CONTAINER_OPEN
    assert (
        tokens.ROLES[tokens.BLOCKQUOTE_CLOSE] == tokens.StructuralRole.CONTAINER_CLOSE
    )


def test_rejects_unclosed_blockquote() -> None:
    with pytest.raises(StructuralError, match="still open"):
        validate_stream(decode_stream([tokens.BLOCKQUOTE_OPEN]))


def test_rejects_blockquote_close_without_matching_open() -> None:
    with pytest.raises(StructuralError, match="no matching open blockquote"):
        validate_stream(decode_stream([tokens.BLOCKQUOTE_CLOSE]))


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


def test_rejects_crossed_item_and_blockquote_closes() -> None:
    values = [tokens.LIST_OPEN, 1, tokens.LIST_ITEM, 1, tokens.BLOCKQUOTE_OPEN]
    with pytest.raises(StructuralError, match="no matching open item"):
        validate_stream(decode_stream(values + [tokens.ITEM_CLOSE]))


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
