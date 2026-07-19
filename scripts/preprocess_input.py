"""Deprecated passthrough.

Previously applied ``rewrite_task3_markdown`` before the IR/SPL path. Act I
and Act III now own strip and link/image resolution; this module no longer
transforms Markdown. Prefer piping stdin directly into ``./shakedown`` or
``python -m scripts.release_runtime``.
"""

from __future__ import annotations

import sys
import warnings


def main() -> int:
    warnings.warn(
        "scripts.preprocess_input is deprecated: Markdown rewrite was retired; "
        "stdin is written unchanged. Pipe input to ./shakedown or "
        "python -m scripts.release_runtime instead.",
        DeprecationWarning,
        stacklevel=1,
    )
    sys.stderr.write(
        "warning: scripts.preprocess_input is deprecated; writing stdin unchanged\n"
    )
    sys.stdout.write(sys.stdin.read())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
