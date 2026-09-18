"""GitHub token loading without printing secret values."""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

DEFAULT_TOKEN_FILE = Path.home() / ".config" / "ace-bench" / "github_token"


def token_file_mode_ok(path: Path) -> bool:
    """True if path is not group/other-accessible (prefer mode 0600)."""
    mode = path.stat().st_mode
    return (mode & (stat.S_IRWXG | stat.S_IRWXO)) == 0


def warn_token_file_perms(path: Path) -> None:
    """Warn if token file is group/world accessible; never print contents."""
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except OSError:
        return
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        print(
            f"warning: token file {path} mode is {mode:04o} "
            "(prefer chmod 600; group/other access increases leak risk)",
            file=sys.stderr,
        )


def load_token_from_file(path: Path) -> str | None:
    """Read a token file; warn on loose perms; never log the value."""
    if not path.is_file():
        return None
    warn_token_file_perms(path)
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def resolve_github_token(
    *,
    explicit: str | None = None,
    token_file: Path | None = None,
) -> str | None:
    """Resolve token from explicit arg, env, then token file.

    Never prints the token. Prefer ``GITHUB_TOKEN`` / ``GH_TOKEN`` env vars.
    """
    if explicit is not None:
        stripped = explicit.strip()
        return stripped or None
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        val = os.environ.get(key)
        if val and val.strip():
            return val.strip()
    path = token_file if token_file is not None else DEFAULT_TOKEN_FILE
    return load_token_from_file(path)
