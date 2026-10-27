"""Tests du prototype : lancer avec `pytest -q` depuis la racine du projet."""
import json
import os
import pathlib
import sys

import httpx
import pytest

os.environ["SCRAPER_ENABLED"] = "0"          # pas de réseau pendant les tests
for _k in ("GROK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "OLLAMA_MODEL"):
    os.environ.pop(_k, None)
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient  # noqa: E402

import legal_scraper  # noqa: E402
import main  # noqa: E402
import rag  # noqa: E402
import terracheck  # noqa: E402

client = TestClient(main.app)
QUESTION = "mon patron ne m'a pas payé mon salaire"


# ---------- garde-fous ----------
def test_guards():
    assert "<" not in rag.clean_user_text("<script>x</script>")
    assert rag.citations_valid("ok [1] [2]", {"1", "2"})
    assert not rag.citations_valid("faux [99]", {"1", "2"})
    assert not rag.citations_valid("aucune citation", {"1"})


# ---------- RAG ----------
def test_retrieval_finds_article():
    top = rag.Retriever(rag.load_chunks(main.LAW_DIR)).search(QUESTION, k=1)[0]
    assert top["article"] == "Article 1" and top["kind"] == "loi"


def test_analysis_documents_are_chunked_by_paragraph(tmp_path):
    (tmp_path / "a.txt").write_text("# source: LQD\n# kind: analyse\n\nPremier paragraphe sur le bail.\n\nSecond paragraphe.", encoding="utf-8")
    chunks = rag.load_chunks(tmp_path)
    assert chunks and chunks[0]["kind"] == "analyse" and chunks[0]["article"].startswith("Analyse")


def test_live_reload_picks_up_new_law_without_restart(tmp_path):
    idx = rag.LiveIndex(tmp_path)
    assert idx.search("préavis expulsion") == []
    (tmp_path / "n.txt").write_text("# source: Test\n\nArticle 7. Le préavis d'expulsion est de trois mois.", encoding="utf-8")
    assert idx.reload() == 1
    assert idx.search("préavis expulsion")[0]["article"] == "Article 7"


# ---------- scraper ----------
HTML_LIST = '<html><body><a href="/textes/code-travail">Code</a><a href="/hors-sujet">x</a></body></html>'
ARTICLES = " ".join(f"Article {i}. Le travailleur a droit à un salaire payé à la date prévue par le contrat de travail et les usages." for i in range(1, 9))
HTML_LAW = f"<html><head><title>Code du travail</title></head><body><nav>menu</nav><main>{ARTICLES}</main></body></html>"


def fake_site(robots="User-agent: *\nAllow: /"):
    def handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        if path == "/robots.txt":
            return httpx.Response(200, text=robots)
        if path == "/":
            return httpx.Response(200, text=HTML_LIST, headers={"content-type": "text/html"})
        if path == "/textes/code-travail":
            return httpx.Response(200, text=HTML_LAW, headers={"content-type": "text/html"})
        return httpx.Response(404)
    return Fetcher_for(handler)


def Fetcher_for(handler):
    return legal_scraper.Fetcher(client=httpx.Client(transport=httpx.MockTransport(handler)), delay=0)


def make_source():
    return legal_scraper.Source("jo", "Journal Officiel", "loi", ["https://jo.test/"], r"/textes/")


def test_scraper_saves_articles_and_reindexes(tmp_path):
    rep = legal_scraper.run(tmp_path, [make_source()], fetcher=fake_site())
    assert rep["sources"]["jo"]["new"] == 1 and rep["sources"]["jo"]["errors"] == 0
    chunks = rag.load_chunks(tmp_path)
    assert len(chunks) == 8 and chunks[0]["url"] == "https://jo.test/textes/code-travail"
    assert "menu" not in chunks[0]["content"]


def test_scraper_skips_unchanged_documents(tmp_path):
    legal_scraper.run(tmp_path, [make_source()], fetcher=fake_site())
    rep = legal_scraper.run(tmp_path, [make_source()], fetcher=fake_site())
    assert rep["sources"]["jo"]["unchanged"] == 1 and rep["sources"]["jo"]["new"] == 0


def test_scraper_respects_robots(tmp_path):
    rep = legal_scraper.run(tmp_path, [make_source()], fetcher=fake_site("User-agent: *\nDisallow: /"))
    assert rep["sources"]["jo"]["skipped_robots"] >= 1 and not list(tmp_path.glob("jo__*"))


def test_scraper_survives_network_failure(tmp_path):
    def boom(req):
        raise httpx.ConnectError("réseau coupé")
    rep = legal_scraper.run(tmp_path, [make_source()], fetcher=Fetcher_for(boom))
    assert rep["sources"]["jo"]["new"] == 0  # aucune exception levée


def test_normalize_articles_splits_glued_articles():
    out = legal_scraper.normalize_articles("Article 1. Texte un. Article 2. Texte deux.")
    assert out.splitlines()[1].startswith("Article 2")


# ---------- TerraCheck ----------
def test_terracheck_scores():
    p = terracheck.load_parcels(main.DATA_DIR / "parcels.json")
    assert terracheck.diagnose(p["TG-BAG-008"])["score"] == "vert"
    assert terracheck.diagnose(p["TG-ADI-042"])["score"] == "orange"
    d = terracheck.diagnose(p["TG-KEG-031"])
    assert d["score"] == "rouge" and not d["checks"][1]["ok"]  # double vente calculée sur les ventes
    assert d["elapsed_ms"] < 10_000


def test_acte_mismatch_downgrades_green_to_orange():
    p = terracheck.load_parcels(main.DATA_DIR / "parcels.json")["TG-BAG-008"]
    assert terracheck.diagnose(p, {"proprietaire": "KPODAR Jean", "superficie_m2": 800})["score"] == "orange"
    assert terracheck.diagnose(p, {"proprietaire": "Edem LAWSON", "superficie_m2": "8 ares"})["score"] == "vert"


def test_match_never_guesses():
    ps = terracheck.load_parcels(main.DATA_DIR / "parcels.json")
    assert terracheck.match_parcel({"lot": "14", "quartier": "Agoè-Nyivé"}, ps)["parcel_id"] == "TG-AGN-014"
    assert terracheck.match_parcel({"lot": "14", "quartier": "Kara"}, ps)["status"] == "not_found"
    assert terracheck.match_parcel({"quartier": "Agoè-Nyivé"}, ps)["status"] == "not_found"


ACTE = ("Acte de vente. Vendeur : Monsieur KOFFI Mensah vend à Madame AKAKPO Ama une parcelle située à Agoè-Nyivé, "
        "lot n° 14, îlot 3, d'une superficie de 600 m². Titre foncier n° 12345/TG.")


def test_regex_extraction():
    f = terracheck.extract_fields(ACTE, ["Agoè-Nyivé"])
    assert f["lot"] == "14" and f["ilot"] == "3" and f["superficie_m2"] == 600 and f["quartier"] == "Agoè-Nyivé"
    assert f["proprietaire"].startswith("KOFFI")


# ---------- API ----------
def test_health_reports_index():
    h = client.get("/health").json()
    assert h["ok"] and h["chunks"] >= 6 and "analyse" in h["by_kind"]


def test_chat_valid_citation(monkeypatch):
    monkeypatch.setattr(main, "llm", lambda s, u, max_tokens=900: "Écrivez une mise en demeure [1].")
    r = client.post("/chat", json={"message": QUESTION}).json()
    assert r["mode"] == "ia" and r["citations"]


def test_chat_blocks_invented_citation(monkeypatch):
    monkeypatch.setattr(main, "llm", lambda s, u, max_tokens=900: "Selon l'article [999]...")
    assert client.post("/chat", json={"message": QUESTION}).json()["mode"] == "citation_invalide"


def test_chat_requires_a_citation(monkeypatch):
    monkeypatch.setattr(main, "llm", lambda s, u, max_tokens=900: "Réponse sans source.")
    assert client.post("/chat", json={"message": QUESTION}).json()["mode"] == "citation_invalide"


def test_chat_refuses_out_of_scope():
    assert client.post("/chat", json={"message": "recette du riz au gras"}).json()["mode"] == "refus"


def test_chat_degrades_to_extracts_when_llm_fails(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("réseau")
    monkeypatch.setattr(main, "llm", boom)
    r = client.post("/chat", json={"message": QUESTION}).json()
    assert r["mode"] == "extraits" and r["citations"]


def test_chat_local_language_gets_a_notice(monkeypatch):
    monkeypatch.setattr(main, "llm", lambda s, u, max_tokens=900: "Voir [1].")
    assert client.post("/chat", json={"message": QUESTION, "lang": "Ewé"}).json()["notice"]


def test_letter_generation():
    body = {"kind": "salaire", "nom": "Ama KOFFI", "destinataire": "Société X", "ville": "Lomé",
            "montant_fcfa": 300000, "periode": "3 mois"}
    r = client.post("/documents", json=body).json()
    assert "300 000 FCFA" in r["texte"] and "inspection du travail" in r["texte"] and r["services"]
    assert client.post("/documents", json={**body, "kind": "autre"}).status_code == 422


def test_decode_falls_back_to_rules_and_links_terracheck():
    r = client.post("/decode", json={"text": ACTE}).json()   # pas de clé API : mode règles
    assert r["mode"] == "regles" and r["match"]["status"] == "found"
    assert r["terracheck"]["id"] == "TG-AGN-014" and r["terracheck"]["score"] == "vert"


def test_decode_with_ai_merges_fields(monkeypatch):
    out = {"resume": "Vente.", "champs": {"lot": "31", "quartier": "Kégué", "proprietaire": "DOGBE Ama", "superficie_m2": "500 m²"},
           "clauses": [{"extrait": "x", "risque": "élevé", "explication": "y"}]}
    monkeypatch.setattr(main, "llm", lambda s, u, max_tokens=900: json.dumps(out))
    r = client.post("/decode", json={"text": "Acte de vente d'un terrain à Kégué, lot 31."}).json()
    assert r["mode"] == "ia" and r["clauses"] and r["terracheck"]["score"] == "rouge"


def test_decode_bad_json_degrades(monkeypatch):
    monkeypatch.setattr(main, "llm", lambda s, u, max_tokens=900: "pas du json")
    assert client.post("/decode", json={"text": ACTE}).json()["mode"] == "regles"


def test_terracheck_endpoints():
    assert len(client.get("/terracheck").json()) == 5
    assert client.get("/terracheck/nope").status_code == 404


def test_ocr_rejects_non_image():
    r = client.post("/ocr", files={"file": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_admin_refresh_is_protected(monkeypatch):
    monkeypatch.setattr(main, "ADMIN_TOKEN", "")
    assert client.post("/admin/refresh").status_code == 503
    monkeypatch.setattr(main, "ADMIN_TOKEN", "secret")
    assert client.post("/admin/refresh", headers={"X-Admin-Token": "faux"}).status_code == 403
    monkeypatch.setattr(main.legal_scraper, "run", lambda d, **kw: {"finished": "now", "sources": {}})
    ok = client.post("/admin/refresh", headers={"X-Admin-Token": "secret"}).json()
    assert ok["status"] == "ok" and ok["chunks"] >= 6


# ---------- fournisseurs de modèles gratuits ----------
def test_no_key_means_no_provider(monkeypatch):
    for var in ("GROK_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "OLLAMA_MODEL"):
        monkeypatch.setenv(var, "")   # indépendant du .env réel de la machine
    monkeypatch.setenv("LLM_PROVIDERS", "gemini,groq")
    assert main.configured_providers() == []
    assert client.get("/health").json()["ai"] == []


def test_providers_follow_configured_order(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")
    monkeypatch.setenv("LLM_PROVIDERS", "gemini,groq,ollama,inconnu")
    assert main.configured_providers() == ["gemini", "groq", "ollama"]


class FakeResp:
    def __init__(self, status, text="ok"):
        self.status, self.text = status, text

    def raise_for_status(self):
        if self.status >= 400:
            raise httpx.HTTPStatusError("erreur", request=None, response=None)

    def json(self):
        return {"choices": [{"message": {"content": self.text}}]}


def test_llm_falls_back_to_next_provider(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("LLM_PROVIDERS", "gemini,groq")
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append((url, json["model"]))
        return FakeResp(429) if "generativelanguage" in url else FakeResp(200, "réponse groq [1]")
    monkeypatch.setattr(main.httpx, "post", fake_post)
    assert main.llm("sys", "question") == "réponse groq [1]"
    assert [c[1] for c in calls] == ["gemini-2.5-flash", "openai/gpt-oss-120b"]


def test_llm_raises_when_all_providers_fail(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("LLM_PROVIDERS", "groq")
    monkeypatch.setattr(main.httpx, "post", lambda *a, **k: FakeResp(500))
    with pytest.raises(Exception):
        main.llm("s", "u")


def test_llm_falls_back_from_openai_to_gemini_and_groq(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("LLM_PROVIDERS", "openai,gemini,groq")
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append((url, json["model"]))
        if "api.openai.com" in url:
            return FakeResp(503)
        if "generativelanguage" in url:
            return FakeResp(429)
        return FakeResp(200, "réponse groq de secours [1]")
    monkeypatch.setattr(main.httpx, "post", fake_post)
    assert main.llm("sys", "question") == "réponse groq de secours [1]"
    assert [c[1] for c in calls] == ["gpt-4.1-mini", "gemini-2.5-flash", "openai/gpt-oss-120b"]


def test_grok_primary_and_fallback(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "xai-test-key")
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key")
    monkeypatch.setenv("LLM_PROVIDERS", "grok,groq")
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append((url, json["model"]))
        if "api.x.ai" in url:
            return FakeResp(503)
        return FakeResp(200, "Explication détaillée du droit togolais [1]")
    monkeypatch.setattr(main.httpx, "post", fake_post)
    assert main.llm("sys", "question") == "Explication détaillée du droit togolais [1]"
    assert calls[0][1] == "grok-3-mini"


def test_oauth_and_email_account_registration():
    r = client.post("/auth/oauth", json={"provider": "google", "email": "citoyen@togo.tg", "name": "Koffi Mensah", "ville": "Lomé"}, headers={"X-Client-Id": "anon_device_12345"})
    assert r.status_code == 200 and r.json()["user"]["provider"] == "google"
    r2 = client.post("/auth/register", json={"email": "ama@togo.tg", "name": "Ama Dogbe", "password": "secretpassword", "ville": "Kara"}, headers={"X-Client-Id": "anon_device_12345"})
    assert r2.status_code == 200 and r2.json()["user"]["email"] == "ama@togo.tg"


def test_deterministic_togolese_risk_clauses():
    acte_risque = "Acte de vente. Vendeur : Monsieur KOFFI Mensah vend à Madame AKAKPO Ama une parcelle située à Agoè-Nyivé, lot n° 14, îlot 3, d'une superficie de 600 m². L'acquéreur paie le prix en totalité à la signature, sans aucune garantie du vendeur."
    r = client.post("/decode", json={"text": acte_risque}).json()
    assert r["mode"] == "regles" and len(r["clauses"]) >= 1


# ---------- non-régression : URLs des fournisseurs & modèle 120b ----------
def test_provider_urls_are_plain_https():
    """Régression : des liens markdown « [https://…](https://…) » avaient été collés dans le code."""
    for name, (base, *_rest) in main.PROVIDERS.items():
        if base and name != "ollama":
            assert base.startswith("https://") and "[" not in base and "](" not in base, name


def test_groq_key_in_grok_slot_uses_120b_then_other_groq_models(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "gsk_cle_groq")
    monkeypatch.setenv("GROQ_API_KEY", "gsk_cle_groq")
    monkeypatch.setenv("GROK_MODEL", "openai/gpt-oss-20b")
    monkeypatch.setenv("GROQ_MODEL", "openai/gpt-oss-120b")
    monkeypatch.setenv("LLM_PROVIDERS", "grok,groq")
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append((url, json["model"], json.get("reasoning_effort")))
        return FakeResp(413) if json["model"] == "openai/gpt-oss-120b" else FakeResp(200, "ok [1]")
    monkeypatch.setattr(main.httpx, "post", fake_post)
    assert main.llm("sys", "question") == "ok [1]"
    assert [c[1] for c in calls] == ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]   # 120b d'abord, sans doublon
    assert calls[0][0] == "https://api.groq.com/openai/v1/chat/completions"
    assert calls[0][2] == "low"


def test_replace_french_headers_in_ewe_and_kabiye():
    import translator
    raw = "**En résumé (Vos droits immédiats) :**\nVous avez droit au salaire [1].\n**Ce que dit le droit togolais :**\nArticle 1 [1]."
    ewe_out = translator.replace_french_headers(raw, "Ewé")
    assert "Nya vevitɔwo" in ewe_out and "Nu si Togo ƒe se gblɔ" in ewe_out
    kab_out = translator.replace_french_headers(raw, "Kabiyè")
    assert "Tɔm kɛdɩtʊ" in kab_out and "Togo paɣtʊ yɔɔdʊʊ se" in kab_out
