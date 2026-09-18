#!/usr/bin/env python3
"""Score an agent unified-diff patch against a human baseline row (ACE v0).

AST proxy: max(added_lines, 1) — see ace_bench.eval_v0 and docs/EVAL.md.

GitHub harvest patches are usually *headerless* hunks (no ``diff --git``). For
self-smoke use ``--self-smoke`` (loads human patch + human file list from DB).
Real agents should emit a normal ``git diff`` (or pass ``--agent-files``).

Examples:
  # Human vs itself (smoke → ACE ≈ 1.0, drift 0):
  python3 scripts/score_against_human.py \\
    --instance django/django#22 --self-smoke --passed-tests true

  # Agent patch with git headers:
  python3 scripts/score_against_human.py \\
    --instance django/django#22 --agent-patch agent.diff --passed-tests false
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.db import PatternStore
from ace_bench.eval_v0 import score_agent_vs_human

FROZEN_NAME = "ace_patterns_django_pre2021_6125.sqlite"


def resolve_db_path(cli_db: str | None) -> Path:
    if cli_db:
        return Path(cli_db).expanduser()
    env = os.environ.get("ACE_DB_PATH")
    if env:
        return Path(env).expanduser()
    for c in (
        Path("data/frozen") / FROZEN_NAME,
        Path.home() / "ace-bench" / "data" / "frozen" / FROZEN_NAME,
        Path("data/ace_patterns.sqlite"),
        Path.home() / "ace-bench" / "data" / "ace_patterns.sqlite",
    ):
        if c.is_file():
            return c
    return Path("data/frozen") / FROZEN_NAME


def parse_instance(value: str) -> tuple[str, int]:
    if "#" in value:
        repo, pr_s = value.rsplit("#", 1)
    elif "@" in value:
        repo, pr_s = value.rsplit("@", 1)
    else:
        raise argparse.ArgumentTypeError(
            "instance must look like owner/name#123 or owner/name@123"
        )
    return repo.strip(), int(pr_s.strip())


def parse_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in ("1", "true", "yes", "y", "pass", "passed"):
        return True
    if v in ("0", "false", "no", "n", "fail", "failed"):
        return False
    raise argparse.ArgumentTypeError("expected true|false")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default=None, help="SQLite path (default: ACE_DB_PATH or frozen)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--instance",
        type=parse_instance,
        help="repo#pr_number (e.g. django/django#12345)",
    )
    g.add_argument("--repo", help="Use with --pr")
    p.add_argument("--pr", type=int, help="PR number (with --repo)")
    p.add_argument(
        "--agent-patch",
        type=Path,
        default=None,
        help="Path to agent unified diff (required unless --self-smoke)",
    )
    p.add_argument(
        "--self-smoke",
        action="store_true",
        help="Score human patch_text against itself (uses DB files_json for F_A)",
    )
    p.add_argument(
        "--agent-files",
        default=None,
        help="Comma-separated agent file paths when patch has no headers",
    )
    p.add_argument(
        "--passed-tests",
        type=parse_bool,
        required=True,
        help="Sandbox test gate: true|false (required; Docker sandbox later)",
    )
    p.add_argument(
        "--dump-human-patch",
        type=Path,
        default=None,
        help="Write human patch_text from DB to this path",
    )
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.instance:
        repo, pr_number = args.instance
    else:
        if not args.repo or args.pr is None:
            print("error: pass --instance OR both --repo and --pr", file=sys.stderr)
            return 2
        repo, pr_number = args.repo, args.pr

    if not args.self_smoke and args.agent_patch is None:
        print("error: pass --agent-patch or --self-smoke", file=sys.stderr)
        return 2

    db_path = resolve_db_path(args.db)
    if not db_path.is_file():
        print(f"error: DB not found: {db_path}", file=sys.stderr)
        return 2

    with PatternStore(db_path) as store:
        human = store.get_pattern(repo, pr_number)
        if human is None:
            print(f"error: no row for {repo}#{pr_number} in {db_path}", file=sys.stderr)
            return 2
        if args.dump_human_patch is not None:
            args.dump_human_patch.parent.mkdir(parents=True, exist_ok=True)
            args.dump_human_patch.write_text(human.patch_text or "", encoding="utf-8")

    agent_files: list[str] | None = None
    if args.agent_files:
        agent_files = [f.strip() for f in args.agent_files.split(",") if f.strip()]

    if args.self_smoke:
        agent_patch = human.patch_text or ""
        agent_files = list(human.files)
        if args.agent_patch is not None:
            args.agent_patch.parent.mkdir(parents=True, exist_ok=True)
            args.agent_patch.write_text(agent_patch, encoding="utf-8")
    else:
        assert args.agent_patch is not None
        if not args.agent_patch.is_file():
            print(f"error: agent patch not found: {args.agent_patch}", file=sys.stderr)
            return 2
        agent_patch = args.agent_patch.read_text(encoding="utf-8", errors="replace")

    report = score_agent_vs_human(
        repo=human.repo,
        pr_number=human.pr_number,
        human_files=list(human.files),
        human_patch=human.patch_text,
        agent_patch=agent_patch,
        passed_tests=args.passed_tests,
        human_metrics=human.metrics,
        agent_files=agent_files,
    )
    payload = report.as_dict()
    payload["db"] = str(db_path)
    payload["human_title"] = human.title
    payload["base_sha"] = human.base_sha

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    drift = payload["boundary"]["symmetric_diff_size"]
    print(f"instance:     {report.instance_id}")
    print(f"title:        {human.title}")
    print(f"passed_tests: {report.passed_tests}")
    print(f"ACE score:    {report.ace_score:.6f}")
    print(f"AST proxy:    {report.ast_proxy}  (H={report.human_ast_nodes} A={report.agent_ast_nodes})")
    print(
        f"files:        H={report.human_file_count} A={report.agent_file_count}  "
        f"|F_A Δ F_H|={drift}"
    )
    churn = "n/a" if report.churn_ratio is None else f"{report.churn_ratio:.4f}"
    print(f"churn_ratio:  {churn}  (agent/human additions+deletions)")
    print(
        f"flags:        agent surgical={report.agent_flags['surgical']} "
        f"sprawl={report.agent_flags['sprawl']} | "
        f"human surgical={report.human_flags['surgical']} "
        f"sprawl={report.human_flags['sprawl']}"
    )
    for n in report.notes:
        print(f"note:         {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
