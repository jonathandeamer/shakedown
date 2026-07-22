"""HTML byte-literal codegen."""

from __future__ import annotations

from pathlib import Path

from scripts.literary_surfaces import load_literary_surfaces

_ROOT = Path(__file__).parent.parent
_LITERARY_TOML = _ROOT / "src" / "literary.toml"
_SURFACES = load_literary_surfaces(_LITERARY_TOML)
_ATOMS_BY_FAMILY: dict[str, dict[int, str]] = {}


def _atoms_for(family: str) -> dict[int, str]:
    """Return the value-atom table for a family, loading it once."""
    if family not in _ATOMS_BY_FAMILY:
        _ATOMS_BY_FAMILY[family] = _SURFACES.value_atoms(family)
    return _ATOMS_BY_FAMILY[family]


_ATOM_BY_VALUE = _atoms_for("default")


def _all_atom_to_value() -> dict[str, int]:
    merged: dict[str, int] = {}
    raw_families = _SURFACES.data.get("value_atoms")
    if isinstance(raw_families, dict):
        for family in sorted(raw_families):
            for value, phrase in _atoms_for(family).items():
                merged.setdefault(phrase, value)
    return merged


_ATOM_TO_VALUE = _all_atom_to_value()

# Arithmetic operator phrases and their limits (per literary compliance)
ARITHMETIC_OPERATORS = (
    "the sum of",
    "the product of",
    "the square of",
    "the difference between",
)
MAX_ARITHMETIC_OPERATORS_PER_STATEMENT = 4


def emit_value(value: int, family: str = "default") -> str:
    """Return the canonical SPL value phrase for a non-negative integer."""
    if value < 0 or value > 1024:
        raise ValueError(f"value out of supported range: {value}")
    atoms = _atoms_for(family)
    if value in atoms:
        return atoms[value]
    return _decompose(value, family)


def emit_byte(value: int, family: str = "default") -> str:
    """Return the canonical SPL value phrase for an integer byte."""
    if value < 0 or value > 255:
        raise ValueError(f"byte value out of range: {value}")
    return emit_value(value, family)


def _decompose(value: int, family: str = "default") -> str:
    """Return an SPL value phrase with <= 4 arithmetic operators."""
    # Try multiple decomposition strategies and pick the best
    candidates = []

    # Strategy 1: Original greedy with products for multiples
    candidates.append(_decompose_greedy_products(value, family))

    # Strategy 2: Difference from next multiple of 16/32/64/128/256
    for base in [16, 32, 64, 128, 256]:
        multiple = ((value // base) + 1) * base
        diff = multiple - value
        if 0 < diff < base:
            candidates.append(_decompose_difference(multiple, diff, family))

    # Strategy 3: Difference from square
    if value > 256:
        root = int(value**0.5)
        if root > 16:
            square = root * root
            if square > value:
                diff = square - value
                candidates.append(_decompose_difference(square, diff, family))

    # Strategy 4: Pure sum of atoms (no products/squares)
    candidates.append(_decompose_pure_sum(value, family))

    # Pick candidate with fewest operators (must be <= 4)
    best = None
    best_ops = 999
    for cand in candidates:
        ops = sum(cand.count(op) for op in ARITHMETIC_OPERATORS)
        if ops <= MAX_ARITHMETIC_OPERATORS_PER_STATEMENT and ops < best_ops:
            best = cand
            best_ops = ops

    if best is None:
        # Fallback: return the greedy one even if over budget
        return _decompose_greedy_products(value, family)
    return best


def _decompose_greedy_products(value: int, family: str = "default") -> str:
    """Original greedy algorithm with products for multiples."""
    atoms = _atoms_for(family)
    terms: list[str] = []
    if value >= 256:
        count = value // 256
        terms.extend([f"the square of {atoms[16]}"] * count)
        value %= 256

    for atom_value in sorted([v for v in atoms if v >= 16], reverse=True):
        if atom_value == 0:
            continue
        if atom_value <= value:
            count = value // atom_value
            if count == 1:
                terms.append(atoms[atom_value])
            else:
                terms.append(
                    f"the product of {atoms[atom_value]} and "
                    f"{emit_value_simple(count, family)}"
                )
            value -= atom_value * count

    for atom_value in sorted([v for v in atoms if 0 < v < 16], reverse=True):
        if atom_value <= value:
            terms.append(atoms[atom_value])
            value -= atom_value

    return _sum_terms(terms, family)


def emit_value_simple(value: int, family: str = "default") -> str:
    """Simple emit_value without recursive decomposition (for multipliers)."""
    atoms = _atoms_for(family)
    if value in atoms:
        return atoms[value]
    # For small multipliers, use greedy with products for multiples of 16
    terms: list[str] = []
    if value >= 16:
        for atom_value in sorted([v for v in atoms if v >= 16], reverse=True):
            if atom_value == 0:
                continue
            if atom_value <= value:
                count = value // atom_value
                if count == 1:
                    terms.append(atoms[atom_value])
                else:
                    terms.append(
                        f"the product of {atoms[atom_value]} and "
                        f"{emit_value_simple(count, family)}"
                    )
                value -= atom_value * count

    for atom_value in sorted([v for v in atoms if 0 < v < 16], reverse=True):
        while atom_value <= value:
            terms.append(atoms[atom_value])
            value -= atom_value

    return _sum_terms(terms, family)


def _decompose_pure_sum(value: int, family: str = "default") -> str:
    """Greedy sum of atoms only (no products/squares)."""
    atoms = _atoms_for(family)
    terms: list[str] = []
    for atom_value in sorted([v for v in atoms if v > 0], reverse=True):
        while atom_value <= value:
            terms.append(atoms[atom_value])
            value -= atom_value
    return _sum_terms(terms, family)


def _decompose_difference(multiple: int, diff: int, family: str = "default") -> str:
    """Express value as difference between multiple and diff."""
    multiple_phrase = emit_value_simple(multiple, family)
    diff_phrase = emit_value_simple(diff, family)
    return f"the difference between {multiple_phrase} and {diff_phrase}"


def _sum_terms(terms: list[str], family: str = "default") -> str:
    if not terms:
        return _atoms_for(family)[0]
    phrase = terms[-1]
    for term in reversed(terms[:-1]):
        phrase = f"the sum of {term} and {phrase}"
    return phrase


def emit_literal(literal: bytes, family: str = "default") -> list[str]:
    """Return one SPL phrase per byte in a literal."""
    return [emit_byte(b, family) for b in literal]


def emit_speak_lines(
    literal: bytes, speaker: str, family: str = "default"
) -> list[str]:
    """Return SPL assignment/output lines for a byte literal.

    The speaker assigns each byte value to the listener, then speaks the
    listener's character value with `Speak your mind!`.
    """
    lines: list[str] = []
    for phrase in emit_literal(literal, family):
        lines.append(f"{speaker}: You are as good as {phrase}.")
        lines.append(f"{speaker}: Speak your mind!")
    return lines


class _ValueParser:
    """Recursive descent parser for SPL value phrases."""

    def __init__(self, text: str):
        self.text = text.lower()
        self.pos = 0
        self.original = text  # Keep original for error messages

    def parse(self) -> int:
        val = self._parse_value()
        self._skip_whitespace()
        if self.pos != len(self.text):
            raise ValueError(f"trailing text: {self.original[self.pos :]}")
        return val

    def _parse_value(self) -> int:
        self._skip_whitespace()

        # Check for operators
        if self._match("the square of "):
            val = self._parse_value()
            return val * val

        if self._match("the product of "):
            left = self._parse_value()
            self._expect(" and ")
            right = self._parse_value()
            return left * right

        if self._match("the sum of "):
            left = self._parse_value()
            self._expect(" and ")
            right = self._parse_value()
            return left + right

        if self._match("the difference between "):
            left = self._parse_value()
            self._expect(" and ")
            right = self._parse_value()
            return left - right

        # Must be an atom
        return self._parse_atom()

    def _parse_atom(self) -> int:
        self._skip_whitespace()
        start = self.pos

        # Scan until next operator, ' and ', or end
        while self.pos < len(self.text):
            if self.text[self.pos :].startswith(" and "):
                break
            if any(
                self.text[self.pos :].startswith(op)
                for op in [
                    "the square of ",
                    "the product of ",
                    "the sum of ",
                    "the difference between ",
                ]
            ):
                break
            self.pos += 1

        atom_text = self.original[start : self.pos].strip()
        if atom_text in _ATOM_TO_VALUE:
            return _ATOM_TO_VALUE[atom_text]
        raise ValueError(f"unknown atom: {atom_text}")

    def _match(self, keyword: str) -> bool:
        self._skip_whitespace()
        if self.text[self.pos :].startswith(keyword):
            self.pos += len(keyword)
            return True
        return False

    def _expect(self, keyword: str):
        # Keywords like ' and ' include their own surrounding spaces
        if self.text[self.pos :].startswith(keyword):
            self.pos += len(keyword)
        else:
            # Try after skipping whitespace
            self._skip_whitespace()
            if self.text[self.pos :].startswith(keyword):
                self.pos += len(keyword)
            else:
                raise ValueError(f"expected '{keyword}' at pos {self.pos}")

    def _skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1


def parse_value_phrase(phrase: str) -> int:
    return _ValueParser(phrase).parse()
