"""Registre documentaire commun (SQLite) : sources, ressources découvertes, versions, articles, relations,
exécutions de collecte et erreurs. C'est la source de vérité du corpus juridique.

Principes :
- une *ressource* = une URL découverte ; une *version* = un contenu précis (empreinte SHA-256) de cette ressource ;
  un même PDF peut contenir plusieurs textes : les *articles* sont rattachés à la version, pas à une loi supposée ;
- une version n'est jamais supprimée : si le contenu change, la nouvelle version devient « courante », l'ancienne reste ;
- une erreur temporaire met la ressource en « retry », jamais en suppression ;
- aucune information de statut juridique n'est déduite : « en vigueur / abrogé » n'existe pas ici (champ vérifié = 0 par défaut).

SQLite a été préféré à PostgreSQL : l'application tourne en local, sans Docker, et la recherche plein texte FTS5 suffit
pour ce volume. Le schéma n'utilise que du SQL standard (hors FTS5) pour rester portable.
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA_VERSION = 2
RESOURCE_STATUSES = ("discovered", "archived", "retry", "review", "unreachable", "non_document", "inspected", "quarantine")
SCOPES = ("national", "regional", "international", "demo")

MIGRATIONS: dict[int, str] = {
    1: """
    CREATE TABLE sources (
        id INTEGER PRIMARY KEY, key TEXT NOT NULL UNIQUE, name TEXT NOT NULL, base_url TEXT,
        scope TEXT NOT NULL DEFAULT 'national' CHECK (scope IN ('national','regional','international','demo')),
        created_at TEXT NOT NULL);
    CREATE TABLE resources (
        id INTEGER PRIMARY KEY,
        source_id INTEGER NOT NULL REFERENCES sources(id),
        url TEXT NOT NULL UNIQUE, discovered_from TEXT,
        kind TEXT NOT NULL DEFAULT 'document' CHECK (kind IN ('document','listing')),
        title TEXT, reference TEXT, text_type TEXT, doc_date TEXT,
        status TEXT NOT NULL DEFAULT 'discovered' CHECK (status IN
            ('discovered','archived','retry','review','unreachable','non_document','inspected','quarantine')),
        http_status INTEGER, etag TEXT, last_modified TEXT, content_type TEXT, size INTEGER,
        attempts INTEGER NOT NULL DEFAULT 0, next_retry TEXT, error TEXT,
        discovered_at TEXT NOT NULL, last_checked TEXT, current_version_id INTEGER);
    CREATE INDEX idx_resources_source_status ON resources(source_id, status);
    CREATE TABLE versions (
        id INTEGER PRIMARY KEY,
        resource_id INTEGER NOT NULL REFERENCES resources(id),
        sha256 TEXT NOT NULL, file_path TEXT, size INTEGER, content_type TEXT,
        pages INTEGER, chars INTEGER,
        extraction_status TEXT NOT NULL CHECK (extraction_status IN ('ok','empty','failed')),
        collected_at TEXT NOT NULL, is_current INTEGER NOT NULL DEFAULT 0,
        UNIQUE (resource_id, sha256));
    CREATE INDEX idx_versions_current ON versions(resource_id, is_current);
    CREATE TABLE articles (
        id INTEGER PRIMARY KEY,
        version_id INTEGER NOT NULL REFERENCES versions(id),
        label TEXT NOT NULL, content TEXT NOT NULL, page INTEGER);
    CREATE INDEX idx_articles_version ON articles(version_id);
    CREATE VIRTUAL TABLE articles_fts USING fts5(
        label, content, content='articles', content_rowid='id', tokenize='unicode61 remove_diacritics 2');
    CREATE TABLE relations (
        id INTEGER PRIMARY KEY,
        from_resource_id INTEGER NOT NULL REFERENCES resources(id),
        to_resource_id INTEGER NOT NULL REFERENCES resources(id),
        relation TEXT NOT NULL CHECK (relation IN ('modifie','abroge','remplace','rectifie','complete','renvoie_a')),
        origin TEXT, verified INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
    CREATE TABLE runs (
        id INTEGER PRIMARY KEY, source_key TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT,
        status TEXT NOT NULL DEFAULT 'running', stats_json TEXT);
    CREATE TABLE errors (
        id INTEGER PRIMARY KEY, run_id INTEGER REFERENCES runs(id), resource_id INTEGER REFERENCES resources(id),
        url TEXT, kind TEXT NOT NULL, message TEXT, at TEXT NOT NULL);
    CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
    """,
    2: """ALTER TABLE sources ADD COLUMN kind TEXT NOT NULL DEFAULT 'loi';""",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fts_query(q: str, operator: str = "AND") -> str:
    tokens = re.findall(r"\w+", q or "", re.UNICODE)[:12]
    return f" {operator} ".join(f'"{t}"' for t in tokens)


class Registry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self._migrate()

    # ---------- migrations ----------
    def _migrate(self) -> None:
        with self._lock:
            has_meta = self.db.execute("SELECT 1 FROM sqlite_master WHERE name='meta'").fetchone()
            current = 0
            if has_meta:
                row = self.db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
                current = int(row["value"]) if row else 0
            for v in range(current + 1, SCHEMA_VERSION + 1):
                self.db.executescript(MIGRATIONS[v])
                self.db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version',?)", (str(v),))
                self.db.commit()

    def schema_version(self) -> int:
        return int(self.db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()["value"])

    def _q(self, sql: str, args: tuple = ()) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def _one(self, sql: str, args: tuple = ()) -> dict | None:
        rows = self._q(sql, args)
        return rows[0] if rows else None

    # ---------- sources et ressources ----------
    def source(self, key: str, name: str, base_url: str = "", scope: str = "national", kind: str = "loi") -> int:
        if scope not in SCOPES:
            raise ValueError(f"scope inconnu : {scope}")
        with self._lock:
            self.db.execute("INSERT INTO sources(key,name,base_url,scope,kind,created_at) VALUES(?,?,?,?,?,?) "
                            "ON CONFLICT(key) DO UPDATE SET name=excluded.name, base_url=excluded.base_url, "
                            "scope=excluded.scope, kind=excluded.kind",
                            (key, name, base_url, scope, kind, now()))
            self.db.commit()
            return self.db.execute("SELECT id FROM sources WHERE key=?", (key,)).fetchone()["id"]

    def discover(self, source_key: str, url: str, from_url: str | None = None, kind: str = "document",
                 **meta: str | None) -> tuple[int, bool]:
        """Enregistre une ressource AVANT de la télécharger. Retourne (id, nouvelle?)."""
        with self._lock:
            row = self.db.execute("SELECT id FROM resources WHERE url=?", (url,)).fetchone()
            if row:
                cols = [k for k in ("title", "reference", "text_type", "doc_date") if meta.get(k)]
                if cols:  # complète les métadonnées manquantes sans écraser l'existant
                    self.db.execute("UPDATE resources SET " + ", ".join(f"{c}=COALESCE({c}, ?)" for c in cols) + " WHERE id=?",
                                    (*[meta[c] for c in cols], row["id"]))
                    self.db.commit()
                return row["id"], False
            sid = self.db.execute("SELECT id FROM sources WHERE key=?", (source_key,)).fetchone()["id"]
            cur = self.db.execute(
                "INSERT INTO resources(source_id,url,discovered_from,kind,title,reference,text_type,doc_date,discovered_at) "
                "VALUES(?,?,?,?,?,?,?,?,?)",
                (sid, url, from_url, kind, meta.get("title"), meta.get("reference"), meta.get("text_type"),
                 meta.get("doc_date"), now()))
            self.db.commit()
            return cur.lastrowid, True

    def resource(self, url: str) -> dict | None:
        return self._one("SELECT * FROM resources WHERE url=?", (url,))

    def mark(self, rid: int, status: str, *, error: str | None = None, increment_attempts: bool = False,
             retry_in_minutes: int | None = None, **fields: object) -> None:
        if status not in RESOURCE_STATUSES:
            raise ValueError(f"statut inconnu : {status}")
        allowed = {"http_status", "etag", "last_modified", "content_type", "size"}
        extra = {k: v for k, v in fields.items() if k in allowed}
        nxt = (datetime.now(timezone.utc) + timedelta(minutes=retry_in_minutes)).isoformat(timespec="seconds") \
            if retry_in_minutes is not None else None
        sets = ["status=?", "error=?", "last_checked=?", "next_retry=?"] + [f"{k}=?" for k in extra]
        args: list[object] = [status, error, now(), nxt, *extra.values()]
        if increment_attempts:
            sets.append("attempts=attempts+1")
        elif status in ("archived", "inspected"):
            sets.append("attempts=0")
        with self._lock:
            self.db.execute(f"UPDATE resources SET {', '.join(sets)} WHERE id=?", (*args, rid))
            self.db.commit()

    def has_good_version(self, rid: int) -> bool:
        return bool(self._one("SELECT 1 AS x FROM versions WHERE resource_id=? AND is_current=1 AND extraction_status='ok'", (rid,)))

    def set_meta(self, rid: int, **meta: str | None) -> None:
        cols = [k for k in ("title", "reference", "text_type", "doc_date") if meta.get(k)]
        if cols:
            with self._lock:
                self.db.execute("UPDATE resources SET " + ", ".join(f"{c}=COALESCE({c}, ?)" for c in cols) + " WHERE id=?",
                                (*[meta[c] for c in cols], rid))
                self.db.commit()

    def pending(self, source_key: str, limit: int = 500) -> list[dict]:
        """File de reprise : ressources découvertes mais pas archivées, ou à réessayer (échéance atteinte)."""
        return self._q(
            "SELECT r.* FROM resources r JOIN sources s ON s.id=r.source_id WHERE s.key=? AND r.kind='document' "
            "AND (r.status='discovered' OR (r.status='retry' AND (r.next_retry IS NULL OR r.next_retry<=?))) "
            "ORDER BY r.id LIMIT ?", (source_key, now(), limit))

    def due_for_recheck(self, source_key: str, days: float, limit: int = 200) -> list[dict]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
        return self._q(
            "SELECT r.* FROM resources r JOIN sources s ON s.id=r.source_id WHERE s.key=? AND r.status='archived' "
            "AND (r.last_checked IS NULL OR r.last_checked<=?) ORDER BY r.last_checked LIMIT ?", (source_key, cutoff, limit))

    # ---------- versions ----------
    def add_version(self, rid: int, sha256: str, *, file_path: str | None, size: int, content_type: str,
                    pages: int | None, chars: int, extraction_status: str,
                    articles: list[tuple[str, str, int | None]]) -> tuple[str, int]:
        """Retourne ('new'|'changed'|'unchanged', version_id). Les anciennes versions sont conservées."""
        with self._lock:
            cur = self.db.execute("SELECT id, is_current FROM versions WHERE resource_id=? AND sha256=?", (rid, sha256)).fetchone()
            had_any = self.db.execute("SELECT 1 FROM versions WHERE resource_id=? LIMIT 1", (rid,)).fetchone()
            if cur and cur["is_current"]:
                return "unchanged", cur["id"]
            if cur:  # retour à une ancienne version : on la remet « courante »
                vid, change = cur["id"], "changed"
            else:
                c = self.db.execute(
                    "INSERT INTO versions(resource_id,sha256,file_path,size,content_type,pages,chars,extraction_status,collected_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?)", (rid, sha256, file_path, size, content_type, pages, chars, extraction_status, now()))
                vid = c.lastrowid
                for label, content, page in articles:
                    a = self.db.execute("INSERT INTO articles(version_id,label,content,page) VALUES(?,?,?,?)",
                                        (vid, label, content, page))
                    self.db.execute("INSERT INTO articles_fts(rowid,label,content) VALUES(?,?,?)", (a.lastrowid, label, content))
                change = "changed" if had_any else "new"
            self.db.execute("UPDATE versions SET is_current=0 WHERE resource_id=?", (rid,))
            self.db.execute("UPDATE versions SET is_current=1 WHERE id=?", (vid,))
            self.db.execute("UPDATE resources SET current_version_id=?, size=?, content_type=? WHERE id=?",
                            (vid, size, content_type, rid))
            self.db.commit()
            return change, vid

    # ---------- exécutions et erreurs ----------
    def start_run(self, source_key: str) -> int:
        with self._lock:
            cur = self.db.execute("INSERT INTO runs(source_key,started_at) VALUES(?,?)", (source_key, now()))
            self.db.commit()
            return cur.lastrowid

    def finish_run(self, run_id: int, stats: dict, status: str = "done") -> None:
        with self._lock:
            self.db.execute("UPDATE runs SET finished_at=?, status=?, stats_json=? WHERE id=?",
                            (now(), status, json.dumps(stats), run_id))
            self.db.commit()

    def log_error(self, run_id: int | None, resource_id: int | None, url: str, kind: str, message: str) -> None:
        with self._lock:
            self.db.execute("INSERT INTO errors(run_id,resource_id,url,kind,message,at) VALUES(?,?,?,?,?,?)",
                            (run_id, resource_id, url, kind, message[:300], now()))
            self.db.commit()

    def add_relation(self, from_id: int, to_id: int, relation: str, origin: str = "", verified: bool = False) -> int:
        with self._lock:
            cur = self.db.execute("INSERT INTO relations(from_resource_id,to_resource_id,relation,origin,verified,created_at) "
                                  "VALUES(?,?,?,?,?,?)", (from_id, to_id, relation, origin, int(verified), now()))
            self.db.commit()
            return cur.lastrowid

    # ---------- lecture : corpus, recherche, API ----------
    _PROVENANCE = ("a.id AS article_id, a.label, a.content, a.page, v.id AS version_id, v.sha256, v.collected_at, "
                   "v.extraction_status, r.id AS resource_id, r.url, r.title, r.reference, r.text_type, r.doc_date, "
                   "s.key AS source_key, s.name AS source, s.scope, s.kind")
    _FROM = ("FROM articles a JOIN versions v ON v.id=a.version_id AND v.is_current=1 "
             "JOIN resources r ON r.id=v.resource_id JOIN sources s ON s.id=r.source_id")

    def chunks(self, include_demo: bool = False) -> list[dict]:
        """Articles des versions courantes, avec leur provenance, pour l'index de recherche du chat."""
        where = "" if include_demo else "WHERE s.scope != 'demo'"
        return self._q(f"SELECT {self._PROVENANCE} {self._FROM} {where} ORDER BY a.id")

    def search(self, q: str, *, source: str | None = None, scope: str | None = None, limit: int = 20) -> list[dict]:
        """Recherche plein texte (FTS5, classement bm25). « article 12 » retrouve aussi l'article numéroté 12."""
        limit = max(1, min(limit, 100))
        filt, fargs = "", []
        if source:
            filt += " AND s.key=?"
            fargs.append(source)
        if scope:
            filt += " AND s.scope=?"
            fargs.append(scope)
        rows: list[dict] = []
        m = re.search(r"\bart(?:icle|\.)?\s*(\d+)\b", q or "", re.I)
        if m:
            rows += self._q(f"SELECT {self._PROVENANCE}, 0.0 AS rank {self._FROM} WHERE (a.label=? OR a.label LIKE ?){filt} LIMIT ?",
                            (f"Article {m.group(1)}", f"Article {m.group(1)} %", *fargs, limit))
        only_article = bool(m) and not re.sub(r"\bart(?:icle|\.)?\s*\d+\b|\W", "", q or "", flags=re.I)
        for op in () if only_article else ("AND", "OR"):
            fq = _fts_query(q, op)
            if not fq or len(rows) >= limit:
                break
            try:
                rows += self._q(
                    f"SELECT {self._PROVENANCE}, bm25(articles_fts) AS rank FROM articles_fts "
                    f"JOIN articles a ON a.id=articles_fts.rowid JOIN versions v ON v.id=a.version_id AND v.is_current=1 "
                    f"JOIN resources r ON r.id=v.resource_id JOIN sources s ON s.id=r.source_id "
                    f"WHERE articles_fts MATCH ?{filt} ORDER BY rank LIMIT ?", (fq, *fargs, limit))
            except sqlite3.OperationalError:
                rows = rows or []
            if rows:
                break
        seen, out = set(), []
        for r in rows:
            if r["article_id"] not in seen:
                seen.add(r["article_id"])
                out.append(r)
        return out[:limit]

    def list_sources(self) -> list[dict]:
        return self._q("SELECT s.key, s.name, s.base_url, s.scope, "
                       "(SELECT COUNT(*) FROM resources r WHERE r.source_id=s.id AND r.kind='document') AS resources, "
                       "(SELECT COUNT(*) FROM resources r WHERE r.source_id=s.id AND r.status='archived') AS archived "
                       "FROM sources s ORDER BY s.key")

    def list_texts(self, *, source: str | None = None, status: str | None = None, q: str | None = None,
                   limit: int = 50, offset: int = 0) -> list[dict]:
        where, args = ["r.kind='document'"], []
        if source:
            where.append("s.key=?"); args.append(source)
        if status:
            where.append("r.status=?"); args.append(status)
        if q:
            where.append("(r.title LIKE ? OR r.reference LIKE ? OR r.url LIKE ?)"); args += [f"%{q}%"] * 3
        return self._q(
            "SELECT r.id, r.title, r.reference, r.text_type, r.doc_date, r.status, r.url, r.discovered_at, r.last_checked, "
            "s.key AS source_key, s.name AS source, s.scope, v.id AS version_id, v.sha256, v.collected_at, v.pages, "
            "v.extraction_status FROM resources r JOIN sources s ON s.id=r.source_id "
            f"LEFT JOIN versions v ON v.id=r.current_version_id WHERE {' AND '.join(where)} "
            "ORDER BY r.id DESC LIMIT ? OFFSET ?", (*args, max(1, min(limit, 200)), max(0, offset)))

    def get_text(self, rid: int) -> dict | None:
        rows = self._q(
            "SELECT r.id, r.title, r.reference, r.text_type, r.doc_date, r.status, r.url, r.error, r.discovered_from, "
            "r.discovered_at, r.last_checked, r.attempts, s.key AS source_key, s.name AS source, s.scope, "
            "v.id AS version_id, v.sha256, v.collected_at, v.pages, v.chars, v.extraction_status, "
            "(SELECT COUNT(*) FROM articles a WHERE a.version_id=v.id) AS article_count "
            "FROM resources r JOIN sources s ON s.id=r.source_id LEFT JOIN versions v ON v.id=r.current_version_id "
            "WHERE r.id=?", (rid,))
        return rows[0] if rows else None

    def versions(self, rid: int) -> list[dict]:
        return self._q("SELECT id AS version_id, sha256, size, content_type, pages, chars, extraction_status, collected_at, "
                       "is_current FROM versions WHERE resource_id=? ORDER BY id DESC", (rid,))

    def article_list(self, rid: int, version_id: int | None = None, limit: int = 200, offset: int = 0) -> list[dict]:
        vid = version_id or (self.get_text(rid) or {}).get("version_id")
        if not vid:
            return []
        return self._q("SELECT a.id AS article_id, a.label, a.content, a.page FROM articles a JOIN versions v ON v.id=a.version_id "
                       "WHERE v.id=? AND v.resource_id=? ORDER BY a.id LIMIT ? OFFSET ?",
                       (vid, rid, max(1, min(limit, 500)), max(0, offset)))

    def recent_errors(self, limit: int = 50) -> list[dict]:
        return self._q("SELECT e.id, e.run_id, e.resource_id, e.url, e.kind, e.message, e.at FROM errors e "
                       "ORDER BY e.id DESC LIMIT ?", (max(1, min(limit, 500)),))

    def last_run(self) -> dict | None:
        return self._one("SELECT id, source_key, started_at, finished_at, status FROM runs ORDER BY id DESC LIMIT 1")

    # ---------- rapport d'exhaustivité ----------
    def report(self) -> dict:
        by_status = {r["status"]: r["n"] for r in self._q(
            "SELECT status, COUNT(*) AS n FROM resources WHERE kind='document' GROUP BY status")}
        listings = self._one("SELECT COUNT(*) AS n FROM resources WHERE kind='listing' AND status='inspected'")["n"]
        listings_todo = self._one("SELECT COUNT(*) AS n FROM resources WHERE kind='listing' AND status!='inspected'")["n"]
        discovered = self._one("SELECT COUNT(*) AS n FROM resources WHERE kind='document'")["n"]
        extracted = self._one("SELECT COUNT(*) AS n FROM versions WHERE is_current=1 AND extraction_status='ok'")["n"]
        not_extracted = self._one("SELECT COUNT(*) AS n FROM versions WHERE is_current=1 AND extraction_status!='ok'")["n"]
        changes = self._q(
            "SELECT r.id AS resource_id, r.title, r.url, v.collected_at FROM versions v JOIN resources r ON r.id=v.resource_id "
            "WHERE v.is_current=1 AND (SELECT COUNT(*) FROM versions v2 WHERE v2.resource_id=r.id)>1 "
            "ORDER BY v.id DESC LIMIT 10")
        pending = by_status.get("discovered", 0) + by_status.get("retry", 0)
        unexplained = self._one("SELECT COUNT(*) AS n FROM errors WHERE at >= ?",
                                ((datetime.now(timezone.utc) - timedelta(days=1)).isoformat(timespec="seconds"),))["n"]
        reasons = []
        if pending:
            reasons.append(f"{pending} ressource(s) découverte(s) pas encore archivée(s) ou à réessayer")
        if listings_todo:
            reasons.append(f"{listings_todo} page(s) de liste pas encore inspectée(s)")
        if by_status.get("review", 0) or by_status.get("quarantine", 0):
            reasons.append("des documents attendent une revue (scannés, sans article, ou corrompus)")
        if by_status.get("unreachable", 0):
            reasons.append(f"{by_status['unreachable']} ressource(s) inaccessible(s)")
        if unexplained:
            reasons.append(f"{unexplained} erreur(s) dans les dernières 24 h")
        if discovered == 0:
            reasons.append("aucune ressource découverte : la collecte n'a pas encore été exécutée")
        return {
            "schema_version": self.schema_version(),
            "sources": self.list_sources(),
            "listing_pages_inspected": listings,
            "listing_pages_pending": listings_todo,
            "resources_discovered": discovered,
            "resources_by_status": by_status,
            "documents_extracted": extracted,
            "documents_not_extracted": not_extracted,
            "versions_total": self._one("SELECT COUNT(*) AS n FROM versions")["n"],
            "recent_changes": changes,
            "last_run": self.last_run(),
            "complete_within_scope": not reasons,
            "reasons_incomplete": reasons,
            "note": "Exhaustivité mesurée dans le périmètre des pages inspectées ; elle ne prouve pas que le site source "
                    "contient tous les textes togolais.",
        }

    def close(self) -> None:
        with self._lock:
            self.db.close()
