from __future__ import annotations

import json
from pathlib import Path

from scripts import mco_loop
from scripts.mco_loop import (
    ActionKind,
    Executor,
    InvocationResult,
    NextAction,
    RoadmapRow,
)


def _row(
    identifier: str,
    status: str,
    plan_path: Path | None = None,
    description: str = "A plan",
) -> RoadmapRow:
    return RoadmapRow(identifier, plan_path, description, status)


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
        "agy-flash",
        "claude-opus",
        "codex",
        "agy-pro",
        "pi",
        "pi",
    ]
    assert [(item.model_provider, item.model) for item in config.implementation] == [
        (None, None),
        (None, "gpt-5.4"),
        (None, None),
        (None, None),
        (None, "gpt-5.6-sol"),
        (None, None),
        ("xai", "grok-build-0.1"),
        ("openrouter", "tencent/hy3:free"),
    ]
    assert config.planning[2].display_model == "opus"
    assert config.implementation[0].display_model == "sonnet"
    assert not {"agy-flash", "agy-pro", "pi"} & {
        item.provider for item in config.planning
    }
    assert all(item.provider != "claude-fable" for item in config.planning)
    assert all(item.provider != "claude-fable" for item in config.implementation)


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
        "OPENROUTER_API_KEY=or-secret\n"
        "XAI_API_KEY='xai-secret'\n"
        "UNRELATED_SECRET=must-not-load\n"
    )

    result = mco_loop.load_named_secrets(env_file, {"PATH": "/bin"})

    assert result["OPENROUTER_API_KEY"] == "or-secret"
    assert result["XAI_API_KEY"] == "xai-secret"
    assert "UNRELATED_SECRET" not in result


def test_exported_secret_takes_precedence_over_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("XAI_API_KEY=file-value\n")

    result = mco_loop.load_named_secrets(env_file, {"XAI_API_KEY": "exported-value"})

    assert result["XAI_API_KEY"] == "exported-value"


def test_mco_argv_contains_model_policy_but_no_secret_values(tmp_path: Path) -> None:
    config = mco_loop.load_config()
    prompt = tmp_path / "prompt.md"
    executor = config.implementation[-1]

    command = mco_loop.mco_command(config, executor, "task", prompt)

    joined = " ".join(command)
    assert "tencent/hy3:free" in joined
    assert "openrouter" in joined
    assert "or-secret" not in joined
    assert "OPENROUTER_API_KEY" not in joined
    assert command[command.index("--max-provider-parallelism") + 1] == "1"


def test_rate_limit_cools_quota_group_and_selects_next_executor(
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
    first = config.implementation[0]
    result = InvocationResult(2, '{"error_kind":"retryable_rate_limit"}', "", False)

    failure = mco_loop.apply_result(config, state, first, result, now=1000)
    selected, _ = mco_loop.available_executor(config.implementation, state, now=1001)

    assert failure == "rate_limit"
    assert selected == config.implementation[1]
    saved = json.loads(config.state_file.read_text())
    assert saved["cooldowns"]["claude"] == 1600


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
    )

    assert "Implement the parser" in prompt
    assert "M src/example.py" in prompt
    assert "rate_limit" in prompt
    assert "private conversation" not in prompt
    assert "Work on one step only" in prompt
    assert "Agent: claude" in prompt
    assert "Model: sonnet" in prompt
    assert "Harness: MCO 0.10.8" in prompt


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
        {"XAI_API_KEY": "secret-value"},
    )

    assert result == 0
    assert "VERDICT: REDIRECT" in directive.read_text()
    assert "secret-value" not in directive.read_text()


def test_redaction_removes_secret_values() -> None:
    output = mco_loop._redact(
        "failure included secret-value",
        {"XAI_API_KEY": "secret-value"},
    )

    assert "secret-value" not in output
    assert "XAI_API_KEY:redacted" in output


def test_artifact_redaction_removes_secret_values(tmp_path: Path) -> None:
    artifact = tmp_path / "nested" / "result.json"
    artifact.parent.mkdir()
    artifact.write_text('{"leak":"secret-value"}')

    mco_loop.redact_artifacts(tmp_path, {"XAI_API_KEY": "secret-value"})

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

    directive.write_text("VERDICT: FIX\n")
    fixed, stopped = mco_loop.apply_governor_directive(action)
    assert fixed.kind is ActionKind.FIX
    assert stopped is False

    directive.write_text("VERDICT: REDIRECT\n")
    redirected, stopped = mco_loop.apply_governor_directive(action)
    assert redirected.kind is ActionKind.PLAN
    assert stopped is False

    directive.write_text("VERDICT: STOP\n")
    unchanged, stopped = mco_loop.apply_governor_directive(action)
    assert unchanged is action
    assert stopped is True

    directive.write_text("VERDICT: CONTINUE\n")
    unchanged, stopped = mco_loop.apply_governor_directive(action)
    assert unchanged is action
    assert stopped is False


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


def test_main_available_executor_preserve_planning_flag(monkeypatch, tmp_path) -> None:
    # Mock files
    roadmap_file = tmp_path / "roadmap.md"
    roadmap_file.write_text("")
    monkeypatch.setattr(mco_loop, "ROADMAP", roadmap_file)

    blockers_file = tmp_path / "blockers.md"
    monkeypatch.setattr(mco_loop, "BLOCKERS", blockers_file)

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

    # Track calls to available_executor
    calls = []

    def fake_available_executor(pool, state, now, preserve_planning=False):
        calls.append((pool, state, now, preserve_planning))
        return None, None

    monkeypatch.setattr(mco_loop, "available_executor", fake_available_executor)

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
    assert calls[0][3] is False

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
    assert calls[0][3] is True

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
    assert calls[0][3] is True
