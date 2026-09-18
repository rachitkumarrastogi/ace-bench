"""Console entry point for `ace-harvest` (same CLI as scripts/run_harvest.py)."""

from __future__ import annotations

import argparse
import json
import os
import sys

from ace_bench.db import PatternStore
from ace_bench.harvest import (
    MAX_PRS_HARD_CAP,
    MIN_REST_SLEEP_SECONDS,
    SEARCH_PAGE_SLEEP_SECONDS,
    SEARCH_RESULT_CAP,
    HarvestConfig,
    harvest,
    validate_repo_slug,
)
from ace_bench.paths import PathEscapeError, resolve_allowed_path
from ace_bench.tokens import resolve_github_token

DEFAULT_DB = os.environ.get("ACE_DB_PATH", "./data/ace_patterns.sqlite")
DEFAULT_REPOS = ["django/django"]
DEFAULT_MERGED_BEFORE = "2021-01-01"
DEFAULT_FULL_MERGED_AFTER = "2012-01-01"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Harvest merged GitHub PRs as human baseline patterns (ACE-Bench).",
    )
    p.add_argument(
        "--repos",
        nargs="+",
        default=DEFAULT_REPOS,
        help=f"owner/name repos to harvest (default: {' '.join(DEFAULT_REPOS)})",
    )
    p.add_argument(
        "--merged-before",
        default=DEFAULT_MERGED_BEFORE,
        help=f"Exclusive upper bound on merge date YYYY-MM-DD (default: {DEFAULT_MERGED_BEFORE})",
    )
    p.add_argument(
        "--merged-after",
        default=None,
        help="Optional inclusive lower bound on merge date YYYY-MM-DD "
        f"(required with --window; full Django baseline uses {DEFAULT_FULL_MERGED_AFTER})",
    )
    p.add_argument(
        "--max-prs",
        type=int,
        default=None,
        help=(
            "Max PRs to harvest per repo per window "
            f"(default: 100 pilot; {SEARCH_RESULT_CAP} when --window is set; "
            f"hard cap {MAX_PRS_HARD_CAP})"
        ),
    )
    p.add_argument(
        "--window",
        choices=("days", "months"),
        default=None,
        help=(
            "Auto-slice [--merged-after, --merged-before) into date windows so each "
            f"GitHub Search query stays under the {SEARCH_RESULT_CAP}-result cap. "
            "Requires --merged-after."
        ),
    )
    p.add_argument(
        "--window-size",
        type=int,
        default=1,
        help="Number of days or months per window when --window is set (default: 1)",
    )
    p.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"SQLite path (default: ACE_DB_PATH or {DEFAULT_DB})",
    )
    p.add_argument(
        "--sleep",
        type=float,
        default=0.75,
        help=(
            "Seconds between GitHub REST calls "
            f"(default: 0.75; Search pages floor at {SEARCH_PAGE_SLEEP_SECONDS}s)"
        ),
    )
    p.add_argument(
        "--summary-only",
        action="store_true",
        help="Print DB summary and exit (no network)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        db_path = resolve_allowed_path(args.db, purpose="--db")
    except PathEscapeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    with PatternStore(db_path) as store:
        if args.summary_only:
            print(json.dumps(store.summary(), indent=2))
            return 0

        if args.window and not args.merged_after:
            print("error: --merged-after is required when using --window", file=sys.stderr)
            return 2

        if args.window_size < 1:
            print("error: --window-size must be >= 1", file=sys.stderr)
            return 2

        if args.sleep < MIN_REST_SLEEP_SECONDS:
            print(
                f"error: --sleep must be >= {MIN_REST_SLEEP_SECONDS}",
                file=sys.stderr,
            )
            return 2

        try:
            repos = [validate_repo_slug(r) for r in args.repos]
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        token = resolve_github_token()
        if not token:
            print(
                "warning: no GITHUB_TOKEN/GH_TOKEN/token file — "
                "unauthenticated rate limits are low",
                file=sys.stderr,
            )

        if args.max_prs is not None:
            if args.max_prs < 1:
                print("error: --max-prs must be >= 1", file=sys.stderr)
                return 2
            max_prs = min(args.max_prs, MAX_PRS_HARD_CAP)
            if args.max_prs > MAX_PRS_HARD_CAP:
                print(
                    f"warning: --max-prs clamped to {MAX_PRS_HARD_CAP} "
                    "(GitHub Search API cap)",
                    file=sys.stderr,
                )
        elif args.window:
            max_prs = SEARCH_RESULT_CAP
        else:
            max_prs = 100

        config = HarvestConfig(
            repos=repos,
            merged_before=args.merged_before,
            merged_after=args.merged_after,
            max_prs_per_repo=max_prs,
            sleep_seconds=args.sleep,
            token=token,
            window_unit=args.window,
            window_size=args.window_size,
        )
        result = harvest(store, config)
        print(json.dumps(result, indent=2))
        if result["error_count"] and result["inserted"] == 0 and result["updated"] == 0:
            return 2
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
