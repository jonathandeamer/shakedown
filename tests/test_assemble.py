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


def test_assemble_resolves_literary_placeholders(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "fragment.spl").write_text(
        "@LIT.play.title\n"
        "Act I: @LIT.acts.act1.title\n"
        "Scene @START: @LIT.scenes.START.title\n"
    )
    (src / "manifest.toml").write_text('fragments = ["fragment.spl"]\n')
    (src / "literary.toml").write_text(
        """
[play]
title = "Shakedown."

[acts.act1]
title = "Wherein the first act begins."

[scenes.START]
title = "The page awakens."
"""
    )

    output = tmp_path / "out.spl"
    assemble(src_dir=src, manifest=src / "manifest.toml", output=output)

    assert output.read_text() == (
        "Shakedown.\nAct I: Wherein the first act begins.\nScene I: The page awakens.\n"
    )


def test_assemble_unknown_literary_placeholder_raises(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "fragment.spl").write_text("@LIT.play.subtitle\n")
    (src / "manifest.toml").write_text('fragments = ["fragment.spl"]\n')
    (src / "literary.toml").write_text('[play]\ntitle = "Shakedown."\n')

    output = tmp_path / "out.spl"
    with pytest.raises(KeyError, match="play.subtitle"):
        assemble(src_dir=src, manifest=src / "manifest.toml", output=output)


MINIMAL_VALID_PLAY = """\
A quiet probe.

Romeo, a probe.
Juliet, a probe.

                    Act I: The probe.

                    Scene I: The probe.

[Enter Romeo and Juliet]

Romeo:
 You are as fair as nothing.

[Exeunt]
"""


def test_assemble_parse_check_rejects_unparseable_output(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.spl").write_text("this is not a play\n")
    (src / "manifest.toml").write_text('fragments = ["a.spl"]\n')

    with pytest.raises(ValueError, match="does not parse"):
        assemble(
            src_dir=src,
            manifest=src / "manifest.toml",
            output=tmp_path / "out.spl",
            parse_check=True,
        )


def test_assemble_parse_check_accepts_valid_play(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "play.spl").write_text(MINIMAL_VALID_PLAY)
    (src / "manifest.toml").write_text('fragments = ["play.spl"]\n')

    output = tmp_path / "out.spl"
    assemble(
        src_dir=src,
        manifest=src / "manifest.toml",
        output=output,
        parse_check=True,
    )
    assert output.read_text() == MINIMAL_VALID_PLAY


def test_assemble_replace_substitutes_fragment(tmp_path: Path) -> None:
    from scripts.assemble import assemble

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.spl").write_text("original\n")
    (src / "manifest.toml").write_text('fragments = ["a.spl"]\n')
    substitute = tmp_path / "substitute.spl"
    substitute.write_text("substituted\n")

    output = tmp_path / "out.spl"
    assemble(
        src_dir=src,
        manifest=src / "manifest.toml",
        output=output,
        replace={"a.spl": substitute},
    )
    assert output.read_text() == "substituted\n"
