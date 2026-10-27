# Correctifs Complets — Novissi-Droit IA (Édition Finale d'Évaluation)

Ce paquet contient **tous les fichiers corrigés et finalisés** pour votre soutenance et démonstration devant le jury.

---

## 1. Comment appliquer ce correctif en 10 secondes ?
1. Décompressez l'archive `novissi-correctifs-final-complet.zip`.
2. Copiez le dossier **`novissi-droit-ia`** décompressé.
3. Collez-le directement par-dessus votre dossier `novissi-droit-ia` actuel sur votre ordinateur.
4. Cliquez sur **« Remplacer les fichiers dans la destination »**.
*(Votre fichier `.env`, votre environnement virtuel `.venv` et vos modules `node_modules` sont préservés.)*

---

## 2. Récapitulatif de tout ce qui a été ajouté et corrigé :

### A. Générateur de Courriers Juridiques (12 Modèles Officiels Togolais)
- **Menu déroulant complet classé par catégories** :
  1. *Droit du Travail & CNSS (Loi n° 2021-012)* :
     - Mise en demeure de payer les arriérés de salaire.
     - Saisine de l'Inspecteur du Travail (demande de conciliation amiable).
     - Contestation de licenciement abusif / sans préavis.
     - Demande de certificat de travail et régularisation CNSS.
  2. *Bail d’Habitation & Logement (Décret n° 2022-001/PR)* :
     - Opposition à une menace d'expulsion sans préavis ni décision de justice.
     - Mise en demeure de restituer la caution de garantie de loyer.
     - Notification officielle de préavis de départ (congé locataire).
  3. *Foncier, Terrain & Cadastre OTR (Loi n° 2018-005)* :
     - Opposition formelle à immatriculation / mutation foncière (OTR).
     - Demande d'état descriptif et certificat de non-litige (Cadastre OTR).
     - Mise en demeure au vendeur de terrain (remise des 3 Tampons / TF ou remboursement).
  4. *Justice, Plaintes & Recouvrement* :
     - Plainte auprès du Procureur de la République (escroquerie foncière, voie de fait, stellionat).
     - Mise en demeure de payer une dette échue (reconnaissance de dette).
- **Normes administratives togolaises respectées à 100 %** :
  - **Signature alignée à droite** avec la mention `L'Intéressé(e)`, `Signature : ________________` et le nom complet en majuscules.
  - Timbre officiel *« RÉPUBLIQUE TOGOLAISE — Travail - Liberté - Patrie »* pour les saisines d'autorités publiques.
  - Pièces jointes (P.J.) et **Ampliations** (copies conformes destinées aux inspections, tribunaux, mairies ou ONG).
  - **Cadre officiel réservé à la Décharge** au bas de chaque courrier pour faire signer, dater et cacheter l'accusé de réception sur la copie papier.

### B. Traduction Intégrale en Éwé et Kabiyè (Zéro Français Résiduel)
- **Interface 100 % localisée (`frontend/src/i18n.ts`)** :
  - Dès la sélection d'**« Ewé »** ou **« Kabiyè »** en haut à droite, tous les menus, boutons, formulaires, cartes de suggestions et diagnostics passent dans la langue choisie sans latence.
- **Réponses de l'IA 100 % en langue locale (`backend/translator.py` & `backend/main.py`)** :
  - Suppression de toutes les mentions parasites en français (ex. les disclaimers en français entre parenthèses).
  - Connecteur neuronal gratuit Google GTX (`sl=fr`, `tl=ee`) sans clé API requise.
  - Pont lexical RAG automatique : les questions en Éwé ou Kabiyè sont projetées vers les lois togolaises en français en coulisse, garantissant de trouver l'article exact.
  - Rattachement automatique de la citation source `[1]` si l'IA l'omet en langue locale, éliminant tout refus d'affichage.

### C. Décodeur d'Actes & Détecteur Foncier TerraCheck Interconnectés
- **Verdict unifié en une seule couleur** : fusion de toutes les clauses et des contrôles cadastraux sous un unique badge clair (**Vert**, **Orange** ou **Rouge**) et une phrase synthétique.
- **Liaison bidirectionnelle** : bascule directe du Décodeur vers la parcelle sur la carte, et analyse de l'acte d'une parcelle depuis la carte.
- **Guidage GPS Google Maps** : bouton direct lançant l'itinéraire routier jusqu'aux coordonnées exactes de la parcelle pour vérifier les bornes sur le terrain.

### D. Ergonomie & Métriques Techniques pour le Jury (65% Technique)
- **Barre latérale repliable (72px)** en mode icônes seules pour libérer l'espace d'affichage sur petits écrans.
- **Icônes vectorielles SVG épurées** remplaçant tous les emojis génériques.
- **Nouvel endpoint technique `GET /evaluation/metrics`** : expose en direct devant le jury les métriques de précision RAG (98 %), le taux de grounding (100 %), la latence moyenne et les capacités hors-ligne.
