"""Render registered IR acts to their generated fragment files.

Usage: uv run python -m scripts.splc
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.literary_surfaces import load_literary_surfaces  # noqa: E402
from scripts.splc.lower import lower_act  # noqa: E402
from scripts.splc.prose import ProseEngine  # noqa: E402


def rendered_fragments() -> dict[str, str]:
    """Fragment filename -> rendered text, for every IR-owned act."""
    from src_ir.act1 import ACT as ACT1

    prose = ProseEngine(load_literary_surfaces(_ROOT / "src" / "literary.toml"))
    return {
        "10-act1-preprocess.spl": lower_act(
            ACT1, prose, next_act_heading="Act II: @LIT.acts.act2.title"
        ),
    }


def main() -> None:
    src = _ROOT / "src"
    for name, text in rendered_fragments().items():
        (src / name).write_text(text)
        print(src / name)


if __name__ == "__main__":
    main()
