"""Act I reference-definition contracts for the SPL-pure release path.

Task 2 of docs/superpowers/plans/2026-07-19-spl-pure-release-path.md
(Amendment A1): after Act I, definition lines are absent from the body
stream and Rosalind holds a case-folded reference table. The IR
interpreter no longer pre-strips via Python ``strip_reference_definitions``;
Act I owns strip at ``HECATE_REF_OPEN``.
"""

from __future__ import annotations

from dataclasses import dataclass

from scripts.slice3_links import ReferenceRecord, strip_reference_definitions
from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.cast import HECATE, HORATIO, ROSALIND

STEP_LIMIT = 200_000

# Immutable Rosalind floor pushed at ACT_I_START (src_ir/act1.py).
_ROSALIND_FLOOR = (1, 101, 0, 2, 102, 201)
_RECORD_END = -6


@dataclass(frozen=True)
class Act1RefView:
    """Body stream + decoded Rosalind table after Act I (no Python strip)."""

    body: str
    body_count: int
    refs: dict[str, ReferenceRecord]


def _normalize_body_after_strip(stripped: str) -> str:
    """Act I final-newline contract on an already-stripped body."""
    lines = stripped.split("\n")
    expanded_lines: list[str] = []
    for line in lines:
        column = 0
        out_chars: list[str] = []
        for ch in line:
            if ch == "\t":
                spaces = 4 - (column % 4)
                out_chars.append(" " * spaces)
                column += spaces
            else:
                out_chars.append(ch)
                column += 1
        expanded_lines.append("".join(out_chars))
    body = "\n".join(expanded_lines).rstrip("\n")
    return body + "\n\n"


def _expected_act1_after_strip(
    input_text: str,
) -> tuple[str, dict[str, ReferenceRecord]]:
    stripped, refs = strip_reference_definitions(input_text)
    return _normalize_body_after_strip(stripped), refs


def _decode_rosalind_table(stack: list[int]) -> dict[str, ReferenceRecord]:
    """Decode Amendment A1.2 records above the bootstrap floor.

    Later stores win for a given label (scan bottom→top assignment).
    """
    if len(stack) < len(_ROSALIND_FLOOR):
        return {}
    if tuple(stack[: len(_ROSALIND_FLOOR)]) != _ROSALIND_FLOOR:
        return {}
    pos = len(_ROSALIND_FLOOR)
    refs: dict[str, ReferenceRecord] = {}
    data = stack
    while pos < len(data):
        if pos >= len(data):
            break
        label_len = data[pos]
        pos += 1
        if label_len < 0 or pos + label_len > len(data):
            return {}
        label = "".join(chr(c) for c in data[pos : pos + label_len])
        pos += label_len
        if pos >= len(data):
            return {}
        dest_len = data[pos]
        pos += 1
        if dest_len < 0 or pos + dest_len > len(data):
            return {}
        dest = "".join(chr(c) for c in data[pos : pos + dest_len])
        pos += dest_len
        if pos >= len(data):
            return {}
        title_len = data[pos]
        pos += 1
        if title_len < 0 or pos + title_len > len(data):
            return {}
        title: str | None
        if title_len == 0:
            title = None
        else:
            title = "".join(chr(c) for c in data[pos : pos + title_len])
            pos += title_len
        if pos >= len(data) or data[pos] != _RECORD_END:
            return {}
        pos += 1
        refs[label] = ReferenceRecord(destination=dest, title=title)
    return refs


def _run_act1_without_python_strip(input_text: str) -> Act1RefView:
    """Act I only — production interpret path has no Python strip hook."""
    state = InterpreterState(input_text=input_text)
    run_act(ACT1, state, step_limit=STEP_LIMIT)
    body = "".join(chr(code) for code in reversed(state.stacks[HECATE]))
    refs = _decode_rosalind_table(list(state.stacks[ROSALIND]))
    return Act1RefView(body=body, body_count=state.values[HORATIO], refs=refs)


def test_simple_definition_stripped_and_stored() -> None:
    source = '[foo]: /url "title"\n'
    expected_body, expected_refs = _expected_act1_after_strip(source)
    view = _run_act1_without_python_strip(source)
    assert "[foo]:" not in view.body
    assert view.body == expected_body
    assert len(view.body) == view.body_count
    assert view.refs == expected_refs
    assert view.refs["foo"] == ReferenceRecord(destination="/url", title="title")


def test_up_to_three_leading_spaces_are_definitions() -> None:
    source = " [once]: /url\n  [twice]: /url\n   [thrice]: /url\n"
    expected_body, expected_refs = _expected_act1_after_strip(source)
    view = _run_act1_without_python_strip(source)
    assert "[once]:" not in view.body
    assert "[twice]:" not in view.body
    assert "[thrice]:" not in view.body
    assert view.body == expected_body
    assert view.refs == expected_refs


def test_four_leading_spaces_are_not_definitions() -> None:
    source = "    [code]: /not-def\n"
    expected_body, expected_refs = _expected_act1_after_strip(source)
    view = _run_act1_without_python_strip(source)
    assert "[code]:" in view.body
    assert view.body == expected_body
    assert view.refs == expected_refs
    assert expected_refs == {}


def test_label_case_fold() -> None:
    source = "[Foo]: /u\n"
    expected_body, expected_refs = _expected_act1_after_strip(source)
    view = _run_act1_without_python_strip(source)
    assert "[Foo]:" not in view.body
    assert view.body == expected_body
    assert "foo" in view.refs
    assert view.refs["foo"].destination == "/u"
    assert view.refs == expected_refs


def test_angle_bracket_destination() -> None:
    source = "[id]: <http://x>\n"
    expected_body, expected_refs = _expected_act1_after_strip(source)
    view = _run_act1_without_python_strip(source)
    assert "[id]:" not in view.body
    assert view.body == expected_body
    assert view.refs["id"].destination == "http://x"
    assert view.refs == expected_refs


def test_title_on_next_line() -> None:
    source = '[foo]: /url\n"title on next line"\n\npara\n'
    expected_body, expected_refs = _expected_act1_after_strip(source)
    view = _run_act1_without_python_strip(source)
    assert "[foo]:" not in view.body
    assert "title on next line" not in view.body or "para" in view.body
    assert "para" in view.body
    assert view.body == expected_body
    assert view.refs["foo"].title == "title on next line"
    assert view.refs == expected_refs


def test_defs_plus_paragraph_body_keeps_only_paragraph() -> None:
    source = '[foo]: /url "title"\n\npara\n'
    expected_body, expected_refs = _expected_act1_after_strip(source)
    view = _run_act1_without_python_strip(source)
    assert "[foo]:" not in view.body
    assert "para" in view.body
    assert view.body == expected_body
    assert view.refs == expected_refs


def test_invalid_bracket_line_remains_body() -> None:
    source = "[not a definition\n"
    expected_body, expected_refs = _expected_act1_after_strip(source)
    view = _run_act1_without_python_strip(source)
    assert "[not a definition" in view.body
    assert view.body == expected_body
    assert view.refs == expected_refs
    assert expected_refs == {}
