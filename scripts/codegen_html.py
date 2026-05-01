"""HTML byte-literal codegen."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.literary_surfaces import load_literary_surfaces

_ROOT = Path(__file__).parent.parent
_LITERARY_TOML = _ROOT / "src" / "literary.toml"
_ATOM_BY_VALUE = load_literary_surfaces(_LITERARY_TOML).value_atoms("default")
_ATOM_TO_VALUE = {phrase: value for value, phrase in _ATOM_BY_VALUE.items()}


def emit_value(value: int) -> str:
    """Return the canonical SPL value phrase for a non-negative integer."""
    if value < 0 or value > 1024:
        raise ValueError(f"value out of supported range: {value}")
    if value in _ATOM_BY_VALUE:
        return _ATOM_BY_VALUE[value]
    return _decompose(value)


def emit_byte(value: int) -> str:
    """Return the canonical SPL value phrase for an integer byte."""
    if value < 0 or value > 255:
        raise ValueError(f"byte value out of range: {value}")
    return emit_value(value)


def _decompose(value: int) -> str:
    terms: list[str] = []
    if value >= 256:
        count = value // 256
        terms.extend([f"the square of {_ATOM_BY_VALUE[16]}"] * count)
        value %= 256

    sixteens = value // 16
    if sixteens == 1:
        terms.append(_ATOM_BY_VALUE[16])
    elif sixteens > 1:
        terms.append(f"the product of {_ATOM_BY_VALUE[16]} and {emit_value(sixteens)}")
    value %= 16

    for atom_value in sorted(_ATOM_BY_VALUE, reverse=True):
        if atom_value == 0:
            continue
        if atom_value <= value:
            terms.append(_ATOM_BY_VALUE[atom_value])
            value -= atom_value

    return _sum_terms(terms)


def _sum_terms(terms: list[str]) -> str:
    if not terms:
        return _ATOM_BY_VALUE[0]
    phrase = terms[-1]
    for term in reversed(terms[:-1]):
        phrase = f"the sum of {term} and {phrase}"
    return phrase


def emit_literal(literal: bytes) -> list[str]:
    """Return one SPL phrase per byte in a literal."""
    return [emit_byte(b) for b in literal]


def emit_speak_lines(literal: bytes, speaker: str) -> list[str]:
    """Return SPL assignment/output lines for a byte literal.

    The speaker assigns each byte value to the listener, then speaks the
    listener's character value with `Speak your mind!`.
    """
    lines: list[str] = []
    for phrase in emit_literal(literal):
        lines.append(f"{speaker}: You are as good as {phrase}.")
        lines.append(f"{speaker}: Speak your mind!")
    return lines


def parse_value_phrase(phrase: str) -> int:
    """Reverse `emit_byte`; used by round-trip tests."""
    text = phrase.strip()
    if text in _ATOM_TO_VALUE:
        return _ATOM_TO_VALUE[text]
    if text.lower().startswith("the square of "):
        inner = text[len("the square of ") :]
        value = parse_value_phrase(inner)
        return value * value
    if text.lower().startswith("the product of "):
        rest = text[len("the product of ") :]
        left, right = _split_binary(rest, phrase)
        return parse_value_phrase(left) * parse_value_phrase(right)
    if text.lower().startswith("the sum of "):
        rest = text[len("the sum of ") :]
        left, right = _split_binary(rest, phrase)
        return parse_value_phrase(left) + parse_value_phrase(right)
    raise ValueError(f"unrecognised atom: {phrase!r}")


def _split_binary(rest: str, phrase: str) -> tuple[str, str]:
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


def main() -> None:
    """CLI smoke test: emit phrases for `&amp;`."""
    for byte, phrase in zip(b"&amp;", emit_literal(b"&amp;"), strict=True):
        print(f"{byte:>3} ({chr(byte)!r}): {phrase}")


if __name__ == "__main__":
    main()
