"""OCR local : prétraitement OpenCV + Tesseract. Renvoie aussi un score de confiance."""
from __future__ import annotations


class OcrUnavailable(Exception):
    pass


def read_image(data: bytes) -> dict:
    try:
        import cv2
        import numpy as np
        import pytesseract
    except ImportError as e:  # dépendances optionnelles
        raise OcrUnavailable(str(e)) from e
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image illisible")
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    try:
        d = pytesseract.image_to_data(img, lang="fra", output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractNotFoundError as e:
        raise OcrUnavailable("Tesseract n'est pas installé") from e
    words = [(w, float(c)) for w, c in zip(d["text"], d["conf"]) if w.strip() and float(c) >= 0]
    text = " ".join(w for w, _ in words)
    conf = round(sum(c for _, c in words) / len(words), 1) if words else 0.0
    return {"text": text, "confidence": conf, "needs_review": conf < 70}
