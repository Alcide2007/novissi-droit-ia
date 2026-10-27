"""Découpage d'un texte en articles (avec numéro de page) ou en groupes de paragraphes (analyses).

Le texte extrait d'un PDF sépare les pages par « \\f\\n » : le numéro de page d'un article est donc le nombre de « \\f »
avant son début, plus un.
"""
from __future__ import annotations

import re

# « Article 1er », « Article premier », « Article 12 », « Article 12 bis », « Art. 5 »
ARTICLE_RE = re.compile(
    r"^[ \t]*(?:Article|ARTICLE|Art\.)\s+(premier|1er|\d+(?:[ \t]*(?:bis|ter|quater))?)\b[ \t]*[:.\-–]?[ \t]*", re.M)


def _clean(s: str) -> str:
    return re.sub(r"[ \t]*\f[ \t]*", " ", s).strip()


def split_articles(text: str) -> list[tuple[str, str, int | None]]:
    """[(« Article 12 bis », contenu, page)] dans l'ordre du texte. Les articles vides sont ignorés."""
    if not text:
        return []
    found = list(ARTICLE_RE.finditer(text))
    out: list[tuple[str, str, int | None]] = []
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        num = re.sub(r"\s+", " ", m.group(1).strip().lower())
        num = "1" if num in ("premier", "1er") else num
        content = _clean(text[m.end():end])
        if content:
            out.append((f"Article {num}", content, text.count("\f", 0, m.start()) + 1))
    return out


def split_paragraphs(text: str, size: int = 700) -> list[tuple[str, str, int | None]]:
    """Analyses : paragraphes regroupés jusqu'à ~size caractères."""
    out: list[tuple[str, str, int | None]] = []
    buf, page_of_buf = "", None
    pos = 0
    for para in re.split(r"\n\s*\n", text):
        page = text.count("\f", 0, pos) + 1
        pos += len(para) + 2
        para = _clean(para)
        if not para:
            continue
        if buf and len(buf) + len(para) > size:
            out.append((f"Analyse §{len(out) + 1}", buf, page_of_buf))
            buf = ""
        if not buf:
            page_of_buf = page
        buf = f"{buf}\n{para}".strip()
    if buf:
        out.append((f"Analyse §{len(out) + 1}", buf, page_of_buf))
    return out


def split_by_kind(text: str, kind: str) -> list[tuple[str, str, int | None]]:
    return split_paragraphs(text) if kind == "analyse" else split_articles(text)
