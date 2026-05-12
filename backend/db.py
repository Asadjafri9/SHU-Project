import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "standupbot.db"


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            avatar_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            deadline DATE,
            standup_closes_at TIME DEFAULT '21:00',
            leader_id INTEGER NOT NULL REFERENCES users(id),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS project_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL REFERENCES projects(id),
            user_id INTEGER REFERENCES users(id),
            email TEXT,
            role TEXT NOT NULL DEFAULT 'Member',
            status TEXT NOT NULL CHECK(status IN ('invited','active','declined','removed')) DEFAULT 'invited',
            invite_token TEXT UNIQUE,
            invite_type TEXT CHECK(invite_type IN ('email','link')),
            joined_at DATETIME,
            is_first_standup BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS standups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL REFERENCES projects(id),
            member_id INTEGER NOT NULL REFERENCES project_members(id),
            date DATE NOT NULL,
            did TEXT NOT NULL,
            will_do TEXT NOT NULL,
            blocker TEXT,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(project_id, member_id, date)
        );

        CREATE TABLE IF NOT EXISTS briefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL REFERENCES projects(id),
            date DATE NOT NULL,
            content TEXT NOT NULL,
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            submissions_count INTEGER NOT NULL,
            total_active_members INTEGER NOT NULL
        );
    """
    )
    conn.commit()
    conn.close()


init_db()