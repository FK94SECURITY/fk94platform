"""
FK94 Security Platform - Event and Lead Store (SQLite)
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
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                source TEXT,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                metadata TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type_created ON events(event_type, created_at DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_email_created ON leads(email, created_at DESC)")
        conn.commit()


def track_event(
    db_path: str,
    event_type: str,
    payload: dict,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    source: Optional[str] = None,
) -> dict:
    event_id = str(uuid.uuid4())
    created_at = _utc_now()
    with _get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO events (id, event_type, user_id, session_id, source, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                event_type,
                user_id,
                session_id,
                source,
                json.dumps(payload or {}),
                created_at,
            ),
        )
        conn.commit()
    return {"id": event_id, "event_type": event_type, "created_at": created_at}


def create_lead(
    db_path: str,
    *,
    name: str,
    email: str,
    subject: str,
    message: str,
    source: str = "website_contact",
    metadata: Optional[dict] = None,
) -> dict:
    lead_id = str(uuid.uuid4())
    created_at = _utc_now()
    with _get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO leads (id, name, email, subject, message, source, status, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lead_id,
                name,
                email.lower().strip(),
                subject,
                message,
                source,
                "new",
                json.dumps(metadata or {}),
                created_at,
            ),
        )
        conn.commit()
    return {"id": lead_id, "created_at": created_at}


def count_events(db_path: str, event_type: Optional[str] = None) -> int:
    with _get_connection(db_path) as conn:
        if event_type:
            row = conn.execute("SELECT COUNT(*) FROM events WHERE event_type = ?", (event_type,)).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) FROM events").fetchone()
    return int(row[0]) if row else 0
