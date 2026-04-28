"""HTML byte-literal codegen."""

from __future__ import annotations

import re

_ATOM_BY_VALUE: dict[int, str] = {
    0: "nothing",
    1: "a cat",
    2: "a big cat",
    4: "a big big cat",
    8: "a big big big cat",
    16: "a big big big big cat",
}


def emit_byte(value: int) -> str:
    """Return the canonical SPL value phrase for an integer byte."""
    if value < 0 or value > 255:
        raise ValueError(f"byte value out of range: {value}")
    if value in _ATOM_BY_VALUE:
        return _ATOM_BY_VALUE[value]
    return _decompose(value)


def _decompose(value: int) -> str:
    """Pick the largest atom <= value, then recurse on the remainder."""
    for atom_value in sorted(_ATOM_BY_VALUE, reverse=True):
        if atom_value == 0:
            continue
        if atom_value <= value:
            remainder = value - atom_value
            left = _ATOM_BY_VALUE[atom_value]
            if remainder == 0:
                return left
            right = emit_byte(remainder)
            return f"the sum of {left} and {right}"
    return _ATOM_BY_VALUE[0]


def emit_literal(literal: bytes) -> list[str]:
    """Return one SPL phrase per byte in a literal."""
    return [emit_byte(b) for b in literal]


_PHRASE_RE = re.compile(r"^a(?: big)*(?: cat)$")


def parse_value_phrase(phrase: str) -> int:
    """Reverse `emit_byte`; used by round-trip tests."""
    text = phrase.strip()
    if text == "nothing":
        return 0
    prefix = "the sum of "
    if text.lower().startswith(prefix):
        rest = text[len(prefix) :]
        idx = rest.find(" and ")
        if idx == -1:
            raise ValueError(f"malformed compound: {phrase!r}")
        return parse_value_phrase(rest[:idx]) + parse_value_phrase(
            rest[idx + len(" and ") :]
        )
    if not _PHRASE_RE.match(text):
        raise ValueError(f"unrecognised atom: {phrase!r}")
    tokens = text.split()
    bigs = tokens[1:-1].count("big")
    return 1 << bigs


def main() -> None:
    """CLI smoke test: emit phrases for `&amp;`."""
    for byte, phrase in zip(b"&amp;", emit_literal(b"&amp;"), strict=True):
        print(f"{byte:>3} ({chr(byte)!r}): {phrase}")


if __name__ == "__main__":
    main()
