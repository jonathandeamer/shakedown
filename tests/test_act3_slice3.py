"""Slice-3 Act III contracts land task by task."""

from tests.test_mdtest import _run_acts


def test_strong_and_em_triple_delimiters_render_nested_tags() -> None:
    actual = _run_acts("***both***\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<p><strong><em>both</em></strong></p>\n"


def test_strong_and_em_triple_underscores_render_nested_tags() -> None:
    actual = _run_acts("___both___\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<p><strong><em>both</em></strong></p>\n"


def test_strong_and_em_nested_inner_emphasis_preserves_outer_strong() -> None:
    actual = _run_acts("**outer *inner* outer**\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<p><strong>outer <em>inner</em> outer</strong></p>\n"


def test_strong_and_em_escaped_and_unmatched_delimiters_stay_literal() -> None:
    actual = _run_acts("\\*literal\\* and *open only\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<p>*literal* and *open only</p>\n"


def test_strong_and_em_code_and_link_title_fields_keep_delimiters_literal() -> None:
    actual = _run_acts('`**code**` and [x](/dest/ "*title*")\n', through_act=4)
    assert isinstance(actual, str)
    assert actual == (
        '<p><code>**code**</code> and <a href="/dest/" title="*title*">x</a></p>\n'
    )


def test_strong_and_em_mixed_paragraphs_reset_resume_state() -> None:
    actual = _run_acts(
        "***This is strong and em.***\n\n"
        "So is ***this*** word.\n\n"
        "___This is strong and em.___\n",
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == (
        "<p><strong><em>This is strong and em.</em></strong></p>\n\n"
        "<p>So is <strong><em>this</em></strong> word.</p>\n\n"
        "<p><strong><em>This is strong and em.</em></strong></p>\n"
    )


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
