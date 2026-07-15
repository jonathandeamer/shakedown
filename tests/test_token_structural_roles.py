"""Verification-only structural-role metadata on top of the lexical token
table, per docs/superpowers/specs/2026-07-11-completability-hardening-design.md
§1. StructuralRole/ROLES are new — they must never change a numeric code or
an ARITY entry."""

from __future__ import annotations

from src_ir import tokens

PRE_EXISTING_CODES = {
    tokens.PARA: 1,
    tokens.HEADER: 2,
    tokens.HR: 3,
    tokens.LIST_OPEN: 4,
    tokens.LIST_ITEM: 5,
    tokens.LIST_CLOSE: 6,
    tokens.BLOCKQUOTE_OPEN: 7,
    tokens.BLOCKQUOTE_CLOSE: 8,
    tokens.CODE_BLOCK: 9,
    tokens.RAW_HTML_HASH: 10,
    tokens.ANCHOR_OPEN: 11,
    tokens.ANCHOR_TITLE: 12,
    tokens.ANCHOR_TEXT: 13,
    tokens.ANCHOR_CLOSE: 14,
    tokens.ITEM_CLOSE: 15,
}

PRE_EXISTING_ARITY = {
    tokens.PARA: (0, True),
    tokens.HR: (0, False),
    tokens.LIST_OPEN: (1, False),
    tokens.LIST_ITEM: (1, False),
    tokens.LIST_CLOSE: (0, False),
    tokens.BLOCKQUOTE_OPEN: (0, False),
    tokens.BLOCKQUOTE_CLOSE: (0, False),
    tokens.CODE_BLOCK: (0, True),
    tokens.RAW_HTML_HASH: (0, True),
    tokens.ITEM_CLOSE: (0, False),
}


def test_numeric_codes_unchanged() -> None:
    for code, value in PRE_EXISTING_CODES.items():
        assert code == value


def test_arity_table_unchanged() -> None:
    assert {
        code: (arity.payloads, arity.has_text) for code, arity in tokens.ARITY.items()
    } == PRE_EXISTING_ARITY


def test_every_allocated_code_has_a_role() -> None:
    assert set(tokens.ROLES) == set(PRE_EXISTING_CODES)


def test_roles_partition_by_grammar_position() -> None:
    Role = tokens.StructuralRole
    assert tokens.ROLES[tokens.PARA] is Role.LEAF_BLOCK
    assert tokens.ROLES[tokens.HEADER] is Role.LEAF_BLOCK
    assert tokens.ROLES[tokens.HR] is Role.LEAF_BLOCK
    assert tokens.ROLES[tokens.CODE_BLOCK] is Role.LEAF_BLOCK
    assert tokens.ROLES[tokens.RAW_HTML_HASH] is Role.LEAF_BLOCK

    assert tokens.ROLES[tokens.LIST_OPEN] is Role.CONTAINER_OPEN
    assert tokens.ROLES[tokens.BLOCKQUOTE_OPEN] is Role.CONTAINER_OPEN

    assert tokens.ROLES[tokens.LIST_CLOSE] is Role.CONTAINER_CLOSE
    assert tokens.ROLES[tokens.BLOCKQUOTE_CLOSE] is Role.CONTAINER_CLOSE

    assert tokens.ROLES[tokens.LIST_ITEM] is Role.ITEM
    assert tokens.ROLES[tokens.ITEM_CLOSE] is Role.ITEM_CLOSE

    assert tokens.ROLES[tokens.ANCHOR_OPEN] is Role.INLINE_MARKER
    assert tokens.ROLES[tokens.ANCHOR_TITLE] is Role.INLINE_MARKER
    assert tokens.ROLES[tokens.ANCHOR_TEXT] is Role.INLINE_MARKER
    assert tokens.ROLES[tokens.ANCHOR_CLOSE] is Role.INLINE_MARKER


def test_framing_markers_have_no_structural_role() -> None:
    assert tokens.TEXT_END not in tokens.ROLES
    assert tokens.STREAM_END not in tokens.ROLES
    assert tokens.ITEM_START not in tokens.ROLES
