#!/usr/bin/env python3
"""Export ~50 Django ACE eval instances (metadata-only JSONL; patches stay in DB).

DB path resolution (first match):
  1. --db CLI arg
  2. ACE_DB_PATH env
  3. data/frozen/ace_patterns_django_pre2021_6125.sqlite (local or $HOME/ace-bench/…)
  4. ./data/ace_patterns.sqlite (live DB; filter repo=django/django)

Example (DGX frozen):
  export ACE_DB_PATH=$HOME/ace-bench/data/frozen/ace_patterns_django_pre2021_6125.sqlite
  python3 scripts/export_eval_instances.py --limit 50
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.db import PatternStore
from ace_bench.eval_v0 import instance_record_from_row, touches_tests, validate_repo_slug
from ace_bench.paths import PathEscapeError, resolve_allowed_path

FROZEN_NAME = "ace_patterns_django_pre2021_6125.sqlite"
DEFAULT_OUT = Path("benchmarks/django_eval_v0.jsonl")
DEFAULT_REPO = "django/django"


def resolve_db_path(cli_db: str | None) -> Path:
    if cli_db:
        return resolve_allowed_path(cli_db, purpose="--db")
    env = os.environ.get("ACE_DB_PATH")
    if env:
        return resolve_allowed_path(env, purpose="ACE_DB_PATH")
    candidates = [
        Path("data/frozen") / FROZEN_NAME,
        Path.home() / "ace-bench" / "data" / "frozen" / FROZEN_NAME,
        Path("data/ace_patterns.sqlite"),
        Path.home() / "ace-bench" / "data" / "ace_patterns.sqlite",
    ]
    for c in candidates:
        try:
            resolved = resolve_allowed_path(c, purpose="db candidate")
        except PathEscapeError:
            continue
        if resolved.is_file():
            return resolved
    return resolve_allowed_path(candidates[0], purpose="default db")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default=None, help="SQLite path (default: ACE_DB_PATH or frozen)")
    p.add_argument("--repo", default=DEFAULT_REPO, help=f"Repo filter (default: {DEFAULT_REPO})")
    p.add_argument("--limit", type=int, default=50, help="Max instances to export (default: 50)")
    p.add_argument("--min-files", type=int, default=1)
    p.add_argument("--max-files", type=int, default=8)
    p.add_argument(
        "--merged-before",
        default="2021-01-01",
        help="Exclusive merge cutoff ISO date (default: 2021-01-01)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Metadata JSONL path (default: {DEFAULT_OUT})",
    )
    p.add_argument(
        "--no-prefer-tests",
        action="store_true",
        help="Do not rank test-touching PRs first",
    )
    p.add_argument(
        "--write-patches-dir",
        type=Path,
        default=None,
        help="Optional gitignored dir for human patches (smoke only); e.g. data/eval/patches",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        db_path = resolve_db_path(args.db)
        out_path = resolve_allowed_path(args.out, purpose="--out")
        patches_dir = None
        if args.write_patches_dir is not None:
            patches_dir = resolve_allowed_path(
                args.write_patches_dir, purpose="--write-patches-dir"
            )
        repo = validate_repo_slug(args.repo)
    except (PathEscapeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not db_path.is_file():
        print(f"error: DB not found: {db_path}", file=sys.stderr)
        print(
            "Set ACE_DB_PATH or pass --db. On DGX:\n"
            f"  $HOME/ace-bench/data/frozen/{FROZEN_NAME}\n"
            "or live DB filtered to django/django.",
            file=sys.stderr,
        )
        return 2

    with PatternStore(db_path) as store:
        candidates = store.fetch_eval_candidates(
            repo=repo,
            min_files=args.min_files,
            max_files=args.max_files,
            merged_before=args.merged_before,
            limit=None,
        )
        # Attach db id for traceability (query by repo+pr otherwise).
        id_map: dict[tuple[str, int], int] = {}
        for row in store._conn.execute(
            "SELECT id, repo, pr_number FROM human_patterns WHERE repo = ?",
            (repo,),
        ):
            id_map[(row["repo"], int(row["pr_number"]))] = int(row["id"])

    # Prefer test-touching within each file_count bucket, then stratify across
    # file counts so the set is not all single-file PRs.
    by_fc: dict[int, list] = {}
    for p in candidates:
        by_fc.setdefault(p.file_count, []).append(p)
    for bucket in by_fc.values():
        bucket.sort(
            key=lambda pat: (
                0 if (not args.no_prefer_tests and touches_tests(pat.files)) else 1,
                pat.merged_at or "",
                pat.pr_number,
            )
        )

    selected = []
    buckets = [by_fc.get(fc, []) for fc in range(args.min_files, args.max_files + 1)]
    idxs = [0] * len(buckets)
    while len(selected) < args.limit:
        progressed = False
        for i, bucket in enumerate(buckets):
            if idxs[i] < len(bucket):
                selected.append(bucket[idxs[i]])
                idxs[i] += 1
                progressed = True
                if len(selected) >= args.limit:
                    break
        if not progressed:
            break

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if patches_dir is not None:
        patches_dir.mkdir(parents=True, exist_ok=True)

    n_tests = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for p in selected:
            if touches_tests(p.files):
                n_tests += 1
            rec = instance_record_from_row(
                {
                    "id": id_map.get((p.repo, p.pr_number)),
                    "repo": p.repo,
                    "pr_number": p.pr_number,
                    "merged_at": p.merged_at,
                    "base_sha": p.base_sha,
                    "merge_commit_sha": p.merge_commit_sha,
                    "title": p.title,
                    "body": p.body,
                    "html_url": p.html_url,
                    "files": p.files,
                    "file_count": p.file_count,
                    "additions": p.additions,
                    "deletions": p.deletions,
                    "directories_touched": p.directories_touched,
                    "metrics": p.metrics,
                }
            )
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if patches_dir is not None and p.patch_text:
                safe = f"{p.repo.replace('/', '__')}__{p.pr_number}.patch"
                (patches_dir / safe).write_text(p.patch_text, encoding="utf-8")

    print(
        json.dumps(
            {
                "db": str(db_path),
                "repo": repo,
                "exported": len(selected),
                "pool_matched_filters": len(candidates),
                "touches_tests": n_tests,
                "out": str(out_path),
                "patches_dir": str(patches_dir) if patches_dir else None,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
