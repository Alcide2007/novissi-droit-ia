"""Collecte des textes juridiques togolais, avec registre documentaire, versions et reprise.

Principes :
- chaque ressource découverte est enregistrée AVANT téléchargement (registry.py) avec un statut explicite :
  discovered, archived, retry, review, unreachable, non_document, inspected, quarantine ;
- les fichiers originaux sont conservés, nommés par leur empreinte SHA-256 (jamais par leur nom de fichier) ;
- un contenu modifié crée une NOUVELLE version ; l'ancienne reste archivée ; un fichier corrompu ne remplace jamais une version valide ;
- une erreur temporaire (délai, 429, 5xx) met la ressource en « retry » avec échéance : jamais une suppression ;
- relancer le programme reprend la file (ressources découvertes, à réessayer, à recontrôler) ;
- robots.txt respecté, délai par hôte, backoff exponentiel avec jitter, identification claire (User-Agent + contact) ;
- jamais d'exception vers l'API : une panne produit un rapport d'erreurs et l'index existant reste servi.

Un connecteur par site (JournalOfficialConnector, LQDDConnector, OTRConnector) : chacun peut décrire ses liens
(titre, référence, date) selon la structure de SON site. Les motifs de liens se règlent par variables d'environnement
et DOIVENT être vérifiés sur le site réel (voir diagnose). Vérifiez aussi les conditions de réutilisation de chaque source.

Usage local :  python legal_scraper.py --once      |      python legal_scraper.py --report
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import os
import pathlib
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from .registry import Registry
from .splitter import split_by_kind

log = logging.getLogger("novissi.scraper")

ARTICLE_START = re.compile(r"^Article\s+(?:\d+|premier|1er)\b", re.M)
MIN_CHARS = 400


@dataclass
class Source:
    key: str            # « jo », « lqd », « otr » : identifiant stable de la source
    name: str           # nom affiché comme source
    kind: str           # « loi » | « decret » | « analyse »
    seeds: list[str]
    link_re: str
    max_chars: int = int(os.getenv("SCRAPER_MAX_CHARS", "600000"))
    hosts: set[str] = field(default_factory=set)
    scope: str = "national"   # « national » | « regional » | « international » | « demo »

    def __post_init__(self) -> None:
        self.hosts = {urlparse(s).netloc for s in self.seeds}

    def describe_links(self, html: str, base_url: str) -> dict[str, dict]:
        """Métadonnées par lien découvert (titre, référence, type, date). Spécifique à chaque site : vide par défaut."""
        return {}


_JO_REF = re.compile(
    r"\b(LOI ORGANIQUE|LOI CONSTITUTIONNELLE|LOI|ORDONNANCE|D[ÉE]CRET|ARR[ÊE]T[ÉE])\s+(?:N[°o]\s*)?(\d{4}\s*-\s*\d+)\s+(\d{2}/\d{2}/\d{4})",
    re.I)


class JournalOfficialConnector(Source):
    """jo.gouv.tg : listes paginées (?page=N). Chaque entrée affiche « LOI 2025-006 14/04/2025 », un intitulé
    et un lien PDF (le PDF est un numéro du Journal officiel qui peut contenir plusieurs textes).
    L'extraction de métadonnées est heuristique : un lien n'est décrit que si son bloc ne contient qu'UN seul PDF."""

    def describe_links(self, html: str, base_url: str) -> dict[str, dict]:
        soup = BeautifulSoup(html, "html.parser")
        out: dict[str, dict] = {}
        for a in soup.find_all("a", href=True):
            u = urljoin(base_url, a["href"]).split("#")[0]
            if not u.lower().split("?")[0].endswith(".pdf") or u in out:
                continue
            node = a
            for _ in range(4):
                node = node.parent
                if node is None:
                    break
                pdfs = [x for x in node.find_all("a", href=True)
                        if x["href"].split("#")[0].lower().split("?")[0].endswith(".pdf")]
                if len(pdfs) != 1:
                    break
                text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
                m = _JO_REF.search(text)
                if m:
                    d, mo, y = m.group(3).split("/")
                    number = re.sub(r"\s+", "", m.group(2))          # hors f-string : compatible Python 3.10/3.11
                    out[u] = {"reference": f"{m.group(1).upper()} {number}",
                              "text_type": m.group(1).lower(), "doc_date": f"{y}-{mo}-{d}",
                              "title": text[m.end():].strip(" -–:")[:200] or None}
                    break
        return out


class LQDDConnector(Source):
    """lqdd.org : catalogue complémentaire (codes, analyses). Pages HTML ou PDF ; source non officielle."""


class OTRConnector(Source):
    """otr.tg (Joomla) : avis fonciers. Les téléchargements sont souvent servis en « …/file.html » ou « …/file »."""


def _csv(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def default_sources() -> list[Source]:
    sources: list[Source] = []
    jo = os.getenv("JO_BASE_URL", "https://jo.gouv.tg").rstrip("/")
    if jo:
        sources.append(JournalOfficialConnector(
            "jo", "Journal Officiel de la République Togolaise", "loi",
            _csv(os.getenv("JO_SEEDS")) or [jo + "/Lois"],
            os.getenv("JO_LINK_PATTERN") or r"\.pdf($|\?)|/(textes?|lois?|decrets?|codes?)/"))
    lqd = os.getenv("LQD_BASE_URL", "https://www.lqdd.org/textes-de-loi").rstrip("/")
    if lqd:
        sources.append(LQDDConnector(
            "lqd", "La Question de Droit", "analyse",
            _csv(os.getenv("LQD_SEEDS")) or [lqd + "/"],
            os.getenv("LQD_LINK_PATTERN") or r"/\d{4}/|/textes-de-loi/|/articles?/|/analyses?/|/lois?/|/codes?/|/decrets?/|\.pdf($|\?)"))
    otr = os.getenv("OTR_BASE_URL", "").rstrip("/")   # inactif tant que l'adresse n'est pas confirmée avec diagnose.sh
    if otr:
        sources.append(OTRConnector(
            "otr", "OTR : avis fonciers", "loi",
            _csv(os.getenv("OTR_SEEDS")) or [otr + "/"],
            os.getenv("OTR_LINK_PATTERN") or r"\.pdf($|\?)|/file(\.html)?($|\?)"))
    return sources


class Fetcher:
    """Client HTTP poli : robots.txt, délai par hôte, délai d'attente, jamais d'exception."""

    def __init__(self, client: httpx.Client | None = None, delay: float | None = None, backoff: float | None = None):
        contact = os.getenv("SCRAPER_CONTACT", "contact@exemple.tg").encode("ascii", "ignore").decode()
        self.client = client or httpx.Client(
            timeout=httpx.Timeout(60.0, connect=25.0), follow_redirects=True,
            headers={"User-Agent": f"NovissiDroitBot/0.1 (projet etudiant; {contact})"})
        self.delay = float(os.getenv("SCRAPER_DELAY_SECONDS", "1.5")) if delay is None else delay
        # backoff exponentiel (secondes) ; nul si le délai est nul (tests, exécution rapide)
        self.backoff = (float(os.getenv("SCRAPER_BACKOFF_SECONDS", "2")) if self.delay > 0 else 0.0) if backoff is None else backoff
        self._robots: dict[str, robotparser.RobotFileParser | None] = {}
        self._last: dict[str, float] = {}

    def _wait(self, host: str) -> None:
        wait = self._last.get(host, 0) + self.delay - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last[host] = time.monotonic()

    def _load_robots(self, url: str) -> robotparser.RobotFileParser | None:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base in self._robots:
            return self._robots[base]
        rp: robotparser.RobotFileParser | None = robotparser.RobotFileParser()
        try:
            self._wait(p.netloc)
            r = self.client.get(base + "/robots.txt")
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
            elif 400 <= r.status_code < 500:
                rp.parse([])          # pas de robots.txt : tout est permis
            else:
                rp = None             # serveur en erreur : on s'abstient
        except httpx.HTTPError:
            rp = None
        self._robots[base] = rp
        return rp

    def allowed(self, url: str) -> bool:
        rp = self._load_robots(url)
        return bool(rp and rp.can_fetch(self.client.headers.get("User-Agent", "*"), url))

    def _sleep_backoff(self, attempt: int, retry_after: str | None = None) -> None:
        if self.backoff <= 0:
            return
        pause = min(60.0, self.backoff * 2 ** (attempt - 1)) * (0.5 + random.random())   # exponentiel + jitter
        if retry_after and retry_after.isdigit():
            pause = max(pause, min(120.0, float(retry_after)))
        time.sleep(pause)

    def fetch(self, url: str, etag: str | None = None, last_modified: str | None = None) -> "Fetched":
        """Télécharge avec 3 essais. Distingue erreur temporaire (réessayer plus tard) et permanente."""
        headers = {}
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified
        for attempt in (1, 2, 3):
            try:
                self._wait(urlparse(url).netloc)
                r = self.client.get(url, headers=headers or None)
            except httpx.TransportError as e:   # délai dépassé, connexion coupée, téléchargement interrompu
                if attempt == 3:
                    log.warning("Échec %s : %s", url, type(e).__name__)
                    return Fetched(error=type(e).__name__, transient=True)
                self._sleep_backoff(attempt)
                continue
            if r.status_code == 304:
                return Fetched(resp=r, status=304, not_modified=True)
            if r.status_code in (429, 500, 502, 503, 504):
                if attempt == 3:
                    return Fetched(status=r.status_code, transient=True, error=f"HTTP {r.status_code}")
                self._sleep_backoff(attempt, r.headers.get("retry-after"))
                continue
            if r.status_code >= 400:
                log.warning("Échec %s : HTTP %s", url, r.status_code)
                return Fetched(status=r.status_code, error=f"HTTP {r.status_code}")
            return Fetched(resp=r, status=r.status_code)
        return Fetched(error="unknown", transient=True)

    def get(self, url: str) -> httpx.Response | None:
        return self.fetch(url).resp


@dataclass
class Fetched:
    resp: httpx.Response | None = None
    status: int | None = None
    transient: bool = False
    not_modified: bool = False
    error: str | None = None


# ---------- extraction ----------
def _clean(text: str) -> str:
    lines = [re.sub(r"[ \t\u00a0]+", " ", ln).strip() for ln in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def normalize_articles(text: str) -> str:
    """Remet chaque « Article N » au début d'une ligne pour que rag.py découpe correctement."""
    return re.sub(r"(?<=[.;:!?])[ \t]+(?=Article\s+(?:\d+|premier|1er)\b)", "\n", text)


def extract_text(resp: httpx.Response) -> tuple[str, str]:
    """Retourne (titre, texte) pour une page HTML ou un PDF. Dans un PDF, les pages sont séparées par « \\f\\n »."""
    ctype = resp.headers.get("content-type", "").lower()
    if "pdf" in ctype or str(resp.url).lower().split("?")[0].endswith(".pdf") or resp.content[:5] == b"%PDF-":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(resp.content))
        pages = [_clean(pg.extract_text() or "") for pg in reader.pages]
        text = normalize_articles("\f\n".join(pages))

        # Beaucoup de journaux anciens sont des scans. Ne lancer l'OCR que si le
        # texte natif est absent ou ne contient aucun article détectable.
        ocr_enabled = os.getenv("PDF_OCR_ENABLED", "1") == "1"
        needs_ocr = len(text) < MIN_CHARS or not ARTICLE_START.search(text)
        if ocr_enabled and needs_ocr:
            try:
                import fitz  # PyMuPDF, rendu page par page
                import pytesseract
                from PIL import Image
                max_pages = max(1, int(os.getenv("PDF_OCR_MAX_PAGES", "80")))
                ocr_pages = []
                with fitz.open(stream=resp.content, filetype="pdf") as pdf:
                    for page in list(pdf)[:max_pages]:
                        pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
                        image = Image.open(io.BytesIO(pix.tobytes("png")))
                        try:
                            page_text = pytesseract.image_to_string(image, lang=os.getenv("TESSERACT_LANG", "fra+eng"))
                        except Exception:
                            # Le pack fra peut ne pas être installé : tenter l'anglais en second recours.
                            page_text = pytesseract.image_to_string(image, lang="eng")
                        ocr_pages.append(_clean(page_text))
                ocr_text = normalize_articles("\f\n".join(ocr_pages))
                if len(ocr_text) > len(text) and ARTICLE_START.search(ocr_text):
                    text = ocr_text
            except Exception as exc:
                # OCR facultatif : conserver le texte natif et laisser le registre
                # classer le document « review » plutôt que perdre le PDF original.
                log.info("OCR indisponible pour %s (%s)", str(resp.url), type(exc).__name__)

        first = next((ln for ln in text.splitlines() if ln.strip()), "")
        return first[:120], text
    soup = BeautifulSoup(resp.text, "html.parser")
    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
        tag.decompose()
    root = soup.find("article") or soup.find("main") or soup.body or soup
    return title, normalize_articles(_clean(root.get_text("\n")))


def discover_links(html: str, base_url: str, src: Source) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    out: list[str] = []
    for a in soup.find_all("a", href=True):
        u = urljoin(base_url, a["href"]).split("#")[0]
        if urlparse(u).netloc in src.hosts and re.search(src.link_re, u, re.I) and u not in out:
            out.append(u)
    return out


_PAGE_PARAM = re.compile(r"(?:^|[?&])(?:page|paged|p|pg|start|offset)=\d+", re.I)


def discover_pagination(html: str, base_url: str, src: Source) -> list[str]:
    """Liens « page suivante / page N » d'une liste : même site, même chemin, paramètre de page dans l'URL."""
    soup = BeautifulSoup(html, "html.parser")
    base_path = urlparse(base_url).path
    out: list[str] = []
    for a in soup.find_all("a", href=True):
        u = urljoin(base_url, a["href"]).split("#")[0]
        pu = urlparse(u)
        if (pu.netloc in src.hosts and pu.path == base_path and _PAGE_PARAM.search(pu.query)
                and u not in out):
            out.append(u)
    return out


# ---------- stockage ----------
def _slug(title: str, url: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", (title or urlparse(url).path).lower()).strip("-")[:50] or "doc"
    return f"{base}-{hashlib.sha1(url.encode()).hexdigest()[:8]}"


def save_document(law_dir: pathlib.Path, src: Source, url: str, title: str, text: str, prov: dict | None = None) -> str:
    """Écrit l'export TEXTE dérivé (data/laws/…txt), régénérable depuis le registre. Retourne « new », « updated » ou « unchanged »."""
    law_dir = pathlib.Path(law_dir)
    law_dir.mkdir(parents=True, exist_ok=True)
    body = text[: src.max_chars].replace("\f", "")
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    idx_path = law_dir / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8")) if idx_path.exists() else {}
    name = f"{src.key}__{_slug(title, url)}.txt"
    old = index.get(name)
    if old and old.get("sha256") == digest and (law_dir / name).exists():
        return "unchanged"
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = (f"# source: {src.name}\n# kind: {src.kind}\n# url: {url}\n"
              f"# title: {title.replace(chr(10), ' ')[:150]}\n# fetched: {fetched}\n# scope: {src.scope}\n"
              + "".join(f"# {k}: {v}\n" for k, v in (prov or {}).items()) + "\n")
    (law_dir / name).write_text(header + body, encoding="utf-8")
    index[name] = {"url": url, "source": src.name, "kind": src.kind, "title": title,
                   "sha256": digest, "fetched": fetched}
    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    return "updated" if old else "new"


def _known_urls(law_dir: pathlib.Path) -> set[str]:
    """URL déjà enregistrées (fichier présent) : sert à reprendre un crawl interrompu."""
    idx = pathlib.Path(law_dir) / "index.json"
    if not idx.exists():
        return set()
    try:
        data = json.loads(idx.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {v["url"] for n, v in data.items() if (pathlib.Path(law_dir) / n).exists() and "url" in v}


# ---------- exécution ----------
def _event(event: str, **kv: object) -> None:
    """Journal structuré (une ligne JSON par événement)."""
    log.info(json.dumps({"event": event, **kv}, ensure_ascii=False, default=str))


def _recheck_days() -> float | None:
    """Âge (jours) au-delà duquel un document archivé est recontrôlé. SCRAPER_REFETCH=1 : à chaque passe. Vide : jamais."""
    if os.getenv("SCRAPER_REFETCH") == "1":
        return 0.0
    v = os.getenv("SCRAPER_RECHECK_DAYS", "7").strip()
    return float(v) if v else None


def store_original(originals: pathlib.Path, sha: str, content: bytes, ext: str) -> str:
    """Conserve le fichier original sous son empreinte (adressage par contenu). Retourne un chemin RELATIF."""
    d = pathlib.Path(originals) / sha[:2]
    d.mkdir(parents=True, exist_ok=True)
    final = d / f"{sha}.{ext}"
    if not final.exists():
        tmp = final.with_suffix(final.suffix + ".part")
        tmp.write_bytes(content)
        tmp.replace(final)               # écriture atomique : jamais de fichier partiel sous le bon nom
    return f"{sha[:2]}/{sha}.{ext}"


def _is_listing_candidate(is_seed: bool, is_html: bool) -> bool:
    return is_seed and is_html


def _crawl_source(src: Source, reg: Registry, fetcher: Fetcher, st: dict, run_id: int, law_dir: pathlib.Path,
                  originals: pathlib.Path, max_pages: int) -> None:
    recheck_days = _recheck_days()
    for u in src.seeds:
        reg.discover(src.key, u, None, kind="listing")
    queue: list[tuple[str, bool]] = [(u, True) for u in src.seeds]
    queue += [(r["url"], False) for r in reg.pending(src.key)]                       # reprise après interruption
    due = {r["url"] for r in reg.due_for_recheck(src.key, recheck_days)} if recheck_days is not None else set()
    queue += [(u, False) for u in sorted(due)]                                        # recontrôle des documents connus
    seen: set[str] = set()
    while queue and st["fetched"] < max_pages:
        url, is_seed = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        res = reg.resource(url)
        if not is_seed and res and res["status"] in ("archived", "unreachable", "non_document", "quarantine", "review") \
                and url not in due:
            st["unchanged"] += 1                      # déjà traité : pas de retéléchargement inutile
            continue
        if not fetcher.allowed(url):
            st["skipped_robots"] += 1
            if res and not is_seed:
                reg.mark(res["id"], "review", error="interdit par robots.txt")
            continue
        rid = res["id"] if res else reg.discover(src.key, url, None)[0]
        use_cond = url in due and res
        fr = fetcher.fetch(url, etag=res["etag"] if use_cond else None, last_modified=res["last_modified"] if use_cond else None)
        if fr.not_modified:
            st["fetched"] += 1
            st["unchanged"] += 1
            reg.mark(rid, "archived", http_status=304)
            continue
        if fr.resp is None:
            st["errors"] += 1
            attempts = (res or {}).get("attempts", 0)
            if fr.transient:       # temporaire : on réessaiera (échéance croissante), jamais de suppression
                reg.mark(rid, "retry", error=fr.error, increment_attempts=True, retry_in_minutes=min(1440, 15 * 2 ** attempts),
                         http_status=fr.status)
            else:
                reg.mark(rid, "unreachable", error=fr.error, http_status=fr.status)
            reg.log_error(run_id, rid, url, "transient" if fr.transient else "permanent", fr.error or "")
            _event("fetch_error", source=src.key, url=url, transient=fr.transient, error=fr.error)
            continue
        resp = fr.resp
        st["fetched"] += 1
        if urlparse(str(resp.url)).netloc not in src.hosts:    # garde SSRF : une redirection ne sort jamais du domaine autorisé
            st["errors"] += 1
            reg.mark(rid, "non_document", error="redirection hors du domaine autorisé")
            reg.log_error(run_id, rid, url, "ssrf_guard", f"redirigé vers {urlparse(str(resp.url)).netloc}")
            continue
        content = resp.content
        ctype = resp.headers.get("content-type", "").split(";")[0].strip().lower()
        meta = dict(http_status=resp.status_code, etag=resp.headers.get("etag"),
                    last_modified=resp.headers.get("last-modified"), content_type=ctype, size=len(content))
        is_html = "html" in ctype
        try:
            if _is_listing_candidate(is_seed, is_html):  # page de liste : on enregistre les liens AVANT de les télécharger
                reg.mark(rid, "inspected", **meta)
                described = src.describe_links(resp.text, url)
                for u in discover_links(resp.text, url, src):
                    if u not in seen:
                        reg.discover(src.key, u, url, **described.get(u, {}))
                        queue.append((u, False))
                for u in discover_pagination(resp.text, url, src):
                    if u not in seen:
                        reg.discover(src.key, u, url, kind="listing")
                        queue.append((u, True))
            sha = hashlib.sha256(content).hexdigest()
            looks_pdf = "pdf" in ctype or url.lower().split("?")[0].endswith(".pdf") or content[:5] == b"%PDF-"
            if looks_pdf and not content.startswith(b"%PDF"):
                st["skipped_empty"] += 1
                reg.mark(rid, "non_document", error="annoncé comme PDF mais autre contenu", **meta)
                reg.log_error(run_id, rid, url, "non_document", "faux PDF")
                continue
            ext = "pdf" if looks_pdf else "html"
            has_good = reg.has_good_version(rid)
            try:
                title, text = extract_text(resp)
            except Exception as e:            # PDF corrompu, HTML inattendu : quarantaine, l'original est conservé
                st["errors"] += 1
                reg.log_error(run_id, rid, url, "extraction", type(e).__name__)
                _event("extraction_failed", source=src.key, url=url, error=type(e).__name__)
                if not has_good:               # on ne remplace jamais une version valide par un fichier corrompu
                    path = store_original(originals, sha, content, ext)
                    reg.add_version(rid, sha, file_path=path, size=len(content), content_type=ctype, pages=None, chars=0,
                                    extraction_status="failed", articles=[])
                    reg.mark(rid, "quarantine", error=type(e).__name__, **meta)
                continue
            articles = split_by_kind(text, src.kind)
            ok = len(text) >= MIN_CHARS and bool(articles) and (src.kind == "analyse" or ARTICLE_START.search(text))
            pages = text.count("\f") + 1 if looks_pdf else None
            if not ok:
                st["skipped_empty"] += 1
                if _is_listing_candidate(is_seed, is_html) or has_good:
                    continue                  # liste de liens, ou version valide déjà en base : rien à remplacer
                path = store_original(originals, sha, content, ext)
                reg.add_version(rid, sha, file_path=path, size=len(content), content_type=ctype, pages=pages, chars=len(text),
                                extraction_status="empty", articles=[])
                reg.mark(rid, "review", error="aucun article détecté (PDF scanné ? OCR à prévoir)", **meta)
                continue
            path = store_original(originals, sha, content, ext)
            change, vid = reg.add_version(rid, sha, file_path=path, size=len(content), content_type=ctype, pages=pages,
                                          chars=len(text), extraction_status="ok", articles=articles)
            reg.set_meta(rid, title=title or None)
            reg.mark(rid, "archived", **meta)
            st[{"new": "new", "changed": "updated", "unchanged": "unchanged"}[change]] += 1
            if change != "unchanged":
                save_document(law_dir, src, url, title, text,
                              prov={"resource_id": rid, "version_id": vid, "sha256": sha, "pages": pages or ""})
            _event("document", source=src.key, change=change, url=url, version=vid, articles=len(articles),
                   n=f"{st['fetched']}/{max_pages}")
        except Exception as e:                # filet de sécurité : une ressource défaillante n'arrête pas la collecte
            st["errors"] += 1
            reg.log_error(run_id, rid, url, "unexpected", type(e).__name__)
            _event("unexpected_error", source=src.key, url=url, error=type(e).__name__)


def run(law_dir: pathlib.Path, sources: list[Source] | None = None, max_pages: int | None = None,
        fetcher: Fetcher | None = None, registry: Registry | None = None,
        originals_dir: pathlib.Path | None = None) -> dict:
    """Parcourt les sources. Ne lève jamais d'exception réseau : renvoie un rapport (et le consigne dans le registre)."""
    law_dir = pathlib.Path(law_dir)
    sources = default_sources() if sources is None else sources
    max_pages = int(os.getenv("SCRAPER_MAX_PAGES", "30")) if max_pages is None else max_pages
    fetcher = fetcher or Fetcher()
    reg = registry or Registry(law_dir / "registry.db")
    originals = pathlib.Path(originals_dir) if originals_dir else law_dir / "originals"
    report: dict = {"started": datetime.now(timezone.utc).isoformat(timespec="seconds"), "sources": {}}
    for src in sources:
        st = {"fetched": 0, "new": 0, "updated": 0, "unchanged": 0,
              "skipped_robots": 0, "skipped_empty": 0, "errors": 0}
        report["sources"][src.key] = st
        base = f"https://{sorted(src.hosts)[0]}" if src.hosts else ""
        reg.source(src.key, src.name, base, src.scope, src.kind)
        run_id = reg.start_run(src.key)
        try:
            _crawl_source(src, reg, fetcher, st, run_id, law_dir, originals, max_pages)
            reg.finish_run(run_id, st)
        except Exception as e:                 # jamais d'exception vers l'appelant
            st["errors"] += 1
            reg.log_error(run_id, None, "", "crash", type(e).__name__)
            reg.finish_run(run_id, st, "failed")
    report["finished"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return report


def diagnose(url: str) -> None:
    """Explique pourquoi une page ne donne rien : accès, robots.txt, type, liens, texte, articles."""
    f = Fetcher(delay=0)
    print(f"URL testée : {url}")
    try:
        r = f.client.get(url)
    except httpx.HTTPError as e:
        print(f"  ECHEC RESEAU : {type(e).__name__} -> le site est injoignable depuis cette machine "
              "(DNS, pare-feu, site en panne ou adresse incorrecte).")
        return
    print(f"  Statut HTTP : {r.status_code}  | URL finale : {r.url}")
    ctype = r.headers.get("content-type", "?")
    print(f"  Type de contenu : {ctype}")
    print(f"  robots.txt autorise : {f.allowed(str(r.url))}")
    if r.status_code >= 400:
        print("  -> Le site refuse ou la page n'existe pas (403 = bloque les robots, 404 = mauvaise adresse).")
        return
    try:
        title, text = extract_text(r)
    except Exception as e:
        print(f"  Extraction impossible : {type(e).__name__}")
        return
    arts = len(ARTICLE_START.findall(text))
    print(f"  Titre : {title[:80]!r}")
    print(f"  Texte extrait : {len(text)} caracteres, {arts} « Article N » detectes (minimum requis : {MIN_CHARS} et 1 article)")
    if "html" in ctype.lower():
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            u = urljoin(str(r.url), a["href"]).split("#")[0]
            if u not in links:
                links.append(u)
        pdfs = [u for u in links if u.lower().split("?")[0].endswith(".pdf")]
        print(f"  Liens trouves : {len(links)} dont {len(pdfs)} PDF")
        for u in pdfs[:10]:
            print("    PDF :", u)
        host = urlparse(str(r.url)).netloc
        pages = [u for u in links if u not in pdfs and urlparse(u).netloc == host]
        print(f"  Pages internes (rubriques, pagination ?) : {len(pages)}")
        for u in pages[:20]:
            print("    PAGE :", u)
        if len(text) < 200 and len(links) < 5:
            print("  -> Page presque vide : le site charge probablement son contenu par JavaScript "
                  "(le scraper ne l'execute pas). Cherche une URL de PDF directe ou une API du site.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    try:  # lancé seul : lit le .env de la racine du projet
        from dotenv import load_dotenv
        load_dotenv(pathlib.Path(__file__).resolve().parent.parent / ".env")
    except ImportError:
        pass
    ap = argparse.ArgumentParser(description="Met à jour data/laws depuis les sources configurées")
    ap.add_argument("--once", action="store_true", help="une passe puis arrêt")
    ap.add_argument("--max-pages", type=int, default=None, help="plafond de pages/PDF téléchargés (défaut : .env)")
    ap.add_argument("--diagnose", metavar="URL", help="teste une URL et explique pourquoi elle donne (ou non) des textes")
    ap.add_argument("--report", action="store_true", help="affiche le rapport d'exhaustivité du registre")
    root = pathlib.Path(__file__).resolve().parent.parent
    data = pathlib.Path(os.getenv("DATA_DIR", root / "data"))
    ap.add_argument("--law-dir", default=str(data / "laws"))
    args = ap.parse_args()
    reg = Registry(data / "registry.db")
    if args.report:
        print(json.dumps(reg.report(), ensure_ascii=False, indent=2, default=str))
        raise SystemExit(0)
    if args.diagnose:
        diagnose(args.diagnose)
        raise SystemExit(0)
    print(json.dumps(run(pathlib.Path(args.law_dir), max_pages=args.max_pages, registry=reg, originals_dir=data / "originals"), ensure_ascii=False, indent=2))
