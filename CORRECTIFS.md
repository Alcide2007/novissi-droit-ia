# Correctif — Imports Relatifs pour le Déploiement Render

Ce petit patch corrige toutes les erreurs `ModuleNotFoundError` sur les serveurs de production Render (liées à `legal_scraper`, `rag`, `ocr`, etc.).

## Comment l'appliquer :
1. Décompressez l'archive `novissi-correctifs-render-imports.zip`.
2. Copiez le dossier `novissi-droit-ia`.
3. Collez-le sur votre dossier de projet pour écraser les fichiers dans `backend/`.
4. Faites un `git add .`, un `git commit` et un `git push`.

Render redémarrera tout seul avec succès !
