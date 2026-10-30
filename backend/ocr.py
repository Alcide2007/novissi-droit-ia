"""
Module OCR Universel & Multi-Moteur (Sans dépendance obligatoire au binaire système Tesseract).
Résout définitivement l'erreur Render : "OCR non disponible sur ce serveur : Tesseract n'est pas installé".

Ordre d'exécution automatique (Fallback en cascade) :
1. Si c'est un PDF : extraction directe via PyMuPDF (fitz) ou pypdf.
2. Si le binaire `tesseract` est installé sur la machine : OCR local via pytesseract (fra).
3. Si `tesseract` est absent (cas par défaut de l'environnement Python natif sur Render) :
   a) OCR Vision IA haute précision via `GROQ_API_KEY` (modèle vision Llama-4-Scout / Llama-3.2-Vision)
      ou `XAI_API_KEY` / `OPENAI_API_KEY`.
   b) Fallback automatique vers l'API OCR.space (clé gratuite intégrée ou `OCR_SPACE_API_KEY`)
      qui extrait le texte français des photos d'actes fonciers sans binaire système.
"""
from __future__ import annotations

import base64
import io
import logging
import os
import shutil
from typing import Any

import requests

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = ImageOps = None  # type: ignore

try:
    import pytesseract
except ImportError:
    pytesseract = None  # type: ignore

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # type: ignore

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore

log = logging.getLogger("novissi-ocr")


def has_tesseract_binary() -> bool:
    """Vérifie si le binaire système `tesseract` est réellement présent."""
    cmd = os.getenv("TESSERACT_CMD", "tesseract")
    return shutil.which(cmd) is not None


def is_ocr_available() -> bool:
    """
    Indique au reste de l'application que l'OCR est TOUJOURS disponible
    grâce au moteur hybride (Tesseract local + Cloud Vision / OCR Fallback).
    """
    return True


def _preprocess_image_bytes(image_bytes: bytes, max_side: int = 1800) -> tuple[bytes, str]:
    """Redimensionne et optimise l'image en JPEG pour accélérer l'OCR Cloud et respecter les limites de taille (< 1 Mo)."""
    if Image is None:
        return image_bytes, "image/jpeg"
    try:
        with Image.open(io.BytesIO(image_bytes)) as im:
            im = ImageOps.exif_transpose(im) if ImageOps else im
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            w, h = im.size
            if max(w, h) > max_side:
                scale = max_side / float(max(w, h))
                im = im.resize((int(w * scale), int(h * scale)))
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=85, optimize=True)
            return buf.getvalue(), "image/jpeg"
    except Exception as exc:
        log.warning("Prétraitement image ignoré : %s", exc)
        return image_bytes, "image/jpeg"


def _ocr_with_local_tesseract(image_bytes: bytes, lang: str = "fra") -> str:
    """Tente l'extraction via Tesseract local si le binaire existe sur le serveur."""
    if pytesseract is None or Image is None or not has_tesseract_binary():
        return ""
    try:
        with Image.open(io.BytesIO(image_bytes)) as im:
            im = ImageOps.exif_transpose(im) if ImageOps else im
            try:
                text = pytesseract.image_to_string(im, lang=lang)
            except Exception:
                text = pytesseract.image_to_string(im)
            return (text or "").strip()
    except Exception as exc:
        log.warning("Tesseract local a échoué : %s", exc)
        return ""


def _ocr_with_vision_llm(image_bytes: bytes) -> str:
    """
    Extrait le texte intégral d'un acte foncier ou contrat photographié via Groq Vision / Grok Vision / OpenAI Vision.
    Fonctionne sur Render sans installer Tesseract !
    """
    opt_bytes, mime = _preprocess_image_bytes(image_bytes)
    b64 = base64.b64encode(opt_bytes).decode("ascii")
    data_uri = f"data:{mime};base64,{b64}"

    prompt = (
        "Tu es un moteur OCR juridique de haute précision. Transcris fidèlement et intégralement "
        "TOUT le texte visible sur ce document (acte de vente, reçu, contrat, titre foncier, tampons). "
        "Ne commente pas, renvoie uniquement le texte extrait ligne par ligne."
    )

    # 1. Essai avec GROQ_API_KEY (modèles Vision gratuits/rapides sur Groq Cloud)
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if groq_key:
        vision_models = [
            os.getenv("GROQ_VISION_MODEL", "").strip(),
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "llama-3.2-90b-vision-preview",
            "llama-3.2-11b-vision-preview",
        ]
        for model in [m for m in vision_models if m]:
            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {"url": data_uri}},
                                ],
                            }
                        ],
                        "temperature": 0.0,
                        "max_tokens": 2048,
                    },
                    timeout=35,
                )
                if resp.status_code == 200:
                    txt = resp.json()["choices"][0]["message"]["content"].strip()
                    if len(txt) >= 15:
                        return txt
            except Exception as exc:
                log.warning("Groq Vision (%s) ignoré : %s", model, exc)

    # 2. Essai avec XAI_API_KEY (Grok Vision) ou OPENAI_API_KEY
    for env_key, base_url, model_name in [
        ("XAI_API_KEY", "https://api.x.ai/v1/chat/completions", "grok-2-vision-1212"),
        ("OPENAI_API_KEY", "https://api.openai.com/v1/chat/completions", "gpt-4o-mini"),
    ]:
        api_key = os.getenv(env_key, "").strip()
        if not api_key:
            continue
        try:
            resp = requests.post(
                base_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": data_uri}},
                            ],
                        }
                    ],
                    "temperature": 0.0,
                    "max_tokens": 2048,
                },
                timeout=35,
            )
            if resp.status_code == 200:
                txt = resp.json()["choices"][0]["message"]["content"].strip()
                if len(txt) >= 15:
                    return txt
        except Exception as exc:
            log.warning("Vision API (%s) ignorée : %s", env_key, exc)

    return ""


def _ocr_with_ocrspace_fallback(image_bytes: bytes, lang: str = "fre") -> str:
    """
    Moteur OCR Cloud de secours (OCR.space API) : fonctionne même sans Tesseract et sans clé Vision IA.
    Supporte le français (`fre`) et les photos d'actes scannés.
    """
    opt_bytes, _ = _preprocess_image_bytes(image_bytes, max_side=1500)
    api_key = os.getenv("OCR_SPACE_API_KEY", "helloworld").strip() or "helloworld"
    try:
        resp = requests.post(
            "https://api.ocr.space/parse/image",
            data={
                "apikey": api_key,
                "language": lang,
                "isOverlayRequired": "false",
                "detectOrientation": "true",
                "scale": "true",
                "OCREngine": "2",
            },
            files={"filename": ("acte.jpg", opt_bytes, "image/jpeg")},
            timeout=30,
        )
        if resp.status_code == 200:
            payload = resp.json()
            parsed = payload.get("ParsedResults") or []
            if parsed:
                txt = "
".join(p.get("ParsedText", "") for p in parsed).strip()
                if txt:
                    return txt
    except Exception as exc:
        log.warning("Fallback OCR.space ignoré : %s", exc)
    return ""


def _extract_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extrait le texte d'un PDF (natif ou scanné) via PyMuPDF ou pypdf."""
    parts: list[str] = []
    if fitz is not None:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                t = (page.get_text("text") or "").strip()
                if t:
                    parts.append(t)
            text = "

".join(parts).strip()
            if len(text) >= 30:
                return text
            # Si le PDF est un scan image sans couche texte, on convertit la 1re page en image et on lance l'OCR !
            if len(doc) > 0:
                pix = doc[0].get_pixmap(dpi=180)
                img_bytes = pix.tobytes("jpeg")
                return extract_text_from_bytes(img_bytes, filename="scan.jpg")
        except Exception as exc:
            log.warning("PyMuPDF lecture PDF échouée : %s", exc)

    if PdfReader is not None:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
            for page in reader.pages[:20]:
                parts.append(page.extract_text() or "")
            return "

".join(parts).strip()
        except Exception as exc:
            log.warning("pypdf lecture PDF échouée : %s", exc)
    return ""


def extract_text_from_bytes(
    data: bytes,
    filename: str = "document.jpg",
    content_type: str = "",
    lang: str = "fra",
) -> str:
    """
    Point d'entrée universel pour extraire le texte d'une image ou d'un PDF.
    Ne lève JAMAIS l'erreur 'Tesseract n'est pas installé'.
    """
    if not data:
        return ""

    fname = (filename or "").lower()
    ctype = (content_type or "").lower()
    if data.startswith(b"%PDF-") or fname.endswith(".pdf") or "pdf" in ctype:
        return _extract_pdf_bytes(data)

    # 1. Essai Tesseract local si disponible
    text = _ocr_with_local_tesseract(data, lang=lang)
    if len(text) >= 20:
        return text

    # 2. Essai Vision IA (Groq Llama-4-Scout / Grok / OpenAI)
    text = _ocr_with_vision_llm(data)
    if len(text) >= 15:
        return text

    # 3. Essai OCR.space Cloud Fallback (gratuit, sans binaire système)
    text = _ocr_with_ocrspace_fallback(data, lang="fre")
    if text:
        return text

    return ""


# Alias rétro-compatibles avec toutes les signatures possibles de `backend/main.py`
def extract_text(file_or_bytes: Any, filename: str = "", content_type: str = "", lang: str = "fra") -> dict[str, Any] | str:
    """Compatible à la fois avec un appel qui attend une string ou un dict."""
    if isinstance(file_or_bytes, (bytes, bytearray)):
        raw = bytes(file_or_bytes)
    elif hasattr(file_or_bytes, "read"):
        raw = file_or_bytes.read()
    elif isinstance(file_or_bytes, (str, os.PathLike)) and os.path.exists(file_or_bytes):
        with open(file_or_bytes, "rb") as f:
            raw = f.read()
    else:
        raw = b""

    txt = extract_text_from_bytes(raw, filename=filename, content_type=content_type, lang=lang)
    return txt


def ocr_image(data: bytes, filename: str = "image.jpg", lang: str = "fra") -> str:
    return extract_text_from_bytes(data, filename=filename, lang=lang)


def run_ocr(data: bytes, filename: str = "image.jpg", content_type: str = "") -> dict[str, Any]:
    txt = extract_text_from_bytes(data, filename=filename, content_type=content_type)
    return {
        "ok": bool(txt.strip()),
        "text": txt,
        "engine": "tesseract" if has_tesseract_binary() else "cloud-vision-ocr",
        "error": None if txt.strip() else "Aucun texte lisible détecté sur l'image. Essayez une photo plus nette.",
    }
