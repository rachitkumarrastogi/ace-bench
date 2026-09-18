"""Safe path resolution for local CLI tools (DB / patch / export paths).

Threat model: operator-supplied ``--db`` / ``--agent-patch`` / ``--out`` should
not escape a small allowlist of roots (cwd, ``$HOME/ace-bench``, ``/tmp``, and
optional ``ACE_ALLOWED_ROOTS``). This is defense-in-depth for a local CLI, not
a multi-tenant sandbox.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

# Soft cap for agent patch files read into memory (DoS / accidental huge diffs).
MAX_AGENT_PATCH_BYTES = 10 * 1024 * 1024


class PathEscapeError(ValueError):
    """Raised when a user path resolves outside allowed roots."""


def default_allowed_roots() -> list[Path]:
    """Roots that user-controlled file paths may resolve under."""
    roots: list[Path] = [Path.cwd().resolve()]
    home_ace = (Path.home() / "ace-bench").resolve()
    roots.append(home_ace)
    tmp = Path("/tmp")
    if tmp.exists():
        roots.append(tmp.resolve())
    # Repo checkout when imported from an editable install / scripts/ layout.
    pkg_root = Path(__file__).resolve().parents[2]
    roots.append(pkg_root)
    extra = os.environ.get("ACE_ALLOWED_ROOTS", "")
    for part in extra.split(os.pathsep):
        part = part.strip()
        if part:
            roots.append(Path(part).expanduser().resolve())
    # Dedupe while preserving order.
    seen: set[Path] = set()
    out: list[Path] = []
    for r in roots:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def resolve_allowed_path(
    raw: str | Path,
    *,
    allowed_roots: Sequence[Path] | None = None,
    purpose: str = "path",
    must_exist: bool = False,
) -> Path:
    """Resolve ``raw`` and require it to live under an allowed root.

    Symlinks are resolved (``Path.resolve``) so a link pointing outside the
    allowlist is rejected.
    """
    path = Path(raw).expanduser()
    resolved = path.resolve(strict=False)
    roots = list(allowed_roots) if allowed_roots is not None else default_allowed_roots()
    for root in roots:
        try:
            resolved.relative_to(root)
            break
        except ValueError:
            continue
    else:
        raise PathEscapeError(
            f"{purpose} escapes allowed directories ({resolved}); "
            f"allowed roots: {', '.join(str(r) for r in roots)} "
            f"(set ACE_ALLOWED_ROOTS to extend)"
        )
    if must_exist and not resolved.is_file() and not resolved.is_dir():
        raise FileNotFoundError(f"{purpose} not found: {resolved}")
    return resolved


def read_text_capped(
    path: Path,
    *,
    max_bytes: int = MAX_AGENT_PATCH_BYTES,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> str:
    """Read a text file with a hard size cap (bytes on disk)."""
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(
            f"file too large ({size} bytes > {max_bytes} max): {path}"
        )
    return path.read_text(encoding=encoding, errors=errors)
