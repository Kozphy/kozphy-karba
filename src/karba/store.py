from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  agent_id TEXT NOT NULL,
  trial_index INTEGER NOT NULL,
  outcome TEXT NOT NULL,
  payload TEXT NOT NULL,
  UNIQUE(run_id, case_id, agent_id, trial_index)
);
CREATE TABLE IF NOT EXISTS metrics (
  run_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    return conn


def upsert_attempt(conn: sqlite3.Connection, record: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO attempts(run_id, case_id, agent_id, trial_index, outcome, payload)
        VALUES(?,?,?,?,?,?)
        ON CONFLICT(run_id, case_id, agent_id, trial_index)
        DO UPDATE SET outcome=excluded.outcome, payload=excluded.payload
        """,
        (
            record["run_id"],
            record["case_id"],
            record["agent_id"],
            record["trial_index"],
            record["outcome"],
            json.dumps(record),
        ),
    )
    conn.commit()


def save_metrics(conn: sqlite3.Connection, run_id: str, metrics: dict[str, Any]) -> None:
    conn.execute(
        "INSERT INTO metrics(run_id, payload) VALUES(?,?) ON CONFLICT(run_id) DO UPDATE SET payload=excluded.payload",
        (run_id, json.dumps(metrics)),
    )
    conn.commit()


def load_metrics(conn: sqlite3.Connection, run_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT payload FROM metrics WHERE run_id=?", (run_id,)).fetchone()
    return json.loads(row[0]) if row else None


def list_attempts(conn: sqlite3.Connection, run_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT payload FROM attempts WHERE run_id=? ORDER BY case_id, agent_id, trial_index",
        (run_id,),
    ).fetchall()
    return [json.loads(r[0]) for r in rows]