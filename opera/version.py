"""Build-version helpers backed by the repository-root VERSION file."""

from __future__ import annotations

import re
from html import escape
from pathlib import Path


VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"
_VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def get_version() -> str:
    """Return the validated build version from the single authoritative file."""
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not _VERSION_PATTERN.fullmatch(version):
        raise RuntimeError(f"Invalid OPERA-X version in {VERSION_FILE}: {version!r}")
    return version


def version_badge_html() -> str:
    """Build the top-ribbon badge from the authoritative version on each render."""
    return f'<div class="version">v{escape(get_version())}</div>'