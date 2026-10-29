# Correctifs d'Optimisation Mobile (Vercel)

Ce patch contient l'ensemble des correctifs pour garantir une expérience fluide sur téléphone, débloquer le défilement et supprimer les lenteurs.

## Problèmes résolus :
1. **Défilement bloqué** : Suppression des verrous `overflow: hidden` et `height: 100vh` sur `#root` et `body`. Ajout de `min-height: 100dvh` pour s'adapter aux barres d'URL des navigateurs mobiles.
2. **Lenteur et surchauffe (Rame sur mobile)** : Désactivation des effets `backdrop-filter: blur()` très gourmands en ressources GPU sur téléphone.
3. **Mise en page tronquée** : Ajout d'un espacement en bas (`padding-bottom: calc(85px + env(safe-area-inset-bottom))`) pour éviter que la barre de navigation ne cache le contenu ou les boutons.
4. **Page d'accueil simplifiée** : Suppression des 4 cartes de suggestion comme demandé.
5. **Ergonomie** : Agrandissement des zones cliquables (boutons de `48px` minimum), ajustement de la taille de police (`16px` sur les inputs pour éviter le zoom automatique sur iOS).

## Fichiers modifiés / à remplacer :
- `src/styles.css` : Le fichier clé. Remplacez ou fusionnez avec vos styles actuels.
- `src/features/HomePage.tsx` (ou `ChatPage.tsx`) : Exemple montrant la suppression de la grille de suggestions.
- `src/features/TerraCheckPage.tsx` : Vérification qu'aucune contrainte de hauteur n'est définie.
- `src/components/Layout.tsx` (Optionnel) : Structure recommandée pour le conteneur principal.

## Instructions de déploiement :
1. Extrayez ces fichiers dans votre projet frontend.
2. Vérifiez que votre structure de composants (ex: balise `<main>`) correspond aux classes ciblées dans `styles.css`.
3. Lancez `npm run build` puis déployez sur Vercel.
