"""Tests for the src/ → shakedown.spl assembler."""

from pathlib import Path

import pytest  # noqa: F401  # used in Task 5 pytest.raises tests


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
