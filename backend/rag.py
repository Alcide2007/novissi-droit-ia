"""Index juridique : lecture des textes, découpage en extraits, recherche, rechargement à chaud.

Format d'un fichier de data/laws/*.txt :
    # source: Journal Officiel de la République Togolaise
    # kind: loi            (loi | decret | analyse)
    # url: https://...
    # title: ...
    <texte ; chaque article commence une ligne par « Article 12. »>
"""
from __future__ import annotations

import pathlib
import os
import re
import threading

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MAX_INPUT = 6000
CITE_RE = re.compile(r"\[(\d+)\]")
HEADER_RE = re.compile(r"^#\s*([A-Za-z_][A-Za-z_0-9]*)\s*:\s*(.*)$")
ART_RE = re.compile(
    r"^(Article\s+(?:\d+[a-z]*(?:[-.]\d+)*|premier|1er))\s*[.:\-–]?\s*", re.I | re.M)
STOP = ["le", "la", "les", "un", "une", "des", "de", "du", "et", "en", "à", "au", "aux",
        "mon", "ma", "mes", "je", "il", "elle", "est", "que", "qui", "pour", "par", "sur",
        "dans", "ce", "se", "ne", "pas", "ou", "d", "l", "qu", "peut", "doit"]


# ---------- garde-fous ----------
def clean_user_text(text: str) -> str:
    """Retire les balises et coupe la longueur : le texte utilisateur reste une donnée."""
    text = re.sub(r"[<>]", " ", text or "")
    return text.strip()[:MAX_INPUT]


def extract_citations(answer: str) -> set[str]:
    return set(CITE_RE.findall(answer))


def citations_valid(answer: str, allowed_ids: set[str]) -> bool:
    """Vrai seulement si au moins une référence existe et si toutes sont dans les extraits fournis."""
    cited = extract_citations(answer)
    return bool(cited) and cited <= allowed_ids


# ---------- lecture des documents ----------
def parse_document(path: pathlib.Path) -> tuple[dict, str]:
    """Sépare l'en-tête (# clé: valeur) du corps."""
    meta: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines) and (HEADER_RE.match(lines[i]) or not lines[i].strip()):
        m = HEADER_RE.match(lines[i])
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
        i += 1
    return meta, "\n".join(lines[i:])


def split_articles(body: str) -> list[tuple[str, str]]:
    parts = ART_RE.split(body)
    return [(parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts) - 1, 2)]


def split_paragraphs(body: str, size: int = 700) -> list[tuple[str, str]]:
    """Analyses : paragraphes regroupés jusqu'à ~size caractères."""
    out, buf = [], ""
    for para in [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]:
        if buf and len(buf) + len(para) > size:
            out.append(buf)
            buf = ""
        buf = f"{buf}\n{para}".strip()
    if buf:
        out.append(buf)
    return [(f"Analyse §{n}", t) for n, t in enumerate(out, 1)]


def _is_demo(f: pathlib.Path, meta: dict) -> bool:
    return f.name.upper().startswith("EXEMPLE_FICTIF") or meta.get("demo", "").lower() == "true" \
        or meta.get("scope", "") == "demo"


def load_chunks(law_dir: pathlib.Path, skip_derived: bool = False) -> list[dict]:
    """Un extrait = un article (lois) ou un groupe de paragraphes (analyses).

    Les fichiers EXEMPLE_FICTIF_* sont marqués « demo ». Les fichiers exportés par le collecteur portent un
    « version_id » (export dérivé du registre) : ils sont ignorés quand l'index lit déjà le registre (skip_derived)."""
    chunks: list[dict] = []
    for f in sorted(pathlib.Path(law_dir).glob("*.txt")):
        meta, body = parse_document(f)
        if skip_derived and meta.get("version_id"):
            continue
        kind = meta.get("kind", "loi").lower()
        demo = _is_demo(f, meta)
        pieces = split_paragraphs(body) if kind == "analyse" else split_articles(body)
        for label, text in pieces:
            chunks.append({"id": len(chunks) + 1, "source": meta.get("source", f.stem),
                           "kind": kind, "url": meta.get("url", ""),
                           "article": label, "content": text, "demo": demo,
                           "scope": "demo" if demo else meta.get("scope", "national"),
                           "resource_id": int(meta["resource_id"]) if meta.get("resource_id", "").isdigit() else None,
                           "version_id": int(meta["version_id"]) if meta.get("version_id", "").isdigit() else None,
                           "sha256": meta.get("sha256"), "page": None, "collected": meta.get("fetched"),
                           "reference": None, "verified": False})
    return chunks


def registry_chunks(registry) -> list[dict]:
    """Articles des versions COURANTES du registre, avec provenance (ressource, version, empreinte, page)."""
    return [{"id": 0, "source": r["source"], "kind": r["kind"], "url": r["url"], "article": r["label"],
             "content": r["content"], "demo": False, "scope": r["scope"], "resource_id": r["resource_id"],
             "version_id": r["version_id"], "sha256": r["sha256"], "page": r["page"],
             "collected": (r["collected_at"] or "")[:10], "reference": r["reference"], "verified": False}
            for r in registry.chunks()]


# ---------- recherche ----------
class Retriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                                   strip_accents="unicode", stop_words=STOP)
        self.matrix = self.vec.fit_transform(
            [f"{c['article']} {c['content']}" for c in chunks]) if chunks else None

    def search(self, query: str, k: int = 4) -> list[dict]:
        if not self.chunks or not query.strip():
            return []
        sims = cosine_similarity(self.vec.transform([query]), self.matrix)[0]
        best = sims.argsort()[::-1][:k]
        return [{**self.chunks[i], "score": float(sims[i])} for i in best if sims[i] > 0]


class LiveIndex:
    """Index remplaçable à chaud : le nouvel index est construit à côté puis échangé d'un coup.
    Les requêtes en cours continuent donc sur l'ancien index (pas d'interruption de service).

    Source du corpus : le registre documentaire (si fourni) + les fichiers de law_dir sans provenance de registre.
    Textes de démonstration (EXEMPLE_FICTIF_*) : DEMO_MODE=auto (défaut) = utilisés SEULEMENT si aucun texte officiel
    n'est disponible ; on = toujours ; off = jamais. Le mode courant est exposé (« officiel », « demonstration », « mixte »)."""

    def __init__(self, law_dir: pathlib.Path, registry=None, demo_mode: str | None = None, catalog=None):
        self.law_dir = pathlib.Path(law_dir)
        self.registry = registry
        self.catalog = catalog
        self.demo_mode = (demo_mode or os.getenv("DEMO_MODE", "auto")).lower()
        self._lock = threading.Lock()
        self.mode = "officiel"
        self._retriever = self._build()

    def _build(self) -> Retriever:
        official: list[dict] = []
        demo: list[dict] = []
        if self.catalog is not None:
            official += self.catalog.chunks()
        elif self.registry is not None:
            official += registry_chunks(self.registry)
        for c in load_chunks(self.law_dir, skip_derived=self.registry is not None or self.catalog is not None):
            (demo if c["demo"] else official).append(c)
        use_demo = self.demo_mode == "on" or (self.demo_mode == "auto" and not official)
        chunks = official + (demo if use_demo else [])
        for i, c in enumerate(chunks, 1):
            c["id"] = i
        self.mode = "demonstration" if chunks and not official else ("mixte" if use_demo and demo and official else "officiel")
        return Retriever(chunks)

    def reload(self) -> int:
        fresh = self._build()
        with self._lock:
            self._retriever = fresh
        return len(fresh.chunks)

    @property
    def chunks(self) -> list[dict]:
        return self._retriever.chunks

    def search(self, query: str, k: int = 4) -> list[dict]:
        return self._retriever.search(query, k)

    def stats(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.chunks:
            out[c["kind"]] = out.get(c["kind"], 0) + 1
        return out
