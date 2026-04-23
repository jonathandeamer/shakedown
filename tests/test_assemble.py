"""Tests for the src/ → shakedown.spl assembler."""

from pathlib import Path

import pytest


def test_assemble_orders_fragments_per_manifest(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.spl").write_text("fragment-a\n")
    (src / "b.spl").write_text("fragment-b\n")
    (src / "manifest.toml").write_text('fragments = ["b.spl", "a.spl"]\n')

    output = tmp_path / "out.spl"
    assemble(src_dir=src, manifest=src / "manifest.toml", output=output)

    assert output.read_text() == "fragment-b\nfragment-a\n"


def test_assemble_resolves_scene_labels_to_roman_within_acts(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "act1.spl").write_text(
        "Act I: The first act.\nScene @READ: Reading input.\nScene @DONE: Finished.\n"
    )
    (src / "act2.spl").write_text(
        "Act II: The second act.\n"
        "Scene @START: Entry point.\n"
        "Let us proceed to scene @START.\n"
    )
    (src / "manifest.toml").write_text('fragments = ["act1.spl", "act2.spl"]\n')

    output = tmp_path / "out.spl"
    assemble(src_dir=src, manifest=src / "manifest.toml", output=output)

    result = output.read_text()
    assert "Scene I: Reading input." in result
    assert "Scene II: Finished." in result
    assert "Scene I: Entry point." in result
    assert "Let us proceed to scene I." in result
    assert "@READ" not in result
    assert "@DONE" not in result
    assert "@START" not in result


def test_assemble_scene_label_collision_within_act_raises(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "act1.spl").write_text(
        "Act I: Duplicate label act.\nScene @FOO: First.\nScene @FOO: Second.\n"
    )
    (src / "manifest.toml").write_text('fragments = ["act1.spl"]\n')

    output = tmp_path / "out.spl"
    with pytest.raises(ValueError, match="@FOO"):
        assemble(src_dir=src, manifest=src / "manifest.toml", output=output)
