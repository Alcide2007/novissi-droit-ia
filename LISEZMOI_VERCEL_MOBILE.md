# Correctif Ultime Mobile & Vercel — Novissi Droit IA

Ce fichier ZIP contient la version **exacte, complète et testée** de l'architecture originale (`novissi-droit-ia/frontend/src/...`), sans aucun fichier parasite et avec la résolution intégrale de tous les bugs mobiles.

---

## 1. Tous les bugs identifiés et corrigés dans cette version

1. **Les 4 messages sous « Comment puis-je vous aider ? »** :
   - **Sur PC (Ordinateur)** : Les 4 cartes de suggestion (`.suggest`) restent **100 % visibles** en grille 2×2.
   - **Sur Mobile (≤ 768 px)** : Les 4 cartes sont **masquées automatiquement** (`display: none !important`) pour offrir une page d'accueil épurée.
2. **Le défilement (Scroll) totalement débloqué sur toutes les pages** :
   - Dans l'ancien `styles.css`, les lignes 293 et 467 forçaient `html, body { position: fixed; overflow: hidden; height: 100%; }` ainsi que `.shell, .main { overflow: hidden !important; }`. Cela paralysait le défilement tactile sur téléphone dans l'accueil, TerraCheck, le Décodeur d'actes, la Génération de courriers et le Guide de prévention.
   - Tout est désormais déverrouillé avec `position: static !important`, `height: auto !important` et `overflow-y: auto !important`.
3. **Le bug critique du voile bloquant (`div.scrim`) corrigé** :
   - Aux lignes 39, 324 et 500 de l'ancien CSS, la règle `.scrim.open, div.scrim { display: block !important; }` forçait l'affichage permanent d'un calque `position: fixed; inset: 0; z-index: 88888` par-dessus toute l'application mobile même quand le menu latéral était fermé ! Ce calque interceptait les gestes du doigt et faisait croire que l'écran ramait ou refusait de défiler.
   - Désormais, `.scrim` reste strictement `display: none !important; pointer-events: none !important;` tant qu'il n'a pas la classe `.scrim.open`.
4. **Fluidité maximale (Anti-Rame sur Mobile)** :
   - Suppression des 3 blocs `@media (max-width: 768px)` contradictoires qui forçaient le navigateur mobile à recalculer les styles en boucle.
   - Utilisation de `translate3d()` pour l'ouverture fluide du tiroir latéral sans saccade GPU.
   - Rafraîchissement automatique (`invalidateSize`) de la carte Leaflet dans `TerraCheckPage.tsx` pour éviter les tuiles grises au chargement sur mobile.
5. **Écriture et mise en page adaptées sur chaque module mobile** :
   - Tailles de police recalibrées pour la lecture sur smartphone (`14.5px` dans le chat, `13px` dans les tableaux cadastraux, titres `h1/h2/h3` proportionnés).
   - Tableaux cadastraux (`fields`), aperçus de courriers (`letter-paper`) et formulaires adaptés à 100 % de la largeur sans débordement horizontal.
   - Champs de saisie à `16px` pour empêcher le zoom brusque sur iPhone (iOS).
   - Barre de saisie du chat (`composer-wrap`) maintenue proprement en bas de l'écran (`position: sticky; bottom: 0`).

---

## 2. Zéro erreur TypeScript sur GitHub Actions & Vercel

Cette archive respecte **strictement** la structure de votre dépôt :
- `novissi-droit-ia/frontend/src/styles.css`
- `novissi-droit-ia/frontend/src/features/TerraCheckPage.tsx` (avec le typage exact `Props = { focus: api.Diag | null; onDecodeParcel?: (d: api.Diag) => void; lang?: Lang; }`)
- `novissi-droit-ia/frontend/src/i18n.ts` (sans doublons de clés Ewé/Kabiyè)

---

## 3. Commandes Git pour déployer proprement sans erreur

Dans votre terminal :

```bash
# 1. Supprimer les 2 fichiers parasites créés lors de l'essai v3 s'ils existent encore
rm -f frontend/src/components/Layout.tsx
rm -f frontend/src/features/HomePage.tsx

# 2. Après avoir copié les 3 fichiers (styles.css, TerraCheckPage.tsx, i18n.ts) dans frontend/src/ :
git pull --rebase origin main
git add .
git commit -m "fix(mobile): unlock mobile scroll, hide suggestions on mobile only, fix scrim bug"
git push origin main
```
