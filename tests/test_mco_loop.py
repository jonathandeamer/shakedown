from __future__ import annotations

import io
import json
import os
import signal
import sys
from pathlib import Path

import pytest

from scripts import mco_loop
from scripts.mco_loop import (
    ActionKind,
    Executor,
    InvocationResult,
    NextAction,
    RoadmapRow,
)

FOR_EACH_REF_HEADS = (
    "for-each-ref",
    "--format=%(refname:short) %(objectname)",
    "refs/heads",
)


def _row(
    identifier: str,
    status: str,
    plan_path: Path | None = None,
    description: str = "A plan",
) -> RoadmapRow:
    return RoadmapRow(identifier, plan_path, description, status)


def test_failed_planner_action_remains_planner_action() -> None:
    action = NextAction(ActionKind.PLAN, "amend blocker", None, None, ())

    assert (
        mco_loop.apply_failure_action(
            action, {"last_failure": {"kind": "backend_failure"}}
        )
        == action
    )


def test_failed_implementation_action_becomes_fix_action() -> None:
    action = NextAction(ActionKind.IMPLEMENT, "execute step", None, "step", ())

    recovered = mco_loop.apply_failure_action(
        action, {"last_failure": {"kind": "no_progress"}}
    )

    assert recovered.kind is ActionKind.FIX
    assert recovered.step == "step"


def test_load_branch_dispositions_accepts_terminal_entries(tmp_path: Path) -> None:
    ledger = tmp_path / "branch-dispositions.toml"
    ledger.write_text(
        """
[branches."topic"]
head = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
disposition = "preserve"
reason = "Keep historical work."
"""
    )

    dispositions = mco_loop.load_branch_dispositions(ledger)

    assert dispositions == {
        "topic": mco_loop.BranchDisposition(
            "topic",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "preserve",
            "Keep historical work.",
        )
    }


def test_load_branch_dispositions_rejects_invalid_disposition(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "branch-dispositions.toml"
    ledger.write_text(
        """
[branches."topic"]
head = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
disposition = "pending"
reason = "Not allowed."
"""
    )

    with pytest.raises(ValueError, match="disposition"):
        mco_loop.load_branch_dispositions(ledger)


def test_load_branch_dispositions_rejects_unknown_keys(tmp_path: Path) -> None:
    ledger = tmp_path / "branch-dispositions.toml"
    ledger.write_text(
        """
[branches."topic"]
head = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
disposition = "preserve"
reason = "Keep historical work."
extra = "unexpected"
"""
    )

    with pytest.raises(ValueError, match="unknown keys"):
        mco_loop.load_branch_dispositions(ledger)


def test_load_branch_dispositions_rejects_non_hex_head(tmp_path: Path) -> None:
    ledger = tmp_path / "branch-dispositions.toml"
    ledger.write_text(
        """
[branches."topic"]
head = "not-a-40-hex-head"
disposition = "preserve"
reason = "Keep historical work."
"""
    )

    with pytest.raises(ValueError, match="head"):
        mco_loop.load_branch_dispositions(ledger)


def test_branch_inventory_returns_empty_when_no_candidates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: {
            FOR_EACH_REF_HEADS: "",
        }.get(tuple(args), ""),
    )

    assert mco_loop.branch_inventory_issues(tmp_path, {}) == ()


def test_branch_inventory_skips_merged_branch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    branch_head = "topic aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: {
            FOR_EACH_REF_HEADS: branch_head,
            ("merge-base", "--is-ancestor", "topic", "main"): "merged\n",
        }.get(tuple(args), ""),
    )

    assert mco_loop.branch_inventory_issues(tmp_path, {}) == ()


def test_branch_inventory_reports_unledgered_unmerged_branch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    branch_head = "topic abc\n"
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: {
            FOR_EACH_REF_HEADS: branch_head,
            ("merge-base", "--is-ancestor", "topic", "main"): "",
            ("merge-base", "topic", "main"): "base\n",
        }.get(tuple(args), ""),
    )

    assert mco_loop.branch_inventory_issues(tmp_path, {}) == (
        mco_loop.BranchIssue("topic", "abc", "base", "missing disposition"),
    )


def test_branch_inventory_reports_review_disposition(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    branch_head = "topic aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
    base = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: {
            FOR_EACH_REF_HEADS: branch_head,
            ("merge-base", "--is-ancestor", "topic", "main"): "",
            ("merge-base", "topic", "main"): base,
        }.get(tuple(args), ""),
    )
    ledger = {
        "topic": mco_loop.BranchDisposition(
            "topic",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "review",
            "Needs review.",
        )
    }

    assert mco_loop.branch_inventory_issues(tmp_path, ledger) == (
        mco_loop.BranchIssue(
            "topic",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "review pending",
        ),
    )


def test_branch_inventory_reports_stale_ledger_head(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    branch_head = "topic bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
    base = "cccccccccccccccccccccccccccccccccccccccc\n"
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: {
            FOR_EACH_REF_HEADS: branch_head,
            ("merge-base", "--is-ancestor", "topic", "main"): "",
            ("merge-base", "topic", "main"): base,
        }.get(tuple(args), ""),
    )
    ledger = {
        "topic": mco_loop.BranchDisposition(
            "topic",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "integrated",
            "Already landed.",
        )
    }

    assert mco_loop.branch_inventory_issues(tmp_path, ledger) == (
        mco_loop.BranchIssue(
            "topic",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "cccccccccccccccccccccccccccccccccccccccc",
            "ledger head mismatch",
        ),
    )


def test_branch_inventory_accepts_matching_preserve_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    branch_head = "topic aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
    base = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: {
            FOR_EACH_REF_HEADS: branch_head,
            ("merge-base", "--is-ancestor", "topic", "main"): "",
            ("merge-base", "topic", "main"): base,
        }.get(tuple(args), ""),
    )
    ledger = {
        "topic": mco_loop.BranchDisposition(
            "topic",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "preserve",
            "Historical branch retained intentionally.",
        )
    }

    assert mco_loop.branch_inventory_issues(tmp_path, ledger) == ()


def test_branch_inventory_reports_missing_local_branch_from_ledger(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: {
            FOR_EACH_REF_HEADS: "",
        }.get(tuple(args), ""),
    )
    ledger = {
        "topic": mco_loop.BranchDisposition(
            "topic",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "integrated",
            "Already landed.",
        )
    }

    assert mco_loop.branch_inventory_issues(tmp_path, ledger) == (
        mco_loop.BranchIssue(
            "topic",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            None,
            "branch missing locally",
        ),
    )


def test_reconciliation_action_returns_planner_action_for_branch_issues(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] Implement it\n")
    rows = (_row("5R", "in flight", plan),)
    review_issue = mco_loop.BranchIssue(
        "topic",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "review pending",
    )
    monkeypatch.setattr(
        mco_loop,
        "load_branch_dispositions",
        lambda path=mco_loop.BRANCH_DISPOSITIONS: {
            "topic": mco_loop.BranchDisposition(
                "topic",
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "review",
                "Needs review.",
            )
        },
    )
    monkeypatch.setattr(
        mco_loop,
        "branch_inventory_issues",
        lambda repo, ledger: (review_issue,),
    )

    action = mco_loop.reconciliation_action(rows, repo=tmp_path)

    assert action == NextAction(
        ActionKind.PLAN,
        "Resolve branch reconciliation before normal roadmap execution: "
        "topic@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa "
        "(base bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb): review pending",
        plan,
        None,
        (),
    )


def _main_test_config_with_planning(tmp_path: Path) -> mco_loop.LoopConfig:
    return mco_loop.LoopConfig(
        env_file=tmp_path / ".env",
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=60,
        iteration_pause_seconds=0,
        planning=(Executor("planner", "claude", "claude"),),
        implementation=(Executor("implementer", "codex", "codex"),),
    )


def test_main_routes_review_branch_disposition_to_planning_pool(
    tmp_path: Path, monkeypatch
) -> None:
    config = _main_test_config_with_planning(tmp_path)
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("ignored")
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] step\n")
    canonical = NextAction(ActionKind.IMPLEMENT, "execute", plan, "step", ())
    selected_actions: list[NextAction] = []
    selected_pools: list[tuple[Executor, ...]] = []

    monkeypatch.setattr(mco_loop, "REPO", tmp_path)
    monkeypatch.setattr(mco_loop, "ROADMAP", roadmap)
    monkeypatch.setattr(
        mco_loop, "load_config", lambda path=mco_loop.DEFAULT_CONFIG: config
    )
    monkeypatch.setattr(mco_loop.shutil, "which", lambda name: "/bin/mco")
    monkeypatch.setattr(mco_loop, "load_named_secrets", lambda path: {})
    monkeypatch.setattr(
        mco_loop,
        "parse_roadmap",
        lambda text: (_row("5R", "in flight", plan),),
    )
    monkeypatch.setattr(
        mco_loop, "determine_next_action", lambda rows, blockers: canonical
    )
    monkeypatch.setattr(
        mco_loop,
        "load_branch_dispositions",
        lambda path=mco_loop.BRANCH_DISPOSITIONS: {
            "topic": mco_loop.BranchDisposition(
                "topic",
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "review",
                "Needs review.",
            )
        },
    )
    monkeypatch.setattr(
        mco_loop,
        "branch_inventory_issues",
        lambda repo, ledger: (
            mco_loop.BranchIssue(
                "topic",
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "review pending",
            ),
        ),
    )
    monkeypatch.setattr(
        mco_loop, "apply_governor_directive", lambda action: (action, False, False)
    )

    def fake_select(executors, state, action, now, preserve_planning=False):
        selected_pools.append(tuple(executors))
        selected_actions.append(action)
        return mco_loop.ExecutorSelection(None, None, True)

    monkeypatch.setattr(mco_loop, "select_executor", fake_select)

    result = mco_loop.main(["--once"])

    assert result == 5
    assert selected_pools == [config.planning]
    assert selected_actions == [
        NextAction(
            ActionKind.PLAN,
            "Resolve branch reconciliation before normal roadmap execution: "
            "topic@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa "
            "(base bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb): review pending",
            plan,
            None,
            (),
        )
    ]


def test_main_keeps_ordinary_action_after_terminal_branch_reconciliation(
    tmp_path: Path, monkeypatch
) -> None:
    config = _main_test_config_with_planning(tmp_path)
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("ignored")
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] step\n")
    canonical = NextAction(ActionKind.IMPLEMENT, "execute", plan, "step", ())
    selected_actions: list[NextAction] = []
    selected_pools: list[tuple[Executor, ...]] = []

    monkeypatch.setattr(mco_loop, "REPO", tmp_path)
    monkeypatch.setattr(mco_loop, "ROADMAP", roadmap)
    monkeypatch.setattr(
        mco_loop, "load_config", lambda path=mco_loop.DEFAULT_CONFIG: config
    )
    monkeypatch.setattr(mco_loop.shutil, "which", lambda name: "/bin/mco")
    monkeypatch.setattr(mco_loop, "load_named_secrets", lambda path: {})
    monkeypatch.setattr(
        mco_loop,
        "parse_roadmap",
        lambda text: (_row("5R", "in flight", plan),),
    )
    monkeypatch.setattr(
        mco_loop, "determine_next_action", lambda rows, blockers: canonical
    )
    monkeypatch.setattr(
        mco_loop,
        "load_branch_dispositions",
        lambda path=mco_loop.BRANCH_DISPOSITIONS: {
            "topic": mco_loop.BranchDisposition(
                "topic",
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "integrated",
                "Already landed.",
            )
        },
    )
    monkeypatch.setattr(
        mco_loop,
        "branch_inventory_issues",
        lambda repo, ledger: (),
    )
    monkeypatch.setattr(
        mco_loop, "apply_governor_directive", lambda action: (action, False, False)
    )

    def fake_select(executors, state, action, now, preserve_planning=False):
        selected_pools.append(tuple(executors))
        selected_actions.append(action)
        return mco_loop.ExecutorSelection(None, None, True)

    monkeypatch.setattr(mco_loop, "select_executor", fake_select)

    result = mco_loop.main(["--once"])

    assert result == 5
    assert selected_pools == [config.implementation]
    assert selected_actions == [canonical]


def _invocation_inputs(
    tmp_path: Path,
) -> tuple[mco_loop.LoopConfig, Executor, NextAction]:
    config = mco_loop.LoopConfig(
        env_file=tmp_path / ".env",
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=600,
        iteration_pause_seconds=0,
        planning=(),
        implementation=(),
    )
    executor = Executor("test", "test-provider", "test-group")
    action = NextAction(ActionKind.FIX, "test subprocess handling", None, None, ())
    return config, executor, action


def test_invoke_mco_terminates_process_group_on_timeout(
    monkeypatch, tmp_path: Path
) -> None:
    config, executor, action = _invocation_inputs(tmp_path)
    popen_kwargs: dict[str, object] = {}
    signals: list[tuple[int, int]] = []

    class FakeProcess:
        stdout = io.StringIO("")
        stderr = io.StringIO("")
        returncode = None
        pid = 4321

        def poll(self) -> None:
            return None

        def wait(self, timeout: float | None = None) -> int:
            self.returncode = -signal.SIGTERM
            return self.returncode

    def fake_popen(command, **kwargs):
        popen_kwargs.update(kwargs)
        return FakeProcess()

    times = iter((100.0, 101.0))
    monkeypatch.setattr(mco_loop.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(mco_loop.time, "time", lambda: next(times))
    monkeypatch.setattr(mco_loop, "MCO_TIMEOUT_SECONDS", 0.5)
    monkeypatch.setattr(os, "killpg", lambda pgid, sig: signals.append((pgid, sig)))
    fingerprints = iter(("before", "after"))
    monkeypatch.setattr(mco_loop, "repo_fingerprint", lambda: next(fingerprints))
    config.artifact_dir.mkdir(parents=True)
    artifact = config.artifact_dir / "provider.json"
    artifact.write_text('{"secret":"secret-value"}')

    result = mco_loop.invoke_mco(
        config,
        executor,
        action,
        {"OPENROUTER_API_KEY": "secret-value"},
        prompt_override="test",
    )

    assert result.exit_code == 124
    assert result.made_progress is True
    assert "secret-value" not in artifact.read_text()
    assert popen_kwargs["start_new_session"] is True
    assert signals == [
        (4321, signal.SIGTERM),
        (4321, 0),
        (4321, signal.SIGKILL),
    ]


def test_invoke_mco_drains_stderr_while_process_runs(
    monkeypatch, tmp_path: Path
) -> None:
    config, executor, action = _invocation_inputs(tmp_path)
    command = [
        sys.executable,
        "-c",
        "import sys; sys.stderr.write('e' * 1000000); "
        "sys.stderr.flush(); sys.stdout.write('done\\n'); sys.stdout.flush()",
    ]
    monkeypatch.setattr(mco_loop, "mco_command", lambda *args: command)
    monkeypatch.setattr(mco_loop, "MCO_TIMEOUT_SECONDS", 2.0)
    monkeypatch.setattr(mco_loop, "repo_fingerprint", lambda: "unchanged")

    result = mco_loop.invoke_mco(config, executor, action, {})

    assert result.exit_code == 0
    assert result.stdout == "done\n"
    assert result.stderr == "e" * 1000000


def test_live_config_has_role_scoped_model_order() -> None:
    config = mco_loop.load_config()

    assert [(item.provider, item.model) for item in config.planning] == [
        ("codex", "gpt-5.6-terra"),
        ("claude-sonnet", None),
        ("claude-opus", None),
        ("codex", "gpt-5.6-sol"),
    ]
    assert [item.provider for item in config.implementation] == [
        "claude-sonnet",
        "codex",
        "claude-opus",
        "codex",
        "pi-nemotron-ultra-stateless",
        "pi-gpt-oss-stateless",
        "pi-nemotron-super-stateless",
        "pi-hy3-stateless",
        "pi-laguna-stateless",
        "pi-qwen-coder-stateless",
    ]
    assert [(item.model_provider, item.model) for item in config.implementation] == [
        (None, None),
        (None, "gpt-5.4"),
        (None, None),
        (None, "gpt-5.6-sol"),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
        (None, None),
    ]
    assert config.planning[2].display_model == "opus"
    assert config.implementation[0].display_model == "sonnet"
    assert not {"agy-flash", "agy-pro", "pi"} & {
        item.provider for item in config.planning
    }
    assert all(item.provider != "claude-fable" for item in config.planning)
    assert all(item.provider != "claude-fable" for item in config.implementation)


def test_automatic_shims_are_stateless_and_models_remain_visible() -> None:
    agents = (mco_loop.REPO / ".mco" / "agents.yaml").read_text()
    config = mco_loop.load_config()

    assert agents.count("claude -p --no-session-persistence") == 3
    assert agents.count("pi --no-session --print") == 6
    assert not {"agy-flash", "agy-pro", "pi"} & {
        item.provider for item in config.implementation
    }
    fallbacks = config.implementation[-6:]
    assert [item.display_model for item in fallbacks] == [
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "openai/gpt-oss-120b:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "tencent/hy3:free",
        "poolside/laguna-m.1:free",
        "qwen/qwen3-coder:free",
    ]


def test_pi_shims_are_stateless_and_write_capable() -> None:
    text = (mco_loop.REPO / ".mco" / "agents.yaml").read_text()

    for name, slug in (
        ("pi-nemotron-ultra-stateless", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        ("pi-gpt-oss-stateless", "openai/gpt-oss-120b:free"),
        ("pi-nemotron-super-stateless", "nvidia/nemotron-3-super-120b-a12b:free"),
        ("pi-hy3-stateless", "tencent/hy3:free"),
        ("pi-laguna-stateless", "poolside/laguna-m.1:free"),
        ("pi-qwen-coder-stateless", "qwen/qwen3-coder:free"),
    ):
        assert name in text
        assert slug in text
    for line in text.splitlines():
        if "command: 'pi " in line:
            assert "--no-session" in line
            assert "--print" in line
            assert "--tools read,bash,edit,write" in line
    for remnant in ("grok", "xai", "nemotron-4-340b", "agy-"):
        assert remnant not in text.lower()


def test_xai_key_is_no_longer_allowlisted() -> None:
    assert mco_loop.ALLOWED_SECRET_NAMES == ("OPENROUTER_API_KEY",)


def test_parse_roadmap_finds_live_rows_and_plan_path() -> None:
    text = """
| # | Plan | Architecture | Ships | Gate | Status |
|---|---|---|---|---|---|
| 3M | Rails (`docs/superpowers/plans/rails.md`) | x | x | x | in flight |
| 4 | Spike | x | x | x | pending |
"""

    rows = mco_loop.parse_roadmap(text)

    assert len(rows) == 2
    assert rows[0].identifier == "3M"
    assert rows[0].plan_path == mco_loop.REPO / "docs/superpowers/plans/rails.md"
    assert rows[1].status == "pending"


def test_blocker_forces_fix_before_plan_or_implementation(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] Implement it\n")

    action = mco_loop.determine_next_action(
        [_row("3M", "in flight", plan)], ["- BLOCK: broken contract"]
    )

    assert action.kind is ActionKind.FIX
    assert action.blockers == ("- BLOCK: broken contract",)


def test_no_in_flight_plan_selects_planning_for_first_pending_row() -> None:
    action = mco_loop.determine_next_action(
        [_row("3L", "shipped"), _row("4", "pending", description="Spike B")], []
    )

    assert action.kind is ActionKind.PLAN
    assert "row 4" in action.summary


def test_active_plan_selects_first_unchecked_implementation_step(
    tmp_path: Path,
) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("- [x] Done\n- [ ] Implement the parser\n- [ ] Later\n")

    action = mco_loop.determine_next_action([_row("3M", "in flight", plan)], [])

    assert action.kind is ActionKind.IMPLEMENT
    assert action.step == "Implement the parser"


def test_explicit_plan_authoring_step_uses_planning_models(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] Write the Spike B implementation plan\n")

    action = mco_loop.determine_next_action([_row("4", "in flight", plan)], [])

    assert action.kind is ActionKind.PLAN


def test_finished_in_flight_plan_requires_fixing_finalization(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("- [x] Everything done\n")

    action = mco_loop.determine_next_action([_row("3M", "in flight", plan)], [])

    assert action.kind is ActionKind.FIX
    assert "remains in flight" in action.summary


def test_more_than_one_in_flight_plan_is_rejected(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] Work\n")

    try:
        mco_loop.determine_next_action(
            [_row("A", "in flight", plan), _row("B", "in flight", plan)], []
        )
    except ValueError as exc:
        assert "more than one" in str(exc)
    else:
        raise AssertionError("multiple in-flight plans were accepted")


def test_load_named_secrets_loads_only_allowlisted_names(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENROUTER_API_KEY='or-secret'\n"
        "XAI_API_KEY=must-not-load\n"
        "UNRELATED_SECRET=must-not-load\n"
    )

    result = mco_loop.load_named_secrets(env_file, {"PATH": "/bin"})

    assert result["OPENROUTER_API_KEY"] == "or-secret"
    assert "XAI_API_KEY" not in result
    assert "UNRELATED_SECRET" not in result


def test_exported_secret_takes_precedence_over_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY=file-value\n")

    result = mco_loop.load_named_secrets(
        env_file, {"OPENROUTER_API_KEY": "exported-value"}
    )

    assert result["OPENROUTER_API_KEY"] == "exported-value"


def test_mco_argv_contains_model_policy_but_no_secret_values(tmp_path: Path) -> None:
    config = mco_loop.load_config()
    prompt = tmp_path / "prompt.md"
    executor = next(
        item for item in config.implementation if item.name == "hy3-implement"
    )

    command = mco_loop.mco_command(config, executor, "task", prompt)

    joined = " ".join(command)
    assert "pi-hy3-stateless" in joined
    assert "--provider-models-json" not in command
    assert "or-secret" not in joined
    assert "OPENROUTER_API_KEY" not in joined
    assert command[command.index("--max-provider-parallelism") + 1] == "1"


@pytest.mark.parametrize(
    ("result", "expected_outcome"),
    (
        (
            InvocationResult(2, '{"error_kind":"retryable_rate_limit"}', "", False),
            "rate_limit",
        ),
        (
            InvocationResult(
                2, '{"error_kind":"retryable_transient_network"}', "", False
            ),
            "transient",
        ),
    ),
)
def test_availability_failure_uses_short_quota_group_cooldown_and_selects_next(
    tmp_path: Path,
    result: InvocationResult,
    expected_outcome: str,
) -> None:
    config = mco_loop.load_config()
    config = mco_loop.LoopConfig(
        env_file=config.env_file,
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=600,
        iteration_pause_seconds=0,
        planning=config.planning,
        implementation=config.implementation,
        rate_limit_cooldown_seconds=300,
    )
    state: dict[str, object] = {
        "cooldowns": {},
        "failures": {},
        "last_failure": None,
    }
    first = config.implementation[0]
    action = NextAction(ActionKind.IMPLEMENT, "test", None, "step", ())
    failure = mco_loop.apply_result(config, state, first, action, result, now=1000)
    selected, _ = mco_loop.available_executor(config.implementation, state, now=1001)

    assert failure == expected_outcome
    assert selected == config.implementation[1]
    saved = json.loads(config.state_file.read_text())
    assert saved["cooldowns"][first.quota_group] == 1300


def test_cooldown_cli_override_preserves_rate_limit_cooldown(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = mco_loop.LoopConfig(
        env_file=tmp_path / ".env",
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=600,
        iteration_pause_seconds=0,
        planning=(),
        implementation=(),
        rate_limit_cooldown_seconds=123,
    )
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("ignored")
    captured: dict[str, mco_loop.LoopConfig] = {}

    monkeypatch.setattr(mco_loop, "ROADMAP", roadmap)
    monkeypatch.setattr(mco_loop, "load_config", lambda path: config)
    monkeypatch.setattr(mco_loop.shutil, "which", lambda name: "/bin/mco")
    monkeypatch.setattr(mco_loop, "load_named_secrets", lambda path: {})
    monkeypatch.setattr(mco_loop, "ensure_git_hooks", lambda: None)
    monkeypatch.setattr(mco_loop, "pi_auth_shadow_warning", lambda: None)
    monkeypatch.setattr(mco_loop, "pi_models_config_warning", lambda: None)
    monkeypatch.setattr(
        mco_loop,
        "parse_roadmap",
        lambda text: (_row("4S", "in flight"),),
    )
    monkeypatch.setattr(
        mco_loop,
        "determine_next_action",
        lambda rows, blockers: NextAction(
            ActionKind.IMPLEMENT, "test", None, "step", ()
        ),
    )

    def fake_run_governor(
        actual: mco_loop.LoopConfig,
        action: NextAction,
        environment: dict[str, str],
    ) -> int:
        captured["config"] = actual
        return 0

    monkeypatch.setattr(mco_loop, "run_governor", fake_run_governor)

    assert mco_loop.main(["--govern", "--cooldown-seconds", "10"]) == 0
    assert captured["config"].cooldown_seconds == 10
    assert captured["config"].rate_limit_cooldown_seconds == 123


def test_no_progress_success_also_advances_to_next_executor(tmp_path: Path) -> None:
    config = mco_loop.load_config()
    config = mco_loop.LoopConfig(
        env_file=config.env_file,
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=60,
        iteration_pause_seconds=0,
        planning=config.planning,
        implementation=config.implementation,
    )
    state: dict[str, object] = {
        "cooldowns": {},
        "failures": {},
        "last_failure": None,
    }

    failure = mco_loop.apply_result(
        config,
        state,
        config.implementation[0],
        NextAction(ActionKind.IMPLEMENT, "test", None, "step", ()),
        InvocationResult(0, "analysis only", "", False),
        now=100,
    )

    assert failure == "no_progress"
    selected, _ = mco_loop.available_executor(config.implementation, state, now=101)
    assert selected == config.implementation[1]
    cooldowns = state["cooldowns"]
    assert isinstance(cooldowns, dict)
    assert "claude" not in cooldowns
    assert cooldowns[f"executor:{config.implementation[0].name}"] == 160


def test_progress_outranks_rate_limit_wording() -> None:
    result = InvocationResult(0, "updated rate limit tests", "", True, False)

    assert mco_loop.classify_result(result) == "progress"


def test_supervisor_timeout_is_substantive_before_transient_markers() -> None:
    result = InvocationResult(124, "", "MCO execution timed out", False, False)

    assert mco_loop.classify_result(result) == "supervisor_timeout"


def test_new_blocker_is_not_no_progress() -> None:
    result = InvocationResult(0, "", "", False, True)

    assert mco_loop.classify_result(result) == "blocked"


def test_openrouter_upstream_throttle_classifies_as_rate_limit() -> None:
    throttle = (
        '429: {"message":"Provider returned error","code":429,"metadata":'
        '{"raw":"openai/gpt-oss-120b:free is temporarily rate-limited '
        'upstream. Please retry shortly."}}'
    )
    result = InvocationResult(0, throttle, "", False, False)

    assert mco_loop.classify_result(result) == "rate_limit"


def test_session_limit_classifies_as_rate_limit() -> None:
    session_limit = "You've hit your session limit · resets 6pm (Europe/London)"
    result = InvocationResult(2, session_limit, "", False, False)
    assert mco_loop.classify_result(result) == "rate_limit"


def test_progress_still_outranks_throttle_wording() -> None:
    result = InvocationResult(
        0, "documented how rate-limited 429: responses are handled", "", True, False
    )

    assert mco_loop.classify_result(result) == "progress"


def test_pi_auth_shadow_warning_detects_openrouter_entry(tmp_path: Path) -> None:
    auth = tmp_path / "auth.json"
    auth.write_text('{"openrouter": {"type": "api_key", "key": "sk-or-v1-stale"}}')

    warning = mco_loop.pi_auth_shadow_warning(auth)

    assert warning is not None
    assert "auth.json" in warning
    assert "openrouter" in warning.lower()
    assert "sk-or-v1-stale" not in warning


def test_pi_auth_shadow_warning_silent_when_clean(tmp_path: Path) -> None:
    clean = tmp_path / "auth.json"
    clean.write_text('{"anthropic": {"type": "api_key", "key": "sk-ant-x"}}')
    assert mco_loop.pi_auth_shadow_warning(clean) is None
    assert mco_loop.pi_auth_shadow_warning(tmp_path / "missing.json") is None
    malformed = tmp_path / "broken.json"
    malformed.write_text("{not json")
    assert mco_loop.pi_auth_shadow_warning(malformed) is None


def test_pi_models_config_warning_names_missing_capped_models(tmp_path: Path) -> None:
    missing = mco_loop.pi_models_config_warning(tmp_path / "models.json")
    assert missing is not None
    assert "models.json" in missing
    assert "qwen/qwen3-coder:free" in missing
    assert "nvidia/nemotron-3-super-120b-a12b:free" in missing

    partial = tmp_path / "partial.json"
    partial.write_text(
        '{"providers": {"openrouter": {"models": '
        '[{"id": "qwen/qwen3-coder:free", "maxTokens": 32768}]}}}'
    )
    warning = mco_loop.pi_models_config_warning(partial)
    assert warning is not None
    assert "nvidia/nemotron-3-super-120b-a12b:free" in warning
    assert "qwen/qwen3-coder:free" not in warning


def test_pi_models_config_warning_requires_valid_max_tokens_cap(
    tmp_path: Path,
) -> None:
    uncapped = tmp_path / "models.json"
    uncapped.write_text(
        '{"providers": {"openrouter": {"models": ['
        '{"id": "qwen/qwen3-coder:free"},'
        '{"id": "nvidia/nemotron-3-super-120b-a12b:free", "maxTokens": 262000}'
        "]}}}"
    )

    warning = mco_loop.pi_models_config_warning(uncapped)

    assert warning is not None
    assert "qwen/qwen3-coder:free" in warning
    assert "nvidia/nemotron-3-super-120b-a12b:free" in warning


def test_pi_models_config_warning_silent_when_complete(tmp_path: Path) -> None:
    complete = tmp_path / "models.json"
    complete.write_text(
        '{"providers": {"openrouter": {"models": ['
        '{"id": "qwen/qwen3-coder:free", "maxTokens": 32768},'
        '{"id": "nvidia/nemotron-3-super-120b-a12b:free", "maxTokens": 32768}'
        "]}}}"
    )

    assert mco_loop.pi_models_config_warning(complete) is None


def test_recovery_rewrite_would_change_key_if_misused() -> None:
    canonical = NextAction(ActionKind.IMPLEMENT, "execute", Path("plan.md"), "step", ())
    rewritten = mco_loop.apply_failure_action(
        canonical, {"last_failure": {"kind": "no_progress", "executor": "claude"}}
    )

    assert rewritten != canonical
    assert mco_loop.action_key(rewritten) != mco_loop.action_key(canonical)


def test_action_key_uses_every_canonical_routing_field() -> None:
    base = NextAction(ActionKind.IMPLEMENT, "execute", Path("plan.md"), "step", ())
    variants = (
        NextAction(
            ActionKind.FIX, base.summary, base.active_plan, base.step, base.blockers
        ),
        NextAction(base.kind, "recover", base.active_plan, base.step, base.blockers),
        NextAction(base.kind, base.summary, Path("other.md"), base.step, base.blockers),
        NextAction(
            base.kind, base.summary, base.active_plan, "other step", base.blockers
        ),
        NextAction(
            base.kind, base.summary, base.active_plan, base.step, ("- BLOCK: x",)
        ),
    )

    assert all(
        mco_loop.action_key(item) != mco_loop.action_key(base) for item in variants
    )


def test_load_state_preserves_optional_action_attempt_and_exhaustion(
    tmp_path: Path,
) -> None:
    path = tmp_path / "state.json"
    path.write_text(
        json.dumps(
            {
                "action_attempt": {
                    "key": "abc",
                    "attempts": {"claude": "no_progress"},
                },
                "exhaustion": {"action_key": "abc"},
            }
        )
    )

    state = mco_loop.load_state(path)

    assert state["action_attempt"] == {
        "key": "abc",
        "attempts": {"claude": "no_progress"},
    }
    assert state["exhaustion"] == {"action_key": "abc"}


def test_missing_state_defaults_optional_records_to_none(tmp_path: Path) -> None:
    state = mco_loop.load_state(tmp_path / "missing.json")

    assert state["action_attempt"] is None
    assert state["exhaustion"] is None


def test_selection_skips_substantively_attempted_executor() -> None:
    action = NextAction(ActionKind.IMPLEMENT, "execute", None, "step", ())
    executors = (
        Executor("claude", "claude", "claude"),
        Executor("fallback", "pi-fallback", "openrouter"),
    )
    state = {
        "cooldowns": {},
        "action_attempt": {
            "key": mco_loop.action_key(action),
            "attempts": {"claude": "no_progress"},
        },
    }

    selection = mco_loop.select_executor(executors, state, action, now=100)

    assert selection.executor == executors[1]
    assert selection.exhausted is False


def test_selection_keeps_configured_priority_for_implementation() -> None:
    action = NextAction(ActionKind.IMPLEMENT, "execute", None, "step", ())
    executors = (
        Executor("claude", "claude", "claude"),
        Executor("fallback", "pi-fallback", "openrouter"),
    )

    selection = mco_loop.select_executor(
        executors, {"cooldowns": {}}, action, now=100, preserve_planning=True
    )

    assert selection.executor == executors[0]


def test_selection_waits_for_unattempted_trusted_cooldown() -> None:
    action = NextAction(ActionKind.IMPLEMENT, "execute", None, "step", ())
    executors = (
        Executor("claude", "claude", "claude"),
        Executor("fallback", "pi-fallback", "openrouter"),
    )
    state = {
        "cooldowns": {"claude": 200},
        "action_attempt": {
            "key": mco_loop.action_key(action),
            "attempts": {"fallback": "no_progress"},
        },
    }

    selection = mco_loop.select_executor(executors, state, action, now=100)

    assert selection.executor is None
    assert selection.next_ready == 200
    assert selection.exhausted is False


def test_selection_exhausts_instead_of_waiting_for_untrusted_cooldown() -> None:
    action = NextAction(ActionKind.IMPLEMENT, "execute", None, "step", ())
    executors = (
        Executor("claude", "claude", "claude"),
        Executor("fallback", "pi-fallback", "openrouter"),
    )
    state = {
        "cooldowns": {"openrouter": 200},
        "action_attempt": {
            "key": mco_loop.action_key(action),
            "attempts": {"claude": "no_progress"},
        },
    }

    selection = mco_loop.select_executor(executors, state, action, now=100)

    assert selection.executor is None
    assert selection.next_ready is None
    assert selection.exhausted is True


def test_substantive_result_records_attempt_for_canonical_action(
    tmp_path: Path,
) -> None:
    config, executor, action = _invocation_inputs(tmp_path)
    state: dict[str, object] = {
        "cooldowns": {},
        "failures": {},
        "last_failure": None,
    }

    outcome = mco_loop.apply_result(
        config,
        state,
        executor,
        action,
        InvocationResult(0, "analysis only", "", False),
        now=100,
    )

    assert outcome == "no_progress"
    assert state["action_attempt"] == {
        "key": mco_loop.action_key(action),
        "attempts": {executor.name: "no_progress"},
    }


def test_availability_result_does_not_record_substantive_attempt(
    tmp_path: Path,
) -> None:
    config, executor, action = _invocation_inputs(tmp_path)
    state: dict[str, object] = {
        "cooldowns": {},
        "failures": {},
        "last_failure": None,
    }

    outcome = mco_loop.apply_result(
        config,
        state,
        executor,
        action,
        InvocationResult(2, '{"error_kind":"retryable_rate_limit"}', "", False),
        now=100,
    )

    assert outcome == "rate_limit"
    assert state.get("action_attempt") is None


def test_progress_and_blocker_clear_action_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mco_loop, "FABLE_DIRECTIVE", tmp_path / "fable-directive.md")
    config, executor, action = _invocation_inputs(tmp_path)
    for result, expected in (
        (InvocationResult(0, "changed", "", True), "progress"),
        (InvocationResult(0, "", "", False, True), "blocked"),
    ):
        state: dict[str, object] = {
            "cooldowns": {},
            "failures": {executor.name: 1},
            "last_failure": {"kind": "no_progress"},
            "action_attempt": {
                "key": mco_loop.action_key(action),
                "attempts": {executor.name: "no_progress"},
            },
        }

        outcome = mco_loop.apply_result(
            config, state, executor, action, result, now=100
        )

        assert outcome == expected
        assert state["action_attempt"] is None
        assert state["last_failure"] is None
        assert state["cooldowns"] == {}


def _main_test_config(tmp_path: Path) -> mco_loop.LoopConfig:
    return mco_loop.LoopConfig(
        env_file=tmp_path / ".env",
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=60,
        iteration_pause_seconds=0,
        planning=(),
        implementation=(Executor("claude", "claude", "claude"),),
    )


def test_main_uses_canonical_action_and_exits_five_on_exhaustion(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    config = _main_test_config(tmp_path)
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("ignored")
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] step\n")
    canonical = NextAction(ActionKind.IMPLEMENT, "execute", plan, "step", ())
    rewritten = NextAction(ActionKind.FIX, "recover", plan, "step", ())
    governed = NextAction(ActionKind.PLAN, "redirect", plan, "step", ())
    selected_actions: list[NextAction] = []

    monkeypatch.setattr(mco_loop, "REPO", tmp_path)
    monkeypatch.setattr(mco_loop, "ROADMAP", roadmap)
    monkeypatch.setattr(
        mco_loop, "load_config", lambda path=mco_loop.DEFAULT_CONFIG: config
    )
    monkeypatch.setattr(mco_loop.shutil, "which", lambda name: "/bin/mco")
    monkeypatch.setattr(mco_loop, "load_named_secrets", lambda path: {})
    monkeypatch.setattr(
        mco_loop,
        "parse_roadmap",
        lambda text: (_row("3M", "in flight", plan),),
    )
    monkeypatch.setattr(
        mco_loop, "determine_next_action", lambda rows, blockers: canonical
    )
    monkeypatch.setattr(
        mco_loop, "reconciliation_action", lambda rows, repo=mco_loop.REPO: None
    )
    monkeypatch.setattr(
        mco_loop, "apply_failure_action", lambda action, state: rewritten
    )
    monkeypatch.setattr(
        mco_loop, "apply_governor_directive", lambda action: (governed, False, True)
    )

    def fake_select(executors, state, action, now, preserve_planning=False):
        selected_actions.append(action)
        return mco_loop.ExecutorSelection(None, None, True)

    monkeypatch.setattr(mco_loop, "select_executor", fake_select)

    result = mco_loop.main(["--once"])

    assert result == 5
    assert selected_actions == [canonical]
    assert json.loads(config.state_file.read_text())["exhaustion"]["action_key"] == (
        mco_loop.action_key(canonical)
    )
    assert "agent-loop: exhausted" in capsys.readouterr().err


def test_main_once_returns_three_only_for_trusted_retry_wait(
    tmp_path: Path, monkeypatch
) -> None:
    config = _main_test_config(tmp_path)
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("ignored")
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] step\n")
    canonical = NextAction(ActionKind.IMPLEMENT, "execute", plan, "step", ())

    monkeypatch.setattr(mco_loop, "REPO", tmp_path)
    monkeypatch.setattr(mco_loop, "ROADMAP", roadmap)
    monkeypatch.setattr(
        mco_loop, "load_config", lambda path=mco_loop.DEFAULT_CONFIG: config
    )
    monkeypatch.setattr(mco_loop.shutil, "which", lambda name: "/bin/mco")
    monkeypatch.setattr(mco_loop, "load_named_secrets", lambda path: {})
    monkeypatch.setattr(
        mco_loop,
        "parse_roadmap",
        lambda text: (_row("3M", "in flight", plan),),
    )
    monkeypatch.setattr(
        mco_loop, "determine_next_action", lambda rows, blockers: canonical
    )
    monkeypatch.setattr(
        mco_loop, "apply_governor_directive", lambda action: (action, False, False)
    )
    monkeypatch.setattr(
        mco_loop,
        "select_executor",
        lambda *args, **kwargs: mco_loop.ExecutorSelection(None, 200, False),
    )
    monkeypatch.setattr(mco_loop.time, "time", lambda: 100)

    assert mco_loop.main(["--once"]) == 3


@pytest.mark.parametrize("secret", ["secret-value", 'abc"def\\ghi\njkl'])
def test_exhaustion_payload_redacts_action_text(secret: str) -> None:
    action = NextAction(
        ActionKind.FIX,
        f"recover {secret}",
        None,
        f"step {secret}",
        (f"- BLOCK: {secret}",),
    )

    payload = mco_loop.exhaustion_payload(
        action,
        (),
        {"action_attempt": None, "cooldowns": {}},
        now=100,
        environment={"OPENROUTER_API_KEY": secret},
    )

    serialized = json.dumps(payload)
    assert secret not in serialized
    assert "OPENROUTER_API_KEY:redacted" in serialized


def test_new_task_ids_are_unique_for_same_executor_and_action() -> None:
    action = NextAction(ActionKind.IMPLEMENT, "execute", None, "step", ())
    executor = Executor("claude", "claude", "claude")

    assert mco_loop.new_task_id(action, executor) != mco_loop.new_task_id(
        action, executor
    )


def test_planning_pool_never_falls_through_to_implementation_only_models() -> None:
    config = mco_loop.load_config()
    state: dict[str, object] = {
        "cooldowns": {"codex": 200, "claude": 200},
        "failures": {},
        "last_failure": None,
    }

    selected, next_ready = mco_loop.available_executor(config.planning, state, now=100)

    assert selected is None
    assert next_ready == 200


def test_prompt_contains_durable_handoff_and_dirty_worktree(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda arguments: " M src/example.py\n?? notes.md\n",
    )
    action = NextAction(
        ActionKind.IMPLEMENT,
        "Execute one step.",
        mco_loop.REPO / "docs/superpowers/plans/example.md",
        "Implement the parser",
        (),
    )

    prompt = mco_loop.build_prompt(
        action,
        Executor("claude", "claude", "claude", "sonnet"),
        {"kind": "rate_limit", "executor": "codex"},
        "implement-1-claude",
    )

    assert "Implement the parser" in prompt
    assert "M src/example.py" in prompt
    assert "rate_limit" in prompt
    assert "private conversation" not in prompt
    assert "Work on one step only" in prompt
    assert "Agent: claude" in prompt
    assert "Model: sonnet" in prompt
    assert "Harness: MCO 0.10.8" in prompt


def test_prompt_contains_invocation_boundary(monkeypatch) -> None:
    monkeypatch.setattr(mco_loop, "_git_output", lambda arguments: "")
    action = NextAction(ActionKind.IMPLEMENT, "Execute one step.", None, "step", ())

    prompt = mco_loop.build_prompt(
        action,
        Executor("claude", "claude", "claude"),
        None,
        "implement-123-claude",
    )

    assert "Invocation: implement-123-claude" in prompt
    assert "complete task for a fresh, isolated session" in prompt
    assert "Do not resume, answer, or rely on any earlier conversation" in prompt


def test_planning_prompt_requires_noninteractive_superpowers_artifacts(
    monkeypatch,
) -> None:
    monkeypatch.setattr(mco_loop, "_git_output", lambda arguments: "")
    action = NextAction(
        ActionKind.PLAN,
        "Plan Spike B.",
        None,
        None,
        (),
    )

    prompt = mco_loop.build_prompt(
        action,
        Executor("planner", "claude-opus", "claude", display_model="opus"),
        None,
        "plan-1-planner",
    )

    assert "do not wait for human input" in prompt
    assert "docs/superpowers/plans/YYYY-MM-DD-<slug>.md" in prompt
    assert "docs/superpowers/specs/YYYY-MM-DD-<slug>.md" in prompt
    assert "sole in-flight plan" in prompt
    assert "ready-to-paste controlled surfaces" in prompt


def test_planning_prompt_refines_existing_plan_without_creating_second(
    monkeypatch,
) -> None:
    monkeypatch.setattr(mco_loop, "_git_output", lambda arguments: "")
    action = NextAction(
        ActionKind.PLAN,
        "Revise the active direction.",
        mco_loop.REPO / "docs/superpowers/plans/existing.md",
        "Write the revised design",
        (),
    )

    prompt = mco_loop.build_prompt(
        action,
        Executor("planner", "codex", "codex", "gpt-5.6-terra"),
        None,
        "plan-2-planner",
    )

    assert "Refine the existing active plan" in prompt
    assert "do not create a second in-flight plan" in prompt


def test_governor_prompt_is_read_only_and_has_bounded_verdicts(monkeypatch) -> None:
    monkeypatch.setattr(mco_loop, "_git_output", lambda arguments: "clean")
    action = NextAction(ActionKind.FIX, "A repeated failure", None, None, ())

    prompt = mco_loop.governor_prompt(action, {"last_failure": "rate_limit"})

    assert "Do not edit files" in prompt
    assert "VERDICT: CONTINUE | FIX | REDIRECT | STOP" in prompt
    assert "without creating a second in-flight plan" in prompt


def test_governor_is_explicit_and_persists_redacted_directive(
    tmp_path: Path, monkeypatch
) -> None:
    config = mco_loop.load_config()
    config = mco_loop.LoopConfig(
        env_file=config.env_file,
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=config.cooldown_seconds,
        iteration_pause_seconds=0,
        planning=config.planning,
        implementation=config.implementation,
    )
    directive = tmp_path / "directive.md"
    monkeypatch.setattr(mco_loop, "FABLE_DIRECTIVE", directive)
    monkeypatch.setattr(
        mco_loop,
        "invoke_mco",
        lambda *args, **kwargs: InvocationResult(
            0,
            "VERDICT: REDIRECT\nDo the safer thing. secret-value",
            "",
            False,
        ),
    )
    action = NextAction(ActionKind.FIX, "stuck", None, None, ())

    result = mco_loop.run_governor(
        config,
        action,
        {"OPENROUTER_API_KEY": "secret-value"},
    )

    assert result == 0
    assert "VERDICT: REDIRECT" in directive.read_text()
    assert "secret-value" not in directive.read_text()


def test_redaction_removes_secret_values() -> None:
    output = mco_loop._redact(
        "failure included secret-value",
        {"OPENROUTER_API_KEY": "secret-value"},
    )

    assert "secret-value" not in output
    assert "OPENROUTER_API_KEY:redacted" in output


def test_artifact_redaction_removes_secret_values(tmp_path: Path) -> None:
    artifact = tmp_path / "nested" / "result.json"
    artifact.parent.mkdir()
    artifact.write_text('{"leak":"secret-value"}')

    mco_loop.redact_artifacts(tmp_path, {"OPENROUTER_API_KEY": "secret-value"})

    assert "secret-value" not in artifact.read_text()


def test_implementation_failover_walks_every_configured_executor(
    tmp_path: Path,
) -> None:
    config = mco_loop.load_config()
    config = mco_loop.LoopConfig(
        env_file=config.env_file,
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=600,
        iteration_pause_seconds=0,
        planning=config.planning,
        implementation=config.implementation,
    )
    state: dict[str, object] = {
        "cooldowns": {},
        "failures": {},
        "last_failure": None,
    }
    selected_names: list[str] = []
    for offset in range(len(config.implementation)):
        selected, _ = mco_loop.available_executor(
            config.implementation, state, now=1000 + offset
        )
        assert selected is not None
        selected_names.append(selected.name)
        mco_loop.apply_result(
            config,
            state,
            selected,
            NextAction(ActionKind.IMPLEMENT, "test", None, "step", ()),
            InvocationResult(2, "backend failed", "", False),
            now=1000 + offset,
        )

    selected, next_ready = mco_loop.available_executor(
        config.implementation, state, now=1010
    )
    assert selected_names == [item.name for item in config.implementation]
    assert selected is None
    assert next_ready == 1600


def test_substantive_failure_routes_next_iteration_to_fix() -> None:
    action = NextAction(ActionKind.IMPLEMENT, "work", None, "step", ())

    fixed = mco_loop.apply_failure_action(
        action,
        {"last_failure": {"kind": "no_progress", "executor": "claude"}},
    )
    unchanged = mco_loop.apply_failure_action(
        action,
        {"last_failure": {"kind": "rate_limit", "executor": "claude"}},
    )

    assert fixed.kind is ActionKind.FIX
    assert unchanged is action


def test_fable_directives_control_routing_without_writing(
    tmp_path: Path, monkeypatch
) -> None:
    directive = tmp_path / "fable.md"
    monkeypatch.setattr(mco_loop, "FABLE_DIRECTIVE", directive)
    action = NextAction(ActionKind.IMPLEMENT, "work", None, "step", ())

    missing, stopped, seen = mco_loop.apply_governor_directive(action)
    assert missing is action
    assert stopped is False
    assert seen is False

    directive.write_text("VERDICT: FIX\n")
    fixed, stopped, seen = mco_loop.apply_governor_directive(action)
    assert fixed.kind is ActionKind.FIX
    assert stopped is False
    assert seen is True

    directive.write_text("VERDICT: REDIRECT\n")
    redirected, stopped, seen = mco_loop.apply_governor_directive(action)
    assert redirected.kind is ActionKind.PLAN
    assert stopped is False
    assert seen is True

    directive.write_text("VERDICT: STOP\n")
    unchanged, stopped, seen = mco_loop.apply_governor_directive(action)
    assert unchanged is action
    assert stopped is True
    assert seen is True

    directive.write_text("VERDICT: CONTINUE\n")
    unchanged, stopped, seen = mco_loop.apply_governor_directive(action)
    assert unchanged is action
    assert stopped is False
    assert seen is True


def test_directive_survives_iteration_it_did_not_route(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directive = tmp_path / "fable-directive.md"
    monkeypatch.setattr(mco_loop, "FABLE_DIRECTIVE", directive)
    config, executor, action = _invocation_inputs(tmp_path)
    progress = InvocationResult(0, "changed", "", True)

    directive.write_text("VERDICT: REDIRECT\n")
    state: dict[str, object] = {"cooldowns": {}, "failures": {}, "last_failure": None}
    mco_loop.apply_result(
        config, state, executor, action, progress, now=100, directive_seen=False
    )
    assert directive.exists(), "mid-iteration directive must survive to route next"

    state = {"cooldowns": {}, "failures": {}, "last_failure": None}
    mco_loop.apply_result(
        config, state, executor, action, progress, now=100, directive_seen=True
    )
    assert not directive.exists(), "directive that routed the iteration is consumed"


def test_completion_requires_pytest_mdtest_and_deterministic_parity(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command, **kwargs):
        calls.append(command)
        result = Result()
        if command[:4] == ["uv", "run", "pytest", "tests/test_mdtest.py"]:
            result.stdout = "23 passed in 1.0s"
        elif "scripts/strict_parity_harness.py" in command:
            result.stdout = "summary: 22/22 byte-identical"
        return result

    monkeypatch.setattr(mco_loop.subprocess, "run", fake_run)
    fixtures = tmp_path / "mdtest" / "Markdown.mdtest"
    fixtures.mkdir(parents=True)
    for index in range(22):
        (fixtures / f"Case {index}.text").write_text("")
    (fixtures / "Auto links.text").write_text("")
    monkeypatch.setattr(mco_loop.Path, "home", lambda: tmp_path)

    complete, detail = mco_loop.completion_gates()

    assert complete is True
    assert "mdtest 23/23" in detail
    assert "22/22" in detail
    assert calls[0] == ["uv", "run", "pytest", "-q"]
    assert calls[1] == ["uv", "run", "pytest", "tests/test_mdtest.py", "-q"]
    assert "Auto links" not in calls[2]


def test_available_executor_preserves_planning_groups() -> None:
    executors = [
        mco_loop.Executor("claude-impl", "claude-sonnet", "claude"),
        mco_loop.Executor("agy-impl", "agy-flash", "agy"),
    ]
    state = {"cooldowns": {}}
    # When preserve_planning=True, agy-impl (index 1) should be chosen over
    # claude-impl (index 0)
    selected, _ = mco_loop.available_executor(
        executors, state, now=100, preserve_planning=True
    )
    assert selected is not None
    assert selected.name == "agy-impl"


def test_available_executor_falls_back_to_preserved_groups() -> None:
    executors = [
        mco_loop.Executor("claude-impl", "claude-sonnet", "claude"),
        mco_loop.Executor("agy-impl", "agy-flash", "agy"),
    ]
    # agy is cooling down, so only claude is available
    state = {"cooldowns": {"agy": 200}}
    selected, _ = mco_loop.available_executor(
        executors, state, now=100, preserve_planning=True
    )
    assert selected is not None
    assert selected.name == "claude-impl"


def test_main_select_executor_preserve_planning_flag(
    monkeypatch, tmp_path: Path
) -> None:
    # Mock files
    roadmap_file = tmp_path / "roadmap.md"
    roadmap_file.write_text("")
    monkeypatch.setattr(mco_loop, "ROADMAP", roadmap_file)

    blockers_file = tmp_path / "blockers.md"
    monkeypatch.setattr(mco_loop, "BLOCKERS", blockers_file)

    monkeypatch.setattr(mco_loop, "FABLE_DIRECTIVE", tmp_path / "fable-directive.md")

    # Mock config
    config = mco_loop.LoopConfig(
        env_file=tmp_path / ".env",
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=600,
        iteration_pause_seconds=0,
        planning=(),
        implementation=(),
    )
    monkeypatch.setattr(mco_loop, "load_config", lambda *args, **kwargs: config)

    # Mock parse_roadmap to return a pending row so loop doesn't complete immediately
    monkeypatch.setattr(
        mco_loop,
        "parse_roadmap",
        lambda text: (mco_loop.RoadmapRow("1", None, "description", "pending"),),
    )
    monkeypatch.setattr(
        mco_loop, "reconciliation_action", lambda rows, repo=mco_loop.REPO: None
    )

    # Track calls to select_executor
    calls = []

    def fake_select_executor(pool, state, action, now, preserve_planning=False):
        calls.append((pool, state, action, now, preserve_planning))
        return mco_loop.ExecutorSelection(None, None, True)

    monkeypatch.setattr(mco_loop, "select_executor", fake_select_executor)

    # 1. ActionKind.PLAN -> preserve_planning should be False
    monkeypatch.setattr(
        mco_loop,
        "determine_next_action",
        lambda rows, blockers: mco_loop.NextAction(
            mco_loop.ActionKind.PLAN, "plan stuff", None, None, ()
        ),
    )
    mco_loop.main(["--status"])
    assert len(calls) == 1
    assert calls[0][4] is False

    # 2. ActionKind.IMPLEMENT -> preserve_planning should be True
    calls.clear()
    monkeypatch.setattr(
        mco_loop,
        "determine_next_action",
        lambda rows, blockers: mco_loop.NextAction(
            mco_loop.ActionKind.IMPLEMENT, "implement stuff", None, None, ()
        ),
    )
    mco_loop.main(["--status"])
    assert len(calls) == 1
    assert calls[0][4] is True

    # 3. ActionKind.FIX -> preserve_planning should be True
    calls.clear()
    monkeypatch.setattr(
        mco_loop,
        "determine_next_action",
        lambda rows, blockers: mco_loop.NextAction(
            mco_loop.ActionKind.FIX, "fix stuff", None, None, ()
        ),
    )
    mco_loop.main(["--status"])
    assert len(calls) == 1
    assert calls[0][4] is True


class _FakeCompletedProcess:
    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def test_ensure_git_hooks_noop_when_already_active(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> _FakeCompletedProcess:
        calls.append(cmd)
        return _FakeCompletedProcess(stdout=".githooks\n")

    monkeypatch.setattr(mco_loop.subprocess, "run", fake_run)
    assert mco_loop.ensure_git_hooks(tmp_path) is None
    assert len(calls) == 1
    assert calls[0][-1] == "core.hooksPath"


def test_ensure_git_hooks_activates_when_unset(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> _FakeCompletedProcess:
        calls.append(cmd)
        if cmd[-1] == ".githooks":
            return _FakeCompletedProcess(returncode=0)
        return _FakeCompletedProcess(stdout="", returncode=1)

    monkeypatch.setattr(mco_loop.subprocess, "run", fake_run)
    message = mco_loop.ensure_git_hooks(tmp_path)
    assert message is not None and "activated .githooks" in message
    assert calls[-1][-2:] == ["core.hooksPath", ".githooks"]


def test_ensure_git_hooks_reports_activation_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> _FakeCompletedProcess:
        if cmd[-1] == ".githooks":
            return _FakeCompletedProcess(stderr="permission denied", returncode=1)
        return _FakeCompletedProcess(stdout="", returncode=1)

    monkeypatch.setattr(mco_loop.subprocess, "run", fake_run)
    message = mco_loop.ensure_git_hooks(tmp_path)
    assert message is not None and "could not set core.hooksPath" in message
    assert "permission denied" in message


def test_read_blockers_includes_plan_tagged_lines(tmp_path: Path) -> None:
    path = tmp_path / "blockers.md"
    path.write_text(
        "# Blockers\n"
        "- BLOCK: broken contract\n"
        "- BLOCK[plan]: step 5 needs a planning amendment\n"
        "unrelated prose\n"
    )

    assert mco_loop.read_blockers(path) == (
        "- BLOCK: broken contract",
        "- BLOCK[plan]: step 5 needs a planning amendment",
    )


def test_parse_branch_blocker_accepts_valid_structured_line() -> None:
    line = (
        "- BLOCK[plan]: branch=topic; "
        "head=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
        "base=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
        "request=review; detail=Need disposition."
    )

    assert mco_loop.parse_branch_blocker(line) == mco_loop.BranchBlocker(
        "topic",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "review",
        "Need disposition.",
    )


def test_parse_branch_blocker_rejects_missing_field() -> None:
    line = (
        "- BLOCK[plan]: branch=topic; "
        "head=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
        "base=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
        "request=review"
    )

    assert mco_loop.parse_branch_blocker(line) is None


def test_invalid_branch_blockers_rejects_invalid_request(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    line = (
        "- BLOCK[plan]: branch=topic; "
        "head=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
        "base=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
        "request=punt; detail=Need disposition."
    )
    monkeypatch.setattr(mco_loop, "_git_output", lambda args, repo=tmp_path: "")

    failures = mco_loop.invalid_branch_blockers((line,), repo=tmp_path)

    assert len(failures) == 1
    assert "request" in failures[0]


def test_invalid_branch_blockers_rejects_branch_head_and_base_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    line = (
        "- BLOCK[plan]: branch=topic; "
        "head=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; "
        "base=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb; "
        "request=supersede; detail=Need disposition."
    )
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: {
            ("rev-parse", "topic"): "cccccccccccccccccccccccccccccccccccccccc\n",
            (
                "merge-base",
                "topic",
                "main",
            ): "dddddddddddddddddddddddddddddddddddddddd\n",
        }.get(tuple(args), ""),
    )

    failures = mco_loop.invalid_branch_blockers((line,), repo=tmp_path)

    assert len(failures) == 2
    assert any("head" in failure for failure in failures)
    assert any("base" in failure for failure in failures)


def test_invalid_branch_blockers_preserves_legacy_planning_blocker(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    line = "- BLOCK[plan]: scanner needs a planning amendment"
    monkeypatch.setattr(mco_loop, "_git_output", lambda args, repo=tmp_path: "")

    assert mco_loop.invalid_branch_blockers((line,), repo=tmp_path) == ()


def test_unregistered_planning_artifacts_returns_empty_when_none_found(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mco_loop, "_git_output", lambda args, repo=tmp_path: "")

    assert mco_loop.unregistered_planning_artifacts(tmp_path) == ()


def test_unregistered_planning_artifacts_reports_untracked_plan_and_spec(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: (
            "docs/superpowers/specs/example.md\n"
            "README.md\n"
            "docs/superpowers/plans/example.md\n"
        ),
    )

    assert mco_loop.unregistered_planning_artifacts(tmp_path) == (
        tmp_path / "docs/superpowers/plans/example.md",
        tmp_path / "docs/superpowers/specs/example.md",
    )


def test_unregistered_planning_artifacts_excludes_ignored_agent_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        mco_loop,
        "_git_output",
        lambda args, repo=tmp_path: (
            "docs/superpowers/plans/example.md\n.agent/mco-loop-state.json\n"
        ),
    )

    assert mco_loop.unregistered_planning_artifacts(tmp_path) == (
        tmp_path / "docs/superpowers/plans/example.md",
    )


def test_plan_tagged_blocker_routes_to_planning(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] Implement it\n")

    action = mco_loop.determine_next_action(
        [_row("4S", "in flight", plan)],
        ["- BLOCK[plan]: scanner needs a planning amendment"],
    )

    assert action.kind is ActionKind.PLAN
    assert action.active_plan == plan
    assert action.blockers == ("- BLOCK[plan]: scanner needs a planning amendment",)


def test_blocker_escalation_walks_normal_escalate_halt() -> None:
    state: dict[str, object] = {"blocker_escalation": None}
    blockers = ("- BLOCK[plan]: same blocker",)

    assert mco_loop.blocker_escalation_phase(state, ()) == "none"
    assert mco_loop.blocker_escalation_phase(state, blockers) == "normal"
    for _ in range(mco_loop.BLOCKER_ESCALATION_THRESHOLD):
        mco_loop.record_blocker_attempt(state, blockers, "blocked", escalated=False)
    assert mco_loop.blocker_escalation_phase(state, blockers) == "escalate"

    mco_loop.record_blocker_attempt(state, blockers, "progress", escalated=True)
    assert mco_loop.blocker_escalation_phase(state, blockers) == "halt"

    changed = ("- BLOCK: a different blocker",)
    assert mco_loop.blocker_escalation_phase(state, changed) == "normal"
    mco_loop.record_blocker_attempt(state, (), "progress", escalated=False)
    assert state["blocker_escalation"] is None


def test_availability_failures_do_not_advance_blocker_escalation() -> None:
    state: dict[str, object] = {"blocker_escalation": None}
    blockers = ("- BLOCK[plan]: same blocker",)

    for outcome in ("rate_limit", "transient", "supervisor_timeout"):
        mco_loop.record_blocker_attempt(state, blockers, outcome, escalated=False)

    assert state["blocker_escalation"] is None
    assert mco_loop.blocker_escalation_phase(state, blockers) == "normal"


def test_load_state_preserves_blocker_escalation(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    record = {"signature": "abc", "count": 3, "escalated": False}
    path.write_text(json.dumps({"blocker_escalation": record}))

    assert mco_loop.load_state(path)["blocker_escalation"] == record
    assert mco_loop.load_state(tmp_path / "missing.json")["blocker_escalation"] is None


def test_live_config_escalation_tier_is_terra_then_opus_without_fable() -> None:
    config = mco_loop.load_config()

    assert [(item.provider, item.model) for item in config.escalation] == [
        ("codex", "gpt-5.6-terra"),
        ("claude-opus", None),
    ]
    assert all("fable" not in item.provider for item in config.escalation)


def _escalation_main_setup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    escalated: bool,
    preseeded: bool = True,
) -> tuple[mco_loop.LoopConfig, tuple[Executor, ...]]:
    escalation = (Executor("claude-opus-escalate", "claude-opus", "claude"),)
    config = mco_loop.LoopConfig(
        env_file=tmp_path / ".env",
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=60,
        iteration_pause_seconds=0,
        planning=(Executor("sonnet-plan", "claude-sonnet", "claude"),),
        implementation=(Executor("claude", "claude", "claude"),),
        escalation=escalation,
    )
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text("ignored")
    plan = tmp_path / "plan.md"
    plan.write_text("- [ ] step\n")
    blockers = ("- BLOCK[plan]: scanner needs a planning amendment",)
    mco_loop.save_state(
        config.state_file,
        {
            "cooldowns": {},
            "failures": {},
            "last_failure": None,
            "action_attempt": None,
            "exhaustion": None,
            "blocker_escalation": {
                "signature": mco_loop.blocker_signature(blockers),
                "count": mco_loop.BLOCKER_ESCALATION_THRESHOLD,
                "escalated": escalated,
            }
            if preseeded
            else None,
        },
    )
    monkeypatch.setattr(mco_loop, "REPO", tmp_path)
    monkeypatch.setattr(mco_loop, "ROADMAP", roadmap)
    monkeypatch.setattr(mco_loop, "FABLE_DIRECTIVE", tmp_path / "directive.md")
    monkeypatch.setattr(
        mco_loop, "load_config", lambda path=mco_loop.DEFAULT_CONFIG: config
    )
    monkeypatch.setattr(mco_loop.shutil, "which", lambda name: "/bin/mco")
    monkeypatch.setattr(mco_loop, "load_named_secrets", lambda path: {})
    monkeypatch.setattr(
        mco_loop, "parse_roadmap", lambda text: (_row("4S", "in flight", plan),)
    )
    monkeypatch.setattr(
        mco_loop, "read_blockers", lambda path=mco_loop.BLOCKERS: blockers
    )
    return config, escalation


def test_main_routes_persistent_blocker_to_escalation_pool(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    _, escalation = _escalation_main_setup(tmp_path, monkeypatch, escalated=False)
    pools: list[tuple[Executor, ...]] = []

    def fake_select(executors, state, action, now, preserve_planning=False):
        pools.append(tuple(executors))
        return mco_loop.ExecutorSelection(None, None, True)

    monkeypatch.setattr(mco_loop, "select_executor", fake_select)

    assert mco_loop.main(["--once"]) == 5
    assert pools == [escalation]
    capsys.readouterr()


def test_main_halts_for_operator_after_failed_escalated_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    _escalation_main_setup(tmp_path, monkeypatch, escalated=True)

    def fail_select(*args, **kwargs):
        raise AssertionError("halt must occur before executor selection")

    monkeypatch.setattr(mco_loop, "select_executor", fail_select)

    assert mco_loop.main(["--once"]) == 6
    assert "operator" in capsys.readouterr().err


def test_main_escalates_after_three_substantive_blocked_iterations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """The counter must accumulate through real iterations, not pre-seeded state:
    three substantive blocked attempts, then escalation, then operator halt."""
    config, escalation = _escalation_main_setup(
        tmp_path, monkeypatch, escalated=False, preseeded=False
    )
    pools: list[tuple[Executor, ...]] = []

    def fake_select(executors, state, action, now, preserve_planning=False):
        pools.append(tuple(executors))
        return mco_loop.ExecutorSelection(executors[0], None, False)

    def fake_invoke(cfg, executor, action, environment):
        return mco_loop.InvocationResult(
            exit_code=0,
            stdout="",
            stderr="",
            made_progress=False,
            recorded_blocker=True,
        )

    monkeypatch.setattr(mco_loop, "select_executor", fake_select)
    monkeypatch.setattr(mco_loop, "invoke_mco", fake_invoke)

    for iteration in range(mco_loop.BLOCKER_ESCALATION_THRESHOLD):
        assert mco_loop.main(["--once"]) == 0, f"iteration {iteration}"
        assert pools[-1] == config.planning

    assert mco_loop.main(["--once"]) == 0
    assert pools[-1] == escalation

    assert mco_loop.main(["--once"]) == 6
    assert len(pools) == mco_loop.BLOCKER_ESCALATION_THRESHOLD + 1
    assert "operator" in capsys.readouterr().err


def test_prompt_teaches_plan_tagged_blocker_lines(monkeypatch) -> None:
    monkeypatch.setattr(mco_loop, "_git_output", lambda arguments: "")
    action = NextAction(ActionKind.IMPLEMENT, "work", None, "step", ())
    executor = Executor("claude", "claude", "claude")

    prompt = mco_loop.build_prompt(action, executor, None, "invocation-1")

    assert "- BLOCK[plan]:" in prompt


def test_governor_runs_on_escalation_tier_not_fable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, Executor] = {}

    def fake_invoke(config, executor, action, environment, prompt_override=None):
        captured["executor"] = executor
        return InvocationResult(0, "VERDICT: CONTINUE\n", "", False)

    monkeypatch.setattr(mco_loop, "invoke_mco", fake_invoke)
    monkeypatch.setattr(mco_loop, "FABLE_DIRECTIVE", tmp_path / "directive.md")
    config = mco_loop.LoopConfig(
        env_file=tmp_path / ".env",
        state_file=tmp_path / "state.json",
        artifact_dir=tmp_path / "artifacts",
        cooldown_seconds=60,
        iteration_pause_seconds=0,
        planning=(Executor("sonnet-plan", "claude-sonnet", "claude"),),
        implementation=(Executor("claude", "claude", "claude"),),
        escalation=(
            Executor("codex-terra-escalate", "codex", "codex", model="gpt-5.6-terra"),
        ),
    )
    action = NextAction(ActionKind.FIX, "stuck", None, None, ())

    assert mco_loop.run_governor(config, action, {}) == 0
    assert captured["executor"].name == "codex-terra-escalate"
    assert captured["executor"].provider != "claude-fable"
