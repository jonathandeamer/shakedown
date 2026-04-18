# tests/test_run_loop.py
import importlib.util
import subprocess
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest  # noqa: F401


def _load_run_loop():
    script = Path(__file__).parent.parent / "run-loop"
    loader = SourceFileLoader("run_loop", str(script))
    spec = importlib.util.spec_from_loader("run_loop", loader)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_run_loop()
expand_refs = _mod.expand_refs
is_limit_message = _mod.is_limit_message
load_state = _mod.load_state
save_state = _mod.save_state
derive_complete_marker = _mod.derive_complete_marker
parse_meminfo = _mod.parse_meminfo
has_swap = _mod.has_swap
evaluate_claude_preflight = _mod.evaluate_claude_preflight
format_preflight_error = _mod.format_preflight_error
format_resource_failure_error = _mod.format_resource_failure_error
classify_claude_resource_failure = _mod.classify_claude_resource_failure


class TestExpandRefs:
    def test_plain_line_unchanged(self, tmp_path):
        assert expand_refs("hello world", tmp_path) == "hello world"

    def test_ref_expanded(self, tmp_path):
        (tmp_path / "foo.txt").write_text("bar content")
        result = expand_refs("@foo.txt", tmp_path)
        assert result == "=== foo.txt ===\nbar content\n=== end foo.txt ==="

    def test_missing_file_fallback(self, tmp_path):
        result = expand_refs("@missing.txt", tmp_path)
        assert "(file not found: missing.txt)" in result
        assert "=== missing.txt ===" in result

    def test_directory_ref_lists_entries(self, tmp_path):
        d = tmp_path / "expdir"
        d.mkdir()
        (d / "a.md").write_text("x")
        (d / "sub").mkdir()
        result = expand_refs("@expdir", tmp_path)
        assert "=== expdir ===" in result
        assert "a.md" in result
        assert "sub/" in result

    def test_empty_directory_ref(self, tmp_path):
        (tmp_path / "empty").mkdir()
        result = expand_refs("@empty", tmp_path)
        assert "(empty directory)" in result

    def test_mixed_lines(self, tmp_path):
        (tmp_path / "data.sql").write_text("SELECT 1")
        text = "preamble\n@data.sql\npostamble"
        result = expand_refs(text, tmp_path)
        assert "preamble" in result
        assert "=== data.sql ===" in result
        assert "SELECT 1" in result
        assert "postamble" in result


class TestLinuxFactParsing:
    def test_parse_meminfo_reads_memavailable_kib(self):
        text = (
            "MemTotal:        1982308 kB\n"
            "MemFree:          120000 kB\n"
            "MemAvailable:     695296 kB\n"
        )
        facts = parse_meminfo(text)
        assert facts["mem_available_kib"] == 695296

    def test_parse_meminfo_missing_memavailable_returns_none(self):
        facts = parse_meminfo("MemTotal: 1 kB\n")
        assert facts["mem_available_kib"] is None

    def test_has_swap_false_for_header_only(self):
        text = "Filename\t\t\tType\t\tSize\t\tUsed\t\tPriority\n"
        assert has_swap(text) is False

    def test_has_swap_true_when_swap_entry_present(self):
        text = (
            "Filename\t\t\tType\t\tSize\t\tUsed\t\tPriority\n"
            "/swapfile                               file\t\t1048572\t\t0\t\t-2\n"
        )
        assert has_swap(text) is True


class TestClaudePreflight:
    def test_fails_when_available_memory_is_below_threshold(self):
        decision = evaluate_claude_preflight(
            mem_available_kib=650 * 1024,
            swap_enabled=False,
            tmp_total_bytes=1_000_000_000,
            tmp_used_bytes=100_000_000,
            claude_tmp_bytes=0,
        )
        assert decision["ok"] is False
        assert "low_mem" in decision["reasons"]

    def test_fails_when_memory_is_marginal_and_swap_is_missing(self):
        decision = evaluate_claude_preflight(
            mem_available_kib=900 * 1024,
            swap_enabled=False,
            tmp_total_bytes=1_000_000_000,
            tmp_used_bytes=100_000_000,
            claude_tmp_bytes=0,
        )
        assert decision["ok"] is False
        assert "no_swap" in decision["reasons"]

    def test_fails_when_tmp_pressure_is_driven_by_claude_temp_data(self):
        decision = evaluate_claude_preflight(
            mem_available_kib=900 * 1024,
            swap_enabled=False,
            tmp_total_bytes=1_000_000_000,
            tmp_used_bytes=970_000_000,
            claude_tmp_bytes=930_000_000,
        )
        assert decision["ok"] is False
        assert "tmp_pressure" in decision["reasons"]

    def test_passes_when_memory_and_swap_are_healthy(self):
        decision = evaluate_claude_preflight(
            mem_available_kib=1_600 * 1024,
            swap_enabled=True,
            tmp_total_bytes=1_000_000_000,
            tmp_used_bytes=100_000_000,
            claude_tmp_bytes=0,
        )
        assert decision["ok"] is True
        assert decision["reasons"] == []


class TestClaudeResourceFailure:
    def test_format_preflight_error_mentions_memory_swap_and_tmp(self):
        decision = {
            "ok": False,
            "reasons": ["low_mem", "no_swap", "tmp_pressure"],
            "mem_available_kib": 695296,
            "swap_enabled": False,
            "tmp_used_bytes": 957_000_000,
            "tmp_total_bytes": 1_000_000_000,
            "claude_tmp_bytes": 932_000_000,
        }
        message = format_preflight_error(decision)
        assert "likely memory pressure" in message
        assert "MemAvailable" in message
        assert "swap: none" in message
        assert "/tmp/claude-" in message

    def test_classify_claude_resource_failure_for_sigkill(self):
        result = classify_claude_resource_failure(
            -9, "Out of memory: Killed process 123 (claude)"
        )
        assert result["is_resource_failure"] is True
        assert result["kind"] == "signal"

    def test_classify_claude_resource_failure_does_not_treat_bare_sigkill_as_oom(
        self,
    ):
        result = classify_claude_resource_failure(-9, "")
        assert result["is_resource_failure"] is False
        assert result["kind"] is None

    def test_classify_claude_resource_failure_does_not_treat_sigabrt_as_oom(
        self,
    ):
        result = classify_claude_resource_failure(-6, "")
        assert result["is_resource_failure"] is False
        assert result["kind"] is None

    def test_classify_claude_resource_failure_for_oom_text(self):
        result = classify_claude_resource_failure(1, "OOM-kill triggered by claude")
        assert result["is_resource_failure"] is True
        assert result["kind"] == "oom_text"

    def test_classify_claude_resource_failure_ignores_normal_exit(self):
        result = classify_claude_resource_failure(0, "All done")
        assert result["is_resource_failure"] is False

    def test_classify_claude_resource_failure_does_not_match_room_or_zoom(self):
        for text in ["room", "zoom", "classroom", "boomer"]:
            result = classify_claude_resource_failure(1, text)
            assert result["is_resource_failure"] is False


class TestClaudeHostFacts:
    def test_sum_claude_tmp_bytes_counts_matching_directories(self, tmp_path):
        claude_dir = tmp_path / "claude-1000"
        other_dir = tmp_path / "not-claude"
        claude_dir.mkdir()
        other_dir.mkdir()
        (claude_dir / "a.bin").write_bytes(b"x" * 10)
        (claude_dir / "b.bin").write_bytes(b"x" * 15)
        (other_dir / "c.bin").write_bytes(b"x" * 99)

        total = _mod.sum_claude_tmp_bytes(tmp_path)
        assert total == 25

    def test_get_tmp_usage_bytes_uses_statvfs(self, monkeypatch):
        class _Stat:
            f_frsize = 4
            f_blocks = 100
            f_bavail = 25

        monkeypatch.setattr(_mod.os, "statvfs", lambda path: _Stat())
        total_bytes, used_bytes = _mod.get_tmp_usage_bytes(Path("/tmp"))
        assert total_bytes == 400
        assert used_bytes == 300

    def test_sum_claude_tmp_bytes_ignores_symlinked_directories(self, tmp_path):
        real_dir = tmp_path / "claude-real"
        real_dir.mkdir()
        (real_dir / "payload.bin").write_bytes(b"x" * 12)

        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.bin").write_bytes(b"y" * 50)

        symlinked_dir = tmp_path / "claude-link"
        symlinked_dir.symlink_to(outside, target_is_directory=True)

        total = _mod.sum_claude_tmp_bytes(tmp_path)
        assert total == 12

    def test_sum_claude_tmp_bytes_ignores_symlinked_files(self, tmp_path):
        claude_dir = tmp_path / "claude-1000"
        claude_dir.mkdir()
        (claude_dir / "payload.bin").write_bytes(b"x" * 7)
        (claude_dir / "payload-link.bin").symlink_to(tmp_path / "nowhere.bin")

        total = _mod.sum_claude_tmp_bytes(tmp_path)
        assert total == 7


class TestIsLimitMessage:
    def test_codex_limit(self):
        msg = "ERROR: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro)"
        assert is_limit_message(msg, "codex")

    def test_claude_limit(self):
        msg = "-You've hit your limit · resets 4pm (UTC)"
        assert is_limit_message(msg, "claude")

    def test_normal_output_not_limit_codex(self):
        assert not is_limit_message("Task 5 complete. Tests passing.", "codex")

    def test_normal_output_not_limit_claude(self):
        assert not is_limit_message("All done!", "claude")

    def test_codex_message_not_matched_by_claude_pattern(self):
        # Should NOT match claude's "You've hit your limit"
        assert not is_limit_message("You've hit your usage limit", "claude")

    def test_claude_message_not_matched_by_codex_pattern(self):
        assert not is_limit_message("You've hit your limit", "codex")

    def test_unknown_backend_returns_false(self):
        assert not is_limit_message("You've hit your limit", "gpt4")


class TestStateIO:
    def test_missing_file_returns_defaults(self, tmp_path):
        state = load_state(tmp_path / "nonexistent.json")
        assert state["last_used"] == "codex"
        assert state["both_limited"] is False

    def test_corrupt_file_returns_defaults(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text("not valid json {{")
        state = load_state(p)
        assert state["last_used"] == "codex"
        assert state["both_limited"] is False

    def test_roundtrip(self, tmp_path):
        p = tmp_path / "state.json"
        original = {"last_used": "claude", "both_limited": True}
        save_state(p, original)
        loaded = load_state(p)
        assert loaded == original

    def test_save_creates_parent_dirs(self, tmp_path):
        p = tmp_path / "a" / "b" / "state.json"
        save_state(p, {"last_used": "codex", "both_limited": False})
        assert p.exists()


class TestRepoProgress:
    def test_snapshot_counts_tracked_and_untracked_files(self, tmp_path):
        tracked = tmp_path / "tracked.txt"
        tracked.write_text("v1")
        subprocess.run(
            ["git", "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "add", "tracked.txt"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )

        tracked.write_text("v2")
        (tmp_path / "new.txt").write_text("new")

        snapshot = _mod.collect_repo_snapshot(tmp_path)

        assert "tracked.txt" in snapshot["tracked_paths"]
        assert "new.txt" in snapshot["untracked_paths"]

    def test_has_useful_repo_progress_ignores_run_loop_state_file(self):
        before = {
            "tracked_paths": (),
            "untracked_paths": (),
        }
        after = {
            "tracked_paths": (".agent/run-loop-state.json",),
            "untracked_paths": (),
        }

        assert _mod.has_useful_repo_progress(before, after) is False

    def test_has_useful_repo_progress_counts_untracked_repo_file(self):
        before = {
            "tracked_paths": (),
            "untracked_paths": (),
        }
        after = {
            "tracked_paths": (),
            "untracked_paths": ("notes.txt",),
        }

        assert _mod.has_useful_repo_progress(before, after) is True


class TestMainLoop:
    def test_both_limited_claude_iteration_switches_next_backend_to_codex(
        self, monkeypatch
    ):
        saved_states = []
        complete_checks = iter([False, True])

        class _Marker:
            def exists(self) -> bool:
                return next(complete_checks)

        class _PromptFile:
            def read_text(self) -> str:
                return "prompt"

        monkeypatch.setattr(_mod, "COMPLETE_MARKER", _Marker())
        monkeypatch.setattr(_mod, "PROMPT_FILE", _PromptFile())
        monkeypatch.setattr(
            _mod,
            "load_state",
            lambda path: {"last_used": "claude", "both_limited": True},
        )
        monkeypatch.setattr(
            _mod,
            "gather_claude_host_facts",
            lambda: {
                "mem_available_kib": 1_500 * 1024,
                "swap_enabled": True,
                "tmp_total_bytes": 1_000_000_000,
                "tmp_used_bytes": 100_000_000,
                "claude_tmp_bytes": 0,
            },
        )
        monkeypatch.setattr(
            _mod,
            "run_backend",
            lambda backend, prompt: (0, "-You've hit your limit · resets 4pm (UTC)"),
        )
        monkeypatch.setattr(_mod, "expand_refs", lambda text, repo: text)
        monkeypatch.setattr(_mod.time, "sleep", lambda seconds: None)
        monkeypatch.setattr(
            _mod,
            "save_state",
            lambda path, state: saved_states.append(state.copy()),
        )

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=[])

        assert excinfo.value.code == 0
        assert saved_states == [{"last_used": "codex", "both_limited": False}]

    def test_claude_preflight_exits_before_launch_on_unsafe_memory_pressure(
        self, monkeypatch, capsys
    ):
        launched = []

        class _Marker:
            def exists(self) -> bool:
                return False

        class _PromptFile:
            def read_text(self) -> str:
                return "prompt"

        monkeypatch.setattr(_mod, "COMPLETE_MARKER", _Marker())
        monkeypatch.setattr(_mod, "PROMPT_FILE", _PromptFile())
        monkeypatch.setattr(
            _mod,
            "load_state",
            lambda path: {"last_used": "claude", "both_limited": False},
        )
        monkeypatch.setattr(
            _mod,
            "gather_claude_host_facts",
            lambda: {
                "mem_available_kib": 650 * 1024,
                "swap_enabled": False,
                "tmp_total_bytes": 1_000_000_000,
                "tmp_used_bytes": 970_000_000,
                "claude_tmp_bytes": 930_000_000,
            },
        )
        monkeypatch.setattr(
            _mod,
            "run_backend",
            lambda backend, prompt: launched.append((backend, prompt)),
        )
        monkeypatch.setattr(_mod, "expand_refs", lambda text, repo: text)

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=[])

        captured = capsys.readouterr()
        assert excinfo.value.code == 1
        assert launched == []
        assert "refusing to launch Claude" in captured.err
        assert "--- run-loop: starting claude iteration ---" not in captured.out
        assert captured.out == ""


class TestClaudeFailFast:
    def test_main_exits_when_claude_process_dies_from_resource_failure(
        self, monkeypatch, capsys
    ):
        complete_checks = iter([False])

        class _Marker:
            def exists(self) -> bool:
                return next(complete_checks)

        class _PromptFile:
            def read_text(self) -> str:
                return "prompt"

        monkeypatch.setattr(_mod, "PROMPT_FILE", _PromptFile())
        monkeypatch.setattr(_mod, "COMPLETE_MARKER", _Marker())
        monkeypatch.setattr(
            _mod,
            "load_state",
            lambda path: {"last_used": "claude", "both_limited": False},
        )
        monkeypatch.setattr(_mod, "expand_refs", lambda text, repo: text)
        monkeypatch.setattr(
            _mod,
            "gather_claude_host_facts",
            lambda: {
                "mem_available_kib": 1_500 * 1024,
                "swap_enabled": True,
                "tmp_total_bytes": 1_000_000_000,
                "tmp_used_bytes": 100_000_000,
                "claude_tmp_bytes": 0,
            },
        )
        monkeypatch.setattr(
            _mod,
            "run_backend",
            lambda backend, prompt: (-9, "Out of memory: Killed process 123 (claude)"),
        )

        with pytest.raises(SystemExit) as excinfo:
            _mod.main(argv=[])

        captured = capsys.readouterr()
        assert excinfo.value.code == 1
        assert "terminated due to likely memory pressure" in captured.err
        assert "--- run-loop: starting claude iteration ---" in captured.out


class TestDeriveCompleteMarker:
    def test_cm_prompt(self, tmp_path):
        result = derive_complete_marker(Path("docs/prompt-cm.md"), tmp_path)
        assert result == tmp_path / ".agent" / "complete-cm.md"

    def test_spl_feasibility_prompt(self, tmp_path):
        result = derive_complete_marker(
            Path("docs/prompt-spl-feasibility.md"), tmp_path
        )
        assert result == tmp_path / ".agent" / "complete-spl-feasibility.md"

    def test_non_prompt_prefix_stem(self, tmp_path):
        result = derive_complete_marker(Path("docs/foo.md"), tmp_path)
        assert result == tmp_path / ".agent" / "complete-foo.md"

    def test_absolute_path(self, tmp_path):
        result = derive_complete_marker(Path("/abs/path/prompt-bar.md"), tmp_path)
        assert result == tmp_path / ".agent" / "complete-bar.md"
