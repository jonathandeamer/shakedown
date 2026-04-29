"""Slice 1 gate: Amps and angle encoding must be SPL-owned and byte-identical."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
SHAKEDOWN = REPO / "shakedown"
HARNESS = REPO / "scripts" / "strict_parity_harness.py"
ASSEMBLED = REPO / "shakedown.spl"
SRC = REPO / "src"


def test_shakedown_entrypoint_no_longer_delegates_to_markdown_pl() -> None:
    text = SHAKEDOWN.read_text()
    forbidden = ("Markdown.pl", "markdown/Markdown.pl", "exec perl", "ORACLE=")
    assert not any(term in text for term in forbidden), text


def test_release_artifact_is_committed() -> None:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(ASSEMBLED.relative_to(REPO))],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_amps_and_angle_encoding_strict_parity() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "Amps and angle encoding",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "summary: 1/1 byte-identical" in result.stdout


def test_slice1_avoids_known_fixture_specific_scene_shapes() -> None:
    source = "\n".join(
        path.read_text()
        for path in (
            SRC / "10-act1-preprocess.spl",
            SRC / "30-act3-span.spl",
        )
    )
    forbidden_labels = {
        "@HECATE_CUT_REFERENCE_TAIL",
        "@LYRIC_INLINE_POP_DIRECT_DESTINATION",
        "@LYRIC_INLINE_POP_BRACKETED_DESTINATION",
        "@LYRIC_OUTPUT_REFERENCE_ONE",
        "@LYRIC_OUTPUT_REFERENCE_TWO",
        "@LYRIC_OUTPUT_INLINE_LINK",
    }
    present = sorted(label for label in forbidden_labels if label in source)
    assert not present, f"fixture-specific scene labels remain: {present}"


def test_slice1_avoids_known_fixed_length_glyph_consumption() -> None:
    source = "\n".join(
        path.read_text()
        for path in (
            SRC / "10-act1-preprocess.spl",
            SRC / "30-act3-span.spl",
        )
    )
    forbidden_fragments = (
        "Recall the bargain glyph 65",
        "Recall the inline path glyph 19",
        "Recall the bracketed path glyph 21",
    )
    present = [fragment for fragment in forbidden_fragments if fragment in source]
    assert not present, f"fixed-length fixture consumption remains: {present}"
