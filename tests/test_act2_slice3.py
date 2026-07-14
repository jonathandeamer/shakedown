"""Slice-3 Act II contracts land task by task."""

from tests.test_mdtest import _run_acts


def test_hard_wrap_digit_dot_line_stays_in_paragraph_without_blank_boundary() -> None:
    actual = _run_acts("Paragraph\n8. Oops\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<p>Paragraph\n8. Oops</p>\n"


def test_hard_wrap_digit_dot_line_forms_list_with_blank_boundary() -> None:
    actual = _run_acts("\n\n8. List\n", through_act=4)
    assert isinstance(actual, str)
    assert actual == "<ol>\n<li>List</li>\n</ol>\n"
