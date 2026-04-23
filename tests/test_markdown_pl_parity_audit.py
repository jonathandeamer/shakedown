"""Unit tests for scripts.markdown_pl_parity_audit."""

from pathlib import Path

import pytest

from scripts.markdown_pl_parity_audit import (
    FixtureAudit,
    audit_fixture,
    collect_audits,
    expected_path_for,
    first_byte_diff,
    normalize_contract,
    render_report,
)


def test_normalize_contract_matches_mdtest_whitespace_rules() -> None:
    text = "  <p>alpha</p>  \n\n\n  <p>beta</p>\n"

    assert normalize_contract(text) == "<p>alpha</p>\n\n<p>beta</p>"


def test_first_byte_diff_reports_value_change() -> None:
    assert first_byte_diff(b"abc", b"axc") == (1, 98, 120)


def test_first_byte_diff_reports_length_change() -> None:
    assert first_byte_diff(b"abc", b"ab") == (2, 99, None)


def test_first_byte_diff_returns_none_for_identical_bytes() -> None:
    assert first_byte_diff(b"abc", b"abc") is None


def test_expected_path_prefers_xhtml(tmp_path: Path) -> None:
    text_path = tmp_path / "Sample.text"
    xhtml_path = tmp_path / "Sample.xhtml"
    html_path = tmp_path / "Sample.html"
    text_path.write_text("input")
    xhtml_path.write_text("xhtml")
    html_path.write_text("html")

    assert expected_path_for(text_path) == xhtml_path


def test_expected_path_falls_back_to_html(tmp_path: Path) -> None:
    text_path = tmp_path / "Sample.text"
    html_path = tmp_path / "Sample.html"
    text_path.write_text("input")
    html_path.write_text("html")

    assert expected_path_for(text_path) == html_path


def test_expected_path_raises_when_no_expected_file(tmp_path: Path) -> None:
    text_path = tmp_path / "Sample.text"
    text_path.write_text("input")

    with pytest.raises(FileNotFoundError):
        expected_path_for(text_path)


def test_render_report_summarizes_raw_and_normalized_mismatches(
    tmp_path: Path,
) -> None:
    audit = FixtureAudit(
        name="Code Blocks",
        input_path=tmp_path / "Code Blocks.text",
        expected_path=tmp_path / "Code Blocks.xhtml",
        raw_equal=False,
        normalized_equal=True,
        expected_bytes=312,
        oracle_bytes=310,
        first_diff_index=219,
        expected_byte=32,
        oracle_byte=10,
        diff="--- expected\n+++ oracle\n",
    )

    report = render_report(
        [audit], tmp_path, Path("/home/ec2-user/markdown/Markdown.pl")
    )

    assert "- **Fixture count:** 1" in report
    assert "- **Raw-byte mismatches:** 1" in report
    assert "- **Normalized-contract mismatches:** 0" in report
    assert "| Code Blocks | fail | pass | 312 | 310 | 219 (32 -> 10) |" in report
    assert "## Raw Mismatch Diffs" in report


def test_collect_audits_raises_when_fixtures_dir_is_missing(tmp_path: Path) -> None:
    missing_dir = tmp_path / "missing"

    with pytest.raises(NotADirectoryError):
        collect_audits(missing_dir, Path("/home/ec2-user/markdown/Markdown.pl"))


def test_collect_audits_raises_when_fixtures_dir_is_empty(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        collect_audits(empty_dir, Path("/home/ec2-user/markdown/Markdown.pl"))


def test_audit_fixture_keeps_invalid_bytes_unequal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text_path = tmp_path / "Sample.text"
    expected_path = tmp_path / "Sample.xhtml"
    text_path.write_text("input")
    expected_path.write_bytes(b"\xff")

    monkeypatch.setattr(
        "scripts.markdown_pl_parity_audit.run_markdown_pl",
        lambda markdown_pl, input_bytes: b"\xfe",
    )

    audit = audit_fixture(text_path, Path("/home/ec2-user/markdown/Markdown.pl"))

    assert audit.raw_equal is False
    assert audit.normalized_equal is False


def test_audit_fixture_uses_hex_fallback_for_non_text_safe_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text_path = tmp_path / "Sample.text"
    expected_path = tmp_path / "Sample.xhtml"
    text_path.write_text("input")
    expected_path.write_bytes(b"\xff")

    monkeypatch.setattr(
        "scripts.markdown_pl_parity_audit.run_markdown_pl",
        lambda markdown_pl, input_bytes: b"\xfe",
    )

    audit = audit_fixture(text_path, Path("/home/ec2-user/markdown/Markdown.pl"))

    assert audit.diff == (
        f"--- {expected_path}\n"
        "+++ local Markdown.pl\n"
        "@@ byte-diff @@\n"
        "- expected bytes: ff\n"
        "+ oracle bytes:   fe\n"
    )
