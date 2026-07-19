"""Pure-IR Act III link/image contracts (no Python rewrite).

Task 3 of docs/superpowers/plans/2026-07-19-spl-pure-release-path.md:
raw Markdown → Act IV HTML via the IR interpreter **without**
``rewrite_task3_markdown``, compared to the local Markdown.pl oracle.

Witnesses 3a–3e are red until Act III resolves links/images from the Act I
reference table and raw span syntax.
"""

from __future__ import annotations

import subprocess

from scripts.paths import markdown_pl
from scripts.runtime_constants import DOCUMENTATION_STEP_LIMIT
from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4

_MARKDOWN_PL = markdown_pl()


def _interpret_ir_pure(input_text: str) -> str:
    """Full IR pipeline without Python ``rewrite_task3_markdown``."""
    state = InterpreterState(input_text=input_text)
    for act in (ACT1, ACT2, ACT3, ACT4):
        state = run_act(act, state, step_limit=DOCUMENTATION_STEP_LIMIT).state
    return state.output_text()


def _oracle_html(input_text: str) -> str:
    """Local Markdown.pl bytes for a minimal slice."""
    return subprocess.run(
        ["perl", str(_MARKDOWN_PL)],
        input=input_text,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _assert_pure_matches_oracle(source: str) -> None:
    assert _interpret_ir_pure(source) == _oracle_html(source)


# --- 3a: Inline link + angle-bracket dest + amp encoding ---


def test_3a_inline_link_with_ampersand_in_url() -> None:
    _assert_pure_matches_oracle("Here's an inline [link](/script?foo=1&bar=2).\n")


def test_3a_inline_link_angle_bracket_dest_with_ampersand() -> None:
    _assert_pure_matches_oracle("Here's an inline [link](</script?foo=1&bar=2>).\n")


def test_3a_inline_link_angle_bracket_dest_unwrapped() -> None:
    """Angle brackets around the destination must not appear in href."""
    _assert_pure_matches_oracle("[URL wrapped in angle brackets](</url/>).\n")


def test_3a_inline_link_title_preceded_by_two_spaces() -> None:
    _assert_pure_matches_oracle(
        '[URL and title](/url/  "title preceded by two spaces").\n'
    )


def test_3a_inline_link_title_with_trailing_spaces_before_close() -> None:
    _assert_pure_matches_oracle(
        '[URL and title](/url/ "title has spaces afterward"  ).\n'
    )


def test_3a_inline_link_angle_bracket_dest_with_title() -> None:
    _assert_pure_matches_oracle(
        '[URL w/ angle brackets + title](</url/> "Here\'s the title").\n'
    )


# --- 3b: Inline image ---


def test_3b_inline_image_empty_title_attribute() -> None:
    """Markdown.pl emits title="" for title-less inline images."""
    _assert_pure_matches_oracle("![Alt text](/path/to/img.jpg)\n")


def test_3b_inline_image_with_title() -> None:
    _assert_pure_matches_oracle('![Alt text](/path/to/img.jpg "Optional title")\n')


def test_3b_inline_image_angle_bracket_dest() -> None:
    _assert_pure_matches_oracle("![alt text](</url/>)\n")


def test_3b_inline_image_title_preceded_by_two_spaces() -> None:
    _assert_pure_matches_oracle('![alt text](/url/  "title preceded by two spaces")\n')


def test_3b_inline_image_parens_in_url() -> None:
    _assert_pure_matches_oracle(
        "![this is a stupid URL](http://example.com/(parens).jpg)\n"
    )


# --- 3c: Full / collapsed / spaced reference links ---


def test_3c_full_reference_link_spaced_id() -> None:
    _assert_pure_matches_oracle('Foo [bar] [1].\n\n[1]: /url/  "Title"\n')


def test_3c_full_reference_link_tight_id() -> None:
    _assert_pure_matches_oracle('Foo [bar][1].\n\n[1]: /url/  "Title"\n')


def test_3c_collapsed_reference_link() -> None:
    _assert_pure_matches_oracle("Indented [once][].\n\n [once]: /url\n")


def test_3c_spaced_reference_link_with_casefold() -> None:
    """Spaced ref + uppercase def id must case-fold to the Act I table."""
    _assert_pure_matches_oracle(
        "Full [one][ref], collapsed [one][], spaced [one] [ref], missing [two][].\n"
        "\n"
        "   [REF]: </dest/>\n"
    )


def test_3c_shortcut_reference_link() -> None:
    _assert_pure_matches_oracle(
        "This is the [simple case].\n\n[simple case]: /simple\n"
    )


# --- 3d: Reference images + title quotes ---


def test_3d_reference_image() -> None:
    _assert_pure_matches_oracle("![alt text][foo]\n\n  [foo]: /url/\n")


def test_3d_reference_image_with_title() -> None:
    _assert_pure_matches_oracle('![alt text][bar]\n\n  [bar]: /url/ "Title here"\n')


def test_3d_inline_link_title_with_literal_quotes() -> None:
    _assert_pure_matches_oracle('Foo [bar](/url/ "Title with "quotes" inside").\n')


def test_3d_reference_link_title_with_literal_quotes() -> None:
    _assert_pure_matches_oracle(
        'Foo [bar][].\n\n  [bar]: /url/ "Title with "quotes" inside"\n'
    )


# --- 3e: Nested brackets / broken-line link text ---


def test_3e_nested_brackets_in_link_text() -> None:
    _assert_pure_matches_oracle("With [embedded [brackets]] [b].\n\n[b]: /url/\n")


def test_3e_link_text_breaks_across_lines() -> None:
    _assert_pure_matches_oracle(
        "Here's one where the [link\nbreaks] across lines.\n\n[link breaks]: /url/\n"
    )


def test_3e_link_text_breaks_with_line_ending_space() -> None:
    _assert_pure_matches_oracle(
        "Here's another where the [link \n"
        "breaks] across lines, but with a line-ending space.\n\n"
        "[link breaks]: /url/\n"
    )


def test_3e_self_referential_shortcut_style() -> None:
    """Reference-style cases from the Links, reference style fixture."""
    _assert_pure_matches_oracle("[this] [this] should work\n\n[this]: foo\n")
