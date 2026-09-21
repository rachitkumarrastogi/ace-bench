#!/usr/bin/env python3
"""Checkout a public GitHub repo at base_sha into an ACE sandbox workdir.

Example:
  python3 scripts/run_sandbox_checkout.py \\
    --repo django/django \\
    --base-sha 02a5b41db4ff8544f93a5d9854b346a9aae4f556 \\
    --work-root ~/ace-bench-data/sandboxes \\
    --title "Example" --body "Fix the bug."
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.sandbox import (
    SandboxError,
    checkout_at_base_sha,
    default_work_root,
    docker_available,
    env_prefers_docker,
)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True, help="owner/name (github.com only)")
    p.add_argument("--base-sha", required=True, help="commit SHA to checkout")
    p.add_argument(
        "--work-root",
        default=None,
        help=f"sandbox root (default: {default_work_root()})",
    )
    p.add_argument("--title", default="", help="ISSUE.md title")
    p.add_argument("--body", default="", help="ISSUE.md body")
    p.add_argument("--instance", default=None, help="optional instance id for ISSUE.md")
    p.add_argument(
        "--prefer-docker",
        action="store_true",
        help="record docker preference (checkout still uses host git in MVP)",
    )
    p.add_argument("--json", action="store_true", help="print JSON summary")
    args = p.parse_args(argv)

    prefer = args.prefer_docker or env_prefers_docker()
    try:
        result = checkout_at_base_sha(
            repo=args.repo,
            base_sha=args.base_sha,
            work_root=args.work_root,
            title=args.title or None,
            body=args.body or None,
            instance_id=args.instance,
            prefer_docker=prefer,
        )
    except SandboxError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    payload = {
        "worktree": str(result.worktree),
        "repo": result.repo,
        "base_sha": result.base_sha,
        "issue_path": str(result.issue_path),
        "clone_url": result.clone_url,
        "used_docker": result.used_docker,
        "docker_available": docker_available(),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"worktree: {result.worktree}")
        print(f"issue:    {result.issue_path}")
        print(f"sha:      {result.base_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
