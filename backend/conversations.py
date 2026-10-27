"""Stockage persistant des conversations et des comptes utilisateurs (SQLite, bibliothèque standard).

Chaque conversation appartient à un `owner` (identifiant d'appareil ou identifiant de compte connecté).
Les utilisateurs peuvent créer un compte ou se connecter via Google, Apple, Microsoft ou Email/Téléphone
afin de synchroniser et retrouver leurs discussions juridiques."""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sqlite3
import threading
import time
import uuid

OWNER_RE = re.compile(r"^[A-Za-z0-9_@.-]{8,64}$")
SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY, owner TEXT NOT NULL, title TEXT NOT NULL,
  created_at REAL NOT NULL, updated_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS ix_conv_owner ON conversations(owner, updated_at DESC);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK(role IN ('u','a')), text TEXT NOT NULL,
  sources TEXT NOT NULL DEFAULT '[]', notice TEXT, mode TEXT, created_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS ix_msg_conv ON messages(conversation_id, id);
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  provider TEXT NOT NULL,
  ville TEXT NOT NULL DEFAULT 'Lomé',
  password_hash TEXT,
  created_at REAL NOT NULL
);
"""


def make_title(text: str) -> str:
    t = " ".join(text.split())
    return (t[:60].rstrip() + "…") if len(t) > 60 else (t or "Nouvelle conversation")


def _hash_pw(pw: str) -> str:
    return hashlib.sha256(("novissi-salt:" + (pw or "")).encode("utf-8")).hexdigest()


class Store:
    def __init__(self, path: str | pathlib.Path):
        if str(path) != ":memory:":
            pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys=ON")
        self._lock = threading.Lock()
        with self._lock:
            self._db.executescript(SCHEMA)

    def _own(self, owner: str, cid: str) -> sqlite3.Row | None:
        return self._db.execute("SELECT * FROM conversations WHERE id=? AND owner=?", (cid, owner)).fetchone()

    def create(self, owner: str, title: str = "Nouvelle conversation") -> dict:
        cid, now = uuid.uuid4().hex, time.time()
        with self._lock:
            self._db.execute("INSERT INTO conversations VALUES (?,?,?,?,?)", (cid, owner, title[:120], now, now))
            self._db.commit()
        return {"id": cid, "title": title[:120], "created_at": now, "updated_at": now}

    def list(self, owner: str, q: str = "") -> list[dict]:
        with self._lock:
            if q.strip():
                like = f"%{q.strip()}%"
                rows = self._db.execute(
                    "SELECT DISTINCT c.id,c.title,c.created_at,c.updated_at FROM conversations c "
                    "LEFT JOIN messages m ON m.conversation_id=c.id WHERE c.owner=? AND (c.title LIKE ? OR m.text LIKE ?) "
                    "ORDER BY c.updated_at DESC LIMIT 200", (owner, like, like)).fetchall()
            else:
                rows = self._db.execute(
                    "SELECT id,title,created_at,updated_at FROM conversations WHERE owner=? "
                    "ORDER BY updated_at DESC LIMIT 200", (owner,)).fetchall()
        return [dict(r) for r in rows]

    def messages(self, owner: str, cid: str) -> list[dict] | None:
        with self._lock:
            if not self._own(owner, cid):
                return None
            rows = self._db.execute("SELECT * FROM messages WHERE conversation_id=? ORDER BY id", (cid,)).fetchall()
        return [{"id": r["id"], "role": r["role"], "text": r["text"], "sources": json.loads(r["sources"]),
                 "notice": r["notice"], "mode": r["mode"], "created_at": r["created_at"]} for r in rows]

    def add_message(self, owner: str, cid: str, role: str, text: str, sources: list | None = None,
                    notice: str | None = None, mode: str | None = None) -> bool:
        now = time.time()
        with self._lock:
            conv = self._own(owner, cid)
            if not conv:
                return False
            self._db.execute(
                "INSERT INTO messages(conversation_id,role,text,sources,notice,mode,created_at) VALUES (?,?,?,?,?,?,?)",
                (cid, role, text, json.dumps(sources or [], ensure_ascii=False), notice, mode, now))
            if role == "u" and conv["title"] == "Nouvelle conversation":
                self._db.execute("UPDATE conversations SET title=? WHERE id=?", (make_title(text), cid))
            self._db.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, cid))
            self._db.commit()
        return True

    def rename(self, owner: str, cid: str, title: str) -> bool:
        with self._lock:
            cur = self._db.execute("UPDATE conversations SET title=?, updated_at=? WHERE id=? AND owner=?",
                                   (make_title(title), time.time(), cid, owner))
            self._db.commit()
            return cur.rowcount > 0

    def delete(self, owner: str, cid: str) -> bool:
        with self._lock:
            cur = self._db.execute("DELETE FROM conversations WHERE id=? AND owner=?", (cid, owner))
            self._db.commit()
            return cur.rowcount > 0

    # ---------- Gestion des comptes utilisateurs (Google, Apple, Microsoft, Email) ----------
    def upsert_oauth_user(self, provider: str, email: str, name: str, ville: str = "Lomé", prev_owner: str = "") -> dict:
        email = email.strip().lower()
        now = time.time()
        with self._lock:
            row = self._db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            if row:
                uid = row["id"]
                self._db.execute("UPDATE users SET name=?, provider=?, ville=? WHERE id=?", (name, provider, ville, uid))
            else:
                uid = "usr_" + hashlib.sha256(email.encode("utf-8")).hexdigest()[:20]
                self._db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", (uid, email, name, provider, ville, None, now))
            if prev_owner and prev_owner != uid and OWNER_RE.match(prev_owner):
                self._db.execute("UPDATE conversations SET owner=? WHERE owner=?", (uid, prev_owner))
            self._db.commit()
        return {"id": uid, "email": email, "name": name, "provider": provider, "ville": ville}

    def register_email_user(self, email: str, name: str, password: str, ville: str = "Lomé", prev_owner: str = "") -> dict:
        email = email.strip().lower()
        now = time.time()
        uid = "usr_" + hashlib.sha256(email.encode("utf-8")).hexdigest()[:20]
        pwh = _hash_pw(password)
        with self._lock:
            row = self._db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            if row and row["password_hash"] and row["password_hash"] != pwh:
                raise ValueError("Cet email est déjà enregistré avec un autre mot de passe.")
            if row:
                uid = row["id"]
                self._db.execute("UPDATE users SET name=?, ville=?, password_hash=? WHERE id=?", (name, ville, pwh, uid))
            else:
                self._db.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", (uid, email, name, "email", ville, pwh, now))
            if prev_owner and prev_owner != uid and OWNER_RE.match(prev_owner):
                self._db.execute("UPDATE conversations SET owner=? WHERE owner=?", (uid, prev_owner))
            self._db.commit()
        return {"id": uid, "email": email, "name": name, "provider": "email", "ville": ville}
