"""Crawl simulé de jo.gouv.tg/Lois : pagination ?page=N, liens PDF avec #page=N, reprise sans retéléchargement."""
import pathlib
import sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "backend"))
import legal_scraper as ls  # noqa: E402

BASE = "https://jo.gouv.tg"


def _list_page(n: int) -> str:
    pdfs = "".join(f'<div><a href="{BASE}/node/{n}{i}">Loi {n}{i}</a>'
                   f'<a href="{BASE}/sites/default/files/JO/JO_{n}_{i}.pdf#page=2">pdf</a></div>' for i in range(2))
    pages = "".join(f'<li><a href="{BASE}/Lois?page={k}">{k + 1}</a></li>' for k in range(0, 3) if k != n)
    return f"<html><body><main>{pdfs}<ul>{pages}</ul></main></body></html>"


def _handler(calls):
    def h(req: httpx.Request) -> httpx.Response:
        calls.append(str(req.url))
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if req.url.path == "/Lois":
            n = int(req.url.params.get("page", 0))
            return httpx.Response(200, headers={"content-type": "text/html"}, text=_list_page(n))
        return httpx.Response(200, headers={"content-type": "application/pdf"}, content=b"%PDF-fake")
    return h


def test_crawl_pagination_and_resume(tmp_path, monkeypatch):
    law = "Article 1 " + "texte de loi " * 60 + "\nArticle 2 suite " * 5
    monkeypatch.setattr(ls, "extract_text",   # seuls les PDF contiennent des articles, pas les pages de liste
                        lambda r: ("JO", law) if str(r.url).endswith(".pdf") else ("", ""))
    src = ls.Source("jo", "Journal Officiel", "loi", [BASE + "/Lois"], r"\.pdf($|\?)")
    calls: list[str] = []
    client = httpx.Client(transport=httpx.MockTransport(_handler(calls)), follow_redirects=True,
                          headers={"User-Agent": "t"})
    f = ls.Fetcher(client=client, delay=0)
    rep = ls.run(tmp_path, [src], max_pages=50, fetcher=f)["sources"]["jo"]
    pdf_calls = [c for c in calls if c.endswith(".pdf")]
    assert rep["new"] == 6, rep                      # 3 pages de liste x 2 PDF, #page=N ignoré
    assert len(set(pdf_calls)) == 6 and all("#" not in c for c in pdf_calls)
    assert any("page=2" in c for c in calls)         # la pagination est suivie

    calls.clear()                                    # 2e passe : tout est déjà en base
    f2 = ls.Fetcher(client=httpx.Client(transport=httpx.MockTransport(_handler(calls)), headers={"User-Agent": "t"}), delay=0)
    rep2 = ls.run(tmp_path, [src], max_pages=50, fetcher=f2)["sources"]["jo"]
    assert rep2["new"] == 0 and rep2["unchanged"] == 6
    assert not [c for c in calls if c.endswith(".pdf")]  # aucun PDF retéléchargé
