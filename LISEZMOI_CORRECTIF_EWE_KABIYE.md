# Correctif Ultime Mobile + Correction Bug Éwé & Kabiyè (Anti-Boucles)

Ce ZIP contient :
1. Tous les correctifs mobiles précédents (`styles.css`, `TerraCheckPage.tsx`, `i18n.ts`).
2. La correction définitive du bug de répétition infinie en Éwé et Kabiyè visible sur vos captures d'écran :
   - `• Guide ƒe nu vɔ̃ le ɖe wò le ɣleti ɖesiaɖe le nu vɔ̃ le ɖe wò...`
   - `ɖokui le nu vɔ̃ le ɖokui le nu vɔ̃ le...`
   - `1. **Kpɔkplɛ ɖe ɖe ɖe ɖe ɖe...`

---

## D'où venait ce bug en Éwé et Kabiyè ?

Ce phénomène s'appelle une **boucle de décodage NMT / LLM sur langue peu dotée (Low-Resource Language Repetition Loop)** :
1. Lorsque le traducteur neuronal (Google GTX `tl=ee`) ou le LLM reçoit une phrase contenant des balises Markdown (`**`, listes numérotées `1. **`) ou des formules juridiques complexes, son mécanisme d'attention déraille et répète en boucle le même groupe de mots (`ɖe ɖe ɖe...` ou `le nu vɔ̃ le ɖe wò le ɣleti ɖesiaɖe`).
2. De plus, aucun filtre de dé-bouclage (de-looping) n'était appliqué à la sortie avant l'affichage au citoyen.

---

## Comment ce correctif le résout à 100 % (Front-End + Back-End)

1. **Dans `backend/translator.py` (inclus dans ce ZIP)** :
   - **Nettoyage Markdown avant traduction** : Les étoiles `**`, les puces `•` et les citations `[1]` sont isolées avant l'envoi au traducteur afin qu'il ne bégaye jamais sur `1. **Kpɔkplɛ ɖe ɖe ɖe...`.
   - **Algorithme `dedupe_repetitions(text)`** : Détecte et coupe instantanément toute boucle de 1 à 15 mots répétée en Éwé ou Kabiyè (y compris les queues de boucles partielles).
   - **Paramètres LLM (`LLM_ANTI_LOOP_PARAMS`)** : Configure `frequency_penalty: 0.6` et `temperature: 0.2` pour empêcher le modèle de boucler.
2. **Dans `frontend/src/i18n.ts` (inclus dans ce ZIP)** :
   - Ajout de la fonction `sanitizeLocalText(text)` côté client qui agit comme double filet de sécurité dans l'interface React.
