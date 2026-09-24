from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLog:
    """Append-only SQLite audit trail for recommendations and external actions."""

    def __init__(self, path: str = "data/audit.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )"""
            )
            connection.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def record(self, event_type: str, correlation_id: str, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO events(created_at,event_type,correlation_id,payload_json) VALUES(?,?,?,?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    event_type,
                    correlation_id,
                    json.dumps(payload, default=str, sort_keys=True),
                ),
            )
            connection.commit()

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT created_at,event_type,correlation_id,payload_json FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"created_at": row[0], "event_type": row[1], "correlation_id": row[2], "payload": json.loads(row[3])}
            for row in rows
        ]
