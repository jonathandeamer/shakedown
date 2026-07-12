from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
SHAKEDOWN = REPO / "shakedown"
MARKDOWN_PL = Path.home() / "markdown" / "Markdown.pl"
LIST_FIXTURES = REPO / "tests" / "fixtures" / "architecture_spikes" / "lists"
NESTED_BLOCK_FIXTURES = (
    REPO / "tests" / "fixtures" / "architecture_spikes" / "nested_blocks"
)
NESTED_BLOCK_BYTE_CASES = [
    (
        "list_quote_sibling",
        b"* alpha\n\n  > bravo\n* charlie\n",
        b"<ul>\n<li><p>alpha</p>\n\n<blockquote>\n  <p>bravo</p>\n"
        b"</blockquote></li>\n<li>charlie</li>\n</ul>\n",
    ),
    (
        "quote_list_then_paragraph",
        b"> * alpha\n> * bravo\n>\n> charlie\n",
        b"<blockquote>\n  <ul>\n<li>alpha</li>\n<li>bravo</li>\n</ul>\n\n"
        b"<p>charlie</p>\n</blockquote>\n",
    ),
    (
        "loose_list_quote",
        b"* alpha\n\n  > bravo\n\n* charlie\n",
        b"<ul>\n<li><p>alpha</p>\n\n<blockquote>\n  <p>bravo</p>\n"
        b"</blockquote></li>\n<li><p>charlie</p></li>\n</ul>\n",
    ),
    (
        "closes_to_text",
        b"* alpha\n\n  > bravo\n\noutside\n",
        b"<ul>\n<li><p>alpha</p>\n\n<blockquote>\n  <p>bravo</p>\n"
        b"</blockquote></li>\n</ul>\n\n<p>outside</p>\n",
    ),
]


def _first_diff(a: bytes, b: bytes) -> int | None:
    for idx, (left, right) in enumerate(zip(a, b, strict=False)):
        if left != right:
            return idx
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def _run(argv: list[str], input_bytes: bytes) -> bytes:
    result = subprocess.run(
        argv,
        input=input_bytes,
        capture_output=True,
        cwd=REPO,
        check=True,
    )
    return result.stdout


def _list_cases() -> list[Path]:
    return sorted(LIST_FIXTURES.glob("*.text"))


def _nested_block_cases() -> list[Path]:
    return sorted(NESTED_BLOCK_FIXTURES.glob("*.text"))


@pytest.mark.parametrize("fixture", _list_cases(), ids=lambda path: path.stem)
def test_list_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
    input_bytes = fixture.read_bytes()
    actual = _run([str(SHAKEDOWN)], input_bytes)
    expected = _run(["perl", str(MARKDOWN_PL)], input_bytes)

    assert actual == expected, (
        f"Output mismatch for {fixture.name}; first diff: "
        f"{_first_diff(actual, expected)}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual\n{actual.decode(errors='replace')}"
    )


@pytest.mark.parametrize("fixture", _nested_block_cases(), ids=lambda path: path.stem)
def test_nested_block_architecture_spike_matches_markdown_pl(fixture: Path) -> None:
    input_bytes = fixture.read_bytes()
    actual = _run([str(SHAKEDOWN)], input_bytes)
    expected = _run(["perl", str(MARKDOWN_PL)], input_bytes)

    assert actual == expected, (
        f"Output mismatch for {fixture.name}; first diff: "
        f"{_first_diff(actual, expected)}\n"
        f"--- expected\n{expected.decode(errors='replace')}\n"
        f"+++ actual\n{actual.decode(errors='replace')}"
    )


@pytest.mark.parametrize(
    ("input_bytes", "expected"),
    [(input_bytes, expected) for _, input_bytes, expected in NESTED_BLOCK_BYTE_CASES],
    ids=[stem for stem, _, _ in NESTED_BLOCK_BYTE_CASES],
)
def test_nested_block_architecture_spike_emits_expected_bytes(
    input_bytes: bytes,
    expected: bytes,
) -> None:
    assert _run([str(SHAKEDOWN)], input_bytes) == expected
