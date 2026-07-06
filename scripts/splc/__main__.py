"""Render registered IR acts to their generated fragment files.

Usage: uv run python -m scripts.splc
"""

from __future__ import annotations

import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import cast

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.literary_surfaces import (  # noqa: E402
    LiterarySurfaces,
    load_literary_surfaces,
)
from scripts.splc.lower import lower_act  # noqa: E402
from scripts.splc.prose import ProseEngine  # noqa: E402

_LIT_RE = re.compile(r"@LIT\.([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*)")


def _surfaces() -> LiterarySurfaces:
    return load_literary_surfaces(_ROOT / "src" / "literary.toml")


def rendered_fragments() -> dict[str, str]:
    """Fragment filename -> rendered text, for every IR-owned act."""
    from src_ir.act1 import ACT as ACT1
    from src_ir.act2 import ACT as ACT2
    from src_ir.act3 import ACT as ACT3
    from src_ir.act4 import ACT as ACT4

    prose = ProseEngine(_surfaces())
    return {
        "10-act1-preprocess.spl": lower_act(
            ACT1, prose, next_act_heading="Act II: @LIT.acts.act2.title"
        ),
        "20-act2-block.spl": lower_act(
            ACT2, prose, next_act_heading="Act III: @LIT.acts.act3.title"
        ),
        "30-act3-span.spl": lower_act(
            ACT3, prose, next_act_heading="Act IV: @LIT.acts.act4.title"
        ),
        # Act IV is the final act — no next-act heading; Act III's fragment
        # emits the "Act IV:" heading at its tail.
        "40-act4-emit.spl": lower_act(ACT4, prose),
    }


def _debug_fragment_text() -> str:
    """The `./shakedown-debug` Act IV shadow, fully inlined.

    The debug play's DBG_* scene titles are deliberately kept out of the
    globbed production ledger (see src_ir/debug_act4.SCENE_TITLES). We inject
    them into a throwaway copy of the surfaces so lowering can validate and
    resolve, then inline every @LIT placeholder so the committed fragment is
    self-contained and assembly needs no DBG_* ledger entries."""
    from src_ir.debug_act4 import ACT as DEBUG_ACT
    from src_ir.debug_act4 import SCENE_TITLES

    data = deepcopy(_surfaces().data)
    scenes = cast(dict[str, object], data.setdefault("scenes", {}))
    for label, title in SCENE_TITLES.items():
        scenes[label] = {"title": title, "pattern": "bare_statement"}
    surfaces = LiterarySurfaces(data)

    text = lower_act(DEBUG_ACT, ProseEngine(surfaces))
    resolved = _LIT_RE.sub(lambda m: surfaces.resolve(m.group(1)), text)
    if "@LIT." in resolved:
        raise ValueError("unresolved @LIT placeholder in debug fragment")
    return resolved


def rendered_debug_fragments() -> dict[str, str]:
    """Repo-relative debug fragment path -> rendered text."""
    return {"debug/40-act4-token-dump.spl": _debug_fragment_text()}


def main() -> None:
    for name, text in rendered_fragments().items():
        (_ROOT / "src" / name).write_text(text)
        print(_ROOT / "src" / name)
    for rel, text in rendered_debug_fragments().items():
        (_ROOT / rel).write_text(text)
        print(_ROOT / rel)


if __name__ == "__main__":
    main()
