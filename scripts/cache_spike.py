"""Cache feasibility spike for the dev wrapper."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import pickle
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).parent.parent
ASSEMBLED = REPO / ".cache" / "spike-shakedown.spl"
CACHE_DIR = REPO / ".cache"
VERDICT_DOC = REPO / "docs" / "architecture" / "cache-spike.md"
CACHE_SHAPE_VERSION = 1

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def cache_key(spl_path: Path) -> str:
    """Return the invalidation key shape a proven cache would need."""
    spl_hash = hashlib.sha256(spl_path.read_bytes()).hexdigest()
    py = platform.python_version()
    sl = importlib.metadata.version("shakespearelang")
    return f"{spl_hash}:{py}:{sl}:v{CACHE_SHAPE_VERSION}"


def assemble_spike_input() -> Path:
    """Concatenate src/*.spl into a one-off file for the spike."""
    from scripts.assemble import assemble

    CACHE_DIR.mkdir(exist_ok=True)
    assemble(
        src_dir=REPO / "src",
        manifest=REPO / "src" / "manifest.toml",
        output=ASSEMBLED,
    )
    return ASSEMBLED


def run_direct(spl_path: Path, stdin_bytes: bytes) -> tuple[bytes, float, int, str]:
    """Run direct interpreter execution and record outcome without failing spike."""
    start = time.perf_counter()
    result = subprocess.run(
        ["uv", "run", "shakespeare", "run", str(spl_path)],
        input=stdin_bytes,
        capture_output=True,
        check=False,
    )
    elapsed = time.perf_counter() - start
    stderr = result.stderr.decode(errors="replace")
    return result.stdout, elapsed, result.returncode, stderr


def attempt_pickle_play(spl_path: Path) -> tuple[bool, str]:
    """Try the architecture-mentioned non-viable path; document failure mode."""
    try:
        from shakespearelang import Shakespeare
    except ImportError as exc:
        return False, f"import-failed:{exc}"
    try:
        play = Shakespeare(spl_path.read_text())
    except Exception as exc:  # noqa: BLE001
        return False, f"parse-failed:{type(exc).__name__}:{exc}"
    try:
        blob = pickle.dumps(play)
    except Exception as exc:  # noqa: BLE001
        return False, f"pickle-dumps-failed:{type(exc).__name__}:{exc}"
    try:
        restored = pickle.loads(blob)
    except Exception as exc:  # noqa: BLE001
        return False, f"pickle-loads-failed:{type(exc).__name__}:{exc}"
    try:
        restored.run()
    except Exception as exc:  # noqa: BLE001
        return False, f"run-after-load-failed:{type(exc).__name__}:{exc}"
    return True, "pickle-smoke-ok-but-cache-not-proven"


def write_verdict(verdict: dict[str, object]) -> None:
    """Write the human-readable spike outcome."""
    VERDICT_DOC.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "# Cache Feasibility Spike Outcome\n"
        "\n"
        "**Status:** Pre-Slice-1 deliverable per architecture spec §7.1 #4 / §5.3a.\n"
        "\n"
        "Re-run with `uv run python scripts/cache_spike.py`.\n"
        "\n"
        "## Result\n"
        "\n"
        "```json\n"
        f"{json.dumps(verdict, indent=2, sort_keys=True)}\n"
        "```\n"
        "\n"
        "## Decision\n"
        "\n"
        f"**Dev-mode shape:** {verdict['decision']}\n"
        "\n"
        "The spike does not prove a reusable cache target. The dev wrapper must use\n"
        "direct assemble-and-run mode until a future spike proves all §5.3a cache\n"
        "criteria: reusable representation, byte-identical cached execution,\n"
        "separate wrapper-overhead measurement, and versioned invalidation key.\n"
        "\n"
        "## References\n"
        "\n"
        "- `docs/superpowers/specs/2026-04-26-shakedown-architecture-design.md` "
        "§5.3a, §7.1 #4.\n"
        "- `docs/verification-plan.md` baseline B14 cold-cost figure.\n"
    )
    VERDICT_DOC.write_text(body)


def main() -> int:
    spl_path = assemble_spike_input()
    stdin_bytes = b"hello *world*\n"

    direct_out, direct_time, direct_code, direct_stderr = run_direct(
        spl_path, stdin_bytes
    )
    pickle_ok, pickle_diag = attempt_pickle_play(spl_path)

    verdict: dict[str, object] = {
        "cache_key": cache_key(spl_path),
        "cache_key_inputs": {
            "spl_hash": hashlib.sha256(spl_path.read_bytes()).hexdigest(),
            "python_version": platform.python_version(),
            "shakespearelang_version": importlib.metadata.version("shakespearelang"),
            "cache_shape_version": CACHE_SHAPE_VERSION,
        },
        "direct_run_seconds": round(direct_time, 3),
        "direct_run_returncode": direct_code,
        "direct_run_stdout_bytes": len(direct_out),
        "direct_run_stderr_excerpt": direct_stderr[:500],
        "pickle_path_outcome": pickle_diag,
        "pickle_candidate_succeeded": pickle_ok,
        "cache_proven_reason": (
            "not proven; byte-identity and overhead criteria were not exercised"
        ),
        "decision": "direct_assemble_and_run",
    }
    write_verdict(verdict)
    print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
