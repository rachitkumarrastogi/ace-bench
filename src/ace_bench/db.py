"""SQLite store for harvested human PR patterns (ACE-Bench first pass)."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS harvest_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    repos_json TEXT NOT NULL,
    merged_before TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS human_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT NOT NULL,
    pr_number INTEGER NOT NULL,
    merged_at TEXT,
    base_sha TEXT,
    merge_commit_sha TEXT,
    title TEXT,
    body TEXT,
    author_login TEXT,
    html_url TEXT,
    files_json TEXT NOT NULL,
    file_count INTEGER NOT NULL,
    additions INTEGER NOT NULL,
    deletions INTEGER NOT NULL,
    directories_touched INTEGER NOT NULL,
    patch_text TEXT,
    metrics_json TEXT NOT NULL,
    harvested_at TEXT NOT NULL,
    harvest_run_id INTEGER,
    UNIQUE(repo, pr_number)
);

CREATE INDEX IF NOT EXISTS idx_human_patterns_repo ON human_patterns(repo);
CREATE INDEX IF NOT EXISTS idx_human_patterns_merged_at ON human_patterns(merged_at);
CREATE INDEX IF NOT EXISTS idx_human_patterns_file_count ON human_patterns(file_count);
"""


@dataclass(frozen=True, slots=True)
class HumanPattern:
    repo: str
    pr_number: int
    merged_at: str | None
    base_sha: str | None
    merge_commit_sha: str | None
    title: str | None
    body: str | None
    author_login: str | None
    html_url: str | None
    files: list[str]
    file_count: int
    additions: int
    deletions: int
    directories_touched: int
    patch_text: str | None
    metrics: dict[str, Any]


class PatternStore:
    """Persistent store for human baseline patterns."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> PatternStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def start_run(self, repos: Iterable[str], merged_before: str) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO harvest_runs (started_at, repos_json, merged_before, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                _utc_now(),
                json.dumps(list(repos)),
                merged_before,
                "running",
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def finish_run(self, run_id: int, status: str, notes: str = "") -> None:
        self._conn.execute(
            """
            UPDATE harvest_runs
            SET finished_at = ?, status = ?, notes = ?
            WHERE id = ?
            """,
            (_utc_now(), status, notes, run_id),
        )
        self._conn.commit()

    def upsert_pattern(self, pattern: HumanPattern, harvest_run_id: int | None) -> bool:
        """Insert or update on (repo, pr_number). Returns True if a new row was inserted."""
        existing = self._conn.execute(
            "SELECT id FROM human_patterns WHERE repo = ? AND pr_number = ?",
            (pattern.repo, pattern.pr_number),
        ).fetchone()
        is_insert = existing is None
        self._conn.execute(
            """
            INSERT INTO human_patterns (
                repo, pr_number, merged_at, base_sha, merge_commit_sha,
                title, body, author_login, html_url,
                files_json, file_count, additions, deletions, directories_touched,
                patch_text, metrics_json, harvested_at, harvest_run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(repo, pr_number) DO UPDATE SET
                merged_at = excluded.merged_at,
                base_sha = excluded.base_sha,
                merge_commit_sha = excluded.merge_commit_sha,
                title = excluded.title,
                body = excluded.body,
                author_login = excluded.author_login,
                html_url = excluded.html_url,
                files_json = excluded.files_json,
                file_count = excluded.file_count,
                additions = excluded.additions,
                deletions = excluded.deletions,
                directories_touched = excluded.directories_touched,
                patch_text = excluded.patch_text,
                metrics_json = excluded.metrics_json,
                harvested_at = excluded.harvested_at,
                harvest_run_id = excluded.harvest_run_id
            """,
            (
                pattern.repo,
                pattern.pr_number,
                pattern.merged_at,
                pattern.base_sha,
                pattern.merge_commit_sha,
                pattern.title,
                pattern.body,
                pattern.author_login,
                pattern.html_url,
                json.dumps(pattern.files),
                pattern.file_count,
                pattern.additions,
                pattern.deletions,
                pattern.directories_touched,
                pattern.patch_text,
                json.dumps(pattern.metrics),
                _utc_now(),
                harvest_run_id,
            ),
        )
        self._conn.commit()
        return is_insert

    def count_patterns(self, repo: str | None = None) -> int:
        if repo is None:
            row = self._conn.execute("SELECT COUNT(*) AS n FROM human_patterns").fetchone()
        else:
            row = self._conn.execute(
                "SELECT COUNT(*) AS n FROM human_patterns WHERE repo = ?",
                (repo,),
            ).fetchone()
        return int(row["n"])

    def get_pattern(self, repo: str, pr_number: int) -> HumanPattern | None:
        """Load one human pattern by (repo, pr_number), or None."""
        row = self._conn.execute(
            "SELECT * FROM human_patterns WHERE repo = ? AND pr_number = ?",
            (repo, pr_number),
        ).fetchone()
        if row is None:
            return None
        return _row_to_pattern(row)

    def fetch_eval_candidates(
        self,
        *,
        repo: str = "django/django",
        min_files: int = 1,
        max_files: int = 8,
        merged_before: str = "2021-01-01",
        limit: int | None = None,
    ) -> list[HumanPattern]:
        """Select eval candidates: title+body+patch, file band, merged before cutoff.

        Returns all matching rows ordered by file_count ASC, merged_at ASC.
        Callers may re-rank (e.g. prefer test-touching) and slice to ``limit``.
        """
        rows = self._conn.execute(
            """
            SELECT * FROM human_patterns
            WHERE repo = ?
              AND file_count BETWEEN ? AND ?
              AND merged_at IS NOT NULL
              AND merged_at < ?
              AND title IS NOT NULL AND TRIM(title) != ''
              AND body IS NOT NULL AND TRIM(body) != ''
              AND patch_text IS NOT NULL AND LENGTH(patch_text) > 0
              AND additions > 0
            ORDER BY file_count ASC, merged_at ASC
            """,
            (repo, min_files, max_files, merged_before),
        ).fetchall()
        patterns = [_row_to_pattern(r) for r in rows]
        if limit is not None:
            return patterns[:limit]
        return patterns

    def summary(self) -> dict[str, Any]:
        by_repo = self._conn.execute(
            """
            SELECT repo, COUNT(*) AS n,
                   AVG(file_count) AS avg_files,
                   AVG(additions + deletions) AS avg_churn
            FROM human_patterns
            GROUP BY repo
            ORDER BY n DESC
            """
        ).fetchall()
        return {
            "total": self.count_patterns(),
            "by_repo": [dict(r) for r in by_repo],
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_to_pattern(row: sqlite3.Row) -> HumanPattern:
    return HumanPattern(
        repo=row["repo"],
        pr_number=int(row["pr_number"]),
        merged_at=row["merged_at"],
        base_sha=row["base_sha"],
        merge_commit_sha=row["merge_commit_sha"],
        title=row["title"],
        body=row["body"],
        author_login=row["author_login"],
        html_url=row["html_url"],
        files=json.loads(row["files_json"]),
        file_count=int(row["file_count"]),
        additions=int(row["additions"]),
        deletions=int(row["deletions"]),
        directories_touched=int(row["directories_touched"]),
        patch_text=row["patch_text"],
        metrics=json.loads(row["metrics_json"]),
    )


def pattern_to_dict(pattern: HumanPattern) -> dict[str, Any]:
    data = asdict(pattern)
    return data
