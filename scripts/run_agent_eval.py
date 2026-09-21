#!/usr/bin/env python3
"""Run a named model/agent against one harvest instance and score vs human.

Flow:
  load human row → (optional) sandbox @ base_sha → agent → score → eval_runs

Examples:
  # Offline human-replay (ACE ≈ 1.0) — skip network checkout:
  python3 scripts/run_agent_eval.py \\
    --instance django/django#22 \\
    --model human-replay \\
    --agent file \\
    --agent-patch /tmp/human.diff \\
    --passed-tests true \\
    --skip-sandbox \\
    --db data/frozen/ace_patterns_django_pre2021_6125.sqlite

  # Stub plumbing (tiny patch → ACE ≫ 1; --stub-bloated → ACE ≪ 1):
  python3 scripts/run_agent_eval.py \\
    --instance django/django#22 --model stub-default --agent stub \\
    --passed-tests true --skip-sandbox
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.agents import AGENT_NAMES, AgentError, build_agent
from ace_bench.agents.base import AgentContext
from ace_bench.db import PatternStore
from ace_bench.eval_runs import (
    EvalRunStore,
    default_eval_runs_db_path,
    patch_sha256,
)
from ace_bench.eval_v0 import (
    InstanceIdError,
    files_from_patch,
    parse_instance_id,
    score_agent_vs_human,
)
from ace_bench.paths import PathEscapeError, resolve_allowed_path
from ace_bench.pr_artifact import write_agent_pr_md
from ace_bench.sandbox import (
    SandboxError,
    checkout_at_base_sha,
    default_work_root,
    env_prefers_docker,
)

FROZEN_NAME = "ace_patterns_django_pre2021_6125.sqlite"


def resolve_harvest_db(cli_db: str | None) -> Path:
    if cli_db:
        return resolve_allowed_path(cli_db, purpose="--db")
    env = os.environ.get("ACE_DB_PATH")
    if env:
        return resolve_allowed_path(env, purpose="ACE_DB_PATH")
    for c in (
        Path("data/frozen") / FROZEN_NAME,
        Path.home() / "ace-bench" / "data" / "frozen" / FROZEN_NAME,
        Path.home() / "ace-bench-data" / "shards" / "ace_patterns_shard_001.sqlite",
        Path("data/ace_patterns.sqlite"),
    ):
        try:
            resolved = resolve_allowed_path(c, purpose="db candidate")
        except PathEscapeError:
            continue
        if resolved.is_file():
            return resolved
    return resolve_allowed_path(Path("data/frozen") / FROZEN_NAME, purpose="default db")


def parse_instance(value: str) -> tuple[str, int]:
    try:
        return parse_instance_id(value)
    except InstanceIdError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def parse_passed(value: str) -> bool | None:
    v = value.strip().lower()
    if v in ("1", "true", "yes", "y", "pass", "passed"):
        return True
    if v in ("0", "false", "no", "n", "fail", "failed"):
        return False
    if v in ("unknown", "null", "none", "?"):
        return None
    raise argparse.ArgumentTypeError("expected true|false|unknown")


def load_prior_snippet(prior_db: Path | None, repo: str) -> dict[str, Any] | None:
    if prior_db is None:
        return None
    if not prior_db.is_file():
        return {"error": f"prior DB not found: {prior_db}"}
    conn = sqlite3.connect(f"file:{prior_db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT repo, p50_files, p90_files, pct_surgical, n FROM repo_baselines WHERE repo = ?",
            (repo,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)
    except sqlite3.Error as exc:
        return {"error": str(exc)}
    finally:
        conn.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--instance",
        type=parse_instance,
        required=True,
        help="owner/repo#pr (e.g. django/django#22)",
    )
    p.add_argument(
        "--model",
        required=True,
        help="model_name stored on the run (required even for file/stub)",
    )
    p.add_argument(
        "--agent",
        choices=AGENT_NAMES,
        required=True,
        help="agent backend",
    )
    p.add_argument("--agent-patch", default=None, help="path for --agent file")
    p.add_argument("--db", default=None, help="harvest / frozen SQLite")
    p.add_argument(
        "--eval-db",
        default=None,
        help=f"eval_runs SQLite (default: {default_eval_runs_db_path()})",
    )
    p.add_argument("--prior", default=None, help="optional pattern prior SQLite")
    p.add_argument(
        "--passed-tests",
        type=parse_passed,
        default="unknown",
        help="true|false|unknown (default unknown: store null, score structurally)",
    )
    p.add_argument(
        "--work-root",
        default=None,
        help=f"sandbox root (default: {default_work_root()})",
    )
    p.add_argument(
        "--skip-sandbox",
        action="store_true",
        help="skip git checkout (offline scoring only)",
    )
    p.add_argument(
        "--prefer-docker",
        action="store_true",
        help="prefer docker when available (MVP still host-git checkout)",
    )
    p.add_argument(
        "--save-patch-dir",
        default=None,
        help="write agent.patch under this dir (default: worktree or eval data)",
    )
    p.add_argument(
        "--stub-bloated",
        action="store_true",
        help="with --agent stub: emit multi-file sprawl (ACE ≪ 1 vs surgical human)",
    )
    p.add_argument(
        "--no-pr-artifact",
        action="store_true",
        help="skip writing AGENT_PR.md (PR-shaped local summary)",
    )
    p.add_argument("--json", action="store_true", help="JSON summary only")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo, pr_number = args.instance
    instance_id = f"{repo}#{pr_number}"
    model_name = (args.model or "").strip()
    if not model_name:
        print("error: --model is required and must be non-empty", file=sys.stderr)
        return 2

    try:
        harvest_db = resolve_harvest_db(args.db)
        eval_db = resolve_allowed_path(
            args.eval_db or default_eval_runs_db_path(),
            purpose="--eval-db",
        )
        prior_path = None
        if args.prior:
            prior_path = resolve_allowed_path(args.prior, purpose="--prior")
    except (PathEscapeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not harvest_db.is_file():
        print(f"error: harvest DB not found: {harvest_db}", file=sys.stderr)
        return 2

    with PatternStore(harvest_db) as store:
        human = store.get_pattern(repo, pr_number)
    if human is None:
        print(
            f"error: no human baseline for {instance_id} in {harvest_db}",
            file=sys.stderr,
        )
        return 2

    # unknown: store NULL but still compute structural ACE (assume pass gate).
    # false: ACE = 0. true: full formula.
    passed_store = args.passed_tests
    passed_for_score = True if args.passed_tests is None else args.passed_tests

    with EvalRunStore(eval_db) as runs:
        run_id = runs.start_run(
            instance_id=instance_id,
            model_name=model_name,
            agent_name=args.agent,
        )

        worktree: Path | None = None
        sandbox_note = "sandbox skipped"
        try:
            if not args.skip_sandbox:
                if not human.base_sha:
                    raise SandboxError("human row has empty base_sha")
                checkout = checkout_at_base_sha(
                    repo=human.repo,
                    base_sha=human.base_sha,
                    work_root=args.work_root,
                    title=human.title,
                    body=human.body,
                    instance_id=instance_id,
                    prefer_docker=args.prefer_docker or env_prefers_docker(),
                )
                worktree = checkout.worktree
                sandbox_note = f"sandbox={worktree}"
        except SandboxError as exc:
            runs.finish_run(run_id, error=f"sandbox: {exc}", notes=str(exc))
            print(f"error: sandbox: {exc}", file=sys.stderr)
            return 2

        if args.stub_bloated and args.agent != "stub":
            print(
                "error: --stub-bloated only applies to --agent stub",
                file=sys.stderr,
            )
            return 2

        try:
            agent = build_agent(
                args.agent,
                model_name=model_name,
                agent_patch=args.agent_patch,
                stub_bloated=args.stub_bloated,
            )
            ctx = AgentContext(
                instance_id=instance_id,
                repo=human.repo,
                pr_number=human.pr_number,
                title=human.title or "",
                body=human.body or "",
                model_name=model_name,
                worktree=worktree,
                human_files=list(human.files),
                base_sha=human.base_sha,
            )
            agent_result = agent.run(ctx)
        except AgentError as exc:
            runs.finish_run(run_id, error=str(exc), notes=sandbox_note)
            print(f"error: agent: {exc}", file=sys.stderr)
            return 2

        agent_patch = agent_result.patch_text
        agent_files = files_from_patch(agent_patch) or list(human.files)

        # Persist patch under worktree or save dir.
        patch_path: Path | None = None
        try:
            if args.save_patch_dir:
                patch_dir = resolve_allowed_path(
                    args.save_patch_dir, purpose="--save-patch-dir"
                )
            elif worktree is not None:
                patch_dir = worktree / ".ace_bench"
            else:
                patch_dir = resolve_allowed_path(
                    Path("data") / "eval" / "agent_patches",
                    purpose="default patch dir",
                )
            patch_dir.mkdir(parents=True, exist_ok=True)
            safe_model = "".join(
                c if c.isalnum() or c in "-_." else "_" for c in model_name
            )[:64]
            patch_path = patch_dir / f"{repo.replace('/', '__')}__{pr_number}__{safe_model}.patch"
            patch_path.write_text(agent_patch, encoding="utf-8")
        except (PathEscapeError, OSError) as exc:
            patch_path = None
            agent_notes_extra = f"patch save failed: {exc}"
        else:
            agent_notes_extra = ""

        report = score_agent_vs_human(
            repo=human.repo,
            pr_number=human.pr_number,
            human_files=list(human.files),
            human_patch=human.patch_text,
            agent_patch=agent_patch,
            passed_tests=passed_for_score,
            human_metrics=human.metrics,
            agent_files=agent_files,
        )

        prior = load_prior_snippet(prior_path, human.repo)
        notes_parts = [
            sandbox_note,
            agent_result.notes,
            agent_notes_extra,
            f"ast_proxy={report.ast_proxy}",
        ]
        if prior:
            notes_parts.append(f"prior={json.dumps(prior, sort_keys=True)}")
        notes = "; ".join(n for n in notes_parts if n)

        pr_path: Path | None = None
        if not args.no_pr_artifact:
            try:
                if worktree is not None:
                    pr_dir = worktree
                elif patch_path is not None:
                    pr_dir = patch_path.parent
                else:
                    pr_dir = resolve_allowed_path(
                        Path("data") / "eval" / "agent_patches",
                        purpose="default pr artifact dir",
                    )
                pr_path = write_agent_pr_md(
                    pr_dir,
                    title=human.title or instance_id,
                    model_name=model_name,
                    instance_id=instance_id,
                    ace_score=float(report.ace_score),
                    file_drift=int(report.boundary["symmetric_diff_size"]),
                    human_files=list(human.files),
                    agent_files=list(agent_files),
                    agent_name=args.agent,
                    churn_ratio=report.churn_ratio,
                    patch_path=patch_path,
                    base_sha=human.base_sha,
                )
                notes = f"{notes}; pr_artifact={pr_path}" if notes else f"pr_artifact={pr_path}"
            except (PathEscapeError, OSError) as exc:
                notes = f"{notes}; pr_artifact failed: {exc}" if notes else str(exc)

        runs.finish_run(
            run_id,
            passed_tests=passed_store,
            ace_score=report.ace_score,
            file_drift=int(report.boundary["symmetric_diff_size"]),
            churn_ratio=report.churn_ratio,
            human_files=list(human.files),
            agent_files=list(agent_files),
            notes=notes,
            patch_path=str(patch_path) if patch_path else None,
            patch_hash=patch_sha256(agent_patch),
        )
        stored = runs.get_run(run_id)

    summary: dict[str, Any] = {
        "run_id": run_id,
        "instance_id": instance_id,
        "model_name": model_name,
        "agent_name": args.agent,
        "ace_score": report.ace_score,
        "file_drift": report.boundary["symmetric_diff_size"],
        "churn_ratio": report.churn_ratio,
        "passed_tests": passed_store,
        "human_files": list(human.files),
        "agent_files": agent_files,
        "human_added_lines": report.human_added_lines,
        "agent_added_lines": report.agent_added_lines,
        "base_sha": human.base_sha,
        "worktree": str(worktree) if worktree else None,
        "patch_path": str(patch_path) if patch_path else None,
        "pr_artifact": str(pr_path) if pr_path else None,
        "patch_hash": stored.patch_hash if stored else None,
        "eval_db": str(eval_db),
        "harvest_db": str(harvest_db),
        "prior": prior,
        "notes": notes,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"run_id:       {run_id}")
        print(f"instance:     {instance_id}")
        print(f"model_name:   {model_name}")
        print(f"agent:        {args.agent}")
        print(f"ACE score:    {report.ace_score:.6f}")
        print(f"file_drift:   {report.boundary['symmetric_diff_size']}")
        churn = "n/a" if report.churn_ratio is None else f"{report.churn_ratio:.4f}"
        print(f"churn_ratio:  {churn}")
        print(f"files:        H={report.human_file_count} A={report.agent_file_count}")
        print(f"eval_db:      {eval_db}")
        if worktree:
            print(f"worktree:     {worktree}")
        if pr_path:
            print(f"pr_artifact:  {pr_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
