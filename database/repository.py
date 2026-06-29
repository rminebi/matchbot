from .db import get_connection
from datetime import datetime


# ─── Profile CRUD ────────────────────────────────────────────────────────────

def upsert_user(user_id, username, name, age, gender, city, bio, photo_id, looking_for, min_age=18, max_age=60):
    conn = get_connection()
    conn.execute("""
        INSERT INTO users (user_id, username, name, age, gender, city, bio, photo_id, looking_for, min_age, max_age, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username, name=excluded.name, age=excluded.age,
            gender=excluded.gender, city=excluded.city, bio=excluded.bio,
            photo_id=excluded.photo_id, looking_for=excluded.looking_for,
            min_age=excluded.min_age, max_age=excluded.max_age,
            updated_at=datetime('now')
    """, (user_id, username, name, age, gender, city, bio, photo_id, looking_for, min_age, max_age))
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_field(user_id, field, value):
    allowed = {"name","age","gender","city","bio","photo_id","looking_for","min_age","max_age","is_active"}
    if field not in allowed:
        raise ValueError(f"Field '{field}' not allowed.")
    conn = get_connection()
    conn.execute(f"UPDATE users SET {field}=?, updated_at=datetime('now') WHERE user_id=?", (value, user_id))
    conn.commit()
    conn.close()


def delete_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


# ─── Discovery ───────────────────────────────────────────────────────────────

def get_candidates(user_id, limit=10):
    """Return users that match the current user's preferences and haven't been liked/blocked."""
    me = get_user(user_id)
    if not me:
        return []

    gender_filter = f"= '{me['looking_for']}'" if me['looking_for'] != 'any' else "IN ('male','female','other')"

    conn = get_connection()
    rows = conn.execute(f"""
        SELECT * FROM users
        WHERE user_id != ?
          AND is_active = 1
          AND gender {gender_filter}
          AND age BETWEEN ? AND ?
          AND user_id NOT IN (
              SELECT to_user   FROM likes  WHERE from_user = ?
              UNION
              SELECT blocker   FROM blocks WHERE blocked  = ?
              UNION
              SELECT blocked   FROM blocks WHERE blocker  = ?
          )
        ORDER BY RANDOM()
        LIMIT ?
    """, (user_id, me['min_age'], me['max_age'], user_id, user_id, user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Likes & Matches ─────────────────────────────────────────────────────────

def add_like(from_user, to_user):
    """Returns True if this like creates a mutual match."""
    conn = get_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO likes (from_user, to_user) VALUES (?,?)", (from_user, to_user))
        conn.commit()
    except Exception:
        conn.close()
        return False

    # Check mutual
    mutual = conn.execute(
        "SELECT 1 FROM likes WHERE from_user=? AND to_user=?", (to_user, from_user)
    ).fetchone()

    if mutual:
        u1, u2 = sorted([from_user, to_user])
        conn.execute("INSERT OR IGNORE INTO matches (user1, user2) VALUES (?,?)", (u1, u2))
        conn.commit()

    conn.close()
    return bool(mutual)


def get_matches(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.* FROM users u
        JOIN matches m ON (m.user1=u.user_id OR m.user2=u.user_id)
        WHERE (m.user1=? OR m.user2=?) AND u.user_id != ?
    """, (user_id, user_id, user_id)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remove_match(user1, user2):
    u1, u2 = sorted([user1, user2])
    conn = get_connection()
    conn.execute("DELETE FROM matches WHERE user1=? AND user2=?", (u1, u2))
    conn.commit()
    conn.close()


# ─── Block ───────────────────────────────────────────────────────────────────

def block_user(blocker, blocked):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO blocks (blocker, blocked) VALUES (?,?)", (blocker, blocked))
    # Remove any existing match
    u1, u2 = sorted([blocker, blocked])
    conn.execute("DELETE FROM matches WHERE user1=? AND user2=?", (u1, u2))
    conn.commit()
    conn.close()
