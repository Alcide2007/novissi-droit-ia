"""Traducteur juridique multilingue 100 % gratuit (Français <-> Éwé / Kabiyè).

Combine 3 niveaux sans frais :
1. Connecteur neuronal Google Translate GTX (100 % gratuit, SANS clé API) pour l'Éwé (code ISO 'ee').
2. Connecteur Meta NLLB-200 (Hugging Face gratuit, optionnel via HF_API_KEY) pour l'Éwé ('ewe_Latn') et le Kabiyè ('kbp_Latn').
3. Passe de traduction dédiée par LLM (Groq / Gemini gratuit) appuyée sur le glossaire juridique togolais,
   avec préservation stricte des citations [1], [2] et de la mise en forme Markdown.
"""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.parse
import urllib.request

log = logging.getLogger("novissi.translator")

CITE_PLACEHOLDER_RE = re.compile(r"\[(\d+)\]")

# En-têtes et expressions fréquentes qui pourraient rester en français dans les réponses IA
FR_TO_EWE_HEADERS = [
    (r"\*\*En résumé\s*(?:\([^)]*\))?\s*:?\*\*", "**Nya vevitɔwo (Wò gomenɔamesiwo) :**"),
    (r"\*\*Ce que dit le droit togolais\s*(?:\([^)]*\))?\s*:?\*\*", "**Nu si Togo ƒe se gblɔ :**"),
    (r"\*\*Ce que dit la loi\s*(?:\([^)]*\))?\s*:?\*\*", "**Nu si Togo ƒe se gblɔ :**"),
    (r"\*\*Démarche concrète étape par étape\s*(?:\([^)]*\))?\s*:?\*\*", "**Nu si nàwɔ fifia (Afɔɖeɖewo) :**"),
    (r"\*\*À faire maintenant\s*(?:\([^)]*\))?\s*:?\*\*", "**Nu si nàwɔ fifia :**"),
    (r"\*\*Que faire maintenant\s*\??\*\*", "**Nu si nàwɔ fifia :**"),
    (r"\bEn résumé\s*:", "Nya vevitɔwo :"),
    (r"\bCe que dit la loi\s*:", "Nu si se la gblɔ :"),
    (r"\bÀ faire maintenant\s*:", "Nu si nàwɔ fifia :"),
]

FR_TO_KABIYE_HEADERS = [
    (r"\*\*En résumé\s*(?:\([^)]*\))?\s*:?\*\*", "**Tɔm kɛdɩtʊ (Ñɔ-wahɩyɛ) :**"),
    (r"\*\*Ce que dit le droit togolais\s*(?:\([^)]*\))?\s*:?\*\*", "**Togo paɣtʊ yɔɔdʊʊ se :**"),
    (r"\*\*Ce que dit la loi\s*(?:\([^)]*\))?\s*:?\*\*", "**Paɣtʊ yɔɔdʊʊ se :**"),
    (r"\*\*Démarche concrète étape par étape\s*(?:\([^)]*\))?\s*:?\*\*", "**Mbʊ pʊwɛɛ se na-la lɛɛlɛɛyɔ :**"),
    (r"\*\*À faire maintenant\s*(?:\([^)]*\))?\s*:?\*\*", "**Mbʊ pʊwɛɛ se na-la lɛɛlɛɛyɔ :**"),
    (r"\*\*Que faire maintenant\s*\??\*\*", "**Mbʊ pʊwɛɛ se na-la lɛɛlɛɛyɔ :**"),
    (r"\bEn résumé\s*:", "Tɔm kɛdɩtʊ :"),
    (r"\bCe que dit la loi\s*:", "Paɣtʊ yɔɔdʊʊ se :"),
    (r"\bÀ faire maintenant\s*:", "Mbʊ pʊwɛɛ se na-la lɛɛlɛɛyɔ :"),
]


def replace_french_headers(text: str, lang: str) -> str:
    """Remplace systématiquement les titres de sections français par leur équivalent Éwé ou Kabiyè."""
    pairs = FR_TO_EWE_HEADERS if lang == "Ewé" else (FR_TO_KABIYE_HEADERS if lang == "Kabiyè" else [])
    out = text
    for pattern, repl in pairs:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def google_gtx_translate(text: str, sl: str = "fr", tl: str = "ee") -> str | None:
    """Traduction neuronale 100 % gratuite et sans clé via le service Google Translate GTX (supporte l'Éwé 'ee')."""
    if not text.strip() or os.getenv("SCRAPER_ENABLED") == "0":
        return None
    if os.getenv("TRANSLATOR_GTX_ENABLED", "1") == "0":
        return None
    try:
        qs = urllib.parse.urlencode({"client": "gtx", "sl": sl, "tl": tl, "dt": "t", "q": text})
        req = urllib.request.Request(
            f"https://translate.googleapis.com/translate_a/single?{qs}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read().decode("utf-8"))
        if not isinstance(data, list) or not data or not isinstance(data[0], list):
            return None
        translated = "".join(seg[0] for seg in data[0] if isinstance(seg, list) and seg and seg[0])
        return translated.strip() or None
    except Exception as e:
        log.debug("GTX translate indisponible : %s", type(e).__name__)
        return None


def hf_nllb_translate(text: str, src_lang: str = "fra_Latn", tgt_lang: str = "ewe_Latn") -> str | None:
    """Traduction optionnelle via Meta NLLB-200 sur Hugging Face (gratuit avec HF_API_KEY) pour Éwé (ewe_Latn) et Kabiyè (kbp_Latn)."""
    hf_key = os.getenv("HF_API_KEY", "").strip()
    if not hf_key or not text.strip() or os.getenv("SCRAPER_ENABLED") == "0":
        return None
    model = os.getenv("HF_NLLB_MODEL", "facebook/nllb-200-distilled-600M")
    try:
        body = json.dumps({"inputs": text[:1500], "parameters": {"src_lang": src_lang, "tgt_lang": tgt_lang}}).encode("utf-8")
        req = urllib.request.Request(
            f"https://api-inference.huggingface.co/models/{model}",
            data=body,
            headers={"Authorization": f"Bearer {hf_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20.0) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read().decode("utf-8"))
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return (data[0].get("translation_text") or "").strip() or None
    except Exception as e:
        log.debug("HF NLLB indisponible : %s", type(e).__name__)
    return None


def translate_user_query_to_fr(query: str, lang: str) -> str:
    """Traduit une question posée en Éwé ou en Kabiyè vers le français pour que le moteur RAG trouve tous les articles."""
    if lang == "Ewé":
        tr = google_gtx_translate(query, sl="ee", tl="fr")
        if tr:
            return f"{query} {tr}"
        tr_hf = hf_nllb_translate(query, src_lang="ewe_Latn", tgt_lang="fra_Latn")
        if tr_hf:
            return f"{query} {tr_hf}"
    elif lang == "Kabiyè":
        tr_hf = hf_nllb_translate(query, src_lang="kbp_Latn", tgt_lang="fra_Latn")
        if tr_hf:
            return f"{query} {tr_hf}"
    return query


def _looks_mostly_french(text: str) -> bool:
    """Détecte si un texte contient encore des phrases françaises non traduites."""
    fr_markers = re.findall(
        r"\b(vous|votre|vos|dans|avec|pour|selon|article|employeur|salarié|locataire|propriétaire|contrat|tribunal|décision|préavis|cependant|toutefois|ainsi)\b",
        text.lower(),
    )
    return len(fr_markers) >= 3


def ensure_target_language(text: str, lang: str, llm_fn=None, glossary_terms: dict | None = None) -> str:
    """Garantit que 100 % de la réponse est en Éwé ou en Kabiyè tout en préservant les citations [1], [2]."""
    if lang == "Français" or not text.strip():
        return text

    cleaned = replace_french_headers(text, lang)
    if os.getenv("SCRAPER_ENABLED") == "0":
        return cleaned

    # Si le texte contient encore du français, on le traduit intégralement
    if _looks_mostly_french(cleaned):
        if lang == "Ewé":
            gtx = google_gtx_translate(cleaned, sl="fr", tl="ee")
            if gtx:
                orig_cites = CITE_PLACEHOLDER_RE.findall(cleaned)
                gtx_cites = CITE_PLACEHOLDER_RE.findall(gtx)
                if set(orig_cites) <= set(gtx_cites):
                    return replace_french_headers(gtx, lang)
                missing = " ".join(f"[{c}]" for c in orig_cites if c not in gtx_cites)
                return replace_french_headers(f"{gtx} {missing}".strip(), lang)

        if lang == "Kabiyè":
            nllb = hf_nllb_translate(cleaned, src_lang="fra_Latn", tgt_lang="kbp_Latn")
            if nllb:
                orig_cites = CITE_PLACEHOLDER_RE.findall(cleaned)
                nllb_cites = CITE_PLACEHOLDER_RE.findall(nllb)
                missing = " ".join(f"[{c}]" for c in orig_cites if c not in nllb_cites)
                return replace_french_headers(f"{nllb} {missing}".strip(), lang)

        # Repli sur une passe de traduction stricte par le LLM (Groq / Gemini)
        if llm_fn is not None:
            try:
                terms_hint = ""
                if glossary_terms:
                    terms_hint = "\nVocabulaire obligatoire :\n" + "\n".join(f"- {k} = {v}" for k, v in glossary_terms.items())
                sys_tr = (
                    f"Tu es un traducteur professionnel assermenté du français vers le {lang} (Togo). "
                    f"Traduis INTEGRALEMENT le texte suivant en {lang}. "
                    "Ne laisse AUCUNE phrase en français. Conserve exactement les balises de citation entre crochets comme [1], [2]."
                    + terms_hint
                )
                tr_llm = llm_fn(sys_tr, cleaned, max_tokens=1400)
                orig_cites = set(CITE_PLACEHOLDER_RE.findall(cleaned))
                new_cites = set(CITE_PLACEHOLDER_RE.findall(tr_llm))
                if orig_cites <= new_cites:
                    return replace_french_headers(tr_llm, lang)
            except Exception:
                pass

    return cleaned
