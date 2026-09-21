"""Cross-repo human pattern baselines (ACE-Bench step 2).

Reads harvest SQLite DBs in **read-only** mode and writes a separate pattern
prior DB. Never mutates harvest shards or the live harvest file.
"""

from __future__ import annotations

import json
import math
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS pattern_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    harvest_sources_json TEXT NOT NULL,
    corpus_json TEXT,
    status TEXT NOT NULL,
    notes TEXT,
    n_repos INTEGER,
    n_prs INTEGER
);

CREATE TABLE IF NOT EXISTS repo_baselines (
    repo TEXT PRIMARY KEY,
    language TEXT,
    n INTEGER NOT NULL,
    p50_files REAL,
    p90_files REAL,
    p50_churn REAL,
    p90_churn REAL,
    p50_dirs REAL,
    p90_dirs REAL,
    pct_surgical REAL,
    pct_le5 REAL,
    pct_sprawl REAL,
    metrics_json TEXT NOT NULL,
    source_dbs_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    run_id INTEGER
);

CREATE TABLE IF NOT EXISTS global_baselines (
    scope TEXT PRIMARY KEY,
    n_repos INTEGER NOT NULL,
    n_prs INTEGER NOT NULL,
    p50_files REAL,
    p90_files REAL,
    p50_churn REAL,
    p90_churn REAL,
    p50_dirs REAL,
    p90_dirs REAL,
    pct_surgical REAL,
    pct_le5 REAL,
    pct_sprawl REAL,
    metrics_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    run_id INTEGER
);

CREATE TABLE IF NOT EXISTS bucket_stats (
    scope TEXT NOT NULL,
    bucket TEXT NOT NULL,
    n INTEGER NOT NULL,
    pct REAL,
    updated_at TEXT NOT NULL,
    run_id INTEGER,
    PRIMARY KEY (scope, bucket)
);

CREATE INDEX IF NOT EXISTS idx_repo_baselines_lang ON repo_baselines(language);
CREATE INDEX IF NOT EXISTS idx_repo_baselines_n ON repo_baselines(n);
"""

# Surgical / sprawl thresholds (aligned with CORPUS.md Django headlines).
SURGICAL_MAX_FILES = 2
LE5_MAX_FILES = 5
SPRAWL_MIN_FILES = 21  # >20 files


@dataclass(frozen=True, slots=True)
class PrStat:
    """One harvested PR's structural signals for baseline aggregation."""

    repo: str
    pr_number: int
    file_count: int
    churn: int
    directories_touched: int
    decision_points: int
    functions_added: int
    loops_added: int
    source_db: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def percentile(values: list[float] | list[int], p: float) -> float | None:
    """Linear-interpolated percentile; ``p`` in [0, 100]. Empty → None."""
    if not values:
        return None
    if p <= 0:
        return float(min(values))
    if p >= 100:
        return float(max(values))
    ordered = sorted(float(v) for v in values)
    k = (len(ordered) - 1) * (p / 100.0)
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - k) + ordered[hi] * (k - lo)


def open_harvest_ro(db_path: Path) -> sqlite3.Connection:
    """Open a harvest SQLite DB read-only (URI ``mode=ro``)."""
    uri = f"file:{db_path.resolve()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn


def load_language_map(corpus_json: Path | None) -> dict[str, str]:
    """Map ``owner/name`` → language from ``corpus_repos.json`` (all tiers + status)."""
    if corpus_json is None or not corpus_json.is_file():
        return {}
    data = json.loads(corpus_json.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    buckets = ["status", "tier_a", "tier_b", "tier_c", "tier_d", "kickoff"]
    for key in buckets:
        entries = data.get(key)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            repo = entry.get("repo")
            lang = entry.get("lang") or entry.get("language")
            if isinstance(repo, str) and isinstance(lang, str) and lang.strip():
                out[repo] = lang.strip()
    return out


def _metrics_ints(metrics_raw: str | None) -> tuple[int, int, int]:
    if not metrics_raw:
        return 0, 0, 0
    try:
        m = json.loads(metrics_raw)
    except json.JSONDecodeError:
        return 0, 0, 0
    if not isinstance(m, dict):
        return 0, 0, 0
    return (
        int(m.get("decision_points_added") or 0),
        int(m.get("functions_added") or 0),
        int(m.get("loops_added") or 0),
    )


def iter_pr_stats(db_path: Path) -> list[PrStat]:
    """Load PR-level stats from one harvest DB (read-only)."""
    label = str(db_path)
    rows: list[PrStat] = []
    with open_harvest_ro(db_path) as conn:
        cur = conn.execute(
            """
            SELECT repo, pr_number, file_count, additions, deletions,
                   directories_touched, metrics_json
            FROM human_patterns
            """
        )
        for row in cur:
            decisions, funcs, loops = _metrics_ints(row["metrics_json"])
            adds = int(row["additions"] or 0)
            dels = int(row["deletions"] or 0)
            rows.append(
                PrStat(
                    repo=str(row["repo"]),
                    pr_number=int(row["pr_number"]),
                    file_count=int(row["file_count"] or 0),
                    churn=adds + dels,
                    directories_touched=int(row["directories_touched"] or 0),
                    decision_points=decisions,
                    functions_added=funcs,
                    loops_added=loops,
                    source_db=label,
                )
            )
    return rows


def merge_pr_stats(sources: list[tuple[Path, list[PrStat]]]) -> dict[str, list[PrStat]]:
    """Group by repo; dedupe on ``(repo, pr_number)`` (first source wins)."""
    by_repo: dict[str, list[PrStat]] = defaultdict(list)
    seen: set[tuple[str, int]] = set()
    for _path, stats in sources:
        for s in stats:
            key = (s.repo, s.pr_number)
            if key in seen:
                continue
            seen.add(key)
            by_repo[s.repo].append(s)
    return dict(by_repo)


def _pct_share(n_match: int, n: int) -> float | None:
    if n <= 0:
        return None
    return round(100.0 * n_match / n, 2)


def _metrics_agg(stats: list[PrStat]) -> dict[str, Any]:
    decisions = [s.decision_points for s in stats]
    funcs = [s.functions_added for s in stats]
    loops = [s.loops_added for s in stats]
    return {
        "decision_points": {
            "p50": percentile(decisions, 50),
            "p90": percentile(decisions, 90),
            "mean": round(sum(decisions) / len(decisions), 3) if decisions else None,
        },
        "functions_added": {
            "p50": percentile(funcs, 50),
            "p90": percentile(funcs, 90),
            "mean": round(sum(funcs) / len(funcs), 3) if funcs else None,
        },
        "loops_added": {
            "p50": percentile(loops, 50),
            "p90": percentile(loops, 90),
            "mean": round(sum(loops) / len(loops), 3) if loops else None,
        },
    }


def compute_baseline(
    stats: list[PrStat],
    *,
    language: str | None = None,
) -> dict[str, Any]:
    """Compute surgical / churn / dir / metrics aggregates for a PR list."""
    n = len(stats)
    files = [s.file_count for s in stats]
    churn = [s.churn for s in stats]
    dirs = [s.directories_touched for s in stats]
    surgical = sum(1 for f in files if f <= SURGICAL_MAX_FILES)
    le5 = sum(1 for f in files if f <= LE5_MAX_FILES)
    sprawl = sum(1 for f in files if f >= SPRAWL_MIN_FILES)
    sources = sorted({s.source_db for s in stats})
    return {
        "language": language,
        "n": n,
        "p50_files": percentile(files, 50),
        "p90_files": percentile(files, 90),
        "p50_churn": percentile(churn, 50),
        "p90_churn": percentile(churn, 90),
        "p50_dirs": percentile(dirs, 50),
        "p90_dirs": percentile(dirs, 90),
        "pct_surgical": _pct_share(surgical, n),
        "pct_le5": _pct_share(le5, n),
        "pct_sprawl": _pct_share(sprawl, n),
        "metrics": _metrics_agg(stats),
        "source_dbs": sources,
        "n_surgical": surgical,
        "n_le5": le5,
        "n_sprawl": sprawl,
    }


def file_count_buckets(stats: list[PrStat]) -> dict[str, int]:
    """Optional histogram buckets for file_count."""
    buckets = {
        "1": 0,
        "2": 0,
        "3-5": 0,
        "6-10": 0,
        "11-20": 0,
        "21+": 0,
    }
    for s in stats:
        f = s.file_count
        if f <= 1:
            buckets["1"] += 1
        elif f == 2:
            buckets["2"] += 1
        elif f <= 5:
            buckets["3-5"] += 1
        elif f <= 10:
            buckets["6-10"] += 1
        elif f <= 20:
            buckets["11-20"] += 1
        else:
            buckets["21+"] += 1
    return buckets


class PatternBaselineStore:
    """Writable store for cross-repo pattern priors (separate from harvest)."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> PatternBaselineStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def start_run(
        self,
        harvest_sources: list[str],
        corpus_json: str | None,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO pattern_runs (
                started_at, harvest_sources_json, corpus_json, status
            ) VALUES (?, ?, ?, ?)
            """,
            (_utc_now(), json.dumps(harvest_sources), corpus_json, "running"),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def finish_run(
        self,
        run_id: int,
        *,
        status: str,
        n_repos: int,
        n_prs: int,
        notes: str = "",
    ) -> None:
        self._conn.execute(
            """
            UPDATE pattern_runs
            SET finished_at = ?, status = ?, notes = ?, n_repos = ?, n_prs = ?
            WHERE id = ?
            """,
            (_utc_now(), status, notes, n_repos, n_prs, run_id),
        )
        self._conn.commit()

    def upsert_repo_baseline(
        self,
        repo: str,
        baseline: dict[str, Any],
        run_id: int,
    ) -> None:
        now = _utc_now()
        self._conn.execute(
            """
            INSERT INTO repo_baselines (
                repo, language, n,
                p50_files, p90_files, p50_churn, p90_churn, p50_dirs, p90_dirs,
                pct_surgical, pct_le5, pct_sprawl,
                metrics_json, source_dbs_json, updated_at, run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(repo) DO UPDATE SET
                language = excluded.language,
                n = excluded.n,
                p50_files = excluded.p50_files,
                p90_files = excluded.p90_files,
                p50_churn = excluded.p50_churn,
                p90_churn = excluded.p90_churn,
                p50_dirs = excluded.p50_dirs,
                p90_dirs = excluded.p90_dirs,
                pct_surgical = excluded.pct_surgical,
                pct_le5 = excluded.pct_le5,
                pct_sprawl = excluded.pct_sprawl,
                metrics_json = excluded.metrics_json,
                source_dbs_json = excluded.source_dbs_json,
                updated_at = excluded.updated_at,
                run_id = excluded.run_id
            """,
            (
                repo,
                baseline.get("language"),
                int(baseline["n"]),
                baseline.get("p50_files"),
                baseline.get("p90_files"),
                baseline.get("p50_churn"),
                baseline.get("p90_churn"),
                baseline.get("p50_dirs"),
                baseline.get("p90_dirs"),
                baseline.get("pct_surgical"),
                baseline.get("pct_le5"),
                baseline.get("pct_sprawl"),
                json.dumps(baseline.get("metrics") or {}),
                json.dumps(baseline.get("source_dbs") or []),
                now,
                run_id,
            ),
        )

    def upsert_global_baseline(
        self,
        scope: str,
        baseline: dict[str, Any],
        *,
        n_repos: int,
        run_id: int,
    ) -> None:
        now = _utc_now()
        self._conn.execute(
            """
            INSERT INTO global_baselines (
                scope, n_repos, n_prs,
                p50_files, p90_files, p50_churn, p90_churn, p50_dirs, p90_dirs,
                pct_surgical, pct_le5, pct_sprawl,
                metrics_json, updated_at, run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(scope) DO UPDATE SET
                n_repos = excluded.n_repos,
                n_prs = excluded.n_prs,
                p50_files = excluded.p50_files,
                p90_files = excluded.p90_files,
                p50_churn = excluded.p50_churn,
                p90_churn = excluded.p90_churn,
                p50_dirs = excluded.p50_dirs,
                p90_dirs = excluded.p90_dirs,
                pct_surgical = excluded.pct_surgical,
                pct_le5 = excluded.pct_le5,
                pct_sprawl = excluded.pct_sprawl,
                metrics_json = excluded.metrics_json,
                updated_at = excluded.updated_at,
                run_id = excluded.run_id
            """,
            (
                scope,
                n_repos,
                int(baseline["n"]),
                baseline.get("p50_files"),
                baseline.get("p90_files"),
                baseline.get("p50_churn"),
                baseline.get("p90_churn"),
                baseline.get("p50_dirs"),
                baseline.get("p90_dirs"),
                baseline.get("pct_surgical"),
                baseline.get("pct_le5"),
                baseline.get("pct_sprawl"),
                json.dumps(baseline.get("metrics") or {}),
                now,
                run_id,
            ),
        )

    def replace_bucket_stats(
        self,
        scope: str,
        buckets: dict[str, int],
        run_id: int,
    ) -> None:
        now = _utc_now()
        total = sum(buckets.values()) or 1
        self._conn.execute("DELETE FROM bucket_stats WHERE scope = ?", (scope,))
        for name, count in buckets.items():
            self._conn.execute(
                """
                INSERT INTO bucket_stats (scope, bucket, n, pct, updated_at, run_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (scope, name, count, round(100.0 * count / total, 2), now, run_id),
            )

    def commit(self) -> None:
        self._conn.commit()

    def summary(self) -> dict[str, Any]:
        global_row = self._conn.execute(
            "SELECT * FROM global_baselines WHERE scope = 'all'"
        ).fetchone()
        n_repos = self._conn.execute("SELECT COUNT(*) AS n FROM repo_baselines").fetchone()[
            "n"
        ]
        return {
            "n_repos": int(n_repos),
            "global_all": dict(global_row) if global_row else None,
        }


def build_pattern_db(
    harvest_dbs: list[Path],
    out_path: Path,
    *,
    corpus_json: Path | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Analyze harvest DBs read-only and upsert into ``out_path`` pattern DB."""
    if not harvest_dbs:
        raise ValueError("at least one harvest DB is required")

    lang_map = load_language_map(corpus_json)
    loaded: list[tuple[Path, list[PrStat]]] = []
    for db in harvest_dbs:
        if not db.is_file():
            raise FileNotFoundError(f"harvest DB not found: {db}")
        loaded.append((db, iter_pr_stats(db)))

    by_repo = merge_pr_stats(loaded)
    source_labels = [str(p) for p, _ in loaded]

    with PatternBaselineStore(out_path) as store:
        run_id = store.start_run(
            source_labels,
            str(corpus_json) if corpus_json else None,
        )
        all_stats: list[PrStat] = []
        by_lang: dict[str, list[PrStat]] = defaultdict(list)

        for repo, stats in sorted(by_repo.items()):
            lang = lang_map.get(repo)
            baseline = compute_baseline(stats, language=lang)
            store.upsert_repo_baseline(repo, baseline, run_id)
            all_stats.extend(stats)
            lang_key = lang or "unknown"
            by_lang[lang_key].extend(stats)

        global_base = compute_baseline(all_stats)
        store.upsert_global_baseline(
            "all",
            global_base,
            n_repos=len(by_repo),
            run_id=run_id,
        )
        store.replace_bucket_stats("all", file_count_buckets(all_stats), run_id)

        lang_summaries: dict[str, dict[str, Any]] = {}
        for lang, stats in sorted(by_lang.items()):
            scope = f"lang:{lang}"
            base = compute_baseline(stats, language=lang)
            n_repos_lang = len({s.repo for s in stats})
            store.upsert_global_baseline(
                scope,
                base,
                n_repos=n_repos_lang,
                run_id=run_id,
            )
            store.replace_bucket_stats(scope, file_count_buckets(stats), run_id)
            lang_summaries[lang] = {
                "n_prs": len(stats),
                "n_repos": n_repos_lang,
                "p50_files": base.get("p50_files"),
                "pct_surgical": base.get("pct_surgical"),
            }

        store.finish_run(
            run_id,
            status="ok",
            n_repos=len(by_repo),
            n_prs=len(all_stats),
            notes=notes,
        )
        store.commit()
        result = {
            "out": str(out_path),
            "run_id": run_id,
            "n_repos": len(by_repo),
            "n_prs": len(all_stats),
            "harvest_sources": source_labels,
            "global": {
                "p50_files": global_base.get("p50_files"),
                "p90_files": global_base.get("p90_files"),
                "p50_churn": global_base.get("p50_churn"),
                "pct_surgical": global_base.get("pct_surgical"),
                "pct_le5": global_base.get("pct_le5"),
                "pct_sprawl": global_base.get("pct_sprawl"),
            },
            "by_language": lang_summaries,
        }
    return result
