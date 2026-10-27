# Rapport de préparation — Novissi-Droit IA local

## Changements intégrés
- Ajout de `run.sh`, menu Bash pour installation, lancement, collecte juridique, tests, audit Voix du Togo et diagnostic.
- Suppression des fichiers Docker/Compose et mise à jour des tâches VS Code pour l'exécution locale.
- Correction de la dictée : sélection de langue, gestion des erreurs, ajout au texte existant et aucune soumission automatique.
- Ajout d'un connecteur d'audit prudent pour `https://voixdutogo.gouv.tg/parler`, d'un schéma d'exemple et d'un répertoire distinct pour les données linguistiques.
- Ajout de `GET /language-resources/status` pour consulter le rapport d'audit local.
- Ajout de la source LQDD dans la configuration d'exemple et activation de la revérification des documents connus via `SCRAPER_REFETCH=1`.
- Ajustement des consignes de réponse en éwé/kabyè pour signaler les limites et préserver les citations juridiques originales.
- Documentation locale mise à jour.

## Vérifications effectuées dans l'environnement de préparation
- `bash -n run.sh setup.sh dev.sh scrape.sh diagnose.sh _common.sh` : réussi.
- `python -m compileall -q backend tests` : réussi.
- Tests Python : 32 réussis avec un petit module de substitution temporaire pour `slowapi`, car le réseau de l'environnement de préparation ne permettait pas d'installer cette dépendance. Ce test ne valide donc pas le vrai mécanisme de limitation de débit.
- Installation npm et build TypeScript : non exécutés jusqu'au bout, car `npm install` a dépassé le délai disponible et l'environnement ne pouvait pas résoudre le registre npm.
- Le site Voix du Togo n'a pas pu être interrogé depuis cet environnement. Le connecteur doit donc être exécuté sur l'ordinateur de l'utilisateur pour établir les ressources réellement accessibles.

## Limites à connaître
- La sélection d'éwé/kabyè ne garantit pas que la reconnaissance vocale native du navigateur prend en charge ces langues.
- Le connecteur Voix du Togo audite les ressources accessibles, mais n'importe pas automatiquement les contenus dont les droits de réutilisation sont inconnus.
- Le corpus juridique et le registre de parcelles d'exemple ne doivent pas être présentés comme exhaustifs ou officiels sans vérification externe.

## Mise à jour issue de `novissi-droit-ia-fusion (1).zip`
- Correction du traitement des relances dans une conversation : le backend récupère l'historique enregistré avant le message courant, utilise la dernière question juridique substantielle pour contextualiser les relances et transmet un historique court au modèle. L'historique sert à résoudre les références, jamais de source juridique.
- Ajout d'une action « Partager » dans l'interface de chat (partage natif ou copie du transcript) et modernisation de la barre latérale : logo, Nouveau chat, icônes des outils, zone « Vos discussions ».
- Dictée vocale en mode continu avec redémarrage lorsque Edge/navigateur interrompt la reconnaissance après un silence. L'utilisateur garde un bouton explicite « Arrêter la dictée » ; aucune soumission automatique n'est faite.
- OCR automatique de secours pendant la collecte des PDF scannés, via PyMuPDF et Tesseract, activé par `PDF_OCR_ENABLED=1`. Installation du programme Tesseract et des langues requise sur le poste Windows.
- Ajout de `backend/postgres_catalog.py` : si `LEGAL_DATABASE_URL` est renseignée, PostgreSQL devient le catalogue de lecture du RAG et de la recherche juridique. Le registre de crawl/reprise reste SQLite et les conversations sont encore dans `data/conversations.db` ; leur migration vers PostgreSQL n'est pas incluse dans cette version.
- Tests backend : 66 réussis dans l'environnement de préparation avec un stub temporaire pour `slowapi` (le vrai mécanisme de limitation de débit n'est pas couvert par ce stub). `py_compile` réussi.
- Le build frontend n'a pas pu être validé ici : le registre npm était inaccessible, donc les dépendances n'ont pas pu être installées intégralement. Les tests frontend doivent être exécutés localement avec `npm install`, puis `npm test` et `npm run build`.
- La connexion réelle à PostgreSQL, la collecte du Journal officiel et l'OCR réel restent à valider sur l'ordinateur de déploiement ; aucune clé API ni mot de passe n'est inclus dans le projet.
