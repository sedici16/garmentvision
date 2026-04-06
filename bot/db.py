"""SQLite analytics database."""

from __future__ import annotations

import os
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "garment_vision.db"


def _connect():
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = _connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            search_count INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            garment_type TEXT,
            garment_category TEXT,
            primary_material TEXT,
            co2_kg REAL,
            water_liters INTEGER,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE INDEX IF NOT EXISTS idx_scans_user ON scans(user_id);
        CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(timestamp);
    """)
    conn.close()
    logger.info("Database initialized at %s", DB_PATH)


def log_scan(user_id: int, username: str | None, first_name: str | None,
             garment_type: str, garment_category: str, primary_material: str,
             co2_kg: float = None, water_liters: int = None):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn = _connect()
    try:
        conn.execute("""
            INSERT INTO users (user_id, username, first_name, first_seen, last_seen, search_count)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_seen = excluded.last_seen,
                search_count = search_count + 1
        """, (user_id, username, first_name, now, now))

        conn.execute("""
            INSERT INTO scans (user_id, garment_type, garment_category, primary_material, co2_kg, water_liters, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, garment_type, garment_category, primary_material, co2_kg, water_liters, now))

        conn.commit()
    except Exception as e:
        logger.error("Failed to log scan: %s", e)
        conn.rollback()
    finally:
        conn.close()


def get_stats() -> dict:
    conn = _connect()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_scans = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    total_co2 = conn.execute("SELECT COALESCE(SUM(co2_kg), 0) FROM scans").fetchone()[0]
    scans_today = conn.execute("SELECT COUNT(*) FROM scans WHERE timestamp LIKE ?", (f"{today}%",)).fetchone()[0]
    conn.close()
    return {"total_users": total_users, "total_scans": total_scans, "total_co2_kg": round(total_co2, 1), "scans_today": scans_today}


def get_recent_scans(limit: int = 50) -> list[dict]:
    conn = _connect()
    rows = conn.execute("""
        SELECT s.garment_type, s.garment_category, s.primary_material, s.co2_kg, s.water_liters, s.timestamp,
               u.username, u.first_name
        FROM scans s JOIN users u ON s.user_id = u.user_id
        ORDER BY s.timestamp DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_materials(limit: int = 10) -> list[dict]:
    conn = _connect()
    rows = conn.execute("""
        SELECT primary_material, COUNT(*) as count, ROUND(AVG(co2_kg), 1) as avg_co2
        FROM scans WHERE primary_material IS NOT NULL
        GROUP BY primary_material ORDER BY count DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_users() -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM users ORDER BY search_count DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user(user_id: int) -> dict | None:
    conn = _connect()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_scans(user_id: int, limit: int = 100) -> list[dict]:
    conn = _connect()
    rows = conn.execute("""
        SELECT garment_type, garment_category, primary_material, co2_kg, water_liters, timestamp
        FROM scans WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
