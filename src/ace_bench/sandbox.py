"""Checkout a public GitHub repo at ``base_sha`` for agent eval (step 3).

Prefer host git into a dedicated workdir under ``/tmp/ace-sandbox/`` or
``~/ace-bench-data/sandboxes/``. Docker is optional (presence check only in MVP;
network-none test runners come later). Does **not** execute untrusted agent code.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ace_bench.eval_v0 import validate_repo_slug
from ace_bench.paths import PathEscapeError, resolve_allowed_path

ALLOWED_GIT_HOSTS = frozenset({"github.com"})
_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
_SAFE_DIR_RE = re.compile(r"^[A-Za-z0-9._#-]+$")
DEFAULT_WORK_ROOT_CANDIDATES = (
    Path.home() / "ace-bench-data" / "sandboxes",
    Path("/tmp") / "ace-sandbox",
)


class SandboxError(ValueError):
    """Invalid sandbox inputs or checkout failure."""


@dataclass(frozen=True, slots=True)
class SandboxCheckout:
    """Result of a sandbox checkout."""

    worktree: Path
    repo: str
    base_sha: str
    issue_path: Path
    clone_url: str
    used_docker: bool


def docker_available() -> bool:
    """True if ``docker`` is on PATH and the daemon responds (best-effort)."""
    if shutil.which("docker") is None:
        return False
    try:
        proc = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def default_work_root() -> Path:
    """Mac-friendly default under ``~/ace-bench-data/sandboxes``, else /tmp."""
    for cand in DEFAULT_WORK_ROOT_CANDIDATES:
        parent = cand.parent
        if parent.exists() or cand == DEFAULT_WORK_ROOT_CANDIDATES[0]:
            return cand
    return Path("/tmp") / "ace-sandbox"


def github_clone_url(repo: str) -> str:
    """HTTPS clone URL for an allowlisted ``owner/name`` on github.com only."""
    slug = validate_repo_slug(repo)
    return f"https://github.com/{slug}.git"


def validate_base_sha(sha: str) -> str:
    text = (sha or "").strip()
    if not _SHA_RE.match(text):
        raise SandboxError(
            f"invalid base_sha {sha!r}; expected 7–40 hex chars"
        )
    return text.lower()


def validate_work_root(work_root: str | Path) -> Path:
    """Resolve work root under path allowlist (cwd, ace-bench-data, /tmp, …)."""
    try:
        root = resolve_allowed_path(work_root, purpose="work_root")
    except PathEscapeError as exc:
        raise SandboxError(str(exc)) from exc
    # Cap nesting: refuse absurdly deep paths.
    if len(root.parts) > 24:
        raise SandboxError(f"work_root path too deep: {root}")
    return root


def _safe_workdir_name(repo: str, base_sha: str) -> str:
    owner, name = repo.split("/", 1)
    short = base_sha[:12]
    raw = f"{owner}__{name}__{short}"
    if not _SAFE_DIR_RE.match(raw):
        raise SandboxError(f"unsafe workdir name derived from {repo!r}")
    return raw


def write_issue_md(
    worktree: Path,
    *,
    title: str | None,
    body: str | None,
    instance_id: str | None = None,
) -> Path:
    """Write ``ISSUE.md`` into the worktree (issue text only; no secrets)."""
    lines = [
        f"# {title or 'Issue'}",
        "",
    ]
    if instance_id:
        lines.extend([f"_Instance: `{instance_id}`_", ""])
    lines.append((body or "").strip() or "(no body)")
    lines.append("")
    path = worktree / "ISSUE.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _run_git(args: list[str], *, cwd: Path | None = None) -> None:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise SandboxError(f"git {' '.join(args[:3])}… failed: {err[:500]}")


def checkout_at_base_sha(
    *,
    repo: str,
    base_sha: str,
    work_root: str | Path | None = None,
    title: str | None = None,
    body: str | None = None,
    instance_id: str | None = None,
    prefer_docker: bool = False,
    timeout_sec: int = 600,
) -> SandboxCheckout:
    """Shallow-fetch ``repo`` and check out ``base_sha`` under ``work_root``.

    Strategy (host git — primary MVP path):
      git clone --filter=blob:none --no-checkout <url> <dir>
      git fetch --depth 1 origin <base_sha>
      git checkout <base_sha>

    Falls back to ``git init`` + remote add + fetch if clone layout fails.
    ``prefer_docker`` is recorded but MVP still uses host git (no untrusted exec).
    """
    slug = validate_repo_slug(repo)
    sha = validate_base_sha(base_sha)
    root = validate_work_root(work_root or default_work_root())
    root.mkdir(parents=True, exist_ok=True)

    workdir = root / _safe_workdir_name(slug, sha)
    if workdir.exists():
        # Reuse existing checkout if already at the right SHA.
        head = _try_rev_parse(workdir)
        if head and head.startswith(sha[:12]):
            issue = write_issue_md(
                workdir, title=title, body=body, instance_id=instance_id
            )
            return SandboxCheckout(
                worktree=workdir,
                repo=slug,
                base_sha=sha,
                issue_path=issue,
                clone_url=github_clone_url(slug),
                used_docker=False,
            )
        shutil.rmtree(workdir)

    url = github_clone_url(slug)
    used_docker = bool(prefer_docker and docker_available())
    # MVP: even when Docker is available we still use host git for checkout.
    # Isolation for *test execution* is a later step (docker --network none).
    _ = timeout_sec  # reserved for future docker/git timeouts

    try:
        _clone_partial(url, workdir, sha)
    except SandboxError:
        if workdir.exists():
            shutil.rmtree(workdir, ignore_errors=True)
        _clone_init_fetch(url, workdir, sha)

    issue = write_issue_md(workdir, title=title, body=body, instance_id=instance_id)
    return SandboxCheckout(
        worktree=workdir,
        repo=slug,
        base_sha=sha,
        issue_path=issue,
        clone_url=url,
        used_docker=used_docker,
    )


def _try_rev_parse(workdir: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return proc.stdout.strip().lower()
    except OSError:
        return None
    return None


def _clone_partial(url: str, workdir: Path, sha: str) -> None:
    _run_git(
        [
            "clone",
            "--filter=blob:none",
            "--no-checkout",
            url,
            str(workdir),
        ]
    )
    _run_git(["fetch", "--depth", "1", "origin", sha], cwd=workdir)
    _run_git(["checkout", sha], cwd=workdir)


def _clone_init_fetch(url: str, workdir: Path, sha: str) -> None:
    workdir.mkdir(parents=True, exist_ok=True)
    _run_git(["init"], cwd=workdir)
    _run_git(["remote", "add", "origin", url], cwd=workdir)
    _run_git(["fetch", "--depth", "1", "origin", sha], cwd=workdir)
    _run_git(["checkout", sha], cwd=workdir)


def assert_sandbox_path_safe(path: Path, *, work_root: Path) -> Path:
    """Ensure a path stays under the sandbox work root (unit-test helper)."""
    resolved = path.expanduser().resolve(strict=False)
    root = work_root.expanduser().resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SandboxError(
            f"sandbox path escapes work_root ({resolved} not under {root})"
        ) from exc
    return resolved


def env_prefers_docker() -> bool:
    return os.environ.get("ACE_SANDBOX_DOCKER", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
