"""
Shadowprint S3 Integrity Engine: SQLite Baseline Storage.
Owner: Gaurang Udgirkar [G]

Persists approved baseline Pin records, Snapshots, and Behavior profiles
into shadowprint.db.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from shadowprint.models import Pin, Snapshot, BehaviorTuple, ToolDefinition

DEFAULT_DB_PATH = Path("shadowprint.db")


class PinDatabase:
    """SQLite database manager for approved server pins and security snapshots."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes tables and indexes."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pins (
                    server_name TEXT PRIMARY KEY,
                    pinned_at REAL NOT NULL,
                    definition_hash TEXT NOT NULL,
                    artifact_hash TEXT NOT NULL,
                    behavior_hash TEXT,
                    approved_by TEXT NOT NULL,
                    tools_count INTEGER NOT NULL,
                    snapshot_json TEXT NOT NULL,
                    behavior_json TEXT
                )
            """)
            conn.commit()

    def save_pin(
        self,
        pin: Pin,
        snapshot: Snapshot,
        behaviors: Optional[Dict[str, BehaviorTuple]] = None,
    ) -> None:
        """
        Saves or updates an approved baseline pin record.
        """
        snapshot_json = snapshot.model_dump_json()
        behavior_json = json.dumps(
            {name: b.model_dump() for name, b in (behaviors or {}).items()}
        )

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO pins (
                    server_name, pinned_at, definition_hash, artifact_hash,
                    behavior_hash, approved_by, tools_count, snapshot_json, behavior_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pin.server_name,
                    pin.pinned_at,
                    pin.definition_hash,
                    pin.artifact_hash,
                    pin.behavior_hash,
                    pin.approved_by,
                    pin.tools_count,
                    snapshot_json,
                    behavior_json,
                ),
            )
            conn.commit()

    def get_pin(self, server_name: str) -> Optional[Pin]:
        """Retrieves a baseline Pin by server name."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM pins WHERE server_name = ?", (server_name,)
            ).fetchone()

            if not row:
                return None

            return Pin(
                server_name=row["server_name"],
                pinned_at=row["pinned_at"],
                definition_hash=row["definition_hash"],
                artifact_hash=row["artifact_hash"],
                behavior_hash=row["behavior_hash"],
                approved_by=row["approved_by"],
                tools_count=row["tools_count"],
            )

    def get_pin_snapshot(self, server_name: str) -> Optional[Snapshot]:
        """Retrieves the full Snapshot associated with a pinned server."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT snapshot_json FROM pins WHERE server_name = ?", (server_name,)
            ).fetchone()

            if not row or not row["snapshot_json"]:
                return None

            data = json.loads(row["snapshot_json"])
            return Snapshot(**data)

    def get_pin_behaviors(self, server_name: str) -> Optional[Dict[str, BehaviorTuple]]:
        """Retrieves the BehaviorTuple map associated with a pinned server."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT behavior_json FROM pins WHERE server_name = ?", (server_name,)
            ).fetchone()

            if not row or not row["behavior_json"]:
                return None

            data = json.loads(row["behavior_json"])
            return {name: BehaviorTuple(**b_data) for name, b_data in data.items()}

    def list_pins(self) -> List[Pin]:
        """Lists all approved server pins."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM pins ORDER BY server_name ASC").fetchall()
            return [
                Pin(
                    server_name=r["server_name"],
                    pinned_at=r["pinned_at"],
                    definition_hash=r["definition_hash"],
                    artifact_hash=r["artifact_hash"],
                    behavior_hash=r["behavior_hash"],
                    approved_by=r["approved_by"],
                    tools_count=r["tools_count"],
                )
                for r in rows
            ]

    def delete_pin(self, server_name: str) -> bool:
        """Deletes a baseline pin record."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM pins WHERE server_name = ?", (server_name,))
            conn.commit()
            return cursor.rowcount > 0
