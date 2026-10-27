"""Splitter, migrations, RAG sur registre (provenance, mode démonstration) et routes /legal et /collection."""
import sqlite3

import pytest
from fastapi.testclient import TestClient

import main
import rag
import registry as registry_mod
from registry import Registry
from splitter import split_articles, split_by_kind

DEMO_TXT = "# source: EXEMPLE FICTIF\n# kind: loi\n\nArticle 1. Le preneur doit payer le loyer fictif chaque mois sans retard.\n"


# ---------- splitter ----------
def test_splitter_articles_pages_et_formes():
    txt = ("Préambule\nArticle premier : Disposition une.\f\nArticle 12 bis. Disposition deux.\nArt. 3 - Disposition trois.\n"
           "Article 4 :   \n")
    got = split_articles(txt)
    assert [g[0] for g in got] == ["Article 1", "Article 12 bis", "Article 3"]     # l'article vide est ignoré
    assert [g[2] for g in got] == [1, 2, 2]
    assert split_by_kind("Para un.\n\nPara deux.", "analyse")[0][0] == "Analyse §1"
    assert split_articles("") == []


# ---------- migrations ----------
def test_migration_v1_vers_v2_conserve_les_donnees(tmp_path):
    p = tmp_path / "old.db"
    db = sqlite3.connect(p)
    db.executescript(registry_mod.MIGRATIONS[1])
    db.execute("INSERT INTO meta VALUES('schema_version','1')")
    db.execute("INSERT INTO sources(key,name,scope,created_at) VALUES('jo','JO','national','2025-01-01')")
    db.commit(); db.close()
    reg = Registry(p)
    assert reg.schema_version() == 2
    assert reg.list_sources()[0]["key"] == "jo"
    assert reg.db.execute("SELECT kind FROM sources").fetchone()[0] == "loi"


# ---------- fixtures ----------
@pytest.fixture
def corpus(tmp_path, monkeypatch):
    laws = tmp_path / "laws"
    laws.mkdir()
    (laws / "EXEMPLE_FICTIF_bail.txt").write_text(DEMO_TXT, encoding="utf-8")
    reg = Registry(tmp_path / "registry.db")
    reg.source("jo", "Journal Officiel", "https://jo.test", "national", "loi")
    rid, _ = reg.discover("jo", "https://jo.test/a.pdf", "https://jo.test/Lois", title="Code du travail",
                          reference="LOI 2021-012", doc_date="2021-06-18")
    reg.add_version(rid, "ab" * 32, file_path="ab/abab.pdf", size=10, content_type="application/pdf", pages=2, chars=300,
                    extraction_status="ok",
                    articles=[("Article 1", "Le salaire doit être payé à la date convenue entre l'employeur et le travailleur.", 1),
                              ("Article 2", "Le licenciement abusif ouvre droit à des dommages et intérêts.", 2)])
    reg.mark(rid, "archived")
    index = rag.LiveIndex(laws, reg)
    monkeypatch.setattr(main, "registry", reg)
    monkeypatch.setattr(main, "index", index)
    return reg, index, rid, TestClient(main.app), laws


# ---------- RAG : provenance et mode démonstration ----------
def test_rag_lit_le_registre_avec_provenance_et_exclut_la_demo_si_officiel(corpus):
    reg, index, rid, _, _ = corpus
    assert index.mode == "officiel" and len(index.chunks) == 2
    hit = index.search("salaire payé employeur", k=1)[0]
    assert hit["resource_id"] == rid and hit["sha256"] == "ab" * 32 and hit["page"] == 1 and not hit["demo"]
    assert hit["verified"] is False and hit["reference"] == "LOI 2021-012"


def test_modes_demonstration_auto_on_off(tmp_path):
    laws = tmp_path / "laws"; laws.mkdir()
    (laws / "EXEMPLE_FICTIF_bail.txt").write_text(DEMO_TXT, encoding="utf-8")
    reg = Registry(tmp_path / "r.db")
    idx = rag.LiveIndex(laws, reg, demo_mode="auto")
    assert idx.mode == "demonstration" and all(c["demo"] for c in idx.chunks)       # corpus vide : démo, explicitement signalée
    assert rag.LiveIndex(laws, reg, demo_mode="off").chunks == []
    reg.source("jo", "JO", "", "national")
    rid, _ = reg.discover("jo", "https://jo.test/x.pdf")
    reg.add_version(rid, "cd" * 32, file_path=None, size=1, content_type="application/pdf", pages=1, chars=99,
                    extraction_status="ok", articles=[("Article 1", "Texte officiel réel.", 1)])
    assert rag.LiveIndex(laws, reg, demo_mode="auto").mode == "officiel"
    mixed = rag.LiveIndex(laws, reg, demo_mode="on")
    assert mixed.mode == "mixte" and {c["demo"] for c in mixed.chunks} == {True, False}


def test_exports_derives_ne_sont_pas_comptes_deux_fois(corpus):
    reg, _, rid, _, laws = corpus
    (laws / "jo__code.txt").write_text(
        f"# source: Journal Officiel\n# kind: loi\n# resource_id: {rid}\n# version_id: 1\n\nArticle 1. Le salaire doit être payé.\n",
        encoding="utf-8")
    assert len(rag.LiveIndex(laws, reg).chunks) == 2        # export dérivé ignoré : le registre est la source de vérité


# ---------- chat : citations avec provenance ----------
def test_chat_citations_portent_la_provenance_du_registre(corpus, monkeypatch):
    _, _, rid, client, _ = corpus
    monkeypatch.setattr(main, "configured_providers", lambda: [])
    r = client.post("/chat", json={"message": "Mon employeur ne paie pas mon salaire à la date convenue"}).json()
    assert r["citations"] and r["citations"][0]["sha256"] == "ab" * 32 and r["citations"][0]["demo"] is False
    assert r["citations"][0]["verified"] is False and r["citations"][0]["url"] == "https://jo.test/a.pdf"


# ---------- routes /legal ----------
def test_routes_legal_consultation(corpus):
    reg, _, rid, client, _ = corpus
    assert client.get("/legal/sources").json()["sources"][0]["key"] == "jo"
    texts = client.get("/legal/texts", params={"status": "archived"}).json()["texts"]
    assert texts[0]["reference"] == "LOI 2021-012" and texts[0]["sha256"] == "ab" * 32
    assert client.get(f"/legal/texts/{rid}").json()["article_count"] == 2
    assert len(client.get(f"/legal/texts/{rid}/versions").json()["versions"]) == 1
    arts = client.get(f"/legal/texts/{rid}/articles").json()["articles"]
    assert [a["label"] for a in arts] == ["Article 1", "Article 2"]
    assert client.get("/legal/texts/9999").status_code == 404
    assert client.get("/legal/texts", params={"status": "inventé"}).status_code == 422


def test_recherche_par_contenu_et_par_numero_article(corpus):
    _, _, rid, client, _ = corpus
    by_content = client.get("/legal/search", params={"q": "licenciement abusif"}).json()
    assert by_content["hits"][0]["article"] == "Article 2" and by_content["hits"][0]["verified"] is False
    by_number = client.get("/legal/search", params={"q": "article 1"}).json()["hits"]
    assert [h["article"] for h in by_number] == ["Article 1"]
    assert client.get("/legal/search", params={"q": "a"}).status_code == 422
    assert client.get("/legal/search", params={"q": "salaire", "source": "autre"}).json()["hits"] == []
    assert "non vérifié" in by_content["note"]


def test_aucun_chemin_de_stockage_expose(corpus):
    _, _, rid, client, _ = corpus
    blob = "".join(client.get(u).text for u in (f"/legal/texts/{rid}", f"/legal/texts/{rid}/versions", "/legal/texts",
                                                 "/collection/status", "/legal/search?q=salaire"))
    assert "file_path" not in blob and "ab/abab.pdf" not in blob and "originals" not in blob


def test_collection_status_et_erreurs(corpus):
    reg, _, rid, client, _ = corpus
    reg.log_error(None, rid, "https://jo.test/b.pdf", "transient", "HTTP 503")
    st = client.get("/collection/status").json()
    assert st["corpus_mode"] == "officiel" and st["indexed_chunks"] == 2 and st["complete_within_scope"] is False
    assert client.get("/collection/errors").json()["errors"][0]["kind"] == "transient"
    assert client.get("/health").json()["corpus_mode"] == "officiel"


def test_synchronisation_reservee_aux_administrateurs(corpus, monkeypatch):
    _, _, _, client, _ = corpus
    monkeypatch.setattr(main, "ADMIN_TOKEN", "secret")
    monkeypatch.setattr(main.legal_scraper, "run", lambda d, **kw: {"finished": "now", "sources": {}})
    assert client.post("/admin/sync").status_code == 403
    assert client.post("/admin/sync", headers={"x-admin-token": "mauvais"}).status_code == 403
    assert client.post("/admin/sync", headers={"x-admin-token": "secret"}).json()["status"] == "ok"
    monkeypatch.setattr(main, "ADMIN_TOKEN", "")
    assert client.post("/admin/sync").status_code == 503
