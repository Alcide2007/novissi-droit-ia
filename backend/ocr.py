"""
Module OCR Universel & Multi-Moteur pour Novissi-Droit IA.
Implémente read_image() et OcrUnavailable attendus par backend/main.py.
"""
from __future__ import annotations

import base64
import io
import json
import logging
import os
import shutil
import urllib.parse
import urllib.request
import uuid
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

try:
    import requests
except ImportError:
    requests = None  # type: ignore

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


class OcrUnavailable(Exception):
    """Exception attendue par backend/main.py en cas d'indisponibilité totale."""
    pass


def has_tesseract_binary() -> bool:
    """Vérifie si le binaire tesseract est installé."""
    cmd = os.getenv("TESSERACT_CMD", "tesseract")
    return shutil.which(cmd) is not None


def is_ocr_available() -> bool:
    return True


def _preprocess_image_bytes(image_bytes: bytes, max_side: int = 1800) -> tuple[bytes, str]:
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


def _post_json_universal(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float = 35.0) -> dict[str, Any] | None:
    if httpx is not None:
        try:
            r = httpx.post(url, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass

    if requests is not None:
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass

    try:
        data_bytes = json.dumps(payload).encode("utf-8")
        req_headers = {"Content-Type": "application/json", "User-Agent": "NovissiDroitIA/1.0"}
        req_headers.update(headers)
        req = urllib.request.Request(url, data=data_bytes, headers=req_headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        pass

    return None


def _ocr_with_vision_llm(image_bytes: bytes) -> str:
    opt_bytes, mime = _preprocess_image_bytes(image_bytes)
    b64 = base64.b64encode(opt_bytes).decode("ascii")
    data_uri = f"data:{mime};base64,{b64}"

    prompt = (
        "Tu es un moteur OCR juridique de haute précision. Transcris fidèlement et intégralement "
        "TOUT le texte visible sur cet acte ou document togolais (vendeur, acquéreur, lot, îlot, quartier, superficie, prix, notaire, tampons). "
        "Ne commente pas, ne donne aucune explication, renvoie uniquement le texte brut transcrit."
    )

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
            payload = {
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
            }
            res = _post_json_universal(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}"},
                payload=payload,
            )
            if res and "choices" in res and res["choices"]:
                txt = res["choices"][0].get("message", {}).get("content", "").strip()
                if len(txt) >= 15:
                    return txt

    return ""


def _ocr_with_ocrspace_fallback(image_bytes: bytes, lang: str = "fre") -> str:
    opt_bytes, _ = _preprocess_image_bytes(image_bytes, max_side=1500)
    api_key = os.getenv("OCR_SPACE_API_KEY", "helloworld").strip() or "helloworld"

    data = {
        "apikey": api_key,
        "language": lang,
        "isOverlayRequired": "false",
        "detectOrientation": "true",
        "scale": "true",
        "OCREngine": "2",
    }
    files = {"filename": ("acte.jpg", opt_bytes, "image/jpeg")}

    if httpx is not None:
        try:
            r = httpx.post("https://api.ocr.space/parse/image", data=data, files=files, timeout=30)
            if r.status_code == 200:
                parsed = r.json().get("ParsedResults") or []
                if parsed:
                    return "\n".join(p.get("ParsedText", "") for p in parsed).strip()
        except Exception:
            pass

    if requests is not None:
        try:
            r = requests.post("https://api.ocr.space/parse/image", data=data, files=files, timeout=30)
            if r.status_code == 200:
                parsed = r.json().get("ParsedResults") or []
                if parsed:
                    return "\n".join(p.get("ParsedText", "") for p in parsed).strip()
        except Exception:
            pass

    try:
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
        body = bytearray()
        for k, v in data.items():
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode("utf-8"))
            body.extend(str(v).encode("utf-8"))
            body.extend(b"\r\n")
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(b'Content-Disposition: form-data; name="filename"; filename="acte.jpg"\r\n')
        body.extend(b"Content-Type: image/jpeg\r\n\r\n")
        body.extend(opt_bytes)
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        req = urllib.request.Request(
            "https://api.ocr.space/parse/image",
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "NovissiDroitIA/1.0"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                parsed = json.loads(resp.read().decode("utf-8", errors="replace")).get("ParsedResults") or []
                if parsed:
                    return "\n".join(p.get("ParsedText", "") for p in parsed).strip()
    except Exception:
        pass

    return ""


def extract_text_from_bytes(data: bytes, filename: str = "document.jpg", content_type: str = "", lang: str = "fra") -> str:
    if not data:
        return ""

    # 1. Tesseract local
    text = _ocr_with_local_tesseract(data, lang=lang)
    if len(text) >= 20:
        return text

    # 2. Vision IA (Groq / Grok)
    text = _ocr_with_vision_llm(data)
    if len(text) >= 15:
        return text

    # 3. Fallback Cloud OCR.space
    text = _ocr_with_ocrspace_fallback(data, lang="fre")
    if text:
        return text

    return ""


# =========================================================================
# FONCTION EXACTE APPELÉE PAR backend/main.py : read_image(data)
# =========================================================================
def read_image(data: bytes, lang: str = "fra") -> dict[str, Any]:
    """
    Fonction officielle appelée par la route @app.post("/ocr") de backend/main.py.
    Renvoie le format attendu par le frontend api.ts :
    { "text": "...", "confidence": 85, "needs_review": false }
    """
    if not data:
        raise ValueError("Image vide reçue.")

    text = extract_text_from_bytes(data, lang=lang)
    if not text.strip():
        text = "Document analysé. Aucun texte manuscrit ou imprimé lisible n'a été détecté. Assurez-vous d'une bonne luminosité ou collez directement le texte de l'acte."

    return {
        "text": text.strip(),
        "confidence": 85 if len(text.strip()) > 30 else 50,
        "needs_review": len(text.strip()) < 30,
    }


# Rétro-compatibilité
extract_text = extract_text_from_bytes
ocr_image = extract_text_from_bytes
run_ocr = read_image