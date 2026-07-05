#!/usr/bin/env python3
"""Query tool to retrieve specific sections/paragraphs from docs/ to save tokens."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Search documentation paragraphs for matches to reduce context size."
        )
    )
    parser.add_argument("query", help="Term to search for (case-insensitive)")
    parser.add_argument(
        "--file-glob",
        default="*.md",
        help="Glob pattern for markdown files to search under docs/",
    )
    args = parser.parse_args()

    query_lower = args.query.lower()
    matches: list[tuple[Path, int, str]] = []

    # Walk docs directory, ignoring archive/
    for path in sorted(DOCS_DIR.rglob(args.file_glob)):
        if "archive" in path.parts:
            continue
        if not path.is_file():
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Split into paragraphs by double newline
        paragraphs = content.split("\n\n")
        for idx, para in enumerate(paragraphs, 1):
            if query_lower in para.lower():
                matches.append((path, idx, para.strip()))

    if not matches:
        print(
            f"No matches found for {args.query!r} under {args.file_glob} "
            "(excluding archive/)."
        )
        return 1

    print(f"Found {len(matches)} matching paragraph(s):\n")
    for path, para_idx, para in matches:
        rel_path = path.relative_to(REPO_ROOT)
        print(f"--- File: {rel_path} (Paragraph {para_idx}) ---")
        print(para)
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
