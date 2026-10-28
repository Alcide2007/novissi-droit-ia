import type { Lang } from "./api";

export type UI = {
  slogan: string;
  newChat: string;
  navChat: string;
  navDocs: string;
  navActe: string;
  navTerra: string;
  navPrev: string;
  titleChat: string;
  titleDocs: string;
  titleActe: string;
  titleTerra: string;
  titlePrev: string;
  downloadPdf: string;
  writeRecommendedLetter: string;
  voiceModeBtn: string;
  historyLabel: string;
  searchConvPlaceholder: string;
  noConv: string;
  signIn: string;
  signInSub: string;
  accountSaveNote: string;
  switchAccount: string;
  logout: string;
  continueGoogle: string;
  continueApple: string;
  continueMicrosoft: string;
  useEmail: string;
  hideEmail: string;
  saveAccount: string;
  share: string;
  themeLight: string;
  themeDark: string;
  greeting: string;
  heroTitle: string;
  suggestions: [string, string, string, string];
  langWarning: string;
  searchingLaws: string;
  loading: string;
  questionPlaceholder: string;
  listenResponse: string;
  stopListening: string;
  copyResponse: string;
  aiDraftedNote: string;
  degradedNote: string;
  demoNote: string;
  sourcesTitle: string;
  copyRef: string;
  refCopied: string;
  originalSource: string;
  unverifiedStatus: string;
  verifiedStatus: string;
  footerDisclaimer: string;
  // Décodeur d'actes
  acteIntro: string;
  photoActe: string;
  sample1: string;
  sample2: string;
  sample3: string;
  actePlaceholder: string;
  analyzeActe: string;
  analyzing: string;
  extractedInfo: string;
  buyerLabel: string;
  areaLabel: string;
  lotLabel: string;
  ilotLabel: string;
  seeOnMap: string;
  mapsItinerary: string;
  switchToTerra: string;
  verdictRougeDefault: string;
  verdictOrangeDefault: string;
  verdictVertDefault: string;
  noParcelMatch: string;
  ambiguousParcelMatch: string;
  // Détecteur foncier TerraCheck
  terraIntro: string;
  terraSearchPlaceholder: string;
  analyzeThisActe: string;
  gpsCoords: string;
  communeQuartier: string;
  legalStatus: string;
  refTitreOtr: string;
  check3Tampons: string;
  tamponsComplete: string;
  tamponsMissing: string;
  tamponsPending: string;
  registeredOwner: string;
  customaryOrigin: string;
  securityChecks: string;
  mutationHistory: string;
  recommendation: string;
  scoreLabels: { vert: string; orange: string; rouge: string };
  // Génération de courriers (12 modèles)
  letterType: string;
  groupTravail: string;
  groupBail: string;
  groupFoncier: string;
  groupJustice: string;
  letterSalaire: string;
  letterInspectionTravail: string;
  letterLicenciement: string;
  letterCertificat: string;
  letterBail: string;
  letterRestitutionCaution: string;
  letterPreavisLocataire: string;
  letterOppFoncier: string;
  letterEtatDescriptif: string;
  letterMiseDemeureVendeur: string;
  letterPlainte: string;
  letterDette: string;
  fullName: string;
  yourAddress: string;
  employer: string;
  landlord: string;
  city: string;
  amountDue: string;
  unpaidPeriod: string;
  unpaidPeriodPlaceholder: string;
  extraDetails: string;
  generateLetter: string;
  generatingLetter: string;
  copy: string;
  download: string;
  whereToGo: string;
  refTexts: string;
  letterIntro: string;
  destLabelOtr: string;
  destLabelProc: string;
  destLabelVendeur: string;
  destLabelDebiteur: string;
  telTogo: string;
  parcelRef: string;
};

export const I18N: Record<Lang, UI> = {
  Français: {
    slogan: "L’avocat du peuple",
    newChat: "Nouveau chat",
    navChat: "Assistant juridique",
    navDocs: "Génération de courriers",
    navActe: "Décodeur d’actes",
    navTerra: "Détecteur foncier",
    navPrev: "Prévention Achat Terrain",
    titleChat: "Assistant juridique",
    titleDocs: "Génération de courriers",
    titleActe: "Analyse d’actes",
    titleTerra: "TerraCheck : vérification foncière",
    titlePrev: "Guide de prévention avant d’acheter un terrain au Togo",
    downloadPdf: "Télécharger en PDF (Modèle officiel)",
    writeRecommendedLetter: "Rédiger ce courrier maintenant",
    voiceModeBtn: "Mode Vocal (Speech-to-Speech FR)",
    historyLabel: "Vos discussions",
    searchConvPlaceholder: "Rechercher une conversation",
    noConv: "Aucune conversation.",
    signIn: "Se connecter",
    signInSub: "Google, Apple, E-mail",
    accountSaveNote: "Sauvegardez vos discussions juridiques, vos courriers et vos vérifications foncières TerraCheck.",
    switchAccount: "Changer de compte",
    logout: "Se déconnecter",
    continueGoogle: "Continuer avec Google",
    continueApple: "Continuer avec Apple",
    continueMicrosoft: "Continuer avec Microsoft",
    useEmail: "Utiliser une adresse e-mail",
    hideEmail: "Masquer le formulaire e-mail",
    saveAccount: "Enregistrer le compte",
    share: "Partager",
    themeLight: "Thème clair",
    themeDark: "Thème sombre",
    greeting: "Bonjour, citoyen togolais",
    heroTitle: "Comment puis-je vous aider sur le droit togolais ?",
    suggestions: [
      "Quels sont mes droits si mon salaire n’est pas payé ?",
      "Que dit le droit togolais sur l’expulsion d’un locataire ?",
      "Comment vérifier un titre foncier avant d’acheter un terrain ?",
      "Retrouver un article précis du Code du travail.",
    ],
    langWarning: "",
    searchingLaws: "Analyse approfondie des textes de loi togolais en cours…",
    loading: "Chargement…",
    questionPlaceholder: "Posez votre question sur le droit togolais",
    listenResponse: "Écouter la réponse",
    stopListening: "Arrêter la lecture",
    copyResponse: "Copier la réponse",
    aiDraftedNote: "Réponse rédigée par l’IA à partir des textes officiels cités ci-dessous.",
    degradedNote: "IA indisponible : extraits bruts des textes, sans reformulation.",
    demoNote: "Cette réponse s’appuie sur des textes de démonstration fictifs, pas sur des textes officiels.",
    sourcesTitle: "Sources juridiques",
    copyRef: "Copier la référence",
    refCopied: "Référence copiée",
    originalSource: "Source d’origine",
    unverifiedStatus: "statut juridique non vérifié (en vigueur ? abrogé ?)",
    verifiedStatus: "statut juridique vérifié",
    footerDisclaimer: "Information générale, pas un avis d’avocat. Parcelles de démonstration fictives.",
    acteIntro: "Photographiez ou collez un acte foncier ou un contrat pour obtenir un verdict immédiat et localiser la parcelle.",
    photoActe: "Photographier un acte",
    sample1: "Essayer avec un acte d’exemple",
    sample2: "Exemple : Double vente (Kégué)",
    sample3: "Exemple : Acte notarié (Baguida)",
    actePlaceholder: "Collez ou photographiez le texte de l’acte…",
    analyzeActe: "Analyser l’acte",
    analyzing: "Analyse…",
    extractedInfo: "Informations extraites",
    buyerLabel: "Acquéreur",
    areaLabel: "Superficie (m²)",
    lotLabel: "Lot",
    ilotLabel: "Îlot",
    seeOnMap: "Voir sur la carte",
    mapsItinerary: "Itinéraire Google Maps",
    switchToTerra: "Détecteur foncier",
    verdictRougeDefault: "Risque élevé détecté (double vente, litige ou clause abusive) : ne signez pas cet acte et ne versez aucun acompte avant vérification à l’OTR.",
    verdictOrangeDefault: "Vigilance requise : faites vérifier le Titre Foncier, les 3 tampons et le bornage contradictoire par un notaire avant de signer.",
    verdictVertDefault: "Acte et parcelle conformes aux données cadastrales disponibles : vous pouvez poursuivre la transaction devant votre notaire.",
    noParcelMatch: "Aucune parcelle du registre ne correspond à cet acte : faites vérifier au cadastre de l’OTR.",
    ambiguousParcelMatch: "Plusieurs parcelles correspondent : précisez le quartier ou l’îlot.",
    terraIntro: "Sélectionnez une parcelle pour vérifier sa conformité cadastrale (OTR / 3 Tampons), analyser son acte ou lancer l’itinéraire Google Maps.",
    terraSearchPlaceholder: "Rechercher un quartier (Agoè, Kégué, Baguida…), lot ou TF",
    analyzeThisActe: "Analyser l’acte",
    gpsCoords: "Coordonnées GPS",
    communeQuartier: "Commune / Quartier",
    legalStatus: "Statut juridique",
    refTitreOtr: "Réf. Titre / OTR",
    check3Tampons: "Vérification « 3 Tampons »",
    tamponsComplete: "Complet (Géomètre, Chef/Mairie, Cadastre OTR)",
    tamponsMissing: "Absent (Risque élevé)",
    tamponsPending: "En attente de visa cadastral",
    registeredOwner: "Propriétaire inscrit",
    customaryOrigin: "Origine coutumière",
    securityChecks: "Contrôles de sécurité foncière",
    mutationHistory: "Historique des mutations",
    recommendation: "Recommandation",
    scoreLabels: { vert: "vert", orange: "orange", rouge: "rouge" },
    letterType: "Type de courrier",
    groupTravail: "1. Droit du Travail & CNSS (Loi n° 2021-012)",
    groupBail: "2. Bail d’Habitation & Logement (Décret n° 2022-001/PR)",
    groupFoncier: "3. Foncier, Terrain & Cadastre OTR (Loi n° 2018-005)",
    groupJustice: "4. Justice, Plaintes & Créances au Togo",
    letterSalaire: "Mise en demeure de payer les arriérés de salaire",
    letterInspectionTravail: "Saisine de l’Inspection du Travail (Demande de conciliation)",
    letterLicenciement: "Contestation de licenciement abusif / sans préavis",
    letterCertificat: "Demande de certificat de travail et régularisation CNSS",
    letterBail: "Opposition à une menace d’expulsion sans préavis ni jugement",
    letterRestitutionCaution: "Mise en demeure de restituer la caution de loyer",
    letterPreavisLocataire: "Notification de préavis de départ par le locataire (Congé)",
    letterOppFoncier: "Opposition à immatriculation / mutation foncière (OTR)",
    letterEtatDescriptif: "Demande d’état descriptif et certificat de non-litige (Cadastre OTR)",
    letterMiseDemeureVendeur: "Mise en demeure au vendeur de terrain (3 Tampons / TF ou remboursement)",
    letterPlainte: "Plainte auprès du Procureur de la République (Escroquerie foncière, voie de fait…)",
    letterDette: "Mise en demeure de rembourser une dette / reconnaissance de dette",
    fullName: "Votre nom complet",
    yourAddress: "Votre adresse",
    employer: "Employeur / Société",
    landlord: "Propriétaire / Bailleur",
    city: "Ville (Togo)",
    amountDue: "Montant (FCFA)",
    unpaidPeriod: "Période concernée",
    unpaidPeriodPlaceholder: "ex. juillet à septembre 2026",
    extraDetails: "Précisions (facultatif)",
    generateLetter: "Générer le courrier",
    generatingLetter: "Rédaction…",
    copy: "Copier",
    download: "Télécharger",
    whereToGo: "Où vous adresser",
    refTexts: "Textes de référence",
    letterIntro: "Modèles rédigés selon la norme administrative et juridique de la République Togolaise (avec références légales, ampliations et cadre de décharge).",
    destLabelOtr: "Autorité OTR destinataire",
    destLabelProc: "Personne visée ou Parquet",
    destLabelVendeur: "Vendeur / Démarcheur",
    destLabelDebiteur: "Débiteur",
    telTogo: "Téléphone (Togo)",
    parcelRef: "Référence de la parcelle (Quartier, Lot, Îlot, TF ou Réquisition OTR)",
  },
  Ewé: {
    slogan: "Dukɔa ƒe senyala",
    newChat: "Dzeɖoɖo yeye",
    navChat: "Senyawo ƒe kpekpeɖeŋu",
    navDocs: "Agbalẽŋɔŋlɔ",
    navActe: "Agbalẽwo me ɖeɖe",
    navTerra: "Anyigba dodokpɔ",
    navPrev: "Afɔɖeɖe 7 hafi aƒle anyigba",
    titleChat: "Senyawo ƒe kpekpeɖeŋu (Assistant juridique)",
    titleDocs: "Agbalẽŋɔŋlɔ (Génération de courriers)",
    titleActe: "Agbalẽwo me ɖeɖe (Analyse d’actes)",
    titleTerra: "TerraCheck : Anyigba dodokpɔ",
    titlePrev: "Afɔɖeɖe 7 siwo hiã hafi nàƒle anyigba le Togo",
    downloadPdf: "Wɔ PDF kopie (Modèle officiel)",
    writeRecommendedLetter: "Ŋlɔ agbalẽ sia fifia",
    voiceModeBtn: "Nuƒoƒo ƒe mɔnu (FR)",
    historyLabel: "Wò dzeɖoɖowo",
    searchConvPlaceholder: "Di dzeɖoɖo aɖe",
    noConv: "Dzeɖoɖo aɖeke meli o.",
    signIn: "Ge ɖe eme",
    signInSub: "Google, Apple, E-mail",
    share: "Ma kple amewo",
    themeLight: "Kekeli",
    themeDark: "Viviti",
    greeting: "Woezɔ, Togovi",
    heroTitle: "Aleke mate ŋu akpe ɖe ŋuwò le Togo ƒe sewo ŋu ?",
    suggestions: [
      "Dɔwɔtɔnye mexe fetu nam o, nu ka mawɔ ?",
      "Aƒetɔ la di be yeanya mí le xɔa me préavis manɔmee, se ɖe mɔa ?",
      "Nu kawo mado akpɔ le Cadastre (OTR) kple Titre Foncier ŋu hafi aƒle anyigba ?",
      "Di Togo ƒe dɔwɔse (Code du travail) ƒe kpukpui aɖe nam.",
    ],
    langWarning: "Ŋuɖoɖo siwo le Eʋegbe me la tso AI gbɔ : Togo ƒe se ƒe agbalẽ si le Fransegbe me lae nye kpeɖodzi.",
    searchingLaws: "Míele Togo ƒe se ƒe agbalẽwo me dzrom…",
    questionPlaceholder: "Bia nya si le dziwò le Togo ƒe sewo ŋu (Eʋegbe alo Fransegbe)…",
    listenResponse: "See (Écouter)",
    stopListening: "Tɔ (Arrêter)",
    copyResponse: "Kɔpi ŋuɖoɖoa",
    aiDraftedNote: "AI ye ŋlɔ ŋuɖoɖo sia tso Togo ƒe se siwo wohe ɖe ete la me.",
    degradedNote: "AI meli fifia o : se ƒe kpukpui ŋutɔŋutɔwoe nye esia.",
    demoNote: "Kpɔɖeŋu ƒe nuŋlɔɖiwo dzi wotu ŋuɖoɖo sia ɖo.",
    sourcesTitle: "Se ƒe agbalẽ siwo dzi wotu ŋuɖoɖoa ɖo",
    copyRef: "Kɔpi se ƒe ŋkɔ",
    originalSource: "Se ƒe agbalẽ",
    footerDisclaimer: "Nyatakaka gbadzaa ko esia nye, menye senyala (avocat) ƒe aɖaŋuɖoɖo o.",
    acteIntro: "Ɖe foto alo da anyigbagbalẽ alo nubabla ƒe nyawo ɖe afii be míado eƒe dedienɔnɔ akpɔ.",
    photoActe: "Ɖe foto agbalẽa",
    sample1: "Kpɔɖeŋu : Agoè-Nyivé, lot 14",
    sample2: "Kpɔɖeŋu : Anyigba dzra zi eve (Kégué)",
    sample3: "Kpɔɖeŋu : Notaire ƒe agbalẽ (Baguida)",
    actePlaceholder: "Da agbalẽa ƒe nyawo ɖe afii alo ɖe eƒe foto…",
    analyzeActe: "Do agbalẽa kpɔ",
    analyzing: "Dodokpɔ le edzi…",
    extractedInfo: "Nyatakaka siwo míekpɔ le agbalẽa me",
    seeOnMap: "Kpɔe le anyigbatata dzi",
    mapsItinerary: "Mɔfiafia (Google Maps)",
    switchToTerra: "Anyigba dodokpɔ",
    terraIntro: "Tia anyigba aɖe be nàdo eƒe Titre Foncier (OTR / Kpeɖodzi 3) akpɔ alo nàdi mɔ ɖe egbɔ to Google Maps dzi.",
    terraSearchPlaceholder: "Di nuto (Agoè, Kégué, Baguida…), lot alo TF",
    analyzeThisActe: "Do agbalẽa kpɔ",
    gpsCoords: "GPS ƒe nɔƒe",
    communeQuartier: "Nuto / Kɔƒe",
    legalStatus: "Se ƒe nɔnɔme",
    refTitreOtr: "Titre / OTR ƒe xexlẽdzesi",
    check3Tampons: "Kpeɖodzi 3 (3 Tampons)",
    registeredOwner: "Anyigbatɔ ƒe ŋkɔ",
    customaryOrigin: "Ƒome si tɔ wònye",
    securityChecks: "Anyigba ƒe dedienɔnɔ dodokpɔ",
    mutationHistory: "Anyigba ƒe dzradzra xoxowo",
    recommendation: "Aɖaŋuɖoɖo",
    letterType: "Agbalẽ ƒe ƒomevi",
    groupTravail: "1. Dɔwɔse (Code du travail)",
    groupBail: "2. Xɔhaya ƒe se (Bail)",
    groupFoncier: "3. Anyigbase kple Cadastre OTR",
    groupJustice: "4. Nyafɔfɔ kple Fe",
    letterSalaire: "Fetu maxemaxe : agbalẽ sẽŋu (mise en demeure)",
    letterInspectionTravail: "Te ɖe dɔwɔnyawo kpɔƒe ŋu",
    letterLicenciement: "Nyanya le dɔme le se madi dzi",
    letterCertificat: "Bia dɔwɔwɔ ƒe agbalẽ kple CNSS",
    letterBail: "Xɔhaya : nyanya le xɔ me préavis manɔmee",
    letterRestitutionCaution: "Bia wò caution si nètsɔ da ɖi la",
    letterPreavisLocataire: "Xɔhayatɔ ƒe gbeɖeɖe ɖi (préavis)",
    letterOppFoncier: "Tsitre ɖe anyigba ŋlɔŋlɔ ɖe ame bubu ŋkɔ me (OTR)",
    letterEtatDescriptif: "Bia anyigba ƒe nɔnɔme nyateƒe (Cadastre)",
    letterMiseDemeureVendeur: "Bia Titre Foncier / Tampons 3 tso nudzrala gbɔ",
    letterPlainte: "Nyadzɔdzɔ (Plainte) ɖe ame aɖe ŋu le ʋɔnudrɔ̃ƒe",
    letterDette: "Bia wò fe si wodu",
    fullName: "Wò ŋkɔ blibo",
    yourAddress: "Nɔƒewò (Adresse)",
    employer: "Dɔwɔtɔ (Employeur)",
    landlord: "Aƒetɔ (Propriétaire)",
    destLabelOtr: "OTR ƒe amegã",
    destLabelProc: "Ame si ŋu nèfo nya ɖo alo Ʋɔnudrɔ̃ƒe",
    destLabelVendeur: "Nudzrala",
    destLabelDebiteur: "Fenyila",
    city: "Du (Ville)",
    telTogo: "Kaƒoƒo (Togo)",
    parcelRef: "Anyigba ƒe xexlẽdzesi (TF, Lot, OTR)",
    amountDue: "Ga home (FCFA)",
    unpaidPeriod: "Ɣeyiɣi si ƒe fetu womexe o",
    unpaidPeriodPlaceholder: "kpɔɖeŋu : Siamlɔm va se ɖe Anyɔnyɔ 2026",
    extraDetails: "Nya bubuwo (ne ehiã)",
    generateLetter: "Ŋlɔ agbalẽa",
    generatingLetter: "Ŋɔŋlɔ le edzi…",
    copy: "Kɔpi",
    download: "Wɔ kopie (Télécharger)",
    whereToGo: "Teƒe siwo nàte ŋu ayi",
    refTexts: "Se ƒe kpukpuiwo",
    letterIntro: "Togo ƒe dziɖuɖu ƒe sewo nu wotua agbalẽ siawo ɖo.",
    accountSaveNote: "Dzra wò dzeɖoɖowo ɖo.",
    switchAccount: "Trɔ akɔnta",
    logout: "Do go le eme",
    continueGoogle: "Yi edzi kple Google",
    continueApple: "Yi edzi kple Apple",
    continueMicrosoft: "Yi edzi kple Microsoft",
    useEmail: "Zã E-mail",
    hideEmail: "Ɣla E-mail",
    saveAccount: "Dzra akɔntaa ɖo",
    loading: "Ele dɔ wɔm…",
    refCopied: "Wokɔpi ŋkɔa",
    unverifiedStatus: "womedo se sia ƒe dɔwɔwɔ kpɔ haɖe o",
    verifiedStatus: "wodo se sia kpɔ",
    buyerLabel: "Nuƒlela (Acquéreur)",
    areaLabel: "Kekeme (m²)",
    lotLabel: "Lot",
    ilotLabel: "Îlot",
    verdictRougeDefault: "Afɔku gã aɖe dze (anyigba dzra zi eve alo nya baɖa le agbalẽa me) : megade asi agbalẽ sia te o eye megaxe ga aɖeke hafi ayi OTR o.",
    verdictOrangeDefault: "Kpɔ nyuie : na Notaire nàdo Titre Foncier, kpeɖodzi 3 (3 tampons) kple anyigba ƒe liƒowo kpɔ hafi nàde asi ete.",
    verdictVertDefault: "Agbalẽa kple anyigbaa sɔ ɖe Cadastre ƒe sewo nu : nàte ŋu ayi edzi le wò Notaire ŋkume.",
    noParcelMatch: "Anyigba sia medze le míaƒe agbalẽ me o : yi ɖado eŋu kpɔ le OTR Cadastre.",
    ambiguousParcelMatch: "Anyigba geɖe sɔ kple esia : yɔ nuto alo îlot ƒe ŋkɔ nyuie.",
    tamponsComplete: "Eblibo (Géomètre, Fia/Mairie, Cadastre OTR)",
    tamponsMissing: "Meli o (Afɔku gã)",
    tamponsPending: "Wole edzrom le Cadastre",
    scoreLabels: { vert: "nyui (vert)", orange: "nudodokpɔ (orange)", rouge: "afɔku (rouge)" },
    destLabelOtr: "OTR amegã",
    destLabelProc: "Ʋɔnudrɔ̃ƒe alo amefuna",
    destLabelVendeur: "Nudzrala",
    destLabelDebiteur: "Fenyila",
    telTogo: "Kaƒoƒo (Togo)",
    parcelRef: "Anyigba ƒe xexlẽdzesi (TF, Lot, OTR)",
  },
  Kabiyè: {
    slogan: "Samaɣ yɔɔ kandɩyʊ",
    newChat: "Kɛdɛɣa kɩfalaɣ",
    navChat: "Paɣtʊ yɔɔ sɩnɩyʊ",
    navDocs: "Takayɩsɩ maʊ",
    navActe: "Takayɩsɩ taa lɩzʊʊ",
    navTerra: "Tɛtʊ ñɩnʊʊ",
    navPrev: "Pʊcɔ na-tɛtʊ yaʊ (7)",
    titleChat: "Paɣtʊ yɔɔ sɩnɩyʊ (Assistant juridique)",
    titleDocs: "Takayɩsɩ maʊ (Génération de courriers)",
    titleActe: "Takayɩsɩ taa lɩzʊʊ (Analyse d’actes)",
    titleTerra: "TerraCheck : Tɛtʊ ñɩnʊʊ",
    titlePrev: "Lɔŋ tasɩtʊ 7 pʊcɔ nɛ na-ya tɛtʊ Togo taa",
    downloadPdf: "Kpaɣ PDF takayaɣ",
    writeRecommendedLetter: "Ma takayaɣ kanɛ lɛɛlɛɛyɔ",
    voiceModeBtn: "Nɔɔ yɔɔdʊʊ (FR)",
    historyLabel: "Ñɔ-tɔm kɛdɩtʊ",
    searchConvPlaceholder: "Ñɩnɩ kɛdɛɣa nakɛyɛ",
    noConv: "Kɛdɛɣa nakɛyɛ fɛyɩ.",
    signIn: "Sʊʊ",
    signInSub: "Google, Apple, E-mail",
    share: "Tɛyɩ",
    themeLight: "Mʊntʊsʊʊ",
    themeDark: "Cɩkpɛndʊʊ",
    greeting: "Kʊjɔŋ, Togo tʊ",
    heroTitle: "Ɛzɩma manpɩzɩɣ mansa-ŋ Togo paɣtʊ yɔɔ ?",
    suggestions: [
      "Mañʊʊdʊ ɛtaahɛyɩ-m ma-tʊmɩyɛ liidiye, manda ɛzɩma ?",
      "Ɖɩɣa tɩnʊ caɣ se ɛlɩzɩ-m ɖɩɣa taa nɛ ɖoŋ, Togo paɣtʊ ha waɖɛ ɖɩnɛ ?",
      "Pʊcɔ nɛ na-tɛtʊ Agoè yaa Lomé lɛ, ɛbɛ pʊwɛɛ se na-cɔnɩ OTR nɛ Titre Foncier taa ?",
      "Ñɩnɩ Togo tʊmɩyɛ paɣtʊ (Code du travail) taa tɔm nakɛyɛ.",
    ],
    langWarning: "Tɔm tʊnɛ AI lɩzɩna-tʊ Kabɩyɛ taa : Fransɩɩ paɣtʊ takayaɣ kɛna tɔm maɣmaɣ.",
    searchingLaws: "Ɖɩñɩnɩɣ Togo paɣtʊ takayɩsɩ taa…",
    questionPlaceholder: "Pozɩ ñɔ-tɔm Togo paɣtʊ yɔɔ (Kabɩyɛ yaa Fransɩɩ)…",
    listenResponse: "Welɩsɩ (Écouter)",
    stopListening: "Sɩɩ (Arrêter)",
    copyResponse: "Kɔpi tɔm tʊnɛ",
    aiDraftedNote: "AI mana tɔm tʊnɛ nɛ pɩtɩŋna Togo paɣtʊ takayɩsɩ nzɩ sɩwɛ yɔ sɩ-yɔɔ.",
    degradedNote: "AI fɛyɩ alɩwaatʊ tʊnɛ : paɣtʊ takayaɣ taa tɔm kɛlɛ.",
    demoNote: "Kpɛlɛkɩtʊ takayɩsɩ yɔɔ patɩŋnaa.",
    sourcesTitle: "Paɣtʊ takayɩsɩ",
    copyRef: "Kɔpi hɩɖɛ",
    originalSource: "Takayaɣ kɩbɩnaɣ",
    footerDisclaimer: "Tɔm kɛdɩtʊ kɛlɛ, pɩtɛkɛ avocat tɔm.",
    acteIntro: "Kpa foto yaa sɩɩ tɛtʊ takayaɣ tɔm cɩnɛ nɛ ɖɩcɔnɩ tɩ-taa.",
    photoActe: "Kpa takayaɣ foto",
    sample1: "Kpɛlɛkɩtʊ : Agoè-Nyivé, lot 14",
    sample2: "Kpɛlɛkɩtʊ : Tɛtʊ pɛdʊʊ nabʊlɛ (Kégué)",
    sample3: "Kpɛlɛkɩtʊ : Notaire takayaɣ (Baguida)",
    actePlaceholder: "Sɩɩ takayaɣ taa tɔm cɩnɛ…",
    analyzeActe: "Cɔnɩ takayaɣ taa",
    analyzing: "Cɔnaʊ…",
    extractedInfo: "Tɔm ndʊ lɩwa yɔ",
    seeOnMap: "Cɔnɩ tɛtʊ tata yɔɔ",
    mapsItinerary: "Nɔmɔʊ (Google Maps)",
    switchToTerra: "Tɛtʊ ñɩnʊʊ",
    terraIntro: "Lɩzɩ tɛtʊ nakɛyɛ nɛ na-cɔnɩ tɩ-yɔɔ OTR (3 Tampons) yaa na-tɩŋ Google Maps nɔmɔʊ.",
    terraSearchPlaceholder: "Ñɩnɩ egeetiye (Agoè, Kégué, Baguida…), lot yaa TF",
    analyzeThisActe: "Cɔnɩ takayaɣ taa",
    gpsCoords: "GPS lone",
    communeQuartier: "Egeetiye",
    legalStatus: "Paɣtʊ wɛtʊ",
    refTitreOtr: "Titre / OTR ñʊʊ",
    check3Tampons: "3 Tampons cɔnaʊ",
    registeredOwner: "Tɛtʊ tɩnʊ hɩɖɛ",
    customaryOrigin: "Liɖe / Ɖɩɣa",
    securityChecks: "Tɛtʊ cɔnaʊ",
    mutationHistory: "Pɛdʊʊ kɩbɩnʊʊ",
    recommendation: "Lɔŋ tasɩtʊ",
    letterType: "Takayaɣ wɛtʊ",
    groupTravail: "1. Tʊmɩyɛ paɣtʊ (Code du travail)",
    groupBail: "2. Ɖɩɣa paɣtʊ (Bail)",
    groupFoncier: "3. Tɛtʊ paɣtʊ nɛ Cadastre OTR",
    groupJustice: "4. Tɔm hʊʊ nɛ Kɩmɩyɛ",
    letterSalaire: "Tʊmɩyɛ liidiye : mise en demeure",
    letterInspectionTravail: "Wolo tʊmɩyɛ cɔnɩyaa cɔlɔ",
    letterLicenciement: "Kʊyɩnaʊ tʊmɩyɛ taa pɩfɛyɩ paɣtʊ taa",
    letterCertificat: "Pɔzɩ tʊmɩyɛ takayaɣ nɛ CNSS",
    letterBail: "Ɖɩɣa : kʊyɩnaʊ ɖɩɣa taa",
    letterRestitutionCaution: "Pɔzɩ ña-caution liidiye",
    letterPreavisLocataire: "Ɖɩɣa hɛyɩyʊ lɩʊ (préavis)",
    letterOppFoncier: "Sɩɩ nɔɔ nɛ tɛtʊ pɛdʊʊ kɩfalʊʊ (OTR)",
    letterEtatDescriptif: "Pɔzɩ tɛtʊ wɛtʊ (Cadastre)",
    letterMiseDemeureVendeur: "Pɔzɩ Titre Foncier / 3 Tampons",
    letterPlainte: "Wolo tɔm hʊʊ kɩyakʊ (Procureur)",
    letterDette: "Pɔzɩ kɩmɩyɛ liidiye",
    fullName: "Ña-hɩɖɛ maɣmaɣ",
    yourAddress: "Ña-lone (Adresse)",
    employer: "Tʊmɩyɛ tɩnʊ",
    landlord: "Ɖɩɣa tɩnʊ",
    destLabelOtr: "OTR ñʊʊdʊ",
    destLabelProc: "Ɛyʊ weyi ewoba tɔm taa yɔ",
    destLabelVendeur: "Tɛtʊ pɛdɩyʊ",
    destLabelDebiteur: "Kɩmɩyɛ tʊ",
    city: "Tɛtʊ (Ville)",
    telTogo: "Telefon (Togo)",
    parcelRef: "Tɛtʊ ñʊʊ (TF, Lot, OTR)",
    amountDue: "Liidiye ñʊʊ (FCFA)",
    unpaidPeriod: "Alɩwaatʊ",
    unpaidPeriodPlaceholder: "kpɛlɛkɩtʊ : Hasɩyaɖɛ ŋtalɩ Salaŋ 2026",
    extraDetails: "Tɔm lɛɛtʊ",
    generateLetter: "Ma takayaɣ",
    generatingLetter: "Maʊ…",
    copy: "Kɔpi",
    download: "Kpaɣ",
    whereToGo: "Ɖenɖe pʊwɛɛ se ewolo yɔ",
    refTexts: "Paɣtʊ takayɩsɩ",
    letterIntro: "Togo komina paɣtʊ takayɩsɩ yɔɔ patɩŋnaa.",
    accountSaveNote: "Sɩɩ ñɔ-tɔm kɛdɩtʊ.",
    switchAccount: "Lɛɣzɩ hɩɖɛ",
    logout: "Lɩɩ",
    continueGoogle: "Tɩŋna Google",
    continueApple: "Tɩŋna Apple",
    continueMicrosoft: "Tɩŋna Microsoft",
    useEmail: "Tɩŋna E-mail",
    hideEmail: "Mɛlɩ E-mail",
    saveAccount: "Sɩɩ",
    loading: "Pɩlakɩ tʊmɩyɛ…",
    refCopied: "Pakɔpɩwa",
    unverifiedStatus: "patacɔnɩ paɣtʊ tʊnɛ tɩ-yɔɔ",
    verifiedStatus: "pacɔnaa",
    buyerLabel: "Pɛdɩyʊ (Acquéreur)",
    areaLabel: "Walanzɩ (m²)",
    lotLabel: "Lot",
    ilotLabel: "Îlot",
    verdictRougeDefault: "Kʊñɔŋ sɔsɔʊ nakʊyʊ wɛɛ (tɛtʊ pɛdʊʊ nabʊlɛ yaa you) : taasɩɩ ñɔ-nesi takayaɣ kanɛ ka-taa nɛ taahɛyɩ liidiye pʊcɔ OTR cɔnɩ.",
    verdictOrangeDefault: "Cɔnɩ camɩyɛ : yeba nɛ Notaire cɔnɩ Titre Foncier nɛ 3 tampons pʊcɔ nasɩɩ nesi.",
    verdictVertDefault: "Takayaɣ nɛ tɛtʊ pɛwɛ ɖeu OTR taa : napɩzɩɣ naɖɔ Notaire cɔlɔ.",
    noParcelMatch: "Tɛtʊ tʊnɛ tɩfɛyɩ ɖa-takayaɣ taa : wolo OTR Cadastre.",
    ambiguousParcelMatch: "Tɛtʊ ndɩ ndɩ wɛɛ : yɔɔdɩ egeetiye yaa îlot.",
    tamponsComplete: "Pɩtɛma (Géomètre, Mairie, Cadastre OTR)",
    tamponsMissing: "Pɩfɛyɩ (Kʊñɔŋ)",
    tamponsPending: "Pɩlakɩ tʊmɩyɛ Cadastre",
    scoreLabels: { vert: "ɖeu (vert)", orange: "cɔnaʊ (orange)", rouge: "kʊñɔŋ (rouge)" },
    destLabelOtr: "OTR ñʊʊ",
    destLabelProc: "Ʋɔnudrɔ̃ƒe",
    destLabelVendeur: "Tɛtʊ pɛdɩyʊ",
    destLabelDebiteur: "Fenyila",
    telTogo: "Telefon (Togo)",
    parcelRef: "Tɛtʊ ñʊʊ (TF, Lot, OTR)",
  },
};

const CHECK_TRANSLATIONS: Record<string, { Ewé: string; Kabiyè: string }> = {
  "Titre foncier enregistré au Livre Foncier (OTR)": {
    Ewé: "Anyigbagbalẽ gã (Titre Foncier) le OTR ƒe agbalẽ me",
    Kabiyè: "Titre Foncier wɛ OTR takayaɣ sɔsɔɣa taa",
  },
  "Aucune double vente détectée sur la parcelle": {
    Ewé: "Womedzra anyigba sia zi eve o (Aucune double vente)",
    Kabiyè: "Patapɛdɩ tɛtʊ tʊnɛ nabʊlɛ",
  },
  "Aucun litige ni opposition judiciaire déclarés": {
    Ewé: "Dzre alo ʋɔnudrɔ̃nya aɖeke mele anyigba sia ŋu o",
    Kabiyè: "You yaa tɔm hʊʊ nakʊyʊ fɛyɩ tɛtʊ tʊnɛ tɩ-yɔɔ",
  },
  "Bornage contradictoire et limites cadastrales précises": {
    Ewé: "Anyigba ƒe liƒowo kple dzidzenuwo le eme nyuie",
    Kabiyè: "Tɛtʊ kamaɣ wɛ ɖeu Cadastre taa",
  },
  "Conforme au plan d'urbanisme (Hors réserve administrative)": {
    Ewé: "Esɔ ɖe du ƒe ɖoɖo nu (Menye dziɖuɖu ƒe anyigba o)",
    Kabiyè: "Pɩkpɛndɩna tɛtʊ ñɔɔzʊʊ paɣtʊ (Pɩtɛkɛ komina tɛtʊ)",
  },
  "Le vendeur de l'acte correspond au propriétaire inscrit à l'OTR": {
    Ewé: "Nudzrala ƒe ŋkɔ sɔ kple anyigbatɔ si le OTR ƒe agbalẽ me",
    Kabiyè: "Pɛdɩyʊ hɩɖɛ kpɛndɩna OTR takayaɣ taa ñɩnɖɛ",
  },
  "Superficie de l'acte cohérente avec le plan cadastral (±5%)": {
    Ewé: "Anyigbaa ƒe kekeme sɔ kple Cadastre ƒe tata (±5%)",
    Kabiyè: "Tɛtʊ walanzɩ kpɛndɩna Cadastre ñɩndʊ (±5%)",
  },
};

export function translateCheckLabel(label: string, lang: Lang): string {
  if (lang === "Français") return label;
  return CHECK_TRANSLATIONS[label]?.[lang] || label;
}

export function translateAdvice(score: "vert" | "orange" | "rouge", defaultAdvice: string, lang: Lang): string {
  if (lang === "Français") return defaultAdvice;
  const ui = t(lang);
  if (score === "rouge") return ui.verdictRougeDefault;
  if (score === "orange") return ui.verdictOrangeDefault;
  return ui.verdictVertDefault;
}

export function t(lang: Lang): UI {
  return I18N[lang] || I18N["Français"];
}
