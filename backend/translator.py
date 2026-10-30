"""
Module de traduction & Pont Lexical (Français <-> Éwé / Kabiyè) — Version corrigée anti-boucles.
Corrige les bugs de répétition infinie ("ɖe ɖe ɖe...", "ɖokui le nu vɔ̃ le...") générés par
le traducteur neuronal ou le LLM sur les structures Markdown et les termes juridiques.
"""
from __future__ import annotations

import re
import urllib.parse
import requests

# Glossaire de pont lexical : Langues locales (Éwé / Kabiyè) -> Mots-clés RAG Français
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

# Termes juridiques officiels à protéger en français ou à traduire proprement
LEGAL_GLOSSARY_EWE: dict[str, str] = {
    "Titre Foncier": "Titre Foncier (Anyigbagbalẽ gã)",
    "OTR": "OTR (Cadastre)",
    "3 tampons": "3 Tampons (Kpeɖodzi 3)",
    "mise en demeure": "mise en demeure (nudodo ɖe ame dzi)",
    "préavis": "préavis (gbeɖeɖe ɖi)",
}

LEGAL_GLOSSARY_KABIYE: dict[str, str] = {
    "Titre Foncier": "Titre Foncier (Tɛtʊ takayaɣ sɔsɔɣa)",
    "OTR": "OTR (Cadastre)",
    "3 tampons": "3 Tampons",
    "mise en demeure": "mise en demeure",
    "préavis": "préavis",
}


def dedupe_repetitions(text: str) -> str:
    """
    Supprime les boucles d'hallucination NMT/LLM en Éwé et Kabiyè :
    - Répétitions d'un même mot ("ɖe ɖe ɖe ɖe..." -> "ɖe")
    - Répétitions de groupes de mots ("ɖokui le nu vɔ̃ le ɖokui le nu vɔ̃ le..." -> 1 seule fois)
    """
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
                            and [w.lower() for w in words[i + reps * n : i + (reps + 1) * n]]
                            == chunk_lower
                        ):
                            reps += 1
                        if (n >= 3 and reps >= 2) or (n < 3 and reps >= 3):
                            new_words.extend(chunk)
                            i += reps * n
                            # Absorbe aussi une queue partielle de la même boucle en fin de ligne
                            rem = len(words) - i
                            if (
                                n >= 4
                                and 3 <= rem < n
                                and [w.lower() for w in words[i : i + rem]] == chunk_lower[:rem]
                            ):
                                i += rem
                            continue
                    new_words.append(words[i])
                    i += 1
                words = new_words
        cleaned_line = " ".join(words)
        # Nettoyage regex supplémentaire pour les bégaiements de syllabes collées
        cleaned_line = re.sub(r"\b(\w+)(?:\s+\1){2,}\b", r"\1", cleaned_line, flags=re.IGNORECASE)
        out_lines.append(cleaned_line)

    return "\n".join(out_lines)


def enrich_query_for_rag(query: str, lang: str = "Français") -> str:
    """
    Convertit ou enrichit une question posée en Éwé ou Kabiyè vers le français
    pour que le moteur RAG trouve toujours les bons articles de loi togolais.
    """
    if not query or lang == "Français":
        return query

    q_lower = query.lower()
    extra_keywords: list[str] = []
    for local_word, fr_terms in LEXICAL_BRIDGE_TO_FR.items():
        if local_word in q_lower:
            extra_keywords.append(fr_terms)

    # Tentative de traduction vers le français via GTX si c'est de l'Éwé
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


def _gtx_translate_chunk(text: str, src: str = "fr", dest: str = "ee") -> str:
    """Traduit un segment court (une seule ligne propre sans Markdown complexe) via Google GTX."""
    clean = text.strip()
    if not clean:
        return text
    try:
        url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl={src}&tl={dest}&dt=t&q={urllib.parse.quote(clean)}"
        )
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data and isinstance(data[0], list):
                out = "".join(seg[0] for seg in data[0] if seg and seg[0])
                return dedupe_repetitions(out)
    except Exception:
        pass
    return text


def translate_response(text_fr: str, lang: str = "Français") -> str:
    """
    Traduit une réponse juridique structurée du français vers l'Éwé ou le Kabiyè :
    1. Protège les balises Markdown (**, listes, numéros) et les citations [1], [2]
       AVANT la traduction pour éviter que le moteur neuronal ne boucle dessus.
    2. Traduit phrase par phrase (segments courts < 250 caractères).
    3. Applique le filtre anti-boucles `dedupe_repetitions` sur chaque sortie.
    """
    if not text_fr or lang == "Français":
        return text_fr

    # Si le texte a déjà été généré en langue locale par le LLM, on le nettoie simplement
    if lang == "Kabiyè":
        # Google GTX ne supporte pas nativement le code ISO 'kbp' (Kabiyè) :
        # si le LLM a répondu en Kabiyè ou en Français, on nettoie toute boucle éventuelle
        return dedupe_repetitions(text_fr)

    # Pour l'Éwé ('ee') : traduction ligne par ligne en isolant le Markdown et les citations [n]
    lines = text_fr.split("\n")
    translated_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            translated_lines.append("")
            continue

        # Isoler les puces ou numéros en début de ligne (ex: "• ", "- ", "1. ", "### ")
        prefix_match = re.match(r"^(\s*(?:[•\-*]|\d+\.|#{1,4})\s+)", line)
        prefix = prefix_match.group(1) if prefix_match else ""
        content = line[len(prefix) :] if prefix_match else line

        # Extraire et protéger les citations [1], [2] en fin ou milieu de phrase
        citations: list[str] = []
        def _save_cit(m: re.Match) -> str:
            citations.append(m.group(0))
            return f" __CIT{len(citations)-1}__ "

        content_no_cit = re.sub(r"\[\d+\]", _save_cit, content)
        # Retirer les étoiles Markdown ** avant d'envoyer à GTX (principale cause du bug "**Kpɔkplɛ ɖe ɖe ɖe...")
        had_bold = "**" in content_no_cit
        clean_content = content_no_cit.replace("**", "").strip()

        # Si la ligne est déjà en Éwé (contient ɖ, ƒ, ɣ, ɔ, ɛ), on la dé-boucle sans la retraduire
        if any(ch in clean_content for ch in ("ɖ", "ƒ", "ɣ", "ʋ")):
            trans = dedupe_repetitions(clean_content)
        else:
            trans = _gtx_translate_chunk(clean_content, src="fr", dest="ee")
            trans = dedupe_repetitions(trans)

        # Restaurer les citations [1], [2]
        for idx, cit in enumerate(citations):
            trans = re.sub(rf"\s*__CIT{idx}__\s*", f" {cit} ", trans, flags=re.IGNORECASE)

        trans = re.sub(r"\s{2,}", " ", trans).strip()
        if had_bold and ":" in trans:
            head, rest = trans.split(":", 1)
            trans = f"**{head.strip()} :** {rest.strip()}"

        translated_lines.append(f"{prefix}{trans}")

    final_text = "\n".join(translated_lines)
    return dedupe_repetitions(final_text)


# Paramètres LLM recommandés pour éviter les boucles en Éwé et Kabiyè lors des appels Grok / Groq :
LLM_ANTI_LOOP_PARAMS = {
    "temperature": 0.2,
    "frequency_penalty": 0.6,
    "presence_penalty": 0.4,
}
