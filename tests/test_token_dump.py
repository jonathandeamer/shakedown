"""The debug target dumps the inter-act token stream as integers."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent
DEBUG_WRAPPER = REPO / "shakedown-debug"
AMPS_FIXTURE = (
    Path.home() / "mdtest" / "Markdown.mdtest" / "Amps and angle encoding.text"
)


def test_debug_target_dumps_integer_token_stream() -> None:
    result = subprocess.run(
        [str(DEBUG_WRAPPER)],
        input=AMPS_FIXTURE.read_bytes(),
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    lines = result.stdout.decode().strip().splitlines()
    assert len(lines) > 10
    values = [int(line) for line in lines]
    # Production Act IV emits <p> first for this fixture (Slice 1 is
    # byte-identical), so the first popped stream value must be the
    # PARAGRAPH_OPEN token.
    assert values[0] == 1
