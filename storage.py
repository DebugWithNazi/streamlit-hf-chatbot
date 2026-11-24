import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime

import config


@contextmanager
def _db():
    """Open a connection, commit on success, rollback on error, always close."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # needed for ON DELETE CASCADE
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with _db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id      TEXT PRIMARY KEY,
                title   TEXT NOT NULL,
                updated TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                role    TEXT NOT NULL,
                content TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id);
            """
        )


init_db()


def new_chat_id() -> str:
    return uuid.uuid4().hex[:10]


def save_chat(chat_id: str, messages: list[dict], updated: str | None = None) -> None:
    title = "New chat"
    for m in messages:
        if m["role"] == "user":
            title = m["content"][:40]
            break
    updated = updated or datetime.now().isoformat(timespec="seconds")

    with _db() as conn:
        # insert the chat, or update title/time if it already exists
        conn.execute(
            """
            INSERT INTO chats (id, title, updated) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET title = excluded.title, updated = excluded.updated
            """,
            (chat_id, title, updated),
        )
        # only insert messages that are not in the database yet
        already_saved = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,)
        ).fetchone()[0]
        conn.executemany(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            [(chat_id, m["role"], m["content"]) for m in messages[already_saved:]],
        )


def load_chat(chat_id: str) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id",
            (chat_id,),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def list_chats() -> list[dict]:
    """Return all saved chats, newest first."""
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, title, updated FROM chats ORDER BY updated DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_chat(chat_id: str) -> None:
    with _db() as conn:
        conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))  # messages go too


def import_json_chats() -> int:
    """One-time import of old chats/*.json files. Returns how many were imported."""
    if not config.OLD_CHATS_DIR.exists():
        return 0
    with _db() as conn:
        existing = {r["id"] for r in conn.execute("SELECT id FROM chats")}
    count = 0
    for p in config.OLD_CHATS_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d["id"] in existing:
                continue
            save_chat(d["id"], d.get("messages", []), d.get("updated"))
            count += 1
        except (json.JSONDecodeError, KeyError):
            continue
    return count