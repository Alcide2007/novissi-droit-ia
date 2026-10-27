"""TerraCheck : extraction des champs d'un acte, rapprochement avec le registre, score Vert/Orange/Rouge.

Adapté aux réalités foncières du Togo (Loi n° 2018-005 portant Code foncier et domanial) :
- Titre Foncier (TF), Réquisition d'immatriculation (OTR / Conservation Foncière), Certificat Administratif
- Plan parcellaire géo-référencé et vérification de la procédure des « 3 Tampons » (Géomètre agréé, Chef traditionnel/Mairie, Cadastre/OTR)
- Détection des clauses à risque togolaises (vente sous seing privé sans notaire, clause de non-garantie d'éviction, terrain familial indivis sans signature des cohéritiers, zone de réserve administrative).
Calcul déterministe et reproductible. Le registre fourni (data/parcels.json) est FICTIF."""
from __future__ import annotations

import difflib
import json
import pathlib
import re
import time
import unicodedata

DEFAULT_DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "parcels.json"


def norm(s: object) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def load_parcels(path: pathlib.Path | None = None) -> dict[str, dict]:
    p = pathlib.Path(path or DEFAULT_DATA)
    return {x["id"]: x for x in json.loads(p.read_text(encoding="utf-8"))}


# ---------- extraction des champs d'un acte (adapté au contexte togolais) ----------
AREA_RE = re.compile(r"(\d[\d\s.,]*)\s*(m2|m²|mètres?\s+carrés?|ares?|ha|hectares?|lots?)", re.I)
LOT_RE = re.compile(r"lot\s*(?:n[°ºo]\s*)?(\d+[a-z]?)", re.I)
ILOT_RE = re.compile(r"[iî]lot\s*(?:n[°ºo]\s*)?(\d+[a-z]?)", re.I)
TITRE_RE = re.compile(
    r"(?:titre\s+foncier|TF|réquisition(?:\s+d['’]immatriculation)?|certificat\s+administratif)\s*(?:n[°ºo]\s*)?([\w./-]*\d[\w./-]*)",
    re.I,
)
NOTAIRE_RE = re.compile(r"(?:Ma[îi]tre|Me|Notaire)\s+([A-ZÉÈÀÂÎÔÛ][\wÉÈÀÂÎÔÛéèàâîôûç'’.-]+(?:\s+[A-ZÉÈÀÂÎÔÛ][\wÉÈÀÂÎÔÛéèàâîôûç'’.-]+){0,2})")
TAMPONS_RE = re.compile(r"(?:trois|3)\s+tampons|vis[ée]\s+par\s+le\s+cadastre|plan\s+parcellaire\s+vis[ée]", re.I)
NAME = r"[A-ZÉÈÀÂÎÔÛ][\wÉÈÀÂÎÔÛéèàâîôûç'’-]+"
PERSON = rf"{NAME}(?:\s+{NAME}){{0,3}}"
VENDEUR_RE = re.compile(rf"(?:vendeur|vendu(?:e)?\s+par|cédé(?:e)?\s+par|collectivité\s+familiale)\s*:?\s*(?:Monsieur|Madame|M\.|Mme|Togbui|Mama)?\s*({PERSON})")
ACQ_RE = re.compile(rf"(?:acquéreur|acheteur|acquis\s+par|vendu(?:e)?\s+à|preneur)\s*:?\s*(?:Monsieur|Madame|M\.|Mme)?\s*({PERSON})")
PERSON_RE = re.compile(rf"(?:Monsieur|Madame|Mme|M\.)\s+({PERSON})")
QUARTIER_RE = re.compile(rf"(?:quartier\s+(?:de\s+)?|situ[ée]e?\s+à\s+|sis(?:e)?\s+à\s+|commune\s+d['’])({NAME}(?:[- ]{NAME})?)")


def parse_area(value: object) -> float | None:
    """Convertit '600 m²', '6 ares', '0,06 ha' ou 600 en m²."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    m = AREA_RE.search(str(value))
    raw, unit = (m.group(1), m.group(2).lower()) if m else (re.sub(r"[^\d.,]", "", str(value)), "m2")
    raw = raw.replace(" ", "").replace(",", ".")
    try:
        n = float(raw)
    except ValueError:
        return None
    if unit.startswith("are"):
        return n * 100
    if unit.startswith("h"):
        return n * 10000
    if unit.startswith("lot") and n <= 10:
        return n * 600
    return n


def extract_fields(text: str, known_quartiers: list[str] | None = None) -> dict:
    """Extraction par règles : sert de filet de sécurité quand l'IA est indisponible."""
    f: dict[str, object] = {}
    if m := LOT_RE.search(text):
        f["lot"] = m.group(1)
    if m := ILOT_RE.search(text):
        f["ilot"] = m.group(1)
    if m := TITRE_RE.search(text):
        f["reference_titre"] = m.group(1)
    if m := AREA_RE.search(text):
        f["superficie_m2"] = parse_area(m.group(0))
    if m := NOTAIRE_RE.search(text):
        f["notaire"] = f"Me {m.group(1).strip()}"
    if TAMPONS_RE.search(text):
        f["trois_tampons"] = "Mentionné dans l'acte"
    nt = norm(text)
    for q in known_quartiers or []:
        if norm(q) and norm(q) in nt:
            f["quartier"] = q
            break
    else:
        if m := QUARTIER_RE.search(text):
            f["quartier"] = m.group(1).strip()
    if m := VENDEUR_RE.search(text):
        f["proprietaire"] = m.group(1).strip()
    elif m := PERSON_RE.search(text):
        f["proprietaire"] = m.group(1).strip()
    if m := ACQ_RE.search(text):
        f["acquereur"] = m.group(1).strip()
    return f


# ---------- détection déterministe des clauses à risque au Togo (sans faille même hors-ligne) ----------
RULE_CLAUSES = [
    (
        re.compile(r"sans\s+(?:aucune\s+)?garantie(?:\s+du\s+vendeur|\s+d['’]éviction)?|non[- ]garantie|à\s+ses\s+risques\s+et\s+périls", re.I),
        "élevé",
        "Clause de non-garantie d'éviction : au Togo, si une collectivité familiale ou un tiers revendique le terrain, le vendeur refuse de vous rembourser (Art. 166+ Code foncier).",
    ),
    (
        re.compile(r"totalité\s+à\s+la\s+signature|payé\s+comptant\s+entre\s+les\s+mains|hors\s+la\s+comptabilité\s+du\s+notaire|reçu\s+sous\s+seing\s+privé", re.I),
        "élevé",
        "Paiement intégral non sécurisé ou acte sous seing privé : selon l'Art. 166 du Code foncier togolais, toute vente immobilière doit passer devant notaire après vérification de l'état descriptif à l'OTR.",
    ),
    (
        re.compile(r"héritiers?\s+non\s+signataires?|collectivité\s+familiale|bien\s+indivis|succession\s+non\s+partagée", re.I),
        "moyen",
        "Terrain familial ou succession indivise : assurez-vous que le procès-verbal du conseil de famille et la signature de TOUS les cohéritiers figurent à l'acte notarié.",
    ),
    (
        re.compile(r"ni\s+titre\s+foncier|en\s+cours\s+d['’]immatriculation|sans\s+bornage|limites?\s+approximatives?", re.I),
        "moyen",
        "Absence de Titre Foncier définitif ou de bornage contradictoire : exigez le plan parcellaire géo-référencé visé (3 tampons) et vérifiez la réquisition à l'OTR.",
    ),
]


def detect_risk_clauses(text: str) -> list[dict]:
    """Détecte automatiquement les extraits dangereux dans un acte foncier ou bail togolais."""
    out: list[dict] = []
    for regex, risque, explication in RULE_CLAUSES:
        m = regex.search(text or "")
        if m:
            start = max(0, m.start() - 25)
            end = min(len(text), m.end() + 35)
            snippet = text[start:end].strip()
            # Trouver la phrase ou le segment exact présent dans le texte
            exact = m.group(0).strip()
            out.append({"extrait": exact if len(exact) >= 6 else snippet, "risque": risque, "explication": explication})
    return out[:5]


# ---------- rapprochement avec le registre ----------
def match_parcel(fields: dict, parcels: dict[str, dict]) -> dict:
    """Ne devine jamais : lot + quartier doivent correspondre, sinon « introuvable » ou « ambigu »."""
    lot = norm(fields.get("lot"))
    if not lot:
        return {"status": "not_found", "parcel_id": None, "candidates": []}
    cands = [p for p in parcels.values() if norm(p["lot"]) == lot]
    q = norm(fields.get("quartier"))
    if q:
        cands = [p for p in cands if q in norm(p["quartier"]) or norm(p["quartier"]) in q]
    il = norm(fields.get("ilot"))
    if il and len(cands) > 1:
        cands = [p for p in cands if norm(p.get("ilot")) == il] or cands
    if len(cands) == 1:
        return {"status": "found", "parcel_id": cands[0]["id"], "candidates": [cands[0]["id"]]}
    if len(cands) > 1:
        return {"status": "ambiguous", "parcel_id": None, "candidates": [c["id"] for c in cands]}
    return {"status": "not_found", "parcel_id": None, "candidates": []}


def _same_person(a: str, b: str) -> bool:
    ta, tb = sorted(norm(a).split()), sorted(norm(b).split())
    return difflib.SequenceMatcher(None, " ".join(ta), " ".join(tb)).ratio() >= 0.8


def _centroid(poly: list[list[float]]) -> list[float]:
    return [sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)]


# ---------- diagnostic ----------
def diagnose(p: dict, acte: dict | None = None) -> dict:
    t0 = time.perf_counter()
    buyers = {norm(v["acquereur"]) for v in p.get("ventes", []) if v.get("statut", "actif") == "actif"}
    checks = [
        {"label": "Titre foncier enregistré au Livre Foncier (OTR)", "ok": p["titre"] == "enregistre", "critical": False},
        {"label": "Aucune double vente détectée sur la parcelle", "ok": len(buyers) <= 1, "critical": True},
        {"label": "Aucun litige ni opposition judiciaire déclarés", "ok": not p["litige"], "critical": True},
        {"label": "Bornage contradictoire et limites cadastrales précises", "ok": p["limites"] == "precises", "critical": False},
        {"label": "Conforme au plan d'urbanisme (Hors réserve administrative)", "ok": p["urbanisme"] == "conforme", "critical": False},
    ]
    if acte:
        if acte.get("proprietaire"):
            checks.append({"label": "Le vendeur de l'acte correspond au propriétaire inscrit à l'OTR",
                           "ok": _same_person(str(acte["proprietaire"]), p["proprietaire"]), "critical": False})
        area = parse_area(acte.get("superficie_m2"))
        if area and p.get("superficie_m2"):
            checks.append({"label": "Superficie de l'acte cohérente avec le plan cadastral (±5%)",
                           "ok": abs(area - p["superficie_m2"]) / p["superficie_m2"] <= 0.05, "critical": False})
    if any(not c["ok"] and c["critical"] for c in checks):
        score = "rouge"
    elif not all(c["ok"] for c in checks):
        score = "orange"
    else:
        score = "vert"
    advice = {
        "vert": "Parcelle sécurisée dans le registre : Titre Foncier valide et aucune double vente. Exigez tout de même un état descriptif récent à l'OTR et signez devant un notaire.",
        "orange": "Vigilance requise avant tout versement : vérifiez le dossier des 3 tampons, exigez un bornage contradictoire par géomètre agréé et contrôlez la réquisition à l'OTR.",
        "rouge": "DANGER IMMÉDIAT — Ne signez rien et ne versez aucun acompte : risque critique de double vente ou de litige familial/judiciaire inscrit sur cette parcelle.",
    }[score]
    return {
        "id": p["id"], "name": p["name"], "quartier": p["quartier"], "lot": p["lot"], "ilot": p.get("ilot", ""),
        "commune": p.get("commune", "Grand Lomé"), "nature_terrain": p.get("nature_terrain", "Urbain"),
        "reference_titre": p.get("reference_titre", "Non renseigné"), "requisition": p.get("requisition", "Non renseignée"),
        "trois_tampons": p.get("trois_tampons", "a_verifier"), "collectivite": p.get("collectivite", ""),
        "proprietaire": p.get("proprietaire", ""), "superficie_m2": p.get("superficie_m2"),
        "ventes": p.get("ventes", []),
        "score": score, "checks": checks, "advice": advice, "polygon": p["polygon"],
        "center": _centroid(p["polygon"]), "simulated": True,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
    }
