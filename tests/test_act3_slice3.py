"""Slice-3 Act III contracts land task by task."""

from tests.test_mdtest import _run_acts


def test_reference_links_resolve_full_collapsed_spaced_and_missing_forms() -> None:
    actual = _run_acts(
        "Full [one][ref], collapsed [one][], spaced [one] [ref], missing [two][].\n"
        "\n"
        "   [REF]: </dest/>\n",
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == (
        '<p>Full <a href="/dest/">one</a>, collapsed <a href="/dest/">one</a>, '
        'spaced <a href="/dest/">one</a>, missing [two][].</p>\n'
    )


def test_reference_record_can_be_reused_for_two_links() -> None:
    actual = _run_acts(
        "Use [first][ref] and [second] [ref].\n\n   [ref]: /dest/\n",
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == (
        '<p>Use <a href="/dest/">first</a> and <a href="/dest/">second</a>.</p>\n'
    )
