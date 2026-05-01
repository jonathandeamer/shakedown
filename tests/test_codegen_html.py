"""Codegen byte-literal round-trip tests."""

from __future__ import annotations

import re

import pytest

from scripts.codegen_html import (
    emit_byte,
    emit_literal,
    emit_speak_lines,
    emit_value,
    parse_value_phrase,
)


@pytest.mark.parametrize(
    ("byte_value", "expected_includes"),
    [
        (0, "nothing"),
        (1, "a cat"),
        (2, "a black cat"),
        (4, "a furry black cat"),
        (16, "a normal little furry black cat"),
    ],
)
def test_emit_byte_atom_forms(byte_value: int, expected_includes: str) -> None:
    spl = emit_byte(byte_value)
    assert expected_includes in spl


def test_emit_byte_returns_compound_when_no_atom() -> None:
    spl = emit_byte(3)
    assert "the sum of" in spl


def test_emit_byte_uses_toml_value_atoms() -> None:
    assert emit_byte(16) == "a normal little furry black cat"
    assert "big big big big cat" not in emit_byte(16)


@pytest.mark.parametrize("value", [38, 65, 97, 256, 505])
def test_emit_value_uses_compact_large_value_recipes(value: int) -> None:
    phrase = emit_value(value)

    assert parse_value_phrase(phrase) == value
    assert "the product of" in phrase or "the square of" in phrase
    assert _max_atom_repetition(phrase) <= 3


def test_parse_value_phrase_understands_compact_arithmetic() -> None:
    assert parse_value_phrase("the square of a normal little furry black cat") == 256
    assert (
        parse_value_phrase(
            "the product of a normal little furry black cat and a furry black cat"
        )
        == 64
    )


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


def test_emit_byte_atoms_do_not_repeat_adjectives() -> None:
    for value in [1, 2, 4, 8, 16]:
        phrase = emit_byte(value)
        adjectives = _atom_adjectives(phrase)
        assert len(adjectives) == len(set(adjectives)), phrase


def _max_atom_repetition(phrase: str) -> int:
    atoms = _atoms(phrase)
    return max((atoms.count(atom) for atom in set(atoms)), default=0)


def _atoms(phrase: str) -> list[str]:
    text = phrase.strip()
    for prefix in ("the sum of ", "the product of "):
        if not text.lower().startswith(prefix):
            continue
        rest = text[len(prefix) :]
        left, right = _split_binary_for_test(rest, phrase)
        return _atoms(left) + _atoms(right)
    square_prefix = "the square of "
    if text.lower().startswith(square_prefix):
        return _atoms(text[len(square_prefix) :])
    return [text]


def _split_binary_for_test(rest: str, phrase: str) -> tuple[str, str]:
    for match in reversed(list(re.finditer(r" and ", rest))):
        left = rest[: match.start()]
        right = rest[match.end() :]
        try:
            parse_value_phrase(left)
            parse_value_phrase(right)
        except ValueError:
            continue
        return left, right
    raise ValueError(f"malformed binary expression: {phrase!r}")


def _atom_adjectives(phrase: str) -> list[str]:
    words = phrase.split()
    return words[1:-1]
