#!/usr/bin/env python3
"""Report ACE SQLite DB size vs the soft ~1 GiB sharding threshold.

Exit codes:
  0 — under threshold (or missing DB with --ok-missing)
  1 — usage / path errors
  2 — at/over threshold (rotate via scripts/rotate_shard_if_needed.py)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.paths import PathEscapeError, resolve_allowed_path

# Soft guardrail (~1 GiB). Triggers shard rotation between harvest repos.
DEFAULT_WARN_BYTES = 1_073_741_824


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--db",
        default=os.environ.get("ACE_DB_PATH", "./data/ace_patterns.sqlite"),
        help="SQLite path (default: ACE_DB_PATH or ./data/ace_patterns.sqlite)",
    )
    p.add_argument(
        "--warn-bytes",
        type=int,
        default=DEFAULT_WARN_BYTES,
        help=f"Soft size threshold in bytes (default: {DEFAULT_WARN_BYTES})",
    )
    p.add_argument(
        "--ok-missing",
        action="store_true",
        help="Exit 0 if DB file does not exist yet",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        db_path = resolve_allowed_path(args.db, purpose="--db")
    except PathEscapeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not db_path.is_file():
        payload = {"db": str(db_path), "exists": False, "size_bytes": 0}
        print(json.dumps(payload, indent=2))
        if args.ok_missing:
            return 0
        print(f"error: DB not found: {db_path}", file=sys.stderr)
        return 1

    size = db_path.stat().st_size
    over = size >= args.warn_bytes
    payload = {
        "db": str(db_path),
        "exists": True,
        "size_bytes": size,
        "size_gib": round(size / (1024**3), 3),
        "warn_bytes": args.warn_bytes,
        "over_threshold": over,
    }
    print(json.dumps(payload, indent=2))
    if over:
        print(
            f"warning: DB size {size} bytes exceeds soft threshold "
            f"{args.warn_bytes} (~1 GiB). Rotate with "
            "scripts/rotate_shard_if_needed.py between repos (see docs/OPS.md).",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
