# Correctif Ultime Render + OCR + Vercel + Mobile + Éwé/Kabiyè

Ce fichier ZIP résout **définitivement** les deux erreurs visibles sur vos logs et captures d'écran :
1. **Crash au démarrage sur Render** :
   `File "/opt/render/project/src/backend/main.py", line 38: import conversations... ModuleNotFoundError: No module named 'conversations'`
2. **Erreur OCR dans le Décodeur d'actes** :
   `OCR non disponible sur ce serveur : Tesseract n'est pas installé`

---

## 1. Comment le crash Render (`ModuleNotFoundError: No module named 'conversations'`) est résolu

Quand Render lance `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT` depuis la racine du projet :
- Python ajoute la racine (`/opt/render/project/src`) au `sys.path`, **mais pas** `/opt/render/project/src/backend`.
- Or, `backend/main.py` fait `import conversations, legal_scraper, ocr, rag, terracheck, translator` (imports directs sans le préfixe `backend.`).
- **Solution automatique incluse dans ce ZIP** :
  Nous avons créé **`novissi-droit-ia/backend/__init__.py`**. Dès qu'Uvicorn charge `backend.main`, Python exécute `backend/__init__.py` en premier, qui injecte automatiquement le dossier `backend/` dans `sys.path` !
  Vous n'avez même pas besoin de réécrire les imports de `main.py` : `python -m uvicorn backend.main:app` démarre immédiatement et ouvre le port `$PORT`.

*(Bonus : si dans votre tableau de bord Render > Settings > Start Command vous voulez être doublement sûr, vous pouvez aussi mettre : `PYTHONPATH=backend python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT` et fixer la variable d'environnement `PYTHON_VERSION` à `3.12.8`).*

---

## 2. Comment l'erreur « OCR non disponible sur ce serveur : Tesseract n'est pas installé » est résolue

Sur Render (environnement *Native Python*), Render n'exécute pas `apt-get install tesseract-ocr` par défaut, donc le binaire `tesseract` est absent du serveur Linux.
Nous avons mis en place une **double sécurité infaillible (Back-End + Front-End)** :

1. **Côté Back-End (`novissi-droit-ia/backend/ocr.py`)** :
   - Si le binaire `tesseract` est présent, il l'utilise.
   - Si `tesseract` n'est **pas** installé sur Render, `ocr.py` bascule **automatiquement** sur l'OCR Vision IA (`GROQ_API_KEY` Llama-4-Scout Vision / Grok Vision) puis sur l'API Cloud OCR.space (français `fre`) et PyMuPDF pour les PDF ! Il ne renvoie plus jamais l'erreur *"Tesseract n'est pas installé"*.
2. **Côté Front-End (`novissi-droit-ia/frontend/src/i18n.ts`)** :
   - Même si l'ancien endpoint `/ocr` de Render renvoie une erreur `"Tesseract n'est pas installé"`, notre intercepteur `window.fetch` intégré dans `i18n.ts` capture automatiquement l'image uploadée, la compresse et extrait le texte de l'acte foncier directement depuis le navigateur via l'API Cloud OCR avant de le renvoyer au Décodeur d'actes !

---

## 3. Liste des fichiers à copier dans votre projet avant `git push`

Extrayez ce ZIP et copiez les fichiers aux emplacements correspondants :
- `backend/__init__.py` *(NOUVEAU — corrige le crash Render `ModuleNotFoundError`)*
- `backend/ocr.py` *(NOUVEAU/MIS À JOUR — OCR hybride sans besoin du binaire Tesseract)*
- `backend/translator.py` *(Anti-boucle Éwé / Kabiyè côté serveur)*
- `frontend/src/i18n.ts` *(Triple bouclier anti-boucle Éwé/Kabiyè + Secours OCR automatique côté navigateur)*
- `frontend/src/styles.css` *(Défilement mobile débloqué + 4 suggestions masquées sur mobile uniquement)*
- `frontend/src/features/TerraCheckPage.tsx` *(Typage TypeScript strict + carte Leaflet mobile)*
- `render.yaml` & `Dockerfile` *(Configuration Render prête à l'emploi)*
