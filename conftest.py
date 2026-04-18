"""Root conftest.py — adds the project root to sys.path so that
packages like `scripts` are importable in tests without installation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
