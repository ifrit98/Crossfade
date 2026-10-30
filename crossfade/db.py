"""SQLite index over the file store. Three tables, no ORM, no semantics."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    id TEXT PRIMARY KEY, kind TEXT, byte_hash TEXT, manifest_hash TEXT,
    validation_state TEXT, path TEXT
);
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY, task_id TEXT, op_id TEXT, status TEXT, path TEXT
);
CREATE TABLE IF NOT EXISTS reports (
    report_id TEXT PRIMARY KEY, experiment_id TEXT, validity TEXT, path TEXT
);
"""


def connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con
