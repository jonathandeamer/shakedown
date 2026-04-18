"""Shared helpers for prototype fixture tests."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "shakedown-dev"
FIXTURES = Path(__file__).parent / "fixtures"


def normalize(text: str) -> str:
    """Trim each line, collapse consecutive blank lines, strip whole result."""
    lines = text.split("\n")
    out: list[str] = []
    prev_blank = False
    for line in lines:
        line = line.strip()
        if line == "":
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(line)
            prev_blank = False
    return "\n".join(out).strip()
