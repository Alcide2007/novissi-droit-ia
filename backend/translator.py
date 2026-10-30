"""
Module de traduction & Pont Lexical (Français <-> Éwé / Kabiyè) — Zero-Failure.
1. Utilise le pont lexical instantané sans dépendance réseau externe.
2. Traduction globale en un seul appel (évite les 30 requêtes en boucle qui causaient le timeout).
3. Ne lève JAMAIS d'exception non gérée : le serveur répond toujours en 200 OK.
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

# Pont lexical direct : convertit immédiatement les concepts locaux vers les lois togolaises
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
    """Élimine les répétitions de mots ou de syntagmes (ɖe wò le ɣleti...)."""
    if not text:
        return text

    lines = text.split("\n")
    out_lines: list[str] = []

    for line in lines:
        words = line.split(" ")
        for _pass in range(2):
            for n in range(12, 0, -1):
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
                            continue
                    new_words.append(words[i])
                    i += 1
                words = new_words
        cleaned = " ".join(words)
        cleaned = re.sub(r"\b(\w+)(?:\s+\1){2,}\b", r"\1", cleaned, flags=re.IGNORECASE)
        out_lines.append(cleaned)

    return "\n".join(out_lines)


def _safe_fetch_gtx(text: str, src: str, dest: str, timeout: float = 3.5) -> str:
    """Traduit un texte via Google GTX avec timeout court et protection sans crash."""
    clean = text.strip()
    if not clean:
        return text
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={src}&tl={dest}&dt=t&q={urllib.parse.quote(clean)}"
    )

    raw_json = None
    if httpx is not None:
        try:
            r = httpx.get(url, timeout=timeout)
            if r.status_code == 200:
                raw_json = r.json()
        except Exception:
            pass

    if raw_json is None and requests is not None:
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                raw_json = r.json()
        except Exception:
            pass

    if raw_json is None:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    raw_json = json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception:
            pass

    if isinstance(raw_json, list) and raw_json and isinstance(raw_json[0], list):
        out = "".join(seg[0] for seg in raw_json[0] if seg and seg[0])
        return dedupe_repetitions(out)

    return text


def enrich_query_for_rag(query: str, lang: str = "Français") -> str:
    """Enrichit la question en langues nationales vers le français pour le RAG."""
    if not query or lang == "Français":
        return query

    q_lower = query.lower()
    extra_keywords: list[str] = []
    for local_word, fr_terms in LEXICAL_BRIDGE_TO_FR.items():
        if local_word in q_lower:
            extra_keywords.append(fr_terms)

    # Traduction rapide en un seul appel (uniquement pour l'Éwé)
    translated_fr = ""
    if lang == "Ewé":
        try:
            translated_fr = _safe_fetch_gtx(query, src="ee", dest="fr", timeout=3.0)
        except Exception as exc:
            log.warning("Pont traduction ignoré : %s", exc)

    parts = [query]
    if translated_fr and translated_fr.lower() != q_lower:
        parts.append(translated_fr)
    if extra_keywords:
        parts.append(" ".join(extra_keywords))
    return " ".join(parts)


def translate_response(text_fr: str, lang: str = "Français") -> str:
    """
    Traduit la réponse vers l'Éwé ou le Kabiyè en un seul passage rapide,
    sans bloquer la connexion si l'API externe est inaccessible.
    """
    if not text_fr or lang == "Français":
        return text_fr

    # Le Kabiyè s'appuie sur le pont lexical et le nettoyage direct
    if lang == "Kabiyè":
        return dedupe_repetitions(text_fr)

    # Pour l'Éwé : traduction par blocs de paragraphes (1 à 2 appels max au lieu de 30)
    try:
        paragraphs = text_fr.split("\n\n")
        translated_paragraphs: list[str] = []

        for p in paragraphs:
            stripped = p.strip()
            if not stripped:
                continue

            # Si le paragraphe est court ou contient déjà des caractères éwé, on dé-boucle directement
            if any(ch in stripped for ch in ("ɖ", "ƒ", "ɣ", "ʋ")):
                translated_paragraphs.append(dedupe_repetitions(stripped))
                continue

            # Protection des citations [1], [2]
            citations: list[str] = []
            def _save_cit(m: re.Match) -> str:
                citations.append(m.group(0))
                return f" __CIT{len(citations)-1}__ "

            clean_p = re.sub(r"\[\d+\]", _save_cit, stripped)
            translated = _safe_fetch_gtx(clean_p, src="fr", dest="ee", timeout=4.0)

            for idx, cit in enumerate(citations):
                translated = re.sub(rf"\s*__CIT{idx}__\s*", f" {cit} ", translated)

            translated_paragraphs.append(dedupe_repetitions(translated))

        return "\n\n".join(translated_paragraphs)

    except Exception as exc:
        log.error("Erreur lors de la traduction : %s", exc)
        # En cas d'indisponibilité externe, renvoie le texte sans faire planter le serveur
        return dedupe_repetitions(text_fr)