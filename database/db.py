import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "matchbot.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            name        TEXT NOT NULL,
            age         INTEGER NOT NULL,
            gender      TEXT NOT NULL CHECK(gender IN ('male','female','other')),
            city        TEXT NOT NULL,
            bio         TEXT,
            photo_id    TEXT,
            looking_for TEXT NOT NULL CHECK(looking_for IN ('male','female','any')),
            min_age     INTEGER DEFAULT 18,
            max_age     INTEGER DEFAULT 60,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS likes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user   INTEGER NOT NULL REFERENCES users(user_id),
            to_user     INTEGER NOT NULL REFERENCES users(user_id),
            created_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(from_user, to_user)
        );

        CREATE TABLE IF NOT EXISTS matches (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user1       INTEGER NOT NULL REFERENCES users(user_id),
            user2       INTEGER NOT NULL REFERENCES users(user_id),
            created_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(user1, user2)
        );

        CREATE TABLE IF NOT EXISTS blocks (
            blocker     INTEGER NOT NULL REFERENCES users(user_id),
            blocked     INTEGER NOT NULL REFERENCES users(user_id),
            PRIMARY KEY(blocker, blocked)
        );

        CREATE INDEX IF NOT EXISTS idx_users_city    ON users(city);
        CREATE INDEX IF NOT EXISTS idx_users_age     ON users(age);
        CREATE INDEX IF NOT EXISTS idx_likes_from    ON likes(from_user);
        CREATE INDEX IF NOT EXISTS idx_likes_to      ON likes(to_user);
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized.")
