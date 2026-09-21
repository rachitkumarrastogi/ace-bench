"""SQLite store for agent eval runs (ACE-Bench step 3).

Multiple runs per (instance_id, model_name) are allowed — distinguished by
``started_at`` / ``id``. Schema lives in code; DB path is gitignored.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    agent_name TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    passed_tests INTEGER,
    ace_score REAL,
    file_drift INTEGER,
    churn_ratio REAL,
    human_files TEXT,
    agent_files TEXT,
    notes TEXT,
    error TEXT,
    patch_path TEXT,
    patch_hash TEXT
);

CREATE INDEX IF NOT EXISTS idx_eval_runs_instance
    ON eval_runs(instance_id);
CREATE INDEX IF NOT EXISTS idx_eval_runs_instance_model
    ON eval_runs(instance_id, model_name);
CREATE INDEX IF NOT EXISTS idx_eval_runs_started
    ON eval_runs(started_at);
"""


@dataclass(frozen=True, slots=True)
class EvalRunRecord:
    """One stored agent evaluation run."""

    id: int | None
    instance_id: str
    model_name: str
    agent_name: str | None
    started_at: str
    finished_at: str | None
    passed_tests: bool | None
    ace_score: float | None
    file_drift: int | None
    churn_ratio: float | None
    human_files: list[str]
    agent_files: list[str]
    notes: str | None
    error: str | None
    patch_path: str | None
    patch_hash: str | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_eval_runs_db_path() -> Path:
    """Prefer Mac mirror, then repo-local gitignored path."""
    home_data = Path.home() / "ace-bench-data" / "eval_runs.sqlite"
    if home_data.parent.is_dir() or not (Path.cwd() / "data").is_dir():
        return home_data
    return Path("data") / "eval_runs.sqlite"


def patch_sha256(patch_text: str) -> str:
    return hashlib.sha256(patch_text.encode("utf-8", errors="replace")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _passed_to_sql(value: bool | None) -> int | None:
    if value is None:
        return None
    return 1 if value else 0


def _passed_from_sql(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(value)


class EvalRunStore:
    """Persistent store for model/agent eval runs."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> EvalRunStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def start_run(
        self,
        *,
        instance_id: str,
        model_name: str,
        agent_name: str | None = None,
    ) -> int:
        model = (model_name or "").strip()
        if not model:
            raise ValueError("model_name is required")
        cur = self._conn.execute(
            """
            INSERT INTO eval_runs (
                instance_id, model_name, agent_name, started_at
            ) VALUES (?, ?, ?, ?)
            """,
            (instance_id, model, agent_name, _utc_now()),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def finish_run(
        self,
        run_id: int,
        *,
        passed_tests: bool | None = None,
        ace_score: float | None = None,
        file_drift: int | None = None,
        churn_ratio: float | None = None,
        human_files: list[str] | None = None,
        agent_files: list[str] | None = None,
        notes: str | None = None,
        error: str | None = None,
        patch_path: str | None = None,
        patch_hash: str | None = None,
    ) -> None:
        self._conn.execute(
            """
            UPDATE eval_runs SET
                finished_at = ?,
                passed_tests = ?,
                ace_score = ?,
                file_drift = ?,
                churn_ratio = ?,
                human_files = ?,
                agent_files = ?,
                notes = ?,
                error = ?,
                patch_path = ?,
                patch_hash = ?
            WHERE id = ?
            """,
            (
                _utc_now(),
                _passed_to_sql(passed_tests),
                ace_score,
                file_drift,
                churn_ratio,
                json.dumps(human_files or []),
                json.dumps(agent_files or []),
                notes,
                error,
                patch_path,
                patch_hash,
                run_id,
            ),
        )
        self._conn.commit()

    def get_run(self, run_id: int) -> EvalRunRecord | None:
        row = self._conn.execute(
            "SELECT * FROM eval_runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return _row_to_record(row)

    def list_runs(
        self,
        *,
        instance_id: str | None = None,
        model_name: str | None = None,
        limit: int = 50,
    ) -> list[EvalRunRecord]:
        clauses: list[str] = []
        params: list[Any] = []
        if instance_id is not None:
            clauses.append("instance_id = ?")
            params.append(instance_id)
        if model_name is not None:
            clauses.append("model_name = ?")
            params.append(model_name)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._conn.execute(
            f"""
            SELECT * FROM eval_runs
            {where}
            ORDER BY id DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()
        return [_row_to_record(r) for r in rows]

    def count_runs(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS n FROM eval_runs").fetchone()
        return int(row["n"])


def _row_to_record(row: sqlite3.Row) -> EvalRunRecord:
    human_raw = row["human_files"]
    agent_raw = row["agent_files"]
    human_files = json.loads(human_raw) if human_raw else []
    agent_files = json.loads(agent_raw) if agent_raw else []
    return EvalRunRecord(
        id=int(row["id"]),
        instance_id=row["instance_id"],
        model_name=row["model_name"],
        agent_name=row["agent_name"],
        started_at=row["started_at"],
        finished_at=row["finished_at"],
        passed_tests=_passed_from_sql(row["passed_tests"]),
        ace_score=row["ace_score"],
        file_drift=row["file_drift"],
        churn_ratio=row["churn_ratio"],
        human_files=list(human_files),
        agent_files=list(agent_files),
        notes=row["notes"],
        error=row["error"],
        patch_path=row["patch_path"],
        patch_hash=row["patch_hash"],
    )
