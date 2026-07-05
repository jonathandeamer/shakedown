"""Generated fragments must match a fresh render — the src_ir/ modules are
the authored source of truth; editing the .spl fragment by hand is a defect
this test catches (same contract shape as the committed shakedown.spl)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).parent.parent


def test_committed_fragments_match_render() -> None:
    from scripts.splc.__main__ import rendered_fragments

    for name, text in rendered_fragments().items():
        committed = (REPO / "src" / name).read_text()
        assert committed == text, (
            f"src/{name} drifted from src_ir render; regenerate with "
            "`uv run python -m scripts.splc`"
        )


def test_committed_debug_fragments_match_render() -> None:
    from scripts.splc.__main__ import rendered_debug_fragments

    for rel, text in rendered_debug_fragments().items():
        committed = (REPO / rel).read_text()
        assert committed == text, (
            f"{rel} drifted from src_ir render; regenerate with "
            "`uv run python -m scripts.splc`"
        )
