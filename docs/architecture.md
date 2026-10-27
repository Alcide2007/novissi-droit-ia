# Architecture : Novissi-Droit IA (prototype)

## Démarrage
```bash
bash run.sh  # installation, lancement local, collecte, tests et diagnostic
```
Interface : http://localhost:5173 · API : http://localhost:8000/docs
Sans clé API, l'application démarre en **mode dégradé** (extraits de loi bruts, extraction d'acte par règles). Pour activer l'IA : `cp .env.example .env`, renseigner au moins une clé gratuite (`GEMINI_API_KEY` ou `GROQ_API_KEY`), relancer.

## Modèles d'IA gratuits avec repli automatique
`llm()` essaie les fournisseurs configurés dans l'ordre de `LLM_PROVIDERS`. En cas de quota atteint, de panne ou de clé invalide, le suivant prend le relais ; si tous échouent, l'application passe en mode dégradé. Les offres gratuites ont des limites de requêtes et leurs conditions changent : vérifiez-les avant la démo. Les invites envoyées aux offres gratuites peuvent servir à améliorer les produits du fournisseur : n'y envoyez pas de vraies données personnelles. Ollama garde tout en local.

## Vue d'ensemble
```mermaid
flowchart LR
  U[Utilisateur] --> F[Frontend React + Leaflet]
  F -- "/api (proxy Vite)" --> B[Backend FastAPI]
  B --> R[rag.py : index TF-IDF à chaud]
  B --> T[terracheck.py : extraction, rapprochement, score]
  B --> O[ocr.py : OpenCV + Tesseract]
  B --> C[(LLM gratuit : Gemini, Groq, OpenRouter, Ollama)]
  S[legal_scraper.py] -- "toutes les N heures" --> L[(data/laws/*.txt + index.json)]
  L --> R
  P[(data/parcels.json)] --> T
  S -. robots.txt, délai configurable .-> J[Journal Officiel / La Question de Droit]
```

## Rôle de chaque module
| Fichier | Rôle |
|---|---|
| `backend/main.py` | Routes, limites de débit, CORS, mode dégradé, boucle d'actualisation |
| `backend/rag.py` | Lecture des textes (articles ou paragraphes d'analyse), recherche, **rechargement à chaud** sans arrêt du service, garde-fou de citations |
| `backend/legal_scraper.py` | Récupération polie (robots.txt, délai, jamais d'exception), empreinte par document, provenance (URL, date) |
| `backend/terracheck.py` | Extraction des champs d'un acte, rapprochement lot + quartier, score Vert/Orange/Rouge **déterministe** |
| `backend/ocr.py` | Prétraitement OpenCV, Tesseract, score de confiance |
| `data/laws/` | Textes indexés. Les fichiers `EXEMPLE_FICTIF_*` sont **fictifs** : à remplacer |
| `data/parcels.json` | Registre de parcelles **fictif** (ventes, titre, litige, limites, polygone) |

## Flux : de l'acte au score TerraCheck
1. Photo → `POST /ocr` → texte + confiance (l'utilisateur relit et corrige).
2. `POST /decode` : l'IA extrait résumé, champs et clauses à risque ; les règles (`extract_fields`) servent de filet de sécurité et complètent l'IA.
3. `match_parcel` : lot **et** quartier doivent correspondre. Sinon « introuvable » ou « ambigu » : jamais de supposition.
4. `diagnose(parcelle, acte)` : double vente calculée sur les ventes actives du registre, litige, titre, limites, urbanisme, vendeur de l'acte comparé au propriétaire du registre, superficie. Une anomalie critique donne Rouge, une autre donne Orange.
5. Le frontend affiche la parcelle sur la carte (Leaflet / OpenStreetMap) avec le temps de calcul (quelques millisecondes).

## Base juridique dynamique
- Sources et motifs de liens dans `.env` (`JO_*`, `LQD_*`). **La Question de Droit est désactivée tant que `LQD_BASE_URL` est vide.**
- Boucle d'actualisation toutes les `REFRESH_HOURS` heures, ou à la demande : `POST /admin/refresh` avec l'en-tête `X-Admin-Token`.
- Le nouvel index est construit à côté puis échangé d'un coup : les requêtes en cours ne sont jamais coupées.
- Une panne du site source ne casse rien : l'ancien index continue d'être servi.
- Les analyses sont présentées comme des explications, jamais comme des textes de loi.

## Robustesse et sécurité
- Clé API côté serveur uniquement ; limites de débit par IP ; taille des entrées et des images limitée.
- Le texte de l'utilisateur est isolé dans des balises et traité comme une donnée.
- Une réponse sans citation valide, ou citant un extrait absent du contexte, est remplacée par un refus.
- Les textes utilisateur ne sont pas journalisés volontairement ; CORS est restreint à l’origine locale configurée. L’application est exécutée directement sur la machine, donc la sécurité de l’ordinateur et des fichiers locaux reste importante.
- Mode dégradé si l'IA est indisponible ; OCR illisible : message clair.

## Limites connues (à dire au jury)
- Corpus et parcelles **fictifs** tant qu'ils n'ont pas été remplacés par des données réelles.
- Éwé et Kabyè : sélection de langue et consignes au modèle disponibles, mais qualité linguistique non mesurée. La dictée utilise les codes `ee-TG` et `kbp-TG` lorsque le navigateur les accepte ; la prise en charge native est variable et doit être testée.
- Recherche TF-IDF : à remplacer par des embeddings (pgvector) pour mieux gérer les synonymes.
- Le scraper n'a pas été testé sur les sites réels : vérifier `JO_SEEDS` / `JO_LINK_PATTERN`, les conditions de réutilisation, et la qualité de l'extraction PDF.
- Pas d'authentification ni de base de données persistante (Supabase/PostGIS prévus dans le deck).
- Le serveur Vite est un serveur de développement, adapté au prototype mais pas à une mise en production.

## Tests
`pip install -r backend/requirements.txt && pytest -q tests`

## Mise à jour 0.4 : interface conversationnelle et historique persistant
- Frontend : `App.tsx` ne contient plus que le shell. Composants dans `src/components/` (Sidebar, ChatPage, ChatMessage, MessageComposer, CitationList, Markdown, ThemeToggle), modules métier conservés tels quels dans `src/features/` (LetterGenerator, ActeAnalyzer, TerraCheckPage), dictée dans `src/hooks/useDictation.ts`.
- Rendu Markdown via `react-markdown` + `remark-gfm` (HTML brut non interprété).
- Backend : `backend/conversations.py` (SQLite, `DATA_DIR/conversations.db`) et routes `/conversations` (POST, GET, PATCH, DELETE) et `/conversations/{id}/messages` (GET, POST). `/chat` est conservée, avec la même logique (`answer_question`).
- Les sources affichées sont celles renvoyées par le backend, jamais fabriquées par le frontend.

### Limites connues
- L'isolation des conversations repose sur un identifiant anonyme d'appareil (`X-Client-Id`), pas sur une authentification.
- Le bouton « Arrêter » annule l'attente côté navigateur ; le backend termine son calcul.
- Le connecteur Voix du Togo réalise un audit de la page et ne constitue pas encore un corpus linguistique validé. La collecte juridique doit être vérifiée sur les sites réels. Les tests frontend n’ont pas pu être exécutés dans l’environnement de préparation si npm ne peut pas télécharger les dépendances.


## Dictée et ressources linguistiques
- La dictée ne soumet pas automatiquement le texte : l’utilisateur peut le corriger et l’envoyer.
- Les langues de dictée reposent sur Web Speech API ; un code de langue configuré ne garantit pas que le navigateur dispose d’un moteur correspondant.
- `backend/language_sources/voix_du_togo.py` réalise un audit prudent et écrit un rapport sous `data/languages/`. Il n’importe pas automatiquement les contenus audio ou textuels protégés.
- `/language-resources/status` expose l’état du dernier rapport local sans lancer de collecte réseau.

## Registre documentaire (source de vérité du corpus)
`backend/registry.py` : base SQLite `data/registry.db` (mode WAL, clés étrangères, migrations versionnées, plein texte FTS5).

| Table | Rôle |
|---|---|
| `sources` | Une par connecteur : clé, nom, URL de base, **périmètre** (`national`, `regional`, `international`, `demo`), type |
| `resources` | Une par URL découverte (enregistrée AVANT téléchargement). Statuts : `discovered`, `archived`, `retry`, `review`, `unreachable`, `non_document`, `inspected`, `quarantine`. Garde ETag, Last-Modified, tentatives, échéance de réessai, erreur |
| `versions` | Un contenu précis (SHA-256) d'une ressource. **Jamais supprimée** ; une seule version « courante ». Un PDF peut contenir plusieurs textes : une version n'est pas « une loi » |
| `articles` (+ `articles_fts`) | Articles d'une version, avec numéro de page |
| `relations` | modifie, abroge, remplace, rectifie, complète, renvoie à. `verified=0` par défaut : aucune relation n'est déduite automatiquement (structure prête, **non alimentée**) |
| `runs`, `errors` | Journal des passes de collecte et erreurs typées (`transient`, `permanent`, `extraction`, `non_document`, `ssrf_guard`…) |

Les PDF originaux sont conservés dans `data/originals/<2 premiers hex>/<sha256>.pdf` (adressage par contenu, écriture atomique). Les chemins ne sont jamais exposés par l'API.

### Collecte (`backend/legal_scraper.py`)
Connecteurs séparés : `JournalOfficialConnector` (jo.gouv.tg : pagination `?page=N`, métadonnées référence/date/titre extraites de façon heuristique), `LQDDConnector` (catalogue, analyses), `OTRConnector` (avis fonciers, inactif tant que `OTR_BASE_URL` est vide). Pour chaque ressource : découverte → statut → téléchargement (3 essais, backoff exponentiel avec jitter, `Retry-After`) → empreinte → original conservé → extraction (pypdf, pages) → découpe en articles → version.
- Reprise : au démarrage, la file contient les graines, les ressources `discovered`, les `retry` échues et les documents à recontrôler (`SCRAPER_RECHECK_DAYS`, requête conditionnelle ETag/Last-Modified).
- Erreur temporaire (délai, 429, 5xx) → `retry` avec échéance croissante, jamais une suppression. 403/404/410 → `unreachable`.
- PDF corrompu → `quarantine` (original gardé). PDF scanné sans texte → `review` (OCR à prévoir), jamais « traité ». Un fichier corrompu **ne remplace jamais** une version valide.
- Redirection hors du domaine autorisé → refusée (garde SSRF). `robots.txt` respecté. Concurrence : 1 requête à la fois par hôte (délai configurable).
- `data/laws/*.txt` : **export dérivé et régénérable** (en-têtes `resource_id`, `version_id`, `sha256`), conservé pour lisibilité et compatibilité ; l'index l'ignore dès qu'il lit le registre.

### Recherche (`backend/rag.py`)
`LiveIndex(law_dir, registry)` indexe les articles des versions **courantes** (TF-IDF) avec leur provenance (ressource, version, empreinte, page, date de collecte). Les textes `EXEMPLE_FICTIF_*` sont marqués `demo` : `DEMO_MODE=auto` (défaut) ne les utilise que si aucun texte officiel n'existe, `on` toujours, `off` jamais. Le mode (`officiel`, `demonstration`, `mixte`) est exposé par `/health` et affiché dans l'interface. Le modèle ne peut citer que les identifiants présents dans le contexte (`citations_valid`), sinon la réponse est refusée.

### API (ajouts ; routes existantes inchangées)
| Route | Contenu |
|---|---|
| `GET /legal/sources` | Sources, périmètre, nombre de ressources |
| `GET /legal/texts?source=&status=&q=&limit=&offset=` | Ressources avec version courante |
| `GET /legal/texts/{id}`, `/versions`, `/articles?version_id=` | Détail, historique des versions, articles |
| `GET /legal/search?q=&source=&scope=&limit=` | Plein texte FTS5 (contenu, titre, « article N ») avec provenance |
| `GET /collection/status` | Rapport d'exhaustivité (pages inspectées, ressources par statut, extraits / non extraits, versions, changements récents, raisons d'incomplétude) |
| `GET /collection/errors` | Dernières erreurs |
| `POST /admin/sync` (alias `/admin/refresh`) | Synchronisation, protégée par `X-Admin-Token` |

Les types TypeScript correspondants sont dans `frontend/src/api.ts`. `verified` vaut toujours `false` : le statut juridique (en vigueur, abrogé) n'est jamais déduit.

### Choix d'architecture
- **SQLite plutôt que PostgreSQL/pgvector/MinIO** : l'application s'exécute en local, sans Docker ; le volume actuel (centaines de textes) ne justifie pas un serveur. Le schéma reste en SQL standard (hors FTS5) pour une migration ultérieure. Le magasin de fichiers adressé par contenu remplace MinIO.
- Conversations : `data/conversations.db` (SQLite), isolées par identifiant anonyme d'appareil. **Ce n'est pas une authentification** : sans comptes, deux personnes partageant un appareil partagent l'historique.



## Catalogue PostgreSQL (mode recommandé)

Lorsque `LEGAL_DATABASE_URL` est renseignée, `backend/postgres_catalog.py` crée les tables `legal_documents` et `legal_articles`, synchronise les articles des versions courantes du registre de collecte et fournit les textes au RAG ainsi qu'à la recherche juridique. Les versions précédentes restent dans PostgreSQL avec `is_current=false`. Le registre SQLite demeure utilisé pour la reprise du crawl et la journalisation des erreurs. Sans URL PostgreSQL, le mode SQLite historique reste disponible.

Les conversations restent persistées dans `data/conversations.db`. Le bug de relance venait surtout du fait que l'historique était enregistré mais que seul le dernier message était transmis au moteur de réponse ; le backend transmet maintenant un historique court et contextualise les relances avant la recherche juridique.
