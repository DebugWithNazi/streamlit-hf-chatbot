import json
import uuid
from datetime import datetime

import config

config.CHATS_DIR.mkdir(exist_ok=True)


def new_chat_id() -> str:
    return uuid.uuid4().hex[:10]


def _path(chat_id: str):
    return config.CHATS_DIR / f"{chat_id}.json"


def save_chat(chat_id: str, messages: list[dict]) -> None:
    title = "New chat"
    for m in messages:
        if m["role"] == "user":
            title = m["content"][:40]
            break
    data = {
        "id": chat_id,
        "title": title,
        "updated": datetime.now().isoformat(timespec="seconds"),
        "messages": messages,
    }
    _path(chat_id).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_chat(chat_id: str) -> list[dict]:
    p = _path(chat_id)
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8")).get("messages", [])


def list_chats() -> list[dict]:
    """Return all saved chats, newest first."""
    chats = []
    for p in config.CHATS_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            chats.append({"id": d["id"], "title": d["title"], "updated": d["updated"]})
        except (json.JSONDecodeError, KeyError):
            continue
    return sorted(chats, key=lambda c: c["updated"], reverse=True)


def delete_chat(chat_id: str) -> None:
    _path(chat_id).unlink(missing_ok=True)