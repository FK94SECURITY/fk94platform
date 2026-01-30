"""
FK94 Security Platform - Job Store (SQLite)
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_connection(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path, check_same_thread=False)


def init_db(db_path: str) -> None:
    with _get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                result TEXT,
                error TEXT,
                run_at TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            )
            """
        )
        conn.commit()


def create_job(
    db_path: str,
    job_type: str,
    payload: dict,
    run_at: Optional[datetime] = None
) -> dict:
    job_id = str(uuid.uuid4())
    run_at_value = run_at.isoformat() if run_at else None

    with _get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                id, job_type, status, payload, result, error,
                run_at, created_at, started_at, finished_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                job_type,
                "queued",
                json.dumps(payload),
                None,
                None,
                run_at_value,
                _utc_now(),
                None,
                None,
            ),
        )
        conn.commit()

    return {
        "id": job_id,
        "status": "queued",
        "job_type": job_type,
        "run_at": run_at_value,
    }


def get_job(db_path: str, job_id: str) -> Optional[dict]:
    with _get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id, job_type, status, payload, result, error, run_at, created_at, started_at, finished_at FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "job_type": row[1],
        "status": row[2],
        "payload": json.loads(row[3]),
        "result": json.loads(row[4]) if row[4] else None,
        "error": row[5],
        "run_at": row[6],
        "created_at": row[7],
        "started_at": row[8],
        "finished_at": row[9],
    }


def fetch_due_jobs(db_path: str, limit: int = 5) -> list[dict]:
    now = _utc_now()
    with _get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, job_type, status, payload, run_at
            FROM jobs
            WHERE status = 'queued'
              AND (run_at IS NULL OR run_at <= ?)
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (now, limit),
        ).fetchall()

    jobs = []
    for row in rows:
        jobs.append(
            {
                "id": row[0],
                "job_type": row[1],
                "status": row[2],
                "payload": json.loads(row[3]),
                "run_at": row[4],
            }
        )
    return jobs


def update_job(
    db_path: str,
    job_id: str,
    *,
    status: Optional[str] = None,
    result: Optional[dict] = None,
    error: Optional[str] = None,
    started_at: Optional[str] = None,
    finished_at: Optional[str] = None
) -> None:
    fields = []
    values = []

    if status is not None:
        fields.append("status = ?")
        values.append(status)
    if result is not None:
        fields.append("result = ?")
        values.append(json.dumps(result))
    if error is not None:
        fields.append("error = ?")
        values.append(error)
    if started_at is not None:
        fields.append("started_at = ?")
        values.append(started_at)
    if finished_at is not None:
        fields.append("finished_at = ?")
        values.append(finished_at)

    if not fields:
        return

    values.append(job_id)
    with _get_connection(db_path) as conn:
        conn.execute(
            f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?",
            tuple(values),
        )
        conn.commit()
