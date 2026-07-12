"""MCO-backed autonomous executor for Shakedown's plan roadmap."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import cast

REPO = Path(__file__).parent.parent
DEFAULT_CONFIG = REPO / "agent-loop.toml"
ROADMAP = REPO / "docs" / "superpowers" / "plans" / "plan-roadmap.md"
BLOCKERS = REPO / ".agent" / "blockers.md"
FABLE_DIRECTIVE = REPO / ".agent" / "fable-directive.md"
ALLOWED_SECRET_NAMES = ("XAI_API_KEY", "OPENROUTER_API_KEY")
PRESERVED_PLANNING_GROUPS = {"claude", "codex"}
TRUSTED_RETRY_GROUPS = {"claude", "codex"}
RATE_LIMIT_MARKERS = (
    "retryable_rate_limit",
    "rate_limit",
    "rate limit",
    "usage limit",
    "too many requests",
    "http 429",
)
TRANSIENT_MARKERS = (
    "retryable_timeout",
    "retryable_transient_network",
    "timed out",
    "service unavailable",
)
MCO_TIMEOUT_SECONDS = 18000


class ActionKind(Enum):
    PLAN = "plan"
    IMPLEMENT = "implement"
    FIX = "fix"


@dataclass(frozen=True)
class Executor:
    name: str
    provider: str
    quota_group: str
    model: str | None = None
    model_provider: str | None = None
    display_model: str | None = None
    best_effort: bool = False
    coauthor_name: str | None = None
    coauthor_email: str | None = None


@dataclass(frozen=True)
class LoopConfig:
    env_file: Path
    state_file: Path
    artifact_dir: Path
    cooldown_seconds: int
    iteration_pause_seconds: int
    planning: tuple[Executor, ...]
    implementation: tuple[Executor, ...]


@dataclass(frozen=True)
class RoadmapRow:
    identifier: str
    plan_path: Path | None
    description: str
    status: str


@dataclass(frozen=True)
class NextAction:
    kind: ActionKind
    summary: str
    active_plan: Path | None
    step: str | None
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class InvocationResult:
    exit_code: int
    stdout: str
    stderr: str
    made_progress: bool
    recorded_blocker: bool = False

    @property
    def combined_output(self) -> str:
        return f"{self.stdout}\n{self.stderr}"


@dataclass(frozen=True)
class ExecutorSelection:
    executor: Executor | None
    next_ready: int | None
    exhausted: bool


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a table")
    return cast(Mapping[str, object], value)


def _string(
    table: Mapping[str, object], key: str, *, required: bool = True
) -> str | None:
    value = table.get(key)
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _integer(table: Mapping[str, object], key: str) -> int:
    value = table.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{key} must be a non-negative integer")
    return value


def _boolean(table: Mapping[str, object], key: str) -> bool:
    value = table.get(key, False)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _resolve_repo_path(value: str) -> Path:
    expanded = Path(value).expanduser()
    return expanded if expanded.is_absolute() else REPO / expanded


def _executors(raw: object, label: str) -> tuple[Executor, ...]:
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{label} must contain at least one executor")
    result: list[Executor] = []
    for index, item in enumerate(raw):
        table = _mapping(item, f"{label}[{index}]")
        result.append(
            Executor(
                name=cast(str, _string(table, "name")),
                provider=cast(str, _string(table, "provider")),
                quota_group=cast(str, _string(table, "quota_group")),
                model=_string(table, "model", required=False),
                model_provider=_string(table, "model_provider", required=False),
                display_model=_string(table, "display_model", required=False),
                best_effort=_boolean(table, "best_effort"),
                coauthor_name=_string(table, "coauthor_name", required=False),
                coauthor_email=_string(table, "coauthor_email", required=False),
            )
        )
    names = [executor.name for executor in result]
    if len(names) != len(set(names)):
        raise ValueError(f"{label} executor names must be unique")
    return tuple(result)


def load_config(path: Path = DEFAULT_CONFIG) -> LoopConfig:
    """Load and validate the project-local loop policy."""
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    table = _mapping(raw, "config")
    loop = _mapping(table.get("loop"), "loop")
    return LoopConfig(
        env_file=_resolve_repo_path(cast(str, _string(loop, "env_file"))),
        state_file=_resolve_repo_path(cast(str, _string(loop, "state_file"))),
        artifact_dir=_resolve_repo_path(cast(str, _string(loop, "artifact_dir"))),
        cooldown_seconds=_integer(loop, "cooldown_seconds"),
        iteration_pause_seconds=_integer(loop, "iteration_pause_seconds"),
        planning=_executors(table.get("planning"), "planning"),
        implementation=_executors(table.get("implementation"), "implementation"),
    )


def parse_roadmap(text: str) -> tuple[RoadmapRow, ...]:
    """Parse live plan rows from the roadmap's Markdown table."""
    rows: list[RoadmapRow] = []
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] in {"#", ""}:
            continue
        status = cells[-1].lower()
        if not any(
            word in status
            for word in ("pending", "in flight", "shipped", "halted", "superseded")
        ):
            continue
        matches = re.findall(r"`(docs/superpowers/plans/[^`]+\.md)`", line)
        plan_path = REPO / matches[0] if matches else None
        rows.append(
            RoadmapRow(
                identifier=cells[0],
                plan_path=plan_path,
                description=cells[1],
                status=status,
            )
        )
    return tuple(rows)


def read_blockers(path: Path = BLOCKERS) -> tuple[str, ...]:
    """Return active blocker lines without modifying the blocker file."""
    try:
        lines = path.read_text().splitlines()
    except FileNotFoundError:
        return ()
    return tuple(line.strip() for line in lines if line.lstrip().startswith("- BLOCK:"))


def first_unchecked_step(plan_text: str) -> str | None:
    """Return the first unchecked plan checkbox in document order."""
    match = re.search(r"^- \[ \] (.+)$", plan_text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def step_is_planning(step: str) -> bool:
    """Return whether a checkbox explicitly authors a plan/design surface."""
    lowered = step.lower()
    patterns = (
        r"\bwrite\b.*\b(plan|design|specification)\b",
        r"\bauthor\b.*\b(plan|design|specification)\b",
        r"\breserve\b.*\bliterary\b",
        r"\bready-to-paste literary\b",
    )
    return any(re.search(pattern, lowered) for pattern in patterns)


def determine_next_action(
    rows: Sequence[RoadmapRow], blockers: Sequence[str]
) -> NextAction:
    """Classify the next durable repository action."""
    in_flight = [row for row in rows if "in flight" in row.status]
    pending = [row for row in rows if "pending" in row.status]
    if len(in_flight) > 1:
        raise ValueError("roadmap has more than one in-flight plan")
    if blockers:
        active = in_flight[0].plan_path if in_flight else None
        return NextAction(
            ActionKind.FIX,
            "Resolve the active blocker before roadmap work continues.",
            active,
            None,
            tuple(blockers),
        )
    if not in_flight:
        if pending:
            target = pending[0]
            return NextAction(
                ActionKind.PLAN,
                (
                    "Write and register the implementation plan for roadmap row "
                    f"{target.identifier}: {target.description}."
                ),
                None,
                None,
                (),
            )
        return NextAction(
            ActionKind.FIX,
            (
                "All roadmap rows are terminal; prove the full-suite and "
                "23-fixture completion gates."
            ),
            None,
            None,
            (),
        )
    row = in_flight[0]
    if row.plan_path is None or not row.plan_path.exists():
        return NextAction(
            ActionKind.FIX,
            f"Repair the missing plan path for in-flight roadmap row {row.identifier}.",
            row.plan_path,
            None,
            (),
        )
    step = first_unchecked_step(row.plan_path.read_text())
    if step is None:
        return NextAction(
            ActionKind.FIX,
            (
                f"Finalize roadmap row {row.identifier}: its plan has no unchecked "
                "steps but remains in flight."
            ),
            row.plan_path,
            None,
            (),
        )
    kind = ActionKind.PLAN if step_is_planning(step) else ActionKind.IMPLEMENT
    return NextAction(
        kind,
        f"Execute the first unchecked step in roadmap row {row.identifier}.",
        row.plan_path,
        step,
        (),
    )


def load_named_secrets(
    path: Path, base_env: Mapping[str, str] | None = None
) -> dict[str, str]:
    """Load only approved API keys, preserving already-exported values."""
    result = dict(os.environ if base_env is None else base_env)
    try:
        lines = path.read_text().splitlines()
    except FileNotFoundError:
        return result
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        name, separator, value = line.partition("=")
        name = name.strip()
        if separator and name in ALLOWED_SECRET_NAMES and name not in result:
            result[name] = value.strip().strip("'\"")
    return result


def load_state(path: Path) -> dict[str, object]:
    """Load persisted non-secret supervisor state."""
    try:
        value = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"cooldowns": {}, "failures": {}, "last_failure": None}
    if not isinstance(value, dict):
        return {"cooldowns": {}, "failures": {}, "last_failure": None}
    state = cast(dict[str, object], value)
    action_attempt = state.get("action_attempt")
    exhaustion = state.get("exhaustion")
    return {
        "cooldowns": state.get("cooldowns", {}),
        "failures": state.get("failures", {}),
        "last_failure": state.get("last_failure"),
        "action_attempt": action_attempt if isinstance(action_attempt, dict) else None,
        "exhaustion": exhaustion if isinstance(exhaustion, dict) else None,
    }


def save_state(path: Path, state: Mapping[str, object]) -> None:
    """Persist state atomically without secrets."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(dict(state), indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def available_executor(
    executors: Sequence[Executor],
    state: Mapping[str, object],
    now: int,
    preserve_planning: bool = False,
) -> tuple[Executor | None, int | None]:
    """Return the first executor whose quota group is not cooling down."""
    raw_cooldowns = state.get("cooldowns", {})
    cooldowns = (
        cast(Mapping[str, object], raw_cooldowns)
        if isinstance(raw_cooldowns, dict)
        else {}
    )

    def get_cooldown_expiry(exe: Executor) -> int:
        group_value = cooldowns.get(exe.quota_group, 0)
        executor_value = cooldowns.get(f"executor:{exe.name}", 0)
        group_until = int(group_value) if isinstance(group_value, int | float) else 0
        executor_until = (
            int(executor_value) if isinstance(executor_value, int | float) else 0
        )
        return max(group_until, executor_until)

    expiries = [(executor, get_cooldown_expiry(executor)) for executor in executors]

    # Pass 1: prioritize executors whose quota groups are NOT in
    # PRESERVED_PLANNING_GROUPS
    if preserve_planning:
        for executor, until in expiries:
            if executor.quota_group in PRESERVED_PLANNING_GROUPS:
                continue
            if until <= now:
                return executor, None

    # Pass 2: Fall back to checking all executors (including preserved groups)
    waits: list[int] = []
    for executor, until in expiries:
        if until <= now:
            return executor, None
        waits.append(until)

    return None, min(waits) if waits else None


def action_key(action: NextAction) -> str:
    """Hash the canonical durable routing fields for one roadmap action."""
    active_plan: str | None = None
    if action.active_plan is not None:
        try:
            active_plan = str(action.active_plan.relative_to(REPO))
        except ValueError:
            active_plan = str(action.active_plan)
    payload = {
        "kind": action.kind.value,
        "summary": action.summary,
        "active_plan": active_plan,
        "step": action.step,
        "blockers": list(action.blockers),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def select_executor(
    executors: Sequence[Executor],
    state: Mapping[str, object],
    action: NextAction,
    now: int,
    preserve_planning: bool = False,
) -> ExecutorSelection:
    """Select, wait for trusted availability, or exhaust one action's pool."""
    raw_cooldowns = state.get("cooldowns", {})
    cooldowns = (
        cast(Mapping[str, object], raw_cooldowns)
        if isinstance(raw_cooldowns, dict)
        else {}
    )
    attempts: Mapping[str, object] = {}
    raw_attempt = state.get("action_attempt")
    if isinstance(raw_attempt, dict) and raw_attempt.get("key") == action_key(action):
        raw_attempts = raw_attempt.get("attempts", {})
        if isinstance(raw_attempts, dict):
            attempts = cast(Mapping[str, object], raw_attempts)

    def expiry(executor: Executor) -> int:
        group = cooldowns.get(executor.quota_group, 0)
        own = cooldowns.get(f"executor:{executor.name}", 0)
        group_until = int(group) if isinstance(group, int | float) else 0
        own_until = int(own) if isinstance(own, int | float) else 0
        return max(group_until, own_until)

    # Compatibility argument retained for callers/status tests. Executor order
    # is policy: Pi models are last-resort and must not leapfrog trusted models.
    _ = preserve_planning
    ordered = list(executors)

    unattempted = [item for item in ordered if item.name not in attempts]
    for executor in unattempted:
        if expiry(executor) <= now:
            return ExecutorSelection(executor, None, False)

    # Substantive failures always add an attempt with the executor cooldown, so
    # an unattempted executor can only be waiting on an availability cooldown.
    trusted_waits = [
        expiry(executor)
        for executor in unattempted
        if executor.quota_group in TRUSTED_RETRY_GROUPS and expiry(executor) > now
    ]
    if trusted_waits:
        return ExecutorSelection(None, min(trusted_waits), False)
    return ExecutorSelection(None, None, True)


def exhaustion_payload(
    action: NextAction,
    executors: Sequence[Executor],
    state: Mapping[str, object],
    now: int,
) -> dict[str, object]:
    """Build a secret-free durable diagnostic for terminal pool exhaustion."""
    raw_attempt = state.get("action_attempt")
    attempts: Mapping[str, object] = {}
    if isinstance(raw_attempt, dict) and raw_attempt.get("key") == action_key(action):
        raw_attempts = raw_attempt.get("attempts", {})
        if isinstance(raw_attempts, dict):
            attempts = cast(Mapping[str, object], raw_attempts)
    raw_cooldowns = state.get("cooldowns", {})
    cooldowns = (
        cast(Mapping[str, object], raw_cooldowns)
        if isinstance(raw_cooldowns, dict)
        else {}
    )
    active_cooldowns = {
        key: int(value)
        for key, value in cooldowns.items()
        if isinstance(key, str)
        and isinstance(value, int | float)
        and int(value) > now
    }
    active_plan: str | None = None
    if action.active_plan is not None:
        try:
            active_plan = str(action.active_plan.relative_to(REPO))
        except ValueError:
            active_plan = str(action.active_plan)
    return {
        "kind": "executor_exhaustion",
        "action_key": action_key(action),
        "action": {
            "kind": action.kind.value,
            "summary": action.summary,
            "active_plan": active_plan,
            "step": action.step,
            "blockers": list(action.blockers),
        },
        "attempts": dict(attempts),
        "active_cooldowns": active_cooldowns,
        "trusted_retry_candidates": [],
        "configured_executors": [executor.name for executor in executors],
        "next_ready": None,
        "recorded_at": now,
    }


def _git_output(arguments: Sequence[str]) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


def repo_fingerprint() -> str:
    """Hash tracked diffs plus untracked content, excluding ignored state."""
    digest = hashlib.sha256()
    digest.update(_git_output(["rev-parse", "HEAD"]).encode())
    digest.update(_git_output(["diff", "--binary", "HEAD", "--", "."]).encode())
    untracked = _git_output(["ls-files", "--others", "--exclude-standard"])
    for relative in sorted(untracked.splitlines()):
        if relative.startswith(".agent/"):
            continue
        path = REPO / relative
        digest.update(relative.encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def build_prompt(action: NextAction, executor: Executor, last_failure: object) -> str:
    """Build a provider-neutral handoff from durable repository state."""
    plan_text = (
        str(action.active_plan.relative_to(REPO)) if action.active_plan else "none"
    )
    blockers = "\n".join(action.blockers) if action.blockers else "none"
    status = (
        _git_output(["status", "--short", "--untracked-files=all"]).strip() or "clean"
    )
    try:
        governor_directive = FABLE_DIRECTIVE.read_text()[-6000:]
    except FileNotFoundError:
        governor_directive = "none"
    if action.kind is ActionKind.PLAN:
        plan_destination = (
            "Refine the existing active plan at the exact path above and amend "
            "its cited Superpowers spec when needed; do not create a second "
            "in-flight plan."
            if action.active_plan
            else (
                "Write a complete Superpowers-style plan at "
                "docs/superpowers/plans/YYYY-MM-DD-<slug>.md with checkboxes and "
                "evidence gates, then update the roadmap with that exact path as "
                "the sole in-flight plan."
            )
        )
        role_rule = (
            "This is non-interactive planning work. Do not implement production "
            "behavior and do not wait for human input. "
            f"{plan_destination} Write any prerequisite accepted design under "
            "docs/superpowers/specs/YYYY-MM-DD-<slug>.md. For SPL-facing work, "
            "obey the literary protocol, reserve ready-to-paste controlled "
            "surfaces plus spares, and name exact compliance tests. Make and "
            "record reasonable assumptions; stop only for a genuine safety or "
            "authority blocker."
        )
    else:
        role_rule = (
            "This is implementation/fix work. Follow the active plan exactly, "
            "run its stated gates, and check a step only after its evidence gate "
            "passes."
        )
    objective = (
        "Make all roadmap work ship and pass the full pytest suite plus all 23 "
        "Markdown.mdtest fixtures. Require strict Markdown.pl bytes for every "
        "deterministic fixture and the documented entity-normalized comparison "
        "for Auto links."
    )
    model_name = executor.display_model or executor.model or "provider default"
    coauthor = (
        f"\nCo-authored-by: {executor.coauthor_name} <{executor.coauthor_email}>"
        if executor.coauthor_name and executor.coauthor_email
        else ""
    )
    provenance = (
        f"Agent: {executor.name}\nModel: {model_name}\nHarness: MCO 0.10.8{coauthor}"
    )
    operating_rules = (
        "Before acting, read AGENTS.md, docs/README.md, and "
        "docs/superpowers/plans/plan-roadmap.md. Preserve existing user changes. "
        "Never hand-edit generated SPL. Work on one step only; do not batch "
        "later steps. At each logical checkpoint, run the relevant evidence "
        "gate, create a small conventional commit, and push the current branch "
        "so progress is visible on GitHub. Never create empty checkpoint commits, "
        "force-push, tag, or expose credentials. If a required push fails, or if "
        "otherwise blocked, record one `- BLOCK:` line in .agent/blockers.md and "
        "exit cleanly. End every commit message with these exact provenance "
        f"trailers after a blank line:\n{provenance}"
    )
    return f"""You are one iteration of Shakedown's MCO autonomous loop.

Ultimate objective: {objective}

Action: {action.kind.value}
Executor: {executor.name}
Summary: {action.summary}
Active plan: {plan_text}
First unchecked step: {action.step or "none"}
Active blockers:
{blockers}

Working tree at handoff:
{status}

Previous failure summary: {last_failure or "none"}

Latest optional Fable governor directive:
{governor_directive}

{role_rule}

{operating_rules}
"""


def mco_command(
    config: LoopConfig, executor: Executor, task_id: str, prompt_file: Path
) -> list[str]:
    """Build one single-provider MCO invocation."""
    command = [
        "mco",
        "run",
        "--repo",
        str(REPO),
        "--file",
        str(prompt_file),
        "--providers",
        executor.provider,
        "--execution-mode",
        "yolo",
        "--max-provider-parallelism",
        "1",
        "--stall-timeout",
        "900",
        "--review-hard-timeout",
        "3600",
        "--artifact-base",
        str(config.artifact_dir),
        "--task-id",
        task_id,
        "--result-mode",
        "both",
        "--json",
    ]
    if executor.model:
        model: object = executor.model
        if executor.model_provider:
            model = {"provider": executor.model_provider, "model": executor.model}
        command.extend(
            ["--provider-models-json", json.dumps({executor.provider: model})]
        )
    if executor.best_effort:
        command.extend(["--enforcement-mode", "best_effort"])
    return command


def invoke_mco(
    config: LoopConfig,
    executor: Executor,
    action: NextAction,
    environment: Mapping[str, str],
    prompt_override: str | None = None,
) -> InvocationResult:
    """Invoke exactly one MCO provider and report repository progress."""
    import datetime
    import select

    config.artifact_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = config.state_file.parent / "mco-current-prompt.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    state = load_state(config.state_file)
    prompt_file.write_text(
        prompt_override
        if prompt_override is not None
        else build_prompt(action, executor, state.get("last_failure"))
    )
    task_id = f"{action.kind.value}-{int(time.time())}-{executor.name}"
    command = mco_command(config, executor, task_id, prompt_file)
    before = repo_fingerprint()
    blockers_before = set(read_blockers())

    stdout_lines: list[str] = []

    model_desc = (
        f"{executor.provider}:{executor.model or executor.display_model or 'default'}"
    )
    print(
        f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        f"agent-loop: starting {executor.name} ({model_desc}) "
        f'on task: "{action.summary}"',
        flush=True,
    )

    try:
        process = subprocess.Popen(
            command,
            cwd=REPO,
            env=dict(environment),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
    except Exception as e:
        return InvocationResult(
            exit_code=1,
            stdout="",
            stderr=str(e),
            made_progress=False,
        )

    assert process.stdout is not None, "process.stdout is None"
    assert process.stderr is not None, "process.stderr is None"
    stderr_pipe = process.stderr
    start_time = time.time()
    stderr_lines: list[str] = []
    stderr_reader = threading.Thread(
        target=lambda: stderr_lines.extend(iter(stderr_pipe.readline, "")),
        name="mco-stderr-reader",
        daemon=True,
    )
    stderr_reader.start()

    while True:
        if time.time() - start_time > MCO_TIMEOUT_SECONDS:
            process_group = process.pid
            os.killpg(process_group, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            try:
                os.killpg(process_group, 0)
            except ProcessLookupError:
                pass
            else:
                os.killpg(process_group, signal.SIGKILL)
                process.wait()
            stderr_reader.join(timeout=5)
            return InvocationResult(
                exit_code=124,
                stdout="".join(stdout_lines),
                stderr=(
                    "".join(stderr_lines)
                    + "MCO execution timed out after 5 hours at Python level."
                ),
                made_progress=False,
                recorded_blocker=bool(set(read_blockers()) - blockers_before),
            )

        ret = process.poll()
        rlist, _, _ = select.select([process.stdout], [], [], 1.0)
        if rlist:
            line = process.stdout.readline()
            if not line:
                if ret is not None:
                    break
                continue
            stdout_lines.append(line)

            try:
                d = json.loads(line)
                event_type = d.get("type")
                if event_type == "tool_execution_start":
                    tool_name = d.get("toolName", "unknown")
                    args = d.get("args", {})
                    cmd = (
                        args.get("command")
                        or args.get("CommandLine")
                        or args.get("path")
                        or args.get("AbsolutePath")
                        or ""
                    )
                    if len(cmd) > 80:
                        cmd = cmd[:77] + "..."
                    print(f"  [tool] {tool_name}: {cmd}", flush=True)
                elif event_type == "tool_execution_end":
                    tool_name = d.get("toolName", "unknown")
                    print(f"  [tool] {tool_name} completed", flush=True)
                elif event_type == "message_end":
                    msg = d.get("message", {})
                    content = msg.get("content", [])
                    thinking = ""
                    for item in content:
                        if item.get("type") == "thinking":
                            thinking = item.get("thinking", "")
                            break
                    if thinking:
                        summary = thinking.strip().splitlines()[0]
                        if len(summary) > 80:
                            summary = summary[:77] + "..."
                        print(f"  [agent] thinking: {summary}", flush=True)
            except Exception:
                pass
        else:
            if ret is not None:
                break

    stderr_reader.join()
    stderr = "".join(stderr_lines)
    redact_artifacts(config.artifact_dir, environment)
    after = repo_fingerprint()
    return InvocationResult(
        exit_code=process.returncode,
        stdout="".join(stdout_lines),
        stderr=stderr,
        made_progress=before != after,
        recorded_blocker=bool(set(read_blockers()) - blockers_before),
    )


def redact_artifacts(path: Path, environment: Mapping[str, str]) -> None:
    """Remove allowlisted secret values from text artifacts defensively."""
    if not path.exists():
        return
    for artifact in path.rglob("*"):
        if not artifact.is_file():
            continue
        try:
            text = artifact.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        redacted = _redact(text, environment)
        if redacted != text:
            artifact.write_text(redacted)


def classify_result(result: InvocationResult) -> str:
    """Classify an MCO result from observable supervisor evidence."""
    if result.made_progress:
        return "progress"
    if result.recorded_blocker:
        return "blocked"
    if result.exit_code == 124:
        return "supervisor_timeout"
    output = result.combined_output.lower()
    if any(marker in output for marker in RATE_LIMIT_MARKERS):
        return "rate_limit"
    if any(marker in output for marker in TRANSIENT_MARKERS):
        return "transient"
    if result.exit_code != 0:
        return "backend_failure"
    return "no_progress"


def apply_result(
    config: LoopConfig,
    state: dict[str, object],
    executor: Executor,
    action: NextAction,
    result: InvocationResult,
    now: int,
) -> str:
    """Update cooldown state from one invocation."""
    outcome = classify_result(result)
    raw_cooldowns = state.get("cooldowns", {})
    cooldowns = (
        dict(cast(Mapping[str, object], raw_cooldowns))
        if isinstance(raw_cooldowns, dict)
        else {}
    )
    raw_failures = state.get("failures", {})
    failures = (
        dict(cast(Mapping[str, object], raw_failures))
        if isinstance(raw_failures, dict)
        else {}
    )
    if outcome in {"progress", "blocked"}:
        failures[executor.name] = 0
        state["last_failure"] = None
        state["action_attempt"] = None
        state["exhaustion"] = None
        FABLE_DIRECTIVE.unlink(missing_ok=True)
    else:
        previous = failures.get(executor.name, 0)
        failures[executor.name] = (
            int(previous) if isinstance(previous, int) else 0
        ) + 1
        availability_failure = outcome in {"rate_limit", "transient"}
        cooldown_key = (
            executor.quota_group
            if availability_failure
            else f"executor:{executor.name}"
        )
        cooldowns[cooldown_key] = now + config.cooldown_seconds
        state["last_failure"] = {
            "executor": executor.name,
            "kind": outcome,
            "exit_code": result.exit_code,
        }
        if not availability_failure:
            key = action_key(action)
            raw_attempt = state.get("action_attempt")
            attempts: dict[str, object] = {}
            if isinstance(raw_attempt, dict) and raw_attempt.get("key") == key:
                raw_attempts = raw_attempt.get("attempts", {})
                if isinstance(raw_attempts, dict):
                    attempts = dict(cast(Mapping[str, object], raw_attempts))
            attempts[executor.name] = outcome
            state["action_attempt"] = {"key": key, "attempts": attempts}
    state["cooldowns"] = cooldowns
    state["failures"] = failures
    save_state(config.state_file, state)
    return outcome


def apply_failure_action(action: NextAction, state: Mapping[str, object]) -> NextAction:
    """Route substantive prior failures through the fixing role."""
    failure = state.get("last_failure")
    if not isinstance(failure, dict):
        return action
    kind = failure.get("kind")
    if kind not in {"backend_failure", "no_progress"}:
        return action
    return NextAction(
        ActionKind.FIX,
        f"Recover the current roadmap step after {kind} from the prior executor.",
        action.active_plan,
        action.step,
        action.blockers,
    )


def apply_governor_directive(action: NextAction) -> tuple[NextAction, bool]:
    """Apply a persisted manual Fable verdict to ordinary-agent routing."""
    try:
        text = FABLE_DIRECTIVE.read_text()
    except FileNotFoundError:
        return action, False
    match = re.search(r"VERDICT:\s*(CONTINUE|FIX|REDIRECT|STOP)", text, re.I)
    if not match:
        return action, False
    verdict = match.group(1).upper()
    if verdict == "STOP":
        return action, True
    if verdict == "FIX":
        return (
            NextAction(
                ActionKind.FIX,
                "Execute the bounded repair in the latest Fable directive.",
                action.active_plan,
                action.step,
                action.blockers,
            ),
            False,
        )
    if verdict == "REDIRECT":
        return (
            NextAction(
                ActionKind.PLAN,
                "Amend the active durable direction per the latest Fable directive.",
                action.active_plan,
                action.step,
                action.blockers,
            ),
            False,
        )
    return action, False


def completion_gates() -> tuple[bool, str]:
    """Run the driver-owned terminal gates."""
    pytest_result = subprocess.run(
        ["uv", "run", "pytest", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if pytest_result.returncode != 0:
        details = f"{pytest_result.stdout[-2000:]}\n{pytest_result.stderr[-1000:]}"
        return (
            False,
            f"full pytest failed:\n{details}",
        )
    mdtest_result = subprocess.run(
        ["uv", "run", "pytest", "tests/test_mdtest.py", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    mdtest_output = f"{mdtest_result.stdout}\n{mdtest_result.stderr}"
    if (
        mdtest_result.returncode != 0
        or not re.search(r"\b23 passed\b", mdtest_output)
        or re.search(r"\bskipped\b", mdtest_output)
    ):
        return False, f"23-fixture mdtest gate incomplete:\n{mdtest_output[-3000:]}"

    fixtures_dir = Path.home() / "mdtest" / "Markdown.mdtest"
    deterministic = [
        fixture.stem
        for fixture in sorted(fixtures_dir.glob("*.text"))
        if fixture.stem != "Auto links"
    ]
    if len(deterministic) != 22:
        return (
            False,
            "strict parity gate expected 22 deterministic fixtures "
            f"but discovered {len(deterministic)}",
        )
    parity_result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/strict_parity_harness.py",
            *deterministic,
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    if (
        parity_result.returncode != 0
        or "summary: 22/22 byte-identical" not in parity_result.stdout
    ):
        details = f"{parity_result.stdout[-3000:]}\n{parity_result.stderr[-1000:]}"
        return (
            False,
            f"strict parity incomplete:\n{details}",
        )
    return (
        True,
        "full pytest, mdtest 23/23 with no skips, and deterministic strict "
        "parity 22/22 passed",
    )


def _redact(text: str, environment: Mapping[str, str]) -> str:
    redacted = text
    for name in ALLOWED_SECRET_NAMES:
        value = environment.get(name)
        if value:
            redacted = redacted.replace(value, f"<{name}:redacted>")
    return redacted


def _arguments(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--once", action="store_true", help="Run at most one MCO invocation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Classify and select without invoking MCO",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print current action, executor, and cooldown state",
    )
    parser.add_argument(
        "--cooldown-seconds", type=int, help="Override configured provider cooldown"
    )
    parser.add_argument(
        "--govern",
        action="store_true",
        help="Run one rare read-only Claude Fable architecture review",
    )
    return parser.parse_args(argv)


def governor_prompt(action: NextAction, state: Mapping[str, object]) -> str:
    """Build the bounded, read-only Fable governor request."""
    plan = str(action.active_plan.relative_to(REPO)) if action.active_plan else "none"
    status = _git_output(["status", "--short", "--untracked-files=all"]).strip()
    review_scope = (
        "Do not edit files or implement code. Inspect AGENTS.md, docs/README.md, "
        "the roadmap, the active plan, relevant accepted specs, blockers, and "
        "the working tree. Decide whether the process can still reach strict "
        "parity for all 23 Markdown.pl fixtures without an architectural trap."
    )
    verdict_rule = (
        "Then give a concise evidence-based directive for the ordinary agents. "
        "CONTINUE means the present plan is sound. FIX names a bounded repair. "
        "REDIRECT explains which existing spec, plan, or roadmap decision should "
        "be amended without creating a second in-flight plan. STOP is only for "
        "a genuine safety or authority problem. Do not ask for human input when "
        "a reasonable assumption is possible."
    )
    return f"""You are the rare read-only governor for Shakedown's autonomous loop.

{review_scope}

Current action: {action.kind.value}
Current summary: {action.summary}
Active plan: {plan}
Current step: {action.step or "none"}
Loop failure state: {state.get("last_failure") or "none"}
Working tree:
{status or "clean"}

Return exactly one leading verdict line:
VERDICT: CONTINUE | FIX | REDIRECT | STOP

{verdict_rule}
"""


def run_governor(
    config: LoopConfig,
    action: NextAction,
    environment: Mapping[str, str],
) -> int:
    """Run one explicit Fable review and persist its non-secret directive."""
    executor = Executor(
        name="fable-governor",
        provider="claude-fable",
        quota_group="claude",
        display_model="claude-fable-5",
        best_effort=True,
    )
    state = load_state(config.state_file)
    result = invoke_mco(
        config,
        executor,
        action,
        environment,
        prompt_override=governor_prompt(action, state),
    )
    output = _redact(result.combined_output, environment).strip()
    if result.exit_code != 0:
        print(output, file=sys.stderr)
        return result.exit_code
    FABLE_DIRECTIVE.parent.mkdir(parents=True, exist_ok=True)
    FABLE_DIRECTIVE.write_text(output + "\n")
    print(output)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the autonomous loop until completion or operator interruption."""
    args = _arguments(argv)
    config = load_config(args.config)
    if args.cooldown_seconds is not None:
        config = LoopConfig(
            env_file=config.env_file,
            state_file=config.state_file,
            artifact_dir=config.artifact_dir,
            cooldown_seconds=max(0, args.cooldown_seconds),
            iteration_pause_seconds=config.iteration_pause_seconds,
            planning=config.planning,
            implementation=config.implementation,
        )
    if shutil.which("mco") is None and not args.dry_run and not args.status:
        print("agent-loop: mco is not installed; install @tt-a1i/mco", file=sys.stderr)
        return 2
    environment = load_named_secrets(config.env_file)
    try:
        while True:
            rows = parse_roadmap(ROADMAP.read_text())
            blockers = read_blockers()
            action = determine_next_action(rows, blockers)
            if args.govern:
                return run_governor(config, action, environment)
            no_remaining_rows = not any(
                "pending" in row.status or "in flight" in row.status for row in rows
            )
            if no_remaining_rows:
                complete, detail = completion_gates()
                if complete:
                    print(f"agent-loop: complete: {detail}")
                    return 0
                action = NextAction(ActionKind.FIX, detail, None, None, blockers)
            canonical_action = action
            state = load_state(config.state_file)
            action = apply_failure_action(canonical_action, state)
            action, governor_stop = apply_governor_directive(action)
            if governor_stop:
                print(
                    "agent-loop: stopped by the latest Fable governor directive",
                    file=sys.stderr,
                )
                return 4
            pool = (
                config.planning
                if action.kind is ActionKind.PLAN
                else config.implementation
            )
            now = int(time.time())
            selection = select_executor(
                pool,
                state,
                canonical_action,
                now,
                preserve_planning=(action.kind is not ActionKind.PLAN),
            )
            executor = selection.executor
            next_ready = selection.next_ready
            status_payload = {
                "action": action.kind.value,
                "summary": action.summary,
                "active_plan": str(action.active_plan.relative_to(REPO))
                if action.active_plan
                else None,
                "step": action.step,
                "executor": executor.name if executor else None,
                "next_ready": next_ready,
                "exhausted": selection.exhausted,
                "action_attempt": state.get("action_attempt"),
                "fable_governor_recommended": executor is None,
                "state": state,
            }
            if args.dry_run or args.status:
                print(json.dumps(status_payload, indent=2, sort_keys=True))
                return 0
            if selection.exhausted:
                payload = exhaustion_payload(canonical_action, pool, state, now)
                state["exhaustion"] = payload
                save_state(config.state_file, state)
                print(json.dumps(payload, indent=2, sort_keys=True))
                print("agent-loop: exhausted", file=sys.stderr, flush=True)
                return 5
            if executor is None:
                if args.once:
                    print(json.dumps(status_payload, indent=2, sort_keys=True))
                    return 3
                print(
                    "agent-loop: full eligible fallback chain is cooling down; "
                    "consider ./agent-loop --govern for a rare Fable review"
                )
                wait_seconds = max(1, (next_ready or now + 60) - now)
                print(
                    "agent-loop: all eligible executors cooling down; "
                    f"waiting {wait_seconds}s"
                )
                time.sleep(wait_seconds)
                continue
            print(
                f"agent-loop: {action.kind.value} via {executor.name} "
                f"({executor.provider}:"
                f"{executor.model or executor.display_model or 'default'})"
            )
            result = invoke_mco(config, executor, action, environment)
            if result.stdout:
                print(_redact(result.stdout, environment))
            if result.stderr:
                print(_redact(result.stderr, environment), file=sys.stderr)
            outcome = apply_result(
                config,
                state,
                executor,
                canonical_action,
                result,
                int(time.time()),
            )
            print(f"agent-loop: supervisor outcome: {outcome}")
            failed = outcome not in {"progress", "blocked"}
            if failed:
                print(f"agent-loop: {executor.name} entered cooldown after {outcome}")
            if args.once:
                return 1 if failed else 0
            time.sleep(config.iteration_pause_seconds)
    except KeyboardInterrupt:
        print("\nagent-loop: interrupted")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
