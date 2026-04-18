import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

SHAKESPEARE = shutil.which("shakespeare")
if SHAKESPEARE is None:
    fallback = Path.home() / ".local/bin/shakespeare"
    if fallback.is_file():
        SHAKESPEARE = str(fallback)
    else:
        pytest.skip(
            "shakespeare interpreter not found on PATH or in ~/.local/bin",
            allow_module_level=True,
        )


def _run_spl(program: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        play_path = Path(tmpdir) / "probe.spl"
        play_path.write_text(program)
        return subprocess.run(
            [str(SHAKESPEARE), "run", str(play_path)],
            input=stdin,
            capture_output=True,
            text=True,
        )


def _program(*body_lines: str) -> str:
    body = "\n".join(body_lines)
    return (
        "Title.\n\n"
        "Romeo, a man.\n"
        "Juliet, a woman.\n\n"
        "                    Act I: Test.\n\n"
        "                    Scene I: Test.\n\n"
        "[Enter Romeo and Juliet]\n\n"
        f"{body}\n\n"
        "[Exeunt]\n"
    )


def _assert_program_output(program: str, expected: str) -> None:
    result = _run_spl(program)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == expected


def test_positive_phrase_example_runs_and_emits_expected_value() -> None:
    program = """Title.

Romeo, a man.
Juliet, a woman.

                    Act I: Test.

                    Scene I: Test.

[Enter Romeo and Juliet]

Juliet: You are as noble as a noble peaceful golden hero.
Juliet: Open your heart!

[Exeunt]
"""
    result = _run_spl(program)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "8"


def test_additional_representative_phrase_examples_run_and_emit_expected_values() -> (
    None
):
    _assert_program_output(
        _program(
            "Juliet: You are as good as a beautiful rural morning.",
            "Juliet: Open your heart!",
        ),
        "4",
    )
    _assert_program_output(
        _program(
            "Juliet: You are as good as a vile smelly plague.",
            "Juliet: Open your heart!",
        ),
        "-4",
    )
    _assert_program_output(
        _program(
            "Juliet: You are as good as a fatherless half-witted coward.",
            "Juliet: Open your heart!",
        ),
        "-4",
    )


def test_same_sign_positive_substitution_preserves_positive_sign() -> None:
    _assert_program_output(
        _program(
            "Juliet: You are as good as a cat.",
            "Juliet: Open your heart!",
        ),
        "1",
    )
    _assert_program_output(
        _program(
            "Juliet: You are as good as a fellow.",
            "Juliet: Open your heart!",
        ),
        "1",
    )


def test_same_sign_negative_substitution_preserves_negative_sign() -> None:
    _assert_program_output(
        _program(
            "Juliet: You are as good as a pig.",
            "Juliet: Open your heart!",
        ),
        "-1",
    )
    _assert_program_output(
        _program(
            "Juliet: You are as good as a wolf.",
            "Juliet: Open your heart!",
        ),
        "-1",
    )


def test_same_magnitude_substitution_preserves_value() -> None:
    _assert_program_output(
        _program(
            "Juliet: You are as good as a big cat.",
            "Juliet: Open your heart!",
        ),
        "2",
    )
    _assert_program_output(
        _program(
            "Juliet: You are as good as a red fellow.",
            "Juliet: Open your heart!",
        ),
        "2",
    )
    _assert_program_output(
        _program(
            "Juliet: You are as good as an old pig.",
            "Juliet: Open your heart!",
        ),
        "-2",
    )
    _assert_program_output(
        _program(
            "Juliet: You are as good as a big pig.",
            "Juliet: Open your heart!",
        ),
        "-2",
    )


def test_invalid_magnitude_variation_changes_value() -> None:
    cat = _run_spl(
        _program(
            "Juliet: You are as good as a cat.",
            "Juliet: Open your heart!",
        )
    )
    big_cat = _run_spl(
        _program(
            "Juliet: You are as good as a big cat.",
            "Juliet: Open your heart!",
        )
    )

    assert cat.returncode == 0, cat.stderr
    assert big_cat.returncode == 0, big_cat.stderr
    assert cat.stdout.strip() == "1"
    assert big_cat.stdout.strip() == "2"
    assert cat.stdout.strip() != big_cat.stdout.strip()


def test_representative_comparison_examples_parse_and_run() -> None:
    equality = _run_spl(
        _program(
            "Juliet: You are as good as a noble peaceful golden hero.",
            "Juliet: Are you as noble as a noble peaceful golden hero?",
            "Juliet: If so, Open your heart!",
        )
    )
    positive = _run_spl(
        _program(
            "Juliet: You are as good as a beautiful rural morning.",
            "Juliet: Are you friendlier than a gentle pony?",
            "Juliet: If so, Open your heart!",
        )
    )
    negative = _run_spl(
        _program(
            "Juliet: You are as good as a vile smelly plague.",
            "Juliet: Are you punier than a dirty pig?",
            "Juliet: If so, Open your heart!",
        )
    )

    assert equality.returncode == 0, equality.stderr
    assert positive.returncode == 0, positive.stderr
    assert negative.returncode == 0, negative.stderr
    assert equality.stdout.strip() == "8"
    assert positive.stdout.strip() == "4"
    assert negative.stdout.strip() == "-4"


def test_codegen_assignment_examples_match_documented_values() -> None:
    _assert_program_output(
        _program(
            "Juliet: You are as good as nothing.",
            "Juliet: Open your heart!",
        ),
        "0",
    )
    _assert_program_output(
        _program(
            "Juliet: You are as lovely as a cat.",
            "Juliet: Open your heart!",
        ),
        "1",
    )
    _assert_program_output(
        _program(
            "Juliet: You are the sum of a cat and a cat.",
            "Juliet: Open your heart!",
        ),
        "2",
    )
    _assert_program_output(
        _program(
            "Juliet: You are the difference between yourself and nothing.",
            "Juliet: Open your heart!",
        ),
        "0",
    )


def test_stack_adjacent_examples_run_without_semantic_contradiction() -> None:
    _assert_program_output(
        _program(
            "Juliet: Remember a cat.",
            "Juliet: Remember nothing.",
            "Juliet: Recall your past sins.",
            "Juliet: Open your heart!",
        ),
        "0",
    )
