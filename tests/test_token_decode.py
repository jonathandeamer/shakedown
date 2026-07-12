"""Lexical decoder: unit and malformed-stream cases, per
docs/superpowers/specs/2026-07-11-completability-hardening-design.md §1."""

from __future__ import annotations

import pytest

from scripts.splc.token_decode import DecodedToken, DecodeError, decode_stream
from src_ir import tokens


def test_decodes_simple_paragraph() -> None:
    values = [tokens.PARA, ord("h"), ord("i"), tokens.TEXT_END]
    assert decode_stream(values) == [
        DecodedToken(code=tokens.PARA, payloads=(), text="hi")
    ]


def test_decodes_explicit_list_item() -> None:
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
    assert decode_stream(values) == [
        DecodedToken(code=tokens.LIST_OPEN, payloads=(1,), text=None),
        DecodedToken(code=tokens.LIST_ITEM, payloads=(1,), text=None),
        DecodedToken(code=tokens.PARA, payloads=(), text="a"),
        DecodedToken(code=tokens.ITEM_CLOSE, payloads=(), text=None),
        DecodedToken(code=tokens.LIST_CLOSE, payloads=(), text=None),
    ]


def test_empty_stream_decodes_to_no_tokens() -> None:
    assert decode_stream([]) == []


def test_rejects_unknown_code() -> None:
    with pytest.raises(DecodeError, match="unknown token code 999"):
        decode_stream([999])


def test_rejects_unallocated_but_documented_code() -> None:
    """HEADER (2) is allocated in docs/spl/token-codes.md but has no ARITY
    row yet — not yet shipped, so the decoder must reject it like any other
    unknown code rather than guessing an arity."""
    with pytest.raises(DecodeError, match="unknown token code 2"):
        decode_stream([tokens.HEADER])


def test_rejects_truncated_fixed_payload() -> None:
    with pytest.raises(DecodeError, match="truncated payloads"):
        decode_stream([tokens.LIST_OPEN])


def test_rejects_truncated_text_bearing_token_with_no_terminator() -> None:
    with pytest.raises(DecodeError, match="unterminated text run"):
        decode_stream([tokens.PARA, ord("h"), ord("i")])


def test_rejects_stray_text_end() -> None:
    with pytest.raises(DecodeError, match="unexpected TEXT_END"):
        decode_stream([tokens.TEXT_END])


def test_rejects_stream_end_at_top_level() -> None:
    with pytest.raises(DecodeError, match="STREAM_END escaped"):
        decode_stream([tokens.STREAM_END])


def test_rejects_item_start_at_top_level() -> None:
    with pytest.raises(DecodeError, match="ITEM_START escaped"):
        decode_stream([tokens.ITEM_START])


def test_rejects_stream_end_inside_a_text_run() -> None:
    with pytest.raises(DecodeError, match="framing marker -1 escaped"):
        decode_stream([tokens.PARA, ord("h"), tokens.STREAM_END, tokens.TEXT_END])


def test_rejects_item_start_inside_a_text_run() -> None:
    with pytest.raises(DecodeError, match="framing marker -2 escaped"):
        decode_stream([tokens.PARA, ord("h"), tokens.ITEM_START, tokens.TEXT_END])


def test_rejects_illegal_glyph_value() -> None:
    with pytest.raises(DecodeError, match="illegal glyph value"):
        decode_stream([tokens.PARA, -5, tokens.TEXT_END])
