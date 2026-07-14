"""Slice-3 Act IV contracts land task by task."""

from tests.test_mdtest import _run_acts


def test_inline_image_emits_stripped_angle_destination_and_title() -> None:
    actual = _run_acts('![Alt text](</url/> "with a title").\n', through_act=4)
    assert isinstance(actual, str)
    assert actual == '<p><img src="/url/" alt="Alt text" title="with a title" />.</p>\n'


def test_reference_image_emits_resolved_source_and_title() -> None:
    actual = _run_acts(
        '![alt text][foo]\n\n  [foo]: /url/ "Title here"\n',
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == '<p><img src="/url/" alt="alt text" title="Title here" /></p>\n'


def test_collapsed_reference_image_uses_alt_text_as_lookup_id() -> None:
    actual = _run_acts(
        '![alt text][]\n\n  [alt text]: /url/ "Title here"\n',
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == '<p><img src="/url/" alt="alt text" title="Title here" /></p>\n'


def test_link_titles_escape_literal_quotes_as_quot_entities() -> None:
    actual = _run_acts(
        'Foo [bar][].\n\n  [bar]: /url/ "Title with "quotes" inside"\n',
        through_act=4,
    )
    assert isinstance(actual, str)
    assert actual == (
        '<p>Foo <a href="/url/" title="Title with &quot;quotes&quot; inside">'
        "bar</a>.</p>\n"
    )
