#!/usr/bin/env python3
"""Rotate ACE live SQLite into a numbered shard when size ≥ ~1 GiB.

Safe only when nothing is writing the live DB (call between harvest repos).
Moves the completed file to data/shards/ace_patterns_shard_NNN.sqlite, starts a
fresh empty ace_patterns.sqlite (schema via PatternStore), and appends an entry
to data/shards_manifest.json.

Exit codes:
  0 — under threshold, or rotate completed / dry-run would rotate
  1 — error (path, busy lock, I/O)
  2 — over threshold but --check-only (no rotate)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ace_bench.db import PatternStore
from ace_bench.paths import PathEscapeError, resolve_allowed_path

DEFAULT_LIMIT_BYTES = 1_073_741_824
SHARD_NAME_RE = re.compile(r"^ace_patterns_shard_(\d+)\.sqlite$")
MANIFEST_NAME = "shards_manifest.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--db",
        default=os.environ.get("ACE_DB_PATH", "./data/ace_patterns.sqlite"),
        help="Live SQLite path (default: ACE_DB_PATH or ./data/ace_patterns.sqlite)",
    )
    p.add_argument(
        "--limit-bytes",
        type=int,
        default=DEFAULT_LIMIT_BYTES,
        help=f"Rotate when size ≥ this many bytes (default: {DEFAULT_LIMIT_BYTES})",
    )
    p.add_argument(
        "--shards-dir",
        default=None,
        help="Directory for completed shards (default: <db-parent>/shards)",
    )
    p.add_argument(
        "--manifest",
        default=None,
        help=f"Manifest JSON path (default: <db-parent>/{MANIFEST_NAME})",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Rotate even if under the size limit",
    )
    p.add_argument(
        "--check-only",
        action="store_true",
        help="Report whether rotate is needed; do not move files",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned rotate without changing files",
    )
    p.add_argument(
        "--repos-covered",
        default="",
        help="Optional comma-separated repo slugs for the manifest entry",
    )
    p.add_argument(
        "--allow-busy",
        action="store_true",
        help="Skip the SQLite busy/lock probe (dangerous if harvest is writing)",
    )
    return p.parse_args(argv)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _db_stats(db_path: Path) -> dict[str, object]:
    size = db_path.stat().st_size
    rows = 0
    repos: list[str] = []
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5.0)
        try:
            rows = int(conn.execute("SELECT COUNT(*) FROM human_patterns").fetchone()[0])
            repos = [
                str(r[0])
                for r in conn.execute(
                    "SELECT DISTINCT repo FROM human_patterns ORDER BY repo"
                ).fetchall()
            ]
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return {
            "size_bytes": size,
            "approx_rows": None,
            "repos": [],
            "stats_error": str(exc),
        }
    return {"size_bytes": size, "approx_rows": rows, "repos": repos}


def _assert_not_busy(db_path: Path) -> None:
    """Fail if another connection holds a write lock."""
    try:
        conn = sqlite3.connect(str(db_path), timeout=0.5)
    except sqlite3.OperationalError as exc:
        raise RuntimeError(f"DB busy (cannot open): {exc}") from exc
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("ROLLBACK")
    except sqlite3.OperationalError as exc:
        raise RuntimeError(f"DB write-locked (harvest still writing?): {exc}") from exc
    finally:
        conn.close()


def _next_shard_index(shards_dir: Path) -> int:
    highest = 0
    if shards_dir.is_dir():
        for path in shards_dir.iterdir():
            m = SHARD_NAME_RE.match(path.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def _load_manifest(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {"version": 1, "shards": [], "updated_at": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "shards": [], "updated_at": None}
    if not isinstance(data, dict):
        return {"version": 1, "shards": [], "updated_at": None}
    shards = data.get("shards")
    if not isinstance(shards, list):
        data["shards"] = []
    data.setdefault("version", 1)
    return data


def _write_manifest(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _utc_now()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        db_path = resolve_allowed_path(args.db, purpose="--db")
    except PathEscapeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not db_path.is_file():
        payload = {"db": str(db_path), "exists": False, "action": "none"}
        print(json.dumps(payload, indent=2))
        return 0

    size = db_path.stat().st_size
    over = size >= args.limit_bytes
    shards_dir = (
        resolve_allowed_path(args.shards_dir, purpose="--shards-dir")
        if args.shards_dir
        else (db_path.parent / "shards")
    )
    manifest_path = (
        resolve_allowed_path(args.manifest, purpose="--manifest")
        if args.manifest
        else (db_path.parent / MANIFEST_NAME)
    )

    base = {
        "db": str(db_path),
        "size_bytes": size,
        "size_gib": round(size / (1024**3), 3),
        "limit_bytes": args.limit_bytes,
        "over_threshold": over,
        "shards_dir": str(shards_dir),
        "manifest": str(manifest_path),
    }

    if not over and not args.force:
        print(json.dumps({**base, "action": "none"}, indent=2))
        return 0

    if args.check_only:
        print(json.dumps({**base, "action": "would_rotate"}, indent=2))
        return 2

    stats = _db_stats(db_path)
    shard_idx = _next_shard_index(shards_dir)
    shard_name = f"ace_patterns_shard_{shard_idx:03d}.sqlite"
    shard_path = shards_dir / shard_name
    repos_covered = [r.strip() for r in args.repos_covered.split(",") if r.strip()]
    if not repos_covered:
        repos_covered = list(stats.get("repos") or [])

    plan = {
        **base,
        "action": "rotate",
        "shard_path": str(shard_path),
        "approx_rows": stats.get("approx_rows"),
        "repos_covered_count": len(repos_covered),
        "dry_run": bool(args.dry_run),
    }
    print(json.dumps(plan, indent=2))

    if args.dry_run:
        return 0

    if not args.allow_busy:
        try:
            _assert_not_busy(db_path)
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    shards_dir.mkdir(parents=True, exist_ok=True)
    if shard_path.exists():
        print(f"error: shard already exists: {shard_path}", file=sys.stderr)
        return 1

    # Move completed live DB aside, then create a fresh empty file with schema.
    db_path.rename(shard_path)
    try:
        with PatternStore(db_path):
            pass
    except Exception as exc:
        # Best-effort rollback: move shard back if fresh DB failed.
        if not db_path.exists() and shard_path.is_file():
            shard_path.rename(db_path)
        print(f"error: failed to create fresh DB after move: {exc}", file=sys.stderr)
        return 1

    entry = {
        "path": str(shard_path),
        "name": shard_name,
        "approx_rows": stats.get("approx_rows"),
        "size_bytes": stats.get("size_bytes", size),
        "created_at": _utc_now(),
        "repos_covered": repos_covered,
        "source_live_db": str(db_path),
    }
    if stats.get("stats_error"):
        entry["stats_error"] = stats["stats_error"]

    manifest = _load_manifest(manifest_path)
    shards = list(manifest.get("shards") or [])
    shards.append(entry)
    manifest["shards"] = shards
    manifest["live_db"] = str(db_path)
    _write_manifest(manifest_path, manifest)

    done = {
        **plan,
        "action": "rotated",
        "fresh_db": str(db_path),
        "fresh_size_bytes": db_path.stat().st_size,
        "manifest_shards": len(shards),
    }
    print(json.dumps(done, indent=2))
    print(
        f"rotated: {shard_path} ({stats.get('approx_rows')} rows, "
        f"{size} bytes) → fresh {db_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
