"""Slice-5 documentation aggregate pre-enable contracts."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.runtime_constants import DOCUMENTATION_STEP_LIMIT
from scripts.slice3_links import rewrite_task3_markdown
from scripts.splc.interpret import InterpreterState, run_act
from src_ir.act1 import ACT as ACT1
from src_ir.act2 import ACT as ACT2
from src_ir.act3 import ACT as ACT3
from src_ir.act4 import ACT as ACT4
from tests.test_act2_slice4 import (
    BASICS_ATX_CLOSING_HASH,
    BASICS_PROJECT_SUBMENU,
    BASICS_SETEXT_H1,
    BASICS_SETEXT_H2,
)
from tests.test_mdtest import (
    _FIXTURES_BY_NAME,
    _IMPLEMENTED_FIXTURES,
    _SLICE5_STRICT_READY_FIXTURES,
    BINARY,
    _normalize_fixture_output,
    _run_acts,
)

REPO = Path(__file__).parent.parent
HARNESS = REPO / "scripts" / "strict_parity_harness.py"
MARKDOWN_PL = Path.home() / "markdown" / "Markdown.pl"
TIDYNESS_INPUT = (
    "> A list within a blockquote:\n"
    "> \n"
    "> *\tasterisk 1\n"
    "> *\tasterisk 2\n"
    "> *\tasterisk 3\n"
)

# Contiguous substrings of Markdown Documentation — Syntax used as the finite
# Task-4 category inventory. Each category must keep fast-IR / release / raw
# oracle assertions before production repairs begin (plan Task 4 Step 1).
SYNTAX_RAW_TOP_LEVEL_HTML = (
    '<h2 id="overview">Overview</h2>\n\n<h3 id="philosophy">Philosophy</h3>\n'
)
SYNTAX_NESTED_LIST_CLOSE = (
    "*   [Span Elements](#span)\n"
    "    *   [Links](#link)\n"
    "    *   [Emphasis](#em)\n"
    "    *   [Code](#code)\n"
    "    *   [Images](#img)\n"
    "*   [Miscellaneous](#misc)\n"
)
SYNTAX_MULTI_DEFINITION_REFERENCE = (
    "I get 10 times more traffic from [Google] [1] than from\n"
    "    [Yahoo] [2] or [MSN] [3].\n"
    "\n"
    '      [1]: http://google.com/        "Google"\n'
    '      [2]: http://search.yahoo.com/  "Yahoo Search"\n'
    '      [3]: http://search.msn.com/    "MSN Search"\n'
)
SYNTAX_PARAGRAPH_BLOCK_SEPARATORS = (
    "**Note:** This document is itself written using Markdown; you\n"
    "can [see the source for it by adding '.text' to the URL][src].\n"
    "\n"
    "  [src]: /projects/markdown/syntax.text\n"
    "\n"
    "* * *\n"
    "\n"
    '<h2 id="overview">Overview</h2>\n'
)


@dataclass(frozen=True)
class ByteDifference:
    """First raw-byte mismatch between oracle and actual HTML."""

    offset: int
    oracle_slice: bytes
    actual_slice: bytes


@dataclass(frozen=True)
class SyntaxDiffCategory:
    """One finite Syntax mismatch category with its source witness."""

    name: str
    source_witness: str
    owning_act: str


SYNTAX_DIFF_CATEGORIES: tuple[SyntaxDiffCategory, ...] = (
    SyntaxDiffCategory(
        name="raw_top_level_html",
        source_witness=SYNTAX_RAW_TOP_LEVEL_HTML,
        owning_act="act2",
    ),
    SyntaxDiffCategory(
        name="nested_list_close_ordering",
        source_witness=SYNTAX_NESTED_LIST_CLOSE,
        owning_act="act2",
    ),
    SyntaxDiffCategory(
        name="multi_definition_reference_resolution",
        source_witness=SYNTAX_MULTI_DEFINITION_REFERENCE,
        owning_act="wrapper_rewrite",
    ),
    SyntaxDiffCategory(
        name="paragraph_block_separators",
        source_witness=SYNTAX_PARAGRAPH_BLOCK_SEPARATORS,
        owning_act="act2",
    ),
)


def _run_acts_with_limit(
    input_text: str, *, through_act: int, step_limit: int
) -> str | list[int]:
    from scripts.splc.ir import Char
    from src_ir import tokens

    state = InterpreterState(input_text=input_text)
    acts = (ACT1, ACT2, ACT3, ACT4)
    for act in acts[:through_act]:
        state = run_act(act, state, step_limit=step_limit).state
    if through_act == 4:
        return state.output_text()
    stream = list(reversed(state.stacks[Char.PUCK]))
    if stream and stream[-1] == tokens.STREAM_END:
        stream.pop()
    return stream


def _fixture_paths(name: str) -> tuple[Path, Path]:
    return _FIXTURES_BY_NAME[name]


def _oracle_bytes(input_bytes: bytes) -> bytes:
    oracle = subprocess.run(
        ["perl", str(MARKDOWN_PL)],
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=False,
    )
    assert oracle.returncode == 0, oracle.stderr.decode()
    return oracle.stdout


def _release_bytes(input_bytes: bytes) -> bytes:
    release = subprocess.run(
        [str(BINARY)],
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=False,
    )
    assert release.returncode == 0, release.stderr.decode()
    return release.stdout


def _first_byte_difference(oracle: bytes, actual: bytes) -> ByteDifference | None:
    """Return the first differing offset and a short context window around it."""
    limit = min(len(oracle), len(actual))
    offset = 0
    while offset < limit and oracle[offset] == actual[offset]:
        offset += 1
    if offset == limit and len(oracle) == len(actual):
        return None
    window = 48
    start = max(0, offset - window)
    end_oracle = min(len(oracle), offset + window)
    end_actual = min(len(actual), offset + window)
    return ByteDifference(
        offset=offset,
        oracle_slice=oracle[start:end_oracle],
        actual_slice=actual[start:end_actual],
    )


def _source_mismatches_oracle(source: str) -> bool:
    input_bytes = source.encode()
    try:
        cand_oracle = _oracle_bytes(input_bytes)
        cand_release = _release_bytes(input_bytes)
    except AssertionError:
        return False
    return _first_byte_difference(cand_oracle, cand_release) is not None


def _minimal_contiguous_source_witness(
    source: str,
    *,
    oracle: bytes,
    release: bytes,
    difference: ByteDifference,
) -> str:
    """Shrink ``source`` to a short contiguous prefix that still mismatches.

    The full Syntax fixture is large; the inventory only needs a contiguous
    witness that still reproduces a release/oracle byte mismatch. Grow an
    exponential prefix until the first mismatch appears, then binary-search
    inside that window so the helper never re-runs the full aggregate.
    """
    del oracle, release, difference  # recorded by caller; shrink uses live runs
    if not source:
        return source

    # Exponential upper bound: stop at the first mismatched prefix window.
    high = 64
    while high < len(source) and not _source_mismatches_oracle(source[:high]):
        high = min(len(source), high * 2)
    if not _source_mismatches_oracle(source[:high]):
        return source

    # Shortest prefix inside [high/2, high] that still mismatches.
    low = max(1, high // 2)
    best = source[:high]
    while low <= high:
        mid = (low + high) // 2
        candidate = source[:mid]
        if _source_mismatches_oracle(candidate):
            best = candidate
            high = mid - 1
        else:
            low = mid + 1
    return best


def _assert_fast_release_raw_oracle(source: str) -> None:
    """Shared three-way strict parity gate for a Syntax category witness."""
    input_bytes = source.encode()
    expected = _oracle_bytes(input_bytes)

    fast_actual = _run_acts(source, through_act=4)
    assert isinstance(fast_actual, str)
    assert fast_actual.encode() == expected

    assert _release_bytes(input_bytes) == expected


@pytest.mark.parametrize(
    "source",
    [
        BASICS_SETEXT_H1,
        BASICS_SETEXT_H2,
        BASICS_PROJECT_SUBMENU,
        BASICS_ATX_CLOSING_HASH,
    ],
    ids=["setext_h1", "setext_h2", "raw_html", "closing_hash"],
)
def test_basics_minimal_witness_matches_fast_release_and_raw_oracle(
    source: str,
) -> None:
    input_bytes = source.encode()
    expected = _oracle_bytes(input_bytes)

    fast_actual = _run_acts(source, through_act=4)
    assert isinstance(fast_actual, str)
    assert fast_actual.encode() == expected

    release = subprocess.run(
        [str(BINARY)],
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=False,
    )
    assert release.returncode == 0, release.stderr.decode()
    assert release.stdout == expected


def test_basics_full_fixture_matches_fast_release_and_raw_oracle() -> None:
    input_path, _ = _fixture_paths("Markdown Documentation - Basics")
    input_bytes = input_path.read_bytes()
    expected = _oracle_bytes(input_bytes)

    fast_actual = _run_acts(input_bytes.decode(), through_act=4)
    assert isinstance(fast_actual, str)
    assert fast_actual.encode() == expected

    release = subprocess.run(
        [str(BINARY)],
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=False,
    )
    assert release.returncode == 0, release.stderr.decode()
    assert release.stdout == expected


@pytest.mark.parametrize("through_act", [1, 2, 3, 4])
def test_syntax_fits_within_documentation_step_limit_per_act(through_act: int) -> None:
    input_path, _ = _fixture_paths("Markdown Documentation - Syntax")
    actual = _run_acts_with_limit(
        input_path.read_text(),
        through_act=through_act,
        step_limit=DOCUMENTATION_STEP_LIMIT,
    )
    if through_act == 4:
        assert isinstance(actual, str)
        return
    assert isinstance(actual, list)


def test_syntax_release_binary_returns_zero() -> None:
    input_path, _ = _fixture_paths("Markdown Documentation - Syntax")
    result = subprocess.run(
        [str(BINARY)],
        input=input_path.read_text(),
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("fixture_name", sorted(_SLICE5_STRICT_READY_FIXTURES))
def test_slice5_strict_ready_fixture_enablement_contracts(fixture_name: str) -> None:
    input_path, expected_path = _fixture_paths(fixture_name)

    assert fixture_name in _IMPLEMENTED_FIXTURES

    actual = _run_acts(input_path.read_text(), through_act=4)
    assert isinstance(actual, str)
    assert _normalize_fixture_output(fixture_name, actual) == _normalize_fixture_output(
        fixture_name, expected_path.read_text()
    )

    result = subprocess.run(
        [str(BINARY)],
        input=input_path.read_text(),
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert _normalize_fixture_output(
        fixture_name, result.stdout
    ) == _normalize_fixture_output(fixture_name, expected_path.read_text())

    harness = subprocess.run(
        [sys.executable, str(HARNESS), fixture_name],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    )
    assert harness.returncode == 0, harness.stderr
    assert "summary: 1/1 byte-identical" in harness.stdout


def test_tidyness_exact_fixture_matches_fast_release_and_raw_oracle() -> None:
    fixture_name = "Tidyness"
    input_path, expected_path = _fixture_paths(fixture_name)
    assert input_path.read_text() == TIDYNESS_INPUT
    input_bytes = TIDYNESS_INPUT.encode()
    oracle = subprocess.run(
        ["perl", str(MARKDOWN_PL)],
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=False,
    )
    assert oracle.returncode == 0, oracle.stderr.decode()

    # The checked-in mdtest expectation is a legacy 133-byte corpus artifact.
    # Tidyness is deterministic, so the installed Markdown.pl bytes are the
    # authoritative parity contract without mutating that fixture.
    assert expected_path.read_bytes() != oracle.stdout

    fast_actual = _run_acts(TIDYNESS_INPUT, through_act=4)
    assert isinstance(fast_actual, str)
    assert fast_actual.encode() == oracle.stdout

    release = subprocess.run(
        [str(BINARY)],
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=False,
    )

    assert fixture_name in _IMPLEMENTED_FIXTURES
    assert release.returncode == 0, release.stderr.decode()
    assert release.stdout == oracle.stdout


def test_syntax_diff_category_inventory_records_first_difference() -> None:
    """Compare release Syntax bytes to the local oracle and record the inventory.

    The helper captures the first differing offset plus a minimal contiguous
    source witness. Seeded categories must remain exact substrings of the
    Syntax fixture so later repairs stay tied to real aggregate evidence.
    """
    input_path, _ = _fixture_paths("Markdown Documentation - Syntax")
    source = input_path.read_text()
    input_bytes = source.encode()

    oracle = _oracle_bytes(input_bytes)
    release = _release_bytes(input_bytes)
    difference = _first_byte_difference(oracle, release)
    assert difference is not None, (
        "Syntax is already byte-identical; inventory is empty"
    )

    minimal_witness = _minimal_contiguous_source_witness(
        source,
        oracle=oracle,
        release=release,
        difference=difference,
    )
    assert minimal_witness
    assert minimal_witness == source[: len(minimal_witness)]
    assert source.startswith(minimal_witness) or minimal_witness in source

    # Inventory seed: exactly the four observed categories, each a contiguous
    # witness drawn from the Syntax source.
    assert [category.name for category in SYNTAX_DIFF_CATEGORIES] == [
        "raw_top_level_html",
        "nested_list_close_ordering",
        "multi_definition_reference_resolution",
        "paragraph_block_separators",
    ]
    for category in SYNTAX_DIFF_CATEGORIES:
        assert category.source_witness
        assert category.source_witness in source, category.name
        assert category.owning_act in {
            "act1",
            "act2",
            "act3",
            "act4",
            "wrapper_rewrite",
        }

    # The recorded first difference and minimal witness stay available to Step 2
    # category repairs via this assertion surface (offset must be stable shape).
    assert difference.offset >= 0
    assert difference.oracle_slice != difference.actual_slice or len(oracle) != len(
        release
    )
    assert (
        _first_byte_difference(
            _oracle_bytes(minimal_witness.encode()),
            _release_bytes(minimal_witness.encode()),
        )
        is not None
    )


@pytest.mark.parametrize(
    "category",
    SYNTAX_DIFF_CATEGORIES,
    ids=[category.name for category in SYNTAX_DIFF_CATEGORIES],
)
def test_syntax_category_matches_fast_release_and_raw_oracle(
    category: SyntaxDiffCategory,
) -> None:
    """Each inventory category needs fast-IR, release, and strict oracle bytes.

    Production behavior must not change until every seeded category has this
    three-way assertion (plan Task 4 Step 1). Categories still red are repaired
    one at a time in Task 4 Step 2.
    """
    _assert_fast_release_raw_oracle(category.source_witness)


# Task 4 Step 2b: multi-definition / lazy-continuation reference rewrite.
_LAZY_CONTINUATION_EMPTY_REFS = (
    "I get 10 times more traffic from [Google] [1] than from\n"
    "    [Yahoo] [2] or [MSN] [3].\n"
)
_CODE_BLOCK_FOUR_SPACE_CONTROL = "para\n\n    [code] [1]\n"


def test_multi_definition_inventory_witness_matches_fast_release_and_raw_oracle() -> (
    None
):
    """Inventory multi-definition witness is byte-identical to local Markdown.pl."""
    _assert_fast_release_raw_oracle(SYNTAX_MULTI_DEFINITION_REFERENCE)


def test_lazy_continuation_rewrite_escapes_unresolved_refs_on_both_lines() -> None:
    """Four-space lazy paragraph continuations still escape unresolved refs.

    When no reference definitions are registered, both the first line and the
    indented continuation must escape brackets, matching ordinary-line handling.
    """
    rewritten = rewrite_task3_markdown(_LAZY_CONTINUATION_EMPTY_REFS)
    assert r"\[Google\] \[1\]" in rewritten
    assert r"\[Yahoo\] \[2\]" in rewritten
    assert r"\[MSN\] \[3\]" in rewritten
    # Continuation indent is preserved; only the labels are escaped.
    assert "\n    \\[Yahoo\\]" in rewritten


def test_code_block_four_space_lines_remain_opaque_to_reference_rewrite() -> None:
    """True code-block context (blank line then four spaces) stays opaque."""
    rewritten = rewrite_task3_markdown(_CODE_BLOCK_FOUR_SPACE_CONTROL)
    assert rewritten == _CODE_BLOCK_FOUR_SPACE_CONTROL
    assert r"\[code\]" not in rewritten
    assert "[code] [1]" in rewritten


def test_tab_indented_code_lines_remain_opaque_to_reference_rewrite() -> None:
    """Leading-tab code samples stay opaque (Markdown.pl alternate code indent)."""
    source = "See:\n\n\t[link text][a]\n\t[link text][A]\n"
    rewritten = rewrite_task3_markdown(source)
    assert rewritten == source
    assert r"\[link text\]" not in rewritten
    _assert_fast_release_raw_oracle(source)


def test_multi_parent_nested_siblings_match_fast_release_and_raw_oracle() -> None:
    """After closing one nest, a later parent's nested siblings stay siblings.

    Regression for nest-depth restore on SIB_OUTDENT: depth was clobbered to
    the list kind so the second parent's second child opened a deeper list.
    """
    _assert_fast_release_raw_oracle(
        "* a\n    * a1\n    * a2\n* b\n    * b1\n    * b2\n"
    )
