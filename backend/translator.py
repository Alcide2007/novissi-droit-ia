"""
Module de traduction & Pont Lexical (Français <-> Éwé / Kabiyè) — Zero-Dependency.
Traduit sans dépendance obligatoire à 'requests' et élimine les boucles de répétition.
"""
from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

try:
    import requests
except ImportError:
    requests = None  # type: ignore

log = logging.getLogger("novissi-translator")

# Glossaire de pont lexical : Langues locales -> Mots-clés juridiques français pour le RAG
LEXICAL_BRIDGE_TO_FR: dict[str, str] = {
    # Éwé
    "fetu": "salaire rémunération paiement employeur code du travail",
    "dɔwɔtɔ": "employeur patron contrat de travail licenciement",
    "dɔwɔla": "travailleur salarié employé",
    "xɔhaya": "loyer bail d'habitation locataire propriétaire caution",
    "aƒetɔ": "propriétaire bailleur expulsion préavis",
    "anyigba": "terrain parcelle foncier titre foncier cadastre OTR lotissement",
    "agbalẽ": "acte contrat document titre foncier",
    "fe": "dette créance remboursement mise en demeure",
    "ʋɔnudrɔ̃ƒe": "tribunal justice plainte procureur",
    # Kabiyè
    "liidiye": "salaire paiement caution argent dette",
    "tʊmɩyɛ": "travail emploi contrat licenciement code du travail",
    "ɖɩɣa": "logement maison bail loyer locataire propriétaire expulsion",
    "tɛtʊ": "terrain parcelle foncier titre foncier cadastre OTR",
    "takayaɣ": "acte contrat titre document",
    "kɩmɩyɛ": "dette créance remboursement",
    "tɔm": "litige plainte tribunal justice",
}


def dedupe_repetitions(text: str) -> str:
    """Supprime les boucles de répétition neuronale en Éwé et Kabiyè."""
    if not text:
        return text

    lines = text.split("\n")
    out_lines: list[str] = []

    for line in lines:
        words = line.split(" ")
        for _pass in range(3):
            for n in range(15, 0, -1):
                i = 0
                new_words: list[str] = []
                while i < len(words):
                    chunk = words[i : i + n]
                    if len(chunk) == n and i + 2 * n <= len(words):
                        reps = 1
                        chunk_lower = [w.lower() for w in chunk]
                        while (
                            i + (reps + 1) * n <= len(words)
                            and [w.lower() for w in words[i + reps * n : i + (reps + 1) * n]] == chunk_lower
                        ):
                            reps += 1
                        if (n >= 3 and reps >= 2) or (n < 3 and reps >= 3):
                            new_words.extend(chunk)
                            i += reps * n
                            rem = len(words) - i
                            if n >= 2 and 1 <= rem < n and [w.lower() for w in words[i : i + rem]] == chunk_lower[:rem]:
                                i += rem
                            continue
                    new_words.append(words[i])
                    i += 1
                words = new_words
        cleaned_line = " ".join(words)
        cleaned_line = re.sub(r"\b(\w+)(?:\s+\1){2,}\b", r"\1", cleaned_line, flags=re.IGNORECASE)
        out_lines.append(cleaned_line)

    return "\n".join(out_lines)


def _http_get_json(url: str, timeout: float = 6.0) -> Any:
    """Effectue une requête GET JSON sans dépendance externe obligatoire."""
    if httpx is not None:
        try:
            r = httpx.get(url, timeout=timeout)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass

    if requests is not None:
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        pass

    return None


def _gtx_translate_chunk(text: str, src: str = "fr", dest: str = "ee") -> str:
    """Traduit un segment court via Google GTX sans planter."""
    clean = text.strip()
    if not clean:
        return text
    try:
        url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl={src}&tl={dest}&dt=t&q={urllib.parse.quote(clean)}"
        )
        data = _http_get_json(url, timeout=6.0)
        if isinstance(data, list) and data and isinstance(data[0], list):
            out = "".join(seg[0] for seg in data[0] if seg and seg[0])
            return dedupe_repetitions(out)
    except Exception as exc:
        log.warning("Échec traduction GTX: %s", exc)
    return text


def enrich_query_for_rag(query: str, lang: str = "Français") -> str:
    """Convertit les questions en langues nationales en français pour le RAG."""
    if not query or lang == "Français":
        return query

    q_lower = query.lower()
    extra_keywords: list[str] = []
    for local_word, fr_terms in LEXICAL_BRIDGE_TO_FR.items():
        if local_word in q_lower:
            extra_keywords.append(fr_terms)

    translated_fr = ""
    if lang in ("Ewé", "Kabiyè"):
        src_code = "ee" if lang == "Ewé" else "auto"
        translated_fr = _gtx_translate_chunk(query, src=src_code, dest="fr")

    parts = [query]
    if translated_fr and translated_fr.lower() != q_lower:
        parts.append(translated_fr)
    if extra_keywords:
        parts.append(" ".join(extra_keywords))
    return " ".join(parts)


def translate_response(text_fr: str, lang: str = "Français") -> str:
    """Traduit et dé-boucle les réponses en Éwé ou Kabiyè."""
    if not text_fr or lang == "Français":
        return text_fr

    if lang == "Kabiyè":
        return dedupe_repetitions(text_fr)

    lines = text_fr.split("\n")
    translated_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            translated_lines.append("")
            continue

        prefix_match = re.match(r"^(\s*(?:[•\-*]|\d+\.|#{1,4})\s+)", line)
        prefix = prefix_match.group(1) if prefix_match else ""
        content = line[len(prefix) :] if prefix_match else line

        citations: list[str] = []
        def _save_cit(m: re.Match) -> str:
            citations.append(m.group(0))
            return f" __CIT{len(citations)-1}__ "

        content_no_cit = re.sub(r"\[\d+\]", _save_cit, content)
        had_bold = "**" in content_no_cit
        clean_content = content_no_cit.replace("**", "").strip()

        if any(ch in clean_content for ch in ("ɖ", "ƒ", "ɣ", "ʋ")):
            trans = dedupe_repetitions(clean_content)
        else:
            trans = _gtx_translate_chunk(clean_content, src="fr", dest="ee")
            trans = dedupe_repetitions(trans)

        for idx, cit in enumerate(citations):
            trans = re.sub(rf"\s*__CIT{idx}__\s*", f" {cit} ", trans, flags=re.IGNORECASE)

        trans = re.sub(r"\s{2,}", " ", trans).strip()
        if had_bold and ":" in trans:
            head, rest = trans.split(":", 1)
            trans = f"**{head.strip()} :** {rest.strip()}"

        translated_lines.append(f"{prefix}{trans}")

    return dedupe_repetitions("\n".join(translated_lines))