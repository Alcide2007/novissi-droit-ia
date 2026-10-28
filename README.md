# NOVISSI-DROIT IA : l'avocat du peuple (équipe LEXTECH)

Assistant juridique pour le Togo. Deux piliers :
1. **Droits citoyens** : chat voix/texte qui cite les articles de loi (RAG), conversations enregistrées, courriers, analyse d'actes.
2. **TerraCheck** : vérification d'actes et de terrains (OCR, verdict vert/orange/rouge, carte).

Compte rendu des travaux, tests et limites : `ETAPES.md`.

## Démarrage rapide (Git Bash dans VS Code, sans Docker)
```bash
bash run.sh        # menu : installer, lancer, collecter, tests, diagnostic
```

### PostgreSQL pour le corpus juridique (recommandé)
1. Créez une base vide, par exemple `novissi_droit`, dans PostgreSQL.
2. Dans `.env`, définissez `LEGAL_DATABASE_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/novissi_droit`.
3. Installez les dépendances avec `bash setup.sh`, puis démarrez l'application. Le schéma PostgreSQL est créé automatiquement ; les articles issus du registre de collecte SQLite sont synchronisés vers PostgreSQL et le RAG les lit depuis ce catalogue.
4. Sans `LEGAL_DATABASE_URL`, le prototype conserve son mode SQLite historique.

Le registre SQLite reste utilisé pour l'état du crawl, les reprises et les erreurs. PostgreSQL est la source de lecture du RAG lorsque configuré. Les fichiers originaux PDF restent archivés dans `data/originals/`.

### PDF scannés
L'OCR de collecte est activé par défaut (`PDF_OCR_ENABLED=1`) et utilise PyMuPDF + Tesseract. Sur Windows, installez aussi le programme Tesseract et les données de langue française (`fra`) ; Python seul ne suffit pas. Les PDF dont l'OCR échoue restent marqués « à revoir » au lieu d'être déclarés correctement extraits.
Détails pas à pas : `MODE_D_EMPLOI.md`. Architecture : `docs/architecture.md`.

## Structure
| Dossier / fichier | Rôle |
|---|---|
| `frontend/` | Application React : chat, historique, recherche juridique, courriers, actes, TerraCheck |
| `backend/main.py` | API FastAPI (chat, conversations, `/legal/*`, `/collection/*`, OCR, TerraCheck) |
| `backend/registry.py` | Registre d'ingestion SQLite : sources, ressources, versions, articles, runs et erreurs ; conserve les états de reprise du collecteur |
| `backend/postgres_catalog.py` | Catalogue PostgreSQL utilisé par le RAG et la recherche juridique lorsque `LEGAL_DATABASE_URL` est configurée |
| `backend/legal_scraper.py` | Connecteurs Journal officiel, LQDD, OTR ; reprise, versions, originaux SHA-256 |
| `backend/rag.py`, `splitter.py` | Index de recherche du chat (avec provenance) et découpe en articles |
| `data/originals/`, `data/registry.db` | PDF originaux et registre (à sauvegarder) |
| `data/laws/` | Exemples fictifs + export texte dérivé (régénérable) |
| `tests/`, `frontend/src/__tests__/` | Tests backend (pytest) et frontend (vitest) |

Scripts : `run.sh` (menu), `setup.sh`, `dev.sh`, `scrape.sh`, `report.sh`, `backup.sh`, `diagnose.sh`, `testia.sh`.

## Tests
```bash
python -m pytest -q                              # backend
cd frontend && npm test && npm run build         # tests vitest + compilation TypeScript
```

## Sécurité
Les clés vont dans `.env` (copié depuis `.env.example`), jamais dans le code ni dans `.env.example`.
Les collecteurs respectent `robots.txt` et espacent leurs requêtes.
