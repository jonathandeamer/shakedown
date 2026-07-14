from __future__ import annotations

import sys

from scripts.slice3_links import rewrite_task3_markdown


def main() -> int:
    sys.stdout.write(rewrite_task3_markdown(sys.stdin.read()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
