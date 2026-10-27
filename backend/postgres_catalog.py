"""Catalogue PostgreSQL des textes juridiques indexés par Novissi-Droit IA.

Le registre SQLite reste le journal d'ingestion du collecteur (reprises, erreurs,
versions archivées). PostgreSQL devient la source de lecture du RAG lorsque
LEGAL_DATABASE_URL est configurée. Les versions antérieures ne sont jamais supprimées.
"""
from __future__ import annotations

from collections import defaultdict
import re
from typing import Any


SCHEMA = [
    """CREATE TABLE IF NOT EXISTS legal_documents (
        id BIGSERIAL PRIMARY KEY,
        source_url TEXT NOT NULL,
        source_key TEXT NOT NULL,
        source_name TEXT NOT NULL,
        scope TEXT NOT NULL DEFAULT 'national',
        title TEXT,
        reference TEXT,
        text_type TEXT,
        document_date TEXT,
        version_id BIGINT,
        resource_id BIGINT,
        sha256 TEXT NOT NULL,
        collected_at TIMESTAMPTZ,
        is_current BOOLEAN NOT NULL DEFAULT TRUE,
        verified BOOLEAN NOT NULL DEFAULT FALSE,
        legal_status TEXT NOT NULL DEFAULT 'a_verifier',
        synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(source_url, sha256)
    )""",
    """CREATE TABLE IF NOT EXISTS legal_articles (
        id BIGSERIAL PRIMARY KEY,
        document_id BIGINT NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE,
        label TEXT NOT NULL,
        content TEXT NOT NULL,
        page INTEGER,
        search_vector TSVECTOR GENERATED ALWAYS AS (
            to_tsvector('simple', COALESCE(label, '') || ' ' || COALESCE(content, ''))
        ) STORED,
        UNIQUE(document_id, label)
    )""",
    "CREATE INDEX IF NOT EXISTS idx_legal_documents_current ON legal_documents(is_current, source_key)",
    "CREATE INDEX IF NOT EXISTS idx_legal_documents_scope ON legal_documents(scope)",
    "CREATE INDEX IF NOT EXISTS idx_legal_articles_search ON legal_articles USING GIN(search_vector)",
    "CREATE INDEX IF NOT EXISTS idx_legal_articles_document ON legal_articles(document_id)",
]


class PostgresCatalog:
    def __init__(self, dsn: str):
        if not dsn.strip():
            raise ValueError("LEGAL_DATABASE_URL est vide")
        self.dsn = dsn
        with self.connect() as conn:
            for statement in SCHEMA:
                conn.execute(statement)

    def connect(self):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("Installez psycopg[binary] pour utiliser PostgreSQL") from exc
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def sync_from_registry(self, registry) -> dict[str, int]:
        """Copie les articles des versions courantes du registre vers PostgreSQL.

        Les anciennes versions déjà présentes dans PostgreSQL sont conservées avec
        is_current=false ; elles ne sont pas supprimées lors d'une mise à jour.
        """
        chunks = registry.chunks()
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for chunk in chunks:
            url, sha = chunk.get("url"), chunk.get("sha256")
            if url and sha:
                grouped[(str(url), str(sha))].append(chunk)

        docs_count = 0
        articles_count = 0
        with self.connect() as conn:
            with conn.transaction():
                for (url, sha), rows in grouped.items():
                    first = rows[0]
                    conn.execute(
                        "UPDATE legal_documents SET is_current=FALSE WHERE source_url=%s AND sha256<>%s",
                        (url, sha),
                    )
                    doc = conn.execute(
                        """INSERT INTO legal_documents (
                            source_url, source_key, source_name, scope, title, reference,
                            text_type, document_date, version_id, resource_id, sha256,
                            collected_at, is_current, synced_at
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE,NOW())
                        ON CONFLICT(source_url, sha256) DO UPDATE SET
                            source_key=EXCLUDED.source_key,
                            source_name=EXCLUDED.source_name,
                            scope=EXCLUDED.scope,
                            title=EXCLUDED.title,
                            reference=EXCLUDED.reference,
                            text_type=EXCLUDED.text_type,
                            document_date=EXCLUDED.document_date,
                            version_id=EXCLUDED.version_id,
                            resource_id=EXCLUDED.resource_id,
                            collected_at=EXCLUDED.collected_at,
                            is_current=TRUE,
                            synced_at=NOW()
                        RETURNING id""",
                        (
                            url, first.get("source_key") or "inconnu", first.get("source") or "Source inconnue",
                            first.get("scope") or "national", first.get("title"), first.get("reference"),
                            first.get("text_type") or first.get("kind"), first.get("doc_date"),
                            first.get("version_id"), first.get("resource_id"), sha,
                            first.get("collected_at") or first.get("collected") or None,
                        ),
                    ).fetchone()
                    doc_id = doc["id"]
                    docs_count += 1
                    for article in rows:
                        conn.execute(
                            """INSERT INTO legal_articles(document_id,label,content,page)
                            VALUES(%s,%s,%s,%s)
                            ON CONFLICT(document_id,label) DO UPDATE SET
                                content=EXCLUDED.content,page=EXCLUDED.page""",
                            (doc_id, article.get("label") or "Texte", article.get("content") or "", article.get("page")),
                        )
                        articles_count += 1
        return {"documents_synced": docs_count, "articles_synced": articles_count}

    def chunks(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT a.id AS article_id, a.label, a.content, a.page,
                    d.version_id, d.sha256, d.collected_at, d.resource_id,
                    d.source_url AS url, d.title, d.reference, d.text_type,
                    d.source_key, d.source_name AS source, d.scope, d.verified,
                    d.legal_status
                FROM legal_articles a
                JOIN legal_documents d ON d.id=a.document_id
                WHERE d.is_current=TRUE AND d.scope <> 'demo'
                ORDER BY d.source_key, d.source_url, a.id"""
            ).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            collected = d.get("collected_at")
            d["collected"] = collected.date().isoformat() if hasattr(collected, "date") else (str(collected)[:10] if collected else None)
            d["kind"] = d.get("text_type") or "loi"
            d["article"] = d.pop("label")
            d["demo"] = False
            d["id"] = 0
            out.append(d)
        return out


    def search(self, query: str, source: str | None = None, scope: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        """Recherche plein texte PostgreSQL, avec priorité aux numéros d'articles exacts."""
        limit = max(1, min(int(limit), 100))
        conditions = ["d.is_current=TRUE"]
        params: list[Any] = []
        if source:
            conditions.append("d.source_key=%s")
            params.append(source)
        if scope:
            conditions.append("d.scope=%s")
            params.append(scope)
        where = " AND ".join(conditions)
        article_match = re.search(r"\bart(?:icle|\.)?\s*(\d+)\b", query or "", re.I)
        article_clause = ""
        if article_match:
            article_clause = "(a.label ILIKE %s OR a.label ILIKE %s) OR "
            params = [f"Article {article_match.group(1)}", f"Article {article_match.group(1)} %", *params]
        sql = f"""SELECT a.id AS article_id, a.label, a.content, a.page,
            d.version_id, d.sha256, d.collected_at, d.resource_id, d.source_url AS url,
            d.title, d.reference, d.text_type, d.document_date AS doc_date,
            d.source_key, d.source_name AS source, d.scope,
            ts_rank(a.search_vector, websearch_to_tsquery('simple', %s)) AS rank
            FROM legal_articles a JOIN legal_documents d ON d.id=a.document_id
            WHERE {where} AND (({article_clause}FALSE) OR a.search_vector @@ websearch_to_tsquery('simple', %s))
            ORDER BY rank DESC, d.source_name, a.id LIMIT %s"""
        # Paramètres SQL ordonnés : tsquery de score, numéro d'article éventuel, filtres, tsquery de match, limite.
        score_q = query
        if article_match:
            params = [score_q, f"Article {article_match.group(1)}", f"Article {article_match.group(1)} %", *([source] if source else []), *([scope] if scope else []), query, limit]
        else:
            params = [score_q, *([source] if source else []), *([scope] if scope else []), query, limit]
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            collected = d.get("collected_at")
            d["collected"] = collected.date().isoformat() if hasattr(collected, "date") else (str(collected)[:10] if collected else None)
            d["demo"] = d.get("scope") == "demo"
            d["verified"] = False
            out.append(d)
        return out

    def health(self) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                """SELECT COUNT(DISTINCT d.id) AS documents, COUNT(a.id) AS articles
                FROM legal_documents d LEFT JOIN legal_articles a ON a.document_id=d.id
                WHERE d.is_current=TRUE"""
            ).fetchone()
        return dict(row)
