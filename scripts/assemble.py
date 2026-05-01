"""Assemble src/*.spl fragments into shakedown.spl per manifest."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from scripts.literary_surfaces import load_literary_surfaces

_ROMAN_ONES = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
_ROMAN_TENS = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
_ROMAN_HUNDREDS = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]


def _int_to_roman(n: int) -> str:
    if n < 1 or n >= 1000:
        raise ValueError(f"scene number out of range: {n}")
    return _ROMAN_HUNDREDS[n // 100] + _ROMAN_TENS[(n // 10) % 10] + _ROMAN_ONES[n % 10]


_ACT_RE = re.compile(r"^\s*Act\s+[IVXLCDM]+\s*:", re.MULTILINE)
_SCENE_DECL_RE = re.compile(r"Scene\s+@([A-Z_][A-Z0-9_]*)\s*:")
_SCENE_REF_RE = re.compile(r"scene\s+@([A-Z_][A-Z0-9_]*)")
_LIT_RE = re.compile(r"@LIT\.([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*)")


def _resolve_literary_placeholders(source: str, literary_path: Path) -> str:
    if "@LIT." not in source:
        return source
    surfaces = load_literary_surfaces(literary_path)

    def replace(match: re.Match[str]) -> str:
        return surfaces.resolve(match.group(1))

    resolved = _LIT_RE.sub(replace, source)
    if "@LIT." in resolved:
        raise ValueError("unresolved @LIT placeholder")
    return resolved


def _resolve_scene_labels(source: str) -> str:
    """Replace `@LABEL` scene references with Roman numerals, act-local."""
    act_positions = [m.start() for m in _ACT_RE.finditer(source)]
    if not act_positions:
        return _resolve_in_segment(source)

    segments: list[str] = []
    segments.append(source[: act_positions[0]])
    for idx, start in enumerate(act_positions):
        end = act_positions[idx + 1] if idx + 1 < len(act_positions) else len(source)
        segments.append(_resolve_in_segment(source[start:end]))

    return "".join(segments)


def _resolve_in_segment(segment: str) -> str:
    """Resolve labels for a single act segment: declarations get I, II, III, ..."""
    label_to_roman: dict[str, str] = {}
    counter = 0

    def assign(match: re.Match[str]) -> str:
        nonlocal counter
        label = match.group(1)
        if label in label_to_roman:
            raise ValueError(f"duplicate scene label @{label} in act")
        counter += 1
        label_to_roman[label] = _int_to_roman(counter)
        return f"Scene {label_to_roman[label]}:"

    with_decls_resolved = _SCENE_DECL_RE.sub(assign, segment)

    def lookup(match: re.Match[str]) -> str:
        label = match.group(1)
        if label not in label_to_roman:
            raise ValueError(f"unresolved scene reference @{label}")
        return f"scene {label_to_roman[label]}"

    return _SCENE_REF_RE.sub(lookup, with_decls_resolved)


def assemble(src_dir: Path, manifest: Path, output: Path) -> None:
    """Concatenate fragments per manifest and resolve scene labels."""
    with manifest.open("rb") as f:
        config = tomllib.load(f)

    fragments: list[str] = config["fragments"]
    combined = "".join((src_dir / name).read_text() for name in fragments)
    with_literary = _resolve_literary_placeholders(
        combined,
        src_dir / "literary.toml",
    )
    resolved = _resolve_scene_labels(with_literary)
    output.write_text(resolved)


def main() -> None:
    root = Path(__file__).parent.parent
    assemble(
        src_dir=root / "src",
        manifest=root / "src" / "manifest.toml",
        output=root / "shakedown.spl",
    )


if __name__ == "__main__":
    main()
