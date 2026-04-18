"""Assemble src/*.spl fragments into shakedown.spl per manifest."""

from __future__ import annotations

import tomllib
from pathlib import Path


def assemble(src_dir: Path, manifest: Path, output: Path) -> None:
    """Concatenate fragments listed in manifest into output, in order."""
    with manifest.open("rb") as f:
        config = tomllib.load(f)

    fragments: list[str] = config["fragments"]

    parts: list[str] = []
    for name in fragments:
        parts.append((src_dir / name).read_text())

    output.write_text("".join(parts))


def main() -> None:
    root = Path(__file__).parent.parent
    assemble(
        src_dir=root / "src",
        manifest=root / "src" / "manifest.toml",
        output=root / "shakedown.spl",
    )


if __name__ == "__main__":
    main()
