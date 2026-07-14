"""Slice 2 Task 2 Act-II contracts: horizontal-rule recognition emits
`tokens.HR`, rejected candidates replay as paragraph text, and
tab-expanded four-space candidates are reserved for the Task-3 code-block
leaf rather than becoming an HR. Verification-only — runs `src_ir.act1.ACT`
then `src_ir.act2.ACT` through the fast interpreter and decodes the forward
token stream Act II hands to Act III, without a `shakespeare` subprocess."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.splc.interpret import InterpreterState, run_act
from scripts.splc.ir import Char
from scripts.splc.token_decode import decode_stream
from scripts.splc.validate import entry_pairs, participants
from src_ir import tokens
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2

# Amendment B (2026-07-14) binary-gate reconstruction ledger: each split or
# retained label must keep the exact companion pair from the accepted design.
_EXPECTED_PAIRS: dict[str, Char] = {
    "PASS_HR_GATE": Char.HORATIO,
    "PASS_HR_GATE_MARKER": Char.PUCK,
    "PASS_HR_SAVE": Char.PUCK,
    "PASS_HR_PAIR_RETURN": Char.HECATE,
    "PASS_CODE_GATE": Char.HORATIO,
    "PASS_CODE_GATE_READ": Char.HECATE,
    "PASS_HR_MARKER_SAVE": Char.PUCK,
    "PASS_HR_SCAN": Char.MACBETH,
    "PASS_HR_SCAN_READ": Char.HECATE,
    "PASS_HR_CONFIRM": Char.MACBETH,
    "PASS_HR_CONFIRM_READ": Char.HECATE,
    "PASS_CODE_OPEN": Char.HORATIO,
    "PASS_CODE_BLANK": Char.HECATE,
}

# The remaining spare labels after Amendment B; none is implementation
# authority and none may be reachable from ACT2.scenes.
_REMAINING_SPARE_LABELS = {
    "PASS_HR_PAIR_GUARD",
    "PASS_CODE_PAIR_GUARD",
    "PASS_CODE_PAIR_RETURN",
    "PASS_BLOCK_PAIR_GUARD",
    "PASS_HR_PAIR_WATCH",
    "PASS_BLOCK_PAIR_WATCH",
}


def test_act2_scenes_have_exactly_one_companion() -> None:
    for sc in ACT2.scenes:
        anchor, companion = participants(sc, ACT2.anchor)
        assert anchor == ACT2.anchor
        assert companion is not None


def test_act2_binary_gate_ledger_pairs() -> None:
    by_label = {sc.label: sc for sc in ACT2.scenes}
    for label, expected_companion in _EXPECTED_PAIRS.items():
        assert label in by_label, f"missing scene {label}"
        anchor, companion = participants(by_label[label], ACT2.anchor)
        assert anchor == ACT2.anchor
        assert companion == expected_companion, (
            f"{label}: expected companion {expected_companion}, got {companion}"
        )


def test_act2_entry_pair_for_hr_pair_return_matches_amendment_b() -> None:
    pairs = entry_pairs(ACT2)
    assert pairs["PASS_HR_PAIR_RETURN"] == (Char.LADY_MACBETH, Char.PUCK)


def test_act2_remaining_spare_labels_are_unreachable() -> None:
    reachable_labels = {sc.label for sc in ACT2.scenes}
    assert not (reachable_labels & _REMAINING_SPARE_LABELS)


STEP_LIMIT = 200_000
FIXTURES_DIR = Path.home() / "mdtest" / "Markdown.mdtest"


def _act2_stream(input_text: str) -> list[int]:
    state = InterpreterState(input_text=input_text)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    state = run_act(ACT2, state, step_limit=STEP_LIMIT).state
    stream: list[int] = []
    while state.stacks[Char.PUCK]:
        value = state.stacks[Char.PUCK].pop()
        if value == tokens.STREAM_END:
            break
        stream.append(value)
    return stream


@pytest.mark.parametrize(
    "candidate",
    [
        "---\n\n",
        "- - -\n\n",
        "***\n\n",
        "_ _ _\n\n",
        " ---\n\n",
        "  ---\n\n",
        "   ---\n\n",
    ],
    ids=[
        "dashes",
        "spaced-dashes",
        "stars",
        "spaced-underscores",
        "one-space-indent",
        "two-space-indent",
        "three-space-indent",
    ],
)
def test_hr_markers_emit_hr_token(candidate: str) -> None:
    decoded = decode_stream(_act2_stream(candidate))
    assert [token.code for token in decoded] == [tokens.HR]


@pytest.mark.parametrize(
    "candidate",
    [" \n  ---\n\n", " \n  - - -\n\n"],
    ids=["space-blank-before-dashes", "space-blank-before-spaced-dashes"],
)
def test_space_only_line_stays_blank_before_hr(candidate: str) -> None:
    decoded = decode_stream(_act2_stream(candidate))
    assert [token.code for token in decoded] == [tokens.HR]


def test_hr_followed_by_plain_paragraph_resets_block_state() -> None:
    decoded = decode_stream(_act2_stream("---\n\nNext:\n\n"))
    assert [token.code for token in decoded] == [tokens.HR, tokens.PARA]
    assert decoded[1].text == "Next:"


def test_tab_expanded_hr_candidate_becomes_code_block_not_hr() -> None:
    decoded = decode_stream(_act2_stream("\t---\n\n"))
    assert decoded[0].code != tokens.HR
    assert decoded[0].code == tokens.CODE_BLOCK


@pytest.mark.parametrize(
    ("fixture_name", "expected_payloads"),
    [
        (
            "Code Blocks",
            [
                "code block on the first line\n",
                "code block indented by spaces\n",
                "the lines in this block  \nall contain trailing spaces  \n",
                "code block on the last line\n",
            ],
        ),
        (
            "Tabs",
            [
                "this code block is indented by one tab\n",
                "    this code block is indented by two tabs\n",
                (
                    "+   this is an example list item\n"
                    "    indented with tabs\n"
                    "\n"
                    "+   this is an example list item\n"
                    "    indented with spaces\n"
                ),
            ],
        ),
    ],
    ids=["Code Blocks", "Tabs"],
)
def test_fixture_code_block_streams(
    fixture_name: str, expected_payloads: list[str]
) -> None:
    input_text = (FIXTURES_DIR / f"{fixture_name}.text").read_text()
    decoded = decode_stream(_act2_stream(input_text))
    code_blocks = [token for token in decoded if token.code == tokens.CODE_BLOCK]

    assert [token.text for token in code_blocks] == expected_payloads
    if fixture_name == "Tabs":
        # The final tab-expanded example-list region is one code leaf. Its
        # leading plus signs must never re-enter the list-token grammar.
        assert decoded[-1] == code_blocks[-1]
