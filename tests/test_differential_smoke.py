"""Unit tests for scripts.differential_smoke."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.differential_smoke import (
    CaseStatus,
    RunOutcome,
    bound_stderr,
    collect_fixtures,
    first_diff,
    main,
    parse_args,
    render_json,
    render_markdown,
    resolve_require_name,
    run_case,
    run_with_timeout,
)

ORACLE = Path.home() / "markdown" / "Markdown.pl"


def test_first_diff_reports_index_on_mismatch() -> None:
    assert first_diff(b"abc", b"axc") == 1


def test_first_diff_reports_length_change() -> None:
    assert first_diff(b"abc", b"ab") == 2


def test_first_diff_returns_none_for_identical_bytes() -> None:
    assert first_diff(b"abc", b"abc") is None


def test_bound_stderr_truncates_long_output() -> None:
    raw = ("x" * 1000).encode()
    result = bound_stderr(raw)
    assert result.endswith("...(truncated)")
    assert len(result) < len(raw)


def test_bound_stderr_passes_through_short_output() -> None:
    assert bound_stderr(b"boom") == "boom"


def test_collect_fixtures_globs_text_files_sorted(tmp_path: Path) -> None:
    (tmp_path / "b.text").write_text("b")
    (tmp_path / "a.text").write_text("a")
    (tmp_path / "ignore.xhtml").write_text("x")

    result = collect_fixtures(tmp_path)

    assert [p.name for p in result] == ["a.text", "b.text"]


def test_resolve_require_name_accepts_bare_name(tmp_path: Path) -> None:
    (tmp_path / "Amps and angle encoding.text").write_text("x")

    resolved = resolve_require_name(tmp_path, "Amps and angle encoding")

    assert resolved == tmp_path / "Amps and angle encoding.text"


def test_resolve_require_name_raises_for_missing_fixture(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        resolve_require_name(tmp_path, "Nonexistent")


def _fake_completed(returncode: int, stdout: bytes, stderr: bytes) -> object:
    class _Result:
        def __init__(self) -> None:
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    return _Result()


def test_run_with_timeout_reports_normal_completion(monkeypatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: _fake_completed(0, b"hello", b""),
    )

    outcome = run_with_timeout(["irrelevant"], b"in", 5.0)

    assert outcome == RunOutcome(
        returncode=0,
        stdout=b"hello",
        stderr_excerpt="",
        elapsed_seconds=outcome.elapsed_seconds,
        timed_out=False,
    )
    assert not outcome.timed_out


def test_run_with_timeout_reports_timeout(monkeypatch) -> None:
    def _raise(*args: object, **kwargs: object) -> object:
        raise subprocess.TimeoutExpired(
            cmd="x", timeout=1.0, output=b"", stderr=b"stuck"
        )

    monkeypatch.setattr(subprocess, "run", _raise)

    outcome = run_with_timeout(["irrelevant"], b"in", 1.0)

    assert outcome.timed_out
    assert outcome.returncode is None
    assert outcome.stderr_excerpt == "stuck"


def test_run_case_classifies_byte_identical(monkeypatch, tmp_path: Path) -> None:
    fixture = tmp_path / "sample.text"
    fixture.write_text("hello")

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        return _fake_completed(0, b"same", b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    result = run_case(fixture, Path("/bin/shakedown"), ORACLE, 5.0)

    assert result.status == CaseStatus.BYTE_IDENTICAL
    assert result.first_diff_index is None
    assert result.name == "sample"


def test_run_case_classifies_mismatch(monkeypatch, tmp_path: Path) -> None:
    fixture = tmp_path / "sample.text"
    fixture.write_text("hello")

    calls: list[list[str]] = []

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        calls.append(argv)
        if "perl" in argv:
            return _fake_completed(0, b"oracle", b"")
        return _fake_completed(0, b"shakedown", b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    result = run_case(fixture, Path("/bin/shakedown"), ORACLE, 5.0)

    assert result.status == CaseStatus.MISMATCH
    assert result.first_diff_index == 0


def test_run_case_classifies_shakedown_crash(monkeypatch, tmp_path: Path) -> None:
    fixture = tmp_path / "sample.text"
    fixture.write_text("hello")

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        if "perl" in argv:
            return _fake_completed(0, b"oracle", b"")
        return _fake_completed(1, b"", b"boom")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    result = run_case(fixture, Path("/bin/shakedown"), ORACLE, 5.0)

    assert result.status == CaseStatus.SHAKEDOWN_CRASH
    assert result.shakedown_stderr == "boom"
    assert result.first_diff_index is None


def test_run_case_classifies_oracle_crash(monkeypatch, tmp_path: Path) -> None:
    fixture = tmp_path / "sample.text"
    fixture.write_text("hello")

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        if "perl" in argv:
            return _fake_completed(1, b"", b"oracle boom")
        return _fake_completed(0, b"shakedown", b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    result = run_case(fixture, Path("/bin/shakedown"), ORACLE, 5.0)

    assert result.status == CaseStatus.ORACLE_CRASH


def test_run_case_classifies_shakedown_timeout(monkeypatch, tmp_path: Path) -> None:
    fixture = tmp_path / "sample.text"
    fixture.write_text("hello")

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        if "perl" in argv:
            return _fake_completed(0, b"oracle", b"")
        raise subprocess.TimeoutExpired(cmd="x", timeout=timeout)

    monkeypatch.setattr(subprocess, "run", _fake_run)

    result = run_case(fixture, Path("/bin/shakedown"), ORACLE, 5.0)

    assert result.status == CaseStatus.SHAKEDOWN_TIMEOUT


def test_render_markdown_includes_summary_and_non_identical_section(
    monkeypatch, tmp_path: Path
) -> None:
    fixture = tmp_path / "sample.text"
    fixture.write_text("hello")

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        if "perl" in argv:
            return _fake_completed(0, b"oracle", b"")
        return _fake_completed(0, b"shakedown", b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    result = run_case(fixture, Path("/bin/shakedown"), ORACLE, 5.0)

    report = render_markdown([result])

    assert "sample" in report
    assert "summary: 0/1 byte-identical" in report
    assert "## Non-identical cases" in report


def test_render_json_round_trips_status_value(monkeypatch, tmp_path: Path) -> None:
    fixture = tmp_path / "sample.text"
    fixture.write_text("hello")

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        return _fake_completed(0, b"same", b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    result = run_case(fixture, Path("/bin/shakedown"), ORACLE, 5.0)

    payload = render_json([result])

    assert '"byte_identical"' in payload
    assert '"sample"' in payload


def test_main_fails_on_missing_fixtures_dir(tmp_path: Path) -> None:
    missing = tmp_path / "nope"

    rc = main(
        [
            "--fixtures-dir",
            str(missing),
            "--markdown-pl",
            str(ORACLE),
            "--shakedown",
            "/bin/cat",
        ]
    )

    assert rc == 2


def test_main_fails_on_missing_oracle(tmp_path: Path) -> None:
    (tmp_path / "sample.text").write_text("hello")

    rc = main(
        [
            "--fixtures-dir",
            str(tmp_path),
            "--markdown-pl",
            str(tmp_path / "no-such-oracle.pl"),
            "--shakedown",
            "/bin/cat",
        ]
    )

    assert rc == 2


def test_main_fails_on_missing_require_fixture(tmp_path: Path) -> None:
    (tmp_path / "sample.text").write_text("hello")

    rc = main(
        [
            "--fixtures-dir",
            str(tmp_path),
            "--markdown-pl",
            str(ORACLE),
            "--shakedown",
            "/bin/cat",
            "--require",
            "Nonexistent Fixture",
        ]
    )

    assert rc == 2


def test_main_observational_mode_succeeds_despite_mismatch(
    monkeypatch, tmp_path: Path
) -> None:
    (tmp_path / "sample.text").write_text("hello")
    (tmp_path / "shakedown_stub").write_text("#!/bin/sh\necho oracle\n")
    shakedown_stub = tmp_path / "shakedown_stub"
    shakedown_stub.chmod(0o755)

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        if "perl" in argv:
            return _fake_completed(0, b"oracle-output", b"")
        return _fake_completed(0, b"shakedown-output", b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    rc = main(
        [
            "--fixtures-dir",
            str(tmp_path),
            "--markdown-pl",
            str(ORACLE),
            "--shakedown",
            str(shakedown_stub),
        ]
    )

    assert rc == 0


def test_main_require_mode_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "sample.text").write_text("hello")
    shakedown_stub = tmp_path / "shakedown_stub"
    shakedown_stub.write_text("#!/bin/sh\necho stub\n")
    shakedown_stub.chmod(0o755)

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        if "perl" in argv:
            return _fake_completed(0, b"oracle-output", b"")
        return _fake_completed(0, b"shakedown-output", b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    rc = main(
        [
            "--fixtures-dir",
            str(tmp_path),
            "--markdown-pl",
            str(ORACLE),
            "--shakedown",
            str(shakedown_stub),
            "--require",
            "sample",
        ]
    )

    assert rc == 1


def test_main_writes_json_output(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "sample.text").write_text("hello")
    shakedown_stub = tmp_path / "shakedown_stub"
    shakedown_stub.write_text("#!/bin/sh\necho stub\n")
    shakedown_stub.chmod(0o755)
    json_path = tmp_path / "out.json"
    md_path = tmp_path / "out.md"

    def _fake_run(
        argv: list[str], input: bytes, timeout: float, capture_output: bool, check: bool
    ) -> object:
        return _fake_completed(0, b"same", b"")

    monkeypatch.setattr(subprocess, "run", _fake_run)

    rc = main(
        [
            "--fixtures-dir",
            str(tmp_path),
            "--markdown-pl",
            str(ORACLE),
            "--shakedown",
            str(shakedown_stub),
            "--json",
            str(json_path),
            "--output",
            str(md_path),
        ]
    )

    assert rc == 0
    assert json_path.exists()
    assert md_path.exists()
    assert "sample" in json_path.read_text()
    assert "sample" in md_path.read_text()


def test_parse_args_supports_repeated_require() -> None:
    args = parse_args(["--require", "one", "--require", "two"])

    assert args.require == ["one", "two"]


@pytest.mark.integration
def test_differential_smoke_integration_against_real_fixtures() -> None:
    fixtures_dir = Path.home() / "mdtest" / "Markdown.mdtest"
    shakedown = Path(__file__).parent.parent / "shakedown"
    if not ORACLE.exists() or not fixtures_dir.is_dir() or not shakedown.exists():
        pytest.skip("oracle, fixtures, or shakedown binary not available locally")

    rc = main(
        [
            "--fixtures-dir",
            str(fixtures_dir),
            "--markdown-pl",
            str(ORACLE),
            "--shakedown",
            str(shakedown),
            "--require",
            "Amps and angle encoding",
        ]
    )

    assert rc == 0
