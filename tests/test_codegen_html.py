"""Codegen byte-literal round-trip tests."""

from __future__ import annotations

import pytest

from scripts.codegen_html import (
    emit_byte,
    emit_literal,
    emit_speak_lines,
    parse_value_phrase,
)


@pytest.mark.parametrize(
    ("byte_value", "expected_includes"),
    [
        (0, "nothing"),
        (1, "a cat"),
        (2, "a big cat"),
        (4, "a big big cat"),
    ],
)
def test_emit_byte_atom_forms(byte_value: int, expected_includes: str) -> None:
    spl = emit_byte(byte_value)
    assert expected_includes in spl


def test_emit_byte_returns_compound_when_no_atom() -> None:
    spl = emit_byte(3)
    assert "the sum of" in spl


@pytest.mark.parametrize("byte_value", list(range(0, 128)))
def test_emit_byte_round_trips_for_ascii(byte_value: int) -> None:
    spl = emit_byte(byte_value)
    assert parse_value_phrase(spl) == byte_value


def test_emit_literal_for_amp() -> None:
    bytes_ = emit_literal(b"&amp;")
    assert len(bytes_) == 5
    parsed = [parse_value_phrase(p) for p in bytes_]
    assert parsed == [ord("&"), ord("a"), ord("m"), ord("p"), ord(";")]


def test_emit_literal_for_open_p_tag() -> None:
    bytes_ = emit_literal(b"<p>")
    parsed = [parse_value_phrase(p) for p in bytes_]
    assert parsed == [ord("<"), ord("p"), ord(">")]


def test_emit_speak_lines_for_literal() -> None:
    lines = emit_speak_lines(b"<p>", speaker="Prospero")
    expected: list[str] = []
    for phrase in emit_literal(b"<p>"):
        expected.append(f"Prospero: You are as good as {phrase}.")
        expected.append("Prospero: Speak your mind!")
    assert lines == expected


def test_atom_cap_on_emitted_atoms() -> None:
    for value in range(0, 128):
        spl = emit_byte(value)
        for atom in _atoms(spl):
            assert len(atom.split()) <= 6, (value, atom)


def _atoms(phrase: str) -> list[str]:
    text = phrase.strip()
    prefix = "the sum of "
    if text.lower().startswith(prefix):
        rest = text[len(prefix) :]
        idx = rest.find(" and ")
        if idx == -1:
            return [text]
        return _atoms(rest[:idx]) + _atoms(rest[idx + len(" and ") :])
    return [text]
