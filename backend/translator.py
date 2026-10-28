"""Traducteur juridique multilingue 100 % gratuit (Français <-> Éwé / Kabiyè) avec préservation des citations."""
from __future__ import annotations

import json
import logging
import os
import re
import urllib.parse
import urllib.request

log = logging.getLogger("novissi.translator")
CITE_RE = re.compile(r"\[(\d+)\]")

FR_TO_EWE_HEADERS = [
    (r"\*\*En résumé\s*(?:\([^)]*\))?\s*:?\*\*", "**1. Nya vevitɔwo (Wò gomenɔamesiwo) :**"),
    (r"\*\*Ce que dit le droit togolais\s*(?:\([^)]*\))?\s*:?\*\*", "**2. Nu si Togo ƒe se gblɔ :**"),
    (r"\*\*Ce que dit la loi\s*(?:\([^)]*\))?\s*:?\*\*", "**2. Nu si Togo ƒe se gblɔ :**"),
    (r"\*\*Démarche concrète étape par étape\s*(?:\([^)]*\))?\s*:?\*\*", "**3. Nu si nàwɔ fifia (Afɔɖeɖewo) :**"),
    (r"3\.\s*Démarche concrète étape par étape[^\n]*", "### 3. Nu si nàwɔ fifia (Nu ɖe ɖeɖeɖe ɖi do ŋgɔ)"),
    (r"\*\*À faire maintenant\s*(?:\([^)]*\))?\s*:?\*\*", "**3. Nu si nàwɔ fifia :**"),
    (r"\*\*Que faire maintenant\s*\??\*\*", "**3. Nu si nàwɔ fifia :**"),
    (r"\bEn résumé\s*:", "Nya vevitɔwo :"),
    (r"\bCe que dit la loi\s*:", "Nu si se la gblɔ :"),
    (r"\bÀ faire maintenant\s*:", "Nu si nàwɔ fifia :"),
    (r"\(Information générale,?\s*pas un avis d['’]avocat\.?\)", ""),
]

FR_TO_KABIYE_HEADERS = [
    (r"\*\*En résumé\s*(?:\([^)]*\))?\s*:?\*\*", "**1. Tɔm kɛdɩtʊ (Ñɔ-wahɩyɛ) :**"),
    (r"\*\*Ce que dit le droit togolais\s*(?:\([^)]*\))?\s*:?\*\*", "**2. Togo paɣtʊ yɔɔdʊʊ se :**"),
    (r"\*\*Ce que dit la loi\s*(?:\([^)]*\))?\s*:?\*\*", "**2. Paɣtʊ yɔɔdʊʊ se :**"),
    (r"\*\*Démarche concrète étape par étape\s*(?:\([^)]*\))?\s*:?\*\*", "**3. Mbʊ pʊwɛɛ se na-la lɛɛlɛɛyɔ :**"),
    (r"\*\*À faire maintenant\s*(?:\([^)]*\))?\s*:?\*\*", "**3. Mbʊ pʊwɛɛ se na-la lɛɛlɛɛyɔ :**"),
    (r"\*\*Que faire maintenant\s*\??\*\*", "**3. Mbʊ pʊwɛɛ se na-la lɛɛlɛɛyɔ :**"),
    (r"\bEn résumé\s*:", "Tɔm kɛdɩtʊ :"),
    (r"\bCe que dit la loi\s*:", "Paɣtʊ yɔɔdʊʊ se :"),
    (r"\bÀ faire maintenant\s*:", "Mbʊ pʊwɛɛ se na-la lɛɛlɛɛyɔ :"),
    (r"\(Information générale,?\s*pas un avis d['’]avocat\.?\)", ""),
    (r"\(Inspection du travail\)", ""),
    (r"\bavocat\b", "lɔŋ pasɩyʊ"),
    (r"\bnotaire\b", "paɣtʊ takayaɣ mayʊ"),
]


def replace_french_headers(text: str, lang: str) -> str:
    pairs = FR_TO_EWE_HEADERS if lang == "Ewé" else (FR_TO_KABIYE_HEADERS if lang == "Kabiyè" else [])
    out = text
    for pattern, repl in pairs:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out.strip()


def google_gtx_translate(text: str, sl: str = "auto", tl: str = "ee") -> str | None:
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
    markers = re.findall(
        r"\b(must|paid|within|after|month|stipule|paiement|intervenir|retard|manquement|autorise|obligatoires|procédure|saisit|licenciement|salaire|employeur|salarié|locataire|propriétaire|contrat|tribunal|décision|préavis|cependant|toutefois|ainsi|loi|droit|vous|votre|vos|dans|avec|pour|selon|article)\b",
        text.lower(),
    )
    return len(markers) >= 2


def _translate_preserving_structure(text: str, tl: str) -> str:
    lines = text.splitlines()
    out_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out_lines.append("")
            continue
        cites = CITE_RE.findall(stripped)
        prefix = ""
        body = stripped
        m = re.match(r"^(\s*(?:[-*•]|\d+\.)\s+|\s*#{1,4}\s+)", line)
        if m:
            prefix = m.group(1)
            body = line[len(prefix):].strip()
        tr = google_gtx_translate(body, sl="auto", tl=tl) or body
        missing_cites = " ".join(f"[{c}]" for c in cites if f"[{c}]" not in tr)
        final_line = f"{prefix}{tr} {missing_cites}".rstrip()
        out_lines.append(final_line)
    return "\n".join(out_lines)


def ensure_target_language(text: str, lang: str, llm_fn=None, glossary_terms: dict | None = None) -> str:
    if lang == "Français" or not text.strip():
        return text

    cleaned = replace_french_headers(text, lang)
    if os.getenv("SCRAPER_ENABLED") == "0":
        return cleaned

    if _looks_mostly_french(cleaned) and llm_fn is not None:
        try:
            terms_hint = ""
            if glossary_terms:
                terms_hint = "\nLexique obligatoire :\n" + "\n".join(f"- {k} = {v}" for k, v in glossary_terms.items())
            sys_tr = (
                f"Tu es un traducteur juridique assermenté togolais spécialisé en {lang}. "
                f"Traduis INTEGRALEMENT ce texte juridique en {lang} pur et fluide. "
                "INTERDICTION ABSOLUE d'écrire en anglais ou de laisser des phrases en français. "
                "Conserve les puces Markdown et conserve exactement les numéros entre crochets comme [1], [2]."
                + terms_hint
            )
            tr_llm = llm_fn(sys_tr, cleaned, max_tokens=1500)
            orig_cites = CITE_RE.findall(cleaned)
            new_cites = CITE_RE.findall(tr_llm)
            missing = " ".join(f"[{c}]" for c in orig_cites if c not in new_cites)
            cleaned = replace_french_headers(f"{tr_llm} {missing}".strip(), lang)
        except Exception:
            pass

    if lang == "Ewé" and _looks_mostly_french(cleaned):
        cleaned = _translate_preserving_structure(cleaned, tl="ee")
        cleaned = replace_french_headers(cleaned, lang)

    if lang == "Kabiyè" and _looks_mostly_french(cleaned):
        nllb = hf_nllb_translate(cleaned, src_lang="fra_Latn", tgt_lang="kbp_Latn")
        if nllb:
            orig_cites = CITE_RE.findall(cleaned)
            nllb_cites = CITE_RE.findall(nllb)
            missing = " ".join(f"[{c}]" for c in orig_cites if c not in nllb_cites)
            cleaned = replace_french_headers(f"{nllb} {missing}".strip(), lang)

    return cleaned
