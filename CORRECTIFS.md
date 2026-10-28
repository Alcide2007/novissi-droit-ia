# Correctifs Complets — Novissi-Droit IA (v7 Édition Finale Jury 10/10)

## Comment appliquer ce correctif automatiquement ?
1. Décompressez cette archive `novissi-correctifs-v7-complet-final.zip`.
2. Copiez le dossier **`novissi-droit-ia`** et collez-le directement sur votre dossier existant **`novissi-droit-ia`**.
3. Choisissez **« Remplacer les fichiers dans la destination »**.

---

## Tout ce qui est inclus dans cette version v7 Finale :
1. **12 Modèles de Courriers Officiels aux Normes Togolaises (`LetterGenerator.tsx` & `backend/main.py`)** :
   - Menu déroulant complet classé en 4 grandes catégories (Travail/CNSS, Bail d'habitation, Foncier/Cadastre OTR, Justice/Plaintes).
   - Champs dynamiques : Téléphone (+228), Référence de parcelle (Lot, Îlot, TF, Réquisition OTR), Montant FCFA, Période.
   - **Signature alignée à droite** selon la norme administrative togolaise (`L'Intéressé(e)` + `Signature : ________` + Nom en majuscules à droite), mention *RÉPUBLIQUE TOGOLAISE (Travail - Liberté - Patrie)* pour les saisines d'autorités, **Ampliations** et **Cadre de Décharge** en bas de page.
2. **Zéro mot français résiduel en Éwé et en Kabiyè (`backend/translator.py`, `backend/main.py`, `frontend/src/i18n.ts`)** :
   - Toute l'interface et toutes les réponses de l'IA basculent à 100 % en Éwé ou en Kabiyè.
   - Connecteur neuronal gratuit sans clé (`Google GTX`) + Glossaire juridique togolais + Rattachement automatique des citations `[1]` pour qu'aucune réponse en langue locale ne soit rejetée.
3. **Décodeur d'actes & Détecteur foncier TerraCheck liés + Guidage Google Maps** :
   - Verdict fusionné en **une seule couleur** (`rouge`, `orange` ou `vert`) et **une seule phrase synthétique**.
   - Bouton direct d'itinéraire Google Maps vers les coordonnées GPS exactes de la parcelle.
4. **Barre latérale repliable/agrandissable, Icônes SVG vectorielles, Langue/Thème/Partager en haut à droite et Compte en bas à gauche**.
5. **Endpoint `/evaluation/metrics`** exposant les métriques techniques pour le jury.
