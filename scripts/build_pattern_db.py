#!/usr/bin/env python3
"""Build ACE pattern prior DB from harvest SQLite (read-only).

Does not lock or mutate harvest DBs. Prefer frozen shard_001 as primary input;
optionally add live DB (also opened mode=ro) or a sqlite .backup snapshot.

Examples:
  python3 scripts/build_pattern_db.py \\
    --harvest-db ~/ace-bench/data/shards/ace_patterns_shard_001.sqlite \\
    --out ~/ace-bench/data/patterns/ace_patterns_prior.sqlite

  python3 scripts/build_pattern_db.py \\
    --shards-dir ~/ace-bench/data/shards \\
    --harvest-db ~/ace-bench/data/ace_patterns.sqlite \\
    --corpus-json data/corpus_repos.json \\
    --out ~/ace-bench/data/patterns/ace_patterns_prior.sqlite
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.paths import PathEscapeError, resolve_allowed_path
from ace_bench.pattern_db import build_pattern_db


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--harvest-db",
        action="append",
        default=[],
        dest="harvest_dbs",
        help="Harvest SQLite path (repeatable). Opened read-only.",
    )
    p.add_argument(
        "--shards-dir",
        default=None,
        help="Directory of ace_patterns_shard_*.sqlite files to include",
    )
    p.add_argument(
        "--out",
        default=os.environ.get(
            "ACE_PATTERN_DB_PATH",
            str(Path.home() / "ace-bench" / "data" / "patterns" / "ace_patterns_prior.sqlite"),
        ),
        help="Output pattern prior DB (default: ACE_PATTERN_DB_PATH or ~/ace-bench/data/patterns/...)",
    )
    p.add_argument(
        "--corpus-json",
        default=None,
        help="corpus_repos.json for language join (default: data/corpus_repos.json beside repo)",
    )
    p.add_argument(
        "--notes",
        default="",
        help="Optional note stored on pattern_runs",
    )
    return p.parse_args(argv)


def _discover_shards(shards_dir: Path) -> list[Path]:
    return sorted(shards_dir.glob("ace_patterns_shard_*.sqlite"))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    default_corpus = repo_root / "data" / "corpus_repos.json"

    try:
        out_path = resolve_allowed_path(args.out, purpose="--out")
        harvest_paths: list[Path] = []
        for raw in args.harvest_dbs:
            harvest_paths.append(
                resolve_allowed_path(raw, purpose="--harvest-db", must_exist=True)
            )
        if args.shards_dir:
            shards_dir = resolve_allowed_path(
                args.shards_dir, purpose="--shards-dir", must_exist=True
            )
            if not shards_dir.is_dir():
                print(f"error: --shards-dir is not a directory: {shards_dir}", file=sys.stderr)
                return 1
            harvest_paths.extend(_discover_shards(shards_dir))

        corpus_raw = args.corpus_json
        if corpus_raw is None and default_corpus.is_file():
            corpus_raw = str(default_corpus)
        corpus_path: Path | None = None
        if corpus_raw:
            corpus_path = resolve_allowed_path(
                corpus_raw, purpose="--corpus-json", must_exist=True
            )
    except (PathEscapeError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Dedupe paths while preserving order (shard_001 before live if both listed).
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in harvest_paths:
        resolved = p.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)

    if not unique:
        print(
            "error: no harvest DBs (pass --harvest-db and/or --shards-dir)",
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            {
                "harvest_dbs": [str(p) for p in unique],
                "out": str(out_path),
                "corpus_json": str(corpus_path) if corpus_path else None,
            },
            indent=2,
        )
    )

    result = build_pattern_db(
        unique,
        out_path,
        corpus_json=corpus_path,
        notes=args.notes,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
