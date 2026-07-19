"""External fixture and oracle path resolution.

Defaults match the historical local layout used by the Markdown.mdtest suite
and Markdown.pl oracle. Override for portable checkouts:

- ``SHAKEDOWN_MDTEST`` — directory of ``*.text`` / ``*.xhtml`` fixtures
  (default: ``~/mdtest/Markdown.mdtest``)
- ``SHAKEDOWN_MARKDOWN_PL`` — path to ``Markdown.pl``
  (default: ``~/markdown/Markdown.pl``)
"""

from __future__ import annotations

import os
from pathlib import Path


def mdtest_fixtures_dir() -> Path:
    """Return the Markdown.mdtest fixtures directory."""
    override = os.environ.get("SHAKEDOWN_MDTEST")
    if override:
        return Path(override).expanduser()
    return Path.home() / "mdtest" / "Markdown.mdtest"


def markdown_pl() -> Path:
    """Return the path to the local Markdown.pl oracle."""
    override = os.environ.get("SHAKEDOWN_MARKDOWN_PL")
    if override:
        return Path(override).expanduser()
    return Path.home() / "markdown" / "Markdown.pl"
