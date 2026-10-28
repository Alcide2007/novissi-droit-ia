# Correctifs Vercel + mobile

## Erreurs de build Vercel (13 erreurs TypeScript, `tsc && vite build` s'arrêtait)
1. `frontend/src/features/TerraCheckPage.tsx` : importait `translateCheckLabel`, qui n'existe pas. La fonction s'appelle `translateCheckLevel`.
2. `frontend/src/i18n.ts` : 12 clés écrites deux fois dans le même objet (Ewé : lignes 410-415 ; Kabiyè : 552-557). Doublons supprimés.
   ATTENTION Kabiyè : les doublons supprimés contenaient des mots qui semblent de l'Ewé (ex. « Ʋɔnudrɔ̃ƒe », « Fenyila »).
   On garde donc les premières valeurs. À faire relire par un locuteur kabiyè.

## Mobile (`frontend/src/styles.css`, bloc « MOBILE » à la fin)
- Barre du haut sur une seule ligne (thème et partage en icônes, langue lisible).
- Plus d'ombre grise parasite à gauche quand le menu est fermé.
- Champs à 16 px (évite le zoom automatique sur iPhone), zones tactiles plus grandes, carte adaptée à l'écran.

## Réglages Vercel
Root Directory : `frontend` · Framework : Vite · Build : `npm run build` · Output : `dist`.
Le backend est sur Render (voir `frontend/vercel.json`) : y mettre GROQ_MODEL=openai/gpt-oss-120b et la clé Groq.
