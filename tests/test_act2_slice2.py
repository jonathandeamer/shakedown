"""Slice 2 Task 2 Act-II contracts: horizontal-rule recognition emits
`tokens.HR`, rejected candidates replay as paragraph text, and
tab-expanded four-space candidates are reserved for the Task-3 code-block
leaf rather than becoming an HR. Verification-only — runs `src_ir.act1.ACT`
then `src_ir.act2.ACT` through the fast interpreter and decodes the forward
token stream Act II hands to Act III, without a `shakespeare` subprocess."""

from __future__ import annotations

import pytest

from scripts.paths import mdtest_fixtures_dir
from scripts.splc.interpret import InterpreterState, StackUnderflow, run_act
from scripts.splc.ir import Branch, Char, Const, Goto, Let, Pop, Push, Val
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
    "PASS_HR_FALLBACK_LIST_HANDOFF": Char.MACBETH,
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
    """Every Act II scene is a legal two-character stage pair.

    Slice 5 authorized per-scene ``anchor=`` overrides (Hecate/Puck/Horatio/
    Macbeth) for Setext, ATX trail, code-line, and whitespace-blank machines.
    The act default remains Lady Macbeth; ``participants`` still requires
    exactly one non-anchor character per scene.
    """
    for sc in ACT2.scenes:
        anchor, companion = participants(sc, ACT2.anchor)
        assert anchor is not None
        assert companion is not None
        assert companion != anchor


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


def test_act2_quote_rewire_keeps_raw_blank_scene_reachable() -> None:
    pairs = entry_pairs(ACT2)
    assert pairs["PASS_LISTS_RAW_BLANK"] == (Char.LADY_MACBETH, Char.HECATE)


def test_act2_remaining_spare_labels_are_unreachable() -> None:
    reachable_labels = {sc.label for sc in ACT2.scenes}
    assert not (reachable_labels & _REMAINING_SPARE_LABELS)


def test_hr_candidate_fallback_preserves_unordered_list_handoff() -> None:
    by_label = {sc.label: sc for sc in ACT2.scenes}
    fallback = by_label["PASS_HR_FALLBACK"]
    handoff_label = "PASS_HR_FALLBACK_LIST_HANDOFF"

    marker_targets = {
        op.cond.right.value: op.then
        for op in fallback.ops
        if isinstance(op, Branch)
        and op.cond.op == "eq"
        and isinstance(op.cond.left, Val)
        and op.cond.left.char is Char.PUCK
        and isinstance(op.cond.right, Const)
    }
    assert marker_targets[42] == handoff_label
    assert marker_targets[45] == handoff_label
    assert marker_targets[95] == "PASS_CODE_REPLAY"

    handoff = by_label[handoff_label]
    assert handoff.ops == (
        Push(Char.LADY_MACBETH, Const(tokens.LIST_OPEN)),
        Push(Char.LADY_MACBETH, Const(1)),
        Push(Char.MACBETH, Const(1)),
        Let(Char.MACBETH, Const(1)),
        Goto("PASS_LISTS_ITEM_BEGIN_TIGHT"),
    )
    assert not any(isinstance(op, Pop) for op in handoff.ops)


def test_rejected_repeated_asterisk_hr_candidate_stays_paragraph_text() -> None:
    decoded = decode_stream(_act2_stream("***both*** and **outer *inner* outer**\n"))

    assert [token.code for token in decoded] == [tokens.PARA]
    assert decoded[0].text == "***both*** and **outer *inner* outer**"


STEP_LIMIT = 200_000
FIXTURES_DIR = mdtest_fixtures_dir()
TIDYNESS_INPUT = (
    "> A list within a blockquote:\n"
    "> \n"
    "> *\tasterisk 1\n"
    "> *\tasterisk 2\n"
    "> *\tasterisk 3\n"
)


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


def test_tidyness_quote_list_stream_stages_every_block_start_read() -> None:
    input_path = FIXTURES_DIR / "Tidyness.text"
    assert input_path.read_text() == TIDYNESS_INPUT

    state = InterpreterState(input_text=TIDYNESS_INPUT)
    state = run_act(ACT1, state, step_limit=STEP_LIMIT).state
    block_start_hecate_depths: list[int] = []

    class _Observer:
        def on_scene(self, label: str, state: InterpreterState) -> None:
            if label == "PASS_LISTS_BLOCK_START":
                block_start_hecate_depths.append(len(state.stacks[Char.HECATE]))

        def on_push(self, char: Char, value: int, stack_after: list[int]) -> None:
            return None

        def on_pop(self, char: Char, value: int, stack_after: list[int]) -> None:
            return None

    try:
        state = run_act(
            ACT2,
            state,
            step_limit=STEP_LIMIT,
            observer=_Observer(),
        ).state
    except StackUnderflow as exc:
        pytest.fail(f"{exc}: PASS_LISTS_BLOCK_START requires a staged Hecate glyph")

    assert block_start_hecate_depths
    assert all(depth > 0 for depth in block_start_hecate_depths)

    stream: list[int] = []
    while state.stacks[Char.PUCK]:
        value = state.stacks[Char.PUCK].pop()
        if value == tokens.STREAM_END:
            break
        stream.append(value)
    decoded = decode_stream(stream)

    assert [(token.code, token.payloads, token.text) for token in decoded] == [
        (tokens.BLOCKQUOTE_OPEN, (), None),
        (tokens.PARA, (), "A list within a blockquote:"),
        (tokens.LIST_OPEN, (1,), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "asterisk 1"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "asterisk 2"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_ITEM, (1,), None),
        (tokens.PARA, (), "asterisk 3"),
        (tokens.ITEM_CLOSE, (), None),
        (tokens.LIST_CLOSE, (), None),
        (tokens.BLOCKQUOTE_CLOSE, (), None),
    ]


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
