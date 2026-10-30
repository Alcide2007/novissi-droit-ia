# Correctif Ultime ZIP — Anti-Boucle Éwé/Kabiyè (Triple Bouclier) & Optimisation Mobile

Ce fichier ZIP contient tous les fichiers prêts à être copiés dans votre dépôt :
1. `novissi-droit-ia/frontend/src/i18n.ts` :
   - Intègre `sanitizeLocalText()` qui coupe au millimètre toutes les boucles de répétition (`ɖe wò le ɣleti...`, `ɖokui le nu vɔ̃ le...`, `ɖe ɖe ɖe...`).
   - Intègre le **Triple Bouclier Automatique** (`installTripleAntiLoopShield()` + `installDomAntiLoopObserver()`) qui :
     1. Intercepte automatiquement toutes les réponses JSON de `window.fetch` avant que React ne les affiche.
     2. Nettoie automatiquement les anciennes discussions déjà enregistrées dans le `localStorage` du navigateur.
     3. Surveille le DOM en temps réel (`MutationObserver`) pour corriger tout texte affiché dans `.md`, `.bubble`, `.turn`.
2. `novissi-droit-ia/frontend/src/styles.css` :
   - Défilement mobile 100 % débloqué sur toutes les pages.
   - Masquage des 4 cartes de suggestion sur mobile uniquement (conservées en 2x2 sur PC).
   - Correction du voile `div.scrim` et optimisation GPU anti-rame.
3. `novissi-droit-ia/frontend/src/features/TerraCheckPage.tsx` :
   - Typage TypeScript strict pour passer le build GitHub Actions / Vercel sans erreur + `invalidateSize()` Leaflet sur mobile.
4. `novissi-droit-ia/backend/translator.py` :
   - Algorithme `dedupe_repetitions()` côté serveur, protection du Markdown (`**`, `[1]`) avant traduction GTX et paramètres `LLM_ANTI_LOOP_PARAMS`.
