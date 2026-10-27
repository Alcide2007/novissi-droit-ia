# Novissi-Droit : mode d'emploi (VS Code, sans Docker)

## Prérequis (une seule fois)
- **VS Code**, avec un terminal **Git Bash** (pas MSYS2/UCRT64).
- **Python 3.10 ou plus** (python.org, cocher « Add Python to PATH ») et **Node.js 18 ou plus** (nodejs.org).
- Navigateur **Chrome ou Edge** (obligatoire pour la dictée vocale).

## 1. Installer
1. Dézippe `novissi-droit-prototype-v0.4-final.zip`, puis ouvre le dossier racine dans VS Code (Fichier > Ouvrir un dossier).
2. Ouvre un terminal Git Bash (Terminal > Nouveau terminal) et lance `bash run.sh`. Choisis « Installer / vérifier les dépendances » au premier démarrage.
3. Le fichier `.env` est créé. Ouvre-le et colle **tes nouvelles clés** :
   ```
   GEMINI_API_KEY=ta_cle_gemini
   GROQ_API_KEY=ta_cle_groq
   ```
   Pas de guillemets, pas d'espace autour du `=`. Laisse `ADMIN_TOKEN` vide.
   (Si tu avais déjà un `.env`, copie-le dans le nouveau dossier à la place.)

## 2. Récupérer les textes juridiques
```bash
bash scrape.sh
```
- Les URL de départ et les motifs du scraper doivent être vérifiés sur le site réel. Le nombre de pages et de textes n’est pas garanti.
- C'est **long** (plusieurs dizaines de minutes) : 1,5 s de pause entre chaque requête, par politesse envers le site.
- Tu peux l'arrêter (Ctrl+C) et le relancer : il **reprend où il s'est arrêté** et ne retélécharge jamais un PDF déjà enregistré.
- Par défaut 400 pages/PDF par passe. Pour aller plus loin : `bash scrape.sh 1000`.
- À la fin, un rapport s'affiche (`new` = nouveaux textes, `errors` = échecs réseau, relance simplement).

### Suivre et contrôler la collecte
```bash
bash report.sh        # rapport d'exhaustivité : pages inspectées, ressources par statut, extraits / à revoir, erreurs
bash backup.sh        # sauvegarde cohérente (registre, conversations, PDF originaux) dans backups/
```
- Les **PDF originaux** sont conservés dans `data/originals/`, le **registre** dans `data/registry.db` : ne supprime pas ces dossiers.
- Une erreur temporaire (site lent, 503) n'efface rien : la ressource passe en « retry » et est reprise à la prochaine passe.
- Un PDF scanné sans texte est marqué « à revoir » (jamais « traité »). Un PDF corrompu est mis en quarantaine.
- **OTR (avis fonciers)** : renseigne `OTR_BASE_URL` et `OTR_SEEDS` dans `.env` après avoir vérifié l'adresse avec `bash diagnose.sh <url>`.
- **Textes fictifs** : `DEMO_MODE=auto` les utilise seulement tant qu'aucun texte officiel n'est collecté, et l'interface l'indique. Mets `off` en production.
- **Restaurer** une sauvegarde : arrête l'application, puis `tar xzf backups/<fichier>.tgz -C data/`.

## 3. Lancer l’application
Choisis « Lancer frontend + backend » dans `bash run.sh`, ou exécute directement `bash dev.sh`.
Ouvre **http://localhost:5173**. Ctrl+C arrête tout. En tête de log tu dois voir `fournisseurs IA : ['gemini', 'groq']`.

Raccourci VS Code : `Terminal > Exécuter la tâche` propose Installer / Lancer / Actualiser les lois / Diagnostiquer un site.

## 4. Vérifier que l'IA répond
Pose une question dans le chat. Sous la réponse :
- **« ✦ Réponse rédigée par l'IA… »** : tout fonctionne.
- **« IA indisponible : extraits bruts »** : l'IA n'a pas répondu. Regarde le terminal de `dev.sh`, cherche la ligne `Fournisseur gemini indisponible : … (HTTP 4xx …)` :
  - `HTTP 400/401/403` : clé fausse ou refusée, régénère-la.
  - `HTTP 429` : quota gratuit atteint, attends ou utilise Groq.
  - aucun fournisseur listé : le `.env` n'est pas lu (voir dépannage).

## Dépannage
| Problème | Solution |
|---|---|
| `fournisseurs IA : AUCUN` | Le fichier doit s'appeler `.env` (pas `.env.txt`), à la racine, sans guillemets. Relance `bash dev.sh`. |
| `python introuvable` | Réinstalle Python en cochant « Add Python to PATH », rouvre le terminal. |
| `pip install` échoue (opencv, scikit-learn) | Tu es dans MSYS2. Utilise Git Bash avec Python de python.org. |
| Le micro ne marche pas | Ouvrez l’application sur `http://localhost:5173`, autorisez le micro et vérifiez la compatibilité du navigateur. La dictée ne soumet plus automatiquement le texte. |
| La dictée en éwé ou kabyè ne démarre pas | Le navigateur peut ne pas fournir de modèle vocal pour ces langues. La saisie manuelle reste disponible ; un moteur vocal compatible devra être ajouté et évalué. |
| Voix du Togo | Choisissez l’audit Voix du Togo dans `bash run.sh`. Le rapport décrit uniquement ce qui est réellement accessible ; il ne télécharge pas automatiquement des contenus dont les droits ne sont pas établis. |
| `ConnectTimeout` pendant le scraping | Normal (site lent) : 3 essais automatiques. Relance `bash scrape.sh` pour les PDF manqués. |
| Un site ne donne rien | `bash diagnose.sh https://adresse-du-site` explique pourquoi. |
| Le chat ne connaît pas une loi récente | Relance `bash scrape.sh`, puis redémarre `bash dev.sh`. |

## Sécurité
Les anciennes clés qui étaient dans `.env.example` ont circulé : **régénère-les** (Google AI Studio, Groq). Ne mets jamais de clé dans `.env.example`, seulement dans `.env` (ignoré par git).

## Recherche juridique
Le menu « Recherche juridique » interroge le registre (mot-clé, titre, « article 12 ») et affiche la version, l'empreinte, la page, la date de collecte et le lien d'origine. Le statut juridique (en vigueur, abrogé) est toujours indiqué comme **non vérifié**.

## Limites connues
- L’audit Voix du Togo est une étape de découverte, pas un corpus linguistique importé. Les droits et la qualité des ressources doivent être vérifiés.
- La sélection Éwé/Kabiyè ne garantit pas une dictée ni une traduction fiable dans ces langues.
- Chaque PDF est un **numéro entier du Journal Officiel** (plusieurs textes). Le chat cite donc « Article N » avec le lien du numéro d'origine, pas toujours la loi précise.
- Les PDF scannés nécessitent Tesseract et une configuration OCR compatible ; les documents non traités sont à vérifier manuellement.
- Ce chat donne de l'information générale, pas un avis d'avocat.
