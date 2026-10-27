"""Audit prudent de la page publique Voix du Togo.

Ce module n'essaie pas de contourner une connexion, un CAPTCHA ou des restrictions.
Il n'importe pas automatiquement de médias protégés. Les ressources collectées doivent
être revues et leur réutilisation autorisée avant d'être ajoutées au corpus.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

URL = "https://voixdutogo.gouv.tg/parler"
HOST = urlparse(URL).netloc


def audit(url: str = URL, timeout: float = 15.0) -> dict:
    report = {"source": "Voix du Togo", "url": url, "checked_at": datetime.now(timezone.utc).isoformat(),
              "status": "unknown", "title": None, "language_mentions": [], "resource_links": [],
              "audio_elements": 0, "notes": []}
    if urlparse(url).netloc != HOST:
        report["status"] = "refused"
        report["notes"].append("L'URL doit appartenir à voixdutogo.gouv.tg.")
        return report
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers={"User-Agent": "Novissi-Droit-IA/0.1 (research prototype)"}) as client:
            robots = client.get("https://" + HOST + "/robots.txt")
            if robots.status_code == 200:
                from urllib.robotparser import RobotFileParser
                rp = RobotFileParser(); rp.parse(robots.text.splitlines())
                if not rp.can_fetch("Novissi-Droit-IA/0.1", url):
                    report["status"] = "disallowed"
                    report["notes"].append("La page est interdite par robots.txt pour cet agent.")
                    return report
            response = client.get(url)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        report["title"] = soup.title.get_text(" ", strip=True) if soup.title else None
        text = soup.get_text(" ", strip=True)
        for term in ("éwé", "ewe", "kabiyè", "kabiye", "français", "audio", "transcription", "traduction"):
            if re.search(re.escape(term), text, re.I): report["language_mentions"].append(term)
        report["audio_elements"] = len(soup.find_all("audio"))
        for a in soup.find_all("a", href=True):
            target = urljoin(str(response.url), a["href"])
            if urlparse(target).netloc == HOST and target not in report["resource_links"]:
                label = a.get_text(" ", strip=True)[:160]
                report["resource_links"].append({"label": label, "url": target})
        report["status"] = "ok"
        report["notes"].append("Audit de page uniquement : la présence d'un lien ne prouve ni l'exhaustivité ni les droits de réutilisation.")
        report["notes"].append("Vérifier les mentions légales et les autorisations avant tout téléchargement ou entraînement de modèle.")
    except Exception as exc:
        report["status"] = "error"
        report["notes"].append(f"Échec d'accès : {type(exc).__name__}. Aucune donnée n'a été inventée.")
    return report


def save_report(report: dict, path: str | Path = "data/languages/voix_du_togo_audit.json") -> Path:
    out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

if __name__ == "__main__":
    result = audit(); target = save_report(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nRapport écrit dans : {target}")
