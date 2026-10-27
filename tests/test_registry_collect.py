"""Collecte avec registre : versions, quarantaine, reprise, nouvelles tentatives, requêtes conditionnelles.
Tous les tests utilisent un faux site (httpx.MockTransport) : aucun accès réseau."""
import hashlib
import io

import httpx
import pytest
from reportlab.pdfgen import canvas

import legal_scraper as ls
from registry import Registry

BASE = "https://jo.test"


def make_pdf(articles: list[str]) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    y = 800
    for a in articles:
        c.drawString(40, y, a)
        y -= 18
    c.save()
    return buf.getvalue()


def law_pdf(variant: str = "A") -> bytes:
    return make_pdf([f"Article {i} : Le travailleur a droit a un salaire paye a la date convenue, version {variant}, numero {i}."
                     for i in range(1, 12)])


def listing(*paths: str, nxt: str | None = None) -> str:
    items = "".join(f'<div><a href="{p}">PDF</a></div>' for p in paths)
    more = f'<a href="{BASE}/Lois?page={nxt}">suivant</a>' if nxt else ""
    return f"<html><body>{items}{more}</body></html>"


class Site:
    """Faux site mutable : state[path] = (status, content_type, body, headers)."""

    def __init__(self):
        self.state: dict[str, tuple] = {}
        self.calls: list[tuple[str, dict]] = []

    def handler(self, req: httpx.Request) -> httpx.Response:
        path = req.url.path + (f"?{req.url.query.decode()}" if req.url.query else "")
        self.calls.append((path, dict(req.headers)))
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        entry = self.state.get(path)
        if entry is None:
            return httpx.Response(404)
        status, ctype, body, headers = entry
        if headers.get("etag") and req.headers.get("if-none-match") == headers["etag"]:
            return httpx.Response(304)
        return httpx.Response(status, content=body if isinstance(body, bytes) else body.encode(),
                              headers={"content-type": ctype, **headers})

    def pdf_calls(self) -> list[str]:
        return [p for p, _ in self.calls if p.endswith(".pdf")]


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.delenv("SCRAPER_REFETCH", raising=False)
    site = Site()
    src = ls.JournalOfficialConnector("jo", "Journal Officiel", "loi", [BASE + "/Lois"], r"\.pdf($|\?)")
    reg = Registry(tmp_path / "registry.db")

    def go(max_pages=50):
        f = ls.Fetcher(client=httpx.Client(transport=httpx.MockTransport(site.handler), follow_redirects=True,
                                           headers={"User-Agent": "t"}), delay=0)
        return ls.run(tmp_path / "laws", [src], max_pages=max_pages, fetcher=f, registry=reg,
                      originals_dir=tmp_path / "orig")["sources"]["jo"]

    return site, reg, go, tmp_path


def html(body):  # (status, ctype, body, headers)
    return (200, "text/html", body, {})


def pdf(body, **h):
    return (200, "application/pdf", body, h)


def test_original_conserve_sous_son_sha256_et_version_courante(env):
    site, reg, go, tmp = env
    data = law_pdf()
    site.state = {"/Lois": html(listing("/a.pdf")), "/a.pdf": pdf(data)}
    rep = go()
    assert rep["new"] == 1 and rep["errors"] == 0
    sha = hashlib.sha256(data).hexdigest()
    assert (tmp / "orig" / sha[:2] / f"{sha}.pdf").read_bytes() == data      # original conservé, nommé par son empreinte
    res = reg.resource(BASE + "/a.pdf")
    assert res["status"] == "archived" and res["discovered_from"] == BASE + "/Lois"
    v = reg.versions(res["id"])
    assert len(v) == 1 and v[0]["sha256"] == sha and v[0]["is_current"] == 1 and v[0]["pages"] == 1
    assert reg.article_list(res["id"])[0]["page"] == 1


def test_contenu_modifie_cree_une_nouvelle_version_et_garde_l_ancienne(env, monkeypatch):
    site, reg, go, tmp = env
    site.state = {"/Lois": html(listing("/a.pdf")), "/a.pdf": pdf(law_pdf("A"))}
    go()
    monkeypatch.setenv("SCRAPER_REFETCH", "1")                      # recontrôle toutes les ressources connues
    site.state["/a.pdf"] = pdf(law_pdf("B"))
    rep = go()
    assert rep["updated"] == 1
    res = reg.resource(BASE + "/a.pdf")
    vs = reg.versions(res["id"])
    assert len(vs) == 2 and [v["is_current"] for v in vs] == [1, 0]  # ancienne version conservée, non courante
    assert all((tmp / "orig" / v["sha256"][:2] / f"{v['sha256']}.pdf").exists() for v in vs)
    assert "version B" in reg.article_list(res["id"])[0]["content"]
    assert reg.report()["recent_changes"][0]["resource_id"] == res["id"]


def test_pdf_corrompu_en_quarantaine_sans_remplacer_une_version_valide(env, monkeypatch):
    site, reg, go, tmp = env
    bad = b"%PDF-1.4\nceci n'est pas un vrai pdf"
    site.state = {"/Lois": html(listing("/bad.pdf", "/a.pdf")), "/bad.pdf": pdf(bad), "/a.pdf": pdf(law_pdf())}
    rep = go()
    assert rep["errors"] == 1 and rep["new"] == 1
    r = reg.resource(BASE + "/bad.pdf")
    assert r["status"] == "quarantine" and reg.versions(r["id"])[0]["extraction_status"] == "failed"
    assert (tmp / "orig" / hashlib.sha256(bad).hexdigest()[:2]).exists()       # l'original corrompu est gardé
    # mise à jour corrompue d'un document valide : la version valide reste courante
    monkeypatch.setenv("SCRAPER_REFETCH", "1")
    site.state["/a.pdf"] = pdf(bad)
    go()
    a = reg.resource(BASE + "/a.pdf")
    assert a["status"] == "archived" and len(reg.versions(a["id"])) == 1 and reg.has_good_version(a["id"])
    assert any(e["kind"] == "extraction" for e in reg.recent_errors())


def test_pdf_scanne_sans_texte_marque_a_revoir_et_non_traite(env):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/scan.pdf")), "/scan.pdf": pdf(make_pdf([]))}
    rep = go()
    r = reg.resource(BASE + "/scan.pdf")
    assert rep["skipped_empty"] >= 1 and r["status"] == "review" and "OCR" in r["error"]
    assert reg.report()["documents_not_extracted"] == 1 and reg.report()["documents_extracted"] == 0


def test_faux_pdf_html_marque_non_document(env):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/faux.pdf")), "/faux.pdf": (200, "text/html", "<html>Erreur</html>", {})}
    go()
    assert reg.resource(BASE + "/faux.pdf")["status"] == "non_document"


def test_erreur_temporaire_retry_puis_reprise_au_redemarrage(env):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/a.pdf")), "/a.pdf": (503, "text/plain", "indisponible", {})}
    rep = go()
    r = reg.resource(BASE + "/a.pdf")
    assert rep["errors"] == 1 and r["status"] == "retry" and r["attempts"] == 1 and r["next_retry"]
    assert any(e["kind"] == "transient" for e in reg.recent_errors())
    # le serveur revient ; l'échéance de retry est atteinte ; nouvelle exécution = reprise
    reg.db.execute("UPDATE resources SET next_retry='2000-01-01T00:00:00+00:00' WHERE id=?", (r["id"],))
    reg.db.commit()
    site.state["/a.pdf"] = pdf(law_pdf())
    assert go()["new"] == 1 and reg.resource(BASE + "/a.pdf")["status"] == "archived"


def test_ressource_permanente_inaccessible_n_est_pas_reessayee(env):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/gone.pdf"))}      # 404
    go()
    assert reg.resource(BASE + "/gone.pdf")["status"] == "unreachable"
    n = len(site.pdf_calls())
    go()
    assert len(site.pdf_calls()) == n                         # pas retéléchargée


def test_reprise_apres_interruption_sans_perdre_l_inventaire(env):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/a.pdf", "/b.pdf")), "/a.pdf": pdf(law_pdf("A")), "/b.pdf": pdf(law_pdf("B"))}
    go(max_pages=2)                                           # « interrompu » après la liste + 1 PDF
    assert reg.resource(BASE + "/b.pdf")["status"] == "discovered"   # découvert AVANT téléchargement, en attente
    site.calls.clear()
    rep = go()                                                # « redémarrage »
    assert rep["new"] == 1 and reg.resource(BASE + "/b.pdf")["status"] == "archived"
    assert site.pdf_calls().count("/a.pdf") == 0              # a.pdf n'est pas retéléchargé


def test_requete_conditionnelle_etag_304(env, monkeypatch):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/a.pdf")), "/a.pdf": pdf(law_pdf(), etag='"v1"')}
    go()
    assert reg.resource(BASE + "/a.pdf")["etag"] == '"v1"'
    monkeypatch.setenv("SCRAPER_REFETCH", "1")
    site.calls.clear()
    rep = go()
    sent = [h for p, h in site.calls if p == "/a.pdf"]
    assert sent and sent[0].get("if-none-match") == '"v1"' and rep["unchanged"] >= 1 and rep["updated"] == 0
    assert len(reg.versions(reg.resource(BASE + "/a.pdf")["id"])) == 1


def test_pagination_suivie_et_listes_inspectees(env):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/a.pdf", nxt="1")), "/Lois?page=1": html(listing("/b.pdf")),
                  "/a.pdf": pdf(law_pdf("A")), "/b.pdf": pdf(law_pdf("B"))}
    assert go()["new"] == 2
    rapport = reg.report()
    assert rapport["listing_pages_inspected"] == 2 and rapport["resources_discovered"] == 2


def test_rapport_ne_pretend_pas_etre_exhaustif_tant_que_des_restes_existent(env):
    site, reg, go, _ = env
    assert reg.report()["complete_within_scope"] is False                  # rien collecté
    site.state = {"/Lois": html(listing("/a.pdf", "/gone.pdf")), "/a.pdf": pdf(law_pdf())}
    go()
    r = reg.report()
    assert r["complete_within_scope"] is False and r["resources_by_status"]["unreachable"] == 1
    assert any("inaccessible" in x for x in r["reasons_incomplete"]) and "ne prouve pas" in r["note"]


def test_connecteur_jo_extrait_reference_date_et_titre():
    page = ('<div class="views-row"><a href="/node/1">LOI 2025 - 006 14/04/2025</a><p>PORTANT LUTTE CONTRE LES CHANGEMENTS CLIMATIQUES.</p>'
            '<a href="/sites/default/files/JO/x.pdf#page=3">dl</a></div>'
            '<div><a href="/a.pdf">x</a><a href="/b.pdf">y</a>LOI 2020-001 01/01/2020 ambigu</div>')
    src = ls.JournalOfficialConnector("jo", "JO", "loi", [BASE + "/Lois"], r"\.pdf")
    d = src.describe_links(page, BASE + "/Lois")
    meta = d[BASE + "/sites/default/files/JO/x.pdf"]
    assert meta["reference"] == "LOI 2025-006" and meta["doc_date"] == "2025-04-14" and "CLIMATIQUES" in meta["title"]
    assert BASE + "/a.pdf" not in d                      # bloc ambigu (2 PDF) : aucune métadonnée devinée


def test_relations_entre_textes_et_migrations(env):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/a.pdf", "/b.pdf")), "/a.pdf": pdf(law_pdf("A")), "/b.pdf": pdf(law_pdf("B"))}
    go()
    a, b = reg.resource(BASE + "/a.pdf")["id"], reg.resource(BASE + "/b.pdf")["id"]
    reg.add_relation(b, a, "modifie", origin="saisie test")
    assert reg.db.execute("SELECT verified FROM relations").fetchone()[0] == 0     # jamais « vérifié » automatiquement
    with pytest.raises(Exception):
        reg.add_relation(b, a, "inconnue")                                          # contrainte CHECK
    assert Registry(reg.path).schema_version() == 2                                 # réouverture : migrations idempotentes


def test_redirection_hors_domaine_refusee(env):
    site, reg, go, _ = env
    site.state = {"/Lois": html(listing("/a.pdf")), "/a.pdf": (302, "text/plain", "", {"location": "https://evil.example/secret.pdf"}),
                  "/secret.pdf": pdf(law_pdf())}
    rep = go()
    assert rep["new"] == 0 and rep["errors"] == 1
    assert reg.resource(BASE + "/a.pdf")["status"] == "non_document"
    assert any(e["kind"] == "ssrf_guard" for e in reg.recent_errors())
