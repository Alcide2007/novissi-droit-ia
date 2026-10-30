"""
Initialisation du package backend Novissi-Droit IA.
Ajoute automatiquement le dossier `backend/` au `sys.path` pour que tous les imports
absolus (`import conversations, legal_scraper, ocr, rag, terracheck, translator`)
fonctionnent aussi bien avec `uvicorn backend.main:app` (Render) qu'avec `uvicorn main:app`.
"""
import os
import sys
from pathlib import Path

_BACKEND_DIR = str(Path(__file__).resolve().parent)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
