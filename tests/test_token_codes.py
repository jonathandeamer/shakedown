"""Validate the dispatch token-code allocation table satisfies the atom cap."""

from __future__ import annotations

import re
from pathlib import Path

TOKEN_CODES_DOC = Path(__file__).parent.parent / "docs" / "spl" / "token-codes.md"

_ROW_RE = re.compile(
    r"^\|\s*(?P<name>[A-Z_]+)\s*\|\s*(?P<code>\d+)\s*\|\s*`(?P<phrase>[^`]+)`\s*\|"
)

REQUIRED_TOKENS = {
    "PARA",
    "HEADER",
    "HR",
    "LIST_OPEN",
    "LIST_ITEM",
    "LIST_CLOSE",
    "BLOCKQUOTE_OPEN",
    "BLOCKQUOTE_CLOSE",
    "CODE_BLOCK",
    "RAW_HTML_HASH",
}

ATOM_WORD_MAX = 6


def parse_table() -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for line in TOKEN_CODES_DOC.read_text().splitlines():
        match = _ROW_RE.match(line)
        if match:
            rows.append((match["name"], int(match["code"]), match["phrase"]))
    return rows


def test_doc_exists() -> None:
    assert TOKEN_CODES_DOC.exists(), TOKEN_CODES_DOC


def test_all_required_tokens_present() -> None:
    names = {row[0] for row in parse_table()}
    missing = REQUIRED_TOKENS - names
    assert not missing, f"missing token names: {sorted(missing)}"


def test_codes_are_unique_positive_integers() -> None:
    codes = [row[1] for row in parse_table()]
    assert all(c > 0 for c in codes), codes
    assert len(codes) == len(set(codes)), f"duplicate codes: {codes}"


def test_atom_word_cap() -> None:
    """Each phrase atom must be <= 6 words."""
    for name, code, phrase in parse_table():
        atoms = _atoms_in(phrase)
        for atom in atoms:
            words = atom.strip().split()
            assert len(words) <= ATOM_WORD_MAX, (
                f"{name}={code} atom {atom!r} exceeds {ATOM_WORD_MAX}-word cap"
            )


def _atoms_in(phrase: str) -> list[str]:
    """Decompose right-nested `the sum of A and B` compounds."""
    text = phrase.strip()
    prefix = "the sum of "
    if text.lower().startswith(prefix):
        rest = text[len(prefix) :]
        idx = rest.find(" and ")
        if idx == -1:
            return [text]
        left, right = rest[:idx], rest[idx + len(" and ") :]
        return _atoms_in(left) + _atoms_in(right)
    return [text]
