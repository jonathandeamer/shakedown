"""Count Markdown reference definitions in the largest mdtest fixture.

Markdown reference definitions match this regex pattern (lifted from
Markdown.pl _StripLinkDefinitions): a line starting with up to three spaces,
followed by `[id]:`, followed by URL and optional title.
"""

from __future__ import annotations

import re
from pathlib import Path

FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Markdown Documentation - Syntax.text"
)

DEF_LINE = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*\S", re.MULTILINE)


def count_definitions(text: str) -> list[str]:
    return [m.group(1) for m in DEF_LINE.finditer(text)]


def main() -> None:
    text = FIXTURE.read_text()
    ids = count_definitions(text)
    print(f"Fixture: {FIXTURE}")
    print(f"Reference definition count: {len(ids)}")
    for identifier in ids:
        print(f"  - {identifier}")


if __name__ == "__main__":
    main()
