"""Lowering: IR -> fragment-shaped SPL with computed choreography."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.literary_surfaces import load_literary_surfaces
from scripts.splc.ir import (
    Char,
    act,
    add,
    branch,
    const,
    eq,
    goto,
    halt_act,
    let,
    print_char,
    scene,
    val,
)

REPO = Path(__file__).parent.parent
LITERARY_TOML = REPO / "src" / "literary.toml"

# A self-contained literary TOML for golden tests, so mini-programs are not
# coupled to production scene labels.
GOLDEN_TOML = """\
[scenes.GOLD_START]
title = "The probe begins."

[scenes.GOLD_DONE]
title = "The probe ends."

[value_atoms.default]
v0 = "nothing"
v1 = "a cat"
v2 = "a black cat"
v4 = "a furry black cat"
v8 = "a little furry black cat"
v16 = "a normal little furry black cat"

[characters.hecate.stable_utility]
v0 = "nothing"
v1 = "a cat"
v2 = "a black cat"
vneg1 = "a toad"

[characters.hecate.soft_variation]
equality = ["as rotten as"]
greater_than = ["bigger than"]
less_than = ["punier than"]
goto_forward = ["Let us proceed to"]
goto_backward = ["We must return to"]

[characters.hecate.recall]
cauldron_dreg = "Recall the cauldron dreg."

[characters.puck.stable_utility]
v0 = "nothing"
v1 = "a cat"

[characters.puck.soft_variation]
equality = ["as swift as"]
greater_than = ["quicker than"]
less_than = ["slower than"]
goto_forward = ["Let us proceed to"]
goto_backward = ["Let us return to"]
"""


def _golden_engine(tmp_path: Path):  # noqa: ANN202
    from scripts.splc.prose import ProseEngine

    toml_path = tmp_path / "literary.toml"
    toml_path.write_text(GOLDEN_TOML)
    return ProseEngine(load_literary_surfaces(toml_path))


def _mini_act():  # noqa: ANN202
    # Prints "H\n" and halts: exercises let, print, branch, goto, halt.
    return act(
        1,
        Char.HECATE,
        [
            scene(
                "GOLD_START",
                let(Char.PUCK, const(72)),
                print_char(Char.PUCK),
                let(Char.PUCK, const(10)),
                print_char(Char.PUCK),
                branch(eq(val(Char.PUCK), const(10)), then="GOLD_DONE"),
                goto("GOLD_DONE"),
            ),
            scene("GOLD_DONE", halt_act(), companion=Char.PUCK),
        ],
    )


def test_lowered_fragment_has_headings_choreography_and_speech(
    tmp_path: Path,
) -> None:
    from scripts.splc.lower import lower_act

    text = lower_act(_mini_act(), _golden_engine(tmp_path))
    assert "Scene @GOLD_START: @LIT.scenes.GOLD_START.title" in text
    assert "[Enter Hecate and Puck]" in text
    assert "Speak your mind!" in text
    assert "Are you as swift as" not in text  # Puck is the tested addressee...
    # ...wait: tested char is Puck, so the SPEAKER is Hecate. Comparator
    # pools belong to the speaker:
    assert "Are you as rotten as" in text
    assert "If so, Let us proceed to scene @GOLD_DONE.".lower() in text.lower()
    assert text.rstrip().endswith("[Exeunt]")


def test_val_renders_yourself_and_myself(tmp_path: Path) -> None:
    from scripts.splc.lower import lower_act

    a = act(
        1,
        Char.HECATE,
        [
            scene(
                "GOLD_START",
                # target is Puck, expr references Puck -> "yourself"
                let(Char.PUCK, add(val(Char.PUCK), const(1))),
                # target is anchor Hecate, so Puck speaks; expr references
                # Puck -> "myself"
                let(Char.HECATE, val(Char.PUCK)),
                goto("GOLD_DONE"),
            ),
            scene("GOLD_DONE", halt_act(), companion=Char.PUCK),
        ],
    )
    text = lower_act(a, _golden_engine(tmp_path))
    assert "the sum of yourself and a cat" in text
    assert "as rotten as myself" not in text  # Puck speaks with his own pool
    assert "as swift as myself" in text


def test_next_act_heading_appended(tmp_path: Path) -> None:
    from scripts.splc.lower import lower_act

    text = lower_act(
        _mini_act(),
        _golden_engine(tmp_path),
        next_act_heading="Act II: @LIT.acts.act2.title",
    )
    assert text.rstrip().endswith("Act II: @LIT.acts.act2.title")


def test_golden_mini_play_parses_and_runs(tmp_path: Path) -> None:
    """End-to-end: lowered SPL assembles into a play that prints H\\n."""
    from scripts.assemble import assemble
    from scripts.splc.lower import lower_act

    fragment = lower_act(_mini_act(), _golden_engine(tmp_path))
    preamble = (
        "The golden probe.\n"
        "\n"
        "Hecate, a witch.\n"
        "Puck, a messenger.\n"
        "\n"
        "                    Act I: The probe act.\n"
        "\n"
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "play.spl").write_text(preamble + fragment)
    (src / "manifest.toml").write_text('fragments = ["play.spl"]\n')
    (src / "literary.toml").write_text(GOLDEN_TOML)
    play = tmp_path / "golden.spl"
    assemble(src_dir=src, manifest=src / "manifest.toml", output=play, parse_check=True)
    result = subprocess.run(
        ["uv", "run", "shakespeare", "run", str(play)],
        input=b"",
        capture_output=True,
        cwd=REPO,
        check=True,
    )
    assert result.stdout == b"H\n"
