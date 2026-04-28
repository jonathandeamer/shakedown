"""Dev wrapper for the SPL Markdown port."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
DEV_ASSEMBLED = REPO / ".cache" / "shakedown-dev.spl"
RELEASE_ASSEMBLED = REPO / "shakedown.spl"
SPIKE_DOC = REPO / "docs" / "architecture" / "cache-spike.md"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _assemble() -> Path:
    from scripts.assemble import assemble

    DEV_ASSEMBLED.parent.mkdir(exist_ok=True)
    assemble(
        src_dir=REPO / "src",
        manifest=REPO / "src" / "manifest.toml",
        output=DEV_ASSEMBLED,
    )
    return DEV_ASSEMBLED


def _read_mode() -> str:
    if not SPIKE_DOC.exists():
        return "direct"
    text = SPIKE_DOC.read_text()
    match = re.search(r'"decision":\s*"([^"]+)"', text)
    if not match:
        return "direct"
    return "cached" if match.group(1) == "cache_proven" else "direct"


def _run(spl_path: Path) -> int:
    proc = subprocess.run(
        ["uv", "run", "shakespeare", "run", str(spl_path)],
        stdin=sys.stdin.buffer,
        stdout=sys.stdout.buffer,
        stderr=sys.stderr.buffer,
        check=False,
    )
    return proc.returncode


def main(argv: list[str]) -> int:
    if "--print-assembled-path" in argv:
        print(_assemble())
        return 0
    if "--print-mode" in argv:
        print(_read_mode())
        return 0
    spl_path = _assemble()
    return _run(spl_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
