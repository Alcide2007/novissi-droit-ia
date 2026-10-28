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
  // Génération de courriers
  letterType: string;
  letterSalaire: string;
  letterBail: string;
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
    letterSalaire: "Salaire non payé : mise en demeure",
    letterBail: "Bail : départ sans préavis",
    fullName: "Votre nom complet",
    yourAddress: "Votre adresse",
    employer: "Employeur",
    landlord: "Propriétaire",
    city: "Ville",
    amountDue: "Montant dû (FCFA)",
    unpaidPeriod: "Période impayée",
    unpaidPeriodPlaceholder: "ex. juillet à septembre 2026",
    extraDetails: "Précisions (facultatif)",
    generateLetter: "Générer le courrier",
    generatingLetter: "Rédaction…",
    copy: "Copier",
    download: "Télécharger",
    whereToGo: "Où vous adresser",
    refTexts: "Textes de référence",
  },
  Ewé: {
    slogan: "Dukɔa ƒe senyala",
    newChat: "Dzeɖoɖo yeye",
    navChat: "Senyawo ƒe kpekpeɖeŋu",
    navDocs: "Agbalẽŋɔŋlɔ",
    navActe: "Agbalẽwo me ɖeɖe",
    navTerra: "Anyigba dodokpɔ",
    titleChat: "Senyawo ƒe kpekpeɖeŋu",
    titleDocs: "Agbalẽŋɔŋlɔ",
    titleActe: "Agbalẽwo me ɖeɖe",
    titleTerra: "TerraCheck : Anyigba dodokpɔ",
    historyLabel: "Wò dzeɖoɖowo",
    searchConvPlaceholder: "Di dzeɖoɖo aɖe",
    noConv: "Dzeɖoɖo aɖeke meli o.",
    signIn: "Ge ɖe eme",
    signInSub: "Google, Apple, E-mail",
    accountSaveNote: "Dzra wò dzeɖoɖowo, wò agbalẽwo kple wò anyigba dodokpɔwo ɖo.",
    switchAccount: "Trɔ akɔnta",
    logout: "Do go le eme",
    continueGoogle: "Yi edzi kple Google",
    continueApple: "Yi edzi kple Apple",
    continueMicrosoft: "Yi edzi kple Microsoft",
    useEmail: "Zã E-mail",
    hideEmail: "Ɣla E-mail",
    saveAccount: "Dzra akɔntaa ɖo",
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
    langWarning: "Ŋuɖoɖo siwo le Eʋegbe me la tso AI gbɔ : Togo ƒe se ƒe agbalẽ lae nye kpeɖodzi.",
    searchingLaws: "Míele Togo ƒe se ƒe agbalẽwo me dzrom…",
    loading: "Ele dɔ wɔm…",
    questionPlaceholder: "Bia nya si le dziwò le Togo ƒe sewo ŋu…",
    listenResponse: "See",
    stopListening: "Tɔ",
    copyResponse: "Kɔpi ŋuɖoɖoa",
    aiDraftedNote: "AI ye ŋlɔ ŋuɖoɖo sia tso Togo ƒe se siwo wohe ɖe ete la me.",
    degradedNote: "AI meli fifia o : se ƒe kpukpui ŋutɔŋutɔwoe nye esia.",
    demoNote: "Kpɔɖeŋu ƒe nuŋlɔɖiwo dzi wotu ŋuɖoɖo sia ɖo.",
    sourcesTitle: "Se ƒe agbalẽ siwo dzi wotu ŋuɖoɖoa ɖo",
    copyRef: "Kɔpi se ƒe ŋkɔ",
    refCopied: "Wokɔpi ŋkɔa",
    originalSource: "Se ƒe agbalẽ",
    unverifiedStatus: "womedo se sia ƒe dɔwɔwɔ kpɔ haɖe o",
    verifiedStatus: "wodo se sia kpɔ",
    footerDisclaimer: "Nyatakaka gbadzaa ko esia nye, menye senyala ƒe aɖaŋuɖoɖo o.",
    acteIntro: "Ɖe foto alo da anyigbagbalẽ alo nubabla ƒe nyawo ɖe afii be míado eƒe dedienɔnɔ akpɔ.",
    photoActe: "Ɖe foto agbalẽa",
    sample1: "Kpɔɖeŋu : Agoè-Nyivé, lot 14",
    sample2: "Kpɔɖeŋu : Anyigba dzra zi eve (Kégué)",
    sample3: "Kpɔɖeŋu : Notaire ƒe agbalẽ (Baguida)",
    actePlaceholder: "Da agbalẽa ƒe nyawo ɖe afii alo ɖe eƒe foto…",
    analyzeActe: "Do agbalẽa kpɔ",
    analyzing: "Dodokpɔ le edzi…",
    extractedInfo: "Nyatakaka siwo míekpɔ le agbalẽa me",
    buyerLabel: "Nuƒlela (Acquéreur)",
    areaLabel: "Kekeme (m²)",
    lotLabel: "Lot",
    ilotLabel: "Îlot",
    seeOnMap: "Kpɔe le anyigbatata dzi",
    mapsItinerary: "Mɔfiafia (Google Maps)",
    switchToTerra: "Anyigba dodokpɔ",
    verdictRougeDefault: "Afɔku gã aɖe dze (anyigba dzra zi eve alo nya baɖa le agbalẽa me) : megade asi agbalẽ sia te o eye megaxe ga aɖeke hafi ayi OTR o.",
    verdictOrangeDefault: "Kpɔ nyuie : na Notaire nàdo Titre Foncier, kpeɖodzi 3 (3 tampons) kple anyigba ƒe liƒowo kpɔ hafi nàde asi ete.",
    verdictVertDefault: "Agbalẽa kple anyigbaa sɔ ɖe Cadastre ƒe sewo nu : nàte ŋu ayi edzi le wò Notaire ŋkume.",
    noParcelMatch: "Anyigba sia medze le míaƒe agbalẽ me o : yi ɖado eŋu kpɔ le OTR Cadastre.",
    ambiguousParcelMatch: "Anyigba geɖe sɔ kple esia : yɔ nuto alo îlot ƒe ŋkɔ nyuie.",
    terraIntro: "Tia anyigba aɖe be nàdo eƒe Titre Foncier (OTR / Kpeɖodzi 3) akpɔ alo nàdi mɔ ɖe egbɔ to Google Maps dzi.",
    terraSearchPlaceholder: "Di nuto (Agoè, Kégué, Baguida…), lot alo TF",
    analyzeThisActe: "Do agbalẽa kpɔ",
    gpsCoords: "GPS ƒe nɔƒe",
    communeQuartier: "Nuto / Kɔƒe",
    legalStatus: "Se ƒe nɔnɔme",
    refTitreOtr: "Titre / OTR ƒe xexlẽdzesi",
    check3Tampons: "Kpeɖodzi 3 (3 Tampons)",
    tamponsComplete: "Eblibo (Géomètre, Fia/Mairie, Cadastre OTR)",
    tamponsMissing: "Meli o (Afɔku gã)",
    tamponsPending: "Wole edzrom le Cadastre",
    registeredOwner: "Anyigbatɔ ƒe ŋkɔ",
    customaryOrigin: "Ƒome si tɔ wònye",
    securityChecks: "Anyigba ƒe dedienɔnɔ dodokpɔ",
    mutationHistory: "Anyigba ƒe dzradzra xoxowo",
    recommendation: "Aɖaŋuɖoɖo",
    scoreLabels: { vert: "nyui (vert)", orange: "nudodokpɔ (orange)", rouge: "afɔku (rouge)" },
    letterType: "Agbalẽ ƒe ƒomevi",
    letterSalaire: "Fetu maxemaxe : agbalẽ sẽŋu (mise en demeure)",
    letterBail: "Xɔhaya : nyanya le xɔ me préavis manɔmee",
    fullName: "Wò ŋkɔ blibo",
    yourAddress: "Nɔƒewò (Adresse)",
    employer: "Dɔwɔtɔ (Employeur)",
    landlord: "Aƒetɔ (Propriétaire)",
    city: "Du (Ville)",
    amountDue: "Ga home si wònyi le ŋuwò (FCFA)",
    unpaidPeriod: "Ɣeyiɣi si ƒe fetu womexe o",
    unpaidPeriodPlaceholder: "kpɔɖeŋu : Siamlɔm va se ɖe Anyɔnyɔ 2026",
    extraDetails: "Nya bubuwo (ne ehiã)",
    generateLetter: "Ŋlɔ agbalẽa",
    generatingLetter: "Ŋɔŋlɔ le edzi…",
    copy: "Kɔpi",
    download: "Wɔ kopie",
    whereToGo: "Teƒe siwo nàte ŋu ayi",
    refTexts: "Se ƒe kpukpuiwo",
  },
  Kabiyè: {
    slogan: "Samaɣ yɔɔ kandɩyʊ",
    newChat: "Kɛdɛɣa kɩfalaɣ",
    navChat: "Paɣtʊ yɔɔ sɩnɩyʊ",
    navDocs: "Takayɩsɩ maʊ",
    navActe: "Takayɩsɩ taa lɩzʊʊ",
    navTerra: "Tɛtʊ ñɩnʊʊ",
    titleChat: "Paɣtʊ yɔɔ sɩnɩyʊ",
    titleDocs: "Takayɩsɩ maʊ",
    titleActe: "Takayɩsɩ taa lɩzʊʊ",
    titleTerra: "TerraCheck : Tɛtʊ ñɩnʊʊ",
    historyLabel: "Ñɔ-tɔm kɛdɩtʊ",
    searchConvPlaceholder: "Ñɩnɩ kɛdɛɣa nakɛyɛ",
    noConv: "Kɛdɛɣa nakɛyɛ fɛyɩ.",
    signIn: "Sʊʊ",
    signInSub: "Google, Apple, E-mail",
    accountSaveNote: "Đʊ ñɔ-tɔm kɛdɩtʊ, ña-takayɩsɩ nɛ tɛtʊ ñɩnʊʊ ɖoli kʊɖʊm.",
    switchAccount: "Lɛɣzɩ hɩɖɛ",
    logout: "Lɩɩ",
    continueGoogle: "Tɩŋna Google",
    continueApple: "Tɩŋna Apple",
    continueMicrosoft: "Tɩŋna Microsoft",
    useEmail: "Tɩŋna E-mail",
    hideEmail: "Mɛlɩ E-mail",
    saveAccount: "Sɩɩ",
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
    loading: "Pɩlakɩ tʊmɩyɛ…",
    questionPlaceholder: "Pozɩ ñɔ-tɔm Togo paɣtʊ yɔɔ…",
    listenResponse: "Welɩsɩ",
    stopListening: "Sɩɩ",
    copyResponse: "Kɔpi tɔm tʊnɛ",
    aiDraftedNote: "AI mana tɔm tʊnɛ nɛ pɩtɩŋna Togo paɣtʊ takayɩsɩ yɔɔ.",
    degradedNote: "AI fɛyɩ alɩwaatʊ tʊnɛ : paɣtʊ takayaɣ taa tɔm kɛlɛ.",
    demoNote: "Kpɛlɛkɩtʊ takayɩsɩ yɔɔ patɩŋnaa.",
    sourcesTitle: "Paɣtʊ takayɩsɩ",
    copyRef: "Kɔpi hɩɖɛ",
    refCopied: "Pakɔpɩwa",
    originalSource: "Takayaɣ kɩbɩnaɣ",
    unverifiedStatus: "patacɔnɩ paɣtʊ tʊnɛ tɩ-yɔɔ haɖɛ",
    verifiedStatus: "pacɔnaa",
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
    buyerLabel: "Pɛdɩyʊ (Acquéreur)",
    areaLabel: "Walanzɩ (m²)",
    lotLabel: "Lot",
    ilotLabel: "Îlot",
    seeOnMap: "Cɔnɩ tɛtʊ tata yɔɔ",
    mapsItinerary: "Nɔmɔʊ (Google Maps)",
    switchToTerra: "Tɛtʊ ñɩnʊʊ",
    verdictRougeDefault: "Kʊñɔŋ sɔsɔʊ nakʊyʊ wɛɛ (tɛtʊ pɛdʊʊ nabʊlɛ yaa you) : taasɩɩ ñɔ-nesi takayaɣ kanɛ ka-taa nɛ taahɛyɩ liidiye pʊcɔ OTR cɔnɩ.",
    verdictOrangeDefault: "Cɔnɩ camɩyɛ : yeba nɛ Notaire cɔnɩ Titre Foncier nɛ 3 tampons pʊcɔ nasɩɩ nesi.",
    verdictVertDefault: "Takayaɣ nɛ tɛtʊ pɛwɛ ɖeu OTR taa : napɩzɩɣ naɖɔ Notaire cɔlɔ.",
    noParcelMatch: "Tɛtʊ tʊnɛ tɩfɛyɩ ɖa-takayaɣ taa : wolo OTR Cadastre.",
    ambiguousParcelMatch: "Tɛtʊ ndɩ ndɩ wɛɛ : yɔɔdɩ egeetiye yaa îlot.",
    terraIntro: "Lɩzɩ tɛtʊ nakɛyɛ nɛ na-cɔnɩ tɩ-yɔɔ OTR (3 Tampons) yaa na-tɩŋ Google Maps nɔmɔʊ.",
    terraSearchPlaceholder: "Ñɩnɩ egeetiye (Agoè, Kégué, Baguida…), lot yaa TF",
    analyzeThisActe: "Cɔnɩ takayaɣ taa",
    gpsCoords: "GPS lone",
    communeQuartier: "Egeetiye",
    legalStatus: "Paɣtʊ wɛtʊ",
    refTitreOtr: "Titre / OTR ñʊʊ",
    check3Tampons: "3 Tampons cɔnaʊ",
    tamponsComplete: "Pɩtɛma (Géomètre, Mairie, Cadastre OTR)",
    tamponsMissing: "Pɩfɛyɩ (Kʊñɔŋ)",
    tamponsPending: "Pɩlakɩ tʊmɩyɛ Cadastre",
    registeredOwner: "Tɛtʊ tɩnʊ hɩɖɛ",
    customaryOrigin: "Liɖe / Ɖɩɣa",
    securityChecks: "Tɛtʊ cɔnaʊ",
    mutationHistory: "Pɛdʊʊ kɩbɩnʊʊ",
    recommendation: "Lɔŋ tasɩtʊ",
    scoreLabels: { vert: "ɖeu (vert)", orange: "cɔnaʊ (orange)", rouge: "kʊñɔŋ (rouge)" },
    letterType: "Takayaɣ wɛtʊ",
    letterSalaire: "Tʊmɩyɛ liidiye : mise en demeure",
    letterBail: "Ɖɩɣa : kʊyɩnaʊ",
    fullName: "Ña-hɩɖɛ maɣmaɣ",
    yourAddress: "Ña-lone (Adresse)",
    employer: "Tʊmɩyɛ tɩnʊ",
    landlord: "Ɖɩɣa tɩnʊ",
    city: "Tɛtʊ (Ville)",
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
